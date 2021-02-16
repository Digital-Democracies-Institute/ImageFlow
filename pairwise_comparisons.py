# This code uses a majority of the code found at: https://github.com/zsavvas/memes_pipeline
# The code was created as part ofxw "On the Origins of Memes by Means of Fringe Web Communities" at IMC 2018.
# This is just a Refactored version with the use of object oriented design
# While refactoring, upgraded code to run with latest version of libraries and python

# libraries:
import os
import json
import time
import threading
import pickle

import numpy as np
import sys
import distance
import json
import math
import multiprocessing 

from scipy.sparse import csr_matrix

class pairwise_comparisons():
    input_path = "data/phashes_full.txt"
    output_dir = "data/"
    output_path = output_dir + "phashes-diffs.json"
    identical = False
    num_avail_proc = 6
    DISTANCE_THRESHOLD = 0

    def __init__(self, input_p="", output_p=""):
        pass

    ### for pre computation ###
    def read_phashes_manifest(self):
        phashes = []
        with open(self.input_path) as infile:
            for line in infile.readlines():
                split = line.split('	')
                hashid = split[0].strip()
                hash_str = split[1].strip()
                phashes.append([hashid, hash_str])
        print('[i] processed', len(phashes))
        return phashes
    
    def calculate_diff(self, phashes, shared_list, input_queue):
        # distance_matrix = csr_matrix((len(phashes),len(phashes)), dtype=np.int)
        # for i, item_i in enumerate(phashes):
        output = {}
        while True:
            try:
                curr_i = input_queue.get(block=False)
            except:
                break
            print(curr_i)
            # now lets compare it to every other image!
            j = curr_i+1
            while j < len(phashes):
                # print(phashes[curr_i][1])
                # print(phashes[j][1])
                ham_dist = distance.hamming(phashes[curr_i][1], phashes[j][1])
                if ham_dist <= self.DISTANCE_THRESHOLD:
                # distance_matrix[curr_i,j] = ham_dist
                # distance_matrix[j,curr_i] = ham_dist
                    key = phashes[curr_i][0] + "-" + phashes[j][0]
                    output[key] = ham_dist
                j = j + 1
            
        # shared_list.append(distance_matrix)
        shared_list.append(output)
        # return distance_matrix
    
    def calculate_diff_test(self, shared_list, input_queue):
        output = {}
        while True:
            try:
                curr_i = input_queue.get()
            except:
                break
            print(input_queue.qsize())
            ham_dist = distance.hamming(curr_i[1][0], curr_i[1][1])
            if ham_dist <= self.DISTANCE_THRESHOLD:
                output[curr_i[0]] = ham_dist
            
        # shared_list.append(distance_matrix)
        shared_list.append(output)
        # return distance_matrix


    def fill_queue(self, input_queue, phashes, proc_i):
        tot_len = int(len(phashes)/self.num_avail_proc)
        start = int(proc_i*tot_len)
        last = int(((proc_i+1)*tot_len))
        if proc_i+1 == self.num_avail_proc:
            last = int(len(phashes))

        for i in range(start ,last):
            print("starting to insert the " +str(i))
            j = i+1
            while j < len(phashes):
                input_queue.put([phashes[i][0] + "-" + phashes[j][0], [phashes[i][1], phashes[j][1]]])
                j = j + 1

    def compare(self, phashes=None):
        if phashes == None:
            phashes = self.read_phashes_manifest()[:10000]

        manager = multiprocessing.Manager()
        return_list = manager.list()
        input_queue = manager.Queue()
        
        for i in range(len(phashes)):
            input_queue.put(i)
        

        # lets prep queue
        # procs = []
        # for i in range(self.num_avail_proc):
        #     proc = multiprocessing.Process(target=self.fill_queue, args=(input_queue, phashes, i))
        #     proc.start()
        #     procs.append(proc)
        
        # for proc in procs:
        #     proc.join()

        procs = []
        for i in range(self.num_avail_proc):
            proc = multiprocessing.Process(target=self.calculate_diff, args=(phashes, return_list, input_queue))
            proc.start()
            procs.append(proc)
        
        for proc in procs:
            proc.join()

        print("done")

        final_json = return_list[0]
        for item in return_list[1:]:
            final_json.update(item)

        with open(self.output_path, 'w') as outfile:
            json.dump(final_json, outfile)
        
        return final_json




# pc = pairwise_comparisons()
# pc.compare()


