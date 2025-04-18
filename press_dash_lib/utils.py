'''Miscellaneous useful functions.
'''

import pandas as pd


def get_year(date, start_of_year='January 1', years_min=None, years_max=None, default_date_start=None, default_date_end=None):
    '''Get the year from a date, with a user-specified start date
    for the year.
    This is commonly used for loading data, so it's kept in the user utils.

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
    try:
        years_min = int(years_min)
        years_max = int(years_max)
    except:
        years_min = default_date_start
        years_max = default_date_end

    date_bins = pd.date_range(
        '{} {}'.format(start_of_year, years_min),
        pd.Timestamp.now() + pd.offsets.DateOffset(years=1),
        freq = pd.offsets.DateOffset(years=1),
        inclusive="left",
    )
    
    date_bin_labels = date_bins.year[:-1]
    #print(date_bin_labels)
    # The actual binning
    years = pd.cut(date, date_bins, right=False, labels=date_bin_labels).astype('Int64')

    return years
