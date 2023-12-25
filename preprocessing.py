import numpy as np
import pandas as pd
from textwrap import wrap
from visualisation_enums import VisualisationEnums


# We are going to connect points for each division (1,2,3), but also each direction in each division ("A" or "R")
# We need to duplicate points with a direction of "A" to also have an identical point with direction "R"
# This is so all points are connected, and there is no gaps between when it goes from direction "A" to "R"
def duplicate_opposite_direction_at_change(map_of_survivors_data):
    connected_survivor_data = []
    for index, row in map_of_survivors_data.iterrows():
        connected_survivor_data.append(row)
        # If the direction is "A" and the next point has "R", add a copy of the next point with direction "A" too
        if (row["DIR"] == "A" and index < len(map_of_survivors_data) - 1
                and map_of_survivors_data.at[index + 1, "DIR"] == "R"):
            next_row = map_of_survivors_data.loc[index + 1].copy()
            next_row["DIR"] = "A"
            connected_survivor_data.append(next_row)

    return pd.DataFrame(connected_survivor_data)


# We need each division to have a distinct color, and a lighter version of the color for when they retreat
def set_colour_conditions_for_each_division_and_direction(map_of_survivors_data):
    # Set initial color to nothing and specify color based on the division and direction in each point
    map_of_survivors_data["color"] = None
    # Color for division 1 (Golden advance "A", orange retreat "R")
    map_of_survivors_data.loc[
        (map_of_survivors_data["DIV"] == 1) & (map_of_survivors_data["DIR"] == "A"), "color"] = (
        VisualisationEnums.Gold.value[0])
    map_of_survivors_data.loc[
        (map_of_survivors_data["DIV"] == 1) & (map_of_survivors_data["DIR"] == "R"), "color"] = (
        VisualisationEnums.Orange.value[0])

    # Colors for division 2 (Dark green advance "A", light green retreat "R")
    map_of_survivors_data.loc[
        (map_of_survivors_data["DIV"] == 2) & (map_of_survivors_data["DIR"] == "A"), "color"] = (
        VisualisationEnums.DarkGreen.value[0])
    map_of_survivors_data.loc[
        (map_of_survivors_data["DIV"] == 2) & (map_of_survivors_data["DIR"] == "R"), "color"] = (
        VisualisationEnums.LightGreen.value[0])

    # Colors for division 3 (Dark blue advance "A", light blue retreat "R")
    map_of_survivors_data.loc[
        (map_of_survivors_data["DIV"] == 3) & (map_of_survivors_data["DIR"] == "A"), "color"] = (
        VisualisationEnums.DarkBlue.value[0])
    map_of_survivors_data.loc[
        (map_of_survivors_data["DIV"] == 3) & (map_of_survivors_data["DIR"] == "R"), "color"] = (
        VisualisationEnums.LightBlue.value[0])

    return pd.DataFrame(map_of_survivors_data)


# We only need survivor data from every third row, so we don't bombard the chart with too much text
# Also, we need to position the y value of the text a little up or down based on a direction of "A" or "R"
# Finally, we don't want any 2 texts being too close to each other, so we can remove any new points that are too close
def process_survivor_count_for_plotting_text(map_of_survivors_data):
    # Get survivor count from every third row
    survivor_count_from_every_third_row = map_of_survivors_data.iloc[np.arange(0, len(map_of_survivors_data), 3)].copy()
    # Move the text up or down depending on the direction of the army
    survivor_count_from_every_third_row["LATP"] = survivor_count_from_every_third_row["LATP"] + np.where(
        survivor_count_from_every_third_row["DIR"] == "A", 0.22, -0.25)
    # Remove any text that will be too close to existing texts
    survivor_text_with_close_text_removed = []
    for i in range(len(survivor_count_from_every_third_row)):
        too_close = False
        for x in range(len(survivor_text_with_close_text_removed)):
            difference_in_x = (survivor_text_with_close_text_removed[x]["LONP"] -
                               survivor_count_from_every_third_row.iloc[i]["LONP"])
            difference_in_y = (survivor_text_with_close_text_removed[x]["LATP"] -
                               survivor_count_from_every_third_row.iloc[i]["LATP"])
            distance_between_texts = np.sqrt(difference_in_x ** 2 + difference_in_y ** 2)
            # If any new text is too close to an existing one, we don't keep this
            if distance_between_texts < 0.2:
                too_close = True
                break
        if not too_close:
            survivor_text_with_close_text_removed.append(survivor_count_from_every_third_row.iloc[i])

    return pd.DataFrame(survivor_text_with_close_text_removed)


# We want to display labels for each temperature point containing the temperature and the date it was recorded
# If the date is missing, then we have to only use the temperature recording as the label
def create_labels_for_temperature_points(temperatures):
    # Any NaN values in "MON" and "DAY" can be filled with zeros to avoid errors, we will check for this later
    temperatures["MON"] = temperatures["MON"].fillna("0")
    temperatures["DAY"] = temperatures["DAY"].fillna("0")
    # Change "DAY" from an object to a string, so it can be used in concatenation later
    temperatures["DAY"] = temperatures["DAY"].astype(str)

    # Put the temperature and date below it if it exists
    temperatures["temperature_text"] = np.where(
        (temperatures["DAY"].astype(float).astype(int).astype(str) == "0") & (temperatures["MON"] == "0"),
        temperatures["TEMP"].astype(str) + "°", temperatures["TEMP"].astype(str) + "° " +
        temperatures["DAY"].astype(float).astype(int).astype(str) + " " + temperatures["MON"]).tolist()
    temperatures["temperature_text"] = temperatures["temperature_text"].apply(wrap, args=[6])

    return pd.DataFrame(temperatures)
