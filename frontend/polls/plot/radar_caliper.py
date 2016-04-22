#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   wuyanjun 00291783
#   E-mail  :   wu.wu@hisilicon.com
#   Date    :   15/01/23 18:38:11
#   Desc    :
#
import matplotlib
matplotlib.use("Agg")

import sys
import os
import string
import yaml
import numpy as np
import logging
import matplotlib.pyplot as plt

from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection

import plot_utils as utils

LOCATION = os.path.dirname(sys.modules[__name__].__file__)
caliper_dir = os.path.join(LOCATION, '..', '..', '..', '..')
yaml_dir = os.path.join(caliper_dir, 'gen', 'output', 'yaml')


def radar_factory(num_vars, frame='circle'):
    """
    Create a radar chart with 'num_vars' axes.

    This function creates a RadarAxes projection and registers it.
    Parameters:
    num_vars: int   Number of variables for radar chart
    frame: {'circle' | 'polygon'}  Shape of frame surrounding axes.
    """
    # calculate evenly-spaced axis angles
    # nu, py.linespace(start, stop, num=50, endpoint=True,
    #                  retstep=Falise, dtype=None)
    theta = 2 * np.pi * np.linspace(0, 1-1./num_vars, num_vars)

    # rotate theta such that the first axis is at the top
    theta += np.pi/2

    def draw_circle_patch(self):
        # unit circle centered on (0.5, 0.5)
        return plt.Circle((0.5, 0.5), 0.5)

    def draw_poly_patch(self):
        verts = unit_poly_verts(theta)
        return plt.Polygon(verts, closed=True, edgecolor='K')

    patch_dict = {'polygon': draw_poly_patch, 'circle': draw_circle_patch}
    if frame not in patch_dict:
        raise ValueError('unknown value for `frame`: %s' % frame)

    class RadarAxes(PolarAxes):
        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1
        # define draw_frame method
        draw_patch = patch_dict[frame]

        def fill(self, *args, **kwargs):
            """Override fill so that lines is closed by default"""
            closed = kwargs.pop('closed', True)
            return super(RadarAxes, self).fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super(RadarAxes, self).plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(theta * 180/np.pi, labels)

        def _gen_axes_patch(self):
            return self.draw_patch()

        def _gen_axes_spines(self):
            if frame == 'circle':
                return PolarAxes._gen_axes_spines(self)
            # The following is a hack to get the spines (i.e. the axes frame)
            # to draw correctly for a polygon frame

            # spine_type must be 'left', 'right', 'top', 'bottom', or 'circle'
            spine_type = 'circle'
            verts = unit_poly_verts(theta)
            # close off polygon by repeating first vertex
            verts.append(verts[0])
            path = Path(verts)

            spine = Spine(self, spine_type, path)
            spine.set_transform(self.transAxes)
            return {'polar': spine}
    register_projection(RadarAxes)
    return theta


def unit_poly_verts(theta):
    """
    Return vertices of polygon for a subplot axes.
    This polygon is circumscribed by a unit circle centered at (0.5, 0.5)
    """
    x0, y0, r = [0.5] * 3
    verts = [(r*np.cos(t) + x0, r*np.sin(t) + y0) for t in theta]
    return verts


def get_Items_score(files_list, category):
    targets_scores = []

    full_path = yaml_dir
    full_path_i = os.path.join(full_path, files_list[0])
    fp = open(files_list[0], 'r')
    results = yaml.load(fp)
    fp.close()
    test_results = results[utils.RESULT][category]
    test_subItems = test_results.keys()
    union_items = test_subItems

    for j in range(1, len(files_list)):
        fp = open(files_list[j], 'r')
        results = yaml.load(fp)
        fp.close()
        test_results = results[utils.RESULT][category]
        test_subItems = test_results.keys()
        union_items = list(set(union_items) & set(test_subItems))

    for i in range(0, len(files_list)):
        full_path = yaml_dir
        full_path_i = os.path.join(full_path, files_list[i])
        fp = open(full_path_i, 'r')
        result = yaml.load(fp)
        fp.close()
        subItems = result[utils.RESULT][category]
        scores_for_target = []
        for key in union_items:
            score = subItems[key][utils.TOTAL_SCORE]
            scores_for_target.append(string.atof(score))
        targets_scores.append(scores_for_target)
    return (union_items, targets_scores)


