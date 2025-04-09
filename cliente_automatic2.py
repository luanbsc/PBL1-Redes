import random
import time
import socket
import json
import threading

HOST = "145"  # IP da VPS
PORT = 8015

def send_request(message):
    parts = message.split(',')
    command = parts[0]

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

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        client.sendall(json.dumps(request_data).encode())
        response = client.recv(1024).decode()
        client.close()
        response_dict = json.loads(response)
        print(f"[{request_data['id']}] {response_dict.get('mensagem', response)}")
        return response
    except Exception as e:
        print(f"Erro na conexão: {e}")
        return ""

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
    print(f"[{user.id}] Iniciando movimentação do carro...")

    while user.battery > 20:
        user.battery -= 1
        user.x += random.choice([-1, 1]) * random.randint(2, 10)
        user.y += random.choice([-1, 1]) * random.randint(2, 10)
        print(f"[{user.id}] Bateria: {user.battery}% | Localização: ({user.x}, {user.y})")
        time.sleep(1)

    print(f"[{user.id}] Bateria baixa! Enviando alerta...")
    message = f"low_battery,{user.x},{user.y},{user.id}"
    send_request(message)
    check_reserved_stations(user)

def check_reserved_stations(user):
    while True:
        message = f"get_stations_by_id,{user.id}"
        response = send_request(message)

        if "você é o 1º da fila" in response:
            print(f"[{user.id}] CARREGANDO...")
        elif "Nenhuma estação ocupada encontrada para o usuário" in response:
            print(f"[{user.id}] Carregamento concluído! Bateria recarregada.")
            user.battery = 100
            start(user)
            break
        else:
            print(f"[{user.id}] {response}")

        time.sleep(10)

def simulate_client():
    user = create_random_user()
    print(f"[{user.id}] Cliente iniciado: {user.name} - {user.car_model}")
    start(user)

def main():
    try:
        threads = int(input("Quantos clientes você deseja simular? "))
    except ValueError:
        print("Por favor, insira um número inteiro válido.")
        return

    for _ in range(threads):
        thread = threading.Thread(target=simulate_client)
        thread.daemon = True
        thread.start()
        time.sleep(0.2)  # pequeno atraso para não sobrecarregar tudo de uma vez

    print(f"Iniciadas {threads} threads de clientes.")
    
    while True:
        time.sleep(1)  # Mantém o script rodando

if __name__ == "__main__":
    main()
