import os
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

def plot_portioning_visualization(cross_sectional_areas, slice_thickness, density, portions, waste_portion, include_waste):
    # Calculate slice weights and cumulative values
    slice_weights = [area * slice_thickness * density for area in cross_sectional_areas]
    n = len(cross_sectional_areas)
    cum_length = np.arange(1, n + 1) * slice_thickness  # in mm
    cum_weight = np.cumsum(slice_weights)               # in grams

    # Total loaf length from the integration curve
    total_loaf_length = cum_length[-1]

    # Create a figure with two subplots (stacked vertically)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    plt.tight_layout(pad=4)

    # --- Subplot 1: Cumulative Integration Plot ---
    ax1.plot(cum_length, cum_weight, label="Cumulative Weight (g)", marker="o", color="blue")
    
    # Mark portion boundaries on the cumulative plot.
    for (start, end, portion_length, portion_weight) in portions:
        # Use the end index to define the cut (assuming the slice index is 0-based).
        cut_position = (end + 1) * slice_thickness
        ax1.axvline(cut_position, color="red", linestyle="--", alpha=0.7)
        # Optionally, annotate the portion on the curve.
        mid_position = (start * slice_thickness + cut_position) / 2
        # Find cumulative weight at end index (or last if out of range)
        weight_at_cut = cum_weight[end] if end < len(cum_weight) else cum_weight[-1]
        ax1.text(mid_position, weight_at_cut, 
                 f"P{portions.index((start, end, portion_length, portion_weight)) + 1}\n{portion_weight:.1f}g",
                 ha="center", va="bottom", fontsize=9, rotation=45)
    
    ax1.set_xlabel("Cumulative Length (mm)")
    ax1.set_ylabel("Cumulative Weight (g)")
    ax1.set_title("Cumulative Integration with Portion Cuts")
    ax1.legend()
    ax1.grid(True)

    # --- Subplot 2: Schematic Loaf Diagram ---
    # Draw the overall loaf as a light blue rectangle.
    # Here we fix the height of the schematic to, say, 50 mm.
    schematic_height = 50
    ax2.add_patch(Rectangle((0, 0), total_loaf_length, schematic_height,
                            edgecolor="black", facecolor="lightblue"))
    
    # Now, overlay each portion as an orange segment.
    current_x = 0
    for i, (start, end, portion_length, portion_weight) in enumerate(portions):
        # Draw the portion as a rectangle
        ax2.add_patch(Rectangle((current_x, 0), portion_length, schematic_height,
                                edgecolor="black", facecolor="orange", alpha=0.7))
        # Annotate the portion in the center
        mid_x = current_x + portion_length / 2
        ax2.text(mid_x, schematic_height / 2, 
                 f"P{i+1}\n{portion_weight:.1f}g\n{portion_length:.1f}mm",
                 ha="center", va="center", fontsize=9, rotation=45, color="black")
        current_x += portion_length

    # If there's waste and it is not included, show it as a red segment.
    if waste_portion and not include_waste:
        waste_length = waste_portion[2]
        ax2.add_patch(Rectangle((current_x, 0), waste_length, schematic_height,
                                edgecolor="black", facecolor="red", alpha=0.5))
        mid_x = current_x + waste_length / 2
        ax2.text(mid_x, schematic_height / 2,
                 f"Waste\n{waste_portion[3]:.1f}g",
                 ha="center", va="center", fontsize=9, color="white", rotation=45)
        current_x += waste_length

    # Set limits and title for schematic
    ax2.set_xlim(0, total_loaf_length)
    ax2.set_ylim(0, schematic_height)
    ax2.set_title("Schematic Cheese Loaf with Portioning")
    ax2.set_xlabel("Loaf Length (mm)")
    ax2.axis("off")  # Hide axis lines and labels for a cleaner schematic


