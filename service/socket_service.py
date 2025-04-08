import socket
import math
from controllers.station_controller import StationController
server = StationController()


def send_to_container(message: str) -> str:
    """ Envia uma mensagem via TCP para o container e retorna a resposta. """
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("145.223.27.42", 8016))  # IP e porta do servidor
        print("Conectado ao servidor TCP!")

        client.sendall(message.encode())
        response = client.recv(1024).decode()
        print(f"Resposta do servidor: {response}")

        return response
    except Exception as e:
        print(f"Erro na comunicação TCP: {e}")
        return f"Erro: {e}"
    finally:
        client.close()
        print("Conexão TCP fechada.")

def calcular_distancia(x1, y1, x2, y2):
    """Calcula a distância Euclidiana entre dois pontos."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def get_recharge_station(x: float, y: float) -> dict:
    """Retorna o posto de recarga mais próximo disponível e o marca como ocupado."""
    try:
        print('1')
        
        postos_disponiveis = server.get_available_stations()
        print(f"postos disponiveis: {postos_disponiveis}")
        print('1')

        if not postos_disponiveis:
            return {"status": "erro", "mensagem": "Nenhum posto disponível no momento."}

        # Encontrar o posto mais próximo
        posto_mais_proximo = min(
            postos_disponiveis,
            key=lambda nome: calcular_distancia(x, y, postos_disponiveis[nome]["x"], postos_disponiveis[nome]["y"])
        )

        # Marcar o posto como ocupado por 2 minutos
        server.set_station_occupied(posto_mais_proximo)

        return {
            "status": "sucesso",
            "mensagem": f"O posto mais próximo disponível é: {posto_mais_proximo}"
        }

    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
