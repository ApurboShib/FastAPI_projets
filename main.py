from fastapi import FastAPI
import json



app = FastAPI()

## define a halper function to load the data.

def load_data():
    with open ('patients.json', 'r') as f:
        data = json.load(f)

    return data


@app.get("/")
def read_root():
    return {"messege": "Patients Managements System API"}
@app.get("/about")
def about():
    return {"messege" : "A fully functional API to manage your patients records"}



## create a view endpoints.

@app.get("/view")
def view():
    data = load_data()
    return data


## create an endpoints to see specific patients info.
## dynamic routes (parramsa)
@app.get("/patients/{patients_id}")
def view_patients(patients_id: str):
    ## load the full data.
    data = load_data()
    ## now we write the conditions.
    if patients_id in data:
        return  data[patients_id]
    return {"error" : "The patients is not found here.."}
