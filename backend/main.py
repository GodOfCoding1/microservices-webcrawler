from fastapi import FastAPI, Query, Depends, HTTPException
from datetime import datetime, timedelta
import requests
from fastapi import FastAPI, Query
from typing import Literal
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import queue
import threading
import time
from datetime import datetime
from db import Company,CompanyMetaData,QueryHistory,QueryToDocumentID,getSessionLocal

# Initialize the queue
data_queue = queue.Queue()

# Background thread to process the queue
def process_queue():
    while True:
        if not data_queue.empty():
            item = data_queue.get()  # Get the next item in the queue
            query, table_data, current_time, document_ids = item.get("query"), item.get("data"), item.get("time"), item.get("document_ids")
            
            # Open a database session
            with getSessionLocal() as db:
                # Check if the query exists in the query_history table
                query_record = db.query(QueryHistory).filter(QueryHistory.query == query).first()
                if not query_record:
                    query_record = QueryHistory(query=query, last_queried=current_time.time())
                    db.add(query_record)
                    db.flush() # does query db but doesnt commit
                    for id in document_ids:
                        db.add(QueryToDocumentID(query_id=query_record.id,document_id=id))
                # Check if the query exists
                data_rows=[]
                for data in table_data:
                    query_record = Company(document_id=data["Document Number"], last_updated=current_time.time()) 
                    db.add(query_record) #can create a hash of data recevied from cralwer and compare witha  new column in company table to determine if data has changed or not. ignored due to complexitly but this will result in data redundance
                    db.flush()
                    for key in data:
                        data_rows.append(CompanyMetaData(company_id=query_record.id, key=key, value= data[key]))
                db.add_all(data_rows)
                db.commit()
            print(f"Uploaded data for query: {query}")
        else:
            time.sleep(1)

# Start the worker thread
worker_thread = threading.Thread(target=process_queue, daemon=True)
worker_thread.start()

# Function to add data to the queue
def add_to_upload_queue(query, data,querytime , doc_ids):
    """
    Add data to the queue for processing in the background.
    """
    data_queue.put({"query": query, "data": data,"time":querytime,"document_ids":doc_ids})

# Dependency to get the database session
def get_db():
    db = getSessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI application
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

def useCrawler(query:str):
    # Call the API if query does not exist or is outdated
    try:
        response = requests.get(f"http://crawler:8000/crawl?query={query}")
        if response.status_code == 200:
            data = response.json() # data strucutre :  {"table_data": table_data, "document_ids":document_ids }
            current_time = datetime.now()
            add_to_upload_queue(query, data["table_data"], current_time, data["document_ids"])
            return {"status":response.status_code, "success":True, "data":data["table_data"]}
        return {"status":response.status_code,"success":False, "data":[] }
    except:
        return {"status":500, "success":False, "data":[]}
    
def useDataBase(db, query_record):
    # Call the API if query does not exist or is outdated
    try:
        if not query_record:
            return {"status":404, "success":False, "message": "No such query in db", "data":[]}
        # return "query record found"
        # Check if the last queried time is greater than 30 days
        # last_queried_time = datetime.combine(current_time.date(), query_record.last_queried)
        # if current_time - last_queried_time < timedelta(days=30):
        #     return "query found"
        # Retrieve data from the query_data table
        # Check if the query exists in the query_history table

        # Get all document_ids linked to the query
        document_ids = db.query(QueryToDocumentID.document_id).filter(QueryToDocumentID.query_id == query_record.id).all()
        if not document_ids:
            return {"status":404, "success":False, "message": "No document IDs associated with the query", "data":[]} #ideally we can even delete the query entry (as something has gone wrong with the uploading part as only query got uploaded) and refetch the data using crawler but ignored for simplicity

        # Flatten document_ids from list of tuples
        document_ids = [doc[0] for doc in document_ids]
        # Get company data for each document ID
        companies = (
            db.query(Company)
            .filter(Company.document_id.in_(document_ids))
            .all()
        )# ideally should wirte a single sql query to avoid making multiple requests to db

        if not companies:
            return {"status":404, "success":False, "message":"No companies found for the given query", "data":[]}

        result = []
        for company in companies:
            # Fetch data for the current company
            metadata = db.query(CompanyMetaData).filter(CompanyMetaData.company_id == company.id).all()
            metadata_dict = {meta.key: meta.value for meta in metadata}
            metadata_dict["Document id"] = company.document_id
            result.append(metadata_dict)

        return {"status":200, "success":True, "data": result}
    except:
        return {"status":500, "success":False,"message":"Unknown Server Error",  "data":[]}

@app.get("/api/data")
def fetch_query_data(
    query: str = Query(..., description="The query string to fetch data for"),
    type: str =  Query(..., description="Type of search"), # Literal["optimal", "db", "crawl"]
    db: Session = Depends(get_db)
):
    """
    API endpoint to fetch query data.

    :param query: The query string to fetch data for.
    :param db: The database session (injected via dependency).
    :return: The data from either the API or the database.
    """
    query = query.lower().strip()
    query_record = db.query(QueryHistory).filter(QueryHistory.query == query).first() 

    if (not type in ["optimal", "db", "crawl"]):
        raise HTTPException(status_code=400, detail="type parameter must be set and one of optimal, db, crawl")

    if (type=="optimal" and query_record) or type=='db':
        response = useDataBase(db, query_record)
        if response["success"]:
            return {"source": "database", "data": response["data"]}
        else:
            raise HTTPException(status_code=response["status"], detail=response["message"])
    
    if (type=="crawl") or (type=="optimal" and not query_record):
        crawler_data = useCrawler(query)
        if (crawler_data["status"]==200):
            return {"source": "crawler", "data": crawler_data["data"]}
        # Raise error if the API call fails
        raise HTTPException(status_code=crawler_data["status"], detail="Failed to fetch data from Crawler.")
    
    raise HTTPException(status_code=500, detail="A error unaccounted for happened")

