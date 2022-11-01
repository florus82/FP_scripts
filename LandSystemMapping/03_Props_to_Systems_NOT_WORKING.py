import numpy as np
import gdal
import math
import ogr
import pandas as pd
import os

##############################################
######## paths, parameter & functions ########
##############################################

########## functions
def loadsingleraster(rasterpath):
    ds = gdal.Open(rasterpath)
    in_arr = ds.GetRasterBand(1).ReadAsArray()
    return in_arr

def loadstacki(rasterpath):
    rasterlist = []
    ds = gdal.Open(rasterpath)
    stackbands = ds.RasterCount
    for band in range(stackbands):
        rasterlist.append(ds.GetRasterBand(band+1).ReadAsArray())
    stacki = np.dstack(rasterlist)
    return stacki

def exportArray(origin_ds, type_origin, out_arr, agg_fac, cols, rows, bands, storpath):
    out_dss = gtiff_driver.Create(storpath,
                                  cols, rows, bands, type_origin.GetRasterBand(1).DataType)
    win_gt = origin_ds.GetGeoTransform()
    out_gt = [win_gt[0], win_gt[1] * agg_fac, win_gt[2], win_gt[3], win_gt[4], win_gt[5] * agg_fac]
    out_dss.SetGeoTransform(out_gt)
    out_dss.SetProjection(origin_ds.GetProjection())
    for band in range(bands):
        out_dss.GetRasterBand(band + 1).WriteArray(out_arr[:, :, band])
        out_dss.GetRasterBand(band + 1).SetNoDataValue(-999)
    del out_dss

def getFilelist(originpath, ftyp):
    files = os.listdir(originpath)
    out   = []
    for i in files:
        if i.split('.')[-1] in ftyp:
            if originpath.endswith('/'):
                out.append(originpath + i)
            else:
                out.append(originpath + '/' + i)
        # else:
        #     print("non-matching file - {} - found".format(i.split('.')[-1]))
    return out

########## paths
combi = '12_20_20_30_18'
agg_path = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/01_Aggregations'
## pixel count per LC per year (1985- 2020)
lc_props_list = [agg_path + '/LandCover/one_stack/300/' + combi + '/lc_props_' + combi + '_agg_300.tif',
                 agg_path + '/LandCover/one_stack/1500/' + combi + '/lc_props_' + combi + '_agg_1500.tif',
                 agg_path + '/LandCover/one_stack/3000/' + combi + '/lc_props_' + combi + '_agg_3000.tif']
tc_props_list = [agg_path + '/TreeCover/300/TC_aggregeated_to_300.tif',
                 agg_path + '/TreeCover/1500/TC_aggregeated_to_1500.tif',
                 agg_path + '/TreeCover/3000/TC_aggregeated_to_3000.tif']
wc_props_list = [agg_path + '/WoodyCover/300/WC_aggregeated_to_300.tif',
                 agg_path + '/WoodyCover/1500/WC_aggregeated_to_1500.tif',
                 agg_path + '/WoodyCover/3000/WC_aggregeated_to_3000.tif']

## Countries and Chaco and others
countriespath = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/99_Auxiliaries/South_America.shp'
chacopath = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/99_Auxiliaries/Chaco_84.shp'
lss_path = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/03_LandSystems/'
puestoL = getFilelist('M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/99_Auxiliaries/Puesto_raster/puestos_agg/', '.tif')
indigL = getFilelist('M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/99_Auxiliaries/Indigenous_raster/', '.tif')
pasL = getFilelist('M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/99_Auxiliaries/PA_raster/', '.tif')

########## parameter
drivMemRas = gdal.GetDriverByName('MEM')
gtiff_driver = gdal.GetDriverByName('GTiff')
## years of annual lc
years = 36

####### dictionary for result export
keys = ['Space', 'Class', 'Area', 'Year', 'threshUP', 'threshLOW', 'aggfac']
vals = [list() for _ in keys]
res = dict(zip(keys, vals))

#########################################
######## load data and get ready ########
#########################################

## read-in lc_props stack, where bands are ordered as follows:
# there are 36 sequences of 12 lc bands in the same order ['F', 'NatGras', 'Sav', 'WetGras', 'C', 'P', 'OV', 'Pdeg_F', 'Pdeg_NatGras', 'Pdeg_Sav', 'Pdeg_WetGras','SP']
# the pixel values are the share of the respective class within that pixel in %

