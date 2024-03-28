# ----------------------------------------------------------------------------------------------------------------------
# Script Name:      KBAUtils.py
#
# Purpose:          Callable functions and variables to be used by the scripts in the KBAToolsLocal Toolbox.
# ----------------------------------------------------------------------------------------------------------------------

# Import libraries
import arcpy

# VARIABLES FOR KBATOOLSLOCAL

""" Dictionary of datasets that need to be filtered out of the InputPolygons dataset. 
The dictionary has four callable values: the dataset name, the unique datasetsourceid value, the polygon fill symbology,
and the polygon outline symbology.  The dataset name is used to print the name in the table of contents in ArcGIS Pro 
when generating the output layers.  The unique datasetsourceid value is used to generate the list of inputdatasetid 
values in the InputDataset table that correspond to the features for the filtered data type."""

# Key : val[0] = output name, val[1] = datasetsourceid, val[2] = polygon sym fill colour, val[3] = outline sym colour
symbology_dict = {"ECCCRangeMaps":
                      ["ECCC Range Map", "994", {'RGB': [255, 0, 197, 30]}, {'RGB': [255, 0, 197, 100]}],
                  "ECCCCriticalHabitatMaps":
                      ["ECCC Critical Habitat", "19", {'RGB': [230, 152, 0, 30]}, {'RGB': [230, 152, 0, 100]}],
                  "IUCNRangeMaps":
                      ["IUCN Range Map", "996", {'RGB': [169, 0, 230, 30]}, {'RGB': [169, 0, 230, 100]}],
                  "WCSCAOOMaps":
                      ["WCSC AOO Map", "1096", {'RGB': [146, 191, 0, 30]}, {'RGB': [146, 191, 0, 100]}],
                  "WCSCRangeMaps":
                      ["WCSC Range Map", "1097", {'RGB': [164, 79, 48, 30]}, {'RGB': [164, 79, 48, 100]}],
                  "COSEWCICRangeMaps":
                      ["COSEWIC Range Map", "1120", {'RGB': [230, 0, 0, 30]}, {'RGB': [230, 0, 0, 100]}],
                  "COSEWICEOOMaps":
                      ["COSEWIC EOO Map", "1121", {'RGB': [2, 172, 158, 30]}, {'RGB': [2, 172, 158, 100]}]}

# FUNCTIONS FOR KBATOOLSLOCAL

def readFilteredInputDatasetID(key_value):
    """Return the inputdatasetid values based on the unique datasetsourceid value for each filtered dataset"""
    datasetids = []

    # Call the search cursor based on the unique datasetsourceid value (key_value) from the dictionary
    with arcpy.da.SearchCursor("InputDataset",
                               ["inputdatasetid", "datasetsourceid"],
                               "datasetsourceid = " + key_value) as inputdataset_cursor:
        for inputdataset_record in inputdataset_cursor:
            datasetids.append(inputdataset_record[0])  # Append inputdatasetid values to list

    # return the inputdatasetid values for the called dataset
    return datasetids
