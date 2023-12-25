import altair as alt
from preprocessing import *
from visualisation_enums import VisualisationEnums


# Create a chart of survivors
def create_chart_of_survivors(minard_data):
    # Get the survivor data and process it
    map_of_survivors_data = minard_data.loc[:, ["LONP", "LATP", "SURV", "DIR", "DIV"]]
    map_of_survivors_data = map_of_survivors_data.sort_values(ascending=False, by=["DIV", "SURV"])
    map_of_survivors_data = duplicate_opposite_direction_at_change(map_of_survivors_data)
    map_of_survivors_data = set_colour_conditions_for_each_division_and_direction(map_of_survivors_data)

    # Create a chart of survivors
    troops_chart = alt.Chart(map_of_survivors_data, title=wrap("Prathamesh's recreation of Minard's visualisation of "
                                                               "Napolean’s Russian Campaign", 49)).mark_trail().encode(
        tooltip=[alt.Tooltip("DIR", title="Direction"), alt.Tooltip("SURV", title="Survivors"),
                 alt.Tooltip("LONP", title="Longitude"), alt.Tooltip("LATP", title="Latitude")],
        detail="DIV", latitude="LATP", longitude="LONP", color=alt.Color("color", scale=None),
        size=alt.Size("SURV", scale=alt.Scale(range=[1, 35]), legend=None),
    )

    return troops_chart


# Create chart of city positions
def create_chart_of_city_positions(minard_data, chart):
    # Get the city data
    map_of_cities_data = minard_data[["LONC", "LATC", "CITY"]].dropna()

    # Create a chart of circles where cities are positioned
    cities_chart_circle = alt.Chart(map_of_cities_data).mark_circle(size=40, color="#000000").encode(
        tooltip=[alt.Tooltip("CITY", title="City"), alt.Tooltip("LONC", title="Longitude"),
                 alt.Tooltip("LATC", title="Latitude")], latitude="LATC", longitude="LONC")

    # Create a chart of text where cities are positioned
    cities_chart_text = alt.Chart(map_of_cities_data).mark_text(dy=10, fontStyle="bold", font='Courier New', fontSize=11
                                                                ).encode(text="CITY", latitude="LATC",
                                                                         longitude="LONC")

    # Combine the circles and text to represent where cities are located
    chart = chart + cities_chart_circle + cities_chart_text

    return chart


# Plot the number of troops continuously along the trail
def plot_troop_numbers(minard_data, chart):
    # Get the survivor data and process it
    map_of_survivors_data = minard_data.loc[:, ["LONP", "LATP", "SURV", "DIR", "DIV"]]
    map_of_survivors_data = process_survivor_count_for_plotting_text(map_of_survivors_data)

    # Create a chart with various texts representing the number of troops
    troops_text_chart = alt.Chart(map_of_survivors_data).mark_text(dx=-5, dy=-2, fontStyle="oblique", fontSize=9,
                                                                   angle=320).encode(longitude="LONP",
                                                                                     latitude="LATP", text="SURV")

    # Append the text on top of the existing chart
    chart = chart + troops_text_chart

    return chart


