
from django.db import models


class ShopProfile(models.Model):
    shop_name = models.CharField(max_length=150)
    owner_name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    gstin = models.CharField(max_length=15, blank=True)
    state_code = models.CharField(max_length=2)

    def __str__(self):
        return self.shop_name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product(models.Model):

    UNIT_CHOICES = [
        ("pcs", "Pieces"),
        ("kg", "Kilogram"),
        ("g", "Gram"),
        ("litre", "Litre"),
        ("ml", "Millilitre"),
    ]

    name = models.CharField(max_length=150)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    barcode = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0
    )
    
    minimum_stock_level = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=5,
        help_text="Minimum stock quantity alert level"
    )

    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default="pcs"
    )

    gst_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Bill(models.Model):

    PAYMENT_CHOICES = [
        ("cash", "Cash"),
        ("upi", "UPI"),
        ("card", "Card"),
    ]
    
    customer = models.ForeignKey(
        "Customer",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="bills"
    )

    invoice_number = models.CharField(
        max_length=30,
        unique=True
    )

    customer_name = models.CharField(
        max_length=150,
        blank=True
    )

    customer_phone = models.CharField(
        max_length=15,
        blank=True
    )

    customer_gstin = models.CharField(
        max_length=15,
        blank=True
    )

    place_of_supply = models.CharField(max_length=2)

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    cgst_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    sgst_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    igst_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    grand_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    due_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    PAYMENT_STATUS_CHOICES = [
        ("paid", "Paid"),
        ("partial", "Partial"),
        ("unpaid", "Unpaid"),
    ]

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default="paid"
    )

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
        default="cash"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_number


class Payment(models.Model):

    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("upi", "UPI"),
        ("card", "Card"),
    ]

    bill = models.ForeignKey(
        Bill,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        default="cash"
    )

    reference = models.CharField(
        max_length=100,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    payment_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.bill.invoice_number} - ₹{self.amount}"


class BillItem(models.Model):

    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    # Product details snapshot
    product_name = models.CharField(max_length=150)

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    gst_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    taxable_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    cgst_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    sgst_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    igst_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.product_name} - {self.bill.invoice_number}"


class StockMovement(models.Model):

    MOVEMENT_CHOICES = [
        ("IN", "Stock In"),
        ("OUT", "Stock Out"),
    ]

    REASON_CHOICES = [
        ("purchase", "New Purchase"),
        ("damaged", "Damaged Stock"),
        ("expired", "Expired Stock"),
        ("adjustment", "Manual Adjustment"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="stock_movements"
    )

    movement_type = models.CharField(
        max_length=3,
        choices=MOVEMENT_CHOICES
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3
    )

    reference = models.CharField(
        max_length=100,
        blank=True
    )
    
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        default="purchase"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.movement_type}"



class Customer(models.Model):

    name = models.CharField(max_length=150)

    phone = models.CharField(max_length=15)

    address = models.TextField(blank=True)

    gstin = models.CharField(max_length=15, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"
    
    

class Expense(models.Model):

    CATEGORY_CHOICES = [
        ("rent", "Shop Rent"),
        ("electricity", "Electricity Bill"),
        ("salary", "Staff Salary"),
        ("transport", "Transport"),
        ("internet", "Internet Bill"),
        ("maintenance", "Maintenance"),
        ("purchase", "Other Purchase"),
        ("other", "Other"),
    ]

    PAYMENT_CHOICES = [
        ("cash", "Cash"),
        ("upi", "UPI"),
        ("card", "Card"),
        ("bank", "Bank Transfer"),
    ]

    title = models.CharField(max_length=150)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
        default="cash"
    )

    expense_date = models.DateField()

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

