from poliastro.twobody import Orbit
from poliastro.bodies import Earth
from astropy import units as u
import numpy as np
import pandas as pd
from astropy.time import Time
from astropy.time import TimeDelta
import matplotlib.pyplot as plt
from multiprocessing import Pool

def calculate_mae(params):
    # Unpack parameters
    random_mean_anomaly, random_inclination, random_raan = params

    # Calculate new parameters
    mean_anomaly = initial_mean_anomaly + random_mean_anomaly
    inclination = initial_inclination + random_inclination
    raan = initial_raan + random_raan

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
    # Calculate MAE
    mae =  np.sum(np.abs(df[['x', 'y', 'z']].values - antiga[['x', 'y', 'z']].values))
    
    return mae

if __name__ == '__main__':
    # Parameters
    EPOCH = Time("2020-01-01 20:20:00", scale='utc')
    SAT_NAME = "LEO"
    ALTITUDE = 600 * u.km
    PERIGEE_ARGUMENT = 0 * u.deg

    # Defining orbit elements
    alt = ALTITUDE
    ecc = 0 * u.one  # For a circular orbit

    # Time step
    step = TimeDelta(1 * u.second)

    # Desired final time
    desired_time = EPOCH + TimeDelta(20 * u.minute)

    # Array of times
    times_array = Time(np.arange(EPOCH.jd, desired_time.jd, step.to(u.day).value), format='jd', scale='utc')

    # Initial values for MEAN_ANOMALY, INCLINATION, and RAAN
    initial_mean_anomaly = (180+127.43197677-5.19692281-2.06593244-0.71249478+0.3813946-0.12797988) * u.deg
    initial_inclination = (90-15.57252947+18.97274162+3.3434524+4.91159402-0.19838546-0.02562409) * u.deg
    initial_raan = (180+123.00275919-7.57253357-4.89084656-0.63449786+0.39320677-0.0781986) * u.deg
    # Load antiga DataFrame
# (<Quantity -0.00763366 deg>, <Quantity -0.2486428 deg>, <Quantity 0.02135888 deg>
    antiga = pd.read_csv("params/wider_scenario_2/LEO-XYZ-Pos.csv")
    antiga.rename(columns={'TIME[UTC]': 'Time', 'X[km]': 'x', 'Y[km]': 'y', 'Z[km]': 'z'}, inplace=True)

    # Define target MAE and initial MAE
    target_mae = 59000  # Define your target MAE here
    current_mae = float('inf')

    # Create pool for parallel processing
    pool = Pool()

    # Loop until reaching target MAE
    while current_mae > target_mae:
        # Generate random values to add to each parameter
        random_params = [(np.random.uniform(-0.02, 0.02) * u.deg,
                          np.random.uniform(-2, 2) * u.deg,
                          np.random.uniform(-0.02, 0.02) * u.deg) for _ in range(8)]



        # Calculate MAE in parallel
        mae_results = pool.map(calculate_mae, random_params)
        # Update current MAE
        current_mae = min(mae_results)

        print(f'mae_results : {mae_results}, parameters : {random_params}')
        print(current_mae, "!!!!!!!!!!!!!!!!!")
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

    # Close the pool
    pool.close()
    pool.join()
