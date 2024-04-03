from poliastro.twobody import Orbit
from poliastro.bodies import Earth
from astropy import units as u
import numpy as np
import pandas as pd
from poliastro.ephem import Ephem

from astropy.time import Time
from astropy.time import TimeDelta

# Definindo a data de referência
epoch = Time("2020-01-01 20:20:00", scale='utc')

alt = 600 * u.km
inc = 98 * u.deg
raan = 20 * u.deg
argp = 0 * u.deg
ecc = 0 *u.one # Para uma órbita circular

# Definindo a época da órbita
epoch = Time("2024-04-02 12:00:00", scale='utc')

# Criando a órbita a partir dos elementos
orb = Orbit.from_classical(Earth, alt + Earth.R, ecc, inc, raan, argp, nu=0 * u.deg, epoch=epoch)

# Definindo o intervalo de tempo desejado (1 segundo)
step = TimeDelta(1 * u.second)

# Definindo a data final desejada (20 minutos após a época)
desired_time = epoch + TimeDelta(500 * u.minute)

# Criando um array de tempos com intervalo de 1 segundo
times_array = Time(np.arange(epoch.jd, desired_time.jd, step.to(u.day).value), format='jd', scale='utc')

# Propagando a órbita para cada momento no array de tempos
coords = []
for time in times_array:
    orb_propagated = orb.propagate(time)
    r = orb_propagated.r  # Obtendo as coordenadas da posição
    coords.append(r)  # Armazenando as coordenadas


# Convertendo as coordenadas para um DataFrame do pandas
df = pd.DataFrame(coords, columns=['x', 'y', 'z'])
# Remover ' km' das colunas
df['x'] = df['x'].astype(str)
df['y'] = df['y'].astype(str)
df['z'] = df['z'].astype(str)


df['x'] = df['x'].str.replace(' km', '').astype(float)
df['y'] = df['y'].str.replace(' km', '').astype(float)
df['z'] = df['z'].str.replace(' km', '').astype(float)

print(type(df['x']))
print(type(df['x'][0]))
print(df['x'])
def cartesian_to_latlon(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    latitude = np.arcsin(z / r)
    longitude = np.arctan2(y, x)
    return np.degrees(latitude), np.degrees(longitude)

# Aplicar a função para converter as coordenadas em cada linha do DataFrame
df['latitude'], df['longitude'] = cartesian_to_latlon(df['x'], df['y'], df['z'])
df.drop(['x', 'y', 'z'], axis=1, inplace=True)
df.to_csv('teste.csv',index=False)
print(df)