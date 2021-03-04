import json




input_path_o = "data/clustering_output_full_o.txt"
input_path_n = "data/clustering_output_full_n.txt"


cluster_json_o = []
with open(input_path_o, 'r') as f:
    for line in f:
        cluster_json_o.append(json.loads(line))

cluster_json_n = []
with open(input_path_n, 'r') as f:
    for line in f:
        cluster_json_n.append(json.loads(line))

## lets see if the new clusters exists in the old one, if not lets save it for reporting
not_found_n = []
for clus_n in cluster_json_n:
    found = False
    for clus_o in cluster_json_o:
        if all(item in clus_n["images"] for item in clus_o["images"]):
            found = True
            break
    if not found:
        not_found_n.append(clus_n)

print(len(not_found_n))