# UK three packers rule - https://www.stevenstraceability.com/average-weight-explained/
# TNE Calculation Based on TNE Table
def get_tne(nominal_weight):
    if 5 <= nominal_weight <= 50:
        return nominal_weight * 0.09  # 9% of nominal weight
    elif 50 < nominal_weight <= 100:
        return 4.5  # Fixed 4.5 g
    elif 100 < nominal_weight <= 200:
        return nominal_weight * 0.045  # 4.5%
    elif 200 < nominal_weight <= 300:
        return 9  # Fixed 9 g
    elif 300 < nominal_weight <= 500:
        return nominal_weight * 0.03  # 3%
    elif 500 < nominal_weight <= 1000:
        return 15  # Fixed 15 g
    elif 1000 < nominal_weight <= 10000:
        return nominal_weight * 0.015  # 1.5%
    elif 10000 < nominal_weight <= 15000:
        return 150  # Fixed 150 g
    elif nominal_weight > 15000:
        return nominal_weight * 0.01  # 1%
    else:
        return 0

def calculate():
    try:

        global target_portion_weight
        global include_waste
        global current_weight
        global waste
        global waste_portion
        global t1_tolerance
        global t2_tolerance

        # Get inputs
        total_weight = float(total_weight_var.get())
        slice_thickness = float(slice_thickness_var.get())
        target_portion_weight = float(target_portion_weight_var.get())
        average_width = float(average_width_var.get())
        average_height = float(average_height_var.get())
        number_of_length_cross_sections = int(number_of_slices_var.get())
        include_waste = include_waste_var.get()
        tolerance = tolerance_var.get() / 100

        # Generate cross-sectional areas
        cross_sectional_areas = [
            (random.gauss(average_width, 2)) * (random.gauss(average_height, 2))
            for _ in range(number_of_length_cross_sections)
        ]

        # Calculate density using rectangular rule
        #total_volume = sum(area * slice_thickness for area in cross_sectional_areas)
        #density = total_weight / total_volume

        # Suppose cross_sectional_areas is a list of the areas for each slice.
        # Calculate volume using the trapezoidal rule:
        volumes = [(slice_thickness / 2) * (cross_sectional_areas[i] + cross_sectional_areas[i+1])
            for i in range(len(cross_sectional_areas) - 1)]

        total_volume = sum(volumes)
        density = total_weight / total_volume

        # Portion calculation
        portions = []
        current_weight = 0
        current_length = 0
        start_index = 0
        slice_weights = []

        for i, area in enumerate(cross_sectional_areas):
            slice_weight = area * slice_thickness * density
            slice_weights.append(slice_weight)

        # Calculate portions using linear interpolation
        for i, weight in enumerate(slice_weights):
            # Add the current slice's weight and thickness
            previous_weight = current_weight
            previous_length = current_length
            current_weight += weight
            current_length += slice_thickness

            # Check if adding this slice causes an overshoot
            if current_weight >= target_portion_weight * tolerance:
                # Interpolate on the current slice:
                overshoot = current_weight - (target_portion_weight * tolerance)
                # Fraction of current slice needed to reach the target
                fraction = (weight - overshoot) / weight if weight != 0 else 1
                # Adjust current_length accordingly:
                adjusted_length = previous_length + fraction * slice_thickness
                adjusted_weight = previous_weight + fraction * weight
                portions.append((start_index, i, adjusted_length, adjusted_weight))
                # Start next portion with the remaining fraction of the slice:
                remaining_fraction = 1 - fraction
                current_weight = remaining_fraction * weight
                current_length = remaining_fraction * slice_thickness
                start_index = i

        waste = current_weight

        waste_portion = None
        if waste > 0:
            waste_hypothetical = waste
            waste_portion = (start_index, len(cross_sectional_areas) - 1, current_length, waste)

            if include_waste:
                redistributed_weight = waste / len(portions)
                new_portions = []
                for start, end, length, weight in portions:
                    # If weight increases by redistributed_weight, then length should increase by:
                    # extra_length = (redistributed_weight / weight) * length
                    if weight > 0:
                        extra_length = (redistributed_weight / weight) * length
                        print(extra_length)
                    else:
                        extra_length = 0
                    new_portions.append((start, end, length + extra_length, weight + redistributed_weight))
                portions = new_portions
                waste = 0


        plot_portioning_visualization(cross_sectional_areas, slice_thickness, density, portions, waste_portion, include_waste)

        tne = get_tne(target_portion_weight)
        t1_tolerance = tne  # T1 = 1x TNE
        t2_tolerance = 2 * tne  # T2 = 2x TNE

        # Rule 1: Average weight must meet or exceed nominal weight
        valid_portions = portions[:-1] if waste_portion and not include_waste else portions
        total_portion_weight = sum(weight for _, _, _, weight in valid_portions)
        average_portion_weight = total_portion_weight / len(valid_portions)
        rule1_pass = average_portion_weight >= target_portion_weight

        # Rule 2: No more than 2.5% of portions can fall below T1 tolerance
        t1_violations = [weight for _, _, _, weight in valid_portions if weight < target_portion_weight - t1_tolerance]
        rule2_pass = len(t1_violations) <= len(valid_portions) * 0.025

        # Rule 3: No portions can fall below T2 tolerance
        t2_violations = [weight for _, _, _, weight in valid_portions if weight < target_portion_weight - t2_tolerance]
        rule3_pass = len(t2_violations) == 0

        # Display Slice Weights in the first output box
        slice_output.delete("1.0", tk.END)
        for idx, weight in enumerate(slice_weights):
            slice_output.insert(tk.END, f"Slice {idx + 1}: Weight = {weight:.2f} g\n")

        # Display T1 and T2 results in the second output box
        cut_solution_output.delete("1.0", tk.END)
        cut_solution_output.insert(tk.END, "--- Three Packers Rule Compliance ---\n")
        cut_solution_output.insert(tk.END, f"Rule 1 (Average Weight >= Nominal): {'PASS' if rule1_pass else 'FAIL'}\n")
        cut_solution_output.insert(tk.END, f"  - Average Weight: {average_portion_weight:.2f} g\n")
        cut_solution_output.insert(tk.END, f"Rule 2 (T1 Violations ≤ 2.5%): {'PASS' if rule2_pass else 'FAIL'}\n")
        if not rule2_pass:
            cut_solution_output.insert(tk.END, f"  - T1 Violations: {len(t1_violations)} / {len(valid_portions)}\n")
        cut_solution_output.insert(tk.END, f"Rule 3 (No T2 Violations): {'PASS' if rule3_pass else 'FAIL'}\n")
        if not rule3_pass:
            cut_solution_output.insert(tk.END, f"  - T2 Violations: {len(t2_violations)}\n")

        # Calculate the total loaf length
        global total_loaf_length
        total_loaf_length = sum(portion[2] for portion in portions)
        if waste_portion and not include_waste:
            total_loaf_length += waste_portion[2]  # Add waste length if waste is not included

        # Display total loaf length
        cut_solution_output.insert(tk.END, f"\nTotal Loaf Length: {total_loaf_length:.2f} mm\n")

        # Display portion details
        for idx, (start, end, length, weight) in enumerate(portions):
            cut_solution_output.insert(tk.END,
                f"\nPortion {idx + 1}:\n"
                f"  Start Slice = {start}\n"
                f"  End Slice = {end}\n"
                f"  Length = {length:.2f} mm\n"
                f"  Weight = {weight:.2f} g\n\n"
            )

        # Display waste details (if applicable)
        if waste_portion and not include_waste:
            cut_solution_output.insert(tk.END,
                f"Waste (discarded):\n"
                f"  Start Slice = {waste_portion[0]}\n"
                f"  End Slice = {waste_portion[1]}\n"
                f"  Length = {waste_portion[2]:.2f} mm\n"
                f"  Weight = {waste_portion[3]:.2f} g\n\n"
            )

        if include_waste and waste_portion:
            cut_solution_output.insert(tk.END, f"\nHypothetical Waste (if not included): {waste_hypothetical:.2f} g\n")
        else:
            cut_solution_output.insert(tk.END, f"\nTotal Waste: {waste:.2f} g\n")

        # Generate image for portions
        generate_portion_image(portions, average_width, average_height, slice_thickness)

        # Show the "View Graph" button
        view_graph_button.grid()
        plt.show()
        
    except ValueError:
        showinfo("Error", "Please enter valid numbers!")


