# Zip Analyzer

Una herramienta escrita en Python para analizar archivos ZIP, generar informes de contenido, metadatos y ejecutar generación de reportes basados en configuración.

---

## Funcionalidad

- Procesa archivos ZIP para extraer la estructura de carpetas y archivos.  
- Extrae metadatos como fecha, tamaño, rutas internas.  
- Aplica generación de reportes mediante un módulo `generator.py` configurado con `config.json`.  
- Permite ejecutar a través de `runner.py` la lógica completa del análisis.  
- Mantiene licencia GPL v3 (o posterior) según el archivo de cabecera del repositorio.

---

## Instalación

1. Clona el repositorio: `git clone https://github.com/ja-rg/zip-analyzer.git; cd zip-analyzer`

2. Asegúrate de tener Python (por ejemplo 3.8+) instalado.
3. Instala requisitos (si los hay — revisa `requirements.txt` o incluye dependencias en `setup.py`).

   ```bash
   pip install -r requirements.txt
   ```

---

## Uso

### Configuración

Edita `config.json` según los parámetros que deseas aplicar para los análisis.
Por ejemplo: definir tipos de reporte, filtros de archivo, rutas a ignorar.

### Ejecución

```bash
python runner.py ruta/al/archivo.zip
```

Esto generará un reporte basado en los datos del ZIP, la configuración y la lógica del generador.

### Ejemplo de salida

```json
{
  "file": "ejemplo.zip",
  "total_entries": 125,
  "folders": 12,
  "files": 113,
  "biggest_file": {
    "name": "datos.bin",
    "size": 45_000_000
  },
  "metadata": {
    "creator": "usuario",
    "timestamp": "2025-11-07T14:22:00Z"
  }
}
```

---

## Arquitectura del proyecto

* `runner.py` → punto de entrada, toma el archivo ZIP y lanza el análisis.
* `generator.py` → módulo que genera los reportes basados en la configuración.
* `config.json` → archivo de configuración, define comportamiento, filtros, formatos.
* `.gitignore` → contiene exclusiones típicas (archivos temporales, entornos virtuales).
* Licencia: Está bajo la GNU General Public License v3.0 (o posterior) como se indica en el repositorio.

---

## Contribuir

¡Se agradecen contribuciones!
Para colaborar:

1. Haz un fork del repositorio.
2. Crea una rama con nombre descriptivo: `feature/nueva-funcionalidad` o `bugfix/issue-xyz`.
3. Haz tus cambios y realiza *commits* claros.
4. Envía un Pull Request explicando el objetivo, la implementación y pruebas realizadas.

---

## Licencia

Este proyecto se distribuye bajo los términos de la GNU General Public License versión 3 (o, a elección del titular, cualquier versión posterior). Consulta el archivo LICENSE para más detalles.

---

## Autor

Desarrollado por **[Alejandro Rosales](https://github.com/ja-rg)**.
Apasionado por análisis de archivos, automatización y seguridad informática.

---

## ¿Te resultó útil?

Si te ayudó este proyecto, considera darle ⭐ al repositorio para apoyar la visibilidad.
Gracias por usar Zip Analyzer.

# ⚠️ Descargo de responsabilidad

Este software se proporciona “tal cual”, sin garantías de ningún tipo, expresas o implícitas.
El autor no se hace responsable de daños, pérdidas de información, fallos en sistemas, usos indebidos, ni de cualquier consecuencia directa o indirecta derivada del uso de este código o de los reportes generados.
El uso de Zip Analyzer implica la aceptación total de esta condición.
