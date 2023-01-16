from app.optimizer.configuration import database_name_get_data, column_names_get_data, columns_get_data_rename, constraint_columns
from app.optimizer.data_loading import get_dataframe
from app.optimizer.constraint import create_constraints
from app.optimizer.preprocessing_tools import prepare_optimization_dataframe
import numpy as np

def get_strategy(isin_list: list, weights: list, conn) -> dict:
    '''Takes in a list of isins and the corresponding weights and returns a dict with the strategy of this portfolio'''

    # Load the dataframe 
    history_data = get_dataframe(conn, database_name_get_data, column_names_get_data, columns_get_data_rename, isin_list, isin_weight_match={})
    # Apply some neccesarry modifications
    strategy_df = prepare_optimization_dataframe(history_data)
    
    # We loop through our isin list and apply all indices of the isins to a list
    indices = []
    for index, isin in enumerate(isin_list):
        if isin in strategy_df["isin"].to_list():
            indices.append(index)
        else:
            continue

    # We convert the weights to a numpy array so we can match the indices easily with our weights
    weights = np.array(weights)  # type: ignore
    final_weights = list(weights[indices])  # type: ignore

    # We append the weights to our df and call our function to get the strategy returned
    strategy_df["weights"] = final_weights
    strategy = create_constraints(strategy_df, constraint_columns)

    return strategy