

###############################################################################################
############## this script takes maps and cuts them into tiles that match the ones from
############## Matthias's landcover product. This might be needed, as script "01_Reclassify" does the reclassifcation under
############## different parameter settings in parallel, where one tile with one parameter setting is treated as one thread


from FloppyToolZL.MasterFuncs import *
drvMemR = gdal.GetDriverByName('MEM')
gtiff_driver = gdal.GetDriverByName('GTiff')


tilespath = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/LandCover/Run12/output_LandCover'
tiles = getFilelist(tilespath, '.tif')

trees = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/temp/TC_comp_reprojed.tif'
shrubs = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/Florian/temp/SC_comp_reprojed.tif'

tree_stor = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/TreeShrubCover/2019/TC/'
shrub_stor = 'M:/_PROJECTS/_ERC-SystemShift_LandSystem_Mapping/TreeShrubCover/2019/SC/'

trees = gdal.Open(trees)
trees_band = trees.GetRasterBand(1)
in_gt = trees.GetGeoTransform()
inv_gt = gdal.InvGeoTransform(in_gt)

for tile in tiles:

    til = gdal.Open(tile, 0)

    common = commonBoundsCoord(commonBoundsDim([getExtentRas(trees), getExtentRas(til)]))[0]

    # transform coordinates into offsets (in cells) and make them integer
    off_UpperLeft = gdal.ApplyGeoTransform(inv_gt, common['UpperLeftXY'][0],common['UpperLeftXY'][1])
    off_LowerRight = gdal.ApplyGeoTransform(inv_gt, common['LowerRightXY'][0], common['LowerRightXY'][1])
    off_ULx, off_ULy = map(round, off_UpperLeft)  # or int????????????????
    off_LRx, off_LRy = map(round, off_LowerRight)

    data = trees_band.ReadAsArray(off_ULx, off_ULy, off_LRx - off_ULx, off_LRy - off_ULy)

    sb = gtiff_driver.Create(tree_stor + '_'.join(tile.split('/')[-1].split('_')[0:2]) + '_TC_2019.tif', til.RasterXSize, til.RasterYSize, 1, gdal.GDT_Float32)
    sb.SetGeoTransform(til.GetGeoTransform())
    sb.SetProjection(til.GetProjection())
    sb.GetRasterBand(1).WriteArray(data)
    # sb.GetRasterBand(1).SetNoDataValue(0)
    del sb


shrub = gdal.Open(shrubs)
shrubs_band = shrub.GetRasterBand(1)
in_gt = shrub.GetGeoTransform()
inv_gt = gdal.InvGeoTransform(in_gt)

for tile in tiles:

    til = gdal.Open(tile, 0)

    common = commonBoundsCoord(commonBoundsDim([getExtentRas(shrub), getExtentRas(til)]))[0]

    # transform coordinates into offsets (in cells) and make them integer
    off_UpperLeft = gdal.ApplyGeoTransform(inv_gt, common['UpperLeftXY'][0],common['UpperLeftXY'][1])
    off_LowerRight = gdal.ApplyGeoTransform(inv_gt, common['LowerRightXY'][0], common['LowerRightXY'][1])
    off_ULx, off_ULy = map(round, off_UpperLeft)  # or int????????????????
    off_LRx, off_LRy = map(round, off_LowerRight)

    data = shrubs_band.ReadAsArray(off_ULx, off_ULy, off_LRx - off_ULx, off_LRy - off_ULy)

    sb = gtiff_driver.Create(shrub_stor + '_'.join(tile.split('/')[-1].split('_')[0:2]) + '_SC_2019.tif', til.RasterXSize, til.RasterYSize, 1, gdal.GDT_Float32)
    sb.SetGeoTransform(til.GetGeoTransform())
    sb.SetProjection(til.GetProjection())
    sb.GetRasterBand(1).WriteArray(data)
    # sb.GetRasterBand(1).SetNoDataValue(0)
    del sb
