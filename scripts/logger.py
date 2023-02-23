import csv
import os
import time
from random import random

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = 15, 30

class GenericEntry():
    def __init__(
        self,
        values
    ):
      self.values = values

    def __repr__(self):
        return str(self.__dict__)

    def to_entry(self):
        return self.values

class GenericLogger:
    def __init__(self, path, headers):
        self.path = 'logs/' + path + '/'
        self.entries = []
        self.headers = headers
        os.makedirs(self.path, exist_ok=True)

    def add_entry(self, entry: GenericEntry):
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