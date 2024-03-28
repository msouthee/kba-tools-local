# ----------------------------------------------------------------------------------------------------------------------
# Script Name:      FullSpeciesScopingTool.py
# Tool Location:    KBAToolsLocal Toolbox >>> Exploratory Data Analysis Toolkit
# Tool Name:        "Exploratory Tool - Species & Infraspecies" [SEPARATE GROUP LAYERS]
#
# Script Created:   2022-02-10
# Last Updated:     2024-03-28
# Script Author:    Meg Southee
# Credits:          © WCS Canada / Meg Southee 2022
#
# Purpose:          Adds output data layers to a map in separate groups for the full species and each infraspecies.
#                   Uses different naming logic for the full species group layer if infraspecies exist.
#                   Creates separate output data layers for each species ID value.
#                   Contains logic to handle ECCC Range Maps, ECCC Critical Habitat & IUCN Range Maps separately from
#                   other InputPolygon records.
#
# Updates:
# 2022-04-26        Added the ability to choose to use the French species name instead of english species names.
# 2024-03-35        Added functionality to separate four additional datasets from the InputPolygon layer using a data
#                   dictionary. The datasets display as their own output layers in the map with custom symbology.
#                   WCSC Area of Occupancy Maps, WCSC Range Maps, COSEWIC Range Maps, COSEWIC Extent of Occurrence Maps.
# ----------------------------------------------------------------------------------------------------------------------

# Import libraries
import arcpy
import sys
import traceback
import KBAExceptions
import KBAUtils


