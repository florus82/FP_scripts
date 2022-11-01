#########################################################################
############# Buffers puestos and rasterizes them into tile-system (Matthias's landcover product)

from FloppyToolZL.MasterFuncs import *
drvMemR = gdal.GetDriverByName('MEM')
gtiff_driver = gdal.GetDriverByName('GTiff')
OPTIONS = ['ALL_TOUCHED=TRUE']

storpath = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/99_Auxiliaries/Puesto_raster/puestos/'
tilespath = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/LandCover/Run12/output_LandCover'
tiles = getFilelist(tilespath, '.tif')

puesto_p = 'K:/Seafile/Uni_Life/CarbonPaper/GIS_Data/Objective_3/puestos/All_puestos_year_no0_fixedMPR_KK_LL.shp'
puesto = ogr.Open(puesto_p)
puestos = puesto.GetLayer()

# get subsets for the years
puestoA = getAttributesALL(puestos)
index85 = [count for count, i in enumerate(puestoA['1985']) if i == 1]
index90 = [count for count, i in enumerate(puestoA['1990']) if i == 1]
index95 = [count for count, i in enumerate(puestoA['1995']) if i == 1]
index00 = [count for count, i in enumerate(puestoA['2000']) if i == 1]
index05 = [count for count, i in enumerate(puestoA['2005']) if i == 1]
index10 = [count for count, i in enumerate(puestoA['2010']) if i == 1]
index15 = [count for count, i in enumerate(puestoA['2015']) if i == 1]
index18 = [count for count, i in enumerate(puestoA['2018']) if i == 1]
indexL = [index85, index90, index95, index00, index05, index10, index15, index18]
buffer_sizes = [300, 1500, 3000]
years = [1985, 1990, 1995, 2000, 2005, 2010, 2015, 2018]

for buff in buffer_sizes:
    for c2, index_year in enumerate(indexL):
        driv = ogr.GetDriverByName('MEMORY')
        source = driv.CreateDataSource('memData')
        out_lyr = source.CreateLayer('', getSpatRefVec(puesto),puestos.GetGeomType())
        out_lyr.CreateFields(puestos.schema)
        out_feat = ogr.Feature(out_lyr.GetLayerDefn())
        for c1, feat in enumerate(puestos):
            if c1 in index_year:
                geom = feat.geometry().Clone()
                # buffer it
                buffi = geom.Buffer(buff)
                # create layer from buffered
                out_feat.SetGeometry(buffi)
                for ii in range(feat.GetFieldCount()):
                    out_feat.SetField(ii, feat.GetField(ii))
                out_lyr.CreateFeature(out_feat)
            else:
                continue
        puestos.ResetReading()
        # rasterize it on tiles
        for tile in tiles:
            til = gdal.Open(tile,0)
            sb = gtiff_driver.Create(storpath + 'tiles/' + '_'.join(tile.split('/')[-1].split('_')[0:2]) + '_Buffsiz_' + str(buff) + '_' + str(years[c2]) + '.tif', til.RasterXSize, til.RasterYSize, 1, gdal.GDT_Int16)
            sb.SetGeoTransform(til.GetGeoTransform())
            sb.SetProjection(til.GetProjection())
            band = sb.GetRasterBand(1)
            gdal.RasterizeLayer(sb, [1], out_lyr, burn_values=[1])
            #sb.GetRasterBand(1).SetNoDataValue(0)
            del sb


# make annual vrts

files = getFilelist(storpath + 'tiles', '.tif')

for year in years:
    subby = [f for f in files if int(f.split('_')[-1].split('.')[0]) == year]
    for buf in buffer_sizes:
        b_sub = [sub for sub in subby if int(sub.split('_')[-2]) == buf]
        img_path = storpath + 'puestos_' + str(year) + '_' + 'Buffer_' + str(buf) + '.vrt'
        my_vrt = gdal.BuildVRT(img_path, b_sub)
        my_vrt = None