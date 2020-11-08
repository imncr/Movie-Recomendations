'''
Created on Nov 18, 2019

@author: Nicolas

This program looks through csv files in the specified subfolder to output back to 
the user the three critics that have the most similar ratings to the person in 
question, measured by euclidean distance, as well as recommendations for movies that
the person has not rated but based on the average rating of the three critics most 
similar the person in question may like, measured by highest average rating of the 
three critics in each genre.

INPUT:
    -subfolder: the subfolder that all needed files can be found in
    -moviefile: the csv with IMDB information about the movie (e.g. Runtime, Genre1, Year )
    -criticfile: the csv with the rating of critics of each movie
    -personalfile: the csv with the rating of the person of interest
PROGRAM DATA:
    -movieDF: the pandas dataframe containing the necessary cols from the moviefile
    -criticDF: the pandas dataframe containing the criticfile
    -personalDF: the pandas dataframe containing the personalfile
    -similarCriticList: the list of three most similar critics, measured by euclidean distance
    -criticStr: the formated string to output of the three most similar critics
    -aName: the name of the person of interest
    -recommendationDF: the pandas dataframe containing necessary information about movies to recommend
OUTPUT:
    -the three most similar critics to the person of interest
    -the information about recommended movies for each genre (e.g. Title, Genre, average rating of three critics, Year, Runtime )
'''
import os
import os.path
import numpy as np
import pandas as pd
pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.width', 1000)

def findClosestCritics(criticDF, personalDF):
    '''
    Function takes movie rating information from a person of interest and from critics,
    calculates the euclidean distance between the person of interest and critics ratings,
    and returns the three critics with the lowest euclidean distance.
    Parameters:
        -criticDF: the pandas dataframe containing the criticfile 
        -personalDF: the pandas dataframe containing the personalfile
    Returns:
        -threeClosestCritics: the list of three most similar critics, measured by euclidean distance
    '''
    criticDF = criticDF.set_index('Title')
    personalDF = personalDF.set_index('Title')
    personalSeries = personalDF.iloc[:,0]
    differenceDF = criticDF.subtract(personalSeries, axis = 0)
    differenceDF = differenceDF**2
    criticDistance = differenceDF.sum()**(0.5)
    criticDistance = criticDistance.sort_values()
    threeClosestCritics = list(criticDistance.index)[:3]
    return threeClosestCritics

def recommendMovies(criticDF, personalDF, similarCriticList, movieDF):
    '''
    Function takes movie rating information from a person of interest and from critics,
    a list of the most similar critics to the person of interest, and information about
    movies.  The function then determines which movies to recommend the person of interest
    based on them having not rated the movie and the critics most similar to them having
    rated that movie on average higher than other movies in that genre.
    Parameters:
        -criticDF: the pandas dataframe containing the criticfile 
        -personalDF: the pandas dataframe containing the personalfile
        -similarCriticList: the list of three most similar critics, measured by euclidean distance
        -movieDF:the pandas dataframe containing the necessary cols from the moviefile
    Returns:
        -recommendationDF: the pandas dataframe containing necessary information about movies to recommend
    '''
    criticDF = criticDF.set_index('Title')
    personalDF = personalDF.set_index('Title')
    movieDF = movieDF.set_index('Title')
    
    criticDF = criticDF.reindex(columns = similarCriticList)
    criticDF['Avg'] = criticDF.mean(axis = 1)
    
    allRatingDF = pd.merge(left = personalDF, right = criticDF, how = 'outer', left_on = personalDF.index, right_on = criticDF.index)
    unwatchedMovieDF = allRatingDF[pd.isnull(allRatingDF.iloc[:,1])]
    potentialRecommendationDF = pd.merge(left = unwatchedMovieDF, right = movieDF, how = 'left', left_on = 'key_0', right_on = movieDF.index)
    potentialRecommendationDF.dropna(axis = 0, subset = ['Genre1'], inplace = True)
    potentialRecommendationDF.fillna(' ', axis = 0, inplace = True)
    
    idx = potentialRecommendationDF.groupby(by = 'Genre1', sort = True)['Avg'].transform(max) == potentialRecommendationDF['Avg']
    recommendationDF = potentialRecommendationDF[idx]
    recommendationDF =recommendationDF.rename(columns = {'key_0':'Title'})
    return recommendationDF

