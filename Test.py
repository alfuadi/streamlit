import streamlit as st
from PIL import Image
from io import BytesIO
import requests
import datetime

def get_images(dtype):
    image_urls = [
        f"https://publik.bmkg.go.id/cawo/inacawo/InaCAWO_{dtype}_6hr_Indo_{(datetime.datetime.today().replace(hour=0)+datetime.timedelta(hours=dh)).strftime('%Y%m%d%H')}0000.png" for dh in range(12,72,6)
    ]
    print(image_urls)
    images = [Image.open(BytesIO(requests.get(url).content)) for url in image_urls]
    return images

def imview(images,num_images):
    session_state = st.session_state
    if "current_index" not in session_state:
        session_state.current_index = 0

    if num_images == 0:
        st.error("Tidak ada file PNG dalam direktori yang diberikan.")
        return

    # Menampilkan gambar saat ini
    st.image(images[session_state.current_index])

    # Tombol Previous
    if st.button("Previous") and session_state.current_index > 0:
        session_state.current_index -= 1

    # Tombol Next
    if st.button("Next") and session_state.current_index < num_images - 1:
        session_state.current_index += 1

def main():
    st.title("InaCAWO Data Display Platform (BETA)")

    # Menampilkan tombol untuk memilih gambar berdasarkan timestamp
    datatypes = ["Mean", "POE5", "POE10", "POE20", "POE50"]
    selected_type = st.selectbox("Select a data type", datatypes)

    # Menampilkan gambar berdasarkan timestamp yang dipilih
    dtype = selected_type
    images = get_images(dtype)
    num_images = len(images)

    imview(images,num_images)

if __name__ == "__main__":
    main()
