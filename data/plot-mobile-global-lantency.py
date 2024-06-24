#  Copyright (c) 2024.
from mpl_toolkits.basemap import Basemap, addcyclic
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib as mpl
from scipy.interpolate import griddata

n_lines = 21
cmap = mpl.colormaps['Blues']


plt.rcParams["font.family"] = "Arial"

XLSX_FILE = r"../data/data.xlsx"

data = pd.read_excel(XLSX_FILE, sheet_name="cloud-latency-geo")

print(data)



# set up orthographic map projection with
# perspective of satellite looking down at 45N, 100W.
# use low resolution coastlines.
# map = Basemap(projection='ortho',lat_0=53,lon_0=00,resolution='l')


map = Basemap(projection='mill',lon_0=0, lat_0=50,resolution='l')
# nylat, nylon are lat/lon of New York
nylat = 40.78; nylon = -73.98
# lonlat, lonlon are lat/lon of London.
lonlat = 51.53; lonlon = 0.08

mcrlat = 53.4667
mcrlon = -2.2333

mcrX, mcrY = map(mcrlon, mcrlat)

maximum_latency = 0.7



ethernet_data = data[data["connectivity"] == "mobile"]
ethernet_data_exclude_mcr = ethernet_data
ethernet_data_exclude_mcr_data = ethernet_data[ethernet_data_exclude_mcr["City"] != "Manchester"]

lon, lat = ethernet_data_exclude_mcr["Longitude"], ethernet_data_exclude_mcr["Latitude"]
latency = ethernet_data_exclude_mcr["total"]

print(ethernet_data)

# print(lon.shape, lat.shape)

m_lon, m_lat = map(*(lon, lat))

m_lon_max, m_lat_max = map(180, 90)
m_lon_min, m_lat_min = map(-180, -90)



# print(m_lon, m_lat)

# generate grid data
numcols, numrows = 240, 240
xi = np.linspace(m_lon_min, m_lon_max, numcols)
yi = np.linspace(m_lat_min, m_lat_max, numrows)
xi, yi = np.meshgrid(xi, yi)

# interpolate, there are better methods, especially if you have many datapoints
zi = griddata((m_lon,m_lat),latency,(xi,yi),method='nearest')

fig, ax = plt.subplots()

# draw map details
map.drawmapboundary(fill_color='skyblue', zorder = 1)
map.drawmeridians(np.arange(0,360,30), linewidth=0.2)
map.drawparallels(np.arange(-90,90,30), linewidth=0.2)

# Plot interpolated temperatures
map.contourf(xi, yi, zi, cmap=cmap, zorder = 2, vmin=0, vmax=maximum_latency)

map.scatter(mcrX, mcrY, 10, marker="s", color="k", zorder=4)
plt.text(mcrX, mcrY, "Manchester", zorder=4)

map.drawlsmask(ocean_color='skyblue', land_color=(0, 0, 0, 0), lakes=True, zorder = 3)



# draw coastlines, country boundaries, fill continents.
map.drawcoastlines(linewidth=0.15)
map.drawcountries(linewidth=0.1)
map.fillcontinents(color='white',lake_color='aqua')
# draw the edge of the map projection region (the projection limb)
# map.drawmapboundary(fill_color='gray')
# draw lat/lon grid lines every 30 degrees.


displayed_country = set()
exclude_country_list = ["Belgium", "Switzerland", "Netherlands", "Poland", "United Kingdom"]
exclude_state_list = ["Taiwan", "Utah", "Java", "Virginia", "Lowa", "Nevada", "Iowa"]

for idx, row in ethernet_data_exclude_mcr_data.iterrows():
    country = row["Country"]
    state = row["State"]

    if country not in exclude_country_list and state not in exclude_state_list:
        displayed_country.add(country)
        lon, lat = map(row["Longitude"], row["Latitude"])
        if row["City"] == "Sydney":
            lon_txt, lat_txt = map(row["Longitude"]-10, row["Latitude"] - 8)
        else:
            lon_txt, lat_txt = map(row["Longitude"], row["Latitude"] - 8)
        plt.scatter(lon, lat, s=8, marker="o", edgecolors="k", color=cmap(row["total"]/maximum_latency), zorder=4)
        plt.text(lon_txt, lat_txt, row["City"] +" (%.2fs)"%row["total"],
                 zorder=4, backgroundcolor="#40FFFFFF" if row["total"]>0.31 else "#00FFFFFF")
        print(row["connectivity"], row["City"], row["total"])

norm = mpl.colors.Normalize(vmin=0, vmax=maximum_latency)
cbar = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
             ax=ax, orientation='vertical', label='Latency')

plt.tight_layout()
plt.show()
