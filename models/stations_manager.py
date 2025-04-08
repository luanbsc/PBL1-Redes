import threading
import time

class StationsManager:
    _instance = None
    _lock = threading.Lock()
    _data_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(StationsManager, cls).__new__(cls)
                    cls._instance.stations_data = {}
        return cls._instance

    def update_station(self, station_ip, station_data):
        """Atualiza os dados de um posto específico"""
        with self._data_lock:
            self.stations_data[station_ip] = {
                "data": station_data,
                "last_update": time.time()
            }
            print(f"[UDP] Dados do posto {station_ip} atualizados")
            print(f"[UDP] Total de postos registrados: {len(self.stations_data)}")

    def get_all_stations(self):
        """Retorna os dados de todos os postos ativos"""
        with self._data_lock:
            # Remove postos inativos
            current_time = time.time()
            expired_stations = [
                ip for ip, data in self.stations_data.items()
                if current_time - data["last_update"] > 30
            ]
            for ip in expired_stations:
                del self.stations_data[ip]
                print(f"[INFO] Posto {ip} removido por inatividade")
            
            # Retorna apenas os dados dos postos ativos
            return {
                ip: data["data"] for ip, data in self.stations_data.items()
            }

    def get_available_stations(self):
        """Retorna apenas os postos disponíveis"""
        with self._data_lock:
            all_stations = self.get_all_stations()
            available_stations = {}
            for ip, stations in all_stations.items():
                available_stations[ip] = {
                    name: data for name, data in stations.items()
                    if not data["ocupado"]
                }
            return available_stations

    def get_station_by_ip(self, station_ip):
        """Retorna os dados de um posto específico pelo IP"""
        with self._data_lock:
            if station_ip in self.stations_data:
                return self.stations_data[station_ip]["data"]
            return None 