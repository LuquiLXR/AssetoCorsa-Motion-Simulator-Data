# 🏎️ Extractor de Datos de Suspensión - Assetto Corsa

Sistema para extraer datos de suspensión de las 4 ruedas de Assetto Corsa en tiempo real y guardarlos en formato JSON para análisis posterior.

## 📋 Características

- ✅ Extracción de datos brutos de suspensión (4 ruedas)
- ✅ Conexión directa via shared memory de AC
- ✅ Guardado en formato JSON estructurado
- ✅ Frecuencia de muestreo configurable
- ✅ Manejo seguro de interrupciones
- ✅ Validación automática del sistema

## 🚀 Inicio Rápido

### Prerrequisitos
- Python 3.7 o superior
- Assetto Corsa instalado y funcionando
- Windows (requerido para shared memory de AC)

### Instalación
1. Clona o descarga este proyecto
2. No se requieren dependencias externas (usa librerías estándar de Python)

### Uso Básico

1. **Ejecuta Assetto Corsa**
2. **Inicia una sesión** (Practice, Race, Hotlap, etc.)
3. **Ejecuta el extractor:**
   ```bash
   python main.py
   ```
4. **Presiona Ctrl+C** para detener y guardar los datos

## 📁 Estructura del Proyecto

```
Data-AC/
├── main.py                 # Script principal
├── ac_shared_memory.py     # Conexión con AC shared memory
├── data_logger.py          # Sistema de logging JSON
├── requirements.txt        # Dependencias
├── README.md              # Este archivo
└── data/                  # Carpeta de salida (se crea automáticamente)
    ├── suspension_data_YYYYMMDD_HHMMSS.json
    └── test_output.json
```

## 📊 Formato de Datos

Los datos se guardan en JSON con la siguiente estructura:

```json
{
  "session_metadata": {
    "start_time": "2024-01-15T10:30:00.000",
    "end_time": "2024-01-15T10:35:00.000",
    "total_samples": 3000,
    "duration_seconds": 300.0,
    "file_version": "1.0"
  },
  "data": [
    {
      "timestamp": 1642248600.123,
      "readable_time": "2024-01-15T10:30:00.123",
      "suspension": {
        "front_left": 0.045,
        "front_right": 0.043,
        "rear_left": 0.038,
        "rear_right": 0.040
      },
      "context": {
        "speed_kmh": 120.5,
        "packet_id": 12345
      }
    }
  ]
}
```

### Descripción de Campos

- **timestamp**: Tiempo Unix en segundos
- **readable_time**: Tiempo en formato ISO legible
- **suspension**: Valores de recorrido de suspensión por rueda
  - **front_left/right**: Suspensión delantera izquierda/derecha
  - **rear_left/right**: Suspensión trasera izquierda/derecha
- **context**: Datos adicionales para contexto
  - **speed_kmh**: Velocidad del vehículo
  - **packet_id**: ID del paquete de datos de AC

## ⚙️ Configuración

### Frecuencia de Muestreo
Puedes modificar la frecuencia en `main.py`:

```python
extractor = SuspensionDataExtractor(sampling_rate_hz=10.0)  # 10 Hz por defecto
```

### Directorio de Salida
Puedes cambiar el directorio en `main.py`:

```python
self.logger = SuspensionDataLogger(output_dir="mi_carpeta")
```

## 🔧 Solución de Problemas

### "No se pudo conectar con Assetto Corsa"
- ✅ Verifica que AC esté ejecutándose
- ✅ Asegúrate de estar en Windows
- ✅ Inicia una sesión de carrera en AC

### "Conectado pero AC no está enviando datos"
- ✅ Inicia una sesión activa (Practice, Race, etc.)
- ✅ No funciona en menús principales
- ✅ Verifica que el auto esté en pista

### "Error leyendo datos de suspensión"
- ✅ Reinicia AC y vuelve a intentar
- ✅ Verifica que no haya otros programas usando shared memory de AC
- ✅ Ejecuta como administrador si es necesario

## 📈 Análisis de Datos

Los archivos JSON generados pueden ser analizados con:

```python
import json
import pandas as pd

# Cargar datos
with open('data/suspension_data_20240115_103000.json', 'r') as f:
    session = json.load(f)

# Convertir a DataFrame para análisis
df = pd.json_normalize(session['data'])
print(df.head())
```

## 🎯 Casos de Uso

- **Desarrollo de setups**: Analizar comportamiento de suspensión
- **Telemetría**: Monitoreo en tiempo real
- **Investigación**: Estudios de dinámica vehicular
- **Simuladores**: Integración con otros sistemas

## 🔄 Próximas Mejoras

- [ ] Soporte para más datos de telemetría
- [ ] Interfaz gráfica en tiempo real
- [ ] Exportación a otros formatos
- [ ] Análisis automático de datos
- [ ] Integración con herramientas de setup

## 📝 Notas Técnicas

- Utiliza shared memory de AC (`acpmf_physics`)
- Frecuencia recomendada: 10-60 Hz
- Archivos se auto-guardan cada 100 muestras
- Compatible con todas las versiones de AC
- No interfiere con el rendimiento del juego

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto. Úsalo libremente para tus proyectos de simulación.

---

**¡Disfruta analizando los datos de tu simulador de carreras!** 🏁