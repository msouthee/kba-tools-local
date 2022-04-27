# ----------------------------------------------------------------------------------------------------------------------
# Script Name:      FullSpeciesMappingTool.py      "MAPPING TOOL FOR FULL SPECIES" [SINGLE GROUP LAYER]
#
# Script Created:   2022-01-05
# Last Updated:     2022-04-26
# Script Author:    Meg Southee
# Credits:          © WCS Canada / Meg Southee 2021
#
# Purpose:          Adds output data layers to a map in a single group for the full species and its infraspecies, when
#                   infraspecies exist.
#                   Uses different naming logic for the group layer and the individual data layers depending on if
#                   infraspecies exist.
#                   Creates output data that is grouped for multiple species ID values.
#                   Contains logic to handle ECCC Range Maps, ECCC Critical Habitat & IUCN Range Maps separately from
#                   other InputPolygon records.
#
# Update:           Added the ability to choose to use the french species name instead of english species names.
# ----------------------------------------------------------------------------------------------------------------------

# Import libraries
import arcpy
import sys
import traceback
import KBAExceptions


# Define class called Tool
class Tool:
    """Create output layers in a single group for full species and for infraspecies (if they exist)."""

    # Instantiate the class
    def __init__(self):
        pass

    """These functions are called from within the run_tool function. The first parameter should be self, 
    but I don't understand how to get this to work properly."""

    # Define a function to create the group layer for a selected record & its infraspecies
    def create_group_lyr(m, grp_lyr, sp_com_name, sp_sci_name, infra_exists):
        # arcpy.AddMessage("Run create_group_lyr function.")

        # Assign naming convention for output group layer in TOC based on infra parameter:
        if infra_exists is True:
            # Common Name (Scientific Name) including data identified to infraspecies
            grp_lyr_name = "{} ({}) including data identified to infraspecies".format(sp_com_name, sp_sci_name)

        else:
            # Common Name (Scientific Name)
            grp_lyr_name = "{} ({})".format(sp_com_name, sp_sci_name)

        # arcpy.AddMessage("Processing {}.".format(grp_lyr_name))
        # arcpy.AddMessage(grp_lyr.filePath)

        # Add a copy of the SpeciesData group layer to the TOC (by referencing the .lyrx file written to scratch)
        m.addLayer(grp_lyr, "TOP")

        # Rename the newly added group layer, because layer was added at top index reference = [0]
        group_lyr = m.listLayers("SpeciesData")[0]
        group_lyr.name = grp_lyr_name  # rename the group layer in TOC
        group_lyr = m.listLayers(grp_lyr_name)[0]
        group_lyr.visible = False  # Turn off the visibility for the group layer

        return group_lyr

    # Define a function to create the InputPoint / InputLine / EO_Polygon layers
    def create_lyr(m, grp_lyr, speciesid_tuple, ft_type, infra_exists):
        # arcpy.AddMessage("Run create_lyr function for {}.".format(ft_type))

        if len(m.listLayers(ft_type)) > 0:
            # Create a variable from the old/existing layer
            lyr = m.listLayers(ft_type)[0]

            # Assign naming conventions & sql query based on value of infra parameter:
            if infra_exists is True:
                # InputPoint_SpeciesID+ / InputLine_SpeciesID+ / EO_Polygon_SpeciesID+
                lyr_name = "{}_{}+".format(ft_type, speciesid_tuple[0])  # the original speciesID

                # select all speciesid values in the tuple
                sql_query = "speciesid IN {}".format(speciesid_tuple)

            else:
                # InputPoint_SpeciesID / InputLine_SpeciesID / EO_Polygon_SpeciesID
                lyr_name = "{}_{}".format(ft_type, speciesid_tuple[0])  # the original speciesID

                # select only the original species id
                sql_query = "speciesid = {}".format(speciesid_tuple[0])  # the original speciesID

            # arcpy.AddMessage(sql_query)

            # Make a new feature layer with sql query and added .getOutput(0) function
            new_lyr = arcpy.MakeFeatureLayer_management(lyr, lyr_name, sql_query,
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

    # Define a function to create the InputPolygon layers (w/out range & critical habitat data)
    def create_poly_lyr(m, grp_lyr, speciesid_tuple, range_data_list, infra_exists):
        # arcpy.AddMessage("Run create_poly_lyr function for InputPolygon.")

        if len(m.listLayers("InputPolygon")) > 0:
            lyr = m.listLayers("InputPolygon")[0]

            # Convert the range_data_list into string variable separated by commas for use in the SQL statement
            range_data_string = ', '.join(str(i) for i in range_data_list)

            # Assign naming conventions for polygon layer in TOC & sql query based on infra parameter:
            if infra_exists is True:
                # InputPolygon_SpeciesID+
                lyr_name = "InputPolygon_{}+".format(speciesid_tuple[0])

                # SQL statement to select InputPolygons for the species w/out Range & Critical Habitat data records
                range_sql = "speciesid IN {} And inputdatasetid NOT IN ({})".format(speciesid_tuple,
                                                                                    range_data_string)

            else:
                # InputPolygon_SpeciesID
                lyr_name = "InputPolygon_{}".format(speciesid_tuple[0])

                # SQL statement to select InputPolygons for the species w/out Range & Critical Habitat data records
                range_sql = "speciesid = {} And inputdatasetid NOT IN ({})".format(speciesid_tuple[0],
                                                                                   range_data_string)

            # arcpy.AddMessage(range_sql)

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

    # Define a function to create the ECCC range / IUCN range / ECCC critical habitat data layers
    def create_range_lyr(m, grp_lyr, speciesid_tuple, range_type, range_data_list, infra_exists):
        # arcpy.AddMessage("Run create_range_lyr function for {}.".format(range_type))

        # Check that the InputPolygon layer is loaded and that there are records in the range_data_list parameter
        if len(m.listLayers("InputPolygon")) > 0 and len(range_data_list) > 0:
            lyr = m.listLayers("InputPolygon")[0]

            # Convert the range_data_list into string variable separated by commas for use in the SQL statement
            range_data_string = ', '.join(str(i) for i in range_data_list)

            # Assign naming convention for Range / Critical Habitat in TOC based on infra parameter:
            if infra_exists is True:
                # ECCCRangeMaps_SpeciesID+ / IUCNRangeMaps_SpeciesID+
                lyr_name = "{}_{}+".format(range_type, speciesid_tuple[0])

                # SQL statement to select InputPolygons for the species and Range / Critical Habitat data only
                range_sql = "speciesid IN {} And inputdatasetid IN ({})".format(speciesid_tuple,
                                                                                range_data_string)

            else:
                # ECCCRangeMaps_SpeciesID / IUCNRangeMaps_SpeciesID
                lyr_name = "{}_{}".format(range_type, speciesid_tuple[0])

                # SQL statement to select InputPolygons for the species and Range / Critical Habitat data only
                range_sql = "speciesid = {} And inputdatasetid IN ({})".format(speciesid_tuple[0],
                                                                               range_data_string)

            # arcpy.AddMessage(range_sql)

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

        # # SET VARIABLES FOR THE SCRIPT ...............................................................................

        # Make variables from input parameters defined in .pyt
        # Input species from filtered list in dropdown menu in tool dialog
        param_species = parameters[0].valueAsText
        arcpy.AddMessage("Species: {}".format(param_species))

        # This is a boolean parameter, if the box is checked then the value is True, otherwise None
        param_french_name = parameters[1].value
        arcpy.AddMessage("Use French Name: {}".format(param_french_name))
        # arcpy.AddMessage(type(param_french_name))

        # Create an sql query based on the species parameter
        sql = "national_scientific_name = '{}'".format(param_species)

        # Tables
        biotics_table = "BIOTICS_ELEMENT_NATIONAL"
        species_table = "Species (view only)"

        # Fields in BIOTICS_ELEMENT_NATIONAL that are used in the search cursor
        biotics_fields = ["speciesid",
                          "element_code",
                          "ca_nname_level",
                          "national_scientific_name",
                          "national_engl_name",
                          "national_fr_name"]  # Added french species names

        # Fields in InputDataset that are used in the search cursor
        inputdataset_fields = ["inputdatasetid",
                               "datasetsourceid"]

        # Empty lists to hold data values
        speciesid_list = []  # hold speciesid values for full species and infraspecies
        eccc_range_data_list = []  # hold inputdatasetid values for ECCC range maps
        iucn_range_data_list = []  # hold inputdatasetid values for IUCN range maps
        crit_habitat_data_list = []  # hold inputdatasetid values for ECCC critical habitat

        # Datasets/tables that need to exist in the map and not have active definition query
        dataset_list = ["InputPoint", "InputLine", "InputPolygon", "EO_Polygon"]
        table_list = [biotics_table, species_table, "InputDataset"]

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

            # Get record details from Biotics table using a search cursor for the selected record
            with arcpy.da.SearchCursor(biotics_table, biotics_fields, sql) as biotics_cursor:
                for row in biotics_cursor:
                    # Assign variables from the record based on the list order in biotics_fields variable
                    speciesid = row[0]
                    element_code = row[1]
                    s_level = row[2]
                    sci_name = row[3]
                    en_name = row[4]
                    fr_name = row[5]

                    arcpy.AddMessage("Species ID: {}".format(speciesid))
                    arcpy.AddMessage("Scientific Name: {}".format(sci_name))
                    arcpy.AddMessage("English Name: {}".format(en_name))
                    arcpy.AddMessage("French Name: {}".format(fr_name))
                    arcpy.AddMessage("Species Level: {}".format(s_level))
                    arcpy.AddMessage("Element Code: {}".format(element_code))

            # If param_french_name is True, then check if fr_name exists, if None then use en_name
            if param_french_name and not fr_name:
                arcpy.AddMessage("There is no french name for this species. Revert to using english name.")
                # Set the french name parameter to False
                param_french_name = False

            else:
                pass

            # Exit the search cursor, but keep the variables from inside the search cursor
            del row, biotics_cursor

            # Append the speciesid to the speciesid_list
            speciesid_list.append(speciesid)

            # # CHECK TO SEE IF THERE ARE RELATED INFRASPECIES RECORDS THAT NEED TO BE PROCESSED [SINGLE OUTPUT]....

            """Use logic to select all infraspecies records for the full species by comparing and matching the 
            element_code for the full species from Biotics table to the fullspecies_elementcode for the infraspecies
            records in Species table. The initial selected record is a full species and the tool will process all 
            infraspecies into a single grouped output layer."""

            arcpy.AddMessage(u"\u200B")  # Unicode literal to create new line
            arcpy.AddMessage("Check to see if infraspecies exist...")

            # Select records from Species table where fullspecies_elementcode matches the element_code from Biotics
            species_records = arcpy.management.SelectLayerByAttribute(species_table,
                                                                      "NEW_SELECTION",
                                                                      "fullspecies_elementcode = '{}'"
                                                                      .format(element_code))

            # Iterate through the selected records and create a list of the additional infraspecies speciesid values
            with arcpy.da.SearchCursor(species_records, ["speciesid"]) as species_cursor:
                for species_row in species_cursor:
                    # Only process new speciesid values
                    if species_row[0] != speciesid:
                        speciesid_list.append(species_row[0])  # Append current speciesid for the row to the list
                    else:
                        pass

            # del species_cursor, species_row  # delete some variables

            """ This is where the processing happens to create the outputs in the Contents pane of the current map. 
            DIFFERENT LOGIC IS IMPLEMENTED BASED ON THE IF/ELSE STATEMENT."""

            # Check to see if infraspecies exist by checking length of the speciesid_list
            # If the list is only 1 record long, PROCESS FULL SPECIES ONLY
            if len(speciesid_list) == 1:
                arcpy.AddMessage("This species has no infraspecies.")
                infraspecies_exist = False
                speciesid_tuple = speciesid_list

            # Else if the list is longer than one record, PROCESS FULL SPECIES AND INFRASPECIES
            else:
                infraspecies_count = len(speciesid_list) - 1
                arcpy.AddMessage("This species has {} infraspecies.".format(str(infraspecies_count)))
                infraspecies_exist = True

                # Convert the speciesid_list into a tuple (puts the values in round brackets(), not square brackets[])
                speciesid_tuple = tuple(speciesid_list)
                arcpy.AddMessage("Species ids in output group layer: {}".format(speciesid_tuple))

            # # USE FUNCTIONS TO CREATE GROUP LAYER AND POINTS/LINES/EOS LAYERS [FOR FULL SPECIES AND INFRASPECIES].
            # Create the group layer by calling the create_group_lyr() function
            # Use french or english name depending on parameters

            # if the parameter to use french names is True, use french name
            if param_french_name:
                group_lyr = Tool.create_group_lyr(m,
                                                  new_group_lyr,
                                                  fr_name,
                                                  sci_name,
                                                  infraspecies_exist)

            # if the parameter to use french names is False or None, use english name
            else:
                group_lyr = Tool.create_group_lyr(m,
                                                  new_group_lyr,
                                                  en_name,
                                                  sci_name,
                                                  infraspecies_exist)

            # Call the create_lyr() function x3 to create the point, lines & EO Layers
            Tool.create_lyr(m, group_lyr, speciesid_tuple, 'InputPoint', infraspecies_exist)
            Tool.create_lyr(m, group_lyr, speciesid_tuple, 'InputLine', infraspecies_exist)
            Tool.create_lyr(m, group_lyr, speciesid_tuple, 'EO_Polygon', infraspecies_exist)

            # # CREATE LISTS OF INPUT DATASET ID VALUES FOR RANGE MAPS AND CRITICAL HABITAT DATASETS ...............

            # # GET LIST OF ECCC RANGE MAP DATASETS ----------------------------------------------------------------
            # Search cursor to get the InputDatasetID values from InputDataset table for records where
            # DatasetSourceID = 994 (i.e., DatasetSourceName = ECCC Range Maps)
            with arcpy.da.SearchCursor("InputDataset",
                                       inputdataset_fields,
                                       "datasetsourceid = 994") as inputdataset_cursor:
                for inputdataset_record in inputdataset_cursor:
                    eccc_range_data_list.append(inputdataset_record[0])  # Append inputdatasetid values

            # # GET LIST OF IUCN RANGE MAP DATASETS ---------------------------------------------------------------
            # Search cursor to get the InputDatasetID values from InputDataset table for records where
            # DatasetSourceID = 996 (i.e., DatasetSourceName = IUCN Range Maps)
            with arcpy.da.SearchCursor("InputDataset",
                                       inputdataset_fields,
                                       "datasetsourceid = 996") as inputdataset_cursor:
                for inputdataset_record in inputdataset_cursor:
                    iucn_range_data_list.append(inputdataset_record[0])  # Append inputdatasetid values

            # # GET LIST OF ECCC CRITICAL HABITAT DATASETS --------------------------------------------------------
            # Search cursor to get the InputDatasetID values from InputDataset table for records where
            # DatasetSourceID = 19 (i.e., DatasetSourceName = ECCC Critical Habitat)
            with arcpy.da.SearchCursor("InputDataset",
                                       inputdataset_fields,
                                       "datasetsourceid = 19") as inputdataset_cursor:
                for inputdataset_record in inputdataset_cursor:
                    crit_habitat_data_list.append(inputdataset_record[0])  # Append inputdatasetid values

            del inputdataset_record, inputdataset_cursor

            # Create a list of all the datasets that are Range or Critical Habitat datasets
            range_and_crit_habitat_list = eccc_range_data_list + iucn_range_data_list + crit_habitat_data_list

            # # CREATE OUTPUT LAYERS IN TOC FOR INPUTPOLYGONS, RANGE MAPS AND CRITICAL HABITAT DATASETS ............
            # Call the function to create the InputPolygon layer w/out Range / Critical Habitat data
            Tool.create_poly_lyr(m, group_lyr, speciesid_tuple, range_and_crit_habitat_list, infraspecies_exist)

            # Call the create_range_lyr() function x3 to process the range maps and critical habitat data
            Tool.create_range_lyr(m, group_lyr, speciesid_tuple, "ECCCRangeMaps", eccc_range_data_list,
                                  infraspecies_exist)
            Tool.create_range_lyr(m, group_lyr, speciesid_tuple, "IUCNRangeMaps", iucn_range_data_list,
                                  infraspecies_exist)
            Tool.create_range_lyr(m, group_lyr, speciesid_tuple, "ECCCCriticalHabitat", crit_habitat_data_list,
                                  infraspecies_exist)

            m.clearSelection()  # clear all selections

            # Check to see if there are any layers in the full species group layer, if empty delete it
            if len(group_lyr.listLayers()) > 0:
                pass
            else:
                m.removeLayer(group_lyr)
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

        # Error handling if custom WCSC_KBA_Symbology isn't in the project
        except KBAExceptions.SymbologyError:
            arcpy.AddError("You need to add the WCSC_KBA_Symbology from Portal to the current Project.")

        # Error handling if an error occurs while using a Geoprocessing Tool in the script
        except arcpy.ExecuteError:
            # If the script crashes, remove the group layer
            m.removeLayer(group_lyr)

            # Get the tool error messages
            msgs = arcpy.GetMessages(2)

            # Return tool error messages for use with a script tool
            arcpy.AddError(msgs)

            # Print tool error messages for use in Python
            print(msgs)

        # Error handling if the script fails for other unexplained reasons
        except:
            # If the script crashes, remove the group layer
            m.removeLayer(group_lyr)

            # Get the traceback object
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]

            # Concatenate information together concerning the error into a message string
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"

            # Return Python error messages for use in script tool or Python window
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)

# End of script
