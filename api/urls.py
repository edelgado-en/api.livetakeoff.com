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
        SharedJobEstimateDetailView
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
    path('jobs/price-breakdown/<int:id>/', JobPriceBreakdownView.as_view()),
    path('jobs/<int:id>/', JobDetail.as_view()),
    path('jobs/basic/<int:id>/', JobDetailBasicView.as_view()),
    path('jobs/edit/<int:id>/', EditJobView.as_view()),
    path('jobs/stats/<int:id>/', JobStatsView.as_view()),
    path('jobs/services/<int:id>/', JobServiceAssignmentView.as_view()),
    path('jobs/retainer-services/<int:id>/', JobRetainerServiceAssignmentView.as_view()),
    path('jobs/activity/<int:jobid>/', JobActivityView.as_view()),
    path('job-photos/<int:jobid>/', JobPhotosView.as_view()),
    path('job-photos/delete/<int:jobid>/', JobPhotosView.as_view()),
    path('job-photos/upload/<int:jobid>/', JobPhotosUploadView.as_view()),
    path('job-comments/<int:jobid>/', JobCommentView.as_view()),
    path('services', ServicesView.as_view()),
    path('retainer-services', RetainerServicesView.as_view()),
    path('airports', AirportsView.as_view()),
    path('aircraft-types', AircraftTypesView.as_view()),
    path('tail-aircraft-lookup/<str:tailnumber>/', TailAircraftLookupView.as_view()),
    path('fbos', FBOsView.as_view()),
    path('pricing-plans', PricePlansView.as_view()),
    path('pricing-plans/<int:id>/', PricePlansView.as_view()),
    path('price-listing/<int:id>/', PriceListingView.as_view()),
    path('customers', CustomersView.as_view()),
    path('customers/create', CreateCustomerView.as_view()),
    path('customers/users', CustomerUsersView.as_view()),
    path('customers/<int:id>/', CustomerDetail.as_view()),
    path('customers/settings/<int:id>/', CustomerSettingsView.as_view()),
    path('customers/discounts/<int:id>/', CustomerDiscountView.as_view()),
    path('customers/discounts/update/<int:id>/', CustomerDiscountUpdateView.as_view()),
    path('customers/fees/<int:id>/', CustomerFeesView.as_view()),
    path('customers/fees/update/<int:id>/', CustomerFeeUpdateView.as_view()),
    path('users/me', UserView.as_view()),
    path('users/me/avatar', UserAvatarView.as_view()),
    path('users/me/reset-password', UserResetPasswordView.as_view()),
    path('users/signup', UserSignupView.as_view()),
    
    path('shared/jobs/<str:encoded_id>/', SharedJobDetailView.as_view()),
    path('shared/contact', ContactView.as_view()),
    path('shared/estimates/<str:encoded_id>/', SharedJobEstimateDetailView.as_view()),

    path('customers/activities', CustomerActivityView.as_view()),
    path('estimates/create', CreateEstimateView.as_view()),
    path('estimates', JobEstimateView.as_view()),
    path('estimates/details/<int:id>/', JobEstimateDetailView.as_view()),
    path('estimates/form-info', JobEstimateFormInfoView.as_view()),
]