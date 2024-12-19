from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    create_engine,
    Text,
    Time
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import queue
import threading
from extract_data import extractCompaniesWithQuery
import time
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Database configuration dictionary
DATABASE_CONFIG = {
    'dbname': 'db',
    'user': 'user',
    'password': 'password',
    'host': 'postgres',
    'port': 5432,  # Default PostgreSQL port
}

# Construct the database URL
DATABASE_URL = (
    f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}"
    f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['dbname']}"
)

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ping
@app.get("/hi")
def hello_world():
    return "Hello World!"

@app.get("/crawl")
def extract_company_details(query: str = Query(..., description="The query parameter to fetch company details")):
    """
    This endpoint fetches details for a given query.
    If the query does not exist in the database, new data is fetched and queued for insertion.
    """
    # Simulate fetching data from an external source
    table_data , document_ids = extractCompaniesWithQuery(query)
    return {"table_data": table_data, "document_ids":document_ids } #return immediately for the user
#query wwould have returned some document ids which have to be saved with the query so that when user makes the same query we can get the results