# Create a chart with temperatures during the army retreat
def create_chart_of_temperatures_during_retreat(minard_data):
    # Get the temperature data and process it
    temperatures = minard_data[["LONT", "TEMP", "DAYS", "MON", "DAY"]].dropna(how="all")
    temperatures = create_labels_for_temperature_points(temperatures)

    # Get the survivor data
    map_of_survivors_data = minard_data[["LONP", "LATP", "SURV", "DIR", "DIV"]]

    # Create chart with temperature text
    temperature_text = alt.Chart(temperatures).mark_text(
        dx=3, dy=20, font="Courier New", fontSize=10, fontStyle="bold").encode(
        x=alt.X("LONT", axis=None, scale=alt.Scale(domain=[map_of_survivors_data["LONP"].min(),
                                                           map_of_survivors_data["LONP"].max()])),
        y=alt.Y("TEMP", axis=alt.Axis(orient="right", grid=True, title="Temperature during retreat (Réaumur)",
                                      offset=25), scale=alt.Scale(domain=[temperatures["TEMP"].min(),
                                                                          temperatures["TEMP"].max()])),
        text="temperature_text",
    )

    # Create chart with temperature points
    temperature_points = alt.Chart(temperatures).mark_circle(size=50, color="#000000").encode(
        tooltip=[alt.Tooltip("TEMP", title="Temperature"), alt.Tooltip("LONT", title="Longitude")],
        x=alt.X("LONT", axis=None, scale=alt.Scale(domain=[map_of_survivors_data["LONP"].min(),
                                                           map_of_survivors_data["LONP"].max()])),
        y=alt.Y("TEMP", axis=alt.Axis(orient="right", grid=True, title="Temperature during retreat (Réaumur)",
                                      offset=25), scale=alt.Scale(domain=[temperatures["TEMP"].min(),
                                                                          temperatures["TEMP"].max()])),
    )

    # Create chart with temperature lines
    temperature_lines = alt.Chart(temperatures).mark_line(color="#000000").encode(
        x=alt.X("LONT", axis=None, scale=alt.Scale(domain=[map_of_survivors_data["LONP"].min(),
                                                           map_of_survivors_data["LONP"].max()])),
        y=alt.Y("TEMP", axis=alt.Axis(orient="right", grid=True, title="Temperature during retreat (Réaumur)",
                                      offset=25), scale=alt.Scale(domain=[temperatures["TEMP"].min(),
                                                                          temperatures["TEMP"].max()])))

    # Combine all three charts to make one temperature chart with text, points, and lines connecting the points
    temperature_chart = temperature_points + temperature_text + temperature_lines

    return temperature_chart.properties(height=200)


# Create vertical red dotted lines to add to the survivor chart
def create_vertical_lines_for_survivors_plot(minard_data):
    # Get the data and add the missing connection points between the longitude of temperatures to latitude of cities
    longitude_of_survivor_points_ = minard_data[["LONT"]].drop_duplicates()
    longitude_of_survivor_points_["LONT_TO_LATC"] = [55.65, 55.05, 54.73, 54.55, 54.33, 54.20, 54.43, 54.3, 54.4, 0]

    # Add vertical red dotted lines to points during the army retreat
    vertical_lines_for_survivors = (
        alt.Chart(longitude_of_survivor_points_).mark_rule(strokeDash=[5, 5], color="red")
        .encode(size=alt.value(1),
                x=alt.X("LONT", axis=None,
                        scale=alt.Scale(domain=[minard_data["LONP"].min(),
                                                minard_data["LONP"].max()])),
                y=alt.Y("LONT_TO_LATC", axis=None,
                        scale=alt.Scale(domain=[minard_data["LATC"].min() - 1.25,
                                                minard_data["LATC"].max() + 1.25]))))
    return vertical_lines_for_survivors


# Create vertical red dotted lines to add to the temperature chart
def create_vertical_lines_for_temperature_plot(minard_data):
    # Create a DataFrame with unique combinations of "lon" and "temperature" points
    longitude_of_temperature_points_ = minard_data[["LONT", "TEMP"]].drop_duplicates()

    # Add vertical red dotted lines from the temperature points
    vertical_lines_for_temperature = (
        alt.Chart(longitude_of_temperature_points_).mark_rule(strokeDash=[5, 5], color="red")
        .encode(size=alt.value(1),
                x=alt.X("LONT", axis=None, scale=alt.Scale(domain=[minard_data["LONP"].min(),
                                                                   minard_data["LONP"].max()])),
                y=alt.Y("TEMP")))
    return vertical_lines_for_temperature


