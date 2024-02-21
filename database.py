from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Location(Base):
    __tablename__ = "locations"

    zip = Column(String, primary_key=True)
    lat = Column(Float)
    lng = Column(Float)
    city = Column(String)
    state_id = Column(String)
    state_name = Column(String)
    zcta = Column(Boolean)
    parent_zcta = Column(String)
    population = Column(Integer)
    density = Column(Float)
    county_fips = Column(String)
    county_name = Column(String)
    county_weights = Column(String)
    county_names_all = Column(String)
    county_fips_all = Column(String)
    imprecise = Column(Boolean)
    military = Column(Boolean)
    timezone = Column(String)


class Location_id(Base):

    __tablename__ = "locations_id"

    id = Column(Integer, primary_key=True, autoincrement=True)
    point = Column(JSON)

Base.metadata.create_all(bind=engine)