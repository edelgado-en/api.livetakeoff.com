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
    # Wrap minimal state updates in transactions to keep rows consistent
    with transaction.atomic():
        ej = ExportJob.objects.select_for_update().get(pk=export_id)
        ej.status = ExportJob.Status.RUNNING
        ej.started_at = timezone.now()
        ej.progress = 0
        ej.save(update_fields=["status", "started_at", "progress"])

    try:
        user = ej.user

        qs = Job.objects.all()
        qs = _apply_filters(qs, ej.params or {}, user)

        total = qs.count()

        show_job_price = True

        # check the customer settings if the user is a customer user to check if show_job_price is True
        if user.profile.customer:
            show_job_price_at_customer_level = user.profile.customer.customer_settings.show_job_price

            if show_job_price_at_customer_level:
                show_job_price_at_customer_user_level = user.profile.show_job_price

                if show_job_price_at_customer_user_level:
                    show_job_price = True
                
                else:
                    show_job_price = False

            else:
                show_job_price = False

        if total == 0:
            # Create a CSV with just headers to keep behavior consistent
            csv_buffer = io.StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=[
                "P.O","Customer","Request Date","Tail Number","Aircraft","Airport","FBO",
                "Arrival Date","Departure Date","Complete By Date","Completion Date",
                "Travel Fees","FBO Fees","Vendor Price Diff","Management Fees","Price",
                "Services","Retainers"
            ])
            writer.writeheader()
        else:
            csv_buffer = io.StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=[
                "P.O","Customer","Request Date","Tail Number","Aircraft","Airport","FBO",
                "Arrival Date","Departure Date","Complete By Date","Completion Date",
                "Travel Fees","FBO Fees","Vendor Price Diff","Management Fees","Price",
                "Services","Retainers"
            ])
            writer.writeheader()

            processed = 0
            
            # Use iterator() to keep memory low
            for job in qs.iterator(chunk_size=2000):
                # If user requested cancel, stop cooperatively
                ej_ref = ExportJob.objects.only("cancel_requested","id").get(pk=ej.pk)
                if ej_ref.cancel_requested:
                    with transaction.atomic():
                        ej = ExportJob.objects.select_for_update().get(pk=export_id)
                        ej.status = ExportJob.Status.CANCELED
                        ej.finished_at = timezone.now()
                        ej.save(update_fields=["status","finished_at"])
                    return

                if job.estimatedETA:
                    arrivalDate = job.estimatedETA.strftime('%m/%d/%Y %H:%M')
                else:
                    arrivalDate = ''
                
                if job.estimatedETD:
                    departureDate = job.estimatedETD.strftime('%m/%d/%Y %H:%M')
                else:
                    departureDate = ''
                
                if job.completeBy:
                    completeByDate = job.completeBy.strftime('%m/%d/%Y %H:%M')
                else:
                    completeByDate = ''
                
                if job.completion_date:
                    completionDate = job.completion_date.strftime('%m/%d/%Y %H:%M')
                else:
                    completionDate = ''

                # add list of services to csv
                services = ''
                for service in job.job_service_assignments.all():
                    services += service.service.name + ' | '

                # add list of retainers to csv
                retainers = ''
                for retainer in job.job_retainer_service_assignments.all():
                    retainers += retainer.retainer_service.name + ' | '

                if show_job_price:
                    writer.writerow({
                        'P.O': job.purchase_order,
                        'Customer': job.customer.name,
                        'Request Date': job.requestDate.strftime('%m/%d/%Y %H:%M'),
                        'Tail Number': job.tailNumber,
                        'Aircraft': job.aircraftType.name,
                        'Airport': job.airport.initials,
                        'FBO': job.fbo.name,
                        'Arrival Date': arrivalDate,
                        'Departure Date': departureDate,
                        'Complete By Date': completeByDate,
                        'Completion Date': completionDate,
                        'Travel Fees': job.travel_fees_amount_applied,
                        'FBO Fees': job.fbo_fees_amount_applied,
                        'Vendor Price Diff': job.vendor_higher_price_amount_applied,
                        'Management Fees': job.management_fees_amount_applied,
                        'Price': job.price,
                        'Services': services,
                        'Retainers': retainers
                    })
                else:
                    writer.writerow({
                        'P.O': job.purchase_order,
                        'Customer': job.customer.name,
                        'Request Date': job.requestDate.strftime('%m/%d/%Y %H:%M'),
                        'Tail Number': job.tailNumber,
                        'Aircraft': job.aircraftType.name,
                        'Airport': job.airport.initials,
                        'FBO': job.fbo.name,
                        'Arrival Date': arrivalDate,
                        'Departure Date': departureDate,
                        'Complete By Date': completeByDate,
                        'Completion Date': completionDate,
                        'Services': services,
                        'Retainers': retainers
                    })

                processed += 1
                
                # update progress occasionally
                if processed % 2000 == 0 or processed == total:
                    pct = int(processed * 100 / max(total, 1))
                    ExportJob.objects.filter(pk=ej.pk).update(progress=pct)

        # Build outer zip filename
        filename = f"jobs_{datetime.datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.zip"

        # Derive inner filename (strip .zip, add .csv)
        base_name = filename.rsplit(".", 1)[0]   # "jobs_2025-08-18_12-34-56"
        inner_filename = f"{base_name}.csv"      # "jobs_2025-08-18_12-34-56.csv"

        # ZIP it in-memory
        zip_bytes = io.BytesIO()
        with zipfile.ZipFile(zip_bytes, mode="w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr(inner_filename, csv_buffer.getvalue())
        zip_bytes.seek(0)

        # Save to DB
        with transaction.atomic():
            ej = ExportJob.objects.select_for_update().get(pk=export_id)
            ej.file_bytes = zip_bytes.getvalue()
            ej.filename = filename
            ej.status = ExportJob.Status.SUCCEEDED
            ej.finished_at = timezone.now()
            ej.progress = 100
            ej.save(update_fields=["file_bytes","filename","status","finished_at","progress"])

        # Notify user via email
        if user.email:
            EmailNotificationService().send_export_job_completed_notification(exportJob=ej)


    except Exception as e:
        with transaction.atomic():
            ej = ExportJob.objects.select_for_update().get(pk=export_id)
            ej.status = ExportJob.Status.FAILED
            ej.error_message = str(e)
            ej.finished_at = timezone.now()
            ej.save(update_fields=["status","error_message","finished_at"])
        raise