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
        self,
        df: pd.DataFrame,
        x_column: str,
        count_column: str,
        groupby_column: str = None,
    ) -> Union[pd.Series, pd.DataFrame]:
        '''Count up stats, e.g. number of articles per year per category.

        Args:
            df: The dataframe containing the selected data.
            x_column: The column containing the year or other time bin value.
            count_column: What to count up.
            groupby_column: The category to group the data by, e.g. 'Research Topics'.
                If not passed, then returns just the totals.

        Returns:
            counts: The dataframe containing the counts per year per category
                or
            totals: The series containing the counts per year
        '''

        if groupby_column is None:
            totals = df.pivot_table(
                index=x_column,
                values=count_column,
                aggfunc='nunique',
            )
            totals.fillna( value=0, inplace=True )
            return totals
        else:
            counts = df.pivot_table(
                index=x_column,
                columns=groupby_column,
                values=count_column,
                aggfunc='nunique',
            )
            counts.fillna( value=0, inplace=True )
            return counts

    def sum(
        self,
        df: pd.DataFrame,
        x_column: str,
        weight_column: str,
        groupby_column: str = None,
    ) -> Union[pd.Series, pd.DataFrame]:
        '''Sum up stats, e.g. dollar amount per year.

        Args:
            df: The dataframe containing the selected data.
            x_column: The column containing the year or other time bin value.
            weight_column: What to count up.
            groupby_column: The category to group the data by, e.g. 'Research Topics'.
                If not passed, then returns just the totals.

        Returns:
            sums: The dataframe containing the counts per year per category
                or
            totals: The series containing the counts per year
        '''

        # We keep one entry per ID and group. This is to avoid double-counting.
        selected_for_sum_df = df.copy()
        if groupby_column is None:
            # For totals we only need one entry per ID.
            selected_for_sum_df.drop_duplicates( subset='id', keep='first', inplace=True )
            totals = selected_for_sum_df.pivot_table(
                values=weight_column,
                index=x_column,
                aggfunc='sum'
            )
            totals = totals.fillna( 0 )

            return totals
        else:
            selected_for_sum_df['id_and_group'] = df['id'].astype( str ) + df[groupby_column]
            selected_for_sum_df.drop_duplicates( subset='id_and_group', keep='first', inplace=True )
            summed = selected_for_sum_df.pivot_table(
                values=weight_column,
                index=x_column,
                columns=groupby_column,
                aggfunc='sum'
            )
            summed = summed.fillna( 0 )

            return summed