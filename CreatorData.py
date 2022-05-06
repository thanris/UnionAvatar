import sqlite3
import requests
import os
import sys
import json
import time
from pydantic import BaseModel

class AS(BaseModel):
    ipv4_prefixes: str
    ipv6_prefixes: str
    asn: int
    country: str
    info: str

    
def download_file(url, file_name):
    with open(file_name, "wb") as file:
        response = requests.get(url)
        file.write(response.content)


def create_db(file_name):
    conn = sqlite3.connect(file_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE ASN (
        start_ip TEXT,
        end_ip TEXT,
        asn INTEGER,
        country TEXT,
        info TEXT
    )''')
    conn.commit()
    conn.close()


def insert_data(file_name, db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    with open(file_name, 'r', encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            start_ip, end_ip, asn, country, info = line.split(None,4)
            if line.startswith('#'):
                continue
            c.execute("INSERT INTO ASN VALUES (?, ?, ?, ?, ?)", (start_ip, end_ip, asn, country, info))
    conn.commit()
    conn.close()


def get_asn_info(asn, db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM ASN WHERE asn = ?", (asn,))
    row = c.fetchone()
    conn.close()
    if row is None:
        return {"error": "ASN not found"}
    return AS(ipv4_prefixes=row[0], ipv6_prefixes=row[1], asn=row[2], country=row[3], info=row[4])


def get_asn_by_ip(ip, db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM ASN WHERE start_ip <= ? AND end_ip >= ?", (ip, ip))
    row = c.fetchone()
    conn.close()
    print(row)
    if row is None:
        return {"error": "IP not found"}
    return AS(ipv4_prefixes=row[0], ipv6_prefixes=row[1], asn=row[2], country=row[3], info=row[4])


def main():
    db_name = "Database"
    if not os.path.exists(db_name):
        print("Database file does not exist. Creating it...")
        create_db(db_name)
        print("Downloading data...")
        download_file("https://iptoasn.com/data/ip2asn-v4.tsv.gz", "ip2asn-v4.tsv.gz")
        download_file("https://iptoasn.com/data/ip2asn-v6.tsv.gz", "ip2asn-v6.tsv.gz")
        print("Unzipping data...")
        os.system("gunzip ip2asn-v4.tsv.gz")
        os.system("gunzip ip2asn-v6.tsv.gz")
        print("Inserting data into database...")
        insert_data("ip2asn-v4.tsv", db_name)
        insert_data("ip2asn-v6.tsv", db_name)
        print("Done!")
    else:
        print("Database file already exists. Using it...")
    print("Getting ASN info...")
    asn_info = get_asn_info("13335", db_name)
    print(asn_info)
    print("Getting ASN by IP...")
    asn_by_ip = get_asn_by_ip("8.8.8.0", db_name)
    print(asn_by_ip)
