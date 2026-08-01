from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Profile, Vendor, Product, Cart, CartItem, Order, OrderItem, TicketScan
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

def auth_gateway(request):
    return render(request, "auth/gateway.html")

def redirect_user_by_role(user):
    """
    Redirect users based on their assigned role.
    """

    if user.is_superuser or user.is_staff:
        return redirect("admin_panel")

    profile = getattr(user, "profile", None)

    if not profile:
        return redirect("hub")

    role = profile.role

    if role == "ADMIN":
        return redirect("admin_panel")

    elif role == "EMPLOYEE":
        return redirect("ticket_center")

    elif role == "VENDOR":
        # Vendor dashboard will be implemented later.
        return redirect("hub")

    return redirect("hub")


def login_view(request):

    if request.user.is_authenticated:
        return redirect_user_by_role(request.user)

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, "auth/login.html")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:
            messages.error(request, "Invalid username or password.")
            return render(request, "auth/login.html")

        if not user.is_active:
            messages.error(request, "This account has been deactivated.")
            return render(request, "auth/login.html")

        login(request, user)

        messages.success(
            request,
            f"Welcome back, {user.username}!"
        )

        return redirect_user_by_role(user)

    return render(request, "auth/login.html")

def signup_view(request):

    if request.user.is_authenticated:
        return redirect_user_by_role(request.user)

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # ----------------------------
        # Required Fields
        # ----------------------------

        if not username or not email or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return render(request, "auth/signup.html")

        # ----------------------------
        # Username
        # ----------------------------

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "auth/signup.html")

        # ----------------------------
        # Email
        # ----------------------------

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, "auth/signup.html")

        # ----------------------------
        # Password Match
        # ----------------------------

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "auth/signup.html")

        # ----------------------------
        # Django Password Validation
        # ----------------------------

        temp_user = User(
            username=username,
            email=email,
        )

        try:
            validate_password(password, temp_user)

        except ValidationError as e:

            for error in e.messages:
                messages.error(request, error)

            return render(request, "auth/signup.html")

        # ----------------------------
        # Create User
        # ----------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        Profile.objects.create(
            user=user,
            role="STUDENT",
        )

        login(request, user)

        messages.success(
            request,
            "Account created successfully. Welcome to ByteBites!"
        )

        return redirect_user_by_role(user)

    return render(request, "auth/signup.html")

@login_required
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("auth_gateway")

@login_required
def hub(request):
    vendors = Vendor.objects.all()
    return render(request, "hub/hub.html", {"vendors": vendors})

@login_required
def vendor_detail(request, slug):
    vendor = get_object_or_404(Vendor, slug=slug)
    if vendor.slug == "campus-kitchen":
        template_name = "vendor/campus-kitchen/campus-kitchen.html"
    elif vendor.slug == "mario":
        template_name = "vendor/mario/mario.html"
    elif vendor.slug == "royal-kitchen":
        template_name = "vendor/royal-kitchen/royal-kitchen.html"
    elif vendor.slug == "tasty-time":
        template_name = "vendor/tasty-time/tasty-time.html"
    else:
        template_name = "vendor/default.html"
    return render(request, template_name, {"vendor": vendor})

@login_required
def product_list(request, vendor_slug, category_name):
    vendor = get_object_or_404(Vendor, slug=vendor_slug)
    products = Product.objects.filter(category__vendor=vendor, category__name=category_name.upper(), is_available=True)
    return render(request, "products/product_list.html", {
        "vendor": vendor,
        "category_name": category_name,
        "products": products,
    })

@login_required
def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    cart, created = Cart.objects.get_or_create(user=request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
    )

    if not created:
        item.quantity += 1
        item.save()

    return redirect(request.META.get("HTTP_REFERER", "hub"))

@login_required
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    items = cart.items.all()

    total = sum(item.total_price for item in items)

    return render(
        request,
        "cart/cart.html",
        {
            "cart": cart,
            "items": items,
            "total": total,
        },
    )

@login_required
def update_cart(request, item_id):

    cart = get_object_or_404(Cart, user=request.user)

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart,
    )

    item.quantity = max(
        1,
        int(request.POST.get("quantity", 1))
    )

    item.save()

    return redirect("cart")



@login_required
def remove_from_cart(request, item_id):

    cart = get_object_or_404(Cart, user=request.user)

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart,
    )

    item.delete()

    return redirect("cart")



@login_required
def checkout(request):

    cart, created = Cart.objects.get_or_create(user=request.user)

    items = cart.items.all()

    if not items.exists():
        return redirect("cart")

    total = sum(item.total_price for item in items)

    ticket_number = (
        f"BB-{timezone.now().strftime('%Y%m%d%H%M%S')}-{request.user.id}"
    )

    order = Order.objects.create(
        user=request.user,
        ticket_number=ticket_number,
        total_amount=total,
    )

    for item in items:

        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price_at_order=item.product.price,
        )

        item.product.weekly_purchased_count += item.quantity
        item.product.save()

    items.delete()

    return redirect("ticket", ticket_number=order.ticket_number)

@login_required
def ticket(request, ticket_number):
    order = get_object_or_404(Order, ticket_number=ticket_number, user=request.user)
    return render(request, "ticket.html", {"order": order})

@login_required
def admin_panel(request):
    profile = getattr(request.user, "profile", None)
    if not (request.user.is_staff or profile and profile.role == "ADMIN"):
        return redirect("hub")
    total_revenue = Order.objects.aggregate(total=Sum("total_amount"))["total"] or 0
    total_orders = Order.objects.count()
    top_products = Product.objects.order_by("-weekly_purchased_count")[:10]
    return render(request, "staff/admin_panel.html", {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "top_products": top_products,
    })

@login_required
def ticket_center(request):
    profile = getattr(request.user, "profile", None)
    if not (profile and profile.role == "EMPLOYEE"):
        return redirect("hub")
    tickets = Order.objects.order_by("-created_at")[:10]
    return render(request, "staff/ticket_center.html", {"tickets": tickets})

@login_required
def scan_ticket(request):
    if request.method == "POST":
        ticket_number = request.POST.get("ticket_number")
        order = get_object_or_404(Order, ticket_number=ticket_number)
        order.status = "COMPLETED"
        order.save()
        TicketScan.objects.create(order=order, scanned_by=request.user)
        messages.success(request, f"{ticket_number} completed successfully.")
    return redirect("ticket_center")
