import csv
import os
import time
from random import random

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = 15, 30

class CsvEntry():
    def __init__(self) -> None:
        pass

class AmmPriceImpactEntry(CsvEntry):
    def __init__(
        self,
        run,
        deposited_eth,
        borrowed_btc,
        max_liquidatable,
        reserve_btc,
        reserve_eth,
        initial_price,
        liquidatable_collateral,
        profitability_bps,
        max_price,
        max_amount
    ):
        self.run = run,
        self.deposited_eth = deposited_eth,
        self.borrowed_btc = borrowed_btc,
        self.max_liquidatable = max_liquidatable,
        self.reserve_btc = reserve_btc,
        self.reserve_eth = reserve_eth,
        self.initial_price = initial_price,
        self.liquidatable_collateral = liquidatable_collateral,
        self.profitability_bps = profitability_bps,
        self.max_price = max_price,
        self.max_amount = max_amount

    def __repr__(self):
        return str(self.__dict__)

    def to_entry(self):
        # TODO: Why are these all returning tuples?
        return [
            self.run[0],
            self.deposited_eth[0],
            self.borrowed_btc[0],
            self.max_liquidatable[0],
            self.reserve_btc[0],
            self.reserve_eth[0],
            self.initial_price[0],
            self.liquidatable_collateral[0],
            self.profitability_bps[0],
            self.max_price[0],
            self.max_amount
        ]

class AmmPriceImpactLogger:
    def __init__(self):
        self.path = 'logs/amm_price_impact_sims/'
        self.entries = []
        self.headers = [
            "run",
            "deposited_eth",
            "borrowed_btc",
            "max_liquidatable",
            "reserve_btc",
            "reserve_eth",
            "initial_price",
            "liquidatable_collateral",
            "profitability_bps",
            "max_price",
            "max_amount"
            
        ]
        os.makedirs(self.path, exist_ok=True)

    def add_entry(self, entry: AmmPriceImpactEntry):
        self.entries.append(entry)

    def __repr__(self):
        return str(self.__dict__)

    def to_csv(self):
        # Create a file with current time as name
        filename = f'{self.path}/{pd.Timestamp.now()}.csv'

        with open(filename, 'w', encoding='UTF8') as f:
            writer = csv.writer(f)

            # write the header
            writer.writerow(self.headers)

            # write the data
            for entry in self.entries:
                writer.writerow(entry.to_entry())

    def plot_to_png(self):
        filename=f'{self.path}/{pd.Timestamp.now()}.png'
        # convert CsvEntry objects to a single DataFrame
        df = (pd.DataFrame(self.entries)[0]
              .astype(str)
              .map(eval)
              .apply(pd.Series)
              .set_index('run')
              )
        print(df.info())
        df.style.set_caption("Hello World")

        # generate subplot for every column; save to single png
        constants = ['liquidatable_collateral', 'max_price']
        fig, axes = plt.subplots()
        df.drop(constants, axis='columns').plot(
            subplots=True, ax=axes,
            # title=[
            #     'Title1', 'Title2', 'Title3',
            #     'Title1', 'Title2', 'Title3',
            #     'Title1', 'Title2', 'Title3',
            #     'Title1', 'Title2', 'Title3',
            #     'Title1', 'Liquidations', "Is_Solvent (Bool)"
            # ]
        )
        # fig.set_size_inches(10, 100)
        title = f'liquidatable_collateral: {df["liquidatable_collateral"].max()}\nmax_price: {df["max_price"].max()}\n'
        fig.tight_layout()
        fig.suptitle(title, fontsize=14, fontweight='bold')
        fig.savefig(filename, dpi=200)

