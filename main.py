"""
Script principal para extraer datos de suspensión de Assetto Corsa
Versión optimizada para alta frecuencia y tiempo real
"""

import time
import signal
import sys
import argparse
from ac_shared_memory import ACSharedMemory
from data_logger import SuspensionDataLogger


class SuspensionDataExtractor:
    """Clase principal para extraer datos de suspensión de AC - Versión Optimizada"""
    
    def __init__(self, sampling_rate_hz: float = 100.0, enable_logging: bool = False):
        self.ac_memory = ACSharedMemory()
        self.logger = SuspensionDataLogger() if enable_logging else None
        self.sampling_rate = sampling_rate_hz
        self.sampling_interval = 1.0 / sampling_rate_hz
        self.running = False
        self.enable_logging = enable_logging
        
        # Buffer circular para datos en tiempo real (últimas 1000 muestras)
        self.buffer_size = 1000
        self.data_buffer = []
        self.buffer_index = 0
        
        # Configurar manejo de señales para cierre limpio
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print(f"🚀 Extractor inicializado:")
        print(f"   Frecuencia: {sampling_rate_hz} Hz ({self.sampling_interval*1000:.1f}ms)")
        print(f"   Logging: {'Habilitado' if enable_logging else 'Deshabilitado (Modo Rendimiento)'}")
        print(f"   Buffer: {self.buffer_size} muestras")
    
    def signal_handler(self, signum, frame):
        """Maneja la señal de interrupción para cierre limpio"""
        print("\n🛑 Señal de interrupción recibida. Cerrando...")
        self.stop()
    
    def test_system(self):
        """Prueba el sistema sin conectar a AC"""
        print("🧪 Ejecutando prueba del sistema...")
        
        if self.enable_logging:
            # Probar logger solo si está habilitado
            test_file = self.logger.create_test_file()
            if test_file:
                print("✅ Sistema de logging funcionando correctamente")
            else:
                print("❌ Error en sistema de logging")
                return False
        else:
            print("✅ Modo sin logging - Sistema listo")
        
        return True
    
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
    
    def add_to_buffer(self, data):
        """Agrega datos al buffer circular (optimizado para rendimiento)"""
        if len(self.data_buffer) < self.buffer_size:
            self.data_buffer.append(data)
        else:
            # Sobrescribir datos antiguos (buffer circular)
            self.data_buffer[self.buffer_index] = data
            self.buffer_index = (self.buffer_index + 1) % self.buffer_size
    
    def get_latest_data(self, count=10):
        """Obtiene las últimas N muestras del buffer"""
        if not self.data_buffer:
            return []
        
        if len(self.data_buffer) < self.buffer_size:
            # Buffer no lleno aún
            return self.data_buffer[-count:] if len(self.data_buffer) >= count else self.data_buffer
        else:
            # Buffer circular lleno
            latest_data = []
            for i in range(count):
                idx = (self.buffer_index - 1 - i) % self.buffer_size
                if idx >= 0:
                    latest_data.insert(0, self.data_buffer[idx])
            return latest_data
    
    def start_extraction(self):
        """Inicia la extracción de datos optimizada"""
        if not self.connect_to_ac():
            return False
        
        print(f"🚀 Iniciando extracción OPTIMIZADA a {self.sampling_rate} Hz")
        print("📊 Presiona Ctrl+C para detener")
        
        # Iniciar sesión de logging solo si está habilitado
        session_file = None
        if self.enable_logging:
            session_file = self.logger.start_session()
        
        self.running = True
        sample_count = 0
        last_packet_id = 0
        start_time = time.time()
        
        # Variables para estadísticas de rendimiento
        last_stats_time = start_time
        last_stats_count = 0
        
        try:
            while self.running:
                loop_start = time.time()
                
                # Leer datos de suspensión (operación más crítica)
                suspension_data = self.ac_memory.read_suspension_data()
                
                if suspension_data:
                    # Verificar que los datos sean nuevos
                    current_packet_id = suspension_data.get('packet_id', 0)
                    
                    if current_packet_id != last_packet_id and current_packet_id > 0:
                        # Agregar al buffer circular (muy rápido)
                        self.add_to_buffer(suspension_data)
                        
                        # Logging opcional (solo si está habilitado)
                        if self.enable_logging:
                            self.logger.log_data(suspension_data)
                        
                        sample_count += 1
                        last_packet_id = current_packet_id
                        
                        # Mostrar estadísticas cada segundo (no cada 50 muestras)
                        current_time = time.time()
                        if current_time - last_stats_time >= 1.0:
                            samples_per_sec = sample_count - last_stats_count
                            elapsed = current_time - start_time
                            
                            print(f"📈 Rendimiento: {samples_per_sec} Hz | Total: {sample_count} | Tiempo: {elapsed:.1f}s")
                            
                            # Mostrar datos actuales (solo cada segundo para no saturar)
                            if suspension_data:
                                susp = suspension_data
                                print(f"   FL: {susp['front_left']:.4f} | FR: {susp['front_right']:.4f}")
                                print(f"   RL: {susp['rear_left']:.4f} | RR: {susp['rear_right']:.4f}")
                                print(f"   Velocidad: {susp['speed_kmh']:.1f} km/h")
                            
                            last_stats_time = current_time
                            last_stats_count = sample_count
                else:
                    print("⚠️ No se pudieron leer datos de AC")
                
                # Timing preciso para mantener frecuencia
                loop_time = time.time() - loop_start
                sleep_time = max(0, self.sampling_interval - loop_time)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                elif loop_time > self.sampling_interval * 1.5:
                    # Advertir si el bucle es demasiado lento
                    print(f"⚠️ Bucle lento: {loop_time*1000:.1f}ms (objetivo: {self.sampling_interval*1000:.1f}ms)")
                
        except KeyboardInterrupt:
            print("\n🛑 Interrupción por teclado")
        except Exception as e:
            print(f"\n❌ Error durante extracción: {e}")
        
        finally:
            self.stop()
            
            # Estadísticas finales
            total_time = time.time() - start_time
            avg_frequency = sample_count / total_time if total_time > 0 else 0
            
            print(f"📊 Estadísticas finales:")
            print(f"   Total muestras: {sample_count}")
            print(f"   Tiempo total: {total_time:.1f} segundos")
            print(f"   Frecuencia promedio: {avg_frequency:.1f} Hz")
            print(f"   Buffer final: {len(self.data_buffer)} muestras")
    
    def stop(self):
        """Detiene la extracción y guarda datos"""
        self.running = False
        
        # Guardar sesión solo si logging está habilitado
        if self.enable_logging and self.logger and self.logger.session_data:
            self.logger.save_session()
            
            # Mostrar estadísticas de logging
            stats = self.logger.get_session_stats()
            if stats:
                print(f"📈 Estadísticas de logging:")
                print(f"   Muestras guardadas: {stats['total_samples']}")
                print(f"   Duración: {stats['duration']:.1f} segundos")
                print(f"   Archivo: {stats['file_path']}")
        
        # Desconectar de AC
        self.ac_memory.disconnect()
        print("✅ Sistema detenido correctamente")


