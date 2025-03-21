import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date
from glob import glob
import pyresample as pr
import json
import pandas as pd

from io_func import getColumn

minconc = '50'
minconc = '70'

cruise = 'ArcticOcean2024'
#cruise = 'BREATHE'
months_after_freezeup=9

outpath = '../io_plots/'
outpath_data = '../data/'
bt_inpath = '../data/backtrajectories'+minconc+'/'
#bt_inpath = '../data/backtrajectories50_BREATHE/'

ib_inpath = '../data/icebird_tracks/'

#SIMS data
infile_sims = '../data/SIMS/SIMSJul2024AllData/AllData_comma.csv'    #ArcticOcean2024

#CS2SMOS data
inpath_cs2 = '../data/CS2SMOS/'
infile_cs2 = 'W_XX-ESA,SMOS_CS2,NH_25KM_EASE2_20240409_20240415_r_v206_01_l4sit.nc'

# Opening JSON file with iceobs
infile = glob('../data/*13.json')[0]    #ArcticOcean2024
#infile = glob('../data/*30_clean.json')[0]    #BREATHE2023
print(infile)
f = open(infile)

# returns JSON object as a dictionary
data = json.load(f)

lat=[]
lon=[]
time=[]
it_eff=[]
it_rea=[]

# Iterating through the json
for i in data['observations']:
    #print(i); exit()
    llat=i['latitude']
    llon=i['longitude']
    ltime=i['observed_at']
    
    if llat==None: llat=0
    if llon==None: llon=0
    if ltime==None: ltime='0000-00-00T00:00:00.000Z'
    
    lat.append(llat)
    lon.append(llon)
    time.append(ltime)
    
    ic = i['ice']['total_concentration']
    
    #estimate of mean ice thickness
    pc1=(i['ice_observations'][0]['partial_concentration'])
    it1=(i['ice_observations'][0]['thickness'])
    
    pc2=(i['ice_observations'][1]['partial_concentration'])
    it2=(i['ice_observations'][1]['thickness'])
    
    pc3=(i['ice_observations'][2]['partial_concentration'])
    it3=(i['ice_observations'][2]['thickness'])
    
    if pc1==None: 
        pc1=0;it1=0
    if pc2==None: 
        pc2=0;it2=0
    if pc3==None: 
        pc3=0;it3=0
    
    #often brash has no thickness
    if it3==None: it3=20
    if it2==None: it2=20
    if it1==None: it1=20
    
    #print(ic,pc1,it1,pc2,it2,pc3,it3)
    #print(ltime)
    
    #convert to fraction
    pc1=pc1/10;pc2=pc2/10;pc3=pc3/10
        
    tmp = it1*pc1+it2*pc2+it3*pc3
    tmp = tmp/100   #convert to m
    
    print(ic,pc1,it1,pc2,it2,tmp)
    
    #effective sea ice thickness (mean with open water)
    it_eff.append(tmp)
    
    #real sea ice thickness (mean thickness without the open water)
    #scale pc to reach 100%
    pc=pc1+pc2+pc3
    if pc>0:
        pc1=pc1/pc; pc2=pc2/pc; pc3=pc3/pc
        tmp = it1*pc1+it2*pc2+it3*pc3
        tmp = tmp/100   #convert to m
        it_rea.append(tmp)
    else:
        it_rea.append(0)

# Closing file
f.close()

#Get SIMS ice thickness
time_sims = getColumn(infile_sims,0,skipheader=1)
dt = [ datetime.strptime(time_sims[x], "%Y-%m-%d %H:%M:%S") for x in range(len(time_sims)) ]

lat_sims = np.asarray(getColumn(infile_sims,1,skipheader=1,delimiter=','),dtype=float)
lon_sims = np.asarray(getColumn(infile_sims,2,skipheader=1,delimiter=','),dtype=float)
it_sims = np.asarray(getColumn(infile_sims,9,skipheader=1,delimiter=','),dtype=float)

#Make 3-hourly means and 90 and 95 percentils
pos = {'lat': lat_sims,
       'lon': lon_sims,
       'it': it_sims}

df = pd.DataFrame(data=pos,index=dt)
means = df.resample('3H').mean()

def custom_resampler(array,p):
    return (np.percentile(array,p))

p66 = df.resample('3H').apply(custom_resampler,66)
p75 = df.resample('3H').apply(custom_resampler,75)

#keep values
lat_sims = means.lat.values
lon_sims = means.lon.values
it_sims = means.it.values
dates = means.index.values

it_sims_p66 = p66.it.values
it_sims_p75 = p75.it.values

##convert back to datetime list
#dt = dates.astype('O')
#dt = [ datetime.utcfromtimestamp(x/1e9) for x in dt ]

#CS2/SMOS winter data
#downloaded from  ftp.awi.de/sea_ice/product/cryosat2_smos/v206/nh/2024/04
#den folgenden Satz in die Danksagung mitaufnehmen (Daten entsprechend der Nutzung einsetzen): Das kombinierte Prozessieren der CryoSat-2 und SMOS Daten wurde gefördert im Rahmen des ESA Projektes SMOS & CryoSat-2 Sea Ice Data Product Processing and Dissemination Service und Daten von DATUM bis DATUM stammen von https://www.meereisportal.de (Förderung: REKLIM-2013-04).
#zitieren: Ricker, R.; Hendricks, S.; Kaleschke, L.; Tian-Kunze, X.; King, J. and Haas, C. (2017), A weekly Arctic sea-ice thickness data record from merged CryoSat-2 and SMOS satellite data, The Cryosphere, 11, 1607-1623, doi:10.5194/tc-11-1607-2017 (PDF).
from netCDF4 import Dataset
fnames = sorted(glob(inpath_cs2+infile_cs2))
f = Dataset(fnames[0])
lat_cs2 = f.variables['lat'][:]
lon_cs2 = f.variables['lon'][:]
it_cs2 = f.variables['analysis_sea_ice_thickness'][0,:,:]   #his time dimension, currently only one

