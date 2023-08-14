from django.urls import path

from inventory.views import (
    ItemFormInfoView,
    CreateItemView,
    InventoryListView,
    ItemLookupView,
    LocationsView,
    LocationItemView,
    LocationUserView
)

urlpatterns = [
    path('items/form-info', ItemFormInfoView.as_view()),
    path('items/create', CreateItemView.as_view()),
    path('items/list', InventoryListView.as_view()),
    path('items/<str:name>/', ItemLookupView.as_view()),
    path('locations/list', LocationsView.as_view()),
    path('location-items/<int:id>/', LocationItemView.as_view()),
    path('location-users/<int:id>/', LocationUserView.as_view()),
]