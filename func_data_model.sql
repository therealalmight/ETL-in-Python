-- functional data model
USE home_db;

-- CREATE TABLE DimProperty, DimLeads, FactsValuation, DimHoa, DimRehab, DimTaxes

-- DimProperty
CREATE TABLE DimProperty (
    Property_ID           INT AUTO_INCREMENT PRIMARY KEY,
    Property_Title        VARCHAR(255),
    Address               VARCHAR(255),
    Market                VARCHAR(100),
    Flood                 VARCHAR(50),
    Street_Address        VARCHAR(255),
    City                  VARCHAR(100),
    State                 VARCHAR(50),
    Zip                   INT,
    Property_Type         VARCHAR(100),
    Highway               VARCHAR(100),
    Train                 VARCHAR(100),
    Tax_Rate              FLOAT,
    SQFT_Basement         INT,
    HTW                   VARCHAR(50),
    Pool                  VARCHAR(50),
    Commercial            VARCHAR(50),
    Water                 VARCHAR(50),
    Sewage                VARCHAR(50),
    Year_Built            INT,
    SQFT_MU               INT,
    SQFT_Total            INT,
    Parking               VARCHAR(50),
    Bed                   INT,
    Bath                  INT,
    BasementYesNo         VARCHAR(10),
    Layout                VARCHAR(100),
    Rent_Restricted       VARCHAR(10),
    Neighborhood_Rating   INT,
    Latitude              FLOAT,
    Longitude             FLOAT,
    Subdivision           VARCHAR(100),
    School_Average        FLOAT,
    Created_At            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DimLeads
CREATE TABLE DimLeads (
    Lead_ID                 INT AUTO_INCREMENT PRIMARY KEY,
    Reviewed_Status          VARCHAR(100),
    Most_Recent_Status       VARCHAR(100),
    Source                   VARCHAR(100),
    Occupancy                VARCHAR(50),
    Net_Yield                FLOAT,
    IRR                      FLOAT,
    Selling_Reason           VARCHAR(255),
    Seller_Retained_Broker   VARCHAR(100),
    Final_Reviewer           VARCHAR(100),
    Created_At               TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DimHoa
CREATE TABLE DimHoa (
    HOA_ID INT AUTO_INCREMENT PRIMARY KEY,
    HOA INT,
    HOA_Flag VARCHAR(255),
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DimRehab
CREATE TABLE DimRehab (
    Rehab_ID               INT AUTO_INCREMENT PRIMARY KEY,
    Underwriting_Rehab      INT,
    Rehab_Calculation       INT,
    Paint                   VARCHAR(50),
    Flooring_Flag           VARCHAR(50),
    Foundation_Flag         VARCHAR(50),
    Roof_Flag               VARCHAR(50),
    HVAC_Flag               VARCHAR(50),
    Kitchen_Flag            VARCHAR(50),
    Bathroom_Flag           VARCHAR(50),
    Appliances_Flag         VARCHAR(50),
    Windows_Flag            VARCHAR(50),
    Landscaping_Flag        VARCHAR(50),
    Trashout_Flag           VARCHAR(50),
    Created_At              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DimTaxes
CREATE TABLE DimTaxes (
    Taxes_ID INT AUTO_INCREMENT PRIMARY KEY,
    Taxes INT,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FactsValuation

CREATE TABLE FactsValuation (
    Valuation_ID        INT AUTO_INCREMENT PRIMARY KEY,
    Property_ID         INT,
    Lead_ID             INT,
    HOA_ID              INT,
    Rehab_ID            INT,
    Taxes_ID            INT,
    Previous_Rent       INT,
    List_Price          INT,
    Zestimate           INT,
    ARV                 INT,
    Expected_Rent       INT,
    Rent_Zestimate      INT,
    Low_FMR             INT,
    High_FMR            INT,
    Redfin_Value        INT,
    Created_At          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    CONSTRAINT fk_property FOREIGN KEY (Property_ID) REFERENCES DimProperty(Property_ID),
    CONSTRAINT fk_lead FOREIGN KEY (Lead_ID) REFERENCES DimLeads(Lead_ID),
    CONSTRAINT fk_hoa FOREIGN KEY (HOA_ID) REFERENCES DimHoa(HOA_ID),
    CONSTRAINT fk_rehab FOREIGN KEY (Rehab_ID) REFERENCES DimRehab(Rehab_ID),
    CONSTRAINT fk_taxes FOREIGN KEY (Taxes_ID) REFERENCES DimTaxes(Taxes_ID)
);