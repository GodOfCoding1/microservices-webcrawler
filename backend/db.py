from sqlalchemy import create_engine, Column, Integer, String, Text, Time
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    Time
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime


# Database configuration (TODO: should come from enviroment config)
DATABASE_CONFIG = {
    'dbname': 'db',
    'user': 'user',
    'password': 'password',
    'host': 'postgres',
    'port': 5432,
}

# Construct the database URL (TODO: should come from enviroment config)
DATABASE_URL = (
    f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}"
    f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['dbname']}"
)

Base = declarative_base()

#Tables defienition
class Company(Base):
    __tablename__ = "company"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(String, nullable=False)
    last_updated = Column(Time, default=lambda: datetime.datetime.now().time(), nullable=False)

    # Relationship
    metadata_entries = relationship("CompanyMetaData", back_populates="company")

# Second Table: Company Metadata
class CompanyMetaData(Base):
    __tablename__ = "company_metadata"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(Text, nullable=True)

    # Relationship 
    company = relationship("Company", back_populates="metadata_entries")

class QueryHistory(Base):
    __tablename__ = "query_history"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    query = Column(String, index=True, nullable=False, unique=True)
    last_queried = Column(Time, nullable=False)

    #relationships
    document_ids = relationship("QueryToDocumentID", back_populates="query")

class QueryToDocumentID(Base):
    __tablename__ = "query_document_id"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    query_id = Column(Integer, ForeignKey("query_history.id"), nullable=False)
    document_id = Column(String, nullable=False)

    #relationships
    query = relationship("QueryHistory", back_populates="document_ids")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Define a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

def getSessionLocal():
    return SessionLocal()