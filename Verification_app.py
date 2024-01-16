import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import unary_union

df = pd.read_csv('D:/Project/VerifikasiNDF/Result/Accuracy.csv')
df['Time'] = pd.to_datetime(df['Time'])

# Sidebar filter
selected_prov = st.sidebar.selectbox('Pilih Provinsi:', df['Prov'].unique())
selected_start_time = st.sidebar.date_input('Pilih Waktu Awal:', df['Time'].min())
selected_end_time = st.sidebar.date_input('Pilih Waktu Akhir:', df['Time'].max())
selected_start_time = pd.to_datetime(selected_start_time)
selected_end_time = pd.to_datetime(selected_end_time)

# Filter DataFrame berdasarkan pilihan pengguna
filtered_df = df[(df['Prov'] == selected_prov) & (df['Time'] >= selected_start_time) & (df['Time'] <= selected_end_time)]
timefiltered_df = df[(df['Time'] >= selected_start_time) & (df['Time'] <= selected_end_time)]

# Tampilkan tabel statistik
st.header('Tabel Statistik Akurasi')
st.write('Provinsi:', selected_prov)
st.write('Rentang Waktu:', f'{selected_start_time} sampai {selected_end_time}')

# Hitung nilai statistik
min_accuracy_ww = filtered_df['Accuracy_WW'].min()
max_accuracy_ww = filtered_df['Accuracy_WW'].max()
mean_accuracy_ww = filtered_df['Accuracy_WW'].mean()

min_accuracy_gsmap = filtered_df['Accuracy_GSMaP'].min()
max_accuracy_gsmap = filtered_df['Accuracy_GSMaP'].max()
mean_accuracy_gsmap = filtered_df['Accuracy_GSMaP'].mean()

# Tampilkan tabel
statistic_table_data = {
    'Statistik': ['Akurasi Minimum', 'Akurasi Maksimum', 'Akurasi Rata-rata'],
    'Obs.Permukaan': [min_accuracy_ww, max_accuracy_ww, mean_accuracy_ww],
    'GSMaP': [min_accuracy_gsmap, max_accuracy_gsmap, mean_accuracy_gsmap]
}

statistic_table = pd.DataFrame(statistic_table_data)
st.markdown(statistic_table.style.hide(axis="index").to_html(), unsafe_allow_html=True)
# st.table(statistic_table)

# Grafik Time Series untuk Rata-rata Agregasi Seluruh Provinsi
st.header('Grafik Time Series')
avg_df = filtered_df.groupby('Time').mean().reset_index()
fig_time_series = px.line(avg_df, x='Time', y=['Accuracy_WW', 'Accuracy_GSMaP'],
                          title=f'Rata-rata Agregasi Provinsi {selected_prov}',
                          labels={'Accuracy_WW': 'Sfc.Obs.', 'Accuracy_GSMaP': 'GSMaP'})
st.plotly_chart(fig_time_series)

# Peta Spasial untuk Rata-rata Agregasi Seluruh Waktu
st.header('Peta Spasial')

# Load shapefile Provinsi
shapefile_path = "D:/Project/ProspekHujanSepekan/shp/BATAS_PROVINSI_DESEMBER_2019_DUKCAPIL.shp"
gdf_provinsi = gpd.read_file(shapefile_path)
gdf_provinsi['geometry'] = gdf_provinsi['geometry'].simplify(0.05)  # Sesuaikan dengan tingkat penyederhanaan yang sesuai

# Merge DataFrame dengan data geometri Provinsi
gdf_merged1 = gdf_provinsi.merge(timefiltered_df[['Prov','Time','Accuracy_WW']].groupby('Prov').mean(), left_on='PROVINSI', right_on='Prov', how='left')
gdf_merged2 = gdf_provinsi.merge(timefiltered_df[['Prov','Time','Accuracy_GSMaP']].groupby('Prov').mean(), left_on='PROVINSI', right_on='Prov', how='left')
min_lon, min_lat, max_lon, max_lat = 93,-12,141,10
fig_map1 = px.choropleth_mapbox(gdf_merged1, geojson=gdf_merged1.geometry, locations=gdf_merged1.index, color='Accuracy_WW',
                               color_continuous_scale="Viridis",
                               mapbox_style="carto-positron",
                               title='Berdasar Obs. Permukaan',
                               labels={'Accuracy_WW': 'Accuracy'},
                               center={'lat': (max_lat+min_lat)/2, 'lon': (max_lon+min_lon)/2},
                               zoom=3)
fig_map2 = px.choropleth_mapbox(gdf_merged2, geojson=gdf_merged2.geometry, locations=gdf_merged2.index, color='Accuracy_GSMaP',
                               color_continuous_scale="Viridis",
                               mapbox_style="carto-positron",
                               title='Berdasar GSMaP',
                               labels={'Accuracy_GSMaP': 'Accuracy'},
                               center={'lat': (max_lat+min_lat)/2, 'lon': (max_lon+min_lon)/2},
                               zoom=3)
st.plotly_chart(fig_map1)
st.plotly_chart(fig_map2)
