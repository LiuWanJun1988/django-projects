from cart.forms import CartAddProductForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.core.urlresolvers import reverse
from django.views.generic import UpdateView
from orders.models import OrderItem, Order
from django.shortcuts import render, get_object_or_404, redirect

from .models import Category, Product


# def signup(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             msg = "Hello " + user.username + ". Welcome to OnionShop."
#             messages.success(request, msg)
#             return redirect("product_list")
#     else:
#         form = SignUpForm()
#     return render(request, 'registration/signup.html', {'form': form})
#
#
# def signin(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             msg = "Welcome back" + user.username
#             messages.success(request, msg)
#             return redirect("product_list")
#     else:
#         form = LoginForm(request)
#     return render(request, 'registration/login.html', {'form': form})


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category)

    context = {
        'category': category,
        'categories': categories,
        'products': products
    }
    return render(request, 'main/product/list.html', context)


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    context = {
        'product': product,
        'cart_product_form': cart_product_form
    }
    return render(request, 'main/product/detail.html', context)


# def user_profile(request):
#     if request.user.is_authenticated:
#         context = {
#             'object': request.user,
#         }
#         return render(request, 'main/profile/user-profile.html', context)
#     else:
#         return render(request, 'main/nlogin.html')
#
#
# class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
#     form_class = UserProfileChangeForm
#
#     def get_object(self, queryset=None):
#         return self.request.user
#
#     def get_success_url(self):
#         return redirect("user_profile")
#
#
# def profile_orders(request):
#     if request.user.is_authenticated is True:
#         orders = Order.objects.filter(user=request.user)
#         context = {
#             'orders': orders,
#         }
#         return render(request, 'main/profile/order-list.html', context)
#     else:
#         return render(request, 'main/nlogin.html')
#
#
# def profile_order(request, order_id):
#     if request.user.is_authenticated is True:
#         orders = OrderItem.objects.filter(order_id=order_id, author=request.user)
#
#         context = {
#             'orders': orders,
#         }
#         return render(request, 'main/profile/order-detail.html', context)
#     else:
#         return render(request, 'main/nlogin.html')
#
