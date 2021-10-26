from django.shortcuts import render, get_object_or_404,redirect

from .models import Product,Category,Cart,CartItem,Order,OrderItem
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import stripe
from django.contrib.auth.models import Group,User
from .forms import SignupForm,ContactForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from .helpers import sendEmail,EmailFunction,session_login
def home(request,category_slug=None):
    category_page = None
    products = None
    if category_slug != None:
        category_page = get_object_or_404(Category,slug=category_slug)
        products = Product.objects.filter(category=category_page,available=True)
    else:
        products = Product.objects.filter(available=True)

    context = {
        'products':products,
        'category':category_page
    }
    return render(request,'home.html',context)

def product(request,category_slug,product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug,slug=product_slug)
    except Exception as e:
        raise e

    return render(request,'product.html',{'product':product})

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return  cart

def add_cart(request,product_id):
    product = Product.objects.get(id=product_id)

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))

    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

    try:
        cart_items = CartItem.objects.get(product=product, cart=cart)
        if cart_items.quantity < cart_items.product.stock:
            cart_items.quantity += 1
        cart_items.save()

    except CartItem.DoesNotExist:
        cart_items = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        cart_items.save()

    return redirect('cart_detail')

def cart_detail(request,total=0,counter=0,cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart,active=True)
        for cart_item in cart_items:
            total +=(cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity

    except ObjectDoesNotExist:
        pass
    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_total = int(total*100)
    description = 'Z-Store - New Order'
    data_key = settings.STRIPE_PUBLISHABLE_KEY
    if request.method == 'POST':
        try:
            token = request.POST['stripeToken']
            email = request.POST['stripeEmail']
            billingName = request.POST['stripeBillingName']
            billingAddress1 = request.POST['stripeBillingAddressLine1']
            billingCity = request.POST['stripeBillingAddressCity']
            billingPostcode = request.POST['stripeBillingAddressZip']
            billingCountry = request.POST['stripeBillingAddressCountryCode']
            shippingName = request.POST['stripeShippingName']
            shippingAddress1 = request.POST['stripeShippingAddressLine1']
            shippingCity = request.POST['stripeShippingAddressCity']
            shippingPostcode = request.POST['stripeShippingAddressZip']
            shippingCountry = request.POST['stripeShippingAddressCountryCode']
            customer = stripe.Customer.create(
                email=email,
                source=token
            )
            charge = stripe.Charge.create(
                amount=stripe_total,
                currency='usd',
                description=description,
                customer=customer.id
            )
            try:
                order_details = Order.objects.create(
                    token=token,
                    total=total,
                    emailAddress=email,
                    billingName=billingName,
                    billingAddress1=billingAddress1,
                    billingCity=billingCity,
                    billingPostcode=billingPostcode,
                    billingCountry=billingCountry,
                    shippingName=shippingName,
                    shippingAddress1=shippingAddress1,
                    shippingCity=shippingCity,
                    shippingPostcode=shippingPostcode,
                    shippingCountry=shippingCountry
                )
                order_details.save()
                for order_item in cart_items:
                    OrderItem.objects.create(
                        product=order_item.product.name,
                        quantity=order_item.quantity,
                        price=order_item.product.price,
                        order=order_details
                    ).save()
                #reduce stock after order
                    product = Product.objects.get(id=order_item.product.id)
                    product.stock = int(order_item.product.stock - order_item.quantity)
                    product.save()
                    order_item.delete()
                    print('Order has been created')
                try:
                    sendEmail(order_details.id)
                    print('The order email has been sent')
                except IOError as e:
                    return e

                return redirect('thanks_page',order_details.id)
            except ObjectDoesNotExist:
                pass
        except stripe.error.CardError as e:
            return False, e

    return render(request,'cart.html',dict(cart_items=cart_items,total=total,counter=counter,data_key=data_key,description=description,stripe_total=stripe_total))

def cart_remove(request,product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product,id = product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    if cart_item.quantity > 1:

        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_detail')

def cartItem_remove(request,product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product,id = product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    cart_item.delete()
    return redirect('cart_detail')

def thanks_page(request,order_id):
    if order_id:
        customer_order = get_object_or_404(Order,id=order_id)
    return render(request,'thankyou.html',{'customer_id':customer_order})

def signupview(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            signup_user = User.objects.get(username=username)
            customer_group = Group.objects.get(name='Customer')
            customer_group.user_set.add(signup_user)
    else:
        form = SignupForm()
    return render(request,'signup.html',{'form':form})
def signinview(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username,password=password)

            if user is not None:
                login(request,user)
                # session_login(username,password)
                return redirect('home')
            else:
                return redirect('sign_up')
    else:
        form = AuthenticationForm()

        return render(request,'signin.html',{'form':form})

def signoutView(request):
    logout(request)
    return redirect('sign_in')

@login_required(redirect_field_name='next',login_url='sign_in')
def orderHistory(request):
    if request.user.is_authenticated:
        email = str(request.user.email)
        order_details = Order.objects.filter(emailAddress=email)
    return render(request,'orders_list.html',{'order_details':order_details})


@login_required(redirect_field_name='next',login_url='sign_in')
def ViewOrder(request,order_id):
    if request.user.is_authenticated:
        email = str(request.user.email)
        order = Order.objects.get(id=order_id,emailAddress=email)
        order_item = OrderItem.objects.filter(order=order)
    return render(request,'order_detail.html',{'order_item':order_item,'order':order})

def search(request):
    products = Product.objects.filter(name__contains=request.GET['title'])
    return render(request, 'home.html', {'products': products})

def Contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            name = form.cleaned_data.get('name')
            from_email= form.cleaned_data.get('from_email')
            message = form.cleaned_data.get('message')
            message_format = "{0} has sent you a new message:\n\n{1}".format(name,message)
            mail = EmailFunction(subject,message_format,from_email,"nauman.arif@zetatech.com.pk")
            print("email has been sent")
            return render(request,'contact_Success.html')

    else:
        form = ContactForm()
    return render(request,'contact.html',{'form':form})












