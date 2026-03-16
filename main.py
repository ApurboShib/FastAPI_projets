from fastapi import FastAPI, Path, HTTPException, Query
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
def view_patients(patients_id: str = Path(..., description = "ID of the patients of the DB", example = "P001")):
    ## load the full data.
    data = load_data()
    ## now we write the conditions.
    if patients_id in data:
        return  data[patients_id]
    raise HTTPException(status_code = 404, detail = "Patients is not found!")



## create a new endpoints to see informattions in sorted manner.

@app.get("/sort")
def sort_patients(sort_by:str = Query(..., description = "sort on the basis of height, weight and BMI"), order :str = Query('asc', description = "sort in the ASC or DESC order")):
    ## the error handeling part.. (for which case it might gives error).
    valid_feilds  = ['height', 'weight', 'bmi']
    valid_order = ['ASE', 'DESC']
    if sort_by not in valid_feilds:
        raise HTTPException(status_code = 400, detail = f'invalid feilds selected from {valid_feilds}')
    if order not in valid_order:
        raise HTTPException(status_code = 400, detail = 'Invalid order selected please select ASC or DESC order')
## first of all we retieved the data first.
    data = load_data()

    sorted_ordder = True if order == 'ASC' else False

    sorted_data = sorted(data.values(), key = lambda x : x.get(sort_by, 0), reverse = (sorted_ordder))
    return sorted_data
