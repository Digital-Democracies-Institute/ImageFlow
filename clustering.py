import json
from scipy.sparse import lil_matrix, csr_matrix
from sklearn.cluster import DBSCAN
from collections import Counter
import math



class clustering():
    input_path = "data/phashes-diffs.json"
    output_path = "data/clustering_output.txt"


    def __init__(self, input_p="", output_p=""):
        if not input_p == "": self.input_path = input_p
        if not output_p == "": self.output_path = output_p
        
        self.all_images = []
        self.phashes_dict = {}
        self.ham_dist = {}
        self.image_index = {}
        self.index_image = {}

        self.CLUSTERING_THRESHOLD = 1
        self.CLUSTERING_MIN_SAMPLES = 2

    # extracts the img1-img2 pair and returns both!
    def extract_pairs(self, pair_text, phashes_dict):
        pairs = []
        els = pair_text.split('-')
        if len(els)>2:
            for i in range(len(els)):
                pair = '-'.join(els[0:i])
                # check if we found first pair
                if pair in phashes_dict:
                    pairs.append(pair)
                    break
            pair2 = '-'.join(els[i:])
            if pair2 in phashes_dict:
                pairs.append(pair2)
        else:
            return els
        return pairs
    
    # runs based on loaded data on all_images, ham_dist, phashes_dict, image_index
    def create_distance_matrix(self):
        n = len(self.all_images)
        distance_matrix = lil_matrix((n, n))
        for pair in self.ham_dist.keys():
            image1, image2 = self.extract_pairs(pair, self.phashes_dict)
            distance = self.ham_dist[pair]
            if distance == 0:
                distance = 0.00000000000001
            index1 = self.image_index[image1]
            index2 = self.image_index[image2]
            distance_matrix[index1, index2] = distance
            distance_matrix[index2, index1] = distance
        # distance_matrix.sort_indices()
        return distance_matrix

    # loads the phashes.txt into a dictionary
    def load_phashes_file(self, file_path):
        phash_dict = {}
        with open(file_path) as f:
            for line in f:
                el = line.replace('\n','').split('\t')
                image = el[0]
                phash = el[1]
                phash_dict[image] = phash
        return phash_dict
    
    def load_phashes(self, phashes):
        phash_dict = {}
        for item in phashes:
            phash_dict[item[0]] = item[1]
        return phash_dict

    # lets print clusters to file!
    def print_clusters_to_file(self, clustering_output, distance_matrix):
        num_clusters = len(dict(Counter(clustering_output.labels_)).keys())
        clusters = clustering_output.labels_.tolist()
        output = open(self.output_path, 'w')
        
        output_json = []
        for k in range(-1, num_clusters):
            output_json_i= {}
            indices = [i for i, x in enumerate(clusters) if x == k]
            #output.write( "Cluster = %d\n" %k)
            images = []
            if k % 100 == 0:
                print("Calculating medoids. Cluster: %d/%d" %(k, num_clusters))
            
            if len(indices) > 0:
                for j in indices:
                    image = self.index_image[j]
                    images.append(image)
                output_json_i['cluster_no'] = k
                output_json_i['images'] = images
                if k!=-1:
                    medroid, medroid_path = self.find_cluster_medroid_phash(clustering_output, k, distance_matrix)
                    output_json_i['medroid_phash'] = medroid
                    output_json_i['medroid_path'] = medroid_path
                    output.write(json.dumps(output_json_i) + '\n')
                output_json.append(output_json_i)
        output.close()
        return output_json

    # finds the medroids of the clusters for documenting
    def find_cluster_medroid_phash(self, cl_output, cluster_num, distance_matrix):
        # get indices of images in cluster
        indices = [i for i, x in enumerate(list(cl_output.labels_)) if x == cluster_num]
        distances = []
        image_names = [self.index_image[i] for i in indices]
        for i in indices:
            sum_distances = 0.0
            count_distances = 0
            for j in indices:
                if i!=j:
                    dist = distance_matrix[i, j]
                    # if dist == 0.0 then it means that we dont have distance for the pair in the matrix
                    # and we set the distance to a higher value 12 in this case
                    if dist == 0.0:
                        dist = 12.0
                    sum_distances+=math.pow(dist, 2) # mean squared error
                    count_distances+=1
            try:
                mse = sum_distances/ float(count_distances)
                distances.append(mse)
            except:
                distances.append(10000)
        # find index of the image with the min average distance
        ind = distances.index(min(distances))
        ind_in_indices = indices[ind]
        # find the image name that corresponds to the index
        image_name = self.index_image[ind_in_indices]
        # find phash of the image
        phash = self.phashes_dict[image_name]
        return phash, image_name


    # main function that will run and cluster all the images based on provided information
    def cluster(self, phashes, phashes_diff=None):
        if ".txt" in phashes:
            self.phashes_dict = self.load_phashes_file(phashes)
        else:
            self.phashes_dict = self.load_phashes(phashes)
        if phashes_diff == None:
            self.ham_dist = json.load(open(self.input_path, 'r'))
        else:
            self.ham_dist = phashes_diff

        # find all pairs and all images from the dict
        all_pairs = self.ham_dist.keys()

        
        for pair in all_pairs:
            self.all_images.extend(self.extract_pairs(pair, self.phashes_dict))

        self.all_images = set(self.all_images)

        print("Number of images that will be clustered is " + str(len(self.all_images)))

        # create a dict that will provide us with the mapping between the image and the
        # index on distance matrix
        for count, image in enumerate(self.all_images):
            self.image_index[image] = count
            self.index_image[count] = image
        
        # create a distance matrix for the images (use sparse matrix instead of dense
        # to avoid memory issues)
        distance_matrix = self.create_distance_matrix()
        
        # print(distance_matrix)
        clustering = DBSCAN(eps=self.CLUSTERING_THRESHOLD, metric='precomputed', n_jobs=8, min_samples=self.CLUSTERING_MIN_SAMPLES).fit(distance_matrix)
        num_clusters = len(dict(Counter(clustering.labels_)).keys())
        print("Number of clusters  = %d " %(num_clusters-1))

        print("Calculating cluster medoids...")
        output_json = self.print_clusters_to_file(clustering, distance_matrix)
        print("Clustering output written to %s" %(self.output_path))
        return output_json








# clust = clustering()
# clust.cluster("data/phashes.txt")

        
