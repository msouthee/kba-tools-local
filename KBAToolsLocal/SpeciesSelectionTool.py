# ----------------------------------------------------------------------------------------------------------------------
# Script Name:      SpeciesSelectionTool.py
#
# Script Created:   2021-10-27
# Last Updated:     2021-11-30
# Script Author:    Meg Southee
#
# Purpose:          Create definition queries and group the output datasets (with valid data) under a species heading
#                   in the TOC in the active map.
# ----------------------------------------------------------------------------------------------------------------------

# Import libraries
import arcpy
import sys
import traceback
import exceptions  # this is a custom module


# # Naming conventions for point/line/polygon layers = InputPoint_SpeciesID
# point_lyr_name = "InputPoint_{}".format(speciesid)
# line_lyr_name = "InputLine_{}".format(speciesid)
# poly_lyr_name = "InputPolygon_{}".format(speciesid)
# eo_lyr_name = "EO_Polygon_{}".format(speciesid)

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

        lyr = m.listLayers(ft_type)[0]

        # Make a new feature layer with sql query and added .getOutput(0) function
        new_lyr = arcpy.MakeFeatureLayer_management(lyr, lyr_name, "speciesid = {}".format(speciesid),
                                                    None).getOutput(0)

        # Get a count of the records in the new feature layer
        row_count = int(arcpy.GetCount_management(new_lyr).getOutput(0))

        # Check to see if there are anyrecords for the species
        if row_count != 0:
            m.addLayerToGroup(grp_lyr, new_lyr, "BOTTOM")  # Add the new layer
        else:
            pass  # Do nothing

        m.removeLayer(lyr)  # remove old layer

    # Define a function to create the InputLine layer for the species
    def create_poly_lyr(m, grp_lyr, speciesid):
        arcpy.AddMessage("Run create_poly_lyr function.")

        # Naming convention for point/line/polygon layers = InputPolygon_SpeciesID
        lyr_name = "InputPolygon_{}".format(speciesid)

        lyr = m.listLayers("InputPolygon")[0]

        # Make a new feature layer with sql query and added .getOutput(0) function
        new_lyr = arcpy.MakeFeatureLayer_management(lyr, lyr_name, "speciesid = {}".format(speciesid),
                                                    None).getOutput(0)

        # Get a count of the records in the new feature layer
        row_count = int(arcpy.GetCount_management(new_lyr).getOutput(0))

        # Check to see if there are any point records for the species
        if row_count != 0:
            m.addLayerToGroup(grp_lyr, new_lyr, "TOP")  # Add the new poly layer
        else:
            pass  # Do nothing

        m.removeLayer(lyr)  # remove old poly layer

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

            # Select the record in BIOTICS table based on the user-specified sql expression
            biotics_record = arcpy.management.SelectLayerByAttribute(param_table,
                                                                     "NEW_SELECTION",
                                                                     param_sql)

            # Logic to check that only one record is selected in the initial query
            biotics_count = int(arcpy.GetCount_management(biotics_record).getOutput(0))

            # if count = 0, throw error using custom exception
            if biotics_count == 0:
                arcpy.AddMessage("No records selected.")
                raise exceptions.InputError

            # if count > 1, throw error using custom exception
            elif biotics_count > 1:
                arcpy.AddMessage("More than one record selected. Please select only one record.")
                raise exceptions.InputError

            # else continue with script
            else:
                pass

            # Create empty speciesid_list - processing is way faster this way instead of getCount from the result object
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

            # # NOTE: DO THIS LOGIC ONLY ONCE! ----------------------------------------------------------------------
            # Get the existing SpeciesDate group layer as a layer object
            group_lyr = m.listLayers("SpeciesData")[0]

            # Write a copy of the SpeciesData group layer to the user's scratch folder
            arcpy.SaveToLayerFile_management(group_lyr, scratch + "\\species_group.lyrx")

            # Create a layer file from the scratch workspace
            new_group_lyr = arcpy.mp.LayerFile(scratch + "\\species_group.lyrx")
            # # END OF NOTE -----------------------------------------------------------------------------------------

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
            # Apply symbology to the new EO polygon layer from old layer
            arcpy.management.ApplySymbologyFromLayer(r"{} ({})\EO_Polygon_{}".format(common_name, sci_name, speciesid),
                                                     r"SpeciesData\EO_Polygon", None, "MAINTAIN")
            aprx.save()  # save the Pro project

            # # FIND ALL RELATED RECORDS THAT NEED TO BE PROCESSED .....................................................
            # Assign sql query variable related to the species id
            speciesid_sql = "speciesid = {}".format(speciesid)

            # Check to see if the initial selected record is a full species or an infraspecies
            # If the user selects a full species, process all sub/infraspecies for this species
            if s_level.lower() == "species":
                arcpy.AddMessage("Full species selected. Process all infraspecies (if they exist).")

                # Select matching record from Species table for the initial full species record in Biotics
                species_records = arcpy.management.SelectLayerByAttribute("Species",
                                                                          "NEW_SELECTION",
                                                                          speciesid_sql)

                """Use logic to select all sub/infraspecies records for this full species by comparing and matching the 
                element_code for the full species from Biotics to the fullspecies_elementcode for the infraspecies
                records in Species table."""

                # Select records from Species table where fullspecies_elementcode matches the element_code from Biotics
                species_records = arcpy.management.SelectLayerByAttribute("Species",
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

                # # Get a count of the # of species records to be processed [WILL BECOME OBSOLETE]
                # count = int(arcpy.GetCount_management(species_records).getOutput(0))
                # arcpy.AddMessage("{} species records selected (full species & infraspecies)".format(count))

            # If the user selects a subspecies/population/variety, check to see if they want the full species too
            elif s_level.lower() in ("subspecies", "population", "variety"):

                # Check if user wants to select the infraspecies & full species [based on param_infraspecies]
                # Logic to select additional records based on element_code
                if param_infraspecies == "Yes":

                    # Select initial record from Species table based on the speciesid
                    species_records = arcpy.management.SelectLayerByAttribute("Species",
                                                                              "NEW_SELECTION",
                                                                              speciesid_sql)

                    # # Get count of selected records
                    # count = int(arcpy.GetCount_management(species_records).getOutput(0))
                    # arcpy.AddMessage("{} species records selected (infraspecies)".format(count))

                    """Use logic to select the full species records for this infraspecies by comparing and matching the 
                    fullspecies_elementcode for the selected infraspecies record in Species table to the element_code
                    for the full species in Biotics."""

                    # Create a search cursor to get the fullspecies_elementcode from the Species table
                    with arcpy.da.SearchCursor("Species",
                                               ["fullspecies_elementcode"],
                                               speciesid_sql) as species_cursor:

                        for species_row in species_cursor:
                            fs_elementcode = species_row[0]  # get the fullspecies_elementcode [singular value]

                    # Add the full species record to the selected infraspecies record in the Species table
                    species_records = arcpy.management.SelectLayerByAttribute("Species",
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

                    # # Get count of selected records (should equal count + 1) [WILL BECOME OBSOLETE]
                    # count = int(arcpy.GetCount_management(species_records).getOutput(0))
                    # arcpy.AddMessage("{} species records selected (after adding full species).".format(count))

                # Logic if user only wants to process the single infraspecies by itself
                else:
                    pass  # Do nothing, record is already processed

                    # speciesid_list.append(speciesid)  # Append ORIGINAL speciesid to the list

                    # # Select initial record from Species table based on the speciesid [WILL BECOME REDUNDANT?]
                    # species_records = arcpy.management.SelectLayerByAttribute("Species",
                    #                                                           "NEW_SELECTION",
                    #                                                           speciesid_sql)
                    #
                    # # Get count of selected record [WILL BECOME OBSOLETE]
                    # count = int(arcpy.GetCount_management(species_records).getOutput(0))
                    # arcpy.AddMessage("{} species records selected (infraspecies only)".format(count))

            """ This is where you end up if you select a full species; if you select an infraspecies and
                param_infraspecies == "Yes"; or if you select an infraspecies and param_infraspecies == "No".
                Check to see if there are additional species records to process and create output layers as needed."""

            # Delete the old variables from the biotics record
            del speciesid, element_code, s_level, sci_name, common_name

            # PROCESS THE ADDITIONAL RECORDS USING THE SPECIESID_LIST [METHOD 2 - IMPLEMENTED]
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
                    with arcpy.da.SearchCursor(param_table,
                                               biotics_fields) as new_biotics_cursor:

                        for row in new_biotics_cursor:
                            arcpy.AddMessage("Processing species id: {}.".format(row[0]))

                            # Assign relevant variables from the biotics record
                            s_level = row[2]
                            sci_name = row[3]
                            common_name = row[4]

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
                            # # Apply symbology to the new EO polygon layer from old layer
                            # arcpy.management.ApplySymbologyFromLayer(
                            #     r"{} ({})\EO_Polygon_{}".format(common_name, sci_name, speciesid),
                            #     r"SpeciesData\EO_Polygon", None, "MAINTAIN")

                    aprx.save()  # save the Pro project for the freshly processed species record

                aprx.save()  # save the Pro project after processing all additional species

            # # Check to see how many records are selected in the Species table [METHOD 1]
            # # If count == 1 then you are only processing the original record selected in BIOTICS
            # if count == 1:  # Process single species [WRITE A FUNCTION TO DO THIS PROCESSING]
            #     arcpy.AddMessage("{} records selected.".format(count))
            #
            #     # The information about the species is from the original Biotics record cause count == 1
            #     # Naming convention for output group layer: Common Name (Scientific Name)
            #     group_lyr_name = "{} ({})".format(common_name, sci_name)
            #     arcpy.AddMessage("Processing {} ...".format(group_lyr_name))
            #
            #     # # NOTE: YOU ONLY WANT TO DO THIS LOGIC ONCE! -------------------------------------------------------
            #     # Get the existing SpeciesDate group layer as a layer object
            #     group_lyr = m.listLayers("SpeciesData")[0]
            #
            #     # Write a copy of the SpeciesData group layer to the user's scratch folder
            #     arcpy.SaveToLayerFile_management(group_lyr, scratch + "\\species_group.lyrx")
            #
            #     # Create a layer file from the scratch workspace
            #     new_group_lyr = arcpy.mp.LayerFile(scratch + "\\species_group.lyrx")
            #     # # END OF NOTE --------------------------------------------------------------------------------------
            #
            #     # Add the SpeciesData group layer to the TOC
            #     m.addLayer(new_group_lyr, "TOP")
            #
            #     # Rename the newly added group layer, because layer was added at top, index reference is still [0]
            #     group_lyr = m.listLayers("SpeciesData")[0]
            #     group_lyr.name = group_lyr_name  # rename the group layer in TOC
            #     group_lyr = m.listLayers(group_lyr_name)[0]
            #
            #     group_lyr.isVisible = False  # turn off the visibility for the group layer
            #     aprx.save()  # save the Pro project
            #
            #     """Decide on the logic to process the points/lines/polygons.
            #
            #     Do I want to remove the sub-layers from the renamed group layer and re-add them based on sql queries?
            #     Or do I want to try and manipulate the data that is already loaded in the points/lines/polygons layers?
            #
            #     Do you lose the relationships if the data is added fresh? That will influence the decision."""
            #
            #     # Naming conventions for point/line/polygon layers = InputPoint_SpeciesID
            #     point_lyr_name = "InputPoint_{}".format(speciesid)
            #     line_lyr_name = "InputLine_{}".format(speciesid)
            #     poly_lyr_name = "InputPolygon_{}".format(speciesid)
            #     eo_lyr_name = "EO_Polygon_{}".format(speciesid)
            #
            #     # Process the point layer - THIS WORKS!!!
            #     point_lyr = m.listLayers("InputPoint")[0]
            #     # # Make a new feature layer with sql query and added .getOutput(0) function
            #     # new_lyr = arcpy.MakeFeatureLayer_management(point_lyr,
            #     #                                             point_lyr_name,
            #     #                                             "speciesid = {}".format(speciesid),
            #     #                                             None).getOutput(0)
            #     # # Add the new point layer
            #     # m.addLayerToGroup(group_lyr, new_lyr, "TOP")
            #     # m.removeLayer(point_lyr)  # remove old point layer
            #
            #     # call the create_lyr function using the current layer
            #     Tool.create_lyr(current_lyr=point_lyr)
            #
            #     # # Iterate through the 4 feature classes and start making data layers
            #     # points = arcpy.management.SelectLayerByAttribute(r"SpeciesData\InputPoint",
            #     #                                                  "NEW_SELECTION",
            #     #                                                  speciesid_sql)
            #     #
            #     # lines = arcpy.management.SelectLayerByAttribute(r"SpeciesData\InputLine",
            #     #                                                 "NEW_SELECTION",
            #     #                                                 speciesid_sql)
            #     #
            #     # polygons = arcpy.management.SelectLayerByAttribute(r"SpeciesData\InputPolygon",
            #     #                                                    "NEW_SELECTION",
            #     #                                                    speciesid_sql)
            #     #
            #     # eo_polygons = arcpy.management.SelectLayerByAttribute(r"SpeciesData\EO_Polygon",
            #     #                                                       "NEW_SELECTION",
            #     #                                                       speciesid_sql)
            #     #
            #     # eo_count = int(arcpy.GetCount_management(eo_polygons).getOutput(0))
            #     # arcpy.AddMessage("{} record selected from EO_Polygon table.".format(eo_count))
            #
            #     # # ................................................................................................
            #     # # List the existing layer that you want to duplicate
            #     # copy_lyr = m.listLayers('EO_Polygon')[0]
            #     #
            #     # # Create the output layer name
            #     # lyr_name = "{} - SpeciesID {}".format(copy_lyr.name, speciesid)
            #     # arcpy.AddMessage(lyr_name)
            #     #
            #     # # Make a new feature layer with added .getOutput(0) function
            #     # new_lyr = arcpy.MakeFeatureLayer_management(copy_lyr, lyr_name, speciesid_sql, None).getOutput(0)
            #     #
            #     # # Add the new layer to the new group layer in the map & turn off visibility
            #     # m.addLayer(new_lyr)  # Works
            #     # new_lyr.isVisible = False  # not clear if this does anything
            #     #
            #     # # Save the project
            #     # aprx.save()
            #     # # ................................................................................................
            #
            #     # m.addLayerToGroup(new_group_lyr, new_lyr, "TOP") # Doesn't work yet
            #     # aprx.save()
            #
            #     # # Add the layer to an existing group
            #     # m.addLayerToGroup(group_lyr, lyr, "TOP")
            #
            #     # Move layer in the TOC?
            #
            #     # # Save the project
            #     # aprx.save()
            #
            # elif count > 1:  # Process species & infraspecies
            #     arcpy.AddMessage("{} records selected.".format(count))
            #
            #     # process all of the species in the list
            #
            #     # create a new search cursor & start calling your function to do stuff
            #
            # else:
            #     # Throw an error that there are no species selected.  This will only happen if the script logic is wrong
            #     arcpy.AddError("{} records selected. Tool script logic is bad."
            #                    .format(count))

            arcpy.AddMessage("End of script.")

        # Error handling for custom input error related to the SQL statement
        except exceptions.InputError:
            arcpy.AddError("Incorrect sql statement. See Messages for more details.")

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

    param_table.value = "BIOTICS_ELEMENT_NATIONAL"
    param_sql.value = "national_scientific_name = 'Abronia umbellata'"
    param_infraspecies = "Yes"

    parameters = [param_table, param_sql, param_infraspecies]

    # Call the run_tool function using the input parameters (for the sst instance of class Tool)
    sst.run_tool(parameters, None)
