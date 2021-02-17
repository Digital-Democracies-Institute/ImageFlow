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
                ham_dist = distance.hamming(phashes[curr_i][1], phashes[j][1])
                if ham_dist <= self.DISTANCE_THRESHOLD:
                    key = phashes[curr_i][0] + "-" + phashes[j][0]
                    output[key] = ham_dist
                j = j + 1
            
        shared_list.append(output)

    def compare(self, phashes=None):
        if phashes == None:
            phashes = self.read_phashes_manifest()[:10000]

        manager = multiprocessing.Manager()
        return_list = manager.list()
        input_queue = manager.Queue()
        
        for i in range(len(phashes)):
            input_queue.put(i)

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


