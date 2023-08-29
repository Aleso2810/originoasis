import csv
from alquiler.models import TipoVehiculo, Vehiculo

def feed_vehiculos():
    Vehiculo.objects.all().delete()    
    with open('data/vehiculos.csv', encoding='UTF-8') as csv_file:
        csv_dict_reader = csv.DictReader(csv_file, delimiter=';')        
        for item in csv_dict_reader:
            tipo_vehiculo = TipoVehiculo.objects.get(pk=item['tipo_vehiculo'])
            vehiculo = Vehiculo(    tipo_vehiculo=tipo_vehiculo,
                                    marca = item['marca'],
                                    modelo = item['modelo'],
                                    imagen = item['imagen'],
                                    precio_dia = item['precio_dia'],
                                    nro_pasajeros = item['nro_pasajeros'],
                                    nro_maletas = item['nro_maletas'],
                                    tipo_transmision = item['tipo_transmision'],
                                    tiene_ac = item['tiene_ac'] )
            
            vehiculo.save() 
            print(f'Vehiculo creado: {vehiculo}')          

def run():
    feed_vehiculos()