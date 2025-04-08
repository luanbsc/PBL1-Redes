import json
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
            
            if action == "update_station_data":
                # Atualiza os dados do posto com os dados recebidos
                new_data = request_data.get("data")
                if new_data:
                    # Substitui os dados do posto atual pelos novos dados
                    station.posto = new_data
                    return {"status": "sucesso", "mensagem": "Dados do posto atualizados com sucesso"}
                else:
                    return {"status": "erro", "mensagem": "Dados não fornecidos"}
            else:
                return {"status": "erro", "mensagem": "Ação não reconhecida"}
                
        except json.JSONDecodeError:
            return {"status": "erro", "mensagem": "JSON inválido"}
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)} 