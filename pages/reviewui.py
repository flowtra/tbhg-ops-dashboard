

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, time
from PIL import Image
import requests
import pandas as pd
from Dashboard import getCapacity, plot_gauge
from streamlit_extras.tags import tagger_component
import streamlit_antd_components as sac
from st_pages import show_pages_from_config, add_indentation


if __name__ == '__main__':
    im = Image.open("tbhg_favico.ico")
    st.set_page_config(page_title="Review UI", page_icon=im, layout="centered")
    # Either this or add_indentation() MUST be called on each page in your
    # app to add indendation in the sidebar
    add_indentation()

    show_pages_from_config()
    st.markdown(
        """
        <style>

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
        
        .name a {
        display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    def starBar(starVal: int):

        stars = ("★" * starVal) + ("☆" * (5-starVal))

        if starVal <= 2:
            tagger_component(
                "",
                [stars],
                color_name=["red"],
            )
        elif starVal == 3:
            tagger_component(
                "",
                [stars],
                color_name=["grey"],
            )
        else:
            tagger_component(
                "",
                [stars],
                color_name=["green"],
            )




    def reviewBlock(source, resvID, concept, stars, name, reviewText, reviewDate, reviewCreated):

        conceptColours = {
            'Afterwit': '#F39A3C',
            'Ela Jalan Sultan': '#79B48F',
            'The Great Mischief': '#ED7C74',
            'Tipo Osteria': '#308FDC',
            'Tipo Pasta Bar': '#9FE2D0',
            'Tipo Pizzeria': '#E67D7A',
            'Tipo Strada KS': '#F8C7AD',
            'Tipo Strada Novena': '#F8C7AD',
            'WT Lasalle': '#FFFFFF',
            'WT Riverside': '#FFFFFF'
        }

        col4, col5, butCol = st.columns([2.5,7,6])
        with col4:
            starBar(stars)
        with col5:

            # st.subheader('Haris Irfan')
            st.markdown(f'<h3 class="name">{name}</h3>', unsafe_allow_html=True)
        with butCol:
            if source == 'sevenrooms':
                sac.buttons([
                    sac.ButtonsItem(label=concept, color=conceptColours[concept]), #check country code thing
                    sac.ButtonsItem(icon='7-circle', href=f"https://wa.me/65", color='#0ecfc9'), #check country code thing
                ], align='end', direction="horizontal", variant='outline', key=resvID, index=None)
            elif source == 'google':
                sac.buttons([
                    sac.ButtonsItem(label=concept, color=conceptColours[concept]), #check country code thing
                    sac.ButtonsItem(icon='google', href=f"https://wa.me/65", color='#fcba03'), #check country code thing
                ], align='end', direction="horizontal", variant='outline', key=reviewCreated, index=None)

        if reviewText != None:
            st.markdown(f'<p>{reviewText}</p>', unsafe_allow_html=True)

        st.markdown(f'<p>Review left on {reviewDate}</p>', unsafe_allow_html=True)

        st.divider()


    title = "<h3 class='mainTitle'>SUCKER THOUGHTS | <img class='titleLogo' src='https://i.ibb.co/RcytMQh/tbhg-logo-FPrint.png'>THE BLACK HOLE GROUP</h3>"
    st.markdown(title, unsafe_allow_html=True)

    sdcol, edcol, filcol, lascol = st.columns([1,1,1,1])
    with sdcol:
        startDate = st.date_input("**Start Date**", value="default_value_today", key="startDate", on_change=None,
                                  args=None, kwargs=None, format="DD/MM/YYYY", label_visibility="visible").strftime("%Y-%m-%d")
    with edcol:
        endDate = st.date_input("**End Date**", value="default_value_today", key="endDate", on_change=None, args=None,
                                kwargs=None, format="DD/MM/YYYY", label_visibility="visible").strftime("%Y-%m-%d")
    with filcol:
        sentiment = st.selectbox('Sentiment',('All', 'AFIs Only', 'Praise Only', 'Mid Only'))

    reviewData = requests.get(f'http://0.0.0.0:8000/getAllReviews?start_date={startDate}&end_date={endDate}').json()

    with st.container(height=1000):

        st.markdown("""
                    <style>
                        @font-face {
                            font-family: 'Futura PT Bold';
                            font-style: normal;
                            font-weight: normal;
                            src: url('https://use.typekit.net/af/053fc9/00000000000000003b9af1e4/27/l?subset_id=2&fvd=n7&v=3') format('woff');
                        }

                        .body {
                            font-family: 'Futura PT Bold';
                        }

                        .name {
                            font-family: 'Futura PT Bold';
                            text-transform: uppercase;
                            margin-top: -7px;
                            margin-left: -5px;
                        }
                    </style>
                    """, unsafe_allow_html=True)

        for review in reviewData["reviews"]:
            if sentiment == 'AFIs Only':
                if review['stars'] <= 2:
                    reviewBlock(review['source'], review['resvID'],review['concept'], review['stars'], review['actual_name'], review['notes'], review['reviewDate'], review['created'])
                    print(f"{review['concept']} | {review['stars']} | {review['actual_name']} | {review['notes']}")

            elif sentiment == 'Praise Only':
                if review['stars'] >= 4:
                    reviewBlock(review['source'], review['resvID'],review['concept'], review['stars'], review['actual_name'], review['notes'], review['reviewDate'], review['created'])


