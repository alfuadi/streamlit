import streamlit as st
import pandas as pd
import requests
from io import StringIO
import datetime
import folium
from streamlit_folium import st_folium
import branca.colormap as cm
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

selected_app = st.sidebar.selectbox('Select The Dashboard:', ['Model Evaluation','NDF Verification'])

def boxplot(filtered_df,variable):
    sns.set(style="whitegrid")
    fig, ax = plt.subplots()
    sns.boxplot(x='WW', y=variable, data=filtered_df, ax=ax)
    ax.set_title(f'Boxplot {variable} for {model_filter}')
    ax.set_xlabel('Weather Categories')
    ax.set_ylabel(variable)
    st.pyplot(fig)

if selected_app=='Model Evaluation':
    # ==============================Model Eval============================
    url1 = 'https://web.meteo.bmkg.go.id//media/data/bmkg/ModelEval_Recap.txt'
    response1 = requests.get(url1)
    data_text1 = response1.text
    de = pd.read_csv(StringIO(data_text1), delimiter=",")
    de['Valid'] = pd.to_datetime(de['Valid'])

    selected_start_time = st.sidebar.date_input('Select The First Date:', de['Valid'].min())
    selected_end_time = st.sidebar.date_input('Select The Last Date:', de['Valid'].max())
    selected_start_time = pd.to_datetime(selected_start_time)
    selected_end_time = pd.to_datetime(selected_end_time)
    timefiltered_df = de[(de['Valid'] >= selected_start_time) & (de['Valid'] <= selected_end_time)]

    model_filter = st.sidebar.selectbox('Select Model:', timefiltered_df['Model'].unique())
    filtered_df = timefiltered_df[timefiltered_df['Model'] == model_filter]
    var_list=['CAPE','KI','LI','SI','TT','RR','T2M','WSPD10M','DIV925',
              'DIV850','DIV700','DIV500','RH850','RH700','RH500']
    st.header('Model Evaluation')
  
    for n in range(1,len(var_list),2):
        col1, col2 = st.columns([1,1])
        with col1:
            boxplot(filtered_df,var_list[n-1])
        with col2:
            boxplot(filtered_df,var_list[n])
