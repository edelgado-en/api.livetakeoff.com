from django.urls import path

from inventory.views import (
    ItemFormInfoView,
    CreateItemView,
    InventoryListView,
    ItemLookupView
)

urlpatterns = [
    path('items/form-info', ItemFormInfoView.as_view()),
    path('items/create', CreateItemView.as_view()),
    path('items/list', InventoryListView.as_view()),
    path('items/<str:name>/', ItemLookupView.as_view()),
]