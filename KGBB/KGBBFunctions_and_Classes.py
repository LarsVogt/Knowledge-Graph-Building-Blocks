# .\.venvs\lpthw\Scripts\activate
# $env:PYTHONPATH = "$env:PYTHONPATH;."

# to run FLASK in development mode use in Windows shell the cmnd:
# $env:FLASK_ENV = "development"

# Connection info to Neo4j UseCaseKGBB_Database pw:test
# username: python    password: useCaseKGBB   uri: bolt://localhost:7687

# use variable value as anothers variable name:  name="variable_name", exec(name + "= 'value'")


from flask import Flask, session, redirect, url_for, escape, request, flash, render_template
from flask import render_template
from flask import request
from neo4j import GraphDatabase
from datetime import datetime
from KGBB.connectNeo4j import Neo4jConnection
from habanero import cn
import crossref_commons.retrieval
import uuid, re
import ast
import json


connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")





###############################################################################
#                                                                             #
#                                  CLASSES                                    #
#                                                                             #
###############################################################################




# INPUT: publication doi

# OUTPUT: authors, year, title, journal, publisher, doi
class GetPubMeta():

    def __init__(self, doi):
        connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")
        check_entry_query_string = '''MATCH (n:orkg_ScholarlyPublicationEntry_IND) RETURN count(n)'''

        # get publication metadata from crossref for adding a new scholarly publication entry
        ids = doi
        try:
            pub_meta = cn.content_negotiation(ids)
        except:
            pub_meta = crossref_commons.retrieval.get_publication_as_json(ids)
            print("-------------------------------------------------------------------------------")
            print("-------------------------------- PUB METATA RETURN ----------------------------")
            print(pub_meta)

            self.doi = doi

            authors = str(pub_meta.get('author'))
            self.authors = authors


            year = pub_meta.get('published-print').get('date-parts')[0][0]
            self.year = year

            title = pub_meta.get('title')[0]
            self.title = title

            publisher = pub_meta.get('publisher')
            self.publisher = publisher

            topics = pub_meta.get('topic')
            self.topics = topics

            journal = pub_meta.get('publisher')
            try:
                journal = pub_meta.get('journal-title')
            except:
                journal = "None"
            if journal == None:
                journal = "None"
            self.journal = journal

            return




#            entry_check = connection.query(check_entry_query_string, db='neo4j')
#            y = entry_check[0].get("count(n)")

#            if y == 0 :
#                print("No entry existing")
#                flash('Error: CrossRef timed out, pleas try again', 'error')
#                return render_template("lobby_form.html", initiated="True", pubEntry="False")
#            else:
#                print(str(y) + " entries in the graph")
#                flash('Error: CrossRef timed out, please try again', 'error')
#                return render_template("lobby_form.html", initiated="True", pubEntry="True")


        pub_meta = pub_meta[:-2] + "X€€€X"
        print("--------------------------------------------------------------")
        print("-------------------------------- DOI METADATA ----------------")
        print(pub_meta)

        self.doi = doi

        authors = re.search('author = {(.*)},', pub_meta).group(1)
        try:
            authors = authors.replace(" and ", ", ")
        except:
            pass
        self.authors = authors


        year = re.search('year = (.*),', pub_meta)
        self.year = int(year.group(1))

        title = re.search('title = {(.*)},', pub_meta)
        self.title = title.group(1)

        publisher = re.search('publisher = {(.*)},', pub_meta).group(1)
        try:
            publisher = publisher.replace("}", "")
            publisher = publisher.replace("{", "")
        except:
            pass
        self.publisher = publisher


        journal = re.search('journal = {(.*)}X€€€X', pub_meta).group(1)
        try:
            journal = journal.replace("}", "")
            journal = journal.replace("{", "")
        except:
            pass
        self.journal = journal














###############################################################################
#                                                                             #
#                                   FUNCTIONS                                 #
#                                                                             #
###############################################################################




# turns a python list or dict into JSON
def getJSON(file):
    JSON = json.dumps(file)
    return JSON




