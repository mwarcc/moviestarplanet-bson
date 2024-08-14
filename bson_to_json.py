import os
import bson
import json
import argparse
import base64
import logging
from bson import Binary, ObjectId, DBRef, Timestamp, Decimal128
from typing import Any, Dict, Union

# Setting up logging with default level INFO
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler('logs/bson_to_json.log')  # Log to file
    ]
)

class BSONEncoder(json.JSONEncoder):
    """
    Custom JSON Encoder for BSON types.
    Converts BSON types to JSON-serializable formats.
    """
    def default(self, obj: Any) -> Union[Dict[str, Any], str]:
        logging.debug(f"Encoding object of type {type(obj).__name__}")
        if isinstance(obj, Binary):
            return {"$binary": base64.b64encode(obj).decode('utf-8')}
        elif isinstance(obj, ObjectId):
            return {"$oid": str(obj)}
        elif isinstance(obj, DBRef):
            return {"$ref": obj.collection, "$id": str(obj.id)}
        elif isinstance(obj, Timestamp):
            return {"$timestamp": {"t": obj.time, "i": obj.inc}}
        elif isinstance(obj, Decimal128):
            return {"$numberDecimal": str(obj)}
        elif isinstance(obj, bytes):
            return {"$binary": base64.b64encode(obj).decode('utf-8')}
        return super().default(obj)

def convert_bson_to_json(data: Any) -> Any:
    """
    Recursively converts BSON data to JSON-serializable formats, handling special BSON types.

    Args:
        data (Any): The BSON data to convert.

    Returns:
        Any: The converted data in JSON-compatible format.
    """
    logging.debug(f"Converting data of type {type(data).__name__}")
    if isinstance(data, dict):
        return {k: convert_bson_to_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_bson_to_json(i) for i in data]
    elif isinstance(data, bytes):
        return {"$binary": base64.b64encode(data).decode('utf-8')}
    return data

def bson_to_json(bson_file_path: str, output_file_name: str, overwrite: bool, validate: bool) -> None:
    """
    Converts a BSON file to a JSON file.

    Args:
        bson_file_path (str): The path to the input BSON file.
        output_file_name (str): The name of the output JSON file.
        overwrite (bool): Whether to overwrite the output file if it exists.
        validate (bool): Whether to validate the BSON file before conversion.

    Raises:
        IOError: If the BSON file cannot be read or the JSON file cannot be written.
        ValueError: If the BSON data cannot be decoded.
    """
    logging.info(f"Starting BSON to JSON conversion: {bson_file_path} -> {output_file_name}")

    # Check if the output file exists and handle overwrite confirmation
    if os.path.exists(output_file_name) and not overwrite:
        logging.warning(f"File '{output_file_name}' already exists. Use '-y' to overwrite.")
        user_input = input(f"File '{output_file_name}' exists. Overwrite? (y/n): ").strip().lower()
        if user_input != 'y':
            logging.info("Operation cancelled by user.")
            return

    try:
        with open(bson_file_path, 'rb') as bson_file:
            logging.debug(f"Reading BSON file: {bson_file_path}")
            bson_data = bson_file.read()

        if validate:
            logging.info("Validating BSON data...")
            # Validate BSON by trying to decode it (simply reading it with bson.decode_all)
            try:
                bson.decode_all(bson_data)
                logging.info("BSON validation successful.")
            except bson.errors.BSONError as e:
                logging.error(f"BSON validation failed: {e}")
                raise ValueError("BSON validation failed") from e

        decoded_data = bson.decode_all(bson_data)
        logging.debug("BSON data successfully decoded")

        converted_data = convert_bson_to_json(decoded_data)

        with open(output_file_name, 'w') as json_file:
            logging.debug(f"Writing JSON to file: {output_file_name}")
            json.dump(converted_data, json_file, indent=4, cls=BSONEncoder)

        logging.info(f"Successfully converted BSON to JSON. Output saved to '{output_file_name}'.")

    except IOError as e:
        logging.error(f"IOError while processing the files: {e}")
        raise
    except bson.errors.BSONError as e:
        logging.error(f"BSONError in decoding BSON data: {e}")
        raise ValueError("Failed to decode BSON data") from e
    except Exception as e:
        logging.critical(f"Unexpected error occurred: {e}", exc_info=True)
        raise

def generate_default_output_name(bson_file_path: str) -> str:
    """
    Generates a default output file name based on the BSON file path.

    Args:
        bson_file_path (str): The path to the input BSON file.

    Returns:
        str: The default output JSON file name.
    """
    base_name = bson_file_path.rsplit('.', 1)[0]
    return f"{base_name}.json"

def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Convert BSON to JSON format.")
    parser.add_argument('-f', '--file', type=str, required=True, help="Path to the BSON file.")
    parser.add_argument('-o', '--output', type=str, help="Name of the output JSON file. If not provided, defaults to the input file name with .json extension.")
    parser.add_argument('-y', '--yes', action='store_true', help="Automatically overwrite the output file if it exists without prompting.")
    parser.add_argument('-v', '--validate', action='store_true', help="Validate the BSON file before conversion.")
    parser.add_argument('-l', '--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help="Set the logging level. Default is 'INFO'.")
    return parser.parse_args()

def main() -> None:
    """
    Main function to parse arguments and initiate the BSON to JSON conversion.
    """
    args = parse_arguments()

    # Set logging level based on user input
    logging.getLogger().setLevel(args.log_level)

    # Generate output file name if not provided
    output_file_name = args.output if args.output else generate_default_output_name(args.file)

    # Convert BSON to JSON
    bson_to_json(args.file, output_file_name, args.yes, args.validate)

if __name__ == "__main__":
    main()