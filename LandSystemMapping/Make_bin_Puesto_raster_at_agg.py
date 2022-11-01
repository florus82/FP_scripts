##############################################################
###### rasterizes a puesto point layer to the resolution of
###### an input raster (img)


from FloppyToolZL.Funcis import *

puesto_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/Objective_3/puestos/All_puestos_year_no0_fixedMPR_KK_LL.shp'
puesto = ogr.Open(puesto_p)
puestos = puesto.GetLayer()

img  = gdal.Open('M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/01_Aggregations/TreeCover/3000/TC_aggregeated_to_3000.tif')
gtiff_driver = gdal.GetDriverByName('GTiff')
out_ds = gtiff_driver.Create('M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/99_Auxiliaries/Puesto_raster/puestos_agg/puesto_bin_3000.tif', img.RasterXSize, img.RasterYSize, 1, gdal.GDT_Int16)
out_ds.SetGeoTransform(img.GetGeoTransform())
out_ds.SetProjection(img.GetProjection())
Band = img.GetRasterBand(1)
Band.SetNoDataValue(0)
gdal.RasterizeLayer(out_ds, [1], puestos, burn_values=[1])
del out_ds