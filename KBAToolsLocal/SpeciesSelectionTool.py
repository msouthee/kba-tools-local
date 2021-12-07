# ----------------------------------------------------------------------------------------------------------------------
# Script Name:      SpeciesSelectionTool.py
#
# Script Created:   2021-10-27
# Last Updated:     2021-12-07
# Script Author:    Meg Southee
# Credits:          © WCS Canada / Meg Southee 2021
#
# Purpose:          Create definition queries and group the output datasets (with valid data) under a species heading
#                   in the TOC in the active map.
# ----------------------------------------------------------------------------------------------------------------------

# Import libraries
import arcpy
import sys
import traceback


# Define custom exception for error handling
class BioticsSQLError(Exception):
    pass


# Define custom exception for error handling
class BioticsTableError(Exception):
    pass


# Define custom exception for error handling
class SpeciesTableError(Exception):
    pass


# Define custom exception for error handling
class SpeciesDataError(Exception):
    pass


# Define class called Tool
class Tool:
    """Select all points, lines and polygons for a specific species."""
    # Instantiate the class
    def __init__(self):
        pass

    # Define a function to create the group layer for a selected record (Function = reusable piece of code)
    # This function will be called from within the run_tool function
    # The first parameter should be self, but I don't understand how to get it work properly
    def create_group_lyr(m, grp_lyr, sp_com_name, sp_sci_name):
        arcpy.AddMessage("Run create_group_lyr function.")

        # Naming convention for output group layer: Common Name (Scientific Name)
        group_lyr_name = "{} ({})".format(sp_com_name, sp_sci_name)
        arcpy.AddMessage("Processing {} ...".format(group_lyr_name))

        # Add a copy of the SpeciesData group layer to the TOC (by referencing the .lyrx file written to scratch)
        m.addLayer(grp_lyr, "TOP")

        # Rename the newly added group layer, because layer was added at top index reference = [0]
        group_lyr = m.listLayers("SpeciesData")[0]
        group_lyr.name = group_lyr_name  # rename the group layer in TOC
        group_lyr = m.listLayers(group_lyr_name)[0]
        group_lyr.isVisible = False  # turn off the visibility for the group layer

        return group_lyr

    # Define a function to create the InputPoint layer for the species
    def create_lyr(m, grp_lyr, speciesid, ft_type):
        arcpy.AddMessage("Run create_lyr function for {}.".format(ft_type))

        # Naming convention for point/line/polygon layers = InputPoint_SpeciesID
        lyr_name = "{}_{}".format(ft_type, speciesid)

        if len(m.listLayers(ft_type)) > 0:
            lyr = m.listLayers(ft_type)[0]

            # Make a new feature layer with sql query and added .getOutput(0) function
            new_lyr = arcpy.MakeFeatureLayer_management(lyr, lyr_name, "speciesid = {}".format(speciesid),
                                                        None).getOutput(0)

            # Get a count of the records in the new feature layer
            row_count = int(arcpy.GetCount_management(new_lyr).getOutput(0))

            # Check to see if there are any records for the species
            if row_count != 0:
                m.addLayerToGroup(grp_lyr, new_lyr, "BOTTOM")  # Add the new layer
            else:
                pass  # Do nothing

            m.removeLayer(lyr)  # remove old layer

        else:
            raise SpeciesDataError

    # Define a function to create the InputPolygon layer for the species
    def create_poly_lyr(m, grp_lyr, speciesid):
        arcpy.AddMessage("Run create_poly_lyr function.")

        # Naming convention for point/line/polygon layers = InputPolygon_SpeciesID
        lyr_name = "InputPolygon_{}".format(speciesid)

        if len(m.listLayers("InputPolygon")) > 0:
            lyr = m.listLayers("InputPolygon")[0]

            # Make a new feature layer with sql query and added .getOutput(0) function
            new_lyr = arcpy.MakeFeatureLayer_management(lyr, lyr_name, "speciesid = {}".format(speciesid),
                                                        None).getOutput(0)

            # Get a count of the records in the new feature layer
            row_count = int(arcpy.GetCount_management(new_lyr).getOutput(0))

            # Check to see if there are any records for the species
            if row_count != 0:
                m.addLayerToGroup(grp_lyr, new_lyr, "TOP")  # Add the new poly layer
            else:
                pass  # Do nothing

            m.removeLayer(lyr)  # remove old poly layer

        else:
            raise SpeciesDataError

    # Define a function to run the tool
    def run_tool(self, parameters, messages):

        # Make variables from parameters
        param_table = parameters[0].valueAsText
        param_sql = parameters[1].valueAsText
        param_infraspecies = parameters[2].valueAsText

        arcpy.AddMessage("Parameters: {0}, {1}, {2}".format(param_table, param_sql, param_infraspecies))

        # # species level list based on the Canadian national name level [ca_nname_level] field
        # sp_level_list = ["species",
        #                  "subspecies",
        #                  "population",
        #                  "variety"]

        # List of biotics fields that you want to use in the search cursor
        biotics_fields = ["speciesid",
                          "element_code",
                          "ca_nname_level",
                          "national_scientific_name",
                          "national_engl_name"]  # new list of fields

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

            # # ERROR HANDLING TO CHECK THAT THE MAP CONTAINS THE NECESSARY TABLES AND DATA LAYERS
            # Error handling to ensure that the Biotics table exists
            if arcpy.Exists("BIOTICS_ELEMENT_NATIONAL"):
                arcpy.AddMessage("BIOTICS_ELEMENT_NATIONAL table exists.")
                pass

            else:
                raise BioticsTableError

            # Error handling to ensure that the Species table exists
            if arcpy.Exists("Species (view only)"):
                arcpy.AddMessage("Species (view only) table exists.")
                species_table = "Species (view only)"
                pass

            else:
                raise SpeciesTableError

            # Error handling to check for existence of the "SpeciesData" group lyr
            if len(m.listLayers("SpeciesData")) > 0:
                # Get the existing SpeciesDate group layer as a layer object
                group_lyr = m.listLayers("SpeciesData")[0]

                # Write a copy of the SpeciesData group layer to the user's scratch folder
                arcpy.SaveToLayerFile_management(group_lyr, scratch + "\\species_group.lyrx")

                # Create a layer file from the scratch workspace
                new_group_lyr = arcpy.mp.LayerFile(scratch + "\\species_group.lyrx")

            else:
                raise SpeciesDataError

            # # START PROCESSING
            # Select the record in BIOTICS table based on the user-specified sql expression
            biotics_record = arcpy.management.SelectLayerByAttribute(param_table, "NEW_SELECTION", param_sql)

            # Logic to check that only one record is selected in the initial query
            biotics_count = int(arcpy.GetCount_management(biotics_record).getOutput(0))

            # if count = 0, throw error using custom exception
            if biotics_count == 0:
                arcpy.AddMessage("No records selected.")
                raise BioticsSQLError

            # if count > 1, throw error using custom exception
            elif biotics_count > 1:
                raise BioticsSQLError

            else:
                pass

            # Create empty speciesid_list - faster processing than using getCount object from arcpy
            speciesid_list = []

            # Get record details from Biotics table using a search cursor for the selected record
            with arcpy.da.SearchCursor(param_table, biotics_fields, param_sql) as biotics_cursor:
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

            # Exit the search cursor, but keep the variables from inside the search cursor.
            del row, biotics_cursor

            # # USE FUNCTIONS TO CREATE GROUP LAYER AND ALL POINTS/LINES/POLY/EOS LAYERS ----------------------------
            # Create the group layer by calling the create_group_lyr() function
            group_lyr = Tool.create_group_lyr(m, new_group_lyr, common_name, sci_name)
            aprx.save()  # save the Pro project

            # # USE THE SAME FUNCTION TO CREATE ALL POINTS/LINES/EOS
            # Create the point layer by calling the create_lyr() function
            Tool.create_lyr(m, group_lyr, speciesid, 'InputPoint')
            aprx.save()  # save the Pro project

            # Create the line layer by calling the create_lyr() function
            Tool.create_lyr(m, group_lyr, speciesid, 'InputLine')
            aprx.save()  # save the Pro project

            # Create the polygon layer by calling the create_lyr() function
            Tool.create_lyr(m, group_lyr, speciesid, 'InputPolygon')
            aprx.save()  # save the Pro project

            # # Create the polygon layer by calling the create_poly_lyr() function [KEEP FOR ADDITIONAL LOGIC LATER]
            # Tool.create_poly_lyr(m, group_lyr, speciesid)
            # aprx.save()  # save the Pro project

            # Create the eo layer by calling the create_lyr() function
            Tool.create_lyr(m, group_lyr, speciesid, 'EO_Polygon')
            aprx.save()  # save the Pro project

            # # FIND ALL RELATED RECORDS THAT NEED TO BE PROCESSED .....................................................
            # Assign sql query variable related to the species id
            speciesid_sql = "speciesid = {}".format(speciesid)

            # Check to see if the initial selected record is a full species or an infraspecies
            # If the user selects a full species, process all sub/infraspecies for this species
            if s_level.lower() == "species":
                arcpy.AddMessage("Full species selected. Process all infraspecies (if they exist).")

                # Select matching record from Species table for the initial full species record in Biotics
                species_records = arcpy.management.SelectLayerByAttribute(species_table,
                                                                          "NEW_SELECTION",
                                                                          speciesid_sql)

                """Use logic to select all sub/infraspecies records for this full species by comparing and matching the 
                element_code for the full species from Biotics to the fullspecies_elementcode for the infraspecies
                records in Species table."""

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

                del species_cursor, species_row  # delete some variables

            # If the user selects a subspecies/population/variety, check to see if they want the full species too
            elif s_level.lower() in ("subspecies", "population", "variety"):

                # Check if user wants to select the infraspecies & full species [based on param_infraspecies]
                # Logic to select additional records based on element_code
                if param_infraspecies == "Yes":

                    # Select initial record from Species table based on the speciesid
                    species_records = arcpy.management.SelectLayerByAttribute(species_table,
                                                                              "NEW_SELECTION",
                                                                              speciesid_sql)

                    """Use logic to select the full species records for this infraspecies by comparing and matching the 
                    fullspecies_elementcode for the selected infraspecies record in Species table to the element_code
                    for the full species in Biotics."""

                    # Create a search cursor to get the fullspecies_elementcode from the Species table
                    with arcpy.da.SearchCursor(species_table,
                                               ["fullspecies_elementcode"],
                                               speciesid_sql) as species_cursor:

                        for species_row in species_cursor:
                            fs_elementcode = species_row[0]  # get the fullspecies_elementcode [singular value]

                    # Add the full species record to the selected infraspecies record in the Species table
                    species_records = arcpy.management.SelectLayerByAttribute(species_table,
                                                                              "ADD_TO_SELECTION",
                                                                              "fullspecies_elementcode = '{}'"
                                                                              .format(fs_elementcode))

                    # Iterate through the selected records and create a list of the species ids
                    with arcpy.da.SearchCursor(species_records, ["speciesid"]) as species_cursor:
                        for species_row in species_cursor:
                            # Only process new species id values
                            if species_row[0] != speciesid:
                                speciesid_list.append(species_row[0])  # Append current speciesid to the list
                            else:
                                pass

                    del species_cursor, species_row  # delete some variables

                # Logic if user only wants to process the single infraspecies by itself
                else:
                    pass  # Do nothing, record is already processed

            """ This is where you end up if you select a full species; if you select an infraspecies and
                param_infraspecies == "Yes"; or if you select an infraspecies and param_infraspecies == "No".
                Check to see if there are additional species records to process and create output layers as needed."""

            # Delete the old variables from the biotics record
            del speciesid, element_code, s_level, sci_name, common_name

            # PROCESS THE ADDITIONAL RECORDS USING THE SPECIESID_LIST [METHOD 2 - IMPLEMENTED] .........................
            if len(speciesid_list) < 1:
                arcpy.AddMessage("No additional records to process.")
                pass  # Do nothing and go to end of script

            else:
                # Iterate through the other species records [ONLY IF THE LIST IS MORE THAN ONE RECORD LONG]
                for s_id in speciesid_list:
                    # arcpy.AddMessage("Processing id {} now ...".format(s_id))

                    # Assign sql query variable related to the current species id in the list
                    biotics_sql = "speciesid = {}".format(s_id)
                    arcpy.AddMessage(biotics_sql)

                    # Select the record in Biotics that you want to process
                    arcpy.SelectLayerByAttribute_management(param_table, "NEW_SELECTION", biotics_sql)

                    # Query the record in Biotics to get species information using a search cursor
                    with arcpy.da.SearchCursor(param_table, biotics_fields) as new_biotics_cursor:
                        for row in new_biotics_cursor:

                            # Assign relevant variables from the biotics record
                            speciesid = row[0]
                            s_level = row[2]
                            sci_name = row[3]
                            common_name = row[4]

                            arcpy.AddMessage("Processing species id: {}.".format(speciesid))
                            arcpy.AddMessage("Scientific Name: {}".format(sci_name))
                            arcpy.AddMessage("Common Name: {}".format(common_name))
                            arcpy.AddMessage("Species Level: {}".format(s_level))

                            # # USE FUNCTIONS TO CREATE GROUP LAYER AND ALL POINTS/LINES/POLY/EOS LAYERS -------------
                            # Create the group layer by calling the create_group_lyr() function
                            group_lyr = Tool.create_group_lyr(m, new_group_lyr, common_name, sci_name)
                            aprx.save()  # save the Pro project

                            # # USE THE SAME FUNCTION TO CREATE ALL POINTS/LINES/EOS
                            # Create the point layer by calling the create_lyr() function
                            Tool.create_lyr(m, group_lyr, speciesid, 'InputPoint')
                            aprx.save()  # save the Pro project

                            # Create the line layer by calling the create_lyr() function
                            Tool.create_lyr(m, group_lyr, speciesid, 'InputLine')
                            aprx.save()  # save the Pro project

                            # Create the polygon layer by calling the create_lyr() function
                            Tool.create_lyr(m, group_lyr, speciesid, 'InputPolygon')
                            aprx.save()  # save the Pro project

                            # # Create the polygon layer by calling the create_poly_lyr() function [KEEP FOR LATER]
                            # Tool.create_poly_lyr(m, group_lyr, speciesid)
                            # aprx.save()  # save the Pro project

                            # Create the eo layer by calling the create_lyr() function
                            Tool.create_lyr(m, group_lyr, speciesid, 'EO_Polygon')

                    aprx.save()  # save the Pro project for the freshly processed species record

                aprx.save()  # save the Pro project after processing all additional species

            m.clearSelection()  # clear all selections
            aprx.save()  # save the Pro project

            arcpy.AddMessage("End of script.")

        # Error handling for custom input error related to the biotics SQL statement
        except BioticsSQLError:
            arcpy.AddError("Incorrect sql statement. See Messages for more details.")

        # Error handling for custom input error related to the biotics SQL statement
        except BioticsTableError:
            arcpy.AddError("BIOTICS_ELEMENT_NATIONAL table does not exist. "
                           "Re-load original Species table from WCSC-KBA Map Template.")

        # Error handling for custom input error related to the biotics SQL statement
        except SpeciesTableError:
            arcpy.AddError("Species table does not exist. Re-load original Species table from WCSC-KBA Map Template.")

        # Error handling for custom error related to SpeciesData group layer not existing
        except SpeciesDataError:
            arcpy.AddError("SpeciesData (Group Layer) or InputPoint/InputLine/InputPolygon/EO_Polygon layers "
                           "do not exist. Re-load original SpeciesData from WCSC-KBA Map Template.")

        # Error handling if an error occurs while using a Geoprocessing Tool in the script
        except arcpy.ExecuteError:
            # Get the tool error messages
            msgs = arcpy.GetMessages(2)

            # Return tool error messages for use with a script tool
            arcpy.AddError(msgs)

            # Print tool error messages for use in Python
            print(msgs)

        # Error handling if the script fails for other unexplained reasons
        except:
            # Get the traceback object
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]

            # Concatenate information together concerning the error into a message string
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"

            # Return Python error messages for use in script tool or Python window
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)

            # # Print Python error messages for use in Python / Python window
            # print(pymsg)
            # print(msgs)


# Controlling process
if __name__ == '__main__':
    # Set sst to an instance of class Tool
    sst = Tool()

    # Hard-coded parameters for debugging
    param_table = arcpy.Parameter()
    param_sql = arcpy.Parameter()
    param_infraspecies = arcpy.Parameter()

    param_table.value = "BIOTICS_ELEMENT_NATIONAL"  # run local & server. User-friendly SQL statements.
    param_sql.value = "national_scientific_name = 'Abronia latifolia'"
    param_infraspecies = "Yes"

    parameters = [param_table, param_sql, param_infraspecies]

    # Call the run_tool function using the input parameters (for the sst instance of class Tool)
    sst.run_tool(parameters, None)
