"""Dicionários para tipos de missão e os seus parãmetros adicionais/eventos de progresso"""

#em vez de usares

MISSION_TYPES = {
    'S': {  # Coleção de amostras
        'name': 'Sample Collection',
        'param': {'S': 'Soil', 'R': 'Rock', 'A': 'Atmosphere', 'W': 'Water'},
        'events': {
            '1': 'Collecting Sample', # 25%
            '2': 'Starting Analysis', # 50% 
            '3': 'Analysis Completed', # 75%
            '4': 'Collection Failed' # Error
        }
    },
    'I': {  # Captura de imagens
        'name': 'Image Capture',
        'param': {'P': 'Panoramic', 'C': 'Infrared', 'M': 'Macro'},
        'events': {
            '1': 'Capturing Imgage', # 25%
            '2': 'Processing Image', # 50%
            '3': 'Quality Verified',# 75%
            '4': 'Camera Error' # Error
        }
    },
    'E': {  # Análise ambiental
        'name': 'Environmental Analysis',
        'param': {'T': 'Temperature', 'R': 'Radiation', 'P': 'Pressure', 'H': 'Humidity'},
        'events': {
            '1': 'Initial Readings',
            '2': 'Analysing Data',
            '3': 'Report Complete',
            '4': 'Sensor Failure'
        }
    },
    'D': {  # Instalação de equipamentos
        'name': 'Equipment Deployment',
        'param': {'S': 'Seismometer', 'W': 'Weather Station', 'M': 'Marker', 'C': 'Communication Relay'},
        'events': {
            '1': 'Positioning Equipment',
            '2': 'Calibrating',
            '3': 'Deployment Success',
            '4': 'Deployment Failed'
        }
    },
    'M': {  # Mapeamento do terreno
        'name': 'Mapping',
        'param': {'H': 'HIGH', 'M': 'MEDIUM', 'L': 'LOW'},
        'events': {
            '1': 'Scanning area',
            '2': 'Processing Data',
            '3': 'Map Generated',
            '4': 'Mapping Error'
        }
    },
    'A': {  # Auto-diagnóstico
        'name': 'Auto-Diagnostic',
        'events': {
            '1': 'Starting Diagnostic',
            '2': 'Checking Systems',
            '3': 'Diagnostic Complete',
            '4': 'Critical Error'
        }
    }
}

def get_mission_name(mission_code: str) -> str:
    return MISSION_TYPES.get(mission_code, {}).get('name', 'UNKNOWN')

def get_param_name(mission_code: str, param_code: str) -> str:
    return MISSION_TYPES.get(mission_code, {}).get('param', {}).get(param_code, 'None')

def get_event_name(mission_code: str, event_code: str) -> str:
    return MISSION_TYPES.get(mission_code, {}).get('events', {}).get(event_code, 'UNKNOWN')

def get_mission_by_name(mission_name: str) -> tuple:
    for code, data in MISSION_TYPES.items():
        if data['name'] == mission_name:
            return code, data
    return None, None

def get_param_code(mission_code: str, param_name: str) -> str:
    mission_data = MISSION_TYPES.get(mission_code, {})
    params = mission_data.get('param', {})
    
    for code, name in params.items():
        if name == param_name:
            return code
    return '0'  # Código default se não encontrar