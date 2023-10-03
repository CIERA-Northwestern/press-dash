'''Functions for loading and preprocessing the data, specific to
the user's data. If you are adapting the dashboard as your own,
you likely need to alter these functions.
'''
import os
import glob
import numpy as np
import pandas as pd

from root_dash_lib import utils


def load_data(config):
    '''Modify this!
    
    This is the main function for loading the data
    (but save cleaning and preprocessing for later).
    
    For compatibility with the existing
    dashboard, this function should accept a pandas DataFrame and a
    config dictionary and return the same.

    Args:
        config (dict): The configuration dictionary, loaded from a YAML file.

    Returns:
        raw_df (pandas.DataFrame): The data to be used in the dashboard.
        config (dict): The configuration dictionary, loaded from a YAML file.
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
    website_df = pd.read_csv(data_fp, parse_dates=['Date',])
    website_df.set_index('id', inplace=True)

    # Load press data
    press_df = pd.read_excel(press_office_data_fp)
    press_df.set_index('id', inplace=True)

    # Combine the data
    raw_df = website_df.join(press_df)

    return raw_df, config


def clean_data(raw_df, config):
    '''Modify this!
    
    This is the main function for cleaning the data,
    i.e. getting rid of NaNs, dropping glitches, etc.
    
    For compatibility with the existing
    dashboard, this function should accept a pandas DataFrame and a
    config dictionary and return the same.

    Args:
        raw_df (pandas.DataFrame): The raw data to be used in the dashboard.
        config (dict): The configuration dictionary, loaded from a YAML file.

    Returns:
        cleaned_df (pandas.DataFrame): The cleaned data.
        config (dict): The (possibly altered) configuration dictionary.
    '''

    # Drop drafts
    cleaned_df = raw_df.drop(
        raw_df.index[raw_df['Date'].dt.year == 1970],
        axis='rows',
    )

    # Drop weird articles---ancient ones w/o a title or press type
    cleaned_df.dropna(
        axis='rows',
        how='any',
        subset=['Title', 'Press Types',],
        inplace=True,
    )

    # Get rid of HTML ampersands
    for str_column in ['Title', 'Research Topics', 'Categories']:
        cleaned_df[str_column] = cleaned_df[str_column].str.replace('&amp;', '&')

    # Handle NaNs and such
    columns_to_fill = ['Press Mentions', 'People Reached',]
    cleaned_df[columns_to_fill] = cleaned_df[columns_to_fill].fillna(
        value=0
    )
    cleaned_df.fillna(value='N/A', inplace=True)

    return cleaned_df, config


def preprocess_data(cleaned_df, config):
    '''Modify this!
    
    This is the main function for doing preprocessing, e.g. 
    adding new columns, renaming them, etc.
    
    For compatibility with the existing
    dashboard, this function should accept a pandas DataFrame and a
    config dictionary and return the same.

    Args:
        cleaned_df (pandas.DataFrame): The raw data to be used in the dashboard.
        config (dict): The configuration dictionary, loaded from a YAML file.

    Returns:
        processed_df (pandas.DataFrame): The processed data.
        config (dict): The (possibly altered) configuration dictionary.
    '''

    preprocessed_df = cleaned_df.copy()

    config['page_title'] = 'Modified Page Title'

    # Get the year, according to the config start date
    preprocessed_df['Year'] = utils.get_year(
        preprocessed_df['Date'], config['start_of_year']
    )

    # Tweaks to the press data
    if 'Title (optional)' in preprocessed_df.columns:
        preprocessed_df.drop('Title (optional)', axis='columns', inplace=True)
    for column in ['Press Mentions', 'People Reached']:
        preprocessed_df[column] = preprocessed_df[column].astype('Int64')

    # Now explode the data
    for group_by_i in config['groupings']:
        preprocessed_df[group_by_i] = preprocessed_df[group_by_i].str.split('|')
        preprocessed_df = preprocessed_df.explode(group_by_i)

    # Exploding the data results in duplicate IDs,
    # so let's set up some new, unique IDs.
    preprocessed_df['id'] = preprocessed_df.index
    preprocessed_df.set_index(np.arange(len(preprocessed_df)), inplace=True)

    return preprocessed_df, config
