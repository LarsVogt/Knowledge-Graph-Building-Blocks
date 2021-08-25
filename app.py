# .\.venvs\lpthw\Scripts\activate
# $env:PYTHONPATH = "$env:PYTHONPATH;."

# to run FLASK in development mode use in Windows shell the cmnd:
# $env:FLASK_ENV = "development"

# Connection info to Neo4j (Version 4.2.4 with APOC Plugin) UseCaseKGBB_Database pw:test
# username: python    password: useCaseKGBB   uri: bolt://localhost:7687
# access app via localhost:5000

from flask import Flask, jsonify, session, redirect, url_for, escape, request, flash, render_template
from neo4j import GraphDatabase
from KGBB.connectNeo4j import Neo4jConnection
from KGBB.KGBBFunctions_and_Classes import *
from habanero import cn
import django
import json
import html
import uuid

app = Flask(__name__)
app.secret_key = b'g5__W#U%Jq3gAH%dndL)/Tfzk86'

global connection
connection = Neo4jConnection(uri="bolt://localhost:7687", user="python", pwd="useCaseKGBB")

global entry_uri
entry_uri = None

global entry_dict
entry_dict = None

global topic_data
topic_data = None

global topic_kgbb_uri
topic_kgbb_uri = None

global topic_types_count
topic_types_count = None

global assertion_elements_dict
assertion_elements_dict = None

global assertion_kgbb_uri
assertion_kgbb_uri = None

global entry_name
entry_name = None

global topic_name
topic_name = None

global assertion_name
assertion_name = None

global navi_dict
navi_dict = None

global topics_length
topics_length = None

global entry_node
entry_node = None

global topic_view_tree
topic_view_tree = None

global assertion_view_tree
assertion_view_tree = None

global entry_view_tree
entry_view_tree = None

global naviJSON
naviJSON = None

global data_view_name
data_view_name = "ORKG"


check_empty_query_string = '''MATCH (n) RETURN count(n);'''

check_entry_query_string = '''MATCH (n:orkg_ScholarlyPublicationEntry_IND) RETURN count(n);'''

delete_graph_query_string = '''MATCH (n) DETACH DELETE n;'''

search_add_scholarly_publication_entry_query_string = '''MATCH (n:ScholarlyPublicationEntryKGBB) RETURN n.storage_model_cypher_code'''

view_all_scholarly_publication_entries_query_string = '''MATCH (n:orkg_ScholarlyPublicationEntry_IND)-[:IS_TRANSLATION_OF]-> (m) RETURN n.name, n.URI, n.research_topic_URI, n.created_on, n.created_by, n.last_updated_on, n.publication_title, m.publication_authors, m.publication_year'''


