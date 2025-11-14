from extract import *
from transform import *
#from load import *
from data_validation import *
#list requirements
with open("requirements.txt", "r") as file:
    lines = file.read()

print("Collect these python libraries", "\n", lines)  # Each line is an element in the list

#----------------------
#---------Extract------
#----------------------
print("Extracting, validating json data.....")
extractor = extract("data/fake_property_data_new.json", "src/data_lake/bronze/fake_property_data_new.csv") #provide source file, raw folder location
extractor.load_json()
extractor.json_to_csv()
print("Extraction Done....... Check File in src/data_lake_bronze")

#---------------------
#-- Transform --------
#---------------------
print("Cleaning Data!..... Wait")
transform = transform("src/data_lake/bronze/fake_property_data_new.csv", #bronze layer
                      "src/data_lake/silver/fake_property_data_new.csv", #silver layer
                      "src/data_lake/gold")               #gold layer
transform.clean()
transform.transform()
print("Cleaning and Transformation is done..... Check data_lake/silver and data_lake/gold")

#-----------------------
#--- Validating --------
#-----------------------
print("Validating Data.... Wait")
valid = DataValidation()
print("Logging details in src/data_lake/gold/validation.log....")
valid.runner()
print("Logged... Check the file")

#------------------------
#---- Loading -----------
#------------------------
