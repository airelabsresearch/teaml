import json
import yaml

try:
    from deepdiff import DeepDiff
except ImportError:
    DeepDiff = None

import teaml as tml

from .config import finance101yaml

def diff(a, b):
    return DeepDiff(a.root, b.root)

def test_load_save(finance101yaml):
    # Test load and save round trip
    fin = tml.loads(finance101yaml)
    original_json = json.dumps(fin.root, indent=2, sort_keys=True)
    out_json = json.dumps(yaml.safe_load(fin.dumps()), indent=2, sort_keys=True)
    assert original_json == out_json

def test_compute_build1(finance101yaml):
    fin = tml.loads(finance101yaml)
    result = fin.compute('Production Tax Credits')
    assert result == 6241500.0

def test_compute_build2(finance101yaml):
    fin = tml.loads(finance101yaml)
    result = fin.compute('AfterTax Operating')
    assert len(result) == 25

def test_compute_local(finance101yaml):
    if not DeepDiff:
        return
    fin = tml.loads(finance101yaml)
    fin.compute()
    tea = fin.copy()
    fin['SolarGenerationChargedtoBattery'] = '=200*365*1'
    assert tea.compute('SolarGenerationChargedtoBattery') == 73000
    assert diff(fin, tea) == {
        'values_changed': {
            "root['Finance101']['Inputs']['BESS']['Solar Generation Charged to Battery']": {
                'new_value': '=200*365*1 =73000',
                'old_value': '=200*365*1'}}}

def test_check_specials(finance101yaml):
    fin = tml.loads(finance101yaml)
    # These test name ambiguity
    assert fin['Solar Capacity'].value == 100
    assert fin['PV.SolarCapacity'].value == 100
    fin.compute()
    assert len(fin['Annual.Battery Maintenance'].value) == 25

def test_formulas(finance101yaml):
    fin = tml.loads(finance101yaml)
    assert fin.build_context('TotalAnnualSolarGeneration') == {
        'SolarCapacity': 100,
        'SolarCapacityFactor': 0.25}

def test_battery_mult(finance101yaml):
    fin = tml.loads(finance101yaml)
    assert len(fin.compute('Annual.BatteryOutput')) == 25

def test_npv(finance101yaml):
    fin = tml.loads(finance101yaml)
    assert fin.compute('NPV') == 68746191.83357899