initiation_query_string = '''
    CREATE (bfoMatEnt:bfo_MaterialEntity:ClassExpression:Entity {{name:"bfo: material entity", URI:"http://purl.obolibrary.org/obo/BFO_0000040", description:"A material entity is an independent continuant that has some portion of matter as proper or improper continuant part. (axiom label in BFO2 Reference: [019-002])", ontology_class:"true", category:"ClassExpression"}})

    CREATE (:ero_agent:bfo_MaterialEntity:ClassExpression:Entity {{name:"ero: agent", URI:"http://xmlns.com/foaf/0.1/Agent", description:"Things that do stuff.  Agents are things that do stuff", ontology_class:"true", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(bfoMatEnt)

    CREATE (:ido_InfectiousAgentPopulation:ClassExpression:Entity {{name:"ido: infectious agent population", URI:"http://purl.obolibrary.org/obo/IDO_0000513", ontology_class:"true", category:"ClassExpression"}})

    CREATE (:omit_BasicReproductionNumber:ClassExpression:Entity {{name:"omit: basic reproduction number", URI:"http://purl.obolibrary.org/obo/OMIT_0024604", ontology_class:"true", category:"ClassExpression"}})

    CREATE (:dcterms_Location:ClassExpression:Entity {{name:"dcterms:location", URI:"http://purl.org/dc/terms/Location", description:"A spatial region or named place.", ontology_class:"true", category:"ClassExpression"}})

    CREATE (:orkg_ResearchResult:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg:research result", URI:"http://orkg???????1", description:"An information content entity that is intended to be a truthful statement about something and is the output of some research activity. It is usually acquired by some research method which reliably tends to produce (approximately) truthful statements (cf. iao:data item).", ontology_class:"true", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(informationContentEntity:iao_InformationContentEntity:ClassExpression:Entity {{name:"iao:information content entity", URI:"http://purl.obolibrary.org/obo/IAO_0000030", ontology_class:"true", description:"A generically dependent continuant that is about some thing. An information entity is an entity that represents information about some other entity. For example, a measurement, a clustered data set.", category:"ClassExpression"}})

    CREATE (:orkg_ResearchActivity:obi_Investigation:obi_PlannedProcess:bfo_Process:ClassExpression:Entity {{name:"orkg:research activity", URI:"http://orkg???????5", ontology_class:"true", description:"A planned process that has been planned and executed by some research agent and that has some research result. The process ends if some specific research objective is achieved.", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(obiInv:obi_Investigation:obi_PlannedProcess:bfo_Process:ClassExpression:Entity {{name:"obi:investigation", ontology_class:"true", URI:"http://purl.obolibrary.org/obo/OBI_0000066", description:"a planned process that consists of parts: planning, study design execution, documentation and which produce conclusion(s).", category:"ClassExpression"}})

    CREATE (obiInv)-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(obiPlannedProc:obi_PlannedProcess:bfo_Process:ClassExpression:Entity {{name:"obi:planned process", URI:"http://purl.obolibrary.org/obo/OBI_0000011", ontology_class:"true", description:"A process that realizes a plan which is the concretization of a plan specification.", category:"ClassExpression"}})

    CREATE (obiPlannedProc)-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(bfoProcess:bfo_Process:ClassExpression:Entity {{name:"bfo:process", URI:"http://purl.obolibrary.org/obo/BFO_0000015", description:"p is a process = Def. p is an occurrent that has temporal proper parts and for some time t, p s-depends_on some material entity at t. (axiom label in BFO2 Reference: [083-003]) [ http://purl.obolibrary.org/obo/bfo/axiom/083-003 ] ", ontology_class:"true", category:"ClassExpression"}})

    CREATE (:orkg_ResearchMethod:iao_PlanSpecification:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg:research method", URI:"http://orkg???????4", ontology_class:"true", description:"An information content entity that specifies how to conduct some research activity. It usually has some research objective as its part. It instructs some research agent how to achieve the objectives by taking the actions it specifies.", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(planSpecification:iao_PlanSpecification:iao_InformationContentEntity:ClassExpression:Entity {{name:"iao:plan specification", ontology_class:"true", URI:"http://purl.obolibrary.org/obo/IAO_0000104", description:"A directive information entity with action specifications and objective specifications as parts that, when concretized, is realized in a process in which the bearer tries to achieve the objectives by taking the actions specified.", category:"ClassExpression"}})

    CREATE (:orkg_ResearchObjective:iao_ObjectiveSpecification:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg:research objective", ontology_class:"true", URI:"http://orkg???????3", description:"An information content entity that describes an intended process endpoint for some research activity.", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(objectiveSpecification:iao_ObjectiveSpecification:iao_InformationContentEntity:ClassExpression:Entity {{name:"iao:objective specification", ontology_class:"true", URI:"http://purl.obolibrary.org/obo/IAO_0000005", description:"A directive information entity that describes an intended process endpoint. When part of a plan specification the concretization is realized in a planned process in which the bearer tries to effect the world so that the process endpoint is achieved.", category:"ClassExpression"}})

    CREATE (researchPaper:orkg_ResearchPaper:iao_PublicationAboutAnInvestigation:iao_Document:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg:research paper", URI:"http://orkg???????2", ontology_class:"true", description:"An information content entity that is a scholarly publication, i.e. a document that has been accepted by a publisher (cf. iao:publication) and has content relevant to research.", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoPub:iao_PublicationAboutAnInvestigation:iao_Document:iao_InformationContentEntity:ClassExpression:Entity {{name:"iao: publication about an investigation", ontology_class:"true", URI:"http://purl.obolibrary.org/obo/IAO_0000312", category:"ClassExpression"}})

    CREATE (iaoPub)-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoDoc:iao_Document:iao_InformationContentEntity:ClassExpression:Entity {{name:"iao: document", description:"A collection of information content entities intended to be understood together as a whole.", URI:"http://purl.obolibrary.org/obo/IAO_0000310", ontology_class:"true", category:"ClassExpression"}})

    CREATE (iaoDoc)-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(informationContentEntity)

    CREATE (iaoDocPart:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"iao: document part", description:"A category denoting a rather broad domain or field of interest, of study, application, work, data, or technology. Topics have no clearly defined borders between each other.", ontology_class:"true", URI:"http://purl.obolibrary.org/obo/IAO_0000314", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(informationContentEntity)

    CREATE (topic:edam_Topic:iao_InformationContentEntity:ClassExpression:Entity {{name:"edam: topic", description:"An information content entity that is part of a document.", ontology_class:"true", URI:"http://edamontology.org/topic_0003", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(informationContentEntity)

    CREATE (orkg_researchtopic:orkg_ResearchTopic:edam_Topic:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg: research topic", ontology_class:"true", description:"A research topic is a subject or issue that a researcher is interested in when conducting research.", URI:"http://orkg/researchtopic_1", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(topic)

    CREATE (objectiveSpecification)-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(informationContentEntity)

    CREATE (planSpecification)-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(informationContentEntity)

    CREATE (:omit_BasicReproductionNumber:omit_MeSHTerm:bfo_Quality:ClassExpression:Entity {{name:"omit:basic reproduction number", URI:"http://purl.obolibrary.org/obo/OMIT_0024604", description:"None", ontology_class:"true", category:"ClassExpression"}})

    CREATE (:pato_Weight:pato_PhysicalQuality:pato_Quality:ClassExpression:Entity {{name:"pato:weight", URI:"http://purl.obolibrary.org/obo/PATO_0000128", description:"A physical quality inhering in a bearer that has mass near a gravitational body. [Wikipedia:http://en.wikipedia.org/wiki/Weight]", ontology_class:"true", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(physicalQuality:pato_PhysicalQuality:pato_Quality:ClassExpression:Entity {{name:"pato:physical quality", URI:"http://purl.obolibrary.org/obo/PATO_0001018", ontology_class:"true", description:"A quality of a physical entity that exists through action of continuants at the physical level of organisation in relation to other entities.", category:"ClassExpression"}})

    CREATE (physicalQuality)-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(:bfo_Quality:ClassExpression:Entity {{name:"bfo:quality", URI:"http://purl.obolibrary.org/obo/BFO_0000019", ontology_class:"true", description:"a quality is a specifically dependent continuant that, in contrast to roles and dispositions, does not require any further process in order to be realized. (axiom label in BFO2 Reference: [055-001]).", category:"ClassExpression"}})

    CREATE (:pato_Temperature:pato_PhysicalQuality:pato_Quality:ClassExpression:Entity {{name:"pato:temperature", URI:"http://purl.obolibrary.org/obo/PATO_0000146", ontology_class:"true", description:"A physical quality of the thermal energy of a system.", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(physicalQuality)

    CREATE (:pato_HeatConductivity:pato_PhysicalQuality:pato_Quality:ClassExpression:Entity {{name:"pato:heat conductivity", URI:"http://purl.obolibrary.org/obo/PATO_0001756", ontology_class:"true", description:"A conductivity quality inhering in a bearer by virtue of the bearer's disposition to spontaneous transfer of thermal energy from a region of higher temperature to a region of lower temperature.", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(physicalQuality)

    CREATE (color:pato_Color:pato_PhysicalQuality:pato_Quality:ClassExpression:Entity {{name:"pato:color", URI:"http://purl.obolibrary.org/obo/PATO_0000014", ontology_class:"true", description:"A composite chromatic quality composed of hue, saturation and intensity parts.", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(physicalQuality)

    CREATE (:pato_red:pato_Color:pato_PhysicalQuality:pato_Quality:ClassExpression:Entity {{name:"pato:red", URI:"http://purl.obolibrary.org/obo/PATO_0000322", ontology_class:"true", description:"A color hue with high wavelength of the long-wave end of the visible spectrum, evoked in the human observer by radiant energy with wavelengths of approximately 630 to 750 nanometers. [Dictionary:http://dictionary.reference.com/]", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(color)

    CREATE (:pato_blue:pato_Color:pato_PhysicalQuality:pato_Quality:ClassExpression:Entity {{name:"pato:blue", URI:"http://purl.obolibrary.org/obo/PATO_0000318", ontology_class:"true", description:"A color hue with low wavelength of that portion of the visible spectrum lying between green and indigo, evoked in the human observer by radiant energy with wavelengths of approximately 420 to 490 nanometers. [ Dictionary:http://dictionary.reference.com/]", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(color)

    CREATE (:uo_Kilogram:uo_GramBasedUnit:ClassExpression:Entity {{name:"uo:kilogram", URI:"http://purl.obolibrary.org/obo/UO_0000009", ontology_class:"true", description:"A mass unit which is equal to the mass of the International Prototype Kilogram kept by the BIPM at Svres, France", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(uo_grambased:uo_GramBasedUnit:ClassExpression:Entity {{name:"uo:gram based unit", URI:"http://purl.obolibrary.org/obo/UO_1000021", ontology_class:"true", description:"A gram based mass unit which is based on the mass of the International Prototype Kilogram kept by the BIPM at Svres, France", category:"ClassExpression"}})

    CREATE (:uo_Gram:uo_GramBasedUnit:ClassExpression:Entity {{name:"uo:gram", URI:"http://purl.obolibrary.org/obo/UO_0000021", description:"A mass unit which is equal to one thousandth of a kilogram or 10^[-3] kg.", ontology_class:"true", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(uo_grambased)

    CREATE (:uo_CountUnit:uo_DimensionlessUnit:uo_Unit:ClassExpression:Entity {{name:"uo:count unit", URI:"http://purl.obolibrary.org/obo/UO_0000189", description:"A dimensionless unit which denotes a simple count of things. [MGED:MGED]", ontology_class:"true", category:"ClassExpression"}})

    CREATE (:uo_Percent:uo_Ratio:uo_DimensionlessUnit:uo_Unit:ClassExpression:Entity {{name:"uo:percent", URI:"http://purl.obolibrary.org/obo/UO_0000187", description:"A dimensionless ratio unit which denotes numbers as fractions of 100. [Wikipedia:Wikipedia]", ontology_class:"true", category:"ClassExpression"}})

    CREATE (:uo_Milligram:uo_GramBasedUnit:ClassExpression:Entity {{name:"uo:milligram", URI:"http://purl.obolibrary.org/obo/UO_0000022", ontology_class:"true", description:"A mass unit which is equal to one thousandth of a gram or 10^[-3] g.", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(uo_grambased)

    CREATE (:uo_Nanogram:uo_GramBasedUnit:ClassExpression:Entity {{name:"uo:nanogram", URI:"http://purl.obolibrary.org/obo/UO_0000024", ontology_class:"true", description:"A mass unit which is equal to one thousandth of one millionth of a gram or 10^[-9] g.", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(uo_grambased)

    CREATE (:stato_ConfidenceInterval:ClassExpression:Entity {{name:"stato:confidence interval", URI:"http://purl.obolibrary.org/obo/STATO_0000196", ontology_class:"true", category:"ClassExpression", description:"A confidence interval is a data item which defines an range of values in which a measurement or trial falls corresponding to a given probability."}})

    CREATE (:stato_LowerConfidenceLimit:ClassExpression:Entity {{name:"stato:lower confidence limit", URI:"http://purl.obolibrary.org/obo/STATO_0000315", ontology_class:"true", category:"ClassExpression", description:"Lower confidence limit is a data item which is a lowest value bounding a confidence interval."}})

    CREATE (:stato_UpperConfidenceLimit:ClassExpression:Entity {{name:"stato:upper confidence limit", URI:"http://purl.obolibrary.org/obo/STATO_0000314", ontology_class:"true", category:"ClassExpression", description:"Upper confidence limit is a data item which is a largest value bounding a confidence interval."}})

    CREATE (:stato_ConfidenceLevel:ClassExpression:Entity {{name:"stato:confidence level", URI:"http://purl.obolibrary.org/obo/STATO_0000561", category:"ClassExpression", ontology_class:"true", description:"The frequency (i.e., the proportion) of possible confidence intervals that contain the true value of their corresponding parameter. In other words, if confidence intervals are constructed using a given confidence level in an infinite number of independent experiments, the proportion of those intervals that contain the true value of the parameter will match the confidence level. A probability measure of the reliability of an inferential statistical test that has been applied to sample data and which is provided along with the confidence interval for the output statistic."}})

    CREATE (:uo_Percent:ClassExpression:Entity {{name:"uo:percent", URI:"http://purl.obolibrary.org/obo/UO_0000187", category:"ClassExpression", ontology_class:"true", description:"A dimensionless ratio unit which denotes numbers as fractions of 100."}})

    CREATE (:Value:Literal:ClassExpression:Entity {{name:"orkg: value", description:"A resource that carries a particular numerical literal.", ontology_class:"true", URI:"orkg_value_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(:Literal:ClassExpression:Entity {{name:"orkg: literal", ontology_class:"true", description:"A resource that carries a particular literal.", URI:"orkg_literal_URI", category:"ClassExpression"}})

    CREATE (:MeasurementDatum:Literal:ClassExpression:Entity {{name:"orkg: measurement datum", description:"A measurement datum is an information content entity that is a recording of the output of some measurement process, either produced by some device or some agent.", ontology_class:"true", URI:"orkg_measurement_datum_URI", category:"ClassExpression"}})

    CREATE (obivalueSpec:obi_ValueSpecification:iao_InformationContentEntity:ClassExpression:Entity {{name:"obi: value specification", description:"An information content entity that specifies a value within a classification scheme or on a quantitative scale.", ontology_class:"true", URI:"http://purl.obolibrary.org/obo/OBI_0001933", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(informationContentEntity)

    CREATE (obiscalvalueSpec:obi_ScalarValueSpecification:obi_ValueSpecification:iao_InformationContentEntity:ClassExpression:Entity {{name:"obi: scalar value specification", description:"A value specification that consists of two parts: a numeral and a unit label.", ontology_class:"true", URI:"http://purl.obolibrary.org/obo/OBI_0001931", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(obivalueSpec)

    CREATE (iaoMeasDatum:iao_MeasurementDatum:iao_data_item:iao_InformationContentEntity:ClassExpression:Entity {{name:"iao: measurement datum", description:"A measurement datum is an information content entity that is a recording of the output of a measurement such as produced by a device.", ontology_class:"true", URI:"http://purl.obolibrary.org/obo/IAO_0000109", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(informationContentEntity)

    CREATE (iaoScalMeasDatum:iao_ScalarMeasurementDatum:iao_MeasurementDatum:iao_data_item:iao_InformationContentEntity:ClassExpression:Entity {{name:"iao: scalar measurement datum", description:"A scalar measurement datum is a measurement datum that is composed of two parts, numerals and a unit label.", ontology_class:"true", URI:"http://purl.obolibrary.org/obo/IAO_0000032", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(informationContentEntity)








    //ASSERTION, TOPIC, GRANULARITY TREE, AND ENTRY CLASSES

    CREATE(GranPersp:orkg_GranularityTree:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg granularity tree", description:"An information content entity that is a tree-like hierarchical structure resulting from inter-connected assertions of a specific type. The relation that the assertions are modelling must be a partial order relation, i.e. a relation that is a binary relation R that is transitive (if b has relation R to c and c has relation R to d, than b has relation R to d), reflexive (b has relation R to itself), and antisymmetric (if b has relation R to c and c has relation R to b, than b and c are identical). The parthood relation is a good example for a partial order relation. Partial order relations result in what is called a granular partition that can be represented as a tree. These trees are called granularity trees. By specifying which types of entities are allowed as domains and ranges of a specific partial order relation, one can distinguish different types of granularity trees, with each type representing a granularity perspective, i.e. a class of particular granularity trees. One could, for example, define the granularity perspective of parthood between material entities, and each particular granularity tree of such parthood-relation-chains between actual material entities represents a granularity tree.", URI:"Granularity_tree_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoDocPart)

    CREATE(parthood_based_gran_tree:orkg_ParthoodBasedGranularityTree:orkg_GranularityTree:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg parthood-based granularity tree", description:"A granularity tree that is based on the parthood relation.", URI:"Parthood_based_Granularity_tree_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(GranPersp)

    CREATE(MatEntParthoodGranTree:orkg_MaterialEntityParthoodGranularityTree:orkg_ParthoodBasedGranularityTree:orkg_GranularityTree:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg material entity parthood granularity tree", description:"A granularity tree that is based on the parthood relation between material entities.", URI:"MatEnt_Parthood_based_Granularity_tree_URI", category:"ClassExpression", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://purl.obolibrary.org/obo/BFO_0000040"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(parthood_based_gran_tree)

    CREATE(Ass:orkg_Assertion:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg assertion", description:"An information content entity that is a proposition from some research paper and that is asserted to be true, either by the authors of the paper or by a third party referenced in the paper. An assertion in the orkg is also a model for representing the contents of a particular assertion from a scholarly publication, representing a smallest unit of information that is independent of other units of information. Different types of such assertions can be differentiated.", URI:"Assertion_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(:sepio_Assertion:ClassExpression:Entity {{name:"sepio: assertion", URI:"http://purl.obolibrary.org/obo/SEPIO_0000001", category:"ClassExpression"}})

    CREATE (Ass)-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoDocPart)

    CREATE (:orkg_VersionedAssertion:orkg_Assertion:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg versioned assertion", description:"A version of an orkg assertion. Versions of assertions capture the content of an assertion at a specific point in time and can be used for referencing and citation purposes.", URI:"orkg_versioned_assertion_class_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)

    CREATE (qualityAssertion:orkg_QualityRelationIdentificationAssertion:orkg_Assertion:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg quality relation identification assertion", description:"This assertion models the relation between a particular entity and one of its qualities.", relevant_properties_URI:["http://purl.obolibrary.org/obo/RO_0000086"], relevant_classes_URI:["http://purl.obolibrary.org/obo/PATO_0000128", "http://purl.obolibrary.org/obo/PATO_0000146", "http://purl.obolibrary.org/obo/PATO_0001756", "http://purl.obolibrary.org/obo/PATO_0000014"], URI:"Quality_Identification_Assertion_URI", category:"ClassExpression", KGBB_URI:"QualityIdentificationAssertionKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)

    CREATE (researchTopicAssertion:orkg_ResearchTopicAssertion:orkg_Assertion:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research topic assertion", description:"This assertion models the relation between a particular orkg research paper and its research topic.", URI:"ResearchTopicAssertion_URI", category:"ClassExpression", KGBB_URI:"ResearchTopicAssertionKGBB_URI", relevant_classes_URI:["http://orkg/researchtopic_1", "http://orkg???????2"], relevant_properties_URI:["http://edamontology.org/has_topic"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)

    CREATE (confidenceLevelAssertion:orkg_ConfidenceLevelAssertion:orkg_Assertion:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg confidence level specification assertion", description:"This assertion models the specification of the confidence level for a given assertion, topic, or entry in the orkg. As such, it is a statement about a statement or a collection of statements.", URI:"ConfidenceLevelAssertion_URI", category:"ClassExpression", KGBB_URI:"ConfidenceLevelAssertionKGBB_URI", relevant_classes_URI:["http://purl.obolibrary.org/obo/NCIT_C107561", "http://purl.obolibrary.org/obo/NCIT_C85550", "http://purl.obolibrary.org/obo/NCIT_C47944"], relevant_properties_URI:["http://purl.obolibrary.org/obo/SEPIO_0000167"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)

    CREATE (AssMeasurement:orkg_MeasurementAssertion:orkg_Assertion:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg measurement assertion", description:"This assertion models the relation between a particular quality and one of its measurements. E.g., a weight measurement.", URI:"Measurement_Assertion_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)

    CREATE (:orkg_GeographicallyLocatedInAssertion:orkg_Assertion:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg geographically located in assertion", description:"This assertion models the relation of a particular material entity and the particular geographic location it is located in.", URI:"GeographicallyLocatedIn_assertion_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)

    CREATE (:orkg_R0MeasurementAssertion:orkg_Assertion:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg basic reproduction number measurement assertion", description:"This assertion models a particular basic reproduction number measurement with its mean value and a 95% confidence interval.", URI:"R0_measurement_assertion_URI", category:"ClassExpression", KGBB_URI:"R0MeasurementAssertionKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(AssMeasurement)

    CREATE (weightMeasurementAssertion:orkg_WeightMeasurementAssertion:orkg_Assertion:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg weight measurement assertion", description:"This assertion models a particular weight measurement with its value and unit.", URI:"weight_measurement_assertion_URI", category:"ClassExpression", KGBB_URI:"WeightMeasurementAssertionKGBB_URI", relevant_classes_URI:["http://purl.obolibrary.org/obo/PATO_0000128"], relevant_properties_URI:["http://purl.obolibrary.org/obo/IAO_0000004", "http://purl.obolibrary.org/obo/IAO_0000039", "http://purl.obolibrary.org/obo/OBI_0001938", "http://purl.obolibrary.org/obo/IAO_0000417"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(AssMeasurement)

    CREATE (r0MeasurementAssertion:orkg_BasicReproductionNumberMeasurementAssertion:orkg_Assertion:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg basic reproduction number measurement assertion", description:"This assertion models a particular basic reproduction number measurement with its value and a 95% confidence interval.", URI:"r0_measurement_assertion_URI", category:"ClassExpression", KGBB_URI:"R0MeasurementAssertionKGBB_URI", relevant_classes_URI:["http://purl.obolibrary.org/obo/OMIT_0024604", "http://purl.obolibrary.org/obo/STATO_0000196", "http://purl.obolibrary.org/obo/STATO_0000315", "http://purl.obolibrary.org/obo/STATO_0000314", "http://purl.obolibrary.org/obo/STATO_0000561"], relevant_properties_URI:["http://purl.obolibrary.org/obo/IAO_0000004", "http://purl.obolibrary.org/obo/IAO_0000039", "http://purl.obolibrary.org/obo/OBI_0001938", "http://purl.obolibrary.org/obo/IAO_0000417"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(AssMeasurement)

    CREATE (orkgTopic:orkg_Topic:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg topic", description:"An orkg topic is a model for representing the contents of one or more orkg assertions on a single UI topic. In other words, topics are containers for assertions. Often, assertions about the same entity are comprised on a single topic. Different types of such topics can be differentiated.", URI:"orkg_topic_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoDocPart)

    CREATE (:orkg_VersionedTopic:orkg_Topic:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg versioned topic", description:"A version of an orkg topic. Versions of topics capture the content of a topic at a specific point in time and can be used for referencing and citation purposes.", URI:"orkg_versioned_topic_class_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgTopic)


    CREATE (ResActTopic:orkg_ResearchActivityTopic:orkg_Topic:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg Research activity topic", description:"This topic models data about a research activity as it is documented in a particular research papers.", URI:"ResearchActivity_topic_class_URI", category:"ClassExpression", KGBB_URI:"ResearchActivityTopicKGBB_URI", relevant_classes_URI:["http://orkg???????5"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgTopic)

    CREATE (ResResTopic:orkg_ResearchResultTopic:orkg_Topic:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg Research result topic", description:"This topic models data about a research result as it is documented in a particular research paper.", URI:"ResearchResult_topic_class_URI", category:"ClassExpression", KGBB_URI:"ResearchResultTopicKGBB_URI", relevant_classes_URI:["http://orkg???????1"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgTopic)

    CREATE (ResMethTopic:orkg_ResearchMethodTopic:orkg_Topic:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg Research method topic", description:"This topic models data about a research method as it is documented in a particular research paper.", URI:"ResearchMethod_topic_class_URI", category:"ClassExpression", KGBB_URI:"ResearchMethodTopicKGBB_URI", relevant_classes_URI:["http://orkg???????4"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgTopic)

    CREATE (ResObjectiveTopic:orkg_ResearchObjectiveTopic:orkg_Topic:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg Research objective topic", description:"This topic models data about a research objective as it is documented in a particular research paper.", URI:"ResearchObjective_topic_class_URI", category:"ClassExpression", KGBB_URI:"ResearchObjectiveTopicKGBB_URI", relevant_classes_URI:["http://orkg???????3"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgTopic)

    CREATE (materialEntityTopic:orkg_MaterialEntityTopic:orkg_Topic:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg material entity topic", description:"This topic models all information relating to a particular material entity.", URI:"material_entity_topic_URI", category:"ClassExpression", KGBB_URI:"MaterialEntityTopicKGBB_URI", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://purl.obolibrary.org/obo/BFO_0000040"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgTopic)

    CREATE (scholarlyPublicationEntry:orkg_ScholarlyPublicationEntry:orkg_Entry:iao_Document:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg scholarly publication entry", description:"This entry models all information relating to a particular scholarly publication.", URI:"scholarly_publication_entry_URI", category:"ClassExpression", KGBB_URI:"ScholarlyPublicationEntryKGBB_URI", relevant_classes_URI:["http://orkg???????2", "http://orkg/researchtopic_1"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(entryClass:orkg_Entry:iao_Document:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg entry", description:"An orkg entry is a model for representing the contents of one or more orkg topics as a single entry. In other words, entries are containers for topics. Often, topics about the same topic or entity are comprised in a single entry. Different types of such entries can be differentiated.", URI:"orkg_entry_class_URI", category:"ClassExpression"}})

    CREATE (:orkg_VersionedEntry:orkg_Entry:iao_Document:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg versioned entry", description:"A version of an orkg entry. Versions of entries capture the content of an entry at a specific point in time and can be used for referencing and citation purposes.", URI:"orkg_versioned_entry_class_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(entryClass)

    CREATE (scholarlyPublicationEntry)-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoPub)

    CREATE (entryClass)-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoDoc)

    CREATE (:ORKGVersionedEntryClass:orkg_Entry:iao_Document:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg versioned entry", URI:"orkg versioned entry", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(entryClass)








    //KGBB CLASSES

    CREATE (assertionKGBB:AssertionKGBB:KGBB:ClassExpression:Entity {{name:"assertion Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages assertion data.", URI:"AssertionKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"assertion"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbb:KGBB:ClassExpression:Entity {{name:"Knowledge Graph Building Block", description:"A Knowledge Graph Building Block is a knowledge graph processing module that manages the storing of data in a knowledge graph application, the presentation of data from a knowledge graph in a user interface and the export of data from a knowledge graph in various export formats and data models.", URI:"KGBB_URI", category:"ClassExpression", operational_KGBB:"false"}})

    CREATE (confidenceLevelAssertionKGBB:ConfidenceLevelAssertionKGBB:AssertionKGBB:KGBB:ClassExpression:Entity {{name:"confidence level specification assertion Knowledge Graph Building Block", description:"An assertion Knowledge Graph Building Block that manages data referring to the specification of confidence levels for particular assertions, topics, or entries.", URI:"ConfidenceLevelAssertionKGBB_URI", category:"ClassExpression", operational_KGBB:"true", data_item_type:"assertion"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(assertionKGBB)

    CREATE (granperspectiveKGBB:GranularityPerspectiveKGBB:KGBB:ClassExpression:Entity {{name:"granularity perspective Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages data referring to granularity trees.", URI:"GranularityPerspectiveKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"assertion"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbb)

    CREATE (parthood_basedgranperspectiveKGBB:ParthoodBasedGranularityPerspectiveKGBB:GranularityPerspectiveKGBB:KGBB:ClassExpression:Entity {{name:"parthood-based granularity perspective Knowledge Graph Building Block", description:"A granularity perspective Knowledge Graph Building Block that manages data referring to granularity trees that are based on the parthood relation.", partial_order_relation:"HAS_PART", URI:"Parthood-BasedGranularityPerspectiveKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"assertion"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(granperspectiveKGBB)

    CREATE (MatEntparthoodgranperspectiveKGBB:MaterialEntityParthoodGranularityPerspectiveKGBB:ParthoodBasedGranularityPerspectiveKGBB:GranularityPerspectiveKGBB:KGBB:ClassExpression:Entity {{name:"material entity parthood-based granularity perspective Knowledge Graph Building Block", description:"A parthood-based granularity perspective Knowledge Graph Building Block that manages data referring to granularity trees that are based on the parthood relation between material entities.", URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", category:"ClassExpression", operational_KGBB:"true", label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(granTree_ind:orkg_MaterialEntityParthoodGranularityTree_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET granTree_ind.last_updated_on = localdatetime(), granTree_ind.instance_label = "$_label_name_$"

    WITH granTree_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN granTree_ind.contributed_by THEN [1] ELSE [] END |
    SET granTree_ind.contributed_by = granTree_ind.contributed_by + "{creator}"
    )', data_item_type:"assertion"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(parthood_basedgranperspectiveKGBB)

    CREATE (entrykgbb:EntryKGBB:KGBB:ClassExpression:Entity {{name:"entry Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages entry data.", URI:"EntryKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"entry"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbb)

    CREATE (scholarlyPublicationEntrykgbb:ScholarlyPublicationEntryKGBB:EntryKGBB:KGBB:ClassExpression:Entity {{name:"scholarly publication entry Knowledge Graph Building Block", description:"An entry Knowledge Graph Building Block that manages data about a scholarly publication.", relevant_classes_URI:["http://orkg???????2", "http://orkg/researchtopic_1"], URI:"ScholarlyPublicationEntryKGBB_URI", category:"ClassExpression", operational_KGBB:"true", storage_model_cypher_code:'MATCH (ORKGEntryClass) WHERE ORKGEntryClass.URI="orkg_entry_class_URI"

    CREATE (entry:orkg_ScholarlyPublicationEntry_IND:orkg_Entry_IND:iao_Document_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"Publication entry unit", URI:"entry_uri", type:"scholarly_publication_entry_URI", entry_doi:"{doiEntry}", publication_doi:"pub_doiX", publication_title:"pub_titleX", entry_URI:"entry_uri", description:"This type of entry models information about a particular research paper.", KGBB_URI:"ScholarlyPublicationEntryKGBB_URI", object_URI:"new_individual_uri1", node_type: "entry", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})-[:HAS_DOI {{category:"DataPropertyExpression", URI:"http://prismstandard.org/namespaces/basic/2.0/doi", entry_URI:"entry_uri"}}]->(doi_entry:EntryDOI_IND:DOI_IND:Literal_IND {{value:"some entry DOI", current_version:"true", entry_doi:"{doiEntry}", entry_URI:"entry_uri", category:"NamedIndividual"}})

    CREATE (entry)-[:IDENTIFIER {{category:"DataPropertyExpression", URI:"https://dublincore.org/specifications/dublin-core/dcmi-terms/#identifier", entry_URI:"entry_uri"}}]->(doi_entry)

    CREATE (publication:orkg_ResearchPaper_IND:iao_PublicationAboutAnInvestigation_IND:iao_Document_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"pub_titleX", type:"http://orkg???????2", publication_doi:"pub_doiX", publication_year:pub_yearX, publication_authors:"pub_authorsX", URI:"new_individual_uri1", publication_journal:"pub_journalX", publication_publisher:"Xpub_publisherX", entry_URI:"entry_uri", category:"NamedIndividual", data_node_type:["entry_object"], current_version:"true", assertion_URI:["NULL"], topic_URI:["NULL"], last_updated_on:localdatetime(), versioned_doi:["NULL"], created_on:localdatetime(), created_by:"{creator}", created_with:"{createdWith}"}})-[:HAS_DOI {{category:"DataPropertyExpression", URI:"http://prismstandard.org/namespaces/basic/2.0/doi", entry_URI:"entry_uri"}}]->(doi_publication:PublicationDOI_IND:DOI_IND:Literal_IND {{value:"pub_doiX", publication_doi:"pub_doiX", entry_URI:"entry_uri", category:"NamedIndividual", versioned_doi:["NULL"], current_version:"true"}})

    CREATE (publication)-[:IDENTIFIER {{category:"DataPropertyExpression", URI:"https://dublincore.org/specifications/dublin-core/dcmi-terms/#identifier", entry_URI:"entry_uri"}}]->(doi_publication)

    CREATE (entry)-[:IS_TRANSLATION_OF {{category:"ObjectPropertyExpression", URI:"http://purl.org/vocab/frbr/core#translationOf", entry_URI:"entry_uri", description:"It identifies the original expression of a translated one."}}]->(publication)', search_cypher_code:"cypherQuery", data_item_type:"entry"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(entrykgbb)

    CREATE (topickgbb:TopicKGBB:KGBB:ClassExpression:Entity {{name:"topic Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages topic data.", URI:"TopicKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"topic"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbb)

    CREATE (ResearchActivityTopickgbb:ResearchActivityTopicKGBB:TopicKGBB:KGBB:ClassExpression:Entity {{name:"research activity topic Knowledge Graph Building Block", description:"A topic Knowledge Graph Building Block that manages data about the research activity that is documented in a particular research paper.", URI:"ResearchActivityTopicKGBB_URI", category:"ClassExpression", relevant_classes_URI:["http://orkg???????5"], storage_model_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}})
    MATCH (publication_node) WHERE publication_node.entry_URI="{entryURI}" AND ("entry_object" IN publication_node.data_node_type)

    CREATE (publication_node)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchActivity:ResearchActivity_ind:orkg_ResearchActivity_IND:obi_Investigation_IND:obi_PlannedProcess_IND:bfo_Process_IND:NamedIndividual:Entity {{name:"research activity", versioned_doi:["NULL"], dataset_doi:["NULL"], description:"A planned process that has been planned and executed by some research agent and that has some research result. The process ends if some specific research objective is achieved.", URI:"new_individual_uri1", ontology_ID:"ORKG", topic_URI:"{topic_uri}", type:"http://orkg???????5", instance_label:"Research overview", category:"NamedIndividual", entry_URI:"{entryURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", data_node_type:["topic_object"]}})

    CREATE (entry_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchActivityTopic_ind:orkg_ResearchActivityTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research overview topic unit", description:"This topic models all data of a particular research activity as it is documented in a particular research paper.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"ResearchActivity_topic_class_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchActivityTopicKGBB_URI", editable:"false", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"Research overview"}})

    CREATE (ResearchActivityTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchActivity)

    CREATE (entry_node)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchActivity)', from_activity_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node

    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node

    CREATE (object_node)-[:HAS_OCCURRENT_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000117", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchActivity:ResearchActivity_ind:orkg_ResearchActivity_IND:obi_Investigation_IND:obi_PlannedProcess_IND:bfo_Process_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["topic_object", "input1"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchActivityTopicIND_URI", user_input:"{topic_uri}"}})

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchActivityTopic_ind:orkg_ResearchActivityTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity topic unit", description:"This topic models all data of a particular research activity as it is documented in a particular research paper.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"ResearchActivity_topic_class_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchActivityTopicKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"$_input_name_$ [$_ontology_ID_$]"}})

    CREATE (ResearchActivityTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchActivity)', from_method_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node

    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node

    CREATE (ResearchActivity:ResearchActivity_ind:orkg_ResearchActivity_IND:obi_Investigation_IND:obi_PlannedProcess_IND:bfo_Process_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["topic_object", "input1"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchActivityTopicIND_URI", user_input:"{topic_uri}"}})-[:REALIZES {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000055", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"to say that b realizes c at t is to assert that there is some material entity d & b is a process which has participant d at t & c is a disposition or role of which d is bearer_of at t& the type instantiated by b is correlated with the type instantiated by c. (axiom label in BFO2 Reference: [059-003])."}}]->(object_node)

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchActivityTopic_ind:orkg_ResearchActivityTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity topic unit", description:"This topic models all data of a particular research activity as it is documented in a particular research paper.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"ResearchActivity_topic_class_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchActivityTopicKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"$_input_name_$ [$_ontology_ID_$]"}})

    CREATE (ResearchActivityTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchActivity)', from_result_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node

    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node

    CREATE (ResearchActivity:ResearchActivity_ind:orkg_ResearchActivity_IND:obi_Investigation_IND:obi_PlannedProcess_IND:bfo_Process_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["topic_object", "input1"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchActivityTopicIND_URI", user_input:"{topic_uri}"}})-[:HAS_SPECIFIED_OUTPUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000299", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"A relation between a planned process and a continuant participating in that process. The presence of the continuant at the end of the process is explicitly specified in the objective specification which the process realizes the concretization of."}}]->(object_node)

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchActivityTopic_ind:orkg_ResearchActivityTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research overview topic unit", description:"This topic models all data of a particular research activity as it is documented in a particular research paper.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"ResearchActivity_topic_class_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchActivityTopicKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"$_input_name_$ [$_ontology_ID_$]"}})

    CREATE (ResearchActivityTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchActivity)', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"

    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(researchActivityTopic_ind:orkg_ResearchActivityTopic_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET researchActivityTopic_ind.last_updated_on = localdatetime(), researchActivityTopic_ind.object_URI = "new_individual_uri1"

    WITH parent_data_item_node, object_node, researchActivityTopic_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN researchActivityTopic_ind.contributed_by THEN [1] ELSE [] END |
    SET researchActivityTopic_ind.contributed_by = researchActivityTopic_ind.contributed_by + "{creator}"
    )

    WITH parent_data_item_node, object_node, researchActivityTopic_ind
    MATCH (researchActivityTopic_ind)-[:IS_ABOUT]->(researchAct_old:orkg_ResearchActivity_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, researchActivityTopic_ind, researchAct_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchAct_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, researchActivityTopic_ind, researchAct_old SET researchAct_old.current_version = "false"
    WITH researchActivityTopic_ind
    MATCH (researchActivityTopic_ind)-[:IS_ABOUT]->(researchAct_new:orkg_ResearchActivity_IND {{current_version:"true"}})
    SET researchAct_new.instance_label = "$_label_name_$", researchAct_new.URI = "new_individual_uri1", researchAct_new.created_on = localdatetime(), researchAct_new.last_updated_on = localdatetime(), researchAct_new.created_by = "{creator}", researchAct_new.contributed_by = ["{creator}"]', edit_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"

    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(researchActivityTopic_ind:orkg_ResearchActivityTopic_IND {{URI:"{topic_uri}", current_version:"true"}}) SET researchActivityTopic_ind.last_updated_on = localdatetime(), researchActivityTopic_ind.topic_label = "$_input_name_$ [$_ontology_ID_$]", researchActivityTopic_ind.object_URI = "new_individual_uri1"

    WITH parent_data_item_node, object_node, researchActivityTopic_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN researchActivityTopic_ind.contributed_by THEN [1] ELSE [] END |
    SET researchActivityTopic_ind.contributed_by = researchActivityTopic_ind.contributed_by + "{creator}"
    )

    WITH parent_data_item_node, object_node, researchActivityTopic_ind
    MATCH (researchActivityTopic_ind)-[:IS_ABOUT]->(researchAct_old:orkg_ResearchActivity_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, researchActivityTopic_ind, researchAct_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchAct_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, researchActivityTopic_ind, researchAct_old SET researchAct_old.current_version = "false"
    WITH researchActivityTopic_ind
    MATCH (researchActivityTopic_ind)-[:IS_ABOUT]->(researchAct_new:orkg_ResearchActivity_IND {{current_version:"true"}})
    SET researchAct_new.name = "$_input_name_$", researchAct_new.instance_label = "$_input_name_$", researchAct_new.ontology_ID = "$_ontology_ID_$", researchAct_new.description = "$_input_description_$", researchAct_new.URI = "new_individual_uri1", researchAct_new.type = "$_input_type_$", researchAct_new.created_on = localdatetime(), researchAct_new.last_updated_on = localdatetime(), researchAct_new.created_by = "{creator}", researchAct_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", operational_KGBB:"true", data_item_type:"topic"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(topickgbb)







    CREATE (ResearchObjectiveTopickgbb:ResearchObjectiveTopicKGBB:TopicKGBB:KGBB:ClassExpression:Entity {{name:"research objective topic Knowledge Graph Building Block", description:"A topic Knowledge Graph Building Block that manages data about the research objective that is documented in a particular research paper.", URI:"ResearchObjectiveTopicKGBB_URI", category:"ClassExpression", relevant_classes_URI:["http://orkg???????3"], storage_model_cypher_code:'MATCH (parent_data_item_node:orkg_ResearchActivityTopic_IND {{entry_URI:"{entryURI}"}})
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI
    OPTIONAL MATCH (object_node)-[:HAS_SPECIFIED_OUTPUT]->(researchResult:orkg_ResearchResult_IND {{current_version:"true"}})
    OPTIONAL MATCH (object_node)-[:REALIZES]->(researchMethod:orkg_ResearchMethod_IND {{current_version:"true"}})

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchObjectiveTopic_ind:orkg_ResearchObjectiveTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective topic unit", description:"This topic models a research objective documented in a particular research paper.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"ResearchObjective_topic_class_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchObjectiveTopicKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"Research objective"}})

    CREATE (object_node)-[:ACHIEVES_PLANNED_OBJECTIVE {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000417", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"This relation obtains between a planned process and a objective specification when the criteria specified in the objective specification are met at the end of the planned process."}}]->(researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"http://orkg???????3", name:"research objective", instance_label:"Research objective", ontology_ID:"ORKG", description:"An information content entity that describes an intended process endpoint for some research activity.", data_node_type:["topic_object"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (ResearchObjectiveTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(researchObjective)

    WITH parent_data_item_node, object_node, researchResult, researchMethod
    FOREACH (i IN CASE WHEN researchResult IS NOT NULL THEN [1] ELSE [] END |
    CREATE (researchObjective)-[:HAS_ACHIEVED_RESULT {{category:"ObjectPropertyExpression", URI:"http://orkg_has_achieved_result", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"This relation obtains between a research objective and a research result when the criteria specified in the objective specification are met at the end of a planned process which has the research result as its output."}}]->(researchResult)
    )

    WITH parent_data_item_node, object_node, researchResult, researchMethod
    FOREACH (i IN CASE WHEN researchMethod IS NOT NULL THEN [1] ELSE [] END |
    CREATE (researchMethod)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"a core relation that holds between a whole and its part."}}]->(researchObjective)
    )', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"

    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(ResearchObjectiveTopic_ind:orkg_ResearchObjectiveTopic_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET ResearchObjectiveTopic_ind.last_updated_on = localdatetime(), ResearchObjectiveTopic_ind.object_URI = "new_individual_uri1"

    WITH parent_data_item_node, object_node, ResearchObjectiveTopic_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchObjectiveTopic_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchObjectiveTopic_ind.contributed_by = ResearchObjectiveTopic_ind.contributed_by + "{creator}"
    )

    WITH parent_data_item_node, object_node, ResearchObjectiveTopic_ind
    MATCH (ResearchObjectiveTopic_ind)-[:IS_ABOUT]->(researchObjective_old:orkg_ResearchObjectiveTopic_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, ResearchObjectiveTopic_ind, researchObjective_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchObjective_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchObjectiveTopic_ind, researchObjective_old SET researchObjective_old.current_version = "false"
    WITH ResearchObjectiveTopic_ind
    MATCH (ResearchObjectiveTopic_ind)-[:IS_ABOUT]->(researchObjective_new:orkg_ResearchObjectiveTopic_IND {{current_version:"true"}})
    SET researchObjective_new.instance_label = "$_label_name_$", researchObjective_new.URI = "new_individual_uri1", researchObjective_new.created_on = localdatetime(), researchObjective_new.last_updated_on = localdatetime(), researchObjective_new.created_by = "{creator}", researchObjective_new.contributed_by = ["{creator}"]', edit_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()WITH entry_node
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node

    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"

    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(ResearchObjectiveTopic_ind:orkg_ResearchObjectiveTopic_IND {{URI:"{topic_uri}", current_version:"true"}}) SET ResearchObjectiveTopic_ind.last_updated_on = localdatetime(), ResearchObjectiveTopic_ind.topic_label = "$_input_name_$ [$_ontology_ID_$]", ResearchObjectiveTopic_ind.object_URI = "new_individual_uri1"

    WITH parent_data_item_node, object_node, ResearchObjectiveTopic_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchObjectiveTopic_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchObjectiveTopic_ind.contributed_by = ResearchObjectiveTopic_ind.contributed_by + "{creator}"
    )

    WITH parent_data_item_node, object_node, ResearchObjectiveTopic_ind
    MATCH (ResearchObjectiveTopic_ind)-[:IS_ABOUT]->(researchObjective_old:orkg_ResearchObjective_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, ResearchObjectiveTopic_ind, researchObjective_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchObjective_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchObjectiveTopic_ind, researchObjective_old SET researchObjective_old.current_version = "false"
    WITH ResearchObjectiveTopic_ind
    MATCH (ResearchObjectiveTopic_ind)-[:IS_ABOUT]->(researchObjective_new:orkg_ResearchObjective_IND {{current_version:"true"}})
    SET researchObjective_new.name = "$_input_name_$", researchObjective_new.instance_label = "$_input_name_$", researchObjective_new.ontology_ID = "$_ontology_ID_$", researchObjective_new.type = "$_input_type_$", researchObjective_new.description = "$_input_description_$", researchObjective_new.URI = "new_individual_uri1", researchObjective_new.created_on = localdatetime(), researchObjective_new.last_updated_on = localdatetime(), researchObjective_new.created_by = "{creator}", researchObjective_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", from_activity_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"
    WITH entry_node, parent_data_item_node, object_node

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchObjectiveTopic_ind:orkg_ResearchObjectiveTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective topic unit", description:"This topic models a research objective documented in a particular research paper.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"ResearchObjective_topic_class_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchObjectiveTopicKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"$_input_name_$ [$_ontology_ID_$]"}})

    CREATE (object_node)-[:ACHIEVES_PLANNED_OBJECTIVE {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000417", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"This relation obtains between a planned process and a objective specification when the criteria specified in the objective specification are met at the end of the planned process."}}]->(researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["topic_object", "input1"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchObjectiveTopicIND_URI", user_input:"{topic_uri}"}})

    CREATE (ResearchObjectiveTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(researchObjective)', from_method_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"
    WITH entry_node, parent_data_item_node, object_node

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchObjectiveTopic_ind:orkg_ResearchObjectiveTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective topic unit", description:"This topic models a research objective documented in a particular research paper.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"ResearchObjective_topic_class_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchObjectiveTopicKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"$_input_name_$ [$_ontology_ID_$]"}})

    CREATE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"a core relation that holds between a whole and its part."}}]->(researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["topic_object", "input1"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchObjectiveTopicIND_URI", user_input:"{topic_uri}"}})

    CREATE (ResearchObjectiveTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(researchObjective)', from_results_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"
    WITH entry_node, parent_data_item_node, object_node

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchObjectiveTopic_ind:orkg_ResearchObjectiveTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective topic unit", description:"This topic models a research objective documented in a particular research paper.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"ResearchObjective_topic_class_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchObjectiveTopicKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"$_input_name_$ [$_ontology_ID_$]"}})

    CREATE (researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["topic_object", "input1"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchObjectiveTopicIND_URI", user_input:"{topic_uri}"}})-[:HAS_ACHIEVED_RESULT {{category:"ObjectPropertyExpression", URI:"http://orkg_has_achieved_result", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"This relation obtains between a research objective and a research result when the criteria specified in the objective specification are met at the end of a planned process which has the research result as its output."}}]->(object_node)

    CREATE (ResearchObjectiveTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(researchObjective)', from_objective_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"
    WITH entry_node, parent_data_item_node, object_node

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_dcontains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchObjectiveTopic_ind:orkg_ResearchObjectiveTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective topic unit", description:"This topic models a research objective documented in a particular research paper.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"ResearchObjective_topic_class_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchObjectiveTopicKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"$_input_name_$ [$_ontology_ID_$]"}})

    CREATE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"a core relation that holds between a whole and its part."}}]->(researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["topic_object", "input1"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchObjectiveTopicIND_URI", user_input:"{topic_uri}"}})

    CREATE (ResearchObjectiveTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(researchObjective)', operational_KGBB:"true", data_item_type:"topic"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(topickgbb)














    CREATE (ResearchResultTopickgbb:ResearchResultTopicKGBB:TopicKGBB:KGBB:ClassExpression:Entity {{name:"research result topic Knowledge Graph Building Block", description:"A topic Knowledge Graph Building Block that manages data about the research results documented in a particular research paper.", relevant_classes_URI:["http://orkg???????1"], URI:"ResearchResultTopicKGBB_URI", category:"ClassExpression", storage_model_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}})
    MATCH (publication_node) WHERE publication_node.entry_URI="{entryURI}" AND ("entry_object" IN publication_node.data_node_type)
    MATCH (parent_data_item_node:orkg_ResearchActivityTopic_IND {{entry_URI:entry_node.URI}})
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI
    OPTIONAL MATCH (object_node)-[:ACHIEVES_PLANNED_OBJECTIVE]->(researchObjective:orkg_ResearchObjective_IND {{current_version:"true"}})

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchResultTopic_ind:orkg_ResearchResultTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result topic unit", description:"This topic models a research result documented in a particular research paper.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"ResearchResult_topic_class_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchResultTopicKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"Research result"}})

    CREATE (object_node)-[:HAS_SPECIFIED_OUTPUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000299", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"A relation between a planned process and a continuant participating in that process. The presence of the continuant at the end of the process is explicitly specified in the objective specification which the process realizes the concretization of."}}]->(researchResult:orkg_ResearchResult_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"http://orkg???????1", name:"research result", instance_label:"Research result", ontology_ID:"ORKG", description:"An information content entity that is intended to be a truthful statement about something and is the output of some research activity. It is usually acquired by some research method which reliably tends to produce (approximately) truthful statements (cf. iao:data item).", data_node_type:["topic_object"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (ResearchResultTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(researchResult)

    CREATE (researchResult)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"a core relation that holds between a whole and its part."}}]->(publication_node)

    WITH parent_data_item_node, object_node, researchObjective
    FOREACH (i IN CASE WHEN researchObjective IS NOT NULL THEN [1] ELSE [] END |
    CREATE (researchObjective)-[:HAS_ACHIEVED_RESULT {{category:"ObjectPropertyExpression", URI:"http://orkg_has_achieved_result", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"This relation obtains between a research objective and a research result when the criteria specified in the objective specification are met at the end of a planned process which has the research result as its output."}}]->(researchResult)
    )', from_results_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchResultTopic_ind:orkg_ResearchResultTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result topic unit", description:"This topic models a research result documented in a particular research paper.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"ResearchResult_topic_class_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchResultTopicKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"$_input_name_$ [$_ontology_ID_$]"}})

    CREATE (researchResult:orkg_ResearchResult_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["topic_object", "input1"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchResultTopicIND_URI", user_input:"{topic_uri}"}})-[:HAS_PART {{category:"ObjectPropertyExpression", property_URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(object_node)

    CREATE (ResearchResultTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(researchResult)', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"

    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(ResearchResultTopic_ind:orkg_ResearchResultTopic_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET ResearchResultTopic_ind.last_updated_on = localdatetime(), ResearchResultTopic_ind.object_URI = "new_individual_uri1"

    WITH parent_data_item_node, object_node, ResearchResultTopic_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchResultTopic_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchResultTopic_ind.contributed_by = ResearchResultTopic_ind.contributed_by + "{creator}"
    )

    WITH parent_data_item_node, object_node, ResearchResultTopic_ind
    MATCH (ResearchResultTopic_ind)-[:IS_ABOUT]->(researchResult_old:orkg_ResearchActivity_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, ResearchResultTopic_ind, researchResult_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchResult_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchResultTopic_ind, researchResult_old SET researchResult_old.current_version = "false"
    WITH ResearchResultTopic_ind
    MATCH (ResearchResultTopic_ind)-[:IS_ABOUT]->(researchResult_new:orkg_ResearchResult_IND {{current_version:"true"}})
    SET researchResult_new.instance_label = "$_label_name_$", researchResult_new.URI = "new_individual_uri1", researchResult_new.created_on = localdatetime(), researchResult_new.last_updated_on = localdatetime(), researchResult_new.created_by = "{creator}", researchResult_new.contributed_by = ["{creator}"]', edit_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()WITH entry_node
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node

    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"

    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(ResearchResultTopic_ind:orkg_ResearchResultTopic_IND {{URI:"{topic_uri}", current_version:"true"}}) SET ResearchResultTopic_ind.last_updated_on = localdatetime(), ResearchResultTopic_ind.topic_label = "$_input_name_$ [$_ontology_ID_$]", ResearchResultTopic_ind.object_URI = "new_individual_uri1"

    WITH parent_data_item_node, object_node, ResearchResultTopic_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchResultTopic_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchResultTopic_ind.contributed_by = ResearchResultTopic_ind.contributed_by + "{creator}"
    )

    WITH parent_data_item_node, object_node, ResearchResultTopic_ind
    MATCH (ResearchResultTopic_ind)-[:IS_ABOUT]->(researchResult_old:orkg_ResearchResult_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, ResearchResultTopic_ind, researchResult_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchResult_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchResultTopic_ind, researchResult_old SET researchResult_old.current_version = "false"
    WITH ResearchResultTopic_ind
    MATCH (ResearchResultTopic_ind)-[:IS_ABOUT]->(researchResult_new:orkg_ResearchResult_IND {{current_version:"true"}})
    SET researchResult_new.name = "$_input_name_$", researchResult_new.instance_label = "$_input_name_$", researchResult_new.ontology_ID = "$_ontology_ID_$", researchResult_new.type = "$_input_type_$", researchResult_new.description = "$_input_description_$", researchResult_new.URI = "new_individual_uri1", researchResult_new.created_on = localdatetime(), researchResult_new.last_updated_on = localdatetime(), researchResult_new.created_by = "{creator}", researchResult_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", from_activity_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH entry_node MATCH (publication_node) WHERE publication_node.entry_URI="{entryURI}" AND ("entry_object" IN publication_node.data_node_type)
    WITH entry_node, publication_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, publication_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"
    WITH entry_node, publication_node, parent_data_item_node, object_node

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchResultTopic_ind:orkg_ResearchResultTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result topic unit", description:"This topic models a research result documented in a particular research paper.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"ResearchResult_topic_class_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchResultTopicKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"$_input_name_$ [$_ontology_ID_$]"}})

    CREATE (object_node)-[:HAS_SPECIFIED_OUTPUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000299", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"A relation between a planned process and a continuant participating in that process. The presence of the continuant at the end of the process is explicitly specified in the objective specification which the process realizes the concretization of."}}]->(researchResult:orkg_ResearchResult_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["topic_object", "input1"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchResultTopicIND_URI", user_input:"{topic_uri}"}})

    CREATE (ResearchResultTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(researchResult)

    CREATE (researchResult)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"a core relation that holds between a whole and its part."}}]->(publication_node)', operational_KGBB:"true", data_item_type:"topic"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(topickgbb)





    CREATE (ResearchMethodTopickgbb:ResearchMethodTopicKGBB:TopicKGBB:KGBB:ClassExpression:Entity {{name:"research method topic Knowledge Graph Building Block", description:"A topic Knowledge Graph Building Block that manages data about the research methods documented in a particular research paper.", relevant_classes_URI:["http://orkg???????4"], URI:"ResearchMethodTopicKGBB_URI", category:"ClassExpression", storage_model_cypher_code:'MATCH (parent_data_item_node:orkg_ResearchActivityTopic_IND {{entry_URI:"{entryURI}"}})
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI
    OPTIONAL MATCH (object_node)-[:ACHIEVES_PLANNED_OBJECTIVE]->(researchObjective:orkg_ResearchObjective_IND {{current_version:"true"}})

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchMethodTopic_ind:orkg_ResearchMethodTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method topic unit", description:"This topic models a research method documented in a particular research paper.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"ResearchMethod_topic_class_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchMethodTopicKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"Research method"}})

    CREATE (object_node)-[:REALIZES {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000055", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"to say that b realizes c at t is to assert that there is some material entity d & b is a process which has participant d at t & c is a disposition or role of which d is bearer_of at t& the type instantiated by b is correlated with the type instantiated by c. (axiom label in BFO2 Reference: [059-003])."}}]->(researchMethod:orkg_ResearchMethod_IND:iao_PlanSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"http://orkg???????4", name:"research method", instance_label:"Research method", ontology_ID:"ORKG", description:"An information content entity that specifies how to conduct some research activity. It usually has some research objective as its part. It instructs some research agent how to achieve the objectives by taking the actions it specifies.", data_node_type:["topic_object"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (ResearchMethodTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(researchMethod)

    WITH parent_data_item_node, object_node, researchObjective
    FOREACH (i IN CASE WHEN researchObjective IS NOT NULL THEN [1] ELSE [] END |
    CREATE (researchMethod)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"a core relation that holds between a whole and its part."}}]->(researchObjective)
    )', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"

    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(ResearchMethodTopic_ind:orkg_ResearchMethodTopic_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET ResearchMethodTopic_ind.last_updated_on = localdatetime(), ResearchMethodTopic_ind.object_URI = "new_individual_uri1"

    WITH parent_data_item_node, object_node, ResearchMethodTopic_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchMethodTopic_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchMethodTopic_ind.contributed_by = ResearchMethodTopic_ind.contributed_by + "{creator}"
    )

    WITH parent_data_item_node, object_node, ResearchMethodTopic_ind
    MATCH (ResearchMethodTopic_ind)-[:IS_ABOUT]->(researchMethod_old:orkg_ResearchMethodTopic_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, ResearchMethodTopic_ind, researchMethod_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchMethod_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchMethodTopic_ind, researchMethod_old SET researchMethod_old.current_version = "false"
    WITH ResearchMethodTopic_ind
    MATCH (ResearchMethodTopic_ind)-[:IS_ABOUT]->(researchMethod_new:orkg_ResearchMethodTopic_IND {{current_version:"true"}})
    SET researchMethod_new.instance_label = "$_label_name_$", researchMethod_new.URI = "new_individual_uri1", researchMethod_new.created_on = localdatetime(), researchMethod_new.last_updated_on = localdatetime(), researchMethod_new.created_by = "{creator}", researchMethod_new.contributed_by = ["{creator}"]', edit_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()WITH entry_node
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node

    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"

    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(ResearchMethodTopic_ind:orkg_ResearchMethodTopic_IND {{URI:"{topic_uri}", current_version:"true"}}) SET ResearchMethodTopic_ind.last_updated_on = localdatetime(), ResearchMethodTopic_ind.topic_label = "$_input_name_$ [$_ontology_ID_$]", ResearchMethodTopic_ind.object_URI = "new_individual_uri1"

    WITH parent_data_item_node, object_node, ResearchMethodTopic_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchMethodTopic_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchMethodTopic_ind.contributed_by = ResearchMethodTopic_ind.contributed_by + "{creator}"
    )

    WITH parent_data_item_node, object_node, ResearchMethodTopic_ind
    MATCH (ResearchMethodTopic_ind)-[:IS_ABOUT]->(researchMethod_old:orkg_ResearchMethod_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, ResearchMethodTopic_ind, researchMethod_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchMethod_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchMethodTopic_ind, researchMethod_old SET researchMethod_old.current_version = "false"
    WITH ResearchMethodTopic_ind
    MATCH (ResearchMethodTopic_ind)-[:IS_ABOUT]->(researchMethod_new:orkg_ResearchMethod_IND {{current_version:"true"}})
    SET researchMethod_new.name = "$_input_name_$", researchMethod_new.instance_label = "$_input_name_$", researchMethod_new.ontology_ID = "$_ontology_ID_$", researchMethod_new.type = "$_input_type_$", researchMethod_new.description = "$_input_description_$", researchMethod_new.URI = "new_individual_uri1", researchMethod_new.created_on = localdatetime(), researchMethod_new.last_updated_on = localdatetime(), researchMethod_new.created_by = "{creator}", researchMethod_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", from_activity_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"
    WITH entry_node, parent_data_item_node, object_node

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchMethodTopic_ind:orkg_ResearchMethodTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method topic unit", description:"This topic models a research method documented in a particular research paper.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"ResearchMethod_topic_class_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchMethodTopicKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"$_input_name_$ [$_ontology_ID_$]"}})

    CREATE (object_node)-[:REALIZES {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000055", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"to say that b realizes c at t is to assert that there is some material entity d & b is a process which has participant d at t & c is a disposition or role of which d is bearer_of at t& the type instantiated by b is correlated with the type instantiated by c. (axiom label in BFO2 Reference: [059-003])."}}]->(researchMethod:orkg_ResearchMethod_IND:iao_PlanSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["topic_object", "input1"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchMethodTopicIND_URI", user_input:"{topic_uri}"}})

    CREATE (ResearchMethodTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(researchMethod)', from_method_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"
    WITH entry_node, parent_data_item_node, object_node

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(ResearchMethodTopic_ind:orkg_ResearchMethodTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method topic unit", description:"This topic models a research method documented in a particular research paper.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"ResearchMethod_topic_class_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchMethodTopicKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"$_input_name_$ [$_ontology_ID_$]"}})

    CREATE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"a core relation that holds between a whole and its part."}}]->(researchMethod:orkg_ResearchMethod_IND:iao_PlanSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["topic_object", "input1"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchMethodTopicIND_URI", user_input:"{topic_uri}"}})

    CREATE (ResearchMethodTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(researchMethod)', operational_KGBB:"true", data_item_type:"topic"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(topickgbb)








    CREATE (materialEntityTopickgbb:MaterialEntityTopicKGBB:TopicKGBB:KGBB:ClassExpression:Entity {{name:"material entity topic Knowledge Graph Building Block", description:"A topic Knowledge Graph Building Block that manages data about a particular material entity.", URI:"MaterialEntityTopicKGBB_URI", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://purl.obolibrary.org/obo/BFO_0000040"], granularity_tree_key:"material_entity_parthood_granularity_tree_URI", category:"ClassExpression", from_result_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"
    WITH object_node, parent_data_item_node
    MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node

    MERGE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(material_entityTopic_ind:orkg_MaterialEntityTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"material entity topic unit", description:"This topic models all information relating to a particular material entity.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"material_entity_topic_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"MaterialEntityTopicKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"$_input_name_$ [$_ontology_ID_$]"}})

    MERGE (material_entityTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(material_entity:bfo_MaterialEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["topic_object", "input1"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1MaterialEntityTopicIND_URI", user_input:"{topic_uri}"}})

    MERGE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"a core relation that holds between a whole and its part."}}]->(material_entityTopic_ind)', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"

    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(material_entityTopic_ind:orkg_MaterialEntityTopic_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET material_entityTopic_ind.last_updated_on = localdatetime(), material_entityTopic_ind.object_URI = "new_individual_uri1"

    WITH parent_data_item_node, object_node, material_entityTopic_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN material_entityTopic_ind.contributed_by THEN [1] ELSE [] END |
    SET material_entityTopic_ind.contributed_by = material_entityTopic_ind.contributed_by + "{creator}"
    )

    WITH parent_data_item_node, object_node, material_entityTopic_ind
    MATCH (material_entityTopic_ind)-[:IS_ABOUT]->(material_entity_old:bfo_MaterialEntity_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, material_entityTopic_ind, material_entity_old
    CALL apoc.refactor.cloneNodesWithRelationships([material_entity_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, material_entityTopic_ind, material_entity_old SET material_entity_old.current_version = "false"
    WITH material_entityTopic_ind
    MATCH (material_entityTopic_ind)-[:IS_ABOUT]->(material_entity_new:bfo_MaterialEntity_IND {{current_version:"true"}})
    SET material_entity_new.instance_label = "$_label_name_$", material_entity_new.URI = "new_individual_uri1", material_entity_new.created_on = localdatetime(), material_entity_new.last_updated_on = localdatetime(), material_entity_new.created_by = "{creator}", material_entity_new.contributed_by = ["{creator}"]', edit_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node

    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"

    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(material_entityTopic_ind:orkg_MaterialEntityTopic_IND {{URI:"{topic_uri}", current_version:"true"}}) SET material_entityTopic_ind.last_updated_on = localdatetime(), material_entityTopic_ind.topic_label = "$_input_name_$ [$_ontology_ID_$]", material_entityTopic_ind.object_URI = "new_individual_uri1"

    WITH parent_data_item_node, object_node, material_entityTopic_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN material_entityTopic_ind.contributed_by THEN [1] ELSE [] END |
    SET material_entityTopic_ind.contributed_by = material_entityTopic_ind.contributed_by + "{creator}"
    )

    WITH parent_data_item_node, object_node, material_entityTopic_ind
    MATCH (material_entityTopic_ind)-[:IS_ABOUT]->(material_entity_old:bfo_MaterialEntity_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, material_entityTopic_ind, material_entity_old
    CALL apoc.refactor.cloneNodesWithRelationships([material_entity_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, material_entityTopic_ind, material_entity_old SET material_entity_old.current_version = "false"
    WITH material_entityTopic_ind
    MATCH (material_entityTopic_ind)-[:IS_ABOUT]->(material_entity_new:bfo_MaterialEntity_IND {{current_version:"true"}})
    SET material_entity_new.name = "$_input_name_$", material_entity_new.instance_label = "$_input_name_$", material_entity_new.ontology_ID = "$_ontology_ID_$", material_entity_new.description = "$_input_description_$", material_entity_new.URI = "new_individual_uri1", material_entity_new.type = "$_input_type_$", material_entity_new.created_on = localdatetime(), material_entity_new.last_updated_on = localdatetime(), material_entity_new.created_by = "{creator}", material_entity_new.contributed_by = ["{creator}"]', from_material_entity_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"
    WITH object_node, parent_data_item_node
    MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    OPTIONAL MATCH (matEnt1 {{current_version:"true"}})-[:HAS_PART]->(object_node)
    OPTIONAL MATCH (root_topic:orkg_MaterialEntityTopic_IND {{current_version:"true"}})-[:CONTAINS]->(parent_data_item_node)
    OPTIONAL MATCH (GranTree:orkg_MaterialEntityParthoodGranularityTree_IND {{URI:object_node.material_entity_parthood_granularity_tree_URI, current_version:"true"}})
    WITH object_node, parent_data_item_node, entry_node, matEnt1, root_topic, GranTree
    FOREACH (i IN CASE WHEN NOT "{creator}" IN GranTree.contributed_by THEN [1] ELSE [] END |
    SET GranTree.contributed_by = GranTree.contributed_by + "{creator}"
    )

    WITH object_node, parent_data_item_node, entry_node, matEnt1, root_topic, GranTree
    OPTIONAL MATCH (object_node)-[:HAS_PART]->(matEnt2 {{current_version:"true"}})

    WITH object_node, parent_data_item_node, entry_node, matEnt1, matEnt2, root_topic, GranTree

    MERGE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(material_entityTopic_ind:orkg_MaterialEntityTopic_IND:orkg_Topic_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"material entity topic unit", description:"This topic models all information relating to a particular material entity.", URI:"{topic_uri}", topic_URI:"{topic_uri}", type:"material_entity_topic_URI", node_type:"topic", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"MaterialEntityTopicKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], topic_label:"$_input_name_$ [$_ontology_ID_$]"}})

    MERGE (material_entityTopic_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}"}}]->(material_entity:bfo_MaterialEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["topic_object", "input1"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1MaterialEntityTopicIND_URI", user_input:"{topic_uri}"}})

    MERGE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", description:"a core relation that holds between a whole and its part."}}]->(material_entity)

    WITH object_node, parent_data_item_node, entry_node, matEnt1, material_entityTopic_ind, material_entity, root_topic, GranTree, matEnt2,  object_node.material_entity_parthood_granularity_tree_URI IS NOT NULL AS Predicate


    FOREACH (i IN CASE WHEN Predicate THEN [1] ELSE [] END |

    SET material_entity.material_entity_parthood_granularity_tree_URI = object_node.material_entity_parthood_granularity_tree_URI
    SET GranTree.last_updated_on = localdatetime()
    )

    WITH object_node, parent_data_item_node, entry_node, matEnt1, material_entityTopic_ind, material_entity, root_topic, GranTree, matEnt2,  object_node.material_entity_parthood_granularity_tree_URI IS NOT NULL AS Predicate

    FOREACH (i IN CASE WHEN matEnt1 IS NOT NULL AND NOT Predicate AND matEnt2 IS NULL THEN [1] ELSE [] END |

    MERGE (root_topic)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", material_entity_parthood_granularity_tree_URI:"new_individual_uri2"}}]->(material_entity_parthood_granTree_ind:orkg_MaterialEntityParthoodGranularityTree_IND:orkg_ParthoodBasedGranularityTree_IND:orkg_GranularityTree_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"material entity parthood granularity tree", URI_property_key:"material_entity_parthood_granularity_tree_URI", description:"This granularity tree models all parthood-related information about a particular material entity.", URI:"new_individual_uri2", type:"MatEnt_Parthood_based_Granularity_tree_URI", node_type:"granularity_tree", category:"NamedIndividual", entry_URI:"{entryURI}", target_KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", object_URI:matEnt1.URI, created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], ontology_ID:"ORKG", instance_label:matEnt1.name + " parthood granularity tree"}})

    MERGE (material_entity_parthood_granTree_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", material_entity_parthood_granularity_tree_URI:"new_individual_uri2"}}]->(matEnt1)
    SET material_entity.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    SET object_node.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    SET matEnt1.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    )

    WITH object_node, parent_data_item_node, entry_node, matEnt1, material_entityTopic_ind, material_entity, root_topic, GranTree, matEnt2,  object_node.material_entity_parthood_granularity_tree_URI IS NOT NULL AS Predicate

    FOREACH (i IN CASE WHEN matEnt2 IS NOT NULL AND NOT Predicate AND matEnt1 IS NULL THEN [1] ELSE [] END |

    MERGE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", material_entity_parthood_granularity_tree_URI:"new_individual_uri2"}}]->(material_entity_parthood_granTree_ind:orkg_MaterialEntityParthoodGranularityTree_IND:orkg_ParthoodBasedGranularityTree_IND:orkg_GranularityTree_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"material entity parthood granularity tree", description:"This granularity tree models all parthood-related information about a particular material entity.", URI:"new_individual_uri2", type:"MatEnt_Parthood_based_Granularity_tree_URI", URI_property_key:"material_entity_parthood_granularity_tree_URI", node_type:"granularity_tree", category:"NamedIndividual", entry_URI:"{entryURI}", target_KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", object_URI:object_node.URI, created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], ontology_ID:"ORKG", instance_label:object_node.name + " parthood granularity tree"}})

    MERGE (material_entity_parthood_granTree_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", material_entity_parthood_granularity_tree_URI:"new_individual_uri2"}}]->(object_node)
    SET material_entity.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    SET object_node.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    SET matEnt2.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    )

    RETURN object_node, matEnt1, matEnt2, material_entityTopic_ind, material_entity', search_cypher_code:"cypherQuery", operational_KGBB:"true", data_item_type:"topic"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(topickgbb)

    CREATE (qualitykgbb:QualityIdentificationAssertionKGBB:AssertionKGBB:KGBB:ClassExpression:Entity {{name:"quality relation identification assertion Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages quality identification assertion data.", relevant_properties_URI:["http://purl.obolibrary.org/obo/RO_0000086"], relevant_classes_URI:["http://purl.obolibrary.org/obo/PATO_0000128", "http://purl.obolibrary.org/obo/PATO_0000146", "http://purl.obolibrary.org/obo/PATO_0001756", "http://purl.obolibrary.org/obo/PATO_0000014"], URI:"QualityIdentificationAssertionKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node

    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "assertion_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH object_node, parent_data_item_node, entry_node

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(QualityAssertionind:orkg_QualityRelationIdentificationAssertion_IND:orkg_Assertion_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"Quality relation identification assertion unit", URI:"{assertionURI}", description:"This assertion models information about the identification of a particular physical quality of a particular material entity.", type:"Quality_Identification_Assertion_URI", object_URI:"new_individual_uri1", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", KGBB_URI:"QualityIdentificationAssertionKGBB_URI", node_type:"assertion", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", assertion_label:"$_input_name_$ [$_ontology_ID_$]"}})

    CREATE (QualityAssertionind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(quality:pato_PhysicalQuality_IND:pato_Quality_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["assertion_object", "input1"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1QualityAssertionIND_URI", user_input:"{assertionURI}"}})

    CREATE (object_node)-[:HAS_QUALITY {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/RO_0000086", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}", description:"a relation between an independent continuant (the bearer) and a quality, in which the quality specifically depends on the bearer for its existence."}}]->(quality)', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "topic_object"

    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(QualityAssertionind:orkg_QualityRelationIdentificationAssertion_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET QualityAssertionind.last_updated_on = localdatetime(), QualityAssertionind.object_URI = "new_individual_uri1"

    WITH parent_data_item_node, object_node, QualityAssertionind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN QualityAssertionind.contributed_by THEN [1] ELSE [] END |
    SET QualityAssertionind.contributed_by = QualityAssertionind.contributed_by + "{creator}"
    )

    WITH parent_data_item_node, object_node, QualityAssertionind
    MATCH (QualityAssertionind)-[:IS_ABOUT]->(quality_old:pato_PhysicalQuality_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, QualityAssertionind, quality_old
    CALL apoc.refactor.cloneNodesWithRelationships([quality_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, QualityAssertionind, quality_old SET quality_old.current_version = "false"
    WITH QualityAssertionind
    MATCH (QualityAssertionind)-[:IS_ABOUT]->(quality_new:pato_PhysicalQuality_IND {{current_version:"true"}})
    SET quality_new.instance_label = "$_label_name_$", quality_new.URI = "new_individual_uri1", quality_new.created_on = localdatetime(), quality_new.last_updated_on = localdatetime(), quality_new.created_by = "{creator}", quality_new.contributed_by = ["{creator}"]', edit_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node

    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "assertion_object"

    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(QualityAssertionind:orkg_QualityRelationIdentificationAssertion_IND {{URI:"{assertionURI}", current_version:"true"}}) SET QualityAssertionind.last_updated_on = localdatetime(), QualityAssertionind.assertion_label = "$_input_name_$ [$_ontology_ID_$]", QualityAssertionind.object_URI = "new_individual_uri1"

    WITH parent_data_item_node, object_node, QualityAssertionind

    FOREACH (i IN CASE WHEN NOT "{creator}" IN QualityAssertionind.contributed_by THEN [1] ELSE [] END |
    SET QualityAssertionind.contributed_by = QualityAssertionind.contributed_by + "{creator}"
    )

    WITH parent_data_item_node, object_node, QualityAssertionind
    MATCH (QualityAssertionind)-[:IS_ABOUT]->(quality_old:pato_PhysicalQuality_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, QualityAssertionind, quality_old
    CALL apoc.refactor.cloneNodesWithRelationships([quality_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, QualityAssertionind, quality_old SET quality_old.current_version = "false"
    WITH QualityAssertionind
    MATCH (QualityAssertionind)-[:IS_ABOUT]->(quality_new:pato_PhysicalQuality_IND {{current_version:"true"}})
    SET quality_new.name = "$_input_name_$", quality_new.instance_label = "$_input_name_$", quality_new.ontology_ID = "$_ontology_ID_$", quality_new.description = "$_input_description_$", quality_new.URI = "new_individual_uri1", quality_new.type = "$_input_type_$", quality_new.created_on = localdatetime(), quality_new.last_updated_on = localdatetime(), quality_new.created_by = "{creator}", quality_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", data_item_type:"assertion"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(assertionKGBB)

    CREATE (measurementkgbb:MeasurementAssertionKGBB:AssertionKGBB:KGBB:ClassExpression:Entity {{name:"measurement assertion Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages measurement assertion data.", URI:"MeasurementAssertionKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"assertion"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(assertionKGBB)

    CREATE (weightkgbb:WeightMeasurementAssertionKGBB:MeasurementAssertionKGBB:AssertionKGBB:KGBB:ClassExpression:Entity {{name:"weight measurement assertion Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages weight measurement assertion data.", URI:"WeightMeasurementAssertionKGBB_URI", relevant_classes_URI:["http://purl.obolibrary.org/obo/PATO_0000128"], relevant_properties_URI:["http://purl.obolibrary.org/obo/IAO_0000004", "http://purl.obolibrary.org/obo/IAO_0000039", "http://purl.obolibrary.org/obo/OBI_0001938", "http://purl.obolibrary.org/obo/IAO_0000417"], category:"ClassExpression", operational_KGBB:"true", weight_measurement_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "assertion_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH object_node, parent_data_item_node, entry_node

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(WeightMeasurementAssertionind:orkg_WeightMeasurementAssertion_IND:orkg_Assertion_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"Weight measurement assertion unit", URI:"{assertionURI}", description:"This assertion models information about a particular weight measurement of a particular material entity.", type:"weight_measurement_assertion_URI", object_URI:"new_individual_uri1", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", KGBB_URI:"WeightMeasurementAssertionKGBB_URI", node_type:"assertion", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", assertion_label:"$_input_value_$ $_input_name_$ [$_ontology_ID_$]"}})

    CREATE (WeightMeasurementAssertionind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(scalarmeasdatum:iao_ScalarMeasurementDatum_IND:iao_MeasurementDatum_IND:iao_data_item_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"http://purl.obolibrary.org/obo/IAO_0000032", name:"iao scalar measurement datum", description:"A scalar measurement datum is a measurement datum that is composed of two parts, numerals and a unit label.", current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (object_node)-[:IS_QUALITY_MEASURED_AS {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000417", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}", description:"inverse of the relation of is quality measurement of, which is: m is a quality measurement of q at t. When q is a quality, there is a measurement process p that has specified output m, a measurement datum, that is about q."}}]->(scalarmeasdatum)

    CREATE (scalarmeasdatum)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(scalarvaluespec:obi_ScalarValueSpecification_IND:obi_ValueSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri2", type:"http://purl.obolibrary.org/obo/OBI_0001931", name:"obi scalar value specification", description:"A value specification that consists of two parts: a numeral and a unit label.", current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (scalarvaluespec)-[:SPECIFIES_VALUE_OF {{category:"ObjectPropertyExpression", description:"A relation between a value specification and an entity which the specification is about.", URI:"http://purl.obolibrary.org/obo/OBI_0001927", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(object_node)

    CREATE (scalarvaluespec)-[:HAS_MEASUREMENT_UNIT_LABEL {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000039", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(weightUnit:uo_GramBasedUnit_IND:NamedIndividual:Entity {{URI:"new_individual_uri3", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["input2"], entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input2", input_version_ID:0, inputVariable:2, input_info_URI:"InputInfo2WeightMeasurementAssertionIND_URI", user_input:"{assertionURI}"}})

    CREATE (scalarvaluespec)-[:HAS_MEASUREMENT_VALUE {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000004", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(weightValue:Value_IND:Literal_IND:NamedIndividual:Entity {{URI:"new_individual_uri4", type:"orkg_value_URI", name:"$_input_value_$", description:"The value of a weight measurement", data_node_type:["input1"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1WeightMeasurementAssertionIND_URI", user_input:"{assertionURI}", value:"$_input_value_$", data_type:"xsd:float"}})', edit_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "assertion_object"

    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(WeightMeasurementAssertionind:orkg_WeightMeasurementAssertion_IND {{URI:"{assertionURI}", current_version:"true"}}) SET WeightMeasurementAssertionind.last_updated_on = localdatetime(), WeightMeasurementAssertionind.assertion_label = "$_input_name_$ [$_ontology_ID_$]"

    WITH parent_data_item_node, object_node, WeightMeasurementAssertionind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN WeightMeasurementAssertionind.contributed_by THEN [1] ELSE [] END |
    SET WeightMeasurementAssertionind.contributed_by = WeightMeasurementAssertionind.contributed_by + "{creator}"
    )

    WITH parent_data_item_node, object_node, WeightMeasurementAssertionind
    MATCH (WeightMeasurementAssertionind)-[:IS_ABOUT]->()-[:HAS_VALUE_SPECIFICATION]->()-[:HAS_MEASUREMENT_UNIT_LABEL]->(weightUnit_old:uo_GramBasedUnit_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, WeightMeasurementAssertionind, weightUnit_old
    CALL apoc.refactor.cloneNodesWithRelationships([weightUnit_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, WeightMeasurementAssertionind, weightUnit_old SET weightUnit_old.current_version = "false"
    WITH parent_data_item_node, object_node, WeightMeasurementAssertionind
    MATCH (WeightMeasurementAssertionind)-[:IS_ABOUT]->()-[:HAS_VALUE_SPECIFICATION]->()-[:HAS_MEASUREMENT_UNIT_LABEL]->(weightUnit_new:uo_GramBasedUnit_IND {{current_version:"true"}})
    SET weightUnit_new.name = "$_input_name_$", weightUnit_new.instance_label = "$_input_name_$", weightUnit_new.ontology_ID = "$_ontology_ID_$", weightUnit_new.description = "$_input_description_$", weightUnit_new.URI = "new_individual_uri1", weightUnit_new.type = "$_input_type_$", weightUnit_new.created_on = localdatetime(), weightUnit_new.last_updated_on = localdatetime(), weightUnit_new.created_by = "{creator}", weightUnit_new.contributed_by = ["{creator}"]

    WITH parent_data_item_node, object_node, WeightMeasurementAssertionind
    MATCH (WeightMeasurementAssertionind)-[:IS_ABOUT]->()-[:HAS_VALUE_SPECIFICATION]->()-[:HAS_MEASUREMENT_VALUE]->(weightValue_old:Value_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, WeightMeasurementAssertionind, weightValue_old
    CALL apoc.refactor.cloneNodesWithRelationships([weightValue_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, WeightMeasurementAssertionind, weightValue_old SET weightValue_old.current_version = "false"
    WITH WeightMeasurementAssertionind
    MATCH (WeightMeasurementAssertionind)-[:IS_ABOUT]->()-[:HAS_VALUE_SPECIFICATION]->()-[:HAS_MEASUREMENT_VALUE]->(weightValue_new:Value_IND {{current_version:"true"}})
    SET weightValue_new.name = "$_input_value_$", weightValue_new.value = "$_input_value_$", weightValue_new.URI = "new_individual_uri2", weightValue_new.created_on = localdatetime(), weightValue_new.last_updated_on = localdatetime(), weightValue_new.created_by = "{creator}", weightValue_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", data_item_type:"assertion"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(measurementkgbb)












    CREATE (R0Measurementkgbb:BasicReproductionNumberMeasurementAssertionKGBB:MeasurementAssertionKGBB:AssertionKGBB:KGBB:ClassExpression:Entity {{name:"basic reproduction number measurement assertion Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages basic reprodcution number measurement assertion data.", URI:"R0MeasurementAssertionKGBB_URI", relevant_classes_URI:["http://purl.obolibrary.org/obo/OMIT_0024604", "http://purl.obolibrary.org/obo/STATO_0000196", "http://purl.obolibrary.org/obo/STATO_0000315", "http://purl.obolibrary.org/obo/STATO_0000314", "http://purl.obolibrary.org/obo/STATO_0000561"], relevant_properties_URI:["http://purl.obolibrary.org/obo/IAO_0000004", "http://purl.obolibrary.org/obo/IAO_0000039", "http://purl.obolibrary.org/obo/OBI_0001938", "http://purl.obolibrary.org/obo/IAO_0000417"], category:"ClassExpression", operational_KGBB:"true", r0_measurement_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "assertion_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(r0MeasurementAssertionind:orkg_BasicReproductionNumberMeasurementAssertion_IND:orkg_Assertion_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"R0 measurement assertion unit", URI:"{assertionURI}", description:"This assertion models information about a particular basic reproduction number measurement of a particular population.", type:"r0_measurement_assertion_URI", object_URI:"new_individual_uri1", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", KGBB_URI:"R0MeasurementAssertionKGBB_URI", node_type:"assertion", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", assertion_label:"R0: $_input_value_$ ($_input_value1_$ - $_input_value2_$)"}})

    CREATE (r0MeasurementAssertionind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(scalarmeasdatum:iao_ScalarMeasurementDatum_IND:iao_MeasurementDatum_IND:iao_data_item_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"http://purl.obolibrary.org/obo/IAO_0000032", name:"iao scalar measurement datum", description:"A scalar measurement datum is a measurement datum that is composed of two parts, numerals and a unit label.", current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (object_node)-[:IS_QUALITY_MEASURED_AS {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000417", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}", description:"inverse of the relation of is quality measurement of, which is: m is a quality measurement of q at t. When q is a quality, there is a measurement process p that has specified output m, a measurement datum, that is about q."}}]->(scalarmeasdatum)

    CREATE (scalarmeasdatum)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(scalarvaluespec:obi_ScalarValueSpecification_IND:obi_ValueSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri2", type:"http://purl.obolibrary.org/obo/OBI_0001931", name:"obi scalar value specification", description:"A value specification that consists of two parts: a numeral and a unit label.", current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (scalarvaluespec)-[:SPECIFIES_VALUE_OF {{category:"ObjectPropertyExpression", description:"A relation between a value specification and an entity which the specification is about.", URI:"http://purl.obolibrary.org/obo/OBI_0001927", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(object_node)

    CREATE (scalarvaluespec)-[:HAS_MEASUREMENT_UNIT_LABEL {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000039", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(r0countUnit:uo_CountUnit_IND:uo_DimensionlessUnit_IND:uo_Unit_IND:NamedIndividual:Entity {{URI:"new_individual_uri3", type:"http://purl.obolibrary.org/obo/UO_0000189", name:"count unit", ontology_ID:"UO", description:"A dimensionless unit which denotes a simple count of things. [MGED:MGED]", current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (scalarvaluespec)-[:HAS_MEASUREMENT_VALUE {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000004", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(r0Value:Value_IND:Literal_IND:NamedIndividual:Entity {{URI:"new_individual_uri4", type:"orkg_value_URI", name:"$_input_value_$", description:"The value of a basic reproduction number measurement", data_node_type:["input1"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1R0MeasurementAssertionIND_URI", user_input:"{assertionURI}", value:"$_input_value_$", data_type:"xsd:float"}})

    CREATE (scalarmeasdatum)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(confInterval:stato_ConfidenceInterval_IND:NamedIndividual:Entity {{URI:"new_individual_uri5", type:"http://purl.obolibrary.org/obo/STATO_0000196", name:"stato confidence interval", description:"A confidence interval is a data item which defines an range of values in which a measurement or trial falls corresponding to a given probability.", current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (confInterval)-[:HAS_PART {{category:"ObjectPropertyExpression", description:"a core relation that holds between a whole and its part.", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(upperconflimit:stato_UpperConfidenceLimit_IND:NamedIndividual:Entity {{URI:"new_individual_uri6", type:"http://purl.obolibrary.org/obo/STATO_0000314", name:"stato upper confidence limit", description:"Upper confidence limit is a data item which is a largest value bounding a confidence interval.", current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (upperconflimit)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(upperscalarvaluespec:obi_ScalarValueSpecification_IND:obi_ValueSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri8", type:"http://purl.obolibrary.org/obo/OBI_0001931", name:"obi scalar value specification", description:"A value specification that consists of two parts: a numeral and a unit label.", current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (confInterval)-[:HAS_PART {{category:"ObjectPropertyExpression", description:"a core relation that holds between a whole and its part.", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(lowerconflimit:stato_LowerConfidenceLimit_IND:NamedIndividual:Entity {{URI:"new_individual_uri7", type:"http://purl.obolibrary.org/obo/STATO_0000315", name:"stato lower confidence limit", description:"Lower confidence limit is a data item which is a lowest value bounding a confidence interval.", current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (lowerconflimit)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(lowerscalarvaluespec:obi_ScalarValueSpecification_IND:obi_ValueSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri9", type:"http://purl.obolibrary.org/obo/OBI_0001931", name:"obi scalar value specification", description:"A value specification that consists of two parts: a numeral and a unit label.", current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (lowerscalarvaluespec)-[:HAS_MEASUREMENT_UNIT_LABEL {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000039", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(lowerCountUnit:uo_CountUnit_IND:uo_DimensionlessUnit_IND:uo_Unit_IND:NamedIndividual:Entity {{URI:"new_individual_uri12", type:"http://purl.obolibrary.org/obo/UO_0000189", name:"count unit", ontology_ID:"UO", description:"A dimensionless unit which denotes a simple count of things. [MGED:MGED]", current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (upperscalarvaluespec)-[:HAS_MEASUREMENT_UNIT_LABEL {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000039", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(upperCountUnit:uo_CountUnit_IND:uo_DimensionlessUnit_IND:uo_Unit_IND:NamedIndividual:Entity {{URI:"new_individual_uri11", type:"http://purl.obolibrary.org/obo/UO_0000189", name:"count unit", ontology_ID:"UO", description:"A dimensionless unit which denotes a simple count of things. [MGED:MGED]", current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (upperscalarvaluespec)-[:HAS_MEASUREMENT_VALUE {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000004", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(upperValue:Value_IND:Literal_IND:NamedIndividual:Entity {{URI:"new_individual_uri13", type:"orkg_value_URI", name:"$_input_value2_$", description:"The value of the upper confidence limit of a basic reproduction number measurement", data_node_type:["input2"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input2", input_version_ID:0, inputVariable:2, input_info_URI:"InputInfo2UpperConfLimitR0MeasurementAssertionIND_URI", user_input:"{assertionURI}", value:"$_input_value2_$", data_type:"xsd:float"}})

    CREATE (lowerscalarvaluespec)-[:HAS_MEASUREMENT_VALUE {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000004", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(lowerValue:Value_IND:Literal_IND:NamedIndividual:Entity {{URI:"new_individual_uri14", type:"orkg_value_URI", name:"$_input_value1_$", description:"The value of the lower confidence limit of a basic reproduction number measurement", data_node_type:["input3"], current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input3", input_version_ID:0, inputVariable:3, input_info_URI:"InputInfo3LowerConfLimitR0MeasurementAssertionIND_URI", user_input:"{assertionURI}", value:"$_input_value1_$", data_type:"xsd:float"}})

    CREATE (confInterval)-[:HAS_PART {{category:"ObjectPropertyExpression", description:"a core relation that holds between a whole and its part.", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(conflevel:stato_ConfidenceLevel_IND:NamedIndividual:Entity {{URI:"new_individual_uri15", type:"http://purl.obolibrary.org/obo/STATO_0000561", name:"stato confidence level", description:"The frequency (i.e., the proportion) of possible confidence intervals that contain the true value of their corresponding parameter. In other words, if confidence intervals are constructed using a given confidence level in an infinite number of independent experiments, the proportion of those intervals that contain the true value of the parameter will match the confidence level. A probability measure of the reliability of an inferential statistical test that has been applied to sample data and which is provided along with the confidence interval for the output statistic.", current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (conflevel)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(conflevelscalarvaluespec:obi_ScalarValueSpecification_IND:obi_ValueSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri16", type:"http://purl.obolibrary.org/obo/OBI_0001931", name:"obi scalar value specification", description:"A value specification that consists of two parts: a numeral and a unit label.", current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

    CREATE (conflevelscalarvaluespec)-[:HAS_MEASUREMENT_VALUE {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000004", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(conflevelValue:Value_IND:Literal_IND:NamedIndividual:Entity {{URI:"new_individual_uri17", type:"orkg_value_URI", name:"95", description:"The value of the confidence level of a basic reproduction number measurement", current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", value:"95"}})

    CREATE (conflevelscalarvaluespec)-[:HAS_MEASUREMENT_UNIT_LABEL {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000039", entry_URI:"{entryURI}", topic_URI:"{topic_uri}", assertion_URI:"{assertionURI}"}}]->(percent:uo_Percent_IND:uo_Ratio_IND:uo_DimensionlessUnit_IND:uo_Unit_IND:NamedIndividual:Entity {{URI:"new_individual_uri18", type:"http://purl.obolibrary.org/obo/UO_0000187", name:"percent", ontology_ID:"UO", description:"A dimensionless ratio unit which denotes numbers as fractions of 100.", current_version:"true", entry_URI:"{entryURI}", topic_URI:["{topic_uri}"], assertion_URI:"{assertionURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})', edit_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "assertion_object"

    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(r0MeasurementAssertionind:orkg_BasicReproductionNumberMeasurementAssertion_IND {{URI:"{assertionURI}", current_version:"true"}}) SET r0MeasurementAssertionind.last_updated_on = localdatetime(), r0MeasurementAssertionind.assertion_label = "R0: $_input_value_$ ($_input_value1_$ - $_input_value2_$)"

    WITH parent_data_item_node, object_node, r0MeasurementAssertionind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN r0MeasurementAssertionind.contributed_by THEN [1] ELSE [] END |
    SET r0MeasurementAssertionind.contributed_by = r0MeasurementAssertionind.contributed_by + "{creator}"
    )

    WITH parent_data_item_node, object_node, r0MeasurementAssertionind
    MATCH (r0MeasurementAssertionind)-[:IS_ABOUT]->({{current_version:"true"}})-[:HAS_VALUE_SPECIFICATION]->(:obi_ScalarValueSpecification_IND {{current_version:"true"}})-[:HAS_MEASUREMENT_VALUE]->(r0Value_old:Value_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, r0MeasurementAssertionind, r0Value_old
    CALL apoc.refactor.cloneNodesWithRelationships([r0Value_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, r0MeasurementAssertionind, r0Value_old SET r0Value_old.current_version = "false"

    WITH parent_data_item_node, object_node, r0MeasurementAssertionind
    MATCH (r0MeasurementAssertionind)-[:IS_ABOUT]->({{current_version:"true"}})-[:HAS_VALUE_SPECIFICATION]->(:obi_ScalarValueSpecification_IND {{current_version:"true"}})-[:HAS_MEASUREMENT_VALUE]->(r0Value_new:Value_IND {{current_version:"true"}})
    SET r0Value_new.value = "$_input_value_$", r0Value_new.name = "$_input_value_$", r0Value_new.URI = "new_individual_uri1", r0Value_new.created_on = localdatetime(), r0Value_new.last_updated_on = localdatetime(), r0Value_new.created_by = "{creator}", r0Value_new.contributed_by = ["{creator}"]

    WITH parent_data_item_node, object_node, r0MeasurementAssertionind
    MATCH (r0MeasurementAssertionind)-[:IS_ABOUT]->({{current_version:"true"}})-[:HAS_VALUE_SPECIFICATION]->(confint:stato_ConfidenceInterval_IND {{current_version:"true"}})-[:HAS_PART]->(:stato_UpperConfidenceLimit_IND {{current_version:"true"}})-[:HAS_VALUE_SPECIFICATION]->({{current_version:"true"}})-[:HAS_MEASUREMENT_VALUE]->(upperValue_old:Value_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, confint, upperValue_old
    CALL apoc.refactor.cloneNodesWithRelationships([upperValue_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, confint, upperValue_old SET upperValue_old.current_version = "false"

    WITH parent_data_item_node, object_node, confint
    MATCH (confint)-[:HAS_PART]->(:stato_UpperConfidenceLimit_IND {{current_version:"true"}})-[:HAS_VALUE_SPECIFICATION]->({{current_version:"true"}})-[:HAS_MEASUREMENT_VALUE]->(upperValue_new:Value_IND {{current_version:"true"}})
    SET upperValue_new.value = "$_input_value2_$", upperValue_new.name = "$_input_value2_$", upperValue_new.URI = "new_individual_uri2", upperValue_new.created_on = localdatetime(), upperValue_new.last_updated_on = localdatetime(), upperValue_new.created_by = "{creator}", upperValue_new.contributed_by = ["{creator}"]

    WITH parent_data_item_node, object_node, confint
    MATCH (confint)-[:HAS_PART]->(:stato_LowerConfidenceLimit_IND {{current_version:"true"}})-[:HAS_VALUE_SPECIFICATION]->({{current_version:"true"}})-[:HAS_MEASUREMENT_VALUE]->(lowerValue_old:Value_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, confint, lowerValue_old
    CALL apoc.refactor.cloneNodesWithRelationships([lowerValue_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, confint, lowerValue_old SET lowerValue_old.current_version = "false"

    WITH parent_data_item_node, object_node, confint
    MATCH (confint)-[:HAS_PART]->(:stato_LowerConfidenceLimit_IND {{current_version:"true"}})-[:HAS_VALUE_SPECIFICATION]->({{current_version:"true"}})-[:HAS_MEASUREMENT_VALUE]->(lowerValue_new:Value_IND {{current_version:"true"}})
    SET lowerValue_new.value = "$_input_value1_$", lowerValue_new.name = "$_input_value1_$", lowerValue_new.URI = "new_individual_uri3", lowerValue_new.created_on = localdatetime(), lowerValue_new.last_updated_on = localdatetime(), lowerValue_new.created_by = "{creator}", lowerValue_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", data_item_type:"assertion"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(measurementkgbb)






    CREATE (researchTopicAssertionKGBB:orkg_ResearchTopicAssertionKGBB:AssertionKGBB:KGBB:ClassExpression:Entity {{name:"research topic assertion Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages assertions about the relation between orkg research papers and the research topics they cover.", URI:"ResearchTopicAssertionKGBB_URI", relevant_classes_URI:["http://orkg/researchtopic_1", "http://orkg???????2"], relevant_properties_URI:["http://edamontology.org/has_topic"], category:"ClassExpression", KGBB_URI:"ResearchTopicAssertionKGBB_URI", search_cypher_code:"some query", research_topic_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "assertion_object"
    WITH parent_data_item_node, object_node

    CREATE (parent_data_item_node)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", assertion_URI:"{assertionURI}"}}]->(researchTopicAssertionind:orkg_ResearchTopicAssertion_IND:orkg_Assertion_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"Research topic assertion unit", description:"This assertion models information about a particular research topic of a particular research paper.", URI:"{assertionURI}", type:"ResearchTopicAssertion_URI", object_URI:object_node.URI, entry_URI:"{entryURI}", KGBB_URI:"ResearchTopicAssertionKGBB_URI", node_type:"assertion", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", assertion_label:"$_input_name_$ [$_ontology_ID_$]"}})

    CREATE (object_node)-[:HAS_TOPIC {{category:"ObjectPropertyExpression", description:"Subject A can be any concept or entity outside of an ontology (or an ontology concept in a role of an entity being semantically annotated). Object B can either be a concept that is a Topic, or in unexpected cases an entity outside of an ontology that is a Topic or is in the role of a Topic. In EDAM, only has_topic is explicitly defined between EDAM concepts (Operation or Data has_topic Topic). The inverse, is_topic_of, is not explicitly defined. A has_topic B defines for the subject A, that it has the object B as its topic (A is in the scope of a topic B).", URI:"http://edamontology.org/has_topic", entry_URI:"{entryURI}", assertion_URI:"{assertionURI}"}}]->(researchTopicind:orkg_orkg_ResearchTopic_IND:edam_Topic_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", URI:"new_individual_uri1", entry_URI:"{entryURI}", assertion_URI:"{assertionURI}", data_node_type:"input1", type:"$_input_type_$", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchTopicAssertionIND_URI", user_input:"{assertionURI}"}})

    CREATE (researchTopicAssertionind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", assertion_URI:"{assertionURI}"}}]->(researchTopicind)', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "assertion_object"

    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(researchTopicAssertionind:orkg_ResearchTopicAssertion_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET researchTopicAssertionind.last_updated_on = localdatetime()

    WITH parent_data_item_node, object_node, researchTopicAssertionind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN researchTopicAssertionind.contributed_by THEN [1] ELSE [] END |
    SET researchTopicAssertionind.contributed_by = researchTopicAssertionind.contributed_by + "{creator}"
    )

    WITH parent_data_item_node, object_node, researchTopicAssertionind
    MATCH (researchTopicAssertionind)-[:IS_ABOUT]->(topic_old:orkg_orkg_ResearchTopic_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, researchTopicAssertionind, topic_old
    CALL apoc.refactor.cloneNodesWithRelationships([topic_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, researchTopicAssertionind, topic_old SET topic_old.current_version = "false"
    WITH researchTopicAssertionind
    MATCH (researchTopicAssertionind)-[:IS_ABOUT]->(topic_new:orkg_orkg_ResearchTopic_IND {{current_version:"true"}})
    SET topic_new.instance_label = "$_label_name_$", topic_new.URI = "new_individual_uri1", topic_new.created_on = localdatetime(), topic_new.last_updated_on = localdatetime(), topic_new.created_by = "{creator}", topic_new.contributed_by = ["{creator}"]', edit_cypher:' MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node

    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )

    WITH entry_node
    MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node

    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )

    WITH parent_data_item_node

    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "assertion_object"

    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:CONTAINS]->(researchTopicAssertionind:orkg_ResearchTopicAssertion_IND {{URI:"{assertionURI}", current_version:"true"}}) SET researchTopicAssertionind.last_updated_on = localdatetime(), researchTopicAssertionind.assertion_label = "$_input_name_$ [$_ontology_ID_$]"

    WITH parent_data_item_node, object_node, researchTopicAssertionind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN researchTopicAssertionind.contributed_by THEN [1] ELSE [] END |
    SET researchTopicAssertionind.contributed_by = researchTopicAssertionind.contributed_by + "{creator}"
    )

    WITH parent_data_item_node, object_node, researchTopicAssertionind
    MATCH (researchTopicAssertionind)-[:IS_ABOUT]->(topic_old:orkg_orkg_ResearchTopic_IND {{current_version:"true"}})

    WITH parent_data_item_node, object_node, researchTopicAssertionind, topic_old
    CALL apoc.refactor.cloneNodesWithRelationships([topic_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, researchTopicAssertionind, topic_old SET topic_old.current_version = "false"
    WITH researchTopicAssertionind
    MATCH (researchTopicAssertionind)-[:IS_ABOUT]->(topic_new:orkg_orkg_ResearchTopic_IND {{current_version:"true"}})
    SET topic_new.instance_label = "$_input_name_$", topic_new.name = "$_input_name_$", topic_new.ontology_ID = "$_ontology_ID_$", topic_new.type = "$_input_type_$", topic_new.description = "$_input_description_$", topic_new.URI = "new_individual_uri1", topic_new.created_on = localdatetime(), topic_new.last_updated_on = localdatetime(), topic_new.created_by = "{creator}", topic_new.contributed_by = ["{creator}"]', operational_KGBB:"true", data_item_type:"assertion"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(assertionKGBB)

    CREATE (researchTopicAssertionKGBB)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(researchTopicAssertion)









    //KGBB ELEMENTS
    CREATE (kgbbelement:KGBBElement:ClassExpression:Entity {{name:"Knowledge Graph Building Block element", description:"An element of a Knowledge Graph Building Block. Knowledge Graph Building Block elements are used to specify functionalities of a Knowledge Graph Building Block.", URI:"KGBBElement_URI", category:"ClassExpression"}})

    CREATE (granularityTreeElementKGBBelement:GranularityTreeElementKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Granularity tree element Knowledge Graph Building Block element", description:"A Knowledge Graph Building Block element that connects a topic to a specific type of granularity tree.", URI:"GranularityTreeElementKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)

    CREATE (assertionElementKGBBelement:AssertionElementKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Assertion element Knowledge Graph Building Block element", description:"A Knowledge Graph Building Block element that connects a topic to a specific type of assertion.", URI:"AssertionElementKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)

    CREATE (topicElementKGBBelement:TopicElementKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Topic element Knowledge Graph Building Block element", description:"A Knowledge Graph Building Block element that connects an entry to a specific type of topic.", URI:"TopicElementKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)

    CREATE (inputInfoKGBBelement:InputInfoKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Input information element", description:"A Knowledge Graph Building Block element that provides input information, i.e. information for the Knowledge Graph Building Block for how to process input from users or from the application.", URI:"InputInfoKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)

    CREATE (topicRepresentationKGBBelement:TopicRepresentationKGBBElement:RepresentationKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Topic representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data belonging to the topic in the user interface in a human-readable form using the corresponding topic Knowledge Graph Building Block.", URI:"TopicRepresentationKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)

    CREATE (entryRepresentationKGBBelement:EntryRepresentationKGBBElement:RepresentationKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Entry representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data belonging to the entry in the user interface in a human-readable form using the corresponding entry Knowledge Graph Building Block.", URI:"EntryRepresentationKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)

    CREATE (containerKGBBelement:ContainerKGBBElement:RepresentationKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Container element", description:"A Knowledge Graph Building Block element that functions as a container to organize and structure information for the front end for representing the data of the topic or assertion in the user interface in a human-readable form using the associated Knowledge Graph Building Block.", URI:"ContainerRepresentationKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)

    CREATE (exportModelKGBBelement:ExportModelKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Export model element", description:"A Knowledge Graph Building Block element that provides an export model, i.e. information for the application for exporting the data associated with this Knowledge Graph Building Block following a specific standard or data model.", URI:"ExportModelKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)

    CREATE (assertionRepresentationKGBBelement:AssertionRepresentationKGBBElement:RepresentationKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Assertion representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the associated assertion Knowledge Graph Building Block in the user interface in a human-readable form.", URI:"AssertionRepresentationKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)

    CREATE (granTreeRepresentationKGBBelement:GranularityTreeRepresentationKGBBElement:RepresentationKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Granularity tree representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the associated granularity perspective Knowledge Graph Building Block in the user interface in a human-readable form.", URI:"GranularityTreeRepresentationKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)










    // SCHOLARLY PUBLICATION KGBB RELATIONS

    CREATE (scholarlyPublicationEntrykgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(scholarlyPublicationEntry)

    CREATE (scholarlyPublicationEntrykgbb)-[:HAS_ASSERTION_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_assertion_element_URI", description:"This assertion element specifies information about the use of research topic assertions in its entry.", KGBB_URI:"ScholarlyPublicationEntryKGBB_URI", target_KGBB_URI:"ResearchTopicAssertionKGBB_URI", required:"false", quantity:"m", query_key:"research_topic_cypher_code", assertion_object_URI:"object$_$URI", input_results_in:"added_assertion"}}]->(researchTopicAssertionKGBB)

    CREATE (scholarlyPublicationEntrykgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about the research activity of a particular research paper.", topic_object_URI:"object$_$URI", KGBB_URI:"ScholarlyPublicationEntryKGBB_URI", target_KGBB_URI:"ResearchActivityTopicKGBB_URI", required:"true", input_results_in:"added_topic", quantity:"m", query_key:"storage_model_cypher_code" }}]->(ResearchActivityTopickgbb)

    CREATE (scholarlyPublicationEntrykgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(scholarlyPublicationEntryRepresentation1KGBBelement:ScholarlyPublicationEntryRepresentationKGBBElement_IND:EntryRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Scholarly publication entry representation 1 element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the scholarly publication entry in the user interface in a human-readable form using the scholarly publication entry Knowledge Graph Building Block.", data_view_name:"{data_view_name}", node_type:"entry representation", component:"scholarly_publication_entry", data_item_type_URI:"scholarly_publication_entry_URI",  link_$$$_1:"{{'name':'research_topic_assertion_input_info', 'ontology_ID':'EDAM', 'input_restricted_to_subclasses_of':'http://edamontology.org/topic_0003', 'target_KGBB_URI':'ResearchTopicAssertionKGBB_URI', 'placeholder_text':'specify the research topic', 'data_item_type':'assertion', 'edit_cypher_key':'edit_cypher', 'query_key':'research_topic_cypher_code', 'links_to_component':'research_topic_assertion', 'assertion_object_URI':'object$_$URI', 'input_results_in':'added_assertion', 'edit_results_in':'edited_assertion'}}",
    link_$$$_2:"{{'name':'research_overview_topic', 'target_KGBB_URI':'ResearchActivityTopicKGBB_URI', 'data_item_type':'topic', 'query_key':'storage_model_cypher_code', 'links_to_component':'research_activity_topic', 'topic_object_URI':'object$_$URI', 'input_results_in':'added_topic'}}", URI:"ScholarlyPublicationEntryRepresentation1KGBBElementIND_URI", type:"EntryRepresentationKGBBElement_URI", KGBB_URI:"ScholarlyPublicationEntryKGBB_URI", category:"NamedIndividual", data_view_information:"true", html:"entry.html"}})
















    // RESEARCH ACTIVITY TOPIC KGBB RELATIONS

    CREATE (ResearchActivityTopickgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(ResActTopic)

    CREATE (ResearchActivityTopickgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(researchActivityTopicRepresentation1KGBBelement:ResearchActivityTopicRepresentationKGBBElement_IND:TopicRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research activity topic representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing research activity data associated with a research paper entry in the user interface in a human-readable form using the research activity topic Knowledge Graph Building Block.", data_view_name:"{data_view_name}", node_type:"topic representation", URI:"ResearchActivityTopicRepresentation1KGBBElementIND_URI", data_item_type_URI:"ResearchActivity_topic_class_URI",  type:"TopicRepresentationKGBBElement_URI", KGBB_URI:"ResearchActivityTopicKGBB_URI", category:"NamedIndividual", data_view_information:"true", topic_html:"research_overview.html", component:"research_activity_topic", link_$$$_1:"{{'name':'research_step_topic_input_info', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/OBI_0000011', 'ontology_ID':'OBI', 'target_KGBB_URI':'ResearchActivityTopicKGBB_URI', 'data_item_type':'topic', 'topic_object_URI':'object$_$URI', 'input_results_in':'added_topic', 'edit_results_in':'edited_topic', 'links_to_component':'research_activity_topic', 'query_key':'from_activity_cypher_code', 'edit_cypher_key':'edit_cypher', 'placeholder_text':'specify the type of research activity', 'input_info_URI':'InputInfo1ResearchActivityTopicIND_URI', 'input_source':'input1', 'editable':'true'}}",
    link_$$$_2:"{{'name':'research_result_topic_input_info', 'placeholder_text':'specify the type of research result', 'ontology_ID':'IAO', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000030', 'target_KGBB_URI':'ResearchResultTopicKGBB_URI', 'data_item_type':'topic', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_topic', 'query_key':'from_activity_cypher_code', 'links_to_component':'research_result_topic', 'topic_object_URI':'object$_$URI', 'input_results_in':'added_topic'}}", link_$$$_3:"{{'name':'research_method_topic_input_info', 'placeholder_text':'specify the type of research method', 'ontology_ID':'MMO,NCIT', 'input_restricted_to_subclasses_of':'', 'target_KGBB_URI':'ResearchMethodTopicKGBB_URI', 'data_item_type':'topic', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_topic', 'query_key':'from_activity_cypher_code', 'links_to_component':'research_method_topic', 'topic_object_URI':'object$_$URI', 'input_results_in':'added_topic'}}", link_$$$_4:"{{'name':'research_objective_topic_input_info', 'placeholder_text':'specify the type of research objective', 'ontology_ID':'AGRO,IAO,ERO,OBI', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000005', 'target_KGBB_URI':'ResearchObjectiveTopicKGBB_URI', 'data_item_type':'topic', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_topic', 'query_key':'from_activity_cypher_code', 'links_to_component':'research_objective_topic', 'topic_object_URI':'object$_$URI', 'input_results_in':'added_topic'}}"}})

    CREATE (ResearchActivityTopickgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(researchActivityInputInfo1KGBBelement:ResearchActivityInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of research activity topic", description:"User input information 1 for the specification of the research activity resource for a research activity topic.", URI:"InputInfo1ResearchActivityTopicIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", input_name:"research_activity_input", node_type:"input1", KGBB_URI:"ResearchActivityTopicKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1ResearchActivityTopicIND_URI", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/OBI_0000011", ontology_ID:"OBI", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})

    CREATE (ResearchActivityTopickgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about a research activity step of a research activity.", topic_object_URI:"object$_$URI", KGBB_URI:"ResearchActivityTopicKGBB_URI", target_KGBB_URI:"ResearchActivityTopicKGBB_URI", required:"false", input_results_in:"added_topic", quantity:"m", query_key:"from_activity_cypher_code"}}]->(ResearchActivityTopickgbb)

    CREATE (ResearchActivityTopickgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about a research result of a research activity.", topic_object_URI:"object$_$URI", KGBB_URI:"ResearchActivityTopicKGBB_URI", target_KGBB_URI:"ResearchResultTopicKGBB_URI", required:"true", input_results_in:"added_topic", quantity:"m", query_key:"from_activity_cypher_code"}}]->(ResearchResultTopickgbb)

    CREATE (ResearchActivityTopickgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about a research method realized in a research activity.", topic_object_URI:"object$_$URI", KGBB_URI:"ResearchActivityTopicKGBB_URI", target_KGBB_URI:"ResearchMethodTopicKGBB_URI", required:"true", input_results_in:"added_topic", quantity:"m", query_key:"from_activity_cypher_code"}}]->(ResearchMethodTopickgbb)

    CREATE (ResearchActivityTopickgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about a research objective achieved by a research activity.", topic_object_URI:"object$_$URI", KGBB_URI:"ResearchActivityTopicKGBB_URI", target_KGBB_URI:"ResearchObjectiveTopicKGBB_URI", required:"true", input_results_in:"added_topic", quantity:"m", query_key:"from_activity_cypher_code"}}]->(ResearchObjectiveTopickgbb)











    // RESEARCH METHOD TOPIC KGBB RELATIONS

    CREATE (ResearchMethodTopickgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(ResMethTopic)

    CREATE (ResearchMethodTopickgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(researchMethodTopicRepresentation1KGBBelement:ResearchMethodTopicRepresentationKGBBElement_IND:TopicRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research method topic representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing research method data associated with a research paper entry in the user interface in a human-readable form using the research method topic Knowledge Graph Building Block.", data_view_name:"{data_view_name}", node_type:"topic representation", URI:"ResearchMethodTopicRepresentation1KGBBElementIND_URI", data_item_type_URI:"ResearchMethod_topic_class_URI",  type:"TopicRepresentationKGBBElement_URI", KGBB_URI:"ResearchMethodTopicKGBB_URI", category:"NamedIndividual", data_view_information:"true", topic_html:"research_method.html", component:"research_method_topic", link_$$$_1:"{{'name':'research_step_topic_input_info', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/OBI_0000011', 'ontology_ID':'OBI', 'target_KGBB_URI':'ResearchActivityTopicKGBB_URI', 'data_item_type':'topic', 'topic_object_URI':'object$_$URI', 'input_results_in':'added_topic', 'edit_results_in':'edited_topic', 'links_to_component':'research_activity_topic', 'query_key':'from_method_cypher_code', 'edit_cypher_key':'edit_cypher', 'placeholder_text':'specify the type of research activity', 'input_info_URI':'InputInfo1ResearchActivityTopicIND_URI', 'input_source':'input1', 'editable':'true'}}",
    link_$$$_2:"{{'name':'research_method_topic_input_info', 'placeholder_text':'specify the type of research method', 'ontology_ID':'MMO,NCIT', 'input_restricted_to_subclasses_of':'', 'target_KGBB_URI':'ResearchMethodTopicKGBB_URI', 'data_item_type':'topic', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_topic', 'query_key':'from_method_cypher_code', 'links_to_component':'research_method_topic', 'topic_object_URI':'object$_$URI', 'input_results_in':'added_topic'}}", link_$$$_3:"{{'name':'research_objective_topic_input_info', 'placeholder_text':'specify the type of research objective', 'ontology_ID':'AGRO,IAO,ERO,OBI', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000005', 'target_KGBB_URI':'ResearchObjectiveTopicKGBB_URI', 'data_item_type':'topic', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_topic', 'query_key':'from_activity_cypher_code', 'links_to_component':'research_objective_topic', 'topic_object_URI':'object$_$URI', 'input_results_in':'added_topic'}}"}})

    CREATE (ResearchMethodTopickgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(researchMethodInputInfo1KGBBelement:ResearchMethodInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of research method topic", description:"User input information 1 for the specification of the research method resource for a research method topic.", URI:"InputInfo1ResearchMethodTopicIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", input_name:"research_method_input", node_type:"input1", KGBB_URI:"ResearchMethodTopicKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1ResearchMethodTopicIND_URI", input_restricted_to_subclasses_of:"", ontology_ID:"MMO,NCIT", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})

    CREATE (ResearchMethodvkgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about a step of the research method.", topic_object_URI:"object$_$URI", KGBB_URI:"ResearchMethodTopicKGBB_URI", target_KGBB_URI:"ResearchMethodTopicKGBB_URI", required:"false", input_results_in:"added_topic", quantity:"m", query_key:"from_method_cypher_code"}}]->(ResearchMethodTopickgbb)

    CREATE (ResearchMethodTopickgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about a research activity that realizes the research method.", topic_object_URI:"object$_$URI", KGBB_URI:"ResearchMethodTopicKGBB_URI", target_KGBB_URI:"ResearchActivityTopicKGBB_URI", required:"false", input_results_in:"added_topic", quantity:"m", query_key:"from_method_cypher_code"}}]->(ResearchActivityTopickgbb)

    CREATE (ResearchMethodTopickgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about a research objective that is part of the research method.", topic_object_URI:"object$_$URI", KGBB_URI:"ResearchMethodTopicKGBB_URI", target_KGBB_URI:"ResearchObjectiveTopicKGBB_URI", required:"false", input_results_in:"added_topic", quantity:"m", query_key:"from_method_cypher_code"}}]->(ResearchObjectiveTopickgbb)










    // RESEARCH OBJECTIVE TOPIC KGBB RELATIONS

    CREATE (ResearchObjectiveTopickgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(ResObjectiveTopic)

    CREATE (ResearchObjectiveTopickgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(researchObjectiveTopicRepresentation1KGBBelement:ResearchObjectiveTopicRepresentationKGBBElement_IND:TopicRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research objective topic representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing research objective data associated with a research paper entry in the user interface in a human-readable form using the research objective topic Knowledge Graph Building Block.", data_view_name:"{data_view_name}", node_type:"topic representation", URI:"ResearchObjectiveTopicRepresentation1KGBBElementIND_URI", data_item_type_URI:"ResearchObjective_topic_class_URI",  type:"TopicRepresentationKGBBElement_URI", KGBB_URI:"ResearchObjectiveTopicKGBB_URI", category:"NamedIndividual", data_view_information:"true", topic_html:"research_objective.html", component:"research_objective_topic", link_$$$_1:"{{'name':'research_objective_topic_input_info', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000005', 'ontology_ID':'AGRO,IAO,ERO,OBI', 'target_KGBB_URI':'ResearchObjectiveTopicKGBB_URI', 'data_item_type':'topic', 'topic_object_URI':'object$_$URI', 'input_results_in':'added_topic', 'edit_results_in':'edited_topic', 'links_to_component':'research_objective_topic', 'query_key':'from_objective_cypher_code', 'edit_cypher_key':'edit_cypher', 'placeholder_text':'specify the type of research objective', 'input_info_URI':'InputInfo1ResearchObjectiveTopicIND_URI', 'input_source':'input1', 'editable':'true'}}",
    link_$$$_2:"{{'name':'research_method_topic_input_info', 'placeholder_text':'specify the type of research method', 'ontology_ID':'MMO,NCIT', 'input_restricted_to_subclasses_of':'', 'target_KGBB_URI':'ResearchMethodTopicKGBB_URI', 'data_item_type':'topic', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_topic', 'query_key':'from_objective_cypher_code', 'links_to_component':'research_method_topic', 'topic_object_URI':'object$_$URI', 'input_results_in':'added_topic'}}", link_$$$_3:"{{'name':'research_step_topic_input_info', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/OBI_0000011', 'ontology_ID':'OBI', 'target_KGBB_URI':'ResearchActivityTopicKGBB_URI', 'data_item_type':'topic', 'topic_object_URI':'object$_$URI', 'input_results_in':'added_topic', 'edit_results_in':'edited_topic', 'links_to_component':'research_activity_topic', 'query_key':'from_objective_cypher_code', 'edit_cypher_key':'edit_cypher', 'placeholder_text':'specify the type of research activity', 'input_info_URI':'InputInfo1ResearchActivityTopicIND_URI', 'input_source':'input1', 'editable':'true'}}", link_$$$_4:"{{'name':'research_result_topic_input_info', 'placeholder_text':'specify the type of research result', 'ontology_ID':'IAO', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000030', 'target_KGBB_URI':'ResearchResultTopicKGBB_URI', 'data_item_type':'topic', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_topic', 'query_key':'from_objective_cypher_code', 'links_to_component':'research_result_topic', 'topic_object_URI':'object$_$URI', 'input_results_in':'added_topic'}}"}})

    CREATE (ResearchObjectiveTopickgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(researchObjectiveInputInfo1KGBBelement:ResearchObjectiveInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of research objective topic", description:"User input information 1 for the specification of the research objective resource for a research objective topic.", URI:"InputInfo1ResearchObjectiveTopicIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", input_name:"research_objective_input", node_type:"input1", KGBB_URI:"ResearchObjectiveTopicKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1ResearchObjectiveTopicIND_URI", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/IAO_0000005", ontology_ID:"AGRO,IAO,ERO,OBI", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})

    CREATE (ResearchObjectiveTopickgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about a the research method this research objective is a part of.", topic_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveTopicKGBB_URI", target_KGBB_URI:"ResearchMethodTopicKGBB_URI", required:"false", input_results_in:"added_topic", quantity:"m", query_key:"from_objective_cypher_code"}}]->(ResearchMethodTopickgbb)

    CREATE (ResearchObjectiveTopickgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about a research activity that achieves the research objective.", topic_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveTopicKGBB_URI", target_KGBB_URI:"ResearchActivityTopicKGBB_URI", required:"false", input_results_in:"added_topic", quantity:"m", query_key:"from_objective_cypher_code"}}]->(ResearchActivityTopickgbb)

    CREATE (ResearchObjectiveTopickgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about a research result that achieves the research objective.", topic_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveTopicKGBB_URI", target_KGBB_URI:"ResearchResultTopicKGBB_URI", required:"false", input_results_in:"added_topic", quantity:"m", query_key:"from_objective_cypher_code"}}]->(ResearchResultTopickgbb)

    CREATE (ResearchObjectiveTopickgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about a research objective that is a part of this research objective.", topic_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveTopicKGBB_URI", target_KGBB_URI:"ResearchObjectiveTopicKGBB_URI", required:"false", input_results_in:"added_topic", quantity:"m", query_key:"from_objective_cypher_code"}}]->(ResearchObjectiveTopickgbb)













    // RESEARCH RESULT TOPIC KGBB RELATIONS

    CREATE (ResearchResultTopickgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(ResResTopic)

    CREATE (ResearchResultTopickgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(researchResultTopicRepresentation1KGBBelement:ResearchResultTopicRepresentationKGBBElement_IND:TopicRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research result topic representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing research result data associated with a research paper entry in the user interface in a human-readable form using the research result topic Knowledge Graph Building Block.", data_item_type_URI:"ResearchResult_topic_class_URI", data_view_name:"{data_view_name}", node_type:"topic representation", URI:"ResearchResultTopicRepresentation1KGBBElementIND_URI", type:"TopicRepresentationKGBBElement_URI", KGBB_URI:"ResearchResultTopicKGBB_URI", category:"NamedIndividual", data_view_information:"true", topic_html:"research_result_topic.html",  component:"research_result_topic", link_$$$_1:"{{'name':'research_activity_topic_input_info', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/OBI_0000011', 'ontology_ID':'OBI', 'edit_results_in':'edited_topic', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'ResearchActivityTopicKGBB_URI', 'data_item_type':'topic', 'topic_object_URI':'object$_$URI', 'input_results_in':'added_topic', 'links_to_component':'research_activity_topic', 'query_key':'from_result_cypher_code', 'placeholder_text':'specify the type of research activity', 'editable':'true'}}",
    link_$$$_2:"{{'name':'research_result_topic_input_info', 'placeholder_text':'specify the type of research result', 'ontology_ID':'IAO', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000030', 'target_KGBB_URI':'ResearchResultTopicKGBB_URI', 'input_info_URI':'InputInfo1ResearchResultTopicIND_URI', 'data_item_type':'topic', 'edit_results_in':'edited_topic', 'edit_cypher_key':'edit_cypher', 'query_key':'from_results_cypher_code', 'links_to_component':'research_result_topic', 'topic_object_URI':'object$_$URI', 'input_source':'input1', 'input_results_in':'added_topic'}}", link_$$$_3:"{{'name':'material_entity_topic_input_info', 'placeholder_text':'specify the type of material entity', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/BFO_0000040', 'edit_results_in':'edited_topic', 'edit_cypher_key':'edit_cypher', 'ontology_ID':'UBERON,OBI,IDO', 'target_KGBB_URI':'MaterialEntityTopicKGBB_URI', 'data_item_type':'topic', 'query_key':'from_result_cypher_code', 'links_to_component':'material_entity_topic', 'topic_object_URI':'object$_$URI', 'input_results_in':'added_topic'}}", link_$$$_4:"{{'name':'research_objective_topic_input_info', 'placeholder_text':'specify the type of research objective', 'ontology_ID':'AGRO,IAO,ERO,OBI', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000005', 'target_KGBB_URI':'ResearchObjectiveTopicKGBB_URI', 'data_item_type':'topic', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_topic', 'query_key':'from_activity_cypher_code', 'links_to_component':'research_objective_topic', 'topic_object_URI':'object$_$URI', 'input_results_in':'added_topic'}}"}})

    CREATE (ResearchResultTopickgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about a research result documented in a particular research paper.", topic_object_URI:"object$_$URI", KGBB_URI:"ResearchResultTopicKGBB_URI", data_view_name:"{data_view_name}", target_KGBB_URI:"ResearchResultTopicKGBB_URI", required:"false", quantity:"m", query_key:"from_results_cypher_code", input_results_in:"added_topic"}}]->(ResearchResultTopickgbb)

    CREATE (ResearchResultTopickgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about a research activity step of a research activity.", topic_object_URI:"object$_$URI", KGBB_URI:"ResearchResultTopicKGBB_URI", target_KGBB_URI:"ResearchActivityTopicKGBB_URI", required:"false", input_results_in:"added_topic", quantity:"m", query_key:"from_activity_cypher_code"}}]->(ResearchActivityTopickgbb)

    CREATE (ResearchResultTopickgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about a particular material entity as it is documented in a particular research paper.", topic_object_URI:"object$_$URI",KGBB_URI:"ResearchResultTopicKGBB_URI", data_view_name:"{data_view_name}", target_KGBB_URI:"MaterialEntityTopicKGBB_URI", required:"false", quantity:"m", query_key:"from_result_cypher_code", input_results_in:"added_topic"
    }}]->(materialEntityTopickgbb)

    CREATE (ResearchResultTopickgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about a research objective that is part of the research method.", topic_object_URI:"object$_$URI", KGBB_URI:"ResearchResultTopicKGBB_URI", target_KGBB_URI:"ResearchObjectiveTopicKGBB_URI", required:"false", input_results_in:"added_topic", quantity:"m", query_key:"from_result_cypher_code"}}]->(ResearchObjectiveTopickgbb)

    CREATE (ResearchResultTopickgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(researchResultInputInfo1KGBBelement:ResearchResultInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of research result topic", input_name:"research_result_input", description:"User input information 1 for the specification of the research result resource for a research result topic.", placeholder_text:"specify the type of research result", URI:"InputInfo1ResearchResultTopicIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"ResearchResultTopicKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1ResearchResultTopicIND_URI", ontology_ID:"IAO", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/IAO_0000030", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})


















    // MATERIAL ENTITY TOPIC KGBB RELATIONS

    CREATE (materialEntityTopickgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(materialEntityTopicRepresentation1KGBBelement:MaterialEntityTopicRepresentationKGBBElement_IND:TopicRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Material entity topic representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing data about a particular material entity from a research paper entry in the user interface in a human-readable form using the material entity topic Knowledge Graph Building Block.", data_view_name:"{data_view_name}", node_type:"topic representation", URI:"MaterialEntityTopicRepresentation1KGBBElementIND_URI", type:"TopicRepresentationKGBBElement_URI", data_item_type_URI:"material_entity_topic_URI",  KGBB_URI:"MaterialEntityTopicKGBB_URI", topic_html:"material_entity_topic.html", category:"NamedIndividual", data_view_information:"true", component:"material_entity_topic", link_$$$_1:"{{'name':'material_entity_topic_input_info', 'placeholder_text':'specify the type of material entity', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/BFO_0000040', 'ontology_ID':'UBERON,OBI,IDO', 'target_KGBB_URI':'MaterialEntityTopicKGBB_URI', 'data_item_type':'topic', 'edit_results_in':'edited_topic', 'edit_cypher_key':'edit_cypher', 'query_key':'from_material_entity_cypher_code', 'links_to_component':'material_entity_topic', 'topic_object_URI':'object$_$URI', 'input_results_in':'added_topic'}}", link_$$$_2:"{{'name':'quality_relation_identification_assertion_input_info', 'placeholder_text':'select a quality', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/BFO_0000019', 'ontology_ID':'PATO,OMIT', 'edit_results_in':'edited_assertion', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'QualityIdentificationAssertionKGBB_URI', 'data_item_type':'assertion', 'query_key':'quality_cypher_code', 'links_to_component':'quality_identification_assertion', 'assertion_object_URI':'object$_$URI', 'input_results_in':'added_assertion', 'edit_results_in':'edited_assertion'}}", link_$$$_3:"{{'name':'material_entity_parthood_granularity_tree_info', 'target_KGBB_URI':'MatEntparthoodgranperspectiveKGBB', 'data_item_type':'granularity_tree', 'links_to_component':'material_entity_parthood_granularity_tree', 'granularity_tree_object_URI':'object$_$URI'}}"}})

    CREATE (materialEntityTopickgbb)-[:HAS_TOPIC_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_topic_element_URI", description:"This topic element specifies information about a particular material entity as it is documented in a particular research paper.", topic_object_URI:"object$_$URI", KGBB_URI:"MaterialEntityTopicKGBB_URI", target_KGBB_URI:"MaterialEntityTopicKGBB_URI", required:"false", quantity:"m", query_key:"from_material_entity_cypher_code", input_results_in:"added_topic"}}]->(materialEntityTopickgbb)

    CREATE (materialEntityTopickgbb)-[:HAS_ASSERTION_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_assertion_element_URI", description:"This assertion element specifies information about the use of quality relation identification assertions in its topic.", KGBB_URI:"MaterialEntityTopicKGBB_URI", target_KGBB_URI:"QualityIdentificationAssertionKGBB_URI", required:"false", quantity:"m", query_key:"quality_cypher_code", assertion_object_URI:"object$_$URI", input_results_in:"added_assertion"}}]->(qualitykgbb)

    CREATE (materialEntityTopickgbb)-[:HAS_GRANULARITY_TREE_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_granularity_tree_element_URI", description:"This granularity tree element specifies information about the existence and composition of a parthood-based granularity tree of particular material entities.", KGBB_URI:"MaterialEntityTopicKGBB_URI", target_KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", required:"false", quantity:"m", granularity_tree_object_URI:"object$_$URI"}}]->(MatEntparthoodgranperspectiveKGBB)

    CREATE (materialEntityTopickgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(materialEntityInputInfo1KGBBelement:MaterialEntityInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of material entity topic", input_name:"material_entity_input", description:"User input information 1 for the specification of the material entity resource for a material entity topic.", placeholder_text:"specify the type of material entity", URI:"InputInfo1MaterialEntityTopicIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"MaterialEntityTopicKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1MaterialEntityTopicIND_URI", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/BFO_0000040", ontology_ID:"UBERON,OBI,IDO", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})

















    // QUALITY ASSERTION KGBB RELATIONS

    CREATE (qualitykgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(qualityAssertionRepresentation1KGBBelement:QualityIdentificationAssertionRepresentationKGBBElement_IND:AssertionRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Quality relation identification assertion representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the identification of a quality relation in the user interface in a human-readable form using the quality relation identification assertion Knowledge Graph Building Block.", URI:"QualityAssertionRepresentation1KGBBElementIND_URI", data_view_name:"{data_view_name}", node_type:"assertion representation", data_item_type_URI:"Quality_Identification_Assertion_URI", KGBB_URI:"QualityIdentificationAssertionKGBB_URI", category:"NamedIndividual", data_view_information:"true", component:"quality_relation_identification_assertion", link_$$$_1:"{{'name':'quality_assertion_relation_identification_input_info', 'component':'quality_relation_identification_assertion', 'input_info_URI':'InputInfo1QualityAssertionIND_URI', 'placeholder_text':'select a type of quality', 'input_source':'input1', 'editable':'true', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/BFO_0000019', 'ontology_ID':'PATO,OMIT', 'edit_results_in':'edited_assertion', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'QualityIdentificationAssertionKGBB_URI', 'assertion_object_URI':'object$_$URI', 'data_item_type':'assertion', 'query_key':'quality_cypher_code', 'input_results_in':'added_assertion'}}", link_$$$_2:"{{'name':'weight_measurement_assertion_input_info', 'placeholder_text_1':'value', 'user_input_data_type':'xsd:float',
     'edit_results_in':'edited_assertion', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'WeightMeasurementAssertionKGBB_URI', 'data_item_type':'assertion', 'query_key':'weight_measurement_cypher_code', 'links_to_component':'weight_measurement_assertion', 'assertion_object_URI':'object$_$URI', 'input_results_in':'added_assertion', 'edit_results_in':'edited_assertion', 'placeholder_text_2':'select a gram-based unit', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/UO_1000021', 'ontology_ID':'UO'}}", link_$$$_3:"{{'name':'R0_measurement_assertion_input_info', 'placeholder_text_1':'value', 'placeholder_text_3':'upper limit', 'placeholder_text_2':'lower limit', 'user_input_data_type':'xsd:float', 'edit_results_in':'edited_assertion', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'R0MeasurementAssertionKGBB_URI', 'data_item_type':'assertion', 'query_key':'r0_measurement_cypher_code', 'links_to_component':'R0_measurement_assertion', 'assertion_object_URI':'object$_$URI', 'input_results_in':'added_assertion', 'edit_results_in':'edited_assertion'}}"}})

    CREATE (qualitykgbb)-[:HAS_EXPORT_MODEL {{category:"ObjectPropertyExpression", URI:"orkg_has_export_model_URI"}}]->(qualityexportModel1KGBBelement:ExportModelKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Quality relation identification assertion export model 1", description:"A Knowledge Graph Building Block element that provides an export model for identified quality relations. The export model 1 is based on the OBO/OBI data model.", URI:"QualityExportModel1KGBBElementIND_URI", type:"ExportModelKGBBElement_URI", KGBB_URI:"QualityIdentificationAssertionKGBB_URI", export_scheme:"OBO", category:"NamedIndividual", export_model_cypher_code:"cypherQuery"}})

    CREATE (qualitykgbb)-[:HAS_EXPORT_MODEL {{category:"ObjectPropertyExpression", URI:"orkg_has_export_model_URI"}}]->(exportModel2KGBBelement:ExportModelKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Quality relation identification assertion export model 2", description:"A Knowledge Graph Building Block element that provides an export model for identified quality relations. The export model 2 is based on the OBOE ontology data model.", URI:"QualityExportModel2KGBBElementIND_URI", type:"ExportModelKGBBElement_URI", KGBB_URI:"QualityIdentificationAssertionKGBB_URI", export_scheme:"OBOE", category:"NamedIndividual", export_model_cypher_code:"cypherQuery"}})

    CREATE (qualitykgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(qualityInputInfo1KGBBelement:QualityInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of quality relation identification assertion", description:"User input information 1 for the specification of the quality resource for a quality relation identification assertion.", input_name:"quality_identification_input", placeholder_text:"select a type of quality", URI:"InputInfo1QualityAssertionIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"QualityIdentificationAssertionKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1QualityAssertionIND_URI", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/BFO_0000019", ontology_ID:"PATO,OMIT", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})

    CREATE (qualitykgbb)-[:HAS_ASSERTION_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_assertion_element_URI", description:"This assertion element specifies information about the use of weight measurement assertions in its assertion.", KGBB_URI:"QualityIdentificationAssertionKGBB_URI", target_KGBB_URI:"WeightMeasurementAssertionKGBB_URI", required:"false", quantity:"m", query_key:"weight_measurement_cypher_code", input_results_in:"added_assertion"}}]->(weightkgbb)

    CREATE (qualitykgbb)-[:HAS_ASSERTION_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_assertion_element_URI", description:"This assertion element specifies information about the use of basic reproduction number measurement assertions in its assertion.", KGBB_URI:"QualityIdentificationAssertionKGBB_URI", target_KGBB_URI:"R0MeasurementAssertionKGBB_URI", required:"false", quantity:"m", query_key:"r0_measurement_cypher_code", input_results_in:"added_assertion"}}]->(R0Measurementkgbb)











    // WEIGHT MEASUREMENT ASSERTION KGBB

    CREATE (weightkgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(weightMeasAssertionRepresentation1KGBBelement:WeightMeasurementAssertionRepresentationKGBBElement_IND:AssertionRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Weight measurement assertion representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the weight measurement assertion in the user interface in a human-readable form using the weight measurement assertion Knowledge Graph Building Block.", URI:"WeightMeasurementAssertionRepresentation1KGBBElementIND_URI", data_view_name:"{data_view_name}", node_type:"assertion representation", data_item_type_URI:"weight_measurement_assertion_URI", KGBB_URI:"WeightMeasurementAssertionKGBB_URI", category:"NamedIndividual", data_view_information:"true", component:"weight_measurement_assertion", link_$$$_1:"{{'name':'weight_measurement_assertion_input_info', 'placeholder_text_1':'value', 'user_input_data_type':'xsd:float', 'edit_results_in':'edited_assertion', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'WeightMeasurementAssertionKGBB_URI', 'data_item_type':'assertion', 'query_key':'weight_measurement_cypher_code', 'links_to_component':'weight_measurement_assertion', 'assertion_object_URI':'object$_$URI', 'input_results_in':'added_assertion', 'edit_results_in':'edited_assertion', 'placeholder_text_2':'select a gram-based unit', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/UO_1000021', 'ontology_ID':'UO'}}"}})

    CREATE (weightkgbb)-[:HAS_EXPORT_MODEL {{category:"ObjectPropertyExpression", URI:"orkg_has_export_model_URI"}}]->(weightMeasurementexportModel1KGBBelement:ExportModelKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Weight measurement assertion export model 1", description:"A Knowledge Graph Building Block element that provides an export model for weight measurements. The export model 1 is based on the OBO/OBI data model.", URI:"WeightMeasurementExportModel1KGBBElementIND_URI", type:"ExportModelKGBBElement_URI", KGBB_URI:"WeightMeasurementAssertionKGBB_URI", export_scheme:"OBO", category:"NamedIndividual", export_model_cypher_code:"cypherQuery"}})

    CREATE (weightkgbb)-[:HAS_EXPORT_MODEL {{category:"ObjectPropertyExpression", URI:"orkg_has_export_model_URI"}}]->(weightMeasurementexportModel2KGBBelement:ExportModelKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Weight measurement assertion export model 2", description:"A Knowledge Graph Building Block element that provides an export model for weight measurements. The export model 2 is based on the OBOE ontology data model.", URI:"WeightMeasurementExportModel2KGBBElementIND_URI", type:"ExportModelKGBBElement_URI", KGBB_URI:"WeightMeasurementAssertionKGBB_URI", export_scheme:"OBOE", category:"NamedIndividual", export_model_cypher_code:"cypherQuery"}})

    CREATE (weightkgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(weightMeasurementAssertion)

    CREATE (weightkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(weightMeasurementInputInfo1KGBBelement:WeightMeasurementInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of weight measurement assertion", description:"User input information 1 for the specification of the weight measurement value for a weight measurement assertion.", placeholder_text:"value", input_name:"weight_value_input", URI:"InputInfo1WeightMeasurementAssertionIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"WeightMeasurementAssertionKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1WeightMeasurementAssertionIND_URI", user_input_data_type:"xsd:float", data_view_information:"true", input_target_property:["value"]}})

    CREATE (weightkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(weightMeasurementInputInfo2KGBBelement:WeightMeasurementInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 2 element of weight measurement assertion", description:"User input information 2 for the specification of the weight measurement unit resource for a weight measurement assertion.", input_name:"weight_unit_input", placeholder_text:"select a gram-based unit", URI:"InputInfo2WeightMeasurementAssertionIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input2", KGBB_URI:"WeightMeasurementAssertionKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo2WeightMeasurementAssertionIND_URI", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/UO_1000021", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})












    // R0 MEASUREMENT ASSERTION KGBB

    CREATE (R0Measurementkgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(R0MeasAssertionRepresentation1KGBBelement:BasicReproductionNumberMeasurementAssertionRepresentationKGBBElement_IND:AssertionRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Basic reproduction number measurement assertion representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the basic reproduction number measurement assertion in the user interface in a human-readable form using the basic reproduction number measurement assertion Knowledge Graph Building Block.", URI:"R0MeasurementAssertionRepresentation1KGBBElementIND_URI", data_view_name:"{data_view_name}", node_type:"assertion representation", data_item_type_URI:"r0_measurement_assertion_URI", KGBB_URI:"R0MeasurementAssertionKGBB_URI", category:"NamedIndividual", data_view_information:"true", component:"R0_measurement_assertion", link_$$$_1:"{{'name':'R0_measurement_assertion_input_info', 'placeholder_text_1':'value', 'placeholder_text_3':'upper limit', 'placeholder_text_2':'lower limit', 'user_input_data_type':'xsd:float', 'edit_results_in':'edited_assertion', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'R0MeasurementAssertionKGBB_URI', 'data_item_type':'assertion', 'query_key':'r0_measurement_cypher_code', 'links_to_component':'R0_measurement_assertion', 'assertion_object_URI':'object$_$URI', 'input_results_in':'added_assertion', 'edit_results_in':'edited_assertion'}}"}})

    CREATE (R0Measurementkgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(r0MeasurementAssertion)

    CREATE (R0Measurementkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(R0MeasurementInputInfo1KGBBelement:R0MeasurementInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of R0 measurement assertion", description:"User input information 1 for the specification of the R0 measurement value for a basic reproduction number measurement assertion.", placeholder_text:"value", input_name:"R0_value_input", URI:"InputInfo1R0MeasurementAssertionIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"R0MeasurementAssertionKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1R0MeasurementAssertionIND_URI", user_input_data_type:"xsd:float", data_view_information:"true", input_target_property:["value"]}})

    CREATE (R0Measurementkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(R0UpperConfLimitMeasurementInputInfo1KGBBelement:R0UpperConfidenceLimitMeasurementInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 2 element of upper confidence limit for R0 measurement assertion", description:"User input information 2 for the specification of the upper confidence limit value for an R0 measurement for a basic reproduction number measurement assertion.", placeholder_text:"upper limit", input_name:"upper_confidence_limit_value_input", URI:"InputInfo2UpperConfLimitR0MeasurementAssertionIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input2", KGBB_URI:"R0MeasurementAssertionKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo2UpperConfLimitR0MeasurementAssertionIND_URI", user_input_data_type:"xsd:float", data_view_information:"true", input_target_property:["value"]}})

    CREATE (R0Measurementkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(R0LowerConfLimitMeasurementInputInfo1KGBBelement:R0LowerConfidenceLimitMeasurementInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 3 element of lower confidence limit for R0 measurement assertion", description:"User input information 3 for the specification of the lower confidence limit value for an R0 measurement for a basic reproduction number measurement assertion.", placeholder_text:"lower limit", input_name:"lower_confidence_limit_value_input", URI:"InputInfo3LowerConfLimitR0MeasurementAssertionIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input3", KGBB_URI:"R0MeasurementAssertionKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo3LowerConfLimitR0MeasurementAssertionIND_URI", user_input_data_type:"xsd:float", data_view_information:"true", input_target_property:["value"]}})



















    // RESEARCH TOPIC KGBB RELATIONS

    CREATE (researchTopicAssertionKGBB)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(researchTopicInputInfo1KGBBelement:ResearchTopicInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"research_topic_input", description:"User input information 1 for the specification of the research topic resource for a research topic assertion.", input_name:"research_topic_input", URI:"InputInfo1ResearchTopicAssertionIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"ResearchTopicAssertionKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1ResearchTopicAssertionIND_URI", input_restricted_to_subclasses_of:"http://edamontology.org/topic_0003", ontology_ID:"EDAM", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})

    CREATE (researchTopicAssertionKGBB)-[:HAS_EXPORT_MODEL {{category:"ObjectPropertyExpression", URI:"orkg_has_export_model_URI"}}]->(researchtopicexportModel1KGBBelement:ExportModelKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research topic assertion export model 1", description:"A Knowledge Graph Building Block element that provides an export model for research topic relations. The export model 1 is based on the XXX data model.", URI:"ResearchTopicExportModel1KGBBElementIND_URI", export_scheme:"OBO", type:"ExportModelKGBBElement_URI", KGBB_URI:"ResearchTopicAssertionKGBB_URI", category:"NamedIndividual", export_model_cypher_code:"cypherQuery"}})

    CREATE (researchTopicAssertionKGBB)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(researchTopicAssertionRepresentation1KGBBelement:ResearchTopicAssertionRepresentationKGBBElement_IND:AssertionRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research topic assertion representation 1 element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the research topic assertion in the user interface in a human-readable form using the research topic assertion Knowledge Graph Building Block.", data_view_name:"{data_view_name}", URI:"ResearchTopicRepresentation1KGBBElementIND_URI", type:"AssertionRepresentationKGBBElement_URI", component:"research_topic_assertion", data_item_type_URI:"ResearchTopicAssertion_URI", node_type:"assertion_representation", KGBB_URI:"ResearchTopicAssertionKGBB_URI", data_view_information:"true", category:"NamedIndividual", link_$$$_1:"{{'name':'research_topic_input', 'component':'research_topic_assertion', 'input_info_URI':'InputInfo1ResearchTopicAssertionIND_URI', 'placeholder_text':'specify the research topic', 'input_source':'input1', 'editable':'true'}}"}})






    // CONFIDENCE LEVEL ASSERTION KGBB

    CREATE (confidenceLevelAssertionKGBB)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(confidenceLevelAssertion)

    CREATE (confidenceLevelAssertionKGBB)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(confidenceLevelAssertionKGBBelement:ConfidenceLevelAssertionRepresentationKGBBElement_IND:AssertionRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Confidence level specification assertion representation 1 element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the confidence level specification assertion in the user interface in a human-readable form using the confidence level specification assertion Knowledge Graph Building Block.", data_view_name:"{data_view_name}", URI:"ConfLevelSpecAssertionRepresentation1KGBBElementIND_URI", type:"AssertionRepresentationKGBBElement_URI", data_item_type_URI:"ConfidenceLevelAssertion_URI", node_type:"assertion_representation", KGBB_URI:"ConfidenceLevelAssertionKGBB_URI", data_view_information:"true", category:"NamedIndividual", topic_html:"", component:"confidence_level_assertion"}})












    // MATERIAL ENTITY PARTHOOD GRANULARITY PERSPECTIVE KGBB RELATIONS

    CREATE (MatEntparthoodgranperspectiveKGBB)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(MatEntParthoodGranTree)

    CREATE (MatEntparthoodgranperspectiveKGBB)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(materialEntityParthoodGranularityTreeRepresentation1KGBBelement:MaterialEntityParthoodGranularityTreeRepresentationKGBBElement_IND:GranularityTreeRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Material entity parthood granularity tree representation 1 element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the parthood-based granularity tree of material entities in the user interface in a human-readable form using the material entity parthood granularity perspective Knowledge Graph Building Block.", data_view_name:"{data_view_name}", URI:"MatEntParthoodGranTreeRepresentation1KGBBElementIND_URI", type:"GranularityTreeRepresentationKGBBElement_URI", data_item_type_URI:"MatEnt_Parthood_based_Granularity_tree_URI", node_type:"granularity_tree_representation", KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", data_view_information:"true", category:"NamedIndividual", topic_html:"granularity_tree.html", component:"material_entity_parthood_granularity_tree"}})


    '''.format(creator = 'ORKGuserORCID', createdWith = 'ORKG', entryURI = 'entry_URIX', topic_uri = 'topic_URIX', assertionURI = 'assertion_URIX', doiEntry = 'Entry_DOI', data_view_name = 'ORKG')

