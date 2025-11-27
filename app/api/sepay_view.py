import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app.models import Order # Import từ app.models thay vì .models

@csrf_exempt
def sepay_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Lấy các thông tin từ SePay
            gateway = data.get('gateway')
            transactionDate = data.get('transactionDate')
            accountNumber = data.get('accountNumber')
            subAccount = data.get('subAccount')
            transferAmount = data.get('transferAmount')
            transferContent = data.get('content')
            transferType = data.get('transferType')
            transaction_id = data.get('referenceCode')

            # Kiểm tra giao dịch tiền vào (in)
            if transferType != 'in':
                return JsonResponse({'success': False, 'message': 'Not an incoming transaction'})

            # --- LOGIC TÌM ORDER ID ---
            # Lọc lấy số từ nội dung chuyển khoản
            order_id_str = ''.join(filter(str.isdigit, transferContent))
            
            if not order_id_str:
                 return JsonResponse({'success': False, 'message': 'No Order ID found in content'})

            order_id = int(order_id_str)

            # Tìm đơn hàng
            order = Order.objects.filter(id=order_id).first()

            if order:
                cart_total = float(order.get_cart_total)
                
                # So sánh số tiền (dùng >= để an toàn phòng khi khách chuyển dư)
                if transferAmount >= cart_total:
                    order.complete = True
                    order.transaction_id = transaction_id
                    order.save()
                    
                    print(f"WEBHOOK: Đơn hàng {order_id} đã thanh toán thành công!")
                    return JsonResponse({'success': True, 'message': 'Payment confirmed'})
                else:
                    return JsonResponse({'success': False, 'message': 'Amount mismatch'})
            else:
                 return JsonResponse({'success': False, 'message': 'Order not found'})

        except Exception as e:
            print("Lỗi Webhook:", e)
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid method'})