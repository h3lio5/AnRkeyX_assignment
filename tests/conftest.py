import py
from urllib3 import Retry
from brownie import Wei, accounts
from brownie import ERC20, LinearVestingToken
import pytest


@pytest.fixture(scope="function")
def owner():
    return accounts[0]


@pytest.fixture(scope="function")
def alice():
    return accounts[1]


@pytest.fixture(scope="function")
def bob():
    return accounts[2]


@pytest.fixture(scope="function")
def charlie():
    return accounts[3]


@pytest.fixture(scope="function")
def dai(owner):
    return ERC20.deploy("MakerDAI", "DAI", Wei(1e18), {"from": owner})


@pytest.fixture(scope="function")
def lusd(owner):
    return ERC20.deploy("Liquity USD", "LUSD", Wei(1e18), {"from": owner})


@pytest.fixture(scope="function")
def vestingContract(owner):
    return LinearVestingToken.deploy({"from": owner})
