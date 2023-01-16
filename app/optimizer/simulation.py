import pandas as pd
import numpy as np
from app.optimizer.dimension import SimulatedDimension, RankedDimension
from app.optimizer.configuration import dimensions_dict
from app.optimizer.preprocessing_tools import prepare_optimization_dataframe, get_weights

def simulator(df: pd.DataFrame, pos_id: np.ndarray, number_of_runs: int, keep_strategy: int, backtest: int, strategy_list: dict):
    '''Simulates portfolio results on a given list of pos ids & number of runs and returns the best result by ranking them and apply the weights (importance) for each dimension'''
    
    # Do some neccesarry modifications on our dataframe before the simulation
    strategy_df = prepare_optimization_dataframe(df)

    # Get the weights depending on the type of request
    weights = get_weights(number_of_runs, keep_strategy, backtest, strategy_df, strategy_list, pos_id)

    # We initiate two dfs - one for the ranking, the ranking will define which is the best result. One for the results where we store the results
    ranking_df = pd.DataFrame()
    results_df = pd.DataFrame()

    # We loop through our dimensions that we want to measure
    for dimension in dimensions_dict:
        # Initiate a dimension with our class
        simulate = SimulatedDimension(dimension)
        # Get the means of the simulations 
        simulated = simulate.run_simulation_on_dimension(df, pos_id, weights)
        # Initiate a rank dimension
        rank = RankedDimension(dimension)
        # Rank the results we got by calling 'run_simulation_on_dimension'
        ranked = rank.rank(simulated, dimensions_dict[dimension]["as_small_as_possible"])
        # We add a column in our ranking df and store the results multiplied with the weight (importance)
        ranking_df[dimension] = ranked[f"{dimension}_rank"] * dimensions_dict[dimension]["weight"]
        # We add the ranking to our results df
        results_df = pd.concat([ranked, results_df], axis=1)

    # Calculate the ranking sum and add this as a new column to the ranking df
    ranking_df["rank_sum"] = ranking_df[ranking_df.columns].sum(axis=1)
    # Add the ranking sum to our results df by concatinating it
    results_df = pd.concat([results_df, ranking_df["rank_sum"]], axis=1)

    return results_df, weights