
import time

def get_mission(rover_id):
    """Retorna UMA missão fixa para testes"""
    return {
        'mission_id': f'MISSION-{rover_id}-001',
        'area': [
            [2.0, 1.5],
            [2.5, 2.5],
        ],
        'task': 'S',  # Sample Collection
        'task_param': 'S',  # Soil
        'duration': 300,  # 5 minutos
        'update_interval': 30,  # Reports a cada 30 segundos
        'timestamp': time.time()
    }