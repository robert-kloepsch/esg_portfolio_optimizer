import pandas as pd
import numpy as np
import plotly.graph_objects as graph_objects
import hashlib
import pickle
import datetime


def visualise_three_dimension(standard_deviations: pd.Series, returns: pd.Series, ratings: pd.Series, ranking_df: pd.DataFrame) -> graph_objects.Figure:
    # Define a 3D scatter plot with 3 dimensions
    fig = graph_objects.Figure()

    # Define layout such as widt and height as well as axis names
    fig.update_layout(
        font=dict(size=14, color="black"),
        font_color="black",
        width=1000,
        height=1000,
        scene = dict(xaxis_title='Risk', yaxis_title='Return', zaxis_title='ESG Score')
    )

    fig.add_trace(
        graph_objects.Scatter3d(name="Simulations", x = standard_deviations, y = returns, z = ratings, mode ='markers', marker_color='#c0d0a1')
    )

    # Add the point out optimizer recommends. For this we take the first point of each dimension in our df sorted by the sum
    fig.add_trace(
        graph_objects.Scatter3d(name="Optimal Point", x = [standard_deviations[ranking_df.sort_values(by="rank_sum").index[0]]],
                    y = [returns[ranking_df.sort_values(by="rank_sum").index[0]]],
                    z = [ratings[ranking_df.sort_values(by="rank_sum").index[0]]],
                    mode='markers', marker_color='#698642', marker_size=13)
    )

    return fig


def visualise_two_dimension(standard_deviations: pd.Series, returns: pd.Series, ranking_df: pd.DataFrame) -> graph_objects.Figure:
    fig = graph_objects.Figure()
    fig.add_trace(graph_objects.Scatter(name="Simulations", x=standard_deviations, y=returns, mode ='markers', marker_color='#c0d0a1'))
    fig.add_trace(graph_objects.Scatter(name="Optimal Point", x=[standard_deviations[ranking_df.sort_values(by="rank_sum").index[0]]], y=[returns[ranking_df.sort_values(by="rank_sum").index[0]]], mode='markers', marker_color='#698642', marker_size=13))

    fig.update_layout(
        width=600,
        height=600,
        xaxis_title='Risk', 
        yaxis_title='Return',
        showlegend = True,
        font_color="black",
    )
    fig.update_layout(
    yaxis_title = dict(font = dict(size=20, color="black")),
    xaxis_title = dict(font = dict(size=20, color="black")),
    xaxis = dict(tickfont = dict(size=12, color="black")),
    yaxis = dict(tickfont = dict(size=12, color="black")))

    return fig


def get_hash(hash: list) -> str:
    '''Takes in a list of constraints and returns a coded hash'''

    hashed = pickle.dumps(hash, -1)

    return hashlib.md5(hashed).hexdigest()


def generate_sql_df(df: pd.DataFrame, pos_id: np.ndarray, weights, ranking_df: pd.DataFrame, number_of_simulations: int, token: str, src_weights) -> pd.DataFrame:
    '''Creates a df that includes all information that need to be send back to the db'''

    sql_df = pd.DataFrame(
        {"sim_id": get_hash([pos_id, datetime.datetime.now()]),
         "sim_valuationdate": df.drop_duplicates(subset="pos_id")["sim_valuationdate"],
         "sim_timestamp": datetime.datetime.now(),
         "sim_src_weight": src_weights,
         "sim_weight": weights[ranking_df.sort_values(by="rank_sum").index[0]],
         "sim_token": token}
    )

    currency = []
    isin = []

    for company in pos_id:
        currency.append(df.query(f"pos_id == '{company}'")["ccy"].iloc[0])
        isin.append(df.query(f"pos_id == '{company}'")["isin"].iloc[0])

    sql_df.insert(loc=3, column="sim_isin", value=isin)
    sql_df.insert(loc=4, column="sim_ccy", value=currency)
    sql_df.insert(loc=5, column="sim_amount_tries", value=number_of_simulations)

    return sql_df


def get_optimal_isin(results_df: pd.DataFrame, history_df: pd.DataFrame, matched_pos_id: np.ndarray) -> list:
    '''Takes the results df, gets the optimal pos id by the lowest rank sum and matches this pos_id with the corresponding isin in the original df'''
    selected_pos_id = matched_pos_id[results_df.sort_values(by="rank_sum").index[0]]  # type: ignore
    optimal_isin = history_df.query(f"pos_id == '{selected_pos_id}'")["isin"].unique()

    return optimal_isin.tolist()


def add_optimal_weights(df: pd.DataFrame, pos_id: np.ndarray, optimal_weights: list) -> pd.DataFrame:
    df["optimal_weights"] = 0

    for weight, pos_id in zip(optimal_weights, pos_id):
        df.loc[df["pos_id"] == pos_id, "optimal_weights"] = weight * 100

    return df