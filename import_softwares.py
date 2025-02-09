import pandas as pd
import psycopg2
from sqlalchemy import create_engine

def import_softwares():
    try:
        # Read the CSV file
        df = pd.read_csv('softwares.csv')
        
        # Create database connection
        engine = create_engine('postgresql://YOUR USER NAME:YOUR PASSWORD@localhost:5432/postgres')
        
        # Create table and import data
        df.to_sql('softwares', 
                  engine, 
                  if_exists='replace',  # Replace if table exists
                  index=False)
        
        # Verify the import
        conn = psycopg2.connect(
            dbname='postgres',
            user='YOUR USER NAME',
            password='YOUR PASSWORD',
            host='localhost',
            port='5432'
        )
        
        cur = conn.cursor()
        
        # Get row count
        cur.execute("SELECT COUNT(*) FROM softwares")
        count = cur.fetchone()[0]
        
        # Get column names
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'softwares'
        """)
        columns = [col[0] for col in cur.fetchall()]
        
        print(f"\nSuccessfully created softwares table!")
        print(f"Imported {count} rows")
        print(f"Columns: {', '.join(columns)}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import_softwares() 
