import streamlit as st
from PIL import Image


st.set_page_config(layout="wide")  # type: ignore
image = Image.open('app/ESG1.png')
st.image(image, width=360)
st.title("Portfolio Optimizer")
st.write("#####")
col_1, col_2 = st.columns(2)
with col_1:
    st.subheader("👋 Welcome to our innovative portfolio optimization platform!")
    st.markdown("With our tool, you can not only review your portfolio based on financial performance factors, but also on sustainable aspects. Our motivation for developing this platform primarily stems from the desire to raise awareness of the impact our investment decisions have on the environment and to give investors the opportunity to optimize their portfolios in an environmentally friendly way.   \n   \n Try it now and see how you can optimize your investments in an environmentally conscious way.   \n   \n Please note that the software is intended for testing purposes only and should not be used to perform actual optimizations.")