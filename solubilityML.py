import urllib
import pandas as pd
from sqlalchemy import create_engine, text
import joblib


#import scikit learn modules
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn import linear_model
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import StackingRegressor
from sklearn.model_selection import GridSearchCV



def fetch_data(database: str, table: str) -> pd.DataFrame:
    server = 'database-1.cp4ckgkwuxiq.eu-north-1.rds.amazonaws.com'
    username = 'admin'
    password = 'password'  # <-- Replace with your actual password
    
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
            df = pd.read_sql(query, con=connection)
            return df
            
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return pd.DataFrame()
df = fetch_data(database='solubility_training', table='mol_properties')

y = df['measured log(solubility:mol/L)']   # Y is feature used for training
x = df.drop(['measured log(solubility:mol/L)', 'Compound ID', 'SMILES'], axis=1)     #X is the feature we are predicting drop logS and axis = 1 --> work in coluns

x_train, x_test, y_train, y_test = train_test_split (x, y, test_size= 0.2, random_state = 100) #splits the data for train and test sets testing set is 20% of data
print (x_train)

base_learners = [
    ('lr', linear_model.BayesianRidge()),
    ('knn', KNeighborsRegressor())
]

stacking_ensemble = StackingRegressor(
    estimators=base_learners,
    final_estimator=RidgeCV(),
    cv = 3
                                        
)

pipeline = Pipeline([
  ('scaler', StandardScaler()),
  ('stack', stacking_ensemble)  
])

param_grid = {

    
    # Tune the KNN model hidden inside the stack step
    'stack__knn__n_neighbors': [9, 11, 15, 21],
    
    # Tune the weights parameter of the KNN model inside the stack step
    'stack__knn__weights': ['uniform']
}
grid_search = GridSearchCV(
    estimator=pipeline,
    param_grid=param_grid,
    cv=5,
    scoring='r2',
    n_jobs=-1
)

grid_search.fit(x_train, y_train)

# 6. Output the results
print(f"Best Parameters: {grid_search.best_params_}")
print(f"Best CV R² Score: {grid_search.best_score_:.4f}")
print(f"Test Set R² Score: {grid_search.score(x_test, y_test):.4f}")
print(df.head())
joblib.dump(grid_search, "solubilityML_grid_search_3")