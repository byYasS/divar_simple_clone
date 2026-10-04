from django.urls import path
from . import views


app_name = "listing"

urlpatterns = [
    path("", views.listing_page, name="list_page"),
    path("<int:id>/", views.listing_detail, name="detail_page"),
    path("<int:id>/bookmark/", views.toggle_bookmark, name="toggle_bookmark"),
    path("search/", views.search_listing, name="search"),
    path("create/", views.create_listing, name="create_listing"),
    path("update/<int:id>/", views.update_listing, name="update_listing"),
    path("delete/<int:id>/", views.delete_listing, name="delete_listing"),
    path("category/<int:category_id>/", views.category, name="category"),
    
]