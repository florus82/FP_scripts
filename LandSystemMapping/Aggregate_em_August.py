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

# exportArrys is used to export aggregated numpy areas to disc
def exportArray(origin_ds, type_origin, out_arr, agg_fac, cols, rows, bands, storpath):
    out_dss = gtiff_driver.Create(storpath,
                                  cols, rows, bands, type_origin.GetRasterBand(1).DataType)
    win_gt = origin_ds.GetGeoTransform()
    out_gt = [win_gt[0], win_gt[1] * agg_fac, win_gt[2], win_gt[3], win_gt[4], win_gt[5] * agg_fac]
    out_dss.SetGeoTransform(out_gt)
    out_dss.SetProjection(origin_ds.GetProjection())
    if bands > 1:
        for band in range(bands):
            out_dss.GetRasterBand(band + 1).WriteArray(out_arr[:, :, band])
            out_dss.GetRasterBand(band + 1).SetNoDataValue(-999)
    else:
        out_dss.GetRasterBand(1).WriteArray(out_arr)
        out_dss.GetRasterBand(1).SetNoDataValue(-999)
    del out_dss
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

########## paths
aggregpath = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/01_Aggregations' # mother folder
reclassfol = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/02_Reclassification'
trash = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/temp' # temp folder
treepath = 'K:/BackUP/NAS_BIOGEO/dump/TC_comp.vrt' # Trees 2019
shrubpath = 'K:/BackUP/NAS_BIOGEO/dump/SC_comp.vrt' # Shrubs 2019

########## parameter
aggfacs = [10, 50, 100] # landsatpixel * aggfacs[x] = 300,1500,3000m --> final resolution of land systems map
gtiff_driver = gdal.GetDriverByName('GTiff')
os.environ['PROJ_LIB'] = 'C:/ProgramData/Anaconda3/envs/pythonProject2/Library/share/proj'
os.environ['GDAL_DATA'] = 'C:/ProgramData/Anaconda3/envs/pythonProject2/Library/share/gdal'


# ## open reclassified vrt and get dimensions and coord/proj
combi = '12_20_20_30_18_1500'
ds = gdal.Open(reclassfol + '/VRT' + '/LC_reclassified_' + combi + '.vrt')
nbands = ds.RasterCount
lc_classes = np.asarray([1, 21, 22, 23, 3, 4, 5, 15, 16, 17, 18, 9]) # 1=forest, 21=naturalGrasslands, 22=savannas, 23=wetGrasslands; 20=deforestation, 3=crop, 4=pasture, 5=other , 15, = puesto degraded forest, 16 = puesto degraded natural grassland, 17 = puesto degraded savanna, 18 = puesto degraded wetgrasslands, 9=silvos])
lc_names = ['F', 'NatGras', 'Sav', 'WetGras', 'C', 'P', 'OV', 'Pdeg_F', 'Pdeg_NatGras', 'Pdeg_Sav', 'Pdeg_WetGras','SP']
cl = ds.RasterXSize
rw = ds.RasterYSize

gt = ds.GetGeoTransform()
pr = ds.GetProjection()

# load trees and shrubs for aggregation in upcoming loop
trees_ds = gdal.Open(trash + '/' + treepath.split('/')[-1].split('.')[0] + '_reprojed.tif')
trees = trees_ds.GetRasterBand(1).ReadAsArray()

shrubs_ds = gdal.Open(trash + '/' + shrubpath.split('/')[-1].split('.')[0] + '_reprojed.tif')
shrubs = shrubs_ds.GetRasterBand(1).ReadAsArray()
# calc woody cover
woods = shrubs + trees

####################################################
######## get dimensions for aggregations ###########
########## aggregate tree & wood cover #############
####################################################

# create lists to hold output array dimensions and arrays for lcprops
cols = []
rows = []
newCols = []
newRows = []
out_arr_lc_list = []

# calculate new dimensions of aggregated outputs for all aggregation level and export aggregated tree and wood cover
for subcount, aggfac in enumerate(aggfacs):

    ## get dimension for aggregated output raster
    cols.append(aggfac * (math.floor(cl/aggfac)))
    rows.append(aggfac * (math.floor(rw/aggfac)))
    newCols.append(int(cols[subcount]/aggfac))
    newRows.append(int(rows[subcount]/aggfac))

    # create output geo-transform for output raster
    # out_gt = [gt[0], float(gt[1])*aggfac, gt[2], gt[3], gt[4], float(gt[5])*aggfac]

    ## create output arrays for tc and wc aggregations
    out_arr_lc_list.append(np.zeros((newRows[subcount], newCols[subcount], len(lc_classes)*nbands), dtype=np.uint16)) # needed right at the end

    # check first if tree and wood cover already aggregated
    if os.path.isfile(aggregpath + '/TreeCover/' + str(aggfac * 30) + '/TC_aggregeated_to_' + str(aggfac * 30) + '.tif'):
        print('tree & wood cover already aggregated to this level')

    else:
        if not os.path.exists(aggregpath + '/TreeCover'):
            os.mkdir(aggregpath + '/TreeCover')
        if not os.path.exists(aggregpath + '/WoodyCover'):
            os.mkdir(aggregpath + '/WoodyCover')
        out_arr_tc = np.zeros((newRows[subcount], newCols[subcount], 1), dtype=np.uint16)
        out_arr_wc = np.zeros((newRows[subcount], newCols[subcount], 1), dtype=np.uint16)

        # aggreate tree & shrubs and & calculate woody cover
        shrub_agg = shrubs[0:rows[subcount], 0:cols[subcount]].reshape(newRows[subcount], aggfac, newCols[subcount], aggfac).mean(axis=(1,3))
        tree_agg = trees[0:rows[subcount], 0:cols[subcount]].reshape(newRows[subcount], aggfac, newCols[subcount], aggfac).mean(axis=(1,3))
        wood_agg = woods[0:rows[subcount], 0:cols[subcount]].reshape(newRows[subcount], aggfac, newCols[subcount], aggfac).mean(axis=(1,3))

        # export TC and WC
        if not os.path.exists(aggregpath + '/TreeCover/' + str(aggfac * 30)):
            os.mkdir(aggregpath + '/TreeCover/' + str(aggfac * 30))
        exportArray(ds, trees_ds, tree_agg, aggfac, newCols[subcount], newRows[subcount], 1, aggregpath + '/TreeCover/' + str(aggfac * 30) + '/TC_aggregeated_to_' + str(aggfac * 30) + '.tif')
        if not os.path.exists(aggregpath + '/WoodyCover/' + str(aggfac * 30)):
            os.mkdir(aggregpath + '/WoodyCover/' + str(aggfac * 30))
        exportArray(ds, trees_ds, wood_agg, aggfac, newCols[subcount], newRows[subcount], 1, aggregpath + '/WoodyCover/' + str(aggfac * 30) + '/WC_aggregeated_to_' + str(aggfac * 30) + '.tif')


