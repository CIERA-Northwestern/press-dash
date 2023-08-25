'''Code for user interaction.
'''
import copy
import os
from typing import Union

import numpy as np
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

        Returns:
            storage_dict: Current values in the dictionary the settings are stored in.
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
    ) -> dict:
        '''Request common data settings from the user.

        Args:
            st_loc: Streamlit object (st or st.sidebar) indicating where to place.
            ask_for: Keys for widgets to include.
            display_defaults: Default values the user sees in the widgets.
            store_in: Where the settings should be stored. Defaults to common data settings.

        Returns:
            storage_dict: Current values in the dictionary the settings are stored in.
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
            store_in: dict = None,
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
            store_in: Where the settings should be stored. Defaults to common view settings.

        Returns:
            storage_dict: Current values in the dictionary the settings are stored in.
        '''

        # Set up generic figure settings
        fig_width, fig_height = matplotlib.rcParams['figure.figsize']
        # The figure size is doubled because this is a primarily horizontal plot
        fig_width *= 2.
        view_kw = {}
        if 'seaborn_style' in ask_for:
            view_kw['seaborn_style'] = st_loc.selectbox(
                'choose seaborn plot style',
                [ 'whitegrid', 'white', 'darkgrid', 'dark', 'ticks', ],
                index=display_defaults.get( 'seaborn_style', 0 ),
            )
        if 'fig_width' in ask_for:
            view_kw['fig_width'] = st_loc.slider(
                'figure width',
                0.1*fig_width,
                2.*fig_width,
                value=display_defaults.get( 'fig_width', fig_width ),
            )
        if 'fig_height' in ask_for:
            view_kw['fig_height'] = st_loc.slider(
                'figure height',
                0.1*fig_height,
                2.*fig_height,
                value=display_defaults.get( 'fig_height', fig_height ),
            )
        if 'font_scale' in ask_for:
            view_kw['font_scale'] = st_loc.slider(
                'font scale',
                0.1,
                2.,
                value=display_defaults.get( 'font_scale', 1. ),
            )
        if 'include_legend' in ask_for:
            view_kw['include_legend'] = st_loc.checkbox(
                'include legend',
                value=display_defaults.get( 'include_legend', True ),
            )
        if view_kw.get( 'include_legend', False ):
            if 'legend_scale' in ask_for:
                view_kw['legend_scale'] = st_loc.slider(
                    'legend scale',
                    0.1,
                    2.,
                    value=display_defaults.get( 'legend_scale', 1. ),
                )
            if 'legend_x' in ask_for:
                view_kw['legend_x'] = st_loc.slider(
                    'legend x',
                    0.,
                    1.5,
                    value=display_defaults.get( 'legend_x', 1. ),
                )
            if 'legend_y' in ask_for:
                view_kw['legend_y'] = st_loc.slider(
                    'legend y',
                    0.,
                    1.5,
                    value=display_defaults.get( 'legend_y', 1. ),
                )
            if 'legend_horizontal_alignment' in ask_for:
                view_kw['legend_horizontal_alignment'] = st_loc.selectbox(
                    'legend horizontal alignment',
                    [ 'left', 'center', 'right' ],
                    index=display_defaults.get( 'legend_horizontal_alignment', 2 ),
                )
            if 'legend_vertical_alignment' in ask_for:
                view_kw['legend_vertical_alignment'] = st_loc.selectbox(
                    'legend vertical alignment',
                    [ 'upper', 'center', 'lower' ],
                    index=display_defaults.get( 'legend_vertical_alignment', 2 ),
                )
        if 'include_annotations' in ask_for:
            view_kw['include_annotations'] = st_loc.checkbox(
                'include annotations',
                value=display_defaults.get( 'include_annotations', False ),
            )
        if view_kw.get( 'include_annotations', False ):
            if 'annotations_horizontal_alignment' in ask_for:
                view_kw['annotations_horizontal_alignment'] = st_loc.selectbox(
                    'annotations horizontal alignment',
                    [ 'left', 'center', 'right' ],
                    index=display_defaults.get( 'annotations_horizontal_alignment', 0 ),
                )
        if 'color_palette' in ask_for:
            view_kw['color_palette'] = st_loc.selectbox(
                'color palette',
                display_options.get('color_palette', [ 'deep', 'colorblind', 'dark', 'bright', 'pastel', 'muted', ]),
                index=display_defaults.get( 'color_palette', 0 ),
            )

        if 'font' in ask_for:
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
                    format_func=lambda x: fonts[x]
                )
                font = font_manager.FontProperties( fname=font_fps[font_ind] )
                view_kw['font'] = font.get_name()
            except:
                view_kw['font'] = original_font

        # Update stored objects
        if store_in is None:
            storage_dict = self.settings.common['view']
        storage_dict.update(view_kw)

        return storage_dict

