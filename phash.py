# This code uses a majority of the code found at: https://github.com/zsavvas/memes_pipeline
# This is just a Refactored version with the use of object oriented design
# While refactoring, upgraded code to run with latest version of libraries and python

# libraries:
import os 
from multiprocessing import Process, Manager, Queue
import queue 
import itertools
import imagehash # used to create the hash
from PIL import Image # for openning and greyscaling the images
import copy


class phash():
    input_path = "/Users/hedayattabesh/Documents/Data/raw data/final_dataset"
    output_path = "data/phashes.txt"
    image_extensions = ['.jpg', '.png', '.jpeg', '.gif']   # case-insensitive (upper/lower doesn't matter)
    identical = False
    
    def __init__(self, input_p="", output_p=""):
        if not input_p == "": self.input_path = input_p
        if not output_p == "": self.output_path = output_p

    # takes in a path to a folder 
    # returns a list of paths to images with an extention in image_extensions
    # if no path is given uses input_path
    def get_files(self, path=""):
        if not path == "": self.input_path = path
        print(self.input_path)
        return [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.input_path) for f in filenames if os.path.splitext(f)[1].lower() in self.image_extensions]


    # This function is meanto to be used for multi-processes
    # It calculates the hash and cordinates with other processes using a Manager
    # It takes in a queue and a list derived from the Manager!
    # this function does not return anything as it is only meant to be used by calculate_phash
    def calculate_hash_func(self, in_queue, out_list):
        while True:
            # lets make sure the queue isnt empty!
            try:
                item = in_queue.get(True, 5)
            except queue.Empty: 
                break

            line_no, line = item

            # this means we are at the end of the line! so lets return!
            if line == None:
                return

            # now lets calculate the Hash!!
            try:
                if self.identical:
                    image_phash = imagehash.phash(Image.open(line))
                else:
                    # this version uses greyscale to remove colors!
                    image_phash = imagehash.phash(Image.open(line).convert('LA'))

                out_list.append([str(line), str(image_phash)])

            except Exception as e:
                print(str(e))
                pass


    # this function will calculate the phash for each image!
    # It takes in a list of images and with the power of multi-processing it computes all phashes
    # it write it all into output_path and returns True if successful
    def calculate_phash(self, image_list, num_workers=8):
        print(len(image_list))
        with Manager() as manager:
            results = manager.list()
            work = manager.Queue(num_workers)

            # start for workers    
            pool = []
            for i in range(num_workers):
                p = Process(target=self.calculate_hash_func, args=(work, results))
                p.start()
                pool.append(p)

            # create an iterator with None's at the end to stop the subprocesses
            iters = itertools.chain(image_list, (None,)*num_workers)
            for num_and_line in enumerate(iters):
                work.put(num_and_line)
            
            # lets wait for the subprocesses
            for p in pool:
                p.join()

            # lets write the results to our output_path
            final = []
            print("Done. Writing to file %d phashes" %(len(results)))
            output = open(self.output_path, 'w')
            for result in results:
                final.append(result)
                output.write(result[0] + '\t' + result[1] + '\n')
            output.close()
            return final


# if __name__ == '__main__':
#     phashes = calculate_phashes()
#     image_list = phashes.get_files()
#     phashes.calculate_phash(image_list, num_workers=1)





