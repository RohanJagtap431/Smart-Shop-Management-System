# 🏪 Smart Shop Management System

A Django-based web application designed to simplify daily shop operations through digital billing, inventory management, customer records, expense tracking, and business reports.

**Live Demo:** https://smart-shop-management-system.onrender.com

**GitHub Repository:** https://github.com/RohanJagtap431/Smart-Shop-Management-System

---

## 📌 About The Project

Smart Shop Management System is a web-based billing and shop management application built using Python and Django.

It helps shop owners manage products, generate GST invoices, track inventory, maintain customer records, record expenses, and monitor business performance from a centralized dashboard.

The project uses PostgreSQL for database management and is deployed using Render.

## ✨ Features

### 1. Dashboard
- Overview of shop activities.
- Today's sales and expenses.
- Estimated profit after recorded expenses.
- Total stock valuation.

### 2. Product Management
- Add, edit, and manage products.
- Product categories.
- Purchase and selling prices.
- Product search.
- Active and inactive product status.
- Minimum stock level configuration.

### 3. Category Management
- Create and manage categories.
- Edit category details.
- Activate or deactivate categories.

### 4. GST Billing System
- Search products while billing.
- Shopping cart and quantity management.
- Automatic GST calculations.
- CGST and SGST for intra-state sales.
- IGST for interstate sales.
- Full payment, partial payment, and credit billing.
- GST invoice generation.
- Payment history.

### 5. Customer Management
- Add and edit customers.
- Customer search.
- Customer ledger.
- Customer billing history.
- Outstanding due tracking.

### 6. Stock Management
- Stock In and Stock Out.
- Automatic stock deduction after billing.
- Stock restoration when eligible bills are deleted.
- Low stock and out-of-stock alerts.
- Stock movement history.

### 7. Reports Management
- Daily sales reports.
- Monthly sales reports.
- Yearly sales reports.
- Overall profit reports.
- Daily, monthly, and yearly profit reports.

### 8. Expense Management
- Record business expenses.
- Categorize expenses.
- Daily, monthly, and yearly expense summaries.
- Expense deletion.

### 9. Authentication & Security
- Django built-in authentication.
- Single-owner login workflow.
- Login-protected application pages.
- Logout functionality.
- CSRF protection.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend Programming |
| Django | Web Framework |
| PostgreSQL | Database |
| HTML5 | Page Structure |
| CSS3 | Styling and Responsive UI |
| JavaScript | Billing Interactions |
| WhiteNoise | Static File Serving |
| Gunicorn | Production WSGI Server |
| Git & GitHub | Version Control |
| Render | Deployment |
| Neon | PostgreSQL Hosting |

---

## 📂 Project Structure

```text
Smart-Shop-Management-System/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── store/
│   ├── migrations/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── templates/
│   ├── registration/
│   ├── billing/
│   ├── categories/
│   ├── customers/
│   ├── dashboard/
│   ├── expenses/
│   ├── inventory/
│   ├── products/
│   └── reports/
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── billing.js
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Installation & Setup

### Prerequisites

- Python
- Git
- PostgreSQL database
- Visual Studio Code (recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/RohanJagtap431/Smart-Shop-Management-System.git
```

### 2. Open Project Directory

```bash
cd Smart-Shop-Management-System
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

**Windows PowerShell:**

```powershell
venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file in the project root directory.

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=your-postgresql-database-url
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=
```

**Important:** Never upload your `.env` file or database credentials to GitHub.

### 7. Apply Database Migrations

```bash
python manage.py migrate
```

### 8. Create Superuser

```bash
python manage.py createsuperuser
```

Use the superuser credentials to log in to the application.

### 9. Run Development Server

```bash
python manage.py runserver
```

Open the application:

```text
http://127.0.0.1:8000/
```

---

## 🚀 Deployment

The application is deployed using:

- **Web Hosting:** Render
- **Database:** Neon PostgreSQL
- **Static Files:** WhiteNoise
- **Application Server:** Gunicorn

**Live Application:** https://smart-shop-management-system.onrender.com

Production environment variables must be configured securely in the hosting dashboard.

---

## 🔐 Security Notes

- Keep `DEBUG=False` in production.
- Use a strong and private Django `SECRET_KEY`.
- Never commit `.env` files.
- Keep database credentials private.
- Use HTTPS in production.
- Create a secure Django superuser account.

---

## 🔮 Future Improvements

- Advanced sales analytics.
- PDF and Excel report downloads.
- Barcode scanner integration.
- Multiple staff accounts and role-based permissions.
- Automated database backups.
- Improved invoice customization.
- Enhanced mobile experience.

---

## 👨‍💻 Developer

**Developed by:** Rohan Jagtap

**GitHub:** https://github.com/RohanJagtap431

**Project:** Smart Shop Management System

---

## 📄 License

No license has been specified for this project yet. All rights are reserved by the project author unless a license is added.
