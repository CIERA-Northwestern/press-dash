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

    def __init__(self, config: dict, settings: Settings, data_handler: DataHandler):
        self.config = config
        self.settings = settings
        self.data_handler = data_handler

    def write(self, data_key: str=None, st_loc=st, columns: list[str]=None):
        '''Show a specified dataframe.

        Args:
            data_key: key to search the data handler for.
                Defaults to providing a widget.
            st_loc: Where to show the data.
            columns: Columns to show. Defaults to all.
        '''

        if data_key is None:
            data_key = st_loc.radio(
                'View what data?',
                options=self.data_handler.data.keys(),
                horizontal=True,
            )

        if data_key not in self.data_handler.data:
            st.write('{} not found in data'.format( data_key ))
            return

        shown_df = self.data_handler.data[data_key]
        if columns is not None:
            shown_df = shown_df[columns]

        st.write(self.data_handler.data[data_key])
