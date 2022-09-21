from brownie import *
from dotmap import DotMap
import pytest

def main():
  deploy_contract()

def deploy_contract():
  MyContract.deploy({"from": a[0]})