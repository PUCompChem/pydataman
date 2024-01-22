from read.data_access import read_metadata

df_meteo = read_metadata('https://meter.ac/gs/metadata/meteo.csv')
print(df_meteo)

df_nodes = read_metadata('https://meter.ac/gs/metadata/nodes.csv')
print(df_nodes)

df_earth = read_metadata('https://meter.ac/gs/metadata/earth.csv')
print(df_earth)
