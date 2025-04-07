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

import matplotlib.patheffects as patheffects
import seaborn as sns

import plotly.graph_objects as go
import plotly.express as px
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
            st.write('{} not found in data'.format(data_key))
            return

        shown_df = data[data_key]
        if columns is not None:
            shown_df = shown_df[columns]

        st.write(data[data_key])

    def lineplot(
        self,
        df: pd.DataFrame,
        month_reindex: list[int] = None,
        year_reindex: list[int] = None,
        totals: pd.Series = None,
        categories: list[str] = None,
        cumulative: bool = False,
        x_label: str = None,
        y_label: str = None,
        fig_width: float = plt.rcParams['figure.figsize'][0] * 2,
        fig_height: float = plt.rcParams['figure.figsize'][1],
        yscale: str = 'linear',
        x_lim: Tuple[float, float] = None,
        y_lim: Tuple[float, float] = None,
        xtick_spacing: float = None,
        ytick_spacing: float = None,
        font_scale: float = 1.,
        linewidth: float = 2.,
        marker_size: float = 30.,
        category_colors: dict[str,str] = None,
        font: str = 'sans serif',
        seaborn_style: str = 'whitegrid',
        include_legend: bool = True,
        legend_x: float = 1.,
        legend_y: float = 1.,
        legend_ha: str = 'right',
        legend_va: str = 'lower',
        legend_scale: float = 1.,
        include_annotations: bool = False,
        annotations_ha: str = 'left',
        **kwargs
    ) -> matplotlib.figure.Figure:
        '''General-purpose matplotlib lineplot.
        This function provides solid defaults with a lot of customization.
        If you want more customization you should probably create your own
        situation-dependent function.

        Args:
            df: Dataframe to plot, formatted s.t. the x-values are the index,
                the y-values are the values in the dataframe,
                and each column is a different category to compare.
            total: Total values (across all categories) to plot, if given.
            categories: Categories to show. Defaults to all columns.
            cumulative: If True, show cumulative quantities, not instantaneous.
            x_label: Label for x axis. If not provided, not shown.
            y_label: Label for y axis. If not provided, not shown.
            fig_width: Figure width.
            fig_height: Figure height.
            yscale: Scale for axis, i.e. 'linear', 'log'.
            x_lim: x-axis limits.
            y_lim: y-axis limits.
            xtick_spacing: Distance (in data units) between x ticks.
            ytick_spacing: Distance (in data units) between y ticks.
            font_scale: Fonts are multiplied by this number (keeping relative size).
            linewidth: Line thickness.
            marker_size: Marker size.
            category_colors: Colors to use for the different categories.
                Defaults to using the seaborn color palette.
            seaborn_style: Seaborn style to use.
            include_legend: Whether to add a legend or not.
            legend_x: Legend x location (axis units).
            legend_y: Legend y location (axis units).
            legend_loc: Legend alignment.
            legend_scale: The legend size is multiplied by this number.
            include_annotations: Whether to annotate the individual lines
                with the category names.
            annotation_ha: Horizontal alignment for the annotations.

        Returns:
            fig: The figure containing the plot.
        '''
        #df.index = df.index + 1

        # Modify data if cumulative
        if cumulative:
            df = df.cumsum(axis='rows')
            if totals is not None:
                totals = totals.cumsum()

        # Set defaults
        xs = df.index

        if categories is None:
            categories = df.columns
        if category_colors is None:
            color_palette = sns.color_palette(n_colors=len(categories))
            category_colors = { key: color_palette[i] for i, key in enumerate(categories) }

        sns.set(font=font, style=seaborn_style)
        plot_context = sns.plotting_context("notebook")

        fig = plt.figure(figsize=(fig_width, fig_height))
        ax = plt.gca()

        is_empty = True
        for cols in df.columns:
            if sum(list(df[cols])) != 0:
                is_empty = False
                break
        reverse_month_dict = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May',6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}

        if not is_empty:
            if df.index.name == 'Reindexed Month':
                plt.xticks(xs, [reverse_month_dict[month_reindex[i-1]] for i in xs])
            elif df.index.name == 'Reindexed Year':
                plt.xticks(xs, year_reindex)
        for j, category_j in enumerate(categories):

            ys = df[category_j]
            
            ax.plot(
                xs,
                ys,
                linewidth = linewidth,
                alpha = 0.5,
                zorder = 2,
                color = category_colors[category_j],
            )
            ax.scatter(
                xs,
                ys,
                label = "{}".format(category_j),
                zorder = 2,
                color = category_colors[category_j],
                s = marker_size,
                )

            # Add labels
            if include_annotations:
                label_y = ys.iloc[-1]

                text = ax.annotate(
                    text = "{}".format(category_j),
                    xy = (1, label_y),
                    xycoords = matplotlib.transforms.blended_transform_factory(ax.transAxes, ax.transData),
                    xytext = (-5 + 10 * (annotations_ha == 'left'), 0),
                    va = 'center',
                    ha = annotations_ha,
                    textcoords = 'offset points',
                )
                text.set_path_effects([
                    patheffects.Stroke(linewidth=2.5, foreground='w'),
                    patheffects.Normal(),
               ])

        if totals is not None:
            ax.plot(
                xs,
                totals,
                linewidth = linewidth,
                alpha = 0.5,
                color = 'k',
                zorder = 1,
            )
            ax.scatter(
                xs,
                totals,
                label = 'Total',
                color = 'k',
                zorder = 1,
                s = marker_size,
            )

        ax.set_yscale(yscale)

        # Limits
        if x_lim is None:
            x_lim = ax.get_xlim()
        else:
            ax.set_xlim(x_lim)
        if y_lim is None:
            y_lim = ax.get_ylim()
        else:
            ax.set_ylim(y_lim)

        # Ticks
        '''
        if xtick_spacing is None:
            if df.index.name == "Reindexed Month":
                ax.set_xticks(xs.astype(str))
            else:
                ax.set_xticks(xs.astype(int))
        else:
            count_ticks = np.arange(x_lim[0], x_lim[1], xtick_spacing)
            ax.set_xticks(count_ticks)
        if ytick_spacing is not None:
            count_ticks = np.arange(y_lim[0], y_lim[1], ytick_spacing)
            ax.set_yticks(count_ticks)
        '''
        if include_legend:
            l = ax.legend(
                bbox_to_anchor = (legend_x, legend_y),
                loc = '{} {}'.format(legend_va, legend_ha),
                framealpha = 1.,
                fontsize = plot_context['legend.fontsize'] * legend_scale,
                ncol = len(categories) // 4 + 1
            )

        # Labels, inc. size
        if x_label is not None:
            ax.set_xlabel(x_label, fontsize=plot_context['axes.labelsize'] * font_scale)
        if y_label is not None:
            ax.set_ylabel(y_label, fontsize=plot_context['axes.labelsize'] * font_scale)
        ax.tick_params(labelsize=plot_context['xtick.labelsize'] * font_scale)

        # Show
        st.write(fig)

        return fig
    
    def barplot(
        self,
        df: pd.DataFrame,
        x_label: str = None,
        y_label: str = None,
        categories: list[str] = None,
        
    ):
        '''
        palette = sns.color_palette(palette='tab10', n_colors=len(df))
        color_set = []
        print(len(df))
        for i in palette:
            color_tuple = (int(i[0]*255), int(i[1]*255), int(i[2]*255))
            color_set.append("#%02x%02x%02x" % color_tuple)
        print(color_set)
        print(len(color_set))
        '''
        #print(df.index) 
        st.bar_chart(df, y='Aggregate', x_label=x_label, y_label=y_label, color="Aggregate")

    
    def testplot(
        self,
        df: pd.DataFrame,
        month_reindex: list[int] = None,
        year_reindex: list[int] = None,
        totals: pd.Series = None,
        x_label: str = None,
        y_label: str = None,
        category: str = None,
        view_mode: str=None
        ):
        fig = go.Figure()
        xs = df.index
        #print(xs)

        #print(totals)
        if totals is not None:
            #print(xs)
            #print(len(xs))
            df['totals'] = totals.to_list()
        categories = df.columns
        
        for category_j in list(categories):
            ys = df[category_j]
            #print(ys)
            fig.add_trace(go.Scatter(x=xs, y=ys, mode=view_mode, name=category_j))
        
        fig.update_layout(
            title=f'{category} by {x_label}',
            xaxis_title=x_label,
            yaxis_title= y_label,
            hovermode='closest',
            plot_bgcolor='white',
            xaxis=dict(gridcolor='lightgray'),
            yaxis=dict(gridcolor='lightgray')
        )

        st.write(fig)

        return fig.to_html(full_html=False)




    def stackplot(
        self,
        df: pd.DataFrame,
        totals: pd.Series = None,
        categories: list[str] = None,
        cumulative: bool = False,
        x_label: str = None,
        y_label: str = None,
        fig_width: float = plt.rcParams['figure.figsize'][0] * 2,
        fig_height: float = plt.rcParams['figure.figsize'][1],
        x_lim: Tuple[float, float] = None,
        y_lim: Tuple[float, float] = (0,1),
        xtick_spacing: float = None,
        ytick_spacing: float = None,
        font_scale: float = 1.,
        category_colors: dict[str,str] = None,
        font: str = 'sans serif',
        seaborn_style: str = 'whitegrid',
        include_legend: bool = True,
        legend_x: float = 1.,
        legend_y: float = 1.,
        legend_ha: str = 'right',
        legend_va: str = 'lower',
        legend_scale: float = 1.,
        include_annotations: bool = False,
        annotations_ha: str = 'left',
    ):
        '''Function to plot the relative contribution of the categories.

        Args:
            df: Dataframe to plot.
            totals: Total values to plot. Currently unused.
            categories: Categories to compare.
            cumulative: Plot the cumulative values?
            x_label: X-axis label.
            y_label: Y-axis label.
            fig_width: Figure width.
            fig_height: Figure height.
            x_lim: X-axis limits.
            y_lim: Y-axis limits.
            xtick_spacing: Spacing between x ticks in data units.
            ytick_spacing: Spacing between y ticks in data units.
            font_scale: Scale the font size by this value.
            category_colors: What colors to use for different categories?
            font: What font to use?
            seaborn_style: What seaborn style to use?
            include_legend: Include a legend?
            legend_x: Legend x location.
            legend_y: Legend y location.
            legend_ha: Legend horizontal alignment.
            legend_va: Legend vertical alignment.
            legend_scale: Scale the size of the legend by this value.
            include_annotations: Include per-category annotations?
            annotations_ha: Horizontal alignment of the annotations.

        Returns:
            fig (matplotlib.figure.Figure): The figure containing the plot.
        '''

        sns.set(font=font, style=seaborn_style)
        plot_context = sns.plotting_context("notebook")

        if cumulative:
            df = df.cumsum(axis='rows')
            if totals is not None:
                totals = totals.cumsum()

        # Set defaults
        xs = df.index
        if categories is None:
            categories = df.columns
        if category_colors is None:
            color_palette = sns.color_palette(n_colors=len(categories))
            category_colors = { key: color_palette[i] for i, key in enumerate(categories) }

        # Get data
        sum_total = df.sum(axis='columns')
        fractions = df.mul(1./sum_total, axis='rows').fillna(value=0.)
        
        fig = plt.figure(figsize=(fig_width, fig_height))
        ax = plt.gca()
        
        stack = ax.stackplot(
            xs,
            fractions.values.transpose(),
            linewidth = 0.3,
            colors = [category_colors[category_j] for category_j in categories],
            labels = categories,
        )

        # Add labels
        if include_annotations:
            for j, poly_j in enumerate(stack):

                # The y labels are centered in the middle of the last band
                vertices = poly_j.get_paths()[0].vertices
                xs = vertices[:,0]
                end_vertices = vertices[:,1][xs == xs.max()]
                label_y = 0.5 * (end_vertices.min() + end_vertices.max())

                text = ax.annotate(
                    text = fractions.columns[j],
                    xy = (1, label_y),
                    xycoords = matplotlib.transforms.blended_transform_factory(ax.transAxes, ax.transData),
                    xytext = (-5 + 10 * (annotations_ha == 'left'), 0),
                    va = 'center',
                    ha = annotations_ha,
                    textcoords = 'offset points',
                )
                text.set_path_effects([
                    patheffects.Stroke(linewidth=2.5, foreground='w'),
                    patheffects.Normal(),
               ])

        # Limits
        if x_lim is None:
            x_lim = ax.get_xlim()
        else:
            ax.set_xlim(x_lim)
        if y_lim is None:
            y_lim = ax.get_ylim()
        else:
            ax.set_ylim(y_lim)

        # Ticks
        if xtick_spacing is None:
            ax.set_xticks(xs.astype(int))
        else:
            count_ticks = np.arange(x_lim[0], x_lim[1], xtick_spacing)
            ax.set_xticks(count_ticks)
        if ytick_spacing is not None:
            count_ticks = np.arange(y_lim[0], y_lim[1], ytick_spacing)
            ax.set_yticks(count_ticks)

        if include_legend:
            l = ax.legend(
                bbox_to_anchor = (legend_x, legend_y),
                loc = '{} {}'.format(legend_va, legend_ha),
                framealpha = 1.,
                fontsize = plot_context['legend.fontsize'] * legend_scale,
                ncol = len(categories) // 4 + 1
            )

        # Labels, inc. size
        if x_label is not None:
            ax.set_xlabel(x_label, fontsize=plot_context['axes.labelsize'] * font_scale)
        if y_label is not None:
            ax.set_ylabel(y_label, fontsize=plot_context['axes.labelsize'] * font_scale)
        ax.tick_params(labelsize=plot_context['xtick.labelsize'] * font_scale)

        # Show
        st.write(fig)

        return fig
