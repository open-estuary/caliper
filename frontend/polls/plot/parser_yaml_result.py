## wuyanjun w00291783
## wu.wu@hisilicon.com
## Copyright @

import os
import yaml
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pylab import *
import numpy.numarray as na
import pdb
import re

import radar_caliper as radar
import plot_utils as utils

PLOT_COLOR = ['ro-', 'yo-', 'bo-', 'go-', 'do-']

# for each subItem get the union points
def get_points_union(file_lists, subItem, category=1):
    classify = utils.get_category(category)
    fp = open(file_lists[0], 'r')
    results = yaml.load(fp)
    fp.close()
    test_results = results[utils.RESULT][classify]
    test_points = test_results[subItem].keys()
    key_test_points = [x for x in test_points if x != utils.TOTAL_SCORE]
    union_points = key_test_points

    for i in range(1, len(file_lists)):
        fp = open(file_lists[i], 'r')
        results = yaml.load(fp)
        fp.close()
        test_results = results[utils.RESULT][classify]
        test_points = test_results[subItem].keys()
        key_test_points = [x for x in test_points if x != utils.TOTAL_SCORE]
        union_points = list(set(union_points) & set(key_test_points))
    return union_points

# for each test point getting test cases
def get_cases_union(file_lists, subItem, subPoint, category=1):
    classify = utils.get_category(category)
    fp = open(file_lists[0], 'r')
    results = yaml.load(fp)
    fp.close()
    test_results = results[utils.RESULT][classify]
    test_points = test_results[subItem].keys()
    test_points = [x for x in test_points if x != utils.TOTAL_SCORE]
    test_cases = test_results[subItem][subPoint][utils.POINT_SCORE].keys()
    union_cases = test_cases

    for i in range(1, len(file_lists)):
        fp = open(file_lists[i], 'r')
        results = yaml.load(fp)
        fp.close()
        test_results = results[utils.RESULT][classify]
        test_points = test_results[subItem].keys()
        test_cases = test_results[subItem][subPoint][utils.POINT_SCORE].keys()
        union_cases = list(set(union_cases) & set(test_cases))
    return union_cases

def _get_labels(files):
    label_total = []
    for i in range(0, len(files)):
        fpi = open(files[i])
        results_i = yaml.load(fpi)
        fpi.close()
        label = results_i['name']
        label_total.append(label)
    return label_total

