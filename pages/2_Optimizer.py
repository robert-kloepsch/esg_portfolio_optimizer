import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go

from app.optimizer.data_loading import get_dataframe
from app.optimizer.configuration import database_name_get_data, column_names_get_data, columns_get_data_rename, request_dict, dimensions_dict
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
from app.optimizer.strategy_reader import get_strategy
from plotly.subplots import make_subplots
from streamlit import session_state as ss
from app.optimizer.simulation_results import generate_simulation_results
from app.optimizer.postprocessing_tools import visualise_two_dimension, visualise_three_dimension
import pandas as pd

st.set_page_config(layout="wide")  # type: ignore
st.subheader("Select your Portfolio")
connection = sqlite3.connect("finance_data")
conn = connection.cursor()

@st.cache()
def load_full_dataframe():
    connection = sqlite3.connect("finance_data")
    conn = connection.cursor()
    df = get_dataframe(conn, database_name_get_data, column_names_get_data, columns_get_data_rename, [], {})
    df = df.drop_duplicates(subset="isin")
    data = df[["isin", "sector", "ccy", "continent"]]

    df = pd.DataFrame(data)

    return df

@st.cache()
def filter_dataframe(df, isin_filter, sector_filter, currency_filter, continent_filter):

    if len(isin_filter) > 0:
        df = df[df["isin"].isin(isin_filter)]

    if len(sector_filter) > 0:
        df = df[df["sector"].isin(sector_filter)]

    if len(currency_filter) > 0:
        df = df[df["ccy"].isin(currency_filter)]
    
    if len(continent_filter) > 0:
        df = df[df["continent"].isin(continent_filter)]

    return df

def load_grid(filterd_dataframe):

    custom_css = {
    ".ag-theme-streamlit": {"--ag-range-selection-border-color": "#698642 !important",
                            "--ag-input-focus-border-color": "#698642 !important",
                            "--ag-row-hover-color": "#E1E7D9 !important",
                            "--ag-font-size": "10.5pt",
                            "--ag-header-foreground-color": "#31333f",
                            "--ag-header-background-color": "#E1E7D9 !important",
                            "--ag-checkbox-checked-color": "#698642",
                            "--ag-selected-row-background-color": "#E1E7D9"
                            }
    }

    gb = GridOptionsBuilder.from_dataframe(filterd_dataframe)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    gridoptions = gb.build()

    response = AgGrid(
        filterd_dataframe,
        custom_css=custom_css,
        height=250,
        gridOptions=gridoptions,
        enable_enterprise_modules=False,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        selectable=True
        )
    
    return response

def calculate_weights_equally(response):
    weights = []
    isins = []
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    columns = [col1, col2, col3, col4, col5, col6, col7, col8]
    run = 0
    count = 1
    for i in response["selected_rows"]:
        with columns[run]:
            if count == len(response["selected_rows"]):
                weight = st.number_input(i["isin"], 0.0, 100.0, float(100 - sum(weights)), disabled=True)
            else:
                weight = st.number_input(i["isin"], 0.0, 100.0, (100 / len(response["selected_rows"])).__round__(2), disabled=True)
            weights.append(weight)
            isins.append(i["isin"])
            count += 1
        if run == 7:
            run = 0
        else:
            run += 1
    
    return weights, isins

def enter_weights_manually(response):
    weights = []
    isins = []
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    columns = [col1, col2, col3, col4, col5, col6, col7, col8]
    run = 0
    count = 1
    for i in response["selected_rows"]:
        with columns[run]:
            if count == len(response["selected_rows"]):
                weight = st.number_input(i["isin"], 0.0, 100.0, 100 - sum(weights), 1.0)
            else:
                weight = st.number_input(i["isin"], 0.0, 100.0, (100 / len(response["selected_rows"])).__round__(2), 1.0)
            weights.append(weight)
            isins.append(i["isin"])
            count += 1
        if run == 7:
            run = 0
        else:
            run += 1
    
    return weights, isins

def auto_calculate(last, input_list_locked, total):
    change = ss.A + ss.B + ss.C - total
    last = input_list_locked.index(last)

    if ss[input_list_locked[last]] == 100 and len(input_list_locked) == 3:
        ss[input_list_locked[(last + 1) % len(input_list_locked)]] = 0
        ss[input_list_locked[(last + 2) % len(input_list_locked)]] = 0
    elif len(input_list_locked) > 1:
        run = 1
        for slider in range(len(input_list_locked) - 1):
            ss[input_list_locked[(last + run) % len(input_list_locked)]] -= change / (len(input_list_locked) - 1)
            run += 1
    else:
        ss[input_list_locked[0]] = ss[input_list_locked[0]]
    
