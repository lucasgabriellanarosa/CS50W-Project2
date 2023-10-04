from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing_page/<int:id>", views.listing_page, name="listing_page"),
    path("new_listing", views.new_listing, name="new_listing"),
    path('categories_page', views.categories_page, name='categories_page'),
    path('category_page/<int:id>', views.category_page, name='category_page'),
    path('close_action/<int:id>', views.close_action, name='close_action'),
    path('watchlist', views.watchlist, name='watchlist'),
    path('add_to_watchlist/<int:id>', views.add_to_watchlist, name='add_to_watchlist'),
    path('remove_from_watchlist/<int:id>', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('add_comment/<int:id>', views.add_comment, name='add_comment'),
    path('add_bid/<int:id>', views.add_bid, name='add_bid'),
]
