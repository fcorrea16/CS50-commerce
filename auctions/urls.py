from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('<int:listing_id>', views.listing, name="listing"),
    path('listings', views.listings, name="listings"),
    path('add', views.add, name="add"),
    path('watchlist', views.watchlist, name="watchlist"),
    path('bid', views.bid, name="bid"),
    path('categories', views.categories, name="categories"),
    path('comment', views.comment, name="comment"),
    path('categories/<int:category_id>', views.category, name="category"),
    path('user/<int:user_id>', views.user, name="user")
]
