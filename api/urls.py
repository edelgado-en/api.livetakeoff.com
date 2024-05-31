from django.urls import path
from .views import (
        JobListView,
        UserView,
        JobDetail,
        JobServiceAssignmentView,
        JobRetainerServiceAssignmentView,
        JobPhotosView,
        JobPhotosUploadView,
        UserAvatarView,
        UserResetPasswordView,
        JobCommentView,
        JobStatsView,
        JobFormInfoView,
        CreateJobView,
        EditJobView,
        ServicesView,
        JobDetailBasicView,
        CustomersView,
        CustomerDetail,
        CustomerSettingsView,
        CustomerDiscountView,
        AirportsView,
        CustomerDiscountUpdateView,
        CustomerFeesView,
        FBOsView,
        CustomerFeeUpdateView,
        PricePlansView,
        CustomerUsersView,
        CreateCustomerView,
        RetainerServicesView,
        CompletedJobsListView,
        JobCloseoutView,
        JobExportCSVView,
        JobPriceBreakdownView,
        JobActivityView,
        JobCompleteCheck,
        AircraftTypesView,
        PriceListingView,
        TailAircraftLookupView,
        UserSignupView,
        SharedJobDetailView,
        ContactView,
        CustomerActivityView,
        CreateEstimateView,
        JobEstimateView,
        JobEstimateDetailView,
        JobEstimateFormInfoView,
        SharedJobEstimateDetailView,
        TailStatsView,
        TailStatsDetailView,
        ServiceByAirportView,
        CustomerRetainersView,
        TeamProductivityView,
        UserProductivityView,
        PremiumContactView,
        UsersView,
        UserDetailView,
        UserAvailableAirportsView,
        ForgotPasswordView,
        TailAlertsView,
        CreateTailAlertView,
        TailAlertLookupView,
        TagListView,
        JobReturnView,
        FboSearchView,
        AirportDetailView,
        AirportAvailableFbosView,
        ServiceReportView,
        ServiceActivityListView,
        RetainerServiceActivityListView,
        RetainerServiceReportView,
        CreateAirportView,
        TailServiceHistoryListView,
        TailOpenJobLookupView,
        UserEmailView,
        JobFileUploadView,
        JobFileView,
        UserCustomersView,
        TailNoteLookupView,
        JobTotalLaborTimeDetail,
        JobScheduleListView,
        CreateJobScheduleView,
        JobScheduleDetailView,
        CustomerRetainersServicesView,
        CustomerAvailableServiceView,
        CustomerAvailableRetainerView,
        UserJobEmailView,
        VendorsView,
        JobInvoiceDetailsView,
        AirportAvailableUsersView,
        AirportCustomerFeesView,
        FBOCustomerFeesView,
        SharedJobConfirmView,
        JobAcceptView,
        SharedJobAcceptView,
        SharedJobReturnView,
        CreateFBOView,
        RemoveAirportAvailableUsersView,
        PriceListExportView,
        PriceListEntriesView,
        PriceListingByServiceView
    )

