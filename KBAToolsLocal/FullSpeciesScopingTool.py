# ----------------------------------------------------------------------------------------------------------------------
# Script Name:      FullSpeciesScopingTool.py      "TOOL 3 - SCOPING TOOL FOR FULL SPECIES"
#
# Script Created:   2022-02-10
# Last Updated:     2022-02-10
# Script Author:    Meg Southee
# Credits:          © WCS Canada / Meg Southee 2022
#
# Purpose:          Add the output data layers (with valid data) to separate groups for full species and each
#                   infraspecies.
# ----------------------------------------------------------------------------------------------------------------------









# Import libraries
import arcpy
import sys
import traceback
import KBAExceptions


# class NoDataError(Exception):
#     """Exception raised for NoDataError in the tool."""
#     pass
#
#
# class NoTableError(Exception):
#     """Exception raised for NoDataError in the tool."""
#     pass
#
#
# class DefQueryError(Exception):
#     """Exception raised for DefQueryError in the tool."""
#     pass
#
#
# class SpeciesDataError(Exception):
#     """Exception raised for SpeciesDataError in the tool."""
#     pass
#
#
# class BioticsSQLError(Exception):
#     """Exception raised for BioticsSQLError in the tool."""
#     pass
#
#
# class SymbologyError(Exception):
#     """Exception raised for SymbologyError in the tool."""
#     pass


