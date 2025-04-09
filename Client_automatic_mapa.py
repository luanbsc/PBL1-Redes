import random
import time
import socket
import json
import hashlib
import os

HOST = "192"  # IP da VPS
PORT = 8015

# Constantes do mapa (tamanho reduzido)
MAP_WIDTH = 30
MAP_HEIGHT = 15
CAR_SYMBOL = "🚗"
EMPTY_SYMBOL = "·"
STATION_SYMBOL = "⚡"

# Coordenadas dos postos de carregamento
CHARGING_STATIONS = {
    "Posto 1": {"x": 18.0, "y": 32.0},
    "Posto 2": {"x": 500.0, "y": 708.0},
    "Posto 3": {"x": 1280.0, "y": 2202.0},
    "Posto 4": {"x": 4000.0, "y": 2190.0},
    "Posto 5": {"x": 1200.0, "y": 3120.0}
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_map(user):
    clear_screen()
    print("\n" + "=" * MAP_WIDTH)
    print(f"Carro: {user.name} ({user.car_model}) | Bateria: {user.battery}%")
    print("=" * MAP_WIDTH + "\n")
    
    # Normaliza as coordenadas para o tamanho do mapa
    car_x = int((user.x * MAP_WIDTH) / 4000)  # Usando 4000 como referência máxima
    car_y = int((user.y * MAP_HEIGHT) / 4000)  # Usando 4000 como referência máxima
    
    # Garante que as coordenadas estejam dentro dos limites do mapa
    car_x = max(0, min(car_x, MAP_WIDTH - 1))
    car_y = max(0, min(car_y, MAP_HEIGHT - 1))
    
    # Desenha o mapa
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            # Verifica se há um posto nesta posição
            station_here = False
            for station in CHARGING_STATIONS.values():
                station_x = int((station["x"] * MAP_WIDTH) / 4000)
                station_y = int((station["y"] * MAP_HEIGHT) / 4000)
                if x == station_x and y == station_y:
                    print(STATION_SYMBOL, end="")
                    station_here = True
                    break
            
            if not station_here:
                if x == car_x and y == car_y:
                    print(CAR_SYMBOL, end="")
                else:
                    print(EMPTY_SYMBOL, end="")
        print()
    
    print("\n" + "=" * MAP_WIDTH)
    print(f"Posição: ({user.x}, {user.y})")
    print("=" * MAP_WIDTH + "\n")

def send_request(message):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.sendall(message.encode())
    response = client.recv(1024).decode()
    response_dict = json.loads(response)
    print(response_dict['mensagem'])
    client.close()
    return response_dict['mensagem']

class User:
    def __init__(self, name, car_model, economy, battery):
        self.name = name
        self.car_model = car_model
        self.economy = economy
        self.battery = battery
        self.x = round(random.uniform(1, 3120))  # Ajustado para 3120
        self.y = round(random.uniform(1, 3120))  # Ajustado para 3120
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
        # Aumentado significativamente o movimento
        move_x = random.randint(100, 500)  # Movimento muito maior
        move_y = random.randint(100, 500)  # Movimento muito maior
        user.x += random.choice([-1, 1]) * move_x
        user.y += random.choice([-1, 1]) * move_y
        
        # Mantém as coordenadas dentro dos limites (1-3120)
        user.x = max(1, min(user.x, 3120))
        user.y = max(1, min(user.y, 3120))
        
        # Atualiza o mapa
        draw_map(user)
        time.sleep(1)
    
    print("Bateria baixa! Enviando alerta...")
    message = f"low_battery,{user.x},{user.y},{user.id}"
    send_request(message)
    check_reserved_stations(user)

def check_reserved_stations(user):
    while True:
        message = f"all_station_id,{user.id}"
        response = send_request(message)
        
        # Atualiza o mapa mesmo durante o carregamento
        draw_map(user)
        
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