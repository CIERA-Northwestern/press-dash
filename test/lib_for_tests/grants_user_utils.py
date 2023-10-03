'''Data-handling functions.
These functions are the most-likely to be changed when adapting this dashboard.
'''
import glob
import numpy as np
import os
import pandas as pd


def load_data(config):
    '''This is the main function for loading the data
    (but save cleaning and preprocessing for later).
    
    This function should accept a pandas DataFrame and a
    config dictionary and return the same.

    Args:
        config (dict): The configuration dictionary, loaded from a YAML file.

    Returns:
        raw_df (pandas.DataFrame): The data to be used in the dashboard.
        config (dict): The configuration dictionary, loaded from a YAML file.
    '''

    # Get possible files
    input_dir = os.path.join(config['data_dir'], config['input_dirname'])
    pattern = os.path.join(input_dir, config['data_file_pattern'])
    data_fps = glob.glob(pattern)

    if len(data_fps) == 0:
        raise IOError('No files found matching pattern {}'.format(pattern))

    # Select the most recent file
    ind_selected = np.argmax([os.path.getctime(_) for _ in data_fps])
    data_fp = data_fps[ind_selected]

    raw_df = pd.read_csv(data_fp, sep='\t', encoding='UTF-16')

    return raw_df, config


def clean_data(raw_df, config):
    '''This is the main function for cleaning the data.
    
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

    # Drop bad data (years earlier than 2000)
    cleaned_df = raw_df.copy()
    for date_column in config.get('date_columns',[]):
        dates = pd.to_datetime(cleaned_df[date_column])
        zero_inds = cleaned_df.index[dates < pd.to_datetime('2000-01-01')]
        cleaned_df = cleaned_df.drop(zero_inds)

    return cleaned_df, config


def preprocess_data(cleaned_df, config):
    '''This is the main function for doing preprocessing, e.g. 
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

    # Set ID
    preprocessed_df['id'] = preprocessed_df[config['primary_id_column']]

    # Convert dates to years.
    for date_column in config.get('date_columns',[]):

        # Convert to datetime
        preprocessed_df[date_column] = pd.to_datetime(preprocessed_df[date_column])

        # Get date bins
        start_year = preprocessed_df[date_column].min().year - 1
        end_year = preprocessed_df[date_column].max().year + 1
        date_bins = pd.date_range(
            '{} {}'.format(config['year_start'], start_year),
            pd.Timestamp.now() + pd.offsets.DateOffset(years=1),
            freq = pd.offsets.DateOffset(years=1),
        )
        date_bin_labels = date_bins.year[:-1]

        # Column name
        year_column = date_column.replace('Date', 'Year')
        if 'time_bin_columns' not in config:
            config['time_bin_columns'] = []
        # To avoid overwriting the year column, we append a label to the end
        if year_column in config['time_bin_columns']:
            year_column += ' (Custom)'
        config['time_bin_columns'].append(year_column)

        # Do the actual binning
        preprocessed_df[year_column] = pd.cut(preprocessed_df[date_column], date_bins, labels=date_bin_labels) 

    return preprocessed_df, config