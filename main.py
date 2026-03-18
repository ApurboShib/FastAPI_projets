from fastapi import FastAPI, Path, HTTPException, Query
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional

app = FastAPI()

## here we create a pydantic model mainly a clsaa jeta directly BaseModel ke inherate korbe.
# step-7: build a pydantic model to validate the data.
class Patient(BaseModel):
    ## we need to write the all required fields.
    id: Annotated[str, Field(..., description = "ID of the patients", example = ["P001"])]
    name: Annotated[str, Field(..., description = "Name of the patients", example = "Abdul Mia")]
    city: Annotated[str, Field(..., description = "City where is the patients Living..", example= "Dhaka")]
    age: Annotated[int, Field(...,gt = 0, lt=120, description = "Age of the patients", example = 22)]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description="gender of the patients")]
    height: Annotated[float, Field(..., gt=0, description="height of the patients")]
    weight: Annotated[float, Field(..., gt=10, lt=200, description="Weight of the patients in Kgs")]
## here we write the computed_fields stuff..
## here we calculated the bmi using this feilds..
# step - 9 : to calculate the bmi
@computed_field
@property
def bmi(self)-> float:
    bmi = round(self.weight/(self.height**2),2)
    return bmi



# step-13 :  build an another pydantic model for update.

class Update_patient(BaseModel):
    id:Annotated[Optional[str], Field(default=None)]
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female', 'others']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

## now after calculating the bmi successfully now we need add a  verdict (overwight, underweight, normal..) 
# step-10 : to decide the verdict
@computed_field
@property
def verdict(self)->str:
    if self.bmi < 18.5:
        return {"messege" : "Under-weight"}
    elif self.bmi < 25:
        return {"messege" : "Normal"}
    elif self.bmi < 30:
        return {"messege" : "Normal"}
     
    return {"messege" : "Over-Weight"}

## define a halper function to load the data.
# step -1 : here we load the full data
def load_data():
    with open ('patients.json', 'r') as f:
        data = json.load(f)

    return data
# step- 11 : after getting the data in dictonary formated we need to convert into JSON format, with write(W) method
def save_data(data):
    with open ('patients.json', 'w') as f:
        json.dump(data, f)
# step-2 : we add a root endpoints
@app.get("/")
def read_root():
    return {"messege": "Patients Managements System API"}

# step -3 : we add a description endpoints.
@app.get("/about")
def about():
    return {"messege" : "A fully functional API to manage your patients records"}



## create a view endpoints.
# step - 4 : we add view endpoints to see the data
@app.get("/view")
def view():
    data = load_data()
    return data

# step-05 : create endpoints to see the data dynamically.
## create an endpoints to see specific patients info.
## dynamic routes (parrams)
@app.get("/patients/{patients_id}")
def view_patients(patients_id: str = Path(..., description = "ID of the patients of the DB", examples = "P001")):
    ## load the full data.
    data = load_data()
    ## now we write the conditions.
    if patients_id in data:
        return  data[patients_id]
    raise HTTPException(status_code = 404, detail = "Patients is not found!")


# step-6 : add the endpoints to see the information by sorted order
## create a new endpoints to see informattions in sorted manner.

@app.get("/sort")
def sort_patients(sort_by:str = Query(..., description = "sort on the basis of height, weight and BMI"), order :str = Query('asc', description = "sort in the ASC or DESC order")):
    ## the error handeling part.. (for which case it might gives error).
    valid_feilds  = ['height', 'weight', 'bmi']
    valid_order = ['ASC', 'DESC']
    if sort_by not in valid_feilds:
        raise HTTPException(status_code = 400, detail = f'invalid feilds selected from {valid_feilds}')
    if order not in valid_order:
        raise HTTPException(status_code = 400, detail = 'Invalid order selected please select ASC or DESC order')
## first of all we retieved the data first.
    data = load_data()

    sorted_ordder = True if order == 'ASC' else False

    sorted_data = sorted(data.values(), key = lambda x : x.get(sort_by, 0), reverse = (sorted_ordder))
    return sorted_data

# step-12 : now make change the patients informations.
## now we create a endpoints to post the changes 
## amra pydantic model thele data ta niye ashtechi tai amader data-type hobe (Patient) jeta ekta pydantic class

@app.post("/create")
def create_patients(patient : Patient):
    # load existing data.
    data = load_data()

    # to check the patients id is already exist?
    if patient.id in data:
        raise HTTPException(status_code = 400, detail = "the is patients is already exist in the system.")

    # if patients new add them into the database
    # patient.model_dump() convert into the dictonariy from the pydantic data
    data[patient.id] = patient.model_dump(exclude=["id"])
    # now we need to save into the JSON file
    save_data(data)
    return JSONResponse(status_code = 201, content = {"messege" : "Patients Created Successfully!"})



# step-14 : build the endpoint for uodate.

@app.put('/edit')
def update_patient_info(patient_id:str, update_patient:Update_patient):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code = 404, detail="Patient not found!")
    existing_patients_info = data[patient_id]
    # now the existing_patients_info in a object so futher operation er jonno eitake dictonary te convert kore nibo.
    # exclude_unset= True (eita na likhle amra full dictonary paitam but eita lekhar por just change data gula ashbe)
    update_data = update_patient.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        existing_patients_info[key] = value
        
    # this field was missing but it's required feilds. so we need to update this things fast.
    existing_patients_info['id'] = patient_id
    # now need to convert this onto the pydantic object.
    parient_pydantic_object = Patient(**existing_patients_info)
    # now pydantic object -> dict and store the (existing_patients_info)
    existing_patients_info = parient_pydantic_object.model_dump(exclude={'id'})

    # now update the existing data to new data.
    data[patient_id] = existing_patients_info

    # now save the informations
    save_data(data)

    return JSONResponse(status_code=200, content={'message' : 'Patients info is updated '})



