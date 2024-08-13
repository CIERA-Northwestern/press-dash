'''This page is a template for creating a customized page with multiple panels.
This page deliberately avoids using too many functions to make it easier to
understand how to use streamlit.
'''
# Computation imports
import copy
import importlib
import os
import types

import streamlit as st

from .. import dash_builder

importlib.reload(dash_builder)


def main(config_fp: str, user_utils: types.ModuleType = None):
    '''This is the main function that runs the dashboard.

    Args:
        config_fp: The filepath to the configuration file.
        user_utils: The module containing the user-defined functions.
            Defaults to those in root_dash_lib.
    '''

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
    min_year = data['preprocessed']['Calendar Year'].min()
    max_year = data['preprocessed']['Calendar Year'].max()
    years_to_display = list(range(min_year,max_year+1, 1))

    # for fiscal year range calcs
    min_year_fisc = data['preprocessed']['Fiscal Year'].min()
    max_year_fisc = data['preprocessed']['Fiscal Year'].max()
    years_to_display_fisc = list(range(min_year_fisc, max_year_fisc+1, 1))
    
    # Data axes
    # entered search category passed down to filter settings for further specification
    st.subheader('Data Axes')
    axes_object = builder.interface.request_data_axes(st, data['preprocessed'])

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

    months_to_num = {'January':1, 'February':2, 'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
    # filters by year binning method
    if (axes_object['x_column_ind'] == 2):
        # tosses all entries that do not fall in specified calendar year
        year = int(axes_object['x_column'].split(':')[1])
        data['time_adjusted'] = data['selected'][data['selected']['Date'].dt.year == year]
        builder.settings.common['data']['x_column'] = 'Month'
    elif (axes_object['x_column_ind'] == 3):
        fisc_year = int(axes_object['x_column'].split(':')[1])
        data['time_adjusted'] = data['selected'][data['selected']['Fiscal Year'] == fisc_year]
        builder.settings.common['data']['x_column'] = 'Fiscal Month'
    elif axes_object['x_column_ind'] == 4:
        # tosses all entries that do not fall in specified month across all years
        month = str(axes_object['x_column'].split(':')[1])
        data['time_adjusted'] = data['selected'][data['selected']['Date'].dt.month == months_to_num[month]]
        builder.settings.common['data']['x_column'] = 'Calendar Year'
    else:
        data['time_adjusted'] = data['selected']

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

    # If you are going to change the configs for x_columns, make sure they are reflected below!
    if len(list(data['aggregated'].columns)) != 0:
        data['aggregated'] = data['aggregated'].T
        data['totals'] = data['totals'].T

        if (builder.settings.common['data']['x_column'] == 'Month') or (builder.settings.common['data']['x_column'] == 'Fiscal Month'):
            for month in months_to_num.values():
                if month not in data['aggregated'].columns:
                    data['aggregated'].insert(month-1, month, [0 for i in range(len(data['aggregated'].index))])
                    data['totals'].insert(month-1, month, [0 for i in range(len(data['totals'].index))])
        elif builder.settings.common['data']['x_column'] == 'Fiscal Year':
            for years in years_to_display_fisc:
                if years not in data['aggregated'].columns:
                    data['aggregated'].insert(years-min_year_fisc, years, [0 for i in range(len(data['aggregated'].index))])
                    data['totals'].insert(years-min_year_fisc, years, [0 for i in range(len(data['totals'].index))])
        else:
            for years in years_to_display:
                if years not in data['aggregated'].columns:
                    data['aggregated'].insert(years-min_year, years, [0 for i in range(len(data['aggregated'].index))])
                    data['totals'].insert(years-min_year, years, [0 for i in range(len(data['totals'].index))])

        data['aggregated'] = data['aggregated'].T
        data['totals'] = data['totals'].T
    
    # adds NaN values to dataframe for viewing
    for topic in builder.settings.common['filters']['categorical'][category_specific['groupby_column']]:
        if topic not in data['aggregated'].columns:
            data['aggregated'][topic] = [0 for i in range(len(data['aggregated'].index))]

    # Lineplot
    local_key = 'lineplot'
    st.header(config.get('lineplot_header', 'Lineplot'))
    st.text("Note: some data entries may correspond to multiple categories, and so may be contribute to dataset of each.\n As such, the all categories combined may exceed the total, which only counts each entry once***")
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
            totals = data['totals'],
            **builder.settings.get_settings(local_key)
        )
    else:
        builder.data_viewer.lineplot(
            df = data['aggregated'],
            **builder.settings.get_settings(local_key)
        )

    # View the data directly
    builder.data_viewer.write(data)

    # Settings download button
    st.sidebar.markdown('# Settings Download')
    builder.settings.download_button(st.sidebar)