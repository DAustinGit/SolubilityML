import urllib
import pandas as pd
from sqlalchemy import create_engine, text
from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski


df = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/data/refs/heads/master/delaney.csv')
#print (df.head())

def push_data(database: str, table: str, dataframe: pd.DataFrame):
    server = 'database-1.cp4ckgkwuxiq.eu-north-1.rds.amazonaws.com'
    username = 'admin'
    password = 'Wireless1996!'  # <-- Replace with your actual password
    
    # 1. Safely URL-encode the pyodbc connection string parameters
    # This prevents errors if your password contains special characters (like @, #, or :)
    params = urllib.parse.quote_plus(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )
    
    # 2. Build the SQLAlchemy connection URL
    connection_url = f"mssql+pyodbc:///?odbc_connect={params}"
    
    try:
        # 3. Create the SQLAlchemy engine
        engine = create_engine(connection_url)
        
        # 4. Wrap the text-based query in SQLAlchemy's text() object
        # This is mandatory in modern SQLAlchemy 2.0+
        query = text(f"SELECT * FROM {table};")
        
        # 5. Connect and read into pandas
        with engine.connect() as connection:
            print("Successfully connected to AWS SQL Server via SQLAlchemy!")
            df.to_sql(name=table, con=engine, if_exists='replace', index=False)
            return df
            
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return pd.DataFrame()

def calculate_aromatic_proportion(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None  # Handle invalid SMILES strings safely
    
    # Count the number of aromatic atoms
    aromatic_atoms = sum(1 for atom in mol.GetAtoms() if atom.GetIsAromatic())
    
    # Count the number of heavy (non-hydrogen) atoms
    heavy_atoms = Descriptors.HeavyAtomCount(mol)
    
    if heavy_atoms == 0:
        return 0.0
        
    return aromatic_atoms / heavy_atoms


df = df.drop('ESOL predicted log(solubility:mol/L)',axis=1)
df = df.rename(columns={'Compound ID':'Compound_ID'})
df['num_Rotatable_Bonds'] = df['SMILES'].apply(lambda x: Lipinski.NumRotatableBonds(Chem.MolFromSmiles(x)) if pd.notnull else None)
df['num_H_Bond_Acceptors'] = df['SMILES'].apply(lambda x: Lipinski.NumHAcceptors(Chem.MolFromSmiles(x)) if pd.notnull else None)
df['num_H_Bond_Doners'] = df['SMILES'].apply(lambda x: Lipinski.NumHDonors(Chem.MolFromSmiles(x)) if pd.notnull else None)
df['num_Nitrogen_Oxygen'] = df['SMILES'].apply(lambda x: Lipinski.NOCount(Chem.MolFromSmiles(x)) if pd.notnull else None)
df['mol_weight'] = df['SMILES'].apply(lambda x: Descriptors.MolWt(Chem.MolFromSmiles(x)) if pd.notnull else None)
df['LogP'] = df['SMILES'].apply(lambda x: Descriptors.MolLogP(Chem.MolFromSmiles(x)) if pd.notnull else None)
df['aromatic proportion'] = df['SMILES'].apply(calculate_aromatic_proportion)
df['TPSA'] = df['SMILES'].apply(lambda x: Descriptors.TPSA(Chem.MolFromSmiles(x), includeSandP=True) if pd.notnull else None)

print (df)
push_data(database='solubility_training', table='mol_properties_exp', dataframe=df)
df.to_csv('mol_properties.csv', index=False)