for lc_props in lc_props_list:

    # determine resolution of current loop
    aggfac = int(lc_props.split('/')[-1].split('_')[-1].split('.')[0])
    # load the aggregated alndcover stack
    lc_props_arr = loadstacki(lc_props)
    # load additional layers
    trees = loadsingleraster(tc_props_list[[int(str.split(i, '/')[-1].split('_')[-1].split('.')[0]) for i in tc_props_list].index(aggfac)])
    puestos = loadsingleraster(puestoL[[int(str.split(i, '/')[-1].split('_')[-1].split('.')[0]) for i in puestoL].index(aggfac)])
    indigenous = loadsingleraster(indigL[[int(str.split(i, '/')[-1].split('_')[-1].split('.')[0]) for i in indigL].index(aggfac)])
    pas = loadsingleraster(pasL[[int(str.split(i, '/')[-1].split('_')[-1].split('.')[0]) for i in pasL].index(aggfac)])

   ## get indices for classes across years
    # get bands for forest
    bands_F =  [i for i in range(0, lc_props_arr.shape[2], int(lc_props_arr.shape[2] / years))]
    # get bands for natural grasslands
    bands_Natgras =  [i for i in range(1, lc_props_arr.shape[2], int(lc_props_arr.shape[2] / years))]
    # get bands for savannas
    bands_Sav = [i for i in range(2, lc_props_arr.shape[2], int(lc_props_arr.shape[2] / years))]
    # get bands for wet grasslands
    bands_Wetgras = [i for i in range(3, lc_props_arr.shape[2], int(lc_props_arr.shape[2] / years))]
    # get bands for crop
    bands_C = [i for i in range(4, lc_props_arr.shape[2], int(lc_props_arr.shape[2] / years))]
    # get bands for pasture
    bands_P = [i for i in range(5, lc_props_arr.shape[2], int(lc_props_arr.shape[2] / years))]
    # get bands for other vegetation
    bands_OV = [i for i in range(6, lc_props_arr.shape[2], int(lc_props_arr.shape[2] / years))]
    # get bands for puesto degraded forests
    bands_PdegF = [i for i in range(7, lc_props_arr.shape[2], int(lc_props_arr.shape[2] / years))]
    # get bands for puesto degraded natrual grasslands
    bands_Pdeg_NatGras = [i for i in range(8, lc_props_arr.shape[2], int(lc_props_arr.shape[2] / years))]
    # get bands for puesto degraded savannas
    bands_Pdeg_Sav = [i for i in range(9, lc_props_arr.shape[2], int(lc_props_arr.shape[2] / years))]
    # get bands for puesto degraded wet grasslands
    bands_Pdeg_WetGras = [i for i in range(10, lc_props_arr.shape[2], int(lc_props_arr.shape[2] / years))]
    # get bands for silvopasture
    bands_SP = [i for i in range(11, lc_props_arr.shape[2], int(lc_props_arr.shape[2] / years))]

    #############################################
    ######## mask to chaco and countries ########
    #############################################

    # load chaco and country layer
    # cha = ogr.Open(chacopath)
    # cha_l = cha.GetLayer()
    cou = ogr.Open(countriespath)
    cou_l = cou.GetLayer()

    # create chaco mask in memory
    # out_ds = drivMemRas.Create('', lc_props_arr.shape[1], lc_props_arr.shape[0], 1, gdal.GDT_Byte)
    # out_ds.SetGeoTransform(gdal.Open(lc_props).GetGeoTransform())
    # out_ds.SetProjection(gdal.Open(lc_props).GetProjection())
    # gdal.RasterizeLayer(out_ds, [1], cha_l, burn_values=[1])
    #
    # cha_mask = out_ds.GetRasterBand(1).ReadAsArray() # 1 = chaco, 0 = outside
    # del out_ds

    # create country mask in memory
    out_ds = drivMemRas.Create('', lc_props_arr.shape[1], lc_props_arr.shape[0], 1, gdal.GDT_Byte)
    out_ds.SetGeoTransform(gdal.Open(lc_props).GetGeoTransform())
    out_ds.SetProjection(gdal.Open(lc_props).GetProjection())
    OPTIONS = ['ATTRIBUTE=Country_ID']
    gdal.RasterizeLayer(out_ds, [1], cou_l, options=OPTIONS)

    cou_mask = out_ds.GetRasterBand(1).ReadAsArray() # 11 = PRY, 2 = BOL, 1= ARG
    del out_ds

    ########################################
    ######## calculate land-systems ########
    ########################################

    ## classes
    # pure (more than/equal to 90% of a class per aggregated pixel)
    pureF = 10 # more than/equal to 90% of class 1 (forest)
    pureOV = 20 # more than/equal to 90% of class 2 (crop)
    pureC = 30 # more than/equal to 90% of class 3 (pasture)
    pureP = 40 # more than/equal to 90% of class 4 (other veg)
    pureO = 50 # more than/equal to 90% of class 5 (other)
    pureSP = 90 # more than/equal to 90% of class 9 (silvopastures)
    # mixed production less than 90% and more than/equal to 50% of forest, crop, pastures, silvopastures)
    mixedProd = 100
    # mixed system
    mixedSys = 200

    lss_classes = [10,20,30,40,50,90,100,200]
    lss_names = ['PureForest', 'PureOtherVeg', 'PureCrop', 'PurePasture', 'PureOther', 'PureSilvoPasture', 'MixedProduction', 'MixedSystem']
    ## create empty array for exporting landsystem-classification
    out_arr_lss = np.zeros((trees.shape[0], trees.shape[1], years), dtype=np.uint8)

    ## transform thresholds into pixelcounts

    tUps = [0.9, 0.85, 0.8, 0.75, 0.7]
    tLow = [0.5, 0.45, 0.4, 0.35, 0.3]

    threshUPs = [math.ceil(i*aggfac**2) for i in tUps]
    threshLOWs = [math.ceil(i*aggfac**2) for i in tLow]

    for threshUP in threshUPs:
        for threshLOW in threshLOWs:
            print('calc between ' + str(threshLOW) + ' and ' + str(threshUP))
            ## pure classes (more than thresUP of a class per aggregated pixel)
            out_arr_lss[np.where(lc_props_arr[:,:,bands_F] >= threshUP)] = pureF
            out_arr_lss[np.where(lc_props_arr[:,:,bands_C] >= threshUP)] = pureC
            out_arr_lss[np.where(lc_props_arr[:,:,bands_P] >= threshUP)] = pureP
            out_arr_lss[np.where(lc_props_arr[:,:,bands_OV] >= threshUP)] = pureOV
            out_arr_lss[np.where(lc_props_arr[:,:,bands_O] >= threshUP)] = pureO
            out_arr_lss[np.where(lc_props_arr[:,:,bands_SP] >= threshUP)] = pureSP

            ## mixed production (sum of forest, crop, pasture and silvopasture between threshLOW and threshUP)
            out_arr_lss[np.where(lc_props_arr[:,:,bands_F] + lc_props_arr[:,:,bands_C] + lc_props_arr[:,:,bands_P] + lc_props_arr[:,:,bands_SP] >= threshLOW)] = mixedProd

            # mixed systems (sum of forest, crop, pasture and silvopasture below threshLOW)
            out_arr_lss[np.where(np.logical_and(lc_props_arr[:,:,bands_F] + lc_props_arr[:,:,bands_C] + lc_props_arr[:,:,bands_P] + lc_props_arr[:,:,bands_SP] < threshLOW,
                                 lc_props_arr[:,:,bands_F] + lc_props_arr[:,:,bands_C] + lc_props_arr[:,:,bands_P] + lc_props_arr[:,:,bands_SP] > 0))] = mixedSys

            ###############################
            ######## export ###############
            ###############################

            # mask to Chaco and export stack
            out_arr_lss_masked = out_arr_lss
            for n in range(out_arr_lss_masked.shape[2]):
                out_arr_lss_masked[:,:,n] = out_arr_lss_masked[:,:,n] #* cha_mask
            exportArray(gdal.Open(lc_props), gdal.Open(lc_props), out_arr_lss_masked, 1, out_arr_lss.shape[1], out_arr_lss.shape[0], out_arr_lss.shape[2],
                        storpath = lss_path + '/lss_map_' + str(threshLOW) + '_' + str(threshUP) + '.tif')


            # get indices for countries
            PRY_rows, PRY_cols = np.where(cou_mask == 11)
            BOL_rows, BOL_cols = np.where(cou_mask == 2)
            ARG_rows, ARG_cols = np.where(cou_mask == 1)
            cou_list = [[PRY_rows, PRY_cols], [BOL_rows, BOL_cols], [ARG_rows, ARG_cols]]
            # loop over all years
            for n in range(out_arr_lss_masked.shape[2]):
                # loop over lss classes for entire chaco
                for i, cl in enumerate(lss_classes):
                    res['Year'].append(n + 1985)
                    res['threshUP'].append(threshUP)
                    res['threshLOW'].append(threshLOW)
                    res['Space'].append('Ecoregion')
                    res['Class'].append(lss_names[i])
                    res['Area'].append((out_arr_lss_masked[:,:,n] == cl).sum() * (((aggfac*30)**2)/1000000)) # in km²
                    res['aggfac'].append(aggfac)
                    # loop over lss classes for countries
                    for j, cou in enumerate(['PRY', 'BOL', 'ARG']):
                        res['Year'].append(n + 1985)
                        res['threshUP'].append(threshUP)
                        res['threshLOW'].append(threshLOW)
                        res['Space'].append(cou)
                        res['Class'].append(lss_names[i])
                        res['Area'].append((out_arr_lss_masked[cou_list[j][0], cou_list[j][1], n] == cl).sum() * (((aggfac*30)**2) / 1000000))  # in km²
                        res['aggfac'].append(aggfac)

df  = pd.DataFrame(data = res)
df.to_csv(lss_path + '/results.csv', sep=',',index=False)