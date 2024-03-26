import arcpy

# Dictionary of the Range/AOO/Habitat Maps with dataset name and datasetsourceid value
filtered_data_dict = {"ECCCRangeMaps": ["ECCC Range Map", "994"],
                  "IUCNRangeMaps": ["IUCN Range Map", "996"],
                  "ECCCCriticalHabitatMaps": ["ECCC Critical Habitat", "19"],
                  "WCSCAOOMaps": ["WCSC AOO Map", "1096"],
                  "WCSCRangeMaps": ["WCSC Range Map", "1097"],
                  "COSEWCICRangeMaps": ["COSEWIC Range Map", "1120"],
                  "COSEWICEOOMaps": ["COSEWIC EOO Map", "1121"]}


def readFilteredInputDatasetID(key_value):
    """Read the inputdatasetid values based on the datasetsourceid value for each filtered dataset"""
    datasetids = []

    # Call the search cursor based on the datasetsourceid value based in from the dictionary
    with arcpy.da.SearchCursor("InputDataset",
                               ["inputdatasetid", "datasetsourceid"],
                               "datasetsourceid = " + key_value) as inputdataset_cursor:

        for inputdataset_record in inputdataset_cursor:
            datasetids.append(inputdataset_record[0])  # Append inputdatasetid values to list

    # return the corresponding inputdatasetid values for the called dataset
    return datasetids



# # TESTING DATA LISTS AND DICTIONARIES
# filtered_data_names_values_list = [["ECCCRangeMaps", "994"],
#                                    ["IUCNRangeMaps", "996"],
#                                    ["ECCCCriticalHabitatMaps", "19"],
#                                    ["WCSCAOOMaps", "1096"],
#                                    ["WCSCRangeMaps", "1097"],
#                                    ["COSEWICRangeMaps", "1120"],
#                                    ["COSEWICEOOMaps", "1121"]]
#
# datasetid_dict = {"ECCCRangeMaps": "994",
#                   "IUCNRangeMaps": "996",
#                   "ECCCCriticalHabitatMaps": "19",
#                   "WCSCAOOMaps": "1096",
#                   "WCSCRangeMaps": "1097",
#                   "COSEWCICRangeMaps": "1120",
#                   "COSEWICEOOMaps": "1121"}
#
# print(filtered_data_list[0][1])
#
# for name, value in filtered_data_list:
#     print(name, value)
#
# print(datasetid_dict["ECCCRangeMaps"])
# print(filtered_data_dict["ECCCRangeMaps"][0])

# # Test that dictionary is working
# for key in filtered_data_dict:
#     myname = filtered_data_dict[key][0]
#     myvalue = filtered_data_dict[key][1]
#     print(myname)
#     print(myvalue)


#
# # # TESTING THE FUNCTION
# local_data_table = "C:\\GIS_Processing\\KBA\\Default.gdb\\InputDataset_Local"
# input_dataset = local_data_table
#
# # DEFINE THE FUNCTION USING LOCAL DATASET
# def readFilteredInputDatasetID(key_value):
#     """Read the inputdatasetid values based on the datasetsourceid value for each filtered dataset"""
#     datasetids = []
#     with arcpy.da.SearchCursor(input_dataset,
#                                ["inputdatasetid", "datasetsourceid"],
#                                "datasetsourceid = " + key_value) as inputdataset_cursor:
#         for inputdataset_record in inputdataset_cursor:
#             datasetids.append(inputdataset_record[0])  # Append inputdatasetid values
#     # return the corresponding inputdatasetid values for the given dataset
#     return datasetids
#
# combined_list = []
#
# # RUN THE FUNCTION USING LOCAL DATA TO CHECK THAT IT RUNS
# for key in filtered_data_dict:
#     myname = filtered_data_dict[key][0]
#     myvalue = filtered_data_dict[key][1]
#     output_values = readFilteredInputDatasetID(myvalue)
#     print("{}, DatasetIDs: {}".format(myname, output_values))
#
#     # Combine all the inputdatasetid values into one list
#     combined_list.extend((output_values))
#
# print(combined_list)