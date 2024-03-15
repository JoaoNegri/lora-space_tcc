import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

leo_lla_df = pd.read_csv('../wider_scenario_2/LEO-LLA-Pos.csv',parse_dates=['TIME[UTC]'])
sites_lla_df = pd.read_csv('../wider_scenario_2/SITES-LLA-Pos.csv')


leo_xyz_df = pd.read_csv('../wider_scenario_2/LEO-XYZ-Pos.csv',parse_dates=['TIME[UTC]'])
sites_xyz_df = pd.read_csv('../wider_scenario_2/SITES-XYZ-Pos.csv')

print(leo_lla_df.head())
# print(sites_lla_df.head())

# print(leo_xyz_df.head())
# print(sites_xyz_df.head())


freq = 868e6
Ptx = 14
G_sat = 12
G_device = 0




for _, site in sites_xyz_df.iterrows():

    x = leo_xyz_df['X[km]'] - site['X[km]']
    y = leo_xyz_df['Y[km]'] - site['Y[km]']
    z = leo_xyz_df['Z[km]'] - site['Z[km]']

    distance = np.sqrt(np.power(x,2)+np.power(y,2)+np.power(z,2))
    plt.subplot(142)

    plt.plot(distance)


    plt.subplot(143)
    Prx = Ptx + G_sat + G_device -20*np.log10(distance*1000) - 20*np.log10(freq) + 147.55 #DISTANCE IS CONVERTED TO METERS
    plt.plot(Prx)

plt.subplot(141)

  
plt.plot(leo_lla_df['LON[deg]'], leo_lla_df['LAT[deg]'])
plt.scatter(sites_lla_df['LONGITUDE[deg]'], sites_lla_df['LATITUDE[deg]'],s= 10,c= sites_lla_df['ALTITUDE[km]'], cmap='viridis')
plt.ylim((0,-50))
plt.xlim((-40,-90))
plt.grid(True)
plt.show()


