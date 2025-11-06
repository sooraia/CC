"""Dicionários para tipos de missão e os seus parãmetros adicionais e eventos de progresso"""

MISSION_TYPES = {
    'S': {  # Coleção de amostras
        'name': 'SAMPLE_COLLECTION',
        'param': {
            'S': 'SOIL',
            'R': 'ROCK', 
            'A': 'ATMOSPHERE',
            'W': 'WATER'
        },
        'events': {
            '1': 'SAMPLE_COLLECTED',
            '2': 'ANALYSIS_STARTED',
            '3': 'ANALYSIS_COMPLETED',
            '4': 'COLLECTION_FAILED'
        }
    },
    'I': { # Captura de Imagens
        'name': 'IMAGE_CAPTURE',
        'params': {
            'P': 'PANORAMIC',
            'C': 'INFRARED', 
            'M': 'MACRO'
        },
        'events': {
            '1': 'IMAGE_CAPTURED',
            '2': 'CAMERA_ERROR', 
            '3': 'LOW_LIGHT_CONDITION',
            '4': 'IMAGE_PROCESSED'
        }
    },
    'E': {  # Análise Ambiental
        'name': 'ENVIRONMENTAL_ANALYSIS',
        'params': {
            'T': 'TEMPERATURE',
            'R': 'RADIATION',
            'P': 'PRESSURE',
            'H': 'HUMIDITY'
        },
        'events': {
            '1': 'MEASUREMENT_TAKEN',
            '2': 'ANOMALY_DETECTED',
            '3': 'BASELINE_ESTABLISHED',
            '4': 'SENSOR_CALIBRATION'
        }
    },
    'D': {  # Instalação de equipamentos
        'name': 'EQUIPMENT_DEPLOYMENT',
        'params': {
            'S': 'SEISMOMETER',
            'W': 'WEATHER_STATION',
            'M': 'MARKER',
            'C': 'COMMUNICATION_RELAY'
        },
        'events' : {
            '1': 'EQUIPMENT_DEPLOYED',
            '2': 'CALIBRATION_IN_PROGRESS',
            '3': 'DEPLOYMENT_FAILED'
        }
    },
    'M': {  # Mapeamento do terreno
        'name': 'MAPPING',
        'param': {
            'H': 'HIGH',
            'M': 'MEDIUM', 
            'L': 'LOW'
        },
        'events': {
            '1': 'AREA_MAPPED',
            '2': 'OBSTACLE_DETECTED',
            '3': 'TERRAIN_ANALYSIS',
            '4': 'MAPPING_COMPLETE'
        }
    },
    'P': {  # Transferência de energia
        'name': 'POWER_TRANSFER',
        'events': {
            '1': 'CONNECTED',
            '2': 'TRANSFERRING_POWER', 
            '3': 'TRANSFER_COMPLETE',
            '4': 'TRANSFER_FAILED',
            '5': 'ERROR_INSUFFICIENT_ENERGY'
        }
    }
}

def get_mission_name(mission_code: str) -> str:
    return MISSION_TYPES.get(mission_code, {}).get('name', 'UNKNOWN')

def get_param_name(mission_code: str, param_code: str) -> str:
    return MISSION_TYPES.get(mission_code, {}).get('param', {}).get(param_code, 'UNKNOWN')

def get_event_name(mission_code: str, event_code: str) -> str:
    return MISSION_TYPES.get(mission_code, {}).get('events', {}).get(event_code, 'UNKNOWN')

def get_mission_by_name(mission_name: str) -> tuple:
    for code, data in MISSION_TYPES.items():
        if data['name'] == mission_name:
            return code, data
    return None, None