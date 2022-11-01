import numpy as np
import pandas as pd
import gdal
import math
import os
import time
#from sklearn.externals import joblib
from joblib import Parallel, delayed
import ogr, osr
import sys

# getFilelist returns a list with all files of a certain type in a path
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
##############################################
######## paths, parameter & functions ########
##############################################


########## paths
#aggregpath = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/01_Aggregations' # mother folder
trash = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/temp' # temp folder
lc_fol = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/LandCover/Run12/output_LandCover'
sc_fol = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/TreeShrubCover/2019/SC'
tc_fol = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/TreeShrubCover/2019/TC'
ma_fol = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/99_Auxiliaries/mask_in_tiles'
pu_fol = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/99_Auxiliaries/Puesto_raster/puestos_buffered/tiles'
csv_path = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/09_csv/'
cleansh_path = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/99_Auxiliaries/CleanerShape1.shp'

########## parameter
gtiff_driver = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
os.environ['PROJ_LIB'] = 'C:/ProgramData/Anaconda3/envs/pythonProject2/Library/share/proj'
os.environ['GDAL_DATA'] = 'C:/ProgramData/Anaconda3/envs/pythonProject2/Library/share/gdal'

########## get the files in lists and check order
tc_files = getFilelist(tc_fol, '.tif')  # order will be checked below
sc_files = getFilelist(sc_fol, '.tif')  # order will be checked below
lc_files = getFilelist(lc_fol, '.tif')  # order will be checked below
ma_files = getFilelist(ma_fol, '.tif')  # order will be checked below
pu_files = getFilelist(pu_fol, '.tif')

for i in range(len(tc_files)):
    if ('_'.join(tc_files[i].split('/')[-1].split('_')[0:2]) ==
        '_'.join(sc_files[i].split('/')[-1].split('_')[0:2])) is False:
        sys.exit('check of list order required')
    if ('_'.join(tc_files[i].split('/')[-1].split('_')[0:2]) == '_'.join(lc_files[i].split('/')[-1].split('_')[0:2])) is False:
        sys.exit('check of list order required')
    if ('_'.join(tc_files[i].split('/')[-1].split('_')[0:2]) ==
        '_'.join(ma_files[i].split('/')[-1].split('_')[0:2])) is False:
        sys.exit('check of list order required')

########## functions
def delete_multiple_element(list_object, indices):
    indices = sorted(indices, reverse=True)
    for idx in indices:
        if idx < len(list_object):
            list_object.pop(idx)
def getSpatRefVec(layer):

    # check the type of layer
    if type(layer) is ogr.Geometry:
        SPRef   = layer.GetSpatialReference()

    elif type(layer) is ogr.Feature:
        lyrRef  = layer.GetGeometryRef()
        SPRef   = lyrRef.GetSpatialReference()

    elif type(layer) is ogr.Layer:
        SPRef   = layer.GetSpatialRef()

    elif type(layer) is ogr.DataSource:
        lyr     = layer.GetLayer(0)
        SPRef   = lyr.GetSpatialRef()

    elif type(layer) is str:
        lyrOpen = ogr.Open(layer)
        lyr     = lyrOpen.GetLayer(0)
        SPRef   = lyr.GetSpatialRef()

    #print(SPRef)
    return(SPRef)
def preCleanUP(cleanshape_path, rasterstack, shape1, shape0, year1): # 21 over the entire time period
    drvMemR = gdal.GetDriverByName('MEM')
    OPTIONS = ['ALL_TOUCHED=TRUE']
    cls = ogr.Open(cleanshape_path)
    cls_ly = cls.GetLayer()
    sub_ras = drvMemR.Create('', shape1, shape0, 1, gdal.GDT_Int16)
    #sub_ras = gtiff_driver.Create('G:/LandSystems_20/99_Auxiliaries/classification_clean_up//test2.tiff', shape1, shape0, 1, gdal.GDT_Int16)
    sub_ras.SetGeoTransform(rasterstack.GetGeoTransform())
    sub_ras.SetProjection(rasterstack.GetProjection())
    band = sub_ras.GetRasterBand(1)
    gdal.RasterizeLayer(sub_ras, [1], cls_ly, burn_values=[1], options=OPTIONS)
    cl_sh = sub_ras.ReadAsArray()
    r, c = np.where(cl_sh == 1)
    relable = np.where(np.logical_or(year1[r, c] == 3, year1[r, c] == 4))
    #year1[r[relable[0]],c[relable[0]]] = 21
    del sub_ras
    return r[relable[0]], c[relable[0]]
# RasterKiller destroys a raster on disc
def RasterKiller(raster_path):
    if os.path.isfile(raster_path):
        os.remove(raster_path)
