from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rdflib import Graph, URIRef, Namespace
import requests

class ActionAddprocessstep(Action):

    def name(self) -> Text:
        return "action_add_process_step"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process = tracker.get_slot('process')
        step = tracker.get_slot('step')

        # Define namespaces and RDF graph
        ex = Namespace("http://emi.ro/")
        g = Graph()

        # Create RDF triples
        process_uri = URIRef(ex[process])
        step_uri = URIRef(ex[step])
        g.add((process_uri, ex.hasStep, step_uri))

        # Serialize the graph in RDF format
        rdf_data = g.serialize(format='turtle')

        send_to_graphdb(rdf_data)

        return []

class ActionGetprocessstep(Action):

    def name(self) -> Text:
        return "action_get_process_step"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process = tracker.get_slot('process')

        adress = "http://localhost:7200/repositories/python"

        interogare = """
        PREFIX ex: <http://emi.ro/>
        SELECT ?step WHERE {
            ex:%s ex:hasStep ?step .
        }
        """ % process

        parametri = {"query":interogare}
        cerere=requests.get(adress,params=parametri)

        steps = cerere.content.decode().replace("http://emi.ro/", "", -1).splitlines()[1:]  # Skip the header line
        steps_text = ', '.join(steps)
        dispatcher.utter_message(text=f"Steps from process {process}: {steps_text}")

        return []
    
class ActionAddmaterialstep(Action):

    def name(self) -> Text:
        return "action_add_material_step"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        material = tracker.get_slot('material')
        step = tracker.get_slot('step')

        # Define namespaces and RDF graph
        ex = Namespace("http://emi.ro/")
        g = Graph()

        # Create RDF triples
        material_uri = URIRef(ex[material])
        step_uri = URIRef(ex[step])
        g.add((material_uri, ex.isMaterialFor, step_uri))

        # Serialize the graph in RDF format
        rdf_data = g.serialize(format='turtle')

        send_to_graphdb(rdf_data)

        return []
    
class ActionGetmaterialstep(Action):

    def name(self) -> Text:
        return "action_get_material_step"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        step = tracker.get_slot('step')

        adress = "http://localhost:7200/repositories/python"

        interogare = """
        PREFIX ex: <http://emi.ro/>
        SELECT ?material WHERE {
            ?material ex:isMaterialFor ex:%s .
        }
        """ % step

        parametri = {"query":interogare}
        cerere=requests.get(adress,params=parametri)

        materials = cerere.content.decode().replace("http://emi.ro/", "", -1).splitlines()[1:]  # Skip the header line
        materials_text = ', '.join(materials)
        dispatcher.utter_message(text=f"Materials used in {step}: {materials_text}")

        return []
    
class ActionAddToolmaterial(Action):

    def name(self) -> Text:
        return "action_add_tool_material"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        tool = tracker.get_slot('tool')
        material = tracker.get_slot('material')

        # Define namespaces and RDF graph
        ex = Namespace("http://emi.ro/")
        g = Graph()

        # Create RDF triples
        tool_uri = URIRef(ex[tool])
        material_uri = URIRef(ex[material])
        g.add((tool_uri, ex.isRequiredBy, material_uri))

        # Serialize the graph in RDF format
        rdf_data = g.serialize(format='turtle')

        send_to_graphdb(rdf_data)

        return []
    
class ActionGetToolmaterial(Action):

    def name(self) -> Text:
        return "action_get_tool_material"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        material = tracker.get_slot('material')

        adress = "http://localhost:7200/repositories/python"

        interogare = """
        PREFIX ex: <http://emi.ro/>
        SELECT ?tool WHERE {
            ?tool ex:isRequiredBy ex:%s .
        }
        """ % material

        parametri = {"query":interogare}
        cerere=requests.get(adress,params=parametri)

        tools = cerere.content.decode().replace("http://emi.ro/", "", -1).splitlines()[1:]  # Skip the header line
        tools_text = ', '.join(tools)
        dispatcher.utter_message(text=f"Tools required for {material}: {tools_text}")

        return []

    
def send_to_graphdb(rdf_data):
    headers = {
        'Content-Type': 'application/x-turtle',
    }
    response = requests.post('http://localhost:7200/repositories/python/statements', headers=headers, data=rdf_data)
    if response.status_code == 204:
        print("Data successfully added to GraphDB")
    else:
        print(f"Failed to add data: {response.text}")