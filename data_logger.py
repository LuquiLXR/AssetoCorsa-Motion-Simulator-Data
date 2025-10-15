"""
Módulo para el logging de datos de suspensión en formato JSON
Maneja la escritura de archivos y organización de datos
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any


class SuspensionDataLogger:
    """Clase para manejar el logging de datos de suspensión"""
    
    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        self.current_session_file = None
        self.session_data = []
        self.session_start_time = None
        
        # Crear directorio de salida si no existe
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"📁 Directorio creado: {self.output_dir}")
    
    def start_session(self):
        """Inicia una nueva sesión de logging"""
        self.session_start_time = datetime.now()
        timestamp = self.session_start_time.strftime("%Y%m%d_%H%M%S")
        self.current_session_file = os.path.join(
            self.output_dir, 
            f"suspension_data_{timestamp}.json"
        )
        self.session_data = []
        
        print(f"🚀 Nueva sesión iniciada: {self.current_session_file}")
        return self.current_session_file
    
    def log_data(self, suspension_data: Dict[str, Any]):
        """Registra un punto de datos de suspensión"""
        if suspension_data is None:
            return False
        
        # Agregar timestamp legible
        readable_time = datetime.fromtimestamp(suspension_data['timestamp']).isoformat()
        
        # Crear entrada de datos con formato limpio
        data_entry = {
            'timestamp': suspension_data['timestamp'],
            'readable_time': readable_time,
            'suspension': {
                'front_left': suspension_data['front_left'],
                'front_right': suspension_data['front_right'],
                'rear_left': suspension_data['rear_left'],
                'rear_right': suspension_data['rear_right']
            },
            'context': {
                'speed_kmh': suspension_data.get('speed_kmh', 0),
                'packet_id': suspension_data.get('packet_id', 0)
            }
        }
        
        self.session_data.append(data_entry)
        return True
    
    def save_session(self):
        """Guarda la sesión actual en archivo JSON"""
        if not self.session_data or not self.current_session_file:
            print("⚠️ No hay datos para guardar")
            return False
        
        try:
            # Crear metadata de la sesión
            session_info = {
                'session_metadata': {
                    'start_time': self.session_start_time.isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'total_samples': len(self.session_data),
                    'duration_seconds': (datetime.now() - self.session_start_time).total_seconds(),
                    'file_version': '1.0'
                },
                'data': self.session_data
            }
            
            # Guardar archivo JSON
            with open(self.current_session_file, 'w', encoding='utf-8') as f:
                json.dump(session_info, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Sesión guardada: {self.current_session_file}")
            print(f"📊 Total de muestras: {len(self.session_data)}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando sesión: {e}")
            return False
    
    def save_realtime(self, suspension_data: Dict[str, Any]):
        """Guarda datos en tiempo real (para sesiones largas)"""
        if not self.current_session_file:
            self.start_session()
        
        # Agregar datos al buffer
        if self.log_data(suspension_data):
            # Guardar cada 100 muestras para evitar pérdida de datos
            if len(self.session_data) % 100 == 0:
                self.save_session()
                print(f"🔄 Auto-guardado: {len(self.session_data)} muestras")
    
    def get_session_stats(self):
        """Obtiene estadísticas de la sesión actual"""
        if not self.session_data:
            return None
        
        return {
            'total_samples': len(self.session_data),
            'duration': (datetime.now() - self.session_start_time).total_seconds() if self.session_start_time else 0,
            'file_path': self.current_session_file,
            'start_time': self.session_start_time.isoformat() if self.session_start_time else None
        }
    
    def create_test_file(self):
        """Crea un archivo de prueba para verificar el sistema"""
        test_data = {
            'test_info': {
                'created_at': datetime.now().isoformat(),
                'purpose': 'Validación del sistema de logging',
                'status': 'Sistema funcionando correctamente'
            },
            'sample_data': {
                'timestamp': 1642248600.123,
                'readable_time': '2024-01-15T10:30:00.123',
                'suspension': {
                    'front_left': 0.045,
                    'front_right': 0.043,
                    'rear_left': 0.038,
                    'rear_right': 0.040
                },
                'context': {
                    'speed_kmh': 120.5,
                    'packet_id': 12345
                }
            }
        }
        
        test_file = os.path.join(self.output_dir, "test_output.json")
        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Archivo de prueba creado: {test_file}")
            return test_file
        except Exception as e:
            print(f"❌ Error creando archivo de prueba: {e}")
            return None