import streamlit as st
from PIL import Image
from io import BytesIO
import requests
import datetime

def on_button_click(dtype,selected_time):
    url = f"https://publik.bmkg.go.id/cawo/inacawo/InaCAWO_{dtype}_6hr_Indo_{selected_time}0000.png"  # Ganti dengan path sesuai struktur direktori Anda
    image_path = Image.open(BytesIO(requests.get(url).content))
    st.image(image_path, caption=f"Image {selected_time}", use_column_width=True)

def get_nearest_multiple_of_six_hours():
    current_time = datetime.datetime.now()
    rounded_hour = (current_time.hour // 6) * 6  # Mendapatkan kelipatan 6 jam terdekat
    return current_time.replace(hour=rounded_hour, minute=0, second=0, microsecond=0)

list_time = [(get_nearest_multiple_of_six_hours() + datetime.timedelta(hours=dh)).strftime('%Y%m%d%H') for dh in range(6, 72, 6)]

def create_buttons():
    button_clicked = None
    columns = st.columns(len(list_time))
    time1=None
    for i, time in enumerate(list_time):
        with columns[i]:
            button_label = f"{time[6:8]}\n{time[8:10]}"
            if st.button(button_label):
                button_clicked = button_label
                time1 = list_time[i]
            
    return button_clicked,time1
def imview(button_clicked,dtype,time):
    if button_clicked is not None and time is not None:
        on_button_click(dtype,time)
    else:
        st.info("Klik salah satu waktu")

def main():
    st.title("InaCAWO Data Display Platform (BETA)")
    
    # Menampilkan tombol untuk memilih gambar berdasarkan timestamp
    datatypes = ["Mean", "POE5", "POE10", "POE20", "POE50"]
    dtype = st.selectbox("Select a data type", datatypes)
    button_clicked,time=create_buttons()
    print(time)
    imview(button_clicked,dtype,time)

if __name__ == "__main__":
    main()
