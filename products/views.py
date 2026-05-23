from django.shortcuts import render, redirect
from django.views.generic import (
    ListView,
    DeleteView,
    DetailView,
    CreateView,
    UpdateView
)
from .models import Product, Category, Order, OrderItem, Brand
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY


# ─── Product CRUD Views ────────────────────────────────────────────────────────

class ProductListView(ListView):
    template_name = "products/list.html"
    model = Product
    context_object_name = 'products'

    def get_queryset(self):
        category = self.request.GET.get("category")
        if not category:
            return Product.objects.all()
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


class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'products/new.html'
    model = Product
    fields = ["img", "title", "brand", "category", "description", "price", "quantity"]

    def test_func(self):
        return self.request.user.is_staff


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'products/edit.html'
    model = Product
    fields = ["img", "title", "brand", "category", "description", "price", "quantity"]

    def test_func(self):
        return self.request.user.is_staff


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = 'products/delete.html'
    model = Product
    success_url = reverse_lazy('product_list')
    context_object_name = 'item'

    def test_func(self):
        return self.request.user.is_staff


# ─── Cart Views ───────────────────────────────────────────────────────────────

@login_required
def add_to_cart(request):
    product_id = request.POST.get("product_id")
    if not product_id:
        return redirect("product_list")

    quantity = int(request.POST.get("quantity", 1))
    product = Product.objects.get(id=product_id)

    order, created = Order.objects.get_or_create(
        user=request.user, paid=False, defaults={"total": 0}
    )

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
        order = item.order
        item.delete()
        order.total = sum(
            i.product.price * i.quantity
            for i in OrderItem.objects.filter(order=order)
        )
        order.save()
    return redirect("cart")


@login_required
def cart(request):
    order = Order.objects.filter(user=request.user, paid=False).first()

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


# ─── Stripe Checkout ──────────────────────────────────────────────────────────

@login_required
def checkout(request):
    """
    Renders the checkout page and creates a Stripe PaymentIntent
    so the frontend can mount Stripe Elements and collect card details.
    """
    order = Order.objects.filter(user=request.user, paid=False).first()
    if not order:
        return redirect("product_list")

    items = OrderItem.objects.filter(order=order).select_related('product')

    # Amount in cents — Stripe requires integer cents
    amount_cents = int(order.total * 100)

    # Create (or reuse) a PaymentIntent stored on the order
    # We store the intent ID on the order so we can reuse it on page reload
    if not getattr(order, 'stripe_payment_intent_id', None):
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='usd',
            metadata={
                'order_id': order.id,
                'user_id': request.user.id,
            },
        )
        order.stripe_payment_intent_id = intent['id']
        order.save()
    else:
        # Update amount in case cart changed
        stripe.PaymentIntent.modify(
            order.stripe_payment_intent_id,
            amount=amount_cents,
        )
        intent = stripe.PaymentIntent.retrieve(order.stripe_payment_intent_id)

    return render(request, "products/checkout.html", {
        "order": order,
        "items": items,
        "client_secret": intent['client_secret'],
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
    })


@login_required
@require_POST
def payment_success(request):
    """
    Called by the frontend after Stripe confirms the payment.
    Verifies the PaymentIntent server-side before marking the order paid.
    """
    data = json.loads(request.body)
    payment_intent_id = data.get('payment_intent_id')

    if not payment_intent_id:
        return JsonResponse({'error': 'Missing payment_intent_id'}, status=400)

    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)}, status=400)

    if intent['status'] != 'succeeded':
        return JsonResponse({'error': 'Payment not successful'}, status=400)

    # Match the order by the stored intent ID
    try:
        order = Order.objects.get(
            stripe_payment_intent_id=payment_intent_id,
            user=request.user,
            paid=False,
        )
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    from django.utils import timezone
    order.paid = True
    order.paid_at = timezone.now()
    order.save()

    return JsonResponse({'redirect': reverse('order_confirmation')})


@csrf_exempt
def stripe_webhook(request):
    """
    Optional but recommended: handle Stripe webhook events for
    asynchronous payment confirmation (e.g. bank transfers, disputes).
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        order_id = intent['metadata'].get('order_id')

        try:
            order = Order.objects.get(id=order_id, paid=False)
            from django.utils import timezone
            order.paid = True
            order.paid_at = timezone.now()
            order.stripe_payment_intent_id = intent['id']
            order.save()
        except Order.DoesNotExist:
            pass  # Already marked paid or not found — safe to ignore

    return HttpResponse(status=200)


@login_required
def order_confirmation(request):
    order = Order.objects.filter(
        user=request.user, paid=True
    ).order_by('-paid_at').first()
    return render(request, "products/order_confirmation.html", {"order": order})