#
import pandas as pd
import re
import os

# File paths #SVPI_SIO_2022_51_16_4 (PG)              #SVPI_NOAA_2024_90_20_2 (PG2)
input_file_path = r"C:\Users\Manoj.Gongati\Documents\ScrappingAutomation\InputFiles\PacificGyre\SVPI_SIO_2022_51_16_4.txt"
output_csv_path = r"C:\Users\Manoj.Gongati\Documents\ScrappingAutomation\outputFiles\PacificGyreDataOutput.csv"

# Read the text file
with open(input_file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Function to extract IMEIs until "Manufacturer:"
def extract_imeis(lines):
    imeis = []
    for line in lines:
        if 'Manufacturer:' in line:
            break
        matched = re.findall(r'\b\d{15}\b', line)
        imeis.extend(matched)
    return imeis

def extract_manufacture_date(lines):
    for line in lines:
        if 'Date' in line and 'Manufacture' in line:
            # Extract all numbers from the line
            numbers = re.findall(r'\d+', line)
            if len(numbers) >= 3:
                # Assuming the first three numbers are Month, Day, Year respectively
                Manuf_Month = int(numbers[0])
                Manuf_Day = int(numbers[1])
                Manuf_Year = int(numbers[2])
                return Manuf_Month, Manuf_Day, Manuf_Year
    return None, None, None
Manuf_Month, Manuf_Day, Manuf_Year = extract_manufacture_date(lines)

def extract_iridium_var(lines):
    for line in lines:
        if 'Iridium' in line and 'VAR:' in line:
            # Extract the part after 'VAR:'
            parts = line.split('VAR:')
            if len(parts) > 1:
                Iridium_VAR = parts[1].strip()  # Remove any leading/trailing whitespace
                return Iridium_VAR
    return None  # Return None if no matching line is found
Iridium_VAR  = extract_iridium_var(lines)

def extract_purchased_by(lines):
    for line in lines:
        if 'Drifter' in line and 'Specifications:' in line and 'SVPI' in line:
            # Split the line at underscores
            parts = line.split('_')
            if len(parts) > 2:
                Purchased_by = parts[1]  # Select the part between the first and second underscore
                return Purchased_by
    return None  # Return None if no matching line is found
Purchased_by = extract_purchased_by(lines)

def extract_surface_float_details(lines):
    for line in lines:
        if 'Surface' in line and 'Float' in line and 'Description:' in line:
            # Extract the float composition after ':'
            parts = line.split('Description:')
            if len(parts) > 1:
                Float_Composition = parts[1].strip()  # Remove any leading/trailing whitespace

            # Find the first number in the line for Surface_Float_cm
            numbers = re.findall(r'\d+', line)
            if numbers:
                Surface_Float_cm = 2.54 * int(numbers[0])  # Convert from inches to cm

                return Surface_Float_cm, Float_Composition
    return None, None  # Return None if no matching line is found
Surface_Float_cm, Float_Composition = extract_surface_float_details(lines)

def extract_tether_details(lines):
    for line in lines:
        if 'Tether' in line and 'Description:' in line:
            # Extract the tether description after ':'
            parts = line.split('Description:')
            if len(parts) > 1:
                Tether_Description = parts[1].strip()  # Remove any leading/trailing whitespace

            # Find patterns like "3/16" or "3x19"
            matches = re.findall(r'(\d+)/(\d+)"|(\d+)x(\d+)"', Tether_Description)
            if matches:
                for match in matches:
                    if match[0]:  # It's a fraction
                        num, den = match[0:2]
                        value = float(num) / float(den) * 2.54  # Convert to cm
                        Tether_Description = Tether_Description.replace(f'{num}/{den}"', f'{value}"')
                    else:  # It's an 'x' dimensional spec
                        num1, num2 = match[2:4]
                        value1 = float(num1) * 2.54
                        value2 = float(num2) * 2.54
                        Tether_Description = Tether_Description.replace(f'{num1}x{num2}"', f'{value1}" x {value2}"')

            # Extract numbers again to get the second number as diameter
            new_numbers = re.findall(r'\d+\.\d+|\d+', Tether_Description)
            
            if len(new_numbers) >= 2:
                Tether_Diameter_cm = float(new_numbers[2])  # Get the second number as diameter in cm

            # Extract Tether Material between first and second numbers
            pattern = re.compile(r'(\d+\.\d+|\d+)(.*?)(Wire Rope)')
            match = pattern.search(Tether_Description)
            if match:
                Tether_Material = match.group(3).strip()
            return Tether_Diameter_cm, Tether_Material, Tether_Description

    return None, None, None  # Return None if no matching line is found
Tether_Diameter_cm, Tether_Material, Tether_Description = extract_tether_details(lines)













# Extract IMEIs
imeis = extract_imeis(lines)
dirfl_ids = [imei[-8:] for imei in imeis]
wmo = ""
Assigned_Month = "NA"
Assigned_Year = "NA"
Manufacturer =  "Pacific Gyre"


# Prepare data for DataFrame, prefixing IMEIs with a single quote
data = []
for imei, dirfl_id in zip(imeis, dirfl_ids):
    data.append([f"IMEI: {imei}", dirfl_id, wmo, Assigned_Month, Assigned_Year, Manufacturer, Manuf_Month, Manuf_Day, Manuf_Year, Iridium_VAR, Purchased_by, Surface_Float_cm, Float_Composition, Tether_Diameter_cm, Tether_Material, Tether_Description])

# Create DataFrame
df = pd.DataFrame(data, columns=['IMEI', 'DirFl ID', 'WMO', 'Assigned_Month', 'Assigned_Year', 'Manufacturer', 'Manuf_Month', 'Manuf_Day', 'Manuf_Year', 'Iridium_VAR', 'Purchased_by', 'Surface_Float_cm', 'Float_Composition', 'Tether_Diameter_cm', 'Tether_Material', 'Tether_Description'])

# Append Data to CSV while ensuring correct headers and saving IMEIs as text
if not os.path.exists(output_csv_path):
    df.to_csv(output_csv_path, index=False)  # Create new file if it doesn't exist
else:
    df.to_csv(output_csv_path, mode='a', header=False, index=False)  # Append without headers

print("Data has been successfully appended to the CSV file with IMEIs saved as text.")
