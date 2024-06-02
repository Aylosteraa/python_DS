import osr
import ogr
import gdal
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import rasterio
import glob
from rasterio.plot import show
from rasterio.mask import mask
from shapely.geometry import mapping
import geopandas as gpd
import math

def read_band_image(band, path):
    a = path + '*B' + band + '*.jp2'
    img = gdal.Open(glob.glob(a)[0])
    data = np.array(img.GetRasterBand(1).ReadAsArray())
    spatialRef = img.GetProjection()
    geoTransform = img.GetGeoTransform()
    targetprj = osr.SpatialReference(wkt=img.GetProjection())
    return data, spatialRef, geoTransform, targetprj

def nbr(band1, band2):
    return (band1 - band2) / (band1 + band2)

def dnbr(nbr1, nbr2):
    return nbr1 - nbr2

def reproject_shp_gdal(infile, outfile, targetprj):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(infile, 1)
    layer = dataSource.GetLayer()
    sourceprj = layer.GetSpatialRef()
    transform = osr.CoordinateTransformation(sourceprj, targetprj)

    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    outDataSource = outDriver.CreateDataSource(outfile)
    outlayer = outDataSource.CreateLayer('', targetprj, ogr.wkbPolygon)
    outlayer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))

    i = 0
    for feature in layer:
        transformed = feature.GetGeometryRef()
        transformed.Transform(transform)

        geom = ogr.CreateGeometryFromWkb(transformed.ExportToWkb())
        defn = outlayer.GetLayerDefn()
        feat = ogr.Feature(defn)
        feat.SetField('id', i)
        feat.SetGeometry(geom)
        outlayer.CreateFeature(feat)
        i += 1
        feat = None

def array2raster(array, geoTransform, projection, filename):
    pixels_x = array.shape[1]
    pixels_y = array.shape[0]

    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(
        filename,
        pixels_x,
        pixels_y,
        1,
        gdal.GDT_Float64,
    )
    dataset.SetGeoTransform(geoTransform)
    dataset.SetProjection(projection)
    dataset.GetRasterBand(1).WriteArray(array)
    dataset.FlushCache()
    return dataset, dataset.GetRasterBand(1)

def clip_raster(filename, shp):
    inraster = rasterio.open(filename)

    extent_geojson = mapping(shp['geometry'][0])
    clipped, crop_affine = mask(inraster,
                                shapes=[extent_geojson],
                                nodata=np.nan,
                                crop=True)
    clipped_meta = inraster.meta.copy()
    clipped_meta.update({
        "driver": "GTiff",
        "height": clipped.shape[1],
        "width": clipped.shape[2],
        "transform": crop_affine
    })
    cr_ext = rasterio.transform.array_bounds(clipped_meta['height'],
                                             clipped_meta['width'],
                                             clipped_meta['transform'])

    gt = crop_affine.to_gdal()

    return clipped, clipped_meta, cr_ext, gt

def reclassify(array):
    reclass = np.zeros((array.shape[0], array.shape[1]))
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            if math.isnan(array[i, j]):
                reclass[i, j] = np.nan
            elif array[i, j] < 0.1:
                reclass[i, j] = 1
            elif array[i, j] < 0.27:
                reclass[i, j] = 2
            elif array[i, j] < 0.44:
                reclass[i, j] = 3
            elif array[i, j] < 0.66:
                reclass[i, j] = 4
            else:
                reclass[i, j] = 5
    return reclass

# Встановлення шляху до даних
path_prefire = "F:/Burn_Severity/S2A_MSIL2A_20161220T143742_N0204_R096_T18HYF_20161220T145131.SAFE/GRANULE/L2A_T18HYF_A007815_20161220T145131/IMG_DATA/R20m/"
path_postfire = "F:/Burn_Severity/S2A_MSIL2A_20170218T143751_N0204_R096_T18HYF_20170218T145150.SAFE/GRANULE/L2A_T18HYF_A008673_20170218T145150/IMG_DATA/R20m/"
infile_shp = "F:/Burn_Severity/Empedrado_adm_boundary/Empedrado.shp"
outfile_shp = "F:/Burn_Severity/Empedrado_adm_boundary/projected.shp"
filename = "F:/Burn_Severity/dNBR.tiff"
filename2 = "F:/Burn_Severity/dNBR_clipped.tiff"
fname = "F:/Burn_Severity/map.png"

band1 = '8A'
band2 = '12'

# Читання передпожежних зображень
pre_fire_b8a, crs, geoTransform, targetprj = read_band_image(band1, path_prefire)
pre_fire_b12, crs, geoTransform, targetprj = read_band_image(band2, path_prefire)

# Розрахунок передпожежного NBR
pre_fire_nbr = nbr(pre_fire_b8a.astype(int), pre_fire_b12.astype(int))

# Читання післяпожежних зображень
post_fire_b8a, crs, geoTransform, targetprj = read_band_image(band1, path_postfire)
post_fire_b12, crs, geoTransform, targetprj = read_band_image(band2, path_postfire)

# Розрахунок післяпожежного NBR
post_fire_nbr = nbr(post_fire_b8a.astype(int), post_fire_b12.astype(int))

# Розрахунок dNBR
DNBR = dnbr(pre_fire_nbr, post_fire_nbr)

# Перепроєкція shapefile
reproject_shp_gdal(infile_shp, outfile_shp, targetprj)

# Читання перепроєктованого shapefile
fire_boundary = gpd.read_file(outfile_shp)

# Створення dNBR растрового зображення
dnbr_tif, dnbr_tifBand = array2raster(DNBR, geoTransform, crs, filename)

# Обрізка растрового зображення на основі shapefile
clipped_dnbr, clipped_dnbr_meta, cr_extent, gt = clip_raster(filename, fire_boundary)
clipped_ds, clipped_ds_rasterband = array2raster(clipped_dnbr[0], gt, crs, filename2)

# Візуалізація результатів
cmap = matplotlib.colors.ListedColormap(['green', 'yellow', 'orange', 'red', 'purple'])
cmap.set_over('purple')
cmap.set_under('white')
bounds = [-0.5, 0.1, 0.27, 0.44, 0.66, 1.3]
norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'xticks': [], 'yticks': []})
cax = ax.imshow(clipped_ds_rasterband.ReadAsArray(), cmap=cmap, norm=norm)
plt.title('Burn Severity Map')
cbar = fig.colorbar(cax, ax=ax, fraction=0.035, pad=0.04, ticks=[-0.2, 0.18, 0.35, 0.53, 1])
cbar.ax.set_yticklabels(['Unburned', 'Low Severity', 'Moderate-low Severity', 'Moderate-high Severity', 'High Severity'])
plt.show()
plt.savefig(fname, bbox_inches="tight")

# Розрахунок площі обпаленої території
reclass = reclassify(clipped_ds_rasterband.ReadAsArray())
k = ['Unburned hectares', 'Low severity hectares', 'Moderate-low severity hectares', 'Moderate-high severity hectares', 'High severity']
for i in range(1, 6):
    x = reclass[reclass == i]
    l = x.size * 0.04
    print(f"{k[i-1]}: {l:.2f}")
