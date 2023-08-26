'''Module for viewing data: Plotting, tables, etc.
'''
import copy
import re
import types
from typing import Tuple

import numpy as np
import pandas as pd
import streamlit as st

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.figure
import seaborn as sns

from .data_handler import DataHandler
from .settings import Settings

class DataViewer:
    '''Class for viewing data.

    Args:
        config: The config dictionary.
        data_handler: The data handler containing the relevant data.
    '''

    def __init__(self, config: dict, settings: Settings):
        self.config = config
        self.settings = settings

    def write(self, data, data_key: str=None, st_loc=st, columns: list[str]=None):
        '''Show a specified dataframe.

        Args:
            data: Data dict containing the data frames.
            data_key: key to search the data handler for.
                Defaults to providing a widget.
            st_loc: Where to show the data.
            columns: Columns to show. Defaults to all.
        '''

        if data_key is None:
            data_key = st_loc.radio(
                'View what data?',
                options=data.keys(),
                horizontal=True,
            )

        if data_key not in data:
            st.write('{} not found in data'.format( data_key ))
            return

        shown_df = data[data_key]
        if columns is not None:
            shown_df = shown_df[columns]

        st.write(data[data_key])

    def lineplot(
            df: pd.DataFrame,
            x_key: str = None,
            total: pd.Series = None,
            cumulative: bool = False,
        ) -> matplotlib.figure.Figure:
        '''General-purpose lineplot.

        Returns:
            fig: The figure containing the plot.
        '''

        if cumulative:
            df = df.cumsum( axis='rows' )
            if total is not None:
                total = total.cumsum()

        xs = df.index
        categories = df.columns

        sns.set( font=lineplot_kw['font'], style=lineplot_kw['seaborn_style'] )
        plot_context = sns.plotting_context("notebook")

        fig = plt.figure( figsize=( lineplot_kw['fig_width'], lineplot_kw['fig_height'] ) )
        ax = plt.gca()
        for j, category_j in enumerate( categories ):

            ys = df[category_j]

            ax.plot(
                xs,
                ys,
                linewidth = lineplot_kw['linewidth'],
                alpha = 0.5,
                zorder = 2,
                color = lineplot_kw['category_colors'][category_j],
            )
            ax.scatter(
                xs,
                ys,
                label = category_j,
                zorder = 2,
                color = lineplot_kw['category_colors'][category_j],
                s = lineplot_kw['marker_size'],
                )

            # Add labels
            if lineplot_kw.get( 'include_annotations', False ):
                label_y = ys.iloc[-1]

                text = ax.annotate(
                    text = category_j,
                    xy = ( 1, label_y ),
                    xycoords = matplotlib.transforms.blended_transform_factory( ax.transAxes, ax.transData ),
                    xytext = ( -5 + 10 * ( lineplot_kw['annotations_horizontal_alignment'] == 'left' ), 0 ),
                    va = 'center',
                    ha = lineplot_kw['annotations_horizontal_alignment'],
                    textcoords = 'offset points',
                )
                text.set_path_effects([
                    path_effects.Stroke(linewidth=2.5, foreground='w'),
                    path_effects.Normal(),
                ])

        if lineplot_kw['show_total']:
            ax.plot(
                xs,
                total,
                linewidth = lineplot_kw['linewidth'],
                alpha = 0.5,
                color = 'k',
                zorder = 1,
            )
            ax.scatter(
                xs,
                total,
                label = 'Total',
                color = 'k',
                zorder = 1,
                s = lineplot_kw['marker_size'],
            )

        ymax = lineplot_kw['y_lim'][1]

        ax.set_xticks( xs.astype( int ) )
        count_ticks = np.arange( 0, ymax, lineplot_kw['tick_spacing'] )
        ax.set_yticks( count_ticks )

        if lineplot_kw['log_yscale']:
            ax.set_yscale( 'log' )

        ax.set_xlim( xs[0], xs[-1] )
        ax.set_ylim( lineplot_kw['y_lim'] )


        if lineplot_kw.get( 'include_legend', False ):
            l = ax.legend(
                bbox_to_anchor = ( lineplot_kw['legend_x'], lineplot_kw['legend_y'] ),
                loc = '{} {}'.format(
                    lineplot_kw['legend_vertical_alignment'],
                    lineplot_kw['legend_horizontal_alignment']
                ), 
                framealpha = 1.,
                fontsize = plot_context['legend.fontsize'] * lineplot_kw['legend_scale'],
                ncol = len( categories ) // 4 + 1
            )

        # Labels, inc. size
        ax.set_xlabel( lineplot_kw['x_label'], fontsize=plot_context['axes.labelsize'] * lineplot_kw['font_scale'] )
        ax.set_ylabel( lineplot_kw['y_label'], fontsize=plot_context['axes.labelsize'] * lineplot_kw['font_scale'] )
        ax.tick_params( labelsize=plot_context['xtick.labelsize']*lineplot_kw['font_scale'] )

        # return facet_grid
        return fig


def get_tick_range_and_spacing( total, cumulative, ax_frac=0.1 ):
    '''Solid defaults for ymax and the tick_spacing.

    Args:
        total (pd.Series): The total counts or sums.
        cumulative (bool): Whether the data is cumulative.
        ax_frac (float): Fraction of axis between ticks.

    Returns:
        ymax (float): The maximum y value.
        tick_spacing (float): The spacing between ticks.
    '''

    # Settings for the lineplot
    if cumulative:
        ymax = total.sum().max() * 1.05
    else:
        ymax = total.values.max() * 1.05

    # Round the tick spacing to a nice number
    unrounded_tick_spacing = ax_frac * ymax
    tick_spacing = np.round( unrounded_tick_spacing, -np.floor(np.log10(unrounded_tick_spacing)).astype(int) )

    return ymax, tick_spacing
