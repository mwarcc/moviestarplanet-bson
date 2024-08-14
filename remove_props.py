import json
import argparse
import base64
from typing import Any, Dict, List, Union

def process_json(data: Union[Dict[str, Any], List[Any]], search_key: str = "pet") -> None:
    """
    Recursively processes JSON data to remove elements containing a specific search key in 'AssetName'
    or having a non-null 'InventoryId'. The processed data is then re-encoded in base64 format.

    Args:
        data (Union[Dict[str, Any], List[Any]]): The JSON data to process.
        search_key (str): The key to search for in 'AssetName' to remove elements.
    """
    if isinstance(data, dict):
        if 'Content' in data:
            base64_content = data['Content'].get('$binary', '')
            try:
                decoded_json = json.loads(base64.b64decode(base64_content).decode('utf-8'))
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Failed to decode JSON from base64 content: {e}")
                return

            if 'Elements' in decoded_json and isinstance(decoded_json['Elements'], list):
                # Remove elements where 'AssetName' contains the search_key or 'InventoryId' is not null
                decoded_json['Elements'] = [
                    elem for elem in decoded_json['Elements']
                    if search_key not in elem.get('AssetName', '') and elem.get('InventoryId') is None
                ]

            encoded_json = base64.b64encode(json.dumps(decoded_json).encode('utf-8')).decode('utf-8')
            data['Content'] = {'$binary': encoded_json}

        # Recursively process nested dictionaries and lists
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                process_json(value, search_key)

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                process_json(item, search_key)

def remove_props(json_file_path: str, search_key: str = "pet") -> None:
    """
    Removes elements from a JSON file where 'AssetName' contains the search key or 'InventoryId' is not null.

    Args:
        json_file_path (str): The path to the JSON file to process.
        search_key (str): The key to search for in 'AssetName' to remove elements.
    """
    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        process_json(data, search_key)

        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Successfully processed JSON. Modified file saved to '{json_file_path}'.")

    except (IOError, json.JSONDecodeError) as e:
        print(f"An error occurred while processing the JSON file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main() -> None:
    """
    Main function to parse command-line arguments and initiate the JSON property removal process.
    """
    parser = argparse.ArgumentParser(description="Remove properties from JSON data based on a search key.")
    parser.add_argument('-f', '--file', type=str, required=True, help="Path to the JSON file.")
    parser.add_argument('search_key', type=str, nargs='?', default="pet", help="Substring to search for in 'AssetName' to remove items (default: 'pet').")

    args = parser.parse_args()

    remove_props(args.file, args.search_key)

if __name__ == "__main__":
    main()