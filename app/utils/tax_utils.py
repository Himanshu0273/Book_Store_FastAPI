def calculate_tax(
    cart_cost: float, shipping_cost: float, tax_rate: float = 0.18
) -> float:
    """
    Calculate tax based on cart cost and shipping cost.

    Args:
        cart_cost (float): Total cost of items in the cart.
        shipping_cost (float): Total shipping cost.
        tax_rate (float): Tax rate as a decimal (default is 18%).

    Returns:
        float: Calculated tax amount rounded to 2 decimal places.
    """
    if cart_cost < 0 or shipping_cost < 0:
        raise ValueError("Cart cost and shipping cost must be non-negative.")

    total_taxable = cart_cost + shipping_cost
    tax = total_taxable * tax_rate
    return round(tax, 2)
