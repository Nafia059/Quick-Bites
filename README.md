# Quick Bites

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5">
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3">
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript">
</p>

<p align="center">
  <b>A full-featured food delivery platform built with Django</b>
</p>

---

## Overview

**Quick Bites** is a comprehensive food delivery application that connects customers with restaurants and grocery vendors. The platform supports multiple user roles including customers, restaurants, grocery vendors, riders, and administrators.

---

## Key Features

### For Customers
- Browse restaurants and menus
- Order food and groceries
- Real-time order tracking
- Multiple payment options (COD & Card)
- Rate and review restaurants
- Referral system with promo codes
- Help ticket support

### For Restaurants
- Dashboard to manage orders
- Menu item management
- Order status updates
- Customer reviews

### For Grocery Vendors
- Product listings
- Stock management
- Order fulfillment

### For Riders
- Delivery assignments
- Location tracking
- Status updates

### For Admin
- User management
- Platform oversight
- Support ticket handling

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python** | Backend Language |
| **Django** | Web Framework |
| **SQLite** | Database |
| **HTML/CSS** | Frontend Templates |
| **JavaScript** | Interactive Features |

---

## Project Structure

``````
Quick-Bites/
├── templates/              # HTML Templates
│   ├── restaurant/        # Restaurant views
│   ├── rider/            # Rider views
│   ├── home.html         # Homepage
│   ├── cart.html         # Shopping cart
│   ├── checkout.html     # Checkout page
│   └── ...
├── models.py             # Database Models
├── views.py              # View Functions
├── urls.py               # URL Routing
├── forms.py              # Django Forms
└── README.md             # Documentation
``````

---

## Database Models

| Model | Description |
|-------|-------------|
| **User** | Extended user model with role types |
| **Restaurant** | Restaurant profiles |
| **MenuItem** | Food items with prices |
| **Cart** | Shopping cart for users |
| **Order** | Order management |
| **Payment** | Payment tracking |
| **Rider** | Delivery personnel |
| **Review** | Customer feedback |
| **PromoCode** | Discount codes |
| **Notification** | User notifications |

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

``````bash
# 1. Clone the repository
git clone https://github.com/Nafia059/Quick-Bites.git

# 2. Navigate to project directory
cd Quick-Bites

# 3. Create virtual environment
python -m venv venv

# 4. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 5. Install dependencies
pip install django

# 6. Run migrations
python manage.py migrate

# 7. Create superuser (admin)
python manage.py createsuperuser

# 8. Run the server
python manage.py runserver
``````

The application will be available at `http://127.0.0.1:8000/`

---

## Features in Detail

### Order Flow
```
Customer Browses → Adds to Cart → Checkout → Payment → Restaurant Prepares → Rider Delivers → Order Complete
```

### User Roles
| Role | Permissions |
|------|-------------|
| **Customer** | Browse, Order, Review |
| **Restaurant** | Manage Menu, Update Orders |
| **Grocery Vendor** | Manage Products, Fulfill Orders |
| **Rider** | Accept Deliveries, Update Status |
| **Admin** | Full Access |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Homepage |
| `/cart/` | GET | View cart |
| `/checkout/` | POST | Process order |
| `/orders/` | GET | Order history |
| `/restaurant/` | GET | Restaurant dashboard |
| `/rider/` | GET | Rider dashboard |

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## Author

**Nafia Aziz** - [GitHub](https://github.com/Nafia059)

---

<p align="center">
  Made by <b>Nafia Aziz</b>
</p>
