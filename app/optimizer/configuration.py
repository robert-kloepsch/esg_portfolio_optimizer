# Define the dimensions that will be used and also define if this dimension needs to be as small as possible / True -> as small as possible 
# and the default weight if the user does not specify. If the user specifies a weight, this dict will be adjusted accordingly
dimensions_dict = {"yearly_risk": {"as_small_as_possible": True, "weight": 33},
                   "yearly_return": {"as_small_as_possible": False, "weight": 33},
                   "cia_rating": {"as_small_as_possible": True, "weight": 33}}

# This dict will be updated with our api request and defines the parameters for each simulation
request_dict = {"number_of_simulations": 1, "isin_list": [], "token": "", "keep_strategy": 0, 
                "selection": 0, "backtest": 0, "strategy_list": {}, "portfolio_id": "", 
                "isin_weight_match": {}}

# Name of the database where we get our data from
database_name_get_data = ('isin_data')
                         
column_names_get_data = ('pos_id,'
                         'sim_valuationdate,'
                         'isin,' 
                         'market_price,'
                         'cia_rating,'
                         'sector,'
                         'continent,' 
                         'ccy')

# The renaming of columns for the dataframe used in this Script
columns_get_data_rename = ["pos_id",  
                           "sim_valuationdate", 
                           "isin", 
                           "market_price", 
                           "cia_rating", 
                           "sector", 
                           "continent", 
                           "ccy"] 

# List of columns that we will take in consideration if the stratgy needs to be kept
constraint_columns = ["sector", "continent", "ccy"]