# Define class called Tool
class Tool:
    """Select all points, lines and polygons for a specific species."""

    # Instantiate the class
    def __init__(self):
        pass

    """These functions are called from within the run_tool function."""

    # Define a function to create the group layer for a selected record
    def create_group_lyr(m, grp_lyr, sp_com_name, sp_sci_name, infra_exists, sp_level):
        arcpy.AddMessage("Run create_group_lyr function.")

        # Assign naming convention for output group layer in TOC based on infra & species level parameters:
        if infra_exists is True and sp_level == "Species":
            # Common Name (Scientific Name) data not identified to infraspecies
            grp_lyr_name = "{} ({}) data not identified to infraspecies".format(sp_com_name, sp_sci_name)

        else:
            # Common Name (Scientific Name)
            grp_lyr_name = "{} ({})".format(sp_com_name, sp_sci_name)

        # Add a copy of the SpeciesData group layer to the TOC (by referencing the .lyrx file written to scratch)
        m.addLayer(grp_lyr, "TOP")

        # Rename the newly added group layer, because layer was added at top index reference = [0]
        group_lyr = m.listLayers("SpeciesData")[0]
        group_lyr.name = grp_lyr_name  # rename the group layer in TOC
        group_lyr = m.listLayers(grp_lyr_name)[0]
        group_lyr.visible = False  # Turn off the visibility for the group layer

        return group_lyr

        # Define a function to create the InputPoint / InputLine / EO_Polygon layer for the species

    def create_lyr(m, grp_lyr, speciesid, ft_type):
        arcpy.AddMessage("Run create_lyr function for {}.".format(ft_type))

        # Naming convention for point/line/eo_polygon layers in TOC:
        # InputPoint_SpeciesID / InputLine_SpeciesID / EO_Polygon_SpeciesID
        lyr_name = "{}_{}".format(ft_type, speciesid)

        if len(m.listLayers(ft_type)) > 0:
            # Create a variable from the old/existing layer
            lyr = m.listLayers(ft_type)[0]

            # Make a new feature layer with sql query and added .getOutput(0) function
            new_lyr = arcpy.MakeFeatureLayer_management(lyr, lyr_name, "speciesid = {}".format(speciesid),
                                                        None).getOutput(0)

            # Get a count of the records in the new feature layer
            row_count = int(arcpy.GetCount_management(new_lyr).getOutput(0))

            # Check to see if there are any records for the species
            if row_count != 0:
                m.addLayerToGroup(grp_lyr, new_lyr, "BOTTOM")  # Add the new layer
                new_lyr = m.listLayers(lyr_name)[0]
                new_lyr.visible = False  # Turn off the visibility for the new layer

                # Check if the current layer is the EO_Polygon layer
                if ft_type == "EO_Polygon":

                    # Apply new symbology from gallery (YOU MUST LOAD THE WCSC_KBA_STYLE TO THE PROJECT FROM PORTAL)
                    sym = new_lyr.symbology
                    sym.renderer.symbol.applySymbolFromGallery("EO Polygon")
                    new_lyr.symbology = sym

                else:
                    pass  # Do nothing for the points and the lines

            else:
                pass

            m.removeLayer(lyr)  # remove old layer

        else:
            raise KBAExceptions.SpeciesDataError

        # Define a function to create the InputPolygon layers for the species (w/out range & critical habitat data)

    def create_poly_lyr(m, grp_lyr, speciesid, range_data_list):
        arcpy.AddMessage("Run create_poly_lyr function for InputPolygon.")

        # Naming convention for polygon layer in TOC:
        # InputPolygon_SpeciesID
        lyr_name = "InputPolygon_{}".format(speciesid)

        if len(m.listLayers("InputPolygon")) > 0:
            lyr = m.listLayers("InputPolygon")[0]

            # Convert the range_data_list into string variable separated by commas for use in the SQL statement
            range_data_string = ', '.join(str(i) for i in range_data_list)

            # SQL statement to select InputPolygons for the species w/out Range & Critical Habitat data records
            range_sql = "speciesid = {} And inputdatasetid NOT IN ({})".format(speciesid, range_data_string)

            # Make a new feature layer with sql query and added .getOutput(0) function
            new_lyr = arcpy.MakeFeatureLayer_management(lyr, lyr_name, range_sql,
                                                        None).getOutput(0)

            # Get a count of the records in the new feature layer
            row_count = int(arcpy.GetCount_management(new_lyr).getOutput(0))

            # Check to see if there are any records for the species
            if row_count != 0:
                m.addLayerToGroup(grp_lyr, new_lyr, "BOTTOM")  # Add the new poly layer
                new_lyr = m.listLayers(lyr_name)[0]
                new_lyr.visible = False  # Turn off the visibility for the new layer

                # Apply new symbology from gallery (YOU MUST LOAD THE WCSC_KBA_STYLE TO THE PROJECT FROM PORTAL)
                sym = new_lyr.symbology
                sym.renderer.symbol.applySymbolFromGallery("Input Polygon")
                new_lyr.symbology = sym

            else:
                pass

            m.removeLayer(lyr)  # remove poly layer from the new species group

        else:
            raise KBAExceptions.SpeciesDataError

        # Define a function to create the ECCC range / IUCN range / ECCC critical habitat data layers for the species

    def create_range_lyr(m, grp_lyr, speciesid, range_type, range_data_list):
        arcpy.AddMessage("Run create_range_lyr function for {}.".format(range_type))

        # Naming convention for Range / Critical Habitat layers:
        # ECCCRangeMaps_SpeciesID / IUCNRangeMaps_SpeciesID
        lyr_name = "{}_{}".format(range_type, speciesid)

        # Check that the InputPolygon layer is loaded and that there are records in the range_data_list parameter
        if len(m.listLayers("InputPolygon")) > 0 and len(range_data_list) > 0:
            lyr = m.listLayers("InputPolygon")[0]

            # Convert the range_data_list into string variable separated by commas for use in the SQL statement
            range_data_string = ', '.join(str(i) for i in range_data_list)

            # SQL statement to select InputPolygons for the species and Range / Critical Habitat data only
            range_sql = "speciesid = {} And inputdatasetid IN ({})".format(speciesid, range_data_string)

            # Make a new feature layer with sql query and added .getOutput(0) function
            new_lyr = arcpy.MakeFeatureLayer_management(lyr, lyr_name, range_sql,
                                                        None).getOutput(0)

            # Get a count of the records in the new feature layer
            row_count = int(arcpy.GetCount_management(new_lyr).getOutput(0))

            # Check to see if there are any records for the species and the Range / Critical Habitat type
            if row_count != 0:
                m.addLayerToGroup(grp_lyr, new_lyr, "BOTTOM")  # Add the new range / critical habitat layer
                new_lyr = m.listLayers(lyr_name)[0]
                new_lyr.visible = False  # Turn off the visibility for the new layer

                if range_type == "ECCCRangeMaps":
                    # Apply new symbology from gallery (YOU MUST LOAD THE WCSC_KBA_STYLE TO THE PROJECT FROM PORTAL)
                    sym = new_lyr.symbology
                    sym.renderer.symbol.applySymbolFromGallery("ECCC Range Map")
                    new_lyr.symbology = sym

                elif range_type == "IUCNRangeMaps":
                    # Apply new symbology from gallery (YOU MUST LOAD THE WCSC_KBA_STYLE TO THE PROJECT FROM PORTAL)
                    sym = new_lyr.symbology
                    sym.renderer.symbol.applySymbolFromGallery("IUCN Range Map")
                    new_lyr.symbology = sym

                else:
                    # Apply new symbology from gallery (YOU MUST LOAD THE WCSC_KBA_STYLE TO THE PROJECT FROM PORTAL)
                    sym = new_lyr.symbology
                    sym.renderer.symbol.applySymbolFromGallery("ECCC Critical Habitat")
                    new_lyr.symbology = sym

            else:
                pass  # Do nothing

        else:
            raise KBAExceptions.SpeciesDataError

    # Define a function to run the tool
    def run_tool(self, parameters, messages):

        # Make variables from parameter
        param_species = parameters[0].valueAsText
        arcpy.AddMessage("Parameter: {0}".format(param_species))

        # Create an sql query based on the species parameter
        sql = "national_scientific_name = '{}'".format(param_species)
        arcpy.AddMessage(sql)

        # List of biotics fields that you want to use in the search cursor
        biotics_fields = ["speciesid",
                          "element_code",
                          "ca_nname_level",
                          "national_scientific_name",
                          "national_engl_name"]

        # List of InputDataset fields that you want to use in the search cursor
        inputdataset_fields = ["inputdatasetid", "datasetsourceid"]

        try:
            # Current ArcPro Project
            aprx = arcpy.mp.ArcGISProject("CURRENT")

            # Current Active Map in ArcPro Project
            m = aprx.activeMap

            # clear all selections in the map
            m.clearSelection()

            # scratchFolder = Guaranteed to exist at run time
            scratch = arcpy.env.scratchFolder
            arcpy.AddMessage("Scratch folder: {}".format(scratch))

            # # START ERROR HANDLING TO CHECK THAT THE MAP CONTAINS THE NECESSARY TABLES AND DATA LAYERS ...............
            arcpy.AddMessage(u"\u200B")  # Unicode literal to create new line
            arcpy.AddMessage("Start Error Handling Processes...")

            """Error handling to check for existence of the "SpeciesData" group layer."""
            # Check that the SpeciesData Group Layer exists in the map
            if arcpy.Exists("SpeciesData"):
                arcpy.AddMessage("SpeciesData group layer exists.")

                # Get the existing SpeciesDate group layer as a layer object
                species_group_lyr = m.listLayers("SpeciesData")[0]

                # Write a copy of the SpeciesData group layer to the user's scratch folder
                arcpy.SaveToLayerFile_management(species_group_lyr, scratch + "\\species_group.lyrx")

                # Create a layer file from the scratch workspace
                new_group_lyr = arcpy.mp.LayerFile(scratch + "\\species_group.lyrx")

            else:
                raise KBAExceptions.SpeciesDataError

            """Error handling to check for existence of required data layers in the current map."""
            # Create a list of the datasets to check that they exist and don't have active definition query
            dataset_list = ["InputPoint", "InputLine", "InputPolygon", "EO_Polygon"]

            # Iterate through the list of dataset names (layers)
            for dataset in dataset_list:
                # Check to see if a dataset layer with that name exists in the map
                if arcpy.Exists("SpeciesData\\{}".format(dataset)):
                    arcpy.AddMessage("{} data layer exists.".format(dataset))

                    # Create a layer variable out of the current dataset
                    lyr = m.listLayers(dataset)[0]

                    # Check if the layer supports a definition query
                    if lyr.supports("DEFINITIONQUERY"):
                        # arcpy.AddMessage("{} supports def query.".format(dataset))

                        # Check if there is an active definition query on any of the layer
                        if lyr.definitionQuery != '':

                            # Raise custom DefQueryError if there is a definition query
                            raise KBAExceptions.DefQueryError

                        else:
                            # arcpy.AddMessage("No def query on {}.".format(dataset))
                            pass
                    else:
                        pass
                else:
                    # Raise the custom NoDataError if the dataset doesn't exist. Pass the dataset name to the error.
                    raise KBAExceptions.NoDataError

            """ Error handling to check for existence of required data tables in the current map."""
            # Create a list of the tables to check that they exist and don't have active definition query
            table_list = ["BIOTICS_ELEMENT_NATIONAL", "Species (view only)", "InputDataset"]

            # Iterate through the list of table names (tables)
            for table in table_list:
                # Error handling to ensure that the required tables exists in the map
                if arcpy.Exists(table):
                    arcpy.AddMessage("{} table exists.".format(table))

                    # Create a layer variable out of the current table
                    lyr = m.listTables(table)[0]

                    # Check if there is an active definition query on any of the layer
                    if lyr.definitionQuery != '':

                        # Raise custom DefQueryError if there is a definition query
                        raise KBAExceptions.DefQueryError

                    else:
                        # arcpy.AddMessage("No def query on {}.".format(table))
                        pass

                else:
                    raise KBAExceptions.NoTableError

            """Error handling to check for existence of required symbology for new data layers.."""
            lyr = m.listLayers("InputPolygon")[0]
            sym = lyr.symbology  # Access symbol parameters in arcpy

            counter = 0
            condition = False
            sym_list = sym.renderer.symbol.listSymbolsFromGallery("")  # List of all symbols in the project gallery

            # While statement to run through the entire sym_list and try to find the custom Input Polygon symbol
            while not condition:
                current_name = sym_list[counter].name  # Get the name of the current symbol
                if current_name == "Input Polygon":
                    condition = True  # exit the while loop after processing the statements in this clause
                    arcpy.AddMessage("Custom WCSC-KBA-Symbology found.")

                    # Update symbology for the InputPolygon layer in the SpeciesData group layer
                    sym.renderer.symbol.applySymbolFromGallery("Input Polygon")
                    lyr.symbology = sym

                else:
                    counter += 1  # increase the counter to move to the next item in the list
                    if counter == len(sym_list):  # you have reached the end of the list and not found the desired sym
                        condition = True
                        raise KBAExceptions.SymbologyError

            # # END ERROR HANDLING .....................................................................................

            # # START DATA PROCESSING ..................................................................................
            arcpy.AddMessage(u"\u200B")  # Unicode literal to create new line
            arcpy.AddMessage("Start Geoprocessing...")

            # Select the record in BIOTICS table based on the user-specified sql expression
            biotics_record = arcpy.management.SelectLayerByAttribute("BIOTICS_ELEMENT_NATIONAL",
                                                                     "NEW_SELECTION",
                                                                     sql)

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

            # Get record details from Biotics table using a search cursor for the selected record
            with arcpy.da.SearchCursor("BIOTICS_ELEMENT_NATIONAL", biotics_fields, sql) as biotics_cursor:
                for row in biotics_cursor:
                    # Assign variables from the record based on the list order in biotics_fields variable
                    speciesid = row[0]
                    element_code = row[1]
                    s_level = row[2]
                    sci_name = row[3]
                    common_name = row[4]

                    arcpy.AddMessage("Species ID: {}".format(speciesid))
                    arcpy.AddMessage("Scientific Name: {}".format(sci_name))
                    arcpy.AddMessage("Common Name: {}".format(common_name))
                    arcpy.AddMessage("Species Level: {}".format(s_level))
                    arcpy.AddMessage("Element Code: {}".format(element_code))

            # Exit the search cursor, but keep the variables from inside the search cursor
            del row, biotics_cursor

            # # CHECK TO SEE IF THERE ARE RELATED RECORDS [INFRASPECIES] THAT NEED TO BE PROCESSED ...................
            # Assign variables related to the species table and the species id sql statement
            speciesid_sql = "speciesid = {}".format(speciesid)
            species_table = "Species (view only)"

            # The initial selected record is full species & the tool will process all infraspecies [SEPARATE GROUPS]
            arcpy.AddMessage(u"\u200B")  # Unicode literal to create new line
            arcpy.AddMessage("Check to see if infraspecies exist...")

            """Use logic to select all sub/infraspecies records for this full species by comparing and matching the 
            element_code for the full species from Biotics to the fullspecies_elementcode for the infraspecies
            records in Species table."""

            # Create empty speciesid_list - faster processing than using getCount object from arcpy
            speciesid_list = []

            # Select matching record from Species table for the initial full species record in Biotics
            species_records = arcpy.management.SelectLayerByAttribute(species_table,
                                                                      "NEW_SELECTION",
                                                                      speciesid_sql)

            # Select records from Species table where fullspecies_elementcode matches the element_code from Biotics
            species_records = arcpy.management.SelectLayerByAttribute(species_table,
                                                                      "ADD_TO_SELECTION",
                                                                      "fullspecies_elementcode = '{}'"
                                                                      .format(element_code))

            # Iterate through the selected records and create a list of the additional species ids
            with arcpy.da.SearchCursor(species_records, ["speciesid"]) as species_cursor:
                for species_row in species_cursor:
                    # Only process new species id values
                    if species_row[0] != speciesid:
                        speciesid_list.append(species_row[0])  # Append current speciesid for the row to the list
                    else:
                        pass

            # arcpy.AddMessage(speciesid_list)

            del species_cursor, species_row  # delete some variables

            # Check to see if there are values in the speciesid_list (i.e. infraspecies exist)
            if not speciesid_list:  # speciesid_list is empty
                # PROCESS FULL SPECIES
                arcpy.AddMessage("This species does not have infraspecies.")
                infraspecies_exist = False

            else:
                # PROCESS SPECIES WITH INFRASPECIES
                arcpy.AddMessage("This species has {} infraspecies that need to be processed.".
                                 format(str(len(speciesid_list))))
                infraspecies_exist = True



            """ This is where the processing happens to create the outputs in the Contents pane of the current map."""

            # # USE FUNCTIONS TO CREATE GROUP LAYER AND POINTS/LINES/EOS LAYERS [FOR FULL SPECIES] ...................
            # Create the group layer by calling the create_group_lyr() function
            species_group_lyr = Tool.create_group_lyr(m, new_group_lyr, common_name, sci_name, infraspecies_exist, s_level)

            # Call the create_lyr() function x3 to create the point, lines & EO Layers
            Tool.create_lyr(m, species_group_lyr, speciesid, 'InputPoint')
            Tool.create_lyr(m, species_group_lyr, speciesid, 'InputLine')
            Tool.create_lyr(m, species_group_lyr, speciesid, 'EO_Polygon')

            # # CREATE LISTS OF INPUT DATASET ID VALUES FOR RANGE MAPS AND CRITICAL HABITAT DATASETS ...............

            # # GET LIST OF ECCC RANGE MAP DATASETS
            # Empty list to hold InputDatasetID values for records that correspond to ECCC Range Maps
            eccc_range_data_list = []

            # Search cursor to get the InputDatasetID values from InputDataset table
            # for records that have DatasetSourceID = 994 (i.e., DatasetSourceName = ECCC Range Maps)
            with arcpy.da.SearchCursor("InputDataset",
                                       inputdataset_fields,
                                       "datasetsourceid = 994") as inputdataset_cursor:

                # Iterate through the selected records in the InputDataset table
                for inputdataset_record in inputdataset_cursor:

                    # Append InputDatasetID values to the specified range_data_list
                    eccc_range_data_list.append(inputdataset_record[0])

            # # GET LIST OF IUCN RANGE MAP DATASETS
            # Empty list to hold InputDatasetID values for records that correspond to IUCN Range Maps
            iucn_range_data_list = []

            # Search cursor to get the InputDatasetID values from InputDataset table
            # for records that have DatasetSourceID = 996 (i.e., DatasetSourceName = IUCN Range Maps)
            with arcpy.da.SearchCursor("InputDataset",
                                       inputdataset_fields,
                                       "datasetsourceid = 996") as inputdataset_cursor:

                # Iterate through the selected records in the InputDataset table
                for inputdataset_record in inputdataset_cursor:

                    # Append InputDatasetID values to the specified range_data_list
                    iucn_range_data_list.append(inputdataset_record[0])

            # # GET LIST OF ECCC CRITICAL HABITAT DATASETS
            # Empty list to hold InputDatasetID values for records that correspond to ECCC Critical Habitat
            crit_habitat_data_list = []

            # Search cursor to get the InputDatasetID values from InputDataset table
            # for records that have DatasetSourceID = 19 (i.e., DatasetSourceName = ECCC Critical Habitat)
            with arcpy.da.SearchCursor("InputDataset",
                                       inputdataset_fields,
                                       "datasetsourceid = 19") as inputdataset_cursor:

                # Iterate through the selected records in the InputDataset table
                for inputdataset_record in inputdataset_cursor:

                    # Append InputDatasetID values to the specified range_data_list
                    crit_habitat_data_list.append(inputdataset_record[0])

            del inputdataset_record, inputdataset_cursor

            # Create a list of all the datasets that are Range or Critical Habitat datasets
            range_and_crit_habitat_list = eccc_range_data_list + iucn_range_data_list + crit_habitat_data_list

            # # CREATE OUTPUT LAYERS IN TOC FOR INPUTPOLYGONS, RANGE MAPS AND CRITICAL HABITAT DATASETS ............
            # Call the function to create the InputPolygon layer w/out Range / Critical Habitat data
            Tool.create_poly_lyr(m, species_group_lyr, speciesid, range_and_crit_habitat_list)

            # Call the create_range_lyr() function x3 to process the range maps and critical habitat data
            Tool.create_range_lyr(m, species_group_lyr, speciesid, "ECCCRangeMaps", eccc_range_data_list)
            Tool.create_range_lyr(m, species_group_lyr, speciesid, "IUCNRangeMaps", iucn_range_data_list)
            Tool.create_range_lyr(m, species_group_lyr, speciesid, "ECCCCriticalHabitat", crit_habitat_data_list)

            """After you process the full species, you have to process the infraspecies (if they exist)."""

            # if the speciesid_list is empty
            if not speciesid_list:
                pass

            # if there are infraspecies to process
            else:
                arcpy.AddMessage("Processing additional records.")

                # Iterate through the other species records [ONLY IF THE SPECIES LIST IS MORE THAN ONE RECORD LONG]
                for s_id in speciesid_list:
                    # arcpy.AddMessage("Processing id {} now ...".format(s_id))

                    # Assign sql query variable related to the current species id in the list
                    biotics_sql = "speciesid = {}".format(s_id)
                    # arcpy.AddMessage(biotics_sql)

                    # Select the record in Biotics that you want to process
                    arcpy.SelectLayerByAttribute_management("BIOTICS_ELEMENT_NATIONAL", "NEW_SELECTION", biotics_sql)

                    # Query the record in Biotics to get species information using a search cursor
                    with arcpy.da.SearchCursor("BIOTICS_ELEMENT_NATIONAL", biotics_fields) as new_biotics_cursor:
                        for row in new_biotics_cursor:
                            # Assign relevant variables from the biotics record
                            speciesid = row[0]
                            s_level = row[2]
                            sci_name = row[3]
                            common_name = row[4]

                            arcpy.AddMessage("Species ID: {}.".format(speciesid))
                            arcpy.AddMessage("Scientific Name: {}".format(sci_name))
                            arcpy.AddMessage("Common Name: {}".format(common_name))
                            arcpy.AddMessage("Species Level: {}".format(s_level))

                            # # USE FUNCTIONS TO CREATE GROUP LAYER AND ALL POINTS/LINES/POLY/EOS LAYERS -------------
                            # Create the group layer by calling the create_group_lyr() function
                            infra_group_lyr = Tool.create_group_lyr(m, new_group_lyr, common_name, sci_name,
                                                                    infraspecies_exist, s_level)

                            # Move the infraspecies group layer below the species group layer
                            m.moveLayer(species_group_lyr, infra_group_lyr, "AFTER")

                            # Call the create_lyr() function x3 for points, lines & EOs
                            Tool.create_lyr(m, infra_group_lyr, speciesid, 'InputPoint')
                            Tool.create_lyr(m, infra_group_lyr, speciesid, 'InputLine')
                            Tool.create_lyr(m, infra_group_lyr, speciesid, 'EO_Polygon')

                            # Call the function to create the InputPolygon layer w/out Range & Critical Habitat data
                            Tool.create_poly_lyr(m, infra_group_lyr, speciesid, range_and_crit_habitat_list)

                            # # Call the create_range_lyr() function x3 for range maps and critical habitat data
                            Tool.create_range_lyr(m, infra_group_lyr, speciesid, "ECCCRangeMaps", eccc_range_data_list)
                            Tool.create_range_lyr(m, infra_group_lyr, speciesid, "IUCNRangeMaps", iucn_range_data_list)
                            Tool.create_range_lyr(m, infra_group_lyr, speciesid, "ECCCCriticalHabitat",
                                                  crit_habitat_data_list)

            m.clearSelection()  # clear all selections

            # Check to see if there are data layers in the full species group layer, if empty delete it
            if len(species_group_lyr.listLayers()) > 0:
                pass
            else:
                m.removeLayer(species_group_lyr)
                arcpy.AddWarning("There is no spatial data for this species.")

            arcpy.AddMessage("End of script.")

        # Error handling for custom error related to required data layers in the map
        except KBAExceptions.NoDataError:
            arcpy.AddError("{} Layer does not exist. "
                           "Re-load {} from WCSC-KBA Map Template.".format(dataset, dataset))

        # Error handling for custom error related to required data tables in the map
        except KBAExceptions.NoTableError:
            arcpy.AddError("{} Table does not exist. "
                           "Re-load {} from WCSC-KBA Map Template.".format(table, table))

        # Error handling for custom error related to active definition queries on required layers
        except KBAExceptions.DefQueryError:
            arcpy.AddError("{} has an active definition query. "
                           "Turn off all active definition queries on {} to run the tool.".format(lyr.name, lyr.name))

        # Error handling for custom error related to SpeciesData group layer not existing
        except KBAExceptions.SpeciesDataError:
            arcpy.AddError("SpeciesData (Group Layer) does not exist. "
                           "Re-load original SpeciesData from WCSC-KBA Map Template.")

        # # Error handling for custom input error related to the biotics dropdown list
        # except KBAExceptions.BioticsError:
        #     arcpy.AddError("No record selected.")

        # Error handling if custom WCSC_KBA_Symbology isn't in the project
        except KBAExceptions.SymbologyError:
            arcpy.AddError("You need to add the WCSC_KBA_Symbology from Portal to the current Project.")

        # Error handling if an error occurs while using a Geoprocessing Tool in the script
        except arcpy.ExecuteError:
            # If the script crashes, remove the group layer
            m.removeLayer(species_group_lyr)

            # Get the tool error messages
            msgs = arcpy.GetMessages(2)

            # Return tool error messages for use with a script tool
            arcpy.AddError(msgs)

            # Print tool error messages for use in Python
            print(msgs)

        # Error handling if the script fails for other unexplained reasons
        except:
            # If the script crashes, remove the group layer
            m.removeLayer(species_group_lyr)

            # Get the traceback object
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]

            # Concatenate information together concerning the error into a message string
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"

            # Return Python error messages for use in script tool or Python window
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)

# End of Script
