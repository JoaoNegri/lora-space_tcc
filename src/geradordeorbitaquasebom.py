from poliastro.twobody import Orbit
from poliastro.bodies import Earth
from astropy import units as u
import numpy as np
import pandas as pd
from astropy.time import Time
from astropy.time import TimeDelta
import matplotlib.pyplot as plt

# Parameters
EPOCH = Time("2020-01-01 20:00:00", scale='utc')
SAT_NAME = "LEO"
ALTITUDE = 600 * u.km
PERIGEE_ARGUMENT = 0 * u.deg

# Defining orbit elements
alt = ALTITUDE
ecc = 0 * u.one  # For a circular orbit

# Time step
step = TimeDelta(1 * u.second)

# Desired final time
desired_time = EPOCH + TimeDelta(96.538 * u.minute)

# Array of times
times_array = Time(np.arange(EPOCH.jd, desired_time.jd, step.to(u.day).value), format='jd', scale='utc')

# Initial values for MEAN_ANOMALY, INCLINATION, and RAAN
initial_mean_anomaly = 180 * u.deg
initial_inclination = 90 * u.deg
initial_raan = 180 * u.deg
antiga = pd.read_csv("../params/wider_scenario_2/LEO-XYZ-Pos.csv")
antiga.rename(columns={'TIME[UTC]': 'Time', 'X[km]': 'x', 'Y[km]': 'y', 'Z[km]': 'z'}, inplace=True)
# Define target MAE and initial MAE
target_mae = 100  # Define your target MAE here
current_mae = float('inf')

# Loop until reaching target MAE
# Generate random values to add to each parameter


# Calculate new parameters
mean_anomaly = (180+127.43197677-5.19692281-2.06593244-0.71249478+0.3813946-0.03042298)* u.deg
inclination = (90-15.57252947+18.97274162+3.3434524+4.91159402-0.19838546-0.04472003)* u.deg
raan = (180+123.00275919-7.57253357-4.89084656-0.63449786+0.39320677-0.00972638) * u.deg
# mean_anomaly = (299.7898776 )* u.deg
# inclination = (101.24756764)* u.deg
# raan = (290.30281295) * u.deg


  
# Creating orbit from classical elements
orb = Orbit.from_classical(Earth, alt + Earth.R, ecc, inclination, raan, PERIGEE_ARGUMENT, nu=mean_anomaly, epoch=EPOCH)

# Propagating the orbit
coords = []
for time in times_array:
    orb_propagated = orb.propagate(time)
    r = orb_propagated.r  # Getting position coordinates
    coords.append(r)  # Storing coordinates


# Converting coordinates to DataFrame
df = pd.DataFrame(coords, columns=['x', 'y', 'z'])

df['x'] = df['x'].astype(str).str.replace(' km', '').astype(float)
df['y'] = df['y'].astype(str).str.replace(' km', '').astype(float)
df['z'] = df['z'].astype(str).str.replace(' km', '').astype(float)


print(antiga[['x', 'y', 'z']])
print(df[['x', 'y', 'z']])
# Calculate MAE
current_mae = np.sum(np.abs(df[['x', 'y', 'z']] - antiga[['x', 'y', 'z']]))
print(current_mae)


# Plotting the final orbit
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(df['x'], df['y'], df['z'], c='b', marker='o')
ax.scatter(antiga['x'], antiga['y'], antiga['z'], c='r', marker='o')
ax.scatter(antiga['x'].iloc[-1], antiga['y'].iloc[-1], antiga['z'].iloc[-1], c='g', marker='o')
ax.set_xlabel('X (km)')
ax.set_ylabel('Y (km)')
ax.set_zlabel('Z (km)')
ax.set_title(f'Final Satellite Orbit - Mean Anomaly: {mean_anomaly}, Inclination: {inclination}, RAAN: {raan}')
plt.show()

df.to_csv('orbita_completa.csv')