from datetime import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from app.forms import CustomerProfileForm, RegistrationForm, EventForm, TicketForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import razorpay
from django.views.decorators.csrf import csrf_exempt
from .models import Newuser, Event, Ticket
from django.conf import settings


# Create your views here.
@login_required
def home(request):
    return render (request,"app/home.html",locals())

@login_required
def about(request):
    return render (request,"app/about.html",locals())

@login_required
def contact(request):
    return render (request,"app/contact.html",locals())

class RegistrationView(View):
    def get(self,request):
        form = RegistrationForm()
        return render(request, 'app/registration.html',locals())

    def post(self,request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Successfully New User Register.")
        else:
            messages.warning(request,"Invalid User!")
        return render(request, 'app/registration.html',locals())

@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html',locals())
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Newuser(user=user,first_name=first_name,last_name=last_name,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,"Profile Save Successfully!")
        else:
            messages.warning(request,"Invalid Data")
        return render(request, 'app/profile.html',locals())
    


@login_required
def details(request):
    add = Newuser.objects.filter(user=request.user)
    return render(request,'app/details.html',locals()) 


@method_decorator(login_required,name='dispatch')
class updatedetails(View):
    def get(self,request,pk):
        add = Newuser.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request,'app/updatedetails.html',locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Newuser.objects.get(pk=pk)
            add.first_name = form.cleaned_data['first_name']
            add.last_name = form.cleaned_data['last_name']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Profile Update Successfully!")
        else:
            messages.warning(request,"Invalid Data")
        return redirect("details")
    


@login_required
def newevent(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            return redirect('dashboard') 
    else:
        form = EventForm()
    
    return render(request, 'app/newevent.html', {'form': form})


def dashboard(request):
    events = Event.objects.filter(organizer=request.user)
    total_events = events.count()

    context = {
        'events': events,
        'total_events': total_events,
    }
    return render(request, 'app/dashboard.html', context)


@login_required
def eventlist(request):
    event = Event.objects.filter()
    title = Event.objects.filter().values('title')
    return render (request,"app/eventlist.html",locals())



@method_decorator(login_required,name='dispatch')
class EventDetail(View):
    def get(self,request,pk):
        event = Event.objects.get(pk=pk)        
        return render(request,"app/eventdetails.html",locals())
    



def ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.organizer = request.user
            ticket.save()
            return redirect('dashboard') 
    else:
        form = TicketForm()
    
    return render(request, 'app/ticket.html', {'form': form})



# @login_required
# def buyticket(request, event_id):
#     event = get_object_or_404(Event, id=event_id)
#     ticket_types = {
#         'General': 300, 
#         'VIP': 500,
#         'Student': 200
#     }

#     if request.method == "POST":
#         ticket_type = request.POST.get("ticket_type")
#         quantity = int(request.POST.get("quantity"))

        
#         price = ticket_types.get(ticket_type, 0)
#         total_price = price * quantity

#         if total_price <= 0 or quantity < 1:
#             messages.error(request, "Invalid ticket purchase.")
#             return redirect("buyticket", event_id=event_id)

        
#         for _ in range(quantity):
#             Ticket.objects.create(
#                 user=request.user,
#                 event=event,
#                 ticket_type=ticket_type,
#                 price=price
#             )

#         messages.success(request, f"You successfully purchased {quantity} {ticket_type} ticket(s)!")
#         return redirect("ticket") 

#     context = {
#         "event": event,
#         "ticket_types": ticket_types
#     }
#     return render(request, "app/buyticket.html", context)



def buyticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    ticket_types = {
        'General': 300,
        'VIP': 500,
        'Student': 200,
    }

    if request.method == "POST":
        ticket_type = request.POST.get("ticket_type")
        quantity = int(request.POST.get("quantity"))

        try:
            # Validate input
            if ticket_type not in ticket_types or quantity < 1:
                raise ValueError("Invalid ticket type or quantity.")

            # Calculate total price
            price_per_ticket = ticket_types[ticket_type]
            total_price = price_per_ticket * quantity

            # Check event capacity
            if event.capacity < quantity:
                messages.error(request, f"Only {event.capacity} tickets are available.")
                return redirect("buyticket", event_id=event_id)

            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Create Razorpay order
            order = client.order.create({
                "amount": total_price * 100,  # Convert to paise (Indian currency requirement)
                "currency": "INR",
                "payment_capture": "1",
            })

            # Store the order details in the session
            request.session['razorpay_order_id'] = order['id']
            request.session['ticket_data'] = {
                "event_id": event.id,
                "ticket_type": ticket_type,
                "quantity": quantity,
                "price_per_ticket": price_per_ticket,
                "total_price": total_price,
            }

            context = {
                "event": event,
                "order": order,
                "razorpay_key_id": settings.RAZORPAY_KEY_ID,
                "ticket_types": ticket_types,
            }
            return render(request, "app/payment.html", context)

        except Exception as e:
            messages.error(request, str(e))
            return redirect("buyticket", event_id=event_id)

    context = {
        "event": event,
        "ticket_types": ticket_types,
    }
    return render(request, "app/buyticket.html", context)

@csrf_exempt
def payment_success(request):
    razorpay_order_id = request.session.get('razorpay_order_id')
    ticket_data = request.session.get('ticket_data')

    if not razorpay_order_id or not ticket_data:
        messages.error(request, "Payment details not found.")
        return redirect("ticket")

    try:
        event = get_object_or_404(Event, id=ticket_data['event_id'])
        for _ in range(ticket_data['quantity']):
            Ticket.objects.create(
                user=request.user,
                event=event,
                ticket_type=ticket_data['ticket_type'],
                price=ticket_data['price_per_ticket'],
            )

        # Update event capacity
        event.capacity -= ticket_data['quantity']
        event.save()

        messages.success(request, f"Payment successful! Tickets purchased for {event.title}.")
        return redirect("ticket")

    except Exception as e:
        messages.error(request, "Payment verification failed.")
        return redirect("buyticket", event_id=ticket_data['event_id'])


