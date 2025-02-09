import pandas as pd
from sqlalchemy import create_engine, text, Integer, String, Date, Column, MetaData, Table, Float
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(asctime)s - %(levelname)s - %(message)s')

# Create PostgreSQL connection
DATABASE_URL = "postgresql://YOUR USER NAME:YOUR PASSWORD@localhost:5432/postgres"
engine = create_engine(DATABASE_URL)

# Define the file path
file_path = '/Users/YOUR USER NAME/code/analisis/clinics_usa.csv'  # Use the absolute path to the CSV file

# Load data from CSV
try:
    clinics_data = pd.read_csv(file_path)
except FileNotFoundError:
    logging.error(f"File not found: {file_path}")
    exit()

# Filter rows where 'keyword_input' is not null
clinics_data = clinics_data[clinics_data['keyword_input'].notnull()]

# Log the first few rows of the DataFrame to verify the data
logging.info(f"DataFrame shape after filtering: {clinics_data.shape}")
logging.info(f"Sample data:\n{clinics_data.head()}")

# Define the metadata
metadata = MetaData(schema='public')  # Ensure the table is created in the public schema

# Dynamically create the table schema based on the DataFrame
columns = []
for column_name, dtype in clinics_data.dtypes.items():
    if pd.api.types.is_integer_dtype(dtype):
        columns.append(Column(column_name, Integer))
    elif pd.api.types.is_float_dtype(dtype):
        columns.append(Column(column_name, Float))
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        columns.append(Column(column_name, Date))
    else:
        columns.append(Column(column_name, String))

# Add a primary key column if needed
columns.insert(0, Column('clinic_id', Integer, primary_key=True, autoincrement=True))

# Define the clinics_usa table
clinics_table = Table('clinics_usa', metadata, *columns)

try:
    with engine.connect() as conn:
        # Drop the existing clinics_usa table if it exists
        conn.execute(text("DROP TABLE IF EXISTS clinics_usa"))
        logging.info("Existing clinics_usa table dropped.")

        # Create the new clinics_usa table
        metadata.create_all(engine)
        logging.info("New clinics_usa table created.")

except Exception as e:
    logging.error(f"An error occurred during table creation: {str(e)}")

# Insert data into the clinics_usa table
try:
    with engine.connect() as conn:
        clinics_data.to_sql('clinics_usa', conn, if_exists='append', index=False)
        logging.info("Data inserted into clinics_usa table successfully.")

        # Verify data insertion
        result = conn.execute(text("SELECT COUNT(*) FROM public.clinics_usa"))
        row_count = result.scalar()
        logging.info(f"Number of rows in clinics_usa table: {row_count}")

except Exception as e:
    logging.error(f"An error occurred during data insertion: {str(e)}") 