get_entry_data_query_string = '''MATCH (n {{URI:"{entry_URI}"}}) RETURN count(n);'''.format(entry_URI="URI")





@app.route("/")

def index():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name


    result = connection.query(check_empty_query_string, db='neo4j')
    x = result[0].get("count(n)")

    entry_check = connection.query(check_entry_query_string, db='neo4j')
    y = entry_check[0].get("count(n)")



    if x == 0 and y == 0:
        print("none")
        flash('No graph. Please initiate graph!', 'error')
        return render_template("lobby_form.html", initiated="False")

    elif x != 0 and y == 0:
        print("graph but no entries")
        flash('Graph but no entries. Please add entry!', 'good')
        return render_template("lobby_form.html", pubEntry="False", initiated="True")

    else:
        print("something")
        flash('Graph with ' + str(y) + ' entry', 'good')
        return render_template("lobby_form.html", pubEntry="True",initiated="True")

    return render_template("lobby_form.html", pubEntry="True",initiated="True")








@app.route("/entry_list", methods=['POST', 'GET'])
# list all entries in the graph
def entry_list():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name



    if request.method == "POST":

        entry_uri = request.form['entry_uri']
        print("----------------------NEW ENTRY URI------------------------")
        print(entry_uri)

        entry_data = EntryRepresentation(entry_uri)

        return render_template("/entry.html", entry_uri=entry_uri, topic_data=topic_data, entry_name=entry_data.entry_label, topic_types_count=topic_types_count, topic_kgbb_uri=topic_kgbb_uri)

    else:
        return render_template("entry.html", topic_data=topic_data, entry_name=entry_data.entry_label, topic_types_count=topic_types_count)









