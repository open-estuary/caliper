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


PLOT_COLOR = ['ro-', 'yo-', 'bo-', 'go-', 'do-']

# for each subItem get the union points
def get_points_union(file_lists, subItem):
    fp = open(file_lists[0], 'r')
    results = yaml.load(fp)
    fp.close()
    test_results = results['results']['Performance']
    test_points = test_results[subItem].keys()
    key_test_points = [x for x in test_points if x != 'Total_Scores']
    union_points = key_test_points

    for i in range(1, len(file_lists)):
        fp = open(file_lists[i], 'r')
        results = yaml.load(fp)
        fp.close()
        test_results = results['results']['Performance']
        test_points = test_results[subItem].keys()
        key_test_points = [x for x in test_points if x != 'Total_Scores']
        union_points = list(set(union_points) & set(key_test_points))
    return union_points

# for each test point getting test cases
def get_cases_union(file_lists, subItem, subPoint):
    fp = open(file_lists[0], 'r')
    results = yaml.load(fp)
    fp.close()
    test_results = results['results']['Performance']
    test_points = test_results[subItem].keys()
    test_points = [x for x in test_points if x != 'Total_Scores']
    test_cases = test_results[subItem][subPoint]['Point_Scores'].keys()
    union_cases = test_cases

    for i in range(1, len(file_lists)):
        fp = open(file_lists[i], 'r')
        results = yaml.load(fp)
        fp.close()
        test_results = results['results']['Performance']
        test_points = test_results[subItem].keys()
        test_cases = test_results[subItem][subPoint]['Point_Scores'].keys()
        union_cases = list(set(union_cases) & set(test_cases))
    return union_cases

class DrawPicture:

    @staticmethod
    def draw_testpoint_picture( file_names, test_sub_items, folder ):
        """
        This function is used to draw the comparion histogram for the subItem

        :Param file_names: the input files which need to be compared
        :Param result_test: the test results in a Test Item, such as in 'performance' or 'functional'
        :Param test_sub_items: the Test Cases need to be draw, each Test Case means a picture
        :Param folder: the location will store the picture
        """
        for subItem in test_sub_items:
            ## get the Test Points in each Test SubItem
            key_points = get_points_union(file_names, subItem)
            
            rcParams['figure.figsize'] = 9, 6
            for point in key_points:
                ## get the keys of the Test Points, namely the Test Cases
                label = get_cases_union(file_names, subItem, point)
                if not label:
                    return 
                # set the length of x axis
                x1 = na.array(range(len(label))) + 0.5
                fig, ax = plt.subplots()
                y_max = 0

                # draw the dot line for each file, namely, draw the target's content one by one
                for i in range(0, len(file_names)):
                    file_name = file_names[i]
                    fpi = open( file_name )
                    resultsi = yaml.load(fpi)
                    fpi.close()

                    try:
                        labeli = resultsi['name']
                        test_resultsi = resultsi['results']['Performance']
                        test_data = test_resultsi[subItem][point]['Point_Scores']
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
                png_name = os.path.join(folder,subItem + '_' + point + '.png')
                plt.savefig( png_name, dit=150 )

    @staticmethod
    def draw_testSubItem_picture( file_names, test_subItems, folder ):
        items_Scores = []
        y_max = 0
        data_total = []
        label_total = []
        color_total = ['r', 'y', 'b', 'g', 'k', 'm', 'c', 'w']
        rects = []
        ind = 0
        width = 0.35
        rcParams['figure.figsize'] = 9, 6
        fig, ax = plt.subplots()   
        
        if not len(test_subItems):
            return 
        # get the lists of each Test SubItems from different targets
        for i in range(0, len(file_names)):
            fpi = open(file_names[i])
            results_i = yaml.load(fpi)
            fpi.close()
           
            try:
                label = results_i['name']
                label_total.append(label)
                test_resultsi = results_i['results']['Performance']
            except Exception:
                print e
                print "Error: %s"  % file_names[i]
                continue

            #calculate the total score of each subItems
            data = []

            for subitem in test_subItems:
                test_sub = test_resultsi[subitem]
                data.append(test_sub['Total_Scores'])
       
                y_value = test_sub['Total_Scores']
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
        leg = plt.gca().get_legend()
        ltext = leg.get_texts()
        plt.setp(ltext, fontsize='small')

        plt.ylim(0, y_max*1.08)
        # set the label for the labelling
        def autolabel(rectsi):
            for rect in rectsi:
                height = rect.get_height()
                ax.text(rect.get_x()+rect.get_width()/2., 1.02*height, '%.2f'%float(height),
                        ha='center', va='bottom')
        for i in range(0, len(rects)):
            autolabel(rects[i])
        png_name = os.path.join(folder, 'Total_Scores.png')
        plt.savefig( png_name, dit=512 )

def get_files_union(file_lists):
    fp = open(file_lists[0], 'r')
    results = yaml.load(fp)
    fp.close()
    test_results = results['results']['Performance']
    test_subItems = test_results.keys()
    union_items = test_subItems

    for i in range(1, len(file_lists)):
        fp = open(file_lists[i], 'r')
        results = yaml.load(fp)
        fp.close()
        test_results = results['results']['Performance']
        test_subItems = test_results.keys()
        union_items = list(set(union_items) & set(test_subItems))
    return union_items

def draw_picture(file_lists, picture_location):
    if len(file_lists) == 0:
        return

    union_Items = get_files_union(file_lists)
    DrawPicture.draw_testpoint_picture(file_lists, union_Items, picture_location )
    DrawPicture.draw_testSubItem_picture( file_lists, union_Items, picture_location )
    if (len(file_lists) >= 3):
        radar.draw_radar(file_lists, picture_location)

#
#if __name__ == "__main__":
#    file_lists = ['D01_16_result.yaml', 'D01_1_result.yaml', 'Server_result.yaml',
#                    'TV_result.yaml']
#    picture_location = "/home/wuyanjun/caliper/gen/output/html"
#    try:
#        draw_picture(file_lists, picture_location)
#    except Exception, e:
#        raise e
# 
