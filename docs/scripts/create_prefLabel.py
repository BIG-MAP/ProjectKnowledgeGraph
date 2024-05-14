from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS, SKOS, OWL, XSD
import os

def ensure_pref_labels(graph):
    """
    Ensure every term with an rdfs:label also has a skos:prefLabel.
    If a term lacks skos:prefLabel, it is created by duplicating the rdfs:label.
    """
    # Query all resources with an rdfs:label
    query = """
    SELECT ?s ?label
    WHERE {
        ?s rdfs:label ?label .
        FILTER NOT EXISTS { ?s skos:prefLabel ?prefLabel }
    }
    """
    results = graph.query(query)

    # Create skos:prefLabel for each result that lacks one
    for row in results:
        subject, label = row
        # Add skos:prefLabel that duplicates rdfs:label
        graph.add((subject, SKOS.prefLabel, label))

    return graph

def load_graph_from_ttl(file_path):
    """
    Load an RDF graph from a Turtle file.
    """
    g = Graph()
    g.parse(file_path, format='turtle')
    return g

def save_graph_to_ttl(graph, file_path):
    """
    Save an RDF graph to a Turtle file.
    """
    graph.serialize(destination=file_path, format='turtle')

if __name__ == "__main__":
    # Define the paths to your TTL files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    input_file = os.path.join(repo_root, "bigmap.ttl")
    output_file = os.path.join(repo_root, "bigmap_updated.ttl")

    # Load the existing TTL file
    rdf_graph = load_graph_from_ttl(input_file)

    # Ensure all terms have skos:prefLabel
    updated_graph = ensure_pref_labels(rdf_graph)

    # Save the updated graph back to TTL
    save_graph_to_ttl(updated_graph, output_file)

    print("Updated graph saved to:", output_file)