@app.route("/certainty", methods=['POST', 'GET'])
# certainty information for an assertion provided by a user

def certainty():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name

    if request.method == "POST":

        if request.form:

            try:
                assertion_uri = request.form['input_name']
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print("++++++++++++++++++ ASSERTION URI +++++++++++++++++++++")
                print(assertion_uri)

            except:
                pass

            try:
                certainty = request.form[assertion_uri + '_certainty']
                print("-------------------------- CERTAINTY -----------------------------")
                print(certainty)
            except:
                certainty = None


            try:
                topic_uri = request.form[assertion_uri + '_topic_uri']
                print("-------------------------- TOPIC URI ------------------------------")
                print(topic_uri)
            except:
                topic_uri = None


            try:
                entry_uri = request.form[assertion_uri + '_entry_uri']
                print("-------------------------- ENTRY URI -----------------------------")
                print(entry_uri)
            except:
                entry_uri = None

            try:
                parent_uri = request.form[assertion_uri + '_parent_uri']
                print("-------------------------- PARENT URI ----------------------------")
                print(parent_uri)
            except:
                parent_uri = None

            try:
                parent_item_type = request.form[assertion_uri + '_parent_type']
                print("-------------------------- PARENT TYPE ---------------------------")
                print(parent_item_type)
            except:
                parent_item_type = None


            if certainty == "certain":
                label = ":ncit_certain_IND:ncit_generalQualifier_IND:ncit_qualifier_IND"
                name = "certain"
                type = "http://purl.obolibrary.org/obo/NCIT_C107561"
                description = "Having no doubts; definitely true. [ NCI ] "
                ontology_ID = "NCIT"

            elif certainty == "likely":
                label = ":ncit_likely_IND:ncit_generalQualifier_IND:ncit_qualifier_IND"
                name = "likely"
                type = "http://purl.obolibrary.org/obo/NCIT_C85550"
                description = "Having a good chance of being the case or of coming about. [ NCI ] "
                ontology_ID = "NCIT"

            elif certainty == "uncertain":
                label = ":ncit_uncertain_IND:ncit_generalQualifier_IND:ncit_qualifier_IND"
                name = "uncertain"
                type = "http://purl.obolibrary.org/obo/NCIT_C47944"
                description = "Not established beyond doubt; still undecided or unknown. [ NCI ] "
                ontology_ID = "NCIT"

            if certainty != "not specified":
                # specify uuid for certainty_uri
                certainty_uri = str(uuid.uuid4())
                certainty_assertion_uri = str(uuid.uuid4())

                # cypher query to specify or update the confidence level of the assertion
                assertion_confidence_query_string = '''MATCH (assertion {{URI:"{assertion_uri}"}})
                WITH assertion
                OPTIONAL MATCH (assertion)-[:ASSERTION_CONFIDENCE_LEVEL]->(confidence {{current_version:"true"}})
                OPTIONAL MATCH (assertion)-[:CONTAINS]->(certaintyAssertion:orkg_CertaintyAssertion {{current_version:"true"}})
                WITH assertion, confidence, certaintyAssertion

                FOREACH (i IN CASE WHEN confidence IS NULL THEN [1] ELSE [] END |

                CREATE (assertion)-[:ASSERTION_CONFIDENCE_LEVEL {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/SEPIO_0000167", entry_URI:"{entry_uri}", topic_URI:"{topic_uri}", assertion_URI:"{assertion_uri}", description:"A relation between an assertion and a value that indicates the degree of confidence that the Proposition it puts forth is true."}}]->(certainty{label}:NamedIndividual:Entity {{URI:"{certainty_uri}", type:"{type}", name:"{name}", ontology_ID:"{ontology_ID}", description:"{description}", current_version:"true", entry_URI:"{entry_uri}", topic_URI:"{topic_uri}", assertion_URI:"{assertion_uri}", created_on:localdatetime(), last_updated_on:localdatetime(), contributed_by:["{creator}"], created_by:"{creator}", created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})

                CREATE (assertion)-[:CONTAINS {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entry_uri}", topic_URI:"{topic_uri}", assertion_URI:"{assertion_uri}"}}]->(confidenceLevelAssertion_ind:orkg_ConfidenceLevelAssertion_IND:orkg_Assertion_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"Confidence level specification assertion", URI:"{certainty_assertion_uri}", description:"This assertion models the specification of the confidence level for a given assertion, topic, or entry in the orkg. As such, it is a statement about a statement or a collection of statements.", type:"ConfidenceLevelAssertion_URI", object_URI:"{certainty_uri}", entry_URI:"{entry_uri}", topic_URI:"{topic_uri}", KGBB_URI:"ConfidenceLevelAssertionKGBB_URI", node_type:"assertion", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", assertion_label:"{name} [{ontology_ID}]"}})

                CREATE (confidenceLevelAssertion_ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entry_uri}", topic_URI:"{topic_uri}", assertion_URI:"{assertion_uri}"}}]->(certainty)
                )

                WITH assertion, confidence, certaintyAssertion

                FOREACH (i IN CASE WHEN confidence IS NOT NULL THEN [1] ELSE [] END |

                SET confidence.name="{name}"
                SET confidence.type="{type}"
                SET confidence.description="{description}"
                SET confidence.last_updated_on=localdatetime()
                SET confidence{label}:NamedIndividual:Entity
                SET certaintyAssertion.assertion_label="{name} [{ontology_ID}]"
                SET certaintyAssertion.last_updated_on = localdatetime()
                )

                RETURN assertion
                '''.format(assertion_uri=assertion_uri, certainty_uri = certainty_uri, name=name, type=type, label=label, description=description, ontology_ID=ontology_ID, entry_uri=entry_uri, topic_uri=topic_uri, creator='ORKGuserORCID', createdWith='ORKG', certainty_assertion_uri=certainty_assertion_uri)

                # query result
                result = connection.query(assertion_confidence_query_string, db='neo4j')
                print("---------------------------------------------------------------------------------")
                print("------------------------------------- RESULT ------------------------------------")
                print(result)


            else:
                # cypher query to delete the confidence level specification of the assertion
                assertion_confidence_query_string = '''OPTIONAL MATCH (assertion {{URI:"{assertion_uri}"}})-[:ASSERTION_CONFIDENCE_LEVEL]->(certainty {{current_version:"true"}})
                SET certainty.current_version = "false"
                RETURN certainty.current_version
                '''.format(assertion_uri=assertion_uri)

                # query result
                result = connection.query(assertion_confidence_query_string, db='neo4j')
                print("---------------------------------------------------------------------------------")
                print("------------------------------------- RESULT ------------------------------------")
                print(result)

        flash('certainty updated', 'good')


        if parent_uri == entry_uri:
            print("---------------------------------------------------------------")
            print("----------------------- GOES TO ENTRY -------------------------")
            entry_dict = getEntryDict(entry_uri, data_view_name)


            return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


        if parent_uri != entry_uri:
            if parent_item_type == "assertion":
                for parent in entry_dict:
                    if parent.get('id') == parent_uri:
                        parent_node_type = parent.get('node_type')
                        if parent_node_type == "assertion":
                            grand_parent_uri = parent.get('parent')
                            for grand_parent in entry_dict:
                                if grand_parent.get('id') == grand_parent_uri:
                                    grand_parent_node_type = grand_parent.get('node_type')
                                    if grand_parent_node_type == 'topic':
                                        entry_dict = getEntryDict(entry_uri, data_view_name)

                                        entry_dict = updateEntryDict(entry_dict, grand_parent_uri)



                                        return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                        else:

                            entry_dict = getEntryDict(entry_uri, data_view_name)
                            entry_dict = updateEntryDict(entry_dict, parent_uri)
                            return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


            else:

                entry_dict = getEntryDict(entry_uri, data_view_name)
                entry_dict = updateEntryDict(entry_dict, parent_uri)
                return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

        else:
            entry_dict = getEntryDict(entry_uri, data_view_name)
            entry_dict = updateEntryDict(entry_dict, entry_uri)

            return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))



        return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))







