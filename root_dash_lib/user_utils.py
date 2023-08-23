import copy
import glob
import numpy as np
import os
import pandas as pd
import re
import streamlit as st
import yaml

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import seaborn as sns

from root_dash_lib import data_utils

################################################################################

def load_data( config ):
    '''This is the main function for loading the data, and one of the most-important functions
    the user will need to modify when adapting this dashboard to their own data.
    For compatibility with the existing dashboard, this function should return a pandas DataFrame
    and take in a config dictionary.

    Args:
        config (dict): The configuration dictionary, loaded from a YAML file.

    Returns:
        df (pandas.DataFrame): The data to be used in the dashboard.
    '''

    ################################################################################
    # Filepaths

    input_dir = os.path.join( config['data_dir'], config['input_dirname'] )

    def get_fp_of_most_recent_file( pattern ):
        '''Get the filepath of the most-recently created file matching the pattern.
        We just define this here because we use it twice.
        
        Args:
            pattern (str): The pattern to match.

        Returns:
            fp (str): The filepath of the most-recently created file matching the pattern.
        '''
        fps = glob.glob( pattern )
        ind_selected = np.argmax([ os.path.getctime( _ ) for _ in fps ])
        return fps[ind_selected]

    data_pattern = os.path.join( input_dir, config['website_data_file_pattern'] )
    data_fp = get_fp_of_most_recent_file( data_pattern )

    press_office_pattern = os.path.join( input_dir, config['press_office_data_file_pattern'] )
    press_office_data_fp = get_fp_of_most_recent_file( press_office_pattern )

    ################################################################################
    # Load data

    # Website data
    df = pd.read_csv( data_fp, parse_dates=[ 'Date', ] )
    df.set_index( 'id', inplace=True )

    # Load press data
    press_df = pd.read_excel( press_office_data_fp )
    press_df.set_index( 'id', inplace=True )

    # Combine the data
    df = df.join( press_df )

    return df

################################################################################

def preprocess_data( df, config ):
    '''This is the main function for preprocessing the data, and one of the most-important functions
    the user will need to modify when adapting this dashboard to their own data.
    For compatibility with the existing dashboard framework this function should return a pandas DataFrame
    and a config dictionary, and accept a pandas DataFrame and a config dictionary.

    Args:
        df (pandas.DataFrame): The data to be used in the dashboard.
        config (dict): The configuration dictionary, loaded from a YAML file.

    Returns:
        df (pandas.DataFrame): The processed data to be used in the dashboard.
        config (dict): The (possibly altered) configuration dictionary.
    '''

    # Drop drafts
    df.drop( df.index[df['Date'].dt.year == 1970], axis='rows', inplace=True )

    # Drop weird articles---ancient ones w/o a title or press type
    df.dropna( axis='rows', how='any', subset=[ 'Title', 'Press Types', ], inplace=True )

    # Get rid of HTML ampersands
    for str_column in [ 'Title', 'Research Topics', 'Categories' ]:
        df[str_column] = df[str_column].str.replace( '&amp;', '&' )

    # Get the year, according to the config start date
    df['Year'] = data_utils.get_year( df['Date'], config['start_of_year'] )

    # Handle NaNs and such
    df[['Press Mentions', 'People Reached']] = df[['Press Mentions','People Reached']].fillna( value=0 )
    df.fillna( value='N/A', inplace=True )

    # Tweaks to the press data
    if 'Title (optional)' in df.columns:
        df.drop( 'Title (optional)', axis='columns', inplace=True )
    for column in [ 'Press Mentions', 'People Reached' ]:
        df[column] = df[column].astype( 'Int64' )

    # Now explode the data
    for group_by_i in config['groupings']:
        df[group_by_i] = df[group_by_i].str.split( '|' )
        df = df.explode( group_by_i )

    # Exploding the data results in duplicate IDs, so let's set up some new, unique IDs.
    df['id'] = df.index
    df.set_index( np.arange( len(df) ), inplace=True )

    return df, config
