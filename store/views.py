from django.shortcuts import render
from .models import (
    Product,
    Category,
    Bill,
    BillItem,
    StockMovement,
    ShopProfile,
    Payment,
)

from .models import Expense
from .forms import ExpenseForm
from datetime import datetime
from django.utils import timezone
from django.db.models import Sum, Count
from .forms import StockMovementForm
from django.db import transaction
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.shortcuts import redirect

from django.db import models
from django.contrib import messages
from .forms import ProductForm, CategoryForm
from django.http import JsonResponse

import json
import uuid

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from django.db.models import Sum



def dashboard(request):
    from django.db.models import Sum, F, ExpressionWrapper, DecimalField
    from decimal import Decimal
    from django.utils import timezone

    today = timezone.localdate()

    # Existing Statistics
    total_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()
    total_bills = Bill.objects.count()

    # Today's Sales
    today_sales = Bill.objects.filter(
        created_at__date=today
    ).aggregate(
        total=Sum("grand_total")
    )["total"] or Decimal("0.00")

    # Today's Expenses
    today_expenses = Expense.objects.filter(
        expense_date=today
    ).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    # Today's Gross Profit
    profit_expression = ExpressionWrapper(
        (F("unit_price") - F("purchase_price")) * F("quantity"),
        output_field=DecimalField(max_digits=14, decimal_places=2)
    )

    today_gross_profit = BillItem.objects.filter(
        bill__created_at__date=today,
        purchase_price__gt=0
    ).aggregate(
        total=Sum(profit_expression)
    )["total"] or Decimal("0.00")

    # Estimated Profit After Expenses
    today_profit = today_gross_profit - today_expenses

    # Total Stock Value
    active_products = Product.objects.filter(is_active=True)

    total_stock_value = sum(
        (
            product.purchase_price * product.stock_quantity
            for product in active_products
        ),
        Decimal("0.00")
    )

    context = {
        "total_products": total_products,
        "total_categories": total_categories,
        "total_bills": total_bills,
        "today_sales": today_sales,
        "today_expenses": today_expenses,
        "today_profit": today_profit,
        "total_stock_value": total_stock_value,
    }

    return render(request, "dashboard/index.html", context)


from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Bill


def product_list(request):
    products = Product.objects.select_related("category").all()

    search = request.GET.get("search", "")
    category_id = request.GET.get("category", "")

    if search:
        products = products.filter(name__icontains=search)

    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()

    context = {
        "products": products,
        "categories": categories,
        "search": search,
        "selected_category": category_id,
    }

    return render(request, "products/product_list.html", context)


def add_product(request):

    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Product added successfully!"
            )

            return redirect("product_list")

    else:
        form = ProductForm()

    context = {
        "form": form,
    }

    return render(
        request,
        "products/product_form.html",
        context
    )



def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "products/product_form.html",
        {"form": form, "is_edit": True, "product": product}
    )


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product_name = product.name
        product.delete()

        messages.success(
            request,
            f"{product_name} deleted successfully!"
        )

    return redirect("product_list")


def category_list(request):
    categories = Category.objects.all().order_by("name")

    search = request.GET.get("search", "")

    if search:
        categories = categories.filter(name__icontains=search)

    context = {
        "categories": categories,
        "search": search,
    }

    return render(
        request,
        "categories/category_list.html",
        context
    )
    

def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully!")
            return redirect("category_list")
    else:
        form = CategoryForm()

    return render(
        request,
        "categories/category_form.html",
        {"form": form}
    )


def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect("category_list")
    else:
        form = CategoryForm(instance=category)

    return render(
        request,
        "categories/category_form.html",
        {"form": form, "is_edit": True}
    )


def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        try:
            category.delete()
            messages.success(request, "Category deleted successfully!")
        except models.ProtectedError:
            messages.error(
                request,
                "This category contains products and cannot be deleted."
            )

    return redirect("category_list")

