# read json file from data then load it into raw folder as csv
import json

class extract:
    import pandas as pd
    def __init__(self, json_file_path, csv_output_path):
        self.json_file_path = json_file_path
        self.csv_output_path = csv_output_path
    # validate json
    def load_json(self):
        #print(f"Loading JSON file from {self.json_file_path}")
        try:
            with open(self.json_file_path, "r") as file:
                data = json.load(file)
                print("JSON is valid!")
        except json.JSONDecodeError as e:
            print("Invalid JSON! Validate the file on https://jsonlint.com/ and make proper changes")
            print(f"Error: {e}")
        return data
    #load json and convert to csv
    def json_to_csv(self):
        data = self.load_json()
        df = self.pd.json_normalize(data)
        df = df.explode('Valuation')
        df = df.explode('HOA')
        df = df.explode('Rehab')
        df = df.reset_index(drop=True)
        df.to_csv(self.csv_output_path, index=False)
        print(f"Data successfully extracted to {self.csv_output_path}")