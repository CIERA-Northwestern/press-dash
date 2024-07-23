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
    st.sidebar.markdown('# Data Settings')
    builder.interface.request_data_settings(
        st.sidebar,
    )
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

    # Data axes
    # entered search category passed down to filter settings for further specification
    st.subheader('Data Axes')
    builder.interface.request_data_axes(st)

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

    # Aggregate data
    data['aggregated'] = builder.aggregate(
        data['selected'],
        builder.settings.common['data']['x_column'],
        builder.settings.common['data']['y_column'],
        builder.settings.common['data']['groupby_column'],
        builder.settings.common['data']['aggregation_method'],
    )
    # Aggregate data
    data['totals'] = builder.aggregate(
        data['selected'],
        builder.settings.common['data']['x_column'],
        builder.settings.common['data']['y_column'],
        aggregation_method=builder.settings.common['data']['aggregation_method'],
    )

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
        )
        local_opt_keys, common_opt_keys, unset_opt_keys = builder.settings.get_local_global_and_unset(
            function = builder.data_viewer.lineplot,
            local_key=local_key,
        )
    builder.data_viewer.lineplot(
        df = data['aggregated'],
        totals = data['totals'],
        **builder.settings.get_settings(local_key)
    )

    # View the data directly
    builder.data_viewer.write(data)

    # Settings download button
    st.sidebar.markdown('# Settings Download')
    builder.settings.download_button(st.sidebar)