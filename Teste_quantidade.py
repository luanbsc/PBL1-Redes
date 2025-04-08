import random
import time
import socket
import threading
from cliente_app import User, create_random_user, send_request

def start_car(car):
    """Função para iniciar o movimento de um carro"""
    print(f"Carro {car.id} ({car.name}) começou a andar")
    # Aqui você pode adicionar a lógica de movimento do carro

def alert_battery(car):
    """Função para alertar bateria baixa de um carro"""
    message = f"low_battery,{car.x},{car.y},{car.id}"
    response = send_request(message)
    print(f"Carro {car.id} ({car.name}) alertou bateria baixa. Resposta: {response}")

def main():
    # Pergunta quantos carros criar
    num_cars = int(input("Quantos carros você quer criar? "))
    
    # Cria a lista de carros
    cars = [create_random_user() for _ in range(num_cars)]
    print(f"\nCriados {num_cars} carros com sucesso!")
    
    while True:
        print("\n=== MENU DE TESTE ===")
        print("1 - Começar a andar (todos os carros)")
        print("2 - Alertar bateria (todos os carros)")
        print("3 - VAZIA")
        print("0 - Sair")
        
        choice = input("Escolha uma opção: ")
        
        if choice == "1":
            print(f"Iniciando movimento para {num_cars} carros...")
            threads = []
            for car in cars:
                thread = threading.Thread(target=start_car, args=(car,))
                threads.append(thread)
                thread.start()
            
            # Aguarda todas as threads terminarem
            for thread in threads:
                thread.join()
                
        elif choice == "2":
            print(f"Enviando alerta de bateria para {num_cars} carros...")
            threads = []
            for car in cars:
                thread = threading.Thread(target=alert_battery, args=(car,))
                threads.append(thread)
                thread.start()
            
            # Aguarda todas as threads terminarem
            for thread in threads:
                thread.join()
                
        elif choice == "3":
            print("Opção vazia")
            
        elif choice == "0":
            print("Saindo...")
            break
            
        else:
            print("Opção inválida! Tente novamente.")
        
        time.sleep(1)

if __name__ == "__main__":
    main() 