from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
import asyncio
from streamlit_autorefresh import st_autorefresh
import requests
from st_pages import show_pages_from_config, add_page_title, add_indentation

async def watch(test):
    while True:
        test.markdown(
            f"""
            <p class="time">
                {str(datetime.now().strftime("%-d %B %Y"))} - {str(datetime.now().strftime("%I:%M:%S %p"))}
            </p>
            """, unsafe_allow_html=True)
        r = await asyncio.sleep(1)

def getLiveSeated(restID):
    liveSeated = allData[restID]
    return liveSeated


def getCapacity(restID: str):
    restID = str(restID)
    capacity = {
         "aw": 40,
         "ela": 62,
         "tgm": 92, #AVAIL 4x4 Parasols Outside
         "to": 43,
         "tpb": 76,
         "tpz": 90,
         "tsks": 46,
         "tsn": 38,
         "wtls": 105, #97 W/O T32, assuming 8 for T32
         "wtrs": 89 #43 L + 34 R + 12 OUT
    }
    restCap = capacity[restID]

    return restCap


def plot_gauge(indicator_number, indicator_color, indicator_title, max_bound):
    fig = go.Figure(
        go.Indicator(
            value=indicator_number,
            mode="gauge",
            domain={"x": [0, 1], "y": [0, 1]},
            # number={
            #     "suffix": f" / {max_bound}",
            #     "font.size": 20,
            #     "font.family": "Futura PT Bold"
            # },
            gauge={
                "axis": {"range": [0, max_bound], "tickwidth": 1},
                "bar": {"color": indicator_color},
            },
            title={
                "text": indicator_title.upper(),
                "font": {"size": 30, "family": "Futura PT Bold"},
            },
    )
    )
    fig.add_annotation(x=0.5, y=0.15,
                       text=f"{max_bound - indicator_number} AVAIL",
                       font={'size': 30, "family": "Futura PT Bold"},
                       showarrow=False)
    fig.add_annotation(x=0.5, y=-0.02,
                       text=f"{indicator_number} / {max_bound}",
                       font={'size': 20, "family": "Futura PT Bold"},
                       showarrow=False)
    fig.update_layout(
        # paper_bgcolor="lightgrey",
        height=200,
        margin=dict(l=10, r=10, t=60, b=10, pad=8),
    )
    fig.update_yaxes(automargin=True)

    st.plotly_chart(fig, use_container_width=True)

if __name__ == '__main__':
    im = Image.open("tbhg_favico.ico")
    st.set_page_config(page_title="BHG Ops Dashboard", page_icon=im, layout="wide")

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
        </style>
        """,
        unsafe_allow_html=True
    )
    title = "<h3 class='mainTitle'>LIVE SUCKERS | <img class='titleLogo' src='https://i.ibb.co/RcytMQh/tbhg-logo-FPrint.png'>THE BLACK HOLE GROUP</h3>"
    st.markdown(title, unsafe_allow_html=True)

    test = st.empty()

    allData = requests.get('http://fastapi:8000/getLiveSeated').json()
    column_1, column_2, column_3, column_4 = st.columns(4)

    with column_1:

        plot_gauge(getLiveSeated('tpb'), "#C4E2DA", "Tipo Pasta Bar", getCapacity('tpb'))
        plot_gauge(getLiveSeated('to'), "#004475", "Tipo Osteria", getCapacity('to'))

    with column_2:

        plot_gauge(getLiveSeated('tsn'), "#F8CFBA", "Tipo Strada Nov", getCapacity('tsn'))
        plot_gauge(getLiveSeated('tsks'), "#F8CFBA", "Tipo Strada KS", getCapacity('tsks'))
        plot_gauge(getLiveSeated('wtrs'), "#FFFFFF", "WT Riverside", getCapacity('wtrs'))

    with column_3:
        # plot_metric("Equity Ratio", 75.38, prefix="", suffix=" %", show_graph=False)
        plot_gauge(getLiveSeated('aw'), "#F37C49", "Afterwit",getCapacity('aw'))
        plot_gauge(getLiveSeated('ela'), "#87938B", "Éla", getCapacity('ela'))
        plot_gauge(getLiveSeated('wtls'), "#FFFFFF", "WT Lasalle", getCapacity('wtls'))

    with column_4:
        plot_gauge(getLiveSeated('tgm'), "#EB5747", "The Great Mischief", getCapacity('tgm'))
        plot_gauge(getLiveSeated('tpz'), "#B1696A", "Tipo Pizzeria", getCapacity('tpz'))

    count = st_autorefresh(interval=60000, limit=100, key="fizzbuzzcounter")
    asyncio.run(watch(test))
