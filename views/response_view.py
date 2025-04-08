import json

class ResponseView:
    @staticmethod
    def format_response(response_data):
        """
        Formata a resposta em JSON.
        """
        return json.dumps(response_data, ensure_ascii=False)
