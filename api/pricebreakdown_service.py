
from api.models import (
    PriceListEntries,
    CustomerDiscount,
    Job
)

class PriceBreakdownService():

    def get_price_breakdown(self, job: Job):
        # get aircraftType name
        aircraftType = job.aircraftType

        # get priceListType name
        priceListType = job.customer.customer_settings.price_list

        # calculate price
        services_price = 0

        # get services with their corresponding prices based on aircraftType
        assigned_services = []
        services = []

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
        
        # calculate total price discounts first, then additional fees
        total_price = services_price

        # iterate through discounts and calculate the actual amount for each discount that is a percentage using the total_price.
        # For example: if a discount is 10% and the total_price is 100, then the discount_dollar_amount is 10.
        # add a new field called discount_dollar_amount to the discount dictionary if the entry is a percentage
        # Do not change total_price in this loop. We just want to calculate the discount_dollar_amount for each discount that is a percentage
        if total_price > 0:
            for discount in discounts:
                if discount['isPercentage']:
                    discount['discount_dollar_amount'] = total_price * discount['discount'] / 100
                else:
                    discount['discount_dollar_amount'] = discount['discount']
            

        if total_price > 0:
            for discount in discounts:
                if discount['isPercentage']:
                    total_price -= total_price * discount['discount'] / 100
                else:
                    total_price -= discount['discount']

            # iterate through additional_fees and calculate the actual amount for each additional_fee that is a percentage using the total_price.
            # For example: if an additional_fee is 10% and the total_price is 100, then the additional_fee_dollar_amount is 10.
            # add a new field called additional_fee_dollar_amount to the additional_fee dictionary if the entry is a percentage
            # Do not change total_price in this loop. We just want to calculate the additional_fee_dollar_amount for each additional_fee that is a percentage
            for additional_fee in additional_fees:
                if additional_fee['isPercentage']:
                    additional_fee['additional_fee_dollar_amount'] = total_price * additional_fee['fee'] / 100
                else:
                    additional_fee['additional_fee_dollar_amount'] = additional_fee['fee']

        discounted_price = total_price

        for additional_fee in additional_fees:
            if additional_fee['isPercentage']:
                if additional_fee['fee'] > 0:
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
    
