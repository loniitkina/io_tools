import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date
from glob import glob
import xarray as xr
from pyproj import Proj, transform

from io_func import getColumn

#plot temperature and other time series along the back-trajectories
outpath = '../io_plots/'
outname = 'ts_bt_temperature'

fig1    = plt.figure(figsize=(20,20))
ax      = fig1.add_subplot(111)

#for data like precipitation, different script has to be written when the hourly precipitation is accummulated to daily totals or similar

#load the ERA-5 data
ds = xr.open_dataset('../data/ERA-5_temperatures.nc')
#print(ds)

#Load/plot backtrajectories
infiles = glob('../data/backtrajectories/*.csv')
colors = plt.cm.rainbow(np.linspace(0, 1, 108))
cc=0

for num in range(1,108):
    infile_bt = '../data/backtrajectories/'+str(num)+'.csv'
    print(infile_bt)
    
    time=[]
    temperature=[]
    
    try:
        #read in the backtrajectories - with the structure:
        #2024-08-10,30.5008,81.5483

        time_b = np.asarray(getColumn(infile_bt,0,skipheader=0),dtype=np.datetime64)
        lat_b = np.asarray(getColumn(infile_bt,2,skipheader=0),dtype=float)
        lon_b = np.asarray(getColumn(infile_bt,1,skipheader=0),dtype=float)

        #search for the nearest neighbor
        for i in range(0,len(time_b)):
            tt = ds.t2m.sel(valid_time=time_b[i], latitude=lat_b[i], longitude=lon_b[i],method='nearest')
            
            time.append(time_b[i])
            temperature.append(tt.values-273.15)

    except:
        print('No BT.')            
            

    #plot
    ax.plot(time, temperature, c=colors[cc], alpha=0.5)
    cc = cc + 1
  
plt.show()
fig1.savefig(outpath+outname,bbox_inches='tight')

#exit()
        
        

    
    
