'''This page is a template for creating a customized page with multiple panels.
This page deliberately avoids using too many functions to make it easier to
understand how to use streamlit.
'''
# Computation imports
import copy
import importlib
import os
import types

import pandas as pd
import streamlit as st

from .. import dash_builder, utils

importlib.reload(dash_builder)


def main(config_fp: str, user_utils: types.ModuleType = None):
    '''This is the main function that runs the dashboard.

    Args:
        config_fp: The filepath to the configuration file.
        user_utils: The module containing the user-defined functions.
            Defaults to those in root_dash_lib.
    '''
    pd.options.mode.copy_on_write = True
    # This must be the first streamlit command
    st.set_page_config(layout='wide')

    # Get the builder used to construct the dashboard
    builder = dash_builder.DashBuilder(config_fp, user_utils=user_utils)

    # Set the title that shows up at the top of the dashboard
    st.title(builder.config.get('page_title','Dashboard'))
    
    # Prep data
    data, config = builder.prep_data(builder.config)
    builder.config.update(config)

    st.sidebar.markdown('# Settings Upload')
    combined_settings = builder.settings.upload_button(st.sidebar)

    # Global settings
    #st.sidebar.markdown('# Data Settings')
    setting_check, toggle = builder.interface.request_data_settings(st.sidebar)

    st.sidebar.markdown('# View Settings')
    builder.interface.request_view_settings(st.sidebar)

    # Recategorize data
    selected_settings = builder.settings.common['data']
    data['recategorized'] = builder.recategorize_data(
        preprocessed_df=data['preprocessed'],
        new_categories=builder.config.get('new_categories', {}),
        recategorize=selected_settings['recategorize'],
        combine_single_categories=selected_settings.get(
            'combine_single_categories',
            False
        ),
    )

    # Identify year bounds for any range calculations
    # for future reference, if you want to set artificial bounds for year/timescale, do it here
    min_year = data['preprocessed']['Date'].dt.year.min()
    max_year = data['preprocessed']['Date'].dt.year.max()
    
    # Data axes
    # entered search category passed down to filter settings for further specification
    st.subheader('Data Axes')
    axes_object = builder.interface.request_data_axes(st, data['preprocessed'], min_year, max_year)
    
    # catches specified groupby category
    category_specific = builder.settings.get_settings(common_to_include=['data'])

    # filters data as per specs
    builder.interface.process_filter_settings(
        st,
        data['recategorized'],
        value=category_specific['groupby_column']
    )

    # Apply data filters
    data['selected'] = builder.filter_data(
        data['recategorized'],
        builder.settings.common['filters']['categorical'],
    )

    # filters data by year bounds selected (so that only entries which fall into this year-bound are displayed)
    reverse_month_dict = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May',6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}
    if (axes_object['x_column_ind'] == 0):

        
        # extracts time information from axes_object
        time_object = axes_object['x_column'].split(':')
        month_start = int(time_object[1])
        year_start = int(time_object[2])
        year_end = int(time_object[3])
        years_to_display = list(range(year_start+1, year_end+1))

        month_redef = [x if x<=12 else x-12 for x in range(month_start, 12+month_start)]


        data['selected']['Reindexed Year'] = utils.get_year(
                data['selected']['Date'], "{} 1".format(reverse_month_dict[month_start])
            )
        data['time_adjusted'] = data['selected'][data['selected']['Reindexed Year'] == year_start]
        
        if len(years_to_display) != 0:
            for i in years_to_display:
                temp = data['selected'][data['selected']['Reindexed Year'] == i]
                data['time_adjusted'] = pd.concat([data['time_adjusted'], temp])

            builder.settings.common['data']['x_column'] = 'Reindexed Year'
        if len(years_to_display) == 0:
            
            # For Fiscal Month visualizations
            def month_fisc_converter(month:int, forward=True):
                return month_redef.index(month)+1
            
            data['time_adjusted'].loc.__setitem__((slice(None), 'Reindexed Month'), data['time_adjusted'].__getitem__('Date').dt.month.map(month_fisc_converter))
            builder.settings.common['data']['x_column'] = 'Reindexed Month'
    else:
        data['time_adjusted'] = data['selected']
        builder.settings.common['data']['x_column'] = 'Calendar Year'

    # Aggregate data
    data['aggregated'] = builder.aggregate(
        data['time_adjusted'],
        builder.settings.common['data']['x_column'],
        builder.settings.common['data']['y_column'],
        builder.settings.common['data']['groupby_column'],
        builder.settings.common['data']['aggregation_method'],
    )

    # Aggregate data
    data['totals'] = builder.aggregate(
        data['time_adjusted'],
        builder.settings.common['data']['x_column'],
        builder.settings.common['data']['y_column'],
        aggregation_method=builder.settings.common['data']['aggregation_method'],
    )

    
    ### adds all years for which we have data back into aggregated dataframe (even if all zero that time bin);
    # more accurately displays trends across multiple years
    years_to_display.insert(0, year_start)

    
    # If you are going to change the configs for x_columns, make sure they are reflected below!
    if len(list(data['aggregated'].columns)) != 0:
        data['aggregated'] = data['aggregated'].T
        data['totals'] = data['totals'].T
    
        if builder.settings.common['data']['x_column'] == 'Reindexed Month':
            for month in month_redef:
                if month not in data['aggregated'].columns:
                    data['aggregated'].insert(month-1, month, [0 for i in range(len(data['aggregated'].index))])
                    data['totals'].insert(month-1, month, [0 for i in range(len(data['totals'].index))])
        elif builder.settings.common['data']['x_column'] == 'Reindexed Year':
            for years in years_to_display:
                if years not in data['aggregated'].columns:
                    data['aggregated'].insert(years-min(years_to_display), years, [0 for i in range(len(data['aggregated'].index))])
                    data['totals'].insert(years-min(years_to_display), years, [0 for i in range(len(data['totals'].index))])

        data['aggregated'] = data['aggregated'].T
        data['totals'] = data['totals'].T
    
    # adds NaN values to dataframe for viewing
    for topic in builder.settings.common['filters']['categorical'][category_specific['groupby_column']]:
        if topic not in data['aggregated'].columns:
            data['aggregated'][topic] = [0 for i in range(len(data['aggregated'].index))]

    # Lineplot
    local_key = 'lineplot'
    st.header(config.get('lineplot_header', 'Lineplot'))
    st.text("Note: entries may correspond to multiple data tags/categories, and so may contribute to the trendline of each (double-counting).\n this results in a conflict between aggregated data and total trendline, which only counts each entry once.\n Users and audience must be made clear of this discrepancy; in essence, total single-counts, aggregate double-counts")
    with st.expander('Lineplot settings'):
        local_opt_keys, common_opt_keys, unset_opt_keys = builder.settings.get_local_global_and_unset(
            function=builder.data_viewer.lineplot,
        )
        builder.interface.request_view_settings(
                st,
                ask_for=unset_opt_keys,
                local_key=local_key,
                selected_settings=builder.settings.local.setdefault('lineplot', {}),
                tag=local_key,
                default_x=builder.settings.common['data']['x_column'],
                default_y=builder.settings.common['data']['y_column'],
        )
        local_opt_keys, common_opt_keys, unset_opt_keys = builder.settings.get_local_global_and_unset(
            function = builder.data_viewer.lineplot,
            local_key=local_key,
        )

    
    #constructs line plot with or without the 'total' line, depending on if relevant feature has been toggled
    if toggle:
        builder.data_viewer.lineplot(
            df = data['aggregated'],
            month_reindex = month_redef if builder.settings.common['data']['x_column_ind'] == 0 else None, 
            year_reindex = years_to_display,
            totals = data['totals'],
            **builder.settings.get_settings(local_key)
        )
    else:
        builder.data_viewer.lineplot(
            df = data['aggregated'],
            month_reindex = month_redef if builder.settings.common['data']['x_column_ind'] == 0 else None, 
            year_reindex=years_to_display,
            **builder.settings.get_settings(local_key)
        )

    # View the data directly
    builder.data_viewer.write(data)

    # Settings download button
    st.sidebar.markdown('# Settings Download')
    builder.settings.download_button(st.sidebar)