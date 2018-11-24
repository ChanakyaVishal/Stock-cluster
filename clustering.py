import numpy as np
import random
import glob
import pandas as pd


def euclidean_dist(t1, t2):
    dist = 0
    for j in range(len(t1)):
        dist = dist + (t1[j] - t2[j]) ** 2
    return dist


def lb_keogh(s1, s2, r):
    lb_sum = 0
    for ind, i in enumerate(s1):

        lower_bound = np.amin(s2[(ind - r if ind - r >= 0 else 0):(ind + r)], axis=0)
        upper_bound = np.amax(s2[(ind - r if ind - r >= 0 else 0):(ind + r)], axis=0)

        for j in range(len(i)):
            if i[j] > upper_bound[j]:
                lb_sum = lb_sum + (i[j] - upper_bound[j]) ** 2
            elif i[j] < lower_bound[j]:
                lb_sum = lb_sum + (i[j] - lower_bound[j]) ** 2

    return np.sqrt(lb_sum)


def dtw_distance(s1, s2, w=None):
    """
    Calculates dynamic time warping Euclidean distance between two
    sequences. Option to enforce locality constraint for window w.
    """
    dtw = {}
    if w:
        w = max(w, abs(len(s1) - len(s2)))

        for i in range(-1, len(s1)):
            for j in range(-1, len(s2)):
                dtw[(i, j)] = float('inf')

    else:
        for i in range(len(s1)):
            dtw[(i, -1)] = float('inf')
        for i in range(len(s2)):
            dtw[(-1, i)] = float('inf')

    dtw[(-1, -1)] = 0

    for i in range(len(s1)):
        if w:
            for j in range(max(0, i - w), min(len(s2), i + w)):
                dist = euclidean_dist(s1[i], s2[j])
                dtw[(i, j)] = dist + min(dtw[(i - 1, j)], dtw[(i, j - 1)], dtw[(i - 1, j - 1)])
        else:
            for j in range(len(s2)):
                dist = euclidean_dist(s1[i], s2[j])
                dtw[(i, j)] = dist + min(dtw[(i - 1, j)], dtw[(i, j - 1)], dtw[(i - 1, j - 1)])

    return np.sqrt(dtw[len(s1) - 1, len(s2) - 1])


class Tscluster:
    def __init__(self, num_cluster):
        """
        num_cluster is the number of clusters for the k-means algorithm
        assignments holds the assignments of data points (indices) to clusters
        centroids holds the centroids of the clusters
        """
        self.num_cluster = num_cluster
        self.assignments = {}
        self.centroids = []

    def k_means_cluster(self, data, num_iter, w, progress=False):
        """
        k-means clustering algorithm for time series data.  dynamic time warping Euclidean distance
        used as default similarity measure.
        """
        self.centroids = random.sample(list(data.values()), self.num_cluster)

        for n in range(num_iter):
            if progress:
                print('Iteration : ' + str(n+1))

            for c, j in enumerate(self.centroids):
                print("cluster " + str(j) + ":")
                print(c)

            # assign data points to clusters
            self.assignments = {}
            for t, i in data.items():
                min_dist = float('inf')
                closest_cluster = None
                print("Stock: " + t)
                for c_ind, j in enumerate(self.centroids):
                    if lb_keogh(i, j, 5) < min_dist:
                        cur_dist = dtw_distance(i, j, w)
                        if cur_dist < min_dist:
                            min_dist = cur_dist
                            closest_cluster = c_ind

                if closest_cluster not in self.assignments:
                    self.assignments[closest_cluster] = []

                self.assignments[closest_cluster].append(t)

                print(self.assignments)

            # recalculate the centroids of clusters
            for key in self.assignments:
                print(key)
                cluster_sum = np.zeros(data[self.assignments[key][0]].shape)
                for k in self.assignments[key]:
                    cluster_sum = cluster_sum + data[k]
                self.centroids[key] = cluster_sum / len(self.assignments[key])


files = glob.glob('./preprocessed_stocks/*')
stock_data = {}
count = 0

for i, f in enumerate(files):
    # read data for each stock
    t_data = pd.read_csv(f)

    # extract data from columns
    oc = np.reshape(np.asarray(t_data['o/c'].tolist()), (-1, 1))
    volume = np.reshape(np.asarray(t_data['volume'].tolist()), (-1, 1))
    high = np.reshape(np.asarray(t_data['high'].tolist()), (-1, 1))
    low = np.reshape(np.asarray(t_data['low'].tolist()), (-1, 1))

    # get stock ticker name and create 2D numpy array for values
    ticker = t_data['name'].tolist()[0]
    ts_data = np.hstack((oc, volume, high, low))

    # handle missing data by ignoring
    if ts_data.shape[0] == 1259:
        stock_data[ticker] = ts_data

cluster = Tscluster(5)
cluster.k_means_cluster(stock_data, 10, 2, progress=True)