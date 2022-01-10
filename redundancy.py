# coding=UTF-8
import xlrd
import random
import numpy
import torch
import os
import sys
import time
import math
import pickle
import signal
import torch.utils.data as Data

neighbors = 8

def calculate_entropy(x, main_factors):
    number = len(x)
    times = [0] * main_factors
    for i in range(number):
        times[int(x[i]/100)] += 1
    
    entropy = 0
    for i in range(main_factors):
        if times[i] != 0:
            entropy += float(times[i])/number * math.log(number/times[i], 2)
    return entropy

def calculate_mutual(x, y, main_factors):
    number = len(x)
    times = [[0] * main_factors for i in range(main_factors)]
    for i in range(number):
        times[int(x[i]/100)][int(y[i]/100)] += 1
    
    mutual = 0
    for i in range(main_factors):
        for j in range(main_factors):
            if times[i][j] != 0:
                mutual += float(times[i][j])/number * math.log(number/times[i][j], 2)
    return mutual

def calculate_redundancy(x, y, mutual):
    return mutual/(x+y)

def judge(redundancy, threshold):
    number = len(redundancy)
    tmp = [[redundancy[i], i] for i in range(number)]
    adj = [0] * number
    tmp.sort(reverse=True)

    for i in range(threshold):
        adj[tmp[i][1]] = 1
    return adj

def create_adj_list(file_name, sheet_name, main_factors):
    wb = xlrd.open_workbook(file_name)
    sh = wb.sheet_by_name(sheet_name)

    data = [[0] * sh.nrows for i in range(sh.ncols)]
    adj_list = [[0] * sh.ncols for i in range(sh.ncols)]
    entropy = [0] * sh.ncols
    redundancy = [[0] * sh.ncols for i in range(sh.ncols)]

    for i in range(sh.ncols):
        for j in range(sh.nrows):
            data[i][j] = float(sh.cell(j, i).value)
    
    for i in range(sh.ncols):
        entropy[i] = calculate_entropy(data[i], main_factors)

    for i in range(sh.ncols):
        for j in range(i+1, sh.ncols):
            mutual = calculate_mutual(data[i], data[j], main_factors)
            redundancy[i][j] = calculate_redundancy(entropy[i], entropy[j], mutual)
            redundancy[j][i] = redundancy[i][j]

    for i in range(sh.ncols):
        print(redundancy[i])

    for i in range(sh.ncols):
        adj_list[i] = judge(redundancy[i], neighbors)
        adj_list[i][i] = 1

    return adj_list

def save_adj_list(adj_list, dataset_name):
    f = open(dataset_name,'wb')
    pickle.dump(adj_list,f)
    f.close()
    print('adj_list saved.')

def import_adj_list(name):
    # Import 
    f = open(name, 'rb')
    x = pickle.load(f)
    f.close()
    print('adj_list imported.')
    print(type(x))
    print(len(x))
    print(len(x[0]))

if __name__ == '__main__':
    file_name = 'data.xlsx'
    sheet_name = 'Sheet2'
    name = 'adj_list_' + str(neighbors + 1)
    adj_list = create_adj_list(file_name, sheet_name, 22)
    for i in range(len(adj_list)):
        print(adj_list[i])
    save_adj_list(adj_list, name)
    #import_adj_list(name)