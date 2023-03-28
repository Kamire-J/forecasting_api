import sqlite3

from config import settings
from data import SQLRepository
from fastapi import FastAPI
from model import GarchModel
from pydantic import BaseModel


# Creating the fitin class
class FitIn(BaseModel):
    ticker:str
    use_new_data:bool
    n_observations:int
    p: int
    q: int

# Creating fitout class
class FitOut(FitIn):
    success: bool
    message: str


# Helper function to aid in building the model by connecting database
def build_model(ticker, use_new_data):
    # Create DB connection
    connection = sqlite3.connect(settings.db_name)

    # Create SQLRepository
    repo = SQLRepository(connection=connection)

    # create model
    model = GarchModel(ticker=ticker, use_new_data=use_new_data, repo=repo)

    # Return model
    return model


# Define fastapi app
app = FastAPI()

# Test api with hello world path
@app.get("/hello", status_code=200)
def hello():
    """Return dictionary with greeting message."""
    return {"message":"Hello, Bomin!"}


#"/fit" path, 200 status
@app.post("/fit", status_code=200, response_model=FitOut)
def fit_model(request: FitIn):
    """Fit model, return confirmation message.

    Parameters
    ----------
    request : FitIn

    Returns
    ------
    dict
        Must conform to `FitOut` class
    """
    # Response dictionary from request
    response = request.dict() 

    # Try and block handle to deal with exceptions
    try:
        model = build_model(ticker=request.ticker, use_new_data=request.use_new_data)
        
        model.wrangle_data(n_observations=request.n_observations)

        filename = model.dump() # saving model

        response["success"] = True # success key

        response["message"] = f"Trained and saved '{filename}'" # message

    except Exception as e:
        response["success"] = False

        response["message"] = str(e)


    return response



    
