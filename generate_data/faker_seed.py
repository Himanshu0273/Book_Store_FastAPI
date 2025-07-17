#!/usr/bin/env python3
"""
Fake Data Generator for Bookstore Database
Generates realistic fake data for all tables in the bookstore database
"""

import os
import random
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.models.book_model import Book
from app.models.cart_item_model import CartItem
from app.models.cart_model import Cart
from app.models.inventory_model import Inventory
from app.models.orders_model import Order
from app.models.payments_model import Payments
from app.models.roles_model import Roles
from app.models.shipping_cost_model import ShippingCost
from app.models.transaction_model import Transactions
# Import models
from app.models.user_model import User

# Import enums (assuming these exist in your utils)
try:
    from app.utils.enums import (CartActivityEnum, GenreEnum,
                                 PaymentMethodEnum, PaymentsEnum,
                                 TransactionStatusEnum)
except ImportError:
    # Fallback enum definitions if import fails
    from enum import Enum

    class GenreEnum(Enum):
        FICTION = "fiction"
        NON_FICTION = "non_fiction"
        MYSTERY = "mystery"
        ROMANCE = "romance"
        SCIENCE_FICTION = "science_fiction"
        FANTASY = "fantasy"
        BIOGRAPHY = "biography"
        HISTORY = "history"
        SELF_HELP = "self_help"
        BUSINESS = "business"
        TECHNOLOGY = "technology"
        COOKING = "cooking"
        TRAVEL = "travel"
        HEALTH = "health"
        CHILDREN = "children"
        EDUCATION = "education"
        POETRY = "poetry"
        DRAMA = "drama"
        HORROR = "horror"
        THRILLER = "thriller"

    class CartActivityEnum(Enum):
        ACTIVE = "active"
        ABANDONED = "abandoned"
        COMPLETED = "completed"
        EXPIRED = "expired"

    class PaymentsEnum(Enum):
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCELLED = "cancelled"
        REFUNDED = "refunded"

    class PaymentMethodEnum(Enum):
        CREDIT_CARD = "credit_card"
        DEBIT_CARD = "debit_card"
        PAYPAL = "paypal"
        STRIPE = "stripe"
        BANK_TRANSFER = "bank_transfer"
        CASH_ON_DELIVERY = "cash_on_delivery"
        DIGITAL_WALLET = "digital_wallet"

    class TransactionStatusEnum(Enum):
        INITIATED = "initiated"
        PENDING = "pending"
        SUCCESS = "success"
        FAILED = "failed"
        CANCELLED = "cancelled"
        TIMEOUT = "timeout"
        DECLINED = "declined"


# Database configuration
DATABASE_URL = "postgresql://postgres:root@localhost:5432/bookstoredb"

# Initialize Faker
fake = Faker()

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def clear_database():
    """Clear all data from database tables"""
    with engine.connect() as conn:
        # Disable foreign key checks temporarily
        conn.execute(text("SET session_replication_role = replica;"))

        # Clear all tables in reverse dependency order
        tables = [
            "transactions",
            "payments",
            "orders",
            "cart_items",
            "carts",
            "inventory",
            "book",
            "users",
            "roles",
            "shipping_cost",
        ]

        for table in tables:
            conn.execute(text(f"DELETE FROM {table};"))
            conn.execute(text(f"ALTER SEQUENCE {table}_id_seq RESTART WITH 1;"))

        # Re-enable foreign key checks
        conn.execute(text("SET session_replication_role = DEFAULT;"))
        conn.commit()


def generate_roles():
    """Generate role data"""
    session = SessionLocal()
    try:
        roles_data = [
            {"role_name": "admin"},
            {"role_name": "customer"},
            {"role_name": "moderator"},
            {"role_name": "staff"},
        ]

        for role_data in roles_data:
            role = Roles(**role_data)
            session.add(role)

        session.commit()
        print("✓ Generated roles")
        return [r.id for r in session.query(Roles).all()]
    except Exception as e:
        session.rollback()
        print(f"Error generating roles: {e}")
        return []
    finally:
        session.close()


