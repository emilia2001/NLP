# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rdflib import Graph, URIRef, Namespace
import requests

class ActionAddPersonJob(Action):

    def name(self) -> Text:
        return "action_add_person_job"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        person = tracker.get_slot('person')
        job = tracker.get_slot('job')

        # Define namespaces and RDF graph
        ex = Namespace("http://emi.ro/")
        g = Graph()

        # Create RDF triples
        person_uri = URIRef(ex[person])
        job_uri = URIRef(ex[job])
        g.add((person_uri, ex.hasJob, job_uri))

        # Serialize the graph in RDF format
        rdf_data = g.serialize(format='turtle')

        send_to_graphdb(rdf_data)

        return []

class ActionGetPersonJob(Action):

    def name(self) -> Text:
        return "action_get_person_job"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        person = tracker.get_slot('person')

        adress = "http://localhost:7200/repositories/python"

        interogare = """
        PREFIX ex: <http://emi.ro/>
        SELECT ?job WHERE {
            ex:%s ex:hasJob ?job .
        }
        """ % person

        parametri = {"query":interogare}
        cerere=requests.get(adress,params=parametri)
        return []
    
class ActionAddTaskJob(Action):

    def name(self) -> Text:
        return "action_add_task_job"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        task = tracker.get_slot('task')
        job = tracker.get_slot('job')

        # Define namespaces and RDF graph
        ex = Namespace("http://emi.ro/")
        g = Graph()

        # Create RDF triples
        task_uri = URIRef(ex[task])
        job_uri = URIRef(ex[job])
        g.add((task_uri, ex.isTaskFor, job_uri))

        # Serialize the graph in RDF format
        rdf_data = g.serialize(format='turtle')

        send_to_graphdb(rdf_data)

        return []
    
class ActionGetTaskJob(Action):

    def name(self) -> Text:
        return "action_get_task_job"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        job = tracker.get_slot('job')

        adress = "http://localhost:7200/repositories/python"

        interogare = """
        PREFIX ex: <http://emi.ro/>
        SELECT ?task WHERE {
            ?task ex:isTaskFor ex:%s .
        }
        """ % job

        parametri = {"query":interogare}
        cerere=requests.get(adress,params=parametri)
        return []
    
class ActionAddToolTask(Action):

    def name(self) -> Text:
        return "action_add_tool_task"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        tool = tracker.get_slot('tool')
        task = tracker.get_slot('task')

        # Define namespaces and RDF graph
        ex = Namespace("http://emi.ro/")
        g = Graph()

        # Create RDF triples
        tool_uri = URIRef(ex[tool])
        task_uri = URIRef(ex[task])
        g.add((tool_uri, ex.hasTask, task_uri))

        # Serialize the graph in RDF format
        rdf_data = g.serialize(format='turtle')

        send_to_graphdb(rdf_data)

        return []
    
class ActionGetToolTask(Action):

    def name(self) -> Text:
        return "action_get_tool_task"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        task = tracker.get_slot('task')

        adress = "http://localhost:7200/repositories/python"

        interogare = """
        PREFIX ex: <http://emi.ro/>
        SELECT ?tool WHERE {
            ?tool ex:hasTask ex:%s .
        }
        """ % task

        parametri = {"query":interogare}
        cerere=requests.get(adress,params=parametri)
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