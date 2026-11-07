
from django import forms
from .models import Product, Category, StockMovement, Expense


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product

        fields = [
            "name",
            "category",
            "barcode",
            "purchase_price",
            "selling_price",
            "stock_quantity",
            "minimum_stock_level",
            "unit",
            "gst_rate",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter product name"
            }),

            "category": forms.Select(attrs={
                "class": "form-control"
            }),

            "barcode": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter barcode (optional)"
            }),

            "purchase_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter purchase price",
                "step": "0.01",
                "min": "0"
            }),

            "selling_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter selling price",
                "step": "0.01",
                "min": "0"
            }),

            "stock_quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter available stock",
                "step": "0.001",
                "min": "0"
            }),

            "minimum_stock_level": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter minimum stock limit",
                "step": "0.001",
                "min": "0"
            }),

            "unit": forms.Select(attrs={
                "class": "form-control"
            }),

            "gst_rate": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter GST rate",
                "step": "0.01",
                "min": "0",
                "max": "100"
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-checkbox"
            }),
        }


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ["name", "description"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter category name"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter category description",
                "rows": 3
            }),
        }

class StockMovementForm(forms.ModelForm):

    class Meta:
        model = StockMovement
        fields = [
            "product",
            "movement_type",
            "quantity",
            "reason",
            "reference",
        ]

        widgets = {
            "product": forms.Select(attrs={
                "class": "form-control"
            }),

            "movement_type": forms.Select(attrs={
                "class": "form-control"
            }),

            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter quantity",
                "step": "0.001",
                "min": "0.001"
            }),

            "reason": forms.Select(attrs={
                "class": "form-control"
            }),

            "reference": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter reference (optional)"
            }),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")

        if quantity is None or quantity <= 0:
            raise forms.ValidationError(
                "Quantity must be greater than zero."
            )

        return quantity


class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense
        fields = [
            "title",
            "category",
            "amount",
            "payment_method",
            "expense_date",
            "description",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter expense title"
            }),

            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter amount",
                "step": "0.01",
                "min": "0.01"
            }),

            "expense_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter description",
                "rows": 3
            }),
        }
