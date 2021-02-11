# This code uses a majority of the code found at: https://github.com/zsavvas/memes_pipeline
# This is just a Refactored version with the use of object oriented design
# While refactoring, upgraded code to run with latest version of libraries and python

import os

import sys
sys.path.append('../../')
from phash import phash
<<<<<<< HEAD
from pairwise_comparisons import pairwise_comparisons
from clustering import clustering
from visualize import visualize

import time

class image_flow():
    output_path = "/data"
    input_path = "/Users/hedayattabesh/Documents/Data/raw data/final_dataset/"
    identical = False
    num_workers = 4
    
    def __init__(self, input_p="", output_p=""):
        if not input_p == "": self.input_path = input_p
        if not output_p == "": self.output_path = output_p
        self.phashes = phash(input_p=self.input_path)
        self.pc = pairwise_comparisons()
        self.clus = clustering()
        self.viz = visualize(self.input_path)


    # step #1: calculate_phashes.py
    def calculate_phashes(self):
        # lets get a list of images first!
        image_list = self.phashes.get_files()
        # now lets calculate there phash!
        return self.phashes.calculate_phash(image_list, num_workers=self.num_workers)

    # step #2: pairwise_comparisons.py
    def calculate_pairwise_comparisons(self, phashes=None):
        return self.pc.compare(phashes)

    # step #3: clustering_phashes.py
    def calculate_clusters(self, phashes, phashes_diff):
        return self.clus.cluster(phashes, phashes_diff)

    # step #4: python visualize_clusters_dup.py
    def visualize_folders(self, clusters=None):
        self.viz.load_clusters_to_folder(clusters)
        return
    

if __name__ == '__main__':
    start = time.time()
    imfl = image_flow()
    # print("Calculating Phashes")
    # phashes = imfl.calculate_phashes()
    print("Calculating phashes_diff")
    phashes_diff = imfl.calculate_pairwise_comparisons()
    # print("Calculating clusters")
    # clusters = imfl.calculate_clusters(phashes, phashes_diff)

    end = time.time()
    elapsed_time = end - start
    print("Elapsed time = " + str(elapsed_time))

    # imfl.visualize_folders()

