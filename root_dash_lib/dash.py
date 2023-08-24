'''Main dashboard class.
'''
import os
import yaml

from . import user_utils as default_user_utils
from . import data_handler


class Dashboard:
    '''Root dashboard class.

    Args:
        config_fp (str): Path to the config file.
        user_utils (module): User-customized module for data loading
            and preprocessing.
    '''

    def __init__(self, config_fp, user_utils=default_user_utils):

        self.config = self.load_config(config_fp)
        self.data_handler = data_handler.DataHandler(self.config, user_utils)

    def load_config(self, config_fp):
        '''Get the config. This is done once per session.
        The config directory is set as the working directory.

        Args:
            config_fp (str): Filepath for the config file.

        Returns:
            config (dict): The config dictionary.
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

    @property
    def dfs(self):
        '''Convenience property for accessing the dataframes.

        Returns:
            dfs (dict): The dataframes.
        '''
        return self.data_handler.dfs
