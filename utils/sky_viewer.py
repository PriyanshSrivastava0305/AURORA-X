import streamlit as st
from astroquery.skyview import SkyView

def show_tess_field(ra, dec):
    images = SkyView.get_images(position=f"{ra} {dec}", survey="DSS", radius=0.2)
    if images:
        st.image(images[0][0].data, caption="Sky View at Target Coordinates")
    else:
        st.warning("Could not retrieve image.")
