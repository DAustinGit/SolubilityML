import urllib
import pandas as pd
from sqlalchemy import create_engine, text


 
def cnx():
   server = 'database-1.cp4ckgkwuxiq.eu-north-1.rds.amazonaws.com'
   username = 'admin'
   password = 'password'
   database =  'solubility_training'
   params = urllib.parse.quote_plus(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
   )
   connection_url = f"mssql+pyodbc:///?odbc_connect={params}"
   
   return connection_url

def fetch_data(column: str, SMILES: str,  table: str) -> pd.DataFrame:    
    url = cnx()
    try:
        engine = create_engine(url)    
        query = text(f"SELECT * FROM {table} WHERE {column} COLLATE Latin1_General_CS_AS = '{SMILES}';")
        print (query)
        with engine.connect() as connection:
            print("Successfully connected to AWS SQL Server via SQLAlchemy!")
            df = pd.read_sql(query, con=connection)
            if df.empty:
                return None
            else:
                return df
            
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return pd.DataFrame()

def push_data (data: pd.DataFrame, table: str):
    url = cnx()
    try:
        engine = create_engine(url, fast_executemany=True)  

        # 2. engine.begin() automatically handles the BEGIN and COMMIT steps
        with engine.connect() as connection:
            print("Successfully connected to AWS SQL Server via SQLAlchemy!")
            
            # 3. Explicitly state your schema if using a non-default one (e.g., 'dbo')
            data.to_sql(
                name=table, 
                con=connection, 
                if_exists='append', 
                index=False,
                schema='dbo'  # Change 'dbo' if your AWS SQL Server uses a different schema
            )
            connection.comit()
                
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return e


#print(fetch_data(entry= "CC(Cl)(Cl)ClC", column = "SMILES", database='solubility_training', table='mol_properties'))