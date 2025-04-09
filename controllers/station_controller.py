import time
import math
import threading
from controllers.socket_controller import SocketController

class StationController:
    # Padrão Singleton para garantir uma única instância
    _instance = None
    _lock = threading.Lock()
    _stations_lock = threading.Lock()  # Lock específico para operações nos postos

    def __new__(cls):
        print("[DEBUG] Criando nova instância do StationController")
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(StationController, cls).__new__(cls)
                    cls._instance.charging_stations = {}
                    cls._instance.stations_ips = {}  # Armazena os IPs dos postos
                    cls._instance.last_update = {}   # Armazena o último update de cada posto
        return cls._instance

    def update_station(self, station_data, ip_address,port):
        print(f"[DEBUG] Atualizando posto com dados: {station_data}")
        """Atualiza os dados de um posto recebido via UDP"""
        with self._stations_lock:
            try:
                
                # Converte os dados recebidos para o formato interno
                station_name = list(station_data.keys())[0]
                station_info = station_data[station_name]
                print(f"[DEBUG] Nome do posto: {station_name}")
                print(f"  VALOR DO STATION_INFO : {station_info}")
                
                # Verifica se o posto já existe
                if station_name in self.charging_stations:
                    print(f"[DEBUG] Posto {station_name} já existe, atualizando...")
                    # Atualiza os dados do posto existente
                    self.charging_stations[station_name].update({
                        "x": station_info["x"],
                        "y": station_info["y"],
                        "ocupado": station_info["ocupado"],
                        "tempo_expiracao": station_info.get("tempo_expiracao", {}),
                        "id": station_info.get("id"),
                        "queue": station_info.get("queue", [])
                    })
                else:
                    print(f"[DEBUG] Posto {station_name} não existe, criando novo...")
                    # Adiciona um novo posto
                    self.charging_stations[station_name] = {
                        "x": station_info["x"],
                        "y": station_info["y"],
                        "ocupado": station_info["ocupado"],
                        "tempo_expiracao": station_info.get("tempo_expiracao", {}),
                        "id": station_info.get("id"),
                        "queue": station_info.get("queue", [])
                    }
                
                # Atualiza o IP e a porta do posto
                self.stations_ips[station_name] = (ip_address, port)
                print(f"[DEBUG] IP e porta do posto {station_name}: {self.stations_ips[station_name]}")
                self.last_update[station_name] = time.time()
                print(f"[DEBUG] Posto {station_name} atualizado com sucesso")
                
                return {"status": "sucesso", "mensagem": f"Posto {station_name} atualizado"}
            except Exception as e:
                print(f"[DEBUG] Erro ao atualizar posto: {str(e)}")
                return {"status": "erro", "mensagem": str(e)}

    def get_all_stations(self):
        print("[DEBUG] Obtendo todos os postos")
        current_time = time.time()
        active_stations = {}
        stations_to_remove = []

        for station_name, last_update in self.last_update.items():
            if current_time - last_update <= 30:
                active_stations[station_name] = self.charging_stations[station_name]
            else:
                stations_to_remove.append(station_name)

        for station_name in stations_to_remove:
            self.charging_stations.pop(station_name, None)
            self.stations_ips.pop(station_name, None)
            self.last_update.pop(station_name, None)
            print(f"[DEBUG] Posto {station_name} removido por inatividade")

        print(f"[DEBUG] Postos ativos: {active_stations}")
        return active_stations

    def get_available_stations(self):
        print("[DEBUG] Obtendo postos disponíveis")
        """Retorna os postos disponíveis (não ocupados)"""
        with self._stations_lock:
            try:
                available = {
                    nome: dados for nome, dados in self.charging_stations.items()
                    if not dados["ocupado"] and time.time() - self.last_update.get(nome, 0) <= 30
                }
                print(f"[DEBUG] Postos disponíveis: {available}")
                return available
            except Exception as e:
                print(f"[DEBUG] Erro ao obter postos disponíveis: {str(e)}")
                return {
                    "status": "erro",
                    "mensagem": f"Erro ao obter postos disponíveis: {str(e)}"
                }

    def get_station_ip(self, station_name):
        print(f"[DEBUG] Obtendo IP e porta do posto {station_name}")
        """Retorna o IP e a porta de um posto específico"""
        with self._stations_lock:
            ip_port = self.stations_ips.get(station_name)
            print(f"[DEBUG] IP e porta do posto {station_name}: {ip_port}")
            return ip_port

    def get_station_mais_proximo(self, x, y, id):
        print(f"[DEBUG] Buscando posto mais próximo para x={x}, y={y}, id={id}")
        """Retorna o nome do posto mais próximo (não ocupado) e marca como ocupado por 2 minutos."""
        with self._stations_lock:
            #garantiremos a atualizacao dos postos expirados antes de ver quem pode ser reservado
            self.get_all_stations()
            print("[DEBUG] Verificando se carro já tem reserva")
            carro_reservado = self.checa_carro_reserva(id)
            print(f"[DEBUG] Resultado da verificação de reserva: {carro_reservado}")
            
            if carro_reservado == False:
                print("[DEBUG] Carro não tem reserva, procurando posto mais próximo")
                menorTempo = 9999999
                print(f"[DEBUG] Postos disponíveis: {self.charging_stations}")
                
                for nome, dados_posto in self.charging_stations.items():
                    print(f"[DEBUG] Analisando posto {nome}")
                    if time.time() - self.last_update.get(nome, 0) <= 30:  # Só considera postos ativos
                        print(f"[DEBUG] Posto {nome} está ativo")
                        tempo = len(dados_posto["queue"]) * 120 + calcular_distancia(x, y, dados_posto["x"], dados_posto["y"])
                        print(f"[DEBUG] Tempo calculado para posto {nome}: {tempo}")
                        if tempo < menorTempo:
                            menorTempo = tempo
                            station_mais_proximo = nome
                            print(f"[DEBUG] Novo posto mais próximo: {station_mais_proximo}")
                    
                print(f"[DEBUG] Posto mais próximo encontrado: {station_mais_proximo}")
                print("[DEBUG] Marcando posto como ocupado")
                self.set_station_occupied(station_mais_proximo, id)
                    
                return {
                    "status": "sucesso",
                    "mensagem": f"Parabens, você acabou de reservar o posto: {station_mais_proximo}"
                }
            else:
                print(f"[DEBUG] Carro já tem reserva em {carro_reservado[0]}")
                return {
                    "status": "erro",
                    "mensagem": f"Este carro já possui uma reserva no {carro_reservado[0]}"
                }

    def checa_carro_reserva(self, id):
        print(f"[DEBUG] Verificando reserva do carro {id}")
        """Verifica se um carro possui reserva em algum posto e o retorna"""
        cont = 0
        print(f"[DEBUG] Postos disponíveis: {self.charging_stations}")
        for nome in self.charging_stations.keys():
            print(f"[DEBUG] Verificando posto {nome}")
            print(f"[DEBUG] Queue do posto {nome}: {self.charging_stations[nome]['queue']}")
            if id in self.charging_stations[nome]["queue"]:
                print(f"[DEBUG] Carro encontrado no posto {nome}")
                return list(self.charging_stations.items())[cont]
            cont += 1
        print("[DEBUG] Carro não encontrado em nenhum posto")
        return False


    def checa_tempo_expirou(self):
        print("[DEBUG] Verificando tempos expirados")
        """Libera os carros das estações cujo tempo já expiraram."""
        with self._stations_lock:
            try:
                ids = []
                for nome in self.charging_stations.keys():
                    if self.charging_stations[nome]["queue"] == []:
                        self.charging_stations[nome]["ocupado"] = False
                        print(f"[DEBUG] Posto {nome} liberado por fila vazia")
                    for id, tempo in self.charging_stations[nome]["tempo_expiracao"].items():
                        if time.time() > tempo:
                            ids.append(id+'/'+nome)
                            print(f"[DEBUG] Tempo expirado para carro {id} no posto {nome}")
                
                for id_carro_remover in ids:
                    print(f"[DEBUG] Removendo reserva do carro {id_carro_remover.split('/')[0]} do posto {id_carro_remover.split('/')[1]}")
                    self.remover_reserva_carro(id_carro_remover.split('/')[0])
                
                    posto_ip_port = self.stations_ips.get(id_carro_remover.split('/')[1])
                    if not posto_ip_port:
                        print(f"[DEBUG] IP e porta não encontrados para o posto {id_carro_remover.split('/')[1]}")
                        continue  # Pula se não tiver IP do posto

                    response = SocketController.send_station_update(
                        {id_carro_remover.split('/')[1]: self.charging_stations[id_carro_remover.split('/')[1]]},
                        posto_ip_port
                    )

                    if response["status"] == "sucesso":
                        print(f"[DEBUG] Atualização enviada com sucesso para o posto {id_carro_remover.split('/')[1]}")
                    else:
                        print(f"[DEBUG] Erro ao atualizar posto {id_carro_remover.split('/')[1]}: {response['mensagem']}")

                return {"status": "sucesso", "mensagem": "Estações expiradas foram liberadas."}
            except Exception as e:
                print(f"[DEBUG] Erro ao verificar tempos expirados: {str(e)}")
                return {"status": "erro", "mensagem": f"Erro ao liberar estações expiradas: {str(e)}"}

    def remover_reserva_carro(self, id):
        print(f"[DEBUG] Removendo reserva do carro {id}")
        """Libera o carro do posto em que ele está reservado."""
        try:
            for nome, dados in self.charging_stations.items():
                if id in dados["queue"]:
                    print(f"[DEBUG] Removendo carro {id} da fila do posto {nome}")
                    dados["queue"].remove(id)
                    dados["tempo_expiracao"].pop(id)
        except Exception as e:
            print(f"[DEBUG] Erro ao remover reserva: {str(e)}")
            print(f"Erro ao liberar reserva do carro: {str(e)}")

    def set_station_occupied(self, station_name, id):
        print(f"[DEBUG] Marcando posto {station_name} como ocupado pelo carro {id}")
        """Marca um posto como ocupado por 2 minutos."""
        try:
            if station_name in self.charging_stations:
                print(f"[DEBUG] Status atual do posto {station_name}: {self.charging_stations[station_name]}")
                    
                # Cria uma cópia dos dados atuais do posto
                station_data = self.charging_stations[station_name].copy()
                    
                # Atualiza os dados da cópia
                station_data["ocupado"] = True
                if len(station_data["queue"]) > 0:
                    id_carro_anterior = station_data["queue"][-1]
                    station_data["tempo_expiracao"][id] = station_data["tempo_expiracao"][id_carro_anterior] + 120  # 2 minutos
                else:
                    station_data["tempo_expiracao"][id] = time.time() + 120  # 2 minutos
                station_data["reservation_data"] = time.time()
                station_data["id"] = id
                station_data["queue"].append(id)
                    
                # Obtém o IP e a porta do posto
                posto_ip_port = self.stations_ips.get(station_name)
                if not posto_ip_port:
                    raise Exception(f"IP e porta não encontrados para o posto {station_name}")
                    
                # Envia os dados atualizados diretamente para o posto
                response = SocketController.send_station_update({station_name: station_data}, posto_ip_port)
                    
                if response["status"] == "sucesso":
                    # Se o posto aceitou a atualização, aplica as mudanças localmente
                    self.charging_stations[station_name] = station_data
                    print(f"[DEBUG] Novo status do posto {station_name}: {self.charging_stations[station_name]}")
                else:
                    print(f"[DEBUG] Erro ao atualizar posto: {response['mensagem']}")
                    raise Exception(response["mensagem"])
            else:
                print(f"[DEBUG] Posto {station_name} não encontrado")
        except Exception as e:
            print(f"[DEBUG] Erro ao marcar posto como ocupado: {str(e)}")
            print(f"Erro ao marcar posto como ocupado: {str(e)}")

    def reset_station(self, station_name):
        print(f"[DEBUG] Resetando posto {station_name}")
        """Libera um posto manualmente."""
        try:
            if station_name in self.charging_stations:
                print(f"[DEBUG] Status atual do posto {station_name}: {self.charging_stations[station_name]}")
                self.charging_stations[station_name]["ocupado"] = False
                self.charging_stations[station_name]["tempo_expiracao"] = {}
                self.charging_stations[station_name]["queue"] = []
                self.charging_stations[station_name]["reservation_data"] = None
                self.charging_stations[station_name]["id"] = None
                print(f"[DEBUG] Novo status do posto {station_name}: {self.charging_stations[station_name]}")
            else:
                print(f"[DEBUG] Posto {station_name} não encontrado")
        except Exception as e:
            print(f"[DEBUG] Erro ao resetar posto: {str(e)}")
            print(f"Erro ao liberar a estação: {str(e)}")

    def get_stations_by_id(self, id_usuario):
        print(f"[DEBUG] Buscando estações do usuário {id_usuario}")
        self.get_all_stations()
        """Retorna todas as estações ocupadas por um determinado ID e a mensagem com a estação mais próxima."""
        with self._stations_lock:
            try:
                # Filtra as estações ocupadas com o id_usuario correspondente
                stations_ocupadas = {
                    nome: dados for nome, dados in self.charging_stations.items()
                    if dados.get("ocupado") and id_usuario in dados.get("queue")
                }
                print(f"[DEBUG] Estações ocupadas encontradas: {stations_ocupadas}")

                if stations_ocupadas:
                    # Considerando a primeira estação ocupada como a mais próxima
                    station_mais_proximo = list(stations_ocupadas.keys())[0]
                    print(f"[DEBUG] Estação mais próxima: {station_mais_proximo}")
                    return {
                        "status": "sucesso",
                        "mensagem": f"Postos reservados: {station_mais_proximo} (você é o {self.charging_stations[station_mais_proximo]['queue'].index(id_usuario)+1}º da fila)"
                    }
                else:
                    print("[DEBUG] Nenhuma estação ocupada encontrada")
                    return {
                        "status": "erro",
                        "mensagem": "Nenhuma estação ocupada encontrada para o usuário."
                    }
            except Exception as e:
                print(f"[DEBUG] Erro ao buscar estações: {str(e)}")
                return {
                    "status": "erro",
                    "mensagem": f"Erro inesperado: {str(e)}"
                }

    def release_stations_by_id(self, id_usuario):
        print(f"[DEBUG] Liberando estações do usuário {id_usuario}")
        """Libera todas as estações ocupadas por um determinado ID e retorna status no formato JSON."""
        with self._stations_lock:
            try:
                stations_lib = []  # Lista para armazenar os nomes das estações liberadas

                for nome, dados in self.charging_stations.items():
                    if dados.get("ocupado") and dados.get("id") == id_usuario:
                        print(f"[DEBUG] Liberando posto {nome}")
                        self.reset_station(nome)  # Usa a função existente para liberar o posto
                        stations_lib.append(nome)

                if stations_lib:
                    print(f"[DEBUG] Postos liberados: {stations_lib}")
                    return {
                        "status": "sucesso",
                        "mensagem": f"As estações liberadas para o usuário {id_usuario} são: {', '.join(stations_lib)}"
                    }
                else:
                    print("[DEBUG] Nenhum posto encontrado para liberar")
                    return {
                        "status": "erro",
                        "mensagem": "Nenhuma estação ocupada encontrada para o usuário."
                    }
            except Exception as e:
                print(f"[DEBUG] Erro ao liberar estações: {str(e)}")
                return {
                    "status": "erro",
                    "mensagem": f"Erro inesperado ao liberar as estações: {str(e)}"
                }

    def release_all_stations(self):
        print("[DEBUG] Liberando todas as estações")
        """Libera todos os postos ocupados, sem precisar de ID de usuário e retorna status no formato JSON."""
        with self._stations_lock:
            try:
                stations_lib = []  # Lista para armazenar os nomes das estações liberadas

                for nome, dados in self.charging_stations.items():
                    if dados.get("ocupado"):
                        print(f"[DEBUG] Liberando posto {nome}")
                        self.reset_station(nome)  # Usa a função existente para liberar o posto
                        stations_lib.append(nome)

                if stations_lib:
                    print(f"[DEBUG] Postos liberados: {stations_lib}")
                    return {
                        "status": "sucesso",
                        "mensagem": f"As estações liberadas são: {', '.join(stations_lib)}"
                    }
                else:
                    print("[DEBUG] Nenhum posto encontrado para liberar")
                    return {
                        "status": "erro",
                        "mensagem": "Nenhuma estação ocupada foi encontrada para liberar."
                    }
            except Exception as e:
                print(f"[DEBUG] Erro ao liberar todas as estações: {str(e)}")
                return {
                    "status": "erro",
                    "mensagem": f"Erro inesperado ao liberar todas as estações: {str(e)}"
                }

def calcular_distancia(x1, y1, x2, y2):
    print(f"[DEBUG] Calculando distância entre ({x1},{y1}) e ({x2},{y2})")
    """Calcula a distância Euclidiana entre dois pontos."""
    distancia = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    print(f"[DEBUG] Distância calculada: {distancia}")
    return distancia