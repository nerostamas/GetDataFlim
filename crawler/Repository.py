from sqlalchemy import *

class Repository:
    def __init__(self, showLog = False):
        self.__showLog = showLog
        print "Connect to database"
        self.__engine = create_engine('mysql+mysqlconnector://root:root@localhost:3306/MovieDB', echo=self.__showLog)
        self.__metadata = MetaData()

        self.__persons = Table('Person', self.__metadata,
            Column('Id', Integer, primary_key = True),
            Column('Name', String(255), nullable = False, unique = True)
        )

        self.__movies = Table('Movie', self.__metadata,
            Column('Id', Integer, primary_key = True),
            Column('Title', String(255), nullable = False, unique = True),
            Column('ImdbLink', String(255), nullable = False, unique = True),
            Column('ReleaseDate', Date, nullable = True),
            Column('Rating', Float, nullable = True),
            Column('Synopsis', Text, nullable = True),
            Column('Img', String(255), nullable= True)
        )

        self.__actors = Table('Actor', self.__metadata,
            Column('Id', Integer, primary_key = True),
            Column('Person_id', None, ForeignKey('Person.Id')),
            Column('Movie_id', None, ForeignKey('Movie.Id')),
            Column('CharacterName', String(255), nullable = True)
        )

        self.__genre = Table('Genre', self.__metadata,
            Column('Id', Integer, primary_key=True),
            Column('Name', String(255), nullable=False, unique=True)
        )

        self.__directors = Table('Director', self.__metadata,
            Column('Id', Integer, primary_key = True),
            Column('Person_id', None, ForeignKey('Person.Id')),
            Column('Movie_id', None, ForeignKey('Movie.Id'))
        )

        self.__movieGenre = Table('Movie_Genre',self.__metadata,
            Column('Id', Integer, primary_key=True),
            Column('Movie_id',None,ForeignKey('Movie.Id')),
            Column('Genre_id',None,ForeignKey('Genre.Id'))
        )

    def createSchema(self):
        """
        Create schema in database.
        """
        self.__metadata.drop_all(self.__engine)
        self.__metadata.create_all(self.__engine)

    # Person methods
    def getPersonId(self, name):
        result = self.__engine.connect().execute(
            select([self.__persons.c.Id],
                and_(self.__persons.c.Name == name)
            )
        )

        firstRow = result.fetchone()

        if firstRow == None:
            return None
        else:
            return firstRow[0]

            # Person methods

    def getGenreId(self, name):
        result = self.__engine.connect().execute(
            select([self.__genre.c.Id],
                   and_(self.__genre.c.Name == name)
                   )
        )

        firstRow = result.fetchone()

        if firstRow == None:
            return None
        else:
            return firstRow[0]

    def savePerson(self, name):
        result = self.__engine.connect().execute(
            self.__persons.insert()
            .values(Name = name)
        )

        return result.inserted_primary_key[0]

    # save Genre
    def saveGenre(self, genreName):
        result = self.__engine.connect().execute(
            self.__genre.insert()
                .values(Name=genreName)
        )

        return result.inserted_primary_key[0]

        #    def updatePerson(self, id, name):
#        conn = self.__engine.connect()
#
#        conn.execute(
#            self.__persons.update().
#            where(self.__persons.c.Id == id).
#            values(Name = name)
#        )

    def savePersonIfDoesnExist(self, name):
        personId = self.getPersonId(name)

        if personId == None:
            return self.savePerson(name)
        else:
            return personId

    def saveGenreIfDoesnExist(self, name):
        genreId = self.getGenreId(name)

        if genreId == None:
            return self.saveGenre(name)
        else:
            return genreId

    # Movie methods
    def getMovieId(self, title):
        result = self.__engine.connect().execute(
            select([self.__movies.c.Id],
                and_(self.__movies.c.Title == title)
            )
        )

        firstRow = result.fetchone()

        if firstRow == None:
            return None
        else:
            return firstRow[0]

    def insertMovie(self, movie):
        result = self.__engine.connect().execute(
            self.__movies.insert()
            .values(Title = movie.Title,
                    ImdbLink = movie.ImdbLink,
                    ReleaseDate = movie.ReleaseDate,
                    Rating = movie.Rating,
                    Synopsis = movie.Synopsis,
                    Img = movie.MovieImg)
        )

        return result.inserted_primary_key[0]

    def saveMovie(self, movie):
        movieId = self.getMovieId(movie.Title)
        if movieId == None:
            movieId = self.insertMovie(movie)

        for directorName in movie.Directors:
            self.saveDirector(movieId, directorName)

        for actorName, characterName in movie.Actors.items():
            self.saveActor(movieId, actorName, characterName)

        for genre in movie.Genres:
            self.saveGenreMovie(movieId, genre)

    # Director methods
    def saveDirector(self, movieId, directorName):
        personId = self.savePersonIfDoesnExist(directorName)

        result = self.__engine.connect().execute(
            self.__directors.insert()
            .values(Movie_id = movieId, Person_id = personId)
        )

        return result.inserted_primary_key[0]

    def saveGenreMovie(self, movieId, genreName ):
        genreId = self.saveGenreIfDoesnExist(genreName)

        result = self.__engine.connect().execute(
            self.__movieGenre.insert()
                .values(Movie_id=movieId, Genre_id=genreId)
        )

        return result.inserted_primary_key[0]

    # Actor methods
    def saveActor(self, movieId, actorName, characterName):
        personId = self.savePersonIfDoesnExist(actorName)

        result = self.__engine.connect().execute(
            self.__actors.insert()
            .values(Movie_id = movieId, Person_id = personId, CharacterName = characterName)
        )

        return result.inserted_primary_key[0]