def generate_portion_image(portions, width, height, slice_thickness):
    fig, ax = plt.subplots(figsize=(12, 8))

    # Draw the loaf
    loaf_length = sum([p[2] for p in portions])
    ax.add_patch(Rectangle((0, 0), loaf_length, height, edgecolor="black", facecolor="lightblue"))

    # Draw the portions
    current_x = 0
    for idx, (_, _, length, weight) in enumerate(portions):
        ax.add_patch(Rectangle((current_x, 0), length, height, edgecolor="black", facecolor="orange", alpha=0.7))
        
        # Center the weight label
        ax.text(
            current_x + length / 2, height / 2, f"{weight:.2f} g\n" f"{length:.2f} mm",
            ha="center", va="center", fontsize=8, color="black", rotation=90
        )
        current_x += length

    # Highlight waste
    if waste_portion and not include_waste:
        ax.add_patch(Rectangle((current_x, 0), waste_portion[2], height, edgecolor="black", facecolor="red", alpha=0.5))
        ax.text(
            current_x + waste_portion[2] / 2, height / 2, "Waste",
            ha="center", va="center", fontsize=8, color="white", rotation=90
        )
        ax.text(
            current_x + waste_portion[2] / 2 + 18, height / 2, f"{waste:.2f} g\n" f"{waste_portion[2]:.2f} mm",
            ha="center", va="center", fontsize=8, color="black", rotation=90
        )

    # Add gridlines and target weight bands
    for idx, (_, _, length, _) in enumerate(portions):
        ax.axvline(current_x, color="gray", linestyle="--", linewidth=0.5)
        current_x += length

    ax.axhline(y=target_portion_weight - t1_tolerance, color="blue", linestyle="--", label="T1 Tolerance")
    ax.axhline(y=target_portion_weight - t2_tolerance, color="red", linestyle="--", label="T2 Tolerance")
    ax.axhline(y=target_portion_weight, color="green", linestyle="-", label="Target Weight")

    # Add titles, labels, and legends
    ax.set_title("Cheese Loaf Portioning Visualization", fontsize=14)
    ax.set_xlabel("Length (mm)", fontsize=12)
    ax.set_ylabel("Height (mm)", fontsize=12)
    ax.legend(loc="upper left")
    ax.grid(True)
    ax.set_aspect("equal", adjustable="box")

    # Add total loaf length to the graph
    ax.text(
    loaf_length / 2, +120,  # Place it below the loaf
    f"Total Loaf Length: {total_loaf_length:.2f} mm",
    ha="center", va="top", fontsize=12, color="black"
    )

    # Save the image
    plt.savefig("loaf_visualization.png")
    #plt.show()


