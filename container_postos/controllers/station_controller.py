import time
import threading
import random
import string
class StationController:
    # Padrão Singleton para garantir uma única instância
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(StationController, cls).__new__(cls)
                    # Gera coordenadas aleatórias para o posto
                    x = random.uniform(0, 500)
                    y = random.uniform(0, 500)
                    # Gera um nome único para o posto
                    timestamp = int(time.time())
                    random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                    nome_posto = f"Posto_{timestamp}_{random_code}"
                    # Inicializa com um único posto
                    cls._instance.posto = {
                        nome_posto: {
                            "x": x,
                            "y": y,
                            "ocupado": False,
                            "tempo_expiracao": {},
                            "id": None,
                            "queue": []
                        }
                    }
        return cls._instance

    def get_all_stations(self):
        """Retorna todos os postos (no caso, apenas um)"""
        return self.posto
    
    
    def remover_reserva_carro(self, id):
        print(f"[DEBUG] Removendo reserva do carro {id}")
        """Libera o carro do posto em que ele está reservado."""
        try:
            for nome, dados in self.posto.items():
                if id in dados["queue"]:
                    print(f"[DEBUG] Removendo carro {id} da fila do posto {nome}")
                    dados["queue"].remove(id)
                    dados["tempo_expiracao"].pop(id)
        except Exception as e:
            print(f"[DEBUG] Erro ao remover reserva: {str(e)}")
            print(f"Erro ao liberar reserva do carro: {str(e)}")
            
            
    
    def checa_tempo_expirou(self):
        print("[DEBUG] Verificando tempos expirados")
        try:
            ids = []
            with self._lock:
                for nome, info in self.posto.items():
                    if info["queue"] == []:
                        info["ocupado"] = False
                        print(f"[DEBUG] Posto {nome} liberado por fila vazia")
                    for id, tempo in info["tempo_expiracao"].items():
                        if time.time() > tempo:
                            ids.append(id + '/' + nome)
                            print(f"[DEBUG] Tempo expirado para carro {id} no posto {nome}")

                for id_carro_remover in ids:
                    carro_id, nome_posto = id_carro_remover.split('/')
                    print(f"[DEBUG] Removendo reserva do carro {carro_id} do posto {nome_posto}")
                    self.remover_reserva_carro(carro_id)

                return {"status": "sucesso", "mensagem": "Estações expiradas foram liberadas."}
        except Exception as e:
            print(f"[DEBUG] Erro ao verificar tempos expirados: {str(e)}")
            return {"status": "erro", "mensagem": f"Erro ao liberar estações expiradas: {str(e)}"}

    