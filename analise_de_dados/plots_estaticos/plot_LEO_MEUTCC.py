import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import Circle
from matplotlib.lines import Line2D
leo_lla_df1 = pd.read_csv('../../params/wider_scenario_2/LEO-LLA-Pos copy.csv', parse_dates=['TIME[UTC]'])
leo_lla_df2 = pd.read_csv('../../params/wider_scenario_2/LEO-LLA-Pos copy 2.csv', parse_dates=['TIME[UTC]'])
leo_lla_df3 = pd.read_csv('../../params/wider_scenario_2/LEO-LLA-Pos copy 3.csv', parse_dates=['TIME[UTC]'])
sites_lla_df = pd.read_csv('../../params/wider_scenario_2/SITES-LLA-Pos.csv')

# Create a new figure
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 10), subplot_kw={'projection': ccrs.PlateCarree()})

# Add features to the map (like coastlines and borders) to both subplots
for ax in [ax1, ax2, ax3]:
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.gridlines(draw_labels=True)
    ax.scatter(sites_lla_df['LONGITUDE[deg]'], sites_lla_df['LATITUDE[deg]'], s=10, c=sites_lla_df['ALTITUDE[km]'], cmap='viridis', alpha=0.1, transform=ccrs.PlateCarree())

# First subplot: initial positions and circles
ax1.scatter(leo_lla_df1['LON[deg]'][0], leo_lla_df1['LAT[deg]'][0], s=90, color='b', edgecolor='black', zorder=5, transform=ccrs.PlateCarree(), label='Satélite 1')
ax1.scatter(leo_lla_df2['LON[deg]'][0], leo_lla_df2['LAT[deg]'][0], s=90, color='r', edgecolor='black', zorder=5, transform=ccrs.PlateCarree(), label='Satélite 2')
ax1.scatter(leo_lla_df3['LON[deg]'][0], leo_lla_df3['LAT[deg]'][0], s=90, color='g', edgecolor='black', zorder=5, transform=ccrs.PlateCarree(), label='Satélite 3')

circle1 = Circle((leo_lla_df1['LON[deg]'][0], leo_lla_df1['LAT[deg]'][0]), 20, edgecolor='b', facecolor='b', alpha=0.2, transform=ccrs.PlateCarree())
circle2 = Circle((leo_lla_df2['LON[deg]'][0], leo_lla_df2['LAT[deg]'][0]), 20, edgecolor='r', facecolor='r', alpha=0.2, transform=ccrs.PlateCarree())
circle3 = Circle((leo_lla_df3['LON[deg]'][0], leo_lla_df3['LAT[deg]'][0]), 20, edgecolor='g', facecolor='g', alpha=0.2, transform=ccrs.PlateCarree())

ax1.add_patch(circle1)
ax1.add_patch(circle2)
ax1.add_patch(circle3)

# Plotting arrows for the direction of the first satellite
# Calculate differences for arrow direction
leo_lla_df2['LON_diff'] = leo_lla_df2['LON[deg]'].diff()
leo_lla_df2['LAT_diff'] = leo_lla_df2['LAT[deg]'].diff()

# Take the second row for the initial direction
initial_lon_diff = leo_lla_df2['LON_diff'].iloc[100]
initial_lat_diff = leo_lla_df2['LAT_diff'].iloc[100]

# Plot the arrow
ax1.quiver(
    leo_lla_df2['LON[deg]'][0] - 18,  # Shift arrow to the left by 1 degree
    leo_lla_df2['LAT[deg]'][0] - 18, 
    initial_lon_diff, 
    initial_lat_diff, 
    scale=0.002,  # Adjust scale to make arrow more visible
    scale_units='xy', 
    color='black', 
    zorder=6, 
    transform=ccrs.PlateCarree(),
    label='Trajetória dos satélites'
)
arrow_legend = Line2D([0], [0], color='black', lw=2, linestyle='-', marker='<', markersize=10)
legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Satélite 1', markerfacecolor='b', markersize=10),
    Line2D([0], [0], marker='o', color='w', label='Satélite 2', markerfacecolor='r', markersize=10),
    Line2D([0], [0], marker='o', color='w', label='Satélite 3', markerfacecolor='g', markersize=10),
    Line2D([0], [0], color='black', lw=2, linestyle='-', marker='<', markersize=10, label='Direção dos satélites')
]

ax1.legend(handles=legend_elements)



ax1.set_ylim(-60, 20)
ax1.set_xlim(-90, -40)
ax1.set_title("Posição Inicial")

# Second subplot: last positions of each satellite
ax2.scatter(leo_lla_df1['LON[deg]'][299], leo_lla_df1['LAT[deg]'][299], s=90, color='b', edgecolor='black', zorder=5, transform=ccrs.PlateCarree(), label='Satélite 1')
ax2.scatter(leo_lla_df2['LON[deg]'][299], leo_lla_df2['LAT[deg]'][299], s=90, color='r', edgecolor='black', zorder=5, transform=ccrs.PlateCarree(), label='Satélite 2')
ax2.scatter(leo_lla_df3['LON[deg]'][299], leo_lla_df3['LAT[deg]'][299], s=90, color='g', edgecolor='black', zorder=5, transform=ccrs.PlateCarree(), label='Satélite 3')

circle1 = Circle((leo_lla_df1['LON[deg]'][299], leo_lla_df1['LAT[deg]'][299]), 20, edgecolor='b', facecolor='b', alpha=0.2, transform=ccrs.PlateCarree())
circle2 = Circle((leo_lla_df2['LON[deg]'][299], leo_lla_df2['LAT[deg]'][299]), 20, edgecolor='r', facecolor='r', alpha=0.2, transform=ccrs.PlateCarree())
circle3 = Circle((leo_lla_df3['LON[deg]'][299], leo_lla_df3['LAT[deg]'][299]), 20, edgecolor='g', facecolor='g', alpha=0.2, transform=ccrs.PlateCarree())

ax2.add_patch(circle1)
ax2.add_patch(circle2)
ax2.add_patch(circle3)

ax2.set_ylim(-60, 20)
ax2.set_xlim(-90, -40)
ax2.set_title("Posição Intermediária")
ax2.legend()

ax3.scatter(leo_lla_df3['LON[deg]'][899], leo_lla_df3['LAT[deg]'][899], s=90, color='g', edgecolor='black', zorder=5, transform=ccrs.PlateCarree(), label='Satélite 3')

circle3 = Circle((leo_lla_df3['LON[deg]'][899], leo_lla_df3['LAT[deg]'][899]), 20, edgecolor='g', facecolor='g', alpha=0.2, transform=ccrs.PlateCarree())

ax3.add_patch(circle3)

ax3.set_ylim(-60, 20)
ax3.set_xlim(-90, -40)
ax3.set_title("Posição Finais")
# plt.savefig('../figuras/Caminho_satelites.png', bbox_inches='tight')
plt.legend()
plt.show()
