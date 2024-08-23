'''Code for user interaction.
'''
import copy
import os
from typing import Union, Tuple
import warnings

import numpy as np
import pandas as pd
import streamlit as st
import calendar

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import seaborn as sns

from press_dash_lib import utils

from .settings import Settings

class Interface:
    '''Main interaction object.

    Args:
        config: The config dictionary.
    '''

    def __init__(self, config: dict, settings: Settings):

        self.config = config
        self.settings = settings

    def request_data_axes(
            self,
            st_loc,
            df,
            min_year,
            max_year,
            ask_for: list[str] = ['aggregation_method', 'x_column', 'y_column', 'groupby_column'],
            local_key: str = None,
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

        # Update the display defaults with any values that exist in the settings
        settings_dict = self.settings.get_settings(
            local_key=local_key,
            common_to_include=['data',]
        )
        display_defaults.update(settings_dict)

        if selected_settings is None:
            selected_settings = self.settings.common['data']

        # We have to add the data settings to a dictionary piece-by-piece
        # because as soon as they're called the user input exists.
        key = 'aggregation_method'
        if key in ask_for:
            value, ind = selectbox(
                st_loc,
                'How do you want to aggregate the data?',
                options = display_options.get(key, ['count', 'sum']),
                index = display_defaults.get(key + '_ind', 0),
            )
            selected_settings[key] = value
            selected_settings[key + '_ind'] = ind
        else:
            selected_settings['aggregation_method'] = aggregation_method
        key = 'x_column'
        if key in ask_for:
            value, ind = selectbox(
                st_loc,
                'How do you want to bin the data in time?',
                options = display_options.get('x_column', self.config['x_columns']),
                index = display_defaults.get(key + '_ind', 0),
            )
            
            if value == 'Year(Flexible)':
                month_dict = {'January(Calendar Year)':1, 'February':2, 'March':3,'April(Reporting Year)':4,'May':5,'June':6,'July':7,'August':8,'September(Fiscal Year)':9,'October':10,'November':11,'December':12}
                col1, col2 = st_loc.columns(2)
                with col1:
                    value_month, ind_month = selectbox(
                        st_loc, 
                        'starting month for twelve-month recording period',
                        options = list(month_dict.keys())
                    )
                    value = value + ':' + str(month_dict[value_month])
                with col2:
                    if month_dict[value_month] >= 9:
                        min_year = min_year - 1
                    start_year, end_year = st_loc.select_slider(
                            'years to view',
                            options=list(range(min_year,max_year+1)),
                            value=(min_year, max_year),
                    )
                    value = value + ':' + str(start_year) + ':' + str(end_year)
            
            selected_settings[key] = value
            selected_settings[key + '_ind'] = ind
        key = 'y_column'
        if key in ask_for:
            if selected_settings['aggregation_method'] == 'count':
                value, ind = selectbox(
                    st_loc,
                    'What do you want to count unique entries of?',
                    display_options.get(key, self.config['id_columns']),
                    index=display_defaults.get(key + '_ind', 0),
                )
                selected_settings[key] = value
                selected_settings[key + '_ind'] = ind
            elif selected_settings['aggregation_method'] == 'sum':
                value, ind = selectbox(
                    st_loc,
                    'What do you want to sum?',
                    display_options.get('y_column', self.config['numerical_columns']),
                    index=display_defaults.get(key + '_ind', 0),
                )
                selected_settings[key] = value
                selected_settings[key + '_ind'] = ind
        key = 'groupby_column'
        if key in ask_for:
            value, ind = selectbox(
                st_loc,
                'What do you want to categorize the data by?',
                options=display_options.get('groupby_column', self.config['categorical_columns']),
                index=display_defaults.get(key + '_ind', 0),
            )
            
        selected_settings[key] = value
        selected_settings[key + '_ind'] = ind

        return selected_settings

    def request_data_settings(
            self,
            st_loc,
            ask_for: list[str] = ['cumulative', 'recategorize', 'combine_single_categories'],
            local_key: str = None,
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

        # Update the display defaults with any values that exist in the settings
        settings_dict = self.settings.get_settings(
            local_key=local_key,
            common_to_include=['data',]
        )
        display_defaults.update(settings_dict)

        if selected_settings is None:
            selected_settings = self.settings.common['data']


        toggled_on = st_loc.toggle(
            label='show total',
            value=True,
        )

        st_loc.markdown('# Data Settings')

        # Setup the tag
        if tag is None:
            tag = ''
        else:
            tag += ':'
        
        key = 'cumulative'
        if key in ask_for:
            selected_settings[key] = st_loc.checkbox(
                'use cumulative values',
                value=display_defaults.get(key, False),
                key=tag + key
            )
        key = 'recategorize'
        if key in ask_for:
            selected_settings[key] = st_loc.checkbox(
                'use combined categories (avoids double counting; definitions can be edited in the config)',
                value=display_defaults.get(key, False),
                key=tag + key
            )
            if selected_settings.get('recategorize', False):
                key = 'combine_single_categories'
                if key in ask_for:
                    selected_settings[key] = st_loc.checkbox(
                        'group all undefined categories as "Other"',
                        value=display_defaults.get(key, False),
                        key=tag + key
                    )

        return selected_settings, toggled_on

    def process_filter_settings(
            self,
            st_loc,
            df: pd.DataFrame,
            ask_for: list[str] = ['categorical'],
            local_key: str = None,
            display_defaults: dict = {},
            value: str = None,
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

        # Update the display defaults with any values that exist in the settings
        settings_dict = self.settings.get_settings(
            local_key=local_key,
            common_to_include=['filters',]
        )
        display_defaults.update(settings_dict)


        if selected_settings is None:
            selected_settings = self.settings.common['filters']

        # Setup the tag
        if tag is None:
            tag = ''
        else:
            tag += ':'
        
        key = 'categorical'
        if key in ask_for:
            current = selected_settings.setdefault(key, {})
            key=tag + key
            
            
            possible_columns = pd.unique(df[value])
            # Check the current values then the passed-in defaults
            # for a default
            default = current.get(value, possible_columns)
            default = display_defaults.get(key, {}).get(value, default)
            selected_settings[key][value] = st_loc.multiselect(
                '"{}" column: What groups to include?'.format(value),
                possible_columns,
                default=default,
                key=tag + key + ':' + value
            )

        return selected_settings

    def request_view_settings(
            self,
            st_loc,
            ask_for: Union[list[str], str] = [
                'font_scale',
                'seaborn_style',
                'fig_width',
                'fig_height',
                'font',
                'color_palette',
           ],
            local_key: str = None,
            display_defaults: dict = {},
            display_options: dict = {},
            selected_settings: dict = None,
            tag: str = None,
            default_x: str = '',
            default_y: str = '',
        ):
        '''Generic and common figure settings.

        Args:
            st_loc: Streamlit object (st or st.sidebar) indicating where to place.
            ask_for: Keys for widgets to include. If 'all' then all settings are used.
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

        # Update the display defaults with any values that exist in the settings
        settings_dict = self.settings.get_settings(
            local_key=local_key,
            common_to_include=['view',]
        )
        display_defaults.update(settings_dict)

        available_settings = [
            'font_scale',
            'seaborn_style',
            'x_label',
            'y_label',
            'yscale',
            'x_lim',
            'y_lim',
            'xtick_spacing',
            'ytick_spacing',
            'linewidth',
            'marker_size',
            'fig_width',
            'fig_height',
            'include_legend',
            'legend_scale',
            'legend_x',
            'legend_y',
            'legend_ha',
            'legend_va',
            'include_annotations',
            'annotations_ha',
            'font',
            'color_palette',
            'category_colors',
            'totals',
            'month_reindex',
            'year_reindex',
            'kwargs'
       ]
        if ask_for == 'all':
            ask_for = available_settings
        unavailable_settings = [_ for _ in ask_for if _ not in available_settings]
        if len(unavailable_settings) > 0:
            warnings.warn(
                'The following settings were requested, but this function does'
                ' not have widgets available for them:{}'.format(unavailable_settings)
            )

        if selected_settings is None:
            selected_settings = self.settings.common['view']

        # Setup the tag
        if tag is None:
            tag = ''
        else:
            tag += ':'

        key = 'x_label'
        if key in ask_for:
            selected_settings[key] = st_loc.text_input(
                'x label',
                value=display_defaults.get(key, default_x),
                key=tag + key,
            )
        key = 'y_label'
        if key in ask_for:
            selected_settings[key] = st_loc.text_input(
                'y label',
                value=display_defaults.get(key, default_y),
                key=tag + key,
            )
        key = 'yscale'
        if key in ask_for:
            value, ind = selectbox(
                st_loc,
                'y scale',
                options=display_options.get(key, ['linear', 'log']),
                index = display_defaults.get(key + '_ind', 0),
                selectbox_or_radio='radio',
                key=tag + key,
                horizontal=True,
            )
            selected_settings[key] = value
            selected_settings[key + '_ind'] = ind
        key = 'x_lim'
        if key in ask_for:
            lower_col, upper_col = st_loc.columns(2)
            with lower_col:
                default = display_defaults.get(key, '')
                if default is None:
                    default = ''
                lower_lim = st_loc.text_input(
                    'x lower limit',
                    value=default,
                    key=tag + key + 'lower',
                )
            with upper_col:
                default = display_defaults.get(key, '')
                if default is None:
                    default = ''
                upper_lim = st_loc.text_input(
                    'x upper limit',
                    value=default,
                    key=tag + key + 'upper',
                )
            try:
                # This only works if the user entered something well-formed.
                selected_settings[key] = (float(lower_lim), float(upper_lim))
            except ValueError:
                selected_settings[key] = None
        key = 'y_lim'
        if key in ask_for:
            lower_col, upper_col = st_loc.columns(2)
            with lower_col:
                default = display_defaults.get(key, '')
                if default is None:
                    default = ''
                lower_lim = st_loc.text_input(
                    'y lower limit',
                    value=default,
                    key=tag + key + 'lower',
                )
            with upper_col:
                default = display_defaults.get(key, '')
                if default is None:
                    default = ''
                upper_lim = st_loc.text_input(
                    'y upper limit',
                    value=default,
                    key=tag + key + 'upper',
                )
            try:
                # This only works if the user entered something well-formed.
                selected_settings[key] = (float(lower_lim), float(upper_lim))
            except ValueError:
                selected_settings[key] = None
        key = 'xtick_spacing'
        if key in ask_for:
            default = display_defaults.get(key, '')
            if default is None:
                default = ''
            value = st_loc.text_input(
                'x tick spacing',
                value=default,
                key=tag + key,
            )
            if value == '':
                selected_settings[key] = None
            else:
                selected_settings[key] = float(value)
        key = 'ytick_spacing'
        if key in ask_for:
            default = display_defaults.get(key, '')
            if default is None:
                default = ''
            value = st_loc.text_input(
                'y tick spacing',
                value=default,
                key=tag + key,
            )
            if value == '':
                selected_settings[key] = None
            else:
                selected_settings[key] = float(value)
        key = 'linewidth'
        if key in ask_for:
            selected_settings[key] = st_loc.slider(
                'linewidth',
                0.,
                10.,
                value=display_defaults.get(key, 2.)
            )
        key = 'marker_size'
        if key in ask_for:
            selected_settings[key] = st_loc.slider(
                'marker size',
                0.,
                100.,
                value=display_defaults.get(key, 50.)
            )
        key = 'font_scale'
        if key in ask_for:
            selected_settings[key] = st_loc.slider(
                'font scale',
                0.1,
                2.,
                value=display_defaults.get(key, 1.),
                key=tag + key,
            )
        fig_width, fig_height = matplotlib.rcParams['figure.figsize']
        # The figure size is doubled because this is a primarily horizontal plot
        fig_width *= 2.
        key = 'seaborn_style'
        if key in ask_for:
            value, ind = selectbox(
                st_loc,
                'choose seaborn plot style',
                display_options.get(key, ['whitegrid', 'white', 'darkgrid', 'dark', 'ticks',]),
                index = display_defaults.get(key + '_ind', 0),
                key=tag + key,
            )
            selected_settings[key] = value
            selected_settings[key + '_ind'] = ind
        key = 'fig_width'
        if key in ask_for:
            selected_settings[key] = st_loc.slider(
                'figure width',
                0.1*fig_width,
                2.*fig_width,
                value=display_defaults.get(key, fig_width),
                key=tag + key,
            )
        key = 'fig_height'
        if key in ask_for:
            selected_settings[key] = st_loc.slider(
                'figure height',
                0.1*fig_height,
                2.*fig_height,
                value=display_defaults.get(key, fig_height),
                key=tag + key,
            )
        key = 'include_legend'
        if key in ask_for:
            selected_settings[key] = st_loc.checkbox(
                'include legend',
                value=display_defaults.get(key, True),
                key=tag + key,
            )
        if selected_settings.get('include_legend', False):
            key = 'legend_scale'
            if key in ask_for:
                selected_settings[key] = st_loc.slider(
                    'legend scale',
                    0.1,
                    2.,
                    value=display_defaults.get(key, 1.32),
                    key=tag + key,
                )
            key = 'legend_x'
            if key in ask_for:
                selected_settings[key] = st_loc.slider(
                    'legend x',
                    0.,
                    1.5,
                    value=display_defaults.get(key, 0.),
                    key=tag + key,
                )
            key = 'legend_y'
            if key in ask_for:
                selected_settings[key] = st_loc.slider(
                    'legend y',
                    0.,
                    1.5,
                    value=display_defaults.get(key, 1.4),
                    key=tag + key,
                )
            key = 'legend_ha'
            if key in ask_for:
                value, ind = selectbox(
                    st_loc,
                    'legend horizontal alignment',
                    ['left', 'center', 'right'],
                    index = display_defaults.get(key + '_ind', 0),
                    key=tag + key,
                )
                selected_settings[key] = value
                selected_settings[key + '_ind'] = ind
            key = 'legend_va'
            if key in ask_for:
                value, ind = selectbox(
                    st_loc,
                    'legend vertical alignment',
                    ['upper', 'center', 'lower'],
                    index = display_defaults.get(key + '_ind', 0),
                    key=tag + key,
                )
                selected_settings[key] = value
                selected_settings[key + '_ind'] = ind
        key = 'include_annotations'
        if key in ask_for:
            selected_settings[key] = st_loc.checkbox(
                'include annotations',
                value=display_defaults.get(key, False),
                key=tag + key,
            )
        if selected_settings.get('include_annotations', False):
            key = 'annotations_ha'
            if key in ask_for:
                value, ind = selectbox(
                    st_loc,
                    'annotations horizontal alignment',
                    ['left', 'center', 'right'],
                    index = display_defaults.get(key + '_ind', 0),
                    key=tag + key,
                )
                selected_settings[key] = value
                selected_settings[key + '_ind'] = ind
        key = 'color_palette'
        if key in ask_for:
            value, ind = selectbox(
                st_loc,
                'color palette',
                display_options.get(key, ['deep', 'colorblind', 'dark', 'bright', 'pastel', 'muted',]),
                index = display_defaults.get(key + '_ind', 0),
                key=tag + key,
            )
            selected_settings[key] = value
            selected_settings[key + '_ind'] = ind

        key = 'font'
        if key in ask_for:
            original_font = copy.copy(plt.rcParams['font.family'])[0]
            # This can be finicky, so we'll wrap it in a try/except
            try:
                ## Get all installed fonts
                font_fps = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
                fonts = [os.path.splitext(os.path.basename(_))[0] for _ in font_fps]
                ## Get the default font
                default_font = font_manager.FontProperties(family='Sans Serif')
                default_font_fp = font_manager.findfont(default_font)
                default_index = int(np.where(np.array(font_fps) == default_font_fp)[0][0])
                ## Make the selection
                font_ind = st_loc.selectbox(
                    'Select font',
                    np.arange(len(fonts)),
                    index=default_index,
                    format_func=lambda x: fonts[x],
                    key=tag + key,
                )
                font = font_manager.FontProperties(fname=font_fps[font_ind])
                selected_settings[key] = font.get_name()
            except:
                selected_settings[key] = original_font

        return selected_settings


def selectbox(
    st_loc,
    label: str,
    options: list[str],
    index: int = 0,
    selectbox_or_radio: str = 'selectbox',
    **kwargs
) -> Tuple[str, int]:
    '''Wrapper for st.selectbox that returns not just the selected
    option, but the index of the selected option.

    Args:
        st_loc: Streamlit object (st or st.sidebar) indicating where to place.
        label: A short label explaining to the user what this select widget is for.
        options: Labels for the select options.
        index: The index of the preselected option.
        selectbox_or_radio: Turn into a wrapper for st.radio by feeding
            'radio' to this argument.
    '''

    ind = getattr(st_loc, selectbox_or_radio)(
        label = label,
        options = range(len(options)),
        index = index,
        format_func = lambda index: options[index],
        **kwargs
    )

    return options[ind], ind
