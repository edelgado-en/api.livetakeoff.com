import csv, io, zipfile, datetime
from django.db import transaction
from django.db.models import Q, When, Value, Case, CharField
from django.utils import timezone

from api.email_notification_service import EmailNotificationService

from api.models import (UserCustomer, UserAvailableAirport, ExportJob, Job)

def _apply_filters(base_qs, params: dict, user):
    """
    Mirrors the original get_queryset() logic but works in an async task context.
    `params` comes from ExportJob.params (the UI filters).
    `user` is the Django user who requested the export.
    """

    # ----- read params with sane defaults -----
    is_mobile_request = params.get("isMobileRequest", False)
    search_text = params.get("searchText", "")
    status = params.get("status", "All")
    airport = params.get("airport")
    fbo = params.get("fbo")
    customer = params.get("customer")
    additional_fees = params.get("additionalFees", []) or []

    requested_from = params.get("requestedDateFrom")
    requested_to   = params.get("requestedDateTo")

    arrival_from = params.get("arrivalDateFrom")
    arrival_to   = params.get("arrivalDateTo")

    departure_from = params.get("departureDateFrom")
    departure_to   = params.get("departureDateTo")

    complete_by_from = params.get("completeByDateFrom")
    complete_by_to   = params.get("completeByDateTo")

    completion_from = params.get("completionDateFrom")
    completion_to   = params.get("completionDateTo")

    qs = base_qs

    # ----- additional fees -----
    # A: travel, F: fbo, M: management, V: vendor higher price
    for fee in additional_fees:
        if fee == "A":
            qs = qs.filter(travel_fees_amount_applied__gt=0)
        elif fee == "F":
            qs = qs.filter(fbo_fees_amount_applied__gt=0)
        elif fee == "M":
            qs = qs.filter(management_fees_amount_applied__gt=0)
        elif fee == "V":
            qs = qs.filter(vendor_higher_price_amount_applied__gt=0)

    # ----- per-user visibility (customer vs staff/internal, etc.) -----
    user_profile = getattr(user, "profile", None)

    if user_profile and getattr(user_profile, "customer", None):
        # Customer users
        if getattr(user_profile, "is_job_submitter_only", False):
            qs = qs.filter(created_by=user)

        if customer and customer != "All":
            qs = qs.filter(customer_id=customer)
        else:
            # self + extra customers granted via UserCustomer
            customer_ids = [user_profile.customer.id]
            extra = UserCustomer.objects.filter(user=user).values_list("customer_id", flat=True)
            customer_ids.extend(list(extra))
            qs = qs.filter(customer_id__in=customer_ids)
    else:
        # Non-customer users
        if customer and customer != "All":
            qs = qs.filter(customer_id=customer)

    # Internal Coordinators restrictions (unless their flags allow everything)
    if user.groups.filter(name="Internal Coordinators").exists():
        if not getattr(user_profile, "enable_all_customers", False):
            cust_ids = list(
                UserCustomer.objects.filter(user=user).values_list("customer_id", flat=True)
            )
            if cust_ids:
                qs = qs.filter(customer_id__in=cust_ids)

        if not getattr(user_profile, "enable_all_airports", False):
            ap_ids = list(
                UserAvailableAirport.objects.filter(user=user).values_list("airport_id", flat=True)
            )
            if ap_ids:
                qs = qs.filter(airport_id__in=ap_ids)

    # ----- search -----
    if search_text:
        qs = qs.filter(
            Q(tailNumber__icontains=search_text)
            | Q(customer_purchase_order__icontains=search_text)
            | Q(purchase_order__icontains=search_text)
        )

    # ----- status set -----
    if status == "All":
        if user_profile and getattr(user_profile, "customer", None):
            # for customer users, exclude 'T' normally; tweak for mobile request
            if is_mobile_request:
                qs = qs.filter(Q(status="C") | Q(status="I") | Q(status="N"))
            else:
                qs = qs.filter(Q(status="C") | Q(status="I") | Q(status="A") | Q(status="S") | Q(status="U") | Q(status="W") | Q(status="N"))
        else:
            qs = qs.filter(Q(status="C") | Q(status="I") | Q(status="T") | Q(status="N"))
    else:
        qs = qs.filter(status=status)

    # ----- simple filters -----
    if airport and airport != "All":
        qs = qs.filter(airport_id=airport)

    if fbo and fbo != "All":
        qs = qs.filter(fbo_id=fbo)

    # ----- date range filters -----
    # Arrival (estimatedETA)
    if arrival_from:
        qs = qs.filter(estimatedETA__gte=arrival_from)
    if arrival_to:
        qs = qs.filter(estimatedETA__lte=arrival_to)

    # Requested (requestDate)
    if requested_from:
        qs = qs.filter(requestDate__gte=requested_from)
    if requested_to:
        qs = qs.filter(requestDate__lte=requested_to)

    # Departure (estimatedETD)
    if departure_from:
        qs = qs.filter(estimatedETD__gte=departure_from)
    if departure_to:
        qs = qs.filter(estimatedETD__lte=departure_to)

    # Complete by (completeBy)
    if complete_by_from:
        qs = qs.filter(completeBy__gte=complete_by_from)
    if complete_by_to:
        qs = qs.filter(completeBy__lte=complete_by_to)

    # Completion (completion_date)
    if completion_from:
        qs = qs.filter(completion_date__gte=completion_from)
    if completion_to:
        qs = qs.filter(completion_date__lte=completion_to)

    # ----- performance selects -----
    qs = qs.select_related("airport", "customer", "fbo", "aircraftType")

    # ----- custom status ordering + secondary ordering -----
    # Order map matches your comment
    order = {
        "U": 1,  # Submitted
        "A": 2,  # Accepted
        "S": 3,  # Assigned
        "W": 4,  # WIP
        "C": 5,  # Complete
        "I": 6,  # Invoiced
        "N": 7,  # (assuming another state you use)
        "T": 8,  # Cancelled
    }
    ordering_conditions = [When(status=s, then=Value(rank)) for s, rank in order.items()]
    secondary_ordering = "-completion_date"

    qs = qs.order_by(
        Case(*ordering_conditions, default=Value(8), output_field=CharField()),
        secondary_ordering,
    )

    return qs