#Plotting
outname = 'map_iceobs_SIMS_thickness'+minconc+'_'+cruise
title = 'Ice Thickness (m)'
cm = plt.cm.rainbow
vmin = 0
vmax = 2

#Set up a map plot
fig1    = plt.figure(figsize=(20,20))

#MEANS
ax      = fig1.add_subplot(131)
area_def = pr.utils.load_area('area.cfg', 'fram_strait')  #smaller 'fram_strait' region is also avalable
m = pr.plot.area_def2basemap(area_def, resolution='l') #resolution: c (crude), l (low), i (intermediate), h (high), f (full)
m.drawmapboundary(fill_color='#9999FF')
m.drawcoastlines()
m.fillcontinents(color='#ddaa66',lake_color='#9999FF')
##Draw parallels and meridians
m.drawparallels(np.arange(60.,86.,5),latmax=85.)
m.drawmeridians(np.arange(-180.,180.,20.),latmax=85.)

#plot CS2 data 
x,y = m(lon_cs2,lat_cs2)
cs = ax.pcolor(x,y,it_cs2-1,cmap=cm,vmin=vmin,vmax=vmax)    #remove some thickness, this is April data!

#plot ice obs data
x,y = m(lon,lat)

#Plot the iceobs
ax.plot(x,y,'.',c='k',ms=1)
cs=ax.scatter(x,y,c=it_eff,s=60,cmap=cm,vmin=vmin,vmax=vmax,ec='k')
from mpl_toolkits.axes_grid1 import make_axes_locatable
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
cb=plt.colorbar(cs, cax=cax)

#plot SIMS data
x,y = m(lon_sims,lat_sims)
ax.scatter(x,y,c=it_sims,s=60,cmap=cm,vmin=vmin,vmax=vmax,ec='k')

cb.ax.tick_params(labelsize=20)
ax.set_title(title+' eff/means', fontsize=25)

#P90 
bx      = fig1.add_subplot(132)
area_def = pr.utils.load_area('area.cfg', 'fram_strait')  #smaller 'fram_strait' region is also avalable
m = pr.plot.area_def2basemap(area_def, resolution='l') #resolution: c (crude), l (low), i (intermediate), h (high), f (full)
m.drawmapboundary(fill_color='#9999FF')
m.drawcoastlines()
m.fillcontinents(color='#ddaa66',lake_color='#9999FF')
##Draw parallels and meridians
m.drawparallels(np.arange(60.,86.,5),latmax=85.)
m.drawmeridians(np.arange(-180.,180.,20.),latmax=85.)

#plot CS2 data 
x,y = m(lon_cs2,lat_cs2)
cs = bx.pcolor(x,y,it_cs2-1,cmap=cm,vmin=vmin,vmax=vmax)

#plot ice obs data
x,y = m(lon,lat)

#Plot the iceobs
bx.plot(x,y,'.',c='k',ms=1)
cs=bx.scatter(x,y,c=it_rea,s=60,cmap=cm,vmin=vmin,vmax=vmax,ec='k')
divider = make_axes_locatable(bx)
cax = divider.append_axes("right", size="5%", pad=0.05)
cb=plt.colorbar(cs, cax=cax)

#plot SIMS data
x,y = m(lon_sims,lat_sims)
bx.scatter(x,y,c=it_sims_p66,s=60,cmap=cm,vmin=vmin,vmax=vmax,ec='k')

cb.ax.tick_params(labelsize=20)
bx.set_title(title+' real/P66', fontsize=25)

#P95 
cx      = fig1.add_subplot(133)
area_def = pr.utils.load_area('area.cfg', 'fram_strait')  #smaller 'fram_strait' region is also avalable
m = pr.plot.area_def2basemap(area_def, resolution='l') #resolution: c (crude), l (low), i (intermediate), h (high), f (full)
m.drawmapboundary(fill_color='#9999FF')
m.drawcoastlines()
m.fillcontinents(color='#ddaa66',lake_color='#9999FF')
##Draw parallels and meridians
m.drawparallels(np.arange(60.,86.,5),latmax=85.)
m.drawmeridians(np.arange(-180.,180.,20.),latmax=85.)

#plot CS2 data 
x,y = m(lon_cs2,lat_cs2)
cs = cx.pcolor(x,y,it_cs2-1,cmap=cm,vmin=vmin,vmax=vmax)

#plot ice obs data
x,y = m(lon,lat)

#Plot the iceobs
cx.plot(x,y,'.',c='k',ms=1)
cs=cx.scatter(x,y,c=it_rea,s=60,cmap=cm,vmin=vmin,vmax=vmax,ec='k')
divider = make_axes_locatable(cx)
cax = divider.append_axes("right", size="5%", pad=0.05)
cb=plt.colorbar(cs, cax=cax)

#plot SIMS data
x,y = m(lon_sims,lat_sims)
cx.scatter(x,y,c=it_sims_p75,s=60,cmap=cm,vmin=vmin,vmax=vmax,ec='k')

cb.ax.tick_params(labelsize=20)
cx.set_title(title+' real/P75', fontsize=25)

plt.show()
fig1.savefig(outpath+outname,bbox_inches='tight')
plt.close()


