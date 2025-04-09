import socket
import threading
import json
import time
from controllers.station_controller import StationController
from models.request_handler import RequestHandler
from views.response_view import ResponseView

class ServerController:
    def __init__(self, host="0.0.0.0", port=8015):
        print('Iniciando o ServerController')
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"[*] Servidor rodando na porta {self.port}")

        # Usa a instância única do StationController
        self.station = StationController()
        
        # Configuração do socket UDP para receber dados dos postos
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.host, self.port))
        
        # Inicia a thread para receber dados UDP
        self.udp_thread = threading.Thread(target=self.receive_station_data)
        self.udp_thread.daemon = True
        self.udp_thread.start()

    def receive_station_data(self):
        """Recebe e processa os dados dos postos via UDP"""
        print("[UDP] Iniciando recepção de dados dos postos")
        while True:
            try:
                data, addr = self.udp_socket.recvfrom(1024)
                json_data = json.loads(data.decode())
                
                if json_data.get("type") == "station_update":
                    station_ip = addr[0]  # IP do posto
                    station_data = json_data.get("data")
                    print(f"[UDP] Dados recebidos de {station_ip}: {json_data}")
                    
                    # Atualiza os dados do posto usando o StationController
                    self.station.update_station(station_data, station_ip,json_data.get("port"))
                    print(f"[UDP] Dados do posto atualizados de {station_ip}")
                    
            except Exception as e:
                print(f"[!] Erro ao receber dados UDP: {str(e)}")
                
                
                
    def handle_client(self, conn, addr):
        """
        Função que será executada em uma thread separada para cada cliente
        """
        try:
            print(f"[+] Conexão recebida de {addr}")
            data = conn.recv(1024).decode()
            print(f"[>] Dados recebidos de {addr}: {data}")
            self.station.checa_tempo_expirou()
                
            # Processa a requisição e envia a resposta
            response_data = RequestHandler.process_request(data)
            response_json = ResponseView.format_response(response_data)
            conn.send(response_json.encode())
                
        except Exception as e:
            print(f"[!] Erro ao processar conexão de {addr}: {str(e)}")
        finally:
            conn.close()
            print(f"[-] Conexão encerrada com {addr}")
            
    def start(self):
        """
        Mantém o servidor rodando e processando conexões em threads separadas
        """
        print("[*] Aguardando conexões...")
        while True:
            try:
                conn, addr = self.server.accept()
                # Cria uma nova thread para cada cliente
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr)
                )
                client_thread.start()
                print(f"[*] Thread iniciada para {addr}")
            except Exception as e:
                print(f"[!] Erro ao aceitar conexão: {str(e)}")

if __name__ == "__main__":
    server = ServerController()
    server.start()