def main():
    """Función principal con argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description='Extractor de datos de suspensión de Assetto Corsa')
    parser.add_argument('--frequency', '-f', type=float, default=100.0,
                       help='Frecuencia de muestreo en Hz (default: 100)')
    parser.add_argument('--enable-logging', '-l', action='store_true',
                       help='Habilitar logging a archivo JSON (reduce rendimiento)')
    parser.add_argument('--test', '-t', action='store_true',
                       help='Solo probar el sistema sin extraer datos')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🏎️  EXTRACTOR DE DATOS DE SUSPENSIÓN - ASSETTO CORSA v2.0")
    print("=" * 70)
    print()
    
    # Validar frecuencia
    if args.frequency < 1 or args.frequency > 1000:
        print("❌ Frecuencia debe estar entre 1 y 1000 Hz")
        return
    
    # Crear extractor con configuración optimizada
    extractor = SuspensionDataExtractor(
        sampling_rate_hz=args.frequency,
        enable_logging=args.enable_logging
    )
    
    # Probar sistema
    if not extractor.test_system():
        print("❌ Fallo en prueba del sistema")
        return
    
    # Si solo es test, terminar aquí
    if args.test:
        print("✅ Test completado exitosamente")
        return
    
    print()
    print("🎯 INSTRUCCIONES:")
    print("1. Asegúrate de que Assetto Corsa esté ejecutándose")
    print("2. Inicia una sesión de carrera (Practice, Race, etc.)")
    print("3. El sistema comenzará a capturar datos automáticamente")
    print("4. Presiona Ctrl+C para detener")
    print()
    
    if args.enable_logging:
        print("📝 LOGGING HABILITADO - Los datos se guardarán en archivo JSON")
        print("⚠️  Esto puede reducir el rendimiento en frecuencias altas")
    else:
        print("🚀 MODO ALTO RENDIMIENTO - Sin logging a archivo")
        print("💡 Usa --enable-logging si necesitas guardar los datos")
    
    print()
    input("Presiona Enter cuando AC esté listo...")
    
    # Iniciar extracción
    extractor.start_extraction()


if __name__ == "__main__":
    main()