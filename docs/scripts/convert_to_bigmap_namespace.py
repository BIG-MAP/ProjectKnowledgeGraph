import rdflib
import os

def update_iri(graph, namespaces_to_update, new_namespace_base):
    triples_to_add = []
    triples_to_remove = []

    # Iterate over all triples in the graph
    for s, p, o in graph:
        if isinstance(s, rdflib.URIRef) and any(s.startswith(ns) for ns in namespaces_to_update):
            unique_id = s.split('/')[-1]
            new_iri = rdflib.URIRef(f"{new_namespace_base}{unique_id}")
            triples_to_add.append((new_iri, rdflib.OWL.equivalentClass, s))
            for (s2, p2, o2) in graph.triples((s, None, None)):
                triples_to_add.append((new_iri, p2, o2))
                triples_to_remove.append((s2, p2, o2))
        if isinstance(o, rdflib.URIRef) and any(o.startswith(ns) for ns in namespaces_to_update):
            if p != rdflib.OWL.equivalentClass:
                unique_id = o.split('/')[-1]
                new_iri = rdflib.URIRef(f"{new_namespace_base}{unique_id}")
                triples_to_add.append((s, p, new_iri))
                triples_to_remove.append((s, p, o))

    # Apply the changes to the graph
    for triple in triples_to_remove:
        graph.remove(triple)
    for triple in triples_to_add:
        graph.add(triple)

def update_ttl_file(input_file, output_file):
    g = rdflib.Graph()
    g.parse(input_file, format="turtle")

    namespaces_to_update = [
        "http://data.europa.eu/s66/resource/results/",
        "http://data.europa.eu/8mn/euroscivoc/",
        "http://data.europa.eu/s66/resource/organisationroles/",
        "http://data.europa.eu/s66/resource/grants/",
        "http://data.europa.eu/s66/resource/grantpayments/",
        "http://data.europa.eu/s66/resource/projects/",
        "http://data.europa.eu/s66/resource/monetaryamounts/"
    ]
    
    new_namespace_base = "https://w3id.org/big-map/public/resource#bigmap_"
    update_iri(g, namespaces_to_update, new_namespace_base)

    g.serialize(destination=output_file, format="turtle")

if __name__ == "__main__":
    # Define the paths to your TTL files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    input_file = os.path.join(repo_root, "bigmap.ttl")
    output_file = os.path.join(repo_root, "bigmap_updated.ttl")

    update_ttl_file(input_file, output_file)
    print(f"Updated file saved as {output_file}")
