from FloppyToolZL.Funcis import *

Chac     = ogr.Open('K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/Chaco_ecoregion/Chaco_84.shp')
#Chac     = ogr.Open('K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/TNC/TNC_84.shp')
Chac_lyr = Chac.GetLayer()
gtiff_driver = gdal.GetDriverByName('GTiff')

tcs = getFilelist('M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/LandCover/Run12/output_LandCover', '.tif')

for tc in tcs:
    img  = gdal.Open(tc)

    out_ds = gtiff_driver.Create('M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/99_Auxiliaries/mask_in_tiles/' + '_'.join(tc.split('/')[-1].split('_')[0:2]) + '_mask.tif', img.RasterXSize, img.RasterYSize, 1, gdal.GDT_Int16)
    out_ds.SetGeoTransform(img.GetGeoTransform())
    out_ds.SetProjection(img.GetProjection())
    Band = img.GetRasterBand(1)
    Band.SetNoDataValue(0)
    gdal.RasterizeLayer(out_ds, [1], Chac_lyr, burn_values=[1])
    del out_ds

#
# # make mask for different resolutions
# path = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/01_Aggregations/LandCover/stacks_by_class/'
# files = [path + '300/12_20_20_30_18/lc_props_12_20_20_30_18_agg_300_C.tif',
#          path + '1500/12_20_20_30_18/lc_props_12_20_20_30_18_agg_1500_C.tif',
#          path + '3000/12_20_20_30_18/lc_props_12_20_20_30_18_agg_3000_C.tif']
#
# for file in files:
#     img = gdal.Open(file)
#     out_ds = gtiff_driver.Create('M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/99_Auxiliaries/Chaco_Mask_Raster/Chaco_Mask_Agg_' + file.split('/')[-1].split('_')[-2] + '.tif', img.RasterXSize, img.RasterYSize, 1, gdal.GDT_Int16)
#     out_ds.SetGeoTransform(img.GetGeoTransform())
#     out_ds.SetProjection(img.GetProjection())
#     Band = img.GetRasterBand(1)
#     Band.SetNoDataValue(0)
#     gdal.RasterizeLayer(out_ds, [1], Chac_lyr, burn_values=[1])
#     del out_ds