urlpatterns = [
    path('jobs', JobListView.as_view()),
    path('jobs/form-info', JobFormInfoView.as_view()),
    path('jobs/create', CreateJobView.as_view()),
    path('jobs/export', JobExportCSVView.as_view()),
    path('jobs/can-complete/<int:id>/', JobCompleteCheck.as_view()),
    path('jobs/completed', CompletedJobsListView.as_view()),
    path('jobs/completed/<int:id>/', CompletedJobsListView.as_view()),
    path('jobs/closeout/<int:id>/', JobCloseoutView.as_view()),
    path('jobs/return/<int:id>/', JobReturnView.as_view()),
    path('jobs/price-breakdown/<int:id>/', JobPriceBreakdownView.as_view()),
    path('jobs/<int:id>/', JobDetail.as_view()),
    path('jobs/accept/<int:id>/', JobAcceptView.as_view()),
    path('jobs/basic/<int:id>/', JobDetailBasicView.as_view()),
    path('jobs/edit/<int:id>/', EditJobView.as_view()),
    path('jobs/stats/<int:id>/', JobStatsView.as_view()),
    path('jobs/services/<int:id>/', JobServiceAssignmentView.as_view()),
    path('jobs/retainer-services/<int:id>/', JobRetainerServiceAssignmentView.as_view()),
    path('jobs/activity/<int:jobid>/', JobActivityView.as_view()),
    path('job-photos/<int:jobid>/', JobPhotosView.as_view()),
    path('job-photos/delete/<int:jobid>/', JobPhotosView.as_view()),
    path('job-photos/upload/<int:jobid>/', JobPhotosUploadView.as_view()),
    path('job-files/upload/<int:jobid>/', JobFileUploadView.as_view()),
    path('job-files/<int:id>/', JobFileView.as_view()),
    path('jobs/schedules', JobScheduleListView.as_view()),
    path('jobs/schedules/create', CreateJobScheduleView.as_view()),

    path('jobs/schedules/<int:id>/', JobScheduleDetailView.as_view()),

    path('jobs/invoice-details/<int:id>/', JobInvoiceDetailsView.as_view()),

    path('job-comments/<int:jobid>/', JobCommentView.as_view()),
    path('services', ServicesView.as_view()),
    path('retainer-services', RetainerServicesView.as_view()),
    path('airports', AirportsView.as_view()),
    path('airports/<int:id>/', AirportDetailView.as_view()),
    path('aircraft-types', AircraftTypesView.as_view()),

    path('airports/available-users/<int:id>/', AirportAvailableUsersView.as_view()),
    path('airports/available-users', AirportAvailableUsersView.as_view()),
    path('airports/remove-available-users', RemoveAirportAvailableUsersView.as_view()),

    path('airports/customer-fees', AirportCustomerFeesView.as_view()),

    path('fbos/customer-fees', FBOCustomerFeesView.as_view()),

    path('vendors', VendorsView.as_view()),

    path('service-report', ServiceReportView.as_view()),
    path('retainer-service-report', RetainerServiceReportView.as_view()),
    path('service-activities', ServiceActivityListView.as_view()),
    path('retainer-service-activities', RetainerServiceActivityListView.as_view()),

    path('tail-service-history', TailServiceHistoryListView.as_view()),
    path('tail-aircraft-lookup/<str:tailnumber>/', TailAircraftLookupView.as_view()),
    path('tail-alert-lookup/<str:tailnumber>/', TailAlertLookupView.as_view()),
    path('tail-open-job-lookup/<str:tailnumber>/', TailOpenJobLookupView.as_view()),

    path('tail-note-lookup', TailNoteLookupView.as_view()),

    path('fbos', FBOsView.as_view()),
    path('fbo-search', FboSearchView.as_view()),
    path('pricing-plans', PricePlansView.as_view()),
    path('pricing-plans/<int:id>/', PricePlansView.as_view()),
    path('price-listing/<int:id>/', PriceListingView.as_view()),
    path('price-listing-by-service/<int:id>/', PriceListingByServiceView.as_view()),
    path('price-listing/export', PriceListExportView.as_view()),
    path('price-listing/entries/', PriceListEntriesView.as_view()),
    path('customers', CustomersView.as_view()),
    path('customers/retainers', CustomerRetainersView.as_view()),
    path('customers/create', CreateCustomerView.as_view()),
    path('customers/users', CustomerUsersView.as_view()),
    path('customers/<int:id>/', CustomerDetail.as_view()),
    path('customers/settings/<int:id>/', CustomerSettingsView.as_view()),
    path('customers/discounts/<int:id>/', CustomerDiscountView.as_view()),
    path('customers/discounts/update/<int:id>/', CustomerDiscountUpdateView.as_view()),
    path('customers/fees/<int:id>/', CustomerFeesView.as_view()),
    path('customers/fees/update/<int:id>/', CustomerFeeUpdateView.as_view()),
    path('customers/retainers-services/<int:id>/', CustomerRetainersServicesView.as_view()),
    path('users', UsersView.as_view()),
    path('users/<int:id>/', UserDetailView.as_view()),
    path('users/me', UserView.as_view()),
    path('users/me/avatar', UserAvatarView.as_view()),
    path('users/me/reset-password', UserResetPasswordView.as_view()),
    path('users/signup', UserSignupView.as_view()),
    path('users/available-airports', UserAvailableAirportsView.as_view()),
    path('users/available-airports/<int:id>/', UserAvailableAirportsView.as_view()),
    path('users/customers', UserCustomersView.as_view()),
    path('users/customers/<int:id>/', UserCustomersView.as_view()),

    path('customers/available-services', CustomerAvailableServiceView.as_view()),
    path('customers/available-services/<int:id>/', CustomerAvailableServiceView.as_view()),

    path('customers/available-retainers', CustomerAvailableRetainerView.as_view()),
    path('customers/available-retainers/<int:id>/', CustomerAvailableRetainerView.as_view()),

    path('user-email', UserEmailView.as_view()),
    path('user-email/<int:user_email_id>/', UserEmailView.as_view()),

    path('user-job-email/<int:job_id>/', UserJobEmailView.as_view()),

    path('airports/available-fbos', AirportAvailableFbosView.as_view()),
    path('airports/available-fbos/<int:id>/', AirportAvailableFbosView.as_view()),
    path('airports/create', CreateAirportView.as_view()),

    path('fbos/create', CreateFBOView.as_view()),

    path('shared/jobs/<str:encoded_id>/', SharedJobDetailView.as_view()),
    path('shared/contact', ContactView.as_view()),
    path('shared/estimates/<str:encoded_id>/', SharedJobEstimateDetailView.as_view()),
    path('shared/jobs/confirm/<str:encoded_id>/', SharedJobConfirmView.as_view()),
    path('shared/jobs/accept/<str:encoded_id>/', SharedJobAcceptView.as_view()),
    path('shared/jobs/return/<str:encoded_id>/', SharedJobReturnView.as_view()),

    path('customers/activities', CustomerActivityView.as_view()),
    path('estimates/create', CreateEstimateView.as_view()),
    path('estimates', JobEstimateView.as_view()),
    path('estimates/<int:id>/', JobEstimateView.as_view()),
    path('estimates/details/<int:id>/', JobEstimateDetailView.as_view()),
    path('estimates/form-info', JobEstimateFormInfoView.as_view()),

    path('tail-stats', TailStatsView.as_view()),
    path('tail-stats/<str:tail_number>/', TailStatsDetailView.as_view()),

    path('services-by-airport', ServiceByAirportView.as_view()),
    path('team-productivity', TeamProductivityView.as_view()),
    path('user-productivity/<int:id>/', UserProductivityView.as_view()),
    path('premium/contact', PremiumContactView.as_view()),

    path('forgot-password', ForgotPasswordView.as_view()),

    path('tail-alerts', TailAlertsView.as_view()),
    path('tail-alerts/<int:id>/', TailAlertsView.as_view()),
    path('create-tail-alert', CreateTailAlertView.as_view()),

    path('tags', TagListView.as_view()),
    
    path('jobs/total-labor-time', JobTotalLaborTimeDetail.as_view()),
]