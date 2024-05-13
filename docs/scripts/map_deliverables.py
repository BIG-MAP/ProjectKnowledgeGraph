import pandas as pd
import rdflib
from rdflib.namespace import RDF, RDFS, OWL, XSD, SKOS
import os

# Paths setup
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
input_file = os.path.join(repo_root, "bigmap.ttl")
output_file = os.path.join(repo_root, "bigmap_updated.ttl")
excel_path = os.path.join(repo_root, "Deliverables.xlsx")

# Load the Excel file, skipping the first row if it contains merged headers or irrelevant information
df = pd.read_excel(excel_path, skiprows=1)

# Print the DataFrame to debug and verify the data structure
print(df.head())

# Manually set the column names
df.columns = ['WP No', 'Del Rel. No', 'Del No', 'Title', 'Description', 'Lead Beneficiary', 'Nature', 'Dissemination Level', 'Est. Del. Date (annex I)', 'Rev. Due Date', 'Receipt Date', 'Approval Date', 'Status']

# Print the column names to debug
print("Column names in the Excel file:", df.columns.tolist())

# Ensure the column names are correct
expected_columns = ['WP No', 'Del Rel. No', 'Del No', 'Title', 'Description', 'Lead Beneficiary', 'Nature', 'Dissemination Level', 'Est. Del. Date (annex I)', 'Rev. Due Date', 'Receipt Date', 'Approval Date', 'Status']
missing_columns = [col for col in expected_columns if col not in df.columns]
if missing_columns:
    print("Missing columns in the Excel file:", missing_columns)
else:
    # Load the RDF graph
    g = rdflib.Graph()

    # Define namespaces
    DATA = rdflib.Namespace("http://example.org/data#")
    EURIO = rdflib.Namespace("http://data.europa.eu/s66#")
    BIGMAP = rdflib.Namespace("https://w3id.org/big-map/resource#")

    # Bind namespaces
    g.bind("data", DATA)
    g.bind("eurio", EURIO)
    g.bind("bigmap", BIGMAP)
    g.bind("skos", SKOS)

    # Parse the RDF graph
    g.parse(input_file, format='turtle')

    # Helper function to find IRI based on rdfs:label, skos:prefLabel, and skos:altLabel
    def find_iri_by_label(graph, label):
        for s, p, o in graph.triples((None, None, rdflib.Literal(label))):
            if p in [RDFS.label, SKOS.prefLabel, SKOS.altLabel]:
                return s
        return None

    # Update RDF graph based on the Excel data
    for index, row in df.iterrows():
        wp_no = row['WP No']
        del_rel_no = row['Del Rel. No']
        lead_beneficiary = row['Lead Beneficiary']
        title = row['Title']
        description = row['Description']

        # Find deliverable IRI by rdfs:label, skos:prefLabel, or skos:altLabel (which should match the Title in the Excel file)
        deliverable_iri = find_iri_by_label(g, title)
        if deliverable_iri:
            # Find WP IRI by rdfs:label, skos:prefLabel, or skos:altLabel
            wp_iri = find_iri_by_label(g, wp_no)
            if wp_iri:
                g.add((deliverable_iri, EURIO.isResultOf, wp_iri))
            else:
                print(f"Warning: Work package IRI for '{wp_no}' not found.")

            # Find Lead Beneficiary IRI by rdfs:label, skos:prefLabel, or skos:altLabel
            lead_beneficiary_iri = find_iri_by_label(g, lead_beneficiary)
            if lead_beneficiary_iri:
                g.add((deliverable_iri, DATA.hasLeadBeneficiary, lead_beneficiary_iri))
            else:
                print(f"Warning: Lead beneficiary IRI for '{lead_beneficiary}' not found.")

            # Add skos:altLabel with the Del Rel. No if it doesn't already exist
            if not (deliverable_iri, SKOS.altLabel, rdflib.Literal(del_rel_no)) in g:
                g.add((deliverable_iri, SKOS.altLabel, rdflib.Literal(del_rel_no)))

            # Add other properties from the Excel if they don't already exist
            if not (deliverable_iri, EURIO.description, rdflib.Literal(description)) in g:
                g.add((deliverable_iri, EURIO.description, rdflib.Literal(description)))
        else:
            print(f"Warning: Deliverable IRI for title '{title}' not found.")

    # Serialize the updated graph to a new Turtle file
    g.serialize(destination=output_file, format='turtle')

    print(f"Updated RDF data has been saved to {output_file}")
