from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import uuid

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(
        max_length=20,
        choices=[
            ("STUDENT", "Student"),
            ("VENDOR", "Vendor"),
            ("EMPLOYEE", "Employee"),
            ("ADMIN", "Admin"),
        ],
        default="STUDENT",
    )

    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = models.CharField(max_length=15, blank=True)

    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    coins = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"





class Vendor(models.Model):

    name = models.CharField(max_length=100)

    slug = models.SlugField(unique=True)

    description = models.TextField()

    venue = models.CharField(max_length=200)

    minimum_price = models.DecimalField(max_digits=10, decimal_places=2)

    maximum_price = models.DecimalField(max_digits=10, decimal_places=2)

    opening_time = models.TimeField()

    closing_time = models.TimeField()

    estimated_wait = models.IntegerField(default=10)

    image = models.ImageField(upload_to="vendors/")

    is_active = models.BooleanField(default=True)

    rating = models.FloatField(default=4.5)

    def __str__(self):
        return self.name




class Category(models.Model):

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="categories",
    )

    name = models.CharField(max_length=50)

    image = models.ImageField(
        upload_to="categories/",
        blank=True,
    )

    def __str__(self):
        return f"{self.vendor.name} - {self.name}"





class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
    )

    name = models.CharField(max_length=100)

    slug = models.SlugField(unique=True)

    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)

    image = models.ImageField(upload_to="products/")

    is_veg = models.BooleanField(default=True)

    preparation_time = models.IntegerField(default=10)

    calories = models.IntegerField(default=0)

    weekly_purchased_count = models.IntegerField(default=0)

    rating = models.FloatField(default=4.5)

    is_popular = models.BooleanField(default=False)

    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def grand_total(self):
        """Calculates the total price of all items in the cart."""
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        # Prevents duplicate products inside the same cart
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart"

    @property
    def total_price(self):
        """Calculates total price for this specific line item."""
        return self.product.price * self.quantity




class Order(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)

    vendor = models.ForeignKey(Vendor,on_delete=models.CASCADE)

    ticket_number = models.CharField(max_length=20,unique=True)

    qr_token = models.UUIDField(default=uuid.uuid4)

    total_amount = models.DecimalField(max_digits=10,decimal_places=2)

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING","Pending"),
            ("PAID","Paid"),
            ("FAILED","Failed"),
        ],
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING","Pending"),
            ("PREPARING","Preparing"),
            ("READY","Ready"),
            ("COMPLETED","Completed"),
        ],
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ticket_number


    


# 8. Order Item
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    # Price is fixed at checkout to prevent future changes if product price changes
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        # Prevents duplicate products in the same order
        unique_together = ("order", "product")

    @property
    def total_price(self):
        """Calculates total price for this specific ordered item."""
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        """Automatically snapshots the product price when creating the order item."""
        if not self.price and self.product:
            self.price = self.product.price
        super().save(*args, **kwargs)


# 9. Reward
class Reward(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True) # Blank allows empty text in forms
    xp_required = models.PositiveIntegerField(default=0) # Prevents negative values
    coins_required = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="rewards/", blank=True, null=True)


# 10. Badge
class Badge(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="badges/", blank=True, null=True)


# 11. User Badge
class UserBadge(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents a user from earning the exact same badge multiple times
        unique_together = ("profile", "badge")


# 12. Achievement
class Achievement(models.Model):
    title = models.CharField(max_length=100, unique=True)
    xp = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)


# 13. Ticket Scan
class TicketScan(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="scans")
    scanned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """Validates that a ticket can only be scanned if the order is paid."""
        # Adjust 'PAID' based on your actual Order status field
        if hasattr(self, 'order') and self.order.status != 'PAID':
            raise ValidationError("Cannot scan a ticket for an unpaid order.")
