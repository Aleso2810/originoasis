# Importaciones necesarias para el proyecto
import json
import uuid
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Sum, Count
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.dispatch import receiver

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.forms import PayPalPaymentsForm

from .models import Campaign, Comment, Contribution, Category

# URL base para el entorno de desarrollo con ngrok
ngrok_base_url = "https://originoasis.azurewebsites.net"  # Asegúrate de reemplazar esto con tu URL ngrok actual

# Función para manejar el inicio de sesión
def do_login(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            username = payload['username']
            password = payload['password']

            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return JsonResponse({'login': True, 'msg': 'Sesión iniciada'})
            else:
                raise PermissionError('Invalid credentials')
        except PermissionError as pe:
            return JsonResponse({'login': False, 'msg': str(pe)}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'signin.html')


# Función para manejar el registro de nuevos usuarios
def signup(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            email = payload['email']
            password = payload['password']
            nombre = payload['nombre']
            apellido = payload['apellido']

            if User.objects.filter(email=email).exists():
                raise ValueError(f'Ya existe un usuario registrado con el email {email}')

            new_user = User(
                username=email,
                password=make_password(password),
                is_superuser=False,
                first_name=nombre,
                last_name=apellido,
                email=email,
                is_staff=False,
                is_active=True,
                date_joined=datetime.now()
            )
            new_user.save()
            return JsonResponse({'success': True, 'msg': 'Usuario registrado'})
        except ValueError as ve:
            return JsonResponse({'success': False, 'msg': str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'signup.html')

# Función para manejar el cierre de sesión
def do_logout(request):
    logout(request)
    return redirect('landing')

# Función para mostrar la página de inicio
def landing_page(request):
    top_campaigns = Campaign.objects.all().order_by('-collected_amount')[:6]  # Cambia 6 al número de campañas que quieres mostrar
    context = {'lista_campaings': top_campaigns}
    return render(request, 'landing.html', context)

# Función para obtener y mostrar todas las campañas
def get_all_campanas(request):
    # Para agregar un comentario
    if request.method == 'POST':
        try:
            campaign_id = request.POST.get('campaign_id')
            comment_text = request.POST.get('comment_text')
            campaign = Campaign.objects.get(id=campaign_id)
            comment = Comment(user=request.user, comment_text=comment_text, campaign=campaign)
            comment.save()
            messages.success(request, 'Comentario agregado satisfactoriamente!')
            # Redirige al usuario de nuevo a la página de la campaña
            return redirect(reverse('campaign_detail', args=[campaign_id]))
        except PermissionError:
            messages.error(request, 'Solo Contribuyentes pueden comentar a la campaña.')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    # Prefetching para optimizar el rendimiento de la base de datos
    comments_prefetch = Prefetch('comment_set', queryset=Comment.objects.all(), to_attr='comments')

    # Filtrar solo campañas activas
    today = datetime.today()
    active_campaigns = Campaign.objects.filter(end_date__gte=today).prefetch_related(comments_prefetch)

    # Obtener todas las categorías
    all_categories = Category.objects.all()

    context = {
        'lista_campaings': active_campaigns,
        'categories': all_categories,
    }
    return render(request, 'campaings.html', context)

# Función para obtener y mostrar todas las contribuciones
def get_all_contributions(request):
    top_contributors = Contribution.objects.values('user__username', 'user__first_name', 'user__last_name')\
        .annotate(total_contributions=Count('user'), total_donated=Sum('amount'))\
        .order_by('-total_donated')

    top_donor = top_contributors[0] if top_contributors else None

    all_campaigns = Campaign.objects.all()

    context = {
    'lista_campaings': all_campaigns,
    'top_contributor': top_contributors,
    'top_donor': top_donor  # añadir esto
    }
    return render(request, 'beneficiarys.html', context)

# Función para mostrar detalles de una campaña en particular
def campaign_detail(request, campaign_id):
    # (Código para mostrar detalles de la campaña, cálculo del tiempo restante, etc.)
    campaign = get_object_or_404(Campaign, id=campaign_id)
    
    # Obteniendo el tiempo actual
    now = datetime.now()
    
    # Convertir campaign.end_date a datetime.datetime
    end_datetime = datetime.combine(campaign.end_date, time())
    
    # Cálculo de la diferencia de tiempo
    if end_datetime > now:
        time_difference = end_datetime - now
        remaining_days = time_difference.days
        remaining_seconds = time_difference.seconds
        remaining_hours = remaining_seconds // 3600
        remaining_minutes = (remaining_seconds % 3600) // 60
        remaining_seconds = remaining_seconds % 60
    else:
        remaining_days, remaining_hours, remaining_minutes, remaining_seconds = 0, 0, 0, 0

    # Configuración de PayPal
    invoice_id = str(uuid.uuid4())
    paypal_dict = {
        "business": "pasm.28.10@gmail.com",
        "amount": "0",  # Aquí deberías configurar el monto real
        "custom": json.dumps({"user_id": request.user.id, "campaign_id": campaign.id}),
        "item_name": campaign.name,
        "item_number": campaign.id,
        "payer_id": request.user.id,
        "invoice": invoice_id,
        "notify_url": ngrok_base_url + reverse('paypal-ipn'),
        "return": ngrok_base_url + reverse('successful'),
        "cancel_return": ngrok_base_url + reverse('cancelled'),
    }

    # Si el usuario está autenticado, almacenamos los detalles de la contribución en la sesión
    if request.user.is_authenticated:
        request.session['temp_contribution'] = {
            'campaign_id': campaign.id,
            'user_id': request.user.id,
            'amount': str(Decimal(paypal_dict["amount"])),  # Convertir Decimal a string
            'status': Contribution.PENDING,
            'invoice': invoice_id
        }

    form = PayPalPaymentsForm(initial=paypal_dict)
    comments = Comment.objects.filter(campaign=campaign).order_by('-date')
    contributions = Contribution.objects.filter(campaign=campaign).order_by('-date')

    has_donated = False
    if request.user.is_authenticated:
        has_donated = request.user.contribution_set.filter(campaign=campaign).exists()

    context = {
        'campaign': campaign,
        'form': form,  # PayPal form
        'comments': comments,
        'contributions': contributions,
        'has_donated': has_donated,
        'remaining_days': remaining_days,
        'remaining_hours': remaining_hours,
        'remaining_minutes': remaining_minutes,
        'remaining_seconds': remaining_seconds
    }
    return render(request, 'campaign_detail.html', context)

# Función para manejar pagos exitosos
def successful(request):
    context = {
        'message': '¡Pago completado con éxito!'
    }
    return render(request, 'successful.html', context)

# Función para manejar pagos cancelados
def cancelled(request):
    context = {
        'message': 'Pago cancelado por el usuario.'
    }
    return render(request, 'cancelled.html', context)

# Función para manejar las IPN de PayPal
@csrf_exempt
def paypal_ipn_handler(request):
    # La librería de PayPal manejará la verificación de la IPN
    return HttpResponse("OK")

@receiver(valid_ipn_received)
def handle_valid_ipn(sender, **kwargs):
    ipn_obj = sender
    custom_value = json.loads(ipn_obj.custom)  # Deserializar el string JSON

    # Usar el valor campaign_id para obtener el objeto Campaign
    try:
        campaign = Campaign.objects.get(id=custom_value['campaign_id'])
        user = User.objects.get(id=custom_value['user_id'])
    except (Campaign.DoesNotExist, User.DoesNotExist):
        # Aquí manejas el caso en que no se encuentre la campaña o el usuario
        return

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # (Código para manejar el estado de la contribución)
        if ipn_obj.receiver_email != "pasm.28.10@gmail.com":
            return

        # Crear la contribución con el estado "Completado"
        contribution = Contribution(
            campaign_id=campaign.id,
            user_id=user.id,  
            amount=ipn_obj.mc_gross,
            status=Contribution.COMPLETED,
        )
        contribution.save()
    else:
        # Manejar otros estados de pago si es necesario
        pass