def generate_shipping_costs():
    """Generate shipping cost data"""
    session = SessionLocal()
    try:
        countries = [
            "India",
            "USA",
            "UK",
            "Canada",
            "Australia",
            "Germany",
            "France",
            "Japan",
            "Brazil",
            "Mexico",
            "Italy",
            "Spain",
            "Netherlands",
            "Sweden",
            "Norway",
            "Denmark",
            "Finland",
            "Belgium",
            "Switzerland",
            "Austria",
            "Portugal",
            "Ireland",
            "New Zealand",
            "Singapore",
            "South Korea",
            "Thailand",
            "Malaysia",
            "Philippines",
            "Indonesia",
        ]

        for country in countries:
            cost = round(random.uniform(5.0, 50.0), 2)
            shipping_cost = ShippingCost(country=country, cost=cost)
            session.add(shipping_cost)

        session.commit()
        print("✓ Generated shipping costs")
    except Exception as e:
        session.rollback()
        print(f"Error generating shipping costs: {e}")
    finally:
        session.close()


def generate_users(num_users=100):
    """Generate user data"""
    session = SessionLocal()
    try:
        role_ids = [r.id for r in session.query(Roles).all()]
        if not role_ids:
            print("No roles found. Generate roles first.")
            return []

        users = []
        countries = [
            "India",
            "USA",
            "UK",
            "Canada",
            "Australia",
            "Germany",
            "France",
            "Japan",
        ]

        for i in range(num_users):
            try:
                user = User(
                    email=fake.unique.email(),
                    password=fake.password(length=12),
                    role_id=random.choice(role_ids),
                    country=random.choice(countries),
                    created_at=fake.date_time_between(start_date="-2y", end_date="now"),
                )
                session.add(user)
                users.append(user)

                if i % 50 == 0:
                    session.commit()

            except IntegrityError:
                session.rollback()
                continue

        session.commit()
        print(f"✓ Generated {len(users)} users")
        return [u.id for u in session.query(User).all()]
    except Exception as e:
        session.rollback()
        print(f"Error generating users: {e}")
        return []
    finally:
        session.close()


def generate_books(num_books=1000):
    """Generate book data"""
    session = SessionLocal()
    try:
        books = []
        genres = list(GenreEnum)

        # Book title templates for variety
        title_templates = [
            "The {adjective} {noun}",
            "{adjective} {noun}",
            "A {adjective} Guide to {noun}",
            "The Art of {noun}",
            "Beyond {noun}",
            "The {noun} Chronicles",
            "Mastering {noun}",
            "The Complete {noun}",
            "Understanding {noun}",
            "The {adjective} {noun} Handbook",
        ]

        adjectives = [
            "Great",
            "Amazing",
            "Ultimate",
            "Complete",
            "Perfect",
            "Essential",
            "Advanced",
            "Modern",
            "Classic",
            "Revolutionary",
            "Comprehensive",
        ]
        nouns = [
            "Adventure",
            "Mystery",
            "Journey",
            "Discovery",
            "Challenge",
            "Success",
            "Innovation",
            "Transformation",
            "Leadership",
            "Excellence",
            "Wisdom",
        ]

        for i in range(num_books):
            try:
                # Generate unique title
                template = random.choice(title_templates)
                title = template.format(
                    adjective=random.choice(adjectives), noun=random.choice(nouns)
                )
                title = f"{title} - {fake.catch_phrase()}"

                book = Book(
                    title=title[:149],  # Ensure it fits in 150 chars
                    author=fake.name(),
                    genre=random.choice(genres),
                    desc=fake.text(max_nb_chars=500),
                    year=str(random.randint(1950, 2024)),
                    price=round(random.uniform(9.99, 199.99), 2),
                    image=f"https://picsum.photos/300/400?random={i}",
                    avg_rating=(
                        round(random.uniform(1.0, 5.0), 1)
                        if random.random() > 0.3
                        else None
                    ),
                    added_on=fake.date_between(start_date="-2y", end_date="today"),
                    purchased=random.randint(0, 1000),
                )

                session.add(book)
                books.append(book)

                if i % 100 == 0:
                    session.commit()

            except IntegrityError:
                session.rollback()
                continue

        session.commit()
        print(f"✓ Generated {len(books)} books")
        return [b.id for b in session.query(Book).all()]
    except Exception as e:
        session.rollback()
        print(f"Error generating books: {e}")
        return []
    finally:
        session.close()


def generate_inventory():
    """Generate inventory data for all books"""
    session = SessionLocal()
    try:
        book_ids = [b.id for b in session.query(Book).all()]

        for book_id in book_ids:
            inventory = Inventory(book_id=book_id, quantity=random.randint(0, 500))
            session.add(inventory)

        session.commit()
        print(f"✓ Generated inventory for {len(book_ids)} books")
    except Exception as e:
        session.rollback()
        print(f"Error generating inventory: {e}")
    finally:
        session.close()


