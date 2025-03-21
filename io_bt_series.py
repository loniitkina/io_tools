import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date
from glob import glob
import xarray as xr
from pyproj import Proj, transform

from io_func import getColumn

#plot temperature and other time series along the back-trajectories
outpath = '../io_plots/'
#outname = 'ts_bt_temperature50';bt_inpath = '../data/backtrajectories50/'
#outname = 'ts_bt_temperature70';bt_inpath = '../data/backtrajectories70/'
outname = 'ts_bt_temperature_BREATHE';bt_inpath = '../data/backtrajectories50_BREATHE/'

fig1    = plt.figure(figsize=(20,20))
ax      = fig1.add_subplot(121)
bx      = fig1.add_subplot(122)

ax.set_title('Mean temperature (C)', fontsize=25)
bx.set_title('Accumulated snowfall (cm)', fontsize=25)

#for data like precipitation, different script has to be written when the hourly precipitation is accummulated to daily totals or similar

#load the ERA-5 data
ds_temperature = xr.open_dataset('../data/ERA-5_temperatures2022-2024.nc')
ds_snowfall = xr.open_dataset('../data/ERA-5_snowfall.nc')
#print(ds_snowfall)

#Load/plot backtrajectories
infiles = glob(bt_inpath+'*.csv')
colors = plt.cm.rainbow(np.linspace(0, 1, len(infiles)))
cc=0

for num in range(1,len(infiles)):
    infile_bt = bt_inpath+str(num)+'.csv'
    print(infile_bt)
    
    time=[]
    temperature=[]
    snowfall=[]

    #read in the backtrajectories - with the structure:
    #2024-08-10,30.5008,81.5483

    time_b = np.asarray(getColumn(infile_bt,0,skipheader=0),dtype=np.datetime64)
    lat_b = np.asarray(getColumn(infile_bt,2,skipheader=0),dtype=float)
    lon_b = np.asarray(getColumn(infile_bt,1,skipheader=0),dtype=float)

    #search for the nearest neighbor
    for i in range(0,len(time_b)):
        
        #get only data until December 2023
        if time_b[i] > np.datetime64('2022-08-31'):
        
            tt = ds_temperature.t2m.sel(valid_time=time_b[i], latitude=lat_b[i], longitude=lon_b[i],method='nearest')
            
            sf = ds_snowfall.sf.sel(valid_time=time_b[i], latitude=lat_b[i], longitude=lon_b[i],method='nearest')
            
            time.append(time_b[i])
            temperature.append(tt.values-273.15)
            snowfall.append(sf.values*24*100)  #m of SWE accummulated over 1 hour - lets assume all 24 had same SWE accumulation, convert to cm

    #plot
    ax.plot(time, temperature, c=colors[cc], alpha=0.1)
    
    bx.plot(time, snowfall, c=colors[cc], alpha=0.1)
    
    #make mean for every 10th BT
    if cc in range(0,len(infiles),10):
        print(cc)
        ax.plot(time, temperature, c=colors[cc], alpha=0.1, label=np.round(np.mean(temperature),1))
        
        bx.plot(time, snowfall, c=colors[cc], alpha=0.1, label=np.round(np.sum(snowfall),0))
    
    cc = cc + 1

ax.legend(fontsize=15)
bx.legend(fontsize=15)

ax.tick_params(labelsize=20)
bx.tick_params(labelsize=20)

fig1.autofmt_xdate()

plt.show()
fig1.savefig(outpath+outname,bbox_inches='tight')

#exit()
        
        

    
    
