# moviestarplanet-bson
A utility for converting BSON to JSON and back, allowing easy editing of user-generated content.

## Features

- **BSON to JSON Conversion:** Easily convert BSON data to JSON for readability and editing.
- **JSON Editing:** Edit content in JSON format.
- **JSON to BSON Conversion:** Convert edited JSON back to BSON format for glitching.

## Installation

To install the moviestarplanet-bson, clone the repository and install the required dependencies.

```bash
git clone https://github.com/mwarcc/moviestarplanet-bson.git
cd  moviestarplanet-bson
pip install bson
```

## Usage
Convert BSON to JSON
Convert a BSON file to a JSON file for editing:
```bash
python bson_to_json.py -f <bson_file_path> -o <output_file_path>
```
Clean a room
Remove all elements and pets from a JSON file, while keeping the music intact (not sure):
```bash
python remove_props.py -f <json_file_path>
```
Convert JSON to BSON
Reconvert an edited JSON file back into BSON format:
```bash
python json_to_bson.py -f <json_file_path> -o <output_file_path>
```
