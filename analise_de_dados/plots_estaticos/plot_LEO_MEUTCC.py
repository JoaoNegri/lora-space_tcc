import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

leo_lla_df1 = pd.read_csv('../../params/wider_scenario_2/LEO-LLA-Pos copy.csv',parse_dates=['TIME[UTC]'])
leo_lla_df2 = pd.read_csv('../../params/wider_scenario_2/LEO-LLA-Pos copy 2.csv',parse_dates=['TIME[UTC]'])
leo_lla_df3 = pd.read_csv('../../params/wider_scenario_2/LEO-LLA-Pos copy 3.csv',parse_dates=['TIME[UTC]'])
sites_lla_df = pd.read_csv('../../params/wider_scenario_2/SITES-LLA-Pos.csv')
  
# plt.plot(leo_lla_df3['LON[deg]'], leo_lla_df3['LAT[deg]'])
plt.scatter(sites_lla_df['LONGITUDE[deg]'], sites_lla_df['LATITUDE[deg]'],s= 10,c= sites_lla_df['ALTITUDE[km]'], cmap='viridis')
circle1 = plt.Circle((leo_lla_df1['LON[deg]'][0], leo_lla_df1['LAT[deg]'][0]), 20, edgecolor='b', facecolor='none')
circle2 = plt.Circle((leo_lla_df2['LON[deg]'][0], leo_lla_df2['LAT[deg]'][0]), 20, edgecolor='r', ls='--', facecolor='none')
circle3 = plt.Circle((leo_lla_df3['LON[deg]'][0], leo_lla_df3['LAT[deg]'][0]), 20, edgecolor='g', facecolor='none')
plt.gca().add_patch(circle1)
plt.gca().add_patch(circle2)
plt.gca().add_patch(circle3)
plt.ylim((0,-50))
plt.xlim((-40,-90))
plt.grid(True)
plt.show()


