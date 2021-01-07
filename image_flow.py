import os

import sys
sys.path.append('../../')
from phash import phash

class image_flow():
    output_path = "/data"
    input_path = "/Users/hedayattabesh/Documents/Data/raw data/final_dataset/facebook"
    identical = False
    num_workers = 8
    
    def __init__(self, input_p="", output_p=""):
        if not input_p == "": input_path = input_p
        if not output_p == "": input_path = output_p
        self.phashes = phash(input_p=self.input_path)    

    # step #1: calculate_phashes.py
    def calculate_phashes(self):
        # lets get a list of images first!
        image_list = self.phashes.get_files()
        # now lets calculate there phash!
        self.phashes.calculate_phash(image_list, num_workers=self.num_workers)

    # step #2: pairwise_comparisons.py

    # step #3: clustering_phashes.py

    # step #4: python visualize_clusters_dup.py 


if __name__ == '__main__':
    imfl = image_flow()
    imfl.calculate_phashes()
