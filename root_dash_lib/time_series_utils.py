'''Time-series functions.
Most functions should be useful for most time-series datasets.
'''

import io
import pandas as pd
import streamlit as st

from . import plot_utils

################################################################################

def get_year( date, start_of_year='January 1', years_min=None, years_max=None ):
    '''Get the year from a date, with a user-specified start date
    for the year.

    Args:
        date (datetime.datetime): The date to get the year from.
        start_of_year (str): The start of the year, e.g. 'January 1'.
        years_min (int): The minimum year to include. Defaults to the minimum year in the data.
        years_max (int): The maximum year to include. Defaults to the maximum year in the data.

    Returns:
        years (pd.Series of int): The year of the date.
    '''

    # Get date bins
    if years_min is None:
        years_min = date.min().year - 1
    if years_max is None:
        years_max = date.max().year + 1
    date_bins = pd.date_range(
        '{} {}'.format( start_of_year, years_min ),
        pd.Timestamp.now() + pd.offsets.DateOffset( years=1 ),
        freq = pd.offsets.DateOffset( years=1 ),
    )
    date_bin_labels = date_bins.year[:-1]

    # The actual binning
    years = pd.cut( date, date_bins, labels=date_bin_labels ).astype( 'Int64' )

    return years

################################################################################

def aggregate( selected_df, time_bin_column, y_column, groupby_column, count_or_sum ):
    '''Aggregate. Wrapper function for other functions for the sake of caching.

    Args:
        selected_df (pd.DataFrame): The dataframe containing the selected data.
        time_bin_column (str): The column containing the year or other time bin value.
        y_column (str): The column containing the data to count or sum.
        groupby_column (str): The category to group the data by, e.g. 'Research Topics'.
        count_or_sum (str): Whether to count or sum.

    Returns:
        agged (pd.DataFrame): The dataframe containing the aggregated_df data per year.
        total (pd.Series): The series containing the aggregated_df data per year, overall.
    '''

    if count_or_sum == 'Count':
        return count( selected_df, time_bin_column, y_column, groupby_column )
    elif count_or_sum == 'Sum':
        return sum( selected_df, time_bin_column, y_column, groupby_column )
    else:
        raise KeyError( 'How did you get here?' )

################################################################################

################################################################################

def view_time_series(
        view,
        df,
        preprocessed_df,
        selected_df,
        aggregated_df,
        total,
        data_kw,
        lineplot_kw,
        stackplot_kw,
        config,
        filetag = None,
        tag = '',
        df_tag = 'selected',
    ):

    if tag != '':
        tag += ':'

    # For easy access
    time_bin_column, y_column, groupby_column = data_kw['time_bin_column'], data_kw['y_column'], data_kw['groupby_column']

    # Tag for the file
    if filetag is None:
        filetag = '{}.{}.{}'.format( *[
            _.lower().replace( ' ', '_' )
            for _ in [ time_bin_column, y_column, groupby_column ]
        ] )

    if view == 'lineplot':
        # st.spinner provides a visual indicator that the data is loading
        with st.spinner():
            fig = plot_utils.lineplot(
                aggregated_df,
                total,
                **lineplot_kw
            )

            st.pyplot( fig )
        # Add a download button for the image
        # The image is saved as PDF, enabling arbitrary resolution
        fn = 'lineplot.{}.pdf'.format( filetag )
        img = io.BytesIO()
        fig.savefig( img, format='pdf', bbox_inches='tight' )
        download_kw = {
            'label': "Download Figure",
            'data': img,
            'file_name': fn,
            'mime': "text/pdf",
            'key': '{}lineplot'.format( tag ),
        }

    elif view == 'stackplot':
        with st.spinner():
            fig = plot_utils.stackplot(
                aggregated_df,
                total,
                **stackplot_kw
            )
            st.pyplot( fig )

        # Add a download button for the image
        fn = 'stackplot.{}.pdf'.format( filetag )
        img = io.BytesIO()
        fig.savefig( img, format='pdf', bbox_inches='tight' )
        download_kw = {
            'label': "Download Figure",
            'data': img,
            'file_name': fn,
            'mime': "text/pdf",
            'key': '{}stackplot'.format( tag ),
        }

    elif view == 'data':

        def view_data( df_tag ):
            if df_tag == 'original':
                st.markdown( 'This table contains all {} selected entries, prior to pre-processing.'.format( len( df ) ) )
                ids = getattr( df, config['primary_id_column'] )
                show_df = df.loc[ids.isin( selected_df['id'] )]
            elif df_tag == 'preprocessed':
                st.markdown( 'This table contains all {} selected entries, after pre-processing and prior to any recategorization.'.format( len( preprocessed_df ) ) )
                show_df = preprocessed_df.loc[preprocessed_df['id'].isin( selected_df['id'] )]
            elif df_tag == 'recategorized':
                st.markdown( 'This table contains all {} selected entries, after recategorization.'.format( len( selected_df ) ) )
                show_df = selected_df
            elif df_tag == 'aggregated':
                show_df = aggregated_df

            st.write( show_df )

            return show_df

        # The selected data is shown in a table,
        # so that the user can always see the raw data being plotted
        st.header( 'Selected Data' )
        with st.spinner():
            show_df = view_data( df_tag )

        # Add a download button for the data
        fn = 'data.{}.csv'.format( filetag )
        f = io.BytesIO()
        selected_df.to_csv( f )
        download_kw = {
            'label': "Download Selected Data",
            'data': f,
            'file_name': fn,
            'mime': "text/plain",
            'key': 'data.{}'.format( filetag ),
            'key': '{}data'.format( tag ),
        }

        # Return here because we're also return the show_df
        return download_kw, show_df

    return download_kw