import numpy as np
import pandas as pd
from matplotlib import cm
from matplotlib import pyplot as plt

from sep._commons.utils import *


class Plotter:
    """
    This class is responsible for plotting and managing tabular results e.g. coming from metricer.
    """

    def __init__(self, fig_size=None):
        self.figure_size = fig_size
        self.plotter_default = {}
        if self.figure_size is not None:
            self.plotter_default['figsize'] = self.figure_size

    def plot_series(self, series: pd.DataFrame, name: str, x_column, y_column, colour,
                    point_size=None, figsize=None, ax=None, kind='scatter', **plot_dict):
        plot_dict = plot_dict or {}
        add_defaults(plot_dict, self.plotter_default)
        specific_params = {}
        if point_size is not None:
            specific_params['s'] = point_size
        if figsize is not None:
            specific_params['figsize'] = figsize
        plot_dict.update(specific_params)

        ax = series.plot(kind=kind, x=x_column, y=y_column, label=name, ax=ax, color=colour,
                         grid=True, **plot_dict)
        return ax

    def plot(self, full_data: pd.DataFrame, groups_column: str, x_column, y_column,
             x_axis_label=None, as_lines=False, **plot_dict):
        plot_dict = plot_dict or {}
        defaults = {'style': '.-', 'ylabel': y_column}
        add_defaults(plot_dict, defaults)

        if as_lines:
            plot_kind = 'line'
            plot_dict = defaults
        else:
            plot_kind = 'scatter'
        cmap = cm.get_cmap('tab10')  # I like it.
        ax = None

        # Check if x_column can be float if not make it labels as plot as ordered.
        unique_xs = None
        x_axis_label = x_axis_label or x_column
        try:
            np.asanyarray(full_data[x_column], float)
        except ValueError:
            unique_xs = full_data[x_column].unique()
            enumerated_xs = [(x, i) for i, x in enumerate(unique_xs)]
            di = dict(enumerated_xs)
            plot_dict['xlabel'] = x_column

            new_x_column = 'order_' + x_column
            full_data[new_x_column] = full_data[x_column].replace(di)
            x_column = new_x_column

        groups = full_data.groupby(groups_column)

        for i, (name, group) in enumerate(groups, 1):
            ax = self.plot_series(group, name, x_column, y_column, colour=cmap([i]), ax=ax, kind=plot_kind, **plot_dict)

        # Pick sensible xtics
        if unique_xs is not None:
            ax.set_xlabel(x_axis_label)
            ax.set_xlim((0, len(unique_xs) - 1))

            ax.set_xticks(list(range(0, len(unique_xs))))
            ax.set_xticklabels(list(unique_xs))
        return ax

    def summary_box(self, full_data: pd.DataFrame, groups_column, y_column, **box_plot_params):
        ax = full_data.boxplot(by=groups_column, column=y_column, **box_plot_params)
        plt.suptitle('')
        return ax