# Function to open the generated graph
def open_graph():
    plt.show()

# Function to show help dialog
def show_help():
    help_text = (
        "Cheese Loaf Portion Calculator - Help\n"
        "\nInputs:\n"
        "\nTotal Weight:\n" 
        "The total weight of the cheese loaf in grams.\n"
        "\nTarget Portion Weight:\n"
        "Desired weight for each portion in grams.\n"
        "\nAverage Width:\n" 
        "Average cross-sectional width of the loaf in mm.\n"
        "\nAverage Height:\n"
        "Average cross-sectional height of the loaf in mm.\n"
        "\nNumber of Slice Cross Sections:\n" 
        "Total number of slices along the loaf.\n"
        "\nCross Sections Slice Thickness:\n" 
        "Thickness of each slice in mm.\n"
        "\nTolerance:\n"
        "- Allowed percentage under target weight. This will be useful if the next cross-section takes the portion weight over.\n\n"
        "Outputs:\n"
        "\nSlice Weights:\n" 
        "Displays the calculated weight of each individual slice.\n"
        "\nCut Solution:\n"
        "Provides the start and end slices, total length, and weight of each portion.\n\n"
        "Visualization:\n"
        "- Generates an image showing the loaf and its portion positions with dimensions.\n\n"
        "Note:\n"
        "- The widths and heights of slices are randomized to simulate realistic variations.\n"
        "- Press calculate once desired inputs are entered.\n"
    )
    showinfo("Help", help_text)

    # Function to show Three Packers Rules help dialog
