#validate data using pydantic models
from pydantic import BaseModel
from pydantic import BaseModel, Field, ValidationError
import pandas as pd
import os
from datetime import datetime


class PropertyModel(BaseModel):
    Property_Title: str
    Address: str
    Market: str
    Flood: str
    Street_Address: str
    City: str
    State: str
    Zip: int
    Property_Type: str
    Highway: str
    Train: str
    Tax_Rate: float
    SQFT_Basement: int
    HTW: str
    Pool: str
    Commercial: str
    Water: str
    Sewage: str
    Year_Built: int
    SQFT_MU: int
    SQFT_Total: int
    Parking: str
    Bed: int
    Bath: int
    BasementYesNo: str
    Layout: str
    Rent_Restricted: str
    Neighborhood_Rating: int
    Latitude: float
    Longitude: float
    Subdivision: str
    School_Average: float

class LeadsModel(BaseModel):
    Reviewed_Status: str 
    Most_Recent_Status: str
    Source: str
    Occupancy: str
    Net_Yield: float
    IRR: float
    Selling_Reason: str
    Seller_Retained_Broker: str
    Final_Reviewer: str

class ValuationModel(BaseModel):
    Previous_Rent : int
    List_Price : int 
    Zestimate: int
    ARV: int 
    Expected_Rent: int 
    Rent_Zestimate: int
    Low_FMR: int 
    High_FMR: int 
    Redfin_Value: int

class HoaModel(BaseModel):
    HOA: int
    HOA_Flag: str

class RehabModel(BaseModel):
    Underwriting_Rehab: int
    Rehab_Calculation: int
    Paint: str
    Flooring_Flag: str
    Foundation_Flag: str
    Roof_Flag: str
    HVAC_Flag: str
    Kitchen_Flag: str
    Bathroom_Flag: str
    Appliances_Flag: str
    Windows_Flag: str
    Landscaping_Flag: str
    Trashout_Flag: str

class TaxesModel(BaseModel):
    Taxes: int

class DataValidation:
    def validate_dataframe(self, df, model):
        valid_rows, invalid_rows = [], []
        for i, row in df.iterrows():
            try:
                record = model(**row.to_dict())
                valid_rows.append(record.model_dump())
            except ValidationError as e:
                invalid_rows.append({
                    "row_index": i,
                    "data": row.to_dict(),
                    "errors": e.errors()
                })
        return pd.DataFrame(valid_rows), pd.DataFrame(invalid_rows)
    def runner(self):
        gold = 'src/data_lake/gold'
        model_dict = {
            "DimProperty": (pd.read_parquet(os.path.join(gold, "DimProperty.parquet")), PropertyModel),
            "DimLeads": (pd.read_parquet(os.path.join(gold, "DimLeads.parquet")), LeadsModel),
            "FactsValuation": (pd.read_parquet(os.path.join(gold, "FactsValuation.parquet")), ValuationModel),
            "DimHoa": (pd.read_parquet(os.path.join(gold, "DimHoa.parquet")), HoaModel),
            "DimRehab": (pd.read_parquet(os.path.join(gold, "DimRehab.parquet")), RehabModel),
            "DimTaxes": (pd.read_parquet(os.path.join(gold, "DimTaxes.parquet")), TaxesModel)
        }

        log_path = os.path.join(gold, "validation.log")

        # Open log file once in append mode
        with open(log_path, "a", encoding="utf-8") as log:
            log.write(f"\n\n=== Validation Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

            for name, (df, model) in model_dict.items():
                log.write(f"\n Validating {name} ...\n")

                valid_df, invalid_df = valid.validate_dataframe(df, model)

                log.write(f"Valid rows: {len(valid_df)}\n")
                log.write(f"Invalid rows: {len(invalid_df)}\n")

                # Optionally include detailed error info for invalid rows
                if not invalid_df.empty:
                    log.write("\n--- Invalid Rows Details ---\n")
                    log.write(invalid_df.to_string(index=False))
                    log.write("\n-----------------------------\n")

                log.write("\n")

        print(f"Validation complete. Logs saved to: {log_path}")

valid = DataValidation()
