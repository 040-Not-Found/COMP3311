# COMP3311 22T1 Ass2 ... print info about cast and crew for Movie

import sys
import psycopg2

# define any local helper functions here

# return a view of all movies contain the input
# order by the rating
def getMovies(cur):
    query = """
        SELECT title, rating, start_year, id
        FROM Movies
        WHERE title ~* %s
        ORDER BY rating DESC, start_year, title;
    """
    cur.execute(cur.mogrify(query, [key]))
    return cur.fetchall()

def printNoMatch():
    print('No movie matching', '\'' + key + '\'', end = '')
    try:    # does not contains year
        print('', year)
    except:
        print('')
    
def printMatchingMovies(movies):
    print('Movies matching', '\'' + key + '\'', end = '')
    
    try:    # does not contains year
        print('', year)
    except:
        print('')
        
    print(line)
    for movie in movies:
        title, rating, start_year, id = movie
        print(rating, title, '(' + str(start_year) +')')

# return a view of all movies contain the input(name and year)
def getMatchingMoviesYear(movies, year):
    moviesMatchingYear = []
    for movie in movies:
        title, rating, start_year, id = movie
        if start_year == year:
            moviesMatchingYear.append(movie)
    return moviesMatchingYear

# return a view of acting roles of the movie
def getActingRoles(cur, movie_id):
    query = """
        SELECT name, played
        FROM Movies
        JOIN Acting_roles
        ON Movies.id = Acting_roles.movie_id
        JOIN Names
        ON Names.id = Acting_roles.name_id 
    """ + principals + "ORDER BY ordering, played;"
    
    cur.execute(cur.mogrify(query, [movie_id]))
    return cur.fetchall()
    
def printActingRoles(actingRoles):
    for role in actingRoles:
        name, played = role
        print('', name, 'as' , played)
    
# return a view of crew roles of the movie
def getCrewRoles(cur, movie_id):
    query = """
        SELECT name, role
        FROM Movies
        JOIN Crew_roles
        ON Movies.id = Crew_roles.movie_id
        JOIN Names
        ON Names.id = Crew_roles.name_id
    """ + principals + "ORDER BY ordering, role;"
    cur.execute(cur.mogrify(query, [movie_id]))
    return cur.fetchall()
    
def printCrewRoles(crewRoles):
    for role in crewRoles:
        name, role = role
        print('', name + ':' , role.capitalize())
    
def printRoles(cur, movie_id, title):
    print(title, '(' + str(start_year) + ')')
    print(line)
    print('Starring')
    
    actingRoles = getActingRoles(cur, movie_id)
    crewRoles = getCrewRoles(cur, movie_id)
    
    printActingRoles(actingRoles)
    print('and with')
    printCrewRoles(crewRoles)

# set up some globals

usage = "Usage: q3.py 'MovieTitlePattern' [Year]"
db = None
line = '==============='

# movies that are principal
principals = """
    JOIN Principals
    ON Names.id = Principals.name_id
    AND Movies.id = Principals.movie_id
    WHERE Movies.id = %s 
"""

# process command-line args

argc = len(sys.argv)

try:
    key = sys.argv[1]   
except: # no input to search
    print(usage)
    exit()
    
if argc == 3:
    try:
        year = int(sys.argv[2])
    except: # year is not an integer
        print(usage)
        exit()
        
# manipulate database

try:
    db = psycopg2.connect("dbname=imdb")
    cur = db.cursor()
    
    movies = getMovies(cur)
    
    if len(movies) == 0:  # no matching movies
        printNoMatch()
        
    elif argc == 2: # movies not related to year
        if len(movies) == 1:    # one matching movie
            title, rating, start_year, id = movies[0]
            printRoles(cur, id, title)
            
        else:   #multiple matching movies
            printMatchingMovies(movies)
            
    elif argc == 3: # movies related to year
            
        moviesMatchingYear = getMatchingMoviesYear(movies, year)
                
        if len(moviesMatchingYear) == 0:    # not matching movie in the year
            printNoMatch()
            
        elif len(moviesMatchingYear) == 1:  # one matching movie in the year
            title, rating, start_year, id = moviesMatchingYear[0]
            printRoles(cur, id, title)
            
        else:   #multiple matching movies in the year
            printMatchingMovies(moviesMatchingYear)
                
except psycopg2.Error as err:
    print("DB error: ", err)
finally:
    if db:
        db.close()

