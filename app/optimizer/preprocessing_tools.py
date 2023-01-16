from app.optimizer.constraint import get_weights_with_strategy
from app.optimizer.configuration import constraint_columns
import pandas as pd
import numpy as np


def get_coverage(df: pd.DataFrame, isin_list: list) -> tuple[float, list]:
    '''Takes in a df and a isin list and compares which of the ISINs in the isin list is in the df. Returns the coverage percentage and a list of not covered ISINs'''
    
    # Initiate two list two store covered and not covered ISINs
    covered = []
    not_covered = []
    # Get all ISINs that exist in our df
    isin_in_df = df["isin"].unique()

    # Append to the according list if isin is in the df or not
    for isin in isin_list:
        if isin in isin_in_df:
            covered.append(isin)
        else:
            not_covered.append(isin)

    return len(covered) / (len(covered) + len(not_covered)), not_covered


def get_weights_no_strategy(pos_id: np.ndarray) -> list:
    '''Takes np array of pos ids and creates random numbers with the amount of pos ids. All random numbers sum up to 1'''

    rand = np.random.random(len(pos_id))
    rand /= rand.sum()

    return rand


def get_pos_id_match(df: pd.DataFrame, isin: str) -> np.ndarray:
    '''Takes df and isin and returns all isins in the df that match certain criterias of the given isin'''
    # Get a list of criterias of the given isin
    try:
        criteria = df.query(f"isin == '{isin}'")[["sector", "continent", "ccy"]].iloc[0]
        # Search in the df of matches with the criterias
        match = df.query((f"sector == '{criteria[0]}' & continent == '{criteria[1]}' & ccy == '{criteria[2]}'"))["pos_id"].unique()
    except:
        match = np.ndarray(0)
        
    return match


def get_isin_source(isin_list: list) -> dict:
    isin_source = {}

    for isin in isin_list:
            isin_source[isin] = isin
    
    return isin_source


def get_pos_id(df: pd.DataFrame) -> np.ndarray:
    return df["pos_id"].unique()


def get_source_weights(df: pd.DataFrame) -> list:
    return df.drop_duplicates(subset="pos_id")["weights"].to_list()


def prepare_optimization_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates(subset="pos_id").reset_index()


def get_weights(number_of_simulations: int, keep_strategy: int, backtest: int, df: pd.DataFrame, strategy_list: dict, pos_id: np.ndarray):
    weights = []

    if keep_strategy == 0 and backtest == 0:
        for run in range(number_of_simulations):
            weights.append(get_weights_no_strategy(pos_id))

    elif keep_strategy == 1 and backtest == 0:
        weights = get_weights_with_strategy(df, constraint_columns, number_of_simulations, strategy_list)

    elif backtest == 1:
        weights = [np.array(df["weights"].to_list()) / 100]
    
    return weights


def add_random_weights(df: pd.DataFrame, pos_id: np.ndarray) -> pd.DataFrame:
    weights = get_weights_no_strategy(pos_id)  # type: ignore

    df["weights"] = 0

    for weight, pos_id in zip(weights, pos_id):
        df.loc[df["pos_id"] == pos_id, "weights"] = (weight * 100).round(2)

    return df


def convert_selected_isin_weight_match(isin_weight_match_old: dict, source_isin: dict, isin_list: list) -> dict:
    '''
    Takes in the old dict with the information which isin has which weight, the source isin dict which shows which isin have been replaced by which isin during selection and the optimal isin list.
    With this we create a new dict which assigns the weights to the new isins accordingly.
    '''
    isin_weight_match_new = {}
    for isin in set(isin_list):
        weight = 0
        for value in source_isin[isin]:
            weight += isin_weight_match_old[value]
        isin_weight_match_new[isin] = weight
    
    return isin_weight_match_new