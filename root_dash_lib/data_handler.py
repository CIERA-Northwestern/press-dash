import pandas as pd


class DataHandler:
    '''Class for handling data.

    Args:
        config (dict): The config dictionary.
        user_utils (module): User-customized module for data loading
    '''

    def __init__(self, config, user_utils):
        self.config = config
        self.user_utils = user_utils