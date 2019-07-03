

from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def student():
    return render_template('template.html')

@app.route('/result',methods = ['POST', 'GET'])
def page2():
    
    text=request.form['text']
    
    reliability=request.form['rank']
    update_old_weight=request.form['update_old_weight']
    init_rank=request.form['init_rank']
    file=request.form['file']
    
    if file == '':
        
        cypher_genration_graph_update(text,reliability,init_rank)
    else:
        graph_update_csv(update_old_weight,reliability,init_rank,file)
    return 'success'
    
def update_graph_csv_file(entity1,relationship,entity2,graph,a,update_old_weight,init_rank,weight):
    
    if update_old_weight:
        for i in a:
            match_query='match a=(:'+ entity1 +'{name:"'+i[0][entity1]+'"})-[:'+ relationship +']->(:'+ entity2 +' {name:"'+i[0][entity2]+'"}) return a'
            a = graph.run(match_query)
            if len(list(a))==0:
                relation_create_query = 'match (a:'+ entity1 +'),(b:'+ entity2 +') where a.name="'+i[0][entity1]+'" and b.name="'+i[0][entity2]+'" create (a)-[:'+ relationship +' {rank:'+str(init_rank)+'}]->(b)'
                graph.run(relation_create_query)
            else:
                weight_update_query = 'match a=(:'+ entity1 +'{name:"'+i[0][entity1]+'"})-[z:'+ relationship +']->(:'+ entity2 +' {name:"'+i[0][entity2]+'"}) set z.rank = z.rank + '+ str(weight)
                graph.run(weight_update_query)
    else:
        for i in a:
            match_query='match a=(:'+ entity1 +'{name:"'+i[0][entity1]+'"})-[:'+ relationship +']->(:'+ entity2 +' {name:"'+i[0][entity2]+'"}) return a'
            a = graph.run(match_query)
            if len(list(a))==0:
                relation_create_query = 'match (a:'+ entity1 +'),(b:'+ entity2 +') where a.name="'+i[0][entity1]+'" and b.name="'+i[0][entity2]+'" create (a)-[:'+ relationship +' {rank:'+str(init_rank)+'}]->(b)'
                graph.run(relation_create_query)
            else:
                pass

def graph_update_csv(update_old_weight,reliability,init_rank,file):
    
    from py2neo import Graph

    weight = reliability
    graph = Graph("http://localhost:7474", auth=("neo4j", "123"))

    file_path = 'file:///'+file
    
    load_data = 'load csv with headers from "'+ file_path +'" as d with d where d.Crop is not null and d.Subcrop is not null and d.Pests is not null and d.Season is not null and d.Diseases is not null return d'
    
    a = graph.run(load_data).to_table()
    
    for i in a:
        for j in i[0]:
            create_nodes = 'merge (:'+j+' {name:"'+i[0][j]+'"})'
            graph.run(create_nodes)
    
    update_graph_csv_file("Crop","subcrop","Subcrop",graph,a,update_old_weight,init_rank,weight)
    
    update_graph_csv_file("Subcrop","affected_by","Pests",graph,a,update_old_weight,init_rank,weight)
    update_graph_csv_file("Subcrop","have_diseases","Diseases",graph,a,update_old_weight,init_rank,weight)
    update_graph_csv_file("Subcrop","suited_season","Season",graph,a,update_old_weight,init_rank,weight)

def relation_entity(Text):
    
    import json
    from ibm_watson import NaturalLanguageUnderstandingV1
    from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, RelationsOptions

    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2019-05-27',
        iam_apikey='Q0YZPCNkdDjJc9G6WOQmtj6jhnHI4MMlOr5pZjT4HRxZ',
        url='https://gateway-fra.watsonplatform.net/natural-language-understanding/api')
    response_relation = natural_language_understanding.analyze(
        text=Text,
        features=Features(relations=RelationsOptions(model="987d6a72-d097-4963-ae8e-8e755b6b07d5"))).get_result()
    response_entity = natural_language_understanding.analyze(
        text=Text,
        features=Features(entities=EntitiesOptions(model="987d6a72-d097-4963-ae8e-8e755b6b07d5"))).get_result()
    return [response_entity,response_relation]



def cypher_genration_graph_update(Text,reliability,init_rank):
    
    import json
    from py2neo import Graph
    entity_json, relation_json = relation_entity(Text)
    graph = Graph("http://localhost:7474", auth=("neo4j", "admin"))
    weight = reliability
    init_rank_for_new_relations = init_rank

    entity = []
    for i in entity_json['entities']:
        entity += [[i['text'].lower(),i['type']]]
    for e in entity:
        entity_create_query = "merge (:"+e[1]+" { name :'"+e[0]+"'})"
        graph.run(entity_create_query)

    relation = []
    for i in relation_json['relations']:
        relation += [[i['arguments'][0]['entities'][0]['type'],i['arguments'][0]['entities'][0]['text'].lower(),i['type'],i['arguments'][1]['entities'][0]['type'],i['arguments'][1]['text'].lower()]]
    for r in relation:
        match_query='match a=(:'+r[0]+'{name:"'+r[1]+'"})-[:'+r[2]+']->(:'+r[3]+'{name:"'+r[4]+'"}) return a'
        a = graph.run(match_query)
        if len(list(a))==0:
            relation_create_query = 'match (a:'+ r[0] +'),(b:'+ r[3] +') where a.name="'+r[1]+'" and b.name="'+r[4]+'" create (a)-[:'+ r[2] +' {rank:'+str(init_rank_for_new_relations)+'}]->(b)'
            graph.run(relation_create_query)
        else:
            graph.run('match a=(:'+r[0]+'{name:"'+r[1]+'"})-[z:'+r[2]+']->(:'+r[3]+'{name:"'+r[4]+'"}) set z.rank = z.rank + '+ str(weight))

if __name__ == '__main__':
    app.run()





