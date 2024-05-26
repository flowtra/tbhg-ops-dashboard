

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, time
from PIL import Image
import requests
import pandas as pd
from Dashboard import getCapacity, plot_gauge
from streamlit_extras.tags import tagger_component


if __name__ == '__main__':
    im = Image.open("tbhg_favico.ico")
    st.set_page_config(page_title="BHG Reviews", page_icon=im, layout="wide")

    st.markdown(
        """
        <style>
        .body {
            /* background-color: #141313; */
            /* background-color: #594747 !important; */
        }
        .time {
            font-size: 30px !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            /* margin-top:-50px !important; */
            margin-bottom: 60px !important;
            font-family: 'Futura PT Bold';
            text-transform: uppercase;
            text-align: center;

        }
        @font-face {
            font-family: 'Futura PT Bold';
            font-style: normal;
            font-weight: normal;
            src: url('https://use.typekit.net/af/053fc9/00000000000000003b9af1e4/27/l?subset_id=2&fvd=n7&v=3') format('woff');
            }

        .mainTitle {
            font-family: 'Futura PT Bold';
            font-size: 56px !important;
            text-align: center;
            margin-top: -40px;
        }

        .titleLogo {
            height: 60px;
            width: 60px;
            margin-right: 20px;
            margin-top: -7px;
        }
        / *
        .stDateInput p {
            font-family: 'Futura PT Bold' !important;
            text-transform: uppercase;
            font-size: 15px;
            margin-left: 4px;
        }
        
        @media screen and (min-width: 1500px) {
            .stDateInput {
                max-width: 600px;
                margin-left: 175px;
            }
            
            .stTimeInput {
                max-width: 600px;
            }
        }
        
        .stTimeInput p {
            font-family: 'Futura PT Bold' !important;
            text-transform: uppercase;
            font-size: 15px;
            margin-left: 4px;
        }
        */
        
        </style>
        """,
        unsafe_allow_html=True
    )
    title = "<h3 class='mainTitle'>SR REVIEWS | <img class='titleLogo' src='https://i.ibb.co/RcytMQh/tbhg-logo-FPrint.png'>THE BLACK HOLE GROUP</h3>"
    st.markdown(title, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        startDate = st.date_input("**Start Date**", value="default_value_today", key="startDate", on_change=None, args=None, kwargs=None, format="DD/MM/YYYY", label_visibility="visible").strftime("%Y-%m-%d")
    with col2:
        endDate = st.date_input("**End Date**", value="default_value_today", key="endDate", on_change=None, args=None, kwargs=None, format="DD/MM/YYYY", label_visibility="visible").strftime("%Y-%m-%d")

    allReviews = requests.get(f'http://0.0.0.0:8000/getAllSevenroomsReviews?start_date={startDate}&end_date={endDate}').json()
    df = pd.DataFrame.from_records(allReviews["reviews"])
    df.drop('created', axis=1)

    st.text("")
    st.text("")

    st.dataframe(df)
    st.experimental_data_editor(df)


#
