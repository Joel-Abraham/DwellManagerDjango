# DwellManager Django

A full-featured apartment management system built with Django, featuring role-based access control (Admin, Guard, Resident), server-side rendered views, and strict data isolation.

## Features

- **Admin Portal** — Flat CRUD, Resident management, Maintenance assignment, Billing overview
- **Guard Dashboard** — Visitor check-in/checkout, searchable visit history
- **Resident Dashboard** — Billing & payments, Maintenance requests, Receipt generation
- **Security** — Server-side role guards, IDOR protection, atomic transactions for financial operations

---

## Setup Instructions (Windows + VS Code)

### 1. Prerequisites
- **Python 3.10+** installed ([python.org](https://www.python.org/downloads/))
- **VS Code** with the Python extension
- **Git** for cloning

### 2. Clone Repository
```powershell
git clone https://github.com/Joel-Abraham/DwellManagerDjango.git
cd DwellManagerDjango
```

### 3. Open in VS Code
```powershell
code .
```

### 4. Create Virtual Environment
```powershell
python -m venv venv
```

### 5. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```
> If you get an execution policy error, run:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

### 6. Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 7. Run Migrations
```powershell
python manage.py migrate
```

### 8. Seed Database
```powershell
$env:PYTHONIOENCODING='utf-8'; python seed_django.py
```

### 9. Run Development Server
```powershell
python manage.py runserver
```

### 10. Open in Browser
Navigate to: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Development Login Credentials

| Role     | Username   | Password     | Flat   |
|----------|------------|--------------|--------|
| Admin    | `admin`    | `admin123`   | —      |
| Guard    | `guard1`   | `guard123`   | —      |
| Resident | `resident1`| `resident123`| A-101  |
| Resident | `resident2`| `resident123`| B-101  |

---

## VS Code Tasks

Use **Terminal → Run Task** for common operations:

| Task                     | Description                              |
|--------------------------|------------------------------------------|
| Install Dependencies     | `pip install -r requirements.txt`        |
| Migrate                  | Apply database migrations                |
| Seed Database            | Populate with development data           |
| Run Server               | Start Django development server          |
| Run Tests                | Execute full test suite                  |
| Reset Database           | Delete `db.sqlite3`                      |
| Full Reset + Seed + Serve| Chain: reset → migrate → seed → server   |

---

## Running Tests

```powershell
python manage.py test api -v 2
```

The test suite covers:
- Flat CRUD operations
- Resident management
- Maintenance request lifecycle
- Atomic billing (assignment + charge creation)
- Payment processing with double-payment protection
- Visitor check-in/checkout
- **IDOR/security tests** — cross-flat access denied (403/404)
- Authentication and role-based redirects

---

## Project Architecture

```
DwellManagerDjango/
├── api/
│   ├── models.py         # Flat, Resident, MaintenanceRequest, Payment, Visitor
│   ├── forms.py          # Django ModelForms for all operations
│   ├── views.py          # Server-side views + DRF ViewSets
│   ├── permissions.py    # DRF permissions + Django view decorators
│   ├── urls.py           # URL patterns for all roles + API
│   ├── serializers.py    # DRF serializers
│   ├── admin.py          # Django admin configuration
│   ├── tests.py          # Comprehensive test suite
│   └── migrations/
├── templates/
│   ├── base.html         # Base layout with role-aware sidebar
│   ├── login.html        # Session-based login
│   ├── admin/            # Admin templates
│   ├── guard/            # Guard templates
│   └── resident/         # Resident templates
├── static/
│   └── style.css         # Dark glassmorphism design system
├── dwellmanager/
│   ├── settings.py
│   └── urls.py
├── seed_django.py        # Development data seeder
├── requirements.txt
├── manage.py
└── README.md
```

---

## Key Design Decisions

- **`Resident` IS `AUTH_USER_MODEL`** — The custom user model stores both authentication and profile data
- **Unified `Payment` model** — Handles both Base Maintenance and Additional Charges via `charge_type` discriminator
- **`MaintenanceRequest`** replaces old `Complaint` model with proper workflow statuses
- **Server-side data isolation** — All resident views derive flat from `request.user.flat`, never from user input
- **`transaction.atomic()`** — Used for maintenance assignment (with charge creation) and payment processing
- **Session auth** (primary) + JWT (backward compatible API)
