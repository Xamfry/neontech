from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
import io
import base64

@login_required
def totp_setup(request):
    device, created = TOTPDevice.objects.get_or_create(user=request.user, name="authenticator", defaults={'confirmed': False})
    if request.method == 'POST':
        token = request.POST.get('token')
        if device.verify_token(token):
            device.confirmed = True
            device.save()
            return redirect('mfa_verify')
    # QR для приложения
    otp_uri = device.config_url
    buf = io.BytesIO()
    qrcode.make(otp_uri).save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode()
    return render(request, 'users/mfa_setup.html', {'qr_b64': qr_b64})

@login_required
def totp_verify(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        for dev in TOTPDevice.objects.filter(user=request.user, confirmed=True):
            if dev.verify_token(token):
                request.session['otp_verified'] = True
                return redirect('/')
    return render(request, 'users/mfa_verify.html')

@login_required
def totp_disable(request):
    TOTPDevice.objects.filter(user=request.user).delete()
    return redirect('/')
