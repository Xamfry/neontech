import stripe
import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logger.error(f"⚠️ Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"⚠️ Invalid signature: {e}")
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        logger.info(f"✅ Stripe checkout.session.completed received:\n{json.dumps(session, indent=2)}")

        order_id = session.get('client_reference_id')
        stripe_session_id = session.get('id')

        try:
            if order_id:
                order = Order.objects.get(id=order_id)
            else:
                order = Order.objects.get(stripe_id=stripe_session_id)

            order.paid = True
            order.save()
            logger.info(f"✅ Order #{order.id} marked as paid via webhook.")
        except Order.DoesNotExist:
            logger.error(f"❌ Order not found. ID: {order_id} or Stripe session: {stripe_session_id}")

    return HttpResponse(status=200)
