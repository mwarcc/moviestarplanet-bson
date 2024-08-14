import argparse
import requests
import os
import base64

def convert_file_to_base64(file_path):
    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()
        
        base64_encoded = base64.b64encode(file_content)
        base64_string = base64_encoded.decode('utf-8')
        
        padding_needed = len(base64_string) % 4
        if padding_needed:
            base64_string += '=' * (4 - padding_needed)
        
        return base64_string

    except FileNotFoundError:
        return "File not found. Please check the file path."
    except Exception as e:
        return f"An error occurred: {e}"

def download_content(url: str) -> str:
    # Extract the file name from the URL
    file_name = url.split("/")[-1]  # This assumes the URL ends with the file name
    file_path = os.path.join('data', file_name)
    
    content_bytes = requests.get(url=url).content
    
    print(file_path)
    with open(file_path, 'wb') as file:
        file.write(content_bytes)
    
    return file_path

def show_base64_cleaned_from_url(url: str, template: str, output_file: str = None) -> str:
    file_path = download_content(url=url)
    
    try:
        os.system(f"python bson_to_json.py -f {file_path} -o results/{template}.json")
        os.system(f"python remove_props.py -f results/{template}.json")
        os.system(f"python json_to_bson.py -f results/{template}.json {file_path}.bson")
        
        base64_string = convert_file_to_base64(f"{file_path}.bson")
        
        if output_file:
            with open(output_file, 'w') as out_file:
                out_file.write(base64_string)
            print(f"Base64 content saved to {output_file}")
        
    finally:
        # Clean up the files
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Error deleting file {file_path}: {e}")
        
        bson_path = f"{file_path}.bson"
        
        try:
            os.remove(bson_path)
        except OSError as e:
            print(f"Error deleting file {bson_path}: {e}")
       

    return base64_string

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download content and save it to a BSON file.")
    parser.add_argument('-u', '--url', type=str, required=True, help="The URL of the resource.")
    parser.add_argument('-t', '--template', type=str, required=True, help="The template of the resource.")
    parser.add_argument('-o', '--output', type=str, help="The file to save the Base64 encoded content.")
    args = parser.parse_args()
    
    result = show_base64_cleaned_from_url(args.url, args.template, args.output)
    if not args.output:
        print(result)