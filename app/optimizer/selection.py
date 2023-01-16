import pandas as pd
import numpy as np
from app.optimizer.dimension import SimulatedDimension, RankedDimension
from app.optimizer.configuration import dimensions_dict

def selector(df: pd.DataFrame, matched_pos_id: np.ndarray):
    '''Takes a df and array with pos_ids as input. Compares the performance of every pos_id and returns a df with the results of each pos_id'''

    # We initiate two dfs - one for the ranking, the ranking will define which is the best result. One for the results where we store the results
    ranking_df = pd.DataFrame()
    results_df = pd.DataFrame()

    # We loop through our dimensions that we want to measure
    for dimension in dimensions_dict:
        # Initiate a dimension with our class
        dim = SimulatedDimension(dimension)
        # We get the mean of this dimension by calling our function for it
        dim_mean = dim.dimension_mean(df, matched_pos_id)
        # Initiate a rank dimension with our class
        rank = RankedDimension(dimension)
        # We rank our results
        ranked = rank.rank(dim_mean, dimensions_dict[dimension]["as_small_as_possible"])
        # We add a column in our ranking df and store the results multiplied with the weight (importance)
        ranking_df[dimension] = ranked[f"{dimension}_rank"] * dimensions_dict[dimension]["weight"]
        # We add the ranking to our results df
        results_df = pd.concat([ranked, results_df], axis=1)

    # Calculate the ranking sum and add this as a new column to the ranking df
    ranking_df["rank_sum"] = ranking_df[ranking_df.columns].sum(axis=1)
    # Add the ranking sum to our results df by concatinating it
    results_df = pd.concat([results_df, ranking_df["rank_sum"]], axis=1)

    return results_df                          