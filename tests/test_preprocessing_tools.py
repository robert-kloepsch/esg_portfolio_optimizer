import pytest
from app.optimizer.preprocessing_tools import get_weights_no_strategy, get_coverage, get_isin_source, get_weights, get_pos_id, prepare_optimization_dataframe
import numpy as np
import pandas as pd


@pytest.fixture(scope='module')
def fixture_weights_no_strategy_ndarray():
    return np.ndarray([1, 2, 3, 4, 5, 6])

@pytest.fixture(scope='module')
def fixture_dataframe():
    df = pd.read_csv("dataframe_for_unit_tests.csv")
    return pd.DataFrame(df)

@pytest.fixture(scope='module')
def fixture_isins():
    user_isins = ["XS1728036366", "US92189F1066", "GB00BVFNZH21", "LU1823376766", "This_Isin_Is_Not_In_The_DF"]
    return user_isins

def test_sum_and_length_of_get_weights_no_strategy(fixture_weights_no_strategy_ndarray):
    list = get_weights_no_strategy(fixture_weights_no_strategy_ndarray)
    assert sum(list) == 1
    assert len(list) == len(fixture_weights_no_strategy_ndarray)

def test_coverage_percentage_and_not_covered_list(fixture_dataframe, fixture_isins):
    percentage, not_covered = get_coverage(fixture_dataframe, fixture_isins)
    assert percentage == 0.8
    assert not_covered == ["This_Isin_Is_Not_In_The_DF"]

def test_length_of_isin_source(fixture_isins):
    isin_source = get_isin_source(fixture_isins)
    assert len(isin_source) == len(fixture_isins)

def test_length_of_weights(fixture_dataframe):
    pos_id = get_pos_id(fixture_dataframe)
    weights_no_strategy = get_weights(number_of_simulations=1, keep_strategy=0, backtest=0, df=fixture_dataframe, strategy_list={}, pos_id=pos_id)
    assert len(weights_no_strategy[0]) == len(fixture_dataframe.drop_duplicates(subset="pos_id"))

def test_dataframe_length_after_preparation(fixture_dataframe):
    pos_id = get_pos_id(fixture_dataframe)
    df_length_check = prepare_optimization_dataframe(fixture_dataframe)
    assert len(df_length_check) == len(pos_id)