import socket
import threading
import json
import time
from models.request_handler import RequestHandler
from controllers.station_controller import StationController

class StationServerController:
    def __init__(self, host="0.0.0.0", tcp_port=8016, udp_port=8015):
        print('Iniciando o StationServerController')
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        
        # Configuração do servidor TCP
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((self.host, self.tcp_port))
        self.tcp_socket.listen(5)
        print(f"[*] Servidor de postos2 rodando na porta {self.tcp_port}")

        # Configuração do socket UDP para comunicação com o servidor principal
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_host = "192.168.0.114"  # IP do servidor principal
        self.server_port = self.udp_port  # Porta do servidor principal

        # Usa a instância única do StationController
        self.station = StationController()
        self.request_handler = RequestHandler()

        # Inicia a thread para enviar dados periodicamente
        self.udp_thread = threading.Thread(target=self.send_station_data)
        self.udp_thread.daemon = True
        self.udp_thread.start()

    def send_station_data(self):
        """Envia os dados do posto para o servidor principal a cada 10 segundos"""
        while True:
            try:
                print('dadtentaaaos enviados')
                self.station.checa_tempo_expirou()
                # Obtém os dados do posto
                station_data = self.station.get_all_stations()
                
                # Converte para JSON
                
                data_to_send = {
                    "type": "station_update",
                    "data": station_data
                }
                data_json = json.dumps(data_to_send)
                

                # Envia para o servidor principal
                self.udp_socket.sendto(data_json.encode(),(self.server_host, self.server_port))
                print(f"dados enviados {data_json}")
                
                time.sleep(10)
            except Exception as e:
                print(f"Erro ao enviar dados do posto: {e}")

    def handle_client(self, conn, addr):
        """
        Função que será executada em uma thread separada para cada cliente
        """
        try:
            print(f"[+] Conexão recebida de {addr}")
            data = conn.recv(1024).decode()
            print(f"[>] Dados recebidos de {addr}: {data}")

            # Processa a requisição e envia a resposta
            response_data = self.request_handler.process_request(data)
            response_json = json.dumps(response_data)
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
                conn, addr = self.tcp_socket.accept()
                # Cria uma nova thread para cada cliente
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr)
                )
                client_thread.start()
                print(f"[*] Thread iniciada para {addr}")
                
            except Exception as e:
                print(f"[!] Erro ao aceitar conexão: {str(e)}")

    def stop(self):
        """Para os servidores TCP e UDP."""
        if self.udp_socket:
            self.udp_socket.close()
        if self.tcp_socket:
            self.tcp_socket.close() 