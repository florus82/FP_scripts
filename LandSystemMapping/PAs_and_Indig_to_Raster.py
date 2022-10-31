
from FloppyToolZL.Funcis import *
drvMemR = gdal.GetDriverByName('MEM')
gtiff_driver = gdal.GetDriverByName('GTiff')
OPTIONS = ['ALL_TOUCHED=TRUE']


# Chaco templates
files = getFilelist('M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/99_Auxiliaries/Chaco_Mask_Raster', '.tif')

############################################################################### load layers
############################### wdpa layers
wdpa_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/PAs/WDPA_JUNE_2020_ARG_BOL_PRY.shp'
wdpa_ = ogr.Open(wdpa_p)
wdpa  = wdpa_.GetLayer()
############################### PRY
# pry privada
ppriv_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/PAs/PAR/privadas.shp'
ppriv_ = ogr.Open(ppriv_p)
ppriv  = ppriv_.GetLayer()
# pry publicadas
ppub_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/PAs/PAR/publicas.shp'
ppub_ = ogr.Open(ppub_p)
ppub  = ppub_.GetLayer()
############################### ARG
# arg forest zones
argf_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/PAs/ARG/ForestLaw/FL_ENTIRE_CHACO_LAEA.shp'
argf_  = ogr.Open(argf_p)
argf   = argf_.GetLayer()
# arg nacionales
argn_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/PAs/ARG/ProtectedAreas/AP_Nacionales_poligonos.shp'
argn_  = ogr.Open(argn_p)
argn   = argn_.GetLayer()
# arg provinciales
argp_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/PAs/ARG/ProtectedAreas/AP_Provinciales_poligonos.shp'
argp_  = ogr.Open(argp_p)
argp   = argp_.GetLayer()
############################### BOL
# bol nacionales
boln_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/PAs/BOL/areas_protegidas_nacionales042015.shp'
boln_  = ogr.Open(boln_p)
boln   = boln_.GetLayer()
# bol departamentales
bold_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/PAs/BOL/areas_protegidas_departamentales42015.shp'
bold_  = ogr.Open(bold_p)
bold   = bold_.GetLayer()


############################################################################### rasterize layers

