# Proyecto Sensor de pH - Dashboard

Dashboard en tiempo real para visualizar las lecturas de pH y temperatura
del sensor conectado al ESP32, con alertas visuales tipo semáforo
(verde / amarillo / rojo) según el estado del agua.

## Arquitectura

```
ESP32 (sensor pH, por USB) --> serial_reader.py --HTTP POST--> backend Flask (SQLite) <--HTTP GET-- dashboard Streamlit
```

No se necesita WiFi ni configurar ninguna IP: todo funciona a través del
mismo cable USB que ya se usa para alimentar y monitorear el ESP32.

## Estructura de carpetas

```
proyecto_ph_sensor/
├── README.md
├── esp32/
│   └── esp32_ph_sensor.ino      # código del ESP32 (lectura pH + temperatura)
├── backend/
│   ├── app.py                   # servidor Flask, guarda lecturas en SQLite
│   ├── serial_reader.py         # lee el puerto USB y reenvía al backend
│   ├── simulate_data.py         # genera datos falsos (para probar sin el ESP32)
│   └── .gitignore               # ignora lecturas.db (se genera localmente)
└── dashboard/
    └── streamlit_app.py         # dashboard con gráficos y semáforo
```

Las dependencias de Python (`flask`, `pyserial`, `requests`, `pandas`,
`streamlit`) están declaradas en el `requirements.txt` de la raíz del
repositorio, junto a las de los otros proyectos del grupo.

## Cómo correrlo

Se necesitan 3 terminales abiertas al mismo tiempo.

### Paso 0: instalar dependencias (una sola vez)
Desde la raíz del repositorio (`proyectos_grupo_investigacion`):
```powershell
pip install -r requirements.txt
```

### Terminal 1: backend
```powershell
cd proyecto_ph_sensor/backend
python app.py
```
Queda escuchando en `http://localhost:5000`.

### Terminal 2: origen de los datos

**Opción A - con el ESP32 real conectado por USB:**

Primero sube `esp32/esp32_ph_sensor.ino` al ESP32 desde el Arduino IDE
(no requiere ningún cambio). Luego identifica el puerto:
```powershell
cd proyecto_ph_sensor/backend
python serial_reader.py --listar
```
Esto muestra algo como `COM3`. Con el Monitor Serial del Arduino IDE
**cerrado** (no pueden usar el puerto al mismo tiempo), corre:
```powershell
python serial_reader.py --puerto COM3
```

**Opción B - sin el ESP32 (para probar el dashboard con datos simulados):**
```powershell
cd proyecto_ph_sensor/backend
python simulate_data.py
```

### Terminal 3: dashboard
```powershell
cd proyecto_ph_sensor/dashboard
streamlit run streamlit_app.py
```
Se abre solo en el navegador, normalmente en `http://localhost:8501`.

## Qué se ve en el dashboard

- **pH actual** y **temperatura actual** en números grandes
- **Semáforo de color**:
  - 🟢 Verde: agua segura (pH 6.5 - 8.5)
  - 🟡 Amarillo: agua marginal (pH 5.5 - 6.5 o 8.5 - 9.5)
  - 🔴 Rojo: agua contaminada (fuera de esos rangos)
- **Gráficos en tiempo real** de pH y temperatura, que se actualizan cada 2 segundos

### Demo sugerida
Con el sensor en un vaso de agua normal (semáforo verde), agregar una
pizca de sal, tierra o unas gotas de limón/vinagre y observar cómo el
gráfico reacciona casi al instante y el semáforo cambia de color.

## Ajustar los rangos de pH
En `dashboard/streamlit_app.py`, al inicio del archivo:
```python
PH_MIN_SEGURO = 6.5
PH_MAX_SEGURO = 8.5
PH_MIN_MARGINAL = 5.5
PH_MAX_MARGINAL = 9.5
```
Cambiar estos valores si el profesor pide otros criterios.

## Problemas comunes
- **"Esperando datos del ESP32..." en el dashboard**: revisa que
  `serial_reader.py` (o `simulate_data.py`) esté corriendo y mostrando
  líneas en pantalla. Si no aparece nada, confirma que el puerto
  (`COM3`, etc.) sea el correcto con `--listar`.
- **Error de puerto ocupado**: el Monitor Serial del Arduino IDE y
  `serial_reader.py` no pueden usar el puerto al mismo tiempo. Cierra el
  Monitor Serial del IDE antes de correr `serial_reader.py`.
- **El dashboard no carga datos**: verifica que `app.py` (backend) esté
  corriendo antes de abrir Streamlit.
- **`lecturas.db` no debe subirse a git**: ya está en el `.gitignore` de
  `backend/`. Si aparece como "untracked" o "modified" en `git status`,
  es normal, se puede ignorar.