@app.route("/instance_label", methods=['POST', 'GET'])
# change of label of a particular resource, provided by a user

def instance_label():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name

    if request.method == "POST":

        if request.form:

            try:
                input_uri = request.form['input_name']
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print("++++++++++++++++++ INPUT URI +++++++++++++++++++++++++")
                print(input_uri)

            except:
                pass

            try:
                input_label = request.form[input_uri + '_instance_label']
                print("---------------------- NEW INSTANCE LABEL -----------------------")
                print(input_label)
            except:
                input_label = None


            parent_uri = request.form[input_uri + '_parent_uri']
            print("------------------------------ PARENT URI -------------------------------")
            print(parent_uri)

            kgbb_uri = request.form[input_uri + '_kgbb_uri']
            print("------------------------------- KGBB URI --------------------------------")
            print(kgbb_uri)

            entry_uri = request.form[input_uri + '_entry_uri']
            print("------------------------------ ENTRY URI --------------------------------")
            print(entry_uri)

            topic_uri = request.form[input_uri + '_topic_uri']
            print("------------------------------ TOPIC URI ---------------------------------")
            print(topic_uri)

            parent_item_type = request.form[input_uri + '_parent_item_type']
            print("--------------------------- PARENT ITEM TYPE ----------------------------")
            print(parent_item_type)

            query_key = "label_cypher"

            # cypher query to edit the label of the resource
            editInstanceLabel(parent_uri, kgbb_uri, entry_uri, topic_uri, input_label, query_key, input_uri)

        flash('resource label updated', 'good')



        if parent_uri == entry_uri:
            print("---------------------------------------------------------------")
            print("----------------------- GOES TO ENTRY -------------------------")
            entry_dict = getEntryDict(entry_uri, data_view_name)


            return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


        if parent_uri != entry_uri:
            if parent_item_type == "assertion":
                for parent in entry_dict:
                    if parent.get('id') == parent_uri:
                        parent_node_type = parent.get('node_type')
                        if parent_node_type == "assertion":
                            grand_parent_uri = parent.get('parent')
                            for grand_parent in entry_dict:
                                if grand_parent.get('id') == grand_parent_uri:
                                    grand_parent_node_type = grand_parent.get('node_type')
                                    if grand_parent_node_type == 'topic':
                                        entry_dict = getEntryDict(entry_uri, data_view_name)

                                        entry_dict = updateEntryDict(entry_dict, grand_parent_uri)



                                        return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                        else:

                            entry_dict = getEntryDict(entry_uri, data_view_name)
                            entry_dict = updateEntryDict(entry_dict, parent_uri)
                            return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


            else:

                entry_dict = getEntryDict(entry_uri, data_view_name)
                entry_dict = updateEntryDict(entry_dict, parent_uri)
                return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

        else:
            entry_dict = getEntryDict(entry_uri, data_view_name)
            entry_dict = updateEntryDict(entry_dict, entry_uri)

            return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))




        return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))






