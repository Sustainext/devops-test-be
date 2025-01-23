import json
from datetime import datetime

# File paths
source_file = "updated_fg_new.json"
target_file = "fields_group.json"
output_file = "fields_group_m.json"

def replace_meta_data(source_path, target_path, output_path):
    try:
        # Load source JSON
        with open(source_path, 'r') as src_file:
            source_json = json.load(src_file)

        # Load target JSON
        with open(target_path, 'r') as tgt_file:
            target_json = json.load(tgt_file)

        # Replace meta_data in target with meta_data from source
        for source_item, target_item in zip(source_json, target_json):
            if "fields" in source_item and "fields" in target_item:
                target_item['fields']['meta_data'] = source_item['fields']['meta_data']

        # Save updated target JSON to output file
        with open(output_path, 'w') as out_file:
            json.dump(target_json, out_file, indent=4)

        print(f"Output saved successfully to {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Run the function
if __name__ == "__main__":
    replace_meta_data(source_file, target_file, output_file)
