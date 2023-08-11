from django.urls import path

from inventory.views import (
    ItemFormInfoView
)

urlpatterns = [
    path('items/form-info', ItemFormInfoView.as_view()),

]