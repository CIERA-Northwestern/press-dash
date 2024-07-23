'''Main dashboard class.
'''
import importlib
import os
import types
from typing import Union
import yaml

import pandas as pd
import streamlit as st

from . import user_utils as default_user_utils
from . import settings, interface, data_handler, aggregator, data_viewer

# We need to reload all the individual pieces if we want changes in them to propagate
for module in [settings, interface, data_handler, aggregator, data_viewer]:
    importlib.reload(module)

class DashBuilder:
    '''Main class for constructing dashboards.

    Args:
        config_fp: Path to the config file.
        user_utils: User-customized module for data loading
            and preprocessing.
    '''

    def __init__(
        self,
        config_fp: str,
        user_utils: types.ModuleType = None,
    ):

        if user_utils is None:
            user_utils = default_user_utils

        self.config = self.load_config(config_fp)
        self.settings = settings.Settings(self.config)
        self.interface = interface.Interface(self.config, self.settings)
        self.data_handler = data_handler.DataHandler(self.config, user_utils)
        self.agg = aggregator.Aggregator(self.config)
        self.data_viewer = data_viewer.DataViewer(self.config, self.settings)

    def load_config(self, config_fp: str) -> dict:
        '''Get the config. This is done once per session.
        The config directory is set as the working directory.

        Args:
            config_fp: Filepath for the config file.

        Returns:
            config: The config dictionary.
        '''

        config_dir, config_fn = os.path.split(config_fp)

        # Check if we're in the directory the script is in,
        # which should also be the directory the config is in.
        # If not, move into that directory
        if os.getcwd() != config_dir:
            os.chdir(config_dir)

        with open(config_fn, "r", encoding='UTF-8') as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
        return config

    @st.cache_data
    def prep_data(_self, config: dict) -> pd.DataFrame:
        '''Load, clean, and preprocess the data.

        *Note*: calculations cannot depend on any values updated during
        any cached functions (a.k.a. calculations cannot rely on any side effects)
        because streamlit caches outputs only.

        This is the one time that the config can be altered during execution,
        chosen as such to allow the user to modify the config on the fly,
        as these two functions are user defined.

        For this and other functions wrapped by a streamlit caching function,
        "self" must be replaced be preceeded by "_" to avoid streamlit
        trying to cache self.

        Args:
            config: The config dict.

        Returns:
            preprocessed_df: The preprocessed data.
            config: The config file. This will also be stored at self.config
        
        Side Effects:
            self.data_handler.data: Updates data stored.
            self.config: Possible updates to the stored config file.
        '''
        msg = 'Prepping data...'
        print(msg)
        with st.spinner(msg):
            data = {}
            data['raw'], config = _self.data_handler.load_data(config)
            data['cleaned'], config = _self.data_handler.clean_data(data['raw'], config)
            data['preprocessed'], config = _self.data_handler.preprocess_data(data['cleaned'], config)

            return data, config
 
    @st.cache_data
    def recategorize_data(
            _self,
            preprocessed_df: pd.DataFrame,
            new_categories: dict = None,
            recategorize: bool = True,
            combine_single_categories: bool = False,
        ) -> pd.DataFrame:
        '''Recategorize the data, i.e. combine existing categories into new ones.
        The end result is one category per article, so no articles are double-counted.
        However, if the new categories are ill-defined they can contradict one another
        and lead to inconsistencies.

        This is a wrapper for the same function in the data handler.
        Part of the motivation for being a wrapper is to limit data caching to the builder.

        Args:
            preprocessed_df: The dataframe containing the original data.
            new_categories: The new categories to use.
            recategorize: Whether to recategorize the data. Included for caching.
            combine_single_categories: If True, instead of leaving
                undefined singly-tagged entries alone,
                group them all into an "Other" category.

        Returns:
            recategorized: The dataframe containing the recategorized data.
                One entry per article.
        '''
        msg = 'Recategorizing data...'
        print(msg)
        with st.spinner(msg):
            return _self.data_handler.recategorize_data(
                preprocessed_df=preprocessed_df,
                new_categories=new_categories,
                recategorize=recategorize,
                combine_single_categories=combine_single_categories,
            )

    @st.cache_data
    def filter_data(
        _self,
        recategorized_df: pd.DataFrame,
        categorical_filters: dict[str, list] = {},
    ) -> pd.DataFrame:
        '''Filter what data shows up in the dashboard.

        Args:
            recategorized_df: The dataframe containing the data.
            text_filters (dict): Search fields for text.
            categorical_filters (dict): How categories are filtered.
            numerical_filters (dict): Ranges for numerical data filters

        Returns:
            selected_df: The dataframe containing the selected data.
        '''
        msg = 'Filtering data...'
        print(msg)
        with st.spinner(msg):
            return _self.data_handler.filter_data(
                recategorized_df=recategorized_df,
                categorical_filters=categorical_filters,
            )

    @st.cache_data
    def aggregate(
        _self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        groupby_column: str = None,
        aggregation_method: str = 'count',
    ) -> Union[pd.Series, pd.DataFrame]:
        '''Aggregate stats.
        
        Args:
            df: The dataframe containing the selected data.
            x_column: The column containing the year or other time bin value.
            weight_column: What to count up.
            groupby_column: The category to group the data by, e.g. 'Research Topics'.
                If not passed, then returns just the totals.
            aggregation_method: How to aggregate.

        Returns:
            sums: The dataframe containing the counts per year per category
                or
            totals: The series containing the counts per year
        '''
        

        msg = 'Aggregating...'
        print(msg)
        with st.spinner(msg):
            if aggregation_method == 'count':
                return _self.agg.count(
                    df=df,
                    x_column=x_column,
                    count_column=y_column,
                    groupby_column=groupby_column,
                )
            elif aggregation_method == 'sum':
                return _self.agg.sum(
                    df=df,
                    x_column=x_column,
                    weight_column=y_column,
                    groupby_column=groupby_column,
                )
            else:
                raise KeyError('Requested aggregation method "{}" is not available.'.format(aggregation_method))