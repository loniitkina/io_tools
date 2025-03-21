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
#outname = 'ts_bt_it70';bt_inpath = '../data/backtrajectories70_SIT_interp/'
outname = 'ts_bt_it_BREATHE';bt_inpath = '../data/BREATHE_BT_interp/'

fig1    = plt.figure(figsize=(20,20))
ax      = fig1.add_subplot(121)
bx      = fig1.add_subplot(122)

ax.set_title('Ice thickness by end of April', fontsize=25)
bx.set_title('Divergence', fontsize=25)

#Load/plot backtrajectories with data from Robert
infiles = glob(bt_inpath+'*.csv')
colors = plt.cm.rainbow(np.linspace(0, 1, len(infiles)))
cc=0

for i in range(1,len(infiles)+1):
    infile_bt = bt_inpath+str(i)+'.csv'
    print(infile_bt)

    #read in the backtrajectories - with the structure:
    #2024-08-10,30.5008,81.5483

    time_b = np.asarray(getColumn(infile_bt,0,skipheader=1),dtype=np.datetime64)
    lat_b = np.asarray(getColumn(infile_bt,2,skipheader=1),dtype=float)
    lon_b = np.asarray(getColumn(infile_bt,1,skipheader=1),dtype=float)
    it_b = np.asarray(getColumn(infile_bt,3,skipheader=1))
    div_b = np.asarray(getColumn(infile_bt,6,skipheader=1))
    
    it_b_filled = np.where(it_b=='','0',it_b)
    it_b_filled = np.array(it_b_filled,dtype=float)
    
    div_b_filled = np.where(div_b=='','0',div_b)
    div_b_filled = np.array(div_b_filled,dtype=float)

    #plot
    ax.plot(time_b, it_b_filled, c=colors[cc], alpha=0.5)
    bx.plot(time_b, div_b_filled, c=colors[cc], alpha=0.5)
    
    #plot iceobs thickness
    
    
    ##make some labels for every 10th BT
    #if cc in range(0,120,10):
        #print(cc)
        #try:
            #label = np.ma.array(it_b_filled, mask=it_b_filled==0).compressed()
            #label = np.nan(np.ma.masked_invalid(label).compressed()[-10:])
            #ax.plot(time_b, it_b_filled, c=colors[cc], alpha=0.3, label=np.round(label,1))
        #except:
            #print('no value')
        
        #bx.plot(time_b, snowfall, c=colors[cc], alpha=0.3, label=np.round(np.sum(snowfall),0))
    
    cc = cc + 1

ax.legend(fontsize=15)
bx.legend(fontsize=15)

ax.tick_params(labelsize=20)
bx.tick_params(labelsize=20)

ax.set_xlim(datetime(2022,10,1),datetime(2023,5,1))
bx.set_xlim(datetime(2022,10,1),datetime(2023,5,1))

fig1.autofmt_xdate()

plt.show()
fig1.savefig(outpath+outname,bbox_inches='tight')

#exit()
        
        

    
    