def show_three_packers_help():
    three_packers_help_text = (
        "Three Packers Rules - Help\n\n"
        "The Three Packers Rules are a set of regulations designed to ensure that packaged goods meet weight and quality "
        "standards. These rules are:\n\n"
        "Rule 1:\n"
        "- The average weight of a batch must meet or exceed the nominal (target) weight.\n\n"
        "Rule 2:\n"
        "- No more than 2.5% of the portions in the batch can be below the T1 tolerance level.\n\n"
        "Rule 3:\n"
        "- No portions in the batch can be below the T2 tolerance level.\n\n"
        "Tolerable Negative Error (TNE):\n"
        "- T1 is defined as 1x the TNE value.\n"
        "- T2 is defined as 2x the TNE value.\n\n"
        "TNE Table:\n"
        "---------------------------------------------\n"
        "Nominal Weight (g) | % of Nominal | TNE (g)\n"
        "---------------------------------------------\n"
        "5 to 50            | 9%           | -\n"
        "50 to 100          | -            | 4.5\n"
        "100 to 200         | 4.5%         | -\n"
        "200 to 300         | -            | 9\n"
        "300 to 500         | 3%           | -\n"
        "500 to 1000        | -            | 15\n"
        "1000 to 10000      | 1.5%         | -\n"
        "10000 to 15000     | -            | 150\n"
        "Above 15000        | 1%           | -\n"
        "---------------------------------------------\n\n"
        "Note:\n"
        "- Portions below the T2 limit are considered extremely underweight and are not allowed.\n"
        "- Portions below the T1 limit but above the T2 limit must not exceed 2.5% of the batch.\n"
    )
    showinfo("Three Packers Rules", three_packers_help_text)

# Function to toggle theme
def toggle_theme():
    current_theme = app.tk.call("ttk::style", "theme", "use")
    if current_theme == "azure-light":
        app.tk.call("set_theme", "dark")
        theme_toggle_button.config(text="Toggle Light Mode")
    else:
        app.tk.call("set_theme", "light")
        theme_toggle_button.config(text="Toggle Dark Mode")

# Create the main application window
app = tk.Tk()
app.title("Cheese Loaf Portion Calculator - By Shaun Harris")
app.geometry("600x800")  # Set an initial size

# Set the Azure theme
theme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "azure.tcl")
app.tk.call("source", theme_path)
app.tk.call("set_theme", "light")

# Input variables
total_weight_var = tk.StringVar(value="3330")
slice_thickness_var = tk.StringVar(value="0.1")
target_portion_weight_var = tk.StringVar(value="250")
average_width_var = tk.StringVar(value="93")
average_height_var = tk.StringVar(value="90")
number_of_slices_var = tk.StringVar(value="3600")
include_waste_var = tk.BooleanVar(value=False) 
tolerance_var = tk.DoubleVar(value=99.9)  # Tolerance percentage (default 99.9%)

