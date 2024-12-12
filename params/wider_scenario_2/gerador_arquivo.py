import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df1 = pd.read_csv('LEO-XYZ-Pos_sat1.csv')
df2 = pd.read_csv('LEO-XYZ-Pos_sat2.csv')
df3 = pd.read_csv('LEO-XYZ-Pos_sat3.csv')
print(df1)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter(df1['X[km]'][df1['X[km]'] != 100000][1200], df1['Y[km]'][df1['X[km]'] != 100000][1200], df1['Z[km]'][df1['X[km]'] != 100000][1200], marker='o')
ax.scatter(df2['X[km]'][df2['X[km]'] != 100000][1200], df2['Y[km]'][df2['X[km]'] != 100000][1200], df2['Z[km]'][df2['X[km]'] != 100000][1200], marker='o')
ax.scatter(df3['X[km]'][df3['X[km]'] != 100000][1200], df3['Y[km]'][df3['X[km]'] != 100000][1200], df3['Z[km]'][df3['X[km]'] != 100000][1200], marker='o')

ax.plot(df3['X[km]'][df3['X[km]'] != 100000], df3['Y[km]'][df3['X[km]'] != 100000], df3['Z[km]'][df3['X[km]'] != 100000], marker='o')

x1, y1, z1 = df1['X[km]'][df1['X[km]'] != 100000][1200], df1['Y[km]'][df1['X[km]'] != 100000][1200],  df1['Z[km]'][df1['X[km]'] != 100000][1200]  # Coordenadas do ponto central do círculo
x2, y2, z2 = df2['X[km]'][df2['X[km]'] != 100000][1200], df2['Y[km]'][df2['X[km]'] != 100000][1200],  df2['Z[km]'][df2['X[km]'] != 100000][1200]  # Coordenadas do ponto central do círculo
x3, y3, z3 = df3['X[km]'][df3['X[km]'] != 100000][1200], df3['Y[km]'][df3['X[km]'] != 100000][1200],  df3['Z[km]'][df3['X[km]'] != 100000][1200]  # Coordenadas do ponto central do círculo
r = 1000  # Raio do círculo

# Gerar pontos do círculo no plano XY
theta = np.linspace(0, 2 * np.pi, 100)  # 100 pontos igualmente espaçados de 0 a 2pi
circle_y1 = y1 + r * np.cos(theta)
circle_y2 = y2 + r * np.cos(theta)
circle_y3 = y3 + r * np.cos(theta)
circle_z1 = z1 + r * np.sin(theta)
circle_z2 = z2 + r * np.sin(theta)
circle_z3 = z3 + r * np.sin(theta)
circle_x1 = np.full_like(circle_y1, x1)  # Manter x constante
circle_x2 = np.full_like(circle_y2, x2)  # Manter x constante
circle_x3 = np.full_like(circle_y3, x3)  # Manter x constante
ax.plot(circle_x1, circle_y1, circle_z1, label='Círculo ao redor do ponto')
ax.plot(circle_x2, circle_y2, circle_z2, label='Círculo ao redor do ponto')
ax.plot(circle_x3, circle_y3, circle_z3, label='Círculo ao redor do ponto')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Órbita 3D')

plt.show()