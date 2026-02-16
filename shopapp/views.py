from django.shortcuts import render,get_object_or_404,redirect
from .models import offerProduct,Category,SubCategory,Product,Review
from django.db.models import Count,Prefetch,Avg
from django.core.paginator import Paginator
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
import uuid
import hashlib 
import uuid 
import base64 
import json 
import hmac

# Create your views here.
def contact(request):
    return render(request, "shopapp/contact.html")

def index(request):
    offer=offerProduct.objects.filter(is_available=True)
    category=Category.objects.annotate(subcategory_count=Count('subcategory')).\
        prefetch_related(Prefetch('subcategory_set',queryset=SubCategory.objects.annotate(product_count=Count('product'))))
    
    subcategory_id=request.GET.get('subcategory')
    min=request.GET.get('min')
    max=request.GET.get('max')

    if subcategory_id and min and max:
        product=Product.objects.filter(is_available=True,subcategory=subcategory_id,price__range=(min,max))
    
    elif subcategory_id:
        product=Product.objects.filter(is_available=True,subcategory=subcategory_id,)

    else:
        product=Product.objects.filter(is_available=True)

    paginator=Paginator(product,3)
    num_p=request.GET.get("page")
    data=paginator.get_page(num_p)
    total=data.paginator.num_pages

    for i in range(total):
        print(i+1)

    context={
        'offer':offer,
        'category':category,
        'product':product,
        'data':data,
        'num':[i+1 for i in range(total)]
    }
    return render(request, 'shopapp/index.html',context)

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    # All reviews of this product
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    review_count = reviews.count()

    # Average rating (safe)
    rating_avg = reviews.aggregate(avg=Avg('rating'))['avg']
    rating_avg = round(rating_avg) if rating_avg else 0

    # Review form
    form = ReviewForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')   # login page name change if needed

        # Prevent duplicate review by same user
        if Review.objects.filter(product=product, user=request.user).exists():
            return redirect('product_detail', id=product.id)

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', id=product.id)

    context = {
        'product': product,
        'reviews': reviews,
        'review_count': review_count,
        'rating_avg': rating_avg,
        'form': form,
        'range': range(1, 6),   # for stars ⭐⭐⭐⭐⭐
    }

    return render(request, 'shopapp/product_detail.html', context)

'''
===========================================================
                             Add To Cart 
===========================================================
'''


@login_required(login_url="log_in")
def cart_add(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("index")


@login_required(login_url="log_in")
def item_clear(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.remove(product)
    return redirect("cart_detail")


@login_required(login_url="log_in")
def item_increment(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart_detail")


@login_required(login_url="log_in")
def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.decrement(product=product)
    return redirect("cart_detail")

def generate_signature(data, secret): 
    # signed_field_names must be included in the payload 
    signed_fields = data["signed_field_names"].split(",") 
     
    # Create message string in exact order 
    message = ",".join([f"{field}={data[field]}" for field in signed_fields]) 
    signature = hmac.new( 
        secret.encode("utf-8"), 
        message.encode("utf-8"), 
        hashlib.sha256 
    ).digest()      
    return base64.b64encode(signature).decode("utf-8") 


@login_required(login_url="log_in")
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")


@login_required(login_url="log_in")
def cart_detail(request):

    cart=request.session.get('cart')
    print(cart)
    amount=0
    for item in cart.values():
        amount += item["quantity"] * float(item['price'])
    
    amount=round(amount,2)
    tax_amount=round(amount*0.13,2)
    total_amount=round(amount+tax_amount,2)
    
    secret_key = "8gBm/:&EnhH.1/q"

    
    data={
        "amount":amount,
        "tax_amount":tax_amount,
        "total_amount":total_amount,
        "transaction_uuid":str(uuid.uuid4()),
        "product_code":"EPAYTEST",
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "success_url":"http://localhost:8000/payments/success_url/",
        "failure_url":"http://localhost:8000/payments/failure_url/"


    }    
    data["signature"]=generate_signature(data,secret_key)
    return render(request, 'shopapp/cart.html',data)