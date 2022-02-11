# # Species level list based on the Canadian national name level [ca_nname_level] field
# sp_level_list = ["species",
#                  "subspecies",
#                  "population",
#                  "variety"]

# # Create a search cursor to filter the values to show only full species names
# biotics_species = arcpy.da.SearchCursor("BIOTICS_ELEMENT_NATIONAL",
#                                         "national_scientific_name",
#                                         "ca_nname_level = 'Species'")


# # Create a search cursor to filter the values to show only full species names
# biotics_infraspecies = arcpy.da.SearchCursor("BIOTICS_ELEMENT_NATIONAL",
#                                              "national_scientific_name",
#                                              "ca_nname_level != 'Species'")

# # From FullSpeciesScopingTool.py ...........................................................................

# # Select the record in BIOTICS table based on the user-specified species
# biotics_record = arcpy.management.SelectLayerByAttribute(biotics_table,
#                                                          "NEW_SELECTION",
#                                                          sql)
#
# # Logic to check that only one record is selected in the initial query
# biotics_count = int(arcpy.GetCount_management(biotics_record).getOutput(0))
#
# # if count = 0, throw error using custom exception
# if biotics_count == 0:
#     arcpy.AddWarning("No record selected. Please select a record using the dropdown.")
#     raise KBAExceptions.BioticsError
#
# # if count > 1, throw error using custom exception
# elif biotics_count > 1:
#     arcpy.AddWarning("More than one record selected. Please select only one record.")
#     raise KBAExceptions.BioticsError
#
# else:
#     pass

# # Create the group layer by calling the create_group_lyr_scoping() function from the KBAFunctions file
# species_group_lyr = KBAFunctions.create_species_group_lyr_scoping(m,
#                                                                   new_group_lyr,
#                                                                   common_name,
#                                                                   sci_name,
#                                                                   infraspecies_exist)


# Create the group layer by calling the create_group_lyr() function
# infra_group_lyr = KBAFunctions.create_infraspecies_group_lyr_scoping(m,
#                                                                      new_group_lyr,
#                                                                      common_name,
#                                                                      sci_name,
#                                                                      species_group_lyr)

