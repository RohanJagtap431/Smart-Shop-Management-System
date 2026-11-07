from django.urls import path
from . import views
from .views import (
    bills_page,
    bill_detail,
    receive_due_payment,
    customers_page, 
    add_customer, 
    edit_customer, 
    delete_customer,
    customers_page,
    add_customer,
    customer_ledger,
    customer_search,
    delete_paid_bill,
    delete_all_paid_bills,
    stock_dashboard,
    stock_movement_view,
    stock_history,
    delete_all_stock_history,
    stock_list,
    reports_dashboard,
    daily_sales_report,
    monthly_sales_report,
    yearly_sales_report,
    profit_report,
    daily_profit_report,
    monthly_profit_report,
    yearly_profit_report,
    expense_list,
    add_expense,
    delete_expense,
    delete_all_expenses,
)


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.add_product, name="add_product"),
    
    path(
        "products/<int:product_id>/edit/",
        views.edit_product,
        name="edit_product"
    ),

    path(
        "products/<int:product_id>/delete/",
        views.delete_product,
        name="delete_product"
    ),
    
    path(
        "categories/",
        views.category_list,
        name="category_list"
    ),
    
    path("categories/add/", views.add_category, name="add_category"),

    path(
        "categories/<int:category_id>/edit/",
        views.edit_category,
        name="edit_category"
    ),

    path(
        "categories/<int:category_id>/delete/",
        views.delete_category,
        name="delete_category"
    ),
    
    path(
        "products/<int:product_id>/toggle-status/",
        views.toggle_product_status,
        name="toggle_product_status"
    ),
    
    path(
        "categories/<int:category_id>/toggle-status/",
        views.toggle_category_status,
        name="toggle_category_status"
    ),
    
    path(
        "api/billing/products/",
        views.billing_product_search,
        name="billing_product_search"
    ),
    
    path(
        "billing/",
        views.billing_page,
        name="billing_page"
    ),
    
    path(
        "api/billing/generate/",
        views.generate_bill,
        name="generate_bill"
    ),
    
    path("bills/", bills_page, name="bills_page"),
    
    path(
        "bills/<int:bill_id>/",
        bill_detail,
        name="bill_detail"
    ),
    
    path(
        "bills/<int:bill_id>/receive-payment/",
        receive_due_payment,
        name="receive_due_payment"
    ),
    
    path("customers/", customers_page, name="customers_page"),
    
    path("customers/add/", add_customer, name="add_customer"),
    
    path(
        "customers/<int:customer_id>/edit/",
        edit_customer,
        name="edit_customer"
    ),

    path(
        "customers/<int:customer_id>/delete/",
        delete_customer,
        name="delete_customer"
    ),
    
    path(
        "customers/<int:customer_id>/ledger/",
        customer_ledger,
        name="customer_ledger"
    ),
    
    path(
        "api/customers/search/",
        customer_search,
        name="customer_search"
    ),
    
    path(
        "bills/<int:bill_id>/delete/",
        delete_paid_bill,
        name="delete_paid_bill"
    ),

    path(
        "bills/delete-all-paid/",
        delete_all_paid_bills,
        name="delete_all_paid_bills"
    ),
    
    path(
        "stock/",
        stock_dashboard,
        name="stock_dashboard"
    ),
    
    path(
        "stock/movement/",
        stock_movement_view,
        name="stock_movement"
    ),
    
    path(
        "stock/history/",
        stock_history,
        name="stock_history"
    ),
    
    path(
        "stock/history/delete-all/",
        delete_all_stock_history,
        name="delete_all_stock_history"
    ),
    
    path(
        "stock/list/",
        stock_list,
        name="stock_list"
    ),
    
    path("reports/", reports_dashboard, name="reports_dashboard"),
    
    path(
        "reports/daily-sales/",
        daily_sales_report,
        name="daily_sales_report"
    ),
    
    path(
        "reports/monthly-sales/",
        monthly_sales_report,
        name="monthly_sales_report"
    ),
    
    path(
        "reports/yearly-sales/",
        yearly_sales_report,
        name="yearly_sales_report"
    ),
    
    path(
        "reports/profit/",
        profit_report,
        name="profit_report"
    ),
    
    path(
        "reports/profit/daily/",
        daily_profit_report,
        name="daily_profit_report"
    ),
    
    path(
        "reports/profit/monthly/",
        monthly_profit_report,
        name="monthly_profit_report"
    ),
    
    path(
        "reports/profit/yearly/",
        yearly_profit_report,
        name="yearly_profit_report"
    ),
    
    path("expenses/", expense_list, name="expense_list"),
    path("expenses/add/", add_expense, name="add_expense"),
    
    path(
        "expenses/delete/<int:expense_id>/",
        delete_expense,
        name="delete_expense"
    ),

    path(
        "expenses/delete-all/",
        delete_all_expenses,
        name="delete_all_expenses"
    ),
]