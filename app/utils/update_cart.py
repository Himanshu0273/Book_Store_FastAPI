from datetime import datetime, timezone
from app.models.cart_model import Cart

def update_cart_totals(cart: Cart):
    cart.total_books = sum(ci.quantity for ci in cart.items)
    cart.total_cost = sum(ci.quantity * ci.price_when_added for ci in cart.items)
    cart.updated_at = datetime.now(timezone.utc)