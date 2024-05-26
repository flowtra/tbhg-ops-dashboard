

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, time
from PIL import Image
import requests
from Dashboard import getCapacity, plot_gauge
from st_pages import show_pages_from_config, add_indentation



def getSeatedAtTime(restID, time: str):
    global allRestShiftsDict
    projSeated = allRestShiftsDict[restID][time]

    return projSeated

if __name__ == '__main__':
    im = Image.open("tbhg_favico.ico")
    st.set_page_config(page_title="BHG Projected", page_icon=im, layout="wide")
    # Either this or add_indentation() MUST be called on each page in your
    # app to add indendation in the sidebar
    add_indentation()

    show_pages_from_config()
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
        
        
        </style>
        """,
        unsafe_allow_html=True
    )
    title = "<h3 class='mainTitle'>EVENT HORIZON | <img class='titleLogo' src='https://i.ibb.co/RcytMQh/tbhg-logo-FPrint.png'>THE BLACK HOLE GROUP</h3>"
    st.markdown(title, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        dateSet = st.date_input("**Select Date**", value="default_value_today", key="dateSet", on_change=None, args=None, kwargs=None, format="DD/MM/YYYY", label_visibility="visible").strftime("%d%m%Y")
    with col2:
        timeSet = st.time_input("**Select Time**", value=time(19, 0, 0), key="timeSet", on_change=None, args=None, kwargs=None, label_visibility="visible", step=1800).strftime("%H%M")

    allRestShiftsDict = requests.get(f'http://fastapi:8000/getAllProjectedSeated?date={dateSet}').json()

    st.text("")
    st.text("")

    column_1, column_2, column_3, column_4 = st.columns(4)

    with column_1:

        plot_gauge(getSeatedAtTime('tpb', timeSet), "#C4E2DA", "Tipo Pasta Bar", getCapacity('tpb'))
        plot_gauge(getSeatedAtTime('to', timeSet), "#004475",  "Tipo Osteria", getCapacity('to'))

    with column_2:

        plot_gauge(getSeatedAtTime('tsn', timeSet), "#F8CFBA", "Tipo Strada Novena", getCapacity('tsn'))
        plot_gauge(getSeatedAtTime('tsks', timeSet), "#F8CFBA", "Tipo Strada KS", getCapacity('tsks'))
        plot_gauge(getSeatedAtTime('wtrs', timeSet), "#FFFFFF", "WT Riverside", getCapacity('wtrs'))

    with column_3:
        # plot_metric("Equity Ratio", 75.38, prefix="", suffix=" %", show_graph=False)
        plot_gauge(getSeatedAtTime('aw', timeSet), "#F37C49", "Afterwit", getCapacity('aw'))
        plot_gauge(getSeatedAtTime('ela', timeSet), "#87938B", "Ela", getCapacity('ela'))
        plot_gauge(getSeatedAtTime('wtls', timeSet), "#FFFFFF", "WT Lasalle", getCapacity('wtls'))

    with column_4:
        plot_gauge(getSeatedAtTime('tgm', timeSet), "#EB5747", "The Great Mischief", getCapacity('tgm'))
        plot_gauge(getSeatedAtTime('tpz', timeSet), "#B1696A", "Tipo Pizzeria", getCapacity('tpz'))


#
