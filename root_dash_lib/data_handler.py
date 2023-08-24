'''Module for handling data.
'''


class DataHandler:
    '''Class for handling data.
    The data is loaded and pre-processed at initialization.

    Args:
        config (dict): The config dictionary.
        user_utils (module): User-customized module for data loading
    '''

    def __init__(self, config, user_utils):
        self.config = config
        self.user_utils = user_utils

        self.dfs = {}
        self.dfs['raw'] = self.load_data()
        self.dfs['preprocessed'], self.config = self.preprocess_data(
            self.dfs['raw']
        )

    def load_data(self):
        '''Load the data using the stored config and user_utils.

        Returns:
            df (pandas.DataFrame): The data.
        '''
        return self.user_utils.load_data(self.config)

    def preprocess_data(self, raw_df):
        '''Preprocess the data using the stored config and user_utils.

        Args:
            df (pandas.DataFrame): The loaded data.

        Returns:
            df (pandas.DataFrame): The preprocessed data.
        '''
        return self.user_utils.preprocess_data(raw_df, self.config)
