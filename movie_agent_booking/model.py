
from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Numeric,
    ForeignKey,
    CheckConstraint,
    select
)

from sqlalchemy.orm import DeclarativeBase, Session


# --------------------------------
# 1. Database connection
# --------------------------------

engine = create_engine(
    "sqlite:///movie_agent_booking.db",
    echo=True
)


# --------------------------------
# 2. Base class
# --------------------------------

class Base(DeclarativeBase):
    pass


# --------------------------------
# 3. Movies table
# --------------------------------

class Movies(Base):

    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(String(255), nullable=False)

    genre = Column(String(100))

    price = Column(Numeric(10, 2), nullable=False)

    total_seats = Column(Integer, default=0, nullable=False)

    booked_seats = Column(Integer, default=0, nullable=False)

    description = Column(Text, nullable=True)

    release_date = Column(DateTime, nullable=True)

    rating = Column(Numeric(3, 1), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    @property
    def available(self)-> int:
        return  self.total_seats -self.booked_seats

    __table_args__ = (
        CheckConstraint("total_seats >= 0"),
        CheckConstraint("booked_seats >= 0"),
        CheckConstraint("booked_seats <= total_seats"),
    )


# --------------------------------
# 4. Bookings table
# --------------------------------

class Bookings(Base):

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, autoincrement=True)

    movie_id = Column(
        Integer,
        ForeignKey("movies.id"),
        nullable=False
    )

    user_name = Column(String(255), nullable=False)

    user_email = Column(String(255), nullable=False)

    seats_booked = Column(Integer, default=1, nullable=False)

    total_amount = Column(Numeric(10, 2), default=0, nullable=False)

    status = Column(String(20), default="CONFIRMED")

    booking_time = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("seats_booked > 0"),
        CheckConstraint("total_amount >= 0"),
        CheckConstraint(
            "status IN ('PENDING', 'CONFIRMED', 'CANCELLED')"
        ),
    )


# --------------------------------
# 5. Create database tables
# --------------------------------

def create_table():

    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully!")


# --------------------------------
# 6. Seed movies
# --------------------------------

def seed_movies(movie_data):

    with Session(engine) as db:

        # Check whether movies already exist
        existing_movie = db.scalar(
            select(Movies.id).limit(1)
        )

        if existing_movie is not None:
            print("Movies already exist. Skipping seed.")
            return

        movies_objects = []

        for movie in movie_data:

            movies_objects.append(
                Movies(
                    title=movie["title"],
                    genre=movie.get("genre"),
                    price=movie["price"],
                    total_seats=movie["total_seats"],
                    description=movie.get("description"),
                    rating=movie.get("rating")
                )
            )

        db.add_all(movies_objects)

        db.commit()

        print(f"{len(movies_objects)} movies seeded successfully!")
