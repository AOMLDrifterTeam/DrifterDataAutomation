#find_wave_sensor_details
import pandas as pd
import re
import os

# File paths                  #2023-03-01_iSVPB #2024-08_Wave_Baro (1)
input_file_path = r"C:\Users\Manoj.Gongati\Documents\ScrappingAutomation\InputFiles\2023-03-01_iSVPB.txt" 
output_csv_path = r"C:\Users\Manoj.Gongati\Documents\ScrappingAutomation\outputFiles\ScrippsTestingOutput.csv"

# Read the text file
with open(input_file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Function to check if a line contains a 15-digit number
def contains_15_digit_number(line):
    return bool(re.search(r'\b\d{15}\b', line))

# Function to find Power Supply information, Battery type and calculate Battery Count
def find_power_supply_and_battery_count(lines):
    power_supply = "NA"
    battery_count = "NA"
    battery_type = "NA"  # Default value if no battery type is found
    battery_capacity_ah = "NA"
    found_power_supply = False

    for i, line in enumerate(lines):
        if "Power supply" in line:
            found_power_supply = True
        elif found_power_supply:
            if line.strip():  # This checks if the line is not empty
                power_supply = line.strip()
                # Regex to find numbers possibly followed by text (e.g., "4 diode-protected strings, each with 8 Alkaline")
                numbers = re.findall(r'\d+', power_supply)
                if len(numbers) >= 3:
                    # Assuming the first number is the count of strings and the second is the count per string
                    battery_count = int(numbers[0]) * int(numbers[1])

                    # Finding the position of the third number in the power supply string
                    match = re.search(r'\b{}\b'.format(numbers[2]), power_supply)
                    if match:
                        # Extract the word after the third number
                        substr_from_third_number = power_supply[match.end():].strip()
                        battery_type_words = substr_from_third_number.split()
                        if battery_type_words:
                            battery_type = battery_type_words[0]  # Assuming the next word is the battery type
                
                # Extract the last number in the power supply line as Battery_Capacity_Ah
                if numbers:
                    battery_capacity_ah = numbers[-1]  # Last number in the line

                break  # Exit the loop after finding the next non-empty line

    return power_supply, battery_count, battery_type, battery_capacity_ah

# Find the first and last valid lines
start_index, end_index = None, None
for i, line in enumerate(lines):
    if contains_15_digit_number(line) and start_index is None:
        start_index = i  # First line with a 15-digit number
    if contains_15_digit_number(line) and (i == len(lines) - 1 or not contains_15_digit_number(lines[i + 1])):
        end_index = i  # Last line before the next one does not have a 15-digit number

# Extract relevant lines, Power Supply, and Battery Count
if start_index is not None and end_index is not None:
    relevant_lines = lines[start_index:end_index + 1]
    power_supply, battery_count, battery_type, Battery_Capacity_Ah = find_power_supply_and_battery_count(lines)
else:
    print("No valid data found in the file.")
    exit()

def find_iridium_var(lines):
    iridium_var = "NA"  # Default value if no Iridium VAR is found
    found_iridium_var = False
    for line in lines:
        if "Iridium VAR" in line:
            found_iridium_var = True
        elif found_iridium_var and line.strip():  # Checks for the next non-empty line
            iridium_var = line.strip()
            break  # Exit the loop after finding the next non-empty line
    return iridium_var
Iridium_VAR = find_iridium_var(lines)

def find_gts_insertion(lines):
    gts_insertion = "NA"  # Default value if no GTS Insertion is found
    found_gts_insertion = False
    for line in lines:
        if "GTS Insertion" in line:
            found_gts_insertion = True
        elif found_gts_insertion and line.strip():  # Checks for the next non-empty line
            gts_insertion = line.strip()
            break  # Exit the loop after finding the next non-empty line
    return gts_insertion
gts_insertion_value = find_gts_insertion(lines)

#surface_float_cm_value, float_composition
def find_surface_float_cm(lines):
    surface_float_cm = "NA"  # Default value if no surface float information is found
    float_composition = "NA"  # Default value if no composition information is found
    found_surface_float = False
    for line in lines:
        if "Surface float description" in line:
            found_surface_float = True
        elif found_surface_float and line.strip():  # Check for the next non-empty line
            float_composition = line.strip()  # Capture the whole line as composition
            # Attempt to extract the first number which is expected to be the diameter in cm
            match = re.search(r'\d+(\.\d+)?', float_composition)  # This regex matches both integers and floating point numbers
            if match:
                surface_float_cm = match.group()
                break  # Exit the loop after finding the first non-empty line and extracting the number
            found_surface_float = False  # Reset flag if no number is found in the expected line
    return surface_float_cm, float_composition
surface_float_cm_value, float_composition = find_surface_float_cm(lines)

def find_tether_details(lines):
    tether_diameter_cm_1 = "NA"
    tether_diameter_cm_2 = "NA"
    tether_material = "NA"
    tether_description = "NA"
    found_tether_description = False
    description_count = 0  # To count the non-empty lines after the keyword

    for line in lines:
        if "Tether description" in line:
            found_tether_description = True
        elif found_tether_description and line.strip():
            description_count += 1
            if description_count == 1:
                tether_description = line.strip()
                # Extract floats
                diameters = re.findall(r'\d+\.\d+', line)
                if len(diameters) >= 2:
                    tether_diameter_cm_1 = diameters[0]
                    tether_diameter_cm_2 = diameters[1]
                
                # Extract Tether Material starting right after the second float
                second_float_index = line.find(diameters[1]) + len(diameters[1])
                tether_material = line[second_float_index:].strip()
            elif description_count <= 4:
                tether_description += " " + line.strip()
                if description_count == 4:
                    break  # We have collected all required lines

    return tether_diameter_cm_1, tether_diameter_cm_2, tether_material, tether_description
tether_diameter_cm_1, tether_diameter_cm_2, tether_material, tether_description = find_tether_details(lines)

def find_drogue_description(lines):
    drogue_description = "NA"
    drogue_material = "NA"
    drogue_diameter_m = "NA"
    no_drogue_sections = "NA"
    drogue_section_length_cm = "NA"
    drogue_ballast_kg = "NA"
    found_drogue_description = False
    description_lines = 0  # Counter for the non-empty lines collected

    for line in lines:
        if "Drogue description" in line:  # Ensure this is the correct starting keyword
            found_drogue_description = True
        elif found_drogue_description and line.strip():
            description_lines += 1
            if description_lines == 1:
                drogue_description = line.strip()
                # Extract material directly without look-behind
                material_match = re.search(r'(\b\w+\s+\w+\s+[^,.]+)', drogue_description)
                if material_match:
                    drogue_material = material_match.group(1).strip()
                
                # Extract Diameter and check for unit
                diameter_match = re.search(r'diameter:\s*(\d+\.?\d*)\s*(cm)?', line)
                if diameter_match:
                    drogue_diameter_m = float(diameter_match.group(1))
                    # Check if the unit group was captured and it is 'cm'
                    if diameter_match.group(2) and diameter_match.group(2) == 'cm':
                        drogue_diameter_m /= 100  # Convert cm to meters
                
                # Extract Number of Drogue Sections
                sections_match = re.search(r'(\d+)\s*cylindrical', line)
                if sections_match:
                    no_drogue_sections = sections_match.group(1)
                
                # Extract Section Length in cm from 'cylindrical'
                length_match = re.search(r'cylindrical.*?(\d+)', line)
                if length_match:
                    drogue_section_length_cm = length_match.group(1)
                    
            elif description_lines == 2:
                drogue_description += " " + line.strip()
                # Extract ballast in kilograms
                ballast_match = re.search(r'(\d+\.?\d*)kg', line)
                if ballast_match:
                    drogue_ballast_kg = ballast_match.group(1)
            elif description_lines > 2 and description_lines <= 4:
                drogue_description += " " + line.strip()
            if description_lines == 4:
                break  # Stop after collecting four non-empty lines

    return (drogue_description, drogue_material, drogue_diameter_m, no_drogue_sections,
            drogue_section_length_cm, drogue_ballast_kg)
drogue_description, drogue_material, drogue_diameter_m, no_drogue_sections, drogue_section_length_cm, drogue_ballast_kg = find_drogue_description(lines)

def find_drogue_length(lines):
    drogue_length_m = "NA"
    found_drogue_length = False

    for line in lines:
        if "Drogue length" in line:
            found_drogue_length = True
        elif found_drogue_length and line.strip():
            # Reset the flag as we're only interested in the first non-empty line after "Drogue length"
            found_drogue_length = False
            # Capture the first number and optional unit
            length_match = re.search(r'(\d+\.?\d*)\s*(cm)?', line.strip())
            if length_match:
                drogue_length_m = float(length_match.group(1))
                # If the unit is 'cm', convert to meters
                if length_match.group(2) == 'cm':
                    drogue_length_m /= 100
            break  # Break after processing the first non-empty line after "Drogue length"
    return drogue_length_m
drogue_length_m = find_drogue_length(lines)

def find_drogue_depth_at_center(lines):
    drogue_depth_at_center_m = "NA"
    found_drogue_depth = False

    for line in lines:
        if "Drogue depth" in line:
            found_drogue_depth = True
        elif found_drogue_depth and line.strip():  # Find the next non-empty line
            found_drogue_depth = False  # Reset the flag after finding the next non-empty line
            # Capture the first number
            depth_match = re.search(r'(\d+\.?\d*)', line.strip())
            if depth_match:
                drogue_depth_at_center_m = depth_match.group(1)
            break  # Stop after extracting the required number

    return drogue_depth_at_center_m
drogue_depth_at_center_m = find_drogue_depth_at_center(lines)

def find_drag_above_drogue_dm2(lines):
    drag_above_drogue_dm2 = "NA"
    found_cross_sectional_area = False

    for line in lines:
        if "Cross-sectional area" in line and not found_cross_sectional_area:
            found_cross_sectional_area = True  # Mark first occurrence
        elif found_cross_sectional_area and line.strip():  # Find the next non-empty line
            found_cross_sectional_area = False  # Reset flag after finding the next non-empty line
            # Capture the first number and check if "sq-cm" follows it
            drag_match = re.search(r'(\d+\.?\d*)\s*(sq-cm)?', line.strip())
            if drag_match:
                drag_above_drogue_dm2 = float(drag_match.group(1))
                # If the unit is 'sq-cm', convert from cm² to dm² (divide by 100)
                if drag_match.group(2) == 'sq-cm':
                    drag_above_drogue_dm2 /= 100
            break  # Stop after extracting the required number

    return drag_above_drogue_dm2
Drag_Above_Drogue_dm2 = find_drag_above_drogue_dm2(lines)

def find_drag_of_drogue_dm2(lines):
    drag_of_drogue_dm2 = "NA"
    cross_sectional_area_count = 0  # Track occurrences of "Cross-sectional area"

    for line in lines:
        if "Cross-sectional area" in line:
            cross_sectional_area_count += 1  # Count occurrences
        
        elif cross_sectional_area_count == 2 and line.strip():  # Process second occurrence
            cross_sectional_area_count = -1  # Ensure only the second instance is processed
            # Capture the first number and check if "sq-cm" follows it
            drag_match = re.search(r'(\d+\.?\d*)\s*(sq-cm)?', line.strip())
            if drag_match:
                drag_of_drogue_dm2 = float(drag_match.group(1))
                # If the unit is 'sq-cm', convert from cm² to dm² (divide by 100)
                if drag_match.group(2) == 'sq-cm':
                    drag_of_drogue_dm2 /= 100
            break  # Stop after extracting the required number

    return drag_of_drogue_dm2
Drag_of_Drogue_dm2 = find_drag_of_drogue_dm2(lines)

def find_transmitter_details(lines):
    communications = "NA"
    transmitter_manuf = "NA"
    transmitter_type = "NA"
    found_transmitter = False

    for line in lines:
        if "Transmitter" in line:
            found_transmitter = True
        elif found_transmitter and line.strip():  # First non-empty line after "Transmitter"
            found_transmitter = False  # Reset flag after finding the next non-empty line
            
            # Extract the first word as both Communications and Transmitter_Manuf
            first_word_match = re.match(r'(\w+)', line.strip())
            if first_word_match:
                communications = transmitter_manuf = first_word_match.group(1)
            
            # Extract the first number as Transmitter_Type
            number_match = re.search(r'(\d+)', line.strip())
            if number_match:
                transmitter_type = number_match.group(1)

            break  # Stop after processing the first non-empty line
    return communications, transmitter_manuf, transmitter_type
communications, transmitter_manuf, transmitter_type = find_transmitter_details(lines)

def find_controller_details(lines):
    controller_manuf = "NA"
    controller_model = "NA"
    duty_cycle = "NA"
    antifouling = "NA"
    Transmission_Cycle = "NA"

    found_manuf = False
    found_model = False
    found_duty_cycle = False
    found_antifouling = False
    found_Transmission_Cycle = False

    for line in lines:
        if "Controller manufacturer" in line:
            found_manuf = True
        elif found_manuf and line.strip():
            controller_manuf = line.strip()
            found_manuf = False  # Reset flag after finding the next non-empty line

        if "Controller Generation" in line:
            found_model = True
        elif found_model and line.strip():
            controller_model = line.strip()
            found_model = False  # Reset flag after finding the next non-empty line

        if "Duty cycle" in line:
            found_duty_cycle = True
        elif found_duty_cycle and line.strip():
            duty_cycle = line.strip()
            found_duty_cycle = False  # Reset flag after finding the next non-empty line
        
        if "Antifouling" in line:
            found_antifouling = True
        elif found_antifouling and line.strip():
            antifouling = line.strip()
            found_antifouling = False  # Reset flag after finding the next non-empty line

        if "Observation cycle" in line:
            found_Transmission_Cycle = True
        elif found_Transmission_Cycle and line.strip():
            Transmission_Cycle = line.strip()
            found_Transmission_Cycle = False  # Reset flag after finding the next non-empty line    

    return controller_manuf, controller_model, duty_cycle, antifouling, Transmission_Cycle
controller_manuf, controller_model, duty_cycle, antifouling, Transmission_Cycle = find_controller_details(lines)

def find_message_format(lines):
    message_format = []
    found_template = False
    skip_first_non_empty = False

    for line in lines:
        if "Template" in line:
            found_template = True
            skip_first_non_empty = True  # Skip the first non-empty line after "Template"
            continue
        
        if "Observation cycle" in line:
            break  # Stop when reaching "Observation cycle"

        if found_template and line.strip():
            if skip_first_non_empty:
                skip_first_non_empty = False  # Skip only the first non-empty line
                continue
            message_format.append(line.strip())

    return "\n".join(message_format) if message_format else "NA"
Message_Format = find_message_format(lines)

def find_temperature_sensor_details(lines):
    temp_sensor_resolution = "NA"
    temp_sensor_manuf = "NA"
    temperature_equation = "NA"
    temperature_sensor = "NA"
    
    found_sst_type = False
    found_accuracy = False
    found_manuf = False
    found_equation = False
    found_sensor_type = False

    for line in lines:
        if "Type:" in line and "SST" in line:
            found_sst_type = True  # Start processing after this line
            continue  # Skip this line

        if found_sst_type and "Accuracy" in line and not found_accuracy:
            words = line.split(maxsplit=1)
            if len(words) > 1:
                temp_sensor_resolution = words[1]  # Everything except the first word
            found_accuracy = True

        elif found_sst_type and "Mfg" in line and not found_manuf:
            words = line.split(maxsplit=1)
            if len(words) > 1:
                temp_sensor_manuf = words[1]  # Everything except the first word
            found_manuf = True

        elif found_sst_type and "Equation" in line and not found_equation:
            equation_match = re.search(r'=\s*(.*)', line)
            if equation_match:
                temperature_equation = equation_match.group(1).strip()  # Keep as is
            found_equation = True

        elif found_sst_type and "Type:" in line and not found_sensor_type:
            words = line.split(maxsplit=1)
            if len(words) > 1:
                temperature_sensor = words[1]  # Everything except the first word
            found_sensor_type = True

        # Stop processing once all values are found
        if found_accuracy and found_manuf and found_equation and found_sensor_type:
            break

    return temp_sensor_resolution, temp_sensor_manuf, temperature_equation, temperature_sensor
temp_sensor_resolution, temp_sensor_manuf, temperature_equation, temperature_sensor = find_temperature_sensor_details(lines)


def find_drogue_sensor_details(lines):
    drogue_sensor_manuf = "NA"
    drogue_sensor_model = "NA"
    drogue_sensor_equation = "NA"

    found_units_count = False
    found_manuf = False
    found_model = False

    last_equation_line = None  # Store the last "Equation" line before "Units: count(s)"

    for line in lines:
        if "Equation" in line:
            last_equation_line = line  # Store the last encountered equation line

        if "Units:" in line and "count(s)" in line:
            found_units_count = True
            # Extract the equation from the last stored equation line
            if last_equation_line:
                equation_match = re.search(r'=\s*(.*)', last_equation_line)
                if equation_match:
                    drogue_sensor_equation = equation_match.group(1).strip()
            continue  # Skip this line

        if found_units_count and "Mfg:" in line and not found_manuf:
            words = line.split(maxsplit=1)
            if len(words) > 1:
                drogue_sensor_manuf = words[1]  # Everything after "Mfg:"
            found_manuf = True

        elif found_units_count and "Type:" in line and not found_model:
            words = line.split(maxsplit=1)
            if len(words) > 1:
                drogue_sensor_model = words[1]  # Everything after "Type:"
            found_model = True

        # Stop processing once all values are found
        if found_manuf and found_model:
            break

    return drogue_sensor_manuf, drogue_sensor_model, drogue_sensor_equation
drogue_sensor_manuf, drogue_sensor_model, drogue_sensor_equation = find_drogue_sensor_details(lines)



def find_gps_details(lines):
    gps_manuf = "NA"
    gps_model = "NA"
    gps_equation = "NA"
    gps_accuracy = "NA"

    found_gps_latitude = False
    found_manuf = False
    found_model = False
    equation_count = 0
    gps_lon_equation = "NA"
    gps_lat_equation = "NA"

    for line in lines:
        if "Type:" in line and "GPS Latitude" in line:
            found_gps_latitude = True  # Start processing after this line
            continue  # Skip this line

        if found_gps_latitude and "Mfg:" in line and not found_manuf:
            words = line.split(maxsplit=1)
            if len(words) > 1:
                gps_manuf = words[1]  # Everything after "Mfg:"
            found_manuf = True

        elif found_gps_latitude and "Type:" in line and not found_model:
            words = line.split(maxsplit=1)
            if len(words) > 1:
                gps_model = words[1]  # Everything after "Type:"
            found_model = True

        elif found_gps_latitude and "Equation:" in line:
            equation_match = re.search(r'=\s*(.*)', line)
            if equation_match:
                equation_count += 1
                if equation_count == 1:
                    gps_lon_equation = equation_match.group(1).strip()
                elif equation_count == 2:
                    gps_lat_equation = equation_match.group(1).strip()
                elif equation_count == 3:
                    gps_accuracy = equation_match.group(1).strip()
                    break  # Stop after extracting GPS_Accuracy

    # Construct GPS_Equation using extracted Lon and Lat equations
    if gps_lon_equation != "NA" and gps_lat_equation != "NA":
        gps_equation = f"Lon={gps_lat_equation}; Lat={gps_lon_equation}"

    return gps_manuf, gps_model, gps_equation, gps_accuracy
gps_manuf, gps_model, gps_equation, gps_accuracy = find_gps_details(lines)



def find_gps_acquisition_time(lines):
    found_gps_time_first_fix = False
    gps_acquisition_time = "NA"

    for line in lines:
        # Check if line contains all three required keywords
        if "GPS" in line and "Time" in line and "First Fix" in line:
            found_gps_time_first_fix = True
            continue
        
        if found_gps_time_first_fix and line.strip():
            # Find the word after "=" in the next non-empty line
            time_match = re.search(r'=\s*(\w+)', line)
            if time_match:
                gps_acquisition_time = "time = " + time_match.group(1)
            break  # Only process the first matching line after the keywords
    return gps_acquisition_time
gps_acquisition_time = find_gps_acquisition_time(lines)


def find_iridium_details(lines):
    iridium_transmit_duration = "NA"
    iridium_retries = "NA"
    found_iridium_line = False
    equation_count = 0

    for line in lines:
        # Check if the line contains all three necessary words
        if "Iridium" in line and "transmit" in line and "duration" in line:
            found_iridium_line = True
            continue
        
        if found_iridium_line and "Equation" in line:
            
            equation_count += 1
            if equation_count == 1:
                iridium_transmit_duration = line.strip()  # First "Equation" line
                
            elif equation_count == 2:
                iridium_retries = line.strip()  # Second "Equation" line
                break  # Break after finding both needed values

    return iridium_transmit_duration, iridium_retries
iridium_transmit_duration, iridium_retries = find_iridium_details(lines)

def find_barometer_details(lines):
    barometer_manufacturer = "NA"
    barometer_model = "NA"
    barometer_equation = "NA"
    
    found_air_pressure = False
    found_manufacturer = False
    found_model = False
    found_equation = False

    for line in lines:
        # Check if the line contains all three necessary words
        if "Type:" in line and "Air" in line and "Pressure" in line:
            found_air_pressure = True
            continue
        
        if found_air_pressure and "Mfg:" in line and not found_manufacturer:
            # Capture everything after "Mfg:"
            mfg_match = re.search(r'Mfg:\s*(.*)', line)
            if mfg_match:
                barometer_manufacturer = mfg_match.group(1).strip()
            found_manufacturer = True

        elif found_air_pressure and "Package:" in line and not found_model:
            # Capture everything after "Package:"
            model_match = re.search(r'Package:\s*(.*)', line)
            if model_match:
                barometer_model = model_match.group(1).strip()
            found_model = True

        elif found_air_pressure and "Equation:" in line and not found_equation:
            # Capture everything after "="
            equation_match = re.search(r'=\s*(.*)', line)
            if equation_match:
                barometer_equation = equation_match.group(1).strip()
            found_equation = True

        # Stop processing once all values are found
        if found_manufacturer and found_model and found_equation:
            break

    return barometer_manufacturer, barometer_model, barometer_equation
barometer_manufacturer, barometer_model, barometer_equation = find_barometer_details(lines)

def find_barometer_tendency_eq(lines):
    barometer_tendency_eq = "NA"
    found_tendency_line = False

    for line in lines:
        # Check if the line contains all three required words
        if "Type:" in line and "Pressure" in line and "Tendency" in line:
            found_tendency_line = True
            continue
        
        if found_tendency_line and "Equation:" in line:
            # Capture everything after "="
            equation_match = re.search(r'Equation:\s*=\s*(.*)', line)
            if equation_match:
                barometer_tendency_eq = equation_match.group(1).strip()
                break  # Break after finding the equation to optimize performance

    return barometer_tendency_eq
barometer_tendency_eq = find_barometer_tendency_eq(lines)

def find_hull_details(lines):
    # Initialize all outputs with default values
    hull_pressure = "No"
    hull_pressure_equation = "NA"
    hull_humidity = "No"
    hull_humidity_equation = "NA"
    hull_temp = "No"
    hull_temp_equation = "NA"

    # Utility function to check for keywords and capture equation
    def find_detail_and_equation(keywords):
        found = False
        equation = "NA"
        for line in lines:
            if all(keyword in line for keyword in keywords):
                found = True
                continue
            if found and "Equation:" in line:
                equation_match = re.search(r'Equation:\s*=\s*(.*)', line)
                if equation_match:
                    equation = equation_match.group(1).strip()
                    break
        return "Yes" if found else "No", equation

    # Find details for Hull Pressure
    hull_pressure, hull_pressure_equation = find_detail_and_equation(['Type:', 'Hull', 'Pressure'])
    
    # Find details for Hull Humidity
    hull_humidity, hull_humidity_equation = find_detail_and_equation(['Type:', 'Hull', 'Humidity'])
    
    # Find details for Hull Temperature
    hull_temp, hull_temp_equation = find_detail_and_equation(['Type:', 'Hull', 'Temperature'])

    return hull_pressure, hull_pressure_equation, hull_humidity, hull_humidity_equation, hull_temp, hull_temp_equation
hull_pressure, hull_pressure_equation, hull_humidity, hull_humidity_equation, hull_temp, hull_temp_equation = find_hull_details(lines)

def find_wave_sensor_details(lines):
    # Initial default states
    wave_spectra_sensor = "No"
    wave_dir_equations = "NA"
    wave_height_equations = "NA"
    wave_period = "NA"

    # Helper function to find the equation after a line containing specific keywords
    def find_equation_after_keywords(keywords):
        found_keywords = False
        for line in lines:
            if all(keyword in line for keyword in keywords):
                found_keywords = True
                continue
            if found_keywords and "Equation:" in line:
                equation_match = re.search(r'Equation:\s*=\s*(.*)', line)
                if equation_match:
                    return equation_match.group(1).strip()
                break
        return "NA"

    # Check for the presence of any line containing 'Type:' and 'Wave'
    if any("Type:" in line and "Wave" in line for line in lines):
        wave_spectra_sensor = "Yes"

    # Find the Wave Direction Equation
    wave_dir_keywords = ['Type:', 'Wave', 'Direction']
    wave_dir_equations = find_equation_after_keywords(wave_dir_keywords)

    # Find the Wave Height Equation
    wave_height_keywords = ['Type:', 'Wave', 'Height']
    wave_height_equations = find_equation_after_keywords(wave_height_keywords)

    # Find the Wave Period Equation
    wave_period_keywords = ['Type:', 'Wave', 'Period']
    wave_period = find_equation_after_keywords(wave_period_keywords)

    return wave_spectra_sensor, wave_dir_equations, wave_height_equations, wave_period
wave_spectra_sensor, wave_dir_equations, wave_height_equations, wave_period = find_wave_sensor_details(lines)


# Process lines to extract data
data = []
for line in relevant_lines:
    parts = re.split(r'\t+', line.strip())  # Handle multiple tabs

    if len(parts) >= 3:
        id_number = parts[0]
        date_of_production = parts[1]
        date_of_shipping = parts[2]

        dirfl_id = id_number[-8:]
        WMO = ""
        manufacturer = "SIO"
        manuf_year = int(date_of_production.split('-')[0])
        manuf_month = int(date_of_production.split('-')[1])
        manuf_day = date_of_production.split('-')[2]  
        Shipped_Month = int(date_of_shipping.split('-')[1])
        Shipped_Year = int(date_of_shipping.split('-')[0])
        On_Shelf = (Shipped_Year - manuf_year) * 12 + (Shipped_Month - manuf_month)
        assigned_month = "NA"
        assigned_year = "NA"
        data.append([id_number, dirfl_id, WMO, manufacturer, manuf_day, manuf_month, manuf_year, On_Shelf, Shipped_Month, Shipped_Year, assigned_month, assigned_year, power_supply, battery_count, battery_type, Battery_Capacity_Ah, Iridium_VAR, gts_insertion_value, surface_float_cm_value, float_composition, tether_diameter_cm_1, tether_diameter_cm_2, tether_material, tether_description, drogue_description, drogue_material, drogue_diameter_m, no_drogue_sections, drogue_section_length_cm, drogue_ballast_kg, drogue_length_m, drogue_depth_at_center_m, Drag_Above_Drogue_dm2, Drag_of_Drogue_dm2, communications, transmitter_manuf, transmitter_type, controller_manuf, controller_model, duty_cycle, antifouling, Message_Format, Transmission_Cycle, temp_sensor_resolution, temp_sensor_manuf, temperature_equation, temperature_sensor, drogue_sensor_manuf, drogue_sensor_model, drogue_sensor_equation, gps_manuf, gps_model, gps_equation, gps_accuracy, gps_acquisition_time, iridium_transmit_duration, iridium_retries, barometer_manufacturer, barometer_model, barometer_equation, barometer_tendency_eq, hull_pressure, hull_pressure_equation, hull_humidity, hull_humidity_equation, hull_temp, hull_temp_equation, wave_spectra_sensor, wave_dir_equations, wave_height_equations, wave_period])

# Create DataFrame and enforce string format for IMEI
df = pd.DataFrame(data, columns=['ID Number', 'DIRFL ID', 'WMO', 'Manufacturer', 'Manufacture Day', 'Manufacture Month', 'Manufacture Year', 'On Shelf', 'Shipped Month', 'Shipped Year', 'Assigned Month', 'Assigned Year', 'Power Supply', 'battery_count', 'battery_type', 'Battery_Capacity_Ah', 'Iridium_VAR', 'gts_insertion_value', 'surface_float_cm_value', 'float_composition', 'tether_diameter_cm_1', 'tether_diameter_cm_2', 'tether_material', 'tether_description', 'drogue_description', 'drogue_material','drogue_diameter_m', 'no_drogue_sections', 'drogue_section_length_cm', 'drogue_ballast_kg', 'drogue_length_m', 'drogue_depth_at_center_m', 'Drag_Above_Drogue_dm2', 'Drag_of_Drogue_dm2', 'communications', 'transmitter_manuf', 'transmitter_type', 'controller_manuf', 'controller_model', 'duty_cycle', 'antifouling', 'Message_Format', 'Transmission_Cycle','temp_sensor_resolution', 'temp_sensor_manuf', 'temperature_equation', 'temperature_sensor', 'drogue_sensor_manuf', 'drogue_sensor_model', 'drogue_sensor_equation', 'gps_manuf', 'gps_model', 'gps_equation', 'gps_accuracy', 'gps_acquisition_time', 'iridium_transmit_duration', 'iridium_retries', 'barometer_manufacturer', 'barometer_model', 'barometer_equation', 'barometer_tendency_eq', 'hull_pressure', 'hull_pressure_equation', 'hull_humidity', 'hull_humidity_equation', 'hull_temp', 'hull_temp_equation', 'wave_spectra_sensor', 'wave_dir_equations', 'wave_height_equations', 'wave_period'])

# Append Data to CSV while ensuring correct headers
if not os.path.exists(output_csv_path):
    df.to_csv(output_csv_path, index=False)  # Create new file if it doesn't exist
else:
    df.to_csv(output_csv_path, mode='a', header=False, index=False)  # Append without headers

print("Data has been successfully appended to the CSV file with correct formatting.")