# Python-CheesePortionCalculator
# Required libaries 

`pip install tkinter`
`pip install matplotlib`

# Generate cross-sectional areas
Cross-sectional areas are generated to simulate a real world cheese loaf, based off the inputted values.
        2 volume methods trapezoidal rule should lean towards a better density number.
        
        # Calculate volume using the rectangle rule:
        cross_sectional_areas = [
            (random.gauss(average_width, 2)) * (random.gauss(average_height, 2))
            for _ in range(number_of_length_cross_sections)
        ]

         # Calculate volume using the trapezoidal rule:
        volumes = np.array([
            (slice_thickness / 2) * (cross_sectional_areas[i] + cross_sectional_areas[i+1])
            for i in range(len(cross_sectional_areas) - 1)

The lower our cross-section thickness, the more precise our portions will be.
360mm loaf length = 3600 cross-sections at 0.1mm thickness

# User-Interface
![image](https://github.com/user-attachments/assets/8a68f1ad-eb71-47a3-952b-99d5fa5eaa37)
![image](https://github.com/user-attachments/assets/80e1a9af-6d69-43fc-9ac8-f17d24c7d171)
![image](https://github.com/user-attachments/assets/f183a1c9-d0be-42ed-bb54-17aa1f387e9d)

