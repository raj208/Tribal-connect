from .cart import totals


def cart_badge(request):
    try:
        _, total_qty = totals(request.session)
    except Exception:
        total_qty = 0
    return {"cart_qty": total_qty}
