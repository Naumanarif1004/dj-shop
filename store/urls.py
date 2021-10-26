"""ecommerce_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path,include
from .views import *

urlpatterns = [
    path('',home,name="home"),
    path('category/<slug:category_slug>',home,name="products_by_category"),
    path('category/<slug:category_slug>/<slug:product_slug>',product,name="product_detail"),
    path('cart/add/<int:product_id>',add_cart,name="add_cart"),
    path('cart',cart_detail,name='cart_detail'),
    path('cart/remove/<int:product_id>',cart_remove,name="remove_cart"),
    path('cart/removeItem/<int:product_id>',cartItem_remove,name="remove_cartItem"),
    path('thankyou/<int:order_id>',thanks_page,name="thanks_page"),
    path('account/create/',signupview,name="sign_up"),
    path('account/signin/',signinview,name="sign_in"),
    path('account/signout/',signoutView,name="sign_out"),
    path('orderhistory/',orderHistory,name="order_history"),
    path('order/<int:order_id>',ViewOrder,name="order_detail"),
    path('search/',search,name="search"),
    path('contact/',Contact,name="contact"),

]
