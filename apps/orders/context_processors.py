from apps.orders.cart import Cart

def cart_info(request):
    c = Cart(request)
    return {"cart_count": len(c)}