# Define class called Tool
class Tool:
    """Create output layers in separate groups for full species and for infraspecies (if they exist)."""

    # Instantiate the class
    def __init__(self):
        pass

    """These functions are called from within the run_tool function."""

    # Define a function to create the group layer for selected full species record
    def create_species_group_lyr(m, grp_lyr, sp_com_name, sp_sci_name, infra_exists):
        # arcpy.AddMessage("Run create_group_lyr function.")

        # Assign naming convention for output group layer in TOC based on infra_exists parameter:
        if infra_exists is True:
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

    # Define a function to create group layers for infraspecies records
    def create_infraspecies_group_lyr(m, empty_grp_lyr, sp_com_name, sp_sci_name, species_grp_lyr):
        # arcpy.AddMessage("Run create_group_lyr function.")

        # Assign naming convention for output group layer in TOC
        # Common Name (Scientific Name)
        grp_lyr_name = "{} ({})".format(sp_com_name, sp_sci_name)

        # Insert an empty copy of the SpeciesData group layer BELOW the full species group layer
        m.insertLayer(species_grp_lyr, empty_grp_lyr, "AFTER")

        # Rename the newly added group layer, because layer was added at top index reference = [0]
        group_lyr = m.listLayers("SpeciesData")[0]
        group_lyr.name = grp_lyr_name  # rename the group layer in TOC
        group_lyr = m.listLayers(grp_lyr_name)[0]
        group_lyr.visible = False  # Turn off the visibility for the group layer

        return group_lyr

    # Define a function to create the InputPoint / InputLine / EO_Polygon layers
    def create_lyr(m, grp_lyr, speciesid, ft_type):
        # arcpy.AddMessage("Run create_lyr function for {}.".format(ft_type))

        # Naming convention for point/line/eo_polygon layers in TOC:
        lyr_name = "{} {}".format(ft_type, speciesid)

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

                    # Apply custom symbology
                    sym = new_lyr.symbology
                    sym.renderer.symbol.color = {'RGB': [0, 112, 255, 30]}
                    sym.renderer.symbol.outlineColor = {'RGB': [10, 112, 255, 100]}
                    sym.renderer.symbol.outlineWidth = 2
                    new_lyr.symbology = sym

                else:
                    pass  # Do nothing for the points and the lines

            else:
                pass

            m.removeLayer(lyr)  # remove old layer

        else:
            raise KBAExceptions.SpeciesDataError

    # Define a function to create the InputPolygon layers (w/out the filtered data layers)
    def create_poly_lyr(m, grp_lyr, speciesid, inputdatasetid_list):
        # arcpy.AddMessage("Run create_poly_lyr function for InputPolygon.")

        # Naming convention for polygon layer in TOC:
        lyr_name = "InputPolygon {}".format(speciesid)

        if len(m.listLayers("InputPolygon")) > 0:
            lyr = m.listLayers("InputPolygon")[0]

            # Convert the range_data_list into string variable separated by commas for use in the SQL statement
            inputdatasetid_list_as_string = ', '.join(str(i) for i in inputdatasetid_list)

            # SQL statement to select InputPolygons for the species w/out filtered data records
            range_sql = "speciesid = {} And inputdatasetid NOT IN ({})".format(speciesid, inputdatasetid_list_as_string)

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

                # Apply custom symbology
                sym = new_lyr.symbology
                sym.renderer.symbol.color = {'RGB': [56, 168, 0, 30]}
                sym.renderer.symbol.outlineColor = {'RGB': [56, 168, 0, 100]}
                sym.renderer.symbol.outlineWidth = 2
                new_lyr.symbology = sym

            else:
                pass

            m.removeLayer(lyr)  # remove poly layer from the new species group

        else:
            raise KBAExceptions.SpeciesDataError

    # Define a function to create the data layers for the filtered datasets [ECCC/IUCN/WCSC/COSEWIC MAPS]
    def create_range_lyr(m, grp_lyr, speciesid, map_dict, inputdatasetid_list):
        # arcpy.AddMessage("Run create_range_lyr function for {}.".format(range_type))

        # Unpack the dictionary
        current_layer_name = map_dict[0]
        fill_rgb = map_dict[2]
        outline_rgb = map_dict[3]

        # Naming convention for output datasets for the filtered data layers
        lyr_name = "{} {}".format(current_layer_name, speciesid)

        # Check that the InputPolygon layer is loaded and that there are records in the value list
        if len(m.listLayers("InputPolygon")) > 0 and len(inputdatasetid_list) > 0:
            lyr = m.listLayers("InputPolygon")[0]

            # Convert the value list into string variable separated by commas for use in the SQL statement
            inputdatasetid_list_as_string = ', '.join(str(i) for i in inputdatasetid_list)

            # SQL statement to select InputPolygons for the filtered data only
            range_sql = "speciesid = {} And inputdatasetid IN ({})".format(speciesid, inputdatasetid_list_as_string)

            # Make a new feature layer with sql query and added .getOutput(0) function
            new_lyr = arcpy.MakeFeatureLayer_management(lyr, lyr_name, range_sql,
                                                        None).getOutput(0)

            # Get a count of the records in the new feature layer
            row_count = int(arcpy.GetCount_management(new_lyr).getOutput(0))

            # Check to see if there are any records for the species and filtered dataset type
            if row_count != 0:
                m.addLayerToGroup(grp_lyr, new_lyr, "BOTTOM")  # Add the new filtered output layer
                new_lyr = m.listLayers(lyr_name)[0]
                new_lyr.visible = False  # Turn off the visibility for the new layer

                # Apply custom symbology
                sym = new_lyr.symbology
                sym.renderer.symbol.color = fill_rgb
                sym.renderer.symbol.outlineColor = outline_rgb
                sym.renderer.symbol.outlineWidth = 2
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

        # SQL query based on the input species parameter
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

        # Load dictionary of filtered datasets (Range/AOO/EOO maps), corresponding datasetsourceid values and symbology
        dataset_dict = KBAUtils.symbology_dict

        # Empty lists to hold data values
        infraspeciesid_list = []  # hold speciesid values for infraspecies
        filtered_inputdatasetid_list = []  # hold all inputdatasetid values for range/aoo/habitat maps

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
                # Set the French name parameter to False
                param_french_name = False

            else:
                pass

            # Exit the search cursor, but keep the variables from inside the search cursor
            del row, biotics_cursor

            # # CHECK TO SEE IF THERE ARE RELATED INFRASPECIES RECORDS THAT NEED TO BE PROCESSED [MULTIPLE OUTPUTS]...

            """Use logic to select all infraspecies records for the full species by comparing and matching the 
            element_code for the full species from Biotics table to the fullspecies_elementcode for the infraspecies
            records in Species table. The initial selected record is a full species and the tool will process all 
            infraspecies into separate output group layers."""

            arcpy.AddMessage(u"\u200B")  # Unicode literal to create new line
            arcpy.AddMessage("Check to see if infraspecies exist...")

            # Select records from Species table where fullspecies_elementcode matches the element_code from Biotics
            species_records = arcpy.management.SelectLayerByAttribute(species_table,
                                                                      "NEW_SELECTION",
                                                                      "fullspecies_elementcode = '{}'"
                                                                      .format(element_code))

            # Iterate through the selected records and create a list of the infraspecies speciesid values
            with arcpy.da.SearchCursor(species_records, ["speciesid"]) as species_cursor:
                for species_row in species_cursor:
                    # Only process speciesid values for infraspecies, not for the original full species record
                    if species_row[0] != speciesid:
                        infraspeciesid_list.append(species_row[0])  # Append infraspecies id for the row to the list
                    else:
                        pass

            # del species_cursor, species_row  # delete some variables

            # Check to see if infraspecies exist by checking if there are values in the infraspeciesid_list
            if not infraspeciesid_list:  # List is empty
                arcpy.AddMessage("This species does not have infraspecies.")
                infraspecies_exist = False

            else:
                arcpy.AddMessage("This species has {} infraspecies.".format(str(len(infraspeciesid_list))))
                infraspecies_exist = True

            """ Process full species record to create the outputs in the Contents pane of the current map."""

            # # USE FUNCTIONS TO CREATE GROUP LAYER AND POINTS/LINES/EOS LAYERS [FOR FULL SPECIES] ...................
            # Create the group layer by calling the create_species_group_lyr() function defined in the tool
            # Use French or english name depending on parameters

            # if the parameter to use French names is True, use French name
            if param_french_name:
                species_group_lyr = Tool.create_species_group_lyr(m,
                                                                  new_group_lyr,
                                                                  fr_name,
                                                                  sci_name,
                                                                  infraspecies_exist)

            # if the parameter to use French names is False or None, use english name
            else:
                species_group_lyr = Tool.create_species_group_lyr(m,
                                                                  new_group_lyr,
                                                                  en_name,
                                                                  sci_name,
                                                                  infraspecies_exist)

            # Call the create_lyr() function x3 to create the point, lines & EO Layers
            Tool.create_lyr(m, species_group_lyr, speciesid, 'InputPoint')
            Tool.create_lyr(m, species_group_lyr, speciesid, 'InputLine')
            Tool.create_lyr(m, species_group_lyr, speciesid, 'EO_Polygon')

            # # CREATE OUTPUT LAYERS IN TOC AND LIST OF DATASETIDS FOR RANGE / AOO / HABITAT DATASETS ...............
            # Iterate through the dictionary of filtered datasets
            for key in dataset_dict:
                myname = dataset_dict[key][0]   # Get the name of the dataset from the dictionary
                myvalue = dataset_dict[key][1]  # Get the datasetsourceid value from the dictionary
                arcpy.AddMessage("Processing: {}".format(myname))

                # Call the readFilteredInputDatasetID function for each of the datasets in the dictionary to generate
                # a list of the inputdatasetid values for that dataset
                id_values = KBAUtils.readFilteredInputDatasetID(myvalue)

                # Call the create_range_lyr() function to process each of the filtered datasets as separate outputs
                Tool.create_range_lyr(m, species_group_lyr, speciesid, dataset_dict[key], id_values)

                # Create a merged list of the inputdatasetids for all the filtered datasets
                filtered_inputdatasetid_list.extend(id_values)

            # # CREATE OUTPUT LAYER IN TOC FOR THE INPUTPOLYGON DATASET W/OUT THE FILTERED DATASETS ............
            # Call the function to create the InputPolygon layer w/out the filtered datasets
            Tool.create_poly_lyr(m, species_group_lyr, speciesid, filtered_inputdatasetid_list)

            # Check to see if there are data layers in the full species group layer, if empty delete it
            if len(species_group_lyr.listLayers()) > 0:
                pass
            else:
                m.removeLayer(species_group_lyr)
                arcpy.AddWarning("There is no spatial data for this species.")

            """ Process infraspecies records (if they exist) to create the outputs in the Contents pane."""
            if infraspecies_exist is False:
                pass  # go to end of script

            # ######################################################################################################
            # Process infraspecies
            else:
                arcpy.AddMessage(u"\u200B")  # Unicode literal to create new line
                arcpy.AddMessage("Processing infraspecies...")

                # Iterate through the list of infraspecies speciesid values
                for s_id in infraspeciesid_list:

                    # Assign sql query variable related to the current species id in the list
                    biotics_sql = "speciesid = {}".format(s_id)

                    # Select the infraspecies record in Biotics that you want to process
                    arcpy.SelectLayerByAttribute_management(biotics_table, "NEW_SELECTION", biotics_sql)

                    # Query the record in Biotics to get species information using a search cursor
                    with arcpy.da.SearchCursor(biotics_table, biotics_fields) as infraspecies_biotics_cursor:
                        for row in infraspecies_biotics_cursor:
                            # Assign relevant variables from the biotics record
                            infraspeciesid = row[0]
                            sci_name = row[3]
                            en_name = row[4]
                            fr_name = row[5]

                            arcpy.AddMessage("Species ID: {} ({}).".format(infraspeciesid, sci_name))

                            # # USE FUNCTIONS TO CREATE OUTPUT LAYERS FOR INFRASPECIES ...........................
                            # Create the infraspecies group layer using the create_infraspecies_group_lyr function

                            # if the parameter to use french names is True, use French name
                            if param_french_name:
                                infra_group_lyr = Tool.create_infraspecies_group_lyr(m,
                                                                                     new_group_lyr,
                                                                                     fr_name,
                                                                                     sci_name,
                                                                                     species_group_lyr)

                            # if the parameter to use French names is False or None, use english name
                            else:
                                infra_group_lyr = Tool.create_infraspecies_group_lyr(m,
                                                                                     new_group_lyr,
                                                                                     en_name,
                                                                                     sci_name,
                                                                                     species_group_lyr)

                            # Call the create_lyr() function x3 for points, lines & EOs
                            Tool.create_lyr(m, infra_group_lyr, infraspeciesid, 'InputPoint')
                            Tool.create_lyr(m, infra_group_lyr, infraspeciesid, 'InputLine')
                            Tool.create_lyr(m, infra_group_lyr, infraspeciesid, 'EO_Polygon')

                            # # CREATE OUTPUT LAYERS IN TOC AND LIST OF DATASETIDS FOR RANGE / AOO / HABITAT DATASETS
                            # Iterate through the dictionary of filtered datasets
                            for key in dataset_dict:
                                myname = dataset_dict[key][0]  # Get the name of the dataset from the dictionary
                                myvalue = dataset_dict[key][1]  # Get the datasetsourceid value from the dictionary
                                arcpy.AddMessage("Processing: {}".format(myname))

                                # Call the readFilteredInputDatasetID function for each of the datasets
                                # a list of the inputdatasetid values for that dataset
                                id_values = KBAUtils.readFilteredInputDatasetID(myvalue)
                                # arcpy.AddMessage("InputDatasetIDs: {}".format(id_values))

                                # Call the create_range_lyr() function to process each of the filtered datasets
                                Tool.create_range_lyr(m, infra_group_lyr, infraspeciesid, dataset_dict[key], id_values)

                                # Create a merged list of the inputdatasetids for all the filtered datasets
                                filtered_inputdatasetid_list.extend(id_values)

                            # # CREATE OUTPUT LAYER IN TOC FOR THE INPUTPOLYGON DATASET W/OUT THE FILTERED DATASETS ..
                            # Call the function to create the InputPolygon layer w/out Range & Critical Habitat data
                            Tool.create_poly_lyr(m, infra_group_lyr, infraspeciesid, filtered_inputdatasetid_list)

                    # Check to see if there are data layers in the infraspecies group layer, if empty delete it
                    if len(infra_group_lyr.listLayers()) > 0:
                        pass
                    else:
                        m.removeLayer(infra_group_lyr)
                        arcpy.AddWarning("There is no spatial data for infraspecies {}.".format(sci_name))

            m.clearSelection()  # clear all selections

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
