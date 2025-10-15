"""
Script principal para extraer datos de suspensión de Assetto Corsa
Extrae valores brutos de posición de suspensión y los guarda en JSON
"""

import time
import signal
import sys
from ac_shared_memory import ACSharedMemory
from data_logger import SuspensionDataLogger


class SuspensionDataExtractor:
    """Clase principal para extraer datos de suspensión de AC"""
    
    def __init__(self, sampling_rate_hz: float = 10.0):
        self.ac_memory = ACSharedMemory()
        self.logger = SuspensionDataLogger()
        self.sampling_rate = sampling_rate_hz
        self.sampling_interval = 1.0 / sampling_rate_hz
        self.running = False
        
        # Configurar manejo de señales para cierre limpio
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Maneja la señal de interrupción para cierre limpio"""
        print("\n🛑 Señal de interrupción recibida. Cerrando...")
        self.stop()
    
    def test_system(self):
        """Prueba el sistema sin conectar a AC"""
        print("🧪 Ejecutando prueba del sistema...")
        
        # Probar logger
        test_file = self.logger.create_test_file()
        if test_file:
            print("✅ Sistema de logging funcionando correctamente")
            return True
        else:
            print("❌ Error en sistema de logging")
            return False
    
    def connect_to_ac(self):
        """Conecta con Assetto Corsa"""
        print("🔌 Intentando conectar con Assetto Corsa...")
        
        if self.ac_memory.connect():
            # Verificar que AC esté enviando datos
            if self.ac_memory.is_ac_running():
                print("✅ Assetto Corsa detectado y enviando datos")
                return True
            else:
                print("⚠️ Conectado pero AC no está enviando datos")
                print("💡 Inicia una sesión de carrera en AC")
                return False
        else:
            print("❌ No se pudo conectar con Assetto Corsa")
            print("💡 Asegúrate de que AC esté ejecutándose")
            return False
    
    def start_extraction(self):
        """Inicia la extracción de datos"""
        if not self.connect_to_ac():
            return False
        
        print(f"🚀 Iniciando extracción de datos a {self.sampling_rate} Hz")
        print("📊 Presiona Ctrl+C para detener")
        
        # Iniciar sesión de logging
        session_file = self.logger.start_session()
        self.running = True
        
        sample_count = 0
        last_packet_id = 0
        
        try:
            while self.running:
                # Leer datos de suspensión
                suspension_data = self.ac_memory.read_suspension_data()
                
                if suspension_data:
                    # Verificar que los datos sean nuevos
                    current_packet_id = suspension_data.get('packet_id', 0)
                    
                    if current_packet_id != last_packet_id and current_packet_id > 0:
                        # Registrar datos
                        if self.logger.log_data(suspension_data):
                            sample_count += 1
                            last_packet_id = current_packet_id
                            
                            # Mostrar progreso cada 50 muestras
                            if sample_count % 50 == 0:
                                print(f"📈 Muestras capturadas: {sample_count}")
                                
                                # Mostrar datos actuales
                                susp = suspension_data
                                print(f"   FL: {susp['front_left']:.4f} | FR: {susp['front_right']:.4f}")
                                print(f"   RL: {susp['rear_left']:.4f} | RR: {susp['rear_right']:.4f}")
                                print(f"   Velocidad: {susp['speed_kmh']:.1f} km/h")
                else:
                    print("⚠️ No se pudieron leer datos de AC")
                
                # Esperar según la frecuencia de muestreo
                time.sleep(self.sampling_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Interrupción por teclado")
        except Exception as e:
            print(f"\n❌ Error durante extracción: {e}")
        
        finally:
            self.stop()
            print(f"📊 Total de muestras capturadas: {sample_count}")
    
    def stop(self):
        """Detiene la extracción y guarda datos"""
        self.running = False
        
        # Guardar sesión
        if self.logger.session_data:
            self.logger.save_session()
            
            # Mostrar estadísticas
            stats = self.logger.get_session_stats()
            if stats:
                print(f"📈 Estadísticas de la sesión:")
                print(f"   Muestras: {stats['total_samples']}")
                print(f"   Duración: {stats['duration']:.1f} segundos")
                print(f"   Archivo: {stats['file_path']}")
        
        # Desconectar de AC
        self.ac_memory.disconnect()
        print("✅ Sistema detenido correctamente")


def main():
    """Función principal"""
    print("=" * 60)
    print("🏎️  EXTRACTOR DE DATOS DE SUSPENSIÓN - ASSETTO CORSA")
    print("=" * 60)
    print()
    
    # Crear extractor
    extractor = SuspensionDataExtractor(sampling_rate_hz=10.0)  # 10 Hz por defecto
    
    # Probar sistema primero
    if not extractor.test_system():
        print("❌ Fallo en prueba del sistema")
        return
    
    print()
    print("🎯 INSTRUCCIONES:")
    print("1. Asegúrate de que Assetto Corsa esté ejecutándose")
    print("2. Inicia una sesión de carrera (Practice, Race, etc.)")
    print("3. El sistema comenzará a capturar datos automáticamente")
    print("4. Presiona Ctrl+C para detener y guardar")
    print()
    
    input("Presiona Enter cuando AC esté listo...")
    
    # Iniciar extracción
    extractor.start_extraction()


if __name__ == "__main__":
    main()