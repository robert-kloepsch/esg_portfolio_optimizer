from app.optimizer.data_loading import get_dataframe
from app.optimizer.selection import selector
from app.optimizer.configuration import database_name_get_data
from app.optimizer.configuration import column_names_get_data, columns_get_data_rename
from app.optimizer.preprocessing_tools import get_pos_id_match
from app.optimizer.postprocessing_tools import get_optimal_isin

def generate_selection_results(isin_list: list, token: str, conn) -> tuple[list, dict]:
    '''
    Takes an ISIN and a token as input. It compares this ISIN with other ISINs that match the base data and returns the best performing one 
    as well as its dimension results (return, risk, carbon score etc.)

    Args:
        isin (str): 
            A isin the user wants to run our selection on
        token (str): 
            Verifies the user

    Returns:
        optimized_values (list):
            Shows the optimal result for each dimension such as return or risk etc.
        optimal_isin (str):
            The optimal isin that the user should have. It can be the same as the input.
    '''

    #Get data and store in a dataframe. We define what columns we want and the correct renaming in the configuration.
    history_data = get_dataframe(conn, database_name_get_data, column_names_get_data, columns_get_data_rename, isin=[], isin_weight_match={})

    # Initiate some lists/dicts that we will store our results
    optimal_isins = []
    isin_source = {}

    # We loop through our isins to check for every isin if there is a better one. For every run we append the optimal isin to optimal_isins
    for isin in isin_list:
        # With get_pos_id_match we get a list of pos_ids, that match our criterias with our input isin. Information such as sector or assetclasses are the same with these pos_ids
        matched_pos_id = get_pos_id_match(history_data, isin)
        
        # If only one pos_id match exists we can just append this isin and skip the rest of the loop because no other alternative than the original isin exists.
        if matched_pos_id.size == 1:
            optimal_isins.append(isin)
            isin_source[isin] = [isin]
            continue
        else:
            # Run selection - in results df we get back the results for all our dimensions for all matching pos_ids. 
            results_df = selector(history_data, matched_pos_id)

            # Depending on the weights we get back the optimal isin with this function. This isin performs best under the defined criterias.
            optimal_isin = get_optimal_isin(results_df, history_data, matched_pos_id)
            optimal_isins.append(optimal_isin[0])

        # We create a dict which will show which isin was replaced by which isin or which multiple isins
        if optimal_isin[0] in isin_source:
            isin_source[optimal_isin[0]].append(isin)
        else:
            isin_source[optimal_isin[0]] = [isin]

    return optimal_isins, isin_source