def generate_carts(user_ids, book_ids):
    """Generate cart data"""
    session = SessionLocal()
    try:
        carts = []
        cart_statuses = list(CartActivityEnum)

        # Generate 1-2 carts per user (reduce to ensure we have enough for orders)
        for user_id in user_ids:
            num_carts = random.randint(1, 2)
            for _ in range(num_carts):
                # Bias towards active carts (80% active, 20% other statuses)
                if random.random() < 0.8:
                    status = CartActivityEnum.ACTIVE
                else:
                    status = random.choice(cart_statuses)

                cart = Cart(
                    user_id=user_id,
                    total_cost=0.0,  # Will be updated when adding items
                    total_books=0,  # Will be updated when adding items
                    status=status,
                    created_at=fake.date_time_between(start_date="-1y", end_date="now"),
                    updated_at=fake.date_time_between(start_date="-1y", end_date="now"),
                )
                session.add(cart)
                carts.append(cart)

        session.commit()

        # Print status distribution for debugging
        status_counts = {}
        for status in CartActivityEnum:
            count = session.query(Cart).filter(Cart.status == status).count()
            status_counts[status.value] = count

        print(
            f"✓ Generated {len(carts)} carts with status distribution: {status_counts}"
        )
        return [c.id for c in session.query(Cart).all()]
    except Exception as e:
        session.rollback()
        print(f"Error generating carts: {e}")
        return []
    finally:
        session.close()


def generate_cart_items(cart_ids, book_ids):
    """Generate cart items"""
    session = SessionLocal()
    try:
        cart_items = []

        for cart_id in cart_ids:
            # Add 1-8 items per cart
            num_items = random.randint(1, 8)
            selected_books = random.sample(book_ids, min(num_items, len(book_ids)))

            total_cost = 0.0
            total_books = 0

            for book_id in selected_books:
                book = session.query(Book).filter(Book.id == book_id).first()
                if book:
                    quantity = random.randint(1, 5)
                    cart_item = CartItem(
                        cart_id=cart_id,
                        book_id=book_id,
                        quantity=quantity,
                        price_when_added=book.price,
                        created_at=fake.date_time_between(
                            start_date="-1y", end_date="now"
                        ),
                        updated_at=fake.date_time_between(
                            start_date="-1y", end_date="now"
                        ),
                    )
                    session.add(cart_item)
                    cart_items.append(cart_item)

                    total_cost += book.price * quantity
                    total_books += quantity

            # Update cart totals
            cart = session.query(Cart).filter(Cart.id == cart_id).first()
            if cart:
                cart.total_cost = round(total_cost, 2)
                cart.total_books = total_books

        session.commit()
        print(f"✓ Generated {len(cart_items)} cart items")
        return [ci.id for ci in session.query(CartItem).all()]
    except Exception as e:
        session.rollback()
        print(f"Error generating cart items: {e}")
        return []
    finally:
        session.close()


def generate_orders(user_ids, cart_ids):
    """Generate order data"""
    session = SessionLocal()
    try:
        orders = []
        payment_statuses = list(PaymentsEnum)
        countries = [
            "India",
            "USA",
            "UK",
            "Canada",
            "Australia",
            "Germany",
            "France",
            "Japan",
        ]

        # Get all carts and mark some as completed to create orders
        all_carts = session.query(Cart).all()

        # Take 60% of carts to create orders (simulate realistic conversion rate)
        num_orders = min(600, int(len(all_carts) * 0.6))
        selected_carts = random.sample(all_carts, num_orders)

        # for cart in selected_carts:
        for cart in selected_carts:
            # Mark cart as completed since we're creating an order for it
            cart.status = CartActivityEnum.COMPLETED

            shipping_cost = round(random.uniform(5.0, 25.0), 2)
            taxes = round(cart.total_cost * 0.08, 2)  # 8% tax
            total = round(cart.total_cost + shipping_cost + taxes, 2)

            order = Order(
                user_id=cart.user_id,
                cart_id=cart.id,
                cart_cost=cart.total_cost,
                shipping_cost=shipping_cost,
                taxes=taxes,
                total=total,
                shipping_address=fake.address(),
                country=random.choice(countries),
                date=fake.date_time_between(start_date="-1y", end_date="now"),
                payment_status=random.choice(payment_statuses),
            )
            session.add(order)
            orders.append(order)

        session.commit()
        print(
            f"✓ Generated {len(orders)} orders from {len(selected_carts)} selected carts"
        )
        return [o.id for o in session.query(Order).all()]
    except Exception as e:
        session.rollback()
        print(f"Error generating orders: {e}")
        return []
    finally:
        session.close()


