from .models import Order, OrderItem

def cart_item_count(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, paid=False).first()
        if order:
            count = OrderItem.objects.filter(order=order).count()
            return {'cart_item_count': count}
    return {'cart_item_count': 0}