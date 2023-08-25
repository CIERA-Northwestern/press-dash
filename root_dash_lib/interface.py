'''Code for user interaction.
'''
from typing import Union

import streamlit as st

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
            store_in: dict = None,
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
            store_in: Where the settings should be stored. Defaults to common data settings.
        '''

        # We have to add the data settings to a dictionary piece-by-piece
        # because as soon as they're called the user input exists.
        data_axes_kw = {}
        if 'aggregation' in ask_for:
            data_axes_kw['aggregation'] = st_loc.selectbox(
                'How do you want to aggregate the data?',
                [ 'count', 'sum' ],
                index=display_defaults.get( 'aggregation', 0 ),
            )
        else:
            data_axes_kw['aggregation'] = aggregation_method
        if 'x_column' in ask_for:
            data_axes_kw['x_column'] = st_loc.selectbox(
                'How do you want to bin the data in time?',
                display_options.get( 'x_column', self.config['x_columns'] ),
                index=display_defaults.get( 'x_column', 0 ),
            )
        if 'y_column' in ask_for:
            if data_axes_kw['aggregation'] == 'count':
                data_axes_kw['y_column'] = st_loc.selectbox(
                    'What do you want to count unique entries of?',
                    display_options.get( 'y_column', self.config['id_columns'] ),
                    index=display_defaults.get( 'y_column', 0 ),
                )
            elif data_axes_kw['aggregation'] == 'sum':
                data_axes_kw['y_column'] = st_loc.selectbox(
                    'What do you want to sum?',
                    display_options.get( 'y_column', self.config['weight_columns'] ),
                    index=display_defaults.get( 'y_column', 0 ),
                )
        if 'groupby_column' in ask_for:
            data_axes_kw['groupby_column'] = st_loc.selectbox(
                'What do you want to group the data by?',
                display_options.get( 'groupby_column', self.config['categorical_columns'] ),
                index=display_defaults.get( 'groupby_column', 0 ),
            )

        # Update stored objects
        if store_in is None:
            storage_dict = self.settings.common['data']
        storage_dict.update( data_axes_kw )

        return storage_dict

    def request_data_settings(
            self,
            st_loc,
            ask_for: list[str] = [ 'show_total', 'cumulative', 'recategorize', 'combine_single_categories' ],
            display_defaults: dict = {},
            store_in: dict = None,
    ):
        '''Request common data settings from the user.

        Args:
            st_loc: Streamlit object (st or st.sidebar) indicating where to place.
            ask_for: Keys for widgets to include.
            display_defaults: Default values the user sees in the widgets.
            store_in: Where the settings should be stored. Defaults to common data settings.
        '''

        data_kw = {}
        if 'show_total' in ask_for:
            data_kw['show_total'] = st_loc.checkbox(    
                'show total',
                value=display_defaults.get( 'show_total', True ),
            )
        if 'cumulative' in ask_for:
            data_kw['cumulative'] = st_loc.checkbox(
                'use cumulative values',
                value=display_defaults.get( 'cumulative', False ),
            )
        if 'recategorize' in ask_for:
            data_kw['recategorize'] = st_loc.checkbox(
                'use combined categories (avoids double counting; definitions can be edited in the config)',
                value=display_defaults.get( 'recategorize', False ),
            )
            if 'combine_single_categories' in ask_for:
                data_kw['combine_single_categories'] = st_loc.checkbox(
                    'group all undefined categories as "Other"',
                    value=display_defaults.get( 'combine_single_categories', False ),
                )

        # Update stored objects
        if store_in is None:
            storage_dict = self.settings.common['data']
        storage_dict.update( data_kw )

        return storage_dict