def create_legend():
    legend_content = pd.DataFrame({
        "colors": [
            VisualisationEnums.Gold.value,
            VisualisationEnums.Orange.value,
            VisualisationEnums.DarkGreen.value,
            VisualisationEnums.LightGreen.value,
            VisualisationEnums.DarkBlue.value,
            VisualisationEnums.LightBlue.value
        ],
        "color_label": [
            "Division 1 (Advance)",
            "Division 1 (Retreat)",
            "Division 2 (Advance)",
            "Division 2 (Retreat)",
            "Division 3 (Advance)",
            "Division 3 (Retreat)"]
    })

    # Find coordinates to center the legend horizontally
    x_value = (VisualisationEnums.PlotWidth.value[0] - VisualisationEnums.LegendWidth.value[0]) / 2
    x2_value = x_value + VisualisationEnums.LegendWidth.value[0]

    # Create rectangles corresponding to colors used in the plot
    colored_rectangles_in_legend = alt.Chart(legend_content).mark_rect(xOffset=30, yOffset=70).encode(
        y=alt.Y("color_label", axis=None), color=alt.Color("colors", scale=None), text="color_label",
        x=alt.value(x_value), x2=alt.value(x_value + 10)
    ).properties(width=20, height=alt.Step(25))

    # Create text to show what each color in the plot represents
    colored_text_in_legend = (
        alt.Chart(legend_content).mark_text(dx=x_value + 105, dy=70, fontStyle="bold", fontSize=15,
                                            stroke="black", strokeWidth=0.4)
        .encode(y=alt.Y("color_label", axis=None), color=alt.Color("colors", scale=None),
                text="color_label").properties(width=20, height=alt.Step(25)))

    # Create a title for the legend
    legend_title_text = alt.Chart(pd.DataFrame({"title": ["Legend"]})).mark_text(
        dx=x_value + 85, dy=-25, fontSize=35, font="Brush Script MT", fontStyle="bold").encode(text="title")

    # Create a black outline to the box that represents the legend
    legend_black_outline_stroke = alt.Chart(pd.DataFrame({"": [None]})).mark_rect(stroke="black", strokeWidth=2,
                                                                                  opacity=0.2).encode(
        x=alt.value(x_value), x2=alt.value(x2_value), y=alt.value(30), y2=alt.value(230))

    # Combine all elements to make the legend
    legend = colored_rectangles_in_legend + colored_text_in_legend + legend_title_text + legend_black_outline_stroke
    return legend


# Plotting my recreation of Minard's visualization of Napolean's Russian Campaign :)
def main():
    # Read the xlsx file and plot the path of the army with their size, city positions, and temperature during retreat
    minard_data = pd.read_excel("Napoleon-Russian-Campaign.xlsx", header=0)
    survivors_plot = create_chart_of_survivors(minard_data)
    survivors_plot = create_chart_of_city_positions(minard_data, survivors_plot)
    survivors_plot = plot_troop_numbers(minard_data, survivors_plot)
    temperature_plot = create_chart_of_temperatures_during_retreat(minard_data)

    # Create vertical red dotted lines between the temperature points and the points during the army retreat
    vertical_lines_for_survivors = create_vertical_lines_for_survivors_plot(minard_data)
    vertical_lines_for_temperature = create_vertical_lines_for_temperature_plot(minard_data)
    survivors_plot = alt.layer(vertical_lines_for_survivors, survivors_plot)
    temperature_plot = alt.layer(vertical_lines_for_temperature, temperature_plot)

    # Create a legend that corresponds to the colors in our chart
    legend_chart = create_legend()

    # Combine the survivors plot, temperature plot and the legend vertically
    chart = (alt.vconcat(survivors_plot, temperature_plot, legend_chart).configure_concat(spacing=-20)
             .configure_view(continuousWidth=VisualisationEnums.PlotWidth.value[0],
                             continuousHeight=VisualisationEnums.PlotHeight.value[0],
                             stroke="transparent").configure_axis(grid=True, labelFont="Courier New",
                                                                  titleFont="Courier New")
             .configure_title(font="Brush Script MT", fontSize=50, offset=-140))

    # Save to html to view in web browser and download page as PDF (avoiding altair-saver pip package)
    chart.save(embed_options={"actions": False}, fp="Prathamesh-Minard-Visualisation.html")


if __name__ == "__main__":
    main()