else:          
  url = 'https://web.meteo.bmkg.go.id//media/data/bmkg/verifikasi/Accuracy.txt'
  response = requests.get(url)
  data_text = response.text
  df = pd.read_csv(StringIO(data_text), delimiter=",")
  dall = pd.DataFrame({'Time':[datetime.datetime(2024,1,1)],
                      'Prov':['-Indonesia-'],
                      'Accuracy_SfcObs':[np.nan],
                      'Accuracy_TT':[np.nan],
                      'Accuracy_RH':[np.nan],
                      'Accuracy_GSMaP':[np.nan]})
  df = pd.concat([dall,df])
  df['Time'] = pd.to_datetime(df['Time'])
  
  # Sidebar filter
  selected_prov = st.sidebar.selectbox('Select Province:', df['Prov'].unique())
  selected_start_time = st.sidebar.date_input('Select The First Date:', df['Time'].min())
  selected_end_time = st.sidebar.date_input('Select The Last Date:', df['Time'].max())
  selected_start_time = pd.to_datetime(selected_start_time)
  selected_end_time = pd.to_datetime(selected_end_time)
  
  # Filter DataFrame berdasarkan pilihan pengguna
  timefiltered_df = df[(df['Time'] >= selected_start_time) & (df['Time'] <= selected_end_time)]
  
  # ====================================================================================
  prov_list = ['ACEH','SUMATERA UTARA','SUMATERA BARAT','RIAU','JAMBI','SUMATERA SELATAN','BENGKULU','LAMPUNG','KEPULAUAN BANGKA BELITUNG','KEPULAUAN RIAU','DKI JAKARTA','JAWA BARAT','JAWA TENGAH','DI YOGYAKARTA','JAWA TIMUR','BANTEN','BALI','NUSA TENGGARA BARAT','NUSA TENGGARA TIMUR','KALIMANTAN BARAT','KALIMANTAN TENGAH','KALIMANTAN SELATAN','KALIMANTAN TIMUR','KALIMANTAN UTARA','SULAWESI UTARA','SULAWESI TENGAH','SULAWESI SELATAN','SULAWESI TENGGARA','GORONTALO','SULAWESI BARAT','MALUKU','MALUKU UTARA','PAPUA BARAT','PAPUA']
  lat_list = [4.695135,2.1153547,-0.7399397,0.2933469,-1.4851831,-3.3194374,-3.5778471,-4.5585849,-2.7410513,3.9456514,-6.211544,-7.090911,-7.150975,-7.8753849,-7.5360639,-6.4058172,-8.4095178,-8.6529334,-8.6573819,-0.2787808,-1.6814878,-3.0926415,1.6406296,3.39529777,0.6246932,-1.4300254,-3.6687994,-4.14491,0.6999372,-2.8441371,-3.2384616,1.5709993,-1.3361154,-4.269928]
  lon_list = [96.7493993,99.5450974,100.8000051,101.7068294,102.4380581,103.914399,102.3463875,105.4068079,106.4405872,108.1428669,106.845172,107.668887,110.1402594,110.4262088,112.2384017,106.0640179,115.188916,117.3616476,121.0793705,111.4752851,113.3823545,115.2837585,116.419389,117.3777922,123.9750018,121.4456179,119.9740534,122.174605,122.4467238,119.2320784,130.1452734,127.8087693,133.1747162,138.0803529]
  
  coords = pd.DataFrame({'Prov':prov_list,'lon':lon_list,'lat':lat_list})
  df_merged1 = timefiltered_df[['Prov','Time','Accuracy_SfcObs']].groupby('Prov').mean().merge(coords, on='Prov')
  df_merged2 = timefiltered_df[['Prov','Time','Accuracy_GSMaP']].groupby('Prov').mean().merge(coords, on='Prov')
  
  def mapview(df):
      m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=4.4)
      # Membuat peta folium untuk custom marker
      color_scale = cm.LinearColormap(["blue", "green", "yellow", "red"], vmin=0, vmax=1)
      for i in range(len(df)):
          print(df['Accuracy_SfcObs'][i])
          folium.CircleMarker(
              location=[df['lat'][i], df['lon'][i]],
              radius=df['Accuracy_SfcObs'][i]*10,
              color=color_scale(df['Accuracy_SfcObs'][i]),  # Warna marker
              fill=True,
              fill_color=color_scale(df['Accuracy_SfcObs'][i]),
              fill_opacity=0.7,
              tooltip=f"{df['Prov'][i]} - Accuracy: {df['Accuracy_SfcObs'][i]*100}"
          ).add_to(m)
      color_scale.caption = 'Accuracy'
      color_scale.add_to(m)
      st_data = st_folium(m, width=700, height=400)
  
  if selected_prov=='-Indonesia-':
      filtered_df = df[(df['Time'] >= selected_start_time) & (df['Time'] <= selected_end_time)]
      st.header('General Overview of Accuracy Score')
      mapview(df_merged1)
      st.write(f'Overall the average of accuracy scores between {selected_start_time} to {selected_end_time}\
              are {round(timefiltered_df.Accuracy_SfcObs.mean()*100,1)}%(Surface based Obs) and {round(timefiltered_df.Accuracy_GSMaP.mean()*100,1)}% (GSMaP).\n\
              The lowest score based on surface based observation belong to {df_merged1["Prov"].iloc[df_merged1.Accuracy_SfcObs.idxmin()]}({round(df_merged1.Accuracy_SfcObs.min()*100,1)}%)\
              and based on GSMaP data belong to {df_merged1["Prov"].iloc[df_merged2.Accuracy_GSMaP.idxmin()]}({round(df_merged2.Accuracy_GSMaP.min()*100,1)}%).\
              Meanwhile, the highest score based on surface based observation belong to {df_merged1["Prov"].iloc[df_merged1.Accuracy_SfcObs.idxmax()]}({round(df_merged1.Accuracy_SfcObs.max()*100,1)}%)\
              and based on GSMaP data belong to {df_merged1["Prov"].iloc[df_merged2.Accuracy_GSMaP.idxmax()]}({round(df_merged2.Accuracy_GSMaP.max()*100,1)}%).')
  else:
      filtered_df = df[(df['Prov'] == selected_prov) & (df['Time'] >= selected_start_time) & (df['Time'] <= selected_end_time)]
      st.header('Table of Statistics')
      st.write('Area:', selected_prov)
      st.write('Time Range:', f'{selected_start_time} to {selected_end_time}')
  
      if selected_prov=='DKI JAKARTA':
          url_fct = 'https://raw.githubusercontent.com/alfuadi/streamlit/main/List_fct.txt'
          response_fct = requests.get(url_fct)
          data_text_fct = response_fct.text
          de_fct = pd.read_csv(StringIO(data_text_fct), delimiter=",")

          datelist = [datetime.datetime(y,m,d) for y,m,d in zip(de_fct['Tahun'],de_fct['Bulan'],de_fct['Tanggal'])]
          de_fct['Time'] = datelist
          dbof = pd.merge(de_fct,filtered_df, on='Time')
          acc_fct = dbof[['Forecaster','Accuracy_SfcObs','Accuracy_GSMaP']].groupby('Forecaster').mean().reset_index()
          st.dataframe(acc_fct)
  
      # Hitung nilai statistik
      min_Accuracy_SfcObs = filtered_df['Accuracy_SfcObs'].min()
      max_Accuracy_SfcObs = filtered_df['Accuracy_SfcObs'].max()
      mean_Accuracy_SfcObs = filtered_df['Accuracy_SfcObs'].mean()
  
      min_accuracy_gsmap = filtered_df['Accuracy_GSMaP'].min()
      max_accuracy_gsmap = filtered_df['Accuracy_GSMaP'].max()
      mean_accuracy_gsmap = filtered_df['Accuracy_GSMaP'].mean()
  
      # Tampilkan tabel
      statistic_table_data = {
          'Statistik': ['Akurasi Minimum', 'Akurasi Maksimum', 'Akurasi Rata-rata'],
          'Obs.Permukaan': [min_Accuracy_SfcObs, max_Accuracy_SfcObs, mean_Accuracy_SfcObs],
          'GSMaP': [min_accuracy_gsmap, max_accuracy_gsmap, mean_accuracy_gsmap]
      }
  
      statistic_table = pd.DataFrame(statistic_table_data)
      st.markdown(statistic_table.style.hide(axis="index").to_html(), unsafe_allow_html=True)
      # st.table(statistic_table)
  
  
  # ===============================Tampilkan tabel statistik================================
  # Grafik Time Series untuk Rata-rata Agregasi Seluruh Provinsi
  st.header('Time Series Graph')
  avg_df = filtered_df[['Time','Accuracy_SfcObs','Accuracy_GSMaP']].dropna().groupby('Time').mean().reset_index()
  fig_time_series = st.line_chart(avg_df, x='Time', y=['Accuracy_SfcObs', 'Accuracy_GSMaP'])
