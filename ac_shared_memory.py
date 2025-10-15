"""
Módulo para acceder a los datos de shared memory de Assetto Corsa
Extrae específicamente los datos de suspensión de las 4 ruedas
"""

import mmap
import ctypes
from ctypes import c_int32, c_float, c_wchar
import struct
import time


class SPageFilePhysics(ctypes.Structure):
    """Estructura de datos de física de Assetto Corsa"""
    _pack_ = 4
    _fields_ = [
        ('packetId', c_int32),
        ('gas', c_float),
        ('brake', c_float),
        ('fuel', c_float),
        ('gear', c_int32),
        ('rpms', c_int32),
        ('steerAngle', c_float),
        ('speedKmh', c_float),
        ('velocity', c_float * 3),
        ('accG', c_float * 3),
        ('wheelSlip', c_float * 4),
        ('wheelLoad', c_float * 4),
        ('wheelsPressure', c_float * 4),
        ('wheelAngularSpeed', c_float * 4),
        ('tyreWear', c_float * 4),
        ('tyreDirtyLevel', c_float * 4),
        ('tyreCoreTemperature', c_float * 4),
        ('camberRAD', c_float * 4),
        ('suspensionTravel', c_float * 4),  # Este es el dato que necesitamos
        ('drs', c_float),
        ('tc', c_float),
        ('heading', c_float),
        ('pitch', c_float),
        ('roll', c_float),
        ('cgHeight', c_float),
        ('carDamage', c_float * 5),
        ('numberOfTyresOut', c_int32),
        ('pitLimiterOn', c_int32),
        ('abs', c_float),
        ('kersCharge', c_float),
        ('kersInput', c_float),
        ('autoShifterOn', c_int32),
        ('rideHeight', c_float * 2),
        ('turboBoost', c_float),
        ('ballast', c_float),
        ('airDensity', c_float),
        ('airTemp', c_float),
        ('roadTemp', c_float),
        ('localAngularVel', c_float * 3),
        ('finalFF', c_float),
        ('performanceMeter', c_float),
        ('engineBrake', c_int32),
        ('ersRecoveryLevel', c_int32),
        ('ersPowerLevel', c_int32),
        ('ersHeatCharging', c_int32),
        ('ersIsCharging', c_int32),
        ('kersCurrentKJ', c_float),
        ('drsAvailable', c_int32),
        ('drsEnabled', c_int32),
        ('brakeTemp', c_float * 4),
        ('clutch', c_float),
    ]


class ACSharedMemory:
    """Clase para manejar la conexión con shared memory de Assetto Corsa"""
    
    def __init__(self):
        self.physics_mmap = None
        self.is_connected = False
        
    def connect(self):
        """Conecta con la shared memory de Assetto Corsa"""
        try:
            # Intentar abrir el mapa de memoria de física
            self.physics_mmap = mmap.mmap(-1, ctypes.sizeof(SPageFilePhysics), "acpmf_physics")
            self.is_connected = True
            print("✅ Conectado exitosamente a Assetto Corsa shared memory")
            return True
        except Exception as e:
            print(f"❌ Error conectando a AC shared memory: {e}")
            print("💡 Asegúrate de que Assetto Corsa esté ejecutándose")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Desconecta de la shared memory"""
        if self.physics_mmap:
            self.physics_mmap.close()
            self.physics_mmap = None
        self.is_connected = False
        print("🔌 Desconectado de Assetto Corsa")
    
    def read_suspension_data(self):
        """Lee los datos de suspensión de las 4 ruedas"""
        if not self.is_connected or not self.physics_mmap:
            return None
        
        try:
            # Leer datos de la memoria compartida
            self.physics_mmap.seek(0)
            data = self.physics_mmap.read(ctypes.sizeof(SPageFilePhysics))
            physics = SPageFilePhysics.from_buffer_copy(data)
            
            # Extraer datos de suspensión (valores brutos)
            suspension_data = {
                'timestamp': time.time(),
                'front_left': float(physics.suspensionTravel[0]),
                'front_right': float(physics.suspensionTravel[1]),
                'rear_left': float(physics.suspensionTravel[2]),
                'rear_right': float(physics.suspensionTravel[3]),
                'speed_kmh': float(physics.speedKmh),  # Para contexto
                'packet_id': int(physics.packetId)  # Para verificar datos válidos
            }
            
            return suspension_data
            
        except Exception as e:
            print(f"❌ Error leyendo datos de suspensión: {e}")
            return None
    
    def is_ac_running(self):
        """Verifica si Assetto Corsa está ejecutándose y enviando datos"""
        data = self.read_suspension_data()
        if data is None:
            return False
        
        # Verificar que el packet_id sea válido (mayor que 0)
        return data.get('packet_id', 0) > 0