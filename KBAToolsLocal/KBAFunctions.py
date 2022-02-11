import arcpy


# Define a function to create the group layer for a selected record
def create_species_group_lyr_scoping(m, empty_grp_lyr, sp_com_name, sp_sci_name, infra_exists):
    arcpy.AddMessage("Run create_group_lyr function.")

    # Assign naming convention for output group layer in TOC based on infra & species level parameters:
    if infra_exists is True:
        # Common Name (Scientific Name) data not identified to infraspecies
        grp_lyr_name = "{} ({}) data not identified to infraspecies".format(sp_com_name, sp_sci_name)

    else:
        # Common Name (Scientific Name)
        grp_lyr_name = "{} ({})".format(sp_com_name, sp_sci_name)

    # Add an empty copy of the SpeciesData group layer to the TOC (by referencing the .lyrx file written to scratch)
    m.addLayer(empty_grp_lyr, "TOP")

    # Rename the newly added group layer, because layer was added at top index reference = [0]
    group_lyr = m.listLayers("SpeciesData")[0]
    group_lyr.name = grp_lyr_name  # rename the group layer in TOC
    group_lyr = m.listLayers(grp_lyr_name)[0]
    group_lyr.visible = False  # Turn off the visibility for the group layer

    return group_lyr


# Define a function to create the group layer for infraspecies records
def create_infraspecies_group_lyr_scoping(m, empty_grp_lyr, sp_com_name, sp_sci_name, species_grp_lyr):
    arcpy.AddMessage("Run create_group_lyr function.")

    grp_lyr_name = "{} ({})".format(sp_com_name, sp_sci_name)

    # Insert an empty copy of the SpeciesData group layer BELOW the full species group layer
    m.insertLayer(species_grp_lyr, empty_grp_lyr, "AFTER")

    # Rename the newly added group layer, because layer was added at top index reference = [0]
    group_lyr = m.listLayers("SpeciesData")[0]
    group_lyr.name = grp_lyr_name  # rename the group layer in TOC
    group_lyr = m.listLayers(grp_lyr_name)[0]
    group_lyr.visible = False  # Turn off the visibility for the group layer

    return group_lyr