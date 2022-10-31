from FloppyToolZL.MasterFuncs import *
drvMemR = gdal.GetDriverByName('MEM')
gtiff_driver = gdal.GetDriverByName('GTiff')
OPTIONS = ['ALL_TOUCHED=TRUE']

# ############################################################################################################################################################## PAs
# ############################### wdpa layers
# wdpa_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/PAs/WDPA_JUNE_2020_ARG_BOL_PRY.shp'
# wdpa_ = ogr.Open(wdpa_p)
# wdpa  = wdpa_.GetLayer()
# ############################### PRY
# # pry privada
# ppriv_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/PAs/PAR/privadas.shp'
# ppriv_ = ogr.Open(ppriv_p)
# ppriv  = ppriv_.GetLayer()
# # pry publicadas
# ppub_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/PAs/PAR/publicas.shp'
# ppub_ = ogr.Open(ppub_p)
# ppub  = ppub_.GetLayer()
# ############################### ARG
# # arg forest zones
# argf_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/PAs/ARG/ForestLaw/FL_ENTIRE_CHACO_LAEA.shp'
# argf_  = ogr.Open(argf_p)
# argf   = argf_.GetLayer()
# # arg nacionales
# argn_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/PAs/ARG/ProtectedAreas/AP_Nacionales_poligonos.shp'
# argn_  = ogr.Open(argn_p)
# argn   = argn_.GetLayer()
# # arg provinciales
# argp_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/PAs/ARG/ProtectedAreas/AP_Provinciales_poligonos.shp'
# argp_  = ogr.Open(argp_p)
# argp   = argp_.GetLayer()
# ############################### BOL
# # bol nacionales
# boln_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/PAs/BOL/areas_protegidas_nacionales042015.shp'
# boln_  = ogr.Open(boln_p)
# boln   = boln_.GetLayer()
# # bol departamentales
# bold_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/PAs/BOL/areas_protegidas_departamentales42015.shp'
# bold_  = ogr.Open(bold_p)
# bold   = bold_.GetLayer()
#

################################################################################################################################################################### Biomass maps
b1 = gdal.Open('G:/LandSystems_20/dump/tempVRT_Run12.vrt')
b2 = b1.GetRasterBand(1)
b3 = b2.ReadAsArray()

