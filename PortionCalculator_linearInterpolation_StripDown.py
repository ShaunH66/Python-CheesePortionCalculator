import random
import numpy as np
import pandas as pd

def calculate():
    try:
        # Get inputs (example values)
        total_weight = 3330             # grams
        slice_thickness = 0.1           # mm
        target_portion_weight = 250      # grams
        average_width = 93              # mm
        average_height = 90             # mm
        # Total length is 360 mm; number of slices:
        number_of_length_cross_sections = int(360 / slice_thickness)
        include_waste = False
        linear_interpolation_enabled = True
        # Assuming tolerance of 99.9% (i.e. target * 0.999)
        tolerance = 1

        # Generate cross-sectional areas
        cross_sectional_areas = [
            random.gauss(average_width, 2) * random.gauss(average_height, 2)
            for _ in range(number_of_length_cross_sections)
        ]

        # Calculate density using the rectangular rule
        #total_volume = sum(area * slice_thickness for area in cross_sectional_areas)
        #density = total_weight / total_volume

        # Calculate volume using the trapezoidal rule:
        volumes = np.array([
            (slice_thickness / 2) * (cross_sectional_areas[i] + cross_sectional_areas[i+1])
            for i in range(len(cross_sectional_areas) - 1)
        ])
        total_volume = np.sum(volumes)
        density = total_weight / total_volume

        # Calculate slice weights using density
        slice_weights = []
        for area in cross_sectional_areas:
            weight = area * slice_thickness * density
            slice_weights.append(weight)

        # Portion calculation in reverse order:
        # We accumulate from the end of the scan backwards so that the leftover (waste)
        # comes from the front (lowest slice indices).
        portions = []  # Each portion: (start_index, end_index, portion_length, portion_weight)
        current_weight = 0.0
        current_length = 0.0
        # The current_end_index starts at the last slice index.
        current_end_index = len(cross_sectional_areas) - 1

        if linear_interpolation_enabled:
            # Process slices in reverse order.
            for i in reversed(range(len(slice_weights))):
                weight = slice_weights[i]
                prev_weight = current_weight
                prev_length = current_length

                current_weight += weight
                current_length += slice_thickness

                # Check if the accumulated weight reaches the threshold
                if current_weight >= target_portion_weight * tolerance:
                    # Interpolate on the current slice:
                    overshoot = current_weight - (target_portion_weight * tolerance)
                    fraction = (weight - overshoot) / weight if weight != 0 else 1
                    # Adjust length and weight so that the portion exactly meets the threshold.
                    adjusted_length = prev_length + fraction * slice_thickness
                    adjusted_weight = prev_weight + fraction * weight
                    # Record the portion: note that since we're iterating in reverse,
                    # the portion covers slices from index i up to current_end_index.
                    portions.append((i, current_end_index, adjusted_length, adjusted_weight))
                    # Reset accumulators with the remaining fraction of the current slice.
                    remaining_fraction = 1 - fraction
                    current_weight = remaining_fraction * weight
                    current_length = remaining_fraction * slice_thickness
                    # Set new current_end_index to the slice before the current one.
                    current_end_index = i - 1
        else:
                # Process slices in reverse order.
                for i in reversed(range(len(slice_weights))):
                    weight = slice_weights[i]
                    current_weight += weight
                    current_length += slice_thickness

                    if current_weight >= target_portion_weight * tolerance:
                        portions.append((i, current_end_index, current_length, current_weight))
                        current_weight = 0.0
                        current_length = 0.0
                        current_end_index = i - 1


        # After the loop, the remaining accumulated weight corresponds to waste.
        waste = current_weight

        # Calculate waste length: slices from 0 up to current_end_index plus any partial slice.
        if current_end_index >= 0:
            waste_length = (current_end_index + 1) * slice_thickness + current_length
        else:
            waste_length = current_length

        waste_portion = (0, current_end_index, waste_length, waste)

        # Optionally, redistribute waste if enabled.
        if include_waste and portions:
            redistributed_weight = waste / len(portions)
            new_portions = []
            for start, end, length, weight in portions:
                extra_length = (redistributed_weight / weight) * length if weight > 0 else 0
                new_portions.append((start, end, length + extra_length, weight + redistributed_weight))
            portions = new_portions
            waste = 0

        # Reverse portions to report in increasing slice order.
        portions = portions[::-1]

        # --- Insert the waste portion as Portion 0 in the portions list ---
        portions.insert(0, waste_portion)

        # Print results
        print("Portions:")
        for idx, (start, end, length, weight) in enumerate(portions):
            print(f"Portion {idx}: Start Slice = {start}, End Slice = {end}, Length = {length:.3f} mm, Weight = {weight:.3f} g")
        
        if waste_portion:
            print("\nWaste (at the front):")
            print(f"Start Slice = {waste_portion[0]}, End Slice = {waste_portion[1]}, Length = {waste_portion[2]:.3f} mm, Weight = {waste_portion[3]:.3f} g")

        # After calculating portions, build a list of dictionaries with the output data.
        data = []
        for idx, (start, end, length, weight) in enumerate(portions):
            data.append({
                "Portion": idx + 1,
                "Start Slice": start,
                "End Slice": end,
                "Length (mm)": length,
                "Weight (g)": weight
            })

        # Optionally, if you want to log waste as well:
        if waste_portion and not include_waste:
            data.append({
                "Portion": "Waste",
                "Start Slice": waste_portion[0],
                "End Slice": waste_portion[1],
                "Length (mm)": waste_portion[2],
                "Weight (g)": waste_portion[3]
            })

        # Convert the list to a DataFrame
        df = pd.DataFrame(data)

        # Save the DataFrame to an Excel file
        df.to_excel("C:\\Users\\PC\\Desktop\\Python\\PortionCalculatorApp\\portion_data.xlsx", index=False)


    except ValueError:
        print("Error in calculating portions")

calculate()
