import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date
from glob import glob
import pyresample as pr

from io_func import getColumn

outpath = '../io_plots/'

outname='icecore_salinity'; title='AO2024 ice core salinity';fld1=1;fld2=3
infiles = sorted(glob('../data/icecores/*salinity.csv'))

#outname='icecore_temperature'; title='AO2024 ice core temperature';fld1=0;fld2=1
#infiles = sorted(glob('../data/icecores/*temperature.csv'))

print(infiles)

for infile in infiles:
    print(infile)
    label=infile.split('_')[3]
    print(label)

    zzz = np.asarray(getColumn(infile,fld1,skipheader=1),dtype=float)
    sal = np.asarray(getColumn(infile,fld2,skipheader=1),dtype=float)
    
    #some cores are upside-down
    if label=='station1' or label=='station2':
        print('upside-down')
        zzz=(zzz-zzz[-1])*-1
        #print(zzz)
        #exit()

    plt.plot(sal,zzz*-1,label=label)

plt.legend()  
plt.title(title)
#plt.show()
plt.savefig(outpath+outname,bbox_inches='tight')
