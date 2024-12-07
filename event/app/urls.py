from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_view
from .forms import LoginForm, MyPasswordChangeForm
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),


    path("profile/", views.ProfileView.as_view(),name='profile'),
    path("details/", views.details,name='details'),
    path("updatedetails/<int:pk>", views.updatedetails.as_view(),name='updatedetails'),


    path('newevent/', views.newevent, name='newevent'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("eventdetail/<int:pk>",views.EventDetail.as_view(),name='eventdetail'),
    path("eventlist/",views.eventlist,name='eventlist'),
    path('ticket/', views.ticket, name='ticket'),
    path('buyticket/<int:event_id>/', views.buyticket, name='buyticket'),
    
    path('registration/', views.RegistrationView.as_view(),name='registration'),
    path('accounts/login/', auth_view.LoginView.as_view(template_name='app/login.html', authentication_form=LoginForm), name='login'),
    path('logout/',auth_view.LogoutView.as_view(next_page="login"),name='logout'),
    path('passwordchange/<int:pk>', auth_view.PasswordChangeView.as_view(template_name='app/changepassword.html',form_class=MyPasswordChangeForm,),name='changepassword'),

    path('payment-success/', views.payment_success, name='payment_success'),


]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)