m = gdal.Open('G:/LandSystems_20/dump/CHaco_Mask_raster.tif')
mb = m.GetRasterBand(1)
mask = mb.ReadAsArray().astype(np.float)
mask[mask == 0] = np.nan
#
# # ###################################################################################################################################  rasterize
# # rasterize WDPA
# wdpa.ResetReading()
# wdpa.SetAttributeFilter("IUCN_CAT = 'Ia' or IUCN_CAT = 'Ib' or IUCN_CAT = 'II'")
# sub_wdpa = drvMemR.Create('', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# # sub = gtiff_driver.Create('E:/Florian/MSc_outside_Seafile/RS_Data/MODIS/test.tiff', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# sub_wdpa.SetGeoTransform(b1.GetGeoTransform())
# sub_wdpa.SetProjection(b1.GetProjection())
# band = sub_wdpa.GetRasterBand(1)
# #band.SetNoDataValue(0)
# gdal.RasterizeLayer(sub_wdpa, [1], wdpa, burn_values=[1], options=OPTIONS)
# sub_wdpa_arr = sub_wdpa.ReadAsArray()
# sub_wdpa_arr[sub_wdpa_arr != 1] = 0
# wdpa.SetAttributeFilter(None)
# wdpa.ResetReading()
#
# # rasterize WDPA opposite!!!!
# wdpa.SetAttributeFilter("IUCN_CAT = 'Not Reported' or IUCN_CAT = 'IV' or IUCN_CAT = 'V' or IUCN_CAT = 'Not Applicable' or IUCN_CAT = 'III'")
# sub_wdpa_opp = drvMemR.Create('', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# # sub = gtiff_driver.Create('E:/Florian/MSc_outside_Seafile/RS_Data/MODIS/test.tiff', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# sub_wdpa_opp.SetGeoTransform(b1.GetGeoTransform())
# sub_wdpa_opp.SetProjection(b1.GetProjection())
# band = sub_wdpa_opp.GetRasterBand(1)
# band.SetNoDataValue(0)
# gdal.RasterizeLayer(sub_wdpa_opp, [1], wdpa, burn_values=[1], options=OPTIONS)
# sub_wdpa_opp_arr = sub_wdpa_opp.ReadAsArray()
# sub_wdpa_opp_arr[sub_wdpa_opp_arr!=1] = 0
# wdpa.SetAttributeFilter(None)
# wdpa.ResetReading()
#
# # rasterize paraguay privadas
# sub_ppriv = drvMemR.Create('', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# sub_ppriv.SetGeoTransform(b1.GetGeoTransform())
# sub_ppriv.SetProjection(b1.GetProjection())
# band = sub_ppriv.GetRasterBand(1)
# #band.SetNoDataValue(0)
# gdal.RasterizeLayer(sub_ppriv, [1], ppriv, burn_values=[1], options=OPTIONS)
# sub_ppriv_arr = sub_ppriv.ReadAsArray()
# sub_ppriv_arr[sub_ppriv_arr!=1] = 0
#
# # rasterize paraguay publicadas
# sub_ppub = drvMemR.Create('', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# sub_ppub.SetGeoTransform(b1.GetGeoTransform())
# sub_ppub.SetProjection(b1.GetProjection())
# band = sub_ppub.GetRasterBand(1)
# #band.SetNoDataValue(0)
# gdal.RasterizeLayer(sub_ppub, [1], ppriv, burn_values=[1], options=OPTIONS)
# sub_ppub_arr = sub_ppub.ReadAsArray()
# sub_ppub_arr[sub_ppub_arr!=1] = 0
#
# # rasterize forest zone 1
# sub_argf = drvMemR.Create('', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# sub_argf.SetGeoTransform(b1.GetGeoTransform())
# sub_argf.SetProjection(b1.GetProjection())
# band = sub_argf.GetRasterBand(1)
# #band.SetNoDataValue(0)
# argf.SetAttributeFilter("OT_class = '1'")
# gdal.RasterizeLayer(sub_argf, [1], argf, burn_values=[1], options=OPTIONS)
# sub_argf_arr = sub_argf.ReadAsArray()
# sub_argf_arr[sub_argf_arr!=1] = 0
# argf.SetAttributeFilter(None)
# argf.ResetReading()
#
# # rasterize argentinia nacionales
# sub_argn  = drvMemR.Create('', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# sub_argn.SetGeoTransform(b1.GetGeoTransform())
# sub_argn.SetProjection(b1.GetProjection())
# band = sub_argn.GetRasterBand(1)
# #band.SetNoDataValue(0)
# gdal.RasterizeLayer(sub_argn, [1], argn, burn_values=[1], options=OPTIONS)
# sub_argn_arr = sub_argn.ReadAsArray()
# sub_argn_arr[sub_argn_arr!=1]=0
#
# # rasterize Bolivia departamentales
# sub_bold = drvMemR.Create('', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# sub_bold.SetGeoTransform(b1.GetGeoTransform())
# sub_bold.SetProjection(b1.GetProjection())
# band = sub_bold.GetRasterBand(1)
# #band.SetNoDataValue(0)
# gdal.RasterizeLayer(sub_bold, [1], bold, burn_values=[1], options=OPTIONS)
# sub_bold_arr = sub_bold.ReadAsArray()
# sub_bold_arr[sub_bold_arr!=1] = 0
#
# # rasterize Bolivia nacionales
# boln.SetAttributeFilter("categoria = 'Parque Nacional y Territorio Indigena' or categoria = 'Parque Nacional'")
# sub_boln = drvMemR.Create('', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# sub_boln.SetGeoTransform(b1.GetGeoTransform())
# sub_boln.SetProjection(b1.GetProjection())
# band = sub_boln.GetRasterBand(1)
# #band.SetNoDataValue(0)
# gdal.RasterizeLayer(sub_boln, [1], boln, burn_values=[1], options=OPTIONS)
# sub_boln_arr = sub_boln.ReadAsArray()
# sub_boln_arr[sub_boln_arr!=1] =0
# boln.SetAttributeFilter(None)
# boln.ResetReading()
#
# ######################################################################################################################################### indigenous territories
# # Kristinas layer
# i1 = ogr.Open('K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/Objective_3/Indigenous_lands/Ayoreo_BOL_PAR_Kristina/ayoreo_bolivia.shp')
# il1 = i1.GetLayer()
# q1 = drvMemR.Create('', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# q1.SetGeoTransform(b1.GetGeoTransform())
# q1.SetProjection(b1.GetProjection())
# band = q1.GetRasterBand(1)
# #band.SetNoDataValue(0)
# gdal.RasterizeLayer(q1, [1], il1, burn_values=[1], options=OPTIONS)
# i1_arr = q1.ReadAsArray()
# i1_arr[i1_arr!=1]=0
#
# i2 = ogr.Open('K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/Objective_3/Indigenous_lands/Ayoreo_BOL_PAR_Kristina/ayoreo_paraguay_bolivia.shp')
# il2 = i2.GetLayer()
# q2 = drvMemR.Create('', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# q2.SetGeoTransform(b1.GetGeoTransform())
# q2.SetProjection(b1.GetProjection())
# band = q2.GetRasterBand(1)
# #band.SetNoDataValue(0)
# gdal.RasterizeLayer(q2, [1], il2, burn_values=[1], options=OPTIONS)
# i2_arr = q2.ReadAsArray()
# i2_arr[i2_arr!=1]=0
#
# # Bol
# i3 = ogr.Open('K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/Objective_3/Indigenous_lands/BOL/tco_titulado_2012/tco_titulado_2012.shp')
# il3 = i3.GetLayer()
# q3 = drvMemR.Create('', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# q3.SetGeoTransform(b1.GetGeoTransform())
# q3.SetProjection(b1.GetProjection())
# band = q3.GetRasterBand(1)
# #band.SetNoDataValue(0)
# gdal.RasterizeLayer(q3, [1], il3, burn_values=[1], options=OPTIONS)
# i3_arr = q3.ReadAsArray()
# i3_arr[i3_arr!=1]=0
#
# # PAR
# i4 = ogr.Open('K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/Objective_3/Indigenous_lands/PRY/Comunidades_1/comunidades1.shp')
# il4 = i4.GetLayer()
# q4 = drvMemR.Create('', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# q4.SetGeoTransform(b1.GetGeoTransform())
# q4.SetProjection(b1.GetProjection())
# band = q4.GetRasterBand(1)
# #band.SetNoDataValue(0)
# gdal.RasterizeLayer(q4, [1], il4, burn_values=[1], options=OPTIONS)
# i4_arr = q4.ReadAsArray()
# i4_arr[i4_arr!=1]=0
#
# # i5 = ogr.Open('K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/Objective_3/Indigenous_lands/Ayoreo_comm_PAR/ayoreos_territory.shp')
# # il5 = i5.GetLayer()
# # q5 = drvMemR.Create('', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# # q5.SetGeoTransform(b1.GetGeoTransform())
# # q5.SetProjection(b1.GetProjection())PR
# # band = q5.GetRasterBand(1)
# # #band.SetNoDataValue(0)
# # gdal.RasterizeLayer(q5, [1], il5, burn_values=[1], options=OPTIONS)
# # i5_arr = q5.ReadAsArray()
# # i5_arr[i5_arr!=1]=0
#
#
# # ARG
# i6 = ogr.Open('K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/Objective_3/Indigenous_lands/ARG/Indigenous_settlements_points_konvex_buffer.shp')
# il6 = i6.GetLayer()
# q6 = drvMemR.Create('', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# q6.SetGeoTransform(b1.GetGeoTransform())
# q6.SetProjection(b1.GetProjection())
# band = q6.GetRasterBand(1)
# #band.SetNoDataValue(0)
# gdal.RasterizeLayer(q6, [1], il6, burn_values=[1], options=OPTIONS)
# i6_arr = q6.ReadAsArray()
# i6_arr[i6_arr!=1]=0

