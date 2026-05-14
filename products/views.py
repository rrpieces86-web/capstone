from django.shortcuts import render, redirect
from django.views.generic import (
    ListView,
    DeleteView,
    DetailView,
    CreateView, 
    UpdateView
)
from .models import Product, Category, Order, OrderItem, Brand
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required

# Create your views here.
class ProductListView(ListView):
    template_name = "products/list.html"
    model = Product
    context_object_name = 'products'
    
    def get_queryset(self):
        category = self.request.GET.get("category")

        if not category:
            return Product.objects.all()
        else:
            return Product.objects.filter(category__name__iexact=category)
        


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category')
        return context

class ProductDetailView(DetailView):
    template_name = 'products/detail.html'
    model = Product
    context_object_name = 'single_product'

class ProductCreateView(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    template_name = 'products/new.html'
    model = Product
    fields = ["img", "title", "brand", "category", "description", "price", "quantity"]

    def test_func(self):
        return self.request.user.is_staff
    

class ProductUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    template_name = 'products/edit.html'
    model = Product
    fields = ["img", "title", "brand", "category", "description", "price", "quantity"]

    def test_func(self):
        return self.request.user.is_staff

class ProductDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    template_name = 'products/delete.html'
    model = Product
    success_url = reverse_lazy('product_list')
    context_object_name = 'item'

    def test_func(self):
        return self.request.user.is_staff
@login_required    
def add_to_cart(request):

    # get the data
    product_id = request.POST.get("product_id")
    if not product_id:
        return redirect("product_list")
    quantity = int(request.POST.get("quantity", 1))
    user = request.user  #logged in user

    product = Product.objects.get(id=product_id)


    # get/create the order
    order, created = Order.objects.get_or_create(user=user, paid=False, defaults= {"total": 0, "paid": False})

    existing_item = OrderItem.objects.filter(order=order, product=product).first()
    if existing_item:
        existing_item.quantity += quantity
        existing_item.save()
    else:
        OrderItem.objects.create(order=order, product=product, quantity=quantity)
    order.total = sum(
        item.product.price * item.quantity
        for item in OrderItem.objects.filter(order=order)
    )
    order.save()

    return redirect("cart")

@login_required
def remove_from_cart(request, item_id):
    item = OrderItem.objects.filter(id=item_id, order__user=request.user).first()
    if item:
        order= item.order
        item.delete()
        order.total = sum(
            i.product.price * i.quantity
            for i in OrderItem.objects.filter(order=order)
        )
        order.save()
    return redirect("cart")

@login_required
def cart(request):
    user = request.user
    order = Order.objects.filter(user=user, paid=False).first()

    if not order:
        items = []
        total = 0
    else:
        items = OrderItem.objects.filter(order=order).select_related('product')
        total = order.total

    return render(request, "products/cart.html", {
        "order": order,
        "items": items,
        "total": total,
    })


@login_required
def checkout(request):
    user = request.user
    order = Order.objects.filter(user=user, paid=False).first()

    if not order:
        return redirect("product_list")
    
    items = OrderItem.objects.filter(order=order).select_related('product')

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        # Mark order as paid (in a real app you'd intergrate a payment gateway here)
        from django.utils import timezone
        order.paid = True
        order.paid_at = timezone.now()
        order.save()
        return redirect("order_confirmation")
    
    return render(request, "products/checkout.html", {
        "order": order,
        "items": items,
    })

@login_required
def order_confirmation(request):
    # get most recent paid order
    order = Order.objects.filter(user=request.user, paid=True).order_by('-paid_at').first()
    return render(request, "products/order_confirmation.html", {"order": order})
   
