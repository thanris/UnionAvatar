import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
import CreatorData as Data
import os

app = FastAPI()
db_name = "database"
Data.main()
@app.get("/as/{asn}")
def get_as(asn: int):
    result = Data.get_asn_info(asn, db_name)
    return result

@app.get("/ip/{ip}")
def get_ip(ip: str):
    result = Data.get_asn_by_ip(ip, db_name)
    return result

