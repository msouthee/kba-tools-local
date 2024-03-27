# ----------------------------------------------------------------------------------------------------------------------
# Script Name:      KBAUtils.py
#
# Purpose:          Callable functions and variables to be used by the scripts in the KBAToolsLocal Toolbox.
# ----------------------------------------------------------------------------------------------------------------------

# Import libraries
import arcpy

# Dictionary of the Range/AOO/Habitat Maps with callable dataset/symbology name and unique datasetsourceid value
filtered_data_dict = {"ECCCRangeMaps": ["ECCC Range Map", "994"],
                      "IUCNRangeMaps": ["IUCN Range Map", "996"],
                      "ECCCCriticalHabitatMaps": ["ECCC Critical Habitat", "19"],
                      "WCSCAOOMaps": ["WCSC AOO Map", "1096"],
                      "WCSCRangeMaps": ["WCSC Range Map", "1097"],
                      "COSEWCICRangeMaps": ["COSEWIC Range Map", "1120"],
                      "COSEWICEOOMaps": ["COSEWIC EOO Map", "1121"]}


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
