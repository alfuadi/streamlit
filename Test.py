import streamlit as st
from PIL import Image
from io import BytesIO
import requests
import datetime

today = datetime.datetime.today().strftime('%Y%m%d')
def get_images():
    image_urls = [
        "https://publik.bmkg.go.id/cawo/inacawo/InaCAWO_Mean_6hr_Indo_"+today+"060000.png",
        "https://publik.bmkg.go.id/cawo/inacawo/InaCAWO_Mean_6hr_Indo_"+today+"120000.png",
        "https://publik.bmkg.go.id/cawo/inacawo/InaCAWO_Mean_6hr_Indo_"+today+"180000.png",
        "https://publik.bmkg.go.id/cawo/inacawo/InaCAWO_Mean_6hr_Indo_"+today+"000000.png",
        "https://publik.bmkg.go.id/cawo/inacawo/InaCAWO_Mean_6hr_Indo_"+today+"060000.png"
    ]
    images = [Image.open(BytesIO(requests.get(url).content)) for url in image_urls]
    return images

def main():
    st.title("Uji Coba menampilkan gambar")

    images = get_images()
    num_images = len(images)

    # Menggunakan session_state untuk menyimpan indeks saat ini
    session_state = st.session_state
    if "current_index" not in session_state:
        session_state.current_index = 0

    if num_images == 0:
        st.error("Tidak dapat mengambil gambar dari tautan yang diberikan.")
        return

    # Menampilkan gambar saat ini
    st.image(images[session_state.current_index])

    # Tombol Previous
    if st.button("Previous") and session_state.current_index > 0:
        session_state.current_index -= 1

    # Tombol Next
    if st.button("Next") and session_state.current_index < num_images - 1:
        session_state.current_index += 1

    # Menampilkan tombol untuk memilih gambar berdasarkan timestamp
    timestamps = ["060000", "090000", "120000", "150000", "180000"]
    selected_timestamp = st.selectbox("Select a timestamp", timestamps)

    # Menampilkan gambar berdasarkan timestamp yang dipilih
    if st.button("Show Image"):
        try:
            index = timestamps.index(selected_timestamp)
            st.image(images[index])
        except ValueError:
            st.warning("Timestamp not found.")

if __name__ == "__main__":
    main()
