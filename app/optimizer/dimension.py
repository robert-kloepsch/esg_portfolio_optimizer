import pandas as pd
import numpy as np
 

class SimulatedDimension():

    def __init__(self, name_in_df):
        self.name_in_df = name_in_df
    
    def dimension_mean(self, df: pd.DataFrame, pos_id: np.ndarray) -> list:
            mean = []
            if self.name_in_df == "cia_rating":
                for company in pos_id:
                    mean.append(float(df.query(f"pos_id == '{company}'")[self.name_in_df].values.mean()))   # type: ignore

            return mean

    def run_simulation_on_dimension(self, df: pd.DataFrame, pos_id: np.ndarray, weights) -> list:
        dimension_means = self.dimension_mean(df, pos_id)

        returns = pd.DataFrame()
        for company in pos_id:
            returns[company] = df.query(f"pos_id == '{company}'").reset_index()["market_price"].pct_change()

        means_per_sim = []
        for weight in weights:
            if self.name_in_df == "yearly_risk":
                means_per_sim.append(np.sqrt(np.dot(weight.T, np.dot(returns.cov() * 12, weight))))
            elif self.name_in_df == "yearly_return":
                means_per_sim.append(np.dot(returns.mean(), weight) * 12)
            else:
                means_per_sim.append(np.dot(dimension_means, weight))
        return means_per_sim


class RankedDimension:

    def __init__(self, name_in_df):
        self.name_in_df = name_in_df

    def rank(self, simulated_results, as_small_as_possible=True):
        ranking_df = pd.DataFrame({f'{self.name_in_df}': simulated_results})
        ranking_df[f"{self.name_in_df}_rank"] = ranking_df[self.name_in_df].rank()

        if as_small_as_possible == False:
            ranking_df[f"{self.name_in_df}_rank"] = ranking_df[f"{self.name_in_df}_rank"] * - 1 

        return ranking_df