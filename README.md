# Python-CheesePortionCalculator
# Required libaries 

`pip install tkinter`
`pip install matplotlib`

# Generate cross-sectional areas
Cross-sectional areas are generated to simulate a real world cheese loaf, based off the inputted values.

        cross_sectional_areas = [
            (random.gauss(average_width, 2)) * (random.gauss(average_height, 2))
            for _ in range(number_of_length_cross_sections)
        ]

The lower our cross-section thickness, the more precise our portions will be.
360mm loaf length = 3600 cross-sections at 0.1mm thickness

# User-Interface
![image](https://github.com/user-attachments/assets/cd6defe0-a916-4995-aa89-30406afc61c0)
![image](https://github.com/user-attachments/assets/80e1a9af-6d69-43fc-9ac8-f17d24c7d171)