################################################################################################################## puestos
puesto_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/Objective_3/puestos/All_puestos_year_no0_fixedMPR_KK_LL.shp'
puesto = ogr.Open(puesto_p)
puestos = puesto.GetLayer()
#
# puestos_container = []
# buffer_sizes = [1000, 2000, 3000, 4000, 5000]
# for buff in buffer_sizes:
#     driv = ogr.GetDriverByName('MEMORY')
#     source = driv.CreateDataSource('memData')
#     out_lyr = source.CreateLayer('', getSpatRefVec(puesto),puestos.GetGeomType())
#     out_lyr.CreateFields(puestos.schema)
#     out_feat = ogr.Feature(out_lyr.GetLayerDefn())
#
#     for feat in puestos:
#         geom = feat.geometry().Clone()
#         # buffer it
#         buffi = geom.Buffer(buff)
#         # create layer from buffered
#         out_feat.SetGeometry(buffi)
#         for ii in range(feat.GetFieldCount()):
#             out_feat.SetField(ii, feat.GetField(ii))
#         out_lyr.CreateFeature(out_feat)
#     puestos.ResetReading()
#     # rasterize it
#     sb = drvMemR.Create('', m.RasterXSize, m.RasterYSize, 1, gdal.GDT_Int16)
#     sb.SetGeoTransform(m.GetGeoTransform())
#     sb.SetProjection(m.GetProjection())
#     band = sb.GetRasterBand(1)
#     gdal.RasterizeLayer(sb, [1], out_lyr, burn_values=[100])
#     pue_arr = sb.ReadAsArray()
#     pue_arr[pue_arr!=100]=0
#     pue_arr_mas = pue_arr * mask
#     puestos_container.append(pue_arr_mas)

