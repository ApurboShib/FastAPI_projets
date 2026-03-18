# here we building our ML model .. 

from fastapi import FastAPI, Path, HTTPException, Query
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import pickle 
import pandas as pd


# Step - 01 : import the ML model here.
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# create a fastapi object.
app = FastAPI()


# build a pydantic model to validate the incoming data.

class UserInput(BaseModel):
    age : Annotated[int, Field(..., gt=0, description="Age of the user.")]
    weight : Annotated[float, Field(..., gt=0, lt=120, description="Weight of the user.")]
    height : Annotated[float, Field(..., gt=0,lt = 2.5,  description="height of the user.")]
    income_lpa : Annotated[Literal['Below 3 LPA', '3-6 LPA', '6-10 LPA', '10-15 LPA', 'Above 15 LPA'], Field(description="An anual income of the user")]
    smoking : Annotated[bool, Field(...,description='is user do smoke?' )]
    city : Annotated[str, Field(..., description="the location of the user")]
    occupations : Annotated[Literal['Self-Employed', 'Retired', 'Student', 'Employed', 'Unemployed'], Field(description="Occupations of the user.")]

    # now we are calculating the computed fields
    @computed_field
    @property
    def bmi(self)->float:
        return self.weight / (self.height ** 2)

    @computed_field
    @property
    def life_cycle(self) -> str:
        if self.smoking and self.bmi >= 30:
            return "High Risk"
        elif self.smoking and self.bmi >= 25:
            return "Medium Risk"
        else:
            return "Low Risk"

    @computed_field
    @property
    def age_avarage(self)-> str:
        if self.age < 18:
            return 'child'
        elif 18 <= self.age <= 65:
            return 'adult'
        else:
            return 'senior'

    @computed_field
    @property
    def city_tier(self)-> int:
        tire1_city = ['Dhaka', 'Chittagong']
        tier2_city = ['Sylhet', 'Rajshahi', 'Khulna']
        if self.city in tire1_city:
            return 1
        elif self.city in tier2_city:
            return 2
        return 3


# now create an endpoints

@app.post('/predict')
def predict_prmium(data : UserInput):

    input_df = pd.DataFrame([{
        'bmi': data.bmi,
        "age_group": data.age_avarage,
        "life_cycle": data.life_cycle,
        "city_tier": data.city_tier,
        "income_lpa": data.income_lpa,
        "occupations": data.occupations
    }]).astype(object)
    
    try:
        prediction = model.predict(input_df)[0]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return JSONResponse(status_code=200, content={"prediction-catagory": str(prediction)})
