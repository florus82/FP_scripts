##################################################################
######### here we tried to implement a decay function for the puesto buffers
######### so that the impact of the puesto and the vegation declines with distance
######### from puesto


from FloppyToolZL.MasterFuncs import *
gtiff_driver = gdal.GetDriverByName('GTiff')

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# load forest from 2019
lc = gdal.Open('G:/LandSystems_20/dump/tempVRT_Run12.vrt')
y2019 = lc.GetRasterBand(34).ReadAsArray()
y2019[np.where(y2019 != 1)] = 0

# load puestos
puesto = gdal.Open('P:/LandSystems_20/dump/puesto_dist_4326.tif')
puestos = puesto.GetRasterBand(1).ReadAsArray()
# conversion factors and set distance
mulfac = 111319.31946789364 # multiply  to get to 30
resol  = 0.000269494585235856 # roundabout resolution one cell corresponds to
dist   = 700
r,c = np.where(puestos > (dist/mulfac)) # find distances larger ~600m

puestos[r,c] = -999
puestos[puestos == -999] = np.nan

# linear decrease
puesto_scaled = np.interp(puestos, (np.nanmin(puestos), np.nanmax(puestos)), (1, 0))
out_arr = y2019 * puesto_scaled
# sigmoid decrease
puesto_scaled_sigmoid = sigmoid(puesto_scaled)
puesto_scaled_sigmoid_scaled = np.interp(puesto_scaled_sigmoid, (np.nanmin(puesto_scaled_sigmoid), np.nanmax(puesto_scaled_sigmoid)), (0,1))
out_arr2 = y2019 * puesto_scaled_sigmoid
out_arr3 = y2019 * puesto_scaled_sigmoid_scaled

names = ['scaled_rev', 'scaled_rev_forest', 'sigmoid_forest','sigmoid_scaled_forest']
nas = [-999,0,0,0]

for i,j in enumerate([puesto_scaled,out_arr,out_arr2,out_arr3]):
    dumm = gtiff_driver.Create('P:/LandSystems_20/dump/puesto_dist_4326_650_' + names[i] + '.tif', puestos.shape[1], puestos.shape[0], 1, gdal.GDT_Float32)
    dumm.SetGeoTransform(puesto.GetGeoTransform())
    dumm.SetProjection(puesto.GetProjection())
    band = dumm.GetRasterBand(1)
    band.SetNoDataValue(-999)
    band.WriteArray(j)
    del dumm


