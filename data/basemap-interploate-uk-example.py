#  Copyright (c) 2024.
import numpy as np
from scipy.interpolate import griddata
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

#Define mapframe
lllon = -11
lllat = 49
urlon = 2
urlat = 61

# Make some toy data, random points + corners
n = 10 # no of stations
lat = np.random.uniform(low=lllat+2, high=urlat-2, size=n)
lat = np.append(lat, [lllat, urlat, urlat, lllat])
lon = np.random.uniform(low=lllon+2, high=urlon-2, size=n)
lon = np.append(lon, [lllon, urlon, lllon, urlon])

print(lon.shape, lat.shape)
temp = np.random.randn(n+4) + 8 # British summer?

# set up basemap chose projection!
m = Basemap(projection = 'merc', resolution='l',
    llcrnrlon = lllon, llcrnrlat = lllat, urcrnrlon = urlon, urcrnrlat = urlat)

# transform coordinates to map projection m
m_lon, m_lat = m(*(lon, lat))

# generate grid data
numcols, numrows = 240, 240
xi = np.linspace(m_lon.min(), m_lon.max(), numcols)
yi = np.linspace(m_lat.min(), m_lat.max(), numrows)
xi, yi = np.meshgrid(xi, yi)

# interpolate, there are better methods, especially if you have many datapoints
zi = griddata((m_lon,m_lat),temp,(xi,yi),method='cubic')

fig, ax = plt.subplots(figsize=(12, 12))

# draw map details
m.drawmapboundary(fill_color = 'skyblue', zorder = 1)

# Plot interpolated temperatures
m.contourf(xi, yi, zi, 500, cmap='OrRd', zorder = 2)

m.drawlsmask(ocean_color='skyblue', land_color=(0, 0, 0, 0), lakes=True, zorder = 3)

cbar = plt.colorbar()
plt.title('Temperature')

plt.show()