from django.urls import path
from . import views

urlpatterns = [
    path("", views.auth_gateway, name="auth_gateway"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),

    path("hub/", views.hub, name="hub"),
    path("vendor/<slug:slug>/", views.vendor_detail, name="vendor_detail"),
    path("vendor/<slug:vendor_slug>/<str:category_name>/", views.product_list, name="product_list"),

    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:item_id>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("ticket/<str:ticket_number>/", views.ticket, name="ticket"),

    path("admin-panel/", views.admin_panel, name="admin_panel"),
    path("ticket-center/", views.ticket_center, name="ticket_center"),
    path("ticket-center/scan/", views.scan_ticket, name="scan_ticket"),
]
