import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import json
from dotenv import load_dotenv
import sys
load_dotenv()
import certifi
import pandas as pd
import numpy as np
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging import logger

ca = certifi.where()
MONGO_URL = os.getenv("MONGO_URL")

class NetworkDataExtract:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URL, server_api=ServerApi('1'), tlsCAFile=ca)
            logger.logging.info("MongoDB client initialized successfully.")
        except Exception as e:
            logger.logging.error(f"Failed to initialize MongoDB client: {e}")
            raise NetworkSecurityException(e, sys)

    def csv_to_json(self, csv_file_path):
        try:
            df = pd.read_csv(csv_file_path)
            df.reset_index(drop=True, inplace=True)
            records = list(json.load(df.T.to_json()).values())
            logger.logging.info(f"CSV file {csv_file_path} converted to JSON successfully.")
            return records
        except Exception as e:
            logger.logging.error(f"Failed to convert CSV to JSON for file {csv_file_path}: {e}")
            raise NetworkSecurityException(e, sys)

    def insert_data(self, data, database_name, collection_name):
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            collection.insert_many(data)
            logger.logging.info(f"Data inserted successfully into {database_name}.{collection_name} with length {len(data)}.")
        except Exception as e:
            logger.logging.error(f"Failed to insert data into {database_name}.{collection_name}: {e}")
            raise NetworkSecurityException(e, sys)
        
    def fetch_data(self, database_name, collection_name):
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            data = list(collection.find())
            logger.logging.info(f"Data fetched successfully from {database_name}.{collection_name}")
            return data
        except Exception as e:
            logger.logging.error(f"Failed to fetch data from {database_name}.{collection_name}: {e}")
            raise NetworkSecurityException(e, sys)
        
if __name__ == "__main__":
    FILE_PATH = "NetworkSecurity\Network_Data\phishingData.csv"
    DATABASE = "NetworkSecurityDB"
    COLLECTION = "NetworkData"
    networkobj = NetworkDataExtract()
    records = networkobj.csv_to_json(FILE_PATH)
    num_records = networkobj.insert_data(records, DATABASE, COLLECTION)
    print(f"Number of records inserted: {num_records}")