'''This page is a template for creating a customized page with multiple panels.
This page deliberately avoids using too many functions to make it easier to
understand how to use streamlit.
'''
# Computation imports
import copy
import importlib
import os
import types
import datetime

import streamlit as st
import pandas as pd

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
    setting_check = builder.interface.request_data_settings(st.sidebar)

    st.sidebar.markdown('# View Settings')
    builder.interface.request_view_settings(st.sidebar)

    # got rid of the data recategorization function
    # because it doesnt really match our goals for this dataset
    # all the infrastructure is still there though
    # if you would like to re-add, uncomment relevant sections in
    # base_page, interface, dash_builder and data_handler
    '''
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
    '''

    # for future reference, if you want to set artificial bounds for year/timescale, do it here
    min_year = int(data['preprocessed']['Date'].dt.year.min())
    max_year = int(data['preprocessed']['Date'].dt.year.max())
    
   
    # Data axes
    # entered search category passed down to filter settings for further specification
    st.subheader('Data Axes')    
    st.text("Note: entries from before Jan 1st, 2014 are classified as LEGACY for the purposes of data categorization")

    axes_object = builder.interface.request_data_axes(st, max_year, min_year)
    #print(axes_object)

    # filters data as per specs
    # filters data as per specs
    temp_data, selecset = builder.interface.process_filter_settings(
        st,
        data['preprocessed'],
        value=builder.settings.get_settings(common_to_include=['data'])['groupby_column'],
    )
    #print(builder.settings.common['data'])

    # Apply data filters
    data['selected'] = builder.filter_data(
        temp_data,
        builder.settings.common['filters'],
    )


    
    
    ## If I have time:
    # move all of the below into a seperate 'time adjuster' file
    # want to make base page as indepedent as possible 

    # filters data by year bounds selected (so that only entries which fall into this year-bound are displayed)
    reverse_month_dict = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May',6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}

    # extracts time information from axes_object
    time_object = axes_object['x_column'].split(':')
    month_start = int(time_object[1])
    year_start = int(time_object[2])
    year_end = int(time_object[3])
    years_to_display = list(range(year_start+1, year_end+1))

    month_redef = [x if x<=12 else x-12 for x in range(month_start, 12+month_start)]

    data['selected']['Reindexed Year'] = utils.get_year(
            data['selected']['Date'], "{} 1".format(reverse_month_dict[month_start]),
            default_date_start=min_year,
            default_date_end=max_year
        )
    data['windowed'] = data['selected'][data['selected']['Reindexed Year'] == year_start]

    if len(years_to_display) != 0:
        for i in years_to_display:
            temp = data['selected'][data['selected']['Reindexed Year'] == i]
            data['windowed'] = pd.concat([data['windowed'], temp])

        builder.settings.common['data']['x_column'] = 'Reindexed Year'
    if len(years_to_display) == 0:

        # For Fiscal Month visualizations
        def month_fisc_converter(month:int, forward=True):
            return month_redef.index(month)+1
        
        # set 'reindexed month' to the result of month_fisc_converter
        data['windowed'].loc.__setitem__((slice(None), 'Reindexed Month'), data['windowed'].__getitem__('Date').dt.month.map(month_fisc_converter))
        builder.settings.common['data']['x_column'] = 'Reindexed Month'
        
        # extract real month, just to have
        def month_extractor(month):
            return reverse_month_dict[int(month)]
        data['windowed']['Calendar Month'] = data['windowed']['Date'].dt.month.apply(month_extractor)

    ### if no entries fall into this time window, we instantiate the whole graph with zeroes
    if data['windowed'].empty:
        locd = {}
        for i in data['windowed'].columns:
            locd[i] = "normalization value; ignore for data purposes"
        data['windowed'].loc[0] = locd
            
    # Here, we make a human-readable final datasheet by collapsing the exploded entries back into single, by unique entry id
    data['final processed'] = data['preprocessed'].filter(items=set(data['windowed'].index), axis=0)

    # aggregation things v
    time_class = builder.settings.common['data']['x_column']
    
    # total data
    data['totals'] = builder.aggregate(
        data['windowed'],
        ('Calendar Month' if time_class == "Reindexed Month" else time_class),
        builder.settings.common['data']['y_column'],
        aggregation_method=builder.settings.common['data']['aggregation_method'],
    )
    
     # Aggregate data
    data['aggregated'] = builder.aggregate(
            data['windowed'],
            ('Calendar Month' if time_class == "Reindexed Month" else time_class),
            builder.settings.common['data']['y_column'],
            builder.settings.common['data']['groupby_column'],
            builder.settings.common['data']['aggregation_method'],
    )

    # the above functions create a rich dataframe; with entries only corresponding to x/y column pairings with nonzero values
    # for the purposes of visualization, this is not the most helpful - it produces tables of different dimensions based on data
    # below, we normalize it to create a standard sparse dataframe which we can pass to the plotting software

    
    # creates the total by instance sheet, which gives every category across all time as a bar chart value
    temp = data['aggregated'].sum()
    data['total by instance'] = pd.DataFrame(index = temp.index, data={'Aggregate': temp.values})
    data['total by instance'].sort_values(ascending=False, by='Aggregate', inplace=True)
    
    ### adds all years for which we have data back into aggregated dataframe (even if all zero that time bin);
    # more accurately displays trends across multiple years
    years_to_display.insert(0, year_start)
    
    # If you are going to change the configs for x_columns, make sure they are reflected below!
    if len(list(data['aggregated'].columns)) != 0:

        data['aggregated'] = data['aggregated'].T
        data['totals'] = data['totals'].T
        
        ### NEW ###
        if time_class == 'Reindexed Month':
            xaxis = [reverse_month_dict[i] for i in month_redef]
        elif time_class == 'Reindexed Year':
            xaxis = years_to_display
        
        yaxis = pd.unique(data['selected'][builder.settings.common['data']['groupby_column']]) 
        datumx = {}
        for x in xaxis:
            datumy = {}
            if x in data['aggregated'].columns:
                for y in yaxis:
                    if y in data['aggregated'].index:
                        datumy[y] = int(getattr(data['aggregated'][x], y, 0))
                    else:
                        datumy[y] = 0
            else:
                for y in yaxis:
                    datumy[y] = 0
            datumx[str(x)] = datumy

        aggregatee = pd.DataFrame(data = datumx)
        data['aggregated'] = aggregatee

        totalx = {}
        for x in xaxis:
            if x in data['totals'].columns:
                totalx[x] = int(getattr(data['totals'][x], builder.settings.common['data']['y_column'], 0))
            else:
                totalx[x] = 0    
        totalee = pd.Series(data=totalx)
        data['totals'] = totalee

        data['aggregated'] = data['aggregated'].T

    else:
        datumx = {}
        for i in range(1, 13):
            datumy = {}
            for j in data['windowed'].columns:
                datumy[j] = 0
            datumx[i] = datumy
        aggregatee = pd.DataFrame(datumx)

        totalx = {}
        for i in range(1, 13):    
            totalx[x] = 0    
        totalee = pd.Series(data=totalx)
        data['totals'] = totalee

        data['aggregated'] = aggregatee.T

    
    # adds NaN values to dataframe for viewing
    if 'categorical' in builder.settings.common['filters']:
        for topic in builder.settings.common['filters']['categorical'][builder.settings.get_settings(common_to_include=['data'])['groupby_column']]:
            if topic not in data['aggregated'].columns:
                data['aggregated'][topic] = [0 for i in range(len(data['aggregated'].index))]

    st.header('Data Plotting')
    st.text("Note: data entries may correspond to multiple categories, and so be represented in each grouping")
    st.text("please be cognizant of this; an accurate count of all entries is provided by 'total' option in data settings")


    # Lineplot IF data option is total or none
    data_option = builder.settings.common['data']['data_options']
    if data_option in ['No Total', 'Only Total', 'Standard']:
        local_key = 'lineplot'
        st.subheader('Line Plot Visualization')
        '''        
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
        '''
    #constructs line plot based on specifications provided
        if data_option == "No Total":
            builder.data_viewer.testplot(
                df = data['aggregated'],
                month_reindex = month_redef if builder.settings.common['data']['x_column_ind'] == 0 else None, 
                year_reindex = years_to_display,
                y_label=builder.settings.common['data']['y_column'],
                x_label=builder.settings.common['data']['x_column'],
                category=builder.settings.common['data']['groupby_column'],
                view_mode=builder.settings.common['view']['view_mode']
            )
        elif data_option == "Only Total":
            builder.data_viewer.testplot(
                df = data['totals'].to_frame(name="totals"),
                month_reindex = month_redef if builder.settings.common['data']['x_column_ind'] == 0 else None, 
                year_reindex=years_to_display,
                y_label=builder.settings.common['data']['y_column'],
                x_label=builder.settings.common['data']['x_column'],
                category=builder.settings.common['data']['groupby_column'],
                view_mode=builder.settings.common['view']['view_mode']
                #**builder.settings.get_settings(local_key)
            )
        elif data_option == "Standard":
            builder.data_viewer.testplot(
                df = data['aggregated'],
                month_reindex = month_redef if builder.settings.common['data']['x_column_ind'] == 0 else None, 
                year_reindex = years_to_display,
                totals = data['totals'],
                y_label=builder.settings.common['data']['y_column'],
                x_label=builder.settings.common['data']['x_column'],
                category=builder.settings.common['data']['groupby_column'],
                view_mode=builder.settings.common['view']['view_mode']
            )
    # Bar Plot IF data option is aggregated
    elif data_option == "Year Aggregate":
        #print(data['total_by_instance'].columns)
        st.subheader('Bar Plot Visualization')
        builder.data_viewer.barplot(
            data['total by instance'],
        )
    
    elif data_option == "testing":
        st.subheader("testing chart; please disregard")
        builder.data_viewer.testplot(
            df = data['aggregated'],
            month_reindex = month_redef if builder.settings.common['data']['x_column_ind'] == 0 else None, 
            year_reindex = years_to_display,
            totals = data['totals'],
            y_label=builder.settings.common['data']['y_column'],
            x_label=builder.settings.common['data']['x_column'],
            category=builder.settings.common['data']['groupby_column'],
            view_mode=builder.settings.common['view']['view_mode']
        )
    
    # View the data directly
    builder.data_viewer.write(data)

    # Settings download button
    st.sidebar.markdown('# Settings Download')
    builder.settings.download_button(st.sidebar)