def generate_payments(order_ids):
    """Generate payment data"""
    session = SessionLocal()
    try:
        payments = []
        payment_methods = list(PaymentMethodEnum)
        payment_statuses = list(PaymentsEnum)

        for order_id in order_ids:
            order = session.query(Order).filter(Order.id == order_id).first()
            if order:
                payment = Payments(
                    order_id=order_id,
                    total_cost=order.total,
                    mode_of_payment=random.choice(payment_methods),
                    attempts=random.randint(1, 3),
                    status=order.payment_status,
                    created_at=fake.date_time_between(start_date="-1y", end_date="now"),
                )
                session.add(payment)
                payments.append(payment)

        session.commit()
        print(f"✓ Generated {len(payments)} payments for {len(order_ids)} orders")
        return [p.id for p in session.query(Payments).all()]
    except Exception as e:
        session.rollback()
        print(f"Error generating payments: {e}")
        return []
    finally:
        session.close()


def generate_transactions(payment_ids):
    """Generate transaction data"""
    session = SessionLocal()
    try:
        transactions = []
        transaction_statuses = list(TransactionStatusEnum)

        for payment_id in payment_ids:
            payment = session.query(Payments).filter(Payments.id == payment_id).first()
            if payment:
                # Generate 1-3 transactions per payment (retries, etc.)
                num_transactions = random.randint(1, payment.attempts)

                for i in range(num_transactions):
                    status = random.choice(transaction_statuses)

                    # Generate appropriate message based on status
                    messages = {
                        TransactionStatusEnum.SUCCESS: "Transaction completed successfully",
                        TransactionStatusEnum.FAILED: "Transaction failed due to insufficient funds",
                        TransactionStatusEnum.CANCELLED: "Transaction cancelled by user",
                        TransactionStatusEnum.TIMEOUT: "Transaction timed out",
                        TransactionStatusEnum.DECLINED: "Transaction declined by bank",
                        TransactionStatusEnum.PENDING: "Transaction is being processed",
                        TransactionStatusEnum.INITIATED: "Transaction initiated",
                    }

                    transaction = Transactions(
                        payment_id=payment_id,
                        status=status,
                        message=messages.get(status, "Transaction processed"),
                        created_at=fake.date_time_between(
                            start_date="-1y", end_date="now"
                        ),
                    )
                    session.add(transaction)
                    transactions.append(transaction)

        session.commit()
        print(
            f"✓ Generated {len(transactions)} transactions for {len(payment_ids)} payments"
        )
    except Exception as e:
        session.rollback()
        print(f"Error generating transactions: {e}")
    finally:
        session.close()


def main():
    """Main function to generate all fake data"""
    print("🚀 Starting fake data generation for bookstore database...")
    print("=" * 60)

    # Clear existing data
    print("🗑️  Clearing existing data...")
    clear_database()

    # Generate data in dependency order
    print("\n📝 Generating fake data...")

    # 1. Generate roles
    role_ids = generate_roles()

    # 2. Generate shipping costs
    generate_shipping_costs()

    # 3. Generate users
    user_ids = generate_users(100)

    # 4. Generate books
    book_ids = generate_books(1000)

    # 5. Generate inventory
    generate_inventory()

    # 6. Generate carts
    cart_ids = generate_carts(user_ids, book_ids)

    # 7. Generate cart items
    cart_item_ids = generate_cart_items(cart_ids, book_ids)

    # 8. Generate orders
    order_ids = generate_orders(user_ids, cart_ids)

    # 9. Generate payments
    payment_ids = generate_payments(order_ids)

    # 10. Generate transactions
    generate_transactions(payment_ids)

    print("\n" + "=" * 60)
    print("✅ Fake data generation completed successfully!")
    print("\n📊 Summary:")
    print(f"   • Users: {len(user_ids)}")
    print(f"   • Books: {len(book_ids)}")
    print(f"   • Carts: {len(cart_ids)}")
    print(f"   • Cart Items: {len(cart_item_ids)}")
    print(f"   • Orders: {len(order_ids)}")
    print(f"   • Payments: {len(payment_ids)}")
    print(f"   • Roles: {len(role_ids)}")
    print(f"   • Shipping Costs: 29 countries")

    # Additional verification
    session = SessionLocal()
    try:
        transaction_count = session.query(Transactions).count()
        print(f"   • Transactions: {transaction_count}")
    except Exception as e:
        print(f"   • Transactions: Error counting - {e}")
    finally:
        session.close()

    print("\n🎉 Your bookstore database is now populated with realistic fake data!")


if __name__ == "__main__":
    main()