# reproject a raster
def reprojRaster(rasterpath, open_Aim,  storPath):
    gtiff_driver = gdal.GetDriverByName('GTiff')

    img = gdal.Open(rasterpath)
    imgNA = img.GetRasterBand(1).GetNoDataValue()
    out_ds = gtiff_driver.Create(storPath + '/' + rasterpath.split('/')[-1].split('.')[0] + '_reprojed.tif',
                                 open_Aim.RasterXSize, open_Aim.RasterYSize, 1, img.GetRasterBand(1).DataType)
    out_ds.SetGeoTransform(open_Aim.GetGeoTransform())
    out_ds.SetProjection(open_Aim.GetProjection())
    # out_ds.GetRasterBand(1).SetNoDataValue(imgNA)
    gdal.ReprojectImage(img, out_ds, img.GetProjection(), out_ds.GetProjection(), gdal.GRA_Cubic)
    del out_ds
# mask_file = ma_files[27]
# tree_file = tc_files[27]
# shrub_file = sc_files[27]
# tile_id = '267'
# landcover_file = lc_files[27]

def disturbedRCube(tree_file, shrub_file, landcover_file, mask_file, tile_id):
    reclassfol = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/02_Reclassification'
    ########## parameter
    gtiff_driver = gdal.GetDriverByName('GTiff')
    # create output template for check20
    keys = ['id', 'TC_silv', 'WC_silv', 'TC_sav', 'WC_sav', 'TC_sav2', 'Year_i', 'Year_j', 'Number_start', 'Number_into_crop', 'Number_into_pasture', 'Number_into_silvopasture', 'Number_into_grassland', 'Number_into_savannah', 'Number_end']
    vals = [list() for i in range(len(keys))]
    res  = dict(zip(keys, vals))

    # create output template for sav_wet
    keys = ['id', 'TC_silv', 'WC_silv', 'TC_sav', 'WC_sav', 'TC_sav2', 'Year_i', 'savwet_start','wet','sav']
    vals = [list() for i in range(len(keys))]
    res2 = dict(zip(keys, vals))

    # create output template for silvos
    keys = ['id', 'TC_silv', 'WC_silv', 'TC_sav', 'WC_sav', 'TC_sav2', 'Year_i', 'silvos']
    vals = [list() for i in range(len(keys))]
    res3 = dict(zip(keys, vals))

    # create output template for puestos
    keys = ['id', 'Year_i', 'buffsize','class15','tree_min_15','tree_max_15','tree_median_15','tree_quant_25_15','tree_quant_75_15','shrub_min_15','shrub_max_15','shrub_median_15','shrub_quant_25_15','shrub_quant_75_15','class16', 'tree_min_16','tree_max_16','tree_median_16','tree_quant_25_16','tree_quant_75_16','shrub_min_16','shrub_max_16','shrub_median_16','shrub_quant_25_16','shrub_quant_75_16', 'class17', 'tree_min_17','tree_max_17','tree_median_17','tree_quant_25_17','tree_quant_75_17','shrub_min_17','shrub_max_17','shrub_median_17','shrub_quant_25_17','shrub_quant_75_17','class18','tree_min_18','tree_max_18','tree_median_18','tree_quant_25_18','tree_quant_75_18','shrub_min_18','shrub_max_18','shrub_median_18','shrub_quant_25_18','shrub_quant_75_18', 'TC_silv', 'WC_silv', 'TC_sav', 'WC_sav', 'TC_sav2']

    vals = [list() for i in range(len(keys))]
    res4 = dict(zip(keys, vals))

    # load Chaco ecoregion mask tile
    m = gdal.Open(mask_file)
    mb = m.GetRasterBand(1)
    mask = mb.ReadAsArray().astype(np.float)
    mask[mask == 0] = np.nan
    # load trees and shrubs for aggregation in upcoming loop
    trees_ds = gdal.Open(tree_file)
    trees = trees_ds.GetRasterBand(1).ReadAsArray()
    trees = trees * mask # mask to Ecoregion extent

    shrubs_ds = gdal.Open(shrub_file)
    shrubs = shrubs_ds.GetRasterBand(1).ReadAsArray()
    shrubs = shrubs * mask # mask to Ecoregion extent
    # calc woody cover
    woods = shrubs + trees

    # get the tile_specific puestos
    sub_buffs = [p for p in pu_files if p.split('/')[-1].split('_')[1] == tile_id]
    # there are different buffer_sizes
    b1 = [b for b in sub_buffs if b.split('/')[-1].split('_')[-2] == '300']
    b2 = [b for b in sub_buffs if b.split('/')[-1].split('_')[-2] == '1500']
    b3 = [b for b in sub_buffs if b.split('/')[-1].split('_')[-2] == '3000']
    buff_sizeL = [b1, b2, b3]
    buffnames = [300,1500,3000]

    # create en empty data cube
    ds = gdal.Open(landcover_file)
        # define the search radius;  for how many years (from the current year in loop) into the future search for crop(3) and pastures(4)
    X = 3
    # loop over thresholds
    TC_silvs = [1200]
    WC_silvs = [2000]
    TC_savs = [2000]
    WC_savs = [3000]
    TC_sav2s = [1800]

    # read in the land cover product
    cube_origin = np.empty([ds.RasterYSize, ds.RasterXSize, ds.RasterCount], dtype='i1')
    for ra in range(ds.RasterCount):
        cube_origin[:,:,ra] = ds.GetRasterBand(ra+1).ReadAsArray()
        cube_origin[:,:,ra] = cube_origin[:,:,ra] * mask # mask to Ecoregion extent

    clean_r, clean_c =preCleanUP(cleansh_path, ds, cube_origin.shape[1], cube_origin.shape[0], cube_origin[:,:,0])
    cube_origin[clean_r,clean_c,:] = 21

    # puesto_counter = 0 # use this to only calculate puesto stuff once and not every iteration of thrreshold combi
    # c1 = TC_silvs[0]
    # c2 = WC_silvs[0]
    # c3 = TC_savs[0]
    # c4 = WC_savs[0]
    # c5 = TC_sav2s[0]
    for c1 in TC_silvs:
        for c2 in WC_silvs:
            for c3 in TC_savs:
                for c4 in WC_savs:
                    for c5 in TC_sav2s:
                        print(c5)
                        storpath = reclassfol + '/' + str(int(c1/100)) + '_' + str(int(c2/100)) + '_' + str(int(c3/100)) + '_' + str(int(c4/100)) + '_' + str(int(c5/100))# creates folder path to threshold combo
                        if os.path.isdir(storpath) is False:
                            os.mkdir(storpath)
                        else:
                            if len(getFilelist(storpath, '.tif')) == 83:
                                continue
                        cube = cube_origin.copy()
                        for i in range(cube.shape[2]):
                            # silvo check and set
                            past_rows, past_cols = np.where(cube[:,:,i] == 4)
                            sps = np.where(np.logical_or(trees[past_rows, past_cols] > c1, woods[past_rows, past_cols] > c2))
                            cube[past_rows[sps], past_cols[sps],i] = 9

                            res3['id'].append(tile_id)
                            res3['TC_silv'].append(c1)
                            res3['WC_silv'].append(c2)
                            res3['TC_sav'].append(c3)
                            res3['WC_sav'].append(c4)
                            res3['TC_sav2'].append(c5)
                            res3['Year_i'].append(i+1985)
                            res3['silvos'].append(len(sps[0]))

                            ##########################################################################
                            ########### What happens up to 3 years after disturbance? ################
                            ########### (DT1 on Miro Board Land System 2.0 Workflow)  ################
                            ##########################################################################

                            # search radius check
                            for j in range(1,X+1):
                                ############ take care of the last years + search radius problem #########

                                # search in the following years (j)
                                if i + j >= 36 and i != 35:  # this prevents from going into the unknow future ,e.g. i stands for the year 2020 (i=35) and j=2 would then search for changes in 2022
                                    continue
                                elif i + j >= 36 and i == 35:  # this takes care of the last year, where we can't look into the future but still want to look at class 20 and check TC and SC
                                    # get dist locations where conditions above don't apply
                                    dist_rows_new, dist_cols_new = np.where(cube[:, :, i] == 20)  # this return the row and col numbers!
                                    # check vegetation at these locations and implement decision tree 1 (DT1 on Miro Board Land System 2.0 Workflow)
                                    # check vegetation at these locations and implement decision tree 1 (DT1 on Miro Board Land System 2.0 Workflow)
                                    sav1 = np.where(trees[
                                                        dist_rows_new, dist_cols_new] >= c5)  # returns the indices of the distrows/cols where condition is true
                                    gras1 = np.where(trees[dist_rows_new, dist_cols_new] <= c1)
                                    other1 = np.where(np.logical_and(trees[dist_rows_new, dist_cols_new] < c5,
                                                                     trees[dist_rows_new, dist_cols_new] > c1))
                                    sav2 = np.where(woods[dist_rows_new[other1], dist_cols_new[other1]] >= c4)
                                    gras2 = np.where(woods[dist_rows_new[other1], dist_cols_new[other1]] <= c2)
                                    silvos = np.where(
                                        np.logical_and(woods[dist_rows_new[other1], dist_cols_new[other1]] < c4,
                                                       woods[dist_rows_new[other1], dist_cols_new[other1]] > c2))
                                    # reclassify
                                    cube[dist_rows_new[other1][silvos], dist_cols_new[other1][silvos], i] = 9
                                    cube[np.concatenate((dist_rows_new[sav1], dist_rows_new[other1][sav2])), np.concatenate((dist_cols_new[sav1], dist_cols_new[other1][sav2])), i] = 22
                                    cube[np.concatenate((dist_rows_new[gras1], dist_rows_new[other1][gras2])), np.concatenate((dist_cols_new[gras1], dist_cols_new[other1][gras2])), i] = 21

                                    # check how many class 20 left
                                    dist_rows_end, dist_cols_end = np.where(cube[:, :, i] == 20)  # this return the row and col numbers!
                                    # keep track of class 20 in this i
                                    res['id'].append(tile_id)
                                    res['Year_i'].append(i+1985)
                                    res['Year_j'].append(j)
                                    res['Number_start'].append(len(dist_rows_new))
                                    res['Number_into_crop'].append(-999)
                                    res['Number_into_pasture'].append(-999)
                                    res['Number_into_silvopasture'].append(len(silvos[0]))
                                    res['Number_into_grassland'].append(len(gras1[0]) + len(gras2[0]))
                                    res['Number_into_savannah'].append(len(sav1[0]) + len(sav2[0]))
                                    res['Number_end'].append(len(dist_rows_end))
                                    res['TC_silv'].append(c1)
                                    res['WC_silv'].append(c2)
                                    res['TC_sav'].append(c3)
                                    res['WC_sav'].append(c4)
                                    res['TC_sav2'].append(c5)
                                    break  # just do it once and not for every year in the search radius
                                ####################### start if not affected by end of search radius problem ###############

                                ########################## search for crop and pasture and replace
                                # find class20 in year i
                                dist_rows, dist_cols = np.where(cube[:, :,i] == 20) # this return the row and col numbers!
                                # check for pasture and crop at those locations in following (j) years
                                a = np.where(cube[dist_rows, dist_cols, i+j] == 3) # this returns the indices of dist_rows and dist_cols
                                cube[dist_rows[a], dist_cols[a], i] = 3
                                b = np.where(cube[dist_rows, dist_cols, i+j] == 4)
                                sps2 = np.where(np.logical_or(trees[dist_rows[b], dist_cols[b]] > c1, woods[dist_rows[b], dist_cols[b]] > c2))
                                cube[dist_rows[b], dist_cols[b], i] = 4
                                cube[dist_rows[sps2], dist_cols[sps2],i] = 9

                                res['id'].append(tile_id)
                                res['Year_i'].append(i+1985)
                                res['Year_j'].append(j)
                                res['Number_start'].append(len(dist_rows))
                                res['Number_into_crop'].append(len(a[0]))
                                res['Number_into_pasture'].append(len(b[0]))
                                res['Number_into_silvopasture'].append(len(sps2[0]))
                                res['Number_into_grassland'].append(-999)
                                res['Number_into_savannah'].append(-999)
                                res['Number_end'].append(len(dist_rows)-(len(a[0])+len(b[0])))
                                res['TC_silv'].append(c1)
                                res['WC_silv'].append(c2)
                                res['TC_sav'].append(c3)
                                res['WC_sav'].append(c4)
                                res['TC_sav2'].append(c5)
                            ########################## still disturbance

                            # get dist locations where conditions above (crop and pasture in following years) don't apply
                            dist_rows_new, dist_cols_new = np.where(cube[:, :,i] == 20) # this return the row and col numbers!
                            # check vegetation at these locations and implement decision tree 1 (DT1 on Miro Board Land System 2.0 Workflow)
                            sav1  = np.where(trees[dist_rows_new, dist_cols_new] >= c5) # returns the indices of the distrows/cols where condition is true
                            gras1 = np.where(trees[dist_rows_new, dist_cols_new] <= c1)
                            other1 = np.where(np.logical_and(trees[dist_rows_new, dist_cols_new] < c5,trees[dist_rows_new, dist_cols_new] > c1))
                            sav2 = np.where(woods[dist_rows_new[other1], dist_cols_new[other1]] >= c4)
                            gras2 = np.where(woods[dist_rows_new[other1], dist_cols_new[other1]] <= c2)
                            silvos = np.where(np.logical_and(woods[dist_rows_new[other1], dist_cols_new[other1]] <c4,woods[dist_rows_new[other1], dist_cols_new[other1]] > c2))

                            # reclassify
                            cube[dist_rows_new[other1][silvos], dist_cols_new[other1][silvos],i] = 9
                            cube[np.concatenate((dist_rows_new[sav1], dist_rows_new[other1][sav2])), np.concatenate((dist_cols_new[sav1], dist_cols_new[other1][sav2])),i] = 22
                            cube[np.concatenate((dist_rows_new[gras1], dist_rows_new[other1][gras2])), np.concatenate((dist_cols_new[gras1], dist_cols_new[other1][gras2])),i] = 21

                            # check how many class 20 left
                            dist_rows_end, dist_cols_end = np.where(cube[:, :,i] == 20) # this return the row and col numbers!
                            # keep track of class 20 in this i
                            res['id'].append(tile_id)
                            res['Year_i'].append(i+1985)
                            res['Year_j'].append(-999)
                            res['Number_start'].append(len(dist_rows_new))
                            res['Number_into_crop'].append(-999)
                            res['Number_into_pasture'].append(-999)
                            res['Number_into_silvopasture'].append(len(silvos[0]))
                            res['Number_into_grassland'].append(len(gras1[0])+len(gras2[0]))
                            res['Number_into_savannah'].append(len(sav1[0])+len(sav2[0]))
                            res['Number_end'].append(len(dist_rows_end))
                            res['TC_silv'].append(c1)
                            res['WC_silv'].append(c2)
                            res['TC_sav'].append(c3)
                            res['WC_sav'].append(c4)
                            res['TC_sav2'].append(c5)

                            ############################################################################
                            ######################### Savannah & Wetland Merge #########################
                            ############################################################################

                            savwet_rows, savwet_cols = np.where(np.logical_or(cube[:,:,i] == 22, cube[:,:,i] == 23))
                            wet1 = np.where(trees[savwet_rows, savwet_cols] >= c3)
                            not_wet = np.where(trees[savwet_rows, savwet_cols] < c3)
                            wet2 = np.where(woods[savwet_rows[not_wet], savwet_cols[not_wet]] >= c4)
                            sav3 = np.where(woods[savwet_rows[not_wet], savwet_cols[not_wet]] < c4)

                            cube[np.concatenate((savwet_rows[wet1],savwet_rows[not_wet][wet2])), np.concatenate((savwet_cols[wet1],savwet_cols[not_wet][wet2])),i] = 23
                            cube[savwet_rows[not_wet][sav3], savwet_cols[not_wet][sav3],i] = 22

                            res2['id'].append(tile_id)
                            res2['Year_i'].append(i+1985)
                            res2['TC_silv'].append(c1)
                            res2['WC_silv'].append(c2)
                            res2['TC_sav'].append(c3)
                            res2['WC_sav'].append(c4)
                            res2['TC_sav2'].append(c5)
                            res2['savwet_start'].append(len(savwet_rows)) # number of pixel that belong to savannah and wet gras
                            res2['wet'].append(len(wet1[0])+len(wet2[0]))
                            res2['sav'].append(len(sav3[0]))

                        ################# export without puestos
                        out_ds = gtiff_driver.Create(
                            storpath + '/Reclass_' + str(int(c1 / 100)) + '_' + str(int(c2 / 100)) + '_' + str(
                                int(c3 / 100)) + '_' + str(int(c4 / 100)) + '_' + str(
                                int(c5 / 100)) + '_Tile_' + tile_id + '.tif', ds.RasterXSize, ds.RasterYSize,
                            ds.RasterCount, ds.GetRasterBand(1).DataType)
                        out_ds.SetGeoTransform(ds.GetGeoTransform())
                        out_ds.SetProjection(ds.GetProjection())

                        for band in range(cube.shape[2]):
                            out_ds.GetRasterBand(band + 1).WriteArray(cube[:, :, band])
                        del out_ds

                        ############################################################################
                        ######################### Puestos ##########################################
                        ############################################################################

                        if os.path.isdir(storpath + '/Buffer') is False:
                            os.mkdir(storpath + '/Buffer')

                            # TURN OFF 2019 & 2020 AS LONG AS NO UPDATED PUESTOS!!!!!!!!!!!!!!!
                        for bc, buff_size in enumerate(buff_sizeL):
                                cubi = cube.copy()
                                for i in range(cube.shape[2]):
                                    res4['id'].append(tile_id)
                                    res4['Year_i'].append(i+1985)
                                    res4['buffsize'].append(buffnames[bc])
                                    res4['TC_silv'].append(c1)
                                    res4['WC_silv'].append(c2)
                                    res4['TC_sav'].append(c3)
                                    res4['WC_sav'].append(c4)
                                    res4['TC_sav2'].append(c5)
                                    # check which year I am in and the following year
                                    target_year = i+1985
                                    if target_year in [1985, 1990, 1995, 2000, 2005, 2010, 2015, 2018]:
                                        tb = gdal.Open([buff for buff in buff_size if buff.split('/')[-1].split('_')[-1].split('.')[0] == str(target_year)][0])
                                        tbuff = tb.GetRasterBand(1).ReadAsArray()
                                    elif target_year in range(1986,1990):
                                        tb = gdal.Open([buff for buff in buff_size if int(buff.split('/')[-1].split('_')[-1].split('.')[0]) == 1990][0])
                                        tbuff = tb.GetRasterBand(1).ReadAsArray()
                                    elif target_year in range(1991,1995):
                                        tb = gdal.Open([buff for buff in buff_size if buff.split('/')[-1].split('_')[-1].split('.')[0] == str(1995)][0])
                                        tbuff = tb.GetRasterBand(1).ReadAsArray()
                                    elif target_year in range(1996,2000):
                                        tb = gdal.Open([buff for buff in buff_size if buff.split('/')[-1].split('_')[-1].split('.')[0] == str(2000)][0])
                                        tbuff = tb.GetRasterBand(1).ReadAsArray()
                                    elif target_year in range(2001,2005):
                                        tb = gdal.Open([buff for buff in buff_size if buff.split('/')[-1].split('_')[-1].split('.')[0] == str(2005)][0])
                                        tbuff = tb.GetRasterBand(1).ReadAsArray()
                                    elif target_year in range(2006,2010):
                                        tb = gdal.Open([buff for buff in buff_size if buff.split('/')[-1].split('_')[-1].split('.')[0] == str(2010)][0])
                                        tbuff = tb.GetRasterBand(1).ReadAsArray()
                                    elif target_year in range(2011,2015):
                                        tb = gdal.Open([buff for buff in buff_size if buff.split('/')[-1].split('_')[-1].split('.')[0] == str(2015)][0])
                                        tbuff = tb.GetRasterBand(1).ReadAsArray()
                                    elif target_year in range(2016,2020):
                                        tb = gdal.Open([buff for buff in buff_size if buff.split('/')[-1].split('_')[-1].split('.')[0] == str(2018)][0])
                                        tbuff = tb.GetRasterBand(1).ReadAsArray()

                                    buff_rows, buff_cols = np.where(tbuff==1)
                                    inbuff1 = np.where(cubi[buff_rows, buff_cols, i] == 1)
                                    if len(inbuff1[0]) >0:
                                        cubi[buff_rows[inbuff1], buff_cols[inbuff1], i] = 15
                                        res4['class15'].append(len(inbuff1[0]))
                                        res4['tree_min_15'].append(np.nanmin(trees[buff_rows[inbuff1], buff_cols[inbuff1]]))
                                        res4['tree_max_15'].append(np.nanmax(trees[buff_rows[inbuff1], buff_cols[inbuff1]]))
                                        res4['tree_median_15'].append(np.nanmedian(trees[buff_rows[inbuff1], buff_cols[inbuff1]]))
                                        res4['tree_quant_25_15'].append(np.nanquantile(trees[buff_rows[inbuff1], buff_cols[inbuff1]],0.25))
                                        res4['tree_quant_75_15'].append(np.nanquantile(trees[buff_rows[inbuff1], buff_cols[inbuff1]],0.75))
                                        res4['shrub_min_15'].append(np.nanmin(shrubs[buff_rows[inbuff1], buff_cols[inbuff1]]))
                                        res4['shrub_max_15'].append(np.nanmax(shrubs[buff_rows[inbuff1], buff_cols[inbuff1]]))
                                        res4['shrub_median_15'].append(np.nanmedian(shrubs[buff_rows[inbuff1], buff_cols[inbuff1]]))
                                        res4['shrub_quant_25_15'].append(np.nanquantile(shrubs[buff_rows[inbuff1], buff_cols[inbuff1]],0.25))
                                        res4['shrub_quant_75_15'].append(np.nanquantile(shrubs[buff_rows[inbuff1], buff_cols[inbuff1]],0.75))
                                    else:
                                        res4['class15'].append(0)
                                        res4['tree_min_15'].append(0)
                                        res4['tree_max_15'].append(0)
                                        res4['tree_median_15'].append(0)
                                        res4['tree_quant_25_15'].append(0)
                                        res4['tree_quant_75_15'].append(0)
                                        res4['shrub_min_15'].append(0)
                                        res4['shrub_max_15'].append(0)
                                        res4['shrub_median_15'].append(0)
                                        res4['shrub_quant_25_15'].append(0)
                                        res4['shrub_quant_75_15'].append(0)
                                    inbuff21 = np.where(cubi[buff_rows, buff_cols, i] == 21)
                                    if len(inbuff21[0]) >0:
                                        cubi[buff_rows[inbuff21], buff_cols[inbuff21], i] = 16
                                        res4['class16'].append(len(inbuff21[0]))
                                        res4['tree_min_16'].append(np.nanmin(trees[buff_rows[inbuff21], buff_cols[inbuff21]]))
                                        res4['tree_max_16'].append(np.nanmax(trees[buff_rows[inbuff21], buff_cols[inbuff21]]))
                                        res4['tree_median_16'].append(np.nanmedian(trees[buff_rows[inbuff21], buff_cols[inbuff21]]))
                                        res4['tree_quant_25_16'].append(np.nanquantile(trees[buff_rows[inbuff21], buff_cols[inbuff21]],.25))
                                        res4['tree_quant_75_16'].append(np.nanquantile(trees[buff_rows[inbuff21], buff_cols[inbuff21]],.75))
                                        res4['shrub_min_16'].append(np.nanmin(shrubs[buff_rows[inbuff21], buff_cols[inbuff21]]))
                                        res4['shrub_max_16'].append(np.nanmax(shrubs[buff_rows[inbuff21], buff_cols[inbuff21]]))
                                        res4['shrub_median_16'].append(np.nanmedian(shrubs[buff_rows[inbuff21], buff_cols[inbuff21]]))
                                        res4['shrub_quant_25_16'].append(np.nanquantile(shrubs[buff_rows[inbuff21], buff_cols[inbuff21]],.25))
                                        res4['shrub_quant_75_16'].append(np.nanquantile(shrubs[buff_rows[inbuff21], buff_cols[inbuff21]],.75))
                                    else:
                                        res4['class16'].append(0)
                                        res4['tree_min_16'].append(0)
                                        res4['tree_max_16'].append(0)
                                        res4['tree_median_16'].append(0)
                                        res4['tree_quant_25_16'].append(0)
                                        res4['tree_quant_75_16'].append(0)
                                        res4['shrub_min_16'].append(0)
                                        res4['shrub_max_16'].append(0)
                                        res4['shrub_median_16'].append(0)
                                        res4['shrub_quant_25_16'].append(0)
                                        res4['shrub_quant_75_16'].append(0)
                                    inbuff22 = np.where(cubi[buff_rows, buff_cols, i] == 22)
                                    if len(inbuff22[0]) >0:
                                        cubi[buff_rows[inbuff22], buff_cols[inbuff22], i] = 17
                                        res4['class17'].append(len(inbuff22[0]))
                                        res4['tree_min_17'].append(np.nanmin(trees[buff_rows[inbuff22], buff_cols[inbuff22]]))
                                        res4['tree_max_17'].append(np.nanmax(trees[buff_rows[inbuff22], buff_cols[inbuff22]]))
                                        res4['tree_median_17'].append(np.nanmedian(trees[buff_rows[inbuff22], buff_cols[inbuff22]]))
                                        res4['tree_quant_25_17'].append(np.nanquantile(trees[buff_rows[inbuff22], buff_cols[inbuff22]],.25))
                                        res4['tree_quant_75_17'].append(np.nanquantile(trees[buff_rows[inbuff22], buff_cols[inbuff22]],.75))
                                        res4['shrub_min_17'].append(np.nanmin(shrubs[buff_rows[inbuff22], buff_cols[inbuff22]]))
                                        res4['shrub_max_17'].append(np.nanmax(shrubs[buff_rows[inbuff22], buff_cols[inbuff22]]))
                                        res4['shrub_median_17'].append(np.nanmedian(shrubs[buff_rows[inbuff22], buff_cols[inbuff22]]))
                                        res4['shrub_quant_25_17'].append(np.nanquantile(shrubs[buff_rows[inbuff22], buff_cols[inbuff22]],.25))
                                        res4['shrub_quant_75_17'].append(np.nanquantile(shrubs[buff_rows[inbuff22], buff_cols[inbuff22]],.75))
                                    else:
                                        res4['class17'].append(0)
                                        res4['tree_min_17'].append(0)
                                        res4['tree_max_17'].append(0)
                                        res4['tree_median_17'].append(0)
                                        res4['tree_quant_25_17'].append(0)
                                        res4['tree_quant_75_17'].append(0)
                                        res4['shrub_min_17'].append(0)
                                        res4['shrub_max_17'].append(0)
                                        res4['shrub_median_17'].append(0)
                                        res4['shrub_quant_25_17'].append(0)
                                        res4['shrub_quant_75_17'].append(0)
                                    inbuff23 = np.where(cubi[buff_rows, buff_cols, i] == 23)
                                    if len(inbuff23[0]) >0:
                                        cubi[buff_rows[inbuff23], buff_cols[inbuff23], i] = 18
                                        res4['class18'].append(len(inbuff23[0]))
                                        res4['tree_min_18'].append(np.nanmin(trees[buff_rows[inbuff23], buff_cols[inbuff23]]))
                                        res4['tree_max_18'].append(np.nanmax(trees[buff_rows[inbuff23], buff_cols[inbuff23]]))
                                        res4['tree_median_18'].append(np.nanmedian(trees[buff_rows[inbuff23], buff_cols[inbuff23]]))
                                        res4['tree_quant_25_18'].append(np.nanquantile(trees[buff_rows[inbuff23], buff_cols[inbuff23]],.25))
                                        res4['tree_quant_75_18'].append(np.nanquantile(trees[buff_rows[inbuff23], buff_cols[inbuff23]],.75))
                                        res4['shrub_min_18'].append(np.nanmin(shrubs[buff_rows[inbuff23], buff_cols[inbuff23]]))
                                        res4['shrub_max_18'].append(np.nanmax(shrubs[buff_rows[inbuff23], buff_cols[inbuff23]]))
                                        res4['shrub_median_18'].append(np.nanmedian(shrubs[buff_rows[inbuff23], buff_cols[inbuff23]]))
                                        res4['shrub_quant_25_18'].append(np.nanquantile(shrubs[buff_rows[inbuff23], buff_cols[inbuff23]],.25))
                                        res4['shrub_quant_75_18'].append(np.nanquantile(shrubs[buff_rows[inbuff23], buff_cols[inbuff23]],.75))
                                    else:
                                        res4['class18'].append(0)
                                        res4['tree_min_18'].append(0)
                                        res4['tree_max_18'].append(0)
                                        res4['tree_median_18'].append(0)
                                        res4['tree_quant_25_18'].append(0)
                                        res4['tree_quant_75_18'].append(0)
                                        res4['shrub_min_18'].append(0)
                                        res4['shrub_max_18'].append(0)
                                        res4['shrub_median_18'].append(0)
                                        res4['shrub_quant_25_18'].append(0)
                                        res4['shrub_quant_75_18'].append(0)

                                ### write raster stack - reclassified
                                out_ds = gtiff_driver.Create(storpath  + '/Buffer' + '/Reclass_' + str(int(c1/100)) + '_' + str(int(c2/100)) + '_' + str(int(c3/100)) + '_' + str(int(c4/100)) + '_' + str(int(c5/100)) + '_' + str(buffnames[bc]) + '_Tile_' + tile_id +'.tif', ds.RasterXSize, ds.RasterYSize, ds.RasterCount, ds.GetRasterBand(1).DataType)
                                out_ds.SetGeoTransform(ds.GetGeoTransform())
                                out_ds.SetProjection(ds.GetProjection())

                                for band in range(cube.shape[2]):
                                    out_ds.GetRasterBand(band+1).WriteArray(cubi[:,:,band])
                                del out_ds

    df  = pd.DataFrame(data = res)
    df.to_csv(csv_path + 'check20_' + tile_id + '.csv', sep=',',index=False)
    df2  = pd.DataFrame(data = res2)
    df2.to_csv(csv_path + 'wet_sav_' + tile_id + '.csv', sep=',',index=False)
    df3  = pd.DataFrame(data = res3)
    df3.to_csv(csv_path + 'silvo_' + tile_id + '.csv', sep=',',index=False)
    df4  = pd.DataFrame(data = res4)
    df4.to_csv(csv_path + 'puesto_' + tile_id + '.csv', sep=',',index=False)
    print('Tile fin')



