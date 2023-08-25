'''Code for user interaction.
'''
import copy
import os
from typing import Union

import numpy as np
import pandas as pd
import streamlit as st

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import seaborn as sns

from . import settings

class Interface:
    '''Main interaction object.

    Args:
        config: The config dictionary.
    '''

    def __init__(self, config: dict, settings: settings.Settings):

        self.config = config
        self.settings = settings

    def request_data_axes(
            self,
            st_loc,
            ask_for: list[str] = [ 'aggregation', 'x_column', 'y_column', 'groupby_column'],
            display_defaults: dict = {},
            display_options: dict = {},
            aggregation_method: str = 'count',
            selected_settings: dict = None,
        ) -> dict:
        '''Add to st_loc widgets commonly used to set up the axes of a plot.

        Args:
            st_loc: Streamlit object (st or st.sidebar) indicating where to place.
            ask_for: Keys for widgets to include.
            display_defaults: Default values the user sees in the widgets.
            display_options: Options the user sees in the widgets.
            aggregation_method: Different aggregation methods have different
                aggregation methods. If the aggregation method isn't provided by
                a widget then it defaults to this value.
            selected_settings: Where the settings should be stored. Defaults to common data settings.

        Returns:
            selected_settings: Current values in the dictionary the settings are stored in.
        '''

        if selected_settings is None:
            selected_settings = self.settings.common['data']

        # We have to add the data settings to a dictionary piece-by-piece
        # because as soon as they're called the user input exists.
        if 'aggregation' in ask_for:
            selected_settings['aggregation'] = st_loc.selectbox(
                'How do you want to aggregate the data?',
                [ 'count', 'sum' ],
                index=display_defaults.get( 'aggregation', 0 ),
            )
        else:
            selected_settings['aggregation'] = aggregation_method
        if 'x_column' in ask_for:
            selected_settings['x_column'] = st_loc.selectbox(
                'How do you want to bin the data in time?',
                display_options.get( 'x_column', self.config['x_columns'] ),
                index=display_defaults.get( 'x_column', 0 ),
            )
        if 'y_column' in ask_for:
            if selected_settings['aggregation'] == 'count':
                selected_settings['y_column'] = st_loc.selectbox(
                    'What do you want to count unique entries of?',
                    display_options.get( 'y_column', self.config['id_columns'] ),
                    index=display_defaults.get( 'y_column', 0 ),
                )
            elif selected_settings['aggregation'] == 'sum':
                selected_settings['y_column'] = st_loc.selectbox(
                    'What do you want to sum?',
                    display_options.get( 'y_column', self.config['weight_columns'] ),
                    index=display_defaults.get( 'y_column', 0 ),
                )
        if 'groupby_column' in ask_for:
            selected_settings['groupby_column'] = st_loc.selectbox(
                'What do you want to group the data by?',
                display_options.get( 'groupby_column', self.config['categorical_columns'] ),
                index=display_defaults.get( 'groupby_column', 0 ),
            )

        return selected_settings

    def request_data_settings(
            self,
            st_loc,
            ask_for: list[str] = [ 'show_total', 'cumulative', 'recategorize', 'combine_single_categories' ],
            display_defaults: dict = {},
            selected_settings: dict = None,
            tag: str = None,
    ) -> dict:
        '''Request common data settings from the user.

        Args:
            st_loc: Streamlit object (st or st.sidebar) indicating where to place.
            ask_for: Keys for widgets to include.
            display_defaults: Default values the user sees in the widgets.
            selected_settings: Where the settings should be stored. Defaults to common data settings.
            tag: Unique tag that allows duplication of widgets.

        Returns:
            selected_settings: Current values in the dictionary the settings are stored in.
        '''

        if selected_settings is None:
            selected_settings = self.settings.common['data']

        # Setup the tag
        if tag is None:
            tag = ''
        else:
            tag += ':'

        key = 'show_total'
        if key in ask_for:
            selected_settings[key] = st_loc.checkbox(    
                'show total',
                value=display_defaults.get( key, True ),
                key=tag + key
            )
        key = 'cumulative'
        if key in ask_for:
            selected_settings[key] = st_loc.checkbox(
                'use cumulative values',
                value=display_defaults.get( key, False ),
                key=tag + key
            )
        key = 'recategorize'
        if key in ask_for:
            selected_settings[key] = st_loc.checkbox(
                'use combined categories (avoids double counting; definitions can be edited in the config)',
                value=display_defaults.get( key, False ),
                key=tag + key
            )
            if selected_settings.get('recategorize', False):
                key = 'combine_single_categories'
                if key in ask_for:
                    selected_settings[key] = st_loc.checkbox(
                        'group all undefined categories as "Other"',
                        value=display_defaults.get( key, False ),
                        key=tag + key
                    )

        return selected_settings

    def request_filter_settings(
            self,
            st_loc,
            df: pd.DataFrame,
            ask_for: list[str] = [ 'text_filters', 'categorical_filters', 'numerical_filters' ],
            display_defaults: dict = {},
            display_options: dict = {},
            selected_settings: dict = None,
            tag: str = None,
    ) -> dict:
        '''Request common data settings from the user.

        Args:
            st_loc: Streamlit object (st or st.sidebar) indicating where to place.
            df: The dataframe that will be filtered. Required because good defaults require it.
            ask_for: Keys for widgets to include.
            display_defaults: Default values the user sees in the widgets.
            display_options: Options the user sees in the widgets.
            selected_settings: Where the settings should be stored. Defaults to common filter settings.
            tag: Unique tag that allows duplication of widgets.

        Returns:
            selected_settings: Current values in the dictionary the settings are stored in.
        '''

        if selected_settings is None:
            selected_settings = self.settings.common['filters']

        # Setup the tag
        if tag is None:
            tag = ''
        else:
            tag += ':'

        key = 'text_filters'
        if key in ask_for:
            current = selected_settings.setdefault(key, {})
            # Select which columns to filter on
            if len(current) == 0:
                multiselect_default = []
            else:
                multiselect_default = list(current)
            filter_columns = st_loc.multiselect(
                'What columns do you want to search? (case insensitive; not a smart search)',
                options=display_options.get(key, self.config['text_columns']),
                default=multiselect_default,
                key=tag + key
            )
            for col in filter_columns:
                # Check the current values then the passed-in defaults
                # for a default
                default = current.get(col,'')
                default = display_defaults.get(key, {}).get(col, default)
                selected_settings[key][col] = st_loc.text_input(
                    '"{}" column: What do you want to search for?'.format(col),
                    value=default,
                    key=tag + key + ':' + col
                )

        key = 'categorical_filters'
        if key in ask_for:
            current = selected_settings.setdefault(key, {})
            # Select which columns to filter on
            if len(current) == 0:
                multiselect_default = []
            else:
                multiselect_default = list(current)
            filter_columns = st_loc.multiselect(
                'What categorical columns do you want to filter on?',
                options=display_options.get(key, self.config['categorical_columns']),
                default=multiselect_default,
                key=tag + key
            )
            for col in filter_columns:
                possible_columns = pd.unique(df[col])
                # Check the current values then the passed-in defaults
                # for a default
                default = current.get(col, possible_columns)
                default = display_defaults.get(key, {}).get(col, default)
                selected_settings[key][col] = st_loc.multiselect(
                    '"{}" column: What groups to include?'.format(col),
                    possible_columns,
                    default=default,
                    key=tag + key + ':' + col
                )

        key = 'numerical_filters'
        if key in ask_for:
            current = selected_settings.setdefault(key, {})
            # Select which columns to filter on
            if len(current) == 0:
                multiselect_default = []
            else:
                multiselect_default = list(current)
            filter_columns = st_loc.multiselect(
                'What numerical columns do you want to filter on?',
                options=display_options.get(key, self.config['numerical_columns']),
                default=multiselect_default,
                key=tag + key
            )
            for col in filter_columns:
                value_min = df[col].min()
                value_max = df[col].max()
                # Check the current values then the passed-in defaults
                # for a default
                default = current.get(col, (value_min, value_max))
                default = display_defaults.get(key, {}).get(col, default)
                selected_settings[key][col] = st_loc.slider(
                    '"{}" column: What range to include?'.format(col),
                    min_value=default[0],
                    max_value=default[1],
                    value=default,
                    key=tag + key + ':' + col
                )

        return selected_settings

    def request_view_settings(
            self,
            st_loc,
            ask_for: list[str] = [
                'seaborn_style',
                'fig_width',
                'fig_height',
                'font_scale',
                'include_legend',
                'legend_scale',
                'legend_x',
                'legend_y',
                'legend_horizontal_alignment',
                'legend_vertical_alignment',
                'include_annotations',
                'annotations_horizontal_alignment',
                'font',
                'color_palette'
            ],
            display_defaults: dict = {},
            display_options: dict = {},
            selected_settings: dict = None,
            tag: str = None,
        ):
        '''Generic and common figure settings.

        Args:
            st_loc: Streamlit object (st or st.sidebar) indicating where to place.
            ask_for: Keys for widgets to include.
            display_defaults: Default values the user sees in the widgets.
            display_options: Options the user sees in the widgets.
            aggregation_method: Different aggregation methods have different
                aggregation methods. If the aggregation method isn't provided by
                a widget then it defaults to this value.
            selected_settings: Where the settings should be stored. Defaults to common view settings.
            tag: Unique tag that allows duplication of widgets.

        Returns:
            selected_settings: Current values in the dictionary the settings are stored in.
        '''

        if selected_settings is None:
            selected_settings = self.settings.common['data']

        # Setup the tag
        if tag is None:
            tag = ''
        else:
            tag += ':'

        # Set up generic figure settings
        fig_width, fig_height = matplotlib.rcParams['figure.figsize']
        # The figure size is doubled because this is a primarily horizontal plot
        fig_width *= 2.
        key = 'seaborn_style'
        if key in ask_for:
            selected_settings[key] = st_loc.selectbox(
                'choose seaborn plot style',
                display_options.get(key, [ 'whitegrid', 'white', 'darkgrid', 'dark', 'ticks', ]),
                index=display_defaults.get(key, 0),
                key=tag + key,
            )
        key = 'fig_width'
        if key in ask_for:
            selected_settings[key] = st_loc.slider(
                'figure width',
                0.1*fig_width,
                2.*fig_width,
                value=display_defaults.get( key, fig_width ),
                key=tag + key,
            )
        key = 'fig_height'
        if key in ask_for:
            selected_settings[key] = st_loc.slider(
                'figure height',
                0.1*fig_height,
                2.*fig_height,
                value=display_defaults.get( key, fig_height ),
                key=tag + key,
            )
        key = 'font_scale'
        if key in ask_for:
            selected_settings[key] = st_loc.slider(
                'font scale',
                0.1,
                2.,
                value=display_defaults.get( key, 1. ),
                key=tag + key,
            )
        key = 'include_legend'
        if key in ask_for:
            selected_settings[key] = st_loc.checkbox(
                'include legend',
                value=display_defaults.get( key, True ),
                key=tag + key,
            )
        if selected_settings.get( 'include_legend', False ):
            key = 'legend_scale'
            if key in ask_for:
                selected_settings[key] = st_loc.slider(
                    'legend scale',
                    0.1,
                    2.,
                    value=display_defaults.get( key, 1. ),
                    key=tag + key,
                )
            key = 'legend_x'
            if key in ask_for:
                selected_settings[key] = st_loc.slider(
                    'legend x',
                    0.,
                    1.5,
                    value=display_defaults.get( key, 1. ),
                    key=tag + key,
                )
            key = 'legend_y'
            if key in ask_for:
                selected_settings[key] = st_loc.slider(
                    'legend y',
                    0.,
                    1.5,
                    value=display_defaults.get( key, 1. ),
                    key=tag + key,
                )
            key = 'legend_ha'
            if key in ask_for:
                selected_settings[key] = st_loc.selectbox(
                    'legend horizontal alignment',
                    [ 'left', 'center', 'right' ],
                    index=display_defaults.get( key, 2 ),
                    key=tag + key,
                )
            key = 'legend_va'
            if key in ask_for:
                selected_settings[key] = st_loc.selectbox(
                    'legend vertical alignment',
                    [ 'upper', 'center', 'lower' ],
                    index=display_defaults.get( key, 2 ),
                    key=tag + key,
                )
        key = 'include_annotations'
        if key in ask_for:
            selected_settings[key] = st_loc.checkbox(
                'include annotations',
                value=display_defaults.get( key, False ),
                key=tag + key,
            )
        if selected_settings.get( 'include_annotations', False ):
            key = 'annotations_ha'
            if key in ask_for:
                selected_settings[key] = st_loc.selectbox(
                    'annotations horizontal alignment',
                    [ 'left', 'center', 'right' ],
                    index=display_defaults.get( key, 0 ),
                    key=tag + key,
                )
        key = 'color_palette'
        if key in ask_for:
            selected_settings[key] = st_loc.selectbox(
                'color palette',
                display_options.get(key, [ 'deep', 'colorblind', 'dark', 'bright', 'pastel', 'muted', ]),
                index=display_defaults.get( key, 0 ),
                key=tag + key,
            )

        key = 'font'
        if key in ask_for:
            original_font = copy.copy( plt.rcParams['font.family'] )[0]
            # This can be finicky, so we'll wrap it in a try/except
            try:
                ## Get all installed fonts
                font_fps = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
                fonts = [ os.path.splitext( os.path.basename( _ ) )[0] for _ in font_fps ]
                ## Get the default font
                default_font = font_manager.FontProperties(family='Sans Serif')
                default_font_fp = font_manager.findfont( default_font )
                default_index = int( np.where( np.array( font_fps ) == default_font_fp )[0][0] )
                ## Make the selection
                font_ind = st_loc.selectbox(
                    'Select font',
                    np.arange( len( fonts ) ),
                    index=default_index,
                    format_func=lambda x: fonts[x],
                    key=tag + key,
                )
                font = font_manager.FontProperties( fname=font_fps[font_ind] )
                selected_settings[key] = font.get_name()
            except:
                selected_settings[key] = original_font

        return selected_settings

