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

def main(config_fp: str, user_utils: types.ModuleType=None):
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

    # Global settings
    st.sidebar.markdown('# Data Settings')
    builder.interface.request_data_settings(st.sidebar)
    st.sidebar.markdown('# View Settings')
    builder.interface.request_view_settings(st.sidebar)

    # Recategorize data
    selected_settings = builder.settings.common['data']
    data['recategorized'] = builder.recategorize_data(
        preprocessed_df=data['preprocessed'],
        new_categories=builder.config.get( 'new_categories', {} ),
        recategorize=selected_settings['recategorize'],
        combine_single_categories=selected_settings.get( 'combine_single_categories', False),
    )

    # Data filter settings
    st.subheader('Data Filters')
    builder.interface.request_filter_settings(
        st,
        data['recategorized'],
    )

    # Apply data filters
    data['selected'] = builder.filter_data(
        data['recategorized'],
        builder.settings.common['filters']['text'],
        builder.settings.common['filters']['categorical'],
        builder.settings.common['filters']['numerical'],
    )

    # Data axes
    st.subheader('Data Axes')
    builder.interface.request_data_axes(st)

    # Aggregate data
    data['aggregated'] = builder.aggregate(
        data['recategorized'],
        builder.settings.common['data']['x_column'],
        builder.settings.common['data']['y_column'],
        builder.settings.common['data']['groupby_column'],
        builder.settings.common['data']['aggregation_method'],
    )
    # Aggregate data
    data['totals'] = builder.aggregate(
        data['recategorized'],
        builder.settings.common['data']['x_column'],
        builder.settings.common['data']['y_column'],
        aggregation_method=builder.settings.common['data']['aggregation_method'],
    )

    # Lineplot
    local_key = 'lineplot'
    st.header(config.get('lineplot_header','Lineplot'))
    local_opt_keys, common_opt_keys, unset_opt_keys = builder.settings.get_local_global_and_unset(
        function = builder.data_viewer.lineplot,
    )
    builder.interface.request_view_settings(
            st,
            ask_for=unset_opt_keys,
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
        **builder.settings.get_local_settings(local_key)
    )

    # DEBUG
    st.write(builder.settings)

    # View the data directly
    builder.data_viewer.write(data)

    # for view in [ 'lineplot', 'stackplot', 'data' ]:

    #     # For datawe include additional options.
    #     if view == 'data':
    #         df_tag = st.radio(
    #             'What data do you want to see?',
    #             [ 'original', 'preprocessed', 'recategorized', 'aggregated' ],
    #             index=0,
    #             horizontal=True,
    #             key='{}:df_tag'.format( tag ),
    #         )
    #     else:
    #         df_tag = 'selected'
    #     download_kw = st.cache_data( time_series_utils.view_time_series )(
    #         view,
    #         df,
    #         preprocessed_df,
    #         selected_df,
    #         aggregated_df,
    #         total,
    #         data_kw,
    #         lineplot_kw,
    #         stackplot_kw,
    #         config,
    #         tag=tag,
    #         df_tag=df_tag,
    #     )
    #     if view == 'data':
    #         download_kw, show_df = download_kw
    #         if st.checkbox( 'View a subset?', value=False, key='{}:view_subset'.format( tag ) ):
    #             try:
    #                 columns_to_show = st.multiselect(
    #                     'Which columns do you want to show?',
    #                     show_df.columns,
    #                     default=[ data_kw['time_bin_column'], data_kw['y_column'], data_kw['groupby_column'] ],
    #                 )
    #             except:
    #                 columns_to_show = st.multiselect(
    #                     'Which columns do you want to show?',
    #                     show_df.columns,
    #                 )

    #             st.write( show_df[ columns_to_show ] )
    #     st.download_button( **download_kw )

    # # Check for the "STOP" environment variable
    # # This is a hack to stop the streamlit app from running
    # if os.environ.get("STOP_STREAMLIT"):
    #     st.stop()