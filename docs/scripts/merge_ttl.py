import rdflib
import os

def merge_ttl_files(file1, file2, output_file):
    # Create a Graph object
    g1 = rdflib.Graph()
    g2 = rdflib.Graph()

    # Parse the TTL files
    g1.parse(file1, format="turtle")
    g2.parse(file2, format="turtle")

    # Combine graphs
    g1 += g2

    # Serialize the merged graph to a new TTL file
    g1.serialize(destination=output_file, format="turtle")

if __name__ == "__main__":
    # Define the paths to your TTL files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    file1 = os.path.join(repo_root, "bigmap.ttl")
    file2 = os.path.join(repo_root, "bigmap_new.ttl")
    output_file = os.path.join(repo_root, "bigmap_merged.ttl")

    merge_ttl_files(file1, file2, output_file)
    print(f"Merged file saved as {output_file}")
