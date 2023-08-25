'''Module for data aggregation.
'''
import copy
import re
import types
from typing import Union, Tuple

import numpy as np
import pandas as pd


class Aggregator:
    '''Class for summarizing data.
    Deals only with behavior---holds no state information
    beyond the config.

    Args:
        config: The config dictionary.
    '''

    def __init__(self, config: dict):

        self.config = config

    def count(
        df: pd.DataFrame,
        x_column: str,
        count_column: str,
        groupby_column: str = None,
    ) -> Union[pd.Series, pd.DataFrame]:
        '''Count up stats, e.g. number of articles per year per category or
        the number of people reached per year per category.

        Args:
            df: The dataframe containing the selected data.
            time_bin_column: The column containing the year or other time bin value.
            count_column: What to count up.
            groupby_column: The category to group the data by, e.g. 'Research Topics'.

        Returns:
            counts: The dataframe containing the counts per year per category.
            total: The series containing the counts per year, overall.
        '''

        if groupby_column is None:
            total = df.pivot_table(
                index=x_column,
                values=count_column,
                aggfunc='nunique',
            )
            total.fillna( value=0, inplace=True )
            return total
        else:
            counts = df.pivot_table(
                index=x_column,
                columns=groupby_column,
                values=count_column,
                aggfunc='nunique',
            )
            counts.fillna( value=0, inplace=True )
            return counts