class DrawPicture:

    @staticmethod
    def draw_testpoint_picture( file_names, test_sub_items, folder, category = 1 ):
        """
        This function is used to draw the comparion histogram for the subItem

        :Param file_names: the input files which need to be compared
        :Param result_test: the test results in a Test Item, such as in 'performance' or 'functional'
        :Param test_sub_items: the Test Cases need to be draw, each Test Case means a picture
        :Param folder: the location will store the picture
        """
        classify = utils.get_category(category)

        for subItem in test_sub_items:
            ## get the Test Points in each Test SubItem
            key_points = get_points_union(file_names, subItem, category)

            rcParams['figure.figsize'] = 9, 6
            for point in key_points:
                ## get the keys of the Test Points, namely the Test Cases
                label = get_cases_union(file_names, subItem, point, category)
                if not label:
                    continue 
                # set the length of x axis
                x1 = na.array(range(len(label))) + 0.5
                fig, ax = plt.subplots()
                fig.set_size_inches(12, 10)
                y_max = 0

                # draw the dot line for each file, namely, draw the target's content one by one
                for i in range(0, len(file_names)):
                    file_name = file_names[i]
                    fpi = open( file_name )
                    resultsi = yaml.load(fpi)
                    fpi.close()

                    try:
                        labeli = resultsi['name']
                        test_resultsi = resultsi[utils.RESULT][classify]
                        test_data = test_resultsi[subItem][point][utils.POINT_SCORE]
                    except Exception, e:
                        print e
                        continue

                    test_values = []
                    for k in range(0, len(label)):
                        data = test_data[label[k]]
                        test_values.append( data )
                    y_value = max(test_values)
                    if (y_value > y_max):
                        y_max = y_value

                    try:
                        ax.plot(x1, test_values, PLOT_COLOR[i] , label=labeli)
                    except Exception, e:
                        print e
                        continue

                str_xlabel = 'Test Cases for ' + subItem + '_'  + point
                title_name = point + ' BarChart'
                ll = ax.legend(loc='upper right')
                leg = plt.gca().get_legend()
                ltext = leg.get_texts()
                plt.setp(ltext, fontsize='small')
                ax.set_xlabel(str_xlabel)
                ax.set_ylabel('Scores')
                ax.set_xticks(x1)
                ax.set_xticklabels(tuple(label))
                label_fig = ax.get_xticklabels()
                for label_tmp in label_fig:
                    label_tmp.set_rotation(30)
                    label_tmp.set_size('small')
                ax.set_title(title_name)
                plt.axis([0, len(label)*1.2, 0, y_max*1.05])
                plt.grid(True)
                if re.search('/', point):
                    point=point.replace('/', '_')
                point = '_'.join(point.split(" "))
                png_name = os.path.join(folder, subItem + '_' + point + '.png')
                plt.savefig( png_name)

    @staticmethod
    def draw_testCase_picture( file_names, test_subItems, folder, category=1 ):
        classify = utils.get_category(category)

        if not len(test_subItems):
            return
        label_total = _get_labels(file_names)
        color_total = ['r', 'y', 'b', 'g', 'k', 'm', 'c', 'w']

        for item in test_subItems:
            key_points = get_points_union(file_names, item, category)
            key_length = len(key_points)
            if not key_points:
                continue
            data_total = []
            y_max = 0
            rects = []
            ind = 0
            width = 0.35
            avialabel_points = []
            error_flag = 0

            fig, ax = plt.subplots()
            fig.set_size_inches(12, 9)
            # get the lists of each Test SubItems from different targets
            for i in range(0, len(file_names)):
                fpi = open(file_names[i])
                results_i = yaml.load(fpi)
                fpi.close()

                try:
                    test_resultsi = results_i[utils.RESULT][classify]
                except Exception:
                    print e
                    print "Error: %s"  % file_names[i]
                    continue

                #calculate the total score of each point in the subitem
                data = []
                for key in key_points:
                    test_key = test_resultsi[item][key]
                    data.append(test_key[utils.TOTAL_SCORE])

                    y_value = test_key[utils.TOTAL_SCORE]
                    if(y_value > y_max):
                        y_max = y_value

                if data:
                    data_total.append(data)
                else:
                    key_length = key_length - 1
                    error_falg = 1

            if error_flag == 1:
                continue
            # compute the length of the x axis
            for i in range(0, len(label_total)):
                ind = na.array(range(key_length))+0.5
                width = 0.20
                rect_item = ax.bar(ind+i*width, data_total[i], width, color=color_total[i])
                rects.append(rect_item)

            ax.set_ylabel('Scores')
            ax.set_title('Total Score of Item %s' % item )
            ax.set_xticks(ind+width*len(rects)/2)
            ax.set_xticklabels( tuple(key_points) )

            ax.legend(tuple(rects), tuple(label_total),  loc="upper right" )
            leg = plt.gca().get_legend()
            ltext = leg.get_texts()
            plt.setp(ltext, fontsize='small')
            plt.ylim(0, y_max*1.20)
            # show the value of the bar
            def autolabel(rectsi):
                for rect in rectsi:
                    height = rect.get_height()
                    ax.text(rect.get_x()+rect.get_width()/2., 1.02*height, '%.2f'%float(height),
                            ha='center', va='bottom')
            #for i in range(0, len(rects)):
                #autolabel(rects[i])
            png_name = os.path.join(folder, item + '_summary.png')
            plt.savefig( png_name )

    @staticmethod
    def draw_testSubItem_picture(file_names, test_subItems, folder, category=1 ):
        y_max = 0
        data_total = []
        label_total = []
        color_total = ['r', 'y', 'b', 'g', 'k', 'm', 'c', 'w']
        rects = []
        ind = 0
        width = 0.35
        rcParams['figure.figsize'] = 9, 6
        fig, ax = plt.subplots()
        fig.set_size_inches(12, 9)
        label_total = _get_labels(file_names)
        classify = utils.get_category(category)

        if not len(test_subItems):
            return 
        # get the lists of each Test SubItems from different targets
        for i in range(0, len(file_names)):
            fpi = open(file_names[i])
            results_i = yaml.load(fpi)
            fpi.close()

            try:
                test_resultsi = results_i[utils.RESULT][classify]
            except Exception:
                print e
                print "Error: %s"  % file_names[i]
                continue

            #calculate the total score of each subItems
            data = []

            for subitem in test_subItems:
                test_sub = test_resultsi[subitem]
                data.append(test_sub[utils.TOTAL_SCORE])

                y_value = test_sub[utils.TOTAL_SCORE]
                if(y_value > y_max):
                    y_max = y_value
            data_total.append(data)
        # compute the length of the x axis
        for i in range(0, len(label_total)):
            ind = na.array(range(len(test_subItems)))+0.5
            width = 0.20
            rect_item = ax.bar(ind+i*width, data_total[i], width, color=color_total[i])
            rects.append(rect_item)

        ax.set_ylabel('Scores')
        ax.set_title('Total Score of each Items')
        ax.set_xticks(ind+width*len(rects)/2)
        ax.set_xticklabels( tuple(test_subItems) )

        ax.legend(tuple(rects), tuple(label_total),  loc="upper left" )
        # set the fonts in the plotting
        leg = plt.gca().get_legend()
        ltext = leg.get_texts()
        plt.setp(ltext, fontsize='small')

        plt.ylim(0, y_max*1.08)
        # show the value of the bar
        def autolabel(rectsi):
            for rect in rectsi:
                height = rect.get_height()
                ax.text(rect.get_x()+rect.get_width()/2., 1.02*height, '%.2f'%float(height),
                        ha='center', va='bottom')
        #for i in range(0, len(rects)):
        #    autolabel(rects[i])
        png_name = os.path.join(folder, 'Total_Scores.png')
        plt.savefig( png_name)

