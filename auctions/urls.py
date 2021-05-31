from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("inactive", views.inactive, name="inactive"),
    path("newlisting", views.newlisting, name="newlisting"),
    path("showwatchlist", views.showwatchlist, name="showwatchlist"),
    path("showcategories", views.showcategories, name="showcategories"),
    path("listing/<int:listingid>", views.listing, name="listing"),
    path("watchlist/<int:listingid>", views.watchlist, name="watchlist"),
    path("bid/<int:listingid>", views.bid, name="bid"),
    path("closelisting/<int:listingid>", views.closelisting, name="closelisting"),
    path("comment/<int:listingid>", views.comment, name="comment"),
    path("showlistingbycat/<str:category>", views.showlistingbycat, name="showlistingbycat"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
