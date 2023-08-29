import csv
from campanas.models import Category

def feed_category():
    Category.objects.all().delete()    
    with open('data/categorys.csv', encoding='UTF-8') as csv_file:
        csv_dict_reader = csv.DictReader(csv_file, delimiter=';')        
        for item in csv_dict_reader:
            # Verificar la existencia de las claves en el diccionario
            if not all(key in item for key in ['id', 'name', 'description']):
                print(f"Datos faltantes o columnas incorrectas en la fila: {item}")
                continue
            
            category = Category(id=item['id'], name=item['name'], description=item['description'])
            category.save()
            print(f'Category creado: {category}')
def run():
    feed_category()