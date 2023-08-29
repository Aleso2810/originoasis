# campanas/apps.py
import json
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.views.decorators.csrf import csrf_exempt
from django.dispatch import receiver
from .models import Contribution
from datetime import datetime


@receiver(valid_ipn_received)
def handle_valid_ipn(sender, **kwargs):
    ipn_obj = sender
    
    #Aquí es donde obtienes el valor de ipn_obj.custom
    custom_data = json.loads(ipn_obj.custom)

    user_id = custom_data["user_id"]
    campaign_id = custom_data["campaign_id"]

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # Confirma que el pago ha sido correcto
        if ipn_obj.receiver_email != "sb-ks7kj27145700@personal.example.com":
            return
        
        # Crear la contribución en la base de datos
        contribution = Contribution(
            campaign_id=campaign_id,  
            user_id=user_id,  
            amount=ipn_obj.mc_gross,
            date=datetime.now()
        )
        print("Donación realizada")
        "contribution.save()"
    else:
        # Manejar otros estados de pago si es necesario (opcional)
        pass
