'''Module for handling data.
'''
import types

import pandas as pd


class DataHandler:
    '''Class for handling data.
    The data is loaded and pre-processed at initialization.

    Args:
        config (dict): The config dictionary.
        user_utils (module): User-customized module for data loading
    '''

    def __init__(self, config: dict, user_utils: types.ModuleType):
        self.config = config
        self.user_utils = user_utils

        self.dfs = {}
        self.dfs['raw'] = self.load_data()
        self.dfs['preprocessed'], self.config = self.preprocess_data(
            self.dfs['raw']
        )

    def load_data(self) -> pd.DataFrame:
        '''Load the data using the stored config and user_utils.

        Returns:
            raw_df: The data.

        Side Effects:
            self.config: Possible updates to the config file.
        '''
        raw_df, self.config = self.user_utils.load_data(self.config)
        self.dfs['raw'] = raw_df
        return raw_df

    def preprocess_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        '''Preprocess the data using the stored config and user_utils.

        Args:
            raw_df: The loaded data.

        Returns:
            preprocessed_df: The preprocessed data.

        Side Effects:
            self.config: Possible updates to the config file.
        '''
        preprocessed_df, self.config = self.user_utils.preprocess_data(
            raw_df, self.config
        )
        self.dfs['preprocessed'] = preprocessed_df
        return preprocessed_df
