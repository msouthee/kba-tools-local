# ----------------------------------------------------------------------------------------------------------------------
# Script Name:      KBAUtils.py
#
# Purpose:          Callable functions and variables to be used by the scripts in the KBAToolsLocal Toolbox.
# ----------------------------------------------------------------------------------------------------------------------

# Import libraries
import arcpy

# VARIABLES FOR KBATOOLSLOCAL

""" Dictionary of datasets that need to be filtered out of the InputPolygons dataset. 
The dictionary has two callable values: the dataset name and the unique datasetsourceid value.  The dataset name
is used to print the name in the table of contents in ArcGIS Pro when generating the output layers.  The dataset name is
also used to display the correct symbology from the shared project symbology file that is published to the portal.
The unique datasetsourceid value is used to generate the list of inputdatasetid values in the InputDataset table that
correspond to the features for the filtered data type."""
filtered_data_dict = {"ECCCRangeMaps": ["ECCC Range Map", "994"],
                      "IUCNRangeMaps": ["IUCN Range Map", "996"],
                      "ECCCCriticalHabitatMaps": ["ECCC Critical Habitat", "19"],
                      "WCSCAOOMaps": ["WCSC AOO Map", "1096"],
                      "WCSCRangeMaps": ["WCSC Range Map", "1097"],
                      "COSEWCICRangeMaps": ["COSEWIC Range Map", "1120"],
                      "COSEWICEOOMaps": ["COSEWIC EOO Map", "1121"]}


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
