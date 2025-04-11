from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInLine(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name',
                    'email', 'city', 'addres',
                    'postal_code', 'created',
                    'updated', 'paid']
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInLine]
