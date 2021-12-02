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
import exceptions


class Tool:
    """Select all points, lines and polygons for a specific species."""
    def __init__(self):
        pass

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

            # Guaranteed to exist at run time
            scratch = arcpy.env.scratchFolder
            arcpy.AddMessage("Scratch folder: {}".format(scratch))

            # Select the record in BIOTICS table based on the user-specified sql expression
            biotics_record = arcpy.management.SelectLayerByAttribute(param_table,
                                                                     "NEW_SELECTION",
                                                                     param_sql)

            # INSERT logic to check that only one record is selected in the initial query
            biotics_count = int(arcpy.GetCount_management(biotics_record).getOutput(0))

            # if count = 0 throw error using custom exception
            if biotics_count == 0:
                arcpy.AddMessage("No records selected.")
                raise exceptions.InputError

            # if count > 1 throw error using custom exception
            elif biotics_count > 1:
                arcpy.AddMessage("More than one record selected. Please select only one record.")
                raise exceptions.InputError

            # else continue with script
            else:
                pass

            # Get record-level information about the selected Biotics record using a search cursor
            with arcpy.da.SearchCursor(param_table, biotics_fields, param_sql) as cursor:
                for row in cursor:

                    # Assign variables for row items
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

            # Exit the search cursor, keep the variables from the search cursor.

            # Check to see if the selected record is a full species or a subspecies
            if s_level.lower() == "species":
                arcpy.AddMessage("Full species selected. Process all infraspecies (if they exist).")
                # arcpy.AddMessage("Species ID = {}".format(speciesid))
                # arcpy.AddMessage("speciesid = {}".format(speciesid))

                # Select record from species table for the full species
                species_records = arcpy.management.SelectLayerByAttribute("Species",
                                                                          "NEW_SELECTION",
                                                                          "speciesid = {}".format(
                                                                              speciesid))

                # Add logic to select all infraspecies records for this full species
                # Compare and match element_code to records in Species table
                # Select records from Species table where fullspecies_elementcode matches the element_code
                species_records = arcpy.management.SelectLayerByAttribute("Species",
                                                                          "ADD_TO_SELECTION",
                                                                          "fullspecies_elementcode = '{}'".format(element_code))

                count = int(arcpy.GetCount_management(species_records).getOutput(0))
                arcpy.AddMessage("{} species records selected (full species & infraspecies)".format(count))

            # If the user selects a subspecies/population/variety, check to see if they want the full species
            elif s_level.lower() in ("subspecies", "population", "variety"):

                # Check if user wants to select the infraspecies & full species [based on param_infraspecies]
                # Logic to select additional records based on element_code
                if param_infraspecies == "Yes":

                    # Select initial record from Species table based on the speciesid
                    species_records = arcpy.management.SelectLayerByAttribute("Species",
                                                                              "NEW_SELECTION",
                                                                              "speciesid = {}".format(
                                                                                  speciesid))

                    # Get count of selected records
                    count = int(arcpy.GetCount_management(species_records).getOutput(0))
                    arcpy.AddMessage("{} species records selected (infraspecies)".format(count))

                    # Create a search cursor for the Species table to get the fullspecies_elementcode
                    # from the currently selected infraspecies record
                    with arcpy.da.SearchCursor("Species",
                                               ["fullspecies_elementcode"],
                                               "speciesid = {}".format(speciesid)) as species_cursor:

                        for species_row in species_cursor:
                            fs_elementcode = species_row[0]  # get the fullspecies_element code

                    # Add the full species record to the selected infraspecies record
                    species_records = arcpy.management.SelectLayerByAttribute("Species",
                                                                              "ADD_TO_SELECTION",
                                                                              "fullspecies_elementcode = '{}'".format(fs_elementcode))

                    # Get count of selected records (should equal count + 1)
                    count = int(arcpy.GetCount_management(species_records).getOutput(0))
                    arcpy.AddMessage("{} species records selected (after adding full species).".format(count))

                # Logic if users only wants to select the single infraspecies by itself
                else:
                    # Select initial record from Species table based on the speciesid
                    species_records = arcpy.management.SelectLayerByAttribute("Species",
                                                                              "NEW_SELECTION",
                                                                              "speciesid = {}".format(
                                                                                  speciesid))
                    # Get count of selected record
                    count = int(arcpy.GetCount_management(species_records).getOutput(0))
                    arcpy.AddMessage("{} species records selected (infraspecies only)".format(count))

            """ This is where you end up if you select a full species; if you select an infraspecies and
                param_infraspecies == "Yes"; or if you select an infraspecies and param_infraspecies == "No".
                Iterate through the selected species records and create output layers in the map TOC."""

            # Check to see how many records are selected in the Species table
            # If count == 1 then you are only processing the original record selected in BIOTICS
            if count == 1:  # Process single species [WRITE A FUNCTION TO DO THIS PROCESSING]
                arcpy.AddMessage("{} records selected.".format(count))

                # The information about the species is from the original Biotics record cause count == 1
                # Naming convention for output group layer: Common Name (Scientific Name)
                group_lyr_name = "{} ({})".format(common_name, sci_name)
                arcpy.AddMessage("Processing {} ...".format(group_lyr_name))

                # # NOTE: YOU ONLY WANT TO DO THIS LOGIC ONCE! -------------------------------------------------------
                # Get the existing SpeciesDate group layer as a layer object
                group_lyr = m.listLayers("SpeciesData")[0]

                # Write a copy of the SpeciesData group layer to the user's scratch folder
                arcpy.SaveToLayerFile_management(group_lyr, scratch + "\\species_group.lyrx")

                # Create a layer file from the scratch workspace
                new_group_lyr = arcpy.mp.LayerFile(scratch + "\\species_group.lyrx")
                # # END OF NOTE --------------------------------------------------------------------------------------

                # Add the SpeciesData group layer to the TOC
                m.addLayer(new_group_lyr, "TOP")

                # Rename the newly added group layer, because layer was added at top, index reference is still [0]
                group_lyr = m.listLayers("SpeciesData")[0]
                group_lyr.name = group_lyr_name

                group_lyr.isVisible = False  # turn off the visibility for the group layer
                aprx.save()  # save the Pro project

                """Decide on the logic to process the points/lines/polygons. 
                
                Do I want to remove the sub-layers from the renamed group layer and re-add them based on sql queries? 
                Or do I want to try and manipulate the data that is already loaded in the points/lines/polygons layers?
                
                Do you lose the relationships if the data is added fresh? That will influence the decision."""

                # # Iterate through the 4 feature classes and start making data layers
                # points = arcpy.management.SelectLayerByAttribute(r"SpeciesData\InputPoint",
                #                                                  "NEW_SELECTION",
                #                                                  speciesid_sql)
                #
                # lines = arcpy.management.SelectLayerByAttribute(r"SpeciesData\InputLine",
                #                                                 "NEW_SELECTION",
                #                                                 speciesid_sql)
                #
                # polygons = arcpy.management.SelectLayerByAttribute(r"SpeciesData\InputPolygon",
                #                                                    "NEW_SELECTION",
                #                                                    speciesid_sql)
                #
                # eo_polygons = arcpy.management.SelectLayerByAttribute(r"SpeciesData\EO_Polygon",
                #                                                       "NEW_SELECTION",
                #                                                       speciesid_sql)
                #
                # eo_count = int(arcpy.GetCount_management(eo_polygons).getOutput(0))
                # arcpy.AddMessage("{} record selected from EO_Polygon table.".format(eo_count))

                # # ................................................................................................
                # # List the existing layer that you want to duplicate
                # copy_lyr = m.listLayers('EO_Polygon')[0]
                #
                # # Create the output layer name
                # lyr_name = "{} - SpeciesID {}".format(copy_lyr.name, speciesid)
                # arcpy.AddMessage(lyr_name)
                #
                # # Make a new feature layer with added .getOutput(0) function
                # new_lyr = arcpy.MakeFeatureLayer_management(copy_lyr, lyr_name, speciesid_sql, None).getOutput(0)
                #
                # # Add the new layer to the new group layer in the map & turn off visibility
                # m.addLayer(new_lyr)  # Works
                # new_lyr.isVisible = False  # not clear if this does anything
                #
                # # Save the project
                # aprx.save()
                # # ................................................................................................

                # m.addLayerToGroup(new_group_lyr, new_lyr, "TOP") # Doesn't work yet
                # aprx.save()

                # # Add the layer to an existing group
                # m.addLayerToGroup(group_lyr, lyr, "TOP")

                # Move layer in the TOC?

                # # Save the project
                # aprx.save()

            elif count > 1:  # Process species & infraspecies
                arcpy.AddMessage("{} records selected.".format(count))

                # process all of the species in the list

                # create a new search cursor & start calling your function to do stuff

            else:
                # Throw an error that there are no species selected.  This will only happen if the script logic is wrong
                arcpy.AddError("{} records selected. Tool script logic is bad."
                               .format(count))

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
    sst = Tool()

    # Hard-coded parameters for debugging
    param_table = arcpy.Parameter()
    param_sql = arcpy.Parameter()
    param_infraspecies = arcpy.Parameter()

    param_table.value = "BIOTICS_ELEMENT_NATIONAL"
    param_sql.value = "national_scientific_name = 'Abronia umbellata'"
    param_infraspecies = "Yes"

    parameters = [param_table, param_sql, param_infraspecies]

    # Run the tool using the parameters
    sst.run_tool(parameters, None)
