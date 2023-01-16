import pandas as pd
from app.optimizer.simulation import simulator
from app.optimizer.configuration import database_name_get_data, column_names_get_data, columns_get_data_rename
from app.optimizer.preprocessing_tools import get_pos_id, get_source_weights, add_random_weights, get_coverage, get_isin_source, convert_selected_isin_weight_match
from app.optimizer.postprocessing_tools import add_optimal_weights, generate_sql_df
from app.optimizer.data_loading import get_dataframe
from app.optimizer.selection_results import generate_selection_results


def generate_simulation_results(request_dict: dict, conn) -> tuple[dict, float, list, pd.DataFrame]:
    '''
    The tool connects to a db, gets the data, simulates the number of simulations, calculates the result for each dimension and returns the best possible allocation (weights) 
    of the isins depending on the user defined weights (importance of each dimension)
    It also sends the results back into a db

    Args:
        number_of_simulations (int): 
            Defines how many simulations are performed
        token (str): 
            Verifies the user
        keep_strategy (int): 
            Defines, if user wants to keep the strategy in his portfolio (0=no, 1=yes)
        strategy_list (dict):
            Exactly tell the program a desired outcome. The user needs to give a range for each constraint dimension as a list with to integers.x
            If strategy list is empty, the strategy of the given portfolio will be taken and kept for optimization.

    Returns:
        weights_and_isins (dict):
            Combines the optimal isins and its corresponding weights -> Gives an overview on what percentage of each isin is reccommended to get the best result
        optimized_values (list):
            Shows the optimal result for each dimension such as return or risk etc.
        coverage (float):
            Percentage of covered isins in our db compared to the users input list
        not_covered (list):
            List of isin that have been provided by the user but are not covered in our db
    '''

    number_of_simulations = request_dict["number_of_simulations"]
    isin_list = request_dict["isin_list"]
    token = request_dict["token"]
    keep_strategy = request_dict["keep_strategy"]
    selection = request_dict["selection"]
    backtest = request_dict["backtest"]
    strategy_list = request_dict["strategy_list"]
    portfolio_id = request_dict["portfolio_id"]
    isin_weight_match = request_dict["isin_weight_match"]

    # If the user allows alternative investment proposals (selection) then we create an optimal isin list and new isin source with generate_selection_results
    # Additionally we also need to update our isin_weight_match dict as it can include different isins depending on the selection results
    if selection == 1:
        isin_list, isin_source = generate_selection_results(isin_list, "", conn)
        isin_weight_match = convert_selected_isin_weight_match(isin_weight_match, isin_source, isin_list)
    else:
        isin_source = get_isin_source(isin_list)

    # Load the dataframe
    history_data = get_dataframe(conn, database_name_get_data, column_names_get_data, columns_get_data_rename, isin_list, isin_weight_match)

    # Call a function that will return a list with isins that are covered in our database and one that are not covered
    coverage, not_covered = get_coverage(history_data, list(set(isin_list)))

    # Define pos_id's to use - with unique() we get all pos_id´s that exist in the dataframe (but filterd depending on isin list of user due to the where string)
    pos_id = get_pos_id(history_data)

    # With this function we add random weights to each pos_id into our dataframe. This is only temporary because we do not have the actual weights yet
    if len(isin_weight_match) == 0:
        history_data = add_random_weights(history_data, pos_id)

    # Run optimization 
    results_df, weights = simulator(history_data, pos_id, number_of_simulations, keep_strategy, backtest, strategy_list)

    # The lowest rank_sum in our results_df reflects the optimal point. Here we take the corresponding weight out of our weights list
    optimal_weights = weights[results_df.sort_values(by = "rank_sum").index[0]]  # type: ignore

    # We add the optimal weights per pos_id to our original dataframe
    history_data = add_optimal_weights(history_data, pos_id, optimal_weights)

    # Generate a list that will include all weights of all isins
    src_weights = get_source_weights(history_data)

    # Generate sql dataframe. These results will be send to the sql database
    sql_df = generate_sql_df(history_data, pos_id, weights, results_df, number_of_simulations, token, src_weights)

    # Prepare data for api response
    optimized_weights = sql_df["sim_weight"]
   
    # Combine list of isins and weights to nicely see which isin has which weight
    weights_and_isin = dict(zip(sql_df["sim_isin"], optimized_weights))

    return weights_and_isin, coverage, not_covered, results_df