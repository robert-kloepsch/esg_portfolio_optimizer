import pandas as pd
import numpy as np
from ortools.sat.python import cp_model


def create_dict_weights(df: pd.DataFrame, model: cp_model.CpModel) -> dict:
    '''
    Takes in a df and adds as many weights to the model as long the df is. The weights can take min and max values - these are addionally modified to support randomization.
    Every weight is added to a dict and returned as a dict at the end
    '''
    count = 0
    dict_weights = {}

    for weight in range(len(df)):
        dict_weights[count] = model.NewIntVar(int(df["weights"].min() * len(df) / 2), int(df["weights"].max() * len(df) * 2), f"weight_{count}")
        count += 1

    return dict_weights


def create_weights_list(dict_weights: dict) -> list:
    '''Creates a simple list of all existing weights'''
    weights_full = []

    for weight in dict_weights:
        weights_full.append(dict_weights[weight])

    return weights_full


def randomize_model(dict_weights: dict, model: cp_model.CpModel, df: pd.DataFrame) -> None:
    '''Add a random int as a hint to the model to support randomization'''
    for weight in dict_weights:
        #model.AddHint(dict_weights[weight], np.random.randint(int(df["weights"].min() * len(df)), int(df["weights"].max() * len(df))))
        model.AddHint(dict_weights[weight], np.random.randint(1, 100))


def create_constraints(df: pd.DataFrame, constraint_columns: list) -> dict:
    '''Takes in a df and the columns the user wants to build constraints on. It reads the distribution of each column and saves it as a dict containing all constraints'''
    constraints = {}

    for column in constraint_columns:
        constraints[column] = dict(zip(df.groupby([column]).sum().reset_index()[column], df.groupby([column]).sum().reset_index()["weights"]))
        
    return constraints


def add_constraints(constraint_columns: list, df: pd.DataFrame, model: cp_model.CpModel, dict_weights, strategy_list: dict, weights_full: list) -> None:
    '''
    Adds constraints to the model. If user has specified constraints then it takes this otherwise it calls function 
    "create_constraints" to create the constrains out of the portfolios strategy
    '''
    if len(strategy_list) <= 0:
        constraints = create_constraints(df, constraint_columns)
        for constraint in constraints:
            for key in constraints[constraint]:
                keys = df.loc[df[constraint] == key].index
                model.Add(sum(list(map(dict_weights.get, keys))) >= int(constraints[constraint][key] * (len(df)) - ((constraints[constraint][key] * (len(df))) * 0.05)))
                model.Add(sum(list(map(dict_weights.get, keys))) <= int(constraints[constraint][key] * (len(df)) + ((constraints[constraint][key] * (len(df))) * 0.05)))
    else:
        constraints = strategy_list
        for constraint in constraints:
            for key in constraints[constraint]:
                keys = df.loc[df[constraint] == key].index
                model.Add(sum(list(map(dict_weights.get, keys))) >= int(constraints[constraint][key][0] * (len(df))))
                model.Add(sum(list(map(dict_weights.get, keys))) <= int(constraints[constraint][key][1] * (len(df))))
        
    carbon_score_var_list = []

    for id, weight in enumerate(weights_full):
        carbon_score_var = model.NewIntVar(0, 2100000, "carbon_var_" + str(id))
        model.AddMultiplicationEquality(carbon_score_var, int(df["cia_rating"].iloc[id] * 100), weight)
        carbon_score_var_list.append(carbon_score_var)

    model.Add(sum(carbon_score_var_list) < int(8.0 * len(df) * 10000))
    model.AddAllDifferent(weights_full)
    model.Add(sum(weights_full) > (99 * len(df)))


class VarArraySolutionCollector(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.solution_list = []
        self.__solution_count = 0

    def on_solution_callback(self):
        self.solution_list.append([self.Value(v) for v in self.__variables])
        self.__solution_count += 1
    
    def solution_count(self):
        return self.__solution_count


def get_weights_with_strategy(strategy_df: pd.DataFrame, constraint_columns: list, number_of_runs: int, strategy_list: dict) -> np.ndarray:
    '''Takes in the df, the columns we want to keep constraints, number of runs and the strategy list. It runs until the amount of solutions matches with the number of runs'''
    weights = []
    solver = cp_model.CpSolver()
    model = cp_model.CpModel()
    dict_weights = create_dict_weights(strategy_df, model)
    weights_full = create_weights_list(dict_weights)
    add_constraints(constraint_columns, strategy_df, model, dict_weights, strategy_list, weights_full)

    while len(weights) < number_of_runs:

        randomize_model(dict_weights, model, strategy_df)

        solver.parameters.cp_model_presolve = False # type: ignore 
        solver.parameters.max_time_in_seconds = 0.1  # type: ignore
        solution_collector = VarArraySolutionCollector(weights_full)

        solver.SolveWithSolutionCallback(model, solution_collector)

        for weight in solution_collector.solution_list:
            if weight in weights:
                continue
            else:
                weights.append(weight)
        print(len(weights), f"of {number_of_runs} solutions found", end='\r')

        model.ClearHints()

    return np.array(weights) / (len(strategy_df) * 100)