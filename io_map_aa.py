import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date
from glob import glob
import pyresample as pr
import json
import pandas as pd
from matplotlib.dates import DateFormatter, date2num
import locale

from io_func import getColumn

minconc = '15'
cruise = 'AA'
bt_inpath = '../data/backtrajectories_AA/AA_Megan2/'

minconc = '0'
cruise = 'AA_mooring'
bt_inpath = '../data/backtrajectories_AA/AA_Lucie/'

outpath = '../io_plots/'
#bt_inpath = '../data/backtrajectories'+minconc+'/'

#Plotting
outname = 'map_backtraj'+minconc+'_'+cruise
title = 'Ice Back-trajectories'

#Set up a map plot
fig1    = plt.figure(figsize=(20,20))
ax      = fig1.add_subplot(111)
area_def = pr.utils.load_area('area.cfg', 'antarctic')  #smaller 'fram_strait' region is also avalablw
m = pr.plot.area_def2basemap(area_def, resolution='l') #resolution: c (crude), l (low), i (intermediate), h (high), f (full)
m.drawmapboundary(fill_color='#9999FF')
m.drawcoastlines()
m.fillcontinents(color='#ddaa66',lake_color='#9999FF')
##Draw parallels and meridians
m.drawparallels(np.arange(-80.,-50.,5),latmax=85.)
m.drawmeridians(np.arange(-180.,180.,20.),latmax=85.)


#Load/plot backtrajectories
infiles = glob(bt_inpath+'*.csv')
colors = plt.cm.rainbow(np.linspace(0, 1, len(infiles)))

#get the times of the first and last BT
#The filenames must have leading zeros to be sorted correctly!
#print(sorted(infiles))
start = np.asarray(getColumn(sorted(infiles)[0],0,skipheader=0),dtype=np.datetime64)[0]
end = np.asarray(getColumn(sorted(infiles)[-1],0,skipheader=0),dtype=np.datetime64)[0]
#end = np.asarray(['2020-01-31'],dtype=np.datetime64)[0]
print(start,end)
timeline = np.arange(start,end)


for i in range(0,len(infiles)):
    infile_bt = sorted(infiles)[i]
    #print(infile_bt)
    #color = next(colors)
    
    #read in the backtrajectories - with the structure:
    #2024-08-10,30.5008,81.5483
    lat_b = np.asarray(getColumn(infile_bt,2,skipheader=0),dtype=float)
    lon_b = np.asarray(getColumn(infile_bt,1,skipheader=0),dtype=float)

    xb,yb = m(lon_b,lat_b)
    ax.plot(xb,yb,lw=2,c=colors[i],alpha=.5)

    ax.plot(xb[0],yb[0],'o',c=colors[i],alpha=.5,ms=10)
    ax.plot(xb[0],yb[0],'x',c='k',alpha=1)

#cb.ax.tick_params(labelsize=20)

ax.set_title(title, fontsize=25)

plt.show()
fig1.savefig(outpath+outname,bbox_inches='tight')
#plt.close()

#timeline colorbar
N = len(timeline)
df = pd.DataFrame({
           'x': np.random.randn(N),
           'y': np.random.randn(N),
           'z': pd.date_range(start=timeline[0], periods=N, freq='D')},index=timeline)

fig, ax = plt.subplots(figsize=(10,4))

smap = ax.scatter(df.x, df.y, s=50,
                   c=[date2num(i.date()) for i in df.z], cmap=plt.cm.rainbow) # <==

fig.gca().set_visible(False)
#cb = fig.colorbar(orientation="horizontal", cax=cax)

cb = fig.colorbar(smap, orientation='horizontal',format=DateFormatter('%d %b')) # <==
cb.ax.tick_params(labelsize=20)
#cb = fig.colorbar(smap, orientation='vertical')
#cb.ax.set_yticklabels(df.index.strftime('%d %b'))

plt.show()
fig.savefig(outpath+outname+'_colorbar',bbox_inches='tight')

