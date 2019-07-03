import logging
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from py2neo import Graph
logger = logging.getLogger(__name__)

class ActionAskQuestation(Action):

    def name(self):
        return "action_ask_questation"

    def run(self, dispatcher, tracker, domain):
        graph = Graph("bolt://localhost:7687", auth=("neo4j","123"))
        print(tracker)
        print(tracker.latest_message)
        print(tracker.latest_message['text'])
        print(tracker.latest_message["intent"])
        a=tracker.latest_message["entities"]
        if len(a)==0:
           dispatcher.utter_message("sorry!! i don't have this information..")
           return []
        e_val=a[0]['value']
        e_type=a[0]['entity']
        b=tracker.latest_message["intent"]['name']
        
        g=graph.run("""match p=(a)-[:"""+b+"""]->(:"""+e_type+"""{name:'"""+e_val+"""'}) return a.name""").to_table()
        h=graph.run("""match p=(:"""+e_type+"""{name:'"""+e_val+"""'})-[:"""+b+"""]->(a)return a.name""").to_table()

        if(list(g)==[] and list(h)==[]):
           dispatcher.utter_message("sorry!! i don't have this information..")
        elif(list(h)==[]):
           dispatcher.utter_message(str(g))
        else:
           dispatcher.utter_message(str(h))

        print(g)
        return []







