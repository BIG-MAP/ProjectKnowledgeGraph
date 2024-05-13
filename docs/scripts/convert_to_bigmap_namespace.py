import rdflib
import os

def update_iri(graph, namespaces_to_update, new_namespace_base):
    # Iterate over all triples in the graph
    for s, p, o in list(graph):
        # Check if the subject's namespace is in the list of namespaces to update
        if isinstance(s, rdflib.URIRef) and any(s.startswith(ns) for ns in namespaces_to_update):
            # Extract the unique part of the old IRI
            unique_id = s.split('/')[-1]
            # Create the new IRI
            new_iri = rdflib.URIRef(f"{new_namespace_base}{unique_id}")
            # Add the owl:EquivalentTo relation
            graph.add((new_iri, rdflib.OWL.equivalentClass, s))
            # Remove the old triple and add the new triple
            graph.remove((s, p, o))
            graph.add((new_iri, p, o))

def update_ttl_file(input_file, output_file):
    # Create a Graph object
    g = rdflib.Graph()

    # Parse the TTL file
    g.parse(input_file, format="turtle")

    # Define namespaces to update
    namespaces_to_update = [
        "http://data.europa.eu/s66/resource/results/",
        "http://data.europa.eu/8mn/euroscivoc/",
        "http://data.europa.eu/s66/resource/organisationroles/",
        "http://data.europa.eu/s66/resource/grants/",
        "http://data.europa.eu/s66/resource/grantpayments/",
        "http://data.europa.eu/s66/resource/projects/",
        "http://data.europa.eu/s66/resource/monetaryamounts/"
    ]
    
    # Define the new namespace base
    new_namespace_base = "https://w3id.org/big-map/public/resource#bigmap_"

    # Update IRIs
    update_iri(g, namespaces_to_update, new_namespace_base)

    # Serialize the updated graph to a new TTL file
    g.serialize(destination=output_file, format="turtle")

if __name__ == "__main__":
    # Define the paths to your TTL files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    input_file = os.path.join(repo_root, "bigmap.ttl")
    output_file = os.path.join(repo_root, "bigmap_updated.ttl")

    update_ttl_file(input_file, output_file)
    print(f"Updated file saved as {output_file}")