#########################################
######## aggregate land cover ###########
#########################################
bandcount = 0
print('Loop over bands starts :)')
for bandcount in range(nbands):
    print(bandcount)
    print('-------------------------------------------------------')
    print('Band: ' + str(bandcount+1))
    start = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print('Read-in starts at: ' + str(start))
    bandx = ds.GetRasterBand(bandcount+1).ReadAsArray()
    start = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print('Read-in finished at: ' + str(start))

    # loop over aggregations
    print('Loop over aggregations starts :)')
    # aggcount = 1
    # aggfac = aggfacs[aggcount]
    # counti = 3
    # lc = lc_classes[counti]
    for aggcount, aggfac in enumerate(aggfacs):
        print('Current aggregation factor: ' + str(aggfac))

        # loop over lc class and populate output array
        print('looping over lc classes')
        for counti, lc in enumerate(lc_classes):
            print('masking band for class: ' + str(lc))
            bandx_ma = np.ma.masked_where(bandx != lc, bandx)
            print('aggregating class')
            compr = bandx_ma[0:rows[aggcount], 0:cols[aggcount]].reshape(newRows[aggcount], aggfac, newCols[aggcount], aggfac).sum(axis=(1,3))
            compr2 = np.asarray(((compr / lc) / aggfac**2)*100, dtype=np.uint) # convert to percent
            out_arr_lc_list[aggcount][:,:,counti + (bandcount * len(lc_classes))] = compr2

# # check only
# for bandcount in range(nbands):
#     for counti, lc in enumerate(np.append(lc_classes,9)):
#         print(counti + (bandcount * (len(lc_classes)+1)))


###########################
######## exoprt ###########
###########################

for aggcount, aggfac in enumerate(aggfacs):
    # check if folder for aggregation level exist and create if not
    if not os.path.exists(aggregpath + '/LandCover/one_stack/' + str(aggfac * 30)):
       os.mkdir(aggregpath + '/LandCover/one_stack/' + str(aggfac * 30))
    # check if old raster version exists and delete first
    RasterKiller(aggregpath + '/LandCover/one_stack/' + str(aggfac * 30) + '/' + combi + '/lc_props_' + str(aggfac * 30) + '.tif')

    if not os.path.exists(aggregpath + '/LandCover/one_stack/' + str(aggfac * 30) + '/' + combi):
        os.mkdir(aggregpath + '/LandCover/one_stack/' + str(aggfac * 30) + '/' + combi)
    # export lc_props stack  at respective aggfac
    exportArray(ds, trees_ds, out_arr_lc_list[aggcount], aggfac, newCols[aggcount], newRows[aggcount], nbands * len(lc_classes),
                aggregpath + '/LandCover/one_stack/' + str(aggfac * 30) + '/' + combi + '/lc_props_' + combi + '_agg_' + str(aggfac * 30) + '.tif')

    # export lc prop stacks for matthias
    for counti, lc in enumerate(lc_classes):
        # check if folder for aggregation level exist and create if not
        if not os.path.exists(aggregpath + '/LandCover/stacks_by_class/' + str(aggfac * 30)):
            os.mkdir(aggregpath + '/LandCover/stacks_by_class/' + str(aggfac * 30))
        # check if old raster version exists and delete first
        RasterKiller(aggregpath + '/LandCover/stacks_by_class/' + str(aggfac * 30) + '/' + combi + '/lc_props_' + combi + '_agg_' + str(aggfac * 30) + '_' + lc_names[counti] + '.tif')

        if not os.path.exists(aggregpath + '/LandCover/stacks_by_class/' + str(aggfac * 30) + '/' + combi):
            os.mkdir(aggregpath + '/LandCover/stacks_by_class/' + str(aggfac * 30) + '/' + combi)

        grab_bands = [i for i in range(counti, len(lc_classes) * nbands, len(lc_classes))]
        exportArray(ds, trees_ds, out_arr_lc_list[aggcount][:,:,grab_bands], aggfac, newCols[aggcount], newRows[aggcount],
                    nbands, aggregpath + '/LandCover/stacks_by_class/' + str(aggfac * 30) + '/' + combi + '/lc_props_' + combi + '_agg_' + str(aggfac * 30) + '_' + lc_names[counti] + '.tif')