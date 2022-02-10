
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

global simpleDescriptionUnit_data
simpleDescriptionUnit_data = None

global simpleDescriptionUnit_kgbb_uri
simpleDescriptionUnit_kgbb_uri = None

global simpleDescriptionUnit_types_count
simpleDescriptionUnit_types_count = None

global basicUnit_elements_dict
basicUnit_elements_dict = None

global basicUnit_kgbb_uri
basicUnit_kgbb_uri = None

global entry_name
entry_name = None

global simpleDescriptionUnit_name
simpleDescriptionUnit_name = None

global basicUnit_name
basicUnit_name = None

global navi_dict
navi_dict = None

global simpleDescriptionUnits_length
simpleDescriptionUnits_length = None

global entry_node
entry_node = None

global simpleDescriptionUnit_view_tree
simpleDescriptionUnit_view_tree = None

global basicUnit_view_tree
basicUnit_view_tree = None

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
    CREATE (iaoDocPart:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"iao: document part", description:"A category denoting a rather broad domain or field of interest, of study, application, work, data, or technology. SimpleDescriptionUnits have no clearly defined borders between each other.", ontology_class:"true", URI:"http://purl.obolibrary.org/obo/IAO_0000314", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(informationContentEntity)
    CREATE (simpleDescriptionUnit:edam_Topic:iao_InformationContentEntity:ClassExpression:Entity {{name:"edam: topic", description:"An information content entity that is part of a document.", ontology_class:"true", URI:"http://edamontology.org/topic_0003", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(informationContentEntity)
    CREATE (orkg_researchtopic:orkg_ResearchTopic:edam_Topic:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg: research topic", ontology_class:"true", description:"A research topic is a subject or issue that a researcher is interested in when conducting research.", URI:"http://orkg/researchtopic_1", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(simpleDescriptionUnit)
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
    //BASIC_UNIT, SIMPLE_DESCRIPTION_UNIT, GRANULARITY TREE, AND ENTRY CLASSES
    CREATE(GranPersp:orkg_GranularityTree:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg granularity tree", description:"An information content entity that is a tree-like hierarchical structure resulting from inter-connected basicUnits of a specific type. The relation that the basicUnits are modelling must be a partial order relation, i.e. a relation that is a binary relation R that is transitive (if b has relation R to c and c has relation R to d, than b has relation R to d), reflexive (b has relation R to itself), and antisymmetric (if b has relation R to c and c has relation R to b, than b and c are identical). The parthood relation is a good example for a partial order relation. Partial order relations result in what is called a granular partition that can be represented as a tree. These trees are called granularity trees. By specifying which types of entities are allowed as domains and ranges of a specific partial order relation, one can distinguish different types of granularity trees, with each type representing a granularity perspective, i.e. a class of particular granularity trees. One could, for example, define the granularity perspective of parthood between material entities, and each particular granularity tree of such parthood-relation-chains between actual material entities represents a granularity tree.", URI:"Granularity_tree_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoDocPart)
    CREATE(parthood_based_gran_tree:orkg_ParthoodBasedGranularityTree:orkg_GranularityTree:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg parthood-based granularity tree", description:"A granularity tree that is based on the parthood relation.", URI:"Parthood_based_Granularity_tree_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(GranPersp)
    CREATE(MatEntParthoodGranTree:orkg_MaterialEntityParthoodGranularityTree:orkg_ParthoodBasedGranularityTree:orkg_GranularityTree:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg material entity parthood granularity tree", description:"A granularity tree that is based on the parthood relation between material entities.", URI:"MatEnt_Parthood_based_Granularity_tree_URI", category:"ClassExpression", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://purl.obolibrary.org/obo/BFO_0000040"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(parthood_based_gran_tree)
    CREATE(Ass:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg basicUnit", description:"An information content entity that is a proposition from some research paper and that is asserted to be true, either by the authors of the paper or by a third party referenced in the paper. An basicUnit in the orkg is also a model for representing the contents of a particular basicUnit from a scholarly publication, representing a smallest unit of information that is independent of other units of information. Different types of such basicUnits can be differentiated.", URI:"BasicUnit_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(:sepio_Assertion:ClassExpression:Entity {{name:"sepio: assertion", URI:"http://purl.obolibrary.org/obo/SEPIO_0000001", category:"ClassExpression"}})
    CREATE (Ass)-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoDocPart)
    CREATE (:orkg_VersionedBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg versioned basicUnit", description:"A version of an orkg basicUnit. Versions of basicUnits capture the content of an basicUnit at a specific point in time and can be used for referencing and citation purposes.", URI:"orkg_versioned_basicUnit_class_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchActivityOutputBasicUnit:orkg_ResearchActivityOutputRelationBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research activity output relation basicUnit", description:"This basicUnit models the relation between a particular research activity and one of its research result outputs.", relevant_properties_URI:["http://purl.obolibrary.org/obo/OBI_0000299"], relevant_classes_URI:["http://orkg???????1", "http://orkg???????5"], URI:"Research_Activity_Output_Relation_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchActivityOutputRelationBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchActivityMethodRelationBasicUnit:orkg_ResearchActivityMethodRelationBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research activity method relation basicUnit", description:"This basicUnit models the relation between a particular research activity and one the research methods it realizes.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000055"], relevant_classes_URI:["http://orkg???????5", "http://orkg???????4"], URI:"Research_Activity_Method_Relation_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchActivityMethodRelationBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchActivityObjectiveRelationBasicUnit:orkg_ResearchActivityObjectiveRelationBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research activity objective relation basicUnit", description:"This basicUnit models the relation between a particular research activity and one the research objectives it achieves.", relevant_properties_URI:["http://purl.obolibrary.org/obo/OBI_0000417"], relevant_classes_URI:["http://orkg???????5", "http://orkg???????3"], URI:"Research_Activity_Objective_Relation_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchActivityObjectiveRelationBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchActivityParthoodBasicUnit:orkg_ResearchActivityParthoodBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research activity parthood basicUnit", description:"This basicUnit models the relation between a particular research activity and its activity parts (i.e. steps).", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000117"], relevant_classes_URI:["http://orkg???????5"], URI:"Research_Activity_Parthood_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchActivityParthoodBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchMethodParthoodBasicUnit:orkg_ResearchMethodParthoodBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research method parthood basicUnit", description:"This basicUnit models the relation between a particular research method and its method parts (i.e. steps).", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????4"], URI:"Research_Method_Parthood_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchMethodParthoodBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchMethodObjectiveRelationBasicUnit:orkg_ResearchMethodObjectiveRelationBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research method objective relation basicUnit", description:"This basicUnit models the relation between a particular research method and its objective specification part.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????4", "http://orkg???????3"], URI:"Research_Method_Objective_Relation_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchMethodObjectiveRelationBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchMethodActivityRelationBasicUnit:orkg_ResearchMethodActivityRelationBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research method activity relation basicUnit", description:"This basicUnit models the relation between a particular research method and the activity that realizes it.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000055"], relevant_classes_URI:["http://orkg???????4", "http://orkg???????5"], URI:"Research_Method_Activity_Relation_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchMethodActivityRelationBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchResultParthoodBasicUnit:orkg_ResearchResultParthoodBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research result parthood basicUnit", description:"This basicUnit models the relation between a particular research result and its result parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????1"], URI:"Research_Result_Parthood_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchResultParthoodBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchResultActivityRelationBasicUnit:orkg_ResearchResultActivityRelationBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research result activity relation basicUnit", description:"This basicUnit models the relation between a particular research result and the research activity that has it as its output.", relevant_properties_URI:["http://purl.obolibrary.org/obo/OBI_0000299"], relevant_classes_URI:["http://orkg???????1", "http://orkg???????5"], URI:"Research_Result_Activity_Relation_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchResultActivityRelationBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchResultObjectiveRelationBasicUnit:orkg_ResearchResultObjectiveRelationBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research result objective relation basicUnit", description:"This basicUnit models the relation between a particular research result and the research objective that achieved it.", relevant_properties_URI:["http://orkg_has_achieved_result"], relevant_classes_URI:["http://orkg???????1", "http://orkg???????3"], URI:"Research_Result_Objective_Relation_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchResultObjectiveRelationBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchResultMaterialEntityRelationBasicUnit:orkg_ResearchResultMaterialEntityRelationBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research result material entity relation basicUnit", description:"This basicUnit models the relation between a particular research result and a material entity that the result is about.", relevant_properties_URI:["http://purl.obolibrary.org/obo/IAO_0000136"], relevant_classes_URI:["http://orkg???????1", "http://purl.obolibrary.org/obo/BFO_0000040"], URI:"Research_Result_Material_Entity_Relation_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchResultMaterialEntityRelationBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchObjectiveParthoodBasicUnit:orkg_ResearchObjectiveParthoodBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research objective parthood basicUnit", description:"This basicUnit models the relation between a particular research objective and its objective parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????3"], URI:"Research_Objective_Parthood_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchObjectiveParthoodBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchObjectiveMethodRelationBasicUnit:orkg_ResearchObjectiveMethodRelationBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research objective method relation basicUnit", description:"This basicUnit models the relation between a particular research objective and the method of which it is a part.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????3", "http://orkg???????4"], URI:"Research_Objective_Method_Relation_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchObjectiveMethodRelationBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchObjectiveActivityRelationBasicUnit:orkg_ResearchObjectiveActivityRelationBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research objective research activity relation basicUnit", description:"This basicUnit models the relation between a particular research objective and the research activity that achieves it.", relevant_properties_URI:["http://purl.obolibrary.org/obo/OBI_0000417"], relevant_classes_URI:["http://orkg???????5", "http://orkg???????4"], URI:"Research_Objective_Activity_Relation_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchObjectiveActivityRelationBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchObjectiveResultRelationBasicUnit:orkg_ResearchObjectiveResultRelationBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research objective result relation basicUnit", description:"This basicUnit models the relation between a particular research objective and the research result that it achieved.", relevant_properties_URI:["http://orkg_has_achieved_result"], relevant_classes_URI:["http://orkg???????3", "http://orkg???????1"], URI:"Research_Objective_Result_Relation_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchObjectiveResultRelationBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (materialEntityParthoodBasicUnit:orkg_MaterialEntityParthoodBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg material entity parthood basicUnit", description:"This basicUnit models the relation between a particular material entity and its material entity parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://purl.obolibrary.org/obo/BFO_0000040"], URI:"Material_Entity_Parthood_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"MaterialEntityParthoodBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (qualityBasicUnit:orkg_QualityRelationIdentificationBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg quality relation identification basicUnit", description:"This basicUnit models the relation between a particular entity and one of its qualities.", relevant_properties_URI:["http://purl.obolibrary.org/obo/RO_0000086"], relevant_classes_URI:["http://purl.obolibrary.org/obo/PATO_0000128", "http://purl.obolibrary.org/obo/PATO_0000146", "http://purl.obolibrary.org/obo/PATO_0001756", "http://purl.obolibrary.org/obo/PATO_0000014"], URI:"Quality_Identification_BasicUnit_URI", category:"ClassExpression", KGBB_URI:"QualityIdentificationBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchTopicBasicUnit:orkg_ResearchTopicBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research topic basicUnit", description:"This basicUnit models the relation between a particular orkg research paper and its research topic.", URI:"ResearchTopicBasicUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchTopicBasicUnitKGBB_URI", relevant_classes_URI:["http://orkg/researchtopic_1", "http://orkg???????2"], relevant_properties_URI:["http://edamontology.org/has_topic"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (confidenceLevelBasicUnit:orkg_ConfidenceLevelBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg confidence level specification basicUnit", description:"This basicUnit models the specification of the confidence level for a given basicUnit, simpleDescriptionUnit, or entry in the orkg. As such, it is a statement about a statement or a collection of statements.", URI:"ConfidenceLevelBasicUnit_URI", category:"ClassExpression", KGBB_URI:"ConfidenceLevelBasicUnitKGBB_URI", relevant_classes_URI:["http://purl.obolibrary.org/obo/NCIT_C107561", "http://purl.obolibrary.org/obo/NCIT_C85550", "http://purl.obolibrary.org/obo/NCIT_C47944"], relevant_properties_URI:["http://purl.obolibrary.org/obo/SEPIO_0000167"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (AssMeasurement:orkg_MeasurementBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg measurement basicUnit", description:"This basicUnit models the relation between a particular quality and one of its measurements. E.g., a weight measurement.", URI:"Measurement_BasicUnit_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (:orkg_GeographicallyLocatedInBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg geographically located in basicUnit", description:"This basicUnit models the relation of a particular material entity and the particular geographic location it is located in.", URI:"GeographicallyLocatedIn_basicUnit_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (:orkg_R0MeasurementBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg basic reproduction number measurement basicUnit", description:"This basicUnit models a particular basic reproduction number measurement with its mean value and a 95% confidence interval.", URI:"R0_measurement_basicUnit_URI", category:"ClassExpression", KGBB_URI:"R0MeasurementBasicUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(AssMeasurement)
    CREATE (weightMeasurementBasicUnit:orkg_WeightMeasurementBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg weight measurement basicUnit", description:"This basicUnit models a particular weight measurement with its value and unit.", URI:"weight_measurement_basicUnit_URI", category:"ClassExpression", KGBB_URI:"WeightMeasurementBasicUnitKGBB_URI", relevant_classes_URI:["http://purl.obolibrary.org/obo/PATO_0000128"], relevant_properties_URI:["http://purl.obolibrary.org/obo/IAO_0000004", "http://purl.obolibrary.org/obo/IAO_0000039", "http://purl.obolibrary.org/obo/OBI_0001938", "http://purl.obolibrary.org/obo/IAO_0000417"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(AssMeasurement)
    CREATE (r0MeasurementBasicUnit:orkg_BasicReproductionNumberMeasurementBasicUnit:orkg_BasicUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg basic reproduction number measurement basicUnit", description:"This basicUnit models a particular basic reproduction number measurement with its value and a 95% confidence interval.", URI:"r0_measurement_basicUnit_URI", category:"ClassExpression", KGBB_URI:"R0MeasurementBasicUnitKGBB_URI", relevant_classes_URI:["http://purl.obolibrary.org/obo/OMIT_0024604", "http://purl.obolibrary.org/obo/STATO_0000196", "http://purl.obolibrary.org/obo/STATO_0000315", "http://purl.obolibrary.org/obo/STATO_0000314", "http://purl.obolibrary.org/obo/STATO_0000561"], relevant_properties_URI:["http://purl.obolibrary.org/obo/IAO_0000004", "http://purl.obolibrary.org/obo/IAO_0000039", "http://purl.obolibrary.org/obo/OBI_0001938", "http://purl.obolibrary.org/obo/IAO_0000417"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(AssMeasurement)
    CREATE (orkgSimpleDescriptionUnit:orkg_SimpleDescriptionUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg simpleDescriptionUnit", description:"An orkg simpleDescriptionUnit is a model for representing the contents of one or more orkg basicUnits on a single UI simpleDescriptionUnit. In other words, simpleDescriptionUnits are containers for basicUnits. Often, basicUnits about the same entity are comprised on a single simpleDescriptionUnit. Different types of such simpleDescriptionUnits can be differentiated.", URI:"orkg_simpleDescriptionUnit_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoDocPart)
    CREATE (:orkg_VersionedSimpleDescriptionUnit:orkg_SimpleDescriptionUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg versioned simpleDescriptionUnit", description:"A version of an orkg simpleDescriptionUnit. Versions of simpleDescriptionUnits capture the content of a simpleDescriptionUnit at a specific point in time and can be used for referencing and citation purposes.", URI:"orkg_versioned_simpleDescriptionUnit_class_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgSimpleDescriptionUnit)
    CREATE (ResActSimpleDescriptionUnit:orkg_ResearchActivitySimpleDescriptionUnit:orkg_SimpleDescriptionUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg Research activity simpleDescriptionUnit", description:"This simpleDescriptionUnit models data about a research activity as it is documented in a particular research papers.", URI:"ResearchActivity_simpleDescriptionUnit_class_URI", category:"ClassExpression", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", relevant_classes_URI:["http://orkg???????5"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgSimpleDescriptionUnit)
    CREATE (ResResSimpleDescriptionUnit:orkg_ResearchResultSimpleDescriptionUnit:orkg_SimpleDescriptionUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg Research result simpleDescriptionUnit", description:"This simpleDescriptionUnit models data about a research result as it is documented in a particular research paper.", URI:"ResearchResult_simpleDescriptionUnit_class_URI", category:"ClassExpression", KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", relevant_classes_URI:["http://orkg???????1"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgSimpleDescriptionUnit)
    CREATE (ResMethSimpleDescriptionUnit:orkg_ResearchMethodSimpleDescriptionUnit:orkg_SimpleDescriptionUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg Research method simpleDescriptionUnit", description:"This simpleDescriptionUnit models data about a research method as it is documented in a particular research paper.", URI:"ResearchMethod_simpleDescriptionUnit_class_URI", category:"ClassExpression", KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", relevant_classes_URI:["http://orkg???????4"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgSimpleDescriptionUnit)
    CREATE (ResObjectiveSimpleDescriptionUnit:orkg_ResearchObjectiveSimpleDescriptionUnit:orkg_SimpleDescriptionUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg Research objective simpleDescriptionUnit", description:"This simpleDescriptionUnit models data about a research objective as it is documented in a particular research paper.", URI:"ResearchObjective_simpleDescriptionUnit_class_URI", category:"ClassExpression", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", relevant_classes_URI:["http://orkg???????3"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgSimpleDescriptionUnit)
    CREATE (materialEntitySimpleDescriptionUnit:orkg_MaterialEntitySimpleDescriptionUnit:orkg_SimpleDescriptionUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg material entity simpleDescriptionUnit", description:"This simpleDescriptionUnit models all information relating to a particular material entity.", URI:"material_entity_simpleDescriptionUnit_URI", category:"ClassExpression", KGBB_URI:"MaterialEntitySimpleDescriptionUnitKGBB_URI", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://purl.obolibrary.org/obo/BFO_0000040"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgSimpleDescriptionUnit)
    CREATE (scholarlyPublicationEntry:orkg_ScholarlyPublicationEntry:orkg_Entry:iao_Document:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg scholarly publication entry", description:"This entry models all information relating to a particular scholarly publication.", URI:"scholarly_publication_entry_URI", category:"ClassExpression", KGBB_URI:"ScholarlyPublicationEntryKGBB_URI", relevant_classes_URI:["http://orkg???????2", "http://orkg/researchtopic_1"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(entryClass:orkg_Entry:iao_Document:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg entry", description:"An orkg entry is a model for representing the contents of one or more orkg simpleDescriptionUnits as a single entry. In other words, entries are containers for simpleDescriptionUnits. Often, simpleDescriptionUnits about the same simpleDescriptionUnit or entity are comprised in a single entry. Different types of such entries can be differentiated.", URI:"orkg_entry_class_URI", category:"ClassExpression"}})
    CREATE (:orkg_VersionedEntry:orkg_Entry:iao_Document:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg versioned entry", description:"A version of an orkg entry. Versions of entries capture the content of an entry at a specific point in time and can be used for referencing and citation purposes.", URI:"orkg_versioned_entry_class_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(entryClass)
    CREATE (scholarlyPublicationEntry)-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoPub)
    CREATE (entryClass)-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoDoc)
    CREATE (:ORKGVersionedEntryClass:orkg_Entry:iao_Document:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg versioned entry", URI:"orkg versioned entry", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(entryClass)
    //KGBB CLASSES
    CREATE (basicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages basicUnit data.", URI:"BasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbb:KGBB:ClassExpression:Entity {{name:"Knowledge Graph Building Block", description:"A Knowledge Graph Building Block is a knowledge graph processing module that manages the storing of data in a knowledge graph application, the presentation of data from a knowledge graph in a user interface and the export of data from a knowledge graph in various export formats and data models.", URI:"KGBB_URI", category:"ClassExpression", operational_KGBB:"false"}})
    CREATE (confidenceLevelBasicUnitKGBB:ConfidenceLevelBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"confidence level specification basicUnit Knowledge Graph Building Block", description:"An basicUnit Knowledge Graph Building Block that manages data referring to the specification of confidence levels for particular basicUnits, simpleDescriptionUnits, or entries.", URI:"ConfidenceLevelBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    CREATE (granperspectiveKGBB:GranularityPerspectiveKGBB:KGBB:ClassExpression:Entity {{name:"granularity perspective Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages data referring to granularity trees.", URI:"GranularityPerspectiveKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbb)
    CREATE (parthood_basedgranperspectiveKGBB:ParthoodBasedGranularityPerspectiveKGBB:GranularityPerspectiveKGBB:KGBB:ClassExpression:Entity {{name:"parthood-based granularity perspective Knowledge Graph Building Block", description:"A granularity perspective Knowledge Graph Building Block that manages data referring to granularity trees that are based on the parthood relation.", partial_order_relation:"HAS_PART", URI:"Parthood-BasedGranularityPerspectiveKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(granperspectiveKGBB)
    //MATERIAL ENTITY PARTHOOD GRANULARITY PERSPECTIVE KGBB
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
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(granTree_ind:orkg_MaterialEntityParthoodGranularityTree_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET granTree_ind.last_updated_on = localdatetime(), granTree_ind.instance_label = "$_label_name_$"
    WITH granTree_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN granTree_ind.contributed_by THEN [1] ELSE [] END |
    SET granTree_ind.contributed_by = granTree_ind.contributed_by + "{creator}"
    )', data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(parthood_basedgranperspectiveKGBB)
    CREATE (entrykgbb:EntryKGBB:KGBB:ClassExpression:Entity {{name:"entry Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages entry data.", URI:"EntryKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"entry"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbb)
    //SCHOLARLY PUBLICATION ENTRY KGBB
    CREATE (scholarlyPublicationEntrykgbb:ScholarlyPublicationEntryKGBB:EntryKGBB:KGBB:ClassExpression:Entity {{name:"scholarly publication entry Knowledge Graph Building Block", description:"An entry Knowledge Graph Building Block that manages data about a scholarly publication.", relevant_classes_URI:["http://orkg???????2", "http://orkg/researchtopic_1"], URI:"ScholarlyPublicationEntryKGBB_URI", category:"ClassExpression", operational_KGBB:"true",storage_model_cypher_code:'MATCH (ORKGEntryClass) WHERE ORKGEntryClass.URI="orkg_entry_class_URI"
    CREATE (entry:orkg_ScholarlyPublicationEntry_IND:orkg_Entry_IND:iao_Document_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"Publication entry unit", URI:"entry_uri", type:"scholarly_publication_entry_URI", entry_doi:"{doiEntry}", publication_doi:"pub_doiX", publication_title:"pub_titleX", entry_URI:"entry_uri", description:"This type of entry models information about a particular research paper.", KGBB_URI:"ScholarlyPublicationEntryKGBB_URI", object_URI:"new_individual_uri1", node_type: "entry", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})-[:HAS_DOI {{category:"DataPropertyExpression", URI:"http://prismstandard.org/namespaces/basic/2.0/doi", entry_URI:"entry_uri"}}]->(doi_entry:EntryDOI_IND:DOI_IND:Literal_IND {{value:"some entry DOI", current_version:"true", entry_doi:"{doiEntry}", entry_URI:"entry_uri", category:"NamedIndividual"}})
    CREATE (entry)-[:IDENTIFIER {{category:"DataPropertyExpression", URI:"https://dublincore.org/specifications/dublin-core/dcmi-terms/#identifier", entry_URI:"entry_uri"}}]->(doi_entry)
    CREATE (publication:orkg_ResearchPaper_IND:iao_PublicationAboutAnInvestigation_IND:iao_Document_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"pub_titleX", type:"http://orkg???????2", publication_doi:"pub_doiX", publication_year:pub_yearX, publication_authors:"pub_authorsX", URI:"new_individual_uri1", publication_journal:"pub_journalX", publication_publisher:"Xpub_publisherX", entry_URI:"entry_uri", category:"NamedIndividual", data_node_type:["entry_object"], current_version:"true", basicUnit_URI:["NULL"], simpleDescriptionUnit_URI:["NULL"], last_updated_on:localdatetime(), versioned_doi:["NULL"], created_on:localdatetime(), created_by:"{creator}", created_with:"{createdWith}"}})-[:HAS_DOI {{category:"DataPropertyExpression", URI:"http://prismstandard.org/namespaces/basic/2.0/doi", entry_URI:"entry_uri"}}]->(doi_publication:PublicationDOI_IND:DOI_IND:Literal_IND {{value:"pub_doiX", publication_doi:"pub_doiX", entry_URI:"entry_uri", category:"NamedIndividual", versioned_doi:["NULL"], current_version:"true"}})
    CREATE (publication)-[:IDENTIFIER {{category:"DataPropertyExpression", URI:"https://dublincore.org/specifications/dublin-core/dcmi-terms/#identifier", entry_URI:"entry_uri"}}]->(doi_publication)
    CREATE (entry)-[:IS_TRANSLATION_OF {{category:"ObjectPropertyExpression", URI:"http://purl.org/vocab/frbr/core#translationOf", entry_URI:"entry_uri", description:"It identifies the original expression of a translated one."}}]->(publication)
    CREATE (publication)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri2"}}]->(ResearchActivity:ResearchActivity_ind:orkg_ResearchActivity_IND:obi_Investigation_IND:obi_PlannedProcess_IND:bfo_Process_IND:NamedIndividual:Entity {{name:"research activity", versioned_doi:["NULL"], dataset_doi:["NULL"], description:"A planned process that has been planned and executed by some research agent and that has some research result. The process ends if some specific research objective is achieved.", URI:"new_individual_uri3", ontology_ID:"ORKG", simpleDescriptionUnit_URI:"new_individual_uri2", type:"http://orkg???????5", instance_label:"Research overview", category:"NamedIndividual", entry_URI:"entry_uri", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", data_node_type:["simpleDescriptionUnit_object"]}})
    CREATE (entry)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri2"}}]->(ResearchActivitySimpleDescriptionUnit_ind:orkg_ResearchActivitySimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research overview simpleDescriptionUnit unit", description:"This simpleDescriptionUnit unit models all data of a particular research activity as it is documented in a particular research paper.", URI:"new_individual_uri2", simpleDescriptionUnit_URI:"new_individual_uri2", type:"ResearchActivity_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"entry_uri", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", editable:"false", object_URI:"new_individual_uri3", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"Research overview"}})
    CREATE (ResearchActivitySimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri2"}}]->(ResearchActivity)
    CREATE (entry)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri2"}}]->(ResearchActivity)
    CREATE (ResearchActivitySimpleDescriptionUnit_ind)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri4"}}]->(ResearchResultSimpleDescriptionUnit_ind:orkg_ResearchResultSimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result simpleDescriptionUnit unit", description:"This simpleDescriptionUnit unit models a research result documented in a particular research paper.", URI:"new_individual_uri4", simpleDescriptionUnit_URI:"new_individual_uri4", type:"ResearchResult_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"entry_uri", KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri5", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"Research result"}})
    CREATE (ResearchActivitySimpleDescriptionUnit_ind)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri10"}}]->(researchActivityOutputBasicUnit_Ind:orkg_ResearchActivityOutputRelationBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity output relation basicUnit unit", description:"This basicUnit unit models the relation between a particular research activity and one of its research result outputs.", URI:"new_individual_uri10", basicUnit_URI:"new_individual_uri10", simpleDescriptionUnit_URI:"new_individual_uri2", type:"Research_Activity_Output_Relation_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"entry_uri", KGBB_URI:"ResearchActivityOutputRelationBasicUnitKGBB_URI", object_URI:"new_individual_uri5", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research activity output"}})
    CREATE (ResearchActivitySimpleDescriptionUnit_ind)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri11"}}]->(researchActivityMethodBasicUnit_Ind:orkg_ResearchActivityMethodRelationBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity method relation basicUnit unit", description:"This basicUnit unit models the relation between a particular research activity and one of the research methods it realizes.", URI:"new_individual_uri11", basicUnit_URI:"new_individual_uri11", simpleDescriptionUnit_URI:"new_individual_uri2", type:"Research_Activity_Method_Relation_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"entry_uri", KGBB_URI:"ResearchActivityMethodRelationBasicUnitKGBB_URI", object_URI:"new_individual_uri7", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research activity method"}})
    CREATE (ResearchActivity)-[:HAS_SPECIFIED_OUTPUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000299", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri2", description:"A relation between a planned process and a continuant participating in that process. The presence of the continuant at the end of the process is explicitly specified in the objective specification which the process realizes the concretization of."}}]->(researchResult:orkg_ResearchResult_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri5", type:"http://orkg???????1", name:"research result", instance_label:"Research result", ontology_ID:"ORKG", description:"An information content entity that is intended to be a truthful statement about something and is the output of some research activity. It is usually acquired by some research method which reliably tends to produce (approximately) truthful statements (cf. iao:data item).", data_node_type:["simpleDescriptionUnit_object"], current_version:"true", entry_URI:"entry_uri", simpleDescriptionUnit_URI:["new_individual_uri2", "new_individual_uri4", "new_individual_uri8"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (researchActivityOutputBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri10"}}]->(ResearchActivity)
    CREATE (researchActivityOutputBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri10"}}]->(ResearchResultSimpleDescriptionUnit_ind)
    CREATE (ResearchResultSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri4"}}]->(researchResult)
    CREATE (researchResult)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri4", description:"a core relation that holds between a whole and its part."}}]->(publication)
    CREATE (ResearchActivitySimpleDescriptionUnit_ind)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri6"}}]->(ResearchMethodSimpleDescriptionUnit_ind:orkg_ResearchMethodSimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method simpleDescriptionUnit unit", description:"This simpleDescriptionUnit unit models a research method documented in a particular research paper.", URI:"new_individual_uri6", simpleDescriptionUnit_URI:"new_individual_uri6", type:"ResearchMethod_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"entry_uri", KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri7", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"Research method"}})
    CREATE (ResearchActivity)-[:REALIZES {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000055", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri2", description:"to say that b realizes c at t is to assert that there is some material entity d & b is a process which has participant d at t & c is a disposition or role of which d is bearer_of at t& the type instantiated by b is correlated with the type instantiated by c. (axiom label in BFO2 Reference: [059-003])."}}]->(researchMethod:orkg_ResearchMethod_IND:iao_PlanSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri7", type:"http://orkg???????4", name:"research method", instance_label:"Research method", ontology_ID:"ORKG", description:"An information content entity that specifies how to conduct some research activity. It usually has some research objective as its part. It instructs some research agent how to achieve the objectives by taking the actions it specifies.", data_node_type:["simpleDescriptionUnit_object"], current_version:"true", entry_URI:"entry_uri", simpleDescriptionUnit_URI:["new_individual_uri2", "new_individual_uri6"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (researchActivityMethodBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri11"}}]->(ResearchActivity)
    CREATE (researchActivityMethodBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri11"}}]->(ResearchMethodSimpleDescriptionUnit_ind)
    CREATE (ResearchMethodSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri6"}}]->(researchMethod)
    CREATE (ResearchActivitySimpleDescriptionUnit_ind)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri8"}}]->(ResearchObjectiveSimpleDescriptionUnit_ind:orkg_ResearchObjectiveSimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective simpleDescriptionUnit unit", description:"This simpleDescriptionUnit unit models a research objective documented in a particular research paper.", URI:"new_individual_uri8", simpleDescriptionUnit_URI:"new_individual_uri8", type:"ResearchObjective_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"entry_uri", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri9", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"Research objective"}})
    CREATE (ResearchActivitySimpleDescriptionUnit_ind)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri12"}}]->(researchActivityObjetiveRelationBasicUnit_Ind:orkg_ResearchActivityObjectiveRelationBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity objective relation basicUnit unit", description:"This basicUnit unit models the relation between a particular research activity and one of the research objectives it achieves.", URI:"new_individual_uri12", basicUnit_URI:"new_individual_uri12", simpleDescriptionUnit_URI:"new_individual_uri2", type:"Research_Activity_Objective_Relation_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"entry_uri", KGBB_URI:"ResearchActivityObjectiveRelationBasicUnitKGBB_URI", object_URI:"new_individual_uri9", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research activity objective"}})
    CREATE (ResearchActivity)-[:ACHIEVES_PLANNED_OBJECTIVE {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000417", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri2", description:"This relation obtains between a planned process and a objective specification when the criteria specified in the objective specification are met at the end of the planned process."}}]->(researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri9", type:"http://orkg???????3", name:"research objective", instance_label:"Research objective", ontology_ID:"ORKG", description:"An information content entity that describes an intended process endpoint for some research activity.", data_node_type:["simpleDescriptionUnit_object"], current_version:"true", entry_URI:"entry_uri", simpleDescriptionUnit_URI:["new_individual_uri2", "new_individual_uri6", "new_individual_uri8"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (researchActivityObjetiveRelationBasicUnit_Ind)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri12"}}]->(ResearchActivity)
    CREATE (researchActivityObjetiveRelationBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri12"}}]->(ResearchObjectiveSimpleDescriptionUnit_ind)
    CREATE (ResearchObjectiveSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri8"}}]->(researchObjective)
    CREATE (researchObjective)-[:HAS_ACHIEVED_RESULT {{category:"ObjectPropertyExpression", URI:"http://orkg_has_achieved_result", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri8", description:"This relation obtains between a research objective and a research result when the criteria specified in the objective specification are met at the end of a planned process which has the research result as its output."}}]->(researchResult)
    CREATE (researchMethod)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"entry_uri", simpleDescriptionUnit_URI:"new_individual_uri6", description:"a core relation that holds between a whole and its part."}}]->(researchObjective)', search_cypher_code:"cypherQuery", data_item_type:"entry"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(entrykgbb)
    CREATE (simpleDescriptionUnitkgbb:SimpleDescriptionUnitKGBB:KGBB:ClassExpression:Entity {{name:"simpleDescriptionUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages simpleDescriptionUnit data.", URI:"SimpleDescriptionUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"simpleDescriptionUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbb)
    //RESEARCH ACTIVITY SIMPLE_DESCRIPTION_UNIT KGBB
    CREATE (ResearchActivitySimpleDescriptionUnitkgbb:ResearchActivitySimpleDescriptionUnitKGBB:SimpleDescriptionUnitKGBB:KGBB:ClassExpression:Entity {{name:"research activity simpleDescriptionUnit Knowledge Graph Building Block", description:"A simpleDescriptionUnit Knowledge Graph Building Block that manages data about the research activity that is documented in a particular research paper.", URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", category:"ClassExpression", relevant_classes_URI:["http://orkg???????5"], storage_model_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}})
    MATCH (publication_node) WHERE publication_node.entry_URI="{entryURI}" AND ("entry_object" IN publication_node.data_node_type)
    CREATE (publication_node)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchActivity:ResearchActivity_ind:orkg_ResearchActivity_IND:obi_Investigation_IND:obi_PlannedProcess_IND:bfo_Process_IND:NamedIndividual:Entity {{name:"research activity", versioned_doi:["NULL"], dataset_doi:["NULL"], description:"A planned process that has been planned and executed by some research agent and that has some research result. The process ends if some specific research objective is achieved.", URI:"new_individual_uri1", ontology_ID:"ORKG", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"http://orkg???????5", instance_label:"Research overview", category:"NamedIndividual", entry_URI:"{entryURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", data_node_type:["simpleDescriptionUnit_object"]}})
    CREATE (entry_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchActivitySimpleDescriptionUnit_ind:orkg_ResearchActivitySimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research overview simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models all data of a particular research activity as it is documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchActivity_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", editable:"false", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"Research overview"}})
    CREATE (ResearchActivitySimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchActivity)
    CREATE (entry_node)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchActivity)', from_activity_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (object_node)-[:HAS_OCCURRENT_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000117", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchActivity:ResearchActivity_ind:orkg_ResearchActivity_IND:obi_Investigation_IND:obi_PlannedProcess_IND:bfo_Process_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["simpleDescriptionUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchActivitySimpleDescriptionUnitIND_URI", user_input:"{simpleDescriptionUnit_uri}"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchActivitySimpleDescriptionUnit_ind:orkg_ResearchActivitySimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models all data of a particular research activity as it is documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchActivity_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"simpleDescriptionUnit_URI:parent_data_item_node.URI", basicUnit_URI:"new_individual_uri2"}}]->(researchActivityParthoodBasicUnit_ind:orkg_ResearchActivityParthoodBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"orkg research activity parthood basicUnit", description:"This basicUnit models the relation between a particular research activity and one its activity parts (i.e., research steps).", URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri2", type:"Research_Activity_Parthood_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchActivityParthoodBasicUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research activity parthood"}})
    CREATE (researchActivityParthoodBasicUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchActivityParthoodBasicUnit_ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(ResearchActivitySimpleDescriptionUnit_ind)
    CREATE (ResearchActivitySimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchActivity)', from_method_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (ResearchActivity:ResearchActivity_ind:orkg_ResearchActivity_IND:obi_Investigation_IND:obi_PlannedProcess_IND:bfo_Process_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["simpleDescriptionUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchActivitySimpleDescriptionUnitIND_URI", user_input:"{simpleDescriptionUnit_uri}"}})-[:REALIZES {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000055", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"to say that b realizes c at t is to assert that there is some material entity d & b is a process which has participant d at t & c is a disposition or role of which d is bearer_of at t& the type instantiated by b is correlated with the type instantiated by c. (axiom label in BFO2 Reference: [059-003])."}}]->(object_node)
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchActivitySimpleDescriptionUnit_ind:orkg_ResearchActivitySimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models all data of a particular research activity as it is documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchActivity_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(researchMethodActivityBasicUnit_Ind:orkg_ResearchMethodActivityRelationBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method activity relation basicUnit unit", description:"This basicUnit models the relation between a particular research method and the activity that realizes it.", URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri2", type:"Research_Method_Activity_Relation_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchMethodActivityRelationBasicUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research method activity"}})
    CREATE (researchMethodActivityBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchMethodActivityBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(ResearchActivitySimpleDescriptionUnit_ind)
    CREATE (ResearchActivitySimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchActivity)', from_result_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (ResearchActivity:ResearchActivity_ind:orkg_ResearchActivity_IND:obi_Investigation_IND:obi_PlannedProcess_IND:bfo_Process_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["simpleDescriptionUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchActivitySimpleDescriptionUnitIND_URI", user_input:"{simpleDescriptionUnit_uri}"}})-[:HAS_SPECIFIED_OUTPUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000299", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"A relation between a planned process and a continuant participating in that process. The presence of the continuant at the end of the process is explicitly specified in the objective specification which the process realizes the concretization of."}}]->(object_node)
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchActivitySimpleDescriptionUnit_ind:orkg_ResearchActivitySimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research overview simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models all data of a particular research activity as it is documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchActivity_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(researchResultActivityRelationBasicUnit_Ind:orkg_ResearchResultActivityRelationBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result activity relation basicUnit unit", description:"This basicUnit models the relation between a particular research result and the research activity that has it as its output.", URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri2", type:"Research_Result_Activity_Relation_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchResultActivityRelationBasicUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research result activity"}})
    CREATE (researchResultActivityRelationBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchResultActivityRelationBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(ResearchActivitySimpleDescriptionUnit_ind)
    CREATE (ResearchActivitySimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchActivity)',  from_objective_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (ResearchActivity:ResearchActivity_ind:orkg_ResearchActivity_IND:obi_Investigation_IND:obi_PlannedProcess_IND:bfo_Process_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["simpleDescriptionUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchActivitySimpleDescriptionUnitIND_URI", user_input:"{simpleDescriptionUnit_uri}"}})-[:ACHIEVES_PLANNED_OBJECTIVE {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000417", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"This relation obtains between a planned process and a objective specification when the criteria specified in the objective specification are met at the end of the planned process."}}]->(object_node)
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchActivitySimpleDescriptionUnit_ind:orkg_ResearchActivitySimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research overview simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models all data of a particular research activity as it is documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchActivity_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(researchObjectiveActivityRelationBasicUnit_Ind:orkg_ResearchObjectiveActivityRelationBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective activity relation basicUnit unit", description:"This basicUnit models the relation between a particular research objective and the research activity that achieves it.", URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri2", type:"Research_Objective_Activity_Relation_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchObjectiveActivityRelationBasicUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research objective activity"}})
    CREATE (researchObjectiveActivityRelationBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchObjectiveActivityRelationBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(ResearchActivitySimpleDescriptionUnit_ind)
    CREATE (ResearchActivitySimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchActivity)', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(researchActivitySimpleDescriptionUnit_ind:orkg_ResearchActivitySimpleDescriptionUnit_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET researchActivitySimpleDescriptionUnit_ind.last_updated_on = localdatetime(), researchActivitySimpleDescriptionUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, researchActivitySimpleDescriptionUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN researchActivitySimpleDescriptionUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET researchActivitySimpleDescriptionUnit_ind.contributed_by = researchActivitySimpleDescriptionUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, researchActivitySimpleDescriptionUnit_ind
    MATCH (researchActivitySimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchAct_old:orkg_ResearchActivity_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, researchActivitySimpleDescriptionUnit_ind, researchAct_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchAct_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, researchActivitySimpleDescriptionUnit_ind, researchAct_old SET researchAct_old.current_version = "false"
    WITH researchActivitySimpleDescriptionUnit_ind
    MATCH (researchActivitySimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchAct_new:orkg_ResearchActivity_IND {{current_version:"true"}})
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(researchActivitySimpleDescriptionUnit_ind:orkg_ResearchActivitySimpleDescriptionUnit_IND {{URI:"{simpleDescriptionUnit_uri}", current_version:"true"}}) SET researchActivitySimpleDescriptionUnit_ind.last_updated_on = localdatetime(), researchActivitySimpleDescriptionUnit_ind.simpleDescriptionUnit_label = "$_input_name_$ [$_ontology_ID_$]", researchActivitySimpleDescriptionUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, researchActivitySimpleDescriptionUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN researchActivitySimpleDescriptionUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET researchActivitySimpleDescriptionUnit_ind.contributed_by = researchActivitySimpleDescriptionUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, researchActivitySimpleDescriptionUnit_ind
    MATCH (researchActivitySimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchAct_old:orkg_ResearchActivity_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, researchActivitySimpleDescriptionUnit_ind, researchAct_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchAct_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, researchActivitySimpleDescriptionUnit_ind, researchAct_old SET researchAct_old.current_version = "false"
    WITH researchActivitySimpleDescriptionUnit_ind
    MATCH (researchActivitySimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchAct_new:orkg_ResearchActivity_IND {{current_version:"true"}})
    SET researchAct_new.name = "$_input_name_$", researchAct_new.instance_label = "$_input_name_$", researchAct_new.ontology_ID = "$_ontology_ID_$", researchAct_new.description = "$_input_description_$", researchAct_new.URI = "new_individual_uri1", researchAct_new.type = "$_input_type_$", researchAct_new.created_on = localdatetime(), researchAct_new.last_updated_on = localdatetime(), researchAct_new.created_by = "{creator}", researchAct_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", operational_KGBB:"true", data_item_type:"simpleDescriptionUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(simpleDescriptionUnitkgbb)
    //RESEARCH OBJECTIVE SIMPLE_DESCRIPTION_UNIT KGBB
    CREATE (ResearchObjectiveSimpleDescriptionUnitkgbb:ResearchObjectiveSimpleDescriptionUnitKGBB:SimpleDescriptionUnitKGBB:KGBB:ClassExpression:Entity {{name:"research objective simpleDescriptionUnit Knowledge Graph Building Block", description:"A simpleDescriptionUnit Knowledge Graph Building Block that manages data about the research objective that is documented in a particular research paper.", URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", category:"ClassExpression", relevant_classes_URI:["http://orkg???????3"], storage_model_cypher_code:'MATCH (parent_data_item_node:orkg_ResearchActivitySimpleDescriptionUnit_IND {{entry_URI:"{entryURI}"}})
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI
    OPTIONAL MATCH (object_node)-[:HAS_SPECIFIED_OUTPUT]->(researchResult:orkg_ResearchResult_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, researchResult
    OPTIONAL MATCH (object_node)-[:REALIZES]->(researchMethod:orkg_ResearchMethod_IND {{current_version:"true"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchObjectiveSimpleDescriptionUnit_ind:orkg_ResearchObjectiveSimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models a research objective documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchObjective_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"Research objective"}})
    CREATE (object_node)-[:ACHIEVES_PLANNED_OBJECTIVE {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000417", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"This relation obtains between a planned process and a objective specification when the criteria specified in the objective specification are met at the end of the planned process."}}]->(researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"http://orkg???????3", name:"research objective", instance_label:"Research objective", ontology_ID:"ORKG", description:"An information content entity that describes an intended process endpoint for some research activity.", data_node_type:["simpleDescriptionUnit_object"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (ResearchObjectiveSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(researchObjective)
    WITH parent_data_item_node, object_node, researchResult, researchMethod, researchObjective
    FOREACH (i IN CASE WHEN researchResult IS NOT NULL THEN [1] ELSE [] END |
    CREATE (researchObjective)-[:HAS_ACHIEVED_RESULT {{category:"ObjectPropertyExpression", URI:"http://orkg_has_achieved_result", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"This relation obtains between a research objective and a research result when the criteria specified in the objective specification are met at the end of a planned process which has the research result as its output."}}]->(researchResult)
    )
    WITH parent_data_item_node, object_node, researchResult, researchMethod, researchObjective
    FOREACH (i IN CASE WHEN researchMethod IS NOT NULL THEN [1] ELSE [] END |
    CREATE (researchMethod)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(researchObjective)
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(ResearchObjectiveSimpleDescriptionUnit_ind:orkg_ResearchObjectiveSimpleDescriptionUnit_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET ResearchObjectiveSimpleDescriptionUnit_ind.last_updated_on = localdatetime(), ResearchObjectiveSimpleDescriptionUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, ResearchObjectiveSimpleDescriptionUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchObjectiveSimpleDescriptionUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchObjectiveSimpleDescriptionUnit_ind.contributed_by = ResearchObjectiveSimpleDescriptionUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, ResearchObjectiveSimpleDescriptionUnit_ind
    MATCH (ResearchObjectiveSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchObjective_old:orkg_ResearchObjective_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, ResearchObjectiveSimpleDescriptionUnit_ind, researchObjective_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchObjective_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchObjectiveSimpleDescriptionUnit_ind, researchObjective_old SET researchObjective_old.current_version = "false"
    WITH ResearchObjectiveSimpleDescriptionUnit_ind
    MATCH (ResearchObjectiveSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchObjective_new:orkg_ResearchObjective_IND {{current_version:"true"}})
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(ResearchObjectiveSimpleDescriptionUnit_ind:orkg_ResearchObjectiveSimpleDescriptionUnit_IND {{URI:"{simpleDescriptionUnit_uri}", current_version:"true"}}) SET ResearchObjectiveSimpleDescriptionUnit_ind.last_updated_on = localdatetime(), ResearchObjectiveSimpleDescriptionUnit_ind.simpleDescriptionUnit_label = "$_input_name_$ [$_ontology_ID_$]", ResearchObjectiveSimpleDescriptionUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, ResearchObjectiveSimpleDescriptionUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchObjectiveSimpleDescriptionUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchObjectiveSimpleDescriptionUnit_ind.contributed_by = ResearchObjectiveSimpleDescriptionUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, ResearchObjectiveSimpleDescriptionUnit_ind
    MATCH (ResearchObjectiveSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchObjective_old:orkg_ResearchObjective_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, ResearchObjectiveSimpleDescriptionUnit_ind, researchObjective_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchObjective_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchObjectiveSimpleDescriptionUnit_ind, researchObjective_old SET researchObjective_old.current_version = "false"
    WITH ResearchObjectiveSimpleDescriptionUnit_ind
    MATCH (ResearchObjectiveSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchObjective_new:orkg_ResearchObjective_IND {{current_version:"true"}})
    SET researchObjective_new.name = "$_input_name_$", researchObjective_new.instance_label = "$_input_name_$", researchObjective_new.ontology_ID = "$_ontology_ID_$", researchObjective_new.type = "$_input_type_$", researchObjective_new.description = "$_input_description_$", researchObjective_new.URI = "new_individual_uri1", researchObjective_new.created_on = localdatetime(), researchObjective_new.last_updated_on = localdatetime(), researchObjective_new.created_by = "{creator}", researchObjective_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", from_activity_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH entry_node, parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchObjectiveSimpleDescriptionUnit_ind:orkg_ResearchObjectiveSimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models a research objective documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchObjective_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (object_node)-[:ACHIEVES_PLANNED_OBJECTIVE {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000417", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"This relation obtains between a planned process and a objective specification when the criteria specified in the objective specification are met at the end of the planned process."}}]->(researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["simpleDescriptionUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchObjectiveSimpleDescriptionUnitIND_URI", user_input:"{simpleDescriptionUnit_uri}"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(researchActivityObjetiveRelationBasicUnit_Ind:orkg_ResearchActivityObjectiveRelationBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity objective relation basicUnit unit", description:"This basicUnit unit models the relation between a particular research activity and one of the research objectives it achieves.", URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri2", simpleDescriptionUnit_URI:parent_data_item_node.URI, type:"Research_Activity_Objective_Relation_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchActivityObjectiveRelationBasicUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research activity objective"}})
    CREATE (researchActivityObjetiveRelationBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchActivityObjetiveRelationBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(ResearchObjectiveSimpleDescriptionUnit_ind)
    CREATE (ResearchObjectiveSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(researchObjective)', from_method_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH entry_node, parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchObjectiveSimpleDescriptionUnit_ind:orkg_ResearchObjectiveSimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models a research objective documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchObjective_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["simpleDescriptionUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchObjectiveSimpleDescriptionUnitIND_URI", user_input:"{simpleDescriptionUnit_uri}"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(researchMethodObjectiveRelationBasicUnit_Ind:orkg_ResearchMethodObjectiveRelationBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method objective relation basicUnit unit", description:"This basicUnit models the relation between a particular research method and its objective specification part.", URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri2", type:"Research_Method_Objective_Relation_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchMethodObjectiveRelationBasicUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research method objective"}})
    CREATE (researchMethodObjectiveRelationBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchMethodObjectiveRelationBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(ResearchObjectiveSimpleDescriptionUnit_ind)
    CREATE (ResearchObjectiveSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(researchObjective)', from_result_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH entry_node, parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchObjectiveSimpleDescriptionUnit_ind:orkg_ResearchObjectiveSimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models a research objective documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchObjective_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["simpleDescriptionUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchObjectiveSimpleDescriptionUnitIND_URI", user_input:"{simpleDescriptionUnit_uri}"}})-[:HAS_ACHIEVED_RESULT {{category:"ObjectPropertyExpression", URI:"http://orkg_has_achieved_result", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"This relation obtains between a research objective and a research result when the criteria specified in the objective specification are met at the end of a planned process which has the research result as its output."}}]->(object_node)
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(researchResultObjectiveRelationBasicUnit_Ind:orkg_ResearchResultObjectiveRelationBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result objective relation basicUnit unit", description:"This basicUnit models the relation between a particular research result and the research objective that achieved it.", URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri2", type:"Research_Result_Objective_Relation_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchResultObjectiveRelationBasicUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research result objective"}})
    CREATE (researchResultObjectiveRelationBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchResultObjectiveRelationBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(ResearchObjectiveSimpleDescriptionUnit_ind)
    CREATE (ResearchObjectiveSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(researchObjective)', from_objective_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH entry_node, parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_dcontains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchObjectiveSimpleDescriptionUnit_ind:orkg_ResearchObjectiveSimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models a research objective documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchObjective_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["simpleDescriptionUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchObjectiveSimpleDescriptionUnitIND_URI", user_input:"{simpleDescriptionUnit_uri}"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(researchObjectiveParthoodBasicUnit_Ind:orkg_ResearchObjectiveParthoodBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective parthood basicUnit unit", description:"This basicUnit unit models the relation between a particular research objective and its objective parts.", URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri2", type:"Research_Objective_Parthood_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchObjectiveParthoodBasicUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research objective parthood"}})
    CREATE (researchObjectiveParthoodBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchObjectiveParthoodBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(ResearchObjectiveSimpleDescriptionUnit_ind)
    CREATE (ResearchObjectiveSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(researchObjective)', operational_KGBB:"true", data_item_type:"simpleDescriptionUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(simpleDescriptionUnitkgbb)
    //RESEARCH RESULT SIMPLE_DESCRIPTION_UNIT KGBB
    CREATE (ResearchResultSimpleDescriptionUnitkgbb:ResearchResultSimpleDescriptionUnitKGBB:SimpleDescriptionUnitKGBB:KGBB:ClassExpression:Entity {{name:"research result simpleDescriptionUnit Knowledge Graph Building Block", description:"A simpleDescriptionUnit Knowledge Graph Building Block that manages data about the research results documented in a particular research paper.", relevant_classes_URI:["http://orkg???????1"], URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", category:"ClassExpression", storage_model_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}})
    MATCH (publication_node) WHERE publication_node.entry_URI="{entryURI}" AND ("entry_object" IN publication_node.data_node_type)
    MATCH (parent_data_item_node:orkg_ResearchActivitySimpleDescriptionUnit_IND {{entry_URI:entry_node.URI}})
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI
    OPTIONAL MATCH (object_node)-[:ACHIEVES_PLANNED_OBJECTIVE]->(researchObjective:orkg_ResearchObjective_IND {{current_version:"true"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchResultSimpleDescriptionUnit_ind:orkg_ResearchResultSimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models a research result documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchResult_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"Research result"}})
    CREATE (object_node)-[:HAS_SPECIFIED_OUTPUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000299", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"A relation between a planned process and a continuant participating in that process. The presence of the continuant at the end of the process is explicitly specified in the objective specification which the process realizes the concretization of."}}]->(researchResult:orkg_ResearchResult_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"http://orkg???????1", name:"research result", instance_label:"Research result", ontology_ID:"ORKG", description:"An information content entity that is intended to be a truthful statement about something and is the output of some research activity. It is usually acquired by some research method which reliably tends to produce (approximately) truthful statements (cf. iao:data item).", data_node_type:["simpleDescriptionUnit_object"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (ResearchResultSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(researchResult)
    CREATE (researchResult)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(publication_node)
    WITH parent_data_item_node, object_node, researchObjective, researchResult
    FOREACH (i IN CASE WHEN researchObjective IS NOT NULL THEN [1] ELSE [] END |
    CREATE (researchObjective)-[:HAS_ACHIEVED_RESULT {{category:"ObjectPropertyExpression", URI:"http://orkg_has_achieved_result", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"This relation obtains between a research objective and a research result when the criteria specified in the objective specification are met at the end of a planned process which has the research result as its output."}}]->(researchResult))', from_result_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchResultSimpleDescriptionUnit_ind:orkg_ResearchResultSimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models a research result documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchResult_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(researchResult:orkg_ResearchResult_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["simpleDescriptionUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchResultSimpleDescriptionUnitIND_URI", user_input:"{simpleDescriptionUnit_uri}"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(researchResultParthoodBasicUnit_Ind:orkg_ResearchResultParthoodBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result parthood basicUnit unit", description:"This basicUnit unit models the relation between a particular research result and one of its research result parts.", URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri2", type:"Research_Activity_Parthood_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchResultParthoodBasicUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research result parthood"}})
    CREATE (researchResultParthoodBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchResultParthoodBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(ResearchResultSimpleDescriptionUnit_ind)
    CREATE (ResearchResultSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(researchResult)', from_objective_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchResultSimpleDescriptionUnit_ind:orkg_ResearchResultSimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models a research result documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchResult_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (object_node)-[:HAS_ACHIEVED_RESULT {{category:"ObjectPropertyExpression", URI:"http://orkg_has_achieved_result", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(researchResult:orkg_ResearchResult_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["simpleDescriptionUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchResultSimpleDescriptionUnitIND_URI", user_input:"{simpleDescriptionUnit_uri}"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(researchObjectiveResultRelationBasicUnit_Ind:orkg_ResearchObjectiveResultRelationBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective result relation basicUnit unit", description:"This basicUnit models the relation between a particular research objective and the research result that it achieved.", URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri2", type:"Research_Objective_Result_Relation_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchObjectiveResultRealtionBasicUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research objective result"}})
    CREATE (researchObjectiveResultRelationBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchObjectiveResultRelationBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(ResearchResultSimpleDescriptionUnit_ind)
    CREATE (ResearchResultSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(researchResult)', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(ResearchResultSimpleDescriptionUnit_ind:orkg_ResearchResultSimpleDescriptionUnit_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET ResearchResultSimpleDescriptionUnit_ind.last_updated_on = localdatetime(), ResearchResultSimpleDescriptionUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, ResearchResultSimpleDescriptionUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchResultSimpleDescriptionUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchResultSimpleDescriptionUnit_ind.contributed_by = ResearchResultSimpleDescriptionUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, ResearchResultSimpleDescriptionUnit_ind
    MATCH (ResearchResultSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchResult_old:orkg_ResearchResult_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, ResearchResultSimpleDescriptionUnit_ind, researchResult_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchResult_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchResultSimpleDescriptionUnit_ind, researchResult_old SET researchResult_old.current_version = "false"
    WITH ResearchResultSimpleDescriptionUnit_ind
    MATCH (ResearchResultSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchResult_new:orkg_ResearchResult_IND {{current_version:"true"}})
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(ResearchResultSimpleDescriptionUnit_ind:orkg_ResearchResultSimpleDescriptionUnit_IND {{URI:"{simpleDescriptionUnit_uri}", current_version:"true"}}) SET ResearchResultSimpleDescriptionUnit_ind.last_updated_on = localdatetime(), ResearchResultSimpleDescriptionUnit_ind.simpleDescriptionUnit_label = "$_input_name_$ [$_ontology_ID_$]", ResearchResultSimpleDescriptionUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, ResearchResultSimpleDescriptionUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchResultSimpleDescriptionUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchResultSimpleDescriptionUnit_ind.contributed_by = ResearchResultSimpleDescriptionUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, ResearchResultSimpleDescriptionUnit_ind
    MATCH (ResearchResultSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchResult_old:orkg_ResearchResult_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, ResearchResultSimpleDescriptionUnit_ind, researchResult_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchResult_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchResultSimpleDescriptionUnit_ind, researchResult_old SET researchResult_old.current_version = "false"
    WITH ResearchResultSimpleDescriptionUnit_ind
    MATCH (ResearchResultSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchResult_new:orkg_ResearchResult_IND {{current_version:"true"}})
    SET researchResult_new.name = "$_input_name_$", researchResult_new.instance_label = "$_input_name_$", researchResult_new.ontology_ID = "$_ontology_ID_$", researchResult_new.type = "$_input_type_$", researchResult_new.description = "$_input_description_$", researchResult_new.URI = "new_individual_uri1", researchResult_new.created_on = localdatetime(), researchResult_new.last_updated_on = localdatetime(), researchResult_new.created_by = "{creator}", researchResult_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", from_activity_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node MATCH (publication_node) WHERE publication_node.entry_URI="{entryURI}" AND ("entry_object" IN publication_node.data_node_type)
    WITH entry_node, publication_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, publication_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH entry_node, publication_node, parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchResultSimpleDescriptionUnit_ind:orkg_ResearchResultSimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models a research result documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchResult_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(researchActivityOutputBasicUnit_Ind:orkg_ResearchActivityOutputRelationBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity output relation basicUnit unit", description:"This basicUnit unit models the relation between a particular research activity and one of its research result outputs.", URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri2", type:"Research_Activity_Output_Relation_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchActivityOutputRelationBasicUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research activity output"}})
    CREATE (object_node)-[:HAS_SPECIFIED_OUTPUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000299", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"A relation between a planned process and a continuant participating in that process. The presence of the continuant at the end of the process is explicitly specified in the objective specification which the process realizes the concretization of."}}]->(researchResult:orkg_ResearchResult_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["simpleDescriptionUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchResultSimpleDescriptionUnitIND_URI", user_input:"{simpleDescriptionUnit_uri}"}})
    CREATE (researchActivityOutputBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(researchResult)
    CREATE (researchActivityOutputBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(ResearchResultSimpleDescriptionUnit_ind)
    CREATE (ResearchResultSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(object_node)
    CREATE (researchResult)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(publication_node)', operational_KGBB:"true", data_item_type:"simpleDescriptionUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(simpleDescriptionUnitkgbb)
    //RESEARCH METHOD SIMPLE_DESCRIPTION_UNIT KGBB
    CREATE (ResearchMethodSimpleDescriptionUnitkgbb:ResearchMethodSimpleDescriptionUnitKGBB:SimpleDescriptionUnitKGBB:KGBB:ClassExpression:Entity {{name:"research method simpleDescriptionUnit Knowledge Graph Building Block", description:"A simpleDescriptionUnit Knowledge Graph Building Block that manages data about the research methods documented in a particular research paper.", relevant_classes_URI:["http://orkg???????4"], URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", category:"ClassExpression", storage_model_cypher_code:'MATCH (parent_data_item_node:orkg_ResearchActivitySimpleDescriptionUnit_IND {{entry_URI:"{entryURI}"}})
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI
    OPTIONAL MATCH (object_node)-[:ACHIEVES_PLANNED_OBJECTIVE]->(researchObjective:orkg_ResearchObjective_IND {{current_version:"true"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchMethodSimpleDescriptionUnit_ind:orkg_ResearchMethodSimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models a research method documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchMethod_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"Research method"}})
    CREATE (object_node)-[:REALIZES {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000055", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"to say that b realizes c at t is to assert that there is some material entity d & b is a process which has participant d at t & c is a disposition or role of which d is bearer_of at t& the type instantiated by b is correlated with the type instantiated by c. (axiom label in BFO2 Reference: [059-003])."}}]->(researchMethod:orkg_ResearchMethod_IND:iao_PlanSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"http://orkg???????4", name:"research method", instance_label:"Research method", ontology_ID:"ORKG", description:"An information content entity that specifies how to conduct some research activity. It usually has some research objective as its part. It instructs some research agent how to achieve the objectives by taking the actions it specifies.", data_node_type:["simpleDescriptionUnit_object"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (ResearchMethodSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(researchMethod)
    WITH parent_data_item_node, object_node, researchObjective, researchMethod
    FOREACH (i IN CASE WHEN researchObjective IS NOT NULL THEN [1] ELSE [] END |
    CREATE (researchMethod)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(researchObjective)
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(ResearchMethodSimpleDescriptionUnit_ind:orkg_ResearchMethodSimpleDescriptionUnit_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET ResearchMethodSimpleDescriptionUnit_ind.last_updated_on = localdatetime(), ResearchMethodSimpleDescriptionUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, ResearchMethodSimpleDescriptionUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchMethodSimpleDescriptionUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchMethodSimpleDescriptionUnit_ind.contributed_by = ResearchMethodSimpleDescriptionUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, ResearchMethodSimpleDescriptionUnit_ind
    MATCH (ResearchMethodSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchMethod_old:orkg_ResearchMethod_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, ResearchMethodSimpleDescriptionUnit_ind, researchMethod_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchMethod_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchMethodSimpleDescriptionUnit_ind, researchMethod_old SET researchMethod_old.current_version = "false"
    WITH ResearchMethodSimpleDescriptionUnit_ind
    MATCH (ResearchMethodSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchMethod_new:orkg_ResearchMethod_IND {{current_version:"true"}})
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(ResearchMethodSimpleDescriptionUnit_ind:orkg_ResearchMethodSimpleDescriptionUnit_IND {{URI:"{simpleDescriptionUnit_uri}", current_version:"true"}}) SET ResearchMethodSimpleDescriptionUnit_ind.last_updated_on = localdatetime(), ResearchMethodSimpleDescriptionUnit_ind.simpleDescriptionUnit_label = "$_input_name_$ [$_ontology_ID_$]", ResearchMethodSimpleDescriptionUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, ResearchMethodSimpleDescriptionUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchMethodSimpleDescriptionUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchMethodSimpleDescriptionUnit_ind.contributed_by = ResearchMethodSimpleDescriptionUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, ResearchMethodSimpleDescriptionUnit_ind
    MATCH (ResearchMethodSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchMethod_old:orkg_ResearchMethod_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, ResearchMethodSimpleDescriptionUnit_ind, researchMethod_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchMethod_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchMethodSimpleDescriptionUnit_ind, researchMethod_old SET researchMethod_old.current_version = "false"
    WITH ResearchMethodSimpleDescriptionUnit_ind
    MATCH (ResearchMethodSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchMethod_new:orkg_ResearchMethod_IND {{current_version:"true"}})
    SET researchMethod_new.name = "$_input_name_$", researchMethod_new.instance_label = "$_input_name_$", researchMethod_new.ontology_ID = "$_ontology_ID_$", researchMethod_new.type = "$_input_type_$", researchMethod_new.description = "$_input_description_$", researchMethod_new.URI = "new_individual_uri1", researchMethod_new.created_on = localdatetime(), researchMethod_new.last_updated_on = localdatetime(), researchMethod_new.created_by = "{creator}", researchMethod_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", from_activity_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH entry_node, parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchMethodSimpleDescriptionUnit_ind:orkg_ResearchMethodSimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models a research method documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchMethod_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(researchActivityMethodBasicUnit_Ind:orkg_ResearchActivityMethodRelationBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity method relation basicUnit unit", description:"This basicUnit unit models the relation between a particular research activity and one of the research methods it realizes.", URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri2", type:"Research_Activity_Method_Relation_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchActivityMethodRelationBasicUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research activity method"}})
    CREATE (researchActivityMethodBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchActivityMethodBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(ResearchMethodSimpleDescriptionUnit_ind)
    CREATE (object_node)-[:REALIZES {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000055", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"to say that b realizes c at t is to assert that there is some material entity d & b is a process which has participant d at t & c is a disposition or role of which d is bearer_of at t& the type instantiated by b is correlated with the type instantiated by c. (axiom label in BFO2 Reference: [059-003])."}}]->(researchMethod:orkg_ResearchMethod_IND:iao_PlanSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["simpleDescriptionUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchMethodSimpleDescriptionUnitIND_URI", user_input:"{simpleDescriptionUnit_uri}"}})
    CREATE (ResearchMethodSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(researchMethod)', from_objective_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH entry_node, parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchMethodSimpleDescriptionUnit_ind:orkg_ResearchMethodSimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models a research method documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchMethod_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(researchObjectiveMethodRelationBasicUnit_Ind:orkg_ResearchObjectiveMethodRelationBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective method relation basicUnit unit", description:"This basicUnit models the relation between a particular research objective and a research method of which it is a part.", URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri2", type:"Research_Objective_Method_Relation_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchObjectiveMethodRelationBasicUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research objective method"}})
    CREATE (researchObjectiveMethodRelationBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchObjectiveMethodRelationBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(ResearchMethodSimpleDescriptionUnit_ind)
    CREATE (researchMethod:orkg_ResearchMethod_IND:iao_PlanSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["simpleDescriptionUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchMethodSimpleDescriptionUnitIND_URI", user_input:"{simpleDescriptionUnit_uri}"}})-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(object_node)
    CREATE (ResearchMethodSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(researchMethod)', from_method_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH entry_node, parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(ResearchMethodSimpleDescriptionUnit_ind:orkg_ResearchMethodSimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models a research method documented in a particular research paper.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"ResearchMethod_simpleDescriptionUnit_class_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(researchMethod:orkg_ResearchMethod_IND:iao_PlanSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["simpleDescriptionUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchMethodSimpleDescriptionUnitIND_URI", user_input:"{simpleDescriptionUnit_uri}"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(researchMethodParthoodBasicUnit_Ind:orkg_ResearchMethodParthoodBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method parthood basicUnit unit", description:"This basicUnit unit models the relation between a particular research method and one of its method parts (i.e. steps).", URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri2", type:"Research_Method_Parthood_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchMethodParthoodBasicUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research method parthood"}})
    CREATE (researchMethodParthoodBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchMethodParthoodBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(ResearchMethodSimpleDescriptionUnit_ind)
    CREATE (ResearchMethodSimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(researchMethod)', operational_KGBB:"true", data_item_type:"simpleDescriptionUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(simpleDescriptionUnitkgbb)
    //MATERIAL ENTITY SIMPLE_DESCRIPTION_UNIT KGBB
    CREATE (materialEntitySimpleDescriptionUnitkgbb:MaterialEntitySimpleDescriptionUnitKGBB:SimpleDescriptionUnitKGBB:KGBB:ClassExpression:Entity {{name:"material entity simpleDescriptionUnit Knowledge Graph Building Block", description:"A simpleDescriptionUnit Knowledge Graph Building Block that manages data about a particular material entity.", URI:"MaterialEntitySimpleDescriptionUnitKGBB_URI", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://purl.obolibrary.org/obo/BFO_0000040"], granularity_tree_key:"material_entity_parthood_granularity_tree_URI", category:"ClassExpression", from_result_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH object_node, parent_data_item_node
    MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    MERGE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(material_entitySimpleDescriptionUnit_ind:orkg_MaterialEntitySimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"material entity simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models all information relating to a particular material entity.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"material_entity_simpleDescriptionUnit_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"MaterialEntitySimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    MERGE (material_entitySimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(material_entity:bfo_MaterialEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["simpleDescriptionUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1MaterialEntitySimpleDescriptionUnitIND_URI", user_input:"{simpleDescriptionUnit_uri}"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(researchResultMaterialEntityRelationBasicUnit_Ind:orkg_ResearchResultMaterialEntityRelationBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result material entity relation basicUnit unit", description:"This basicUnit models the relation between a particular research result and a material entity that it is about.", URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri2", type:"Research_Result_Material_Entity_Relation_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchResultMaterialEntityRelationBasicUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Research result material entity"}})
    CREATE (researchResultMaterialEntityRelationBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchResultMaterialEntityRelationBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(material_entitySimpleDescriptionUnit_ind)
    MERGE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(material_entitySimpleDescriptionUnit_ind)', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(material_entitySimpleDescriptionUnit_ind:orkg_MaterialEntitySimpleDescriptionUnit_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET material_entitySimpleDescriptionUnit_ind.last_updated_on = localdatetime(), material_entitySimpleDescriptionUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, material_entitySimpleDescriptionUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN material_entitySimpleDescriptionUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET material_entitySimpleDescriptionUnit_ind.contributed_by = material_entitySimpleDescriptionUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, material_entitySimpleDescriptionUnit_ind
    MATCH (material_entitySimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(material_entity_old:bfo_MaterialEntity_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, material_entitySimpleDescriptionUnit_ind, material_entity_old
    CALL apoc.refactor.cloneNodesWithRelationships([material_entity_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, material_entitySimpleDescriptionUnit_ind, material_entity_old SET material_entity_old.current_version = "false"
    WITH material_entitySimpleDescriptionUnit_ind
    MATCH (material_entitySimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(material_entity_new:bfo_MaterialEntity_IND {{current_version:"true"}})
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(material_entitySimpleDescriptionUnit_ind:orkg_MaterialEntitySimpleDescriptionUnit_IND {{URI:"{simpleDescriptionUnit_uri}", current_version:"true"}}) SET material_entitySimpleDescriptionUnit_ind.last_updated_on = localdatetime(), material_entitySimpleDescriptionUnit_ind.simpleDescriptionUnit_label = "$_input_name_$ [$_ontology_ID_$]", material_entitySimpleDescriptionUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, material_entitySimpleDescriptionUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN material_entitySimpleDescriptionUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET material_entitySimpleDescriptionUnit_ind.contributed_by = material_entitySimpleDescriptionUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, material_entitySimpleDescriptionUnit_ind
    MATCH (material_entitySimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(material_entity_old:bfo_MaterialEntity_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, material_entitySimpleDescriptionUnit_ind, material_entity_old
    CALL apoc.refactor.cloneNodesWithRelationships([material_entity_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, material_entitySimpleDescriptionUnit_ind, material_entity_old SET material_entity_old.current_version = "false"
    WITH material_entitySimpleDescriptionUnit_ind
    MATCH (material_entitySimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(material_entity_new:bfo_MaterialEntity_IND {{current_version:"true"}})
    SET material_entity_new.name = "$_input_name_$", material_entity_new.instance_label = "$_input_name_$", material_entity_new.ontology_ID = "$_ontology_ID_$", material_entity_new.description = "$_input_description_$", material_entity_new.URI = "new_individual_uri1", material_entity_new.type = "$_input_type_$", material_entity_new.created_on = localdatetime(), material_entity_new.last_updated_on = localdatetime(), material_entity_new.created_by = "{creator}", material_entity_new.contributed_by = ["{creator}"]', from_material_entity_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH object_node, parent_data_item_node
    MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    OPTIONAL MATCH (matEnt1 {{current_version:"true"}})-[:HAS_PART]->(object_node)
    OPTIONAL MATCH (root_simpleDescriptionUnit:orkg_MaterialEntitySimpleDescriptionUnit_IND {{current_version:"true"}})-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(parent_data_item_node)
    OPTIONAL MATCH (GranTree:orkg_MaterialEntityParthoodGranularityTree_IND {{URI:object_node.material_entity_parthood_granularity_tree_URI, current_version:"true"}})
    WITH object_node, parent_data_item_node, entry_node, matEnt1, root_simpleDescriptionUnit, GranTree
    FOREACH (i IN CASE WHEN NOT "{creator}" IN GranTree.contributed_by THEN [1] ELSE [] END |
    SET GranTree.contributed_by = GranTree.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node, matEnt1, root_simpleDescriptionUnit, GranTree
    OPTIONAL MATCH (object_node)-[:HAS_PART]->(matEnt2 {{current_version:"true"}})
    WITH object_node, parent_data_item_node, entry_node, matEnt1, matEnt2, root_simpleDescriptionUnit, GranTree
    MERGE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(material_entitySimpleDescriptionUnit_ind:orkg_MaterialEntitySimpleDescriptionUnit_IND:orkg_SimpleDescriptionUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"material entity simpleDescriptionUnit unit", description:"This simpleDescriptionUnit models all information relating to a particular material entity.", URI:"{simpleDescriptionUnit_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", type:"material_entity_simpleDescriptionUnit_URI", node_type:"simpleDescriptionUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"MaterialEntitySimpleDescriptionUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], simpleDescriptionUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    MERGE (material_entitySimpleDescriptionUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}"}}]->(material_entity:bfo_MaterialEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["simpleDescriptionUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1MaterialEntitySimpleDescriptionUnitIND_URI", user_input:"{simpleDescriptionUnit_uri}"}})
    MERGE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(materialEntityParthoodBasicUnit_Ind:orkg_MaterialEntityParthoodBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"material entity parthood basicUnit unit", description:"This basicUnit models the relation between a particular material entity and its material entity parts.", URI:"new_individual_uri2", basicUnit_URI:"new_individual_uri2", type:"Material_Entity_Parthood_BasicUnit_URI", node_type:"basicUnit", category:"NamedIndividual", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, KGBB_URI:"MaterialEntityParthoodBasicUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], basicUnit_label:"Material entity parthood"}})
    MERGE (materialEntityParthoodBasicUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(object_node)
    MERGE (materialEntityParthoodBasicUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:parent_data_item_node.URI, basicUnit_URI:"new_individual_uri2"}}]->(material_entitySimpleDescriptionUnit_ind)
    MERGE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(material_entity)
    WITH object_node, parent_data_item_node, entry_node, matEnt1, material_entitySimpleDescriptionUnit_ind, material_entity, root_simpleDescriptionUnit, GranTree, matEnt2,  object_node.material_entity_parthood_granularity_tree_URI IS NOT NULL AS Predicate
    FOREACH (i IN CASE WHEN Predicate THEN [1] ELSE [] END |
    SET material_entity.material_entity_parthood_granularity_tree_URI = object_node.material_entity_parthood_granularity_tree_URI
    SET GranTree.last_updated_on = localdatetime()
    )
    WITH object_node, parent_data_item_node, entry_node, matEnt1, material_entitySimpleDescriptionUnit_ind, material_entity, root_simpleDescriptionUnit, GranTree, matEnt2,  object_node.material_entity_parthood_granularity_tree_URI IS NOT NULL AS Predicate
    FOREACH (i IN CASE WHEN matEnt1 IS NOT NULL AND NOT Predicate AND matEnt2 IS NULL THEN [1] ELSE [] END |
    MERGE (root_simpleDescriptionUnit)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", material_entity_parthood_granularity_tree_URI:"new_individual_uri2"}}]->(material_entity_parthood_granTree_ind:orkg_MaterialEntityParthoodGranularityTree_IND:orkg_ParthoodBasedGranularityTree_IND:orkg_GranularityTree_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"material entity parthood granularity tree", URI_property_key:"material_entity_parthood_granularity_tree_URI", description:"This granularity tree models all parthood-related information about a particular material entity.", URI:"new_individual_uri2", type:"MatEnt_Parthood_based_Granularity_tree_URI", node_type:"granularity_tree", category:"NamedIndividual", entry_URI:"{entryURI}", target_KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", object_URI:matEnt1.URI, created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], ontology_ID:"ORKG", instance_label:matEnt1.name + " parthood granularity tree", granularity_tree_label:matEnt1.name + " parthood granularity tree"}})
    MERGE (material_entity_parthood_granTree_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", material_entity_parthood_granularity_tree_URI:"new_individual_uri2"}}]->(matEnt1)
    SET material_entity.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    SET object_node.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    SET matEnt1.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    )
    WITH object_node, parent_data_item_node, entry_node, matEnt1, material_entitySimpleDescriptionUnit_ind, material_entity, root_simpleDescriptionUnit, GranTree, matEnt2,  object_node.material_entity_parthood_granularity_tree_URI IS NOT NULL AS Predicate
    FOREACH (i IN CASE WHEN matEnt2 IS NOT NULL AND NOT Predicate AND matEnt1 IS NULL THEN [1] ELSE [] END |
    MERGE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", material_entity_parthood_granularity_tree_URI:"new_individual_uri2"}}]->(material_entity_parthood_granTree_ind:orkg_MaterialEntityParthoodGranularityTree_IND:orkg_ParthoodBasedGranularityTree_IND:orkg_GranularityTree_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"material entity parthood granularity tree", description:"This granularity tree models all parthood-related information about a particular material entity.", URI:"new_individual_uri2", type:"MatEnt_Parthood_based_Granularity_tree_URI", URI_property_key:"material_entity_parthood_granularity_tree_URI", node_type:"granularity_tree", category:"NamedIndividual", entry_URI:"{entryURI}", target_KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", object_URI:object_node.URI, created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], ontology_ID:"ORKG", instance_label:object_node.name + " parthood granularity tree"}})
    MERGE (material_entity_parthood_granTree_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", material_entity_parthood_granularity_tree_URI:"new_individual_uri2"}}]->(object_node)
    SET material_entity.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    SET object_node.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    SET matEnt2.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    )
    RETURN object_node, matEnt1, matEnt2, material_entitySimpleDescriptionUnit_ind, material_entity', search_cypher_code:"cypherQuery", operational_KGBB:"true", data_item_type:"simpleDescriptionUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(simpleDescriptionUnitkgbb)
    //RESEARCH ACTIVITY OUTPUT RELATION BASIC_UNIT KGBB
    CREATE (researchActivityOutputBasicUnitkgbb:ResearchActivityOuputRelationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"research activity output relation basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research activities and their research result outputs.", relevant_properties_URI:["http://purl.obolibrary.org/obo/OBI_0000299"], relevant_classes_URI:["http://orkg???????1", "http://orkg???????5"], URI:"ResearchActivityOutputRelationBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //RESEARCH ACTIVITY METHOD RELATION BASIC_UNIT KGBB
    CREATE (researchActivityMethodBasicUnitkgbb:ResearchActivityMethodRelationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"research activity method relation basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research activities and the research methods they realize.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000055"], relevant_classes_URI:["http://orkg???????5", "http://orkg???????4"], URI:"ResearchActivityMethodRelationBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //RESEARCH ACTIVITY OBJECTIVE RELATION BASIC_UNIT KGBB
    CREATE (researchActivityObjectiveBasicUnitkgbb:ResearchActivityObjectiveRelationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"research activity objective relation basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research activities and the research objective they achieve.", relevant_properties_URI:["http://purl.obolibrary.org/obo/OBI_0000417"], relevant_classes_URI:["http://orkg???????5", "http://orkg???????3"], URI:"ResearchActivityObjectiveRelationBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //RESEARCH ACTIVITY PARTHOOD BASIC_UNIT KGBB
    CREATE (researchActivityParthoodBasicUnitkgbb:ResearchActivityParthoodRelationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"research activity parthood basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research activities and their activity parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000117"], relevant_classes_URI:["http://orkg???????5"], URI:"ResearchActivityParthoodBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //RESEARCH METHOD PARTHOOD BASIC_UNIT KGBB
    CREATE (researchMethodParthoodBasicUnitkgbb:ResearchMethodParthoodRelationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"research method parthood basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research methods and their method parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????4"], URI:"ResearchMethodParthoodBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //RESEARCH METHOD OBJECTIVE RELATION BASIC_UNIT KGBB
    CREATE (researchMethodObjectiveRelationBasicUnitkgbb:ResearchMethodObjectiveRelationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"research method objective relation basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research methods and their research objective parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????4", "http://orkg???????3"], URI:"ResearchMethodObjectiveRelationBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //RESEARCH METHOD ACTIVITY RELATION BASIC_UNIT KGBB
    CREATE (researchMethodActivityRelationBasicUnitkgbb:ResearchMethodActivityRelationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"research method activity relation basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research methods and the research activities that realize them.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000055"], relevant_classes_URI:["http://orkg???????4", "http://orkg???????5"], URI:"ResearchMethodActivityRelationBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //RESEARCH RESULT PARTHOOD BASIC_UNIT KGBB
    CREATE (researchResultParthoodBasicUnitkgbb:ResearchResultParthoodRelationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"research result parthood basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research results and their result parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????1"], URI:"ResearchResultParthoodBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //RESEARCH RESULT ACTIVITY RELATION BASIC_UNIT KGBB
    CREATE (researchResultActivityRelationBasicUnitkgbb:ResearchResultActivityRelationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"research result activity relation basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research results and the research activities that have them as their output.", relevant_properties_URI:["http://purl.obolibrary.org/obo/OBI_0000299"], relevant_classes_URI:["http://orkg???????1", "http://orkg???????5"], URI:"ResearchResultActivityRelationBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //RESEARCH RESULT OBJECTIVE RELATION BASIC_UNIT KGBB
    CREATE (researchResultObjectiveRelationBasicUnitkgbb:ResearchResultObjectiveRelationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"research result objective relation basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research results and the research objectives that achieved them.", relevant_properties_URI:["http://orkg_has_achieved_result"], relevant_classes_URI:["http://orkg???????1", "http://orkg???????3"], URI:"ResearchResultObjectiveRelationBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //RESEARCH OBJECTIVE PARTHOOD BASIC_UNIT KGBB
    CREATE (researchObjectiveParthoodBasicUnitkgbb:ResearchObjectiveParthoodRelationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"research objective parthood basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research objectives and their objective parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????3"], URI:"ResearchObjectiveParthoodBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //RESEARCH OBJECTIVE METHOD RELATION BASIC_UNIT KGBB
    CREATE (researchObjectiveMethodRelationBasicUnitkgbb:ResearchObjectiveMethodRelationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"research objective method relation basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research objectives and the research methods they are part of.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????3", "http://orkg???????4"], URI:"ResearchObjectiveMethodRelationBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //RESEARCH OBJECTIVE ACTIVITY RELATION BASIC_UNIT KGBB
    CREATE (researchObjectiveActivityRelationBasicUnitkgbb:ResearchObjectiveActivityRelationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"research objective activity relation basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research objectives and the reseach activities that achieve them.", relevant_properties_URI:["http://purl.obolibrary.org/obo/OBI_0000417"], relevant_classes_URI:["http://orkg???????5", "http://orkg???????4"], URI:"ResearchObjectiveActivityRelationBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //RESEARCH OBJECTIVE RESULT RELATION BASIC_UNIT KGBB
    CREATE (researchObjectiveResultRelationBasicUnitkgbb:ResearchObjectiveResultRelationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"research objective result relation basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research objectives and the reseach results they achieved.", relevant_properties_URI:["http://orkg_has_achieved_result"], relevant_classes_URI:["http://orkg???????3", "http://orkg???????1"], URI:"ResearchObjectiveResultRelationBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //MATERIAL ENTITY PARTHOOD BASIC_UNIT KGBB
    CREATE (materialEntityParthoodBasicUnitkgbb:MaterialEntityParthoodRelationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"material entity parthood basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between material entities and their material entity parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://purl.obolibrary.org/obo/BFO_0000040"], URI:"MaterialEntityParthoodBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //RESEARCH RESULT MATERIAL ENTITY RELATION BASIC_UNIT KGBB
    CREATE (researchResultMaterialEntityRelationBasicUnitkgbb:ResearchResultMaterialEntityRelationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"research result material entity relation basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research results and the material entities they are about.", relevant_properties_URI:["http://purl.obolibrary.org/obo/IAO_0000136"], relevant_classes_URI:["http://orkg???????1", "http://purl.obolibrary.org/obo/BFO_0000040"], URI:"ResearchResultMaterialEntityRelationBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //QUALITY BASIC_UNIT KGBB
    CREATE (qualitykgbb:QualityIdentificationBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"quality relation identification basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages quality identification basicUnit data.", relevant_properties_URI:["http://purl.obolibrary.org/obo/RO_0000086"], relevant_classes_URI:["http://purl.obolibrary.org/obo/PATO_0000128", "http://purl.obolibrary.org/obo/PATO_0000146", "http://purl.obolibrary.org/obo/PATO_0001756", "http://purl.obolibrary.org/obo/PATO_0000014"], URI:"QualityIdentificationBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "basicUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(QualityBasicUnitind:orkg_QualityRelationIdentificationBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"Quality relation identification basicUnit unit", URI:"{basicUnitURI}", description:"This basicUnit models information about the identification of a particular physical quality of a particular material entity.", type:"Quality_Identification_BasicUnit_URI", object_URI:"new_individual_uri1", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", KGBB_URI:"QualityIdentificationBasicUnitKGBB_URI", node_type:"basicUnit", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", basicUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (QualityBasicUnitind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(object_node)
    CREATE (object_node)-[:HAS_QUALITY {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/RO_0000086", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}", description:"a relation between an independent continuant (the bearer) and a quality, in which the quality specifically depends on the bearer for its existence."}}]->(quality:pato_PhysicalQuality_IND:pato_Quality_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["basicUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1QualityBasicUnitIND_URI", user_input:"{basicUnitURI}"}})', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "simpleDescriptionUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(QualityBasicUnitind:orkg_QualityRelationIdentificationBasicUnit_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET QualityBasicUnitind.last_updated_on = localdatetime(), QualityBasicUnitind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, QualityBasicUnitind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN QualityBasicUnitind.contributed_by THEN [1] ELSE [] END |
    SET QualityBasicUnitind.contributed_by = QualityBasicUnitind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, QualityBasicUnitind
    MATCH (object_node)-[:HAS_QUALITY]->(quality_old:pato_PhysicalQuality_IND {{current_version:"true", basicUnit_URI:QualityBasicUnitind.URI}})
    WITH parent_data_item_node, object_node, QualityBasicUnitind, quality_old
    CALL apoc.refactor.cloneNodesWithRelationships([quality_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, QualityBasicUnitind, quality_old SET quality_old.current_version = "false"
    WITH object_node, parent_data_item_node, QualityBasicUnitind
    MATCH (object_node)-[:HAS_QUALITY]->(quality_new:pato_PhysicalQuality_IND {{current_version:"true", basicUnit_URI:QualityBasicUnitind.URI}})
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "basicUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(QualityBasicUnitind:orkg_QualityRelationIdentificationBasicUnit_IND {{URI:"{basicUnitURI}", current_version:"true"}}) SET QualityBasicUnitind.last_updated_on = localdatetime(), QualityBasicUnitind.basicUnit_label = "$_input_name_$ [$_ontology_ID_$]", QualityBasicUnitind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, QualityBasicUnitind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN QualityBasicUnitind.contributed_by THEN [1] ELSE [] END |
    SET QualityBasicUnitind.contributed_by = QualityBasicUnitind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, QualityBasicUnitind
    MATCH (object_node)-[:HAS_QUALITY]->(quality_old:pato_PhysicalQuality_IND {{current_version:"true", basicUnit_URI:"{basicUnitURI}"}})
    WITH parent_data_item_node, object_node, QualityBasicUnitind, quality_old
    CALL apoc.refactor.cloneNodesWithRelationships([quality_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, QualityBasicUnitind, quality_old SET quality_old.current_version = "false"
    WITH object_node, parent_data_item_node
    MATCH (object_node)-[:HAS_QUALITY]->(quality_new:pato_PhysicalQuality_IND {{current_version:"true", basicUnit_URI:"{basicUnitURI}"}})
    SET quality_new.name = "$_input_name_$", quality_new.instance_label = "$_input_name_$", quality_new.ontology_ID = "$_ontology_ID_$", quality_new.description = "$_input_description_$", quality_new.URI = "new_individual_uri1", quality_new.type = "$_input_type_$", quality_new.created_on = localdatetime(), quality_new.last_updated_on = localdatetime(), quality_new.created_by = "{creator}", quality_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    CREATE (measurementkgbb:MeasurementBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"measurement basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages measurement basicUnit data.", URI:"MeasurementBasicUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    //WEIGHT MEASUREMENT BASIC_UNIT KGBB
    CREATE (weightkgbb:WeightMeasurementBasicUnitKGBB:MeasurementBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"weight measurement basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages weight measurement basicUnit data.", URI:"WeightMeasurementBasicUnitKGBB_URI", relevant_classes_URI:["http://purl.obolibrary.org/obo/PATO_0000128"], relevant_properties_URI:["http://purl.obolibrary.org/obo/IAO_0000004", "http://purl.obolibrary.org/obo/IAO_0000039", "http://purl.obolibrary.org/obo/OBI_0001938", "http://purl.obolibrary.org/obo/IAO_0000417"], category:"ClassExpression", operational_KGBB:"true", weight_measurement_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "basicUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(WeightMeasurementBasicUnitind:orkg_WeightMeasurementBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"Weight measurement basicUnit unit", URI:"{basicUnitURI}", description:"This basicUnit models information about a particular weight measurement of a particular material entity.", type:"weight_measurement_basicUnit_URI", object_URI:"new_individual_uri1", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", KGBB_URI:"WeightMeasurementBasicUnitKGBB_URI", node_type:"basicUnit", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", basicUnit_label:"$_input_value_$ $_input_name_$ [$_ontology_ID_$]"}})
    CREATE (WeightMeasurementBasicUnitind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(object_node)
    CREATE (object_node)-[:IS_QUALITY_MEASURED_AS {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000417", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}", description:"inverse of the relation of is quality measurement of, which is: m is a quality measurement of q at t. When q is a quality, there is a measurement process p that has specified output m, a measurement datum, that is about q."}}]->(scalarmeasdatum:iao_ScalarMeasurementDatum_IND:iao_MeasurementDatum_IND:iao_data_item_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"http://purl.obolibrary.org/obo/IAO_0000032", name:"iao scalar measurement datum", description:"A scalar measurement datum is a measurement datum that is composed of two parts, numerals and a unit label.", current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (scalarmeasdatum)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(scalarvaluespec:obi_ScalarValueSpecification_IND:obi_ValueSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri2", type:"http://purl.obolibrary.org/obo/OBI_0001931", name:"obi scalar value specification", description:"A value specification that consists of two parts: a numeral and a unit label.", current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (scalarvaluespec)-[:SPECIFIES_VALUE_OF {{category:"ObjectPropertyExpression", description:"A relation between a value specification and an entity which the specification is about.", URI:"http://purl.obolibrary.org/obo/OBI_0001927", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(object_node)
    CREATE (scalarvaluespec)-[:HAS_MEASUREMENT_UNIT_LABEL {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000039", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(weightUnit:uo_GramBasedUnit_IND:NamedIndividual:Entity {{URI:"new_individual_uri3", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["input2"], entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input2", input_version_ID:0, inputVariable:2, input_info_URI:"InputInfo2WeightMeasurementBasicUnitIND_URI", user_input:"{basicUnitURI}"}})
    CREATE (scalarvaluespec)-[:HAS_MEASUREMENT_VALUE {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000004", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(weightValue:Value_IND:Literal_IND:NamedIndividual:Entity {{URI:"new_individual_uri4", type:"orkg_value_URI", name:"$_input_value_$", description:"The value of a weight measurement", data_node_type:["input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1WeightMeasurementBasicUnitIND_URI", user_input:"{basicUnitURI}", value:"$_input_value_$", data_type:"xsd:float"}})', edit_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "basicUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (WeightMeasurementBasicUnitind:orkg_WeightMeasurementBasicUnit_IND {{URI:"{basicUnitURI}", current_version:"true"}}) SET WeightMeasurementBasicUnitind.last_updated_on = localdatetime(), WeightMeasurementBasicUnitind.basicUnit_label = "$_input_name_$ [$_ontology_ID_$]"
    WITH parent_data_item_node, object_node, WeightMeasurementBasicUnitind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN WeightMeasurementBasicUnitind.contributed_by THEN [1] ELSE [] END |
    SET WeightMeasurementBasicUnitind.contributed_by = WeightMeasurementBasicUnitind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, WeightMeasurementBasicUnitind
    MATCH (scalarValueSpecification:obi_ScalarValueSpecification_IND {{current_version:"true", basicUnit_URI:WeightMeasurementBasicUnitind.URI}})-[:HAS_MEASUREMENT_UNIT_LABEL {{basicUnit_URI:WeightMeasurementBasicUnitind.URI}}]->(weightUnit_old:uo_GramBasedUnit_IND {{current_version:"true", basicUnit_URI:WeightMeasurementBasicUnitind.URI}})
    WITH scalarValueSpecification, parent_data_item_node, object_node, WeightMeasurementBasicUnitind, weightUnit_old
    CALL apoc.refactor.cloneNodesWithRelationships([weightUnit_old])
    YIELD input, output
    WITH scalarValueSpecification, parent_data_item_node, object_node, WeightMeasurementBasicUnitind, weightUnit_old SET weightUnit_old.current_version = "false"
    WITH scalarValueSpecification, parent_data_item_node, object_node, WeightMeasurementBasicUnitind
    MATCH (scalarValueSpecification)-[:HAS_MEASUREMENT_UNIT_LABEL {{basicUnit_URI:WeightMeasurementBasicUnitind.URI}}]->(weightUnit_new:uo_GramBasedUnit_IND {{current_version:"true", basicUnit_URI:WeightMeasurementBasicUnitind.URI}})
    SET weightUnit_new.name = "$_input_name_$", weightUnit_new.instance_label = "$_input_name_$", weightUnit_new.ontology_ID = "$_ontology_ID_$", weightUnit_new.description = "$_input_description_$", weightUnit_new.URI = "new_individual_uri1", weightUnit_new.type = "$_input_type_$", weightUnit_new.created_on = localdatetime(), weightUnit_new.last_updated_on = localdatetime(), weightUnit_new.created_by = "{creator}", weightUnit_new.contributed_by = ["{creator}"]
    WITH scalarValueSpecification, parent_data_item_node, object_node, WeightMeasurementBasicUnitind
    MATCH (scalarValueSpecification)-[:HAS_MEASUREMENT_VALUE {{basicUnit_URI:WeightMeasurementBasicUnitind.URI}}]->(weightValue_old:Value_IND {{current_version:"true",basicUnit_URI:WeightMeasurementBasicUnitind.URI}})
    WITH scalarValueSpecification, parent_data_item_node, object_node, WeightMeasurementBasicUnitind, weightValue_old
    CALL apoc.refactor.cloneNodesWithRelationships([weightValue_old])
    YIELD input, output
    WITH scalarValueSpecification, parent_data_item_node, object_node, WeightMeasurementBasicUnitind, weightValue_old SET weightValue_old.current_version = "false"
    WITH scalarValueSpecification, WeightMeasurementBasicUnitind
    MATCH (scalarValueSpecification)-[:HAS_MEASUREMENT_VALUE {{basicUnit_URI:WeightMeasurementBasicUnitind.URI}}]->(weightValue_new:Value_IND {{current_version:"true", basicUnit_URI:WeightMeasurementBasicUnitind.URI}})
    SET weightValue_new.name = "$_input_value_$", weightValue_new.value = "$_input_value_$", weightValue_new.URI = "new_individual_uri2", weightValue_new.created_on = localdatetime(), weightValue_new.last_updated_on = localdatetime(), weightValue_new.created_by = "{creator}", weightValue_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(measurementkgbb)
    //R0 MEASUREMENT BASIC_UNIT KGBB
    CREATE (R0Measurementkgbb:BasicReproductionNumberMeasurementBasicUnitKGBB:MeasurementBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"basic reproduction number measurement basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages basic reprodcution number measurement basicUnit data.", URI:"R0MeasurementBasicUnitKGBB_URI", relevant_classes_URI:["http://purl.obolibrary.org/obo/OMIT_0024604", "http://purl.obolibrary.org/obo/STATO_0000196", "http://purl.obolibrary.org/obo/STATO_0000315", "http://purl.obolibrary.org/obo/STATO_0000314", "http://purl.obolibrary.org/obo/STATO_0000561"], relevant_properties_URI:["http://purl.obolibrary.org/obo/IAO_0000004", "http://purl.obolibrary.org/obo/IAO_0000039", "http://purl.obolibrary.org/obo/OBI_0001938", "http://purl.obolibrary.org/obo/IAO_0000417"], category:"ClassExpression", operational_KGBB:"true", r0_measurement_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "basicUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(r0MeasurementBasicUnitind:orkg_BasicReproductionNumberMeasurementBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"R0 measurement basicUnit unit", URI:"{basicUnitURI}", description:"This basicUnit models information about a particular basic reproduction number measurement of a particular population.", type:"r0_measurement_basicUnit_URI", object_URI:"new_individual_uri1", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", KGBB_URI:"R0MeasurementBasicUnitKGBB_URI", node_type:"basicUnit", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", basicUnit_label:"R0: $_input_value_$ ($_input_value1_$ - $_input_value2_$)"}})
    CREATE (r0MeasurementBasicUnitind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(object_node)
    CREATE (object_node)-[:IS_QUALITY_MEASURED_AS {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000417", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}", description:"inverse of the relation of is quality measurement of, which is: m is a quality measurement of q at t. When q is a quality, there is a measurement process p that has specified output m, a measurement datum, that is about q."}}]->(scalarmeasdatum:iao_ScalarMeasurementDatum_IND:iao_MeasurementDatum_IND:iao_data_item_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"http://purl.obolibrary.org/obo/IAO_0000032", name:"iao scalar measurement datum", description:"A scalar measurement datum is a measurement datum that is composed of two parts, numerals and a unit label.", current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (scalarmeasdatum)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(scalarvaluespec:obi_ScalarValueSpecification_IND:obi_ValueSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri2", type:"http://purl.obolibrary.org/obo/OBI_0001931", name:"obi scalar value specification", description:"A value specification that consists of two parts: a numeral and a unit label.", current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (scalarvaluespec)-[:SPECIFIES_VALUE_OF {{category:"ObjectPropertyExpression", description:"A relation between a value specification and an entity which the specification is about.", URI:"http://purl.obolibrary.org/obo/OBI_0001927", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(object_node)
    CREATE (scalarvaluespec)-[:HAS_MEASUREMENT_UNIT_LABEL {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000039", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(r0countUnit:uo_CountUnit_IND:uo_DimensionlessUnit_IND:uo_Unit_IND:NamedIndividual:Entity {{URI:"new_individual_uri3", type:"http://purl.obolibrary.org/obo/UO_0000189", name:"count unit", ontology_ID:"UO", description:"A dimensionless unit which denotes a simple count of things. [MGED:MGED]", current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (scalarvaluespec)-[:HAS_MEASUREMENT_VALUE {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000004", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(r0Value:Value_IND:Literal_IND:NamedIndividual:Entity {{URI:"new_individual_uri4", type:"orkg_value_URI", name:"$_input_value_$", description:"The value of a basic reproduction number measurement", data_node_type:["input1"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1R0MeasurementBasicUnitIND_URI", user_input:"{basicUnitURI}", value:"$_input_value_$", data_type:"xsd:float"}})
    CREATE (scalarmeasdatum)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(confInterval:stato_ConfidenceInterval_IND:NamedIndividual:Entity {{URI:"new_individual_uri5", type:"http://purl.obolibrary.org/obo/STATO_0000196", name:"stato confidence interval", description:"A confidence interval is a data item which defines an range of values in which a measurement or trial falls corresponding to a given probability.", current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (confInterval)-[:HAS_PART {{category:"ObjectPropertyExpression", description:"a core relation that holds between a whole and its part.", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(upperconflimit:stato_UpperConfidenceLimit_IND:NamedIndividual:Entity {{URI:"new_individual_uri6", type:"http://purl.obolibrary.org/obo/STATO_0000314", name:"stato upper confidence limit", description:"Upper confidence limit is a data item which is a largest value bounding a confidence interval.", current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (upperconflimit)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(upperscalarvaluespec:obi_ScalarValueSpecification_IND:obi_ValueSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri8", type:"http://purl.obolibrary.org/obo/OBI_0001931", name:"obi scalar value specification", description:"A value specification that consists of two parts: a numeral and a unit label.", current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (confInterval)-[:HAS_PART {{category:"ObjectPropertyExpression", description:"a core relation that holds between a whole and its part.", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(lowerconflimit:stato_LowerConfidenceLimit_IND:NamedIndividual:Entity {{URI:"new_individual_uri7", type:"http://purl.obolibrary.org/obo/STATO_0000315", name:"stato lower confidence limit", description:"Lower confidence limit is a data item which is a lowest value bounding a confidence interval.", current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (lowerconflimit)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(lowerscalarvaluespec:obi_ScalarValueSpecification_IND:obi_ValueSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri9", type:"http://purl.obolibrary.org/obo/OBI_0001931", name:"obi scalar value specification", description:"A value specification that consists of two parts: a numeral and a unit label.", current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (lowerscalarvaluespec)-[:HAS_MEASUREMENT_UNIT_LABEL {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000039", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(lowerCountUnit:uo_CountUnit_IND:uo_DimensionlessUnit_IND:uo_Unit_IND:NamedIndividual:Entity {{URI:"new_individual_uri12", type:"http://purl.obolibrary.org/obo/UO_0000189", name:"count unit", ontology_ID:"UO", description:"A dimensionless unit which denotes a simple count of things. [MGED:MGED]", current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (upperscalarvaluespec)-[:HAS_MEASUREMENT_UNIT_LABEL {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000039", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(upperCountUnit:uo_CountUnit_IND:uo_DimensionlessUnit_IND:uo_Unit_IND:NamedIndividual:Entity {{URI:"new_individual_uri11", type:"http://purl.obolibrary.org/obo/UO_0000189", name:"count unit", ontology_ID:"UO", description:"A dimensionless unit which denotes a simple count of things. [MGED:MGED]", current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (upperscalarvaluespec)-[:HAS_MEASUREMENT_VALUE {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000004", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(upperValue:Value_IND:Literal_IND:NamedIndividual:Entity {{URI:"new_individual_uri13", type:"orkg_value_URI", name:"$_input_value2_$", description:"The value of the upper confidence limit of a basic reproduction number measurement", data_node_type:["input2"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input2", input_version_ID:0, inputVariable:2, input_info_URI:"InputInfo2UpperConfLimitR0MeasurementBasicUnitIND_URI", user_input:"{basicUnitURI}", value:"$_input_value2_$", data_type:"xsd:float"}})
    CREATE (lowerscalarvaluespec)-[:HAS_MEASUREMENT_VALUE {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000004", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(lowerValue:Value_IND:Literal_IND:NamedIndividual:Entity {{URI:"new_individual_uri14", type:"orkg_value_URI", name:"$_input_value1_$", description:"The value of the lower confidence limit of a basic reproduction number measurement", data_node_type:["input3"], current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input3", input_version_ID:0, inputVariable:3, input_info_URI:"InputInfo3LowerConfLimitR0MeasurementBasicUnitIND_URI", user_input:"{basicUnitURI}", value:"$_input_value1_$", data_type:"xsd:float"}})
    CREATE (confInterval)-[:HAS_PART {{category:"ObjectPropertyExpression", description:"a core relation that holds between a whole and its part.", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(conflevel:stato_ConfidenceLevel_IND:NamedIndividual:Entity {{URI:"new_individual_uri15", type:"http://purl.obolibrary.org/obo/STATO_0000561", name:"stato confidence level", description:"The frequency (i.e., the proportion) of possible confidence intervals that contain the true value of their corresponding parameter. In other words, if confidence intervals are constructed using a given confidence level in an infinite number of independent experiments, the proportion of those intervals that contain the true value of the parameter will match the confidence level. A probability measure of the reliability of an inferential statistical test that has been applied to sample data and which is provided along with the confidence interval for the output statistic.", current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (conflevel)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(conflevelscalarvaluespec:obi_ScalarValueSpecification_IND:obi_ValueSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri16", type:"http://purl.obolibrary.org/obo/OBI_0001931", name:"obi scalar value specification", description:"A value specification that consists of two parts: a numeral and a unit label.", current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (conflevelscalarvaluespec)-[:HAS_MEASUREMENT_VALUE {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000004", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(conflevelValue:Value_IND:Literal_IND:NamedIndividual:Entity {{URI:"new_individual_uri17", type:"orkg_value_URI", name:"95", description:"The value of the confidence level of a basic reproduction number measurement", current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", value:"95"}})
    CREATE (conflevelscalarvaluespec)-[:HAS_MEASUREMENT_UNIT_LABEL {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000039", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnitURI}"}}]->(percent:uo_Percent_IND:uo_Ratio_IND:uo_DimensionlessUnit_IND:uo_Unit_IND:NamedIndividual:Entity {{URI:"new_individual_uri18", type:"http://purl.obolibrary.org/obo/UO_0000187", name:"percent", ontology_ID:"UO", description:"A dimensionless ratio unit which denotes numbers as fractions of 100.", current_version:"true", entry_URI:"{entryURI}", simpleDescriptionUnit_URI:["{simpleDescriptionUnit_uri}"], basicUnit_URI:"{basicUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})', edit_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "basicUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (r0MeasurementBasicUnitind:orkg_BasicReproductionNumberMeasurementBasicUnit_IND {{URI:"{basicUnitURI}", current_version:"true"}}) SET r0MeasurementBasicUnitind.last_updated_on = localdatetime(), r0MeasurementBasicUnitind.basicUnit_label = "R0: $_input_value_$ ($_input_value1_$ - $_input_value2_$)"
    WITH parent_data_item_node, object_node, r0MeasurementBasicUnitind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN r0MeasurementBasicUnitind.contributed_by THEN [1] ELSE [] END |
    SET r0MeasurementBasicUnitind.contributed_by = r0MeasurementBasicUnitind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, r0MeasurementBasicUnitind
    MATCH (r0Value_old:Value_IND {{current_version:"true", basicUnit_URI:r0MeasurementBasicUnitind.URI, input_source:"input1"}})
    WITH parent_data_item_node, object_node, r0MeasurementBasicUnitind, r0Value_old
    CALL apoc.refactor.cloneNodesWithRelationships([r0Value_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, r0MeasurementBasicUnitind, r0Value_old SET r0Value_old.current_version = "false"
    WITH parent_data_item_node, object_node, r0MeasurementBasicUnitind
    MATCH (r0Value_new:Value_IND {{current_version:"true", basicUnit_URI:r0MeasurementBasicUnitind.URI, input_source:"input1"}})
    SET r0Value_new.value = "$_input_value_$", r0Value_new.name = "$_input_value_$", r0Value_new.URI = "new_individual_uri1", r0Value_new.created_on = localdatetime(), r0Value_new.last_updated_on = localdatetime(), r0Value_new.created_by = "{creator}", r0Value_new.contributed_by = ["{creator}"]
    WITH parent_data_item_node, object_node, r0MeasurementBasicUnitind
    MATCH (upperValue_old:Value_IND {{current_version:"true", basicUnit_URI:r0MeasurementBasicUnitind.URI, input_source:"input2"}})
    WITH parent_data_item_node, object_node, upperValue_old, r0MeasurementBasicUnitind
    CALL apoc.refactor.cloneNodesWithRelationships([upperValue_old])
    YIELD input, output
    WITH r0MeasurementBasicUnitind, parent_data_item_node, object_node, upperValue_old SET upperValue_old.current_version = "false"
    WITH parent_data_item_node, object_node, r0MeasurementBasicUnitind
    MATCH (upperValue_new:Value_IND {{current_version:"true", basicUnit_URI:r0MeasurementBasicUnitind.URI, input_source:"input2"}})
    SET upperValue_new.value = "$_input_value2_$", upperValue_new.name = "$_input_value2_$", upperValue_new.URI = "new_individual_uri2", upperValue_new.created_on = localdatetime(), upperValue_new.last_updated_on = localdatetime(), upperValue_new.created_by = "{creator}", upperValue_new.contributed_by = ["{creator}"]
    WITH parent_data_item_node, object_node, r0MeasurementBasicUnitind
    MATCH (lowerValue_old:Value_IND {{current_version:"true", basicUnit_URI:r0MeasurementBasicUnitind.URI, input_source:"input3"}})
    WITH parent_data_item_node, object_node, lowerValue_old, r0MeasurementBasicUnitind
    CALL apoc.refactor.cloneNodesWithRelationships([lowerValue_old])
    YIELD input, output
    WITH parent_data_item_node, r0MeasurementBasicUnitind, object_node, lowerValue_old SET lowerValue_old.current_version = "false"
    WITH parent_data_item_node, r0MeasurementBasicUnitind, object_node
    MATCH (lowerValue_new:Value_IND {{current_version:"true", basicUnit_URI:r0MeasurementBasicUnitind.URI, input_source:"input3"}})
    SET lowerValue_new.value = "$_input_value1_$", lowerValue_new.name = "$_input_value1_$", lowerValue_new.URI = "new_individual_uri3", lowerValue_new.created_on = localdatetime(), lowerValue_new.last_updated_on = localdatetime(), lowerValue_new.created_by = "{creator}", lowerValue_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(measurementkgbb)
    //RESEARCH TOPIC BASIC_UNIT KGBB
    CREATE (researchTopicBasicUnitKGBB:orkg_ResearchTopicBasicUnitKGBB:BasicUnitKGBB:KGBB:ClassExpression:Entity {{name:"research topic basicUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages basicUnits about the relation between orkg research papers and the research topics they cover.", URI:"ResearchTopicBasicUnitKGBB_URI", relevant_classes_URI:["http://orkg/researchtopic_1", "http://orkg???????2"], relevant_properties_URI:["http://edamontology.org/has_topic"], category:"ClassExpression", KGBB_URI:"ResearchTopicBasicUnitKGBB_URI", search_cypher_code:"some query", research_topic_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "basicUnit_object"
    WITH parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", basicUnit_URI:"{basicUnitURI}"}}]->(researchTopicBasicUnitind:orkg_ResearchTopicBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"Research topic basicUnit unit", description:"This basicUnit models information about a particular research topic of a particular research paper.", URI:"{basicUnitURI}", type:"ResearchTopicBasicUnit_URI", object_URI:object_node.URI, entry_URI:"{entryURI}", KGBB_URI:"ResearchTopicBasicUnitKGBB_URI", node_type:"basicUnit", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", basicUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (object_node)-[:HAS_TOPIC {{category:"ObjectPropertyExpression", description:"Subject A can be any concept or entity outside of an ontology (or an ontology concept in a role of an entity being semantically annotated). Object B can either be a concept that is a Topic, or in unexpected cases an entity outside of an ontology that is a Topic or is in the role of a Topic. In EDAM, only has_topic is explicitly defined between EDAM concepts (Operation or Data has_topic Topic). The inverse, is_topic_of, is not explicitly defined. A has_topic B defines for the subject A, that it has the object B as its topic (A is in the scope of a topic B).", URI:"http://edamontology.org/has_topic", entry_URI:"{entryURI}", basicUnit_URI:"{basicUnitURI}"}}]->(researchTopicind:orkg_orkg_ResearchTopic_IND:edam_Topic_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", URI:"new_individual_uri1", entry_URI:"{entryURI}", basicUnit_URI:"{basicUnitURI}", data_node_type:"input1", type:"$_input_type_$", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchTopicBasicUnitIND_URI", user_input:"{basicUnitURI}"}})
    CREATE (researchTopicBasicUnitind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", basicUnit_URI:"{basicUnitURI}"}}]->(object_node)', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "basicUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(researchTopicBasicUnitind:orkg_ResearchTopicBasicUnit_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET researchTopicBasicUnitind.last_updated_on = localdatetime()
    WITH parent_data_item_node, object_node, researchTopicBasicUnitind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN researchTopicBasicUnitind.contributed_by THEN [1] ELSE [] END |
    SET researchTopicBasicUnitind.contributed_by = researchTopicBasicUnitind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, researchTopicBasicUnitind
    MATCH (object_node)-[:HAS_SIMPLE_DESCRIPTION_UNIT]->(simpleDescriptionUnit_old:orkg_orkg_ResearchTopic_IND {{current_version:"true", basicUnit_URI:researchTopicBasicUnitind.URI}})
    WITH parent_data_item_node, object_node, researchTopicBasicUnitind, simpleDescriptionUnit_old
    CALL apoc.refactor.cloneNodesWithRelationships([simpleDescriptionUnit_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, researchTopicBasicUnitind, simpleDescriptionUnit_old SET simpleDescriptionUnit_old.current_version = "false"
    WITH researchTopicBasicUnitind
    MATCH (object_node)-[:HAS_SIMPLE_DESCRIPTION_UNIT]->(simpleDescriptionUnit_new:orkg_orkg_ResearchTopic_IND {{current_version:"true", basicUnit_URI:researchTopicBasicUnitind.URI}})
    SET simpleDescriptionUnit_new.instance_label = "$_label_name_$", simpleDescriptionUnit_new.URI = "new_individual_uri1", simpleDescriptionUnit_new.created_on = localdatetime(), simpleDescriptionUnit_new.last_updated_on = localdatetime(), simpleDescriptionUnit_new.created_by = "{creator}", simpleDescriptionUnit_new.contributed_by = ["{creator}"]', edit_cypher:' MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
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
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "basicUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(researchTopicBasicUnitind:orkg_ResearchTopicBasicUnit_IND {{URI:"{basicUnitURI}", current_version:"true"}}) SET researchTopicBasicUnitind.last_updated_on = localdatetime(), researchTopicBasicUnitind.basicUnit_label = "$_input_name_$ [$_ontology_ID_$]"
    WITH parent_data_item_node, object_node, researchTopicBasicUnitind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN researchTopicBasicUnitind.contributed_by THEN [1] ELSE [] END |
    SET researchTopicBasicUnitind.contributed_by = researchTopicBasicUnitind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, researchTopicBasicUnitind
    MATCH (object_node)-[:HAS_SIMPLE_DESCRIPTION_UNIT]->(simpleDescriptionUnit_old:orkg_orkg_ResearchTopic_IND {{current_version:"true", basicUnit_URI:researchTopicBasicUnitind.URI}})
    WITH parent_data_item_node, object_node, researchTopicBasicUnitind, simpleDescriptionUnit_old
    CALL apoc.refactor.cloneNodesWithRelationships([simpleDescriptionUnit_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, researchTopicBasicUnitind, simpleDescriptionUnit_old SET simpleDescriptionUnit_old.current_version = "false"
    WITH object_node, researchTopicBasicUnitind
    MATCH (object_node)-[:HAS_SIMPLE_DESCRIPTION_UNIT]->(simpleDescriptionUnit_new:orkg_orkg_ResearchTopic_IND {{current_version:"true", basicUnit_URI:researchTopicBasicUnitind.URI}})
    SET simpleDescriptionUnit_new.instance_label = "$_input_name_$", simpleDescriptionUnit_new.name = "$_input_name_$", simpleDescriptionUnit_new.ontology_ID = "$_ontology_ID_$", simpleDescriptionUnit_new.type = "$_input_type_$", simpleDescriptionUnit_new.description = "$_input_description_$", simpleDescriptionUnit_new.URI = "new_individual_uri1", simpleDescriptionUnit_new.created_on = localdatetime(), simpleDescriptionUnit_new.last_updated_on = localdatetime(), simpleDescriptionUnit_new.created_by = "{creator}", simpleDescriptionUnit_new.contributed_by = ["{creator}"]', operational_KGBB:"true", data_item_type:"basicUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(basicUnitKGBB)
    CREATE (researchTopicBasicUnitKGBB)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(researchTopicBasicUnit)
    //KGBB ELEMENTS
    CREATE (kgbbelement:KGBBElement:ClassExpression:Entity {{name:"Knowledge Graph Building Block element", description:"An element of a Knowledge Graph Building Block. Knowledge Graph Building Block elements are used to specify functionalities of a Knowledge Graph Building Block.", URI:"KGBBElement_URI", category:"ClassExpression"}})
    CREATE (granularityTreeElementKGBBelement:GranularityTreeElementKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Granularity tree element Knowledge Graph Building Block element", description:"A Knowledge Graph Building Block element that connects a simpleDescriptionUnit to a specific type of granularity tree.", URI:"GranularityTreeElementKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (basicUnitElementKGBBelement:BasicUnitElementKGBBElement:KGBBElement:ClassExpression:Entity {{name:"BasicUnit element Knowledge Graph Building Block element", description:"A Knowledge Graph Building Block element that connects a simpleDescriptionUnit to a specific type of basicUnit.", URI:"BasicUnitElementKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (simpleDescriptionUnitElementKGBBelement:SimpleDescriptionUnitElementKGBBElement:KGBBElement:ClassExpression:Entity {{name:"SimpleDescriptionUnit element Knowledge Graph Building Block element", description:"A Knowledge Graph Building Block element that connects an entry to a specific type of simpleDescriptionUnit.", URI:"SimpleDescriptionUnitElementKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (inputInfoKGBBelement:InputInfoKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Input information element", description:"A Knowledge Graph Building Block element that provides input information, i.e. information for the Knowledge Graph Building Block for how to process input from users or from the application.", URI:"InputInfoKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (simpleDescriptionUnitRepresentationKGBBelement:SimpleDescriptionUnitRepresentationKGBBElement:RepresentationKGBBElement:KGBBElement:ClassExpression:Entity {{name:"SimpleDescriptionUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data belonging to the simpleDescriptionUnit in the user interface in a human-readable form using the corresponding simpleDescriptionUnit Knowledge Graph Building Block.", URI:"SimpleDescriptionUnitRepresentationKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (entryRepresentationKGBBelement:EntryRepresentationKGBBElement:RepresentationKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Entry representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data belonging to the entry in the user interface in a human-readable form using the corresponding entry Knowledge Graph Building Block.", URI:"EntryRepresentationKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (containerKGBBelement:ContainerKGBBElement:RepresentationKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Container element", description:"A Knowledge Graph Building Block element that functions as a container to organize and structure information for the front end for representing the data of the simpleDescriptionUnit or basicUnit in the user interface in a human-readable form using the associated Knowledge Graph Building Block.", URI:"ContainerRepresentationKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (exportModelKGBBelement:ExportModelKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Export model element", description:"A Knowledge Graph Building Block element that provides an export model, i.e. information for the application for exporting the data associated with this Knowledge Graph Building Block following a specific standard or data model.", URI:"ExportModelKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (basicUnitRepresentationKGBBelement:BasicUnitRepresentationKGBBElement:RepresentationKGBBElement:KGBBElement:ClassExpression:Entity {{name:"BasicUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the associated basicUnit Knowledge Graph Building Block in the user interface in a human-readable form.", URI:"BasicUnitRepresentationKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (granTreeRepresentationKGBBelement:GranularityTreeRepresentationKGBBElement:RepresentationKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Granularity tree representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the associated granularity perspective Knowledge Graph Building Block in the user interface in a human-readable form.", URI:"GranularityTreeRepresentationKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    // SCHOLARLY PUBLICATION KGBB RELATIONS
    CREATE (scholarlyPublicationEntrykgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(scholarlyPublicationEntry)
    CREATE (scholarlyPublicationEntrykgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of research topic basicUnits in its entry.", KGBB_URI:"ScholarlyPublicationEntryKGBB_URI", target_KGBB_URI:"ResearchTopicBasicUnitKGBB_URI", required:"false", quantity:"m", query_key:"research_topic_cypher_code", basicUnit_object_URI:"object$_$URI", input_results_in:"added_basicUnit"}}]->(researchTopicBasicUnitKGBB)
    CREATE (scholarlyPublicationEntrykgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about the research activity of a particular research paper.", simpleDescriptionUnit_object_URI:"object$_$URI", KGBB_URI:"ScholarlyPublicationEntryKGBB_URI", target_KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", required:"true", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"storage_model_cypher_code" }}]->(ResearchActivitySimpleDescriptionUnitkgbb)
    CREATE (scholarlyPublicationEntrykgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(scholarlyPublicationEntryRepresentation1KGBBelement:ScholarlyPublicationEntryRepresentationKGBBElement_IND:EntryRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Scholarly publication entry representation 1 element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the scholarly publication entry in the user interface in a human-readable form using the scholarly publication entry Knowledge Graph Building Block.", data_view_name:"{data_view_name}", node_type:"entry representation", component:"scholarly_publication_entry", data_item_type_URI:"scholarly_publication_entry_URI",  link_$$$_1:"{{'name':'research_topic_basicUnit_input_info', 'ontology_ID':'EDAM', 'input_restricted_to_subclasses_of':'http://edamontology.org/topic_0003', 'target_KGBB_URI':'ResearchTopicBasicUnitKGBB_URI', 'placeholder_text':'specify the research topic', 'data_item_type':'basicUnit', 'edit_cypher_key':'edit_cypher', 'query_key':'research_topic_cypher_code', 'links_to_component':'research_topic_basicUnit', 'basicUnit_object_URI':'object$_$URI', 'input_results_in':'added_basicUnit', 'edit_results_in':'edited_basicUnit'}}",
    link_$$$_2:"{{'name':'research_overview_simpleDescriptionUnit', 'target_KGBB_URI':'ResearchActivitySimpleDescriptionUnitKGBB_URI', 'data_item_type':'simpleDescriptionUnit', 'query_key':'storage_model_cypher_code', 'links_to_component':'research_activity_simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_results_in':'added_simpleDescriptionUnit'}}", URI:"ScholarlyPublicationEntryRepresentation1KGBBElementIND_URI", type:"EntryRepresentationKGBBElement_URI", KGBB_URI:"ScholarlyPublicationEntryKGBB_URI", category:"NamedIndividual", data_view_information:"true", html:"entry.html"}})
    // RESEARCH ACTIVITY SIMPLE_DESCRIPTION_UNIT KGBB RELATIONS
    CREATE (ResearchActivitySimpleDescriptionUnitkgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(ResActSimpleDescriptionUnit)
    CREATE (ResearchActivitySimpleDescriptionUnitkgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(researchActivitySimpleDescriptionUnitRepresentation1KGBBelement:ResearchActivitySimpleDescriptionUnitRepresentationKGBBElement_IND:SimpleDescriptionUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research activity simpleDescriptionUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing research activity data associated with a research paper entry in the user interface in a human-readable form using the research activity simpleDescriptionUnit Knowledge Graph Building Block.", data_view_name:"{data_view_name}", node_type:"simpleDescriptionUnit representation", URI:"ResearchActivitySimpleDescriptionUnitRepresentation1KGBBElementIND_URI", data_item_type_URI:"ResearchActivity_simpleDescriptionUnit_class_URI",  type:"SimpleDescriptionUnitRepresentationKGBBElement_URI", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", category:"NamedIndividual", data_view_information:"true", simpleDescriptionUnit_html:"research_overview.html", component:"research_activity_simpleDescriptionUnit", link_$$$_1:"{{'name':'research_step_simpleDescriptionUnit_input_info', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/OBI_0000011', 'ontology_ID':'OBI', 'target_KGBB_URI':'ResearchActivitySimpleDescriptionUnitKGBB_URI', 'instantiated_by_basicUnitKGBB':'ResearchActivityParthoodBasicUnitKGBB_URI', 'data_item_type':'simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_results_in':'added_simpleDescriptionUnit', 'edit_results_in':'edited_simpleDescriptionUnit', 'links_to_component':'research_activity_simpleDescriptionUnit', 'query_key':'from_activity_cypher_code', 'edit_cypher_key':'edit_cypher', 'placeholder_text':'specify the type of research activity', 'input_info_URI':'InputInfo1ResearchActivitySimpleDescriptionUnitIND_URI', 'input_source':'input1', 'editable':'true'}}",
    link_$$$_2:"{{'name':'research_result_simpleDescriptionUnit_input_info', 'placeholder_text':'specify the type of research result', 'ontology_ID':'IAO', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000030', 'target_KGBB_URI':'ResearchResultSimpleDescriptionUnitKGBB_URI', 'instantiated_by_basicUnitKGBB':'ResearchActivityOutputRelationBasicUnitKGBB_URI', 'data_item_type':'simpleDescriptionUnit', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_simpleDescriptionUnit', 'query_key':'from_activity_cypher_code', 'links_to_component':'research_result_simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_results_in':'added_simpleDescriptionUnit'}}", link_$$$_3:"{{'name':'research_method_simpleDescriptionUnit_input_info', 'placeholder_text':'specify the type of research method', 'ontology_ID':'MMO,NCIT', 'input_restricted_to_subclasses_of':'', 'target_KGBB_URI':'ResearchMethodSimpleDescriptionUnitKGBB_URI', 'instantiated_by_basicUnitKGBB':'ResearchActivityMethodRelationBasicUnitKGBB_URI', 'data_item_type':'simpleDescriptionUnit', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_simpleDescriptionUnit', 'query_key':'from_activity_cypher_code', 'links_to_component':'research_method_simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_results_in':'added_simpleDescriptionUnit'}}", link_$$$_4:"{{'name':'research_objective_simpleDescriptionUnit_input_info', 'placeholder_text':'specify the type of research objective', 'ontology_ID':'AGRO,IAO,ERO,OBI', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000005', 'target_KGBB_URI':'ResearchObjectiveSimpleDescriptionUnitKGBB_URI', 'instantiated_by_basicUnitKGBB':'ResearchActivityObjectiveRelationBasicUnitKGBB_URI', 'data_item_type':'simpleDescriptionUnit', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_simpleDescriptionUnit', 'query_key':'from_activity_cypher_code', 'links_to_component':'research_objective_simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_results_in':'added_simpleDescriptionUnit'}}"}})
    CREATE (ResearchActivitySimpleDescriptionUnitkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(researchActivityInputInfo1KGBBelement:ResearchActivityInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of research activity simpleDescriptionUnit", description:"User input information 1 for the specification of the research activity resource for a research activity simpleDescriptionUnit.", URI:"InputInfo1ResearchActivitySimpleDescriptionUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", input_name:"research_activity_input", node_type:"input1", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1ResearchActivitySimpleDescriptionUnitIND_URI", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/OBI_0000011", ontology_ID:"OBI", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})
    CREATE (ResearchActivitySimpleDescriptionUnitkgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about a research activity step of a research activity.", simpleDescriptionUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_activity_cypher_code", instantiated_by_basicUnitKGBB:"ResearchActivityParthoodBasicUnitKGBB_URI"}}]->(ResearchActivitySimpleDescriptionUnitkgbb)
    CREATE (ResearchActivitySimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of research activity parthood basicUnits in its entry.", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchActivityParthoodBasicUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_activity_cypher_code", basicUnit_object_URI:"object$_$URI", input_results_in:"added_basicUnit", instantiates_simpleDescriptionUnitKGBB:"ResearchActivitySimpleDescriptionUnitKGBB_URI"}}]->(researchActivityParthoodBasicUnitkgbb)
    CREATE (ResearchActivitySimpleDescriptionUnitkgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about a research result of a research activity.", simpleDescriptionUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", required:"true", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_activity_cypher_code", instantiated_by_basicUnitKGBB:"ResearchActivityOutputRelationBasicUnitKGBB_URI"}}]->(ResearchResultSimpleDescriptionUnitkgbb)
    CREATE (ResearchActivitySimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of research activity output relation basicUnits in its entry.", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchActivityOutputRelationBasicUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_activity_cypher_code", basicUnit_object_URI:"object$_$URI", input_results_in:"added_basicUnit", instantiates_simpleDescriptionUnitKGBB:"ResearchResultSimpleDescriptionUnitKGBB_URI"}}]->(researchActivityOutputBasicUnitkgbb)
    CREATE (ResearchActivitySimpleDescriptionUnitkgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about a research method realized in a research activity.", simpleDescriptionUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", required:"true", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_activity_cypher_code", instantiated_by_basicUnitKGBB:"ResearchActivityMethodRelationBasicUnitKGBB_URI"}}]->(ResearchMethodSimpleDescriptionUnitkgbb)
    CREATE (ResearchActivitySimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of research activity method relation basicUnits in its entry.", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchActivityMethodRelationBasicUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_activity_cypher_code", basicUnit_object_URI:"object$_$URI", input_results_in:"added_basicUnit", instantiates_simpleDescriptionUnitKGBB:"ResearchMethodSimpleDescriptionUnitKGBB_URI"}}]->(researchActivityMethodBasicUnitkgbb)
    CREATE (ResearchActivitySimpleDescriptionUnitkgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about a research objective achieved by a research activity.", simpleDescriptionUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", required:"true", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_activity_cypher_code", instantiated_by_basicUnitKGBB:"ResearchActivityObjectiveRelationBasicUnitKGBB_URI"}}]->(ResearchObjectiveSimpleDescriptionUnitkgbb)
    CREATE (ResearchActivitySimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of research activity objective relation basicUnits in its entry.", KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchActivityObjectiveRelationBasicUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_activity_cypher_code", basicUnit_object_URI:"object$_$URI", input_results_in:"added_basicUnit", instantiates_simpleDescriptionUnitKGBB:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI"}}]->(researchActivityObjectiveBasicUnitkgbb)
    // RESEARCH METHOD SIMPLE_DESCRIPTION_UNIT KGBB RELATIONS
    CREATE (ResearchMethodSimpleDescriptionUnitkgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(ResMethSimpleDescriptionUnit)
    CREATE (ResearchMethodSimpleDescriptionUnitkgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(researchMethodSimpleDescriptionUnitRepresentation1KGBBelement:ResearchMethodSimpleDescriptionUnitRepresentationKGBBElement_IND:SimpleDescriptionUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research method simpleDescriptionUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing research method data associated with a research paper entry in the user interface in a human-readable form using the research method simpleDescriptionUnit Knowledge Graph Building Block.", data_view_name:"{data_view_name}", node_type:"simpleDescriptionUnit representation", URI:"ResearchMethodSimpleDescriptionUnitRepresentation1KGBBElementIND_URI", data_item_type_URI:"ResearchMethod_simpleDescriptionUnit_class_URI",  type:"SimpleDescriptionUnitRepresentationKGBBElement_URI", KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", category:"NamedIndividual", data_view_information:"true", simpleDescriptionUnit_html:"research_method.html", component:"research_method_simpleDescriptionUnit", link_$$$_1:"{{'name':'research_step_simpleDescriptionUnit_input_info', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/OBI_0000011', 'ontology_ID':'OBI', 'target_KGBB_URI':'ResearchActivitySimpleDescriptionUnitKGBB_URI', 'instantiated_by_basicUnitKGBB':'ResearchMethodActivityRelationBasicUnitKGBB_URI', 'data_item_type':'simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_results_in':'added_simpleDescriptionUnit', 'edit_results_in':'edited_simpleDescriptionUnit', 'links_to_component':'research_activity_simpleDescriptionUnit', 'query_key':'from_method_cypher_code', 'edit_cypher_key':'edit_cypher', 'placeholder_text':'specify the type of research activity', 'input_info_URI':'InputInfo1ResearchActivitySimpleDescriptionUnitIND_URI', 'input_source':'input1', 'editable':'true'}}",
    link_$$$_2:"{{'name':'research_method_simpleDescriptionUnit_input_info', 'placeholder_text':'specify the type of research method', 'ontology_ID':'MMO,NCIT', 'input_restricted_to_subclasses_of':'', 'target_KGBB_URI':'ResearchMethodSimpleDescriptionUnitKGBB_URI', 'instantiated_by_basicUnitKGBB':'ResearchMethodParthoodBasicUnitKGBB_URI','data_item_type':'simpleDescriptionUnit', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_simpleDescriptionUnit', 'query_key':'from_method_cypher_code', 'links_to_component':'research_method_simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_results_in':'added_simpleDescriptionUnit'}}", link_$$$_3:"{{'name':'research_objective_simpleDescriptionUnit_input_info', 'placeholder_text':'specify the type of research objective', 'ontology_ID':'AGRO,IAO,ERO,OBI', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000005', 'target_KGBB_URI':'ResearchObjectiveSimpleDescriptionUnitKGBB_URI', 'instantiated_by_basicUnitKGBB':'ResearchMethodObjectiveRelationBasicUnitKGBB_URI', 'data_item_type':'simpleDescriptionUnit', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_simpleDescriptionUnit', 'query_key':'from_method_cypher_code', 'links_to_component':'research_objective_simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_results_in':'added_simpleDescriptionUnit'}}"}})
    CREATE (ResearchMethodSimpleDescriptionUnitkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(researchMethodInputInfo1KGBBelement:ResearchMethodInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of research method simpleDescriptionUnit", description:"User input information 1 for the specification of the research method resource for a research method simpleDescriptionUnit.", URI:"InputInfo1ResearchMethodSimpleDescriptionUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", input_name:"research_method_input", node_type:"input1", KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1ResearchMethodSimpleDescriptionUnitIND_URI", input_restricted_to_subclasses_of:"", ontology_ID:"MMO,NCIT", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})
    CREATE (ResearchMethodSimpleDescriptionUnitkgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about a step of the research method.", simpleDescriptionUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_method_cypher_code", instantiated_by_basicUnitKGBB:"ResearchMethodParthoodBasicUnitKGBB_URI"}}]->(ResearchMethodSimpleDescriptionUnitkgbb)
    CREATE (ResearchMethodSimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of research method parthood basicUnits in its entry.", KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchMethodParthoodBasicUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_method_cypher_code", basicUnit_object_URI:"object$_$URI", input_results_in:"added_basicUnit", instantiates_simpleDescriptionUnitKGBB:"ResearchMethodSimpleDescriptionUnitKGBB_URI"}}]->(researchMethodParthoodBasicUnitkgbb)
    CREATE (ResearchMethodSimpleDescriptionUnitkgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about a research activity that realizes the research method.", simpleDescriptionUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_method_cypher_code", instantiated_by_basicUnitKGBB:"ResearchMethodActivityRelationBasicUnitKGBB_URI"}}]->(ResearchActivitySimpleDescriptionUnitkgbb)
    CREATE (ResearchMethodSimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of research method activity relation basicUnits in its entry.", KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchMethodActivityRelationBasicUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_method_cypher_code", basicUnit_object_URI:"object$_$URI", input_results_in:"added_basicUnit", instantiates_simpleDescriptionUnitKGBB:"ResearchActivitySimpleDescriptionUnitKGBB_URI"}}]->(researchMethodActivityRelationBasicUnitkgbb)
    CREATE (ResearchMethodSimpleDescriptionUnitkgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about a research objective that is part of the research method.", simpleDescriptionUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_method_cypher_code", instantiated_by_basicUnitKGBB:"ResearchMethodObjectiveRelationBasicUnitKGBB_URI"}}]->(ResearchObjectiveSimpleDescriptionUnitkgbb)
    CREATE (ResearchMethodSimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of research method objective relation basicUnits in its entry.", KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchMethodObjectiveRelationBasicUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_method_cypher_code", basicUnit_object_URI:"object$_$URI", input_results_in:"added_basicUnit", instantiates_simpleDescriptionUnitKGBB:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI"}}]->(researchMethodObjectiveRelationBasicUnitkgbb)
    // RESEARCH OBJECTIVE SIMPLE_DESCRIPTION_UNIT KGBB RELATIONS
    CREATE (ResearchObjectiveSimpleDescriptionUnitkgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(ResObjectiveSimpleDescriptionUnit)
    CREATE (ResearchObjectiveSimpleDescriptionUnitkgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(researchObjectiveSimpleDescriptionUnitRepresentation1KGBBelement:ResearchObjectiveSimpleDescriptionUnitRepresentationKGBBElement_IND:SimpleDescriptionUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research objective simpleDescriptionUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing research objective data associated with a research paper entry in the user interface in a human-readable form using the research objective simpleDescriptionUnit Knowledge Graph Building Block.", data_view_name:"{data_view_name}", node_type:"simpleDescriptionUnit representation", URI:"ResearchObjectiveSimpleDescriptionUnitRepresentation1KGBBElementIND_URI", data_item_type_URI:"ResearchObjective_simpleDescriptionUnit_class_URI",  type:"SimpleDescriptionUnitRepresentationKGBBElement_URI", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", category:"NamedIndividual", data_view_information:"true", simpleDescriptionUnit_html:"research_objective.html", component:"research_objective_simpleDescriptionUnit", link_$$$_1:"{{'name':'research_objective_simpleDescriptionUnit_input_info', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000005', 'ontology_ID':'AGRO,IAO,ERO,OBI', 'target_KGBB_URI':'ResearchObjectiveSimpleDescriptionUnitKGBB_URI', 'instantiated_by_basicUnitKGBB':'ResearchObjectiveParthoodBasicUnitKGBB_URI', 'data_item_type':'simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_results_in':'added_simpleDescriptionUnit', 'edit_results_in':'edited_simpleDescriptionUnit', 'links_to_component':'research_objective_simpleDescriptionUnit', 'query_key':'from_objective_cypher_code', 'edit_cypher_key':'edit_cypher', 'placeholder_text':'specify the type of research objective', 'input_info_URI':'InputInfo1ResearchObjectiveSimpleDescriptionUnitIND_URI', 'input_source':'input1', 'editable':'true'}}",
    link_$$$_2:"{{'name':'research_method_simpleDescriptionUnit_input_info', 'placeholder_text':'specify the type of research method', 'ontology_ID':'MMO,NCIT', 'input_restricted_to_subclasses_of':'', 'target_KGBB_URI':'ResearchMethodSimpleDescriptionUnitKGBB_URI', 'instantiated_by_basicUnitKGBB':'ResearchObjectiveMethodRelationBasicUnitKGBB_URI', 'data_item_type':'simpleDescriptionUnit', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_simpleDescriptionUnit', 'query_key':'from_objective_cypher_code', 'links_to_component':'research_method_simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_results_in':'added_simpleDescriptionUnit'}}", link_$$$_3:"{{'name':'research_step_simpleDescriptionUnit_input_info', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/OBI_0000011', 'ontology_ID':'OBI', 'target_KGBB_URI':'ResearchActivitySimpleDescriptionUnitKGBB_URI', 'instantiated_by_basicUnitKGBB':'ResearchObjectiveActivityRelationBasicUnitKGBB_URI', 'data_item_type':'simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_results_in':'added_simpleDescriptionUnit', 'edit_results_in':'edited_simpleDescriptionUnit', 'links_to_component':'research_activity_simpleDescriptionUnit', 'query_key':'from_objective_cypher_code', 'edit_cypher_key':'edit_cypher', 'placeholder_text':'specify the type of research activity', 'input_info_URI':'InputInfo1ResearchActivitySimpleDescriptionUnitIND_URI', 'input_source':'input1', 'editable':'true'}}", link_$$$_4:"{{'name':'research_result_simpleDescriptionUnit_input_info', 'placeholder_text':'specify the type of research result', 'ontology_ID':'IAO', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000030', 'target_KGBB_URI':'ResearchResultSimpleDescriptionUnitKGBB_URI', 'instantiated_by_basicUnitKGBB':'ResearchObjectiveResultRelationBasicUnitKGBB_URI', 'data_item_type':'simpleDescriptionUnit', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_simpleDescriptionUnit', 'query_key':'from_objective_cypher_code', 'links_to_component':'research_result_simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_results_in':'added_simpleDescriptionUnit'}}"}})
    CREATE (ResearchObjectiveSimpleDescriptionUnitkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(researchObjectiveInputInfo1KGBBelement:ResearchObjectiveInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of research objective simpleDescriptionUnit", description:"User input information 1 for the specification of the research objective resource for a research objective simpleDescriptionUnit.", URI:"InputInfo1ResearchObjectiveSimpleDescriptionUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", input_name:"research_objective_input", node_type:"input1", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1ResearchObjectiveSimpleDescriptionUnitIND_URI", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/IAO_0000005", ontology_ID:"AGRO,IAO,ERO,OBI", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})
    CREATE (ResearchObjectiveSimpleDescriptionUnitkgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about a the research method this research objective is a part of.", simpleDescriptionUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchMethodSimpleDescriptionUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_objective_cypher_code", instantiated_by_basicUnitKGBB:"ResearchObjectiveMethodRelationBasicUnitKGBB_URI"}}]->(ResearchMethodSimpleDescriptionUnitkgbb)
    CREATE (ResearchObjectiveSimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of research objective method relation basicUnits in its entry.", basicUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchObjectiveMethodRelationBasicUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_objective_cypher_code", instantiates_simpleDescriptionUnitKGBB:"ResearchMethodSimpleDescriptionUnitKGBB_URI"}}]->(researchObjectiveMethodRelationBasicUnitkgbb)
    CREATE (ResearchObjectiveSimpleDescriptionUnitkgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about a research activity that achieves the research objective.", simpleDescriptionUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_objective_cypher_code", instantiated_by_basicUnitKGBB:"ResearchObjectiveActivityRelationBasicUnitKGBB_URI"}}]->(ResearchActivitySimpleDescriptionUnitkgbb)
    CREATE (ResearchObjectiveSimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of research objective activity relation basicUnits in its entry.", basicUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchObjectiveActivityRelationBasicUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_objective_cypher_code", instantiates_simpleDescriptionUnitKGBB:"ResearchActivitySimpleDescriptionUnitKGBB_URI"}}]->(researchObjectiveActivityRelationBasicUnitkgbb)
    CREATE (ResearchObjectiveSimpleDescriptionUnitkgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about a research result that achieves the research objective.", simpleDescriptionUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_objective_cypher_code", instantiated_by_basicUnitKGBB:"ResearchObjectiveResultRelationBasicUnitKGBB_URI"}}]->(ResearchResultSimpleDescriptionUnitkgbb)
    CREATE (ResearchObjectiveSimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of research objective result relation basicUnits in its entry.", basicUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchObjectiveResultRelationBasicUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_objective_cypher_code", instantiates_simpleDescriptionUnitKGBB:"ResearchResultSimpleDescriptionUnitKGBB_URI"}}]->(researchObjectiveResultRelationBasicUnitkgbb)
    CREATE (ResearchObjectiveSimpleDescriptionUnitkgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about a research objective that is a part of this research objective.", simpleDescriptionUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_objective_cypher_code", instantiated_by_basicUnitKGBB:"ResearchObjectiveParthoodBasicUnitKGBB_URI"}}]->(ResearchObjectiveSimpleDescriptionUnitkgbb)
    CREATE (ResearchObjectiveSimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of research objective parthood basicUnits in its entry.", basicUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchObjectiveParthoodBasicUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_objective_cypher_code", instantiates_simpleDescriptionUnitKGBB:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI"}}]->(ResearchObjectiveSimpleDescriptionUnitkgbb)
    // RESEARCH RESULT SIMPLE_DESCRIPTION_UNIT KGBB RELATIONS
    CREATE (ResearchResultSimpleDescriptionUnitkgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(ResResSimpleDescriptionUnit)
    CREATE (ResearchResultSimpleDescriptionUnitkgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(researchResultSimpleDescriptionUnitRepresentation1KGBBelement:ResearchResultSimpleDescriptionUnitRepresentationKGBBElement_IND:SimpleDescriptionUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research result simpleDescriptionUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing research result data associated with a research paper entry in the user interface in a human-readable form using the research result simpleDescriptionUnit Knowledge Graph Building Block.", data_item_type_URI:"ResearchResult_simpleDescriptionUnit_class_URI", data_view_name:"{data_view_name}", node_type:"simpleDescriptionUnit representation", URI:"ResearchResultSimpleDescriptionUnitRepresentation1KGBBElementIND_URI", type:"SimpleDescriptionUnitRepresentationKGBBElement_URI", KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", category:"NamedIndividual", data_view_information:"true", simpleDescriptionUnit_html:"research_result_simpleDescriptionUnit.html",  component:"research_result_simpleDescriptionUnit", link_$$$_1:"{{'name':'research_activity_simpleDescriptionUnit_input_info', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/OBI_0000011', 'ontology_ID':'OBI', 'edit_results_in':'edited_simpleDescriptionUnit', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'ResearchActivitySimpleDescriptionUnitKGBB_URI', 'instantiated_by_basicUnitKGBB':'ResearchResultActivityRelationBasicUnitKGBB_URI', 'data_item_type':'simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_results_in':'added_simpleDescriptionUnit', 'links_to_component':'research_activity_simpleDescriptionUnit', 'query_key':'from_result_cypher_code', 'placeholder_text':'specify the type of research activity', 'editable':'true'}}",
    link_$$$_2:"{{'name':'research_result_simpleDescriptionUnit_input_info', 'placeholder_text':'specify the type of research result', 'ontology_ID':'IAO', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000030', 'target_KGBB_URI':'ResearchResultSimpleDescriptionUnitKGBB_URI', 'instantiated_by_basicUnitKGBB':'ResearchResultParthoodBasicUnitKGBB_URI', 'input_info_URI':'InputInfo1ResearchResultSimpleDescriptionUnitIND_URI', 'data_item_type':'simpleDescriptionUnit', 'edit_results_in':'edited_simpleDescriptionUnit', 'edit_cypher_key':'edit_cypher', 'query_key':'from_result_cypher_code', 'links_to_component':'research_result_simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_source':'input1', 'input_results_in':'added_simpleDescriptionUnit'}}", link_$$$_3:"{{'name':'material_entity_simpleDescriptionUnit_input_info', 'placeholder_text':'specify the type of material entity', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/BFO_0000040', 'edit_results_in':'edited_simpleDescriptionUnit', 'edit_cypher_key':'edit_cypher', 'ontology_ID':'UBERON,OBI,IDO', 'target_KGBB_URI':'MaterialEntitySimpleDescriptionUnitKGBB_URI', 'instantiated_by_basicUnitKGBB':'ResearchResultMaterialEntityRelationBasicUnitKGBB_URI', 'data_item_type':'simpleDescriptionUnit', 'query_key':'from_result_cypher_code', 'links_to_component':'material_entity_simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_results_in':'added_simpleDescriptionUnit'}}", link_$$$_4:"{{'name':'research_objective_simpleDescriptionUnit_input_info', 'placeholder_text':'specify the type of research objective', 'ontology_ID':'AGRO,IAO,ERO,OBI', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000005', 'target_KGBB_URI':'ResearchObjectiveSimpleDescriptionUnitKGBB_URI', 'instantiated_by_basicUnitKGBB':'ResearchResultObjectiveRelationBasicUnitKGBB_URI', 'data_item_type':'simpleDescriptionUnit', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_simpleDescriptionUnit', 'query_key':'from_result_cypher_code', 'links_to_component':'research_objective_simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_results_in':'added_simpleDescriptionUnit'}}"}})
    CREATE (ResearchResultSimpleDescriptionUnitkgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about a research result documented in a particular research paper.", simpleDescriptionUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", data_view_name:"{data_view_name}", target_KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_result_cypher_code", input_results_in:"added_simpleDescriptionUnit", instantiated_by_basicUnitKGBB:"ResearchResultParthoodBasicUnitKGBB_URI"}}]->(ResearchResultSimpleDescriptionUnitkgbb)
    CREATE (ResearchResultSimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of research result parthood basicUnits in its entry.", basicUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchResultParthoodBasicUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_result_cypher_code", instantiates_simpleDescriptionUnitKGBB:"ResearchResultSimpleDescriptionUnitKGBB_URI"}}]->(researchResultParthoodBasicUnitkgbb)
    CREATE (ResearchResultSimpleDescriptionUnitkgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about a research activity step of a research activity.", simpleDescriptionUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchActivitySimpleDescriptionUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_result_cypher_code", instantiated_by_basicUnitKGBB:"ResearchResultActivityRelationBasicUnitKGBB_URI"}}]->(ResearchActivitySimpleDescriptionUnitkgbb)
    CREATE (ResearchResultSimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of research result activity relation basicUnits in its entry.", basicUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchResultActivityRelationBasicUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_result_cypher_code", instantiates_simpleDescriptionUnitKGBB:"ResearchActivitySimpleDescriptionUnitKGBB_URI"}}]->(researchResultActivityRelationBasicUnitkgbb)
    CREATE (ResearchResultSimpleDescriptionUnitkgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about a particular material entity as it is documented in a particular research paper.", simpleDescriptionUnit_object_URI:"object$_$URI",KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", data_view_name:"{data_view_name}", target_KGBB_URI:"MaterialEntitySimpleDescriptionUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_result_cypher_code", input_results_in:"added_simpleDescriptionUnit", instantiated_by_basicUnitKGBB:"ResearchResultMaterialEntityRelationBasicUnitKGBB_URI"}}]->(materialEntitySimpleDescriptionUnitkgbb)
    CREATE (ResearchResultSimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of research result material entity relation basicUnits in its entry.", basicUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchResultMaterialEntityRelationBasicUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_result_cypher_code", instantiates_simpleDescriptionUnitKGBB:"MaterialEntitySimpleDescriptionUnitKGBB_URI"}}]->(researchResultMaterialEntityRelationBasicUnitkgbb)
    CREATE (ResearchResultSimpleDescriptionUnitkgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about a research objective that is part of the research method.", simpleDescriptionUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_result_cypher_code", instantiated_by_basicUnitKGBB:"ResearchResultObjectiveRelationBasicUnitKGBB_URI"}}]->(ResearchObjectiveSimpleDescriptionUnitkgbb)
    CREATE (ResearchResultSimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of research result objective relation basicUnits in its entry.", basicUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"ResearchResultObjectiveRelationBasicUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_result_cypher_code", instantiates_simpleDescriptionUnitKGBB:"ResearchObjectiveSimpleDescriptionUnitKGBB_URI"}}]->(researchResultObjectiveRelationBasicUnitkgbb)
    CREATE (ResearchResultSimpleDescriptionUnitkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(researchResultInputInfo1KGBBelement:ResearchResultInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of research result simpleDescriptionUnit", input_name:"research_result_input", description:"User input information 1 for the specification of the research result resource for a research result simpleDescriptionUnit.", placeholder_text:"specify the type of research result", URI:"InputInfo1ResearchResultSimpleDescriptionUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"ResearchResultSimpleDescriptionUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1ResearchResultSimpleDescriptionUnitIND_URI", ontology_ID:"IAO", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/IAO_0000030", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})
    // MATERIAL ENTITY SIMPLE_DESCRIPTION_UNIT KGBB RELATIONS
    CREATE (materialEntitySimpleDescriptionUnitkgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(materialEntitySimpleDescriptionUnitRepresentation1KGBBelement:MaterialEntitySimpleDescriptionUnitRepresentationKGBBElement_IND:SimpleDescriptionUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Material entity simpleDescriptionUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing data about a particular material entity from a research paper entry in the user interface in a human-readable form using the material entity simpleDescriptionUnit Knowledge Graph Building Block.", data_view_name:"{data_view_name}", node_type:"simpleDescriptionUnit representation", URI:"MaterialEntitySimpleDescriptionUnitRepresentation1KGBBElementIND_URI", type:"SimpleDescriptionUnitRepresentationKGBBElement_URI", data_item_type_URI:"material_entity_simpleDescriptionUnit_URI",  KGBB_URI:"MaterialEntitySimpleDescriptionUnitKGBB_URI", simpleDescriptionUnit_html:"material_entity_simpleDescriptionUnit.html", category:"NamedIndividual", data_view_information:"true", component:"material_entity_simpleDescriptionUnit", link_$$$_1:"{{'name':'material_entity_simpleDescriptionUnit_input_info', 'placeholder_text':'specify the type of material entity', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/BFO_0000040', 'ontology_ID':'UBERON,OBI,IDO', 'target_KGBB_URI':'MaterialEntitySimpleDescriptionUnitKGBB_URI', 'instantiated_by_basicUnitKGBB':'MaterialEntityParthoodBasicUnitKGBB_URI', 'data_item_type':'simpleDescriptionUnit', 'edit_results_in':'edited_simpleDescriptionUnit', 'edit_cypher_key':'edit_cypher', 'query_key':'from_material_entity_cypher_code', 'links_to_component':'material_entity_simpleDescriptionUnit', 'simpleDescriptionUnit_object_URI':'object$_$URI', 'input_results_in':'added_simpleDescriptionUnit'}}", link_$$$_2:"{{'name':'quality_relation_identification_basicUnit_input_info', 'placeholder_text':'select a quality', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/BFO_0000019', 'ontology_ID':'PATO,OMIT', 'edit_results_in':'edited_basicUnit', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'QualityIdentificationBasicUnitKGBB_URI', 'data_item_type':'basicUnit', 'query_key':'quality_cypher_code', 'links_to_component':'quality_identification_basicUnit', 'basicUnit_object_URI':'object$_$URI', 'input_results_in':'added_basicUnit', 'edit_results_in':'edited_basicUnit'}}", link_$$$_3:"{{'name':'material_entity_parthood_granularity_tree_info', 'target_KGBB_URI':'MatEntparthoodgranperspectiveKGBB', 'data_item_type':'granularity_tree', 'links_to_component':'material_entity_parthood_granularity_tree', 'granularity_tree_object_URI':'object$_$URI'}}"}})
    CREATE (materialEntitySimpleDescriptionUnitkgbb)-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_simpleDescriptionUnit_element_URI", description:"This simpleDescriptionUnit element specifies information about a particular material entity as it is documented in a particular research paper.", simpleDescriptionUnit_object_URI:"object$_$URI", KGBB_URI:"MaterialEntitySimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"MaterialEntitySimpleDescriptionUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_material_entity_cypher_code", input_results_in:"added_simpleDescriptionUnit", instantiated_by_basicUnitKGBB:"MaterialEntityParthoodBasicUnitKGBB_URI"}}]->(materialEntitySimpleDescriptionUnitkgbb)
    CREATE (materialEntitySimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of material entity parthood basicUnits in its entry.", basicUnit_object_URI:"object$_$URI", KGBB_URI:"MaterialEntitySimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"MaterialEntityParthoodBasicUnitKGBB_URI", required:"false", input_results_in:"added_simpleDescriptionUnit", quantity:"m", query_key:"from_material_entity_cypher_code", instantiates_simpleDescriptionUnitKGBB:"MaterialEntitySimpleDescriptionUnitKGBB_URI"}}]->(materialEntityParthoodBasicUnitkgbb)
    CREATE (materialEntitySimpleDescriptionUnitkgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of quality relation identification basicUnits in its simpleDescriptionUnit.", KGBB_URI:"MaterialEntitySimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"QualityIdentificationBasicUnitKGBB_URI", required:"false", quantity:"m", query_key:"quality_cypher_code", basicUnit_object_URI:"object$_$URI", input_results_in:"added_basicUnit"}}]->(qualitykgbb)
    CREATE (materialEntitySimpleDescriptionUnitkgbb)-[:HAS_GRANULARITY_TREE_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_granularity_tree_element_URI", description:"This granularity tree element specifies information about the existence and composition of a parthood-based granularity tree of particular material entities.", KGBB_URI:"MaterialEntitySimpleDescriptionUnitKGBB_URI", target_KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", required:"false", quantity:"m", granularity_tree_object_URI:"object$_$URI"}}]->(MatEntparthoodgranperspectiveKGBB)
    CREATE (materialEntitySimpleDescriptionUnitkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(materialEntityInputInfo1KGBBelement:MaterialEntityInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of material entity simpleDescriptionUnit", input_name:"material_entity_input", description:"User input information 1 for the specification of the material entity resource for a material entity simpleDescriptionUnit.", placeholder_text:"specify the type of material entity", URI:"InputInfo1MaterialEntitySimpleDescriptionUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"MaterialEntitySimpleDescriptionUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1MaterialEntitySimpleDescriptionUnitIND_URI", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/BFO_0000040", ontology_ID:"UBERON,OBI,IDO", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})
    // QUALITY BASIC_UNIT KGBB RELATIONS
    CREATE (qualitykgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(qualityBasicUnitRepresentation1KGBBelement:QualityIdentificationBasicUnitRepresentationKGBBElement_IND:BasicUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Quality relation identification basicUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the identification of a quality relation in the user interface in a human-readable form using the quality relation identification basicUnit Knowledge Graph Building Block.", URI:"QualityBasicUnitRepresentation1KGBBElementIND_URI", data_view_name:"{data_view_name}", node_type:"basicUnit representation", data_item_type_URI:"Quality_Identification_BasicUnit_URI", KGBB_URI:"QualityIdentificationBasicUnitKGBB_URI", category:"NamedIndividual", data_view_information:"true", component:"quality_relation_identification_basicUnit", link_$$$_1:"{{'name':'quality_basicUnit_relation_identification_input_info', 'component':'quality_relation_identification_basicUnit', 'input_info_URI':'InputInfo1QualityBasicUnitIND_URI', 'placeholder_text':'select a type of quality', 'input_source':'input1', 'editable':'true', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/BFO_0000019', 'ontology_ID':'PATO,OMIT', 'edit_results_in':'edited_basicUnit', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'QualityIdentificationBasicUnitKGBB_URI', 'basicUnit_object_URI':'object$_$URI', 'data_item_type':'basicUnit', 'query_key':'quality_cypher_code', 'input_results_in':'added_basicUnit'}}", link_$$$_2:"{{'name':'weight_measurement_basicUnit_input_info', 'placeholder_text_1':'value', 'user_input_data_type':'xsd:float', 'edit_results_in':'edited_basicUnit', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'WeightMeasurementBasicUnitKGBB_URI', 'data_item_type':'basicUnit', 'query_key':'weight_measurement_cypher_code', 'links_to_component':'weight_measurement_basicUnit', 'basicUnit_object_URI':'object$_$URI', 'input_results_in':'added_basicUnit', 'edit_results_in':'edited_basicUnit', 'placeholder_text_2':'select a gram-based unit', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/UO_1000021', 'ontology_ID':'UO'}}", link_$$$_3:"{{'name':'R0_measurement_basicUnit_input_info', 'placeholder_text_1':'value', 'placeholder_text_3':'upper limit', 'placeholder_text_2':'lower limit', 'user_input_data_type':'xsd:float', 'edit_results_in':'edited_basicUnit', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'R0MeasurementBasicUnitKGBB_URI', 'data_item_type':'basicUnit', 'query_key':'r0_measurement_cypher_code', 'links_to_component':'R0_measurement_basicUnit', 'basicUnit_object_URI':'object$_$URI', 'input_results_in':'added_basicUnit', 'edit_results_in':'edited_basicUnit'}}"}})
    CREATE (qualitykgbb)-[:HAS_EXPORT_MODEL {{category:"ObjectPropertyExpression", URI:"orkg_has_export_model_URI"}}]->(qualityexportModel1KGBBelement:ExportModelKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Quality relation identification basicUnit export model 1", description:"A Knowledge Graph Building Block element that provides an export model for identified quality relations. The export model 1 is based on the OBO/OBI data model.", URI:"QualityExportModel1KGBBElementIND_URI", type:"ExportModelKGBBElement_URI", KGBB_URI:"QualityIdentificationBasicUnitKGBB_URI", export_scheme:"OBO", category:"NamedIndividual", export_model_cypher_code:"cypherQuery"}})
    CREATE (qualitykgbb)-[:HAS_EXPORT_MODEL {{category:"ObjectPropertyExpression", URI:"orkg_has_export_model_URI"}}]->(exportModel2KGBBelement:ExportModelKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Quality relation identification basicUnit export model 2", description:"A Knowledge Graph Building Block element that provides an export model for identified quality relations. The export model 2 is based on the OBOE ontology data model.", URI:"QualityExportModel2KGBBElementIND_URI", type:"ExportModelKGBBElement_URI", KGBB_URI:"QualityIdentificationBasicUnitKGBB_URI", export_scheme:"OBOE", category:"NamedIndividual", export_model_cypher_code:"cypherQuery"}})
    CREATE (qualitykgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(qualityInputInfo1KGBBelement:QualityInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of quality relation identification basicUnit", description:"User input information 1 for the specification of the quality resource for a quality relation identification basicUnit.", input_name:"quality_identification_input", placeholder_text:"select a type of quality", URI:"InputInfo1QualityBasicUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"QualityIdentificationBasicUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1QualityBasicUnitIND_URI", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/BFO_0000019", ontology_ID:"PATO,OMIT", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})
    CREATE (qualitykgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of weight measurement basicUnits in its basicUnit.", KGBB_URI:"QualityIdentificationBasicUnitKGBB_URI", target_KGBB_URI:"WeightMeasurementBasicUnitKGBB_URI", required:"false", quantity:"m", query_key:"weight_measurement_cypher_code", input_results_in:"added_basicUnit"}}]->(weightkgbb)
    CREATE (qualitykgbb)-[:HAS_BASIC_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_basicUnit_element_URI", description:"This basicUnit element specifies information about the use of basic reproduction number measurement basicUnits in its basicUnit.", KGBB_URI:"QualityIdentificationBasicUnitKGBB_URI", target_KGBB_URI:"R0MeasurementBasicUnitKGBB_URI", required:"false", quantity:"m", query_key:"r0_measurement_cypher_code", input_results_in:"added_basicUnit"}}]->(R0Measurementkgbb)
    // WEIGHT MEASUREMENT BASIC_UNIT KGBB
    CREATE (weightkgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(weightMeasBasicUnitRepresentation1KGBBelement:WeightMeasurementBasicUnitRepresentationKGBBElement_IND:BasicUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Weight measurement basicUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the weight measurement basicUnit in the user interface in a human-readable form using the weight measurement basicUnit Knowledge Graph Building Block.", URI:"WeightMeasurementBasicUnitRepresentation1KGBBElementIND_URI", data_view_name:"{data_view_name}", node_type:"basicUnit representation", data_item_type_URI:"weight_measurement_basicUnit_URI", KGBB_URI:"WeightMeasurementBasicUnitKGBB_URI", category:"NamedIndividual", data_view_information:"true", component:"weight_measurement_basicUnit", link_$$$_1:"{{'name':'weight_measurement_basicUnit_input_info', 'placeholder_text_1':'value', 'user_input_data_type':'xsd:float', 'edit_results_in':'edited_basicUnit', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'WeightMeasurementBasicUnitKGBB_URI', 'data_item_type':'basicUnit', 'query_key':'weight_measurement_cypher_code', 'links_to_component':'weight_measurement_basicUnit', 'basicUnit_object_URI':'object$_$URI', 'input_results_in':'added_basicUnit', 'edit_results_in':'edited_basicUnit', 'placeholder_text_2':'select a gram-based unit', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/UO_1000021', 'ontology_ID':'UO'}}"}})
    CREATE (weightkgbb)-[:HAS_EXPORT_MODEL {{category:"ObjectPropertyExpression", URI:"orkg_has_export_model_URI"}}]->(weightMeasurementexportModel1KGBBelement:ExportModelKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Weight measurement basicUnit export model 1", description:"A Knowledge Graph Building Block element that provides an export model for weight measurements. The export model 1 is based on the OBO/OBI data model.", URI:"WeightMeasurementExportModel1KGBBElementIND_URI", type:"ExportModelKGBBElement_URI", KGBB_URI:"WeightMeasurementBasicUnitKGBB_URI", export_scheme:"OBO", category:"NamedIndividual", export_model_cypher_code:"cypherQuery"}})
    CREATE (weightkgbb)-[:HAS_EXPORT_MODEL {{category:"ObjectPropertyExpression", URI:"orkg_has_export_model_URI"}}]->(weightMeasurementexportModel2KGBBelement:ExportModelKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Weight measurement basicUnit export model 2", description:"A Knowledge Graph Building Block element that provides an export model for weight measurements. The export model 2 is based on the OBOE ontology data model.", URI:"WeightMeasurementExportModel2KGBBElementIND_URI", type:"ExportModelKGBBElement_URI", KGBB_URI:"WeightMeasurementBasicUnitKGBB_URI", export_scheme:"OBOE", category:"NamedIndividual", export_model_cypher_code:"cypherQuery"}})
    CREATE (weightkgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(weightMeasurementBasicUnit)
    CREATE (weightkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(weightMeasurementInputInfo1KGBBelement:WeightMeasurementInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of weight measurement basicUnit", description:"User input information 1 for the specification of the weight measurement value for a weight measurement basicUnit.", placeholder_text:"value", input_name:"weight_value_input", URI:"InputInfo1WeightMeasurementBasicUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"WeightMeasurementBasicUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1WeightMeasurementBasicUnitIND_URI", user_input_data_type:"xsd:float", data_view_information:"true", input_target_property:["value"]}})
    CREATE (weightkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(weightMeasurementInputInfo2KGBBelement:WeightMeasurementInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 2 element of weight measurement basicUnit", description:"User input information 2 for the specification of the weight measurement unit resource for a weight measurement basicUnit.", input_name:"weight_unit_input", placeholder_text:"select a gram-based unit", URI:"InputInfo2WeightMeasurementBasicUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input2", KGBB_URI:"WeightMeasurementBasicUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo2WeightMeasurementBasicUnitIND_URI", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/UO_1000021", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})
    // R0 MEASUREMENT BASIC_UNIT KGBB
    CREATE (R0Measurementkgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(R0MeasBasicUnitRepresentation1KGBBelement:BasicReproductionNumberMeasurementBasicUnitRepresentationKGBBElement_IND:BasicUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Basic reproduction number measurement basicUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the basic reproduction number measurement basicUnit in the user interface in a human-readable form using the basic reproduction number measurement basicUnit Knowledge Graph Building Block.", URI:"R0MeasurementBasicUnitRepresentation1KGBBElementIND_URI", data_view_name:"{data_view_name}", node_type:"basicUnit representation", data_item_type_URI:"r0_measurement_basicUnit_URI", KGBB_URI:"R0MeasurementBasicUnitKGBB_URI", category:"NamedIndividual", data_view_information:"true", component:"R0_measurement_basicUnit", link_$$$_1:"{{'name':'R0_measurement_basicUnit_input_info', 'placeholder_text_1':'value', 'placeholder_text_3':'upper limit', 'placeholder_text_2':'lower limit', 'user_input_data_type':'xsd:float', 'edit_results_in':'edited_basicUnit', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'R0MeasurementBasicUnitKGBB_URI', 'data_item_type':'basicUnit', 'query_key':'r0_measurement_cypher_code', 'links_to_component':'R0_measurement_basicUnit', 'basicUnit_object_URI':'object$_$URI', 'input_results_in':'added_basicUnit', 'edit_results_in':'edited_basicUnit'}}"}})
    CREATE (R0Measurementkgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(r0MeasurementBasicUnit)
    CREATE (R0Measurementkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(R0MeasurementInputInfo1KGBBelement:R0MeasurementInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of R0 measurement basicUnit", description:"User input information 1 for the specification of the R0 measurement value for a basic reproduction number measurement basicUnit.", placeholder_text:"value", input_name:"R0_value_input", URI:"InputInfo1R0MeasurementBasicUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"R0MeasurementBasicUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1R0MeasurementBasicUnitIND_URI", user_input_data_type:"xsd:float", data_view_information:"true", input_target_property:["value"]}})
    CREATE (R0Measurementkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(R0UpperConfLimitMeasurementInputInfo1KGBBelement:R0UpperConfidenceLimitMeasurementInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 2 element of upper confidence limit for R0 measurement basicUnit", description:"User input information 2 for the specification of the upper confidence limit value for an R0 measurement for a basic reproduction number measurement basicUnit.", placeholder_text:"upper limit", input_name:"upper_confidence_limit_value_input", URI:"InputInfo2UpperConfLimitR0MeasurementBasicUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input2", KGBB_URI:"R0MeasurementBasicUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo2UpperConfLimitR0MeasurementBasicUnitIND_URI", user_input_data_type:"xsd:float", data_view_information:"true", input_target_property:["value"]}})
    CREATE (R0Measurementkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(R0LowerConfLimitMeasurementInputInfo1KGBBelement:R0LowerConfidenceLimitMeasurementInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 3 element of lower confidence limit for R0 measurement basicUnit", description:"User input information 3 for the specification of the lower confidence limit value for an R0 measurement for a basic reproduction number measurement basicUnit.", placeholder_text:"lower limit", input_name:"lower_confidence_limit_value_input", URI:"InputInfo3LowerConfLimitR0MeasurementBasicUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input3", KGBB_URI:"R0MeasurementBasicUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo3LowerConfLimitR0MeasurementBasicUnitIND_URI", user_input_data_type:"xsd:float", data_view_information:"true", input_target_property:["value"]}})
    // RESEARCH TOPIC KGBB RELATIONS
    CREATE (researchTopicBasicUnitKGBB)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(researchTopicInputInfo1KGBBelement:ResearchTopicInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"research_topic_input", description:"User input information 1 for the specification of the research topic resource for a research topic basicUnit.", input_name:"research_topic_input", URI:"InputInfo1ResearchTopicBasicUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"ResearchTopicBasicUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1ResearchTopicBasicUnitIND_URI", input_restricted_to_subclasses_of:"http://edamontology.org/topic_0003", ontology_ID:"EDAM", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})
    CREATE (researchTopicBasicUnitKGBB)-[:HAS_EXPORT_MODEL {{category:"ObjectPropertyExpression", URI:"orkg_has_export_model_URI"}}]->(researchtopicexportModel1KGBBelement:ExportModelKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research topic basicUnit export model 1", description:"A Knowledge Graph Building Block element that provides an export model for research topic relations. The export model 1 is based on the XXX data model.", URI:"ResearchTopicExportModel1KGBBElementIND_URI", export_scheme:"OBO", type:"ExportModelKGBBElement_URI", KGBB_URI:"ResearchTopicBasicUnitKGBB_URI", category:"NamedIndividual", export_model_cypher_code:"cypherQuery"}})
    CREATE (researchTopicUnitKGBB)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(researchTopicBasicUnitRepresentation1KGBBelement:ResearchTopicBasicUnitRepresentationKGBBElement_IND:BasicUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research topic basicUnit representation 1 element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the research topic basicUnit in the user interface in a human-readable form using the research topic basicUnit Knowledge Graph Building Block.", data_view_name:"{data_view_name}", URI:"ResearchTopicRepresentation1KGBBElementIND_URI", type:"BasicUnitRepresentationKGBBElement_URI", component:"research_topic_basicUnit", data_item_type_URI:"ResearchTopicBasicUnit_URI", node_type:"basicUnit_representation", KGBB_URI:"ResearchTopicBasicUnitKGBB_URI", data_view_information:"true", category:"NamedIndividual", link_$$$_1:"{{'name':'research_topic_input', 'component':'research_topic_basicUnit', 'input_info_URI':'InputInfo1ResearchTopicBasicUnitIND_URI', 'placeholder_text':'specify the research topic', 'input_source':'input1', 'editable':'true'}}"}})
    // CONFIDENCE LEVEL BASIC_UNIT KGBB
    CREATE (confidenceLevelBasicUnitKGBB)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(confidenceLevelBasicUnit)
    CREATE (confidenceLevelBasicUnitKGBB)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(confidenceLevelBasicUnitKGBBelement:ConfidenceLevelBasicUnitRepresentationKGBBElement_IND:BasicUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Confidence level specification basicUnit representation 1 element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the confidence level specification basicUnit in the user interface in a human-readable form using the confidence level specification basicUnit Knowledge Graph Building Block.", data_view_name:"{data_view_name}", URI:"ConfLevelSpecBasicUnitRepresentation1KGBBElementIND_URI", type:"BasicUnitRepresentationKGBBElement_URI", data_item_type_URI:"ConfidenceLevelBasicUnit_URI", node_type:"basicUnit_representation", KGBB_URI:"ConfidenceLevelBasicUnitKGBB_URI", data_view_information:"true", category:"NamedIndividual", simpleDescriptionUnit_html:"", component:"confidence_level_basicUnit"}})
    // MATERIAL ENTITY PARTHOOD GRANULARITY PERSPECTIVE KGBB RELATIONS
    CREATE (MatEntparthoodgranperspectiveKGBB)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(MatEntParthoodGranTree)
    CREATE (MatEntparthoodgranperspectiveKGBB)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(materialEntityParthoodGranularityTreeRepresentation1KGBBelement:MaterialEntityParthoodGranularityTreeRepresentationKGBBElement_IND:GranularityTreeRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Material entity parthood granularity tree representation 1 element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the parthood-based granularity tree of material entities in the user interface in a human-readable form using the material entity parthood granularity perspective Knowledge Graph Building Block.", data_view_name:"{data_view_name}", URI:"MatEntParthoodGranTreeRepresentation1KGBBElementIND_URI", type:"GranularityTreeRepresentationKGBBElement_URI", data_item_type_URI:"MatEnt_Parthood_based_Granularity_tree_URI", node_type:"granularity_tree_representation", KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", data_view_information:"true", category:"NamedIndividual", simpleDescriptionUnit_html:"granularity_tree.html", component:"material_entity_parthood_granularity_tree"}})
    '''.format(creator = 'ORKGuserORCID', createdWith = 'ORKG', entryURI = 'entry_URIX', simpleDescriptionUnit_uri = 'simpleDescriptionUnit_URIX', basicUnitURI = 'basicUnit_URIX', doiEntry = 'Entry_DOI', data_view_name = 'ORKG')

get_entry_data_query_string = '''MATCH (n {{URI:"{entry_URI}"}}) RETURN count(n);'''.format(entry_URI="URI")





@app.route("/")

def index():
    global entry_uri
    global entry_dict
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
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
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name



    if request.method == "POST":

        entry_uri = request.form['entry_uri']
        print("----------------------NEW ENTRY URI------------------------")
        print(entry_uri)

        entry_data = EntryRepresentation(entry_uri)

        return render_template("/entry.html", entry_uri=entry_uri, simpleDescriptionUnit_data=simpleDescriptionUnit_data, entry_name=entry_data.entry_label, simpleDescriptionUnit_types_count=simpleDescriptionUnit_types_count, simpleDescriptionUnit_kgbb_uri=simpleDescriptionUnit_kgbb_uri)

    else:
        return render_template("entry.html", simpleDescriptionUnit_data=simpleDescriptionUnit_data, entry_name=entry_data.entry_label, simpleDescriptionUnit_types_count=simpleDescriptionUnit_types_count)









@app.route("/certainty", methods=['POST', 'GET'])
# certainty information for an basicUnit provided by a user

def certainty():
    global entry_uri
    global entry_dict
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name

    if request.method == "POST":

        if request.form:

            try:
                basicUnit_uri = request.form['input_name']
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print("++++++++++++++++++ BASIC_UNIT URI +++++++++++++++++++++")
                print(basicUnit_uri)

            except:
                pass

            try:
                certainty = request.form[basicUnit_uri + '_certainty']
                print("-------------------------- CERTAINTY -----------------------------")
                print(certainty)
            except:
                certainty = None


            try:
                simpleDescriptionUnit_uri = request.form[basicUnit_uri + '_simpleDescriptionUnit_uri']
                print("-------------------------- SIMPLE_DESCRIPTION_UNIT URI ------------------------------")
                print(simpleDescriptionUnit_uri)
            except:
                simpleDescriptionUnit_uri = None


            try:
                entry_uri = request.form[basicUnit_uri + '_entry_uri']
                print("-------------------------- ENTRY URI -----------------------------")
                print(entry_uri)
            except:
                entry_uri = None

            try:
                parent_uri = request.form[basicUnit_uri + '_parent_uri']
                print("-------------------------- PARENT URI ----------------------------")
                print(parent_uri)
            except:
                parent_uri = None

            try:
                parent_item_type = request.form[basicUnit_uri + '_parent_type']
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
                certainty_basicUnit_uri = str(uuid.uuid4())

                # cypher query to specify or update the confidence level of the basicUnit
                basicUnit_confidence_query_string = '''MATCH (basicUnit {{URI:"{basicUnit_uri}"}})
                WITH basicUnit
                OPTIONAL MATCH (basicUnit)-[:BASIC_UNIT_CONFIDENCE_LEVEL]->(confidence {{current_version:"true"}})
                OPTIONAL MATCH (basicUnit)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(certaintyBasicUnit:orkg_CertaintyBasicUnit {{current_version:"true"}})
                WITH basicUnit, confidence, certaintyBasicUnit
                FOREACH (i IN CASE WHEN confidence IS NULL THEN [1] ELSE [] END |
                CREATE (basicUnit)-[:BASIC_UNIT_CONFIDENCE_LEVEL {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/SEPIO_0000167", entry_URI:"{entry_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnit_uri}", description:"A relation between an basicUnit and a value that indicates the degree of confidence that the Proposition it puts forth is true."}}]->(certainty{label}:NamedIndividual:Entity {{URI:"{certainty_uri}", type:"{type}", name:"{name}", ontology_ID:"{ontology_ID}", description:"{description}", current_version:"true", entry_URI:"{entry_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnit_uri}", created_on:localdatetime(), last_updated_on:localdatetime(), contributed_by:["{creator}"], created_by:"{creator}", created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
                CREATE (basicUnit)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entry_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnit_uri}"}}]->(confidenceLevelBasicUnit_ind:orkg_ConfidenceLevelBasicUnit_IND:orkg_BasicUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"Confidence level specification basicUnit", URI:"{certainty_basicUnit_uri}", description:"This basicUnit models the specification of the confidence level for a given basicUnit, simpleDescriptionUnit, or entry in the orkg. As such, it is a statement about a statement or a collection of statements.", type:"ConfidenceLevelBasicUnit_URI", object_URI:"{certainty_uri}", entry_URI:"{entry_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", KGBB_URI:"ConfidenceLevelBasicUnitKGBB_URI", node_type:"basicUnit", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", basicUnit_label:"{name} [{ontology_ID}]"}})
                CREATE (confidenceLevelBasicUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entry_uri}", simpleDescriptionUnit_URI:"{simpleDescriptionUnit_uri}", basicUnit_URI:"{basicUnit_uri}"}}]->(certainty)
                )
                WITH basicUnit, confidence, certaintyBasicUnit
                FOREACH (i IN CASE WHEN confidence IS NOT NULL THEN [1] ELSE [] END |
                SET confidence.name="{name}"
                SET confidence.type="{type}"
                SET confidence.description="{description}"
                SET confidence.last_updated_on=localdatetime()
                SET confidence{label}:NamedIndividual:Entity
                SET certaintyBasicUnit.basicUnit_label="{name} [{ontology_ID}]"
                SET certaintyBasicUnit.last_updated_on = localdatetime()
                )
                RETURN basicUnit
                '''.format(basicUnit_uri=basicUnit_uri, certainty_uri = certainty_uri, name=name, type=type, label=label, description=description, ontology_ID=ontology_ID, entry_uri=entry_uri, simpleDescriptionUnit_uri=simpleDescriptionUnit_uri, creator='ORKGuserORCID', createdWith='ORKG', certainty_basicUnit_uri=certainty_basicUnit_uri)

                # query result
                result = connection.query(basicUnit_confidence_query_string, db='neo4j')
                print("---------------------------------------------------------------------------------")
                print("------------------------------------- RESULT ------------------------------------")
                print(result)


            else:
                # cypher query to delete the confidence level specification of the basicUnit
                basicUnit_confidence_query_string = '''OPTIONAL MATCH (basicUnit {{URI:"{basicUnit_uri}"}})-[:BASIC_UNIT_CONFIDENCE_LEVEL]->(certainty {{current_version:"true"}})
                SET certainty.current_version = "false"
                RETURN certainty.current_version
                '''.format(basicUnit_uri=basicUnit_uri)

                # query result
                result = connection.query(basicUnit_confidence_query_string, db='neo4j')
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
            if parent_item_type == "basicUnit":
                for parent in entry_dict:
                    if parent.get('id') == parent_uri:
                        parent_node_type = parent.get('node_type')
                        if parent_node_type == "basicUnit":
                            grand_parent_uri = parent.get('parent')
                            for grand_parent in entry_dict:
                                if grand_parent.get('id') == grand_parent_uri:
                                    grand_parent_node_type = grand_parent.get('node_type')
                                    if grand_parent_node_type == 'simpleDescriptionUnit':
                                        entry_dict = getEntryDict(entry_uri, data_view_name)

                                        entry_dict = updateEntryDict(entry_dict, grand_parent_uri)



                                        return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                        else:

                            entry_dict = getEntryDict(entry_uri, data_view_name)
                            entry_dict = updateEntryDict(entry_dict, parent_uri)
                            return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


            else:

                entry_dict = getEntryDict(entry_uri, data_view_name)
                entry_dict = updateEntryDict(entry_dict, parent_uri)
                return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

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
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
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

            simpleDescriptionUnit_uri = request.form[input_uri + '_simpleDescriptionUnit_uri']
            print("------------------------------ SIMPLE_DESCRIPTION_UNIT URI ---------------------------------")
            print(simpleDescriptionUnit_uri)

            parent_item_type = request.form[input_uri + '_parent_item_type']
            print("--------------------------- PARENT ITEM TYPE ----------------------------")
            print(parent_item_type)

            query_key = "label_cypher"

            # cypher query to edit the label of the resource
            editInstanceLabel(parent_uri, kgbb_uri, entry_uri, simpleDescriptionUnit_uri, input_label, query_key, input_uri)

        flash('resource label updated', 'good')



        if parent_uri == entry_uri:
            print("---------------------------------------------------------------")
            print("----------------------- GOES TO ENTRY -------------------------")
            entry_dict = getEntryDict(entry_uri, data_view_name)


            return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


        if parent_uri != entry_uri:
            if parent_item_type == "basicUnit":
                for parent in entry_dict:
                    if parent.get('id') == parent_uri:
                        parent_node_type = parent.get('node_type')
                        if parent_node_type == "basicUnit":
                            grand_parent_uri = parent.get('parent')
                            for grand_parent in entry_dict:
                                if grand_parent.get('id') == grand_parent_uri:
                                    grand_parent_node_type = grand_parent.get('node_type')
                                    if grand_parent_node_type == 'simpleDescriptionUnit':
                                        entry_dict = getEntryDict(entry_uri, data_view_name)

                                        entry_dict = updateEntryDict(entry_dict, grand_parent_uri)



                                        return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                        else:

                            entry_dict = getEntryDict(entry_uri, data_view_name)
                            entry_dict = updateEntryDict(entry_dict, parent_uri)
                            return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


            else:

                entry_dict = getEntryDict(entry_uri, data_view_name)
                entry_dict = updateEntryDict(entry_dict, parent_uri)
                return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

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
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
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
                simpleDescriptionUnit_uri = answer[6]
                basicUnit_uri = answer[7]
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
                simpleDescriptionUnit_uri = answer[6]
                basicUnit_uri = answer[7]
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



            if input_result == 'added_basicUnit' or input_result == 'added_simpleDescriptionUnit':
                added_resource = addResource(parent_uri, kgbb_uri, entry_uri, simpleDescriptionUnit_uri, basicUnit_uri, description, bioportal_full_id, bioportal_preferred_name, bioportal_ontology_id, input_result, query_key, input_value, input_value1, input_value2)
                print("------------------------------------------------------------------")
                print("----------------------- ADDED RESOURCE ---------------------------")
                print(added_resource)
                resource_uri = added_resource[0]
                parent_uri = added_resource[1]
                result = added_resource[2]

                if result == "added_basicUnit":
                    basicUnit_uri = resource_uri
                    message = "BasicUnit has been added"
                    print("---------------------------------------------------------------")
                    print("------------------------ BASIC_UNIT URI ------------------------")
                    print(basicUnit_uri)

                elif result == "added_simpleDescriptionUnit":
                    simpleDescriptionUnit_uri = resource_uri
                    message = "SimpleDescriptionUnit has been added"
                    print("---------------------------------------------------------------")
                    print("-------------------------- SIMPLE_DESCRIPTION_UNIT URI ---------------------------")
                    print(simpleDescriptionUnit_uri)


                if parent_uri == entry_uri:
                    print("---------------------------------------------------------------")
                    print("----------------------- GOES TO ENTRY -------------------------")
                    entry_dict = getEntryDict(entry_uri, data_view_name)


                    flash(message, 'good')

                    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


                if parent_uri != entry_uri:
                    if parent_item_type == "basicUnit":
                        for child in entry_dict:
                            if child.get('id') == parent_uri:
                                select_uri = child.get('parent')
                                entry_dict = getEntryDict(entry_uri, data_view_name)
                                entry_dict = updateEntryDict(entry_dict, select_uri)

                                flash(message, 'good')

                                return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                    elif parent_item_type == "simpleDescriptionUnit":
                        entry_dict = getEntryDict(entry_uri, data_view_name)
                        entry_dict = updateEntryDict(entry_dict, parent_uri)

                        flash(message, 'good')
                        return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))




            elif input_result == 'edited_basicUnit' or input_result == 'edited_simpleDescriptionUnit':
                added_resource = addResource(parent_uri, kgbb_uri, entry_uri, simpleDescriptionUnit_uri, basicUnit_uri, description, bioportal_full_id, bioportal_preferred_name, bioportal_ontology_id, input_result, query_key, input_value, input_value1, input_value2)
                print("------------------------------------------------------------------")
                print("----------------------- ADDED/EDITED RESOURCE --------------------")
                print(added_resource)
                resource_uri = added_resource[0]
                parent_uri = added_resource[1]
                result = added_resource[2]

                if result == "added_basicUnit":
                    basicUnit_uri = resource_uri
                    message = "BasicUnit has been added"
                    print("---------------------------------------------------------------")
                    print("------------------------ BASIC_UNIT URI ------------------------")
                    print(basicUnit_uri)

                if result == "edited_basicUnit":
                    basicUnit_uri = resource_uri
                    message = "BasicUnit has been successfully edited"
                    print("---------------------------------------------------------------")
                    print("------------------------ BASIC_UNIT URI ------------------------")
                    print(basicUnit_uri)

                elif result == "added_simpleDescriptionUnit":
                    simpleDescriptionUnit_uri = resource_uri
                    message = "SimpleDescriptionUnit has been added"
                    print("---------------------------------------------------------------")
                    print("-------------------------- SIMPLE_DESCRIPTION_UNIT URI ---------------------------")
                    print(simpleDescriptionUnit_uri)

                elif result == "edited_simpleDescriptionUnit":
                    simpleDescriptionUnit_uri = resource_uri
                    message = "SimpleDescriptionUnit has been successfully edited"
                    print("---------------------------------------------------------------")
                    print("-------------------------- SIMPLE_DESCRIPTION_UNIT URI ---------------------------")
                    print(simpleDescriptionUnit_uri)


                if parent_uri == entry_uri:
                    print("---------------------------------------------------------------")
                    print("----------------------- GOES TO ENTRY -------------------------")
                    entry_dict = getEntryDict(entry_uri, data_view_name)


                    flash(message, 'good')

                    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


                if parent_uri != entry_uri:
                    if parent_item_type == "basicUnit":
                        for parent in entry_dict:
                            if parent.get('id') == parent_uri:
                                parent_node_type = parent.get('node_type')
                                if parent_node_type == "basicUnit":
                                    grand_parent_uri = parent.get('parent')
                                    for grand_parent in entry_dict:
                                        if grand_parent.get('id') == grand_parent_uri:
                                            grand_parent_node_type = grand_parent.get('node_type')
                                            if grand_parent_node_type == 'simpleDescriptionUnit':
                                                entry_dict = getEntryDict(entry_uri, data_view_name)

                                                entry_dict = updateEntryDict(entry_dict, grand_parent_uri)

                                                flash(message, 'good')

                                                return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                                else:
                                    flash(message, 'good')
                                    entry_dict = getEntryDict(entry_uri, data_view_name)
                                    entry_dict = updateEntryDict(entry_dict, parent_uri)
                                    return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


                    else:
                        flash(message, 'good')
                        entry_dict = getEntryDict(entry_uri, data_view_name)
                        entry_dict = updateEntryDict(entry_dict, parent_uri)
                        return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                else:
                    entry_dict = getEntryDict(entry_uri, data_view_name)
                    entry_dict = updateEntryDict(entry_dict, entry_uri)

                    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

        else:
            return render_template("/entry.html", entry_data=entry_data, simpleDescriptionUnits_length=simpleDescriptionUnits_length, simpleDescriptionUnits_elements_length=simpleDescriptionUnits_elements_length, simpleDescriptionUnit_types_count=simpleDescriptionUnit_types_count, navi_dict=navi_dict, simpleDescriptionUnit_view_tree=simpleDescriptionUnit_view_tree)

    return render_template("/entry.html", entry_data=entry_data, simpleDescriptionUnit_types_count=simpleDescriptionUnit_types_count, navi_dict=navi_dict, simpleDescriptionUnit_view_tree=simpleDescriptionUnit_view_tree)








@app.route("/delete_input", methods=['POST', 'GET'])
# process information provided by a user

def delete_input():
    global entry_uri
    global entry_dict
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name


    if request.method == "POST":

        if request.form:
            try:
                request.form['delete_basicUnit']
                response = request.form['delete_basicUnit_uri']
                # response is a list of basicUnit_uri and parent_uri as a string
                response = response.replace("['","")
                response = response.replace("']","")

                parent_uri = response.partition("', '")[0]
                print("-----------------------------------------------------")
                print("------------------- PARENT URI ----------------------")
                print(parent_uri)

                basicUnit_uri = response.partition("', '")[2]
                print("-----------------------------------------------------")
                print("------------------ BASIC_UNIT URI --------------------")
                print(basicUnit_uri)

                deleteBasicUnit(basicUnit_uri, 'userID')

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
                            if parent_node_type == "basicUnit":
                                grand_parent_uri = parent.get('parent')
                                for grand_parent in entry_dict:
                                    if grand_parent.get('id') == grand_parent_uri:
                                        grand_parent_node_type = grand_parent.get('node_type')
                                        if grand_parent_node_type == 'simpleDescriptionUnit':
                                            entry_dict = updateEntryDict(entry_dict, grand_parent_uri)

                                            return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                            else:
                                entry_dict = updateEntryDict(entry_dict, parent_uri)
                                return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))



                else:
                    entry_dict = updateEntryDict(entry_dict, entry_uri)

                    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))




            except:
                pass
            try:
                request.form['delete_simpleDescriptionUnit']
                response = request.form['delete_simpleDescriptionUnit_uri']
                # response is a list of basicUnit_uri and parent_uri as a string
                response = response.replace("['","")
                response = response.replace("']","")

                parent_uri = response.partition("', '")[0]
                print("-----------------------------------------------------")
                print("------------------- PARENT URI ----------------------")
                print(parent_uri)

                simpleDescriptionUnit_uri = response.partition("', '")[2]
                print("-----------------------------------------------------")
                print("------------------ SIMPLE_DESCRIPTION_UNIT URI -------------------------")
                print(simpleDescriptionUnit_uri)

                deleteSimpleDescriptionUnit(simpleDescriptionUnit_uri, 'userID')

                entry_dict = getEntryDict(entry_uri, data_view_name)

                entry_dict = updateEntryDict(entry_dict, parent_uri)

                flash('SimpleDescriptionUnit has been deleted', 'good')

                if parent_uri != entry_uri:
                    return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))
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
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name


    if request.method == "POST":
        if request.form['entry_uri']:
            entry_uri = request.form['entry_uri']

            entry_dict = getEntryDict(entry_uri, data_view_name)



            return render_template("/entry.html", naviJSON=getJSON(entry_dict), entry_dict=entry_dict)

        else:
            return render_template("/entry.html", entry_data=entry_data, simpleDescriptionUnits_length=simpleDescriptionUnits_length, simpleDescriptionUnits_elements_length=simpleDescriptionUnits_elements_length, simpleDescriptionUnit_types_count=simpleDescriptionUnit_types_count, navi_dict=navi_dict, simpleDescriptionUnit_view_tree=simpleDescriptionUnit_view_tree, entry_view_tree=entry_view_tree)

    return render_template("/entry.html", entry_data=entry_data, simpleDescriptionUnits_length=simpleDescriptionUnits_length, simpleDescriptionUnits_elements_length=simpleDescriptionUnits_elements_length, simpleDescriptionUnit_types_count=simpleDescriptionUnit_types_count, navi_dict=navi_dict, simpleDescriptionUnit_view_tree=simpleDescriptionUnit_view_tree, entry_view_tree=entry_view_tree)









# navigating through an entry via the navi-tree
@app.route("/navi", methods=['POST', 'GET'])
def navi():
    global entry_uri
    global entry_dict
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name

    if request.method == 'POST':
        if request.form:
            data = json.loads(request.form['node_data'])
            print(data)
            simpleDescriptionUnit_uri = data['node_data'][0].get('original').get('id')
            node_type = data['node_data'][0].get('original').get('node_type')
            parent_uri = data['node_data'][0].get('original').get('parent')
            entry_uri = entry_dict[0].get('id')
            #simpleDescriptionUnit_uri = simpleDescriptionUnit_uri.decode("utf-8")
            print("---------------------------------------------------------------")
            print("---------------------------------------------------------------")
            print("-------------------------- SIMPLE_DESCRIPTION_UNIT URI ---------------------------")
            print(simpleDescriptionUnit_uri)
            print(type(simpleDescriptionUnit_uri))
            print("---------------------------------------------------------------")
            print("---------------------------------------------------------------")
            print("-------------------------- NODE TYPE ---------------------------")
            print(node_type)


            if simpleDescriptionUnit_uri == entry_uri:
                entry_dict = updateEntryDict(entry_dict, simpleDescriptionUnit_uri)

                return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

            if node_type == "basicUnit" or node_type == "granularity_tree":
                if parent_uri != entry_uri:
                    for parent in entry_dict:
                        if parent.get('id') == parent_uri:
                            parent_node_type = parent.get('node_type')
                            if parent_node_type == "basicUnit":
                                grand_parent_uri = parent.get('parent')
                                for grand_parent in entry_dict:
                                    if grand_parent.get('id') == grand_parent_uri:
                                        grand_parent_node_type = grand_parent.get('node_type')
                                        if grand_parent_node_type == 'simpleDescriptionUnit':
                                            entry_dict = updateEntryDict(entry_dict, grand_parent_uri)

                                            return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                            else:
                                entry_dict = updateEntryDict(entry_dict, parent_uri)
                                return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))



                else:
                    entry_dict = updateEntryDict(entry_dict, entry_uri)

                    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


            entry_dict = updateEntryDict(entry_dict, simpleDescriptionUnit_uri)

            return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

        else:
            return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

    return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))







# navigating to a particular simpleDescriptionUnit via a simpleDescriptionUnit resource
@app.route("/simpleDescriptionUnit", methods=['POST', 'GET'])
def simpleDescriptionUnit():
    global entry_uri
    global entry_dict
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name

    if request.method == 'POST':

        if request.form['simpleDescriptionUnit_uri']:
            simpleDescriptionUnit_uri = request.form['simpleDescriptionUnit_uri']

            entry_dict = updateEntryDict(entry_dict, simpleDescriptionUnit_uri)

            return render_template("/simpleDescriptionUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

        else:
            return render_template("/simpleDescriptionUnit.html", navi_dict=navi_dict, simpleDescriptionUnit_view_tree=simpleDescriptionUnit_view_tree, entry_view_tree=entry_view_tree, naviJSON=getJSON(naviJSON))

    return render_template("/simpleDescriptionUnit.html", navi_dict=navi_dict, simpleDescriptionUnit_view_tree=simpleDescriptionUnit_view_tree, entry_view_tree=entry_view_tree, naviJSON=getJSON(naviJSON))







# getting versions of item back
@app.route("/_versioning", methods=['POST', 'GET'])
def versioning():
    global entry_uri
    global entry_dict
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
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
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
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
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
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
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
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
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
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
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
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
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
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

                entry_dict = getEntryDict(entry_uri, data_view_name)

                return render_template("/entry.html", naviJSON=getJSON(entry_dict), entry_dict=entry_dict)




                #return render_template("lobby_form.html", initiated="True", pubEntry="True")



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
            basicUnit_class_list = getBasicUnitClassList()
            simpleDescriptionUnit_class_list = getSimpleDescriptionUnitClassList()
            entry_class_list = getEntryClassList()

            return render_template("search.html", ontology_class_list=ontology_class_list, basicUnit_class_list=basicUnit_class_list, simpleDescriptionUnit_class_list=simpleDescriptionUnit_class_list, entry_class_list=entry_class_list)


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
    global simpleDescriptionUnit_data
    global simpleDescriptionUnit_kgbb_uri
    global simpleDescriptionUnit_types_count
    global basicUnit_kgbb_uri
    global entry_name
    global simpleDescriptionUnit_name
    global basicUnit_name
    global basicUnit_elements_dict
    global navi_dict
    global simpleDescriptionUnits_length
    global entry_node
    global connection
    global simpleDescriptionUnit_view_tree
    global basicUnit_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name



    if request.method == "POST":

        try:
            class_uri = request.form['simpleDescriptionUnit_class_uri']
            print("---------------------- SIMPLE_DESCRIPTION_UNIT CLASS URI ---------------------------")
            print(class_uri)

            instances_list = getInstanceList(class_uri)
            print("---------------------- INSTANCES LIST ---------------------------")
            print(instances_list)

        except:
            pass

        simpleDescriptionUnit_nodes_list = []

        for i in range (0, len(instances_list)):
            simpleDescriptionUnit_uri = instances_list[i].get('URI')
            simpleDescriptionUnit_dict = getSimpleDescriptionUnitRepresentation(simpleDescriptionUnit_uri, "ORKG")
            print("-------------------------------------------SIMPLE_DESCRIPTION_UNIT_DICT----------------")
            print(simpleDescriptionUnit_dict)
            simpleDescriptionUnit_nodes_list.append(simpleDescriptionUnit_dict)

        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("+++++++++++++++++++++ FINAL SIMPLE_DESCRIPTION_UNIT NODES LIST ++++++++++++++++++++++++++")
        print(simpleDescriptionUnit_nodes_list)
        print(len(simpleDescriptionUnit_nodes_list))

        return render_template("/search_result.html", simpleDescriptionUnit_nodes_list=simpleDescriptionUnit_nodes_list)




    else:
        return render_template("entry.html", simpleDescriptionUnit_data=simpleDescriptionUnit_data, entry_name=entry_data.entry_label, simpleDescriptionUnit_types_count=simpleDescriptionUnit_types_count)





if __name__ == "__main__":
    app.run()
