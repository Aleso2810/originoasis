from django.urls import path
from . import views
from django.urls import path, include


urlpatterns = [
    # Páginas generales
    path('', views.landing_page, name='landing'),
    path('login/', views.do_login, name='login'),
    path('logout/', views.do_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    
    # Operaciones de campaña
    path('campaings/', views.get_all_campanas, name='campaings'),
    path('campaign/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    
    # Operaciones de beneficiario
    path('beneficiars/', views.get_all_contributions, name='beneficiarys'),
    
    # Páginas de resultados de Paypal
    path('successful', views.successful, name='successful'),
    path('cancelled', views.cancelled, name='cancelled'),
    # Integración con PayPal
    path('paypal/', include('paypal.standard.ipn.urls')),

    # Operaciones de Analitycs
    path('analitycs/', views.analytics, name='analitycs'),
]
    