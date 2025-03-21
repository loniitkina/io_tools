import numpy as np
import matplotlib.pyplot as plt
from glob import glob

from io_func import getColumn

#plot Magnaponder PDF data
inpath = '../data/magnaponder/'
outpath = '../io_plots/'
outname = 'magnaponder_pdf'

#bowline contains 11 meltponds
#survey contains 47 meltponds

srbins = np.arange(0,1,.02)

fig1    = plt.figure(figsize=(20,20))
ax      = fig1.add_subplot(111)

ax.set_ylabel('Probability',fontsize=20)
ax.set_xlabel('Depth (m)',fontsize=20)

#Load data
infiles = glob(inpath+'*.csv')

for fn in infiles:
    print(fn)
    
    ssl = np.asarray(getColumn(fn,3,skipheader=4),dtype=float)/100
    pond = np.asarray(getColumn(fn,22,skipheader=4),dtype=float)/100*-1
    
    mask = pond==0
    
    ssl = np.ma.array(ssl,mask=~mask).compressed()
    
    pond = np.ma.array(pond,mask=mask).compressed()
    
    #print(pond)
    #exit()
    

    #make histograms
    weights = np.ones_like(ssl) / (len(ssl))
    n, bins, patches = ax.hist(ssl, srbins, histtype='step', linewidth=4, alpha=.5, weights=weights,label=fn.split('/')[-1].split('_')[0]+' SSL')
    
    weights = np.ones_like(pond) / (len(pond))
    n, bins, patches = ax.hist(pond, srbins, histtype='step', linewidth=4, alpha=.5, weights=weights,label=fn.split('/')[-1].split('_')[0]+' ponds')
    
ax.legend(fontsize=20)
ax.tick_params(labelsize=20)
  
plt.show()
fig1.savefig(outpath+outname,bbox_inches='tight')

#exit()
        
        

    
    
