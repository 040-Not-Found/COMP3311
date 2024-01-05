# COMP3311 22T1 Ass2 ... print num_of_movies, name of top N people with most movie directed

import sys
import psycopg2

# define any local helper functions here

def printInfo(directors):
    for director in directors:
        countM, name = director
        print(countM, name)
        
# return a view of directors and the number of movies they directed
# order by the number of movies they had directed
def getNDirectors(cur):
    cur.execute("""
        SELECT count(Movies.id), Names.name
        FROM Crew_roles
        JOIN Movies
        ON Crew_roles.movie_id = Movies.id
        JOIN Names
        ON Crew_roles.name_id = Names.id
        WHERE Crew_roles.role = 'director'
        GROUP BY Names.id
        ORDER BY count(Movies.id) DESC, Names.name;
    """)
    
    # print N people
    return cur.fetchmany(N)

# set up some globals

usage = "Usage: q1.py [N]"
db = None

# process command-line args

argc = len(sys.argv)
N = 10  #defult N

if argc > 1:    # has N people
    try: 
        N = int(sys.argv[1])
    except:
        print(usage)
        exit()
        
if N < 1:   #less than one person
    print(usage)
    exit()
    
# manipulate database

try:
    db = psycopg2.connect("dbname=imdb")
    cur = db.cursor()
    
    directors = getNDirectors(cur)
    printInfo(directors)
    
except psycopg2.Error as err:
    print("DB error: ", err)
finally:
    if db:
        db.close()
