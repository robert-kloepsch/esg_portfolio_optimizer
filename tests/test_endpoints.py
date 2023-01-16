import pytest
from app.optimizer.strategy_reader import get_strategy
from app.optimizer.selection_results import generate_selection_results


@pytest.fixture(scope='module')
def fixture_isins():
    user_isins = ["XS1728036366", "US92189F1066", "GB00BVFNZH21", "LU1823376766"]
    return user_isins

@pytest.fixture(scope='module')
def fixture_weights():
    user_weights = [0.25, 0.25, 0.25, 0.25]
    return user_weights

@pytest.fixture(scope="module")
def fixture_selection_isins():
    selection_isins = ['CH0000222130', 'CH0441911739', 'CH1176493729', 'US88034P1093', 'HK0066009694', 'FR0010326140', 'NO0003054108', 'XS2330501995', 'US03852U1060', 'NL0000116150']
    return selection_isins

def test_strategy_reader(fixture_isins, fixture_weights, fxd_nucleus_engine):
    strategy = get_strategy(fixture_isins, fixture_weights, fxd_nucleus_engine)

    sum_category_values = 0
    for category in strategy:
        for category_value in strategy[category]:
            sum_category_values += 1

    assert sum_category_values == 7
    assert len(strategy) == 3

    assert strategy["sector"]["99"] == 0.5
    assert strategy["sector"]["40"] == 0.25
    assert strategy["sector"]["20"] == 0.25
    assert strategy["continent"]["1.0"] == 0.75
    assert strategy["continent"]["nan"] == 0.25
    assert strategy["ccy"]["GBP"] == 0.5
    assert strategy["ccy"]["USD"] == 0.5

def test_selection_results(fixture_selection_isins, fxd_nucleus_engine):
    optimal_isins, isin_source = generate_selection_results(fixture_selection_isins, "", fxd_nucleus_engine)
    assert len(set(optimal_isins)) == len(isin_source)
    assert len(set(optimal_isins)) == 9