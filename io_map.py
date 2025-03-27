import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date
from glob import glob
import pyresample as pr
import json

from io_func import getColumn

minconc = '50'
minconc = '70'
minconc = '15'

cruise = 'BREATHE';months_after_freezeup=9
cruise = 'ICEX2024';months_after_freezeup=6


outpath = '../io_plots/'
outpath_data = '../data/'
bt_inpath = '../data/backtrajectories'+minconc+'/'
bt_inpath = '../data/backtrajectories50_BREATHE/'
bt_inpath = '../data/ICEX2024/BT/'

ib_inpath = '../data/icebird_tracks/'

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
iconc=[]
it=[]
algae=[]
sedim=[]

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
    iconc.append(ic)
    
    #estimate of mean ice thickness
    pc1=(i['ice_observations'][0]['partial_concentration'])
    it1=(i['ice_observations'][0]['thickness'])
    
    pc2=(i['ice_observations'][1]['partial_concentration'])
    it2=(i['ice_observations'][1]['thickness'])
    
    print(ic,pc1,it1,pc2,pc2)
    
    if it2==None:
        tmp=it1
    else:
        tmp = (it1*pc1+it2*pc2)/ic
    
    it.append(tmp)
    
    #estimate of mean algae concentration
    ac1=(i['ice_observations'][0]['algae_density_lookup_code'])
    #print(ac1)
    if ac1==None: ac1=0
    
    ac2=(i['ice_observations'][1]['algae_density_lookup_code'])
    if ac2==None: ac2=0
    
    if pc2==None:
        tmp=ac1
    else:
        tmp = (ac1*pc1+ac2*pc2)/ic
    
    algae.append(tmp)
    
    #estimate of mean sediment concentration
    s1=(i['ice_observations'][0]['sediment_lookup_code'])
    if s1==None: s1=0
    
    s2=(i['ice_observations'][1]['sediment_lookup_code'])
    if s2==None: s2=0
    
    if pc2==None:
        tmp=s1
    else:
        tmp = (s1*pc1+s2*pc2)/ic
    
    sedim.append(tmp)

# Closing file
f.close()

#Plotting
outnames = ['map_iceobs_concentration'+minconc+'_'+cruise, 'map_iceobs_thickness'+minconc+'_'+cruise, 'map_iceobs_algae'+minconc+'_'+cruise, 'map_iceobs_sediment'+minconc+'_'+cruise]
titles = ['Ice Concentration (0-10)', 'Ice Thickness (cm)', 'Ice algae concentration', 'Ice sediment concentration']
datas = [iconc, it, algae, sedim]
cms = [plt.cm.Reds, plt.cm.Reds, plt.cm.Greens, plt.cm.Blues]
vmins = [1,50, 0, 0]
vmaxs = [10, 150, 1, 1]

for i in range(0,len(outnames)):
    outname = outnames[i]
    title = titles[i]
    data = datas[i]
    cm = cms[i]
    vmin = vmins[i]
    vmax = vmaxs[i]

    #Set up a map plot
    fig1    = plt.figure(figsize=(20,20))
    ax      = fig1.add_subplot(111)
    area_def = pr.utils.load_area('area.cfg', 'arctic')  #smaller 'fram_strait' region is also avalablw
    m = pr.plot.area_def2basemap(area_def, resolution='l') #resolution: c (crude), l (low), i (intermediate), h (high), f (full)
    m.drawmapboundary(fill_color='#9999FF')
    m.drawcoastlines()
    m.fillcontinents(color='#ddaa66',lake_color='#9999FF')
    ##Draw parallels and meridians
    m.drawparallels(np.arange(60.,86.,5),latmax=85.)
    m.drawmeridians(np.arange(-180.,180.,20.),latmax=85.)
    
    #Load/plot backtrajectories
    infiles = glob(bt_inpath+'*.csv')
    colors = plt.cm.rainbow(np.linspace(0, 1, len(infiles)+1))
    
    for j in range(1,len(infiles)+1):
        infile_bt = bt_inpath+str(j)+'.csv'
        print(infile_bt)
        #color = next(colors)
        
        #try:
        #read in the backtrajectories - with the structure:
        #2024-08-10,30.5008,81.5483
        lat_b = np.asarray(getColumn(infile_bt,2,skipheader=0),dtype=float)
        lon_b = np.asarray(getColumn(infile_bt,1,skipheader=0),dtype=float)
        
        

        xb,yb = m(lon_b,lat_b)
        ax.plot(xb,yb,lw=3,c=colors[j],alpha=.5)
        
        ax.plot(xb[0],yb[0],'o',c=colors[j],alpha=.5,ms=10)
        ax.plot(xb[0],yb[0],'x',c='k',alpha=1)

        
        #separate between FYI and SYI/MYI
        if len(xb)>30.5*months_after_freezeup:
            ax.plot(xb,yb,lw=.5,c='k',alpha=1)
            
            
        #except:
            #print('No BT.')
        

    #plot ice obs data
    x,y = m(lon,lat)
    
    ##put in IceBird tracks
    #infiles = glob(ib_inpath+'*.dat')
    #for infile_ib in infiles:
        #print(infile_ib)
        #lat_i = np.asarray(getColumn(infile_ib,1,skipheader=0,delimiter='\t'),dtype=float)
        #lon_i = np.asarray(getColumn(infile_ib,0,skipheader=0,delimiter='\t'),dtype=float)
        
        #xi,yi = m(lon_i,lat_i)
        #ax.plot(xi,yi,lw=2)

    #Plot the iceobs
    #ax.plot(x,y)    #get cruise track
    cs=ax.scatter(x,y,c=data,s=100,cmap=cm,vmin=vmin,vmax=vmax)
    
    cb=plt.colorbar(cs,orientation='vertical',pad=.01)
    cb.ax.tick_params(labelsize=20)

    ax.set_title(title, fontsize=25)
    
    plt.show()
    fig1.savefig(outpath+outname,bbox_inches='tight')
    exit()
#plt.close()

#store data for back-trajectories
file_name = infile.split('.json')[0]+'_coords.csv'
print(file_name)

#backtrajectory algorithm doesnt take negative values for the W hemisphere
for ll in range(0,len(lon)):
    if lon[ll] < 0:
        lon[ll] = 360+lon[ll]

#backtrajectories are daily, take only date
for tt in range(0,len(time)):
    time[tt] = time[tt][:10]

tt = [time,lon,lat]
table = list(zip(*tt))

with open(file_name, 'wb') as f:
    #header
    f.write(b'time,lon,lat\n')
    np.savetxt(f, table, fmt="%s", delimiter=",")
