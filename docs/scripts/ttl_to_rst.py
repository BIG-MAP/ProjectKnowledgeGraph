from rdflib import Graph, URIRef, Literal



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
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
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
            entity_info[g.qname(URIRef(prop))] = ", ".join([str(v) for v in values])  # Convert all values to string
        text_entities.append(entity_info)

    # Optionally sort by a specific property, like IRI or a label
    text_entities.sort(key=lambda e: e.get('skos:prefLabel', e['IRI']))

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

def entities_to_rst(entities: list[dict]) -> str:
    rst = ""
    for item in entities:
        # Use get() with a default value to avoid KeyError
        prefLabel = item.get('prefLabel', 'No Label Provided')
        
        # Check if '#' is in the IRI, skip if not present or handle differently
        if '#' not in item['IRI']:
            print(f"Skipping IRI without '#': {item['IRI']}")
            continue

        iri_prefix, iri_suffix = item['IRI'].split("#")

        rst += ".. _" + iri_suffix + ":\n\n"
        rst += prefLabel + "\n"
        rst += "-" * len(prefLabel) + "\n\n"

        rst += "* " + item['IRI'] + "\n\n"

        rst += ".. raw:: html\n\n"
        indent = "  "
        rst += indent + "<table class=\"element-table\">\n"
        for key, value in item.items():
            if key not in ['IRI', 'prefLabel'] and value:  # Check if value is non-empty
                rst += indent + "<tr>\n"
                rst += indent + "<td class=\"element-table-key\"><span class=\"element-table-key\">" + key + "</span></td>\n"
                if isinstance(value, str) and value.startswith("http"):
                    value = f"<a href='{value}'>{value}</a>"
                rst += indent + "<td class=\"element-table-value\">" + value + "</td>\n"
                rst += indent + "</tr>\n"
                
        rst += indent + "</table>\n\n"

    return rst



########## RENDER RST BOTTOM ################


def render_rst_bottom() -> str:
    return """
    
        """


########### RUN THE RENDERING WORKFLOW ##############


def rendering_workflow():

    # PAGES
    ttl_modules = [
        {"section title": "BIG-MAP Resources",
         "path": "./bigmap.ttl"}
    ]

    # GENERATE PAGES
    rst_filename = "bigmap.rst"

    rst = render_rst_top()

    for module in ttl_modules:

        g = load_ttl_from_url(module["path"])

        entities_list = extract_terms_info_sparql(g)
        
        page_title = module["section title"]
        rst += page_title + "\n"
        for ind in range(len(page_title)):
            rst += "="
        rst += "\n\n"
        rst += entities_to_rst(entities_list)

    rst += render_rst_bottom()

    with open("./docs/"+ rst_filename, "w+", encoding="utf-8") as f:
        f.write(rst)



if __name__ == "__main__":

    rendering_workflow()
