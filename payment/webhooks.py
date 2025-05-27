import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order


@csrf_exempt
def stripe_webhook(request):
    print(f'Webhook start')
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    if sig_header is None:
        print("❌ Webhook: missing Stripe signature header.")
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        print("❌ Webhook payload error:", e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print("❌ Webhook signature error:", e)
        return HttpResponse(status=400)

    print(f"✅ Webhook received: {event['type']}")

    if event["type"] == "checkout.session.completed":
        session = event['data']['object']

        client_reference_id = session.get('client_reference_id')
        payment_intent = session.get('payment_intent')

        print("→ client_reference_id:", client_reference_id)
        print("→ payment_intent:", payment_intent)

        if not client_reference_id:
            print("⚠️ No client_reference_id in session. Skipping.")
            return HttpResponse(status=200)

        try:
            order = Order.objects.get(id=client_reference_id)
            order.paid = True
            order.stripe_id = payment_intent
            order.save()
            print(f"✅ Order {order.id} marked as paid.")
        except Order.DoesNotExist:
            print(f"❌ Order with ID {client_reference_id} not found.")
            return HttpResponse(status=404)

    return HttpResponse(status=200)