for file in files:
    m = gdal.Open(file)
    mb = m.GetRasterBand(1)
    mask = mb.ReadAsArray()
    # mask[mask == 0] = np.nan

    # rasterize WDPA
    wdpa.ResetReading()
    wdpa.SetAttributeFilter("IUCN_CAT = 'Ia' or IUCN_CAT = 'Ib' or IUCN_CAT = 'II'")
    sub_wdpa = drvMemR.Create('', mask.shape[1], mask.shape[0], 1, gdal.GDT_Int16)
    # sub = gtiff_driver.Create('E:/Florian/MSc_outside_Seafile/RS_Data/MODIS/test.tiff', mask.shape[1], mask.shape[0], 1, gdal.GDT_Int16)
    sub_wdpa.SetGeoTransform(m.GetGeoTransform())
    sub_wdpa.SetProjection(m.GetProjection())
    band = sub_wdpa.GetRasterBand(1)
    #band.SetNoDataValue(0)
    gdal.RasterizeLayer(sub_wdpa, [1], wdpa, burn_values=[1], options=OPTIONS)
    sub_wdpa_arr = sub_wdpa.ReadAsArray()
    sub_wdpa_arr[sub_wdpa_arr != 1] = 0
    wdpa.SetAttributeFilter(None)
    wdpa.ResetReading()

    # rasterize paraguay privadas
    sub_ppriv = drvMemR.Create('', mask.shape[1], mask.shape[0], 1, gdal.GDT_Int16)
    sub_ppriv.SetGeoTransform(m.GetGeoTransform())
    sub_ppriv.SetProjection(m.GetProjection())
    band = sub_ppriv.GetRasterBand(1)
    #band.SetNoDataValue(0)
    gdal.RasterizeLayer(sub_ppriv, [1], ppriv, burn_values=[1], options=OPTIONS)
    sub_ppriv_arr = sub_ppriv.ReadAsArray()
    sub_ppriv_arr[sub_ppriv_arr!=1] = 0

    # rasterize paraguay publicadas
    sub_ppub = drvMemR.Create('', mask.shape[1], mask.shape[0], 1, gdal.GDT_Int16)
    sub_ppub.SetGeoTransform(m.GetGeoTransform())
    sub_ppub.SetProjection(m.GetProjection())
    band = sub_ppub.GetRasterBand(1)
    #band.SetNoDataValue(0)
    gdal.RasterizeLayer(sub_ppub, [1], ppriv, burn_values=[1], options=OPTIONS)
    sub_ppub_arr = sub_ppub.ReadAsArray()
    sub_ppub_arr[sub_ppub_arr!=1] = 0

    # rasterize forest zone 1
    sub_argf = drvMemR.Create('', mask.shape[1], mask.shape[0], 1, gdal.GDT_Int16)
    sub_argf.SetGeoTransform(m.GetGeoTransform())
    sub_argf.SetProjection(m.GetProjection())
    band = sub_argf.GetRasterBand(1)
    #band.SetNoDataValue(0)
    argf.SetAttributeFilter("OT_class = '1'")
    gdal.RasterizeLayer(sub_argf, [1], argf, burn_values=[1], options=OPTIONS)
    sub_argf_arr = sub_argf.ReadAsArray()
    sub_argf_arr[sub_argf_arr!=1] = 0
    argf.SetAttributeFilter(None)
    argf.ResetReading()

    # rasterize argentinia nacionales
    sub_argn  = drvMemR.Create('', mask.shape[1], mask.shape[0], 1, gdal.GDT_Int16)
    sub_argn.SetGeoTransform(m.GetGeoTransform())
    sub_argn.SetProjection(m.GetProjection())
    band = sub_argn.GetRasterBand(1)
    #band.SetNoDataValue(0)
    gdal.RasterizeLayer(sub_argn, [1], argn, burn_values=[1], options=OPTIONS)
    sub_argn_arr = sub_argn.ReadAsArray()
    sub_argn_arr[sub_argn_arr!=1]=0

    # rasterize Bolivia departamentales
    sub_bold = drvMemR.Create('', mask.shape[1], mask.shape[0], 1, gdal.GDT_Int16)
    sub_bold.SetGeoTransform(m.GetGeoTransform())
    sub_bold.SetProjection(m.GetProjection())
    band = sub_bold.GetRasterBand(1)
    #band.SetNoDataValue(0)
    gdal.RasterizeLayer(sub_bold, [1], bold, burn_values=[1], options=OPTIONS)
    sub_bold_arr = sub_bold.ReadAsArray()
    sub_bold_arr[sub_bold_arr!=1] = 0

    # rasterize Bolivia nacionales
    boln.SetAttributeFilter("categoria = 'Parque Nacional y Territorio Indigena' or categoria = 'Parque Nacional'")
    sub_boln = drvMemR.Create('', mask.shape[1], mask.shape[0], 1, gdal.GDT_Int16)
    sub_boln.SetGeoTransform(m.GetGeoTransform())
    sub_boln.SetProjection(m.GetProjection())
    band = sub_boln.GetRasterBand(1)
    #band.SetNoDataValue(0)
    gdal.RasterizeLayer(sub_boln, [1], boln, burn_values=[1], options=OPTIONS)
    sub_boln_arr = sub_boln.ReadAsArray()
    sub_boln_arr[sub_boln_arr!=1] =0
    boln.SetAttributeFilter(None)
    boln.ResetReading()

    strict = sub_wdpa_arr + sub_argf_arr + sub_argn_arr + sub_boln_arr + sub_ppriv_arr + sub_ppub_arr
    strict_masked = strict * mask
    strict_masked[strict_masked > 0] = 1

    dumm2 = gtiff_driver.Create(
        'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/99_Auxiliaries/PA_raster/ProtectedAreas_bin_' + file.split('/')[-1].split('_')[-1].split('.')[0] + '.tif', mask.shape[1],
        mask.shape[0], 1, gdal.GDT_Int16)
    dumm2.SetGeoTransform(m.GetGeoTransform())
    dumm2.SetProjection(m.GetProjection())
    band = dumm2.GetRasterBand(1)
    band.SetNoDataValue(0)
    band.WriteArray(strict_masked)
    del dumm2

################################################################################################# load indigenous territories
# Kristinas layer
i1 = ogr.Open('K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/Objective_3/Indigenous_lands/Ayoreo_BOL_PAR_Kristina/ayoreo_bolivia.shp')
il1 = i1.GetLayer()

