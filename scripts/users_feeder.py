import os
import django
from faker import Faker
from django.contrib.auth.models import User

# Configuración de Django para que se pueda ejecutar como script independiente.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campanas.settings")
django.setup()

fake = Faker()

def create_random_users(num=3):
    # Borrar todos los usuarios antes de crear nuevos
    User.objects.all().delete()
    
    for _ in range(num):
        # Genera un nombre de usuario, email y contraseña aleatorios
        username = fake.user_name()
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
        
        user = User(username=username, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()

        print(f"Usuario creado: {username} - Email: {email} - Contraseña: {password}")

def run():
    create_random_users()

if __name__ == "__main__":
    run()
