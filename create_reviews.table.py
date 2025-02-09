import pandas as pd
from sqlalchemy import create_engine, text, Integer, String, Date, Column, MetaData, Table, Float, UniqueConstraint
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(asctime)s - %(levelname)s - %(message)s')

# Create PostgreSQL connection
DATABASE_URL = "postgresql://YOUR USER NAME:YOUR PASSWORD@localhost:5432/postgres"
engine = create_engine(DATABASE_URL)

# File path for review_clinics_1.csv
file_path = '/Users/YOUR USER NAME/code/analisis/review_clinics_1.csv'

# Define the metadata
metadata = MetaData(schema='public')  # Ensure the table is created in the public schema

# Load data from the CSV
try:
    reviews_data = pd.read_csv(file_path)
    reviews_data.drop_duplicates(subset='review_link', inplace=True)
    logging.info(f"Loaded data from {file_path}")
except FileNotFoundError:
    logging.error(f"File not found: {file_path}")
    reviews_data = pd.DataFrame()  # Create an empty DataFrame if file not found

# Log the DataFrame
logging.info(f"DataFrame shape: {reviews_data.shape}")
logging.info(f"Sample data:\n{reviews_data.head()}")

print(reviews_data.head())
print(reviews_data.shape)

# Dynamically create the table schema based on the DataFrame
columns = []
for column_name, dtype in reviews_data.dtypes.items():
    if pd.api.types.is_integer_dtype(dtype):
        columns.append(Column(column_name, Integer))
    elif pd.api.types.is_float_dtype(dtype):
        columns.append(Column(column_name, Float))
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        columns.append(Column(column_name, Date))
    else:
        columns.append(Column(column_name, String))

# Define the clinics_usa_reviews table
reviews_table = Table('clinics_usa_reviews', metadata, *columns)

try:
    with engine.connect() as conn:
        # Drop the existing clinics_usa_reviews table if it exists
        conn.execute(text("DROP TABLE IF EXISTS clinics_usa_reviews CASCADE"))
        logging.info("Existing clinics_usa_reviews table dropped.")

        # Create the new clinics_usa_reviews table
        metadata.create_all(engine)
        logging.info("New clinics_usa_reviews table created.")

except Exception as e:
    logging.error(f"An error occurred during table creation: {str(e)}")

# Insert data into the clinics_usa_reviews table
try:
    with engine.connect() as conn:
        reviews_data.to_sql('clinics_usa_reviews', conn, if_exists='append', index=False)
        logging.info("Data inserted into clinics_usa_reviews table successfully.")

        # Verify data insertion
        result = conn.execute(text("SELECT COUNT(*) FROM public.clinics_usa_reviews"))
        row_count = result.scalar()
        logging.info(f"Number of rows in clinics_usa_reviews table: {row_count}")

except Exception as e:
    logging.error(f"An error occurred during data insertion: {str(e)}") 
