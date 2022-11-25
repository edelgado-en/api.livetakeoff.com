
from api.models import (
    PriceListEntries,
    CustomerDiscount,
    Job,
    JobEstimate,
    JobEstimateDiscount,
    JobServiceEstimate,
    JobEstimateAdditionalFee)

class PriceBreakdownService():

    def get_price_breakdown(self, job: Job):
        # get aircraftType name
        aircraftType = job.aircraftType

        # get priceListType name
        priceListType = job.customer.customer_settings.price_list

        # calculate price
        services_price = 0

        # if there is an estimate for this job, get the discounts and additional fees and their prices from the estimate instead
        try:
            job_estimate = JobEstimate.objects.get(job=job)
        except JobEstimate.DoesNotExist:
            job_estimate = None

        # get services with their corresponding prices based on aircraftType
        assigned_services = []
        services = []
        # if there is an estimate for this job, get the services and their prices from the JobServiceEstimate. The JobEstimate already has the services_price value
        if job_estimate:
            job_service_estimates = JobServiceEstimate.objects.filter(job_estimate=job_estimate)
            for job_service_estimate in job_service_estimates:
                services.append(job_service_estimate.service)
                
                assigned_services.append({'id': job_service_estimate.service.id, 'name': job_service_estimate.service.name,
                                 'price': job_service_estimate.price})

                services_price += job_service_estimate.price

        else:
            for job_service_assignment in job.job_service_assignments.all():
                service = job_service_assignment.service
                services.append(service)
                
                try:
                    price = PriceListEntries.objects.get(aircraft_type=aircraftType,
                                                        price_list=priceListType, service=service).price
                    
                    services_price += price

                except PriceListEntries.DoesNotExist:
                    price = 0

                assigned_services.append({'id': service.id,
                                        'name': service.name,
                                        'price': price})
        
         # do all services have a price?
        all_services_have_price = True
        for service in assigned_services:
            if service['price'] == 0:
                all_services_have_price = False
                break


        discounts = []
        additional_fees = []

        if job_estimate:
            job_estimate_discounts = JobEstimateDiscount.objects.filter(job_estimate=job_estimate)
            job_estimate_additional_fees = JobEstimateAdditionalFee.objects.filter(job_estimate=job_estimate)

            for discount in job_estimate_discounts:
                discounts.append({'id': discount.id, 'name': discount.type,
                                  'discount': discount.amount, 'isPercentage': discount.percentage})

            for additional_fee in job_estimate_additional_fees:
                additional_fees.append({'id': additional_fee.id, 'name': additional_fee.type,
                                        'fee': additional_fee.amount, 'isPercentage': additional_fee.percentage})
        
        else:
            customer_discounts = CustomerDiscount.objects \
                                        .prefetch_related('services') \
                                        .prefetch_related('airports') \
                                        .filter(customer_setting=job.customer.customer_settings)

            # we only include the discounts that apply to this job based on discount type
            for customer_discount in customer_discounts:
                if customer_discount.type == 'G':
                    discounts.append({'id': customer_discount.id, 'name': customer_discount.type,
                                  'discount': customer_discount.discount, 'isPercentage': customer_discount.percentage})
            
                elif customer_discount.type == 'S':
                    for service in customer_discount.services.all():
                        if service.service in services:
                            discounts.append({'id': customer_discount.id, 'name': customer_discount.type,
                                            'discount': customer_discount.discount, 'isPercentage': customer_discount.percentage})
                            break
                
                elif customer_discount.type == 'A':
                    discounted_airports = customer_discount.airports.all()
                    for discounted_airport in discounted_airports:
                        if job.airport == discounted_airport.airport:
                            discounts.append({'id': customer_discount.id, 'name': customer_discount.type,
                                        'discount': customer_discount.discount, 'isPercentage': customer_discount.percentage})
                            break
            

            customer_additional_fees = job.customer.customer_settings.fees.all()
            # we only include the additional fees that apply to this job based on fee type
            for customer_additional_fee in customer_additional_fees:
                # if there are no services, we only apply FIXED additional fees, not percentages
                if all_services_have_price or (not all_services_have_price and not customer_additional_fee.percentage):
                    if customer_additional_fee.type == 'G':
                        additional_fees.append({'id': customer_additional_fee.id, 'name': customer_additional_fee.type,
                                                'fee': customer_additional_fee.fee, 'isPercentage': customer_additional_fee.percentage})
                    
                    elif customer_additional_fee.type == 'F':
                        for fbo in customer_additional_fee.fbos.all():
                            if job.fbo == fbo.fbo:
                                additional_fees.append({'id': customer_additional_fee.id, 'name': customer_additional_fee.type,
                                                        'fee': customer_additional_fee.fee, 'isPercentage': customer_additional_fee.percentage})
                                break

                    elif customer_additional_fee.type == 'A':
                        upcharged_airports = customer_additional_fee.airports.all()
                        for upcharged_airport in upcharged_airports:
                            if job.airport == upcharged_airport.airport:
                                additional_fees.append({'id': customer_additional_fee.id, 'name': customer_additional_fee.type,
                                                    'fee': customer_additional_fee.fee, 'isPercentage': customer_additional_fee.percentage})
                                break

        
        #if there is an estimate for this job, we get the total_price and the discounted_price from the estimate instead
        if job_estimate:
            total_price = job_estimate.total_price
            discounted_price = job_estimate.discounted_price
        
        else:
            # calculate total price discounts first, then additional fees
            total_price = services_price
            
            if total_price > 0:
                for discount in discounts:
                    if discount['isPercentage']:
                        total_price -= total_price * discount['discount'] / 100
                    else:
                        total_price -= discount['discount']

            discounted_price = total_price

            for additional_fee in additional_fees:
                if additional_fee['isPercentage']:
                    total_price += total_price * additional_fee['fee'] / 100
                else:
                    total_price += additional_fee['fee']


        price_breakdown = {
            'aircraftType': aircraftType.name,
            'priceListType': priceListType.name.upper(),
            'services': assigned_services,
            'servicesPrice': f'{services_price:,.2f}',
            'discounts': discounts,
            'discountedPrice': f'{discounted_price:,.2f}',
            'additionalFees': additional_fees,
            'totalPrice': total_price,
            'manuallySet': not job.is_auto_priced
        }

        return price_breakdown