import pandas as pd
import ast
from pandas import json_normalize
import os

class transform:
    def __init__(self, bronze_csv, silver_csv, gold_parquet):
        self.bronze_csv = bronze_csv
        self.silver_csv = silver_csv
        self.gold_parquet = gold_parquet

    def clean(self):
        #read csv file
        with open(self.bronze_csv, "r") as csv_file:
            df = pd.read_csv(csv_file, low_memory=False)
        #transform Valuation
        df['Valuation'] = df['Valuation'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.strip().startswith('{') else x)
        col_expanded = json_normalize(df['Valuation'])
        df_final = pd.concat([df.drop(columns=['Valuation']), col_expanded], axis=1)
        df = df_final
        #transform HOA
        df['HOA'] = df['HOA'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.strip().startswith('{') else x)
        col_expanded = json_normalize(df['HOA'])
        df_final = pd.concat([df.drop(columns=['HOA']), col_expanded], axis=1)
        df = df_final
        #transform Rehab
        df['Rehab'] = df['Rehab'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.strip().startswith('{') else x)
        col_expanded = json_normalize(df['Rehab'])
        df_final = pd.concat([df.drop(columns=['Rehab']), col_expanded], axis=1)
        df = df_final
        # find null, NaN, missing values
        false_value = {}
        for col in df.columns:
            total_missing = (
                df[col].isna().sum() +
                df[col].isnull().sum()+
                df[col].astype(str).str.strip().eq('').sum() +
                df[col].astype(str).str.contains('Null').sum()
            )
            false_value[col] = total_missing
        #print(false_value.items())
        #return columns with missing values and store it in list
        non_zero_cols = [k for k, v in false_value.items() if v != 0]
        #print(non_zero_cols)
        print("We have " + str(len(non_zero_cols)) + " columns having null, NaN, missing values")
        #40 columns have missing values, null or NaN or empty strings
        #handle null, NaN, missing values
        for col in non_zero_cols:
            if (col in ['Previous_Rent', 'ARV', 'Rent_Zestimate', 'Low_FMR', 'Redfin_Value', 'Zestimate', 'Expected_Rent', 'High_FMR', 'HOA', 'List_Price']):
            # These are numerical columns we can replace missing/null value with average/mean but since requirement is not clear I'm moving with 0
                df[col] = df[col].fillna(0)
            else:
                if df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col]):
                    if (df[col].str.strip().eq('').any() or df[col].isin(['NaN', 'nan', 'None', 'N/A', 'Null', '', ' ']).any()):
                        df[col] = df[col].replace(['NaN', 'nan', 'None', 'N/A', 'Null', '', ' '], 'No Data')
                    else:
                        df[col] = df[col].fillna('No Data')
                elif pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                #no bool, date, timestamp columns
        #   Perform column level transformation
        #   col SQFT_Total has some value with string 
        #   col ARV, Redfin_Value, Zestimate has some value having ',' in field converted it into string to parse incorrect json
        #   col Bed has value in str format convert it into raw numeric format
        #   col Reviewed_Status has Neww which I think incorrect form of New

        #   col SQFT_Total has some value with string 
        str_value = df['SQFT_Total'].apply(lambda x: isinstance(x, str))
        df.loc[str_value, 'SQFT_Total'] = (
            df.loc[str_value, 'SQFT_Total']
            .str.extract(r'(\d+\.?\d*)')[0]
            .astype(int)
        )

        #   col ARV, Redfin_Value, Zestimate has some value having ',' in field converted it into string to parse incorrect json 
        col_to_manipulate = ['ARV', 'Redfin_Value', 'Zestimate', 'List_Price']
        for col in col_to_manipulate:
            df[col] = df[col].astype(str).str.replace(',', '', regex=False)

        #   col Bed has value in str format convert it into raw numeric format
        df['Bed'] = df['Bed'].astype(str).str.replace('Four', '4', regex=False)
        df['Bed'] = df['Bed'].astype(str).str.replace('Five', '5', regex=False)


        #   col Reviewed_Status has Neww which I think incorrect form of New
        df['Reviewed_Status'] = df['Reviewed_Status'].astype(str).str.replace('Neww', 'New', regex=False)
        #write cleaned data to silver layer
        df.to_csv(self.silver_csv, index=False)
        return df
    
    def transform(self):
    # conceptual data model
        df = transform.clean(self)

        # property
        columns_prop = ["Property_Title","Address","Market","Flood","Street_Address","City","State","Zip",
                        "Property_Type","Highway","Train","Tax_Rate","SQFT_Basement","HTW","Pool","Commercial",
                        "Water","Sewage","Year_Built","SQFT_MU","SQFT_Total","Parking","Bed","Bath",
                        "BasementYesNo","Layout","Rent_Restricted","Neighborhood_Rating","Latitude","Longitude",
                        "Subdivision","School_Average"]
        DimProperty = df[columns_prop]

        # Leads
        columns_leads = ['Reviewed_Status','Most_Recent_Status','Source','Occupancy','Net_Yield','IRR',
                         'Selling_Reason','Seller_Retained_Broker','Final_Reviewer']
        DimLeads = df[columns_leads]

        # Valuation
        columns_val = ['Previous_Rent','List_Price','Zestimate','ARV','Expected_Rent','Rent_Zestimate',
                       'Low_FMR','High_FMR','Redfin_Value']
        FactsValuation = df[columns_val]

        # HOA
        columns_hoa = ['HOA','HOA_Flag']
        DimHoa = df[columns_hoa]

        # Rehab
        columns_rehab = ["Underwriting_Rehab","Rehab_Calculation","Paint","Flooring_Flag","Foundation_Flag",
                         "Roof_Flag","HVAC_Flag","Kitchen_Flag","Bathroom_Flag","Appliances_Flag",
                         "Windows_Flag","Landscaping_Flag","Trashout_Flag"]
        DimRehab = df[columns_rehab]

        # Taxes
        columns_taxes = ['Taxes']
        DimTaxes = df[columns_taxes]

        # ---------------------------------------------------------
        # Write each table to a Parquet file in gold directory
        # ---------------------------------------------------------
        gold_dir = self.gold_parquet
        os.makedirs(gold_dir, exist_ok=True)

        tables = {
            "DimProperty": DimProperty,
            "DimLeads": DimLeads,
            "FactsValuation": FactsValuation,
            "DimHoa": DimHoa,
            "DimRehab": DimRehab,
            "DimTaxes": DimTaxes
        }

        for name, df_table in tables.items():
            gold_path = os.path.join(gold_dir, f"{name}.parquet")
            df_table.to_parquet(gold_path, index=False)
            print(f"{name} written to {gold_path}")