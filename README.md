# Dashboard Becas UPCH

Dashboard interactivo para gestión y análisis de becarios UPCH, construido con Streamlit + Supabase.

## Estructura del proyecto

```
dashboard_becas/
├── app.py              # App principal Streamlit
├── db.py               # Conexión y carga de datos desde Supabase
├── utils.py            # Helpers para exportación (Excel/CSV)
├── requirements.txt    # Dependencias
├── render.yaml         # Configuración de deploy en Render
├── .env                # Variables de entorno (NO subir a git)
└── .gitignore
```

## Configuración local

1. **Clonar el repositorio e instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Crear el archivo `.env`** con tus credenciales de Supabase:
```
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key
```

3. **Ejecutar localmente:**
```bash
streamlit run app.py
```

## Deploy en Render

1. Subir el proyecto a GitHub (sin el `.env`)
2. Crear un nuevo **Web Service** en [render.com](https://render.com)
3. Conectar el repositorio
4. En **Environment Variables** agregar:
   - `SUPABASE_URL` → URL de tu proyecto Supabase
   - `SUPABASE_KEY` → Anon key de Supabase
5. Render usará el `render.yaml` automáticamente

## Tablas en Supabase

| Tabla | Descripción |
|-------|-------------|
| `BECARIO` | Datos principales de becarios por semestre |
| `MATRICULA` | Información académica y promedios |
| `PERDIDAS DE BECA` | Casos de pérdida de beca |
| `EGRESADOS` | Becarios que completaron sus estudios |
| `ORDEN DE MERITO` | Rankings académicos históricos |

## Funcionalidades

- 📊 Resumen general con KPIs y gráficos por semestre
- 👤 Tabla de becarios con filtros y búsqueda por nombre/DNI
- 📚 Análisis de matrícula y promedios académicos
- ⚠️ Seguimiento de pérdidas de beca
- 🏁 Estadísticas de egresados
- 🏆 Orden de mérito con distribución de notas
- ⬇️ Exportar cualquier vista a Excel o CSV
