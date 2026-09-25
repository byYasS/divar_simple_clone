from django.urls import path
from . import views


app_name = "listing"

urlpatterns = [
    path('listings/', views.listing_page, name="list_page"),
    path("listings/<int:id>/", views.listing_detail, name="detail_page"),
    path("listings/<int:id>/bookmark/", views.toggle_bookmark, name="toggle_bookmark"),
    path('listings/search/', views.search_listing, name="search"),
    path("listings/create/", views.create_listing, name="create_listing"),
    path("listings/update/<int:id>/", views.update_listing, name="update_listing"),
    path("listings/delete/<int:id>/", views.delete_listing, name="delete_listing"),
    
]