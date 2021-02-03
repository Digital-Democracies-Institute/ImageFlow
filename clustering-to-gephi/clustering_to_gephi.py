import pandas as pd
import json
import os
import numpy as np

#global variable for multi-platform filter
filter = 'no'

# Borrowed method to parse absolute and relative paths
def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


def convert_to_df(file_path):
    print("Converting to CSV")
    print(file_path)
    output = []

    with open(file_path, 'r') as f:
        for line in f:
            output_json = json.loads(line)
            images_in_cluster = output_json['images']
            cluster = output_json['cluster_no']

            for i in images_in_cluster:
                #TODO: This will need to be adjusted when used in ComputeCanada
                socialmedia = splitall(i)
                socialmedia = socialmedia[5]
                filename = splitall(i)
                filename = filename[-1]
                z = {"cluster": cluster, "FileName": filename, "images": i, "socialmedia": socialmedia}

                output.append(z)

    pd_dataframe = pd.DataFrame(output)
    pd_dataframe = pd_dataframe.drop_duplicates(subset='images')
    pd_dataframe.to_csv("clustering.csv")
    return(pd_dataframe)

def multiplatform_filter(dataframe):
    print("Filtering out any cluster that does not cross platforms...")

    df2 = dataframe.drop_duplicates(["cluster", "socialmedia"])
    df = df2.groupby('cluster')['socialmedia'].agg(size= len, set= lambda x: set(x))
    single_platforms = df[df['size'] == 1]
    multi_platforms = df[df['size'] > 1]

    single_platforms = pd.DataFrame(single_platforms)
    multi_platforms = pd.DataFrame(multi_platforms)
    single_cluster_list = single_platforms.index.values.tolist()
    output_single = []

    print("Scanning files...")

    output_single.append(dataframe.loc[dataframe['cluster'].isin(single_cluster_list)])
    single_df = pd.DataFrame(np.concatenate(output_single))
    single_df= single_df.rename(columns={0:"cluster", 1:"FileName", 2:"images", 3:"socialmedia", 4:"URL", 5:"SocialMedia", 6:"BoardName", 7:"group", 8:"hashtags", 9:"UserName", 10:"TimeStamp", 11:"date", 12:"time"})
    single_df.to_csv("single_platforms.csv", index=False)

    multi_cluster_list = multi_platforms.index.values.tolist()
    output_multi = []
    output_multi.append(dataframe.loc[dataframe['cluster'].isin(multi_cluster_list)])
    multi_df = pd.DataFrame(np.concatenate(output_multi))
    multi_df = multi_df.rename(
        columns={0: "cluster", 1: "FileName", 2: "images", 3: "socialmedia", 4: "URL", 5: "SocialMedia", 6: "BoardName",
                 7: "group", 8: "hashtags", 9: "UserName", 10: "TimeStamp", 11: "date", 12: "time"})

    multi_df.to_csv("multi_platforms.csv", index=False)

    return multi_df

def metadata_merge(df, merge_file):
    df_merge = pd.read_csv(merge_file)
    print("Merging files...")
    output = pd.merge(df, df_merge, on='FileName', how='left')
    print("Merging at the filename...")
    output = output[output['socialmedia'].notna()]
    output = output.drop_duplicates(subset='images')
    output.to_csv("merge.csv")
    print(output)
    return output

def date_check(df):
    df2 = df['date'].isnull().values.sum()
    print("Checking if there are any invalid or missing dates...")
    print("There are " + str(df2) + " files missing dates.")

def remove_clusters(df):
    cluster_list = input("Enter the cluster numbers that you would like to remove: ")
    try:
        cluster_list = []
        while True:
            cluster_list.append(int(input()))
    except:
        print(cluster_list)

    for i in cluster_list:
        df.drop(df[df['cluster'] == i].index, inplace=True)

    return df


def main():
    # file_path = input("Let's get started. Add the filepath of your clustering_output.txt here:")
    # alternative to manually add file_path here and not use UI
    file_path = "clustering_output_identicals.txt"
    pd_dataframe = convert_to_df(file_path)
    print(pd_dataframe)

    merge = input("Would you like to merge your data with a csv of corresponding metadata? (Yes/No)")
    if merge == 'Yes':
        #merge_file = input("What is the filepath to the metadata csv file?")
        merge_file = '/Volumes/Elsa_HD2/Memes/data/All-Metadata/all_metadata.csv'
        pd_dataframe = metadata_merge(pd_dataframe, merge_file)

    filter = input("Would you like to filter out for only multi-platform clusters? (Yes/No) ")
    if filter == 'Yes':
        pd_dataframe = multiplatform_filter(pd_dataframe)

    rm_clusters = input("Would you like to remove specific cluster(s) from the data? (Yes/No) ")
    if rm_clusters == 'Yes':
        pd_dataframe = remove_clusters(pd_dataframe)

    date_check(pd_dataframe)



if __name__ == "__main__":
    main()