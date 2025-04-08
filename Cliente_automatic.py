import random
import time
import socket
import json
import hashlib

HOST = "145.223.27.42"  # IP da VPS
PORT = 8015

def send_request(message):
    # Divide a mensagem em partes
    parts = message.split(',')
    command = parts[0]
    
    # Cria o JSON baseado no comando low_battery,{user.x},{user.y},{user.id}
    if command == "low_battery":
        request_data = {
            "action": "low_battery",
            "x": float(parts[1]),
            "y": float(parts[2]),
            "id": parts[3]
        }
    elif command == "get_station_mais_proximo":
        request_data = {
            "action": "get_station_mais_proximo",
            "x": float(parts[1]),
            "y": float(parts[2]),
            "id": parts[3]
        }
    elif command == "get_stations_by_id":
        request_data = {
            "action": "get_stations_by_id",
            "id": parts[1]
        }
    elif command == "release_stations_by_id":
        request_data = {
            "action": "release_stations_by_id",
            "id": parts[1]
        }
    elif command == "release_all_stations":
        request_data = {
            "action": "release_all_stations"
        }
    else:
        return {"status": "erro", "mensagem": "Comando não reconhecido"}
    
    # Converte para JSON e envia
    print(f"print do request {request_data}")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.sendall(json.dumps(request_data).encode())
    response = client.recv(1024).decode()
    response_dict = json.loads(response)
    print(response_dict['mensagem'])
    client.close()
    return response

class User:
    def __init__(self, name, car_model, economy, battery):
        self.name = name
        self.car_model = car_model
        self.economy = economy
        self.battery = battery
        self.x = round(random.uniform(100, 200))
        self.y = round(random.uniform(100, 200))
        self.id = str(time.time_ns())[-5:]
        self.balance = 0

def create_random_user():
    names = ["Alice", "Bruno", "Carlos", "Diana", "Eduardo"]
    car_models = ["Tesla", "BYD"]
    name = random.choice(names)
    car_model = random.choice(car_models)
    economy = random.randint(100, 400)
    battery = random.randint(70, 100)
    return User(name, car_model, economy, battery)

def start(user):
    print("Iniciando movimentação do carro... Consumo de bateria ativado.")
    
    while user.battery > 20:
        user.battery -= 1
        move_x = random.randint(2, 10)
        move_y = random.randint(2, 10)
        user.x += random.choice([-1, 1]) * move_x
        user.y += random.choice([-1, 1]) * move_y
        print(f"Bateria: {user.battery}% | Localização: ({user.x}, {user.y})")
        time.sleep(1)
    
    print("Bateria baixa! Enviando alerta...")
    message = f"low_battery,{user.x},{user.y},{user.id}"
    send_request(message)
    check_reserved_stations(user)

def check_reserved_stations(user):
    while True:
        message = f"get_stations_by_id,{user.id}"
        response = send_request(message)
        
        if "você é o 1º da fila" in response:
            print("SEU CARRO ESTA CARREGANDO, AGUARDE...")
        elif "Nenhuma estação ocupada encontrada para o usuário" in response:
            print("Carregamento concluído! Bateria recarregada para 100%")
            user.battery = 100
            start(user)
            break
        else:
            print(response)
        
        time.sleep(10)

def main():
    user = create_random_user()
    print(f"Carro criado: {user.name} - {user.car_model}")
    print(f"Bateria inicial: {user.battery}%")
    print(f"Localização inicial: ({user.x}, {user.y})")
    print(f"ID do carro: {user.id}")
    
    # Inicia o processo automaticamente
    start(user)

if __name__ == "__main__":
    main()