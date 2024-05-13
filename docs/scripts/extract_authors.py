import re
import json
import os
import requests

def reorder_name(name):
    """
    Reorder name from 'lastname, firstname' to 'firstname lastname'.
    """
    parts = name.split(', ')
    if len(parts) == 2:
        return f"{parts[1]} {parts[0]}"
    return name

def extract_authors_from_ttl(ttl_file):
    """
    Extract authors from the eurio:author field in the TTL file.
    """
    authors_set = set()
    with open(ttl_file, 'r', encoding='utf-8') as file:
        content = file.read()
        matches = re.findall(r'eurio:author "(.*?)"\s*;', content)
        for match in matches:
            # Check if both semicolons and commas are present
            if ';' in match and ',' in match:
                # Assume "lastname, firstname" notation
                authors = match.split('; ')
                for author in authors:
                    authors_set.add(reorder_name(author.strip()))
            else:
                # Split by semicolons, commas, or "and"
                semicolon_split = re.split(r'; |, | and ', match)
                for author in semicolon_split:
                    authors_set.add(author.strip())
    return sorted(authors_set)

def query_orcid_api(author_name):
    """
    Query the ORCID API to get the ORCID for the given author name.
    """
    base_url = "https://pub.orcid.org/v3.0/search/?q="
    headers = {"Accept": "application/json"}
    response = requests.get(base_url + author_name, headers=headers)
    if response.status_code == 200:
        results = response.json().get('result', [])
        if results:
            orcid = results[0]['orcid-identifier']['path']
            return f"https://orcid.org/{orcid}"
    return ""

def create_author_jsonld(authors):
    """
    Create a JSON-LD list of authors using schema.org terms.
    """
    jsonld_list = []
    for author in authors:
        orcid = query_orcid_api(author)
        jsonld_list.append({
            "@context": "http://schema.org",
            "@type": "Person",
            "name": author,
            "identifier": {
                "@type": "PropertyValue",
                "propertyID": "ORCID",
                "value": orcid
            }
        })
    return jsonld_list

def save_json(data, output_file):
    """
    Save the JSON data to a file.
    """
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# File paths
# Define the paths to your TTL files
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
data_dir = os.path.join(repo_root, 'assets', 'data')
input_file = os.path.join(repo_root, "bigmap.ttl")
output_json_file = os.path.join(data_dir, 'authors.json')

# Extract authors from TTL file
authors = extract_authors_from_ttl(input_file)

# Create JSON-LD list with empty ORCID fields
author_jsonld = create_author_jsonld(authors)

# Save the JSON-LD to a file
save_json(author_jsonld, output_json_file)

print(f"Authors with empty ORCID fields saved to {output_json_file}")
