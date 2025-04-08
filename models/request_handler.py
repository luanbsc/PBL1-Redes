import json
# nao to usando mais o socket (pois nao vamos conectar a outra imagem) from service.socket_service import send_to_container, get_recharge_station
from controllers.station_controller import StationController

# Instância única do StationController
station = StationController()  # MESMA INSTANCIA SEMPRE 

class RequestHandler:
    @staticmethod
    def process_request(data):
        """
        Processa a requisição recebida e retorna a resposta apropriada
        """
        try:
            request_data = json.loads(data)
            action = request_data.get("action")
            
            if action == "get_station_status":
                # Retorna os dados de todos os postos armazenados
                return station.get_all_stations()
            elif action == "get_available_stations":
                # Retorna apenas os postos disponíveis
                return station.get_available_stations()
            elif action == "get_station_mais_proximo":
                x = request_data.get("x")
                y = request_data.get("y")
                id = request_data.get("id")
                return station.get_station_mais_proximo(x, y, id)
            elif action == "get_stations_by_id":
                id_usuario = request_data.get("id")
                return station.get_stations_by_id(id_usuario)
            elif action == "release_stations_by_id":
                id_usuario = request_data.get("id")
                return station.release_stations_by_id(id_usuario)
            elif action == "release_all_stations":
                return station.release_all_stations()
            elif action == "low_battery":
                # Nova ação para bateria baixa
                x = request_data.get("x")
                y = request_data.get("y")
                id = request_data.get("id")
                return station.get_station_mais_proximo(x, y, id)
            elif action == "update_station":
                # Nova ação para atualizar dados do posto
                station_data = request_data.get("station_data")
                ip_address = request_data.get("ip_address")
                return station.update_station(station_data, ip_address)
            elif action == "checa_tempo_expirou":
                # Nova ação para verificar tempos expirados
                return station.checa_tempo_expirou()
            else:
                return {"status": "erro", "mensagem": "Ação não reconhecida"}
                
        except json.JSONDecodeError:
            return {"status": "erro", "mensagem": "JSON inválido"}
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)}
