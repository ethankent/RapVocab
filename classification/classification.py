#!/usr/bin/env python3
'''
Created on Mar 23, 2017
@author: arno

Classify the different rappers and their songs based on TF.IDF score
of the entire voabulary set of a rapper or of the lyrics of a song.

The module produces the following:
    - For all songs, find the top N most similar ones (writes results in songSimilarities.txt)
    - For each rappers, list them the other rappers most similar to it (plots generated in plots/ subfolder) 
    - Cluster the different rappers
'''

import sys
import os
sys.path.append('../')
from plotclassification import plotItemClassification
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans, MiniBatchKMeans
from libs import iohelper
import re
import operator


WORKING_DIR = os.getcwd()
DATA_LYRICS_PATH = WORKING_DIR + "/../data/azlyrics/"
DATA_SONG_NAMES_PATH = WORKING_DIR + "/../data/artist_songtitle.txt"

'''
Get lyrics for each song
'''
def gatherSongs():
    files = iohelper.listDirectoryContent(DATA_LYRICS_PATH, True)
    documents = []
    for f in files :
        for line in open(DATA_LYRICS_PATH + f):
            documents.append(line.strip())
    
    return documents

'''
Get song names
'''
def gatherSongNames():
    songnames = []
    for line in open(DATA_SONG_NAMES_PATH):
        lineArr = line.split('::')
        artist = lineArr[0]
        songs = lineArr[1]
        songsArr = songs.split('_')
        songnames += list(map(lambda x: ''.join([artist, '::', x.strip()]), songsArr))
    
    return songnames
  
    
def artistName(filename):
    return re.sub("\..*$", "", filename)


def gatherArtistLyrics():
    
    files = iohelper.listDirectoryContent(DATA_LYRICS_PATH, True)
    documents = {}
    for f in files :
        documents[artistName(f)] = open(DATA_LYRICS_PATH +f).read()
    
    return documents


def songSimilarity():
    songs = gatherSongs()
    songNames = gatherSongNames()
    print(len(songs), len(songNames))
    
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(songs)
    similarity = cosine_similarity(tfidf_matrix[0:len(songs)], tfidf_matrix)
    
    topNsimilarities = ''
    
    simMap = {}
    for i, sims in enumerate(similarity):
        songSim = {}
        for j, sim in enumerate(sims):
            songSim[songNames[j]] = sim
            
        song = songNames[i]
        simMap[song] = songSim
        topNsimilarities = ''.join([topNsimilarities, topNSimilarItems(simMap[song], song, song), '\n'])
    
    f = open("songSimilarities.txt", 'w')
    f.write(topNsimilarities)
    f.close()
    

'''
Find the top similar items based on cosine3 similarity
'''
def topNSimilarItems(similars, item, key, limit=10):
    similars.pop(key)
    
    sortedSim = sorted(similars.items(), key=operator.itemgetter(1), reverse=True)
    if limit > -1:
        sortedSim = sortedSim[0:limit]
    
    entry = ''.join([item,"\t", ', '.join(list(map(lambda x: x[0], sortedSim)))])
    print(entry)
    return entry

'''
Find all rappers' top similar rappers
'''
def artistSimilarity():
    lyrics = gatherArtistLyrics()
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(lyrics.values())
    similarity = cosine_similarity(tfidf_matrix[0:len(lyrics)], tfidf_matrix)
    
    artistNames = list(lyrics.keys())
    
    simMap = {}
    for i, sims in enumerate(similarity):
        artistSim = {}
        for j, sim in enumerate(sims):
            artistSim[artistName(artistNames[j])] = sim
            
        artist = artistName(artistNames[i])
        simMap[artist] = artistSim
        plotItemClassification(simMap[artist], artist, artist, "Similarity with Rapper: " + artist)
        
'''
Cluster rappers based on their vocabulary set
'''
def artistClustering():
    artistLyrics = gatherArtistLyrics()
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(artistLyrics.values())
    km = KMeans(n_clusters=5, init='k-means++', verbose=1)
    km.fit(tfidf_matrix)
    
    artistNames = list(artistLyrics.keys())
    clusterGroups = {}
    for i, label in enumerate(km.labels_):
        if label not in clusterGroups.keys():
            clusterGroups[label] = []
        clusterGroups[label].append(artistNames[i])
    
    f = open("rappersClustering.txt", "w")
    for k,v in clusterGroups.items():
        print(v)
        f.write(str(v))
        f.write("\n")
    f.close()
        
                
if __name__ == '__main__':
    
#     artistSimilarity()
#     songSimilarity()
    artistClustering()
    
    
    
    
    
    