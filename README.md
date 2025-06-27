# Herramienta de Georreferenciación de Plantas de Café

Este proyecto permite transformar las coordenadas detectadas de plantas de café en imágenes georreferenciadas a capas vectoriales compatibles con QGIS. La herramienta facilita la integración de los datos generados por herramientas de detección (como la de Shakime) en entornos de análisis geoespacial, permitiendo una visualización clara y precisa del cultivo.

## Características

- Conversión de coordenadas en píxeles a coordenadas geográficas utilizando metadatos de imágenes `.tif`.
- Exportación automática de archivos `.shp` para cada imagen procesada.
- Interfaz interactiva por consola para usuarios sin experiencia técnica.
- Modo avanzado con argumentos por línea de comandos para automatización.

## Estructura esperada

- Carpeta con imágenes `.tif` georreferenciadas.
- Carpeta con archivos `.csv` que contengan las coordenadas de detección (columnas: `left`, `top`, `right`, `bottom`; formato default para la herramienta de detección de Shakime Richards).

## Requisitos

- Python 3.8 o superior
- Bibliotecas necesarias:
  - `pandas`
  - `rasterio`
  - `geopandas`
  - `shapely`
  - `questionary`

## Uso

### Modo interactivo

```bash
python main.py
```
El sistema guiará al usuario paso a paso con un menú amigable.

### Modo por línea de comandos

```bash
python main.py --images "ruta/a/imagenes" --csvs "ruta/a/csvs" --output "ruta/a/salida"
```

##Ejemplo de salida

Cada imagen procesada genera un conjunto de archivos .shp, .dbf, .shx, .prj, .cpg en la carpeta indicada, listos para cargar en QGIS.

**Proyecto de diseño desarrollado como parte del curso CE-1114 del Instituto Tecnológico de Costa Rica**
