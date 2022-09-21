from brownie import *
from dotmap import DotMap
import pytest

@pytest.fixture
def deployer():
    return accounts[0]

@pytest.fixture
def user():
    return accounts[1]

@pytest.fixture
def rando():
    return accounts[6]

## Forces reset before each test
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