sub_puestopoints  = drvMemR.Create('', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
sub_puestopoints.SetGeoTransform(b1.GetGeoTransform())
sub_puestopoints.SetProjection(b1.GetProjection())
band = sub_puestopoints.GetRasterBand(1)
gdal.RasterizeLayer(sub_puestopoints, [1], puestos, burn_values=[1])
puestop_arr = sub_puestopoints.ReadAsArray()
# puestop_arr[puestop_arr<100]=0
puestop_masked = puestop_arr * mask
puestop_masked[puestop_masked==0] = np.nan
#
# ##################################################################################################################################################### countries
# cou = ogr.Open('K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/south_america/countries_sub.shp')
# coun = cou.GetLayer()
# subc  = drvMemR.Create('', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
# subc.SetGeoTransform(b1.GetGeoTransform())
# subc.SetProjection(b1.GetProjection())
# band = subc.GetRasterBand(1)
# gdal.RasterizeLayer(subc, [1], coun, options=["ALL_TOUCHED=TRUE", "ATTRIBUTE=Burner"])
# subc_arr = subc.ReadAsArray()
# subc_arr[subc_arr<100]=0
# subc_arr_masked = subc_arr * mask
# subc_arr_masked[subc_arr_masked==0] = np.nan
#
# ##################################################################################################################################################### Nori
# n1 = gdal.Open('P:/LandSystems_20/dump/Nori_CAZ_raster.tif')
# n2 = gdal.Open('P:/LandSystems_20/dump/Nori_ABF_raster.tif')
# nori_CAZ = n1.GetRasterBand(1).ReadAsArray()
# nori_ABF = n2.GetRasterBand(1).ReadAsArray()
# nori_CAZ_masked = nori_CAZ * mask
# nori_CAZ_masked = nori_CAZ_masked.astype(np.float)
# nori_CAZ_masked[nori_CAZ_masked==0] = np.nan
# nori_ABF_masked = nori_ABF * mask
# nori_ABF_masked = nori_ABF_masked.astype(np.float)
# nori_ABF_masked[nori_ABF_masked==0] = np.nan
#
# ##################################################################################################################################################### TNC
# tn = gdal.Open('P:/LandSystems_20/dump/TNC_84_raster.tif')
# tnc = tn.GetRasterBand(1).ReadAsArray()
# tnc_masked = tnc * mask
# tnc_masked[tnc_masked==0] = np.nan
#
# ##################################################################################################################################################### bring them together
# ind_arr = i1_arr + i2_arr + i3_arr + i4_arr +i6_arr
# ind_arr_masked = ind_arr * mask
# ind_arr_masked[ind_arr_masked>0] = 10
#
# p_arr_masked = puestos_container[0] + puestos_container[1] + puestos_container[2] + puestos_container[3] + puestos_container[4]
# p_arr_masked[p_arr_masked==500] = 1000
# p_arr_masked[p_arr_masked==400] = 2000
# p_arr_masked[p_arr_masked==300] = 3000
# p_arr_masked[p_arr_masked==200] = 4000
# p_arr_masked[p_arr_masked==100] = 5000
#
# strict = sub_wdpa_arr + sub_argf_arr + sub_argn_arr + sub_boln_arr + sub_ppriv_arr + sub_ppub_arr
# strict_masked = strict * mask
# strict_masked[strict_masked>0] = 1
#
# rows, cols = np.where(strict_masked==1)
#
# non_strict = sub_wdpa_opp_arr + sub_bold_arr
# non_strict_masked = non_strict * mask
# non_strict_masked[rows, cols] = 0
# non_strict_masked[non_strict_masked>0] = 2
#
# all_protected = strict_masked + non_strict_masked
# all_protected[all_protected>0] = 3
#
# nori_ABF_masked[nori_ABF_masked>0] = 100
# nori_CAZ_masked[nori_CAZ_masked>0] = 200
#
# tnc_masked[tnc_masked>0] = 300


#################################################################### extract
names = [#'allChaco','strict','nonstrict','countries','puestos','indig','nori_abf','nori_caz',
         #'all_protected', 'tnc',
         'puestopoints_bin']

combis = [#mask, strict_masked, non_strict_masked,subc_arr_masked,p_arr_masked,ind_arr_masked,nori_ABF_masked,nori_CAZ_masked,
          #all_protected,tnc_masked,
          puestop_masked]


################################################################################################################################# run it
for count2,nami in enumerate(names):
    print(nami)
    dumm2 = gtiff_driver.Create('P:/LandSystems_20/PAs_Indig_Puesto_raster/' + names[count2] + '.tiff', b3.shape[1], b3.shape[0], 1, gdal.GDT_Int16)
    dumm2.SetGeoTransform(b1.GetGeoTransform())
    dumm2.SetProjection(b1.GetProjection())
    band = dumm2.GetRasterBand(1)
    # band.SetNoDataValue(0)
    band.WriteArray(combis[count2])
    del dumm2