# get the apppropriate scale for each dimension for the spider diagram
def get_rgrids(data_lists):
    if len(data_lists) < 1:
        return []

    trans_data = [[d[col] for d in data_lists] for col in
                    range(len(data_lists[0]))]

    rgrid_lists = []
    for i in range(0, len(trans_data)):
        tmp_max = max(trans_data[i])
        delta = tmp_max / len(trans_data)
        tmp_rgrids = []
        for j in range(0, len(trans_data)):
            tmp_rgrids.append(str("%.2f" % (delta + j * delta)))
        rgrid_lists.append(tmp_rgrids)
    return rgrid_lists


def deal_data(data_lists):
    #   function: make the data in each dimension almostly near
    # the data_lists is planar
    max_of_matrix = data_lists[0][0]
    max_of_columns = []
    # i means the columns
    for i in range(0, len(data_lists[0])):
        tmp_max_column = data_lists[0][i]
        # j means the rows
        for j in range(0, len(data_lists)):
            if data_lists[j][i] > max_of_matrix:
                max_of_matrix = data_lists[j][i]
            if data_lists[j][i] > tmp_max_column:
                tmp_max_column = data_lists[j][i]
        max_of_columns.append(tmp_max_column)

    divisor_of_columns = [max_of_matrix/data for data in max_of_columns]
    for i in range(0, len(data_lists[0])):
        for j in range(0, len(data_lists)):
            data_lists[j][i] = data_lists[j][i] * divisor_of_columns[i]
    return data_lists


def draw_radar(file_lists, store_folder, kind=1):
    category = utils.get_category(kind)
    (spoke_labels, data_lists) = get_Items_score(file_lists, category)
    dimension = len(spoke_labels)
    if (dimension < 3):
        #SKD++ spelling corrected for comparison
        logging.info("The comparison dimension is less than 3")
        return 1
    theta = radar_factory(dimension, frame='circle')
    labels = [file_list.split('/')[-1].split('_')[0]
                 for file_list in file_lists]
    
    #skd++ commented and updated the colors to handle more than 7 platforms
    #colors = ['b', 'r', 'g', 'm', 'y', 'c', 'k']
    colors = ['#40ff00','#ff0000', 'y', 'b', 'g', 'k', 'm', 'c', 'w']

    if len(file_lists) < len(colors):
        colors = colors[0:len(file_lists)]
    title = 'Radar / Spider Diagram'

    fig = plt.figure(figsize=(9, 9))
    fig.set_size_inches(13.0, 13.0)
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)
    ax = fig.add_subplot(1, 1, 1, projection='radar')
    # get the approriate scale for the picture
    rgrid_list = get_rgrids(data_lists)

    ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.1),
                horizontalalignment='center', verticalalignment='center')
    # angles_list = [ th*180/np.pi for th in theta ]
    # angles = np.array(angles_list)
    # length = len(rgrid_list)
    data = deal_data(data_lists)

    for d, color in zip(data, colors):
        ax.plot(theta, d, color=color)
        ax.fill(theta, d, facecolor=color, alpha=0.25)

    # FIXME: why can this work?
    # for angle, rgrid_data in zip(angles, rgrid_list):
    #    ax.set_rgrids(range(1, 1+length), angle=angle, labels=rgrid_data)
    ax.set_varlabels(spoke_labels)

    # the usage of subplot is plt.subplot(x, y, m)   m<=x*y
    plt.subplot(1, 1, 1)
    legend = plt.legend(labels, loc=(0.9, 0.95), labelspacing=0.1)

    plt.setp(legend.get_texts(), fontsize='small')
    
    #skd++ commented
    #plt.figtext(0.5, 0.965, 'Drawing Radar Diagram for Caliper',
    #            ha='center', color='black', weight='bold', size='large')
    
    #skd++ added
    plt.figtext(0.5, 0.965, ' ',
                ha='center', color='black', weight='bold', size='large')

    path_name = os.path.join(store_folder, '_'.join([category,
                        "Total_Scores.png"]))

    #skd++ commented and updated to handle legend position plt.savefig(path_name, dit=512)
    plt.savefig(path_name, dit=512, bbox_extra_artists=(legend,), bbox_inches='tight')
    return 0

# if __name__ == "__main__":
#     file_lists = ['D01_16_result.yaml', 'D01_1_result.yaml',
#                     'Server_result.yaml',
#                     'TV_result.yaml']
#     picture_location = "/home/wuyanjun/caliper/gen/output/html"
#     try:
#         draw_radar(file_lists, picture_location)
#     except Exception, e:
#         raise e
