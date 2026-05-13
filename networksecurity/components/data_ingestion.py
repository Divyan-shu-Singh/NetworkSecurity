import os
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact
from networksecurity.constants import training_pipeline
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import sys
from sklearn.model_selection import train_test_split
import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import certifi
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_URL")


class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_collection_as_dataframe(self, collection_name: str, database_name: str) -> pd.DataFrame:
        try:
            if not MONGO_DB_URL:
                raise ValueError("MONGO_URL is not set. Add it to .env or your environment before running ingestion.")

            client = MongoClient(
                MONGO_DB_URL,
                server_api=ServerApi("1"),
                tlsCAFile=certifi.where(),
            )
            db = client[database_name]
            collection = db[collection_name]
            logging.info(f"Fetching data from MongoDB collection: {database_name}.{collection_name}")
            data = list(collection.find())
            logging.info(f"Records fetched from MongoDB: {len(data)}")

            if not data:
                available_collections = db.list_collection_names()
                raise ValueError(
                    f"No records found in MongoDB collection '{database_name}.{collection_name}'. "
                    f"Available collections in '{database_name}': {available_collections}"
                )

            df = pd.DataFrame(data)
            if "_id" in df.columns:
                df.drop("_id", axis=1, inplace=True)
            df.replace(to_replace="Infinity", value=pd.NA, inplace=True)
            logging.info(f"MongoDB dataframe shape: {df.shape}")
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_data_as_feature_store(self, df: pd.DataFrame):
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_dir
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            df.to_csv(feature_store_file_path, index=False, header=True)
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def split_data_as_train_test(self, df: pd.DataFrame):
        try:
            train_set, test_set = train_test_split(df, test_size=self.data_ingestion_config.train_test_split_ratio, random_state=42)
            logging.info(f"Splitting data into train and test sets with test size {self.data_ingestion_config.train_test_split_ratio}")
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)
            logging.info(f"Saving train set to {self.data_ingestion_config.training_file_path} and test set to {self.data_ingestion_config.testing_file_path}")

            train_set.to_csv(self.data_ingestion_config.training_file_path, index=False, header=True)
            test_set.to_csv(self.data_ingestion_config.testing_file_path, index=False, header=True)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def initiate_data_ingestion(self):
        try:
            df = self.export_collection_as_dataframe(
                collection_name=self.data_ingestion_config.collection_name,
                database_name=self.data_ingestion_config.database_name
            )
            df = self.export_data_as_feature_store(df)
            self.split_data_as_train_test(df)
            
            return DataIngestionArtifact(
                training_file_path=self.data_ingestion_config.training_file_path,
                testing_file_path=self.data_ingestion_config.testing_file_path
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    