def run_export(export_id: int):
    # --- 0) Fetch the job row safely (no lock). Bail out if missing. ---
    ej = (
        ExportJob.objects
        .filter(pk=export_id)
        .select_related(
            "user",
            "user__profile",
            "user__profile__customer",
            "user__profile__customer__customer_settings",
        )
        .first()
    )
    if not ej:
        # Guard: if the task ever runs before the row is committed
        # (should not happen once you use transaction.on_commit to enqueue),
        # just exit gracefully.
        return

    # --- 1) Flip to RUNNING inside a short transaction/lock ---
    with transaction.atomic():
        ej_running = ExportJob.objects.select_for_update().get(pk=export_id)
        ej_running.status = ExportJob.Status.RUNNING
        ej_running.started_at = timezone.now()
        ej_running.progress = 0
        ej_running.save(update_fields=["status", "started_at", "progress"])

    try:
        user = ej.user

        qs = Job.objects.all()
        qs = _apply_filters(qs, ej.params or {}, user)

        ExportJob.objects.filter(pk=ej.pk).update(progress=1)

        total = qs.count()

        ExportJob.objects.filter(pk=ej.pk).update(progress=2)

        # Determine price visibility
        show_job_price = True
        if getattr(user, "profile", None) and getattr(user.profile, "customer", None):
            show_job_price_at_customer_level = (
                user.profile.customer.customer_settings.show_job_price
            )
            if show_job_price_at_customer_level:
                show_job_price = bool(user.profile.show_job_price)
            else:
                show_job_price = False

        # Prepare CSV
        headers = [
            "P.O","Customer","Request Date","Tail Number","Aircraft","Airport","FBO",
            "Arrival Date","Departure Date","Complete By Date","Completion Date",
            "Travel Fees","FBO Fees","Vendor Price Diff","Management Fees","Price",
            "Services","Retainers"
        ]
        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=headers)
        writer.writeheader()

        processed = 0

        # Use iterator() to keep memory low
        for job in qs.iterator(chunk_size=500):
            # Cooperative cancel check
            ej_ref = ExportJob.objects.only("cancel_requested", "id").filter(pk=ej.pk).first()
            if ej_ref and ej_ref.cancel_requested:
                with transaction.atomic():
                    ej_cancel = ExportJob.objects.select_for_update().get(pk=export_id)
                    ej_cancel.status = ExportJob.Status.CANCELED
                    ej_cancel.finished_at = timezone.now()
                    ej_cancel.save(update_fields=["status", "finished_at"])
                return

            arrivalDate = job.estimatedETA.strftime("%m/%d/%Y %H:%M") if job.estimatedETA else ""
            departureDate = job.estimatedETD.strftime("%m/%d/%Y %H:%M") if job.estimatedETD else ""
            completeByDate = job.completeBy.strftime("%m/%d/%Y %H:%M") if job.completeBy else ""
            completionDate = job.completion_date.strftime("%m/%d/%Y %H:%M") if job.completion_date else ""

            services = ""
            for s in job.job_service_assignments.all():
                services += f"{s.service.name} | "

            retainers = ""
            for r in job.job_retainer_service_assignments.all():
                retainers += f"{r.retainer_service.name} | "

            row_common = {
                "P.O": job.purchase_order,
                "Customer": job.customer.name,
                "Request Date": job.requestDate.strftime("%m/%d/%Y %H:%M"),
                "Tail Number": job.tailNumber,
                "Aircraft": job.aircraftType.name,
                "Airport": job.airport.initials,
                "FBO": job.fbo.name,
                "Arrival Date": arrivalDate,
                "Departure Date": departureDate,
                "Complete By Date": completeByDate,
                "Completion Date": completionDate,
                "Services": services,
                "Retainers": retainers,
            }

            if show_job_price:
                row_common.update({
                    "Travel Fees": job.travel_fees_amount_applied,
                    "FBO Fees": job.fbo_fees_amount_applied,
                    "Vendor Price Diff": job.vendor_higher_price_amount_applied,
                    "Management Fees": job.management_fees_amount_applied,
                    "Price": job.price,
                })
            else:
                # Ensure columns still exist even if not shown
                row_common.update({
                    "Travel Fees": "",
                    "FBO Fees": "",
                    "Vendor Price Diff": "",
                    "Management Fees": "",
                    "Price": "",
                })

            writer.writerow(row_common)

            processed += 1
            if total and (processed % 2000 == 0 or processed == total):
                pct = int(processed * 100 / max(total, 1))
                ExportJob.objects.filter(pk=ej.pk).update(progress=pct)

        # If there were no rows, csv_buffer already only has headers (that’s fine)

        # --- 2) Build filenames (outer zip + inner csv) ---
        filename = f"jobs_{datetime.datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.zip"
        base_name = filename.rsplit(".", 1)[0]
        inner_filename = f"{base_name}.csv"

        # --- 3) Create ZIP in-memory ---
        zip_bytes = io.BytesIO()
        with zipfile.ZipFile(zip_bytes, mode="w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr(inner_filename, csv_buffer.getvalue())
        zip_bytes.seek(0)

        # --- 4) Save results atomically ---
        with transaction.atomic():
            ej_done = ExportJob.objects.select_for_update().get(pk=export_id)
            ej_done.file_bytes = zip_bytes.getvalue()
            ej_done.filename = filename
            ej_done.status = ExportJob.Status.SUCCEEDED
            ej_done.finished_at = timezone.now()
            ej_done.progress = 100
            ej_done.save(update_fields=[
                "file_bytes", "filename", "status", "finished_at", "progress"
            ])

        # --- 5) Notify user ---
        if ej.user and ej.user.email:
            EmailNotificationService().send_export_job_completed_notification(exportJob=ej_done)

    except Exception as e:
        with transaction.atomic():
            ej_fail = ExportJob.objects.select_for_update().get(pk=export_id)
            ej_fail.status = ExportJob.Status.FAILED
            ej_fail.error_message = str(e)
            ej_fail.finished_at = timezone.now()
            ej_fail.save(update_fields=["status", "error_message", "finished_at"])
        raise