# INPUT: node_uri
#
# OUTPUT: node
def getNode(node_uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    get_node_query_string = '''MATCH (n {{URI:"{node_uri}"}}) RETURN n'''.format(node_uri=node_uri)
    node_query = connection.query(get_node_query_string, db='neo4j')

    node = node_query[0].get("n")

    return node


# INPUT: entry_uri, node_uri
#
# OUTPUT: Boolean - true for node_uri == root_topic_uri
def checkRootTopic(entry_uri, node_uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    get_node_query_string = '''MATCH (n {{entry_URI:"{entry_uri}", root_topic:"true"}})
    RETURN n.URI'''.format(entry_uri=entry_uri)
    node_query = connection.query(get_node_query_string, db='neo4j')

    root_topic_uri = node_query[0].get("n.URI")

    if root_topic_uri == node_uri:
        result = True
    else:
        result = False
    return result





# INPUT: data_item_uri, key
#
# OUTPUT: object node
def getObjectNodeByDataItem(data_item_uri, key):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    get_object_node_query_string = '''MATCH (n {{URI:"{data_item_uri}"}})
    MATCH (m {{URI:n.{key}}}) RETURN m'''.format(data_item_uri=data_item_uri, key=key)
    node_query = connection.query(get_object_node_query_string, db='neo4j')

    object_node = node_query[0].get("m")

    return object_node




# INPUT: data_item_kgbb_uri
#
# OUTPUT: a dictionary of all input info (including input control information) for the different input possibilities for this KGBB
def getInputInfoNodesDict(data_item_kgbb_uri):
    get_input_info_nodes_query_string = '''MATCH (n:InputInfoKGBBElement_IND {{KGBB_URI:"{data_item_kgbb_uri}"}}) WITH n ORDER BY n.node_type RETURN n'''.format(data_item_kgbb_uri=data_item_kgbb_uri)

    data_item_input_info_nodes = connection.query(get_input_info_nodes_query_string, db='neo4j')

    if data_item_input_info_nodes != None:

        input_info_nodes_dict = {}

        # add all input info nodes as items to input_info_nodes_dict
        for i in range (0, len(data_item_input_info_nodes)):
            node = data_item_input_info_nodes[i].get('n')

            input_info_nodes_dict[i] = node

        print("----------------------------------------------------------------------")
        print("------------------------- INPUT INFO NODES DICT ----------------------")
        print(input_info_nodes_dict)
        return input_info_nodes_dict
    else:
        print("----------------------------------------------------------------------")
        print("------------------------- NO INFO NODES FOUND ------------------------")
        return







# INPUT: data_item_kgbb_uri + data_item_type + data_view_name (e.g. "orkg")
#
# OUTPUT: generates a dict of all container nodes with input info information and saves it to the rep node under the "container_nodes_dict" key
def addContainerAndInputInfoDictToReprNode(data_item_kgbb_uri, data_item_type, data_view_name):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # FIRST: get all container nodes in a dict
    get_kgbb_container_query_string = '''MATCH (m:ContainerKGBBElement_IND {{KGBB_URI:"{data_item_kgbb_uri}", data_view_name:"{data_view_name}"}})
    OPTIONAL MATCH (p:RepresentationKGBBElement_IND {{KGBB_URI:"{data_item_kgbb_uri}", data_view_name:"{data_view_name}"}})
    WITH p, m ORDER BY m.order RETURN m, p.include_html '''.format(data_item_kgbb_uri=data_item_kgbb_uri, data_view_name=data_view_name)

    data_item_container_nodes = connection.query(get_kgbb_container_query_string, db='neo4j')

    print("----------------------------------------------------------------------------")
    print("------------------------ REP & CONTAINER NODES QUERY RESULT ----------------")
    print(data_item_container_nodes)

    if data_item_container_nodes != None:

        raw_container_nodes_dict = {}
        raw_container_nodes_dict["data_item_type"] = data_item_type
        raw_container_nodes_dict["KGBB_URI"] = data_item_kgbb_uri
        raw_container_nodes_dict["include_html"] = data_item_container_nodes[0].get('p.include_html')


        container_nodes_number = len(data_item_container_nodes)   # number of container nodes
        print("----------------------------------------------------------------------------")
        print("--------------------------- DATA ITEM CONTAINER NODES NUMBER ---------------")
        print(container_nodes_number)

        # add all container nodes as items to container_nodes_dict
        for i in range (0, container_nodes_number):
            container_node = data_item_container_nodes[i].get('m')
            order = container_node.get('order')
            raw_container_nodes_dict[order] = container_node
        print("----------------------------------------------------------------------------")
        print("-------------------------- RAW CONTAINER NODES DICT ------------------------")
        print(raw_container_nodes_dict)

    else:
        print("----------------------------------------------------------------------------")
        print("------------------------------ NO CONTAINERS FOUND -------------------------")
        return

    # SECOND: get all input info nodes in a dict
    try:
        input_info_nodes_dict = getInputInfoNodesDict(data_item_kgbb_uri)

        if len(input_info_nodes_dict) > 0:
            # THIRD: include items from the input info nodes dict in the corresponding container dict item
            # iterate over the data_item_container_dict
            more_container_nodes = True
            while more_container_nodes:
                for i in range (0,60000):
                    if i in raw_container_nodes_dict:
                        value = raw_container_nodes_dict.get(i)
                        print("---------------------------------------------------------------------")
                        print("----------------------- UNMODIFIED CONTAINER NODE -------------------")
                        print(value)
                        print(type(value))

                        input_info_URI = value.get('input_info_URI')
                        for m in input_info_nodes_dict:
                            if input_info_nodes_dict.get(m).get('input_info_URI') == input_info_URI:
                                value['input_control'] = input_info_nodes_dict.get(m)
                                print("---------------------------------------------------------------------")
                                print("------------------------- MODIFIED CONTAINER NODE -------------------")
                                print(value)
                                print(type(value))

                        raw_container_nodes_dict[i] = value

                    else:
                        more_container_nodes = False

    except:
        print("----------------------------------------------------------------------")
        print("----------------------- NO INPUT INFO NODES FOUND --------------------")
        pass

    print("----------------------------------------------------------------------------")
    print("--------------- CONTAINER NODES DICT READY TO BE STORED --------------------")
    print(raw_container_nodes_dict)

    if len(raw_container_nodes_dict) > 0:
        set_query_string = '''MATCH (m:RepresentationKGBBElement_IND {{KGBB_URI:"{data_item_kgbb_uri}", data_view_name:"{data_view_name}"}}) SET m.container_nodes_dict = "{raw_container_nodes_dict}"; '''.format(data_item_kgbb_uri=data_item_kgbb_uri, data_view_name=data_view_name, raw_container_nodes_dict=raw_container_nodes_dict)
        print("----------------------------------------------------------------------------")
        print("----------------------- SET CONTAINER QUERY STRING -------------------------")
        print(set_query_string)

        connection.query(set_query_string, db='neo4j')
        return

    else:
        print("----------------------------------------------------------------------------")
        print("----------------------- NO CONTAINER DICT STORED ---------------------------")
        return












# INPUT: entry_uri + data_view_name (e.g. "orkg")
#
# OUTPUT: root_topic_uri, root_topic_cont_dict
def getContDictForRootTopic(entry_uri, data_view_name):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    get_ContDict_for_RootTopic_query_string = '''MATCH (entry {{URI:"{entry_uri}"}})-[:CONTAINS]->(topic {{root_topic:"true"}})
    MATCH (entry_rep:RepresentationKGBBElement_IND {{KGBB_URI:topic.KGBB_URI, data_view_name:"{data_view_name}"}})
    MATCH (topic)-[:CONTAINS*]->(ass {{current_version="true"}})
    MATCH (ass_rep:RepresentationKGBBElement_IND {{KGBB_URI:ass.KGBB_URI, data_view_name:"{data_view_name}"}})
    RETURN DISTINCT topic.URI as root_topic_uri, entry_rep.container_nodes_dict as root_topic_container_dict, ass.URI as ass_uri, ass_rep.container_nodes_dict as ass_container_dict'''.format(entry_uri=entry_uri, data_view_name=data_view_name)

    query_result = connection.query(get_ContDict_for_RootTopic_query_string, db='neo4j')
    root_topic_uri = query_result[0].get('root_topic_uri')
    print("---------------------------------------------------------------------")
    print("------------------- ROOT TOPIC URI -----------------------------------")
    print(root_topic_uri)

    root_topic_cont_dict = query_result[0].get('root_topic_container_dict')
    root_topic_cont_dict = ast.literal_eval(root_topic_cont_dict)
    print("---------------------------------------------------------------------")
    print("------------------- ROOT TOPIC CONTAINER DICT ------------------------")
    print(root_topic_cont_dict)
    print(type(root_topic_cont_dict))

    return root_topic_uri, root_topic_cont_dict











# INPUT: data_item_uri + data_view_name (e.g. "orkg")
#
# OUTPUT: topic_cont_dict
def getContDictForDataItem(data_item_uri, data_view_name):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    get_ContDict_and_InputInfoDict_for_Topic_query_string = '''MATCH (data_item {{URI:"{data_item_uri}"}})
    MATCH (data_item_rep:RepresentationKGBBElement_IND {{KGBB_URI:data_item.KGBB_URI, data_view_name:"{data_view_name}"}})
    RETURN DISTINCT data_item_rep.container_nodes_dict as data_item_container_dict'''.format(data_item_uri=data_item_uri, data_view_name=data_view_name)

    query_result = connection.query(get_ContDict_and_InputInfoDict_for_Topic_query_string, db='neo4j')
    data_item_uri_cont_dict = query_result[0].get('data_item_container_dict')
    data_item_uri_cont_dict = ast.literal_eval(data_item_uri_cont_dict)
    return data_item_uri_cont_dict















# data_view_name (e.g. "orkg")

# Initiates all KGBBs and adds the raw container nodes dict to each KGBB representation node under the key "container_nodes_dict" and the input_info_nodes_dict under the key "input_info_nodes_dict"
def initiateKGBBs(data_view_name):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    get_all_kgbbs_query_string = '''MATCH (n:KGBB) RETURN n'''
    kgbb_nodes = connection.query(get_all_kgbbs_query_string, db='neo4j')


    kgbb_nodes_number = len(kgbb_nodes)   # number of kgbbs
    print("----------------------------------------------------------------------------")
    print("--------------------------- NUMBER OF KGBBs FOUND --------------------------")
    print(kgbb_nodes_number)

    # add all container nodes as items to container_nodes_dict
    for i in range (0, kgbb_nodes_number):
        kgbb_uri = kgbb_nodes[i].get("n").get("URI")
        print("----------------------------------------------------------------------------")
        print("--------------------------------- KGBB URI ---------------------------------")
        print(kgbb_uri)

        data_item_type = kgbb_nodes[i].get("n").get("data_item_type")
        print("----------------------------------------------------------------------------")
        print("-------------------------- KGBB DATA ITEM TYPE -----------------------------")
        print(data_item_type)

        try:
            addContainerAndInputInfoDictToReprNode(kgbb_uri, data_item_type, data_view_name)
        except:
            pass

    return























# add a new entry using a specific Entry KGBB
def addEntry(entry_kgbb_uri, publication_DOI):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # get publication metadata
    pub_meta = GetPubMeta(publication_DOI)

    # cypher query to get the storage_model_cypher_code for the kgbb in question
    search_add_scholarly_publication_entry_query_string = '''MATCH (n {{URI:"{entry_kgbb_uri}"}})
    RETURN n.storage_model_cypher_code'''.format(entry_kgbb_uri=entry_kgbb_uri)

    # query result
    result = connection.query(search_add_scholarly_publication_entry_query_string, db='neo4j')
    print("-------------------------------------------------------------------------------")
    print("--------------------------- INITIAL QUERY -------------------------------------")
    print(result)
    # specify uuid for entry_uri
    entry_uri = str(uuid.uuid4())

    # update some query parameters for the result
    add_scholarly_publication_entry_query_string = result[0].get("n.storage_model_cypher_code")

    add_scholarly_publication_entry_query_string = add_scholarly_publication_entry_query_string.replace("entry_uri", entry_uri)

    add_scholarly_publication_entry_query_string = add_scholarly_publication_entry_query_string.replace("pub_authorsX", pub_meta.authors)

    add_scholarly_publication_entry_query_string = add_scholarly_publication_entry_query_string.replace("pub_titleX", pub_meta.title)

    add_scholarly_publication_entry_query_string = add_scholarly_publication_entry_query_string.replace("pub_yearX", str(pub_meta.year))

    add_scholarly_publication_entry_query_string = add_scholarly_publication_entry_query_string.replace("pub_authorsX", pub_meta.authors)

    add_scholarly_publication_entry_query_string = add_scholarly_publication_entry_query_string.replace("pub_journalX", pub_meta.journal)

    add_scholarly_publication_entry_query_string = add_scholarly_publication_entry_query_string.replace("Xpub_publisherX", pub_meta.publisher)

    add_scholarly_publication_entry_query_string = add_scholarly_publication_entry_query_string.replace("pub_doiX", pub_meta.doi)

    new_uris = True
    i = 1
    while  new_uris:
        if "new_individual_uri{}".format(str(i)) in add_scholarly_publication_entry_query_string:
            add_scholarly_publication_entry_query_string = add_scholarly_publication_entry_query_string.replace("new_individual_uri{}".format(str(i)), str(uuid.uuid4()))
            i += 1
        else:
            new_uris = False

    # query that creates the new entry
    connection.query(add_scholarly_publication_entry_query_string, db='neo4j')


    # check for required topics
    addRequiredTopics(entry_kgbb_uri, entry_uri)

    print("--------------------------------------------------------------------")
    print("---------------------------ADD ENTRY RETURNS ENTRY URI--------------")
    print(entry_uri)
    return entry_uri





# add a new topic to a specific parent_data_item using a specific Topic KGBB
def addTemplateTopic(topic_kgbb_uri, entry_uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # cypher query to get the storage_model_cypher_code for the kgbb in question
    search_add_topic_query_string = '''MATCH (n {{URI:"{topic_kgbb_uri}"}}) RETURN n.storage_model_cypher_code'''.format(topic_kgbb_uri=topic_kgbb_uri)

    # query result
    result = connection.query(search_add_topic_query_string, db='neo4j')

    # specify uuid for topic_uri
    topic_uri = str(uuid.uuid4())

    # update some query parameters for the result
    add_topic_query_string = result[0].get("n.storage_model_cypher_code")

    print("------------------------------------------------------------------------")
    print("----------------------------INITIAL TOPIC QUERY STRING-------------------")
    print(add_topic_query_string)

    add_topic_query_string = add_topic_query_string.replace("entry_URIX", entry_uri)

    add_topic_query_string = add_topic_query_string.replace("topic_URIX", topic_uri)

    print("------------------------------------------------------------------------")
    print("--------------------------------ADD TOPIC QUERY STRING-------------------")
    print(add_topic_query_string)

    new_uris = True
    i = 1
    while  new_uris:
        if "new_individual_uri{}".format(str(i)) in add_topic_query_string:
            add_topic_query_string = add_topic_query_string.replace("new_individual_uri{}".format(str(i)), str(uuid.uuid4()))
            i += 1
        else:
            new_uris = False


    # query that creates the new entry
    connection.query(add_topic_query_string, db='neo4j')



    # check for required assertions
    addRequiredAssertions(topic_kgbb_uri, topic_uri, "topic", entry_uri, topic_uri)

    # check for required topics
    addRequiredTopics(topic_kgbb_uri, entry_uri)


    print("--------------------------------------------------------------------")
    print("---------------------------ADD TOPIC RETURNS TOPIC URI----------------")
    print(topic_uri)
    return topic_uri








# add a new assertion to a specific data item (entry, topic, assertion) using a specific Assertion KGBB

# INPUT: parent_data_item_uri (the uri for data item that contains the assertion - entry, topic, assertion), assertion_kgbb_uri (uri for the relevant assertion KGBB), entry_uri (uri of the entry to which the assertion belongs), topic_uri (uri of the topic to which the assertion belongs - can be None)

# OUTPUT: assertion graph will be created
def addTemplateAssertion(parent_data_item_uri, assertion_kgbb_uri, entry_uri, topic_uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # cypher query to get the storage_model_cypher_code for the kgbb in question
    add_assertion_query_string = '''MATCH (n {{URI:"{assertion_kgbb_uri}"}}) RETURN n.storage_model_cypher_code'''.format(assertion_kgbb_uri=assertion_kgbb_uri)

    # query result
    result = connection.query(add_assertion_query_string, db='neo4j')
    print("---------------------------------------------------------------------------------")
    print("----------------------------INITIAL CYPHER CODE STORAGE QUERY -------------------")
    print(result)


    # specify uuid for assertion_uri
    assertion_uri = str(uuid.uuid4())

    # update some query parameters for the result
    add_assertion_query_string = result[0].get("n.storage_model_cypher_code")

    print("---------------------------------------------------------------------------------")
    print("--------------------------------INITIAL ASSERTION QUERY STRING-------------------")
    print(add_assertion_query_string)

    add_assertion_query_string = add_assertion_query_string.replace("entry_URIX", entry_uri)
    print("---------------------------------------------------------------------------------")
    print("-------------------------------------- REPLACED entry_URIX ----------------------")
    print(add_assertion_query_string)

    add_assertion_query_string = add_assertion_query_string.replace("topic_URIX", topic_uri)
    print("---------------------------------------------------------------------------------")
    print("-------------------------------------- REPLACED topic_URIX -----------------------")
    print(add_assertion_query_string)

    add_assertion_query_string = add_assertion_query_string.replace("assertion_URIX", assertion_uri)

    print("---------------------------------------------------------------------------------")
    print("-------------------------------- REPLACED assertion_URIX ------------------------")
    print(add_assertion_query_string)


    add_assertion_query_string = add_assertion_query_string.replace("parent_data_item_uri", parent_data_item_uri)
    print("--------------------------------------------------------------------------------")
    print("------------------------------------ FINAL QUERY STRING ------------------------")
    print(add_assertion_query_string)


    new_uris = True
    i = 1
    while  new_uris:
        if "new_individual_uri{}".format(str(i)) in add_assertion_query_string:
            add_assertion_query_string = add_assertion_query_string.replace("new_individual_uri{}".format(str(i)), str(uuid.uuid4()))
            i += 1
        else:
            new_uris = False


    # query that creates the new entry
    connection.query(add_assertion_query_string, db='neo4j')


    print("----------------------------------------------------------------------------")
    print("---------------------------ADD ASSERTION RETURNS ASSERTION URI--------------")
    print(assertion_uri)
    return assertion_uri








# sets the key "current_version" for the assertion node and all its data input nodes to "false"
def deleteAssertion(assertion_uri, creator):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # cypher query to get the assertion node, all its input nodes and set them to current_version:"false"
    delete_assertion_query_string = '''MATCH (n)-[:CONTAINS]->(assertion {{URI:"{assertion_uri}"}}) SET n.last_updated_on=localdatetime(), assertion.current_version="false", assertion.last_updated_on=localdatetime()
    WITH n, assertion
    FOREACH (i IN CASE WHEN NOT "{creator}" IN n.contributed_by THEN [1] ELSE [] END |
    SET n.contributed_by = n.contributed_by + "{creator}"
    )
    WITH assertion OPTIONAL MATCH (m {{assertion_URI:"{assertion_uri}", current_version:"true"}})
    SET m.current_version="false", m.last_updated_on = localdatetime()
    WITH assertion MATCH (entry_node {{URI:assertion.entry_URI}}) SET entry_node.last_updated_on=localdatetime()
    WITH assertion, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH assertion OPTIONAL MATCH (assertion)-[:CONTAINS*]->(child {{current_version:"true"}}) SET child.current_version="false", child.last_updated_on=localdatetime()
    WITH assertion, child OPTIONAL MATCH (o {{current_version:"true"}}) WHERE (child.URI IN o.topic_URI) OR (o.topic_URI=child.URI) OR (child.URI IN o.assertion_URI) OR (o.assertion_URI = child.URI) SET o.current_version="false", o.last_updated_on=localdatetime()
    WITH assertion MATCH (parent_data_item_node {{URI:assertion.topic_URI}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH assertion, parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )
    '''.format(assertion_uri=assertion_uri, creator=creator)

    # execute query
    connection.query(delete_assertion_query_string, db='neo4j')
    return






# sets the key "current_version" for the topic node and all data items that it contains together with all of its and their data input nodes to "false"
def deleteTopic(topic_uri, creator):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # cypher query to get the topic node, all its input nodes and all data that it contains and set them to current_version:"false"
    delete_topic_query_string = '''MATCH (n)-[:CONTAINS]->(topic {{URI:"{topic_uri}"}}) SET n.last_updated_on=localdatetime(), topic.current_version="false", topic.last_updated_on=localdatetime()
    WITH n, topic
    FOREACH (i IN CASE WHEN NOT "{creator}" IN n.contributed_by THEN [1] ELSE [] END |
    SET n.contributed_by = n.contributed_by + "{creator}"
    )

    WITH topic OPTIONAL MATCH (m {{current_version:"true"}}) WHERE ("{topic_uri}" IN m.topic_URI) SET m.current_version="false", m.last_updated_on=localdatetime()
    WITH topic MATCH (entry_node {{URI:topic.entry_URI}}) SET entry_node.last_updated_on=localdatetime()
    WITH topic, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH topic OPTIONAL MATCH (topic)-[:CONTAINS*]->(child {{current_version:"true"}}) SET child.current_version="false", child.last_updated_on=localdatetime()
    WITH topic, child OPTIONAL MATCH (o {{current_version:"true"}}) WHERE (child.URI IN o.topic_URI) OR (o.topic_URI=child.URI) OR (child.URI IN o.assertion_URI) OR (o.assertion_URI = child.URI) SET o.current_version="false", o.last_updated_on=localdatetime()'''.format(topic_uri=topic_uri, creator=creator)

    # execute query
    connection.query(delete_topic_query_string, db='neo4j')
    return








# add a single resource to a specific data item (entry, topic, assertion) using a specific KGBB
# INPUT: parent_data_item_uri (the uri for data item that contains the resource - entry, topic, assertion), kgbb_uri (uri for the relevant KGBB), entry_uri (uri of the entry to which the resource belongs), topic_uri (uri of the topic to which the resource belongs - can be None), assertion_uri (uri of the assertion to which the resource belongs - can be None), input_result (specifies what will happen with adding the single resource - either "edit", "added_assertion", or "added_topic"), query_key (the key under which the query can be found), input_value input_value1 input_value2 (user input in form of a string or number - can be None),
# OUTPUT: redirect to the appropriate function and returns their return
def addResource(parent_data_item_uri, kgbb_uri, entry_uri, topic_uri, assertion_uri, input_description, input_type, input_name, ontology_id, input_result, query_key, input_value, input_value1, input_value2):
    if input_result == "added_assertion" or input_result == "edited_assertion":
        result = addAssertion(parent_data_item_uri, kgbb_uri, entry_uri, topic_uri, input_description, input_type, input_name, ontology_id, input_result, query_key, input_value, input_value1, input_value2, assertion_uri)

    elif input_result == "added_topic" or input_result == "edited_topic":
        result = addTopic(parent_data_item_uri, kgbb_uri, entry_uri, topic_uri, input_description, input_type, input_name, ontology_id, input_result, query_key, input_value, input_value1, input_value2)

    return result







# add a new topic to a specific data item (entry, topic, assertion) using a specific Topic KGBB
# INPUT: parent_data_item_uri (the uri for data item that contains the assertion - entry, topic, assertion), topic_kgbb_uri (uri for the relevant topic KGBB), entry_uri (uri of the entry to which the topic belongs), topic_uri (uri of the topic to which the topic belongs - can be None), input_result = "added_topic", query_key (the key under which the query can be found), input_value input_value1 input_value2 (user input in form of a string or number - can be None)
# OUTPUT: topic graph will be created and topic_uri + parent_data_item_uri returned + input_result = "added_topic" returned
def addTopic(parent_data_item_uri, topic_kgbb_uri, entry_uri, topic_uri, input_description, input_type, input_name, ontology_id, input_result, query_key, input_value, input_value1, input_value2):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # cypher query to get the user_input_cypher_code for the kgbb in question
    add_topic_query_string = '''MATCH (n {{URI:"{topic_kgbb_uri}"}}) RETURN n.{query_key}'''.format(topic_kgbb_uri=topic_kgbb_uri, query_key=query_key)

    # query result
    result = connection.query(add_topic_query_string, db='neo4j')
    print("---------------------------------------------------------------------------------")
    print("----------------------------INITIAL CYPHER CODE STORAGE QUERY -------------------")
    print(result)

    # check, whether topic_uri is None
    if topic_uri == "None":
        # specify uuid for topic_uri
        topic_uri = str(uuid.uuid4())


    # update some query parameters for the result
    add_topic_query_string = result[0].get("n." + query_key)
    print("---------------------------------------------------------------------------------")
    print("-------------------------------- INITIAL TOPIC QUERY STRING ----------------------")
    print(add_topic_query_string)

    add_topic_query_string = add_topic_query_string.replace("entry_URIX", entry_uri)
    print("---------------------------------------------------------------------------------")
    print("-------------------------------------- REPLACED entry_URIX ----------------------")
    print(add_topic_query_string)

    add_topic_query_string = add_topic_query_string.replace("topic_URIX", topic_uri)
    print("---------------------------------------------------------------------------------")
    print("-------------------------------------- REPLACED topic_URIX -----------------------")
    print(add_topic_query_string)

    add_topic_query_string = add_topic_query_string.replace("$_input_description_$", input_description)
    print("---------------------------------------------------------------------------------")
    print("-------------------------------- REPLACED DESCRIPTION ---------------------------")
    print(add_topic_query_string)

    add_topic_query_string = add_topic_query_string.replace("$_input_type_$", input_type)
    print("---------------------------------------------------------------------------------")
    print("-------------------------------- REPLACED TYPE ----------------------------------")
    print(add_topic_query_string)

    add_topic_query_string = add_topic_query_string.replace("$_input_name_$", input_name)
    print("---------------------------------------------------------------------------------")
    print("-------------------------------- REPLACED NAME ----------------------------------")
    print(add_topic_query_string)

    add_topic_query_string = add_topic_query_string.replace("$_ontology_ID_$", ontology_id)
    print("---------------------------------------------------------------------------------")
    print("-------------------------------- REPLACED ONTOLOGY ID ---------------------------")
    print(add_topic_query_string)

    if input_value != None:
        add_topic_query_string = add_topic_query_string.replace("$_input_value_$", input_value)
        print("---------------------------------------------------------------------------------")
        print("-------------------------------- REPLACED INPUT VALUE ---------------------------")
        print(add_topic_query_string)

    if input_value1 != None:
        add_topic_query_string = add_topic_query_string.replace("$_input_value1_$", input_value)
        print("---------------------------------------------------------------------------------")
        print("------------------------------- REPLACED INPUT1 VALUE ---------------------------")
        print(add_topic_query_string)

    if input_value2 != None:
        add_topic_query_string = add_topic_query_string.replace("$_input_value2_$", input_value)
        print("---------------------------------------------------------------------------------")
        print("------------------------------- REPLACED INPUT2 VALUE ---------------------------")
        print(add_topic_query_string)

    add_topic_query_string = add_topic_query_string.replace("parent_data_item_uri", parent_data_item_uri)
    print("--------------------------------------------------------------------------------")
    print("------------------------------------ FINAL QUERY STRING ------------------------")
    print(add_topic_query_string)


    new_uris = True
    i = 1
    while  new_uris:
        if "new_individual_uri{}".format(str(i)) in add_topic_query_string:
            add_topic_query_string = add_topic_query_string.replace("new_individual_uri{}".format(str(i)), str(uuid.uuid4()))
            i += 1
        else:
            new_uris = False


    # query that creates the new entry
    connection.query(add_topic_query_string, db='neo4j')

    result = "new_topic"

    print("----------------------------------------------------------------------------")
    print("--------------------------- ADD TOPIC RETURNS TOPIC URI ----------------------")
    print(topic_uri)
    return topic_uri, parent_data_item_uri, input_result

















# add a new assertion to a specific data item (entry, topic, assertion) using a specific Assertion KGBB
# INPUT: parent_data_item_uri (the uri for data item that contains the assertion - entry, topic, assertion), assertion_kgbb_uri (uri for the relevant assertion KGBB), entry_uri (uri of the entry to which the assertion belongs), topic_uri (uri of the topic to which the assertion belongs - can be None), input_result = "added_assertion", query_key (the key under which the query can be found), input_value input_value1 input_value2 (user input in form of a string or number - can be None), assertion_uri (if the parent is an assertion - can be None)
# OUTPUT: assertion graph will be created and assertion_uri + parent_data_item_uri + input_result = "added_assertion" returned
def addAssertion(parent_data_item_uri, assertion_kgbb_uri, entry_uri, topic_uri, input_description, input_type, input_name, ontology_id, input_result, query_key, input_value, input_value1, input_value2, assertion_uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # cypher query to get the user_input_cypher_code for the kgbb in question
    add_assertion_query_string = '''MATCH (n {{URI:"{assertion_kgbb_uri}"}}) RETURN n.{query_key}'''.format(assertion_kgbb_uri=assertion_kgbb_uri, query_key=query_key)

    # query result
    result = connection.query(add_assertion_query_string, db='neo4j')
    print("---------------------------------------------------------------------------------")
    print("----------------------------INITIAL CYPHER CODE STORAGE QUERY -------------------")
    print(result)

    # check, whether assertion_uri is None
    if assertion_uri == "None":
        # specify uuid for assertion_uri
        assertion_uri = str(uuid.uuid4())

    # update some query parameters for the result
    add_assertion_query_string = result[0].get("n." + query_key)
    print("---------------------------------------------------------------------------------")
    print("--------------------------------INITIAL ASSERTION QUERY STRING-------------------")
    print(add_assertion_query_string)

    add_assertion_query_string = add_assertion_query_string.replace("entry_URIX", entry_uri)
    print("---------------------------------------------------------------------------------")
    print("-------------------------------------- REPLACED entry_URIX ----------------------")
    print(add_assertion_query_string)

    add_assertion_query_string = add_assertion_query_string.replace("topic_URIX", topic_uri)
    print("---------------------------------------------------------------------------------")
    print("-------------------------------------- REPLACED topic_URIX -----------------------")
    print(add_assertion_query_string)

    add_assertion_query_string = add_assertion_query_string.replace("assertion_URIX", assertion_uri)
    print("---------------------------------------------------------------------------------")
    print("-------------------------------- REPLACED assertion_URIX ------------------------")
    print(add_assertion_query_string)

    if input_description != None:
        add_assertion_query_string = add_assertion_query_string.replace("$_input_description_$", input_description)
        print("---------------------------------------------------------------------------------")
        print("-------------------------------- REPLACED DESCRIPTION ---------------------------")
        print(add_assertion_query_string)

    if input_type != None:
        add_assertion_query_string = add_assertion_query_string.replace("$_input_type_$", input_type)
        print("---------------------------------------------------------------------------------")
        print("-------------------------------- REPLACED TYPE ----------------------------------")
        print(add_assertion_query_string)

    if input_name != None:
        add_assertion_query_string = add_assertion_query_string.replace("$_input_name_$", input_name)
        print("---------------------------------------------------------------------------------")
        print("-------------------------------- REPLACED NAME ----------------------------------")
        print(add_assertion_query_string)

    if ontology_id != None:
        add_assertion_query_string = add_assertion_query_string.replace("$_ontology_ID_$", ontology_id)
        print("---------------------------------------------------------------------------------")
        print("-------------------------------- REPLACED ONTOLOGY ID ---------------------------")
        print(add_assertion_query_string)

    if input_value != None:
        add_assertion_query_string = add_assertion_query_string.replace("$_input_value_$", input_value)
        print("---------------------------------------------------------------------------------")
        print("-------------------------------- REPLACED INPUT VALUE ---------------------------")
        print(add_assertion_query_string)

    if input_value1 != None:
        add_assertion_query_string = add_assertion_query_string.replace("$_input_value1_$", input_value1)
        print("---------------------------------------------------------------------------------")
        print("-------------------------------- REPLACED INPUT1 VALUE --------------------------")
        print(add_assertion_query_string)

    if input_value2 != None:
        add_assertion_query_string = add_assertion_query_string.replace("$_input_value2_$", input_value2)
        print("---------------------------------------------------------------------------------")
        print("-------------------------------- REPLACED INPUT2 VALUE --------------------------")
        print(add_assertion_query_string)



    add_assertion_query_string = add_assertion_query_string.replace("parent_data_item_uri", parent_data_item_uri)
    print("--------------------------------------------------------------------------------")
    print("------------------------------------ FINAL QUERY STRING ------------------------")
    print(add_assertion_query_string)


    new_uris = True
    i = 1
    while  new_uris:
        if "new_individual_uri{}".format(str(i)) in add_assertion_query_string:
            add_assertion_query_string = add_assertion_query_string.replace("new_individual_uri{}".format(str(i)), str(uuid.uuid4()))
            i += 1
        else:
            new_uris = False


    # query that creates the new entry
    connection.query(add_assertion_query_string, db='neo4j')

    result = "new_assertion"
    print("----------------------------------------------------------------------------")
    print("---------------------------ADD ASSERTION RETURNS ASSERTION URI--------------")
    print(assertion_uri)
    return assertion_uri, parent_data_item_uri, input_result








# add a new assertion to a specific data item (entry, topic, assertion) using a specific Assertion KGBB
# INPUT: parent_data_item_uri (the uri for data item that contains the assertion - entry, topic, assertion), input_kgbb_uri (uri for the KGBB of the resource of which the label must be changed), entry_uri (uri of the entry to which the assertion belongs), topic_uri (uri of the topic to which the assertion belongs - can be None), query_key (the key under which the query can be found), input_label (the new label provided by the user), input_uri (URI of the resource of which the label must be changed)
def editInstanceLabel(parent_data_item_uri, input_kgbb_uri, entry_uri, topic_uri, input_label, query_key, input_uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # cypher query to get the label editing cypher code for the kgbb in question
    edit_label_query_string = '''MATCH (n {{URI:"{input_kgbb_uri}"}}) RETURN n.{query_key}'''.format(input_kgbb_uri=input_kgbb_uri, query_key=query_key)

    # query result
    result = connection.query(edit_label_query_string, db='neo4j')
    print("---------------------------------------------------------------------------------")
    print("----------------------------INITIAL CYPHER CODE EDIT LABEL QUERY ----------------")
    print(result)

    # update some query parameters for the result
    edit_query_string = result[0].get("n." + query_key)
    print("---------------------------------------------------------------------------------")
    print("------------------------------ INITIAL EDIT LABEL QUERY STRING ------------------")
    print(edit_query_string)

    edit_query_string = edit_query_string.replace("entry_URIX", entry_uri)
    print("---------------------------------------------------------------------------------")
    print("-------------------------------------- REPLACED entry_URIX ----------------------")
    print(edit_query_string)

    try:
        edit_query_string = edit_query_string.replace("topic_URIX", topic_uri)
        print("---------------------------------------------------------------------------------")
        print("-------------------------------------- REPLACED topic_URIX -----------------------")
        print(edit_query_string)
    except:
        pass

    edit_query_string = edit_query_string.replace("$_input_uri_$", input_uri)
    print("---------------------------------------------------------------------------------")
    print("-------------------------------- REPLACED INPUT URI -----------------------------")
    print(edit_query_string)




    if input_label != None:
        edit_query_string = edit_query_string.replace("$_label_name_$", input_label)
        print("---------------------------------------------------------------------------------")
        print("-------------------------------- REPLACED LABEL ---------------------------------")
        print(edit_query_string)




    edit_query_string = edit_query_string.replace("parent_data_item_uri", parent_data_item_uri)
    print("--------------------------------------------------------------------------------")
    print("------------------------------------ FINAL QUERY STRING ------------------------")
    print(edit_query_string)


    new_uris = True
    i = 1
    while  new_uris:
        if "new_individual_uri{}".format(str(i)) in edit_query_string:
            edit_query_string = edit_query_string.replace("new_individual_uri{}".format(str(i)), str(uuid.uuid4()))
            i += 1
        else:
            new_uris = False


    # query that creates the new entry
    connection.query(edit_query_string, db='neo4j')

    return






















def existenceCheck(uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # cypher query to check for existence of node with input uri
    check_query_string = '''OPTIONAL MATCH (n {{URI:"{uri}"}}) RETURN n IS NOT NULL AS Predicate'''.format(uri=uri)
    # execute query
    result = connection.query(check_query_string, db='neo4j')
    result = result[0].get("Predicate")
    return result








def addClass(full_id, preferred_name, ontology_id, description):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # cypher query to add the resource as a class resource
    add_class_resource_query_string = '''CREATE (:{ontology_id}_ClassEntity:ClassExpression:Entity {{name:"{ontology_id}: {preferred_name}", URI:"{full_id}", description:"{description}", ontology_class:"true", category:"ClassExpression"}})
    '''.format(full_id=full_id, preferred_name=preferred_name, ontology_id=ontology_id, description=description)

    # execute query
    connection.query(add_class_resource_query_string, db='neo4j')
    return















# INPUT: parent_kgbb_uri, parent_uri,
#
# OUTPUT: not really an output, but adds any required topics
# CONDITION: is used during adding a topic or an entry
def addRequiredTopics(parent_kgbb_uri, parent_uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    search_required_topics_query_string = '''OPTIONAL MATCH (n {{URI:"{parent_kgbb_uri}"}})-[r:HAS_TOPIC_ELEMENT {{required:"true"}}]->()
    WITH PROPERTIES(r) AS required_topic
    RETURN required_topic'''.format(parent_kgbb_uri=parent_kgbb_uri)

    topics_query = connection.query(search_required_topics_query_string, db='neo4j')
    print("-------------------------------------------------------------------------------")
    print("--------------------- INITIAL REQUIRED TOPICS QUERY ----------------------------")
    print(topics_query)

    if topics_query[0].get("required_topic") == None:
        print("-------------------------------------------------------------------------------")
        print("---------------------------- NO REQUIRED TOPICS FOUND --------------------------")
        return

    # add any required topic
    topics_query_len = len(topics_query)
    print("-------------------------------------------------------------------------------")
    print("----------------------------- # OF REQUIRED TOPICS -----------------------------")
    print(topics_query_len)

    for i in range (0, topics_query_len):
        subset = topics_query[i].get("required_topic")
        print("-------------------------------------------------------------------------------")
        print("------------------------- FOUND A REQUIRED TOPIC -------------------------------")
        topic_kgbb_uri = subset.get("target_KGBB_URI")
        topic_uri = addTemplateTopic(topic_kgbb_uri,parent_uri)
        print("-------------------------------------------------------------------------------")
        print("---------------------------- URI OF ADDED TOPICS -------------------------------")
        print(topic_uri)

    return








# INPUT: parent_kgbb_uri, parent_uri, parent_type ("entry", "topic", "assertion"), entry_uri, topic_uri
#
# OUTPUT: not really an output, but adds any required assertions
# CONDITION: is used during adding a topic or an entry
def addRequiredAssertions(parent_kgbb_uri, parent_uri, parent_type, entry_uri, topic_uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # check for required assertions
    search_required_assertions_query_string = '''OPTIONAL MATCH (n {{URI:"{parent_kgbb_uri}"}})-[r:HAS_ASSERTION_ELEMENT {{required:"true"}}]->()
    WITH PROPERTIES(r) AS required_assertion
    RETURN required_assertion'''.format(parent_kgbb_uri=parent_kgbb_uri)

    assertion_query = connection.query(search_required_assertions_query_string, db='neo4j')
    print("-------------------------------------------------------------------------------")
    print("------------------- INITIAL REQUIRED ASSERTIONS QUERY -------------------------")
    print(assertion_query)

    if assertion_query[0].get("required_assertion") == None:
        print("-------------------------------------------------------------------------------")
        print("------------------------ NO REQUIRED ASSERTION FOUND --------------------------")
        return


    # add any required assertion
    assertion_query_len = len(assertion_query)
    print("-------------------------------------------------------------------------------")
    print("-------------------------- # OF REQUIRED ASSERTIONS ---------------------------")
    print(assertion_query_len)

    for i in range (0, assertion_query_len):
        subset = assertion_query[i].get("required_assertion")

        print("-------------------------------------------------------------------------------")
        print("------------------------- ASSERTION KGBB URI & OBJECT URI ---------------------")
        assertion_kgbb_uri = subset.get("target_KGBB_URI")
        print(assertion_kgbb_uri)
        assertion_object_uri = subset.get("assertion_object_URI")
        print(assertion_object_uri)

        try:
            if "$_$" in assertion_object_uri:
                target_node = assertion_object_uri.partition("$_$")[0]
                print("target node: " + target_node)
                target_key = assertion_object_uri.partition("$_$")[2]
                print("target key: " + target_key)

                if target_node == "object":
                    assertion_uri = addTemplateAssertion(parent_uri, assertion_kgbb_uri, entry_uri, topic_uri)

                    print("-------------------------------------------------------------------------------")
                    print("------------------------- URI OF ADDED ASSERTION ------------------------------")
                    print(assertion_uri)

        except:
            pass












# gather initial information about the data item
# INPUT: data_item_uri (i.e. URI of entry, topic, assertion,...) and its data_item_type ("entry", "topic", "assertion")

# OUTPUT: [0]:data_item_uri, [1]:data_item_node, [2]:data_item_kgbb_uri, [3]:data_item_object_uri, [4]:data_item_object_node (entry/topic/assertion object node), [5]:data_item_representation_node (entry/topic/assertion representation node)
def getDataItemInfo(data_item_uri, data_item_type):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # get data item node data from graph as dict
    data_item_return = getDataItemNode(data_item_uri)
    data_item_node = data_item_return[0]
    kgbb_uri = data_item_return[1]
    data_item_object_uri = data_item_return[2]

    # get data item object node data from graph as dict
    data_item_object_node = getDataItemObjectNode(data_item_uri, data_item_type)

    # get data item representation node
    data_item_Rep_data = getDataItemRepNode(kgbb_uri, data_view_name)
    data_item_representation_node =  data_item_Rep_data[0]
    data_item_representation_URI = data_item_Rep_data[1]

    # get all input info nodes for this data item
    input_info_nodes_dict = getInputInfoNodes(kgbb_uri)



    # get all data input nodes belonging to this data item
    input_nodes_dict = getInputNodes(data_item_uri)




    # get all data item container nodes
    container_nodes_dict = getContainerNodes(data_item_representation_URI, data_item_type, data_item_node)

    return data_item_uri, data_item_node, kgbb_uri, data_item_object_uri, data_item_object_node, data_item_representation_node, container_nodes_dict, input_info_nodes_dict, input_nodes_dict








# INPUT: data_item_uri (uri of entry, topic, assertion, etc)
#
# OUTPUT: [0]data_item_node, [1]data_item_kgbb_uri, [2]data_item_object_uri
def getDataItemNode(data_item_uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    get_data_item_node_query_string = '''MATCH (n {{URI:"{data_item_uri}"}}) RETURN n'''.format(data_item_uri=data_item_uri)
    data_item_nodes = connection.query(get_data_item_node_query_string, db='neo4j')
    print("----------------------------------------------------------------------")
    print("------------------------- INITIAL QUERY RESULT -----------------------")
    print(data_item_nodes)
    data_item_node = data_item_nodes[0].get('n')
    print("----------------------------------------------------------------------")
    print("----------------------------- DATA ITEM NODE -------------------------")
    print(data_item_node)


    # get uri of data item knowledge graph building block that manages this data item
    data_item_kgbb_uri = data_item_node.get('KGBB_URI')
    print("----------------------------------------------------------------------")
    print("-------------------------------- KGBB URI ----------------------------")
    print(data_item_kgbb_uri)


    # get uri of data item object
    data_item_object_uri = data_item_node.get('object_URI')
    print("----------------------------------------------------------------------")
    print("---------------------- DATA ITEM OBJECT URI -------------------------")
    print(data_item_object_uri)

    return data_item_node, data_item_kgbb_uri, data_item_object_uri








# INPUT: data_item_uri (uri of entry, topic, assertion, etc), data_item_type (entr, topic, assertion, etc)
#
# OUTPUT: data_item_object_node
def getDataItemObjectNode(data_item_uri, data_item_type):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # get data item object node data from graph as dict
    if data_item_type == "entry":
        label = "entry_URI"
        node_type_label = "entry_object"
    elif data_item_type == "topic":
        label = "topic_URI"
        node_type_label = "topic_object"
    elif data_item_type == "assertion":
        label = "assertion_URI"
        node_type_label = "assertion_object"

    get_data_item_object_node_query_string = '''MATCH (n) WHERE ("{data_item_uri}" IN n.{label}) AND ("{node_type_label}" IN n.data_node_type) RETURN n'''.format(data_item_uri=data_item_uri, label=label, node_type_label=node_type_label)

    data_item_object_nodes = connection.query(get_data_item_object_node_query_string, db='neo4j')
    data_item_object_node = data_item_object_nodes[0].get('n')
    print("----------------------------------------------------------------------")
    print("------------------------ DATA ITEM OBJECT NODE -----------------------")
    print(data_item_object_node)
    return data_item_object_node





# INPUT: data_item_kgbb_uri
#
# OUTPUT: data_item_representation_node, data_item_representation_URI
def getDataItemRepNode(data_item_kgbb_uri, data_view_name):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    get_kgbb_Rep_query_string = '''MATCH (n {{URI:"{data_item_kgbb_uri}"}})-[:HAS_DATA_REPRESENTATION]-> (m {{data_view_name:"{data_view_name}"}}) RETURN m'''.format(data_item_kgbb_uri=data_item_kgbb_uri)
    data_item_representation_nodes = connection.query(get_kgbb_Rep_query_string, db='neo4j')
    data_item_representation_node = data_item_representation_nodes[0].get('m')
    print("----------------------------------------------------------------------")
    print("------------------ DATA ITEM REPRESENTATION NODE ---------------------")
    print(data_item_representation_node)
    data_item_representation_URI = data_item_representation_node.get("URI")
    print("----------------------------------------------------------------------")
    print("---------------- DATA ITEM REPRESENTATION NODE URI -------------------")
    print(data_item_representation_URI)
    return data_item_representation_node, data_item_representation_URI








# INPUT: data_item_kgbb_uri
#
# OUTPUT: input_info_nodes_dict = a dict of all info input nodes
def getInputInfoNodes(data_item_kgbb_uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    get_input_info_nodes_query_string = '''MATCH (n {{URI:"{data_item_kgbb_uri}"}})-[:HAS_INPUT_INFO]->(m {{KGBB_URI:"{data_item_kgbb_uri}"}}) RETURN m'''.format(data_item_kgbb_uri=data_item_kgbb_uri)
    data_item_input_info_nodes = connection.query(get_input_info_nodes_query_string, db='neo4j')

    input_info_nodes_dict = {}

    try:
        len(data_item_input_info_nodes) # number of input info nodes

        # add all input info nodes as items to input_info_nodes_dict
        for i in range (0, len(data_item_input_info_nodes)):
            node = data_item_input_info_nodes[i].get('m')

            input_info_nodes_dict[i] = [node]

    except:
        print("No more input info nodes found.")

    print("----------------------------------------------------------------------")
    print("------------------------- INPUT INFO NODES DICT ----------------------")
    print(input_info_nodes_dict)
    return input_info_nodes_dict






# INPUT: data_item_uri
#
# OUTPUT: input_nodes_dict = a dict of all nodes that carry input data
def getInputNodes(data_item_uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    get_input_nodes_query_string = '''MATCH (m {{user_input:"{data_item_uri}", current_version:"true"}}) WITH m ORDER BY m.data_node_type RETURN m'''.format(data_item_uri=data_item_uri)
    input_nodes = connection.query(get_input_nodes_query_string, db='neo4j')

    input_nodes_dict = {}

    try:
        len(input_nodes) # number of input nodes

        # add all input nodes as items to input_nodes_dict
        i = 0
        for i in range (0, len(input_nodes)):
            node = input_nodes[i].get('m')

            i += 1
            input_nodes_dict[i] = [node]

    except:
        print("No more input nodes found.")

    print("-----------------------------------------------------------------------")
    print("-------------------------- INPUT NODES DICT ---------------------------")
    print(input_nodes_dict)
    return input_nodes_dict




# INPUT: data_item_uri, input_source (input1, input2, etc.)
#
# OUTPUT: input_nodes_dict = a dict of all nodes that carry input data
def getSpecificInputNode(data_item_uri, input_source):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    get_input_node_query_string = '''MATCH (m {{user_input:"{data_item_uri}", input_source:"{input_source}", current_version:"true"}}) RETURN m'''.format(data_item_uri=data_item_uri, input_source=input_source)

    try:
        input_node_query = connection.query(get_input_node_query_string, db='neo4j')
        input_node = input_node_query[0].get('m')
        print("-----------------------------------------------------------------------")
        print("-------------------------- SINGLE INPUT NODE --------------------------")
        return input_node

    except:
        print("No input node found.")






# INPUT: data_item_representation_URI, data_item_type ("entry", "topic", etc), data_item_node
#
# OUTPUT: container_nodes_dict = a dict of all container nodes belonging to this data_item (i.e. entry, topic, assertion)
def getContainerNodes(data_item_representation_URI, data_item_type, data_item_node):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    get_kgbb_container_query_string = '''MATCH (n {{URI:"{data_item_representation_URI}"}})-[:HAS_PART]->(m {{node_type:"container"}}) RETURN m'''.format(data_item_representation_URI=data_item_representation_URI)
    data_item_container_nodes = connection.query(get_kgbb_container_query_string, db='neo4j')

    container_nodes_dict = {}

    try:
        len(data_item_container_nodes) # number of container nodes
        print("--------------------------- DATA ITEM CONTAINER NODES NUMBER ---------------")
        print(len(data_item_container_nodes))

        # add all container nodes as items to container_nodes_dict
        i = 0
        while i < len(data_item_container_nodes)+1:
            container_node = data_item_container_nodes[i].get('m')
            print("------------------------------------------------------------------------")
            print("------------------------------------------------------------------------")
            print("------------------ INPUT CONTAINER NODE --------------------------------")
            print(container_node)
            resolved_container_node = resolveValueAndLabels(container_node, data_item_type, data_item_node)
            print("------------------------------------------------------------------------")
            print("------------------------- OUTPUT CONTAINER NODE ------------------------")
            print(resolved_container_node)


            container_nodes_dict[i] = resolved_container_node
            print("------------------------------------------------------------------------")
            print("--------------------- UPDATED CONTAINER NODE DICT ----------------------")
            print(container_nodes_dict)
            i += 1

    except:
        print("No more container elements found.")

    print("----------------------------------------------------------------------")
    print("-------------------------- CONTAINER NODES DICT ----------------------")
    print(container_nodes_dict)
    return container_nodes_dict










# INPUT: input_node (some container element), data_item_type ("entry", "topic", "assertion"), data_item_node, object_node (entry/topic/assertion object node), input nodes dict)

# OUTPUT: updates the labels, values, tooltip_labels, and tooltip_values of the input node for UI
def resolveValueAndLabels(input_node, data_item_type, data_item_node, object_node, input_nodes_dict):
    b = ["_label", "_value", "_label_tooltip", "_value_tooltip"]
    for x in b:

        # build the label/value/tooltip based on information from various key-value pairs of the representation node
        for i in range (1, 11):

            key = "{a}{x}{i}".format(a=data_item_type, x=x, i=i)

            try:
                if "$_$" in input_node.get(key):
                    target_node = input_node.get(key).partition("$_$")[0]
                    print("front_partition: " + target_node)
                    target_key = input_node.get(key).partition("$_$")[2]
                    print("back_partition: " + target_key)

                    if target_node == "object":
                        label = object_node.get(target_key)
                        input_node[key] = label

                    elif target_node == "node":
                        label = data_item_node.get(target_key)
                        input_node[key] = label

                    elif "input" in target_node:
                        for i in range (0, len(input_nodes_dict)):
                            if target_node == input_nodes_dict[i].get('data_node_type'):
                                input_target = input_nodes_dict[i]
                                label = input_target.get(target_key)
                                input_node[key] = label

                            elif target_node in input_nodes_dict[i].get('data_node_type'):
                                input_target = input_nodes_dict[i]
                                label = input_target.get(target_key)
                                input_node[key] = label

            except:
                pass

    return input_node










# turns a list of items with duplicates into a list of unique items without None-items
def getUniqueList(list):
    # initialize list
    unique_list = []

    # traverse for all elements in list
    for i in list:
        # checks if item already in unique_list
        if i not in unique_list and i != None:
            unique_list.append(i)

    return unique_list




# INPUT: entry_uri, data_view_name (e.g. "orkg")

# OUTPUT:
# getEntryViewData[0] = navi_dict   ->  a dict of all topics and assertions linked to an entry node via :CONTAINS relation chaings, following syntax:  {uri: {'node_type':string, 'name':string, 'child_uris':[list of child uris]}, etc.}
# getEntryViewData[1] = entry_view_tree     ->  a dict of all information required for representing data from an entry in the UI. It follows the syntax:  {order[integer]: {entry_label1:string, entry_value1:string, entry_label_tooltip1:string, entry_value_tooltip1:string...
# getEntryViewData[2] = root_topic_view_tree     ->    a dict of all information required for representing data from the root_topic (i.e. landing topic) of an entry in the UI. It follows the syntax:  {order[integer]: {topic_label1:string, topic_value1:string, topic_label_tooltip1:string, topic_value_tooltip1:string,  placeholder_text:string, editable:Boolean, include_html:string, div_class:string, input_control:{input_info_node}, sub_view_tree: {index[integer]: [assertion_uri, {assertion_view_tree}], etc.}, etc.
def getEntryViewData(entry_uri, data_view_name):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # get navi_dict
    navi_dict = getNaviDict(entry_uri)

    # query string definition for getting all information relevant for viewing the root topic of the entry
    query_string = '''MATCH (entry {{URI:"{entry_uri}"}})-[:CONTAINS]->(topics:orkg_Topic_IND {{current_version:"true", root_topic:"true"}})
    OPTIONAL MATCH (entry_object {{URI:entry.object_URI, current_version:"true"}})
    MATCH (entry_rep:RepresentationKGBBElement_IND {{KGBB_URI:entry.KGBB_URI, data_view_name:"{data_view_name}"}})
    OPTIONAL MATCH (topics_object {{URI:topics.object_URI, current_version:"true"}})
    MATCH (topics_rep:RepresentationKGBBElement_IND {{KGBB_URI:topics.KGBB_URI, data_view_name:"{data_view_name}"}})
    OPTIONAL MATCH (topics)-[:CONTAINS]->(assertion:orkg_Assertion_IND {{current_version:"true"}})
    OPTIONAL MATCH (assertion_object {{URI:assertion.object_URI, current_version:"true"}})
    OPTIONAL MATCH (assertion_rep:RepresentationKGBBElement_IND {{KGBB_URI:assertion.KGBB_URI, data_view_name:"{data_view_name}"}})
    OPTIONAL MATCH (assertion_input_node) WHERE assertion.URI IN assertion_input_node.user_input AND assertion_input_node.input="true"
    OPTIONAL MATCH (topics)-[:CONTAINS]->(topics2:orkg_Topic_IND {{current_version:"true"}})
    OPTIONAL MATCH (topics2_object {{URI:topics2.object_URI, current_version:"true"}})
    OPTIONAL MATCH (topics2_rep:RepresentationKGBBElement_IND {{KGBB_URI:topics2.KGBB_URI, data_view_name:"{data_view_name}"}})
    OPTIONAL MATCH (topics2_input_node) WHERE topics2.URI IN topics2_input_node.user_input AND topics2_input_node.input="true"

    WITH DISTINCT [entry, entry_object, entry_rep.container_nodes_dict] AS entry_info, [topics, topics_object, topics_rep.container_nodes_dict] AS topics, [assertion, assertion_object, assertion_rep.container_nodes_dict] AS assertion, [topics2, topics2_object, topics2_rep.container_nodes_dict] AS topics2, topics2_input_node AS topics2_input, assertion_input_node AS assertion_input, [topics.KGBB_URI, assertion.KGBB_URI, topics2.KGBB_URI] AS KGBBs
    RETURN DISTINCT entry_info, topics, assertion, assertion_input, KGBBs, topics2, topics2_input'''.format(entry_uri=entry_uri, data_view_name=data_view_name)

    query_result = connection.query(query_string, db='neo4j')
    query_result = query_result
    print("---------------------------------------------------------------")
    print("-------------------------- QUERY RESULT -----------------------")
    print(query_result)

    entry_node = query_result[0].get('entry_info')[0]
    print("---------------------------------------------------------------")
    print("-------------------------- ENTRY NODE -------------------------")
    print(entry_node)

    entry_object = query_result[0].get('entry_info')[1]
    print("---------------------------------------------------------------")
    print("------------------------- ENTRY OBJECT ------------------------")
    print(entry_object)

    entry_raw_container_nodes_dict = ast.literal_eval(query_result[0].get('entry_info')[2])
    print("---------------------------------------------------------------")
    print("--------------------- ENTRY RAW CONT DICT ---------------------")
    print(entry_raw_container_nodes_dict)

    entry_view_tree = getSubViewTree(entry_raw_container_nodes_dict, entry_node, entry_object, None)
    print("---------------------------------------------------------------")
    print("----------------------- ENTRY VIEW TREE -----------------------")
    print(entry_view_tree)



    print("---------------------------------------------------------------")
    print("--------------------- QUERY LENGTH ----------------------------")
    print(len(query_result))


    init_assertions = []
    init_topics2 = []
    init_kgbb_list = []
    init_assertion_input = []
    init_topics2_input = []
    for i in range (0, len(query_result)):
        init_assertions.append(query_result[i].get('assertion'))
        print("--------------------------------------------------------------------")
        print("------------------ INIT ASSERTIONS QUERY RESULT --------------------")
        print(init_assertions)

        for m in range (0,2):
            init_kgbb_list.append(query_result[i].get('KGBBs')[m])
        print("--------------------------------------------------------------------")
        print("-------------------------- INIT KGBB LIST --------------------------")
        print(init_kgbb_list)

        init_assertion_input.append(query_result[i].get('assertion_input'))
        print("--------------------------------------------------------------------")
        print("------------------ INIT ASSERTIONS INPUT QUERY RESULT --------------")
        print(init_assertion_input)

        try:
            init_topics2.append(query_result[i].get('topics2'))
            print("--------------------------------------------------------------------")
            print("------------------ INIT TOPICS2 QUERY RESULT ------------------------")
            print(init_topics2)
        except:
            pass

        try:
            init_topics2_input.append(query_result[i].get('topics2_input'))
            print("--------------------------------------------------------------------")
            print("------------------ INIT TOPICS2 INPUT QUERY RESULT ------------------")
            print(init_topics2_input)
        except:
            pass


    # filter for only unique elements in lists
    assertions = getUniqueList(init_assertions)
    print("---------------------------------------------------------------")
    print("---------------- UNIQUE ASSERTIONS RESULT ---------------------")
    print(assertions)
    print(len(assertions))

    kgbb_list = getUniqueList(init_kgbb_list)
    print("---------------------------------------------------------------")
    print("---------------- UNIQUE KGBB LIST RESULT ----------------------")
    print(kgbb_list)
    print(len(kgbb_list))

    assertion_input = getUniqueList(init_assertion_input)
    print("---------------------------------------------------------------")
    print("--------------- UNIQUE ASSERTION INPUT RESULT -----------------")
    print(assertion_input)
    print(len(assertion_input))

    try:
        topics2 = getUniqueList(init_topics2)
        print("---------------------------------------------------------------")
        print("--------------- UNIQUE TOPICS2 RESULT --------------------------")
        print(topics2)
        print(len(topics2))
    except:
        pass

    try:
        topics2_input = getUniqueList(init_topics2_input)
        print("---------------------------------------------------------------")
        print("--------------- UNIQUE TOPICS2 INPUT RESULT --------------------")
        print(topics2_input)
        print(len(topics2_input))
    except:
        pass


    assertion_view_tree = []
    for i in range (0, len(assertions)):
        if assertions[i][0] != None:
            assertion_node = assertions[i][0]
            print("---------------------------------------------------------------")
            print("------------------------ ASSERTION NODE -----------------------")
            print(assertion_node)

            assertion_object = assertions[i][1]
            print("---------------------------------------------------------------")
            print("----------------------- ASSERTION OBJECT ----------------------")
            print(assertion_object)

            assertion_raw_container_nodes_dict = ast.literal_eval(assertions[i][2])
            print("---------------------------------------------------------------")
            print("------------------- ASSERTION RAW CONT DICT -------------------")
            print(assertion_raw_container_nodes_dict)

            assertion_uri = assertions[i][0].get('URI')
            print("---------------------------------------------------------------")
            print("------------------- ASSERTION URI -----------------------------")
            print(assertion_uri)
            assertion_input_item = []
            for m in range (0, len(assertion_input)):
                if assertion_uri == assertion_input[m].get('assertion_URI'):
                    assertion_input_item.append(assertion_input[m])
                    print("---------------------------------------------------------------")
                    print("------------------- ASSERTION INPUT NODES ---------------------")
                    print(assertion_input_item)
            assertion_tree = getSubViewTree(assertion_raw_container_nodes_dict, assertion_node, assertion_object, assertion_input_item)
            assertion_view_tree.append(assertion_tree)

    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print("------------------- ASSERTION VIEW TREE LIST ------------------")
    print(assertion_view_tree)


    if topics2:
        topics2_view_tree = []
        for i in range (0, len(topics2)):
            if topics2[i][0] != None:
                topic2_node = topics2[i][0]
                print("---------------------------------------------------------------")
                print("------------------------ TOPIC2 NODE ---------------------------")
                print(topic2_node)

                topic2_object = topics2[i][1]
                print("---------------------------------------------------------------")
                print("----------------------- TOPIC2 OBJECT --------------------------")
                print(topic2_object)

                topic2_raw_container_nodes_dict = ast.literal_eval(topics2[i][2])
                print("---------------------------------------------------------------")
                print("------------------- TOPIC2 RAW CONT DICT -----------------------")
                print(topic2_raw_container_nodes_dict)

                topic2_uri = topics2[i][0].get('URI')
                print("---------------------------------------------------------------")
                print("------------------- TOPIC2 URI ---------------------------------")
                print(topic2_uri)
                topics2_input_item = []
                if topics2_input:
                    for m in range (0, len(topics2_input)):
                        if topic2_uri == topics2_input[m].get('topic_URI')[0]:
                            topics2_input_item.append(topics2_input[m])
                            print("---------------------------------------------------------------")
                            print("------------------- TOPIC2 INPUT NODES -------------------------")
                            print(topics2_input_item)
                topic2_tree = getSubViewTree(topic2_raw_container_nodes_dict, topic2_node, topic2_object, topics2_input_item)
                topics2_view_tree.append(topic2_tree)

        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")
        print("------------------- TOPICS2 VIEW TREE LIST ---------------------")
        print(topics2_view_tree)


    topics = query_result[0].get('topics')
    topic_node = topics[0]
    print("---------------------------------------------------------------")
    print("------------------------- TOPIC NODE ---------------------------")
    print(topic_node)

    topic_object = topics[1]
    print("---------------------------------------------------------------")
    print("------------------------ TOPIC OBJECT --------------------------")
    print(topic_object)

    topic_raw_container_nodes_dict = ast.literal_eval(topics[2])
    print("---------------------------------------------------------------")
    print("------------------------ TOPIC RAW CONT DICT -------------------")
    print(topic_raw_container_nodes_dict)

    topic_view_tree = getSubViewTree(topic_raw_container_nodes_dict, topic_node, topic_object, None)

    # check for topics and assertions that are displayed by topic
    topic_child_list = navi_dict.get(topic_node.get('URI')).get('children')
    print("---------------------------------------------------------------")
    print("----------------------- TOPIC CHILD LIST -----------------------")
    print(topic_child_list)
    topic_child_len = len(topic_child_list)
    print(topic_child_len)

    for i in range (0, topic_child_len):
        print("i = " + str(i))
        child_uri = topic_child_list[i]
        for j in range (0, len(assertion_view_tree)):
            if assertion_view_tree[j].get('URI') == child_uri:
                kgbb_uri = assertion_view_tree[j].get('KGBB_URI')
                print("---------------------------------------------------------------")
                print("------------------- FOUND KGBB URI ----------------------------")
                print(kgbb_uri)

                for m in range (0, 600):
                    try:
                        topic_view_tree_container = topic_view_tree.get(m)
                        target_kgbb_uri = topic_view_tree_container.get('target_KGBB_URI')
                        if kgbb_uri == target_kgbb_uri:
                            sub_view_tree = topic_view_tree.get(m).get('sub_view_tree')
                            sub_view_tree.append(assertion_view_tree[j])
                            sub_view_tree_length = len(sub_view_tree)
                            topic_view_tree.get(m)['sub_view_tree'] = sub_view_tree
                            topic_view_tree.get(m)['sub_view_tree_length'] = sub_view_tree_length

                            m = 601
                            print("-----------------------------------------------------------")
                            print("----------- SUB VIEW TREE SUCCESSFULLY ADDED --------------")

                    except:
                        pass

        if topics2_view_tree:
            for j in range (0, len(topics2_view_tree)):
                if topics2_view_tree[j].get('URI') == child_uri:
                    kgbb_uri = topics2_view_tree[j].get('KGBB_URI')
                    print("---------------------------------------------------------------")
                    print("------------------- FOUND KGBB URI ----------------------------")
                    print(kgbb_uri)

                    for m in range (0, 600):
                        try:
                            topic_view_tree_container = topic_view_tree.get(m)
                            target_kgbb_uri = topic_view_tree_container.get('target_KGBB_URI')
                            if kgbb_uri == target_kgbb_uri:
                                sub_view_tree = topic_view_tree.get(m).get('sub_view_tree')
                                sub_view_tree.append(topics2_view_tree[j])
                                sub_view_tree_length = len(sub_view_tree)
                                topic_view_tree.get(m)['sub_view_tree'] = sub_view_tree
                                topic_view_tree.get(m)['sub_view_tree_length'] = sub_view_tree_length

                                m = 601
                                print("-----------------------------------------------------------")
                                print("----------- SUB VIEW TREE SUCCESSFULLY ADDED --------------")

                        except:
                            pass


    print("---------------------------------------------------------------")
    print("-------------------------- TOPIC VIEW TREE ---------------------")
    print(topic_view_tree)


    return navi_dict, entry_view_tree, topic_view_tree









# INPUT: entry_uri, topic_uri, data_view_name (e.g. "orkg")

# OUTPUT:
# getTopicViewData[0] = navi_dict   ->  a dict of all topics and assertions linked to an entry node via :CONTAINS relation chaings, following syntax:  {uri: {'node_type':string, 'name':string, 'child_uris':[list of child uris]}, etc.}
# getTopicViewData[1] = topic_view_tree     ->    a dict of all information required for representing data from the input topic of an entry in the UI. It follows the syntax:  {order[integer]: {topic_label1:string, topic_value1:string, topic_label_tooltip1:string, topic_value_tooltip1:string,  placeholder_text:string, editable:Boolean, include_html:string, div_class:string, input_control:{input_info_node}, sub_view_tree: {index[integer]: [assertion_uri, {assertion_view_tree}], etc.}, etc.
def getTopicViewData(entry_uri, topic_uri, data_view_name):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # get navi_dict
    navi_dict = getNaviDict(entry_uri)

    # query string definition for getting all information relevant for viewing the root topic of the entry
    query_string = '''MATCH (topic {{URI:"{topic_uri}"}})
    OPTIONAL MATCH (topic_object {{URI:topic.object_URI, current_version:"true"}})
    MATCH (topic_rep:RepresentationKGBBElement_IND {{KGBB_URI:topic.KGBB_URI, data_view_name:"{data_view_name}"}})
    OPTIONAL MATCH (topic)-[:CONTAINS]->(assertion:orkg_Assertion_IND {{current_version:"true"}})
    OPTIONAL MATCH (assertion_object {{URI:assertion.object_URI, current_version:"true"}})
    OPTIONAL MATCH (assertion_rep:RepresentationKGBBElement_IND {{KGBB_URI:assertion.KGBB_URI, data_view_name:"{data_view_name}"}})
    OPTIONAL MATCH (assertion_input_node) WHERE assertion.URI IN assertion_input_node.user_input AND assertion_input_node.input="true"
    OPTIONAL MATCH (assertion)-[:CONTAINS]->(assertion2:orkg_Assertion_IND {{current_version:"true"}})
    OPTIONAL MATCH (assertion2_object {{URI:assertion2.object_URI, current_version:"true"}})
    OPTIONAL MATCH (assertion2_rep:RepresentationKGBBElement_IND {{KGBB_URI:assertion2.KGBB_URI, data_view_name:"{data_view_name}"}})
    OPTIONAL MATCH (assertion2_input_node) WHERE assertion2.URI IN assertion2_input_node.user_input AND assertion2_input_node.input="true"
    OPTIONAL MATCH (topic)-[:CONTAINS]->(topics2:orkg_Topic_IND {{current_version:"true"}})
    OPTIONAL MATCH (topics2_object {{URI:topics2.object_URI, current_version:"true"}})
    OPTIONAL MATCH (topics2_rep:RepresentationKGBBElement_IND {{KGBB_URI:topics2.KGBB_URI, data_view_name:"{data_view_name}"}})
    OPTIONAL MATCH (topics2_input_node) WHERE topics2.URI IN topics2_input_node.user_input AND topics2_input_node.input="true"
    OPTIONAL MATCH (topic)-[:CONTAINS]->(granTree:orkg_GranularityTree_IND {{current_version:"true"}})
    OPTIONAL MATCH (granTree_object {{URI:granTree.object_URI, current_version:"true"}})
    OPTIONAL MATCH (granTree_rep:RepresentationKGBBElement_IND {{KGBB_URI:granTree.KGBB_URI, data_view_name:"{data_view_name}"}})

    WITH DISTINCT [topic, topic_object, topic_rep.container_nodes_dict] AS topic, [assertion, assertion_object, assertion_rep.container_nodes_dict] AS assertion, [assertion2, assertion2_object, assertion2_rep.container_nodes_dict] AS assertion2, [topics2, topics2_object, topics2_rep.container_nodes_dict] AS topics2, topics2_input_node AS topics2_input, assertion_input_node AS assertion_input, assertion2_input_node AS assertion2_input, [topic.KGBB_URI, assertion.KGBB_URI] AS KGBBs, [granTree, granTree_object, granTree_rep.container_nodes_dict] AS granularityTree
    RETURN DISTINCT topic, assertion, assertion_input, KGBBs, topics2, topics2_input, assertion2, assertion2_input, granularityTree'''.format(topic_uri=topic_uri, data_view_name=data_view_name)

    query_result = connection.query(query_string, db='neo4j')
    query_result = query_result
    print("---------------------------------------------------------------")
    print("-------------------------- QUERY RESULT -----------------------")
    print(query_result)
    print("---------------------------------------------------------------")
    print("--------------------- QUERY LENGTH ----------------------------")
    print(len(query_result))

    init_granularity_trees = []
    init_assertions = []
    init_topics2 = []
    init_kgbb_list = []
    init_assertion_input = []
    init_topics2_input = []
    init_assertion2 = []
    init_assertion2_input = []
    for i in range (0, len(query_result)):
        init_assertions.append(query_result[i].get('assertion'))
        print("--------------------------------------------------------------------")
        print("------------------ INIT ASSERTIONS QUERY RESULT --------------------")
        print(init_assertions)

        for m in range (0,2):
            init_kgbb_list.append(query_result[i].get('KGBBs')[m])
        print("--------------------------------------------------------------------")
        print("-------------------------- INIT KGBB LIST --------------------------")
        print(init_kgbb_list)

        init_assertion_input.append(query_result[i].get('assertion_input'))
        print("--------------------------------------------------------------------")
        print("------------------ INIT ASSERTIONS INPUT QUERY RESULT --------------")
        print(init_assertion_input)

        try:
            init_granularity_trees.append(query_result[i].get('granularityTree'))
            print("--------------------------------------------------------------------")
            print("-------------- INIT GRANULARITY TREES QUERY RESULT -----------------")
            print(init_granularity_trees)
        except:
            pass
        try:
            init_topics2.append(query_result[i].get('topics2'))
            print("--------------------------------------------------------------------")
            print("------------------ INIT TOPICS2 QUERY RESULT ------------------------")
            print(init_topics2)
        except:
            pass

        try:
            init_topics2_input.append(query_result[i].get('topics2_input'))
            print("--------------------------------------------------------------------")
            print("------------------ INIT TOPICS2 INPUT QUERY RESULT ------------------")
            print(init_topics2_input)
        except:
            pass

        try:
            init_assertion2.append(query_result[i].get('assertion2'))
            print("--------------------------------------------------------------------")
            print("------------------ INIT ASSERTION2 QUERY RESULT --------------------")
            print(init_assertion2)
        except:
            pass

        try:
            init_assertion2_input.append(query_result[i].get('assertion2_input'))
            print("--------------------------------------------------------------------")
            print("-------------- INIT ASSERTION2 INPUT QUERY RESULT ------------------")
            print(init_assertion2_input)
        except:
            pass


    # filter for only unique elements in lists
    assertions = getUniqueList(init_assertions)
    print("---------------------------------------------------------------")
    print("---------------- UNIQUE ASSERTIONS RESULT ---------------------")
    print(assertions)
    print(len(assertions))

    kgbb_list = getUniqueList(init_kgbb_list)
    print("---------------------------------------------------------------")
    print("---------------- UNIQUE KGBB LIST RESULT ----------------------")
    print(kgbb_list)
    print(len(kgbb_list))

    assertion_input = getUniqueList(init_assertion_input)
    print("---------------------------------------------------------------")
    print("--------------- UNIQUE ASSERTION INPUT RESULT -----------------")
    print(assertion_input)
    print(len(assertion_input))

    try:
        granularity_trees = getUniqueList(init_granularity_trees)
        print("---------------------------------------------------------------")
        print("--------------- UNIQUE GRANULARITY TREES RESULT ---------------")
        print(granularity_trees)
        print(len(granularity_trees))
    except:
        pass

    try:
        topics2 = getUniqueList(init_topics2)
        print("---------------------------------------------------------------")
        print("--------------- UNIQUE TOPICS2 RESULT --------------------------")
        print(topics2)
        print(len(topics2))
    except:
        pass

    try:
        topics2_input = getUniqueList(init_topics2_input)
        print("---------------------------------------------------------------")
        print("--------------- UNIQUE TOPICS2 INPUT RESULT --------------------")
        print(topics2_input)
        print(len(topics2_input))
    except:
        pass

    try:
        assertion2 = getUniqueList(init_assertion2)
        print("---------------------------------------------------------------")
        print("--------------- UNIQUE ASSERTION2 RESULT ----------------------")
        print(assertion2)
        print(len(assertion2))
    except:
        pass

    try:
        assertion2_input = getUniqueList(init_assertion2_input)
        print("---------------------------------------------------------------")
        print("--------------- UNIQUE ASSERTION2 INPUT RESULT ----------------")
        print(assertion2_input)
        print(len(assertion2_input))
    except:
        pass


    if granularity_trees:
        granularity_trees_view_tree = []
        for i in range (0, len(granularity_trees)):
            if granularity_trees[i][0] != None:
                granularity_trees_node = granularity_trees[i][0]
                print("---------------------------------------------------------------")
                print("----------------------- GRANULARITY TREES NODE ----------------")
                print(granularity_trees_node)

                granularity_trees_object = granularity_trees[i][1]
                print("---------------------------------------------------------------")
                print("---------------------- GRANULARITY TREES OBJECT ---------------")
                print(granularity_trees_object)

                granularity_trees_raw_container_nodes_dict = ast.literal_eval(granularity_trees[i][2])
                print("---------------------------------------------------------------")
                print("------------------ GRANULARITY TREES RAW CONT DICT ------------")
                print(granularity_trees_raw_container_nodes_dict)

                granularity_trees_uri = granularity_trees[i][0].get('URI')
                print("---------------------------------------------------------------")
                print("------------------- GRANULARITY TREES URI ---------------------")
                print(granularity_trees_uri)
                granularity_trees_input_item = []

                granularity_trees_tree = getSubViewTree(granularity_trees_raw_container_nodes_dict, granularity_trees_node, granularity_trees_object, granularity_trees_input_item)
                granularity_trees_view_tree.append(granularity_trees_tree)

        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")
        print("------------------ GRANULARITY TREES VIEW TREE LIST -----------")
        print(granularity_trees_view_tree)



    if assertion2:
        assertion2_view_tree = []
        for i in range (0, len(assertion2)):
            if assertion2[i][0] != None:
                assertion2_node = assertion2[i][0]
                print("---------------------------------------------------------------")
                print("----------------------- ASSERTION2 NODE -----------------------")
                print(assertion2_node)

                assertion2_object = assertion2[i][1]
                print("---------------------------------------------------------------")
                print("---------------------- ASSERTION2 OBJECT ----------------------")
                print(assertion2_object)

                assertion2_raw_container_nodes_dict = ast.literal_eval(assertion2[i][2])
                print("---------------------------------------------------------------")
                print("------------------ ASSERTION2 RAW CONT DICT -------------------")
                print(assertion2_raw_container_nodes_dict)

                assertion2_uri = assertion2[i][0].get('URI')
                print("---------------------------------------------------------------")
                print("------------------- ASSERTION2 URI ----------------------------")
                print(assertion2_uri)
                assertion2_input_item = []
                for m in range (0, len(assertion2_input)):
                    if assertion2_uri == assertion2_input[m].get('assertion_URI'):
                        assertion2_input_item.append(assertion2_input[m])
                        print("---------------------------------------------------------------")
                        print("------------------- ASSERTION2 INPUT NODES --------------------")
                        print(assertion2_input_item)
                assertion2_tree = getSubViewTree(assertion2_raw_container_nodes_dict, assertion2_node, assertion2_object, assertion2_input_item)
                assertion2_view_tree.append(assertion2_tree)

        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")
        print("------------------ ASSERTION2 VIEW TREE LIST ------------------")
        print(assertion2_view_tree)






    assertion_view_tree = []
    for i in range (0, len(assertions)):
        if assertions[i][0] != None:
            assertion_node = assertions[i][0]
            print("---------------------------------------------------------------")
            print("------------------------ ASSERTION NODE -----------------------")
            print(assertion_node)

            assertion_object = assertions[i][1]
            print("---------------------------------------------------------------")
            print("----------------------- ASSERTION OBJECT ----------------------")
            print(assertion_object)

            assertion_raw_container_nodes_dict = ast.literal_eval(assertions[i][2])
            print("---------------------------------------------------------------")
            print("------------------- ASSERTION RAW CONT DICT -------------------")
            print(assertion_raw_container_nodes_dict)

            assertion_uri = assertions[i][0].get('URI')
            print("---------------------------------------------------------------")
            print("------------------- ASSERTION URI -----------------------------")
            print(assertion_uri)
            assertion_input_item = []
            for m in range (0, len(assertion_input)):
                if assertion_uri == assertion_input[m].get('assertion_URI'):
                    assertion_input_item.append(assertion_input[m])
                    print("---------------------------------------------------------------")
                    print("------------------- ASSERTION INPUT NODES ---------------------")
                    print(assertion_input_item)
            assertion_tree = getSubViewTree(assertion_raw_container_nodes_dict, assertion_node, assertion_object, assertion_input_item)

            # check for assertions that are displayed by one of the topic's assertions
            try:
                assertion_child_list = navi_dict.get(assertion_node.get('URI')).get('children')
                print("---------------------------------------------------------------")
                print("----------------------- ASSERTION CHILD LIST ------------------")
                print(assertion_child_list)
                assertion_child_len = len(assertion_child_list)
                print(assertion_child_len)

                for i in range (0, assertion_child_len):
                    print("i = " + str(i))
                    child_uri = assertion_child_list[i]
                    for j in range (0, len(assertion2_view_tree)):
                        if assertion2_view_tree[j].get('URI') == child_uri:
                            kgbb_uri = assertion2_view_tree[j].get('KGBB_URI')
                            print("---------------------------------------------------------------")
                            print("------------------- FOUND KGBB URI ----------------------------")
                            print(kgbb_uri)

                            for m in range (0, 600):
                                try:
                                    assertion_tree_container = assertion_tree.get(m)
                                    target_kgbb_uri = assertion_tree_container.get('target_KGBB_URI')
                                    if kgbb_uri == target_kgbb_uri:
                                        sub_view_tree = assertion_tree.get(m).get('sub_view_tree')
                                        sub_view_tree.append(assertion2_view_tree[j])
                                        sub_view_tree_length = len(sub_view_tree)
                                        assertion_tree.get(m)['sub_view_tree'] = sub_view_tree
                                        assertion_tree.get(m)['sub_view_tree_length'] = sub_view_tree_length

                                        m = 601
                                        print("-----------------------------------------------------------")
                                        print("------ ASSERTION2 SUB VIEW TREE SUCCESSFULLY ADDED --------")
                                except:
                                    pass
            except:
                pass

            assertion_view_tree.append(assertion_tree)

    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print("------------------- ASSERTION VIEW TREE LIST ------------------")
    print(assertion_view_tree)



    if topics2:
        topics2_view_tree = []
        for i in range (0, len(topics2)):
            if topics2[i][0] != None:
                topic2_node = topics2[i][0]
                print("---------------------------------------------------------------")
                print("------------------------ TOPIC2 NODE ---------------------------")
                print(topic2_node)

                topic2_object = topics2[i][1]
                print("---------------------------------------------------------------")
                print("----------------------- TOPIC2 OBJECT --------------------------")
                print(topic2_object)

                topic2_raw_container_nodes_dict = ast.literal_eval(topics2[i][2])
                print("---------------------------------------------------------------")
                print("------------------- TOPIC2 RAW CONT DICT -----------------------")
                print(topic2_raw_container_nodes_dict)

                topic2_uri = topics2[i][0].get('URI')
                print("---------------------------------------------------------------")
                print("------------------- TOPIC2 URI ---------------------------------")
                print(topic2_uri)
                topics2_input_item = []
                if topics2_input:
                    for m in range (0, len(topics2_input)):
                        if topic2_uri == topics2_input[m].get('topic_URI')[0]:
                            topics2_input_item.append(topics2_input[m])
                            print("---------------------------------------------------------------")
                            print("------------------- TOPIC2 INPUT NODES -------------------------")
                            print(topics2_input_item)
                topic2_tree = getSubViewTree(topic2_raw_container_nodes_dict, topic2_node, topic2_object, topics2_input_item)
                topics2_view_tree.append(topic2_tree)

        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")
        print("------------------- TOPICS2 VIEW TREE LIST ---------------------")
        print(topics2_view_tree)


    topic = query_result[0].get('topic')
    topic_node = topic[0]
    print("---------------------------------------------------------------")
    print("------------------------- TOPIC NODE ---------------------------")
    print(topic_node)

    topic_object = topic[1]
    print("---------------------------------------------------------------")
    print("------------------------ TOPIC OBJECT --------------------------")
    print(topic_object)

    topic_raw_container_nodes_dict = ast.literal_eval(topic[2])
    print("---------------------------------------------------------------")
    print("------------------------ TOPIC RAW CONT DICT -------------------")
    print(topic_raw_container_nodes_dict)

    topic_view_tree = getSubViewTree(topic_raw_container_nodes_dict, topic_node, topic_object, None)

    # check for topics, assertions, and granularity trees that are displayed by topic
    topic_child_list = navi_dict.get(topic_node.get('URI')).get('children')
    print("---------------------------------------------------------------")
    print("----------------------- TOPIC CHILD LIST -----------------------")
    print(topic_child_list)
    topic_child_len = len(topic_child_list)
    print(topic_child_len)

    for i in range (0, topic_child_len):
        print("i = " + str(i))
        child_uri = topic_child_list[i]
        for j in range (0, len(assertion_view_tree)):
            if assertion_view_tree[j].get('URI') == child_uri:
                kgbb_uri = assertion_view_tree[j].get('KGBB_URI')
                print("---------------------------------------------------------------")
                print("------------------- FOUND KGBB URI ----------------------------")
                print(kgbb_uri)

                for m in range (0, 600):
                    try:
                        topic_view_tree_container = topic_view_tree.get(m)
                        target_kgbb_uri = topic_view_tree_container.get('target_KGBB_URI')
                        if kgbb_uri == target_kgbb_uri:
                            sub_view_tree = topic_view_tree.get(m).get('sub_view_tree')
                            sub_view_tree.append(assertion_view_tree[j])
                            sub_view_tree_length = len(sub_view_tree)
                            topic_view_tree.get(m)['sub_view_tree'] = sub_view_tree
                            topic_view_tree.get(m)['sub_view_tree_length'] = sub_view_tree_length

                            m = 601
                            print("-----------------------------------------------------------")
                            print("----------- SUB VIEW TREE SUCCESSFULLY ADDED --------------")

                    except:
                        pass

        if topics2_view_tree:
            for j in range (0, len(topics2_view_tree)):
                if topics2_view_tree[j].get('URI') == child_uri:
                    kgbb_uri = topics2_view_tree[j].get('KGBB_URI')
                    print("---------------------------------------------------------------")
                    print("------------------- FOUND KGBB URI ----------------------------")
                    print(kgbb_uri)

                    for m in range (0, 600):
                        try:
                            topic_view_tree_container = topic_view_tree.get(m)
                            target_kgbb_uri = topic_view_tree_container.get('target_KGBB_URI')
                            if kgbb_uri == target_kgbb_uri:
                                sub_view_tree = topic_view_tree.get(m).get('sub_view_tree')
                                sub_view_tree.append(topics2_view_tree[j])
                                sub_view_tree_length = len(sub_view_tree)
                                topic_view_tree.get(m)['sub_view_tree'] = sub_view_tree
                                topic_view_tree.get(m)['sub_view_tree_length'] = sub_view_tree_length

                                m = 601
                                print("-----------------------------------------------------------")
                                print("----------- SUB VIEW TREE SUCCESSFULLY ADDED --------------")

                        except:
                            pass

        if granularity_trees_view_tree:
            for j in range (0, len(granularity_trees_view_tree)):
                if granularity_trees_view_tree[j].get('URI') == child_uri:
                    kgbb_uri = granularity_trees_view_tree[j].get('KGBB_URI')
                    print("---------------------------------------------------------------")
                    print("------------------- FOUND KGBB URI ----------------------------")
                    print(kgbb_uri)

                    for m in range (0, 600):
                        try:
                            topic_view_tree_container = topic_view_tree.get(m)
                            target_kgbb_uri = topic_view_tree_container.get('target_KGBB_URI')
                            if kgbb_uri == target_kgbb_uri:
                                sub_view_tree = topic_view_tree.get(m).get('sub_view_tree')
                                sub_view_tree.append(granularity_trees_view_tree[j])
                                sub_view_tree_length = len(sub_view_tree)
                                topic_view_tree.get(m)['sub_view_tree'] = sub_view_tree
                                topic_view_tree.get(m)['sub_view_tree_length'] = sub_view_tree_length

                                m = 601
                                print("-----------------------------------------------------------")
                                print("----------- SUB VIEW TREE SUCCESSFULLY ADDED --------------")

                        except:
                            pass


    print("---------------------------------------------------------------")
    print("-------------------------- TOPIC VIEW TREE ---------------------")
    print(topic_view_tree)

    return navi_dict, topic_view_tree












# INPUT: data_item_container_dict, data_item_node, data_item_object_node, data_item_input_nodes_dict

# OUTPUT: view_tree dictionary -> a dict of all information required for representing data from a specific data item (i.e. topic, assertion) in the UI. It follows the syntax (here for a topic): {'URI':uri, 'data_item_type':"entry/topic/assertion", 'KGBB_URI':uri, order[integer]: {topic_label1:string, topic_value1:string, topic_label_tooltip1:string, topic_value_tooltip1:string,  placeholder_text:string, editable:Boolean, include_html:string, div_class:string, input_control:{input_info_node}, sub_view_tree: {index[integer]: [assertion_uri, {assertion_view_tree}], etc.}, etc.
def getSubViewTree(data_item_container_dict, data_item_node, data_item_object_node, data_item_input_nodes_dict):
    data_item_type = data_item_container_dict.get('data_item_type')
    data_item_uri = data_item_node.get('URI')

    view_tree = data_item_container_dict # initiates the view_tree as the container nodes dict that must be modified in the following steps

    input_type_list = []
    # if data_item_input_nodes_dict is not empty, then
    try:
        for m in data_item_input_nodes_dict:
            input_type = m.get('type')
            input_type_list.append(input_type)
    except:
        pass

    # add input_type_list to view_tree under key 'input_type_list'
    input_info = {'input_type_list': input_type_list}
    input_info.update(view_tree)
    view_tree = input_info

    # add data_item_uri to view_tree
    data_item_uri_info = {'URI': data_item_uri}
    data_item_uri_info.update(view_tree)
    view_tree = data_item_uri_info


    # iterate over the data_item_container_dict
    more_container_nodes = True
    while more_container_nodes:
        for i in range (0,60000):
            if i in view_tree:
                value = view_tree.get(i)

                value = resolveValueAndLabels(value, data_item_type, data_item_node, data_item_object_node, data_item_input_nodes_dict)
                view_tree[i] = value
            else:
                more_container_nodes = False

    return view_tree










# gather dictionary for navigating through topics and assertions of an entry
# INPUT: entry_uri

# OUTPUT: navi_dict -> a dict of all topics and assertions linked to an entry node via :CONTAINS relation chaings, following syntax:  {uri: {'node_type':string, 'name':string, 'child_uris':[list of child uris]}, etc.}
def getNaviDict(entry_uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # return entry node and all topic nodes that are directly displayed by this entry
    get_displayed_topics_query_string = '''
    MATCH (n {{URI:"{entry_uri}"}})-[:CONTAINS]-> (root_topic {{root_topic:"true", current_version:"true"}})
    OPTIONAL MATCH (n)-[:CONTAINS*]-> (m {{current_version:"true"}})
    OPTIONAL MATCH (m)<-[:CONTAINS]-(x {{current_version:"true"}})
    WITH [n.URI, n.name, n.KGBB_URI, root_topic.node_type, root_topic.name, root_topic.URI, root_topic.KGBB_URI, n.publication_title] as entry_info,
    [x.URI, m.node_type, m.name, m.URI, m.KGBB_URI, m.assertion_label, m.topic_label] as child_info,
    [root_topic.URI, root_topic.node_type, root_topic.name, root_topic.KGBB_URI] as root_topic_info
    RETURN entry_info, child_info, root_topic_info'''.format(entry_uri=entry_uri)
    topic_nodes = connection.query(get_displayed_topics_query_string, db='neo4j')
    print("---------------------------------------------------------------")
    print("----------------- TOPIC_NODES INITIAL QUERY RESULT -------------")
    print(topic_nodes)

    # defines dict and adds entry and root_topic information
    navi_dict = {}
    navi_dict[topic_nodes[0].get('entry_info')[0]] = {'node_type': 'entry', 'name': topic_nodes[0].get('entry_info')[1], 'KGBB_URI': topic_nodes[0].get('entry_info')[2], 'children':[topic_nodes[0].get('entry_info')[5]], 'title':topic_nodes[0].get('entry_info')[7]}
    navi_dict[topic_nodes[0].get('entry_info')[5]] = {'root_topic':"true", 'node_type': topic_nodes[0].get('entry_info')[3], 'name': topic_nodes[0].get('entry_info')[4], 'KGBB_URI': topic_nodes[0].get('entry_info')[6], 'children':[]}

    print("--------------------------------------------------------------------")
    print("------------------INITIAL NAVIGATION DICT---------------------------")
    print(navi_dict)

    len(topic_nodes) # number of found topic nodes
    print(len(topic_nodes))

    # add all topic nodes as items to topics dict
    for i in range(0, len(topic_nodes)):
        # gather information to be added to the topic element dict
        item_node = topic_nodes[i].get('child_info')
        parent_uri = item_node[0]
        node_uri = item_node[3]
        if not navi_dict.get(node_uri):
            if item_node[1] == 'assertion':
                navi_dict[node_uri] = {'node_type': item_node[1], 'name': item_node[5], 'KGBB_URI': item_node[4], 'children':[]}
            elif 'topic' in item_node[1]:
                if item_node[6]:
                    navi_dict[node_uri] = {'node_type': item_node[1], 'name': item_node[6], 'KGBB_URI': item_node[4], 'children':[]}
                else:
                    navi_dict[node_uri] = {'node_type': item_node[1], 'name': item_node[5], 'KGBB_URI': item_node[4], 'children':[]}
            else:
                navi_dict[node_uri] = {'node_type': item_node[1], 'name': item_node[2], 'KGBB_URI': item_node[4], 'children':[]}
            navi_dict.get(parent_uri).get('children').append(node_uri)
        else:
            continue

    print("--------------------- FINAL NAVIGATION DICT OUTPUT -----------------")
    print(navi_dict)
    return navi_dict












def updateEntryDict(entry_dict, selected_uri):
    # find previously selected item
    for item in entry_dict:
        if item.get('state').get('selected') == True:
            print("----------------------------------------------------------------------")
            print("--------------------- URI PREVIOUSLY SELECTED ------------------------")
            print(item.get('id'))
            if item.get('id') != selected_uri:
                item.get('state')['selected'] = False
                item.get('state')['opened'] = False
                print("----------------------------------------------------------------------")
                print("---------------- UPDATED PREVIOUSLY SELECTED -------------------------")
                print(item)
            else:
                return entry_dict
    # find selected item
    for selected_item in entry_dict:
        if selected_item.get('id') == selected_uri:
            selected_item.get('state')['selected'] = True
            selected_item.get('state')['opened'] = True
            print("----------------------------------------------------------------------")
            print("-------------- UPDATED SELECTED ITEM ---------------------------------")
            print(selected_item)

    print("------------------------------------------------------------------------")
    print("---------------------- UPDATED ENTRY DICT ------------------------------")
    print(entry_dict)
    return entry_dict









# gives back bioportal return [0]answer, [1]preferred_name, [2] full_id, [3]ontology_id, [4]parent_uri, [5]entry_uri, [6]topic_uri, [7]assertion_uri, [8]parent_item_type, [9]kgbb_uri, [10]input_results_in, [11]description, [12]query_key, [13]deleted_item_uri, [14]input_value
def getBioPortalSingleInputData (input_name):
    description = "Bioportal API does not provide a description for this resource"

    try:
        bioportal_answer = request.form[input_name]
        print("-------------------------- BIOPORTAL ANSWER -----------------------------")
        print(bioportal_answer)
    except:
        bioportal_answer=None

    try:
        bioportal_preferred_name = request.form[input_name + '_bioportal_preferred_name']
        print("----------------------- BIOPORTAL PREFERRED NAME ------------------------")
        print(bioportal_preferred_name)
    except:
        bioportal_preferred_name=None

    try:
        bioportal_full_id = request.form[input_name + '_bioportal_full_id']
        print("------------------------- BIOPORTAL FULL ID -----------------------------")
        print(bioportal_full_id)
    except:
        bioportal_full_id=None

    try:
        bioportal_ontology_id = request.form[input_name + '_bioportal_ontology_id']
        print("----------------------- BIOPORTAL ONTOLOGY ID ---------------------------")
        print(bioportal_ontology_id)
    except:
        bioportal_ontology_id=None

    parent_uri = request.form[input_name + '_parent_uri']
    print("------------------------------ PARENT URI -------------------------------")
    print(parent_uri)

    entry_uri = request.form[input_name + '_entry_uri']
    print("------------------------------ ENTRY URI --------------------------------")
    print(entry_uri)

    topic_uri = request.form[input_name + '_topic_uri']
    print("------------------------------ TOPIC URI ---------------------------------")
    print(topic_uri)

    assertion_uri = request.form[input_name + '_assertion_uri']
    print("------------------------------ ASSERTION URI ----------------------------")
    print(assertion_uri)

    parent_item_type = request.form[input_name + '_parent_item_type']
    print("----------------------- PARENT DATA ITEM TYPE ---------------------------")
    print(parent_item_type)

    kgbb_uri = request.form[input_name + '_kgbb_uri']
    print("------------------------------- KGBB URI --------------------------------")
    print(kgbb_uri)

    input_result = request.form[input_name + '_input_result']
    print("---------------------------- INPUT RESULTS IN ---------------------------")
    print(input_result)

    query_key = request.form[input_name + '_query_key']
    print("---------------------------- QUERY KEY ----------------------------------")
    print(query_key)

    deleted_item_uri = request.form[input_name + '_deleted_item_uri']
    print("--------------------- DETELED ITEM URI ----------------------------------")
    print(deleted_item_uri)

    try:
        input_value = request.form[input_name + '_value']
        print("---------------------- INPUT VALUE ----------------------------------")
        print(input_value)
    except:
        input_value=None

    try:
        input_value1 = request.form[input_name + '_value1']
        print("---------------------- INPUT VALUE ----------------------------------")
        print(input_value1)
    except:
        input_value1=None

    try:
        input_value2 = request.form[input_name + '_value2']
        print("---------------------- INPUT VALUE ----------------------------------")
        print(input_value2)
    except:
        input_value2=None

    return bioportal_answer, bioportal_preferred_name, bioportal_full_id, bioportal_ontology_id, parent_uri, entry_uri, topic_uri, assertion_uri, parent_item_type, kgbb_uri, input_result, description, query_key, deleted_item_uri, input_value, input_value1, input_value2






def getEditHistory(data_item_uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # query string definition for getting all edit steps for this data item uri and all its child items by date, item name, user name, and uri of edited resource
    history_query_string = '''MATCH (n {{URI:"{data_item_uri}"}})
    OPTIONAL MATCH (n)-[:CONTAINS*]->(m)
    OPTIONAL MATCH (x) WHERE (m.URI IN x.topic_URI) OR (m.URI IN x.assertion_URI) OR (x.topic_URI=m.URI) OR (x.assertion_URI=m.URI)
    WITH n, m, x ORDER BY n.last_updated_on, m.last_updated_on, x.last_updated_on DESC
    RETURN [n.last_updated_on, n.name, n.created_by, n.current_version, n.created_on, n.URI] AS n, [m.last_updated_on, m.name, m.created_by, m.current_version, m.created_on, m.URI] AS m, [x.last_updated_on, x.name, x.created_by, x.current_version, x.created_on, x.URI] AS x'''.format(data_item_uri=data_item_uri)

    query_result = connection.query(history_query_string, db='neo4j')
    print("---------------------------------------------------------------")
    print("---------------------- HISTORY QUERY RESULT -------------------")
    print(query_result)
    edit_history = []
    for i in range (0, len(query_result)):
        item = query_result[i]
        #for each n, m, and x in dictonary, get the corresponding list and change the neo4j datetime into isoformat and append to edit_history list as list-items
        item1 = item.get('n')
        item1_last_update = item1[0].isoformat()
        item1_created = item1[4].isoformat()
        item1.pop(0)
        item1.insert(0, item1_last_update)
        item1.pop(4)
        item1.insert(4, item1_created)
        edit_history.append(item1)

        item2 = item.get('m')
        if item2[0] != None:
            item2_last_update = item2[0].isoformat()
            item2_created = item2[4].isoformat()
            item2.pop(0)
            item2.insert(0, item2_last_update)
            item2.pop(4)
            item2.insert(4, item2_created)
            edit_history.append(item2)

        item3 = item.get('x')
        if item3[0] != None:
            item3_last_update = item3[0].isoformat()
            item3_created = item3[4].isoformat()
            item3.pop(0)
            item3.insert(0, item3_last_update)
            item3.pop(4)
            item3.insert(4, item3_created)
            edit_history.append(item3)

    # delete duplicates in list of lists
    edit_history = getUniqueList(edit_history)

    return edit_history





# creates a new version of the data_item and links it to the data_item using pav properties. Also updates the previous current version of the data_item as just a version and links it to the new current version.
def createVersion(data_item_uri, type):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    if type == "Entry":
        key = "entry_URI"
        label = ":orkg_VersionedEntry_IND:orkg_Entry_IND:iao_Document_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity"
        type_uri = "orkg_versioned_entry_class_URI"
        label2 =":VersionedEntryDOI_IND:EntryDOI_IND:DOI_IND:Literal_IND"

    elif type == "Topic":
        key = "topic_URI"
        label = ":orkg_VersionedTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity"
        type_uri = "orkg_versioned_topic_class_URI"
        label2 =":VersionedTopicDOI_IND:TopicDOI_IND:DOI_IND:Literal_IND"

    elif type == "Assertion":
        key = "assertion_URI"
        label = ":orkg_VersionedAssertion_IND:orkg_Assertion_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity"
        type_uri = "orkg_versioned_assertion_class_URI"
        label2 =":VersionedAssertionDOI_IND:AssertionDOI_IND:DOI_IND:Literal_IND"


    version_uri = str(uuid.uuid4())
    version_doi = str(uuid.uuid4())

    # query string definition for getting all versions of this data item uri
    versions_query_string = '''MATCH (data_item {{URI:"{data_item_uri}", current_version:"true"}})

    WITH DISTINCT data_item
    MATCH (current_version_true_nodes {{{key}:"{data_item_uri}", current_version:"true"}}) SET current_version_true_nodes.versioned_doi = current_version_true_nodes.versioned_doi + "{version_doi}"

    WITH DISTINCT data_item, current_version_true_nodes
    OPTIONAL MATCH (data_item)-[r1:HAS_CURRENT_VERSION]->(previous_current_version)

    MERGE (data_item)-[:HAS_CURRENT_VERSION {{category:"ObjectPropertyExpression", URI:"http://purl.org/pav/hasCurrentVersion", description:"This resource has a more specific, versioned resource with equivalent content. This property is intended for relating a non-versioned or abstract resource to a single snapshot that can be used as a permalink to indicate the current version of the content. For instance, if today is 2013-12-25, then a News topic can indicate a corresponding snapshot resource which will refer to the news as they were of 2013-12-25. <http://news.example.com/> pav:hasCurrentVersion <http://news.example.com/2013-12-25/> . 'Equivalent content' is a loose definition, for instance the snapshot resource might include additional information to indicate it is a snapshot, and is not required to be immutable. Other versioned resources indicating the content at earlier times MAY be indicated with the superproperty pav:hasVersion, one of which MAY be related to the current version using pav:hasCurrentVersion: <http://news.example.com/2013-12-25/> pav:previousVersion <http://news.example.com/2013-12-24/> . <http://news.example.com/> pav:hasVersion <http://news.example.com/2013-12-23/> . Note that it might be confusing to also indicate pav:previousVersion from a resource that has hasCurrentVersion relations, as such a resource is intended to be a long-living 'unversioned' resource. The PAV ontology does however not formally restrict this, to cater for more complex scenarios with multiple abstraction levels. Similarly, it would normally be incorrect to indicate a pav:hasCurrentVersion from an older version; instead the current version would be found by finding the non-versioned resource that the particular resource is a version of, and then its current version. This property is normally used in a functional way, although PAV does not formally restrict this."}}]->(version{label} {{name:"Version of:" + data_item.name, URI:"{version_uri}", {key}:"{data_item_uri}", created_on:datetime(), version_type:"{type}", version:1, versioned_doi:"{version_doi}", version_of:"{data_item_uri}", created_by:"ORKGuserORCID", contributed_by:data_item.contributed_by, type:"{type_uri}"}})

    MERGE (version)-[:HAS_DOI {{category:"DataPropertyExpression", URI:"http://prismstandard.org/namespaces/basic/2.0/doi"}}]->(doi{label2} {{value:"{version_doi}", versioned_doi:"{version_doi}", {key}:"{data_item_uri}", category:"NamedIndividual"}})

    MERGE (version)-[:IDENTIFIER {{category:"DataPropertyExpression", URI:"https://dublincore.org/specifications/dublin-core/dcmi-terms/#identifier"}}]->(doi)

    WITH DISTINCT data_item, version, previous_current_version, r1

    FOREACH (i IN CASE WHEN previous_current_version IS NOT NULL THEN [1] ELSE [] END |

    MERGE (data_item)-[:HAS_VERSION {{category:"ObjectPropertyExpression", URI:"http://purl.org/pav/hasVersion", description:"This resource has a more specific, versioned resource. This property is intended for relating a non-versioned or abstract resource to several versioned resources, e.g. snapshots. For instance, if there are two snapshots of the News topic, made on 23rd and 24th of December, then: <http://news.example.com/> pav:hasVersion <http://news.example.com/2013-12-23/> ; pav:hasVersion <http://news.example.com/2013-12-24/> . If one of the versions has somewhat the equivalent content to this resource (e.g. can be used as a permalink for this resource), then it should instead be indicated with the subproperty pav:hasCurrentVersion: <http://news.example.com/> pav:hasCurrentVersion <http://news.example.com/2013-12-25/> . To order the versions, use pav:previousVersion: <http://news.example.com/2013-12-25/> pav:previousVersion <http://news.example.com/2013-12-24/> . <http://news.example.com/2013-12-24/> pav:previousVersion <http://news.example.com/2013-12-23/> . Note that it might be confusing to also indicate pav:previousVersion from a resource that has pav:hasVersion relations, as such a resource is intended to be a long-living 'unversioned' resource. The PAV ontology does however not formally restrict this, to cater for more complex scenarios with multiple abstraction levels. pav:hasVersion is a subproperty of dcterms:hasVersion to more strongly define this hierarchical pattern. It is therefore also a subproperty of pav:generalizationOf (inverse of prov:specializationOf). To indicate the existence of other, non-hierarchical kind of editions and adaptations of this resource that are not versioned snapshots (e.g. Powerpoint slides has a video recording version), use instead dcterms:hasVersion or prov:alternateOf."}}]->(previous_current_version)

    MERGE (version)-[:PREVIOUS_VERSION {{category:"ObjectPropertyExpression", URI:"http://purl.org/pav/previousVersion", description:"The previous version of a resource in a lineage. For instance a news article updated to correct factual information would point to the previous version of the article with pav:previousVersion. If however the content has significantly changed so that the two resources no longer share lineage (say a new article that talks about the same facts), they can instead be related using pav:derivedFrom. This property is normally used in a functional way, although PAV does not formally restrict this. Earlier versions which are not direct ancestors of this resource may instead be provided using the superproperty pav:hasEarlierVersion. A version number of this resource can be provided using the data property pav:version. To indicate that this version is a snapshot of a more general, non-versioned resource, e.g. 'Weather Today' vs. 'Weather Today on 2013-12-07', see pav:hasVersion. Note that it might be confusing to indicate pav:previousVersion from a resource that also has pav:hasVersion or pav:hasCurrentVersion relations, as such resources are intended to be a long-living and 'unversioned', while pav:previousVersion is intended for use between permalink-like 'snapshots' arranged in a linear history."}}]->(previous_current_version)

    SET version.version = previous_current_version.version +1

    DELETE r1
    )

    RETURN version'''.format(data_item_uri=data_item_uri, key=key, label=label, version_uri=version_uri, type_uri=type_uri, version_doi=version_doi, label2=label2, type=type)

    connection.query(versions_query_string, db='neo4j')

    return









def getVersionsDict(data_item_uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # query string definition for getting all versions of this data item uri
    versions_query_string = '''MATCH (n {{URI:"{data_item_uri}"}})
    OPTIONAL MATCH (n)-[:HAS_VERSION]->(m)
    OPTIONAL MATCH (n)-[:HAS_CURRENT_VERSION]-> (o)
    RETURN o, m'''.format(data_item_uri=data_item_uri)

    query_result = connection.query(versions_query_string, db='neo4j')
    print("---------------------------------------------------------------")
    print("---------------------- VERSIONS QUERY RESULT ------------------")
    print(query_result)

    if query_result[0].get('m') == None and query_result[0].get('o') == None:
        result = None
        return result

    else:
        past_versions = []
        versions_dict = {}
        try:
            for i in range (0, len(query_result)):
                past_version = query_result[i].get('m')
                past_version['created_on'] = past_version['created_on'].isoformat()
                past_versions.append(past_version)

            # delete duplicates in list
            past_versions = getUniqueList(past_versions)
            versions_dict['past_versions'] = past_versions
            print("-------------------------------------------------------")
            print("-------------------- PAST VERSIONS LIST ----------------")
            print(versions_dict)
        except:
            pass
        current_version = query_result[0].get('o')
        current_version['created_on'] = current_version['created_on'].isoformat()
        versions_dict['current_version'] = current_version
        print("-------------------------------------------------------")
        print("-------------------- VERSIONS DICT --------------------")
        print(versions_dict)
        return versions_dict
















# gather dictionary for navigating of a granularity tree
# INPUT: granularity_tree_uri, kgbb_uri, selected_uri

# OUTPUT: a dict of all elements of the granularity tree, following syntax:  [{id:element_uri, parent:parent_element_uri, text:string, topic:topic_URI, state:{opened:boolean, selected:boolean}, li_attr:{}, a_attr:{}}, etc.]
def getGranularityTreeNaviJSON(granularity_tree_uri, kgbb_uri, selected_uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # return entry node and all topic nodes that are directly displayed by this entry
    get_granularity_tree_items_query_string = '''
    MATCH (n {{URI:"{kgbb_uri}"}})
    WITH n.granularity_tree_key AS key, n.partial_order_relation AS granularity_tree_relation
    MATCH (n)-[:IS_ABOUT]->(root {{key:"{granularity_tree_uri}", current_version:"true"}})
    MATCH (root)-[:granularity_tree_relation*]->(nodes {{key:"{granularity_tree_uri}", current_version:"true"}})
    MATCH (nodes)<-[:granularity_tree_relation]-(parent_node {{key:"{granularity_tree_uri}", current_version:"true"}})
    WITH [parent_node.URI, nodes.URI, nodes.topic_URI, nodes.name] AS child_info, [root.URI, root.topic_URI, root.name] AS root_info
    RETURN child_info, root_info'''.format(kgbb_uri=kgbb_uri, granularity_tree_uri=granularity_tree_uri)
    results = connection.query(get_granularity_tree_items_query_string, db='neo4j')
    print("---------------------------------------------------------------")
    print("--------- GRANULARITY TREE NAVI INITIAL QUERY RESULT ----------")
    print(results)

    # starting the GranTreeNaviJS with the root node
    root_info = results[0].get('root_info')
    if root_info[0] == selected_uri:
        granularity_tree_naviJSON = [{'id': root_info[0], 'parent':'''#''', 'text': root_info[2], 'topic':root_info[1], 'state': {'opened': True, 'selected': True}, 'li_attr':{}, 'a_attr':{}}]
    else:
        granularity_tree_naviJSON = [{'id': root_info[0], 'parent':'''#''', 'text': root_info[2], 'topic':root_info[1], 'state': {'opened': False, 'selected': False}, 'li_attr':{}, 'a_attr':{}}]
    # adding the other nodes
    child_info = results[0].get('child_info')
    for node in child_info:
        if node[1] == selected_uri:
            nodeJSON = [{'id': node[1], 'parent':node[0], 'text': node[3], 'topic':node[2], 'state': {'opened': True, 'selected': True}, 'li_attr':{}, 'a_attr':{}}]
        else:
            nodeJSON = [{'id': node[1], 'parent':node[0], 'text': node[3], 'topic':node[2], 'state': {'opened': False, 'selected': False}, 'li_attr':{}, 'a_attr':{}}]
        granularity_tree_naviJSON.append(nodeJSON)

    print("---------------------------------------------------------")
    print("---------- GRANULARITY TREE NAVI JSON -------------------")
    print(granularity_tree_naviJSON)
    return granularity_tree_naviJSON










# gather list of dictionaries for navigating through topics and assertions of an entry
# INPUT: entry_uri, data_view_name

# OUTPUT: a list of dictionaries of all topics, assertions, and granularity trees linked to an entry node via :CONTAINS relation chains, following syntax:  [{id:data_item_uri, component:string, node:{data_item_node}, parent:parent_uri, node_type:entry/topic/assertion/granularity_tree, text:name, icon:image, object:{object_node}, rep_node:{representation_node}, html:html, topics: [{HAS_topic_ELEMENT representation info}], assertions: [{HAS_ASSERTION_ELEMENT representation info}], granularity_trees: [{HAS_GRANULARITY_TREE_ELEMENT representation info}], (various component links by their own keys, extracted from the rep_node), state:{required for navi tree}, "input_name//from input_info":{'input_control':{input control}, 'input_nodes':[{input_node}, etc.]}}, etc.]

def getEntryDict(entry_uri, data_view_name):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # return entry node and all topic nodes that are directly displayed by this entry
    get_entry_dict_information_query_string = '''
    MATCH (entry {{URI:"{entry_uri}"}})
    MATCH (entry_rep:RepresentationKGBBElement_IND {{KGBB_URI:entry.KGBB_URI, data_view_name:"{data_view_name}"}})
    OPTIONAL MATCH (entry)-[:HAS_CURRENT_VERSION]->(entry_current_version)
    OPTIONAL MATCH (entry)-[:HAS_VERSION]->(entry_version)
    OPTIONAL MATCH (entry_kgbb {{URI:entry.KGBB_URI}})-[entry_topics:HAS_TOPIC_ELEMENT]->()
    OPTIONAL MATCH (entry_kgbb {{URI:entry.KGBB_URI}})-[entry_assertions:HAS_ASSERTION_ELEMENT]->()
    OPTIONAL MATCH (entry_kgbb {{URI:entry.KGBB_URI}})-[entry_granularity_trees:HAS_GRANULARITY_TREE_ELEMENT]->()
    OPTIONAL MATCH (entry_obj {{URI:entry.object_URI, current_version:"true"}})
    OPTIONAL MATCH (entry_input_info:InputInfoKGBBElement_IND {{KGBB_URI:entry.KGBB_URI}})
    OPTIONAL MATCH (entry_input_node {{entry_URI:"{entry_uri}", current_version:"true", input_info_URI:entry_input_info.URI}})

    OPTIONAL MATCH (entry)-[:CONTAINS*]-> (child_item {{current_version:"true"}})
    OPTIONAL MATCH (child_item)<-[:CONTAINS]-(parent_item {{current_version:"true"}})
    MATCH (child_item_rep:RepresentationKGBBElement_IND {{KGBB_URI:child_item.KGBB_URI, data_view_name:"{data_view_name}"}})
    OPTIONAL MATCH (child_item)-[:HAS_CURRENT_VERSION]->(child_item_current_version)
    OPTIONAL MATCH (child_item)-[:HAS_VERSION]->(child_item_version)
    OPTIONAL MATCH (child_item_kgbb {{URI:child_item.KGBB_URI}})-[child_item_topics:HAS_TOPIC_ELEMENT]->()
    OPTIONAL MATCH (child_item_kgbb {{URI:child_item.KGBB_URI}})-[child_item_assertions:HAS_ASSERTION_ELEMENT]->()
    OPTIONAL MATCH (child_item_kgbb {{URI:child_item.KGBB_URI}})-[child_item_granularity_trees:HAS_GRANULARITY_TREE_ELEMENT]->()
    OPTIONAL MATCH (child_item_obj {{URI:child_item.object_URI, current_version:"true"}})
    OPTIONAL MATCH (child_item_input_info:InputInfoKGBBElement_IND {{KGBB_URI:child_item.KGBB_URI}})
    OPTIONAL MATCH (child_item_input_node {{current_version:"true", input_info_URI:child_item_input_info.URI}}) WHERE (child_item.URI IN child_item_input_node.topic_URI) OR (child_item.URI IN child_item_input_node.assertion_URI)

    WITH [entry, entry_rep, entry_obj, entry_input_info, entry_input_node, PROPERTIES(entry_topics), PROPERTIES(entry_assertions), PROPERTIES(entry_granularity_trees)] AS entry_info, [parent_item.URI, child_item, child_item_rep, child_item_obj, child_item_input_info, child_item_input_node, PROPERTIES(child_item_topics), PROPERTIES(child_item_assertions), PROPERTIES(child_item_granularity_trees)] AS child_info, entry_current_version AS entry_current_version, entry_version AS entry_version, child_item_current_version AS child_item_current_version, child_item_version AS child_item_version

    RETURN DISTINCT entry_info, child_info, entry_current_version, entry_version, child_item_current_version, child_item_version'''.format(entry_uri=entry_uri, data_view_name=data_view_name)
    results = connection.query(get_entry_dict_information_query_string, db='neo4j')

    entry_node = results[0].get('entry_info')[0]
    entry_node['created_on'] = entry_node['created_on'].isoformat()
    entry_node['last_updated_on'] = entry_node['last_updated_on'].isoformat()

    entry_object = results[0].get('entry_info')[2]
    entry_object['created_on'] = entry_object['created_on'].isoformat()
    entry_object['last_updated_on'] = entry_object['last_updated_on'].isoformat()

    init_entry_input_info = []
    try:
        for i in range (0, len(results)):
            init_entry_input_info.append(results[i].get('entry_info')[3])
    except:
        pass
    entry_input_info = getUniqueList(init_entry_input_info)
    print("---------------------------------------------------------------")
    print("----------------- ENTRY INPUT INFO QUERY RESULT ---------------")
    print(entry_input_info)
    print(len(entry_input_info))

    init_entry_input_nodes = []
    try:
        for i in range (0, len(results)):
            init_entry_input_nodes.append(results[i].get('entry_info')[4])
    except:
        pass
    entry_input_nodes = getUniqueList(init_entry_input_nodes)
    print("---------------------------------------------------------------")
    print("---------------- ENTRY INPUT NODES QUERY RESULT ---------------")
    print(entry_input_nodes)
    print(len(entry_input_nodes))

    init_entry_topics = []
    try:
        for i in range (0, len(results)):
            init_entry_topics.append(results[i].get('entry_info')[5])
    except:
        pass
    entry_topics = getUniqueList(init_entry_topics)
    print("---------------------------------------------------------------")
    print("----------------- ENTRY TOPICS QUERY RESULT --------------------")
    print(entry_topics)
    print(len(entry_topics))

    init_entry_assertions = []
    try:
        for i in range (0, len(results)):
            init_entry_assertions.append(results[i].get('entry_info')[6])
    except:
        pass
    entry_assertions = getUniqueList(init_entry_assertions)
    print("---------------------------------------------------------------")
    print("----------------- ENTRY ASSERTIONS QUERY RESULT ---------------")
    print(entry_assertions)
    print(len(entry_assertions))

    init_entry_granularity_trees = []
    try:
        for i in range (0, len(results)):
            init_entry_granularity_trees.append(results[i].get('entry_info')[7])
    except:
        pass
    entry_granularity_trees = getUniqueList(init_entry_granularity_trees)
    print("---------------------------------------------------------------")
    print("----------- ENTRY GRANULARITY TREES QUERY RESULT --------------")
    print(entry_granularity_trees)
    print(len(entry_granularity_trees))


    init_entry_versions = []
    try:
        entry_current_version = results[0].get('entry_current_version')
        entry_current_version['created_on'] = entry_current_version['created_on'].isoformat()
        init_entry_versions.append(entry_current_version)
    except:
        pass

    try:
        for i in range (0, len(results)):
            version = results[i].get('entry_version')
            version['created_on'] = version['created_on'].isoformat()
            init_entry_versions.append(version)
    except:
        pass
    entry_versions = getUniqueList(init_entry_versions)
    print("---------------------------------------------------------------")
    print("----------------- ENTRY VERSIONS QUERY RESULT -----------------")
    print(entry_versions)
    print(len(entry_versions))

    if entry_current_version:
        version_value = True
    else:
        version_value = False



    entry_dict = []
    # preparing the entry_dict_element for the entry_dict
    entry_dict_element = {'id': entry_uri, 'version': False, 'version_exists': version_value, 'component':results[0].get('entry_info')[1].get('component'), 'node':entry_node, 'parent':'''#''', 'node_type': results[0].get('entry_info')[0].get('node_type'), 'text': results[0].get('entry_info')[2].get('name'), 'versions_info': entry_versions,'icon': url_for('static', filename='Entry_ICON_small.png'), 'object':entry_object, 'html':results[0].get('entry_info')[1].get('html'), 'topics':entry_topics, 'assertions':entry_assertions, 'granularity_trees':entry_granularity_trees, 'state': {'opened': True, 'selected': True}, 'li_attr':{}, 'a_attr':{}}

    # extract various component links from the entry rep_node. They are "stored" in the rep_node by consecutively numbered integer keys and the key under which they must be added to the entry_dict_element is the value of the "name" key.
    entry_rep_node = results[0].get('entry_info')[1]
    search_key = "link_$$$_"
    link_dict = dict(filter(lambda item: search_key in item[0], entry_rep_node.items()))
    for link_key in link_dict:
        component_link_string = entry_rep_node.get(link_key)
        component_link = ast.literal_eval(component_link_string)
        print("------------------------------------------------")
        print("------------------------------------------------")
        print("------------ COMPONENT LINK DICT ---------------")
        print("------------------------------------------------")
        print("------------------------------------------------")
        print(component_link)
        key_name = component_link.get('name')
        print("------------------------------------------------")
        print("------------------------------------------------")
        print("------------ KEY NAME --------------------------")
        print("------------------------------------------------")
        print("------------------------------------------------")
        print(key_name)
        print(type(key_name))
        print(type(component_link))
        entry_dict_element[key_name] = component_link
        # delete this key-value from the entry_rep_node
        entry_rep_node.pop(link_key)
    # add the entry_rep_node to the entry_dict_element under the key 'rep_node'
    entry_dict_element['rep_node'] = entry_rep_node

    # gathering input information by input type - if information available, the following will be added: 'input_name': {'input_control': input_info_node, 'input_nodes': [list of input nodes that belong to the input control]}
    try:
        for input in entry_input_info:
            input_name = input.get('input_name')
            input_uri = input.get('URI')
            input_dict = {'input_control': input, 'input_nodes':[]}
            try:
                for node in entry_input_nodes:
                    if node.get('input_info_URI') == input_uri:
                        node['created_on'] = node['created_on'].isoformat()
                        node['last_updated_on'] = node['last_updated_on'].isoformat()
                        input_dict.get('input_nodes').append(node)
                entry_dict_element[input_name] = input_dict
            except:
                pass
    except:
        pass
    entry_dict.append(entry_dict_element)
    print("---------------------------------------------------------------")
    print("-------------------- ENTRY DICT ITEM --------------------------")
    print(entry_dict)
    print(len(entry_dict))






    # clearing the child_info results to unique results
    init_child_info = []
    try:
        for i in range (0, len(results)):
            init_child_info.append(results[i].get('child_info'))
    except:
        pass
    child_info = getUniqueList(init_child_info)
    print("---------------------------------------------------------------")
    print("-------------- UNIQUE CHILD INFO QUERY RESULT -----------------")
    print(child_info)
    print(len(child_info))


    init_child_input_nodes = []
    try:
        for i in range (0, len(child_info)):
            init_child_input_nodes.append(child_info[i][5])
    except:
        pass
    child_input_nodes = getUniqueList(init_child_input_nodes)
    print("---------------------------------------------------------------")
    print("---------------- CHILD INPUT NODES QUERY RESULT ---------------")
    print(child_input_nodes)
    print(len(child_input_nodes))

    init_child_input_infos = []
    try:
        for i in range (0, len(child_info)):
            init_child_input_infos.append(child_info[i][4])
    except:
        pass
    child_input_infos = getUniqueList(init_child_input_infos)
    print("---------------------------------------------------------------")
    print("---------------- CHILD INPUT INFOS QUERY RESULT ---------------")
    print(child_input_infos)
    print(len(child_input_infos))




    # appending the entry_dict with child items
    for child_item in child_info:
        child_node = child_item[1]
        child_node['created_on'] = child_node['created_on'].isoformat()
        child_node['last_updated_on'] = child_node['last_updated_on'].isoformat()
        child_item_uri = child_node.get('URI')
        child_object = child_item[3]
        child_object['created_on'] = child_object['created_on'].isoformat()
        child_object['last_updated_on'] = child_object['last_updated_on'].isoformat()

        init_child_item_topics = []
        try:
            for i in range (0, len(child_info)):
                if child_info[i][1].get('URI') == child_item_uri:
                    if child_item[1].get('KGBB_URI') == child_info[i][6].get('KGBB_URI'):
                        init_child_item_topics.append(child_info[i][6])
        except:
            pass
        child_item_topics = getUniqueList(init_child_item_topics)
        print("---------------------------------------------------------------")
        print("----------------- CHILD ITEM TOPICS QUERY RESULT ---------------")
        print(child_item_topics)
        print(len(child_item_topics))

        init_child_item_assertions = []
        try:
            for i in range (0, len(child_info)):
                if child_info[i][1].get('URI') == child_item_uri:
                    if child_item[1].get('KGBB_URI') == child_info[i][7].get('KGBB_URI'):
                        init_child_item_assertions.append(child_info[i][7])
        except:
            pass
        child_item_assertions = getUniqueList(init_child_item_assertions)
        print("---------------------------------------------------------------")
        print("------------ CHILD ITEM ASSERTIONS QUERY RESULT ---------------")
        print(child_item_assertions)
        print(len(child_item_assertions))

        init_child_item_granularity_trees = []
        try:
            for i in range (0, len(child_info)):
                if child_info[i][1].get('URI') == child_item_uri:
                    if child_item[1].get('KGBB_URI') == child_info[i][8].get('KGBB_URI'):
                        init_child_item_granularity_trees.append(child_info[i][8])
        except:
            pass
        child_item_granularity_trees = getUniqueList(init_child_item_granularity_trees)
        print("---------------------------------------------------------------")
        print("---------- CHILD ITEM GRANULARITY TREES QUERY RESULT ----------")
        print(child_item_granularity_trees)
        print(len(child_item_granularity_trees))

        if child_item[1].get('node_type') == "topic":
            icon = url_for('static', filename='Topic_ICON_small.png')
        elif child_item[1].get('node_type') == "assertion":
            icon = url_for('static', filename='Assertion_ICON_small.png')
        elif child_item[1].get('node_type') == "granularity_tree":
            icon = url_for('static', filename='GranularityTree_ICON_small.png')


        # starting the NaviJS with the entry node
        child_dict = {'id': child_node.get('URI'), 'component':child_item[2].get('component'),'node':child_node, 'parent':child_item[0], 'node_type': child_item[1].get('node_type'), 'icon': icon, 'object':child_object, 'html':child_item[2].get('html'), 'topics':child_item_topics, 'assertions':child_item_assertions, 'granularity_trees':child_item_granularity_trees, 'state': {'opened': False, 'selected': False}, 'li_attr':{}, 'a_attr':{}}

        # extract various component links from the child_item rep_node. They are "stored" in the rep_node by consecutively numbered integer keys and the key under which they must be added to the child_dict dictionary is the value of the "name" key.
        child_rep_node = child_item[2]
        search_key = "link_$$$_"
        child_link_dict = dict(filter(lambda item: search_key in item[0], child_rep_node.items()))
        for child_link_key in child_link_dict:
            component_link_string = child_rep_node.get(child_link_key)
            component_link = ast.literal_eval(component_link_string)
            key_name = component_link.get('name')
            child_dict[key_name] = component_link
            # delete this key-value from the child_rep_node
            child_rep_node.pop(child_link_key)
        # add the child_rep_node to the child_dict under the key 'rep_node'
        child_dict['rep_node'] = child_rep_node

        # gathering input information by input type - if information available, the following will be added: 'input_name': {'input_control': input_info_node, 'input_nodes': [list of input nodes that belong to the input control]}
        if child_item[1].get('node_type') == 'assertion':
            child_dict['text'] = child_node.get('assertion_label')

        elif child_item[1].get('node_type') == 'topic':
            child_dict['text'] = child_node.get('topic_label')

        elif child_item[1].get('node_type') == 'granularity_tree':
            child_dict['text'] = child_node.get('name')


        entry_dict.append(child_dict)

    # check for duplicates
    entry_dict = getUniqueList(entry_dict)


    # check for input_info and input_nodes
    for item in entry_dict:
        init_child_item_input_info = []
        try:
            for i in range (0, len(child_input_infos)):
                if item.get('node').get('KGBB_URI') == child_input_infos[i].get('KGBB_URI'):
                        init_child_item_input_info.append(child_input_infos[i])
        except:
            pass
        child_item_input_info = getUniqueList(init_child_item_input_info)
        print("---------------------------------------------------------------")
        print("----------------- CHILD ITEM INPUT INFO QUERY RESULT ---------------")
        print(child_item_input_info)
        print(len(child_item_input_info))

        try:
            for input in child_item_input_info:
                input_name = input.get('input_name')
                input_uri = input.get('URI')
                input_dict = {'input_control': input, 'input_nodes':[]}

                try:
                    for node in child_input_nodes:
                        if node.get('input_info_URI') == input_uri and node.get('user_input') == item.get('node').get('URI'):
                            node['created_on'] = node['created_on'].isoformat()
                            node['last_updated_on'] = node['last_updated_on'].isoformat()
                            input_dict.get('input_nodes').append(node)
                    item[input_name] = input_dict
                except:
                    pass
        except:
            pass


    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print("-------------------- FINAL ENTRY DICT ITEM --------------------")
    print(entry_dict)
    print(len(entry_dict))
    return entry_dict




















# gather list of dictionaries for navigating through topics and assertions of an entry
# INPUT: entry_uri, data_view_name

# OUTPUT: a list of dictionaries of all topics, assertions, and granularity trees linked to an entry node via :CONTAINS relation chains, following syntax:  [{id:data_item_uri, component:string, node:{data_item_node}, parent:parent_uri, node_type:entry/topic/assertion/granularity_tree, text:name, icon:image, object:{object_node}, rep_node:{representation_node}, html:html, topics: [{HAS_topic_ELEMENT representation info}], assertions: [{HAS_ASSERTION_ELEMENT representation info}], granularity_trees: [{HAS_GRANULARITY_TREE_ELEMENT representation info}], (various component links by their own keys, extracted from the rep_node), state:{required for navi tree}, "input_name//from input_info":{'input_control':{input control}, 'input_nodes':[{input_node}, etc.]}}, etc.]

def getVersDict(entry_uri, data_view_name, version_doi):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # return entry node and all topic nodes that are directly displayed by this entry
    get_entry_dict_information_query_string = '''
    MATCH (entry {{URI:"{entry_uri}"}})
    MATCH (entry_rep:RepresentationKGBBElement_IND {{KGBB_URI:entry.KGBB_URI, data_view_name:"{data_view_name}"}})
    OPTIONAL MATCH (entry)-[:HAS_CURRENT_VERSION]->(current_version) WHERE "{version_doi}" IN current_version.versioned_doi
    OPTIONAL MATCH (entry)-[:HAS_VERSION]->(version) WHERE "{version_doi}" IN version.versioned_doi
    OPTIONAL MATCH (entry_kgbb {{URI:entry.KGBB_URI}})-[entry_topics:HAS_TOPIC_ELEMENT]->()
    OPTIONAL MATCH (entry_kgbb {{URI:entry.KGBB_URI}})-[entry_assertions:HAS_ASSERTION_ELEMENT]->()
    OPTIONAL MATCH (entry_kgbb {{URI:entry.KGBB_URI}})-[entry_granularity_trees:HAS_GRANULARITY_TREE_ELEMENT]->()
    OPTIONAL MATCH (entry_obj {{URI:entry.object_URI}}) WHERE "{version_doi}" IN entry_obj.versioned_doi
    OPTIONAL MATCH (entry_input_info:InputInfoKGBBElement_IND {{KGBB_URI:entry.KGBB_URI}})
    OPTIONAL MATCH (entry_input_node {{entry_URI:"{entry_uri}", input_info_URI:entry_input_info.URI}}) WHERE "{version_doi}" IN entry_input_node.versioned_doi

    OPTIONAL MATCH (entry)-[:CONTAINS*]-> (child_item) WHERE "{version_doi}" IN child_item.versioned_doi
    OPTIONAL MATCH (child_item)<-[:CONTAINS]-(parent_item) WHERE "{version_doi}" IN parent_item.versioned_doi
    MATCH (child_item_rep:RepresentationKGBBElement_IND {{KGBB_URI:child_item.KGBB_URI, data_view_name:"{data_view_name}"}})
    OPTIONAL MATCH (child_item_kgbb {{URI:child_item.KGBB_URI}})-[child_item_topics:HAS_TOPIC_ELEMENT]->()
    OPTIONAL MATCH (child_item_kgbb {{URI:child_item.KGBB_URI}})-[child_item_assertions:HAS_ASSERTION_ELEMENT]->()
    OPTIONAL MATCH (child_item_kgbb {{URI:child_item.KGBB_URI}})-[child_item_granularity_trees:HAS_GRANULARITY_TREE_ELEMENT]->()
    OPTIONAL MATCH (child_item_obj {{URI:child_item.object_URI}}) WHERE "{version_doi}" IN child_item_obj.versioned_doi
    OPTIONAL MATCH (child_item_input_info:InputInfoKGBBElement_IND {{KGBB_URI:child_item.KGBB_URI}})
    OPTIONAL MATCH (child_item_input_node {{input_info_URI:child_item_input_info.URI}}) WHERE ( (child_item.URI IN child_item_input_node.topic_URI) OR (child_item.URI IN child_item_input_node.assertion_URI) ) AND "{version_doi}" IN child_item_input_node.versioned_doi

    WITH [entry, entry_rep, entry_obj, entry_input_info, entry_input_node, PROPERTIES(entry_topics), PROPERTIES(entry_assertions), PROPERTIES(entry_granularity_trees)] AS entry_info, [parent_item.URI, child_item, child_item_rep, child_item_obj, child_item_input_info, child_item_input_node, PROPERTIES(child_item_topics), PROPERTIES(child_item_assertions), PROPERTIES(child_item_granularity_trees)] AS child_info, current_version AS latest_version, version AS version

    RETURN DISTINCT entry_info, child_info, latest_version, version'''.format(version_doi=version_doi, entry_uri=entry_uri, data_view_name=data_view_name)
    results = connection.query(get_entry_dict_information_query_string, db='neo4j')

    print("---------------------------------------RESULT-------------------------------------------------")
    print(results)
    version = None
    if results[0].get('latest_version') != None:
        version = results[0].get('latest_version')
        version['created_on'] = version['created_on'].isoformat()

    elif results[0].get('version') != None:
        version = results[0].get('version')
        version['created_on'] = version['created_on'].isoformat()


    entry_node = results[0].get('entry_info')[0]
    entry_node['created_on'] = entry_node['created_on'].isoformat()
    entry_node['last_updated_on'] = entry_node['last_updated_on'].isoformat()

    entry_object = results[0].get('entry_info')[2]
    entry_object['created_on'] = entry_object['created_on'].isoformat()
    entry_object['last_updated_on'] = entry_object['last_updated_on'].isoformat()

    init_entry_input_info = []
    try:
        for i in range (0, len(results)):
            init_entry_input_info.append(results[i].get('entry_info')[3])
    except:
        pass
    entry_input_info = getUniqueList(init_entry_input_info)
    print("---------------------------------------------------------------")
    print("----------------- ENTRY INPUT INFO QUERY RESULT ---------------")
    print(entry_input_info)
    print(len(entry_input_info))

    init_entry_input_nodes = []
    try:
        for i in range (0, len(results)):
            init_entry_input_nodes.append(results[i].get('entry_info')[4])
    except:
        pass
    entry_input_nodes = getUniqueList(init_entry_input_nodes)
    print("---------------------------------------------------------------")
    print("---------------- ENTRY INPUT NODES QUERY RESULT ---------------")
    print(entry_input_nodes)
    print(len(entry_input_nodes))

    init_entry_topics = []
    try:
        for i in range (0, len(results)):
            init_entry_topics.append(results[i].get('entry_info')[5])
    except:
        pass
    entry_topics = getUniqueList(init_entry_topics)
    print("---------------------------------------------------------------")
    print("----------------- ENTRY TOPICS QUERY RESULT --------------------")
    print(entry_topics)
    print(len(entry_topics))

    init_entry_assertions = []
    try:
        for i in range (0, len(results)):
            init_entry_assertions.append(results[i].get('entry_info')[6])
    except:
        pass
    entry_assertions = getUniqueList(init_entry_assertions)
    print("---------------------------------------------------------------")
    print("----------------- ENTRY ASSERTIONS QUERY RESULT ---------------")
    print(entry_assertions)
    print(len(entry_assertions))

    init_entry_granularity_trees = []
    try:
        for i in range (0, len(results)):
            init_entry_granularity_trees.append(results[i].get('entry_info')[7])
    except:
        pass
    entry_granularity_trees = getUniqueList(init_entry_granularity_trees)
    print("---------------------------------------------------------------")
    print("----------- ENTRY GRANULARITY TREES QUERY RESULT --------------")
    print(entry_granularity_trees)
    print(len(entry_granularity_trees))

    entry_dict = []
    # preparing the entry_dict_element for the entry_dict
    entry_dict_element = {'id': entry_uri, 'version':True, 'version_node': version, 'component':results[0].get('entry_info')[1].get('component'), 'node':entry_node, 'parent':'''#''', 'node_type': results[0].get('entry_info')[0].get('node_type'), 'text': results[0].get('entry_info')[2].get('name'), 'icon': url_for('static', filename='Entry_ICON_small.png'), 'object':entry_object, 'html':results[0].get('entry_info')[1].get('html'), 'topics':entry_topics, 'assertions':entry_assertions, 'granularity_trees':entry_granularity_trees, 'state': {'opened': True, 'selected': True}, 'li_attr':{}, 'a_attr':{}}

    # extract various component links from the entry rep_node. They are "stored" in the rep_node by consecutively numbered integer keys and the key under which they must be added to the entry_dict_element is the value of the "name" key.
    entry_rep_node = results[0].get('entry_info')[1]
    search_key = "link_$$$_"
    link_dict = dict(filter(lambda item: search_key in item[0], entry_rep_node.items()))
    for link_key in link_dict:
        component_link_string = entry_rep_node.get(link_key)
        component_link = ast.literal_eval(component_link_string)
        print("------------------------------------------------")
        print("------------------------------------------------")
        print("------------ COMPONENT LINK DICT ---------------")
        print("------------------------------------------------")
        print("------------------------------------------------")
        print(component_link)
        key_name = component_link.get('name')
        print("------------------------------------------------")
        print("------------------------------------------------")
        print("------------ KEY NAME --------------------------")
        print("------------------------------------------------")
        print("------------------------------------------------")
        print(key_name)
        print(type(key_name))
        print(type(component_link))
        entry_dict_element[key_name] = component_link
        # delete this key-value from the entry_rep_node
        entry_rep_node.pop(link_key)
    # add the entry_rep_node to the entry_dict_element under the key 'rep_node'
    entry_dict_element['rep_node'] = entry_rep_node

    # gathering input information by input type - if information available, the following will be added: 'input_name': {'input_control': input_info_node, 'input_nodes': [list of input nodes that belong to the input control]}
    try:
        for input in entry_input_info:
            input_name = input.get('input_name')
            input_uri = input.get('URI')
            input_dict = {'input_control': input, 'input_nodes':[]}
            try:
                for node in entry_input_nodes:
                    if node.get('input_info_URI') == input_uri:
                        node['created_on'] = node['created_on'].isoformat()
                        node['last_updated_on'] = node['last_updated_on'].isoformat()
                        input_dict.get('input_nodes').append(node)
                entry_dict_element[input_name] = input_dict
            except:
                pass
    except:
        pass
    entry_dict.append(entry_dict_element)
    print("---------------------------------------------------------------")
    print("-------------------- ENTRY DICT ITEM --------------------------")
    print(entry_dict)
    print(len(entry_dict))






    # clearing the child_info results to unique results
    init_child_info = []
    try:
        for i in range (0, len(results)):
            init_child_info.append(results[i].get('child_info'))
    except:
        pass
    child_info = getUniqueList(init_child_info)
    print("---------------------------------------------------------------")
    print("-------------- UNIQUE CHILD INFO QUERY RESULT -----------------")
    print(child_info)
    print(len(child_info))


    init_child_input_nodes = []
    try:
        for i in range (0, len(child_info)):
            init_child_input_nodes.append(child_info[i][5])
    except:
        pass
    child_input_nodes = getUniqueList(init_child_input_nodes)
    print("---------------------------------------------------------------")
    print("---------------- CHILD INPUT NODES QUERY RESULT ---------------")
    print(child_input_nodes)
    print(len(child_input_nodes))

    init_child_input_infos = []
    try:
        for i in range (0, len(child_info)):
            init_child_input_infos.append(child_info[i][4])
    except:
        pass
    child_input_infos = getUniqueList(init_child_input_infos)
    print("---------------------------------------------------------------")
    print("---------------- CHILD INPUT INFOS QUERY RESULT ---------------")
    print(child_input_infos)
    print(len(child_input_infos))




    # appending the entry_dict with child items
    for child_item in child_info:
        child_node = child_item[1]
        child_node['created_on'] = child_node['created_on'].isoformat()
        child_node['last_updated_on'] = child_node['last_updated_on'].isoformat()
        child_item_uri = child_node.get('URI')
        child_object = child_item[3]
        child_object['created_on'] = child_object['created_on'].isoformat()
        child_object['last_updated_on'] = child_object['last_updated_on'].isoformat()

        init_child_item_topics = []
        try:
            for i in range (0, len(child_info)):
                if child_info[i][1].get('URI') == child_item_uri:
                    if child_item[1].get('KGBB_URI') == child_info[i][6].get('KGBB_URI'):
                        init_child_item_topics.append(child_info[i][6])
        except:
            pass
        child_item_topics = getUniqueList(init_child_item_topics)
        print("---------------------------------------------------------------")
        print("----------------- CHILD ITEM TOPICS QUERY RESULT ---------------")
        print(child_item_topics)
        print(len(child_item_topics))

        init_child_item_assertions = []
        try:
            for i in range (0, len(child_info)):
                if child_info[i][1].get('URI') == child_item_uri:
                    if child_item[1].get('KGBB_URI') == child_info[i][7].get('KGBB_URI'):
                        init_child_item_assertions.append(child_info[i][7])
        except:
            pass
        child_item_assertions = getUniqueList(init_child_item_assertions)
        print("---------------------------------------------------------------")
        print("------------ CHILD ITEM ASSERTIONS QUERY RESULT ---------------")
        print(child_item_assertions)
        print(len(child_item_assertions))

        init_child_item_granularity_trees = []
        try:
            for i in range (0, len(child_info)):
                if child_info[i][1].get('URI') == child_item_uri:
                    if child_item[1].get('KGBB_URI') == child_info[i][8].get('KGBB_URI'):
                        init_child_item_granularity_trees.append(child_info[i][8])
        except:
            pass
        child_item_granularity_trees = getUniqueList(init_child_item_granularity_trees)
        print("---------------------------------------------------------------")
        print("---------- CHILD ITEM GRANULARITY TREES QUERY RESULT ----------")
        print(child_item_granularity_trees)
        print(len(child_item_granularity_trees))

        if child_item[1].get('node_type') == "topic":
            icon = url_for('static', filename='Topic_ICON_small.png')
        elif child_item[1].get('node_type') == "assertion":
            icon = url_for('static', filename='Assertion_ICON_small.png')
        elif child_item[1].get('node_type') == "granularity_tree":
            icon = url_for('static', filename='GranularityTree_ICON_small.png')


        # starting the NaviJS with the entry node
        child_dict = {'id': child_node.get('URI'), 'component':child_item[2].get('component'),'node':child_node, 'parent':child_item[0], 'node_type': child_item[1].get('node_type'), 'icon': icon, 'object':child_object, 'html':child_item[2].get('html'), 'topics':child_item_topics, 'assertions':child_item_assertions, 'granularity_trees':child_item_granularity_trees, 'state': {'opened': False, 'selected': False}, 'li_attr':{}, 'a_attr':{}}

        # extract various component links from the child_item rep_node. They are "stored" in the rep_node by consecutively numbered integer keys and the key under which they must be added to the child_dict dictionary is the value of the "name" key.
        child_rep_node = child_item[2]
        search_key = "link_$$$_"
        child_link_dict = dict(filter(lambda item: search_key in item[0], child_rep_node.items()))
        for child_link_key in child_link_dict:
            component_link_string = child_rep_node.get(child_link_key)
            component_link = ast.literal_eval(component_link_string)
            key_name = component_link.get('name')
            child_dict[key_name] = component_link
            # delete this key-value from the child_rep_node
            child_rep_node.pop(child_link_key)
        # add the child_rep_node to the child_dict under the key 'rep_node'
        child_dict['rep_node'] = child_rep_node

        # gathering input information by input type - if information available, the following will be added: 'input_name': {'input_control': input_info_node, 'input_nodes': [list of input nodes that belong to the input control]}
        if child_item[1].get('node_type') == 'assertion':
            child_dict['text'] = child_node.get('assertion_label')

        elif child_item[1].get('node_type') == 'topic':
            child_dict['text'] = child_node.get('topic_label')

        elif child_item[1].get('node_type') == 'granularity_tree':
            child_dict['text'] = child_node.get('granularity_tree_label')


        entry_dict.append(child_dict)

    # check for duplicates
    entry_dict = getUniqueList(entry_dict)


    # check for input_info and input_nodes
    for item in entry_dict:
        init_child_item_input_info = []
        try:
            for i in range (0, len(child_input_infos)):
                if item.get('node').get('KGBB_URI') == child_input_infos[i].get('KGBB_URI'):
                        init_child_item_input_info.append(child_input_infos[i])
        except:
            pass
        child_item_input_info = getUniqueList(init_child_item_input_info)
        print("---------------------------------------------------------------")
        print("----------------- CHILD ITEM INPUT INFO QUERY RESULT ---------------")
        print(child_item_input_info)
        print(len(child_item_input_info))

        try:
            for input in child_item_input_info:
                input_name = input.get('input_name')
                input_uri = input.get('URI')
                input_dict = {'input_control': input, 'input_nodes':[]}

                try:
                    for node in child_input_nodes:
                        if node.get('input_info_URI') == input_uri and node.get('user_input') == item.get('node').get('URI'):
                            node['created_on'] = node['created_on'].isoformat()
                            node['last_updated_on'] = node['last_updated_on'].isoformat()
                            input_dict.get('input_nodes').append(node)
                    item[input_name] = input_dict
                except:
                    pass
        except:
            pass


    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print("-------------------- FINAL ENTRY DICT ITEM --------------------")
    print(entry_dict)
    print(len(entry_dict))
    return entry_dict












# gather list of ontology terms from graph
# OUTPUT: a list of ontology class nodes
def getOntoClassList():
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # return entry node and all topic nodes that are directly displayed by this entry
    get_ontology_class_list_information_query_string = '''
    MATCH (ontology_class:ClassExpression {{ontology_class:"true"}})
    RETURN ontology_class'''.format()
    results = connection.query(get_ontology_class_list_information_query_string, db='neo4j')

    print("------------- ONTOLOGY CLASS SEARCH RESULT --------------------")
    print(results)
    print(len(results))

    ontology_class_list = []
    for i in range (0, len(results)):
        ontology_class_list.append(results[i].get('ontology_class'))

    ontology_class_list = getUniqueList(ontology_class_list)
    print("---------------------------------------------------------------")
    print("----------------- ONTOLOGY CLASS LIST -------------------------")
    print(ontology_class_list)
    print(len(ontology_class_list))

    return ontology_class_list




# gather list of assertion classes from graph
# OUTPUT: a list of assertion class nodes
def getAssertionClassList():
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # return entry node and all topic nodes that are directly displayed by this entry
    get_assertion_class_list_information_query_string = '''
    MATCH (assertion_class:orkg_Assertion)
    RETURN assertion_class'''.format()
    results = connection.query(get_assertion_class_list_information_query_string, db='neo4j')

    print("------------- ASSERTION CLASS SEARCH RESULT -------------------")
    print(results)
    print(len(results))

    assertion_class_list = []
    for i in range (0, len(results)):
        assertion_class_list.append(results[i].get('assertion_class'))

    assertion_class_list = getUniqueList(assertion_class_list)
    print("---------------------------------------------------------------")
    print("----------------- ASSERTION CLASS LIST ------------------------")
    print(assertion_class_list)
    print(len(assertion_class_list))

    return assertion_class_list




# gather list of topic classes from graph
# OUTPUT: a list of topic class nodes
def getTopicClassList():
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # return entry node and all topic nodes that are directly displayed by this entry
    get_topic_class_list_information_query_string = '''
    MATCH (topic_class:orkg_Topic)
    RETURN topic_class'''.format()
    results = connection.query(get_topic_class_list_information_query_string, db='neo4j')

    print("----------------- TOPIC CLASS SEARCH RESULT --------------------")
    print(results)
    print(len(results))

    topic_class_list = []
    for i in range (0, len(results)):
        topic_class_list.append(results[i].get('topic_class'))

    topic_class_list = getUniqueList(topic_class_list)
    print("---------------------------------------------------------------")
    print("---------------------- TOPIC CLASS LIST ------------------------")
    print(topic_class_list)
    print(len(topic_class_list))

    return topic_class_list




# gather list of entry classes from graph
# OUTPUT: a list of entry class nodes
def getEntryClassList():
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # return entry node and all topic nodes that are directly displayed by this entry
    get_entry_class_list_information_query_string = '''
    MATCH (entry_class:orkg_Entry)
    RETURN entry_class'''.format()
    results = connection.query(get_entry_class_list_information_query_string, db='neo4j')

    print("----------------- ENTRY CLASS SEARCH RESULT -------------------")
    print(results)
    print(len(results))

    entry_class_list = []
    for i in range (0, len(results)):
        entry_class_list.append(results[i].get('entry_class'))

    entry_class_list = getUniqueList(entry_class_list)
    print("---------------------------------------------------------------")
    print("---------------------- ENTRY CLASS LIST -----------------------")
    print(entry_class_list)
    print(len(entry_class_list))

    return entry_class_list









# gather list of instances of a specific class from graph
# INPUT: URI of class
# OUTPUT: a list of instances of the input class
def getInstanceList(type_uri):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

    # return entry node and all topic nodes that are directly displayed by this entry
    get_instance_list_information_query_string = '''
    MATCH (instance:NamedIndividual {{type:"{type_uri}", current_version:"true"}})
    RETURN instance'''.format(type_uri=type_uri)
    results = connection.query(get_instance_list_information_query_string, db='neo4j')

    print("----------------- INSTANCES SEARCH RESULT ---------------------")
    print(results)
    print(len(results))

    instances_list = []
    for i in range (0, len(results)):
        instances_list.append(results[i].get('instance'))

    instances_list = getUniqueList(instances_list)
    print("---------------------------------------------------------------")
    print("---------------------- INSTANCES LIST -------------------------")
    print(instances_list)
    print(len(instances_list))

    return instances_list








# gather subgraph of topic from graph
# INPUT: URI of topic
# OUTPUT: a list of dictionaries of all topics, assertions, and granularity trees linked to a particular topic node via :CONTAINS relation chains, following syntax:  [{id:data_item_uri, component:string, node:{data_item_node}, parent:parent_uri, node_type:topic/assertion/granularity_tree, text:name, icon:image, object:{object_node}, rep_node:{representation_node}, html:html, topics: [{HAS_topic_ELEMENT representation info}], assertions: [{HAS_ASSERTION_ELEMENT representation info}], granularity_trees: [{HAS_GRANULARITY_TREE_ELEMENT representation info}], (various component links by their own keys, extracted from the rep_node), state:{required for navi tree}, "input_name//from input_info":{'input_control':{input control}, 'input_nodes':[{input_node}, etc.]}}, etc.]
def getTopicRepresentation(topic_uri, data_view_name):
    connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")
    print("------------------------- TOPIC URI INPUT ----------------------------------------")
    print(topic_uri)

    # return topic node and all child nodes that are directly displayed by this topic
    get_topic_dict_information_query_string = '''
    MATCH (topic {{URI:"{topic_uri}"}})
    MATCH (entry {{URI:topic.entry_URI}})
    OPTIONAL MATCH (topic_parent  {{current_version:"true"}})-[:CONTAINS]->(topic)
    MATCH (topic_rep:RepresentationKGBBElement_IND {{KGBB_URI:topic.KGBB_URI, data_view_name:"{data_view_name}"}})
    OPTIONAL MATCH (topic_kgbb {{URI:topic.KGBB_URI}})-[topic_topics:HAS_TOPIC_ELEMENT]->()
    OPTIONAL MATCH (topic_kgbb {{URI:topic.KGBB_URI}})-[topic_assertions:HAS_ASSERTION_ELEMENT]->()
    OPTIONAL MATCH (topic_kgbb {{URI:topic.KGBB_URI}})-[topic_granularity_trees:HAS_GRANULARITY_TREE_ELEMENT]->()
    OPTIONAL MATCH (topic_obj {{URI:topic.object_URI, current_version:"true"}})
    OPTIONAL MATCH (topic_input_info:InputInfoKGBBElement_IND {{KGBB_URI:topic.KGBB_URI}})
    OPTIONAL MATCH (topic_input_node {{topic_URI:"{topic_uri}", current_version:"true", input_info_URI:topic_input_info.URI}})

    OPTIONAL MATCH (topic)-[:CONTAINS*1..2]-> (child_item {{current_version:"true"}})
    OPTIONAL MATCH (child_item)<-[:CONTAINS]-(parent_item {{current_version:"true"}})
    OPTIONAL MATCH (child_item_rep:RepresentationKGBBElement_IND {{KGBB_URI:child_item.KGBB_URI, data_view_name:"{data_view_name}"}})
    OPTIONAL MATCH (child_item_kgbb {{URI:child_item.KGBB_URI}})-[child_item_topics:HAS_TOPIC_ELEMENT]->()
    OPTIONAL MATCH (child_item_kgbb {{URI:child_item.KGBB_URI}})-[child_item_assertions:HAS_ASSERTION_ELEMENT]->()
    OPTIONAL MATCH (child_item_kgbb {{URI:child_item.KGBB_URI}})-[child_item_granularity_trees:HAS_GRANULARITY_TREE_ELEMENT]->()
    OPTIONAL MATCH (child_item_obj {{URI:child_item.object_URI, current_version:"true"}})
    OPTIONAL MATCH (child_item_input_info:InputInfoKGBBElement_IND {{KGBB_URI:child_item.KGBB_URI}})
    OPTIONAL MATCH (child_item_input_node {{current_version:"true", input_info_URI:child_item_input_info.URI}}) WHERE (child_item.URI IN child_item_input_node.topic_URI) OR (child_item.URI IN child_item_input_node.assertion_URI)

    WITH [topic, topic_rep, topic_obj, topic_input_info, topic_input_node, PROPERTIES(topic_topics), PROPERTIES(topic_assertions), PROPERTIES(topic_granularity_trees)] AS topic_info, [parent_item.URI, child_item, child_item_rep, child_item_obj, child_item_input_info, child_item_input_node, PROPERTIES(child_item_topics), PROPERTIES(child_item_assertions), PROPERTIES(child_item_granularity_trees)] AS child_info, topic_parent.URI AS parent_URI, entry.publication_title AS entry_title

    RETURN DISTINCT topic_info, child_info, parent_URI, entry_title'''.format(topic_uri=topic_uri, data_view_name=data_view_name)
    results = connection.query(get_topic_dict_information_query_string, db='neo4j')
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("+++++++++++++++++++++ INITIAL QUERY RESULT +++++++++++++++++++++++++++")
    print(results)

    topic_parent_URI = results[0].get('parent_URI')
    entry_title = results[0].get('entry_title')
    topic_node = results[0].get('topic_info')[0]
    topic_node['created_on'] = topic_node['created_on'].isoformat()
    topic_node['last_updated_on'] = topic_node['last_updated_on'].isoformat()

    topic_object = results[0].get('topic_info')[2]
    topic_object['created_on'] = topic_object['created_on'].isoformat()
    topic_object['last_updated_on'] = topic_object['last_updated_on'].isoformat()

    init_topic_input_info = []
    try:
        for i in range (0, len(results)):
            init_topic_input_info.append(results[i].get('topic_info')[3])
    except:
        pass
    topic_input_info = getUniqueList(init_topic_input_info)
    print("---------------------------------------------------------------")
    print("----------------- TOPIC INPUT INFO QUERY RESULT ----------------")
    print(topic_input_info)
    print(len(topic_input_info))

    init_topic_input_nodes = []
    try:
        for i in range (0, len(results)):
            init_topic_input_nodes.append(results[i].get('topic_info')[4])
    except:
        pass
    topic_input_nodes = getUniqueList(init_topic_input_nodes)
    print("---------------------------------------------------------------")
    print("----------------- TOPIC INPUT NODES QUERY RESULT ---------------")
    print(topic_input_nodes)
    print(len(topic_input_nodes))

    init_topic_topics = []
    try:
        for i in range (0, len(results)):
            init_topic_topics.append(results[i].get('topic_info')[5])
    except:
        pass
    topic_topics = getUniqueList(init_topic_topics)
    print("---------------------------------------------------------------")
    print("----------------- TOPIC TOPICS QUERY RESULT ---------------------")
    print(topic_topics)
    print(len(topic_topics))

    init_topic_assertions = []
    try:
        for i in range (0, len(results)):
            init_topic_assertions.append(results[i].get('topic_info')[6])
    except:
        pass
    topic_assertions = getUniqueList(init_topic_assertions)
    print("---------------------------------------------------------------")
    print("----------------- TOPIC ASSERTIONS QUERY RESULT ----------------")
    print(topic_assertions)
    print(len(topic_assertions))

    init_topic_granularity_trees = []
    try:
        for i in range (0, len(results)):
            init_topic_granularity_trees.append(results[i].get('topic_info')[7])
    except:
        pass
    topic_granularity_trees = getUniqueList(init_topic_granularity_trees)
    print("---------------------------------------------------------------")
    print("------------ TOPIC GRANULARITY TREES QUERY RESULT --------------")
    print(topic_granularity_trees)
    print(len(topic_granularity_trees))


    topic_dict = []
    # preparing the topic_dict_element for the topic_dict
    topic_dict_element = {'id': topic_uri, 'component':results[0].get('topic_info')[1].get('component'), 'entry_title':entry_title, 'node':topic_node, 'parent':topic_parent_URI, 'node_type': results[0].get('topic_info')[0].get('node_type'), 'text': results[0].get('topic_info')[2].get('name'), 'icon': url_for('static', filename='Topic_ICON_small.png'), 'object':topic_object, 'html':results[0].get('topic_info')[1].get('html'), 'topics':topic_topics, 'assertions':topic_assertions, 'granularity_trees':topic_granularity_trees, 'state': {'opened': True, 'selected': True}, 'li_attr':{}, 'a_attr':{}}

    # extract various component links from the topic rep_node. They are "stored" in the rep_node by consecutively numbered integer keys and the key under which they must be added to the topic_dict_element is the value of the "name" key.
    topic_rep_node = results[0].get('topic_info')[1]
    search_key = "link_$$$_"
    link_dict = dict(filter(lambda item: search_key in item[0], topic_rep_node.items()))
    for link_key in link_dict:
        component_link_string = topic_rep_node.get(link_key)
        component_link = ast.literal_eval(component_link_string)
        print("------------------------------------------------")
        print("------------------------------------------------")
        print("------------ COMPONENT LINK DICT ---------------")
        print("------------------------------------------------")
        print("------------------------------------------------")
        print(component_link)
        key_name = component_link.get('name')
        print("------------------------------------------------")
        print("------------------------------------------------")
        print("------------ KEY NAME --------------------------")
        print("------------------------------------------------")
        print("------------------------------------------------")
        print(key_name)
        print(type(key_name))
        print(type(component_link))
        topic_dict_element[key_name] = component_link
        # delete this key-value from the topic_rep_node
        topic_rep_node.pop(link_key)
    # add the topic_rep_node to the topic_dict_element under the key 'rep_node'
    topic_dict_element['rep_node'] = topic_rep_node

    # gathering input information by input type - if information available, the following will be added: 'input_name': {'input_control': input_info_node, 'input_nodes': [list of input nodes that belong to the input control]}
    try:
        for input in topic_input_info:
            input_name = input.get('input_name')
            input_uri = input.get('URI')
            input_dict = {'input_control': input, 'input_nodes':[]}
            try:
                for node in topic_input_nodes:
                    if node.get('input_info_URI') == input_uri:
                        node['created_on'] = node['created_on'].isoformat()
                        node['last_updated_on'] = node['last_updated_on'].isoformat()
                        input_dict.get('input_nodes').append(node)
                topic_dict_element[input_name] = input_dict
            except:
                pass
    except:
        pass
    topic_dict.append(topic_dict_element)
    print("---------------------------------------------------------------")
    print("-------------------- TOPIC DICT ITEM ---------------------------")
    print(topic_dict)
    print(len(topic_dict))




    # clearing the child_info results to unique results
    init_child_info = []
    try:
        for i in range (0, len(results)):
            init_child_info.append(results[i].get('child_info'))
    except:
        pass
    child_info = getUniqueList(init_child_info)
    print("---------------------------------------------------------------")
    print("-------------- UNIQUE CHILD INFO QUERY RESULT -----------------")
    print(child_info)
    print(len(child_info))


    init_child_input_nodes = []
    try:
        for i in range (0, len(child_info)):
            init_child_input_nodes.append(child_info[i][5])
    except:
        pass
    child_input_nodes = getUniqueList(init_child_input_nodes)
    print("---------------------------------------------------------------")
    print("---------------- CHILD INPUT NODES QUERY RESULT ---------------")
    print(child_input_nodes)
    print(len(child_input_nodes))

    init_child_input_infos = []
    try:
        for i in range (0, len(child_info)):
            init_child_input_infos.append(child_info[i][4])
    except:
        pass
    child_input_infos = getUniqueList(init_child_input_infos)
    print("---------------------------------------------------------------")
    print("---------------- CHILD INPUT INFOS QUERY RESULT ---------------")
    print(child_input_infos)
    print(len(child_input_infos))




    # appending the topic_dict with child items
    for child_item in child_info:
        if child_info[0][0] != None:
            child_node = child_item[1]
            child_node['created_on'] = child_node['created_on'].isoformat()
            child_node['last_updated_on'] = child_node['last_updated_on'].isoformat()
            child_item_uri = child_node.get('URI')
            child_object = child_item[3]
            child_object['created_on'] = child_object['created_on'].isoformat()
            child_object['last_updated_on'] = child_object['last_updated_on'].isoformat()

            init_child_item_topics = []
            try:
                for i in range (0, len(child_info)):
                    if child_info[i][1].get('URI') == child_item_uri:
                        if child_item[1].get('KGBB_URI') == child_info[i][6].get('KGBB_URI'):
                            init_child_item_topics.append(child_info[i][6])
            except:
                pass
            child_item_topics = getUniqueList(init_child_item_topics)
            print("---------------------------------------------------------------")
            print("----------------- CHILD ITEM TOPICS QUERY RESULT ---------------")
            print(child_item_topics)
            print(len(child_item_topics))

            init_child_item_assertions = []
            try:
                for i in range (0, len(child_info)):
                    if child_info[i][1].get('URI') == child_item_uri:
                        if child_item[1].get('KGBB_URI') == child_info[i][7].get('KGBB_URI'):
                            init_child_item_assertions.append(child_info[i][7])
            except:
                pass
            child_item_assertions = getUniqueList(init_child_item_assertions)
            print("---------------------------------------------------------------")
            print("------------ CHILD ITEM ASSERTIONS QUERY RESULT ---------------")
            print(child_item_assertions)
            print(len(child_item_assertions))

            init_child_item_granularity_trees = []
            try:
                for i in range (0, len(child_info)):
                    if child_info[i][1].get('URI') == child_item_uri:
                        if child_item[1].get('KGBB_URI') == child_info[i][8].get('KGBB_URI'):
                            init_child_item_granularity_trees.append(child_info[i][8])
            except:
                pass
            child_item_granularity_trees = getUniqueList(init_child_item_granularity_trees)
            print("---------------------------------------------------------------")
            print("---------- CHILD ITEM GRANULARITY TREES QUERY RESULT ----------")
            print(child_item_granularity_trees)
            print(len(child_item_granularity_trees))

            if child_item[1].get('node_type') == "topic":
                icon = url_for('static', filename='Topic_ICON_small.png')
            elif child_item[1].get('node_type') == "assertion":
                icon = url_for('static', filename='Assertion_ICON_small.png')
            elif child_item[1].get('node_type') == "granularity_tree":
                icon = url_for('static', filename='GranularityTree_ICON_small.png')


            # starting the NaviJS with the topic node
            child_dict = {'id': child_node.get('URI'), 'component':child_item[2].get('component'),'node':child_node, 'parent':child_item[0], 'node_type': child_item[1].get('node_type'), 'icon': icon, 'object':child_object, 'html':child_item[2].get('html'), 'topics':child_item_topics, 'assertions':child_item_assertions, 'granularity_trees':child_item_granularity_trees, 'state': {'opened': False, 'selected': False}, 'li_attr':{}, 'a_attr':{}}

            # extract various component links from the child_item rep_node. They are "stored" in the rep_node by consecutively numbered integer keys and the key under which they must be added to the child_dict dictionary is the value of the "name" key.
            child_rep_node = child_item[2]
            search_key = "link_$$$_"
            child_link_dict = dict(filter(lambda item: search_key in item[0], child_rep_node.items()))
            for child_link_key in child_link_dict:
                component_link_string = child_rep_node.get(child_link_key)
                component_link = ast.literal_eval(component_link_string)
                key_name = component_link.get('name')
                child_dict[key_name] = component_link
                # delete this key-value from the child_rep_node
                child_rep_node.pop(child_link_key)
            # add the child_rep_node to the child_dict under the key 'rep_node'
            child_dict['rep_node'] = child_rep_node

            # gathering input information by input type - if information available, the following will be added: 'input_name': {'input_control': input_info_node, 'input_nodes': [list of input nodes that belong to the input control]}
            if child_item[1].get('node_type') == 'assertion':
                child_dict['text'] = child_node.get('assertion_label')

            elif child_item[1].get('node_type') == 'topic':
                child_dict['text'] = child_node.get('topic_label')

            elif child_item[1].get('node_type') == 'granularity_tree':
                child_dict['text'] = child_node.get('name')


            topic_dict.append(child_dict)

    # check for duplicates
    topic_dict = getUniqueList(topic_dict)


    # check for input_info and input_nodes
    for item in topic_dict:
        init_child_item_input_info = []
        try:
            for i in range (0, len(child_input_infos)):
                if item.get('node').get('KGBB_URI') == child_input_infos[i].get('KGBB_URI'):
                        init_child_item_input_info.append(child_input_infos[i])
        except:
            pass
        child_item_input_info = getUniqueList(init_child_item_input_info)
        print("---------------------------------------------------------------")
        print("----------------- CHILD ITEM INPUT INFO QUERY RESULT ---------------")
        print(child_item_input_info)
        print(len(child_item_input_info))

        try:
            for input in child_item_input_info:
                input_name = input.get('input_name')
                input_uri = input.get('URI')
                input_dict = {'input_control': input, 'input_nodes':[]}

                try:
                    for node in child_input_nodes:
                        if node.get('input_info_URI') == input_uri and node.get('user_input') == item.get('node').get('URI'):
                            node['created_on'] = node['created_on'].isoformat()
                            node['last_updated_on'] = node['last_updated_on'].isoformat()
                            input_dict.get('input_nodes').append(node)
                    item[input_name] = input_dict
                except:
                    pass
        except:
            pass


    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print("--------------------- FINAL TOPIC DICT ITEM --------------------")
    print(topic_dict)
    print(len(topic_dict))
    return topic_dict

























    # return entry node and all topic nodes that are directly displayed by this entry
    get_topic_node_list_information_query_string = '''
    MATCH (nodes:orkg_Topic_IND {{topic_URI:"{topic_uri}", current_version:"true"}})
    RETURN nodes'''.format(topic_uri=topic_uri)
    results = connection.query(get_topic_node_list_information_query_string, db='neo4j')

    print("----------------- TOPIC NODES SEARCH RESULT ---------------------")
    print(results)
    print(len(results))

    nodes_list = []
    for i in range (0, len(results)):
        nodes_list.append(results[i].get('nodes'))

    nodes_list = getUniqueList(nodes_list)
    print("---------------------------------------------------------------")
    print("-------------------------- NODES LIST -------------------------")
    print(nodes_list)
    print(len(nodes_list))

    return nodes_list