def get_files_union(file_lists, category=1):
    fp = open(file_lists[0], 'r')
    results = yaml.load(fp)
    fp.close()

    classify = utils.get_category(category)

    if classify not in results[utils.RESULT]:
        return ''

    test_results = results[utils.RESULT][classify]
    test_subItems = test_results.keys()
    union_items = test_subItems

    for i in range(1, len(file_lists)):
        fp = open(file_lists[i], 'r')
        results = yaml.load(fp)
        fp.close()
        test_results = results[utils.RESULT][classify]
        test_subItems = test_results.keys()
        union_items = list(set(union_items) & set(test_subItems))
    return union_items

def draw_picture(file_lists, picture_location):
    if len(file_lists) == 0:
        return

    perf_Items = get_files_union(file_lists, utils.PERF_FLAG)
    if perf_Items:
        DrawPicture.draw_testpoint_picture(file_lists, perf_Items,
                picture_location, utils.PERF_FLAG )
        DrawPicture.draw_testCase_picture( file_lists, perf_Items,
                picture_location, utils.PERF_FLAG)
        DrawPicture.draw_testSubItem_picture( file_lists, perf_Items,
                picture_location, utils.PERF_FLAG)
        if (len(file_lists) >= 3):
            radar.draw_radar(file_lists, picture_location, utils.PERF_FLAG)

    func_Items = get_files_union(file_lists, utils.FUNC_FLAG)
    if func_Items:
        #DrawPicture.draw_testpoint_picture(file_lists, func_Items,
        #        picture_location, utils.FUNC_FLAG)
        DrawPicture.draw_testCase_picture( file_lists, func_Items,
                picture_location, utils.FUNC_FLAG)
        DrawPicture.draw_testSubItem_picture( file_lists, func_Items,
                picture_location, utils.FUNC_FLAG)
        if (len(file_lists) >= 3):
            radar.draw_radar(file_lists, picture_location, utils.FUNC_FLAG)

