from .jobs import JobListView
from .user import UserView
from .users import UsersView
from .job_detail import JobDetail
from .job_service_assignment import (
    JobServiceAssignmentView
    )
from .job_retainer_service_assignment import JobRetainerServiceAssignmentView
from .job_photos import JobPhotosView
from .job_photos_upload import JobPhotosUploadView
from .user_avatar import UserAvatarView
from .user_reset_password import UserResetPasswordView
from .job_comment import JobCommentView
from .job_stats import JobStatsView
from .job_form_info import JobFormInfoView
from .create_job import CreateJobView
from .edit_job import EditJobView
from .services import ServicesView
from .job_detail_basic import JobDetailBasicView
from .customers import CustomersView
from .customer_detail import CustomerDetail
from .customer_settings import CustomerSettingsView
from .customer_discounts import CustomerDiscountView
from .airports import AirportsView
from .customer_discount_update import CustomerDiscountUpdateView
from .customer_fees import CustomerFeesView
from .fbos import FBOsView
from .customer_fee_update import CustomerFeeUpdateView
from .price_plans import PricePlansView
from .customer_users import CustomerUsersView
from .create_customer import CreateCustomerView
from .retainer_services import RetainerServicesView
from .completed_jobs import CompletedJobsListView
from .job_closeout import JobCloseoutView
from .job_export import JobExportCSVView
from .job_price_breakdown import JobPriceBreakdownView
from .job_activity import JobActivityView
from .job_complete_check import JobCompleteCheck
from .aircraft_types import AircraftTypesView
from .price_listing import PriceListingView
from .tail_aircraft_lookup import TailAircraftLookupView
from .user_signup import UserSignupView
from .shared_job_detail import SharedJobDetailView
from .contact import ContactView
from .customer_activity import CustomerActivityView
from .job_estimate import JobEstimateView
from .create_estimate import CreateEstimateView
from .job_estimate_detail import JobEstimateDetailView
from .job_estimate_form_info import JobEstimateFormInfoView
from .shared_job_estimate_detail import SharedJobEstimateDetailView
from .tail_stats import TailStatsView
from .tail_stats_detail import TailStatsDetailView
from .services_by_airport import ServiceByAirportView
from .customer_retainers import CustomerRetainersView
from .team_productivity import TeamProductivityView
from .user_productivity import UserProductivityView
from .premium_contact import PremiumContactView
from .user_detail import UserDetailView
from .user_available_airports import UserAvailableAirportsView
from .forgot_password import ForgotPasswordView
from .tail_alert import TailAlertsView
from .create_tail_alert import CreateTailAlertView
from .tail_alert_lookup import TailAlertLookupView
from .tags import TagListView
from .job_return import JobReturnView
from .fbo_search import FboSearchView
from .airport_detail import AirportDetailView
from .airport_available_fbos import AirportAvailableFbosView
from .service_report import ServiceReportView
from .service_activities import ServiceActivityListView
from .retainer_services_activities import RetainerServiceActivityListView
from .retainer_service_report import RetainerServiceReportView
from .create_airport import CreateAirportView
from .tail_service_history import TailServiceHistoryListView
from .tail_open_job_lookup import TailOpenJobLookupView
from .user_email import UserEmailView
from .job_file_upload import JobFileUploadView
from .job_file import JobFileView
from .user_customers import UserCustomersView
from .tail_note_lookup import TailNoteLookupView
from .job_total_labor_time import JobTotalLaborTimeDetail
from .job_schedules import JobScheduleListView
from .create_job_schedule import CreateJobScheduleView
from .job_schedule_detail import JobScheduleDetailView
from .customer_retainers_services import CustomerRetainersServicesView
from .customer_available_service import CustomerAvailableServiceView
from .customer_available_retainer import CustomerAvailableRetainerView
from .user_job_email import UserJobEmailView
from .vendors import VendorsView
from .job_invoice_details import JobInvoiceDetailsView
from .airport_available_users import AirportAvailableUsersView
from .airport_customer_fees import AirportCustomerFeesView
from .fbo_customer_fees import FBOCustomerFeesView
from .shared_job_confirm import SharedJobConfirmView
from .job_accept import JobAcceptView
from .shared_job_accept import SharedJobAcceptView
from .shared_job_return import SharedJobReturnView
from .create_fbo import CreateFBOView
from .remove_airport_available_user import RemoveAirportAvailableUsersView
from .price_list_export import PriceListExportView
from .price_list_entries import PriceListEntriesView
from .price_listing_by_service import PriceListingByServiceView
from .create_help_file import CreateHelpFileView
from .help_files import HelpFileListView
from .users_productivity import UsersProductivityView
from .apply_fee_changes import ApplyFeeChangesView
from .vendor_detail import VendorDetailView
from .create_vendor import CreateVendorView
from .vendor_file_upload import VendorFileUploadView
from .vendor_files import VendorFilesView
from .price_plan_details import PricePlanDetailView
from .price_list_mappings import PriceListMappingsView
from .price_list_available_vendors import PriceListAvailableVendorsView
from .prices_listing import PricesListingView
from .prices_listing_by_service import PricesListingByServiceView