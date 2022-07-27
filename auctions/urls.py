from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

# URL Paths the user can go to which take Python functions into account when rendering or returning anything
urlpatterns = [
    # Home
    path("", views.index, name="index"),
    
    # Login & Registration
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # Create a New Listing
    path("auction/new", views.create_listing, name="create_listing"),

    # Active Listing Pages
    path("auction/active", views.active_listings, name="active_listings"),
    # <int:cat_id> accepts a value to be passed into the CleanURL that helps populate the Django HTML on the target page
    path("auction/active/<int:cat_id>", views.active_listings, name="active_listings"),

    # Categories
    path("categories", views.categories, name="categories"),
    path("auction/category/<int:cat_id>", views.category_list, name="category_list"),

    # Listing Page
    path("auction/listing/<int:listing_id>", views.listing, name="listing"),
    path("auction/listing/<int:listing_id>/bid", views.take_bid, name="take_bid"),
    path("auction/watchlist", views.watchlist, name="watchlist"),
    path("auction/watchlist/<int:listing_id>/switch/<str:reverse_method>", views.watchlist_switch, name="watchlist_switch"),
    path("auction/listing/<int:listing_id>/comment", views.comment, name="comment"),
    path("auction/listing/<int:listing_id>/close", views.close_listing, name="close_listing")
]

