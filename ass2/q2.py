# COMP3311 22T1 Ass2 ... print info about different releases for Movie

from ast import IsNot
import sys
import psycopg2

# define any local helper functions here

def printNoMatch():
    print('No movie matching', '\'' + key + '\'')

# return a view of all movies contain the input
# order by the rating
def getMatchingMovies(cur):
    query = """
        SELECT title, rating, start_year, id
        FROM Movies
        WHERE title ~* %s
        ORDER BY rating DESC, start_year, title;
    """
    cur.execute(cur.mogrify(query, [key]))
    return cur.fetchall()

def getInfoOfMovie(cur, movie):
    title, rating, start_year, id = movie
    print(title, '(' + str(start_year) +')', end = " ")
    newQuery = """
        SELECT local_title, region, language, extra_info
        FROM Aliases
        WHERE movie_id = %s
        ORDER BY ordering
    """
    cur.execute(cur.mogrify(newQuery, [id]))
    return cur.fetchall()

def printMovieInfo(movieInfo):
    # no extra information
    if len(movieInfo) == 0:
        print('has no alternative releases')
            
    else:
        print('was also released as')
        for tup in movieInfo:
            title, region, language, extra_info = tup
            print('\'' + title + '\'', end =  " ")
            
            # print region/language/extra information about the movie
            if region or language is not None:
                aliases = "("
                
                if region is not None:
                    aliases += 'region: ' + str(region).strip()
                if language is not None:
                    aliases += ', language: ' + str(language).strip()
                    
                aliases += ")"
                print(aliases)
            elif extra_info is not None:
                print('(' + extra_info + ')')
    
def printMatchingMovies(movies):
    print('Movies matching', '\'' + key + '\'')
    print(line)
    for movie in movies:
        title, rating, start_year, id = movie
        print(rating, title, '(' + str(start_year) +')')
    
# set up some globals

usage = "Usage: q2.py 'PartialMovieTitle'"
db = None
line = '==============='

# process command-line args

argc = len(sys.argv)

# no input to search
if argc < 2:
        print(usage)
        exit()
        
key = sys.argv[1]

# manipulate database

try:
    db = psycopg2.connect("dbname=imdb")
    cur = db.cursor()
    
    tups = getMatchingMovies(cur)
    
    # No matching movie
    if len(tups) == 0:  
        printNoMatch()
    
    # one matching movie
    # print it's information
    elif len(tups) == 1:
        movieInfo = getInfoOfMovie(cur, tups[0])
        printMovieInfo(movieInfo)
        
    # multiplue matching movies
    # list the matching movies
    else:
       printMatchingMovies(tups)
    
except psycopg2.Error as err:
    print("DB error: ", err)
finally:
    if db:
        db.close()