# Create input fields
fields = [
    ("Total Weight (g):", total_weight_var),
    ("Target Portion Weight (g):", target_portion_weight_var),
    ("Average Width (mm):", average_width_var),
    ("Average Height (mm):", average_height_var),
    ("Number of Slice Cross Sections:", number_of_slices_var),
    ("Slice Cross Section Thickness (mm):", slice_thickness_var),
]

for i, (label, var) in enumerate(fields):
    ttk.Label(app, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
    ttk.Entry(app, textvariable=var).grid(row=i, column=1, padx=5, pady=5, sticky="ew")

# Add tolerance slider and display its value
ttk.Label(app, text="Tolerance (%):").grid(row=len(fields), column=0, sticky=tk.W, padx=5, pady=5)

# Create a label to display the slider value
tolerance_value_label = ttk.Label(app, text=f"{tolerance_var.get():.1f}%")
tolerance_value_label.grid(row=len(fields), column=2, sticky=tk.W, padx=5, pady=5)

# Create the slider
tolerance_slider = ttk.Scale(
    app,
    from_=90,  # Minimum value
    to=100,    # Maximum value
    orient="horizontal",
    variable=tolerance_var,
    command=lambda val: tolerance_value_label.config(text=f"{float(val):.1f}%")  # Update label dynamically
)
tolerance_slider.grid(row=len(fields), column=1, padx=5, pady=5, sticky="ew")

# Add help button
ttk.Button(app, text="Helper", command=show_help).grid(row=0, column=2, padx=5, pady=5)

# Add Three Packers Rules help button
ttk.Button(app, text="Three Packers Rules", command=show_three_packers_help).grid(row=1, column=2, padx=5, pady=5)

# Add theme toggle button
theme_toggle_button = ttk.Button(app, text="Toggle Dark Mode", command=toggle_theme)
theme_toggle_button.grid(row=2, column=2, padx=5, pady=5)

# Add waste inclusion checkbox
ttk.Checkbutton(
    app, text="Include Waste in Portions", variable=include_waste_var
).grid(row=len(fields) + 1, column=0, columnspan=3, pady=5, sticky="w")

# Scrollable text box for slice weights
ttk.Label(app, text="Slice Weights:").grid(row=len(fields) + 2, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(10, 0))
slice_output_frame = ttk.Frame(app)
slice_output_frame.grid(row=len(fields) + 3, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
slice_output_scrollbar = ttk.Scrollbar(slice_output_frame)
slice_output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
slice_output = tk.Text(slice_output_frame, height=10, width=50, yscrollcommand=slice_output_scrollbar.set)
slice_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
slice_output_scrollbar.config(command=slice_output.yview)

# Scrollable text box for cut solution
ttk.Label(app, text="Cut Solution:").grid(row=len(fields) + 4, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(10, 0))
cut_solution_frame = ttk.Frame(app)
cut_solution_frame.grid(row=len(fields) + 5, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
cut_solution_scrollbar = ttk.Scrollbar(cut_solution_frame)
cut_solution_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
cut_solution_output = tk.Text(cut_solution_frame, height=10, width=50, yscrollcommand=cut_solution_scrollbar.set)
cut_solution_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
cut_solution_scrollbar.config(command=cut_solution_output.yview)

# Calculate button
ttk.Button(app, text="Calculate", command=calculate).grid(row=len(fields) + 6, column=0, columnspan=3, pady=10)

# Button to open graph (initially hidden)
view_graph_button = ttk.Button(app, text="View Visualization Graph", command=open_graph)
view_graph_button.grid(row=len(fields) + 7, column=0, columnspan=3, pady=10)
view_graph_button.grid_remove()  # Hide initially

# Configure resizing
app.grid_rowconfigure(len(fields) + 3, weight=1)
app.grid_rowconfigure(len(fields) + 5, weight=1)
app.grid_columnconfigure(1, weight=1)

# Run the app
app.mainloop()