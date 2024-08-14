import bson
import json
import argparse
import base64
from bson import Binary, ObjectId, DBRef, Timestamp, Decimal128
from typing import Union, Any, Dict, List

def json_to_bson(json_file_path: str, output_file_name: str) -> None:
    """
    Converts a JSON file to a BSON file.

    Args:
        json_file_path (str): The path to the input JSON file.
        output_file_name (str): The name of the output BSON file.

    Raises:
        IOError: If the JSON file cannot be read or the BSON file cannot be written.
        ValueError: If the JSON data is not in the expected format.
    """
    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        converted_data = convert_json_to_bson(data)

        with open(output_file_name, 'wb') as bson_file:
            if isinstance(converted_data, list):
                for doc in converted_data:
                    bson_file.write(bson.encode(doc))
            else:
                bson_file.write(bson.encode(converted_data))

        print(f"Successfully converted JSON to BSON. Output saved to '{output_file_name}'.")

    except (IOError, ValueError) as e:
        print(f"An error occurred while processing the files: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def convert_json_to_bson(data: Any) -> Any:
    """
    Recursively converts JSON data to BSON, handling special BSON types.

    Args:
        data (Any): The JSON data to convert.

    Returns:
        Any: The converted BSON data.
    """
    if isinstance(data, dict):
        if '$binary' in data:
            # needed for bson
            return Binary(base64.b64decode(data['$binary']))
        elif '$oid' in data:
            return ObjectId(data['$oid'])
        elif '$ref' in data and '$id' in data:
            return DBRef(data['$ref'], ObjectId(data['$id']))
        elif '$timestamp' in data:
            ts = data['$timestamp']
            return Timestamp(ts['t'], ts['i'])
        elif '$numberDecimal' in data:
            return Decimal128(data['$numberDecimal'])
        else:
            return {k: convert_json_to_bson(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_json_to_bson(i) for i in data]
    elif isinstance(data, str) and data.startswith('$binary:'):
        return Binary(base64.b64decode(data.split(':')[1]))
    
    return data

def main() -> None:
    """
    Main function to parse arguments and initiate the JSON to BSON conversion.
    """
    parser = argparse.ArgumentParser(description="Convert JSON to BSON format.")
    parser.add_argument('-f', '--file', type=str, required=True, help="Path to the JSON file.")
    parser.add_argument('output', type=str, help="Name of the output BSON file.")

    args = parser.parse_args()

    json_to_bson(args.file, args.output)

if __name__ == "__main__":
    main()