@app.route("/user_input", methods=['POST', 'GET'])
# process information provided by a user

def user_input():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name

    if request.method == "POST":

        if request.form:
            try:
                request.form['single_resource_input']
                answer = getBioPortalSingleInputData ('single_resource_input')
                print("ANSWER")
                print(answer)
                bioportal_answer = answer[0]
                bioportal_preferred_name = answer[1]
                bioportal_full_id = answer[2]
                bioportal_ontology_id = answer[3]
                parent_uri = answer[4]
                entry_uri = answer[5]
                topic_uri = answer[6]
                assertion_uri = answer[7]
                parent_item_type = answer[8]
                kgbb_uri = answer[9]
                input_result = answer[10]
                description = answer[11]
                query_key = answer[12]
                deleted_item_uri = answer[13]
                input_value = answer[14]
                input_value1 = answer[15]
                input_value2 = answer[16]
            except:
                pass

            try:
                input_name = request.form['input_name']
                print("+++++++++++++++++++++++++++++++++++++++++++++++++++")
                print("++++++++++++++++++ INPUT NAME +++++++++++++++++++++")
                print(input_name)

                answer = getBioPortalSingleInputData(input_name)
                print("ANSWER")
                print(answer)
                bioportal_answer = answer[0]
                bioportal_preferred_name = answer[1]
                bioportal_full_id = answer[2]
                bioportal_ontology_id = answer[3]
                parent_uri = answer[4]
                entry_uri = answer[5]
                topic_uri = answer[6]
                assertion_uri = answer[7]
                parent_item_type = answer[8]
                kgbb_uri = answer[9]
                input_result = answer[10]
                description = answer[11]
                query_key = answer[12]
                deleted_item_uri = answer[13]
                input_value = answer[14]
                input_value1 = answer[15]
                input_value2 = answer[16]

            except:
                pass



            # checks whether the selected class resource is already in the graph
            existence_check = existenceCheck(bioportal_full_id)
            print("---------------------------- EXISTENCE CHECK ----------------------------")
            print(existence_check)
            print(type(existence_check))

            # if the class is not yet in the graph, it will now be added
            if existence_check == False:
                addClass(bioportal_full_id, bioportal_preferred_name, bioportal_ontology_id, description)



            if input_result == 'added_assertion' or input_result == 'added_topic':
                added_resource = addResource(parent_uri, kgbb_uri, entry_uri, topic_uri, assertion_uri, description, bioportal_full_id, bioportal_preferred_name, bioportal_ontology_id, input_result, query_key, input_value, input_value1, input_value2)
                print("------------------------------------------------------------------")
                print("----------------------- ADDED RESOURCE ---------------------------")
                print(added_resource)
                resource_uri = added_resource[0]
                parent_uri = added_resource[1]
                result = added_resource[2]

                if result == "added_assertion":
                    assertion_uri = resource_uri
                    message = "Assertion has been added"
                    print("---------------------------------------------------------------")
                    print("------------------------ ASSERTION URI ------------------------")
                    print(assertion_uri)

                elif result == "added_topic":
                    topic_uri = resource_uri
                    message = "Topic has been added"
                    print("---------------------------------------------------------------")
                    print("-------------------------- TOPIC URI ---------------------------")
                    print(topic_uri)


                if parent_uri == entry_uri:
                    print("---------------------------------------------------------------")
                    print("----------------------- GOES TO ENTRY -------------------------")
                    entry_dict = getEntryDict(entry_uri, data_view_name)


                    flash(message, 'good')

                    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


                if parent_uri != entry_uri:
                    if parent_item_type == "assertion":
                        for child in entry_dict:
                            if child.get('id') == parent_uri:
                                select_uri = child.get('parent')
                                entry_dict = getEntryDict(entry_uri, data_view_name)
                                entry_dict = updateEntryDict(entry_dict, select_uri)

                                flash(message, 'good')

                                return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                    elif parent_item_type == "topic":
                        entry_dict = getEntryDict(entry_uri, data_view_name)
                        entry_dict = updateEntryDict(entry_dict, parent_uri)

                        flash(message, 'good')
                        return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))




            elif input_result == 'edited_assertion' or input_result == 'edited_topic':
                added_resource = addResource(parent_uri, kgbb_uri, entry_uri, topic_uri, assertion_uri, description, bioportal_full_id, bioportal_preferred_name, bioportal_ontology_id, input_result, query_key, input_value, input_value1, input_value2)
                print("------------------------------------------------------------------")
                print("----------------------- ADDED/EDITED RESOURCE --------------------")
                print(added_resource)
                resource_uri = added_resource[0]
                parent_uri = added_resource[1]
                result = added_resource[2]

                if result == "added_assertion":
                    assertion_uri = resource_uri
                    message = "Assertion has been added"
                    print("---------------------------------------------------------------")
                    print("------------------------ ASSERTION URI ------------------------")
                    print(assertion_uri)

                if result == "edited_assertion":
                    assertion_uri = resource_uri
                    message = "Assertion has been successfully edited"
                    print("---------------------------------------------------------------")
                    print("------------------------ ASSERTION URI ------------------------")
                    print(assertion_uri)

                elif result == "added_topic":
                    topic_uri = resource_uri
                    message = "Topic has been added"
                    print("---------------------------------------------------------------")
                    print("-------------------------- TOPIC URI ---------------------------")
                    print(topic_uri)

                elif result == "edited_topic":
                    topic_uri = resource_uri
                    message = "Topic has been successfully edited"
                    print("---------------------------------------------------------------")
                    print("-------------------------- TOPIC URI ---------------------------")
                    print(topic_uri)


                if parent_uri == entry_uri:
                    print("---------------------------------------------------------------")
                    print("----------------------- GOES TO ENTRY -------------------------")
                    entry_dict = getEntryDict(entry_uri, data_view_name)


                    flash(message, 'good')

                    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


                if parent_uri != entry_uri:
                    if parent_item_type == "assertion":
                        for parent in entry_dict:
                            if parent.get('id') == parent_uri:
                                parent_node_type = parent.get('node_type')
                                if parent_node_type == "assertion":
                                    grand_parent_uri = parent.get('parent')
                                    for grand_parent in entry_dict:
                                        if grand_parent.get('id') == grand_parent_uri:
                                            grand_parent_node_type = grand_parent.get('node_type')
                                            if grand_parent_node_type == 'topic':
                                                entry_dict = getEntryDict(entry_uri, data_view_name)

                                                entry_dict = updateEntryDict(entry_dict, grand_parent_uri)

                                                flash(message, 'good')

                                                return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                                else:
                                    flash(message, 'good')
                                    entry_dict = getEntryDict(entry_uri, data_view_name)
                                    entry_dict = updateEntryDict(entry_dict, parent_uri)
                                    return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


                    else:
                        flash(message, 'good')
                        entry_dict = getEntryDict(entry_uri, data_view_name)
                        entry_dict = updateEntryDict(entry_dict, parent_uri)
                        return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                else:
                    entry_dict = getEntryDict(entry_uri, data_view_name)
                    entry_dict = updateEntryDict(entry_dict, entry_uri)

                    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

        else:
            return render_template("/entry.html", entry_data=entry_data, topics_length=topics_length, topics_elements_length=topics_elements_length, topic_types_count=topic_types_count, navi_dict=navi_dict, topic_view_tree=topic_view_tree)

    return render_template("/entry.html", entry_data=entry_data, topic_types_count=topic_types_count, navi_dict=navi_dict, topic_view_tree=topic_view_tree)








