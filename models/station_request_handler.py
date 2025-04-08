import json
from controllers.station_controller import StationController

# Instância única do StationController
station = StationController()

class StationRequestHandler:
    @staticmethod
    def process_request(data):
        """
        Processa a requisição recebida e retorna a resposta apropriada
        """
        try:
            request_data = json.loads(data)
            action = request_data.get("action")
            
            if action == "get_station_status":
                return station.get_all_stations()
            elif action == "get_available_stations":
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
            else:
                return {"status": "erro", "mensagem": "Ação não reconhecida"}
                
        except json.JSONDecodeError:
            return {"status": "erro", "mensagem": "JSON inválido"}
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)} 