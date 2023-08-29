import csv
from datetime import datetime
from django.contrib.auth.models import User
from campanas.models import Category, Campaign

def feed_campaigns():
    with open('data/Campaings.csv', encoding='utf-8-sig') as csv_file:
        header = csv_file.readline().strip()
        print(f"Encabezado del CSV: {header}")

        # Diagnóstico: Mostrar todos los usuarios en la base de datos
        all_users = User.objects.all()
        print("Usuarios en la base de datos:")
        for user in all_users:
            print(user.id, user.username)

        csv_file.seek(0)
        csv_dict_reader = csv.DictReader(csv_file, delimiter=';')
        
        for item in csv_dict_reader:
            print(f"Leyendo fila: {item}")
            
            try:
                category = Category.objects.get(pk=int(item['category_name']))
            except Category.DoesNotExist:
                print(f"Categoría no encontrada con ID: {item['category_name']}. Saltando fila.")
                continue
            
            try:
                user_instance = User.objects.get(pk=int(item['beneficiary']))
            except User.DoesNotExist:
                print(f"Usuario no encontrado con ID: {item['beneficiary']}. Saltando fila.")
                continue

            start_date_obj = datetime.strptime(item['start_date'], '%d/%m/%Y')
            end_date_obj = datetime.strptime(item['end_date'], '%d/%m/%Y')
            
            campaign = Campaign(
                category=category,
                name=item['name'],
                description=item['description'],
                photo=item['photo'],
                beneficiary=user_instance,
                target_amount=float(item['target_amount']),
                collected_amount=float(item['collected_amount']),
                start_date=start_date_obj,
                end_date=end_date_obj
            )
            campaign.save()
            print(f"Campaña creada: {campaign}")

def run():
    feed_campaigns()

if __name__ == "__main__":
    run()