@app.route("/delete_input", methods=['POST', 'GET'])
# process information provided by a user

def delete_input():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name


    if request.method == "POST":

        if request.form:
            try:
                request.form['delete_assertion']
                response = request.form['delete_assertion_uri']
                # response is a list of assertion_uri and parent_uri as a string
                response = response.replace("['","")
                response = response.replace("']","")

                parent_uri = response.partition("', '")[0]
                print("-----------------------------------------------------")
                print("------------------- PARENT URI ----------------------")
                print(parent_uri)

                assertion_uri = response.partition("', '")[2]
                print("-----------------------------------------------------")
                print("------------------ ASSERTION URI --------------------")
                print(assertion_uri)

                deleteAssertion(assertion_uri, 'userID')

                if parent_uri == entry_uri:
                    print("---------------------------------------------------------------")
                    print("----------------------- GOES TO ENTRY -------------------------")
                    entry_dict = getEntryDict(entry_uri, data_view_name)

                    flash('Entry has been updated', 'good')

                    return render_template("/entry.html", naviJSON=getJSON(entry_dict), entry_dict=entry_dict)

                entry_dict = getEntryDict(entry_uri, data_view_name)

                if parent_uri != entry_uri:
                    for parent in entry_dict:
                        if parent.get('id') == parent_uri:
                            parent_node_type = parent.get('node_type')
                            if parent_node_type == "assertion":
                                grand_parent_uri = parent.get('parent')
                                for grand_parent in entry_dict:
                                    if grand_parent.get('id') == grand_parent_uri:
                                        grand_parent_node_type = grand_parent.get('node_type')
                                        if grand_parent_node_type == 'topic':
                                            entry_dict = updateEntryDict(entry_dict, grand_parent_uri)

                                            return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                            else:
                                entry_dict = updateEntryDict(entry_dict, parent_uri)
                                return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))



                else:
                    entry_dict = updateEntryDict(entry_dict, entry_uri)

                    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))




            except:
                pass
            try:
                request.form['delete_topic']
                response = request.form['delete_topic_uri']
                # response is a list of assertion_uri and parent_uri as a string
                response = response.replace("['","")
                response = response.replace("']","")

                parent_uri = response.partition("', '")[0]
                print("-----------------------------------------------------")
                print("------------------- PARENT URI ----------------------")
                print(parent_uri)

                topic_uri = response.partition("', '")[2]
                print("-----------------------------------------------------")
                print("------------------ TOPIC URI -------------------------")
                print(topic_uri)

                deleteTopic(topic_uri, 'userID')

                entry_dict = getEntryDict(entry_uri, data_view_name)

                entry_dict = updateEntryDict(entry_dict, parent_uri)

                flash('Topic has been deleted', 'good')

                if parent_uri != entry_uri:
                    return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))
                else:
                    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

            except:
                pass


        else:
            entry_dict = getEntryDict(entry_uri, data_view_name)

            entry_dict = updateEntryDict(entry_dict, parent_uri)

            return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

    entry_dict = getEntryDict(entry_uri, data_view_name)

    entry_dict = updateEntryDict(entry_dict, parent_uri)

    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))









