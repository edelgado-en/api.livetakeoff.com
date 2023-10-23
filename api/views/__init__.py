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