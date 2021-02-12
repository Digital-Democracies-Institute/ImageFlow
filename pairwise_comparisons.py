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

import tensorflow as tf
import numpy as np
import sys
import distance
import json
import math
import multiprocessing 

class pairwise_comparisons():
    input_path = "data/phashes_full.txt"
    output_dir = "data/"
    output_path = output_dir + "phashes-diffs.json"
    identical = False
    num_threads = 1
    DISTANCE_THRESHOLD = 0
    # FLAGS = tf.app.flags.FLAGS

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
        distance_matrix = np.empty(shape=(len(phashes),len(phashes)))
        # for i, item_i in enumerate(phashes):
        while True:
            # if input_queue.empty():
            #     break
            try:
                curr_i = input_queue.get(block=False)
            except:
                break
            print(curr_i)
            # set itself to 0
            distance_matrix[curr_i,curr_i] = 0
            # now lets compare it to every other image!
            j = curr_i+1
            while j < len(phashes):
                # print(phashes[curr_i][1])
                # print(phashes[j][1])
                ham_dist = distance.hamming(phashes[curr_i][1], phashes[j][1])
                distance_matrix[curr_i,j] = ham_dist
                distance_matrix[j,curr_i] = ham_dist
                j = j + 1
            
        shared_list.append(distance_matrix)
        # return distance_matrix


    # def calculate_diff_i(self, phashes, shared_list):
    #     distance_matrix = np.empty(shape=(len(phashes),len(phashes)))
    #     for i, item_i in enumerate(phashes):
    #         # set itself to 0
    #         print(i)
    #         distance_matrix[i,i] = 0
    #         # now lets compare it to every other image!
    #         j = i+1
    #         while j < len(phashes):
    #             ham_dist = distance.hamming(item_i, phashes[j])
    #             distance_matrix[i,j] = ham_dist
    #             distance_matrix[j,i] = ham_dist
    #             j = j + 1

    #     shared_list.append(distance_matrix)

    def compare(self, phashes=None):
        if phashes == None:
            phashes = self.read_phashes_manifest()[:100000]

        # print(len(phashes))
        phash_len = len(phashes[0][1])
        str_size = math.floor(phash_len/self.num_threads)

        # manager = multiprocessing.Manager()
        # return_list = manager.list()
        # procs = []
        # for i in range(0, phash_len, str_size):
        #     if i+str_size > phash_len:
        #         str_size = len(phashes[0][i:])

        #     temp_phash = []
        #     for item in phashes:
        #         temp_phash.append(item[1][i:i+str_size])
            

        #     proc = multiprocessing.Process(target=self.calculate_diff_i, args=(temp_phash, return_list))
        #     proc.start()
        #     procs.append(proc)
        
        # for proc in procs:
        #     proc.join()

        manager = multiprocessing.Manager()
        return_list = manager.list()
        input_queue = manager.Queue()
        procs = []
        for i in range(len(phashes)):
            input_queue.put(i) 
        
        for i in range(self.num_threads):
            proc = multiprocessing.Process(target=self.calculate_diff, args=(phashes, return_list, input_queue))
            proc.start()
            procs.append(proc)
        
        for proc in procs:
            proc.join()

        print("done")

        distance_matrix = return_list[0]
        for item in return_list[1:]:
            distance_matrix = np.add(distance_matrix, item)

        # print(distance_matrix)

        # now we need to check if its below threshold! If so then lets save it into our clustering file!
        # format will be a json with key value bing the image1-image2 and the value is its distance
        final_json = {}
        for i, item_i in enumerate(distance_matrix):
            # need to check if any numbers beat the threshold
            for j, item_j in enumerate(item_i):
                if item_j <= self.DISTANCE_THRESHOLD:
                    if not phashes[i][0] == phashes[j][0]:
                        key = phashes[i][0] + "-" + phashes[j][0]
                        final_json[key] = item_j

        with open(self.output_path, 'w') as outfile:
            json.dump(final_json, outfile)
        
        return final_json




# pc = pairwise_comparisons()
# pc.compare()