def reset_input(input, locks):
    for reset in range(3):
        ss[input[reset]] = 33.33 
        ss[locks[reset]] = False 

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

dataframe_with_all_isins = load_full_dataframe()

st.write("**Filters**")

col1, col2, col3, col4 = st.columns(4)
with col1:
    isin_filter = st.multiselect("ISIN", dataframe_with_all_isins["isin"].unique())
with col2:
    sector_filter = st.multiselect("Sector", dataframe_with_all_isins["sector"].unique())
with col3:
    currency_filter = st.multiselect("Currency", dataframe_with_all_isins["ccy"].unique())
with col4:
    continent_filter = st.multiselect("Continent", dataframe_with_all_isins["continent"].unique())

filterd_dataframe = filter_dataframe(dataframe_with_all_isins, isin_filter, sector_filter, currency_filter, continent_filter)

st.write("**Pick your ISIN's**")

response = load_grid(filterd_dataframe)

st.write("#####")
portfolio_allocation_button = True

if len(response["selected_rows"]) < 2:
    st.write(f"You have **{len(response['selected_rows'])}** ISIN's selected. **A minimum of 2 are required to continue**")
else:
    st.write(f"You have **{len(response['selected_rows'])}** ISIN's selected.")

    st.write("#####")
    st.subheader("Weights per ISIN")
    st.write("#####")
    if st.checkbox("Adjust weights manually"):
        weights, isins = enter_weights_manually(response)
    else:
        weights, isins = calculate_weights_equally(response)
    
    if sum(weights) != 100.0:
        st.write("#####")
        st.write(f"**Total weights need to be 100. Currently they are {sum(weights)} - Please adjust!**")
        portfolio_allocation_button = True
    else:
        st.write("#####")
        st.write("#####")
        st.subheader("Your portfolio allocation")
        allocation = get_strategy(isins, weights, conn)

        sector = pd.DataFrame(allocation["sector"], index=[0])
        continent = pd.DataFrame(allocation["continent"], index=[0])
        currency = pd.DataFrame(allocation["ccy"], index=[0])

        irises_colors = ['rgb(33, 75, 99)', 'rgb(79, 129, 102)', 'rgb(151, 179, 100)', 'rgb(175, 49, 35)', 'rgb(36, 73, 147)']

        sector_labels = sector.T.reset_index()["index"].to_list()
        continent_labels = continent.T.reset_index()["index"].to_list()
        currency_labels = currency.T.reset_index()["index"].to_list()

        fig = make_subplots(1, 3, specs=[[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}]], subplot_titles=['<b>Sectors', '<b>Continent', '<b>Currency'])

        fig.add_trace(go.Pie(labels=sector_labels, values=sector.T.reset_index()[0], scalegroup='one', textinfo='label+percent', marker_colors=irises_colors), 1, 1)
        fig.add_trace(go.Pie(labels=continent_labels,values=continent.T.reset_index()[0], scalegroup='one', textinfo='label+percent', marker_colors=irises_colors), 1, 2)
        fig.add_trace(go.Pie(labels=currency_labels,values=currency.T.reset_index()[0], scalegroup='one', textinfo='label+percent', marker_colors=irises_colors), 1, 3)

        fig.update_layout(font=dict(size=14))
        fig.layout.annotations[0].update(y=1.05)  # type: ignore
        fig.layout.annotations[1].update(y=1.05)  # type: ignore
        fig.layout.annotations[2].update(y=1.05)  # type: ignore

        fig.update_layout(width=800, height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    if len(isins) > 0:

        st.subheader("**Optimization parameters**")
        st.write("#")

        col1, col2, col3 = st.columns(3)
        total = 100
        input_list = ['A','B','C']
        locked_list_reset = ['A1', 'B1', 'C1']
        locked_list = []

        with col1:
            locked_list.append(st.checkbox("Lock", key='A1'))
        with col2:
            locked_list.append(st.checkbox("Lock", key='B1'))
        with col3:
            locked_list.append(st.checkbox("Lock", key='C1'))

        input_list_locked = []
        for locks, input in zip(locked_list, input_list):
            if locks == False:
                input_list_locked.append(input)

        with col1:
            yearly_return = st.slider('Yearly return', key='A', min_value=0.0, max_value=100.0, value=33.0, on_change=auto_calculate, args=('A', input_list_locked, total), step=1.0, disabled=locked_list[0])
            st.write("#")
            number_of_simulations = st.number_input("Number of simultaions", 1000, value=1000, step=1000, help=("Min: 10 / Max: 10000"))
        with col2:
            yearly_risk = st.slider('Yearly risk', key='B', min_value=0.0, max_value=100.0, value=33.0, on_change=auto_calculate, args=('B', input_list_locked, total), step=1.0, disabled=locked_list[1])
            st.write("#")
            selection = st.selectbox("Alternative investment proposals", ("No", "Yes"), 
            help="Allow if ISINs can be replaced by better performing ISINs that have the same sector, assetclass & currency")
            if selection == "Yes":
                selection = 1
            else:
                selection = 0
        with col3:
            cia_rating = st.slider('ESG score', key='C', min_value=0.0, max_value=100.0, value=34.0, on_change=auto_calculate, args=('C', input_list_locked, total), step=1.0, disabled=locked_list[2])
            st.write("#")
            if len(isins) < 10:
                keep_strategy_disabled = True
            elif len(isins) >= 10:
                keep_strategy_disabled = False

            keep_strategy = st.selectbox("Keep strategy", ("No", "Yes"), disabled=keep_strategy_disabled, help="Keep current strategy of your selection. Min. 10 ISIN's required")
            if keep_strategy == "Yes":
                keep_strategy = 1
            else:
                keep_strategy = 0

        st.write('#')

        dimensions_dict["yearly_return"]["weight"] = yearly_return
        dimensions_dict["yearly_risk"]["weight"] = yearly_risk
        dimensions_dict["cia_rating"]["weight"] = cia_rating


    if len(isins) > 0:
        if st.button("Run Optimization"):
            request_dict["number_of_simulations"] = number_of_simulations
            request_dict["isin_list"] = isins
            request_dict["selection"] = selection
            request_dict["keep_strategy"] = keep_strategy
            isin_weight_match = {}
            for weight, isin in zip(weights, request_dict["isin_list"]):
                isin_weight_match[isin] = weight
            request_dict["isin_weight_match"] = isin_weight_match

            weights_and_isin, coverage, not_covered, results_df = generate_simulation_results(request_dict, conn)
            
            efficient_frontier_plot = visualise_two_dimension(results_df["yearly_risk"], results_df["yearly_return"], results_df)
            col1, col2 = st.columns(2)
            three_dimension_plot = visualise_three_dimension(results_df["yearly_risk"], results_df["yearly_return"], results_df["cia_rating"], results_df)

            st.write('#####')
            st.subheader("Visualisations")
            with st.expander("Efficient Frontier"):
                st.plotly_chart(efficient_frontier_plot, use_container_width=True)
            with st.expander("3D Plot"):
                st.plotly_chart(three_dimension_plot, use_container_width=True)

            st.write('#####')
            st.subheader("Optimized portfolio")
            st.write('#####')
            optimized_weights = [weight.__round__(2) for weight in list(weights_and_isin.values())]
            optimized_portfolio = pd.DataFrame({"ISIN": list(weights_and_isin.keys()), "Weight": optimized_weights})

            custom_css = {
            ".ag-theme-streamlit": {"--ag-range-selection-border-color": "#698642 !important",
                                    "--ag-input-focus-border-color": "#698642 !important",
                                    "--ag-row-hover-color": "#E1E7D9 !important",
                                    "--ag-font-size": "10.5pt",
                                    "--ag-header-foreground-color": "#31333f",
                                    "--ag-header-background-color": "#E1E7D9 !important",
                                    "--ag-checkbox-checked-color": "#698642",
                                    "--ag-selected-row-background-color": "#E1E7D9"
                                    }
            }

            gb = GridOptionsBuilder.from_dataframe(optimized_portfolio)
            gb.configure_column("ISIN", editable=True, sortable=True, singleClickEdit=True)
            gb.configure_column("Weight", editable=True, sortable=True, singleClickEdit=True)
            gridoptions = gb.build()

            response = AgGrid(
                optimized_portfolio,
                custom_css=custom_css,
                height=(len(optimized_portfolio) * 28) + 34,
                gridOptions=gridoptions,
                enable_enterprise_modules=False,
                update_mode=GridUpdateMode.MODEL_CHANGED,
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                fit_columns_on_grid_load=False,
                allow_unsafe_jscode=True,
                selectable=True
                )
            
            optimized_portfolio_download_file = convert_df(optimized_portfolio)
            st.download_button(
                label="Export as .csv file",
                data=optimized_portfolio_download_file,
                file_name='optimized_portfolio.csv'
            )