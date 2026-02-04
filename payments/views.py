from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import base64, json,hashlib,hmac
from .models import *
from shopapp.models import Product


@login_required(login_url='log_in')
def success_esewa(request):
    encoded_data = request.GET.get("data")
    if not encoded_data:
        return HttpResponse("Invalid response",status=400)
    try:
        decoded_json = base64.b64decode(encoded_data).decode("utf-8")
        payload = json.loads(decoded_json)
    except Exception:
        return HttpResponse("Invalid date", status=400)
    try:
        signed_fieldss = payload["signed_field_names"].split(",")
        message = ",".join([f"{field}={payload[field]}" for field in signed_fieldss])
        secret_key = "8gBm/:&EnhH.1/q"
        expected_signature = base64.b64encode(
        hmac.new(secret_key.encode(), message.encode(),hashlib.sha256).digest()
        ).decode()
        if expected_signature.rstrip('=') != payload['signature'].rstrip('='):
            # Debugging: show mismatch
            print("Message to sign:", message)
            print("Expected signature:", expected_signature)
            print("Payload signature:", payload['signature'])
            return HttpResponse("Invalid signature", status=400)
    except KeyError as e:
        return HttpResponse(f"Missing field: {e}", status=400)
    print("check data:", payload)
    txn,created=Transaction.objects.get_or_create(transaction_uuid=payload['transaction_uuid'],
    transaction_code=payload['transaction_code'],product_code=payload['product_code'],
    total_amount=payload['total_amount'],user=request.user,status=payload['status'])
    
    order,creates=Order.objects.get_or_create(user=request.user,transaction_uuid=payload['transaction_uuid'],
    status=payload['status'])
    
    cart=request.session.get('cart')
    for item in cart.values():
        OrderItem.objects.create(order=order,product_id=item['product_id'],price=item['price'],
        quantity=item['quantity'])
    request.session['cart']={}
    return render(request, 'success_esewa.html',{'txn':txn})



@login_required(login_url='log_in')
def failure_esewa(request):
    return render(request, "failure_esewa.html")
