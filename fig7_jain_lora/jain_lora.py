import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


file = '/home/joao/tcc/lora-space/resultados_simulacao_30_random/LB/LB2_3CH_s94846839_p10/LB2_3000_3CH_16_s94846839_p10.csv'

df = pd.read_csv(file,names=['timestamp','id','dist','elev','SF','status'])


# for item in 
df['Prx'] = 14 + 12 + 0 -20*np.log10(df[df['id']==100]['dist']*1000) - 20*np.log10(868e6) + 147.55

colors = {7: 'darkblue', 8: 'blue', 9: 'lightblue', 10: 'lightcoral', 11: 'red', 12: 'darkred'}

a = df['SF'].map(colors)

print(df[df['id']==100])
plt.scatter(df['timestamp'], df['id'], alpha=0.3, c=a.values)
plt.show()