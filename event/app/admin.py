from django.contrib import admin
from .models import Event, Newuser, Ticket, Order

# Register your models here.


@admin.register(Event)
class EventModelAdmin(admin.ModelAdmin):
    list_display = ['id','title','location','date']


@admin.register(Newuser)
class NewuserModelAdmin(admin.ModelAdmin):
    list_display = ['id','first_name','last_name','city','mobile']


@admin.register(Ticket)
class TicketModelAdmin(admin.ModelAdmin):
    list_display = ['id','ticket_type','price','date_purchased']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'razorpay_order_id', 'amount', 'is_paid', 'created_at']
    list_filter = ['is_paid']
    search_fields = ['razorpay_order_id', 'user__username', 'event__title']