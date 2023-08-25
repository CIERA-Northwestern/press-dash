'''Module for viewing data: Plotting, tables, etc.
'''
import copy
import re
import types
from typing import Tuple

import numpy as np
import pandas as pd
import streamlit as st

from .data_handler import DataHandler
from .settings import Settings

class DataViewer:
    '''Class for viewing data.

    Args:
        config: The config dictionary.
        data_handler: The data handler containing the relevant data.
    '''

    def __init__(self, config: dict, settings: Settings):
        self.config = config
        self.settings = settings

    def write(self, data, data_key: str=None, st_loc=st, columns: list[str]=None):
        '''Show a specified dataframe.

        Args:
            data: Data dict containing the data frames.
            data_key: key to search the data handler for.
                Defaults to providing a widget.
            st_loc: Where to show the data.
            columns: Columns to show. Defaults to all.
        '''

        if data_key is None:
            data_key = st_loc.radio(
                'View what data?',
                options=data.keys(),
                horizontal=True,
            )

        if data_key not in data:
            st.write('{} not found in data'.format( data_key ))
            return

        shown_df = data[data_key]
        if columns is not None:
            shown_df = shown_df[columns]

        st.write(data[data_key])

def get_tick_range_and_spacing( total, cumulative, ax_frac=0.1 ):
    '''Solid defaults for ymax and the tick_spacing.

    Args:
        total (pd.Series): The total counts or sums.
        cumulative (bool): Whether the data is cumulative.
        ax_frac (float): Fraction of axis between ticks.

    Returns:
        ymax (float): The maximum y value.
        tick_spacing (float): The spacing between ticks.
    '''

    # Settings for the lineplot
    if cumulative:
        ymax = total.sum().max() * 1.05
    else:
        ymax = total.values.max() * 1.05

    # Round the tick spacing to a nice number
    unrounded_tick_spacing = ax_frac * ymax
    tick_spacing = np.round( unrounded_tick_spacing, -np.floor(np.log10(unrounded_tick_spacing)).astype(int) )

    return ymax, tick_spacing
