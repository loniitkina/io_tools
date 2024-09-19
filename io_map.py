import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date
from glob import glob
import pyresample as pr
import json

from io_func import getColumn

outpath = '../io_plots/'
outpath_data = '../data/'

# Opening JSON file with iceobs
infile = glob('../data/*13.json')[0]
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
outnames = ['map_iceobs_concentration', 'map_iceobs_thickness', 'map_iceobs_algae', 'map_iceobs_sediment']
titles = ['Ice Concentration (0-10)', 'Ice Thickness (cm)', 'Ice algae concentration', 'Ice sediment concentration']
datas = [iconc, it, algae, sedim]
cms = [plt.cm.Reds, plt.cm.Reds, plt.cm.Greens, plt.cm.Blues]
vmins = [1,100, 0, 0]
vmaxs = [10, 200, 1, 1]

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
    infiles = glob('../data/backtrajectories/*.csv')
    colors = plt.cm.rainbow(np.linspace(0, 1, 108))
    i=0
    for num in range(1,108):
        infile_bt = '../data/backtrajectories/'+str(num)+'.csv'
        print(infile_bt)
        #color = next(colors)
        
        try:
            #read in the backtrajectories - with the structure:
            #2024-08-10,30.5008,81.5483
            lat_b = np.asarray(getColumn(infile_bt,2,skipheader=0),dtype=float)
            lon_b = np.asarray(getColumn(infile_bt,1,skipheader=0),dtype=float)

            xb,yb = m(lon_b,lat_b)
            ax.plot(xb,yb,lw=2,c=colors[i],alpha=.5)
        except:
            print('No BT.')
        
        i = i +1

    #plot ice obs data
    x,y = m(lon,lat)

    cs=ax.scatter(x,y,c=data,s=100,cmap=cm,vmin=vmin,vmax=vmax)

    cb=plt.colorbar(cs,orientation='vertical',pad=.01)
    cb.ax.tick_params(labelsize=20)

    ax.set_title(title, fontsize=25)
    
    plt.show()
    fig1.savefig(outpath+outname,bbox_inches='tight')
#plt.close()

#store data for back-trajectories
file_name = infile.split('.json')[0]+'_coords.csv'
print(file_name)

tt = [time,lon,lat]
table = list(zip(*tt))

with open(file_name, 'wb') as f:
    #header
    f.write(b'time,lon,lat\n')
    np.savetxt(f, table, fmt="%s", delimiter=",")
