import json
import sys
import os

def main(filename):
    # Load JSON data from the specified file
    with open(filename, 'r') as file:
        data = json.load(file)

    # Check if the data is a list
    if not isinstance(data, list):
        print("The JSON data should be an array of objects.")
        return

    # Process each JSON object in the array
    for obj in data:
        if 'fields' in obj and 'name' in obj['fields']:
            name = obj['fields']['name']
            print(f"Name: {name}")
            module = input("Enter module name: ")
            sub_module = input("Enter sub-module name: ")

            # Create metadata object
            metadata = {
                "module": module,
                "sub_module": sub_module
            }

            # Add metadata to the original object
            obj['fields']['meta_data'] = metadata

    # Extract base name of the file and create a new filename
    base_name = os.path.basename(filename)
    updated_filename = 'updated_' + base_name

    # Save updated data back to a new file
    with open(updated_filename, 'w') as file:
        json.dump(data, file, indent=4)

    print(f"Updated JSON saved to {updated_filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename.json>")
    else:
        main(sys.argv[1])