def toggle_product_status(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.is_active = not product.is_active
        product.save(update_fields=["is_active"])

        status = "activated" if product.is_active else "deactivated"

        messages.success(
            request,
            f"{product.name} has been {status} successfully."
        )

    return redirect("product_list")


def toggle_category_status(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        category.is_active = not category.is_active
        category.save(update_fields=["is_active"])

        status = "activated" if category.is_active else "deactivated"

        messages.success(
            request,
            f"{category.name} has been {status} successfully."
        )

    return redirect("category_list")



def billing_product_search(request):

    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()

    try:
        page = max(int(request.GET.get("page", 1)), 1)
    except (ValueError, TypeError):
        page = 1

    page_size = 10

    products = Product.objects.filter(
        is_active=True,
        category__is_active=True
    ).select_related("category")

    if query:
        products = products.filter(name__icontains=query)

    if category_id:
        products = products.filter(category_id=category_id)

    products = products.order_by("name")

    total_count = products.count()

    start = (page - 1) * page_size
    end = start + page_size

    page_products = products[start:end]

    data = []

    for product in page_products:
        data.append({
            "id": product.id,
            "name": product.name,
            "category": product.category.name,
            "category_id": product.category_id,
            "selling_price": str(product.selling_price),
            "stock_quantity": str(product.stock_quantity),
            "unit": product.get_unit_display(),
            "gst_rate": str(product.gst_rate),
        })

    return JsonResponse({
        "success": True,
        "count": len(data),
        "total_count": total_count,
        "current_page": page,
        "total_pages": (total_count + page_size - 1) // page_size,
        "has_next": end < total_count,
        "has_previous": page > 1,
        "products": data,
    })


def billing_page(request):
    categories = Category.objects.filter(
        is_active=True
    ).order_by("name")

    return render(request, "billing/billing_page.html", {
        "categories": categories
    })

def round_money(value):
    return Decimal(value).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


@require_POST
def generate_bill(request):

    try:
        payload = json.loads(request.body)

        items = payload.get("items", [])
        customer_name = payload.get("customer_name", "").strip()
        customer_phone = payload.get("customer_phone", "").strip()
        customer_gstin = payload.get("customer_gstin", "").strip()
        place_of_supply = payload.get("place_of_supply", "").strip()
        payment_method = payload.get("payment_method", "cash")

        if not items:
            return JsonResponse({
                "success": False,
                "message": "Cart is empty."
            }, status=400)

        if not place_of_supply.isdigit() or len(place_of_supply) != 2:
            return JsonResponse({
                "success": False,
                "message": "Invalid State Code."
            }, status=400)

        if payment_method not in ["cash", "upi", "card"]:
            return JsonResponse({
                "success": False,
                "message": "Invalid payment method."
            }, status=400)

        with transaction.atomic():

            shop = ShopProfile.objects.first()

            if not shop:
                return JsonResponse({
                    "success": False,
                    "message": "Shop profile not configured."
                }, status=400)

            shop_state = str(shop.state_code).zfill(2)

            subtotal = Decimal("0.00")
            cgst_total = Decimal("0.00")
            sgst_total = Decimal("0.00")
            igst_total = Decimal("0.00")

            bill_lines = []
            seen_product_ids = set()

            for item in items:

                product_id = item.get("product_id")

                if product_id in seen_product_ids:
                    raise ValueError("Duplicate product in cart.")

                seen_product_ids.add(product_id)

                try:
                    quantity = Decimal(str(item.get("quantity")))
                except (InvalidOperation, TypeError):
                    raise ValueError("Invalid product quantity.")

                if not quantity.is_finite() or quantity <= 0:
                    raise ValueError("Quantity must be greater than zero.")

                product = Product.objects.select_for_update().filter(
                    id=product_id,
                    is_active=True,
                    category__is_active=True
                ).first()

                if not product:
                    raise ValueError("Product is unavailable.")

                if quantity > product.stock_quantity:
                    raise ValueError(
                        f"Insufficient stock for {product.name}."
                    )

                # Always use database price and GST.
                price = Decimal(str(product.selling_price))
                gst_rate = Decimal(str(product.gst_rate))

                taxable_amount = round_money(price * quantity)
                tax_amount = round_money(
                    taxable_amount * gst_rate / Decimal("100")
                )

                if place_of_supply == shop_state:
                    cgst = round_money(tax_amount / Decimal("2"))
                    sgst = tax_amount - cgst
                    igst = Decimal("0.00")
                else:
                    cgst = Decimal("0.00")
                    sgst = Decimal("0.00")
                    igst = tax_amount

                total_amount = (
                    taxable_amount + cgst + sgst + igst
                )

                subtotal += taxable_amount
                cgst_total += cgst
                sgst_total += sgst
                igst_total += igst

                bill_lines.append({
                    "product": product,
                    "quantity": quantity,
                    "price": price,
                    "gst_rate": gst_rate,
                    "taxable": taxable_amount,
                    "cgst": cgst,
                    "sgst": sgst,
                    "igst": igst,
                    "total": total_amount,
                })

            subtotal = round_money(subtotal)
            cgst_total = round_money(cgst_total)
            sgst_total = round_money(sgst_total)
            igst_total = round_money(igst_total)

            grand_total = round_money(
                subtotal + cgst_total + sgst_total + igst_total
            )
            
            # PAYMENT CALCULATION

            try:
                paid_amount = Decimal(
                    str(payload.get("paid_amount", grand_total))
                )
            except (InvalidOperation, TypeError):
                raise ValueError("Invalid paid amount.")

            if not paid_amount.is_finite():
                raise ValueError("Invalid paid amount.")

            paid_amount = round_money(paid_amount)

            if paid_amount < 0:
                raise ValueError("Paid amount cannot be negative.")

            if paid_amount > grand_total:
                raise ValueError("Paid amount cannot exceed bill total.")

            due_amount = round_money(
                grand_total - paid_amount
            )

            if due_amount > 0 and (
                not customer_name or not customer_phone
            ):
                raise ValueError(
                    "Customer name and mobile number are required for credit."
                )

            if due_amount == 0:
                payment_status = "paid"
            elif paid_amount > 0:
                payment_status = "partial"
            else:
                payment_status = "unpaid"

            invoice_number = (
                f"INV-{timezone.now():%Y%m%d}-"
                f"{uuid.uuid4().hex[:8].upper()}"
            )
            
            # FIND OR CREATE CUSTOMER

            customer = None

            if customer_name and customer_phone:

                customer = Customer.objects.filter(
                    phone=customer_phone,
                    is_active=True
                ).first()

                if not customer:
                    customer = Customer.objects.create(
                        name=customer_name,
                        phone=customer_phone,
                        gstin=customer_gstin
                    )

            bill = Bill.objects.create(
                customer=customer,
                invoice_number=invoice_number,
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_gstin=customer_gstin,
                place_of_supply=place_of_supply,
                subtotal=subtotal,
                cgst_amount=cgst_total,
                sgst_amount=sgst_total,
                igst_amount=igst_total,
                grand_total=grand_total,
                payment_method=payment_method,
                paid_amount=paid_amount,
                due_amount=due_amount,
                payment_status=payment_status,
            )
            
            if paid_amount > 0:
                Payment.objects.create(
                    bill=bill,
                    amount=paid_amount,
                    payment_method=payment_method,
                    notes="Initial payment during billing"
                )

            for line in bill_lines:

                product = line["product"]
                quantity = line["quantity"]

                BillItem.objects.create(
                    bill=bill,
                    product=product,
                    product_name=product.name,
                    quantity=quantity,
                    unit_price=line["price"],
                    purchase_price=product.purchase_price,
                    gst_rate=line["gst_rate"],
                    taxable_amount=line["taxable"],
                    cgst_amount=line["cgst"],
                    sgst_amount=line["sgst"],
                    igst_amount=line["igst"],
                    total_amount=line["total"],
                )

                product.stock_quantity -= quantity
                product.save(update_fields=["stock_quantity"])

                StockMovement.objects.create(
                    product=product,
                    movement_type="OUT",
                    quantity=quantity,
                    reference=f"Bill {invoice_number}",
                )

        return JsonResponse({
            "success": True,
            "message": "Bill generated successfully.",
            "invoice_number": bill.invoice_number,
            "grand_total": str(bill.grand_total),
            "paid_amount": str(bill.paid_amount),
            "due_amount": str(bill.due_amount),
            "payment_status": bill.payment_status,
        })

    except (ValueError, InvalidOperation, TypeError) as error:
        return JsonResponse({
            "success": False,
            "message": str(error)
        }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid request data."
        }, status=400)


def bills_page(request):
    bills = Bill.objects.all().order_by("-created_at")

    total_sales = bills.aggregate(
        total=Sum("grand_total")
    )["total"] or 0

    total_received = bills.aggregate(
        total=Sum("paid_amount")
    )["total"] or 0

    total_due = bills.aggregate(
        total=Sum("due_amount")
    )["total"] or 0

    pending_bills = bills.exclude(
        payment_status="paid"
    ).count()

    context = {
        "bills": bills,
        "total_sales": total_sales,
        "total_received": total_received,
        "total_due": total_due,
        "pending_bills": pending_bills,
    }

    return render(request, "billing/bills_page.html", context)


def bill_detail(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    items = BillItem.objects.filter(bill=bill).order_by("id")
    payments = Payment.objects.filter(bill=bill).order_by("-payment_date")
    shop = ShopProfile.objects.first()

    context = {
        "bill": bill,
        "items": items,
        "payments": payments,
        "shop": shop,
    }

    return render(request, "billing/bill_detail.html", context)


@require_POST
def receive_due_payment(request, bill_id):
    try:
        amount = Decimal(request.POST.get("amount", "0"))
    except (InvalidOperation, TypeError):
        messages.error(request, "Invalid payment amount.")
        return redirect("bill_detail", bill_id=bill_id)

    payment_method = request.POST.get("payment_method", "cash")

    if not amount.is_finite() or amount <= 0:
        messages.error(request, "Enter a valid payment amount.")
        return redirect("bill_detail", bill_id=bill_id)

    valid_methods = ["cash", "upi", "card"]

    if payment_method not in valid_methods:
        messages.error(request, "Invalid payment method.")
        return redirect("bill_detail", bill_id=bill_id)

    try:
        with transaction.atomic():
            bill = Bill.objects.select_for_update().get(id=bill_id)

            if amount > bill.due_amount:
                messages.error(
                    request,
                    "Payment cannot exceed the remaining due amount."
                )
                return redirect("bill_detail", bill_id=bill_id)

            Payment.objects.create(
                bill=bill,
                amount=amount,
                payment_method=payment_method,
                notes="Due payment received"
            )

            bill.paid_amount += amount
            bill.due_amount -= amount

            if bill.due_amount == 0:
                bill.payment_status = "paid"
            else:
                bill.payment_status = "partial"

            bill.save(update_fields=[
                "paid_amount",
                "due_amount",
                "payment_status"
            ])

        messages.success(request, "Payment received successfully!")

    except Bill.DoesNotExist:
        messages.error(request, "Bill not found.")

    return redirect("bill_detail", bill_id=bill_id)




from .models import Customer

def customers_page(request):
    customers = Customer.objects.filter(
        is_active=True
    ).order_by("-created_at")

    context = {
        "customers": customers,
        "total_customers": customers.count(),
    }

    return render(request, "customers/customers_page.html", context)



from django.contrib import messages
from django.shortcuts import redirect
from .models import Customer



def add_customer(request):
    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        gstin = request.POST.get("gstin", "").strip().upper()

        if not name or not phone:
            messages.error(request, "Customer name and mobile number are required.")
            return redirect("add_customer")

        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Enter a valid 10-digit mobile number.")
            return redirect("add_customer")

        if gstin and len(gstin) != 15:
            messages.error(request, "GSTIN must contain 15 characters.")
            return redirect("add_customer")

        Customer.objects.create(
            name=name,
            phone=phone,
            address=address,
            gstin=gstin
        )

        messages.success(request, "Customer added successfully!")
        return redirect("customers_page")

    return render(request, "customers/add_customer.html")



def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        gstin = request.POST.get("gstin", "").strip().upper()

        if not name or not phone:
            messages.error(request, "Name and mobile number are required.")
            return redirect("edit_customer", customer_id=customer.id)

        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Enter valid 10-digit mobile number.")
            return redirect("edit_customer", customer_id=customer.id)

        if gstin and len(gstin) != 15:
            messages.error(request, "GSTIN must contain 15 characters.")
            return redirect("edit_customer", customer_id=customer.id)

        customer.name = name
        customer.phone = phone
        customer.address = address
        customer.gstin = gstin
        customer.save()

        messages.success(request, "Customer updated successfully!")
        return redirect("customers_page")

    return render(
        request,
        "customers/edit_customer.html",
        {"customer": customer}
    )


@require_POST
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    has_bills = Bill.objects.filter(
        customer_name=customer.name,
        customer_phone=customer.phone
    ).exists()

    if has_bills:
        customer.is_active = False
        customer.save(update_fields=["is_active"])
        messages.warning(
            request,
            "Customer has billing history. Customer deactivated instead of deleted."
        )
    else:
        customer.delete()
        messages.success(request, "Customer deleted successfully!")

    return redirect("customers_page")



def customer_ledger(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    bills = Bill.objects.filter(
        customer=customer
    ).order_by("-created_at")

    summary = bills.aggregate(
        total_sales=Sum("grand_total"),
        total_received=Sum("paid_amount"),
        total_due=Sum("due_amount")
    )

    # Customer Payment History
    payments = Payment.objects.filter(
        bill__customer=customer
    ).select_related("bill").order_by("-payment_date")

    context = {
        "customer": customer,
        "bills": bills,
        "payments": payments,
        "total_bills": bills.count(),
        "total_sales": summary["total_sales"] or 0,
        "total_received": summary["total_received"] or 0,
        "total_due": summary["total_due"] or 0,
    }

    return render(
        request,
        "customers/customer_ledger.html",
        context
    )



def customer_search(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"customers": []})

    customers = (
        Customer.objects.filter(
            is_active=True,
            name__icontains=query
        )
        |
        Customer.objects.filter(
            is_active=True,
            phone__icontains=query
        )
    ).distinct().order_by("name")[:8]

    results = [
        {
            "id": customer.id,
            "name": customer.name,
            "phone": customer.phone,
            "gstin": customer.gstin,
        }
        for customer in customers
    ]

    return JsonResponse({"customers": results})



def delete_paid_bill_record(bill):
    """
    Delete a fully paid bill and restore its product stock.
    Must be called inside transaction.atomic().
    """

    if bill.payment_status != "paid" or bill.due_amount != 0:
        raise ValueError("Only fully paid bills can be deleted.")

    items = BillItem.objects.filter(bill=bill).select_related("product")

    for item in items:

        product = Product.objects.select_for_update().get(
            id=item.product_id
        )

        # Restore sold quantity
        product.stock_quantity += item.quantity

        product.save(update_fields=["stock_quantity"])

        # Keep stock audit history
        StockMovement.objects.create(
            product=product,
            movement_type="IN",
            quantity=item.quantity,
            reference=f"Restore deleted bill: {bill.invoice_number}"
        )

    # Payment has PROTECT relationship, so delete payments first
    Payment.objects.filter(bill=bill).delete()

    # BillItem records are deleted through CASCADE
    bill.delete()


@require_POST
def delete_paid_bill(request, bill_id):

    try:
        with transaction.atomic():

            bill = get_object_or_404(
                Bill.objects.select_for_update(),
                id=bill_id
            )

            delete_paid_bill_record(bill)

        messages.success(
            request,
            "Paid bill deleted and stock restored successfully!"
        )

    except ValueError as error:
        messages.error(request, str(error))

    return redirect("bills_page")


@require_POST
def delete_all_paid_bills(request):

    deleted_count = 0

    try:
        with transaction.atomic():

            paid_bills = list(
                Bill.objects.select_for_update()
                .filter(
                    payment_status="paid",
                    due_amount=0
                )
                .order_by("id")
            )

            for bill in paid_bills:
                delete_paid_bill_record(bill)
                deleted_count += 1

        messages.success(
            request,
            f"{deleted_count} paid bills deleted and stock restored successfully!"
        )

    except ValueError as error:
        messages.error(request, str(error))

    return redirect("bills_page")


def stock_dashboard(request):

    products = Product.objects.filter(is_active=True)

    total_products = products.count()

    total_stock_value = sum(
        (
            product.purchase_price * product.stock_quantity
            for product in products
        ),
        Decimal("0.00")
    )

    low_stock_products = products.filter(
        stock_quantity__gt=0,
        stock_quantity__lte=models.F("minimum_stock_level")
    ).count()

    out_of_stock_products = products.filter(
        stock_quantity=0
    ).count()
    
    low_stock_items = products.filter(
        stock_quantity__gt=0,
        stock_quantity__lte=models.F("minimum_stock_level")
    ).order_by("stock_quantity")

    out_of_stock_items = products.filter(
        stock_quantity=0
    ).order_by("name")

    context = {
        "total_products": total_products,
        "total_stock_value": total_stock_value,
        "low_stock_products": low_stock_products,
        "out_of_stock_products": out_of_stock_products,
        "low_stock_items": low_stock_items,
        "out_of_stock_items": out_of_stock_items,
    }

    return render(
        request,
        "inventory/stock_dashboard.html",
        context
    )


def stock_movement_view(request):

    form = StockMovementForm(request.POST or None)

    if request.method == "POST" and form.is_valid():

        try:
            with transaction.atomic():

                product = Product.objects.select_for_update().get(
                    id=form.cleaned_data["product"].id
                )

                movement_type = form.cleaned_data["movement_type"]
                quantity = form.cleaned_data["quantity"]

                if movement_type == "IN":
                    product.stock_quantity += quantity

                elif movement_type == "OUT":

                    if product.stock_quantity < quantity:
                        form.add_error(
                            "quantity",
                            "Insufficient stock available."
                        )
                        raise ValueError("Insufficient stock")

                    product.stock_quantity -= quantity

                product.save(update_fields=["stock_quantity"])

                movement = form.save(commit=False)
                movement.product = product
                movement.save()

            messages.success(
                request,
                "Stock movement recorded successfully!"
            )

            return redirect("stock_movement")

        except ValueError:
            pass

        except Product.DoesNotExist:
            messages.error(request, "Product not found.")

    return render(
        request,
        "inventory/stock_movement.html",
        {"form": form}
    )


def stock_history(request):

    movements = StockMovement.objects.select_related(
        "product"
    ).order_by("-created_at")

    search = request.GET.get("search", "").strip()
    movement_type = request.GET.get("movement_type", "")
    reason = request.GET.get("reason", "")

    if search:
        movements = movements.filter(
            models.Q(product__name__icontains=search) |
            models.Q(reference__icontains=search)
        )

    if movement_type in ["IN", "OUT"]:
        movements = movements.filter(
            movement_type=movement_type
        )

    valid_reasons = [
        choice[0] for choice in StockMovement.REASON_CHOICES
    ]

    if reason in valid_reasons:
        movements = movements.filter(reason=reason)

    context = {
        "movements": movements,
        "total_movements": movements.count(),
        "stock_in_count": movements.filter(
            movement_type="IN"
        ).count(),
        "stock_out_count": movements.filter(
            movement_type="OUT"
        ).count(),
        "search": search,
        "selected_movement": movement_type,
        "selected_reason": reason,
    }

    return render(
        request,
        "inventory/stock_history.html",
        context
    )
    
    

def delete_all_stock_history(request):

    if request.method == "POST":

        total = StockMovement.objects.count()

        StockMovement.objects.all().delete()

        messages.success(
            request,
            f"{total} stock history records deleted successfully!"
        )

    else:
        messages.error(
            request,
            "Invalid request."
        )

    return redirect("stock_history")


def stock_list(request):

    products = Product.objects.filter(
        is_active=True
    ).select_related("category").order_by("name")

    search = request.GET.get("search", "").strip()
    category_id = request.GET.get("category", "")
    stock_status = request.GET.get("status", "")

    if search:
        products = products.filter(
            models.Q(name__icontains=search) |
            models.Q(barcode__icontains=search)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    if stock_status == "low":
        products = products.filter(
            stock_quantity__gt=0,
            stock_quantity__lte=models.F("minimum_stock_level")
        )

    elif stock_status == "out":
        products = products.filter(stock_quantity=0)

    elif stock_status == "available":
        products = products.filter(
            stock_quantity__gt=models.F("minimum_stock_level")
        )

    context = {
        "products": products,
        "categories": Category.objects.filter(is_active=True),
        "search": search,
        "selected_category": category_id,
        "selected_status": stock_status,
        "total_products": products.count(),
    }

    return render(
        request,
        "inventory/stock_list.html",
        context
    )


def reports_dashboard(request):
    from django.utils import timezone
    from django.db.models import Sum
    from datetime import timedelta

    today = timezone.localdate()
    first_day = today.replace(day=1)

    today_bills = Bill.objects.filter(created_at__date=today)
    monthly_bills = Bill.objects.filter(created_at__date__gte=first_day)

    today_sales = today_bills.aggregate(
        total=Sum("grand_total")
    )["total"] or 0

    monthly_sales = monthly_bills.aggregate(
        total=Sum("grand_total")
    )["total"] or 0

    total_bills = Bill.objects.count()

    context = {
        "today_sales": today_sales,
        "monthly_sales": monthly_sales,
        "today_bills_count": today_bills.count(),
        "monthly_bills_count": monthly_bills.count(),
        "total_bills": total_bills,
    }

    return render(request, "reports/dashboard.html", context)

def daily_sales_report(request):
    selected_date = request.GET.get("date")

    if selected_date:
        try:
            report_date = datetime.strptime(
                selected_date, "%Y-%m-%d"
            ).date()
        except ValueError:
            report_date = timezone.localdate()
    else:
        report_date = timezone.localdate()

    bills = Bill.objects.filter(
        created_at__date=report_date
    ).order_by("-created_at")

    summary = bills.aggregate(
        total_sales=Sum("grand_total"),
        total_bills=Count("id")
    )

    context = {
        "report_date": report_date,
        "bills": bills,
        "total_sales": summary["total_sales"] or 0,
        "total_bills": summary["total_bills"] or 0,
    }

    return render(
        request,
        "reports/daily_sales.html",
        context
    )
    

def monthly_sales_report(request):
    from django.utils import timezone
    from django.db.models import Sum, Count, Avg
    from datetime import date
    import calendar

    today = timezone.localdate()

    try:
        selected_month = int(request.GET.get("month", today.month))
        selected_year = int(request.GET.get("year", today.year))

        if selected_month < 1 or selected_month > 12:
            raise ValueError

        if selected_year < 2000 or selected_year > 2100:
            raise ValueError

    except (ValueError, TypeError):
        selected_month = today.month
        selected_year = today.year

    first_day = date(selected_year, selected_month, 1)

    last_day = date(
        selected_year,
        selected_month,
        calendar.monthrange(selected_year, selected_month)[1]
    )

    bills = Bill.objects.filter(
        created_at__date__gte=first_day,
        created_at__date__lte=last_day
    ).order_by("-created_at")

    summary = bills.aggregate(
        total_sales=Sum("grand_total"),
        total_bills=Count("id"),
        average_bill=Avg("grand_total")
    )

    context = {
        "bills": bills,
        "selected_month": selected_month,
        "selected_year": selected_year,
        "month_name": calendar.month_name[selected_month],
        "month_choices": [
            (i, calendar.month_name[i])
            for i in range(1, 13)
        ],
        "total_sales": summary["total_sales"] or 0,
        "total_bills": summary["total_bills"] or 0,
        "average_bill": summary["average_bill"] or 0,
    }

    return render(
        request,
        "reports/monthly_sales.html",
        context
    )


def yearly_sales_report(request):
    from django.utils import timezone
    from django.db.models import Sum, Count, Avg
    from django.db.models.functions import TruncMonth
    from datetime import date
    import calendar

    today = timezone.localdate()

    try:
        selected_year = int(
            request.GET.get("year", today.year)
        )

        if selected_year < 2000 or selected_year > 2100:
            raise ValueError

    except (ValueError, TypeError):
        selected_year = today.year

    first_day = date(selected_year, 1, 1)
    last_day = date(selected_year, 12, 31)

    bills = Bill.objects.filter(
        created_at__date__gte=first_day,
        created_at__date__lte=last_day
    )

    summary = bills.aggregate(
        total_sales=Sum("grand_total"),
        total_bills=Count("id"),
        average_bill=Avg("grand_total")
    )

    monthly_data = bills.annotate(
        month=TruncMonth("created_at")
    ).values("month").annotate(
        total_sales=Sum("grand_total"),
        total_bills=Count("id")
    ).order_by("month")

    monthly_sales = {
        item["month"].month: item
        for item in monthly_data
    }

    monthly_summary = []

    for month_number in range(1, 13):
        month_data = monthly_sales.get(month_number, {})

        monthly_summary.append({
            "month_name": calendar.month_name[month_number],
            "total_sales": month_data.get("total_sales") or 0,
            "total_bills": month_data.get("total_bills") or 0,
        })

    context = {
        "selected_year": selected_year,
        "total_sales": summary["total_sales"] or 0,
        "total_bills": summary["total_bills"] or 0,
        "average_bill": summary["average_bill"] or 0,
        "monthly_summary": monthly_summary,
    }

    return render(
        request,
        "reports/yearly_sales.html",
        context
    )


def profit_report(request):
    from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
    from django.db.models.functions import Coalesce
    from decimal import Decimal

    bill_items = BillItem.objects.filter(
        purchase_price__gt=0
    )

    profit_expression = ExpressionWrapper(
        (F("unit_price") - F("purchase_price")) * F("quantity"),
        output_field=DecimalField(max_digits=14, decimal_places=2)
    )

    cost_expression = ExpressionWrapper(
        F("purchase_price") * F("quantity"),
        output_field=DecimalField(max_digits=14, decimal_places=2)
    )

    summary = bill_items.aggregate(
        total_sales=Coalesce(
            Sum("taxable_amount"), Decimal("0.00")
        ),
        total_cost=Coalesce(
            Sum(cost_expression), Decimal("0.00")
        ),
        gross_profit=Coalesce(
            Sum(profit_expression), Decimal("0.00")
        ),
        total_bills=Count("bill", distinct=True)
    )

    uncaptured_items = BillItem.objects.filter(
        purchase_price=0
    ).count()

    context = {
        "total_sales": summary["total_sales"],
        "total_cost": summary["total_cost"],
        "gross_profit": summary["gross_profit"],
        "total_bills": summary["total_bills"],
        "uncaptured_items": uncaptured_items,
    }

    return render(
        request,
        "reports/profit_report.html",
        context
    )



def daily_profit_report(request):
    from datetime import datetime
    from django.utils import timezone
    from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
    from decimal import Decimal

    selected_date = request.GET.get("date")

    if selected_date:
        try:
            report_date = datetime.strptime(
                selected_date, "%Y-%m-%d"
            ).date()
        except ValueError:
            report_date = timezone.localdate()
    else:
        report_date = timezone.localdate()

    items = BillItem.objects.filter(
        bill__created_at__date=report_date,
        purchase_price__gt=0
    )

    profit_expression = ExpressionWrapper(
        (F("unit_price") - F("purchase_price")) * F("quantity"),
        output_field=DecimalField(max_digits=14, decimal_places=2)
    )

    cost_expression = ExpressionWrapper(
        F("purchase_price") * F("quantity"),
        output_field=DecimalField(max_digits=14, decimal_places=2)
    )

    summary = items.aggregate(
        total_sales=Sum("taxable_amount"),
        total_cost=Sum(cost_expression),
        gross_profit=Sum(profit_expression),
        total_bills=Count("bill", distinct=True)
    )

    uncaptured_items = BillItem.objects.filter(
        bill__created_at__date=report_date,
        purchase_price=0
    ).count()

    context = {
        "report_date": report_date,
        "total_sales": summary["total_sales"] or Decimal("0.00"),
        "total_cost": summary["total_cost"] or Decimal("0.00"),
        "gross_profit": summary["gross_profit"] or Decimal("0.00"),
        "total_bills": summary["total_bills"] or 0,
        "uncaptured_items": uncaptured_items,
    }

    return render(
        request,
        "reports/daily_profit.html",
        context
    )



def monthly_profit_report(request):
    from datetime import date
    import calendar
    from decimal import Decimal
    from django.utils import timezone
    from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper

    today = timezone.localdate()

    try:
        selected_month = int(request.GET.get("month", today.month))
        selected_year = int(request.GET.get("year", today.year))

        if not 1 <= selected_month <= 12:
            raise ValueError

        if not 2000 <= selected_year <= 2100:
            raise ValueError

    except (ValueError, TypeError):
        selected_month = today.month
        selected_year = today.year

    first_day = date(selected_year, selected_month, 1)

    last_day = date(
        selected_year,
        selected_month,
        calendar.monthrange(selected_year, selected_month)[1]
    )

    items = BillItem.objects.filter(
        bill__created_at__date__gte=first_day,
        bill__created_at__date__lte=last_day,
        purchase_price__gt=0
    )

    profit_expression = ExpressionWrapper(
        (F("unit_price") - F("purchase_price")) * F("quantity"),
        output_field=DecimalField(max_digits=14, decimal_places=2)
    )

    cost_expression = ExpressionWrapper(
        F("purchase_price") * F("quantity"),
        output_field=DecimalField(max_digits=14, decimal_places=2)
    )

    summary = items.aggregate(
        total_sales=Sum("taxable_amount"),
        total_cost=Sum(cost_expression),
        gross_profit=Sum(profit_expression),
        total_bills=Count("bill", distinct=True)
    )

    uncaptured_items = BillItem.objects.filter(
        bill__created_at__date__gte=first_day,
        bill__created_at__date__lte=last_day,
        purchase_price=0
    ).count()

    context = {
        "selected_month": selected_month,
        "selected_year": selected_year,
        "month_name": calendar.month_name[selected_month],
        "month_choices": [
            (i, calendar.month_name[i])
            for i in range(1, 13)
        ],
        "total_sales": summary["total_sales"] or Decimal("0.00"),
        "total_cost": summary["total_cost"] or Decimal("0.00"),
        "gross_profit": summary["gross_profit"] or Decimal("0.00"),
        "total_bills": summary["total_bills"] or 0,
        "uncaptured_items": uncaptured_items,
    }

    return render(
        request,
        "reports/monthly_profit.html",
        context
    )


def yearly_profit_report(request):
    from datetime import date
    from decimal import Decimal
    from django.utils import timezone
    from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
    from django.db.models.functions import TruncMonth
    import calendar

    today = timezone.localdate()

    try:
        selected_year = int(
            request.GET.get("year", today.year)
        )

        if not 2000 <= selected_year <= 2100:
            raise ValueError

    except (ValueError, TypeError):
        selected_year = today.year

    first_day = date(selected_year, 1, 1)
    last_day = date(selected_year, 12, 31)

    items = BillItem.objects.filter(
        bill__created_at__date__gte=first_day,
        bill__created_at__date__lte=last_day,
        purchase_price__gt=0
    )

    profit_expression = ExpressionWrapper(
        (F("unit_price") - F("purchase_price")) * F("quantity"),
        output_field=DecimalField(max_digits=14, decimal_places=2)
    )

    cost_expression = ExpressionWrapper(
        F("purchase_price") * F("quantity"),
        output_field=DecimalField(max_digits=14, decimal_places=2)
    )

    summary = items.aggregate(
        total_sales=Sum("taxable_amount"),
        total_cost=Sum(cost_expression),
        gross_profit=Sum(profit_expression),
        total_bills=Count("bill", distinct=True)
    )

    monthly_data = items.annotate(
        month=TruncMonth("bill__created_at")
    ).values("month").annotate(
        total_sales=Sum("taxable_amount"),
        total_cost=Sum(cost_expression),
        gross_profit=Sum(profit_expression),
        total_bills=Count("bill", distinct=True)
    ).order_by("month")

    monthly_profit_data = {
        item["month"].month: item
        for item in monthly_data
    }

    monthly_summary = []

    for month_number in range(1, 13):
        month_data = monthly_profit_data.get(month_number, {})

        monthly_summary.append({
            "month_name": calendar.month_name[month_number],
            "total_sales": month_data.get("total_sales") or Decimal("0.00"),
            "total_cost": month_data.get("total_cost") or Decimal("0.00"),
            "gross_profit": month_data.get("gross_profit") or Decimal("0.00"),
            "total_bills": month_data.get("total_bills") or 0,
        })

    uncaptured_items = BillItem.objects.filter(
        bill__created_at__date__gte=first_day,
        bill__created_at__date__lte=last_day,
        purchase_price=0
    ).count()

    context = {
        "selected_year": selected_year,
        "total_sales": summary["total_sales"] or Decimal("0.00"),
        "total_cost": summary["total_cost"] or Decimal("0.00"),
        "gross_profit": summary["gross_profit"] or Decimal("0.00"),
        "total_bills": summary["total_bills"] or 0,
        "monthly_summary": monthly_summary,
        "uncaptured_items": uncaptured_items,
    }

    return render(
        request,
        "reports/yearly_profit.html",
        context
    )


from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def expense_list(request):
    from django.utils import timezone
    from django.db.models import Sum
    from decimal import Decimal

    today = timezone.localdate()

    expenses = Expense.objects.all().order_by(
        "-expense_date", "-created_at"
    )

    daily_total = Expense.objects.filter(
        expense_date=today
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    monthly_total = Expense.objects.filter(
        expense_date__year=today.year,
        expense_date__month=today.month
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    yearly_total = Expense.objects.filter(
        expense_date__year=today.year
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    total_expenses = Expense.objects.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    context = {
        "expenses": expenses,
        "daily_total": daily_total,
        "monthly_total": monthly_total,
        "yearly_total": yearly_total,
        "total_expenses": total_expenses,
    }

    return render(
        request,
        "expenses/expense_list.html",
        context
    )

@login_required
def add_expense(request):

    if request.method == "POST":
        form = ExpenseForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Expense added successfully!")
            return redirect("expense_list")

    else:
        form = ExpenseForm()

    return render(
        request,
        "expenses/add_expense.html",
        {"form": form}
    )



@login_required
def delete_expense(request, expense_id):
    from django.shortcuts import get_object_or_404
    from django.views.decorators.http import require_POST
    from django.contrib import messages

    if request.method != "POST":
        return redirect("expense_list")

    expense = get_object_or_404(Expense, id=expense_id)
    expense.delete()

    messages.success(request, "Expense deleted successfully!")
    return redirect("expense_list")


@login_required
def delete_all_expenses(request):
    from django.views.decorators.http import require_POST
    from django.contrib import messages

    if request.method != "POST":
        return redirect("expense_list")

    deleted_count, _ = Expense.objects.all().delete()

    messages.success(
        request,
        f"{deleted_count} expense records deleted successfully!"
    )

    return redirect("expense_list")


