from osgeo import gdal, ogr
import sys

gdal.UseExceptions()

from qgis.core import (
    QgsVectorLayer
)

path_to_png = r"C:\Users\Joseff01\Downloads\Ljimz.png"

rlayer = QgsRasterLayer(path_to_png, "raster_layer")

if not rlayer.isValid():
    print("Layer failed to load!")
    
iface.addRasterLayer(path_to_png, "my_raster_layer")

try:
    src_ds = gdal.Open(r"C:\Users\Joseff01\Downloads\Ljimz.png")
    srcband = src_ds.GetRasterBand(3)
except RuntimeError as e:
    # for example, try GetRasterBand(10)
    print(f'Band ( {band_num} ) not found')
    print(e)
    sys.exit(1)

if src_ds is None:
    print(f'Unable to open {src_filename}')
    sys.exit(1)

dst_layername = "POLYGONIZED_STUFF"
drv = ogr.GetDriverByName("ESRI Shapefile")
dst_ds = drv.CreateDataSource(dst_layername + ".shp")
dst_layer = dst_ds.CreateLayer(dst_layername, srs=None)

gdal.Polygonize(srcband, None, dst_layer, -1, [], callback=None)