# ######################################################################################################################
# ################################## do it parallel ####################################################################
# ######################################################################################################################

jobs = [[tc_files[i], sc_files[i], lc_files[i], ma_files[i],tc_files[i].split('/')[-1].split('_')[1]]  for i in range(len(tc_files))]

# check if tile was already processed
# csv_list = getFilelist(csv_path, '.csv')
# tiles_processed = set([csv.split('/')[-1].split('_')[-1].split('.')[0] for csv in csv_list])
# killer = []
# for k, job in enumerate(jobs):
#     if job[0].split('/')[-1].split('_')[0] in tiles_processed:
#         killer.append(k)
#
# delete_multiple_element(jobs,killer)


if __name__ == '__main__':
    # ####################################### SET TIME COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" + starttime)
    print("")

    Parallel(n_jobs=31)(delayed(disturbedRCube)(i[0], i[1], i[2], i[3], i[4]) for i in jobs)

    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start : " + starttime)
    print("end: " + endtime)
    print("")


############## make vrts with pyramids
reclassfol = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/02_Reclassification'
folder = os.listdir(reclassfol)
folder.remove('VRT')
vrts = getFilelist(reclassfol + '/VRT', '.vrt')

for fold in folder:
    if fold not in ['_'.join(vrt.split('/')[-1].split('_')[2:7]).split('.')[0] for vrt in vrts]:
        sub = getFilelist(reclassfol + '/' + fold, '.tif')
        # divide into no buffer and 3 buffsizes
        vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest', addAlpha=False)
        vrt = gdal.BuildVRT(reclassfol + '/VRT/' + 'LC_reclassified_' + fold + '.vrt', sub, options=vrt_options)
        vrt = None
        Image = gdal.Open(reclassfol + '/VRT/' + 'LC_reclassified_' + fold + '.vrt', 0) # 0 = read-only, 1 = read-write.
        gdal.SetConfigOption('COMPRESS_OVERVIEW', 'DEFLATE')
        Image.BuildOverviews("NEAREST", [2,4,8,16,32,64])
        del Image

        buffs = getFilelist(reclassfol + '/' + fold + '/Buffer', '.tif')

        for buf in [300,1500,3000]:
            sub =[buff for buff in buffs if buff.split('/')[-1].split('_')[6] == str(buf)]
            vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest', addAlpha=False)
            vrt = gdal.BuildVRT(reclassfol + '/VRT/' + 'LC_reclassified_' + fold + '_' + str(buf) + '.vrt', sub, options=vrt_options)
            vrt = None
            Image = gdal.Open(reclassfol + '/VRT/' + 'LC_reclassified_' + fold + '_' + str(buf) + '.vrt',
                              0)  # 0 = read-only, 1 = read-write.
            gdal.SetConfigOption('COMPRESS_OVERVIEW', 'DEFLATE')
            Image.BuildOverviews("NEAREST", [2, 4, 8, 16, 32, 64])
            del Image