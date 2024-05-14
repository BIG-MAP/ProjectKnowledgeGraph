from rdflib import Graph, URIRef



########## LOAD TTL ################


def load_ttl_from_url(url:str)->Graph:
    g = Graph()
    g.parse(url, format="turtle")
    return g




########## QUERY TLL ################

def extract_terms_info_sparql(g: Graph) -> list:
    """
    Extract all predicates and their corresponding objects for each subject in the graph.
    """
    PREFIXES = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    """
    query = PREFIXES + """
        SELECT ?subject ?predicate ?object
        WHERE {
            ?subject ?predicate ?object.
        }
    """
    results = g.query(query)
    
    entities = {}
    # Organize data by subject and collect all predicates and objects
    for row in results:
        subject = str(row.subject)
        predicate = str(row.predicate)
        object = str(row.object)
        
        if subject not in entities:
            entities[subject] = {'IRI': subject, 'properties': {}}
        
        # Handle multiple values for the same predicate
        if predicate in entities[subject]['properties']:
            entities[subject]['properties'][predicate].append(object)
        else:
            entities[subject]['properties'][predicate] = [object]

    # Convert the dictionary to a list of dictionaries for easier processing or output
    text_entities = []
    for subject, data in entities.items():
        entity_info = {'IRI': data['IRI']}
        for prop, values in data['properties'].items():
            entity_info[prop] = ", ".join([str(v) for v in values])  # Convert all values to string
        text_entities.append(entity_info)

    return text_entities






########## RENDER HTML TOP ################

def render_rst_top() -> str:

    top_rst = """
===========
Class Index
===========

"""

    return top_rst




########## RENDER ENTITIES ################

def entities_to_rst(entities: list[dict], g: Graph) -> str:
    rst = ""
    for item in entities:
        if '#' not in item['IRI']:
            print(f"Skipping IRI without '#': {item['IRI']}")
            continue

        # Split the IRI to get the suffix which will be used as the anchor
        iri_suffix = item['IRI'].split("#")[-1]

        # Use the prefLabel for the section header, fallback to IRI suffix if prefLabel is not available
        prefLabel = item.get('http://www.w3.org/2004/02/skos/core#prefLabel', iri_suffix)

        rst += ".. raw:: html\n\n"
        rst += "   <div id=\"" + iri_suffix + "\"></div>\n\n"
        rst += prefLabel + "\n"  # Display readable prefLabel as the title
        rst += '-' * len(prefLabel) + "\n\n"
        rst += "* " + item['IRI'] + "\n\n"

        rst += ".. raw:: html\n\n"
        indent = "  "
        rst += indent + "<table class=\"element-table\">\n"
        for key, value in item.items():
            if key not in ['IRI', 'http://www.w3.org/2004/02/skos/core#prefLabel'] and value:  # Exclude 'IRI' and 'prefLabel' to avoid duplication
                prefixed_key = g.qname(URIRef(key))  # Transform URI to QName
                rst += indent + "<tr>\n"
                rst += indent + f"<td class=\"element-table-key\">{prefixed_key}</td>\n"
                rst += indent + f"<td class=\"element-table-value\">{format_value(value)}</td>\n"
                rst += indent + "</tr>\n"
        rst += indent + "</table>\n\n"

    return rst

def format_value(value):
    """Format the value for display in the RST document."""
    if isinstance(value, str) and value.startswith("http"):
        return f"<a href='{value}'>{value}</a>"
    return str(value)






########## RENDER RST BOTTOM ################


def render_rst_bottom() -> str:
    return """
    
        """


########### RUN THE RENDERING WORKFLOW ##############


def rendering_workflow():
    # Load the graph and prepare entities list
    ttl_modules = [
        {"section title": "BIG-MAP Resources", "path": "./bigmap.ttl"}
    ]
    for module in ttl_modules:
        g = load_ttl_from_url(module["path"])
        entities_list = extract_terms_info_sparql(g)

        # Start generating documentation
        rst = render_rst_top()
        page_title = module["section title"]
        rst += page_title + "\n" + "=" * len(page_title) + "\n\n"
        rst += entities_to_rst(entities_list, g)  # Pass the Graph object here

        rst += render_rst_bottom()
        with open("./docs/" + "bigmap.rst", "w+", encoding="utf-8") as f:
            f.write(rst)

if __name__ == "__main__":
    rendering_workflow()

