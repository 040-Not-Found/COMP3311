# COMP3311 22T1 Ass2 ... get Name's biography/filmography

from collections import Counter
from statistics import mean
import sys
import psycopg2

# define any local helper functions here

def getPeople():
    query = """
        SELECT id, name, birth_year, death_year
        FROM Names
        WHERE name ~* %s
        ORDER BY name, birth_year, id
    """
    cur.execute(cur.mogrify(query, [key]))
    return cur.fetchall()

def getMatchingPeopleYear(people):
    peopleInYear = []
    for person in people:
        id, name, birth_year, death_year = person
        if birth_year == year:
            peopleInYear.append(person)
    return peopleInYear

def printNoMatch():
    text = 'No name matching \'' + str(sys.argv[1]) + '\''
    try:
        text += ' ' + sys.argv[2]
    except:
        pass
    print(text)
    exit()

def printName(name, birth_year, death_year):
    person = name + ' ('
    if birth_year != 'None':
        person += birth_year + '-'
        if death_year != 'None':
            person += death_year
    else:
        person += '???'
    person += ')'
    print(person)

def printNames(names):
    print('Names matching \'' + str(key) + '\'')
    print(line)
    for name in names:
        id, name, birth_year, death_year = name
        printName(str(name), str(birth_year), str(death_year))
        
def printInfo(cur, person):
    name_id, name, birth_year, death_year = person
    
    print('Filmography for ', end= '')
    printName(str(name), str(birth_year), str(death_year))
    print(line)
    
    cur.execute(cur.mogrify(id_query, [name_id, name_id]))
    movie_ids = cur.fetchall()
    
    cur.execute(cur.mogrify(ratingGenreQ, [name_id, name_id]))
    ratingGenres = cur.fetchall()
    
    cur.execute(cur.mogrify(actingCrewQ, [name_id, name_id]))
    actingCrews = cur.fetchall()
    
    printInfoHelper(movie_ids, ratingGenres, actingCrews)
    
def printInfoHelper(movie_ids, ratingGenres, actingCrews):
    printText = ''
    ratings = []
    genres = []
    
    for id in movie_ids:
        movie_id0, title0, start_year0, rating0 = id
        
        # adding movie's title and year
        printText += str(title0)  + ' (' + str(start_year0) + ')\n'
        ratings.append(rating0)
        
        # adding movie genres
        for ratingGenre in ratingGenres:
            movie_id, genre, start_year, title = ratingGenre
            if movie_id0 == movie_id:
                genres.append(genre)

        # adding acting and crew roles
        for actingCrew in actingCrews:
            movie_id, played, role, start_year, title = actingCrew
            if movie_id0 == movie_id:
                if played is not None:
                    printText += ' playing ' + str(played) + '\n'
                elif role is not None:
                    printText += ' as ' + str(role.replace('_', ' ').capitalize()) + '\n'
            
    # calculate the average rating
    try:
        avgRateing = round(mean(ratings), 1)
    except: 
        avgRateing = 0
    
    # get the top 3 genres
    topGenres = Counter(sorted(genres)).most_common(3)
    
    printFullInfo(avgRateing, topGenres, printText)
    
def printFullInfo(avgRateing, topGenres, printText):
    print('Personal Rating:', avgRateing)
    print('Top 3 Genres:')
    for genre in topGenres:
        print(' ' + str(genre[0]))
    print(line)
    print(printText)

# set up some globals

usage = "Usage: q4.py 'NamePattern' [Year]"
db = None
line = '==============='

# view of movieid, played, role of the person
query = """
    WITH Acts AS (
        SELECT Principals.movie_id, played
        FROM Principals
        LEFT JOIN Acting_roles
        ON Acting_roles.movie_id = Principals.movie_id
        AND Principals.name_id = Acting_roles.name_id
        WHERE Principals.name_id = %s
    ),
    Roles AS (
        SELECT Principals.movie_id, role
        FROM Principals
        LEFT JOIN Crew_roles
        ON Crew_roles.movie_id = Principals.movie_id
        AND Principals.name_id = Crew_roles.name_id
        WHERE Principals.name_id = %s
    ),
    T AS (
        SELECT movie_id, played, NULL AS role
        FROM Acts
        UNION ALL
        SELECT movie_id, NULL As played, role
        FROM Roles
    )
"""

# view of unqiue movie ids of the person presented
id_query = query + """
    SELECT DISTINCT movie_id, title, start_year, rating
    FROM T 
    JOIN Movies
    ON id = movie_id
    ORDER BY start_year, title
"""

# view of movies' rating of the person presented
ratingGenreQ = query + """
    SELECT id, genre, start_year, title
    FROM (
        SELECT DISTINCT movie_id
        FROM T
    ) As ids
    JOIN Movie_genres
    ON ids.movie_id = Movie_genres.movie_id
    JOIN Movies
    ON id = ids.movie_id
    ORDER BY start_year, title
"""

# view of the person's acting and crew roles
actingCrewQ = query + """
    SELECT T.movie_id, played, role, start_year, title
    FROM T
    JOIN Movies
    ON Movies.id = T.movie_id
    ORDER BY start_year, title, played, role
"""

# process command-line args

argc = len(sys.argv)
if argc < 2:
    print(usage)
    exit()

try:
    key = sys.argv[1]
except:
    print(usage)
    exit()
    
if argc == 3:
    try:
        year = int(sys.argv[2])
    except:
        print(usage)
        exit()
    
# manipulate database

try:
    db = psycopg2.connect("dbname=imdb")
    cur = db.cursor()
    people = getPeople()
    
    if len(people) == 0:    # no matching people
        printNoMatch()
        
    if argc == 2:   # not related to year
        if len(people) == 1:    # one matching person
            printInfo(cur, people[0])
            
        else:   # multiple matching people
            printNames(people)
            
    elif argc == 3: #related to year
        if len(people) == 1:
            id, name, birth_year, death_year = people[0]
            
            if birth_year == year:  # one matching person in the year
                printInfo(cur, people[0])
                
            else:   # no matching people in the year
                printNoMatch()
                
        else:   # multiple matching people
            peopleInYear = getMatchingPeopleYear(people)
            
            if len(peopleInYear) == 0:  # no matching people in the year
                printNoMatch()   

            elif len(peopleInYear) == 1:    # one matching person in the year
                printInfo(cur, peopleInYear[0])
                
            else:   # multiple matching people in the year
                printNames(peopleInYear)
            
except psycopg2.Error as err:
    print("DB error: ", err)
finally:
    if db:
        db.close()

