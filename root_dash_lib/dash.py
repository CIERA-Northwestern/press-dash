'''Main dashboard class.
'''
import os
import types
import yaml

import pandas as pd

from . import user_utils as default_user_utils
from . import data_handler


class Dashboard:
    '''Root dashboard class.

    Args:
        config_fp: Path to the config file.
        user_utils: User-customized module for data loading
            and preprocessing.
    '''

    def __init__(
        self,
        config_fp: str,
        user_utils: types.ModuleType = default_user_utils,
    ):

        self.config = self.load_config(config_fp)
        self.data_handler = data_handler.DataHandler(self.config, user_utils)

    @property
    def data(self):
        '''Convenience property for accessing the dataframes.

        Returns:
            data (dict): The dataframes.
        '''
        return self.data_handler.data

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

    def prep_data(self, config: dict) -> pd.DataFrame:
        '''Load, clean, and preprocess the data.

        This is the one time that the config can be altered during execution,
        chosen as such to allow the user to modify the config on the fly,
        as these two functions are user defined.

        Args:
            config: The config dict.

        Returns:
            preprocessed_df: The preprocessed data.
            config: The config file. This will also be stored at self.config
        
        Side Effects:
            self.data_handler.data: Updates data stored.
            self.config: Possible updates to the stored config file.
        '''

        raw_df, self.config = self.data_handler.load_data(config)
        cleaned_df, self.config = self.data_handler.clean_data(raw_df, self.config)
        preprocessed_df, self.config = self.data_handler.preprocess_data(cleaned_df, self.config)

        return preprocessed_df, config
 