def getName(personalDF):
    '''
    This function takes movie rating information from a person of interest and returns
    the name of the person of interest.
    Parameters:
        -personalDF: the pandas dataframe containing the personalfile
    Returns:
        -list(personalDF.columns)[1]: the name of the person of interest
    '''
    return list(personalDF.columns)[1]

def printRecommendations(recommendationDF, aName):
    '''
    This function formats and prints the movie recommendations in the way specified by
    sample interactions.
    Parameters:
        -recommendationDF: the pandas dataframe containing necessary information about movies to recommend
        -aName: the name of the person of interest
    '''
    recommendationDF = recommendationDF.reindex(columns = ['Title','Genre1','Avg','Year','Runtime'])
    recommendationDF = recommendationDF.sort_values('Genre1')
    largestTitleLen = recommendationDF.Title.str.len().max()
    largestTitleLen = str(largestTitleLen + 2) + 's'
    titleList = list(recommendationDF.loc[:,'Title'])
    titleList = ['\"' + title + '\"' for title in titleList]
    genreList = list(recommendationDF.loc[:,'Genre1'])
    genreList = ['(' + genre + ')' for genre in genreList]
    avgList = list(recommendationDF.loc[:,'Avg'])
    avgList = ['rating: ' + str(round(avg,2)) for avg in avgList]
    yearList = list(recommendationDF.loc[:,'Year'])
    runtimeList = list(recommendationDF.loc[:,'Runtime'])
    runtimeList = ['runs ' + runtime for runtime in runtimeList]
    
    i = 0
    print('Recommendations for ', aName, ':', sep = '')
    for i in range(len(titleList)):
        print(format(titleList[i],largestTitleLen), end = ' ')
        print(genreList[i], end = ', ')
        print(avgList[i], end = ', ')
        print(yearList[i], end = '')
        if runtimeList[i] != 'runs  ':
            print(', ' + runtimeList[i])
        else:
            print()
        i += 1

def main():
    #Gets the name of subfolder and files needed to make movie recommendations from user input
    subfolder,moviefile,criticfile,personalfile = input('Please enter the name of the folder with files, the name of movies file,\nthe name of critics file, the name of personal ratings file, separated by spaces:\n').split()
    print()
    
    #creates device independent paths to import csv data
    cwd = os.getcwd()
    subfolderPath = os.path.join(cwd,subfolder)
    moviefilePath = os.path.join(subfolderPath,moviefile)
    criticfilePath = os.path.join(subfolderPath,criticfile)
    personalfilePath = os.path.join(subfolderPath,personalfile)
    
    #imports csv data into pandas dataframes
    movieDF = pd.read_csv(moviefilePath, usecols = ['Title','Genre1','Year','Runtime'])
    criticDF = pd.read_csv(criticfilePath)
    personalDF = pd.read_csv(personalfilePath)
    
    #finds the most similar critics and prints them in the properly formated way
    print('The following critics had reviews closest to the person\'s:')
    similarCriticList = findClosestCritics(criticDF, personalDF)
    criticStr = ''
    for critic in similarCriticList:
        criticStr = criticStr + critic + ', '
    criticStr = criticStr[:len(criticStr)-2]
    print(criticStr)
    print()
    
    #finds the persons name and movie recommendations and prints them in the properly formated way
    aName = getName(personalDF)
    recommendationDF = recommendMovies(criticDF, personalDF, similarCriticList, movieDF)
    printRecommendations(recommendationDF, aName)
    
main()