i2 = ogr.Open('K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/Objective_3/Indigenous_lands/Ayoreo_BOL_PAR_Kristina/ayoreo_paraguay_bolivia.shp')
il2 = i2.GetLayer()


# Bol
i3 = ogr.Open('K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/Objective_3/Indigenous_lands/BOL/tco_titulado_2012/tco_titulado_2012.shp')
il3 = i3.GetLayer()

# PAR
i4 = ogr.Open('K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/Objective_3/Indigenous_lands/PRY/Comunidades_1/comunidades1.shp')
il4 = i4.GetLayer()

# ARG
i6 = ogr.Open('K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/Objective_3/Indigenous_lands/ARG/Indigenous_settlements_points_konvex_buffer.shp')
il6 = i6.GetLayer()

############################################################################### rasterize layers

for file in files:
    m = gdal.Open(file)
    mb = m.GetRasterBand(1)
    mask = mb.ReadAsArray()

    q1 = drvMemR.Create('', mask.shape[1], mask.shape[0], 1, gdal.GDT_Int16)
    q1.SetGeoTransform(m.GetGeoTransform())
    q1.SetProjection(m.GetProjection())
    band = q1.GetRasterBand(1)
    # band.SetNoDataValue(0)
    gdal.RasterizeLayer(q1, [1], il1, burn_values=[1], options=OPTIONS)
    i1_arr = q1.ReadAsArray()
    i1_arr[i1_arr != 1] = 0

    q2 = drvMemR.Create('', mask.shape[1], mask.shape[0], 1, gdal.GDT_Int16)
    q2.SetGeoTransform(m.GetGeoTransform())
    q2.SetProjection(m.GetProjection())
    band = q2.GetRasterBand(1)
    # band.SetNoDataValue(0)
    gdal.RasterizeLayer(q2, [1], il2, burn_values=[1], options=OPTIONS)
    i2_arr = q2.ReadAsArray()
    i2_arr[i2_arr != 1] = 0

    q3 = drvMemR.Create('', mask.shape[1], mask.shape[0], 1, gdal.GDT_Int16)
    q3.SetGeoTransform(m.GetGeoTransform())
    q3.SetProjection(m.GetProjection())
    band = q3.GetRasterBand(1)
    # band.SetNoDataValue(0)
    gdal.RasterizeLayer(q3, [1], il3, burn_values=[1], options=OPTIONS)
    i3_arr = q3.ReadAsArray()
    i3_arr[i3_arr != 1] = 0

    q4 = drvMemR.Create('', mask.shape[1], mask.shape[0], 1, gdal.GDT_Int16)
    q4.SetGeoTransform(m.GetGeoTransform())
    q4.SetProjection(m.GetProjection())
    band = q4.GetRasterBand(1)
    # band.SetNoDataValue(0)
    gdal.RasterizeLayer(q4, [1], il4, burn_values=[1], options=OPTIONS)
    i4_arr = q4.ReadAsArray()
    i4_arr[i4_arr != 1] = 0

    q6 = drvMemR.Create('', mask.shape[1], mask.shape[0], 1, gdal.GDT_Int16)
    q6.SetGeoTransform(m.GetGeoTransform())
    q6.SetProjection(m.GetProjection())
    band = q6.GetRasterBand(1)
    # band.SetNoDataValue(0)
    gdal.RasterizeLayer(q6, [1], il6, burn_values=[1], options=OPTIONS)
    i6_arr = q6.ReadAsArray()
    i6_arr[i6_arr != 1] = 0

    ind_arr = i1_arr + i2_arr + i3_arr + i4_arr + i6_arr
    ind_arr_masked = ind_arr * mask
    ind_arr_masked[ind_arr_masked > 0] = 1

    dumm2 = gtiff_driver.Create(
        'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/99_Auxiliaries/Indigenous_raster/IndigenousAreas_bin_' +
        file.split('/')[-1].split('_')[-1].split('.')[0] + '.tif', mask.shape[1],
        mask.shape[0], 1, gdal.GDT_Int16)
    dumm2.SetGeoTransform(m.GetGeoTransform())
    dumm2.SetProjection(m.GetProjection())
    band = dumm2.GetRasterBand(1)
    band.SetNoDataValue(0)
    band.WriteArray(ind_arr_masked)
    del dumm2
