from .mtbf import MTBFCalculator
from .duanemodel import DuaneModelCalculator
from .test_sample_size import TestSampleSizeCalculator
from .dummy1 import DummyCalculator1
from .dummy2 import DummyCalculator2
from .dummy3 import DummyCalculator3

# Registry of all available calculators
CALCULATOR_REGISTRY = {
    "mtbf": MTBFCalculator(),
    "duane_model": DuaneModelCalculator(),
    "test_sample_size": TestSampleSizeCalculator(),
    "dummy_calculator_1": DummyCalculator1(),
    "dummy_calculator_2": DummyCalculator2(),
    "dummy_calculator_3": DummyCalculator3(),
}

def get_calculator(calculator_id: str):
    """Get calculator instance by ID"""
    if calculator_id not in CALCULATOR_REGISTRY:
        raise ValueError(f"Unknown calculator: {calculator_id}")
    return CALCULATOR_REGISTRY[calculator_id]

def list_calculators():
    """Get list of all available calculators with their info"""
    return [calc.info for calc in CALCULATOR_REGISTRY.values()]