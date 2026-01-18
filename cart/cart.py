from decimal import Decimal
from typing import Dict, List, Tuple

from catalog.models import Product


SESSION_KEY = "cart"  # { "product_id": qty }


def get_cart(session) -> Dict[str, int]:
    cart = session.get(SESSION_KEY)
    if not isinstance(cart, dict):
        cart = {}
        session[SESSION_KEY] = cart
    return cart


def save_cart(session, cart: Dict[str, int]) -> None:
    session[SESSION_KEY] = cart
    session.modified = True


def add(session, product_id: int, qty: int = 1) -> None:
    cart = get_cart(session)
    key = str(product_id)
    cart[key] = int(cart.get(key, 0)) + int(qty)
    if cart[key] <= 0:
        cart.pop(key, None)
    save_cart(session, cart)


def set_qty(session, product_id: int, qty: int) -> None:
    cart = get_cart(session)
    key = str(product_id)
    qty = int(qty)
    if qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = qty
    save_cart(session, cart)


def remove(session, product_id: int) -> None:
    cart = get_cart(session)
    cart.pop(str(product_id), None)
    save_cart(session, cart)


def clear(session) -> None:
    save_cart(session, {})


def items(session) -> List[Tuple[Product, int, Decimal]]:
    """
    Returns list of (product, qty, line_total)
    """
    cart = get_cart(session)
    ids = [int(pid) for pid in cart.keys()] if cart else []
    products = {p.id: p for p in Product.objects.filter(id__in=ids, is_active=True).select_related("artisan", "artisan__user")}
    out = []
    for pid_str, qty in cart.items():
        pid = int(pid_str)
        p = products.get(pid)
        if not p:
            continue
        line_total = (p.price or Decimal("0.00")) * int(qty)
        out.append((p, int(qty), line_total))
    return out


def totals(session) -> Tuple[Decimal, int]:
    """
    Returns (subtotal, total_qty)
    """
    subtotal = Decimal("0.00")
    total_qty = 0
    for _, qty, line_total in items(session):
        subtotal += line_total
        total_qty += qty
    return subtotal, total_qty