@app.route("/entry", methods=['POST', 'GET'])
# gather information about the entry and bind it to an EntryRepresentation class instance

def entry():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name


    if request.method == "POST":
        if request.form['entry_uri']:
            entry_uri = request.form['entry_uri']

            entry_dict = getEntryDict(entry_uri, data_view_name)



            return render_template("/entry.html", naviJSON=getJSON(entry_dict), entry_dict=entry_dict)

        else:
            return render_template("/entry.html", entry_data=entry_data, topics_length=topics_length, topics_elements_length=topics_elements_length, topic_types_count=topic_types_count, navi_dict=navi_dict, topic_view_tree=topic_view_tree, entry_view_tree=entry_view_tree)

    return render_template("/entry.html", entry_data=entry_data, topics_length=topics_length, topics_elements_length=topics_elements_length, topic_types_count=topic_types_count, navi_dict=navi_dict, topic_view_tree=topic_view_tree, entry_view_tree=entry_view_tree)









# navigating through an entry via the navi-tree
@app.route("/navi", methods=['POST', 'GET'])
def navi():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name

    if request.method == 'POST':
        if request.form:
            data = json.loads(request.form['node_data'])
            print(data)
            topic_uri = data['node_data'][0].get('original').get('id')
            node_type = data['node_data'][0].get('original').get('node_type')
            parent_uri = data['node_data'][0].get('original').get('parent')
            entry_uri = entry_dict[0].get('id')
            #topic_uri = topic_uri.decode("utf-8")
            print("---------------------------------------------------------------")
            print("---------------------------------------------------------------")
            print("-------------------------- TOPIC URI ---------------------------")
            print(topic_uri)
            print(type(topic_uri))
            print("---------------------------------------------------------------")
            print("---------------------------------------------------------------")
            print("-------------------------- NODE TYPE ---------------------------")
            print(node_type)


            if topic_uri == entry_uri:
                entry_dict = updateEntryDict(entry_dict, topic_uri)

                return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

            if node_type == "assertion" or node_type == "granularity_tree":
                if parent_uri != entry_uri:
                    for parent in entry_dict:
                        if parent.get('id') == parent_uri:
                            parent_node_type = parent.get('node_type')
                            if parent_node_type == "assertion":
                                grand_parent_uri = parent.get('parent')
                                for grand_parent in entry_dict:
                                    if grand_parent.get('id') == grand_parent_uri:
                                        grand_parent_node_type = grand_parent.get('node_type')
                                        if grand_parent_node_type == 'topic':
                                            entry_dict = updateEntryDict(entry_dict, grand_parent_uri)

                                            return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                            else:
                                entry_dict = updateEntryDict(entry_dict, parent_uri)
                                return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))



                else:
                    entry_dict = updateEntryDict(entry_dict, entry_uri)

                    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


            entry_dict = updateEntryDict(entry_dict, topic_uri)

            return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

        else:
            return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

    return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))







# navigating to a particular topic via a topic resource
@app.route("/topic", methods=['POST', 'GET'])
def topic():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name

    if request.method == 'POST':

        if request.form['topic_uri']:
            topic_uri = request.form['topic_uri']

            entry_dict = updateEntryDict(entry_dict, topic_uri)

            return render_template("/topic.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

        else:
            return render_template("/topic.html", navi_dict=navi_dict, topic_view_tree=topic_view_tree, entry_view_tree=entry_view_tree, naviJSON=getJSON(naviJSON))

    return render_template("/topic.html", navi_dict=navi_dict, topic_view_tree=topic_view_tree, entry_view_tree=entry_view_tree, naviJSON=getJSON(naviJSON))







# getting versions of item back
@app.route("/_versioning", methods=['POST', 'GET'])
def versioning():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name

    data_item_uri = request.args.get('version_data_item_uri', 0, type=str)
    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print("---------------- DATA ITEM URI FOR VERSION SEARCH -------------")
    print(data_item_uri)

    versions_dict = getVersionsDict(data_item_uri)

    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print("-------------------------- DICT OF VERSIONS -------------------")
    print(versions_dict)

    if versions_dict == None:
        versions_dict_length = None
    else:
        versions_dict_length = len(versions_dict)
    print(versions_dict_length)


    return render_template("/versions.html", versions_dict=versions_dict, versions_dict_length=versions_dict_length)






@app.route("/version", methods=['POST', 'GET'])
# gather information about the version
def version():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name


    if request.method == "POST":
        if request.form:
            try:
                version_uri = request.form['current_version_uri']
                print("-----------------------------------------------------")
                print("----------------- CURRENT VERSION URI ---------------")
                print(version_uri)
            except:
                pass



            try:
                version_uri = request.form['version_uri']
                print("-----------------------------------------------------")
                print("----------------- VERSION URI -----------------------")
                print(version_uri)

            except:
                pass

            entry_dict = getVersDict(entry_uri, data_view_name, version_uri)
            print("-----------------------------------------------------")
            print("----------------- VERSION ENTRY DICT ----------------")
            print(entry_dict)

            entry_dict = updateEntryDict(entry_dict,entry_uri)
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print("+++++++++++++++++++++++ UPDATED +++++++++++++++++++++++++++")
            print(entry_dict)

            return render_template("/entry.html", naviJSON=getJSON(entry_dict), entry_dict=entry_dict)


        return render_template("/entry.html", naviJSON=getJSON(version_entry_dict), entry_dict=version_entry_dict)
    return render_template("/entry.html", naviJSON=getJSON(version_entry_dict), entry_dict=version_entry_dict)





@app.route("/version_safe", methods=['POST', 'GET'])
def version_safe():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name

    if request.method == "POST":
        if request.form['entry_uri_']:
            data_item_uri = request.form['entry_uri_']
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print(data_item_uri)

        type = "Entry"


        if data_item_uri != None:
            createVersion(data_item_uri, type)

            entry_dict = getEntryDict(entry_uri, data_view_name)

            return render_template("/entry.html", naviJSON=getJSON(entry_dict), entry_dict=entry_dict)





# getting versions of item back
@app.route("/_safeVersion", methods=['POST', 'GET'])
def safeVersion():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name

    data_item_uri = request.args.get('version_data', 0, type=str)
    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print("---------------- URI OF DATA ITEM TO BE VERSIONED -------------")
    print(data_item_uri)

    type_request = data_item_uri.replace('-', '')

    type = request.args.get('type', 0, type=str)
    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print("------------------------------- TYPE --------------------------")
    print(type)


    if data_item_uri != None:
        createVersion(data_item_uri, type)

        versions_dict = getVersionsDict(data_item_uri)

        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")
        print("---------------------------------------------------------------")
        print("-------------------------- DICT OF VERSIONS -------------------")
        print(versions_dict)


        versions_dict_length = len(versions_dict)
        print(versions_dict_length)


        return render_template("/versions.html", versions_dict=versions_dict, versions_dict_length=versions_dict_length)









# getting editing history back
@app.route("/_edit_history", methods=['POST', 'GET'])
def edit_history():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name

    data_item_uri = request.args.get('data_item_uri', 0, type=str)
    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print("---------------------- HISTORY DATA ITEM URI ------------------")
    print(data_item_uri)

    edit_history = getEditHistory(data_item_uri)

    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print("-------------------------- EDIT HISTORY -----------------------")
    print(edit_history)
    edit_history_length = len(edit_history)
    print(edit_history_length)

    return render_template("/history.html", edit_history=edit_history, edit_history_length=edit_history_length)







# getting editing history back
@app.route("/_granularity_tree", methods=['POST', 'GET'])
def granularity_tree():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name

    granularity_tree_uri = request.args.get('data_item_uri', 0, type=str)
    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print("---------------------- GRANULARITY TREE URI -------------------")
    print(gran_tree_uri)

    granularity_tree_navijson = getGranularityTreeNaviJSON(granularity_tree_uri)

    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print("---------------------------------------------------------------")
    print("--------------- GRANULARITY TREE NAVI JSON --------------------")
    print(granularity_tree_navijson)
    granularity_tree_navijson_length = len(granularity_tree_navijson)
    print(granularity_tree_navijson_length)

    return render_template("/granularity_tree.html", granularity_tree_navijson=granularity_tree_navijson, granularity_tree_navijson_length=granularity_tree_navijson_length)














@app.route("/lobby", methods=['POST', 'GET'])
# delete graph, initiate graph, add new entries
def lobby():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name


    entry_check = connection.query(check_entry_query_string, db='neo4j')
    y = entry_check[0].get("count(n)")
    if y == 0 :
        pubEntry="False"
    else:
        pubEntry="True"

    if request.method == "POST":

        if request.form['button_action'] == 'add publication':

            pub_doi = request.form['publication_DOI']
            print(pub_doi)

            entry_uri = addEntry("ScholarlyPublicationEntryKGBB_URI", pub_doi)
            entry_check = connection.query(check_entry_query_string, db='neo4j')

            y = entry_check[0].get("count(n)")

            if y == 0 :
                print("No entry existing")
                flash('Error: No entry in graph', 'error')
                return render_template("lobby_form.html", initiated="True", pubEntry="False")
            else:
                print(str(y) + " entries in the graph")
                flash(str(y) + ' entries in the graph', 'good')
                return render_template("lobby_form.html", initiated="True", pubEntry="True")



        elif request.form['button_action'] == 'initiate graph':

            connection.query(initiation_query_string, db='neo4j')

            #initiateKGBBs(data_view_name)

            result = connection.query(check_empty_query_string, db='neo4j')

            x = result[0].get("count(n)")

            if x == 0:
                print("none")
                flash('Error: Graph could not be initiated', 'error')
                return render_template("lobby_form.html", initiated="False", pubEntry="False")
            else:
                print("something")
                flash('Graph successfully initiated', 'good')
                return render_template("lobby_form.html", initiated="True", pubEntry=pubEntry)


        elif request.form['button_action'] == 'delete graph':
            connection.query(delete_graph_query_string, db='neo4j')

            connection.query(check_empty_query_string, db='neo4j')

            result = connection.query(check_empty_query_string, db='neo4j')

            x = result[0].get("count(n)")

            if x == 0:
                print("none")
                flash('Graph successfully deleted', 'good')
                return render_template("lobby_form.html", initiated="False", pubEntry="False")
            else:
                print("something")
                flash('Error: Graph could not be deleted', 'error')
                return render_template("lobby_form.html", initiated="True", pubEntry=pubEntry)



        elif request.form['button_action'] == 'view entry list':
            entry_list = connection.query(view_all_scholarly_publication_entries_query_string, db='neo4j')
            return render_template("entrylist_form.html", list_length=len(entry_list), entry_list=entry_list)

        elif request.form['button_action'] == 'search page':
            ontology_class_list = getOntoClassList()
            assertion_class_list = getAssertionClassList()
            topic_class_list = getTopicClassList()
            entry_class_list = getEntryClassList()

            return render_template("search.html", ontology_class_list=ontology_class_list, assertion_class_list=assertion_class_list, topic_class_list=topic_class_list, entry_class_list=entry_class_list)


        elif request.form['button_action'] == 'Return to Entry List':
            entry_list = connection.query(view_all_scholarly_publication_entries_query_string, db='neo4j')
            return render_template("entrylist_form.html", list_length=len(entry_list), entry_list=entry_list)

        elif request.form['button_action'] == 'Return to Lobby':
            return render_template("lobby_form.html", initiated="True", pubEntry=pubEntry)

        else:
            pass
        return render_template("lobby_form.html")
    else:
        return render_template("lobby_form.html")









@app.route("/search", methods=['POST', 'GET'])
# list all entries in the graph
def search():
    global entry_uri
    global entry_dict
    global topic_data
    global topic_kgbb_uri
    global topic_types_count
    global assertion_kgbb_uri
    global entry_name
    global topic_name
    global assertion_name
    global assertion_elements_dict
    global navi_dict
    global topics_length
    global entry_node
    global connection
    global topic_view_tree
    global assertion_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name



    if request.method == "POST":

        try:
            class_uri = request.form['topic_class_uri']
            print("---------------------- TOPIC CLASS URI ---------------------------")
            print(class_uri)

            instances_list = getInstanceList(class_uri)
            print("---------------------- INSTANCES LIST ---------------------------")
            print(instances_list)

        except:
            pass

        topic_nodes_list = []

        for i in range (0, len(instances_list)):
            topic_uri = instances_list[i].get('URI')
            topic_dict = getTopicRepresentation(topic_uri, "ORKG")
            print("-------------------------------------------TOPIC_DICT----------------")
            print(topic_dict)
            topic_nodes_list.append(topic_dict)

        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("+++++++++++++++++++++ FINAL TOPIC NODES LIST ++++++++++++++++++++++++++")
        print(topic_nodes_list)
        print(len(topic_nodes_list))

        return render_template("/search_result.html", topic_nodes_list=topic_nodes_list)




    else:
        return render_template("entry.html", topic_data=topic_data, entry_name=entry_data.entry_label, topic_types_count=topic_types_count)





if __name__ == "__main__":
    app.run()
