from poliastro.twobody import Orbit
from poliastro.bodies import Earth
from astropy import units as u
import numpy as np
import pandas as pd
from astropy.time import Time
from scipy.optimize import minimize
from poliastro.twobody import Orbit
from poliastro.bodies import Earth
from astropy import units as u
import numpy as np
import pandas as pd
from astropy.time import Time
from astropy.time import TimeDelta
import matplotlib.pyplot as plt
from multiprocessing import Pool

# Parameters
EPOCH = Time("2020-01-01 20:20:00", scale='utc')
SAT_NAME = "LEO"
ALTITUDE = 600 * u.km
PERIGEE_ARGUMENT = 0 * u.deg

# Load provided data
antiga = pd.read_csv("params/wider_scenario_2/LEO-XYZ-Pos.csv")
antiga.rename(columns={'TIME[UTC]': 'Time', 'X[km]': 'x', 'Y[km]': 'y', 'Z[km]': 'z'}, inplace=True)

# Defining orbit elements
alt = ALTITUDE
ecc = 0 * u.one  # For a circular orbit

# Time step
step = TimeDelta(1 * u.second)

# Desired final time
desired_time = EPOCH + TimeDelta(20 * u.minute)

# Array of times
times_array = Time(np.arange(EPOCH.jd, desired_time.jd, step.to(u.day).value), format='jd', scale='utc')

# Define a function to calculate the absolute error
def absolute_error(params):
    mean_anomaly, inclination, raan = params
    
    # Create orbit with current parameters
    orb = Orbit.from_classical(Earth, alt + Earth.R, ecc, inclination * u.deg, raan * u.deg, PERIGEE_ARGUMENT, nu=mean_anomaly * u.deg, epoch=EPOCH)
    
    # Propagate the orbit
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
    # Calculate absolute error
    absolute_error = np.sum(np.abs(df[['x', 'y', 'z']].values - antiga[['x', 'y', 'z']].values))
    
    return absolute_error

# Initial guess for parameters
initial_guess = [180+127.43197677-5.19692281-2.06593244-0.71249478+0.3813946-0.03042298, 90-15.57252947+18.97274162+3.3434524+4.91159402-0.19838546-0.04472003, 180+123.00275919-7.57253357-4.89084656-0.63449786+0.39320677-0.00972638]  # Initial values for mean anomaly, inclination, and RAAN

# Perform optimization
result = minimize(absolute_error, initial_guess, method='Nelder-Mead')

# Extract optimized parameters
optimized_params = result.x
print("Optimized parameters:", optimized_params)
