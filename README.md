# 📚 Bookstore Backend API

![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Relational-blue?logo=postgresql)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A fully functional, modular, and secure **Bookstore Backend API**, built with **FastAPI** and **SQLAlchemy**, using PostgreSQL for data persistence. This backend supports authentication, cart management, book inventory, order placement, payment simulation, and soft deletion—all designed with clean architecture principles.

---

## 🧱 Tech Stack

| Tech            | Role                  |
| --------------- | --------------------- |
| 🐍 Python       | Programming Language  |
| ⚡ FastAPI       | Web Framework (Async) |
| 🐘 PostgreSQL   | Relational Database   |
| 🛠️ SQLAlchemy  | ORM (2.x style)       |
| 🔐 JWT + OAuth2 | Auth & Authorization  |
| 🛆 Uvicorn      | ASGI Server           |
| 📜 Pydantic     | Data validation       |

---

## 📂 Project Structure

```
app/
├── auth/            # JWT auth, permission checks
├── config/          # Logger, settings
├── db/              # DB session & Base
├── exceptions/      # Custom exception handlers
├── models/          # SQLAlchemy ORM models
├── queries/         # Abstracted DB queries
├── routes/          # FastAPI API routers
├── schemas/         # Pydantic models for validation
├── services/        # Core service logic (transactions, rollback)
├── utils/           # Enums, helpers, response builders
```

---

## 🔐 Authentication & Authorization

* 🔑 JWT-based login
* 👤 Role-based access: `admin`, `customer`
* Middleware to restrict sensitive routes

---

## ✅ Features

### 📚 Books

* Add, update, delete, and fetch books
* Auto-maintain inventory linkage

### 🛒 Cart

* Add/remove/update cart items
* Each user has one active cart

### 📦 Orders

* Create orders from cart
* Calculate taxes + shipping + total cost
* Cancel orders and restore stock

### 💳 Payments

* Simulate transaction (random success/failure)
* Track max 3 attempts
* Auto rollback inventory/cart if all attempts fail
* Soft delete with complete rollback

### 🌍 Shipping

* Country-wise shipping cost management
* Applied during order calculation

### 👤 Users & Roles

* Full CRUD on users & roles
* Admin-only access for sensitive actions

---

## 🔗 API Endpoints Summary

### 📘️ Books

| Method | Endpoint                            | Description           |
| ------ | ----------------------------------- | --------------------- |
| POST   | /books/add-new-book                 | Add a new book        |
| GET    | /books/get-all-books                | Get all books         |
| GET    | /books/get-book-by-id/{id}          | Get book by ID        |
| GET    | /books/get-books-by-author/{author} | Get books by author   |
| PUT    | /books/update-book/{id}             | Update book details   |
| PATCH  | /books/update-inventory/{id}        | Update book inventory |
| DELETE | /books/delete-book/{id}             | Delete book           |

### 🛒 Cart

| Method | Endpoint               | Description             |
| ------ | ---------------------- | ----------------------- |
| POST   | /cart/add-item         | Add item to cart        |
| PATCH  | /cart/update-item/{id} | Update item in cart     |
| DELETE | /cart/remove-item/{id} | Remove item from cart   |
| GET    | /cart/get-cart         | Get current user's cart |

### 📦 Orders

| Method | Endpoint                                     | Description                  |
| ------ | -------------------------------------------- | ---------------------------- |
| POST   | /order/                                      | Place order                  |
| GET    | /order/get-order-details                     | Get all orders               |
| GET    | /order/get-order/{order\_id}                 | Get order by ID              |
| DELETE | /order/delete-order/{order\_id}              | Delete order & restore stock |
| PATCH  | /order/update-address-in-address/{order\_id} | Update order address         |

### 💳 Payments

| Method | Endpoint                            | Description                    |
| ------ | ----------------------------------- | ------------------------------ |
| POST   | /payments/{ord\_id}                 | Attempt payment for order      |
| PATCH  | /payments/soft-delete/{payment\_id} | Soft-delete payment & rollback |

### 🚚 Shipping

| Method | Endpoint                       | Description                     |
| ------ | ------------------------------ | ------------------------------- |
| POST   | /shipping-cost/add-cost        | Add shipping cost for a country |
| GET    | /shipping-cost/                | Get all shipping costs          |
| GET    | /shipping-cost/{country\_name} | Get cost by country name        |
| PATCH  | /shipping-cost/{id}            | Update shipping cost row        |
| DELETE | /shipping-cost/{id}            | Delete shipping cost row        |

### 👥 Users

| Method | Endpoint            | Description         |
| ------ | ------------------- | ------------------- |
| POST   | /user/add-user      | Create a new user   |
| GET    | /user/get-all-users | List all users      |
| PUT    | /user/{user\_id}    | Update user details |
| DELETE | /user/{user\_id}    | Delete a user       |

### 🔐 Auth & Roles

| Method | Endpoint                | Description       |
| ------ | ----------------------- | ----------------- |
| POST   | /auth/login             | User login        |
| POST   | /roles/create-role      | Create a new role |
| GET    | /roles/get-all-roles    | Get all roles     |
| PUT    | /roles/update-role/{id} | Update role       |
| DELETE | /roles/delete-role/{id} | Delete role       |

---

## 🧪 Sample User Flow

1. 🔐 Register or login
2. 📘️ Browse books
3. ➕ Add items to cart
4. 📦 Place order
5. 💳 Make payment (simulate)
6. ↻ Retry up to 3 times
7. ❌ On failure, rollback stock
8. 🧹 Soft delete if needed

---

## 🛠️ Setup Instructions

### 🔧 Prerequisites

* Python 3.10+
* PostgreSQL installed
* `virtualenv` or `venv` recommended

### 📅 Clone and Install

```bash
git clone https://github.com/<your-username>/bookstore-backend.git
cd bookstore-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### ⚙️ Environment Variables (`.env`)

```
DATABASE_URL=postgresql://<user>:<password>@localhost/<dbname>
JWT_SECRET_KEY=your-super-secret-key
```

### 🛠️ Run Migrations (if using Alembic)

```bash
alembic upgrade head
```

### 🚀 Start the Server

```bash
uvicorn main:app --reload
```

---

## 📌 Notes

* Modular design: routes, services, queries, schemas
* Business logic wrapped with rollback-safe try/except
* Transaction logic simulates real-world payment flow

---

## 👨‍💼 Author

Made with ❤️ by [**Himanshu Baid**](https://github.com/baidhimanshu)

---

## 📄 License

This project is licensed under the **MIT License**.
