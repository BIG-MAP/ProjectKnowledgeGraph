import json
from rdflib import Graph, URIRef
import os
from pyld import jsonld

from osw.core import OSW
from osw.wtsite import WtSite
from osw.auth import CredentialManager
import osw.model.entity as model

cred_mngr=CredentialManager()
cred_mngr.add_credential(CredentialManager.UserPwdCredential(
    iri="https://osl-sandbox.big-map.eu",
    username="<bot>",
    password="<pass>"
))
oswc = OSW(site=WtSite(WtSite.WtSiteConfig(
    iri="https://osl-sandbox.big-map.eu",
    cred_mngr=cred_mngr
)))
if not hasattr(model, "Project"):
    oswc.fetch_schema(OSW.FetchSchemaParam(
        schema_title=["Category:OSWb2d7e6a2eff94c82b7f1f2699d5b0ee3"]
    ))

data_folder = os.path.dirname(os.path.dirname(__file__))
print(data_folder)
rdf_graph = Graph()
files = [
    "bigmap.ttl",
    #"domain-datamanagement.ttl",
    #"EURIO.ttl"
]
export_name = "bigmap"
for file in files:
    rdf_graph.parse(os.path.join(data_folder, file), format='ttl')

graph_str = rdf_graph.serialize(format='json-ld', encoding='utf-8', auto_compact=True)
graph = json.loads(graph_str)
graph["@graph"] = sorted(graph["@graph"], key=lambda x: x['@id'])
with open(os.path.join(data_folder, f"{export_name}.jsonld"), 'wt', encoding='utf-8') as f:
    json.dump(graph, f, ensure_ascii=False, indent=4, sort_keys=True)

#with open(os.path.join(data_folder, f"{export_name}.jsonld"), 'rt', encoding='utf-8') as f:
#    graph = json.load(f)

org_context = graph["@context"]
context = {**org_context, **{
    "rdfs_label": "rdfs:label", #sameAs "skos:prefLabel"
    "skos_label": "skos:prefLabel",
    #"eurio_title": "eurio:title",
    #"eurio_description": "eurio:description"
}}

graph = jsonld.compact(graph, context)
with open(os.path.join(data_folder, f"{export_name}.compact.jsonld"), 'wt', encoding='utf-8') as f:
    json.dump(graph, f, ensure_ascii=False, indent=4)

graph["@context"] = context = {**org_context, **{
    "rdfs_label": {"@id": "skos:prefLabel", "@language": "en", "@container": "@set"}, #sameAs "skos:prefLabel"
    "skos_label": {"@id": "skos:prefLabel", "@container": "@set"}
}}
graph = jsonld.expand(graph)


# OwlClass
osw_context_domain_datamanagement = [
    "https://demo.open-semantic-lab.org/wiki/Special:SlotResolver/Category/OSW725a3cf5458f4daea86615fcbd0029f8.slot_jsonschema.json",
    {
        "label": "http://www.w3.org/2004/02/skos/core#prefLabel",
        "description": "rdfs:comment",
        "owl": "http://www.w3.org/2002/07/owl#",
        "eurio": "http://data.europa.eu/s66#"
    }
]
osw_context_bigmap = [
    "https://demo.open-semantic-lab.org/wiki/Special:SlotResolver/Category/OSW725a3cf5458f4daea86615fcbd0029f8.slot_jsonschema.json",
    {
        "eurio": "http://data.europa.eu/s66#",
        "label": {"@id": "http://www.w3.org/2004/02/skos/core#prefLabel", "@container": "@set"},
        #"label": "eurio:title",
        "description": "eurio:description",
        "doi": {"@id": "eurio:doi", "@type": "xsd:anyURI"},
        "start_date": {"@id": "eurio:startDate", "@type": "xsd:date"},
        "end_date": {"@id": "eurio:endDate", "@type": "xsd:date"},
    }
]
osw_context = osw_context_bigmap
graph = jsonld.compact(graph, osw_context)
with open(os.path.join(data_folder, f"{export_name}.osw.compact.jsonld"), 'wt', encoding='utf-8') as f:
    json.dump(graph, f, ensure_ascii=False, indent=4)

classes = [
    {
        "name": "Project",
        "iri": ["http://data.europa.eu/s66#Project", "eurio:Project"]
    },
    {
        "name": "Workpackage",
        "iri": "https://w3id.org/emmo/domain/datamanagement#datamanagement_0a817093_49a9_4762_9eea_7f79a0fcc16b",
        "iri_compact": ""
    },
    {
        "name": "Task",
        "iri": "https://w3id.org/emmo/domain/datamanagement#datamanagement_1ac2d2a5_35d8_48bc_bf3e_5739762cf245",
        "iri_compact": ""
    }
]

def value_match(v1, v2):
    if not isinstance(v1, list): v1 = [v1]
    if not isinstance(v2, list): v2 = [v2]
    return len(list(set(v1) & set(v2))) > 0

entities = []

for c in classes:
    for node in graph["@graph"]:
        if "rdf_type" in node and value_match(node["rdf_type"], c["iri"]):
            print(node["@id"])
            print(f'{c["name"]} {node["label"]} {node["@id"]})')# {node["description"]}') 
            p = model.Project(**node)
            entities.append(node)
            label = node["label"][0]["text"]
            if label.startswith("Task"):
                wp_name = label.split(".")[0].replace("Task ", "WP").replace("Task", "WP")
                wp = None
                for e in entities:
                    e_label = e["label"][0]["text"]
                    if e_label.startswith(wp_name): wp = e
                print(f"Task {label} => WP {wp_name}: {wp['@id']}")
                rdf_graph.add(triple=(
                    URIRef(node["@id"]),
                    URIRef("http://data.europa.eu/s66#isDivisionOf"),
                    URIRef(wp['@id'])
                ))
            if label.startswith("Workpackage"):
                rdf_graph.add(triple=(
                    URIRef(node["@id"]),
                    URIRef("http://data.europa.eu/s66#isDivisionOf"),
                    URIRef("http://data.europa.eu/s66/resource/projects/bf15e03c-4a6e-3ed2-8c1c-184014344ebf") #BIG-MAP
                ))

rdf_graph.serialize(os.path.join(data_folder, f"{export_name}.ttl"), format='ttl', encoding='utf-8',)
graph_str = rdf_graph.serialize(format='json-ld', encoding='utf-8', auto_compact=True)
graph = json.loads(graph_str)
graph["@graph"] = sorted(graph["@graph"], key=lambda x: x['@id'])
with open(os.path.join(data_folder, f"{export_name}.jsonld"), 'wt', encoding='utf-8') as f:
    json.dump(graph, f, ensure_ascii=False, indent=4, sort_keys=True)
