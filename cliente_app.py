import random
import time
import socket
import json
import hashlib

HOST = "142"  # IP da VPS
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
        self.x = round(random.uniform(1, 3150))  # Coordenada X do carro
        self.y = round(random.uniform(1, 3150))  # Coordenada Y do carro
        timestamp = time
        self.id = str(time.time_ns())[-5:]
        self.balance = 0  # saldo


#FUNCAO DE ENVIAR ALERTAR DE BATERIA (UTILIZAREMOS NA FUNCAO START APOS ATINGIR O LIMITE DE BATERIA)
def low_battery(user):
    # Esta função será chamada quando a bateria atingir 20% ou menos
    print("Bateria baixa! Enviando alerta...")
    message = f"low_battery,{user.x},{user.y},{user.id}"
    send_request(message)
    print("Alerta de bateria enviado!")

def start(user):
    # A função vai consumir 1% de bateria por segundo até atingir 20%
    print("Iniciando movimentação do carro... Consumo de bateria ativado.")
    
    while user.battery > 20:
        user.battery -= 1
        
        # Simula o movimento do carro alterando as coordenadas X e Y
        move_x = random.randint(2, 10)  # Move entre 2 e 10 unidades no eixo X
        move_y = random.randint(2, 10)  # Move entre 2 e 10 unidades no eixo Y
        
        # Randomiza se o movimento será positivo ou negativo para cada eixo
        user.x += random.choice([-1, 1]) * move_x
        user.y += random.choice([-1, 1]) * move_y
        
        print(f"Bateria: {user.battery}% | Localização: ({user.x}, {user.y})")
        
        time.sleep(1)
    
    # Quando a bateria atingir ou for inferior a 20%, chamamos a função de alerta
    low_battery(user)


def generate_pix(user):
    try:
        # Pede o valor a ser adicionado
        valor = float(input("Digite o valor que deseja adicionar ao saldo: R$ "))
        
        # Gera um código PIX aleatório
        codigo_pix = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=32))
        
        print("\n=== CÓDIGO PIX GERADO ===")
        print(f"Código: {codigo_pix}")
        print(f"Valor: R$ {valor:.2f}")
        print("=======================\n")
        
        # Pergunta se o usuário pagou
        pagamento = input("SIMULAR QUE O USUÁRIO PAGOU O PIX? DIGITE Y OU N: ").upper()
        
        if pagamento == "Y":
            user.balance += valor
            print(f"\nSaldo atualizado! Novo saldo: R$ {user.balance:.2f}")
        else:
            print("\nOperação cancelada.")
            
    except ValueError:
        print("Por favor, insira um valor numérico válido.")
        
        


def create_random_user():
    names = [
        "Alice", "Bruno", "Carlos", "Diana", "Eduardo",
        "Fernanda", "Gabriel", "Helena", "Igor", "Julia",
        "Lucas", "Mariana", "Nicolas", "Olivia", "Pedro",
        "Rafaela", "Samuel", "Tatiana", "Vitor", "Yasmin",
        "Zoe", "André", "Beatriz", "Cecília", "Daniel",
        "Elisa", "Felipe", "Giovanna", "Henrique", "Isabela"
    ]
    
    car_models = [
        "Tesla Model S", "Tesla Model 3", "Tesla Model X", "Tesla Model Y",
        "BYD Han", "BYD Tang", "BYD Song", "BYD Yuan",
        "NIO ET7", "NIO ES8", "NIO EC6",
        "Volkswagen ID.4", "Volkswagen ID.3",
        "Chevrolet Bolt", "Chevrolet Volt",
        "Nissan Leaf", "Nissan Ariya",
        "Hyundai Kona", "Hyundai Ioniq",
        "Kia EV6", "Kia Niro",
        "Ford Mustang Mach-E", "Ford F-150 Lightning",
        "Audi e-tron", "Audi Q4 e-tron",
        "BMW i4", "BMW iX",
        "Mercedes EQS", "Mercedes EQC",
        "Porsche Taycan", "Porsche Macan EV"
    ]
    name = random.choice(names)
    car_model = random.choice(car_models)
    economy = random.randint(100, 400)
    battery = random.randint(70, 100)
    
    return User(name, car_model, economy, battery)

def show_menu(user):
    print("\n=== MENU ===")
    print(f"Usuário: {user.name} | Carro: {user.car_model} | Economia: {user.economy} km/kWh | Bateria: {user.battery}% | Localização: {user.x},{user.y} | ID: {user.id} | SALDO: {user.balance} ")
    print("1 - Start")
    print("2 - Alterar localização")
    print("3 - Alertar bateria")
    print("4 - Postos reservados")
    print("5 - Encerrar reservas")
    print("6 - Encerrar todas as reservas (ADM Geral)")
    print("7 - GERAR PIX 7")
    print("0 - Sair")

def main():
    user = create_random_user()
    
    while True:
        show_menu(user)
        choice = input("Escolha uma opção: ")
        
        if choice == "1":
            start(user)

        elif choice == "2":
            try:
                new_x = float(input("Digite a nova coordenada X: "))
                new_y = float(input("Digite a nova coordenada Y: "))
                
                # Atualiza as coordenadas do usuário
                user.x = new_x
                user.y = new_y
                
                print(f"Localização atualizada para X: {user.x} | Y: {user.y}")
            except ValueError:
                print("Por favor, insira valores numéricos válidos para X e Y.")
        elif choice == "3":
            message = f"low_battery,{user.x},{user.y},{user.id}"
            send_request(message)

        elif choice == "4":
            message = f"get_stations_by_id,{user.id}"
            send_request(message)

        elif choice == "5":
            message = f"release_stations_by_id,{user.id}"
            send_request(message)
            
        elif choice == "6":
            message = f"release_all_stations"
            send_request(message)

        elif choice == "7":
            generate_pix(user)
        elif choice == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida! Tente novamente.")
        
        time.sleep(1)

if __name__ == "__main__":
    main()
