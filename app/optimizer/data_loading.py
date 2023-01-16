import sqlalchemy as sqa
import pandas as pd
import random


class NucleusEngine:
    def __init__(self, pyodbc_string):
        self.pyodbc = pyodbc_string
    
    def get_engine(self):
        engine = sqa.create_engine(sqa.engine.URL.create("mssql+pyodbc", query={"odbc_connect": self.pyodbc}))

        return engine


def get_connection(pyodbc_string: str) -> sqa.engine.base.Engine:
    '''Takes in a string with connection information and returns a sqa engine'''
    my_engine = NucleusEngine(pyodbc_string)
    conn = my_engine.get_engine()

    return conn


def get_dataframe(conn: sqa.engine.base.Engine, database_name_get_data: str, columns_get_data: str, columns_get_data_rename: list, isin: list, isin_weight_match: dict) -> pd.DataFrame:
    '''Takes in all neccesarry information to load data such as database name and isin list and returns a preprocessed dataframe'''
    # Create a tuple of our isin list so we can nicley use it in out sql request
    tuple_isin = tuple(isin)

    # Load dataframe. Three differen loading types depending on the lenght of the isin list
    if len(tuple_isin) == 0:
        df = pd.DataFrame(conn.execute(f'SELECT {columns_get_data} FROM {database_name_get_data}'))
    elif len(tuple_isin) == 1:
        df = pd.DataFrame(conn.execute(f"SELECT {columns_get_data} FROM {database_name_get_data} WHERE isin = '{isin[0]}'"))
    else:
        df = pd.DataFrame(conn.execute(f'SELECT {columns_get_data} FROM {database_name_get_data} WHERE isin IN {tuple_isin}'))

    # Rename columns
    df.columns = columns_get_data_rename

    # Change some datatypes
    df = df.astype({'market_price': 'float64'})
    df = df.astype({'sector': "str"})
    df = df.astype({'continent': "str"})

    # Replace NULL values for bia and cris rating with "business as usual" values
    df["cia_rating"] = df["cia_rating"].apply(lambda v: random.randint(5, 10))

    # Fill Nan values with 0
    df = df.fillna(0)

    # We add for every isin its corresponding weight match if the user has given it.
    if len(isin_weight_match) >= 1:
        df["weights"] = 0
        for index, row in df.iterrows():
            df.loc[df["isin"] == row["isin"], "weights"] = isin_weight_match[row["isin"]]
        df["weights"] = df["weights"] * (100 / df.drop_duplicates(subset="pos_id")["weights"].sum())

    return df