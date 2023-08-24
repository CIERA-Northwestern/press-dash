'''Functions for loading and preprocessing the data, specific to
the user's data. If you are adapting the dashboard as your own,
you likely need to alter these functions.
'''
import os
import glob
import numpy as np
import pandas as pd

from root_dash_lib import time_series_utils


def load_data(config):
    '''This is the main function for loading the data, and one of the
    most-important functions the user will need to modify when adapting
    this dashboard to their own data. For compatibility with the existing
    dashboard, this function should return a pandas DataFrame and take
    in a config dictionary.

    Args:
        config (dict): The configuration dictionary, loaded from a YAML file.

    Returns:
        df (pandas.DataFrame): The data to be used in the dashboard.
    '''

    ##########################################################################
    # Filepaths

    input_dir = os.path.join(config['data_dir'], config['input_dirname'])

    def get_fp_of_most_recent_file(pattern):
        '''Get the filepath of the most-recently created file matching
        the pattern. We just define this here because we use it twice.

        Args:
            pattern (str): The pattern to match.

        Returns:
            fp (str): The filepath of the most-recently created file
                matching the pattern.
        '''
        fps = glob.glob(pattern)
        ind_selected = np.argmax([os.path.getctime(_) for _ in fps])
        return fps[ind_selected]

    data_pattern = os.path.join(input_dir, config['website_data_file_pattern'])
    data_fp = get_fp_of_most_recent_file(data_pattern)

    press_office_pattern = os.path.join(
        input_dir, config['press_office_data_file_pattern']
    )
    press_office_data_fp = get_fp_of_most_recent_file(press_office_pattern)

    ##########################################################################
    # Load data

    # Website data
    website_df = pd.read_csv(data_fp, parse_dates=['Date', ])
    website_df.set_index('id', inplace=True)

    # Load press data
    press_df = pd.read_excel(press_office_data_fp)
    press_df.set_index('id', inplace=True)

    # Combine the data
    raw_df = website_df.join(press_df)

    return raw_df


def preprocess_data(raw_df, config):
    '''This is the main function for loading the data, and one of the
    most-important functions the user will need to modify when adapting
    this dashboard to their own data. For compatibility with the existing
    dashboard, this function should accept a pandas DataFrame and a
    config dictionary and return the same.

    Args:
        df (pandas.DataFrame): The data to be used in the dashboard.
        config (dict): The configuration dictionary, loaded from a YAML file.

    Returns:
        df (pandas.DataFrame): The processed data to be used in the dashboard.
        config (dict): The (possibly altered) configuration dictionary.
    '''

    # Drop drafts
    raw_df.drop(
        raw_df.index[raw_df['Date'].dt.year == 1970], axis='rows', inplace=True
    )

    # Drop weird articles---ancient ones w/o a title or press type
    raw_df.dropna(
        axis='rows',
        how='any',
        subset=['Title', 'Press Types', ],
        inplace=True,
    )

    # Get rid of HTML ampersands
    for str_column in ['Title', 'Research Topics', 'Categories']:
        raw_df[str_column] = raw_df[str_column].str.replace('&amp;', '&')

    # Get the year, according to the config start date
    raw_df['Year'] = time_series_utils.get_year(
        raw_df['Date'], config['start_of_year']
    )

    # Handle NaNs and such
    columns_to_fill = ['Press Mentions', 'People Reached', ]
    raw_df[columns_to_fill] = raw_df[columns_to_fill].fillna(value=0)
    raw_df.fillna(value='N/A', inplace=True)

    # Tweaks to the press data
    if 'Title (optional)' in raw_df.columns:
        raw_df.drop('Title (optional)', axis='columns', inplace=True)
    for column in ['Press Mentions', 'People Reached']:
        raw_df[column] = raw_df[column].astype('Int64')

    # Now explode the data
    for group_by_i in config['groupings']:
        raw_df[group_by_i] = raw_df[group_by_i].str.split('|')
        raw_df = raw_df.explode(group_by_i)

    # Exploding the data results in duplicate IDs,
    # so let's set up some new, unique IDs.
    raw_df['id'] = raw_df.index
    raw_df.set_index(np.arange(len(raw_df)), inplace=True)

    return raw_df, config
