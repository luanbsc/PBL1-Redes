import socket
import json

class SocketController:
    POSTO_PORT = 8016  # Porta padrão dos postos

    @staticmethod
    def send_station_update(station_data, posto_ip):
        """
        Envia os dados atualizados diretamente para o posto
        """
        try:
            print(f"[DEBUG] Enviando atualização para o posto no IP {posto_ip}")
            
            # Cria o socket TCP
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Conecta ao posto
            client_socket.connect((posto_ip, SocketController.POSTO_PORT))
            
            # Prepara os dados no formato esperado pelo posto
            request_data = {
                "action": "update_station_data",
                "data": station_data
            }
            
            # Converte para JSON e envia
            json_data = json.dumps(request_data)
            client_socket.send(json_data.encode())
            
            # Recebe a resposta
            response = client_socket.recv(1024).decode()
            response_data = json.loads(response)
            
            # Fecha a conexão
            client_socket.close()
            
            print(f"[DEBUG] Resposta do posto: {response_data}")
            return response_data
            
        except Exception as e:
            print(f"[DEBUG] Erro ao enviar atualização para o posto {posto_ip}: {str(e)}")
            return {"status": "erro", "mensagem": str(e)}