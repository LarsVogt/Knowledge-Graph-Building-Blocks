
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

global itemUnit_data
itemUnit_data = None

global itemUnit_kgbb_uri
itemUnit_kgbb_uri = None

global itemUnit_types_count
itemUnit_types_count = None

global statementUnit_elements_dict
statementUnit_elements_dict = None

global statementUnit_kgbb_uri
statementUnit_kgbb_uri = None

global entry_name
entry_name = None

global itemUnit_name
itemUnit_name = None

global statementUnit_name
statementUnit_name = None

global navi_dict
navi_dict = None

global itemUnits_length
itemUnits_length = None

global entry_node
entry_node = None

global itemUnit_view_tree
itemUnit_view_tree = None

global statementUnit_view_tree
statementUnit_view_tree = None

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
    CREATE (iaoDocPart:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"iao: document part", description:"A category denoting a rather broad domain or field of interest, of study, application, work, data, or technology. ItemUnits have no clearly defined borders between each other.", ontology_class:"true", URI:"http://purl.obolibrary.org/obo/IAO_0000314", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(informationContentEntity)
    CREATE (itemUnit:edam_Topic:iao_InformationContentEntity:ClassExpression:Entity {{name:"edam: topic", description:"An information content entity that is part of a document.", ontology_class:"true", URI:"http://edamontology.org/topic_0003", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(informationContentEntity)
    CREATE (orkg_researchtopic:orkg_ResearchTopic:edam_Topic:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg: research topic", ontology_class:"true", description:"A research topic is a subject or issue that a researcher is interested in when conducting research.", URI:"http://orkg/researchtopic_1", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(itemUnit)
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
    //STATEMENT_UNIT, ITEM_UNIT, GRANULARITY TREE, AND ENTRY CLASSES
    CREATE(GranPersp:orkg_GranularityTree:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg granularity tree", description:"An information content entity that is a tree-like hierarchical structure resulting from inter-connected statementUnits of a specific type. The relation that the statementUnits are modelling must be a partial order relation, i.e. a relation that is a binary relation R that is transitive (if b has relation R to c and c has relation R to d, than b has relation R to d), reflexive (b has relation R to itself), and antisymmetric (if b has relation R to c and c has relation R to b, than b and c are identical). The parthood relation is a good example for a partial order relation. Partial order relations result in what is called a granular partition that can be represented as a tree. These trees are called granularity trees. By specifying which types of entities are allowed as domains and ranges of a specific partial order relation, one can distinguish different types of granularity trees, with each type representing a granularity perspective, i.e. a class of particular granularity trees. One could, for example, define the granularity perspective of parthood between material entities, and each particular granularity tree of such parthood-relation-chains between actual material entities represents a granularity tree.", URI:"Granularity_tree_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoDocPart)
    CREATE(parthood_based_gran_tree:orkg_ParthoodBasedGranularityTree:orkg_GranularityTree:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg parthood-based granularity tree", description:"A granularity tree that is based on the parthood relation.", URI:"Parthood_based_Granularity_tree_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(GranPersp)
    CREATE(MatEntParthoodGranTree:orkg_MaterialEntityParthoodGranularityTree:orkg_ParthoodBasedGranularityTree:orkg_GranularityTree:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg material entity parthood granularity tree", description:"A granularity tree that is based on the parthood relation between material entities.", URI:"MatEnt_Parthood_based_Granularity_tree_URI", category:"ClassExpression", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://purl.obolibrary.org/obo/BFO_0000040"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(parthood_based_gran_tree)
    CREATE(Ass:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg statementUnit", description:"An information content entity that is a proposition from some research paper and that is asserted to be true, either by the authors of the paper or by a third party referenced in the paper. An statementUnit in the orkg is also a model for representing the contents of a particular statementUnit from a scholarly publication, representing a smallest unit of information that is independent of other units of information. Different types of such statementUnits can be differentiated.", URI:"StatementUnit_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(:sepio_Assertion:ClassExpression:Entity {{name:"sepio: assertion", URI:"http://purl.obolibrary.org/obo/SEPIO_0000001", category:"ClassExpression"}})
    CREATE (Ass)-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoDocPart)
    CREATE (:orkg_VersionedStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg versioned statementUnit", description:"A version of an orkg statementUnit. Versions of statementUnits capture the content of an statementUnit at a specific point in time and can be used for referencing and citation purposes.", URI:"orkg_versioned_statementUnit_class_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchActivityOutputStatementUnit:orkg_ResearchActivityOutputRelationStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research activity output relation statementUnit", description:"This statementUnit models the relation between a particular research activity and one of its research result outputs.", relevant_properties_URI:["http://purl.obolibrary.org/obo/OBI_0000299"], relevant_classes_URI:["http://orkg???????1", "http://orkg???????5"], URI:"Research_Activity_Output_Relation_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchActivityOutputRelationStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchActivityMethodRelationStatementUnit:orkg_ResearchActivityMethodRelationStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research activity method relation statementUnit", description:"This statementUnit models the relation between a particular research activity and one the research methods it realizes.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000055"], relevant_classes_URI:["http://orkg???????5", "http://orkg???????4"], URI:"Research_Activity_Method_Relation_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchActivityMethodRelationStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchActivityObjectiveRelationStatementUnit:orkg_ResearchActivityObjectiveRelationStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research activity objective relation statementUnit", description:"This statementUnit models the relation between a particular research activity and one the research objectives it achieves.", relevant_properties_URI:["http://purl.obolibrary.org/obo/OBI_0000417"], relevant_classes_URI:["http://orkg???????5", "http://orkg???????3"], URI:"Research_Activity_Objective_Relation_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchActivityObjectiveRelationStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchActivityParthoodStatementUnit:orkg_ResearchActivityParthoodStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research activity parthood statementUnit", description:"This statementUnit models the relation between a particular research activity and its activity parts (i.e. steps).", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000117"], relevant_classes_URI:["http://orkg???????5"], URI:"Research_Activity_Parthood_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchActivityParthoodStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchMethodParthoodStatementUnit:orkg_ResearchMethodParthoodStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research method parthood statementUnit", description:"This statementUnit models the relation between a particular research method and its method parts (i.e. steps).", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????4"], URI:"Research_Method_Parthood_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchMethodParthoodStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchMethodObjectiveRelationStatementUnit:orkg_ResearchMethodObjectiveRelationStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research method objective relation statementUnit", description:"This statementUnit models the relation between a particular research method and its objective specification part.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????4", "http://orkg???????3"], URI:"Research_Method_Objective_Relation_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchMethodObjectiveRelationStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchMethodActivityRelationStatementUnit:orkg_ResearchMethodActivityRelationStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research method activity relation statementUnit", description:"This statementUnit models the relation between a particular research method and the activity that realizes it.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000055"], relevant_classes_URI:["http://orkg???????4", "http://orkg???????5"], URI:"Research_Method_Activity_Relation_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchMethodActivityRelationStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchResultParthoodStatementUnit:orkg_ResearchResultParthoodStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research result parthood statementUnit", description:"This statementUnit models the relation between a particular research result and its result parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????1"], URI:"Research_Result_Parthood_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchResultParthoodStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchResultActivityRelationStatementUnit:orkg_ResearchResultActivityRelationStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research result activity relation statementUnit", description:"This statementUnit models the relation between a particular research result and the research activity that has it as its output.", relevant_properties_URI:["http://purl.obolibrary.org/obo/OBI_0000299"], relevant_classes_URI:["http://orkg???????1", "http://orkg???????5"], URI:"Research_Result_Activity_Relation_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchResultActivityRelationStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchResultObjectiveRelationStatementUnit:orkg_ResearchResultObjectiveRelationStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research result objective relation statementUnit", description:"This statementUnit models the relation between a particular research result and the research objective that achieved it.", relevant_properties_URI:["http://orkg_has_achieved_result"], relevant_classes_URI:["http://orkg???????1", "http://orkg???????3"], URI:"Research_Result_Objective_Relation_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchResultObjectiveRelationStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchResultMaterialEntityRelationStatementUnit:orkg_ResearchResultMaterialEntityRelationStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research result material entity relation statementUnit", description:"This statementUnit models the relation between a particular research result and a material entity that the result is about.", relevant_properties_URI:["http://purl.obolibrary.org/obo/IAO_0000136"], relevant_classes_URI:["http://orkg???????1", "http://purl.obolibrary.org/obo/BFO_0000040"], URI:"Research_Result_Material_Entity_Relation_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchResultMaterialEntityRelationStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchObjectiveParthoodStatementUnit:orkg_ResearchObjectiveParthoodStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research objective parthood statementUnit", description:"This statementUnit models the relation between a particular research objective and its objective parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????3"], URI:"Research_Objective_Parthood_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchObjectiveParthoodStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchObjectiveMethodRelationStatementUnit:orkg_ResearchObjectiveMethodRelationStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research objective method relation statementUnit", description:"This statementUnit models the relation between a particular research objective and the method of which it is a part.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????3", "http://orkg???????4"], URI:"Research_Objective_Method_Relation_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchObjectiveMethodRelationStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchObjectiveActivityRelationStatementUnit:orkg_ResearchObjectiveActivityRelationStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research objective research activity relation statementUnit", description:"This statementUnit models the relation between a particular research objective and the research activity that achieves it.", relevant_properties_URI:["http://purl.obolibrary.org/obo/OBI_0000417"], relevant_classes_URI:["http://orkg???????5", "http://orkg???????4"], URI:"Research_Objective_Activity_Relation_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchObjectiveActivityRelationStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchObjectiveResultRelationStatementUnit:orkg_ResearchObjectiveResultRelationStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research objective result relation statementUnit", description:"This statementUnit models the relation between a particular research objective and the research result that it achieved.", relevant_properties_URI:["http://orkg_has_achieved_result"], relevant_classes_URI:["http://orkg???????3", "http://orkg???????1"], URI:"Research_Objective_Result_Relation_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchObjectiveResultRelationStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (materialEntityParthoodStatementUnit:orkg_MaterialEntityParthoodStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg material entity parthood statementUnit", description:"This statementUnit models the relation between a particular material entity and its material entity parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://purl.obolibrary.org/obo/BFO_0000040"], URI:"Material_Entity_Parthood_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"MaterialEntityParthoodStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (qualityStatementUnit:orkg_QualityRelationIdentificationStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg quality relation identification statementUnit", description:"This statementUnit models the relation between a particular entity and one of its qualities.", relevant_properties_URI:["http://purl.obolibrary.org/obo/RO_0000086"], relevant_classes_URI:["http://purl.obolibrary.org/obo/PATO_0000128", "http://purl.obolibrary.org/obo/PATO_0000146", "http://purl.obolibrary.org/obo/PATO_0001756", "http://purl.obolibrary.org/obo/PATO_0000014"], URI:"Quality_Identification_StatementUnit_URI", category:"ClassExpression", KGBB_URI:"QualityIdentificationStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (researchTopicStatementUnit:orkg_ResearchTopicStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg research topic statementUnit", description:"This statementUnit models the relation between a particular orkg research paper and its research topic.", URI:"ResearchTopicStatementUnit_URI", category:"ClassExpression", KGBB_URI:"ResearchTopicStatementUnitKGBB_URI", relevant_classes_URI:["http://orkg/researchtopic_1", "http://orkg???????2"], relevant_properties_URI:["http://edamontology.org/has_topic"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (confidenceLevelStatementUnit:orkg_ConfidenceLevelStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg confidence level specification statementUnit", description:"This statementUnit models the specification of the confidence level for a given statementUnit, itemUnit, or entry in the orkg. As such, it is a statement about a statement or a collection of statements.", URI:"ConfidenceLevelStatementUnit_URI", category:"ClassExpression", KGBB_URI:"ConfidenceLevelStatementUnitKGBB_URI", relevant_classes_URI:["http://purl.obolibrary.org/obo/NCIT_C107561", "http://purl.obolibrary.org/obo/NCIT_C85550", "http://purl.obolibrary.org/obo/NCIT_C47944"], relevant_properties_URI:["http://purl.obolibrary.org/obo/SEPIO_0000167"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (AssMeasurement:orkg_MeasurementStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg measurement statementUnit", description:"This statementUnit models the relation between a particular quality and one of its measurements. E.g., a weight measurement.", URI:"Measurement_StatementUnit_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (:orkg_GeographicallyLocatedInStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg geographically located in statementUnit", description:"This statementUnit models the relation of a particular material entity and the particular geographic location it is located in.", URI:"GeographicallyLocatedIn_statementUnit_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(Ass)
    CREATE (:orkg_R0MeasurementStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg basic reproduction number measurement statementUnit", description:"This statementUnit models a particular basic reproduction number measurement with its mean value and a 95% confidence interval.", URI:"R0_measurement_statementUnit_URI", category:"ClassExpression", KGBB_URI:"R0MeasurementStatementUnitKGBB_URI"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(AssMeasurement)
    CREATE (weightMeasurementStatementUnit:orkg_WeightMeasurementStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg weight measurement statementUnit", description:"This statementUnit models a particular weight measurement with its value and unit.", URI:"weight_measurement_statementUnit_URI", category:"ClassExpression", KGBB_URI:"WeightMeasurementStatementUnitKGBB_URI", relevant_classes_URI:["http://purl.obolibrary.org/obo/PATO_0000128"], relevant_properties_URI:["http://purl.obolibrary.org/obo/IAO_0000004", "http://purl.obolibrary.org/obo/IAO_0000039", "http://purl.obolibrary.org/obo/OBI_0001938", "http://purl.obolibrary.org/obo/IAO_0000417"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(AssMeasurement)
    CREATE (r0MeasurementStatementUnit:orkg_BasicReproductionNumberMeasurementStatementUnit:orkg_StatementUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg basic reproduction number measurement statementUnit", description:"This statementUnit models a particular basic reproduction number measurement with its value and a 95% confidence interval.", URI:"r0_measurement_statementUnit_URI", category:"ClassExpression", KGBB_URI:"R0MeasurementStatementUnitKGBB_URI", relevant_classes_URI:["http://purl.obolibrary.org/obo/OMIT_0024604", "http://purl.obolibrary.org/obo/STATO_0000196", "http://purl.obolibrary.org/obo/STATO_0000315", "http://purl.obolibrary.org/obo/STATO_0000314", "http://purl.obolibrary.org/obo/STATO_0000561"], relevant_properties_URI:["http://purl.obolibrary.org/obo/IAO_0000004", "http://purl.obolibrary.org/obo/IAO_0000039", "http://purl.obolibrary.org/obo/OBI_0001938", "http://purl.obolibrary.org/obo/IAO_0000417"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(AssMeasurement)
    CREATE (orkgItemUnit:orkg_ItemUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg itemUnit", description:"An orkg itemUnit is a model for representing the contents of one or more orkg statementUnits on a single UI itemUnit. In other words, itemUnits are containers for statementUnits. Often, statementUnits about the same entity are comprised on a single itemUnit. Different types of such itemUnits can be differentiated.", URI:"orkg_itemUnit_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoDocPart)
    CREATE (:orkg_VersionedItemUnit:orkg_ItemUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg versioned itemUnit", description:"A version of an orkg itemUnit. Versions of itemUnits capture the content of a itemUnit at a specific point in time and can be used for referencing and citation purposes.", URI:"orkg_versioned_itemUnit_class_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgItemUnit)
    CREATE (ResActItemUnit:orkg_ResearchActivityItemUnit:orkg_ItemUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg Research activity itemUnit", description:"This itemUnit models data about a research activity as it is documented in a particular research papers.", URI:"ResearchActivity_itemUnit_class_URI", category:"ClassExpression", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", relevant_classes_URI:["http://orkg???????5"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgItemUnit)
    CREATE (ResResItemUnit:orkg_ResearchResultItemUnit:orkg_ItemUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg Research result itemUnit", description:"This itemUnit models data about a research result as it is documented in a particular research paper.", URI:"ResearchResult_itemUnit_class_URI", category:"ClassExpression", KGBB_URI:"ResearchResultItemUnitKGBB_URI", relevant_classes_URI:["http://orkg???????1"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgItemUnit)
    CREATE (ResMethItemUnit:orkg_ResearchMethodItemUnit:orkg_ItemUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg Research method itemUnit", description:"This itemUnit models data about a research method as it is documented in a particular research paper.", URI:"ResearchMethod_itemUnit_class_URI", category:"ClassExpression", KGBB_URI:"ResearchMethodItemUnitKGBB_URI", relevant_classes_URI:["http://orkg???????4"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgItemUnit)
    CREATE (ResObjectiveItemUnit:orkg_ResearchObjectiveItemUnit:orkg_ItemUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg Research objective itemUnit", description:"This itemUnit models data about a research objective as it is documented in a particular research paper.", URI:"ResearchObjective_itemUnit_class_URI", category:"ClassExpression", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", relevant_classes_URI:["http://orkg???????3"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgItemUnit)
    CREATE (materialEntityItemUnit:orkg_MaterialEntityItemUnit:orkg_ItemUnit:iao_DocumentPart:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg material entity itemUnit", description:"This itemUnit models all information relating to a particular material entity.", URI:"material_entity_itemUnit_URI", category:"ClassExpression", KGBB_URI:"MaterialEntityItemUnitKGBB_URI", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://purl.obolibrary.org/obo/BFO_0000040"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(orkgItemUnit)
    CREATE (scholarlyPublicationEntry:orkg_ScholarlyPublicationEntry:orkg_Entry:iao_Document:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg scholarly publication entry", description:"This entry models all information relating to a particular scholarly publication.", URI:"scholarly_publication_entry_URI", category:"ClassExpression", KGBB_URI:"ScholarlyPublicationEntryKGBB_URI", relevant_classes_URI:["http://orkg???????2", "http://orkg/researchtopic_1"]}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(entryClass:orkg_Entry:iao_Document:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg entry", description:"An orkg entry is a model for representing the contents of one or more orkg itemUnits as a single entry. In other words, entries are containers for itemUnits. Often, itemUnits about the same itemUnit or entity are comprised in a single entry. Different types of such entries can be differentiated.", URI:"orkg_entry_class_URI", category:"ClassExpression"}})
    CREATE (:orkg_VersionedEntry:orkg_Entry:iao_Document:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg versioned entry", description:"A version of an orkg entry. Versions of entries capture the content of an entry at a specific point in time and can be used for referencing and citation purposes.", URI:"orkg_versioned_entry_class_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(entryClass)
    CREATE (scholarlyPublicationEntry)-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoPub)
    CREATE (entryClass)-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(iaoDoc)
    CREATE (:ORKGVersionedEntryClass:orkg_Entry:iao_Document:iao_InformationContentEntity:ClassExpression:Entity {{name:"orkg versioned entry", URI:"orkg versioned entry", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(entryClass)
    //KGBB CLASSES
    CREATE (statementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages statementUnit data.", URI:"StatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbb:KGBB:ClassExpression:Entity {{name:"Knowledge Graph Building Block", description:"A Knowledge Graph Building Block is a knowledge graph processing module that manages the storing of data in a knowledge graph application, the presentation of data from a knowledge graph in a user interface and the export of data from a knowledge graph in various export formats and data models.", URI:"KGBB_URI", category:"ClassExpression", operational_KGBB:"false"}})
    CREATE (confidenceLevelStatementUnitKGBB:ConfidenceLevelStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"confidence level specification statementUnit Knowledge Graph Building Block", description:"An statementUnit Knowledge Graph Building Block that manages data referring to the specification of confidence levels for particular statementUnits, itemUnits, or entries.", URI:"ConfidenceLevelStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    CREATE (granperspectiveKGBB:GranularityPerspectiveKGBB:KGBB:ClassExpression:Entity {{name:"granularity perspective Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages data referring to granularity trees.", URI:"GranularityPerspectiveKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbb)
    CREATE (parthood_basedgranperspectiveKGBB:ParthoodBasedGranularityPerspectiveKGBB:GranularityPerspectiveKGBB:KGBB:ClassExpression:Entity {{name:"parthood-based granularity perspective Knowledge Graph Building Block", description:"A granularity perspective Knowledge Graph Building Block that manages data referring to granularity trees that are based on the parthood relation.", partial_order_relation:"HAS_PART", URI:"Parthood-BasedGranularityPerspectiveKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(granperspectiveKGBB)
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
    )', data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(parthood_basedgranperspectiveKGBB)
    CREATE (entrykgbb:EntryKGBB:KGBB:ClassExpression:Entity {{name:"entry Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages entry data.", URI:"EntryKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"entry"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbb)
    //SCHOLARLY PUBLICATION ENTRY KGBB
    CREATE (scholarlyPublicationEntrykgbb:ScholarlyPublicationEntryKGBB:EntryKGBB:KGBB:ClassExpression:Entity {{name:"scholarly publication entry Knowledge Graph Building Block", description:"An entry Knowledge Graph Building Block that manages data about a scholarly publication.", relevant_classes_URI:["http://orkg???????2", "http://orkg/researchtopic_1"], URI:"ScholarlyPublicationEntryKGBB_URI", category:"ClassExpression", operational_KGBB:"true",storage_model_cypher_code:'MATCH (ORKGEntryClass) WHERE ORKGEntryClass.URI="orkg_entry_class_URI"
    CREATE (entry:orkg_ScholarlyPublicationEntry_IND:orkg_Entry_IND:iao_Document_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"Publication entry unit", URI:"entry_uri", type:"scholarly_publication_entry_URI", entry_doi:"{doiEntry}", publication_doi:"pub_doiX", publication_title:"pub_titleX", entry_URI:"entry_uri", description:"This type of entry models information about a particular research paper.", KGBB_URI:"ScholarlyPublicationEntryKGBB_URI", object_URI:"new_individual_uri1", node_type: "entry", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})-[:HAS_DOI {{category:"DataPropertyExpression", URI:"http://prismstandard.org/namespaces/basic/2.0/doi", entry_URI:"entry_uri"}}]->(doi_entry:EntryDOI_IND:DOI_IND:Literal_IND {{value:"some entry DOI", current_version:"true", entry_doi:"{doiEntry}", entry_URI:"entry_uri", category:"NamedIndividual"}})
    CREATE (entry)-[:IDENTIFIER {{category:"DataPropertyExpression", URI:"https://dublincore.org/specifications/dublin-core/dcmi-terms/#identifier", entry_URI:"entry_uri"}}]->(doi_entry)
    CREATE (publication:orkg_ResearchPaper_IND:iao_PublicationAboutAnInvestigation_IND:iao_Document_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"pub_titleX", type:"http://orkg???????2", publication_doi:"pub_doiX", publication_year:pub_yearX, publication_authors:"pub_authorsX", URI:"new_individual_uri1", publication_journal:"pub_journalX", publication_publisher:"Xpub_publisherX", entry_URI:"entry_uri", category:"NamedIndividual", data_node_type:["entry_object"], current_version:"true", statementUnit_URI:["NULL"], itemUnit_URI:["NULL"], last_updated_on:localdatetime(), versioned_doi:["NULL"], created_on:localdatetime(), created_by:"{creator}", created_with:"{createdWith}"}})-[:HAS_DOI {{category:"DataPropertyExpression", URI:"http://prismstandard.org/namespaces/basic/2.0/doi", entry_URI:"entry_uri"}}]->(doi_publication:PublicationDOI_IND:DOI_IND:Literal_IND {{value:"pub_doiX", publication_doi:"pub_doiX", entry_URI:"entry_uri", category:"NamedIndividual", versioned_doi:["NULL"], current_version:"true"}})
    CREATE (publication)-[:IDENTIFIER {{category:"DataPropertyExpression", URI:"https://dublincore.org/specifications/dublin-core/dcmi-terms/#identifier", entry_URI:"entry_uri"}}]->(doi_publication)
    CREATE (entry)-[:IS_TRANSLATION_OF {{category:"ObjectPropertyExpression", URI:"http://purl.org/vocab/frbr/core#translationOf", entry_URI:"entry_uri", description:"It identifies the original expression of a translated one."}}]->(publication)
    CREATE (publication)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri2"}}]->(ResearchActivity:ResearchActivity_ind:orkg_ResearchActivity_IND:obi_Investigation_IND:obi_PlannedProcess_IND:bfo_Process_IND:NamedIndividual:Entity {{name:"research activity", versioned_doi:["NULL"], dataset_doi:["NULL"], description:"A planned process that has been planned and executed by some research agent and that has some research result. The process ends if some specific research objective is achieved.", URI:"new_individual_uri3", ontology_ID:"ORKG", itemUnit_URI:"new_individual_uri2", type:"http://orkg???????5", instance_label:"Research overview", category:"NamedIndividual", entry_URI:"entry_uri", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", data_node_type:["itemUnit_object"]}})
    CREATE (entry)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri2"}}]->(ResearchActivityItemUnit_ind:orkg_ResearchActivityItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research overview item unit", description:"This item unit models all data of a particular research activity as it is documented in a particular research paper.", URI:"new_individual_uri2", itemUnit_URI:"new_individual_uri2", type:"ResearchActivity_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"entry_uri", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", editable:"false", object_URI:"new_individual_uri3", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"Research overview"}})
    CREATE (ResearchActivityItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri2"}}]->(ResearchActivity)
    CREATE (entry)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri2"}}]->(ResearchActivity)
    CREATE (ResearchActivityItemUnit_ind)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri4"}}]->(ResearchResultItemUnit_ind:orkg_ResearchResultItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result item unit", description:"This item unit models a research result documented in a particular research paper.", URI:"new_individual_uri4", itemUnit_URI:"new_individual_uri4", type:"ResearchResult_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"entry_uri", KGBB_URI:"ResearchResultItemUnitKGBB_URI", object_URI:"new_individual_uri5", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"Research result"}})
    CREATE (ResearchActivityItemUnit_ind)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri10"}}]->(researchActivityOutputStatementUnit_Ind:orkg_ResearchActivityOutputRelationStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity output relation statement unit", description:"This statement unit models the relation between a particular research activity and one of its research result outputs.", URI:"new_individual_uri10", statementUnit_URI:"new_individual_uri10", itemUnit_URI:"new_individual_uri2", type:"Research_Activity_Output_Relation_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"entry_uri", KGBB_URI:"ResearchActivityOutputRelationStatementUnitKGBB_URI", object_URI:"new_individual_uri5", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research activity output"}})
    CREATE (ResearchActivityItemUnit_ind)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri11"}}]->(researchActivityMethodStatementUnit_Ind:orkg_ResearchActivityMethodRelationStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity method relation statement unit", description:"This statement unit models the relation between a particular research activity and one of the research methods it realizes.", URI:"new_individual_uri11", statementUnit_URI:"new_individual_uri11", itemUnit_URI:"new_individual_uri2", type:"Research_Activity_Method_Relation_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"entry_uri", KGBB_URI:"ResearchActivityMethodRelationStatementUnitKGBB_URI", object_URI:"new_individual_uri7", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research activity method"}})
    CREATE (ResearchActivity)-[:HAS_SPECIFIED_OUTPUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000299", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri2", description:"A relation between a planned process and a continuant participating in that process. The presence of the continuant at the end of the process is explicitly specified in the objective specification which the process realizes the concretization of."}}]->(researchResult:orkg_ResearchResult_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri5", type:"http://orkg???????1", name:"research result", instance_label:"Research result", ontology_ID:"ORKG", description:"An information content entity that is intended to be a truthful statement about something and is the output of some research activity. It is usually acquired by some research method which reliably tends to produce (approximately) truthful statements (cf. iao:data item).", data_node_type:["itemUnit_object"], current_version:"true", entry_URI:"entry_uri", itemUnit_URI:["new_individual_uri2", "new_individual_uri4", "new_individual_uri8"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (researchActivityOutputStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri10"}}]->(ResearchActivity)
    CREATE (researchActivityOutputStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri10"}}]->(ResearchResultItemUnit_ind)
    CREATE (ResearchResultItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri4"}}]->(researchResult)
    CREATE (researchResult)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri4", description:"a core relation that holds between a whole and its part."}}]->(publication)
    CREATE (ResearchActivityItemUnit_ind)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri6"}}]->(ResearchMethodItemUnit_ind:orkg_ResearchMethodItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method item unit", description:"This item unit models a research method documented in a particular research paper.", URI:"new_individual_uri6", itemUnit_URI:"new_individual_uri6", type:"ResearchMethod_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"entry_uri", KGBB_URI:"ResearchMethodItemUnitKGBB_URI", object_URI:"new_individual_uri7", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"Research method"}})
    CREATE (ResearchActivity)-[:REALIZES {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000055", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri2", description:"to say that b realizes c at t is to assert that there is some material entity d & b is a process which has participant d at t & c is a disposition or role of which d is bearer_of at t& the type instantiated by b is correlated with the type instantiated by c. (axiom label in BFO2 Reference: [059-003])."}}]->(researchMethod:orkg_ResearchMethod_IND:iao_PlanSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri7", type:"http://orkg???????4", name:"research method", instance_label:"Research method", ontology_ID:"ORKG", description:"An information content entity that specifies how to conduct some research activity. It usually has some research objective as its part. It instructs some research agent how to achieve the objectives by taking the actions it specifies.", data_node_type:["itemUnit_object"], current_version:"true", entry_URI:"entry_uri", itemUnit_URI:["new_individual_uri2", "new_individual_uri6"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (researchActivityMethodStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri11"}}]->(ResearchActivity)
    CREATE (researchActivityMethodStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri11"}}]->(ResearchMethodItemUnit_ind)
    CREATE (ResearchMethodItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri6"}}]->(researchMethod)
    CREATE (ResearchActivityItemUnit_ind)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri8"}}]->(ResearchObjectiveItemUnit_ind:orkg_ResearchObjectiveItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective item unit", description:"This item unit models a research objective documented in a particular research paper.", URI:"new_individual_uri8", itemUnit_URI:"new_individual_uri8", type:"ResearchObjective_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"entry_uri", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", object_URI:"new_individual_uri9", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"Research objective"}})
    CREATE (ResearchActivityItemUnit_ind)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri12"}}]->(researchActivityObjetiveRelationStatementUnit_Ind:orkg_ResearchActivityObjectiveRelationStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity objective relation statement unit", description:"This statement unit models the relation between a particular research activity and one of the research objectives it achieves.", URI:"new_individual_uri12", statementUnit_URI:"new_individual_uri12", itemUnit_URI:"new_individual_uri2", type:"Research_Activity_Objective_Relation_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"entry_uri", KGBB_URI:"ResearchActivityObjectiveRelationStatementUnitKGBB_URI", object_URI:"new_individual_uri9", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research activity objective"}})
    CREATE (ResearchActivity)-[:ACHIEVES_PLANNED_OBJECTIVE {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000417", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri2", description:"This relation obtains between a planned process and a objective specification when the criteria specified in the objective specification are met at the end of the planned process."}}]->(researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri9", type:"http://orkg???????3", name:"research objective", instance_label:"Research objective", ontology_ID:"ORKG", description:"An information content entity that describes an intended process endpoint for some research activity.", data_node_type:["itemUnit_object"], current_version:"true", entry_URI:"entry_uri", itemUnit_URI:["new_individual_uri2", "new_individual_uri6", "new_individual_uri8"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (researchActivityObjetiveRelationStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri12"}}]->(ResearchActivity)
    CREATE (researchActivityObjetiveRelationStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri12"}}]->(ResearchObjectiveItemUnit_ind)
    CREATE (ResearchObjectiveItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri8"}}]->(researchObjective)
    CREATE (researchObjective)-[:HAS_ACHIEVED_RESULT {{category:"ObjectPropertyExpression", URI:"http://orkg_has_achieved_result", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri8", description:"This relation obtains between a research objective and a research result when the criteria specified in the objective specification are met at the end of a planned process which has the research result as its output."}}]->(researchResult)
    CREATE (researchMethod)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"entry_uri", itemUnit_URI:"new_individual_uri6", description:"a core relation that holds between a whole and its part."}}]->(researchObjective)', search_cypher_code:"cypherQuery", data_item_type:"entry"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(entrykgbb)
    CREATE (itemUnitkgbb:ItemUnitKGBB:KGBB:ClassExpression:Entity {{name:"itemUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages itemUnit data.", URI:"ItemUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"itemUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbb)
    //RESEARCH ACTIVITY ITEM_UNIT KGBB
    CREATE (ResearchActivityItemUnitkgbb:ResearchActivityItemUnitKGBB:ItemUnitKGBB:KGBB:ClassExpression:Entity {{name:"research activity itemUnit Knowledge Graph Building Block", description:"A itemUnit Knowledge Graph Building Block that manages data about the research activity that is documented in a particular research paper.", URI:"ResearchActivityItemUnitKGBB_URI", category:"ClassExpression", relevant_classes_URI:["http://orkg???????5"], storage_model_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}})
    MATCH (publication_node) WHERE publication_node.entry_URI="{entryURI}" AND ("entry_object" IN publication_node.data_node_type)
    CREATE (publication_node)-[:IS_ABOUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000136", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchActivity:ResearchActivity_ind:orkg_ResearchActivity_IND:obi_Investigation_IND:obi_PlannedProcess_IND:bfo_Process_IND:NamedIndividual:Entity {{name:"research activity", versioned_doi:["NULL"], dataset_doi:["NULL"], description:"A planned process that has been planned and executed by some research agent and that has some research result. The process ends if some specific research objective is achieved.", URI:"new_individual_uri1", ontology_ID:"ORKG", itemUnit_URI:"{itemUnit_uri}", type:"http://orkg???????5", instance_label:"Research overview", category:"NamedIndividual", entry_URI:"{entryURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", data_node_type:["itemUnit_object"]}})
    CREATE (entry_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchActivityItemUnit_ind:orkg_ResearchActivityItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research overview item unit", description:"This itemUnit models all data of a particular research activity as it is documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchActivity_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", editable:"false", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"Research overview"}})
    CREATE (ResearchActivityItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchActivity)
    CREATE (entry_node)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchActivity)', from_activity_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (object_node)-[:HAS_OCCURRENT_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000117", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchActivity:ResearchActivity_ind:orkg_ResearchActivity_IND:obi_Investigation_IND:obi_PlannedProcess_IND:bfo_Process_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["itemUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchActivityItemUnitIND_URI", user_input:"{itemUnit_uri}"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchActivityItemUnit_ind:orkg_ResearchActivityItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity item unit", description:"This itemUnit models all data of a particular research activity as it is documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchActivity_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"itemUnit_URI:parent_data_item_node.URI", statementUnit_URI:"new_individual_uri2"}}]->(researchActivityParthoodStatementUnit_ind:orkg_ResearchActivityParthoodStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"orkg research activity parthood statementUnit", description:"This statementUnit models the relation between a particular research activity and one its activity parts (i.e., research steps).", URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri2", type:"Research_Activity_Parthood_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchActivityParthoodStatementUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research activity parthood"}})
    CREATE (researchActivityParthoodStatementUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchActivityParthoodStatementUnit_ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(ResearchActivityItemUnit_ind)
    CREATE (ResearchActivityItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchActivity)', from_method_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (ResearchActivity:ResearchActivity_ind:orkg_ResearchActivity_IND:obi_Investigation_IND:obi_PlannedProcess_IND:bfo_Process_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["itemUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchActivityItemUnitIND_URI", user_input:"{itemUnit_uri}"}})-[:REALIZES {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000055", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"to say that b realizes c at t is to assert that there is some material entity d & b is a process which has participant d at t & c is a disposition or role of which d is bearer_of at t& the type instantiated by b is correlated with the type instantiated by c. (axiom label in BFO2 Reference: [059-003])."}}]->(object_node)
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchActivityItemUnit_ind:orkg_ResearchActivityItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity item unit", description:"This itemUnit models all data of a particular research activity as it is documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchActivity_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(researchMethodActivityStatementUnit_Ind:orkg_ResearchMethodActivityRelationStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method activity relation statement unit", description:"This statementUnit models the relation between a particular research method and the activity that realizes it.", URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri2", type:"Research_Method_Activity_Relation_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchMethodActivityRelationStatementUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research method activity"}})
    CREATE (researchMethodActivityStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchMethodActivityStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(ResearchActivityItemUnit_ind)
    CREATE (ResearchActivityItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchActivity)', from_result_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (ResearchActivity:ResearchActivity_ind:orkg_ResearchActivity_IND:obi_Investigation_IND:obi_PlannedProcess_IND:bfo_Process_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["itemUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchActivityItemUnitIND_URI", user_input:"{itemUnit_uri}"}})-[:HAS_SPECIFIED_OUTPUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000299", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"A relation between a planned process and a continuant participating in that process. The presence of the continuant at the end of the process is explicitly specified in the objective specification which the process realizes the concretization of."}}]->(object_node)
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchActivityItemUnit_ind:orkg_ResearchActivityItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research overview item unit", description:"This itemUnit models all data of a particular research activity as it is documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchActivity_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(researchResultActivityRelationStatementUnit_Ind:orkg_ResearchResultActivityRelationStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result activity relation statement unit", description:"This statementUnit models the relation between a particular research result and the research activity that has it as its output.", URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri2", type:"Research_Result_Activity_Relation_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchResultActivityRelationStatementUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research result activity"}})
    CREATE (researchResultActivityRelationStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchResultActivityRelationStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(ResearchActivityItemUnit_ind)
    CREATE (ResearchActivityItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchActivity)',  from_objective_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (ResearchActivity:ResearchActivity_ind:orkg_ResearchActivity_IND:obi_Investigation_IND:obi_PlannedProcess_IND:bfo_Process_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["itemUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchActivityItemUnitIND_URI", user_input:"{itemUnit_uri}"}})-[:ACHIEVES_PLANNED_OBJECTIVE {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000417", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"This relation obtains between a planned process and a objective specification when the criteria specified in the objective specification are met at the end of the planned process."}}]->(object_node)
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchActivityItemUnit_ind:orkg_ResearchActivityItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research overview item unit", description:"This itemUnit models all data of a particular research activity as it is documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchActivity_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(researchObjectiveActivityRelationStatementUnit_Ind:orkg_ResearchObjectiveActivityRelationStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective activity relation statement unit", description:"This statementUnit models the relation between a particular research objective and the research activity that achieves it.", URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri2", type:"Research_Objective_Activity_Relation_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchObjectiveActivityRelationStatementUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research objective activity"}})
    CREATE (researchObjectiveActivityRelationStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchObjectiveActivityRelationStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(ResearchActivityItemUnit_ind)
    CREATE (ResearchActivityItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchActivity)', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(researchActivityItemUnit_ind:orkg_ResearchActivityItemUnit_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET researchActivityItemUnit_ind.last_updated_on = localdatetime(), researchActivityItemUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, researchActivityItemUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN researchActivityItemUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET researchActivityItemUnit_ind.contributed_by = researchActivityItemUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, researchActivityItemUnit_ind
    MATCH (researchActivityItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchAct_old:orkg_ResearchActivity_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, researchActivityItemUnit_ind, researchAct_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchAct_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, researchActivityItemUnit_ind, researchAct_old SET researchAct_old.current_version = "false"
    WITH researchActivityItemUnit_ind
    MATCH (researchActivityItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchAct_new:orkg_ResearchActivity_IND {{current_version:"true"}})
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(researchActivityItemUnit_ind:orkg_ResearchActivityItemUnit_IND {{URI:"{itemUnit_uri}", current_version:"true"}}) SET researchActivityItemUnit_ind.last_updated_on = localdatetime(), researchActivityItemUnit_ind.itemUnit_label = "$_input_name_$ [$_ontology_ID_$]", researchActivityItemUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, researchActivityItemUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN researchActivityItemUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET researchActivityItemUnit_ind.contributed_by = researchActivityItemUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, researchActivityItemUnit_ind
    MATCH (researchActivityItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchAct_old:orkg_ResearchActivity_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, researchActivityItemUnit_ind, researchAct_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchAct_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, researchActivityItemUnit_ind, researchAct_old SET researchAct_old.current_version = "false"
    WITH researchActivityItemUnit_ind
    MATCH (researchActivityItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchAct_new:orkg_ResearchActivity_IND {{current_version:"true"}})
    SET researchAct_new.name = "$_input_name_$", researchAct_new.instance_label = "$_input_name_$", researchAct_new.ontology_ID = "$_ontology_ID_$", researchAct_new.description = "$_input_description_$", researchAct_new.URI = "new_individual_uri1", researchAct_new.type = "$_input_type_$", researchAct_new.created_on = localdatetime(), researchAct_new.last_updated_on = localdatetime(), researchAct_new.created_by = "{creator}", researchAct_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", operational_KGBB:"true", data_item_type:"itemUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(itemUnitkgbb)
    //RESEARCH OBJECTIVE ITEM_UNIT KGBB
    CREATE (ResearchObjectiveItemUnitkgbb:ResearchObjectiveItemUnitKGBB:ItemUnitKGBB:KGBB:ClassExpression:Entity {{name:"research objective itemUnit Knowledge Graph Building Block", description:"A itemUnit Knowledge Graph Building Block that manages data about the research objective that is documented in a particular research paper.", URI:"ResearchObjectiveItemUnitKGBB_URI", category:"ClassExpression", relevant_classes_URI:["http://orkg???????3"], storage_model_cypher_code:'MATCH (parent_data_item_node:orkg_ResearchActivityItemUnit_IND {{entry_URI:"{entryURI}"}})
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI
    OPTIONAL MATCH (object_node)-[:HAS_SPECIFIED_OUTPUT]->(researchResult:orkg_ResearchResult_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, researchResult
    OPTIONAL MATCH (object_node)-[:REALIZES]->(researchMethod:orkg_ResearchMethod_IND {{current_version:"true"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchObjectiveItemUnit_ind:orkg_ResearchObjectiveItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective item unit", description:"This itemUnit models a research objective documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchObjective_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"Research objective"}})
    CREATE (object_node)-[:ACHIEVES_PLANNED_OBJECTIVE {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000417", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"This relation obtains between a planned process and a objective specification when the criteria specified in the objective specification are met at the end of the planned process."}}]->(researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"http://orkg???????3", name:"research objective", instance_label:"Research objective", ontology_ID:"ORKG", description:"An information content entity that describes an intended process endpoint for some research activity.", data_node_type:["itemUnit_object"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (ResearchObjectiveItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(researchObjective)
    WITH parent_data_item_node, object_node, researchResult, researchMethod, researchObjective
    FOREACH (i IN CASE WHEN researchResult IS NOT NULL THEN [1] ELSE [] END |
    CREATE (researchObjective)-[:HAS_ACHIEVED_RESULT {{category:"ObjectPropertyExpression", URI:"http://orkg_has_achieved_result", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"This relation obtains between a research objective and a research result when the criteria specified in the objective specification are met at the end of a planned process which has the research result as its output."}}]->(researchResult)
    )
    WITH parent_data_item_node, object_node, researchResult, researchMethod, researchObjective
    FOREACH (i IN CASE WHEN researchMethod IS NOT NULL THEN [1] ELSE [] END |
    CREATE (researchMethod)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(researchObjective)
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(ResearchObjectiveItemUnit_ind:orkg_ResearchObjectiveItemUnit_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET ResearchObjectiveItemUnit_ind.last_updated_on = localdatetime(), ResearchObjectiveItemUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, ResearchObjectiveItemUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchObjectiveItemUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchObjectiveItemUnit_ind.contributed_by = ResearchObjectiveItemUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, ResearchObjectiveItemUnit_ind
    MATCH (ResearchObjectiveItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchObjective_old:orkg_ResearchObjective_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, ResearchObjectiveItemUnit_ind, researchObjective_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchObjective_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchObjectiveItemUnit_ind, researchObjective_old SET researchObjective_old.current_version = "false"
    WITH ResearchObjectiveItemUnit_ind
    MATCH (ResearchObjectiveItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchObjective_new:orkg_ResearchObjective_IND {{current_version:"true"}})
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(ResearchObjectiveItemUnit_ind:orkg_ResearchObjectiveItemUnit_IND {{URI:"{itemUnit_uri}", current_version:"true"}}) SET ResearchObjectiveItemUnit_ind.last_updated_on = localdatetime(), ResearchObjectiveItemUnit_ind.itemUnit_label = "$_input_name_$ [$_ontology_ID_$]", ResearchObjectiveItemUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, ResearchObjectiveItemUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchObjectiveItemUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchObjectiveItemUnit_ind.contributed_by = ResearchObjectiveItemUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, ResearchObjectiveItemUnit_ind
    MATCH (ResearchObjectiveItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchObjective_old:orkg_ResearchObjective_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, ResearchObjectiveItemUnit_ind, researchObjective_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchObjective_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchObjectiveItemUnit_ind, researchObjective_old SET researchObjective_old.current_version = "false"
    WITH ResearchObjectiveItemUnit_ind
    MATCH (ResearchObjectiveItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchObjective_new:orkg_ResearchObjective_IND {{current_version:"true"}})
    SET researchObjective_new.name = "$_input_name_$", researchObjective_new.instance_label = "$_input_name_$", researchObjective_new.ontology_ID = "$_ontology_ID_$", researchObjective_new.type = "$_input_type_$", researchObjective_new.description = "$_input_description_$", researchObjective_new.URI = "new_individual_uri1", researchObjective_new.created_on = localdatetime(), researchObjective_new.last_updated_on = localdatetime(), researchObjective_new.created_by = "{creator}", researchObjective_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", from_activity_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH entry_node, parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchObjectiveItemUnit_ind:orkg_ResearchObjectiveItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective item unit", description:"This itemUnit models a research objective documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchObjective_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (object_node)-[:ACHIEVES_PLANNED_OBJECTIVE {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000417", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"This relation obtains between a planned process and a objective specification when the criteria specified in the objective specification are met at the end of the planned process."}}]->(researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["itemUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchObjectiveItemUnitIND_URI", user_input:"{itemUnit_uri}"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(researchActivityObjetiveRelationStatementUnit_Ind:orkg_ResearchActivityObjectiveRelationStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity objective relation statement unit", description:"This statement unit models the relation between a particular research activity and one of the research objectives it achieves.", URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri2", itemUnit_URI:parent_data_item_node.URI, type:"Research_Activity_Objective_Relation_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchActivityObjectiveRelationStatementUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research activity objective"}})
    CREATE (researchActivityObjetiveRelationStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchActivityObjetiveRelationStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(ResearchObjectiveItemUnit_ind)
    CREATE (ResearchObjectiveItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(researchObjective)', from_method_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH entry_node, parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchObjectiveItemUnit_ind:orkg_ResearchObjectiveItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective item unit", description:"This itemUnit models a research objective documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchObjective_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["itemUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchObjectiveItemUnitIND_URI", user_input:"{itemUnit_uri}"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(researchMethodObjectiveRelationStatementUnit_Ind:orkg_ResearchMethodObjectiveRelationStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method objective relation statement unit", description:"This statementUnit models the relation between a particular research method and its objective specification part.", URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri2", type:"Research_Method_Objective_Relation_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchMethodObjectiveRelationStatementUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research method objective"}})
    CREATE (researchMethodObjectiveRelationStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchMethodObjectiveRelationStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(ResearchObjectiveItemUnit_ind)
    CREATE (ResearchObjectiveItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(researchObjective)', from_result_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH entry_node, parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchObjectiveItemUnit_ind:orkg_ResearchObjectiveItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective item unit", description:"This itemUnit models a research objective documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchObjective_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["itemUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchObjectiveItemUnitIND_URI", user_input:"{itemUnit_uri}"}})-[:HAS_ACHIEVED_RESULT {{category:"ObjectPropertyExpression", URI:"http://orkg_has_achieved_result", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"This relation obtains between a research objective and a research result when the criteria specified in the objective specification are met at the end of a planned process which has the research result as its output."}}]->(object_node)
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(researchResultObjectiveRelationStatementUnit_Ind:orkg_ResearchResultObjectiveRelationStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result objective relation statement unit", description:"This statementUnit models the relation between a particular research result and the research objective that achieved it.", URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri2", type:"Research_Result_Objective_Relation_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchResultObjectiveRelationStatementUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research result objective"}})
    CREATE (researchResultObjectiveRelationStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchResultObjectiveRelationStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(ResearchObjectiveItemUnit_ind)
    CREATE (ResearchObjectiveItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(researchObjective)', from_objective_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH entry_node, parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_dcontains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchObjectiveItemUnit_ind:orkg_ResearchObjectiveItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective item unit", description:"This itemUnit models a research objective documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchObjective_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(researchObjective:orkg_ResearchObjective_IND:iao_ObjectiveSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["itemUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchObjectiveItemUnitIND_URI", user_input:"{itemUnit_uri}"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(researchObjectiveParthoodStatementUnit_Ind:orkg_ResearchObjectiveParthoodStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective parthood statement unit", description:"This statement unit models the relation between a particular research objective and its objective parts.", URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri2", type:"Research_Objective_Parthood_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchObjectiveParthoodStatementUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research objective parthood"}})
    CREATE (researchObjectiveParthoodStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchObjectiveParthoodStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(ResearchObjectiveItemUnit_ind)
    CREATE (ResearchObjectiveItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(researchObjective)', operational_KGBB:"true", data_item_type:"itemUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(itemUnitkgbb)
    //RESEARCH RESULT ITEM_UNIT KGBB
    CREATE (ResearchResultItemUnitkgbb:ResearchResultItemUnitKGBB:ItemUnitKGBB:KGBB:ClassExpression:Entity {{name:"research result itemUnit Knowledge Graph Building Block", description:"A itemUnit Knowledge Graph Building Block that manages data about the research results documented in a particular research paper.", relevant_classes_URI:["http://orkg???????1"], URI:"ResearchResultItemUnitKGBB_URI", category:"ClassExpression", storage_model_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}})
    MATCH (publication_node) WHERE publication_node.entry_URI="{entryURI}" AND ("entry_object" IN publication_node.data_node_type)
    MATCH (parent_data_item_node:orkg_ResearchActivityItemUnit_IND {{entry_URI:entry_node.URI}})
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI
    OPTIONAL MATCH (object_node)-[:ACHIEVES_PLANNED_OBJECTIVE]->(researchObjective:orkg_ResearchObjective_IND {{current_version:"true"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchResultItemUnit_ind:orkg_ResearchResultItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result item unit", description:"This itemUnit models a research result documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchResult_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchResultItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"Research result"}})
    CREATE (object_node)-[:HAS_SPECIFIED_OUTPUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000299", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"A relation between a planned process and a continuant participating in that process. The presence of the continuant at the end of the process is explicitly specified in the objective specification which the process realizes the concretization of."}}]->(researchResult:orkg_ResearchResult_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"http://orkg???????1", name:"research result", instance_label:"Research result", ontology_ID:"ORKG", description:"An information content entity that is intended to be a truthful statement about something and is the output of some research activity. It is usually acquired by some research method which reliably tends to produce (approximately) truthful statements (cf. iao:data item).", data_node_type:["itemUnit_object"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (ResearchResultItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(researchResult)
    CREATE (researchResult)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(publication_node)
    WITH parent_data_item_node, object_node, researchObjective, researchResult
    FOREACH (i IN CASE WHEN researchObjective IS NOT NULL THEN [1] ELSE [] END |
    CREATE (researchObjective)-[:HAS_ACHIEVED_RESULT {{category:"ObjectPropertyExpression", URI:"http://orkg_has_achieved_result", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"This relation obtains between a research objective and a research result when the criteria specified in the objective specification are met at the end of a planned process which has the research result as its output."}}]->(researchResult))', from_result_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchResultItemUnit_ind:orkg_ResearchResultItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result item unit", description:"This itemUnit models a research result documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchResult_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchResultItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(researchResult:orkg_ResearchResult_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["itemUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchResultItemUnitIND_URI", user_input:"{itemUnit_uri}"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(researchResultParthoodStatementUnit_Ind:orkg_ResearchResultParthoodStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result parthood statement unit", description:"This statement unit models the relation between a particular research result and one of its research result parts.", URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri2", type:"Research_Activity_Parthood_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchResultParthoodStatementUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research result parthood"}})
    CREATE (researchResultParthoodStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchResultParthoodStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(ResearchResultItemUnit_ind)
    CREATE (ResearchResultItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(researchResult)', from_objective_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchResultItemUnit_ind:orkg_ResearchResultItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result item unit", description:"This itemUnit models a research result documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchResult_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchResultItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (object_node)-[:HAS_ACHIEVED_RESULT {{category:"ObjectPropertyExpression", URI:"http://orkg_has_achieved_result", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(researchResult:orkg_ResearchResult_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["itemUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchResultItemUnitIND_URI", user_input:"{itemUnit_uri}"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(researchObjectiveResultRelationStatementUnit_Ind:orkg_ResearchObjectiveResultRelationStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective result relation statement unit", description:"This statementUnit models the relation between a particular research objective and the research result that it achieved.", URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri2", type:"Research_Objective_Result_Relation_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchObjectiveResultRealtionStatementUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research objective result"}})
    CREATE (researchObjectiveResultRelationStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchObjectiveResultRelationStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(ResearchResultItemUnit_ind)
    CREATE (ResearchResultItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(researchResult)', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(ResearchResultItemUnit_ind:orkg_ResearchResultItemUnit_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET ResearchResultItemUnit_ind.last_updated_on = localdatetime(), ResearchResultItemUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, ResearchResultItemUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchResultItemUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchResultItemUnit_ind.contributed_by = ResearchResultItemUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, ResearchResultItemUnit_ind
    MATCH (ResearchResultItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchResult_old:orkg_ResearchResult_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, ResearchResultItemUnit_ind, researchResult_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchResult_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchResultItemUnit_ind, researchResult_old SET researchResult_old.current_version = "false"
    WITH ResearchResultItemUnit_ind
    MATCH (ResearchResultItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchResult_new:orkg_ResearchResult_IND {{current_version:"true"}})
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(ResearchResultItemUnit_ind:orkg_ResearchResultItemUnit_IND {{URI:"{itemUnit_uri}", current_version:"true"}}) SET ResearchResultItemUnit_ind.last_updated_on = localdatetime(), ResearchResultItemUnit_ind.itemUnit_label = "$_input_name_$ [$_ontology_ID_$]", ResearchResultItemUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, ResearchResultItemUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchResultItemUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchResultItemUnit_ind.contributed_by = ResearchResultItemUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, ResearchResultItemUnit_ind
    MATCH (ResearchResultItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchResult_old:orkg_ResearchResult_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, ResearchResultItemUnit_ind, researchResult_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchResult_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchResultItemUnit_ind, researchResult_old SET researchResult_old.current_version = "false"
    WITH ResearchResultItemUnit_ind
    MATCH (ResearchResultItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchResult_new:orkg_ResearchResult_IND {{current_version:"true"}})
    SET researchResult_new.name = "$_input_name_$", researchResult_new.instance_label = "$_input_name_$", researchResult_new.ontology_ID = "$_ontology_ID_$", researchResult_new.type = "$_input_type_$", researchResult_new.description = "$_input_description_$", researchResult_new.URI = "new_individual_uri1", researchResult_new.created_on = localdatetime(), researchResult_new.last_updated_on = localdatetime(), researchResult_new.created_by = "{creator}", researchResult_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", from_activity_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node MATCH (publication_node) WHERE publication_node.entry_URI="{entryURI}" AND ("entry_object" IN publication_node.data_node_type)
    WITH entry_node, publication_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, publication_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH entry_node, publication_node, parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchResultItemUnit_ind:orkg_ResearchResultItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result item unit", description:"This itemUnit models a research result documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchResult_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchResultItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(researchActivityOutputStatementUnit_Ind:orkg_ResearchActivityOutputRelationStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity output relation statement unit", description:"This statement unit models the relation between a particular research activity and one of its research result outputs.", URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri2", type:"Research_Activity_Output_Relation_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchActivityOutputRelationStatementUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research activity output"}})
    CREATE (object_node)-[:HAS_SPECIFIED_OUTPUT {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/OBI_0000299", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"A relation between a planned process and a continuant participating in that process. The presence of the continuant at the end of the process is explicitly specified in the objective specification which the process realizes the concretization of."}}]->(researchResult:orkg_ResearchResult_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["itemUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchResultItemUnitIND_URI", user_input:"{itemUnit_uri}"}})
    CREATE (researchActivityOutputStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(researchResult)
    CREATE (researchActivityOutputStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(ResearchResultItemUnit_ind)
    CREATE (ResearchResultItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(object_node)
    CREATE (researchResult)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(publication_node)', operational_KGBB:"true", data_item_type:"itemUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(itemUnitkgbb)
    //RESEARCH METHOD ITEM_UNIT KGBB
    CREATE (ResearchMethodItemUnitkgbb:ResearchMethodItemUnitKGBB:ItemUnitKGBB:KGBB:ClassExpression:Entity {{name:"research method itemUnit Knowledge Graph Building Block", description:"A itemUnit Knowledge Graph Building Block that manages data about the research methods documented in a particular research paper.", relevant_classes_URI:["http://orkg???????4"], URI:"ResearchMethodItemUnitKGBB_URI", category:"ClassExpression", storage_model_cypher_code:'MATCH (parent_data_item_node:orkg_ResearchActivityItemUnit_IND {{entry_URI:"{entryURI}"}})
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI
    OPTIONAL MATCH (object_node)-[:ACHIEVES_PLANNED_OBJECTIVE]->(researchObjective:orkg_ResearchObjective_IND {{current_version:"true"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchMethodItemUnit_ind:orkg_ResearchMethodItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method item unit", description:"This itemUnit models a research method documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchMethod_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchMethodItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"Research method"}})
    CREATE (object_node)-[:REALIZES {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000055", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"to say that b realizes c at t is to assert that there is some material entity d & b is a process which has participant d at t & c is a disposition or role of which d is bearer_of at t& the type instantiated by b is correlated with the type instantiated by c. (axiom label in BFO2 Reference: [059-003])."}}]->(researchMethod:orkg_ResearchMethod_IND:iao_PlanSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"http://orkg???????4", name:"research method", instance_label:"Research method", ontology_ID:"ORKG", description:"An information content entity that specifies how to conduct some research activity. It usually has some research objective as its part. It instructs some research agent how to achieve the objectives by taking the actions it specifies.", data_node_type:["itemUnit_object"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (ResearchMethodItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(researchMethod)
    WITH parent_data_item_node, object_node, researchObjective, researchMethod
    FOREACH (i IN CASE WHEN researchObjective IS NOT NULL THEN [1] ELSE [] END |
    CREATE (researchMethod)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(researchObjective)
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(ResearchMethodItemUnit_ind:orkg_ResearchMethodItemUnit_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET ResearchMethodItemUnit_ind.last_updated_on = localdatetime(), ResearchMethodItemUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, ResearchMethodItemUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchMethodItemUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchMethodItemUnit_ind.contributed_by = ResearchMethodItemUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, ResearchMethodItemUnit_ind
    MATCH (ResearchMethodItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchMethod_old:orkg_ResearchMethod_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, ResearchMethodItemUnit_ind, researchMethod_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchMethod_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchMethodItemUnit_ind, researchMethod_old SET researchMethod_old.current_version = "false"
    WITH ResearchMethodItemUnit_ind
    MATCH (ResearchMethodItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchMethod_new:orkg_ResearchMethod_IND {{current_version:"true"}})
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(ResearchMethodItemUnit_ind:orkg_ResearchMethodItemUnit_IND {{URI:"{itemUnit_uri}", current_version:"true"}}) SET ResearchMethodItemUnit_ind.last_updated_on = localdatetime(), ResearchMethodItemUnit_ind.itemUnit_label = "$_input_name_$ [$_ontology_ID_$]", ResearchMethodItemUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, ResearchMethodItemUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN ResearchMethodItemUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET ResearchMethodItemUnit_ind.contributed_by = ResearchMethodItemUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, ResearchMethodItemUnit_ind
    MATCH (ResearchMethodItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchMethod_old:orkg_ResearchMethod_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, ResearchMethodItemUnit_ind, researchMethod_old
    CALL apoc.refactor.cloneNodesWithRelationships([researchMethod_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, ResearchMethodItemUnit_ind, researchMethod_old SET researchMethod_old.current_version = "false"
    WITH ResearchMethodItemUnit_ind
    MATCH (ResearchMethodItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(researchMethod_new:orkg_ResearchMethod_IND {{current_version:"true"}})
    SET researchMethod_new.name = "$_input_name_$", researchMethod_new.instance_label = "$_input_name_$", researchMethod_new.ontology_ID = "$_ontology_ID_$", researchMethod_new.type = "$_input_type_$", researchMethod_new.description = "$_input_description_$", researchMethod_new.URI = "new_individual_uri1", researchMethod_new.created_on = localdatetime(), researchMethod_new.last_updated_on = localdatetime(), researchMethod_new.created_by = "{creator}", researchMethod_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", from_activity_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH entry_node, parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchMethodItemUnit_ind:orkg_ResearchMethodItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method item unit", description:"This itemUnit models a research method documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchMethod_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchMethodItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(researchActivityMethodStatementUnit_Ind:orkg_ResearchActivityMethodRelationStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research activity method relation statement unit", description:"This statement unit models the relation between a particular research activity and one of the research methods it realizes.", URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri2", type:"Research_Activity_Method_Relation_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchActivityMethodRelationStatementUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research activity method"}})
    CREATE (researchActivityMethodStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchActivityMethodStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(ResearchMethodItemUnit_ind)
    CREATE (object_node)-[:REALIZES {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000055", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"to say that b realizes c at t is to assert that there is some material entity d & b is a process which has participant d at t & c is a disposition or role of which d is bearer_of at t& the type instantiated by b is correlated with the type instantiated by c. (axiom label in BFO2 Reference: [059-003])."}}]->(researchMethod:orkg_ResearchMethod_IND:iao_PlanSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["itemUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchMethodItemUnitIND_URI", user_input:"{itemUnit_uri}"}})
    CREATE (ResearchMethodItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(researchMethod)', from_objective_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH entry_node, parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchMethodItemUnit_ind:orkg_ResearchMethodItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method item unit", description:"This itemUnit models a research method documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchMethod_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchMethodItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(researchObjectiveMethodRelationStatementUnit_Ind:orkg_ResearchObjectiveMethodRelationStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research objective method relation statement unit", description:"This statementUnit models the relation between a particular research objective and a research method of which it is a part.", URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri2", type:"Research_Objective_Method_Relation_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchObjectiveMethodRelationStatementUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research objective method"}})
    CREATE (researchObjectiveMethodRelationStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchObjectiveMethodRelationStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(ResearchMethodItemUnit_ind)
    CREATE (researchMethod:orkg_ResearchMethod_IND:iao_PlanSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["itemUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchMethodItemUnitIND_URI", user_input:"{itemUnit_uri}"}})-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(object_node)
    CREATE (ResearchMethodItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(researchMethod)', from_method_cypher_code:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH entry_node MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH entry_node, parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH entry_node, parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(ResearchMethodItemUnit_ind:orkg_ResearchMethodItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method item unit", description:"This itemUnit models a research method documented in a particular research paper.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"ResearchMethod_itemUnit_class_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"ResearchMethodItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(researchMethod:orkg_ResearchMethod_IND:iao_PlanSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["itemUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchMethodItemUnitIND_URI", user_input:"{itemUnit_uri}"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(researchMethodParthoodStatementUnit_Ind:orkg_ResearchMethodParthoodStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research method parthood statement unit", description:"This statement unit models the relation between a particular research method and one of its method parts (i.e. steps).", URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri2", type:"Research_Method_Parthood_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchMethodParthoodStatementUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research method parthood"}})
    CREATE (researchMethodParthoodStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchMethodParthoodStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(ResearchMethodItemUnit_ind)
    CREATE (ResearchMethodItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(researchMethod)', operational_KGBB:"true", data_item_type:"itemUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(itemUnitkgbb)
    //MATERIAL ENTITY ITEM_UNIT KGBB
    CREATE (materialEntityItemUnitkgbb:MaterialEntityItemUnitKGBB:ItemUnitKGBB:KGBB:ClassExpression:Entity {{name:"material entity itemUnit Knowledge Graph Building Block", description:"A itemUnit Knowledge Graph Building Block that manages data about a particular material entity.", URI:"MaterialEntityItemUnitKGBB_URI", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://purl.obolibrary.org/obo/BFO_0000040"], granularity_tree_key:"material_entity_parthood_granularity_tree_URI", category:"ClassExpression", from_result_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH object_node, parent_data_item_node
    MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    MERGE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(material_entityItemUnit_ind:orkg_MaterialEntityItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"material entity item unit", description:"This itemUnit models all information relating to a particular material entity.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"material_entity_itemUnit_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"MaterialEntityItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    MERGE (material_entityItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(material_entity:bfo_MaterialEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["itemUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1MaterialEntityItemUnitIND_URI", user_input:"{itemUnit_uri}"}})
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(researchResultMaterialEntityRelationStatementUnit_Ind:orkg_ResearchResultMaterialEntityRelationStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"research result material entity relation statement unit", description:"This statementUnit models the relation between a particular research result and a material entity that it is about.", URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri2", type:"Research_Result_Material_Entity_Relation_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, KGBB_URI:"ResearchResultMaterialEntityRelationStatementUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Research result material entity"}})
    CREATE (researchResultMaterialEntityRelationStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(object_node)
    CREATE (researchResultMaterialEntityRelationStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(material_entityItemUnit_ind)
    MERGE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(material_entityItemUnit_ind)', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(material_entityItemUnit_ind:orkg_MaterialEntityItemUnit_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET material_entityItemUnit_ind.last_updated_on = localdatetime(), material_entityItemUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, material_entityItemUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN material_entityItemUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET material_entityItemUnit_ind.contributed_by = material_entityItemUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, material_entityItemUnit_ind
    MATCH (material_entityItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(material_entity_old:bfo_MaterialEntity_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, material_entityItemUnit_ind, material_entity_old
    CALL apoc.refactor.cloneNodesWithRelationships([material_entity_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, material_entityItemUnit_ind, material_entity_old SET material_entity_old.current_version = "false"
    WITH material_entityItemUnit_ind
    MATCH (material_entityItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(material_entity_new:bfo_MaterialEntity_IND {{current_version:"true"}})
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(material_entityItemUnit_ind:orkg_MaterialEntityItemUnit_IND {{URI:"{itemUnit_uri}", current_version:"true"}}) SET material_entityItemUnit_ind.last_updated_on = localdatetime(), material_entityItemUnit_ind.itemUnit_label = "$_input_name_$ [$_ontology_ID_$]", material_entityItemUnit_ind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, material_entityItemUnit_ind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN material_entityItemUnit_ind.contributed_by THEN [1] ELSE [] END |
    SET material_entityItemUnit_ind.contributed_by = material_entityItemUnit_ind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, material_entityItemUnit_ind
    MATCH (material_entityItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(material_entity_old:bfo_MaterialEntity_IND {{current_version:"true"}})
    WITH parent_data_item_node, object_node, material_entityItemUnit_ind, material_entity_old
    CALL apoc.refactor.cloneNodesWithRelationships([material_entity_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, material_entityItemUnit_ind, material_entity_old SET material_entity_old.current_version = "false"
    WITH material_entityItemUnit_ind
    MATCH (material_entityItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT]->(material_entity_new:bfo_MaterialEntity_IND {{current_version:"true"}})
    SET material_entity_new.name = "$_input_name_$", material_entity_new.instance_label = "$_input_name_$", material_entity_new.ontology_ID = "$_ontology_ID_$", material_entity_new.description = "$_input_description_$", material_entity_new.URI = "new_individual_uri1", material_entity_new.type = "$_input_type_$", material_entity_new.created_on = localdatetime(), material_entity_new.last_updated_on = localdatetime(), material_entity_new.created_by = "{creator}", material_entity_new.contributed_by = ["{creator}"]', from_material_entity_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}})
    WITH parent_data_item_node
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH object_node, parent_data_item_node
    MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    OPTIONAL MATCH (matEnt1 {{current_version:"true"}})-[:HAS_PART]->(object_node)
    OPTIONAL MATCH (root_itemUnit:orkg_MaterialEntityItemUnit_IND {{current_version:"true"}})-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(parent_data_item_node)
    OPTIONAL MATCH (GranTree:orkg_MaterialEntityParthoodGranularityTree_IND {{URI:object_node.material_entity_parthood_granularity_tree_URI, current_version:"true"}})
    WITH object_node, parent_data_item_node, entry_node, matEnt1, root_itemUnit, GranTree
    FOREACH (i IN CASE WHEN NOT "{creator}" IN GranTree.contributed_by THEN [1] ELSE [] END |
    SET GranTree.contributed_by = GranTree.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node, matEnt1, root_itemUnit, GranTree
    OPTIONAL MATCH (object_node)-[:HAS_PART]->(matEnt2 {{current_version:"true"}})
    WITH object_node, parent_data_item_node, entry_node, matEnt1, matEnt2, root_itemUnit, GranTree
    MERGE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(material_entityItemUnit_ind:orkg_MaterialEntityItemUnit_IND:orkg_ItemUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"material entity item unit", description:"This itemUnit models all information relating to a particular material entity.", URI:"{itemUnit_uri}", itemUnit_URI:"{itemUnit_uri}", type:"material_entity_itemUnit_URI", node_type:"itemUnit", category:"NamedIndividual", entry_URI:"{entryURI}", KGBB_URI:"MaterialEntityItemUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], itemUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    MERGE (material_entityItemUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}"}}]->(material_entity:bfo_MaterialEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["itemUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1MaterialEntityItemUnitIND_URI", user_input:"{itemUnit_uri}"}})
    MERGE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(materialEntityParthoodStatementUnit_Ind:orkg_MaterialEntityParthoodStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"material entity parthood statement unit", description:"This statementUnit models the relation between a particular material entity and its material entity parts.", URI:"new_individual_uri2", statementUnit_URI:"new_individual_uri2", type:"Material_Entity_Parthood_StatementUnit_URI", node_type:"statementUnit", category:"NamedIndividual", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, KGBB_URI:"MaterialEntityParthoodStatementUnitKGBB_URI", object_URI:"new_individual_uri1", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], statementUnit_label:"Material entity parthood"}})
    MERGE (materialEntityParthoodStatementUnit_Ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(object_node)
    MERGE (materialEntityParthoodStatementUnit_Ind)-[:OBJECT_DESCRIBED_BY_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"http://orkg?????5", entry_URI:"{entryURI}", itemUnit_URI:parent_data_item_node.URI, statementUnit_URI:"new_individual_uri2"}}]->(material_entityItemUnit_ind)
    MERGE (object_node)-[:HAS_PART {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", description:"a core relation that holds between a whole and its part."}}]->(material_entity)
    WITH object_node, parent_data_item_node, entry_node, matEnt1, material_entityItemUnit_ind, material_entity, root_itemUnit, GranTree, matEnt2,  object_node.material_entity_parthood_granularity_tree_URI IS NOT NULL AS Predicate
    FOREACH (i IN CASE WHEN Predicate THEN [1] ELSE [] END |
    SET material_entity.material_entity_parthood_granularity_tree_URI = object_node.material_entity_parthood_granularity_tree_URI
    SET GranTree.last_updated_on = localdatetime()
    )
    WITH object_node, parent_data_item_node, entry_node, matEnt1, material_entityItemUnit_ind, material_entity, root_itemUnit, GranTree, matEnt2,  object_node.material_entity_parthood_granularity_tree_URI IS NOT NULL AS Predicate
    FOREACH (i IN CASE WHEN matEnt1 IS NOT NULL AND NOT Predicate AND matEnt2 IS NULL THEN [1] ELSE [] END |
    MERGE (root_itemUnit)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", material_entity_parthood_granularity_tree_URI:"new_individual_uri2"}}]->(material_entity_parthood_granTree_ind:orkg_MaterialEntityParthoodGranularityTree_IND:orkg_ParthoodBasedGranularityTree_IND:orkg_GranularityTree_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"material entity parthood granularity tree", URI_property_key:"material_entity_parthood_granularity_tree_URI", description:"This granularity tree models all parthood-related information about a particular material entity.", URI:"new_individual_uri2", type:"MatEnt_Parthood_based_Granularity_tree_URI", node_type:"granularity_tree", category:"NamedIndividual", entry_URI:"{entryURI}", target_KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", object_URI:matEnt1.URI, created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], ontology_ID:"ORKG", instance_label:matEnt1.name + " parthood granularity tree", granularity_tree_label:matEnt1.name + " parthood granularity tree"}})
    MERGE (material_entity_parthood_granTree_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", material_entity_parthood_granularity_tree_URI:"new_individual_uri2"}}]->(matEnt1)
    SET material_entity.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    SET object_node.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    SET matEnt1.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    )
    WITH object_node, parent_data_item_node, entry_node, matEnt1, material_entityItemUnit_ind, material_entity, root_itemUnit, GranTree, matEnt2,  object_node.material_entity_parthood_granularity_tree_URI IS NOT NULL AS Predicate
    FOREACH (i IN CASE WHEN matEnt2 IS NOT NULL AND NOT Predicate AND matEnt1 IS NULL THEN [1] ELSE [] END |
    MERGE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", material_entity_parthood_granularity_tree_URI:"new_individual_uri2"}}]->(material_entity_parthood_granTree_ind:orkg_MaterialEntityParthoodGranularityTree_IND:orkg_ParthoodBasedGranularityTree_IND:orkg_GranularityTree_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"material entity parthood granularity tree", description:"This granularity tree models all parthood-related information about a particular material entity.", URI:"new_individual_uri2", type:"MatEnt_Parthood_based_Granularity_tree_URI", URI_property_key:"material_entity_parthood_granularity_tree_URI", node_type:"granularity_tree", category:"NamedIndividual", entry_URI:"{entryURI}", target_KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", object_URI:object_node.URI, created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], ontology_ID:"ORKG", instance_label:object_node.name + " parthood granularity tree"}})
    MERGE (material_entity_parthood_granTree_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", material_entity_parthood_granularity_tree_URI:"new_individual_uri2"}}]->(object_node)
    SET material_entity.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    SET object_node.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    SET matEnt2.material_entity_parthood_granularity_tree_URI="new_individual_uri2"
    )
    RETURN object_node, matEnt1, matEnt2, material_entityItemUnit_ind, material_entity', search_cypher_code:"cypherQuery", operational_KGBB:"true", data_item_type:"itemUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(itemUnitkgbb)
    //RESEARCH ACTIVITY OUTPUT RELATION STATEMENT_UNIT KGBB
    CREATE (researchActivityOutputStatementUnitkgbb:ResearchActivityOuputRelationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"research activity output relation statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research activities and their research result outputs.", relevant_properties_URI:["http://purl.obolibrary.org/obo/OBI_0000299"], relevant_classes_URI:["http://orkg???????1", "http://orkg???????5"], URI:"ResearchActivityOutputRelationStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //RESEARCH ACTIVITY METHOD RELATION STATEMENT_UNIT KGBB
    CREATE (researchActivityMethodStatementUnitkgbb:ResearchActivityMethodRelationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"research activity method relation statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research activities and the research methods they realize.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000055"], relevant_classes_URI:["http://orkg???????5", "http://orkg???????4"], URI:"ResearchActivityMethodRelationStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //RESEARCH ACTIVITY OBJECTIVE RELATION STATEMENT_UNIT KGBB
    CREATE (researchActivityObjectiveStatementUnitkgbb:ResearchActivityObjectiveRelationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"research activity objective relation statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research activities and the research objective they achieve.", relevant_properties_URI:["http://purl.obolibrary.org/obo/OBI_0000417"], relevant_classes_URI:["http://orkg???????5", "http://orkg???????3"], URI:"ResearchActivityObjectiveRelationStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //RESEARCH ACTIVITY PARTHOOD STATEMENT_UNIT KGBB
    CREATE (researchActivityParthoodStatementUnitkgbb:ResearchActivityParthoodRelationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"research activity parthood statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research activities and their activity parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000117"], relevant_classes_URI:["http://orkg???????5"], URI:"ResearchActivityParthoodStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //RESEARCH METHOD PARTHOOD STATEMENT_UNIT KGBB
    CREATE (researchMethodParthoodStatementUnitkgbb:ResearchMethodParthoodRelationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"research method parthood statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research methods and their method parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????4"], URI:"ResearchMethodParthoodStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //RESEARCH METHOD OBJECTIVE RELATION STATEMENT_UNIT KGBB
    CREATE (researchMethodObjectiveRelationStatementUnitkgbb:ResearchMethodObjectiveRelationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"research method objective relation statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research methods and their research objective parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????4", "http://orkg???????3"], URI:"ResearchMethodObjectiveRelationStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //RESEARCH METHOD ACTIVITY RELATION STATEMENT_UNIT KGBB
    CREATE (researchMethodActivityRelationStatementUnitkgbb:ResearchMethodActivityRelationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"research method activity relation statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research methods and the research activities that realize them.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000055"], relevant_classes_URI:["http://orkg???????4", "http://orkg???????5"], URI:"ResearchMethodActivityRelationStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //RESEARCH RESULT PARTHOOD STATEMENT_UNIT KGBB
    CREATE (researchResultParthoodStatementUnitkgbb:ResearchResultParthoodRelationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"research result parthood statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research results and their result parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????1"], URI:"ResearchResultParthoodStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //RESEARCH RESULT ACTIVITY RELATION STATEMENT_UNIT KGBB
    CREATE (researchResultActivityRelationStatementUnitkgbb:ResearchResultActivityRelationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"research result activity relation statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research results and the research activities that have them as their output.", relevant_properties_URI:["http://purl.obolibrary.org/obo/OBI_0000299"], relevant_classes_URI:["http://orkg???????1", "http://orkg???????5"], URI:"ResearchResultActivityRelationStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //RESEARCH RESULT OBJECTIVE RELATION STATEMENT_UNIT KGBB
    CREATE (researchResultObjectiveRelationStatementUnitkgbb:ResearchResultObjectiveRelationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"research result objective relation statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research results and the research objectives that achieved them.", relevant_properties_URI:["http://orkg_has_achieved_result"], relevant_classes_URI:["http://orkg???????1", "http://orkg???????3"], URI:"ResearchResultObjectiveRelationStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //RESEARCH OBJECTIVE PARTHOOD STATEMENT_UNIT KGBB
    CREATE (researchObjectiveParthoodStatementUnitkgbb:ResearchObjectiveParthoodRelationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"research objective parthood statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research objectives and their objective parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????3"], URI:"ResearchObjectiveParthoodStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //RESEARCH OBJECTIVE METHOD RELATION STATEMENT_UNIT KGBB
    CREATE (researchObjectiveMethodRelationStatementUnitkgbb:ResearchObjectiveMethodRelationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"research objective method relation statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research objectives and the research methods they are part of.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://orkg???????3", "http://orkg???????4"], URI:"ResearchObjectiveMethodRelationStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //RESEARCH OBJECTIVE ACTIVITY RELATION STATEMENT_UNIT KGBB
    CREATE (researchObjectiveActivityRelationStatementUnitkgbb:ResearchObjectiveActivityRelationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"research objective activity relation statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research objectives and the reseach activities that achieve them.", relevant_properties_URI:["http://purl.obolibrary.org/obo/OBI_0000417"], relevant_classes_URI:["http://orkg???????5", "http://orkg???????4"], URI:"ResearchObjectiveActivityRelationStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //RESEARCH OBJECTIVE RESULT RELATION STATEMENT_UNIT KGBB
    CREATE (researchObjectiveResultRelationStatementUnitkgbb:ResearchObjectiveResultRelationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"research objective result relation statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research objectives and the reseach results they achieved.", relevant_properties_URI:["http://orkg_has_achieved_result"], relevant_classes_URI:["http://orkg???????3", "http://orkg???????1"], URI:"ResearchObjectiveResultRelationStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //MATERIAL ENTITY PARTHOOD STATEMENT_UNIT KGBB
    CREATE (materialEntityParthoodStatementUnitkgbb:MaterialEntityParthoodRelationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"material entity parthood statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between material entities and their material entity parts.", relevant_properties_URI:["http://purl.obolibrary.org/obo/BFO_0000051"], relevant_classes_URI:["http://purl.obolibrary.org/obo/BFO_0000040"], URI:"MaterialEntityParthoodStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //RESEARCH RESULT MATERIAL ENTITY RELATION STATEMENT_UNIT KGBB
    CREATE (researchResultMaterialEntityRelationStatementUnitkgbb:ResearchResultMaterialEntityRelationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"research result material entity relation statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages relations between research results and the material entities they are about.", relevant_properties_URI:["http://purl.obolibrary.org/obo/IAO_0000136"], relevant_classes_URI:["http://orkg???????1", "http://purl.obolibrary.org/obo/BFO_0000040"], URI:"ResearchResultMaterialEntityRelationStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'cypherQuery', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //QUALITY STATEMENT_UNIT KGBB
    CREATE (qualitykgbb:QualityIdentificationStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"quality relation identification statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages quality identification statementUnit data.", relevant_properties_URI:["http://purl.obolibrary.org/obo/RO_0000086"], relevant_classes_URI:["http://purl.obolibrary.org/obo/PATO_0000128", "http://purl.obolibrary.org/obo/PATO_0000146", "http://purl.obolibrary.org/obo/PATO_0001756", "http://purl.obolibrary.org/obo/PATO_0000014"], URI:"QualityIdentificationStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"true", quality_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "statementUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(QualityStatementUnitind:orkg_QualityRelationIdentificationStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"Quality relation identification statement unit", URI:"{statementUnitURI}", description:"This statementUnit models information about the identification of a particular physical quality of a particular material entity.", type:"Quality_Identification_StatementUnit_URI", object_URI:"new_individual_uri1", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", KGBB_URI:"QualityIdentificationStatementUnitKGBB_URI", node_type:"statementUnit", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", statementUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (QualityStatementUnitind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(object_node)
    CREATE (object_node)-[:HAS_QUALITY {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/RO_0000086", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}", description:"a relation between an independent continuant (the bearer) and a quality, in which the quality specifically depends on the bearer for its existence."}}]->(quality:pato_PhysicalQuality_IND:pato_Quality_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["statementUnit_object", "input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1QualityStatementUnitIND_URI", user_input:"{statementUnitURI}"}})', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "itemUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(QualityStatementUnitind:orkg_QualityRelationIdentificationStatementUnit_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET QualityStatementUnitind.last_updated_on = localdatetime(), QualityStatementUnitind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, QualityStatementUnitind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN QualityStatementUnitind.contributed_by THEN [1] ELSE [] END |
    SET QualityStatementUnitind.contributed_by = QualityStatementUnitind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, QualityStatementUnitind
    MATCH (object_node)-[:HAS_QUALITY]->(quality_old:pato_PhysicalQuality_IND {{current_version:"true", statementUnit_URI:QualityStatementUnitind.URI}})
    WITH parent_data_item_node, object_node, QualityStatementUnitind, quality_old
    CALL apoc.refactor.cloneNodesWithRelationships([quality_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, QualityStatementUnitind, quality_old SET quality_old.current_version = "false"
    WITH object_node, parent_data_item_node, QualityStatementUnitind
    MATCH (object_node)-[:HAS_QUALITY]->(quality_new:pato_PhysicalQuality_IND {{current_version:"true", statementUnit_URI:QualityStatementUnitind.URI}})
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "statementUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(QualityStatementUnitind:orkg_QualityRelationIdentificationStatementUnit_IND {{URI:"{statementUnitURI}", current_version:"true"}}) SET QualityStatementUnitind.last_updated_on = localdatetime(), QualityStatementUnitind.statementUnit_label = "$_input_name_$ [$_ontology_ID_$]", QualityStatementUnitind.object_URI = "new_individual_uri1"
    WITH parent_data_item_node, object_node, QualityStatementUnitind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN QualityStatementUnitind.contributed_by THEN [1] ELSE [] END |
    SET QualityStatementUnitind.contributed_by = QualityStatementUnitind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, QualityStatementUnitind
    MATCH (object_node)-[:HAS_QUALITY]->(quality_old:pato_PhysicalQuality_IND {{current_version:"true", statementUnit_URI:"{statementUnitURI}"}})
    WITH parent_data_item_node, object_node, QualityStatementUnitind, quality_old
    CALL apoc.refactor.cloneNodesWithRelationships([quality_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, QualityStatementUnitind, quality_old SET quality_old.current_version = "false"
    WITH object_node, parent_data_item_node
    MATCH (object_node)-[:HAS_QUALITY]->(quality_new:pato_PhysicalQuality_IND {{current_version:"true", statementUnit_URI:"{statementUnitURI}"}})
    SET quality_new.name = "$_input_name_$", quality_new.instance_label = "$_input_name_$", quality_new.ontology_ID = "$_ontology_ID_$", quality_new.description = "$_input_description_$", quality_new.URI = "new_individual_uri1", quality_new.type = "$_input_type_$", quality_new.created_on = localdatetime(), quality_new.last_updated_on = localdatetime(), quality_new.created_by = "{creator}", quality_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    CREATE (measurementkgbb:MeasurementStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"measurement statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages measurement statementUnit data.", URI:"MeasurementStatementUnitKGBB_URI", category:"ClassExpression", operational_KGBB:"false", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    //WEIGHT MEASUREMENT STATEMENT_UNIT KGBB
    CREATE (weightkgbb:WeightMeasurementStatementUnitKGBB:MeasurementStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"weight measurement statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages weight measurement statementUnit data.", URI:"WeightMeasurementStatementUnitKGBB_URI", relevant_classes_URI:["http://purl.obolibrary.org/obo/PATO_0000128"], relevant_properties_URI:["http://purl.obolibrary.org/obo/IAO_0000004", "http://purl.obolibrary.org/obo/IAO_0000039", "http://purl.obolibrary.org/obo/OBI_0001938", "http://purl.obolibrary.org/obo/IAO_0000417"], category:"ClassExpression", operational_KGBB:"true", weight_measurement_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "statementUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(WeightMeasurementStatementUnitind:orkg_WeightMeasurementStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"Weight measurement statement unit", URI:"{statementUnitURI}", description:"This statementUnit models information about a particular weight measurement of a particular material entity.", type:"weight_measurement_statementUnit_URI", object_URI:"new_individual_uri1", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", KGBB_URI:"WeightMeasurementStatementUnitKGBB_URI", node_type:"statementUnit", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", statementUnit_label:"$_input_value_$ $_input_name_$ [$_ontology_ID_$]"}})
    CREATE (WeightMeasurementStatementUnitind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(object_node)
    CREATE (object_node)-[:IS_QUALITY_MEASURED_AS {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000417", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}", description:"inverse of the relation of is quality measurement of, which is: m is a quality measurement of q at t. When q is a quality, there is a measurement process p that has specified output m, a measurement datum, that is about q."}}]->(scalarmeasdatum:iao_ScalarMeasurementDatum_IND:iao_MeasurementDatum_IND:iao_data_item_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"http://purl.obolibrary.org/obo/IAO_0000032", name:"iao scalar measurement datum", description:"A scalar measurement datum is a measurement datum that is composed of two parts, numerals and a unit label.", current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (scalarmeasdatum)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(scalarvaluespec:obi_ScalarValueSpecification_IND:obi_ValueSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri2", type:"http://purl.obolibrary.org/obo/OBI_0001931", name:"obi scalar value specification", description:"A value specification that consists of two parts: a numeral and a unit label.", current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (scalarvaluespec)-[:SPECIFIES_VALUE_OF {{category:"ObjectPropertyExpression", description:"A relation between a value specification and an entity which the specification is about.", URI:"http://purl.obolibrary.org/obo/OBI_0001927", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(object_node)
    CREATE (scalarvaluespec)-[:HAS_MEASUREMENT_UNIT_LABEL {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000039", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(weightUnit:uo_GramBasedUnit_IND:NamedIndividual:Entity {{URI:"new_individual_uri3", type:"$_input_type_$", name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", data_node_type:["input2"], entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input2", input_version_ID:0, inputVariable:2, input_info_URI:"InputInfo2WeightMeasurementStatementUnitIND_URI", user_input:"{statementUnitURI}"}})
    CREATE (scalarvaluespec)-[:HAS_MEASUREMENT_VALUE {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000004", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(weightValue:Value_IND:Literal_IND:NamedIndividual:Entity {{URI:"new_individual_uri4", type:"orkg_value_URI", name:"$_input_value_$", description:"The value of a weight measurement", data_node_type:["input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1WeightMeasurementStatementUnitIND_URI", user_input:"{statementUnitURI}", value:"$_input_value_$", data_type:"xsd:float"}})', edit_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "statementUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (WeightMeasurementStatementUnitind:orkg_WeightMeasurementStatementUnit_IND {{URI:"{statementUnitURI}", current_version:"true"}}) SET WeightMeasurementStatementUnitind.last_updated_on = localdatetime(), WeightMeasurementStatementUnitind.statementUnit_label = "$_input_name_$ [$_ontology_ID_$]"
    WITH parent_data_item_node, object_node, WeightMeasurementStatementUnitind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN WeightMeasurementStatementUnitind.contributed_by THEN [1] ELSE [] END |
    SET WeightMeasurementStatementUnitind.contributed_by = WeightMeasurementStatementUnitind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, WeightMeasurementStatementUnitind
    MATCH (scalarValueSpecification:obi_ScalarValueSpecification_IND {{current_version:"true", statementUnit_URI:WeightMeasurementStatementUnitind.URI}})-[:HAS_MEASUREMENT_UNIT_LABEL {{statementUnit_URI:WeightMeasurementStatementUnitind.URI}}]->(weightUnit_old:uo_GramBasedUnit_IND {{current_version:"true", statementUnit_URI:WeightMeasurementStatementUnitind.URI}})
    WITH scalarValueSpecification, parent_data_item_node, object_node, WeightMeasurementStatementUnitind, weightUnit_old
    CALL apoc.refactor.cloneNodesWithRelationships([weightUnit_old])
    YIELD input, output
    WITH scalarValueSpecification, parent_data_item_node, object_node, WeightMeasurementStatementUnitind, weightUnit_old SET weightUnit_old.current_version = "false"
    WITH scalarValueSpecification, parent_data_item_node, object_node, WeightMeasurementStatementUnitind
    MATCH (scalarValueSpecification)-[:HAS_MEASUREMENT_UNIT_LABEL {{statementUnit_URI:WeightMeasurementStatementUnitind.URI}}]->(weightUnit_new:uo_GramBasedUnit_IND {{current_version:"true", statementUnit_URI:WeightMeasurementStatementUnitind.URI}})
    SET weightUnit_new.name = "$_input_name_$", weightUnit_new.instance_label = "$_input_name_$", weightUnit_new.ontology_ID = "$_ontology_ID_$", weightUnit_new.description = "$_input_description_$", weightUnit_new.URI = "new_individual_uri1", weightUnit_new.type = "$_input_type_$", weightUnit_new.created_on = localdatetime(), weightUnit_new.last_updated_on = localdatetime(), weightUnit_new.created_by = "{creator}", weightUnit_new.contributed_by = ["{creator}"]
    WITH scalarValueSpecification, parent_data_item_node, object_node, WeightMeasurementStatementUnitind
    MATCH (scalarValueSpecification)-[:HAS_MEASUREMENT_VALUE {{statementUnit_URI:WeightMeasurementStatementUnitind.URI}}]->(weightValue_old:Value_IND {{current_version:"true",statementUnit_URI:WeightMeasurementStatementUnitind.URI}})
    WITH scalarValueSpecification, parent_data_item_node, object_node, WeightMeasurementStatementUnitind, weightValue_old
    CALL apoc.refactor.cloneNodesWithRelationships([weightValue_old])
    YIELD input, output
    WITH scalarValueSpecification, parent_data_item_node, object_node, WeightMeasurementStatementUnitind, weightValue_old SET weightValue_old.current_version = "false"
    WITH scalarValueSpecification, WeightMeasurementStatementUnitind
    MATCH (scalarValueSpecification)-[:HAS_MEASUREMENT_VALUE {{statementUnit_URI:WeightMeasurementStatementUnitind.URI}}]->(weightValue_new:Value_IND {{current_version:"true", statementUnit_URI:WeightMeasurementStatementUnitind.URI}})
    SET weightValue_new.name = "$_input_value_$", weightValue_new.value = "$_input_value_$", weightValue_new.URI = "new_individual_uri2", weightValue_new.created_on = localdatetime(), weightValue_new.last_updated_on = localdatetime(), weightValue_new.created_by = "{creator}", weightValue_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(measurementkgbb)
    //R0 MEASUREMENT STATEMENT_UNIT KGBB
    CREATE (R0Measurementkgbb:BasicReproductionNumberMeasurementStatementUnitKGBB:MeasurementStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"basic reproduction number measurement statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages basic reprodcution number measurement statementUnit data.", URI:"R0MeasurementStatementUnitKGBB_URI", relevant_classes_URI:["http://purl.obolibrary.org/obo/OMIT_0024604", "http://purl.obolibrary.org/obo/STATO_0000196", "http://purl.obolibrary.org/obo/STATO_0000315", "http://purl.obolibrary.org/obo/STATO_0000314", "http://purl.obolibrary.org/obo/STATO_0000561"], relevant_properties_URI:["http://purl.obolibrary.org/obo/IAO_0000004", "http://purl.obolibrary.org/obo/IAO_0000039", "http://purl.obolibrary.org/obo/OBI_0001938", "http://purl.obolibrary.org/obo/IAO_0000417"], category:"ClassExpression", operational_KGBB:"true", r0_measurement_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "statementUnit_object"
    WITH object_node, parent_data_item_node MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
    WITH object_node, parent_data_item_node, entry_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN entry_node.contributed_by THEN [1] ELSE [] END |
    SET entry_node.contributed_by = entry_node.contributed_by + "{creator}"
    )
    WITH object_node, parent_data_item_node, entry_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(r0MeasurementStatementUnitind:orkg_BasicReproductionNumberMeasurementStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"R0 measurement statement unit", URI:"{statementUnitURI}", description:"This statementUnit models information about a particular basic reproduction number measurement of a particular population.", type:"r0_measurement_statementUnit_URI", object_URI:"new_individual_uri1", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", KGBB_URI:"R0MeasurementStatementUnitKGBB_URI", node_type:"statementUnit", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", statementUnit_label:"R0: $_input_value_$ ($_input_value1_$ - $_input_value2_$)"}})
    CREATE (r0MeasurementStatementUnitind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(object_node)
    CREATE (object_node)-[:IS_QUALITY_MEASURED_AS {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/IAO_0000417", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}", description:"inverse of the relation of is quality measurement of, which is: m is a quality measurement of q at t. When q is a quality, there is a measurement process p that has specified output m, a measurement datum, that is about q."}}]->(scalarmeasdatum:iao_ScalarMeasurementDatum_IND:iao_MeasurementDatum_IND:iao_data_item_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri1", type:"http://purl.obolibrary.org/obo/IAO_0000032", name:"iao scalar measurement datum", description:"A scalar measurement datum is a measurement datum that is composed of two parts, numerals and a unit label.", current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (scalarmeasdatum)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(scalarvaluespec:obi_ScalarValueSpecification_IND:obi_ValueSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri2", type:"http://purl.obolibrary.org/obo/OBI_0001931", name:"obi scalar value specification", description:"A value specification that consists of two parts: a numeral and a unit label.", current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (scalarvaluespec)-[:SPECIFIES_VALUE_OF {{category:"ObjectPropertyExpression", description:"A relation between a value specification and an entity which the specification is about.", URI:"http://purl.obolibrary.org/obo/OBI_0001927", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(object_node)
    CREATE (scalarvaluespec)-[:HAS_MEASUREMENT_UNIT_LABEL {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000039", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(r0countUnit:uo_CountUnit_IND:uo_DimensionlessUnit_IND:uo_Unit_IND:NamedIndividual:Entity {{URI:"new_individual_uri3", type:"http://purl.obolibrary.org/obo/UO_0000189", name:"count unit", ontology_ID:"UO", description:"A dimensionless unit which denotes a simple count of things. [MGED:MGED]", current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (scalarvaluespec)-[:HAS_MEASUREMENT_VALUE {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000004", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(r0Value:Value_IND:Literal_IND:NamedIndividual:Entity {{URI:"new_individual_uri4", type:"orkg_value_URI", name:"$_input_value_$", description:"The value of a basic reproduction number measurement", data_node_type:["input1"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1R0MeasurementStatementUnitIND_URI", user_input:"{statementUnitURI}", value:"$_input_value_$", data_type:"xsd:float"}})
    CREATE (scalarmeasdatum)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(confInterval:stato_ConfidenceInterval_IND:NamedIndividual:Entity {{URI:"new_individual_uri5", type:"http://purl.obolibrary.org/obo/STATO_0000196", name:"stato confidence interval", description:"A confidence interval is a data item which defines an range of values in which a measurement or trial falls corresponding to a given probability.", current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (confInterval)-[:HAS_PART {{category:"ObjectPropertyExpression", description:"a core relation that holds between a whole and its part.", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(upperconflimit:stato_UpperConfidenceLimit_IND:NamedIndividual:Entity {{URI:"new_individual_uri6", type:"http://purl.obolibrary.org/obo/STATO_0000314", name:"stato upper confidence limit", description:"Upper confidence limit is a data item which is a largest value bounding a confidence interval.", current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (upperconflimit)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(upperscalarvaluespec:obi_ScalarValueSpecification_IND:obi_ValueSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri8", type:"http://purl.obolibrary.org/obo/OBI_0001931", name:"obi scalar value specification", description:"A value specification that consists of two parts: a numeral and a unit label.", current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (confInterval)-[:HAS_PART {{category:"ObjectPropertyExpression", description:"a core relation that holds between a whole and its part.", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(lowerconflimit:stato_LowerConfidenceLimit_IND:NamedIndividual:Entity {{URI:"new_individual_uri7", type:"http://purl.obolibrary.org/obo/STATO_0000315", name:"stato lower confidence limit", description:"Lower confidence limit is a data item which is a lowest value bounding a confidence interval.", current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (lowerconflimit)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(lowerscalarvaluespec:obi_ScalarValueSpecification_IND:obi_ValueSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri9", type:"http://purl.obolibrary.org/obo/OBI_0001931", name:"obi scalar value specification", description:"A value specification that consists of two parts: a numeral and a unit label.", current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (lowerscalarvaluespec)-[:HAS_MEASUREMENT_UNIT_LABEL {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000039", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(lowerCountUnit:uo_CountUnit_IND:uo_DimensionlessUnit_IND:uo_Unit_IND:NamedIndividual:Entity {{URI:"new_individual_uri12", type:"http://purl.obolibrary.org/obo/UO_0000189", name:"count unit", ontology_ID:"UO", description:"A dimensionless unit which denotes a simple count of things. [MGED:MGED]", current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (upperscalarvaluespec)-[:HAS_MEASUREMENT_UNIT_LABEL {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000039", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(upperCountUnit:uo_CountUnit_IND:uo_DimensionlessUnit_IND:uo_Unit_IND:NamedIndividual:Entity {{URI:"new_individual_uri11", type:"http://purl.obolibrary.org/obo/UO_0000189", name:"count unit", ontology_ID:"UO", description:"A dimensionless unit which denotes a simple count of things. [MGED:MGED]", current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (upperscalarvaluespec)-[:HAS_MEASUREMENT_VALUE {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000004", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(upperValue:Value_IND:Literal_IND:NamedIndividual:Entity {{URI:"new_individual_uri13", type:"orkg_value_URI", name:"$_input_value2_$", description:"The value of the upper confidence limit of a basic reproduction number measurement", data_node_type:["input2"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input2", input_version_ID:0, inputVariable:2, input_info_URI:"InputInfo2UpperConfLimitR0MeasurementStatementUnitIND_URI", user_input:"{statementUnitURI}", value:"$_input_value2_$", data_type:"xsd:float"}})
    CREATE (lowerscalarvaluespec)-[:HAS_MEASUREMENT_VALUE {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000004", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(lowerValue:Value_IND:Literal_IND:NamedIndividual:Entity {{URI:"new_individual_uri14", type:"orkg_value_URI", name:"$_input_value1_$", description:"The value of the lower confidence limit of a basic reproduction number measurement", data_node_type:["input3"], current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input3", input_version_ID:0, inputVariable:3, input_info_URI:"InputInfo3LowerConfLimitR0MeasurementStatementUnitIND_URI", user_input:"{statementUnitURI}", value:"$_input_value1_$", data_type:"xsd:float"}})
    CREATE (confInterval)-[:HAS_PART {{category:"ObjectPropertyExpression", description:"a core relation that holds between a whole and its part.", URI:"http://purl.obolibrary.org/obo/BFO_0000051", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(conflevel:stato_ConfidenceLevel_IND:NamedIndividual:Entity {{URI:"new_individual_uri15", type:"http://purl.obolibrary.org/obo/STATO_0000561", name:"stato confidence level", description:"The frequency (i.e., the proportion) of possible confidence intervals that contain the true value of their corresponding parameter. In other words, if confidence intervals are constructed using a given confidence level in an infinite number of independent experiments, the proportion of those intervals that contain the true value of the parameter will match the confidence level. A probability measure of the reliability of an inferential statistical test that has been applied to sample data and which is provided along with the confidence interval for the output statistic.", current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (conflevel)-[:HAS_VALUE_SPECIFICATION {{category:"ObjectPropertyExpression", description:"A relation between an information content entity and a value specification that specifies its value.", URI:"http://purl.obolibrary.org/obo/OBI_0001938", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(conflevelscalarvaluespec:obi_ScalarValueSpecification_IND:obi_ValueSpecification_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{URI:"new_individual_uri16", type:"http://purl.obolibrary.org/obo/OBI_0001931", name:"obi scalar value specification", description:"A value specification that consists of two parts: a numeral and a unit label.", current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}",versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
    CREATE (conflevelscalarvaluespec)-[:HAS_MEASUREMENT_VALUE {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000004", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(conflevelValue:Value_IND:Literal_IND:NamedIndividual:Entity {{URI:"new_individual_uri17", type:"orkg_value_URI", name:"95", description:"The value of the confidence level of a basic reproduction number measurement", current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", value:"95"}})
    CREATE (conflevelscalarvaluespec)-[:HAS_MEASUREMENT_UNIT_LABEL {{category:"ObjectPropertyExpression", description:"No definition provided by IAO.", URI:"http://purl.obolibrary.org/obo/IAO_0000039", entry_URI:"{entryURI}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnitURI}"}}]->(percent:uo_Percent_IND:uo_Ratio_IND:uo_DimensionlessUnit_IND:uo_Unit_IND:NamedIndividual:Entity {{URI:"new_individual_uri18", type:"http://purl.obolibrary.org/obo/UO_0000187", name:"percent", ontology_ID:"UO", description:"A dimensionless ratio unit which denotes numbers as fractions of 100.", current_version:"true", entry_URI:"{entryURI}", itemUnit_URI:["{itemUnit_uri}"], statementUnit_URI:"{statementUnitURI}", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})', edit_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "statementUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (r0MeasurementStatementUnitind:orkg_BasicReproductionNumberMeasurementStatementUnit_IND {{URI:"{statementUnitURI}", current_version:"true"}}) SET r0MeasurementStatementUnitind.last_updated_on = localdatetime(), r0MeasurementStatementUnitind.statementUnit_label = "R0: $_input_value_$ ($_input_value1_$ - $_input_value2_$)"
    WITH parent_data_item_node, object_node, r0MeasurementStatementUnitind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN r0MeasurementStatementUnitind.contributed_by THEN [1] ELSE [] END |
    SET r0MeasurementStatementUnitind.contributed_by = r0MeasurementStatementUnitind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, r0MeasurementStatementUnitind
    MATCH (r0Value_old:Value_IND {{current_version:"true", statementUnit_URI:r0MeasurementStatementUnitind.URI, input_source:"input1"}})
    WITH parent_data_item_node, object_node, r0MeasurementStatementUnitind, r0Value_old
    CALL apoc.refactor.cloneNodesWithRelationships([r0Value_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, r0MeasurementStatementUnitind, r0Value_old SET r0Value_old.current_version = "false"
    WITH parent_data_item_node, object_node, r0MeasurementStatementUnitind
    MATCH (r0Value_new:Value_IND {{current_version:"true", statementUnit_URI:r0MeasurementStatementUnitind.URI, input_source:"input1"}})
    SET r0Value_new.value = "$_input_value_$", r0Value_new.name = "$_input_value_$", r0Value_new.URI = "new_individual_uri1", r0Value_new.created_on = localdatetime(), r0Value_new.last_updated_on = localdatetime(), r0Value_new.created_by = "{creator}", r0Value_new.contributed_by = ["{creator}"]
    WITH parent_data_item_node, object_node, r0MeasurementStatementUnitind
    MATCH (upperValue_old:Value_IND {{current_version:"true", statementUnit_URI:r0MeasurementStatementUnitind.URI, input_source:"input2"}})
    WITH parent_data_item_node, object_node, upperValue_old, r0MeasurementStatementUnitind
    CALL apoc.refactor.cloneNodesWithRelationships([upperValue_old])
    YIELD input, output
    WITH r0MeasurementStatementUnitind, parent_data_item_node, object_node, upperValue_old SET upperValue_old.current_version = "false"
    WITH parent_data_item_node, object_node, r0MeasurementStatementUnitind
    MATCH (upperValue_new:Value_IND {{current_version:"true", statementUnit_URI:r0MeasurementStatementUnitind.URI, input_source:"input2"}})
    SET upperValue_new.value = "$_input_value2_$", upperValue_new.name = "$_input_value2_$", upperValue_new.URI = "new_individual_uri2", upperValue_new.created_on = localdatetime(), upperValue_new.last_updated_on = localdatetime(), upperValue_new.created_by = "{creator}", upperValue_new.contributed_by = ["{creator}"]
    WITH parent_data_item_node, object_node, r0MeasurementStatementUnitind
    MATCH (lowerValue_old:Value_IND {{current_version:"true", statementUnit_URI:r0MeasurementStatementUnitind.URI, input_source:"input3"}})
    WITH parent_data_item_node, object_node, lowerValue_old, r0MeasurementStatementUnitind
    CALL apoc.refactor.cloneNodesWithRelationships([lowerValue_old])
    YIELD input, output
    WITH parent_data_item_node, r0MeasurementStatementUnitind, object_node, lowerValue_old SET lowerValue_old.current_version = "false"
    WITH parent_data_item_node, r0MeasurementStatementUnitind, object_node
    MATCH (lowerValue_new:Value_IND {{current_version:"true", statementUnit_URI:r0MeasurementStatementUnitind.URI, input_source:"input3"}})
    SET lowerValue_new.value = "$_input_value1_$", lowerValue_new.name = "$_input_value1_$", lowerValue_new.URI = "new_individual_uri3", lowerValue_new.created_on = localdatetime(), lowerValue_new.last_updated_on = localdatetime(), lowerValue_new.created_by = "{creator}", lowerValue_new.contributed_by = ["{creator}"]', search_cypher_code:"cypherQuery", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(measurementkgbb)
    //RESEARCH TOPIC STATEMENT_UNIT KGBB
    CREATE (researchTopicStatementUnitKGBB:orkg_ResearchTopicStatementUnitKGBB:StatementUnitKGBB:KGBB:ClassExpression:Entity {{name:"research topic statementUnit Knowledge Graph Building Block", description:"A Knowledge Graph Building Block that manages statementUnits about the relation between orkg research papers and the research topics they cover.", URI:"ResearchTopicStatementUnitKGBB_URI", relevant_classes_URI:["http://orkg/researchtopic_1", "http://orkg???????2"], relevant_properties_URI:["http://edamontology.org/has_topic"], category:"ClassExpression", KGBB_URI:"ResearchTopicStatementUnitKGBB_URI", search_cypher_code:"some query", research_topic_cypher_code:'MATCH (parent_data_item_node {{URI:"parent_data_item_uri"}}) SET parent_data_item_node.last_updated_on = localdatetime()
    WITH parent_data_item_node
    FOREACH (i IN CASE WHEN NOT "{creator}" IN parent_data_item_node.contributed_by THEN [1] ELSE [] END |
    SET parent_data_item_node.contributed_by = parent_data_item_node.contributed_by + "{creator}"
    )
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "statementUnit_object"
    WITH parent_data_item_node, object_node
    CREATE (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entryURI}", statementUnit_URI:"{statementUnitURI}"}}]->(researchTopicStatementUnitind:orkg_ResearchTopicStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"Research topic statement unit", description:"This statementUnit models information about a particular research topic of a particular research paper.", URI:"{statementUnitURI}", type:"ResearchTopicStatementUnit_URI", object_URI:object_node.URI, entry_URI:"{entryURI}", KGBB_URI:"ResearchTopicStatementUnitKGBB_URI", node_type:"statementUnit", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", statementUnit_label:"$_input_name_$ [$_ontology_ID_$]"}})
    CREATE (object_node)-[:HAS_TOPIC {{category:"ObjectPropertyExpression", description:"Subject A can be any concept or entity outside of an ontology (or an ontology concept in a role of an entity being semantically annotated). Object B can either be a concept that is a Topic, or in unexpected cases an entity outside of an ontology that is a Topic or is in the role of a Topic. In EDAM, only has_topic is explicitly defined between EDAM concepts (Operation or Data has_topic Topic). The inverse, is_topic_of, is not explicitly defined. A has_topic B defines for the subject A, that it has the object B as its topic (A is in the scope of a topic B).", URI:"http://edamontology.org/has_topic", entry_URI:"{entryURI}", statementUnit_URI:"{statementUnitURI}"}}]->(researchTopicind:orkg_orkg_ResearchTopic_IND:edam_Topic_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"$_input_name_$", instance_label:"$_input_name_$", ontology_ID:"$_ontology_ID_$", description:"$_input_description_$", URI:"new_individual_uri1", entry_URI:"{entryURI}", statementUnit_URI:"{statementUnitURI}", data_node_type:"input1", type:"$_input_type_$", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", data_view_information:"true", input:"true", input_source:"input1", input_version_ID:0, inputVariable:1, input_info_URI:"InputInfo1ResearchTopicStatementUnitIND_URI", user_input:"{statementUnitURI}"}})
    CREATE (researchTopicStatementUnitind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entryURI}", statementUnit_URI:"{statementUnitURI}"}}]->(object_node)', label_cypher:'MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
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
    WITH parent_data_item_node MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "statementUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(researchTopicStatementUnitind:orkg_ResearchTopicStatementUnit_IND {{URI:"$_input_uri_$", current_version:"true"}}) SET researchTopicStatementUnitind.last_updated_on = localdatetime()
    WITH parent_data_item_node, object_node, researchTopicStatementUnitind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN researchTopicStatementUnitind.contributed_by THEN [1] ELSE [] END |
    SET researchTopicStatementUnitind.contributed_by = researchTopicStatementUnitind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, researchTopicStatementUnitind
    MATCH (object_node)-[:HAS_ITEM_UNIT]->(itemUnit_old:orkg_orkg_ResearchTopic_IND {{current_version:"true", statementUnit_URI:researchTopicStatementUnitind.URI}})
    WITH parent_data_item_node, object_node, researchTopicStatementUnitind, itemUnit_old
    CALL apoc.refactor.cloneNodesWithRelationships([itemUnit_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, researchTopicStatementUnitind, itemUnit_old SET itemUnit_old.current_version = "false"
    WITH researchTopicStatementUnitind
    MATCH (object_node)-[:HAS_ITEM_UNIT]->(itemUnit_new:orkg_orkg_ResearchTopic_IND {{current_version:"true", statementUnit_URI:researchTopicStatementUnitind.URI}})
    SET itemUnit_new.instance_label = "$_label_name_$", itemUnit_new.URI = "new_individual_uri1", itemUnit_new.created_on = localdatetime(), itemUnit_new.last_updated_on = localdatetime(), itemUnit_new.created_by = "{creator}", itemUnit_new.contributed_by = ["{creator}"]', edit_cypher:' MATCH (entry_node {{URI:"{entryURI}"}}) SET entry_node.last_updated_on = localdatetime()
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
    MATCH (object_node) WHERE object_node.URI=parent_data_item_node.object_URI SET object_node.data_node_type=object_node.data_node_type + "statementUnit_object"
    WITH parent_data_item_node, object_node
    MATCH (parent_data_item_node)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(researchTopicStatementUnitind:orkg_ResearchTopicStatementUnit_IND {{URI:"{statementUnitURI}", current_version:"true"}}) SET researchTopicStatementUnitind.last_updated_on = localdatetime(), researchTopicStatementUnitind.statementUnit_label = "$_input_name_$ [$_ontology_ID_$]"
    WITH parent_data_item_node, object_node, researchTopicStatementUnitind
    FOREACH (i IN CASE WHEN NOT "{creator}" IN researchTopicStatementUnitind.contributed_by THEN [1] ELSE [] END |
    SET researchTopicStatementUnitind.contributed_by = researchTopicStatementUnitind.contributed_by + "{creator}"
    )
    WITH parent_data_item_node, object_node, researchTopicStatementUnitind
    MATCH (object_node)-[:HAS_ITEM_UNIT]->(itemUnit_old:orkg_orkg_ResearchTopic_IND {{current_version:"true", statementUnit_URI:researchTopicStatementUnitind.URI}})
    WITH parent_data_item_node, object_node, researchTopicStatementUnitind, itemUnit_old
    CALL apoc.refactor.cloneNodesWithRelationships([itemUnit_old])
    YIELD input, output
    WITH parent_data_item_node, object_node, researchTopicStatementUnitind, itemUnit_old SET itemUnit_old.current_version = "false"
    WITH object_node, researchTopicStatementUnitind
    MATCH (object_node)-[:HAS_ITEM_UNIT]->(itemUnit_new:orkg_orkg_ResearchTopic_IND {{current_version:"true", statementUnit_URI:researchTopicStatementUnitind.URI}})
    SET itemUnit_new.instance_label = "$_input_name_$", itemUnit_new.name = "$_input_name_$", itemUnit_new.ontology_ID = "$_ontology_ID_$", itemUnit_new.type = "$_input_type_$", itemUnit_new.description = "$_input_description_$", itemUnit_new.URI = "new_individual_uri1", itemUnit_new.created_on = localdatetime(), itemUnit_new.last_updated_on = localdatetime(), itemUnit_new.created_by = "{creator}", itemUnit_new.contributed_by = ["{creator}"]', operational_KGBB:"true", data_item_type:"statementUnit"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(statementUnitKGBB)
    CREATE (researchTopicStatementUnitKGBB)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(researchTopicStatementUnit)
    //KGBB ELEMENTS
    CREATE (kgbbelement:KGBBElement:ClassExpression:Entity {{name:"Knowledge Graph Building Block element", description:"An element of a Knowledge Graph Building Block. Knowledge Graph Building Block elements are used to specify functionalities of a Knowledge Graph Building Block.", URI:"KGBBElement_URI", category:"ClassExpression"}})
    CREATE (granularityTreeElementKGBBelement:GranularityTreeElementKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Granularity tree element Knowledge Graph Building Block element", description:"A Knowledge Graph Building Block element that connects a itemUnit to a specific type of granularity tree.", URI:"GranularityTreeElementKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (statementUnitElementKGBBelement:StatementUnitElementKGBBElement:KGBBElement:ClassExpression:Entity {{name:"StatementUnit element Knowledge Graph Building Block element", description:"A Knowledge Graph Building Block element that connects a itemUnit to a specific type of statementUnit.", URI:"StatementUnitElementKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (itemUnitElementKGBBelement:ItemUnitElementKGBBElement:KGBBElement:ClassExpression:Entity {{name:"ItemUnit element Knowledge Graph Building Block element", description:"A Knowledge Graph Building Block element that connects an entry to a specific type of itemUnit.", URI:"ItemUnitElementKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (inputInfoKGBBelement:InputInfoKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Input information element", description:"A Knowledge Graph Building Block element that provides input information, i.e. information for the Knowledge Graph Building Block for how to process input from users or from the application.", URI:"InputInfoKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (itemUnitRepresentationKGBBelement:ItemUnitRepresentationKGBBElement:RepresentationKGBBElement:KGBBElement:ClassExpression:Entity {{name:"ItemUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data belonging to the itemUnit in the user interface in a human-readable form using the corresponding itemUnit Knowledge Graph Building Block.", URI:"ItemUnitRepresentationKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (entryRepresentationKGBBelement:EntryRepresentationKGBBElement:RepresentationKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Entry representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data belonging to the entry in the user interface in a human-readable form using the corresponding entry Knowledge Graph Building Block.", URI:"EntryRepresentationKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (containerKGBBelement:ContainerKGBBElement:RepresentationKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Container element", description:"A Knowledge Graph Building Block element that functions as a container to organize and structure information for the front end for representing the data of the itemUnit or statementUnit in the user interface in a human-readable form using the associated Knowledge Graph Building Block.", URI:"ContainerRepresentationKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (exportModelKGBBelement:ExportModelKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Export model element", description:"A Knowledge Graph Building Block element that provides an export model, i.e. information for the application for exporting the data associated with this Knowledge Graph Building Block following a specific standard or data model.", URI:"ExportModelKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (statementUnitRepresentationKGBBelement:StatementUnitRepresentationKGBBElement:RepresentationKGBBElement:KGBBElement:ClassExpression:Entity {{name:"StatementUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the associated statementUnit Knowledge Graph Building Block in the user interface in a human-readable form.", URI:"StatementUnitRepresentationKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    CREATE (granTreeRepresentationKGBBelement:GranularityTreeRepresentationKGBBElement:RepresentationKGBBElement:KGBBElement:ClassExpression:Entity {{name:"Granularity tree representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the associated granularity perspective Knowledge Graph Building Block in the user interface in a human-readable form.", URI:"GranularityTreeRepresentationKGBBElement_URI", category:"ClassExpression"}})-[:SUBCLASS_OF {{category:"ObjectPropertyExpression", URI:"http://www.w3.org/2000/01/rdf-schema#subClassOf"}}]->(kgbbelement)
    // SCHOLARLY PUBLICATION KGBB RELATIONS
    CREATE (scholarlyPublicationEntrykgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(scholarlyPublicationEntry)
    CREATE (scholarlyPublicationEntrykgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of research topic statementUnits in its entry.", KGBB_URI:"ScholarlyPublicationEntryKGBB_URI", target_KGBB_URI:"ResearchTopicStatementUnitKGBB_URI", required:"false", quantity:"m", query_key:"research_topic_cypher_code", statementUnit_object_URI:"object$_$URI", input_results_in:"added_statementUnit"}}]->(researchTopicStatementUnitKGBB)
    CREATE (scholarlyPublicationEntrykgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about the research activity of a particular research paper.", itemUnit_object_URI:"object$_$URI", KGBB_URI:"ScholarlyPublicationEntryKGBB_URI", target_KGBB_URI:"ResearchActivityItemUnitKGBB_URI", required:"true", input_results_in:"added_itemUnit", quantity:"m", query_key:"storage_model_cypher_code" }}]->(ResearchActivityItemUnitkgbb)
    CREATE (scholarlyPublicationEntrykgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(scholarlyPublicationEntryRepresentation1KGBBelement:ScholarlyPublicationEntryRepresentationKGBBElement_IND:EntryRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Scholarly publication entry representation 1 element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the scholarly publication entry in the user interface in a human-readable form using the scholarly publication entry Knowledge Graph Building Block.", data_view_name:"{data_view_name}", node_type:"entry representation", component:"scholarly_publication_entry", data_item_type_URI:"scholarly_publication_entry_URI",  link_$$$_1:"{{'name':'research_topic_statementUnit_input_info', 'ontology_ID':'EDAM', 'input_restricted_to_subclasses_of':'http://edamontology.org/topic_0003', 'target_KGBB_URI':'ResearchTopicStatementUnitKGBB_URI', 'placeholder_text':'specify the research topic', 'data_item_type':'statementUnit', 'edit_cypher_key':'edit_cypher', 'query_key':'research_topic_cypher_code', 'links_to_component':'research_topic_statementUnit', 'statementUnit_object_URI':'object$_$URI', 'input_results_in':'added_statementUnit', 'edit_results_in':'edited_statementUnit'}}",
    link_$$$_2:"{{'name':'research_overview_itemUnit', 'target_KGBB_URI':'ResearchActivityItemUnitKGBB_URI', 'data_item_type':'itemUnit', 'query_key':'storage_model_cypher_code', 'links_to_component':'research_activity_itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_results_in':'added_itemUnit'}}", URI:"ScholarlyPublicationEntryRepresentation1KGBBElementIND_URI", type:"EntryRepresentationKGBBElement_URI", KGBB_URI:"ScholarlyPublicationEntryKGBB_URI", category:"NamedIndividual", data_view_information:"true", html:"entry.html"}})
    // RESEARCH ACTIVITY ITEM_UNIT KGBB RELATIONS
    CREATE (ResearchActivityItemUnitkgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(ResActItemUnit)
    CREATE (ResearchActivityItemUnitkgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(researchActivityItemUnitRepresentation1KGBBelement:ResearchActivityItemUnitRepresentationKGBBElement_IND:ItemUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research activity itemUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing research activity data associated with a research paper entry in the user interface in a human-readable form using the research activity itemUnit Knowledge Graph Building Block.", data_view_name:"{data_view_name}", node_type:"itemUnit representation", URI:"ResearchActivityItemUnitRepresentation1KGBBElementIND_URI", data_item_type_URI:"ResearchActivity_itemUnit_class_URI",  type:"ItemUnitRepresentationKGBBElement_URI", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", category:"NamedIndividual", data_view_information:"true", itemUnit_html:"research_overview.html", component:"research_activity_itemUnit", link_$$$_1:"{{'name':'research_step_itemUnit_input_info', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/OBI_0000011', 'ontology_ID':'OBI', 'target_KGBB_URI':'ResearchActivityItemUnitKGBB_URI', 'instantiated_by_statementUnitKGBB':'ResearchActivityParthoodStatementUnitKGBB_URI', 'data_item_type':'itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_results_in':'added_itemUnit', 'edit_results_in':'edited_itemUnit', 'links_to_component':'research_activity_itemUnit', 'query_key':'from_activity_cypher_code', 'edit_cypher_key':'edit_cypher', 'placeholder_text':'specify the type of research activity', 'input_info_URI':'InputInfo1ResearchActivityItemUnitIND_URI', 'input_source':'input1', 'editable':'true'}}",
    link_$$$_2:"{{'name':'research_result_itemUnit_input_info', 'placeholder_text':'specify the type of research result', 'ontology_ID':'IAO', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000030', 'target_KGBB_URI':'ResearchResultItemUnitKGBB_URI', 'instantiated_by_statementUnitKGBB':'ResearchActivityOutputRelationStatementUnitKGBB_URI', 'data_item_type':'itemUnit', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_itemUnit', 'query_key':'from_activity_cypher_code', 'links_to_component':'research_result_itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_results_in':'added_itemUnit'}}", link_$$$_3:"{{'name':'research_method_itemUnit_input_info', 'placeholder_text':'specify the type of research method', 'ontology_ID':'MMO,NCIT', 'input_restricted_to_subclasses_of':'', 'target_KGBB_URI':'ResearchMethodItemUnitKGBB_URI', 'instantiated_by_statementUnitKGBB':'ResearchActivityMethodRelationStatementUnitKGBB_URI', 'data_item_type':'itemUnit', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_itemUnit', 'query_key':'from_activity_cypher_code', 'links_to_component':'research_method_itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_results_in':'added_itemUnit'}}", link_$$$_4:"{{'name':'research_objective_itemUnit_input_info', 'placeholder_text':'specify the type of research objective', 'ontology_ID':'AGRO,IAO,ERO,OBI', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000005', 'target_KGBB_URI':'ResearchObjectiveItemUnitKGBB_URI', 'instantiated_by_statementUnitKGBB':'ResearchActivityObjectiveRelationStatementUnitKGBB_URI', 'data_item_type':'itemUnit', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_itemUnit', 'query_key':'from_activity_cypher_code', 'links_to_component':'research_objective_itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_results_in':'added_itemUnit'}}"}})
    CREATE (ResearchActivityItemUnitkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(researchActivityInputInfo1KGBBelement:ResearchActivityInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of research activity itemUnit", description:"User input information 1 for the specification of the research activity resource for a research activity itemUnit.", URI:"InputInfo1ResearchActivityItemUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", input_name:"research_activity_input", node_type:"input1", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1ResearchActivityItemUnitIND_URI", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/OBI_0000011", ontology_ID:"OBI", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})
    CREATE (ResearchActivityItemUnitkgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about a research activity step of a research activity.", itemUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", target_KGBB_URI:"ResearchActivityItemUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_activity_cypher_code", instantiated_by_statementUnitKGBB:"ResearchActivityParthoodStatementUnitKGBB_URI"}}]->(ResearchActivityItemUnitkgbb)
    CREATE (ResearchActivityItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of research activity parthood statementUnits in its entry.", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", target_KGBB_URI:"ResearchActivityParthoodStatementUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_activity_cypher_code", statementUnit_object_URI:"object$_$URI", input_results_in:"added_statementUnit", instantiates_itemUnitKGBB:"ResearchActivityItemUnitKGBB_URI"}}]->(researchActivityParthoodStatementUnitkgbb)
    CREATE (ResearchActivityItemUnitkgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about a research result of a research activity.", itemUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", target_KGBB_URI:"ResearchResultItemUnitKGBB_URI", required:"true", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_activity_cypher_code", instantiated_by_statementUnitKGBB:"ResearchActivityOutputRelationStatementUnitKGBB_URI"}}]->(ResearchResultItemUnitkgbb)
    CREATE (ResearchActivityItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of research activity output relation statementUnits in its entry.", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", target_KGBB_URI:"ResearchActivityOutputRelationStatementUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_activity_cypher_code", statementUnit_object_URI:"object$_$URI", input_results_in:"added_statementUnit", instantiates_itemUnitKGBB:"ResearchResultItemUnitKGBB_URI"}}]->(researchActivityOutputStatementUnitkgbb)
    CREATE (ResearchActivityItemUnitkgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about a research method realized in a research activity.", itemUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", target_KGBB_URI:"ResearchMethodItemUnitKGBB_URI", required:"true", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_activity_cypher_code", instantiated_by_statementUnitKGBB:"ResearchActivityMethodRelationStatementUnitKGBB_URI"}}]->(ResearchMethodItemUnitkgbb)
    CREATE (ResearchActivityItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of research activity method relation statementUnits in its entry.", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", target_KGBB_URI:"ResearchActivityMethodRelationStatementUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_activity_cypher_code", statementUnit_object_URI:"object$_$URI", input_results_in:"added_statementUnit", instantiates_itemUnitKGBB:"ResearchMethodItemUnitKGBB_URI"}}]->(researchActivityMethodStatementUnitkgbb)
    CREATE (ResearchActivityItemUnitkgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about a research objective achieved by a research activity.", itemUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", target_KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", required:"true", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_activity_cypher_code", instantiated_by_statementUnitKGBB:"ResearchActivityObjectiveRelationStatementUnitKGBB_URI"}}]->(ResearchObjectiveItemUnitkgbb)
    CREATE (ResearchActivityItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of research activity objective relation statementUnits in its entry.", KGBB_URI:"ResearchActivityItemUnitKGBB_URI", target_KGBB_URI:"ResearchActivityObjectiveRelationStatementUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_activity_cypher_code", statementUnit_object_URI:"object$_$URI", input_results_in:"added_statementUnit", instantiates_itemUnitKGBB:"ResearchObjectiveItemUnitKGBB_URI"}}]->(researchActivityObjectiveStatementUnitkgbb)
    // RESEARCH METHOD ITEM_UNIT KGBB RELATIONS
    CREATE (ResearchMethodItemUnitkgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(ResMethItemUnit)
    CREATE (ResearchMethodItemUnitkgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(researchMethodItemUnitRepresentation1KGBBelement:ResearchMethodItemUnitRepresentationKGBBElement_IND:ItemUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research method itemUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing research method data associated with a research paper entry in the user interface in a human-readable form using the research method itemUnit Knowledge Graph Building Block.", data_view_name:"{data_view_name}", node_type:"itemUnit representation", URI:"ResearchMethodItemUnitRepresentation1KGBBElementIND_URI", data_item_type_URI:"ResearchMethod_itemUnit_class_URI",  type:"ItemUnitRepresentationKGBBElement_URI", KGBB_URI:"ResearchMethodItemUnitKGBB_URI", category:"NamedIndividual", data_view_information:"true", itemUnit_html:"research_method.html", component:"research_method_itemUnit", link_$$$_1:"{{'name':'research_step_itemUnit_input_info', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/OBI_0000011', 'ontology_ID':'OBI', 'target_KGBB_URI':'ResearchActivityItemUnitKGBB_URI', 'instantiated_by_statementUnitKGBB':'ResearchMethodActivityRelationStatementUnitKGBB_URI', 'data_item_type':'itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_results_in':'added_itemUnit', 'edit_results_in':'edited_itemUnit', 'links_to_component':'research_activity_itemUnit', 'query_key':'from_method_cypher_code', 'edit_cypher_key':'edit_cypher', 'placeholder_text':'specify the type of research activity', 'input_info_URI':'InputInfo1ResearchActivityItemUnitIND_URI', 'input_source':'input1', 'editable':'true'}}",
    link_$$$_2:"{{'name':'research_method_itemUnit_input_info', 'placeholder_text':'specify the type of research method', 'ontology_ID':'MMO,NCIT', 'input_restricted_to_subclasses_of':'', 'target_KGBB_URI':'ResearchMethodItemUnitKGBB_URI', 'instantiated_by_statementUnitKGBB':'ResearchMethodParthoodStatementUnitKGBB_URI','data_item_type':'itemUnit', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_itemUnit', 'query_key':'from_method_cypher_code', 'links_to_component':'research_method_itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_results_in':'added_itemUnit'}}", link_$$$_3:"{{'name':'research_objective_itemUnit_input_info', 'placeholder_text':'specify the type of research objective', 'ontology_ID':'AGRO,IAO,ERO,OBI', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000005', 'target_KGBB_URI':'ResearchObjectiveItemUnitKGBB_URI', 'instantiated_by_statementUnitKGBB':'ResearchMethodObjectiveRelationStatementUnitKGBB_URI', 'data_item_type':'itemUnit', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_itemUnit', 'query_key':'from_method_cypher_code', 'links_to_component':'research_objective_itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_results_in':'added_itemUnit'}}"}})
    CREATE (ResearchMethodItemUnitkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(researchMethodInputInfo1KGBBelement:ResearchMethodInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of research method itemUnit", description:"User input information 1 for the specification of the research method resource for a research method itemUnit.", URI:"InputInfo1ResearchMethodItemUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", input_name:"research_method_input", node_type:"input1", KGBB_URI:"ResearchMethodItemUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1ResearchMethodItemUnitIND_URI", input_restricted_to_subclasses_of:"", ontology_ID:"MMO,NCIT", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})
    CREATE (ResearchMethodItemUnitkgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about a step of the research method.", itemUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchMethodItemUnitKGBB_URI", target_KGBB_URI:"ResearchMethodItemUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_method_cypher_code", instantiated_by_statementUnitKGBB:"ResearchMethodParthoodStatementUnitKGBB_URI"}}]->(ResearchMethodItemUnitkgbb)
    CREATE (ResearchMethodItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of research method parthood statementUnits in its entry.", KGBB_URI:"ResearchMethodItemUnitKGBB_URI", target_KGBB_URI:"ResearchMethodParthoodStatementUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_method_cypher_code", statementUnit_object_URI:"object$_$URI", input_results_in:"added_statementUnit", instantiates_itemUnitKGBB:"ResearchMethodItemUnitKGBB_URI"}}]->(researchMethodParthoodStatementUnitkgbb)
    CREATE (ResearchMethodItemUnitkgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about a research activity that realizes the research method.", itemUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchMethodItemUnitKGBB_URI", target_KGBB_URI:"ResearchActivityItemUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_method_cypher_code", instantiated_by_statementUnitKGBB:"ResearchMethodActivityRelationStatementUnitKGBB_URI"}}]->(ResearchActivityItemUnitkgbb)
    CREATE (ResearchMethodItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of research method activity relation statementUnits in its entry.", KGBB_URI:"ResearchMethodItemUnitKGBB_URI", target_KGBB_URI:"ResearchMethodActivityRelationStatementUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_method_cypher_code", statementUnit_object_URI:"object$_$URI", input_results_in:"added_statementUnit", instantiates_itemUnitKGBB:"ResearchActivityItemUnitKGBB_URI"}}]->(researchMethodActivityRelationStatementUnitkgbb)
    CREATE (ResearchMethodItemUnitkgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about a research objective that is part of the research method.", itemUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchMethodItemUnitKGBB_URI", target_KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_method_cypher_code", instantiated_by_statementUnitKGBB:"ResearchMethodObjectiveRelationStatementUnitKGBB_URI"}}]->(ResearchObjectiveItemUnitkgbb)
    CREATE (ResearchMethodItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of research method objective relation statementUnits in its entry.", KGBB_URI:"ResearchMethodItemUnitKGBB_URI", target_KGBB_URI:"ResearchMethodObjectiveRelationStatementUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_method_cypher_code", statementUnit_object_URI:"object$_$URI", input_results_in:"added_statementUnit", instantiates_itemUnitKGBB:"ResearchObjectiveItemUnitKGBB_URI"}}]->(researchMethodObjectiveRelationStatementUnitkgbb)
    // RESEARCH OBJECTIVE ITEM_UNIT KGBB RELATIONS
    CREATE (ResearchObjectiveItemUnitkgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(ResObjectiveItemUnit)
    CREATE (ResearchObjectiveItemUnitkgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(researchObjectiveItemUnitRepresentation1KGBBelement:ResearchObjectiveItemUnitRepresentationKGBBElement_IND:ItemUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research objective itemUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing research objective data associated with a research paper entry in the user interface in a human-readable form using the research objective itemUnit Knowledge Graph Building Block.", data_view_name:"{data_view_name}", node_type:"itemUnit representation", URI:"ResearchObjectiveItemUnitRepresentation1KGBBElementIND_URI", data_item_type_URI:"ResearchObjective_itemUnit_class_URI",  type:"ItemUnitRepresentationKGBBElement_URI", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", category:"NamedIndividual", data_view_information:"true", itemUnit_html:"research_objective.html", component:"research_objective_itemUnit", link_$$$_1:"{{'name':'research_objective_itemUnit_input_info', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000005', 'ontology_ID':'AGRO,IAO,ERO,OBI', 'target_KGBB_URI':'ResearchObjectiveItemUnitKGBB_URI', 'instantiated_by_statementUnitKGBB':'ResearchObjectiveParthoodStatementUnitKGBB_URI', 'data_item_type':'itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_results_in':'added_itemUnit', 'edit_results_in':'edited_itemUnit', 'links_to_component':'research_objective_itemUnit', 'query_key':'from_objective_cypher_code', 'edit_cypher_key':'edit_cypher', 'placeholder_text':'specify the type of research objective', 'input_info_URI':'InputInfo1ResearchObjectiveItemUnitIND_URI', 'input_source':'input1', 'editable':'true'}}",
    link_$$$_2:"{{'name':'research_method_itemUnit_input_info', 'placeholder_text':'specify the type of research method', 'ontology_ID':'MMO,NCIT', 'input_restricted_to_subclasses_of':'', 'target_KGBB_URI':'ResearchMethodItemUnitKGBB_URI', 'instantiated_by_statementUnitKGBB':'ResearchObjectiveMethodRelationStatementUnitKGBB_URI', 'data_item_type':'itemUnit', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_itemUnit', 'query_key':'from_objective_cypher_code', 'links_to_component':'research_method_itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_results_in':'added_itemUnit'}}", link_$$$_3:"{{'name':'research_step_itemUnit_input_info', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/OBI_0000011', 'ontology_ID':'OBI', 'target_KGBB_URI':'ResearchActivityItemUnitKGBB_URI', 'instantiated_by_statementUnitKGBB':'ResearchObjectiveActivityRelationStatementUnitKGBB_URI', 'data_item_type':'itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_results_in':'added_itemUnit', 'edit_results_in':'edited_itemUnit', 'links_to_component':'research_activity_itemUnit', 'query_key':'from_objective_cypher_code', 'edit_cypher_key':'edit_cypher', 'placeholder_text':'specify the type of research activity', 'input_info_URI':'InputInfo1ResearchActivityItemUnitIND_URI', 'input_source':'input1', 'editable':'true'}}", link_$$$_4:"{{'name':'research_result_itemUnit_input_info', 'placeholder_text':'specify the type of research result', 'ontology_ID':'IAO', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000030', 'target_KGBB_URI':'ResearchResultItemUnitKGBB_URI', 'instantiated_by_statementUnitKGBB':'ResearchObjectiveResultRelationStatementUnitKGBB_URI', 'data_item_type':'itemUnit', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_itemUnit', 'query_key':'from_objective_cypher_code', 'links_to_component':'research_result_itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_results_in':'added_itemUnit'}}"}})
    CREATE (ResearchObjectiveItemUnitkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(researchObjectiveInputInfo1KGBBelement:ResearchObjectiveInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of research objective itemUnit", description:"User input information 1 for the specification of the research objective resource for a research objective itemUnit.", URI:"InputInfo1ResearchObjectiveItemUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", input_name:"research_objective_input", node_type:"input1", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1ResearchObjectiveItemUnitIND_URI", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/IAO_0000005", ontology_ID:"AGRO,IAO,ERO,OBI", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})
    CREATE (ResearchObjectiveItemUnitkgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about a the research method this research objective is a part of.", itemUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", target_KGBB_URI:"ResearchMethodItemUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_objective_cypher_code", instantiated_by_statementUnitKGBB:"ResearchObjectiveMethodRelationStatementUnitKGBB_URI"}}]->(ResearchMethodItemUnitkgbb)
    CREATE (ResearchObjectiveItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of research objective method relation statementUnits in its entry.", statementUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", target_KGBB_URI:"ResearchObjectiveMethodRelationStatementUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_objective_cypher_code", instantiates_itemUnitKGBB:"ResearchMethodItemUnitKGBB_URI"}}]->(researchObjectiveMethodRelationStatementUnitkgbb)
    CREATE (ResearchObjectiveItemUnitkgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about a research activity that achieves the research objective.", itemUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", target_KGBB_URI:"ResearchActivityItemUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_objective_cypher_code", instantiated_by_statementUnitKGBB:"ResearchObjectiveActivityRelationStatementUnitKGBB_URI"}}]->(ResearchActivityItemUnitkgbb)
    CREATE (ResearchObjectiveItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of research objective activity relation statementUnits in its entry.", statementUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", target_KGBB_URI:"ResearchObjectiveActivityRelationStatementUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_objective_cypher_code", instantiates_itemUnitKGBB:"ResearchActivityItemUnitKGBB_URI"}}]->(researchObjectiveActivityRelationStatementUnitkgbb)
    CREATE (ResearchObjectiveItemUnitkgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about a research result that achieves the research objective.", itemUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", target_KGBB_URI:"ResearchResultItemUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_objective_cypher_code", instantiated_by_statementUnitKGBB:"ResearchObjectiveResultRelationStatementUnitKGBB_URI"}}]->(ResearchResultItemUnitkgbb)
    CREATE (ResearchObjectiveItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of research objective result relation statementUnits in its entry.", statementUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", target_KGBB_URI:"ResearchObjectiveResultRelationStatementUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_objective_cypher_code", instantiates_itemUnitKGBB:"ResearchResultItemUnitKGBB_URI"}}]->(researchObjectiveResultRelationStatementUnitkgbb)
    CREATE (ResearchObjectiveItemUnitkgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about a research objective that is a part of this research objective.", itemUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", target_KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_objective_cypher_code", instantiated_by_statementUnitKGBB:"ResearchObjectiveParthoodStatementUnitKGBB_URI"}}]->(ResearchObjectiveItemUnitkgbb)
    CREATE (ResearchObjectiveItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of research objective parthood statementUnits in its entry.", statementUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", target_KGBB_URI:"ResearchObjectiveParthoodStatementUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_objective_cypher_code", instantiates_itemUnitKGBB:"ResearchObjectiveItemUnitKGBB_URI"}}]->(ResearchObjectiveItemUnitkgbb)
    // RESEARCH RESULT ITEM_UNIT KGBB RELATIONS
    CREATE (ResearchResultItemUnitkgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(ResResItemUnit)
    CREATE (ResearchResultItemUnitkgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(researchResultItemUnitRepresentation1KGBBelement:ResearchResultItemUnitRepresentationKGBBElement_IND:ItemUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research result itemUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing research result data associated with a research paper entry in the user interface in a human-readable form using the research result itemUnit Knowledge Graph Building Block.", data_item_type_URI:"ResearchResult_itemUnit_class_URI", data_view_name:"{data_view_name}", node_type:"itemUnit representation", URI:"ResearchResultItemUnitRepresentation1KGBBElementIND_URI", type:"ItemUnitRepresentationKGBBElement_URI", KGBB_URI:"ResearchResultItemUnitKGBB_URI", category:"NamedIndividual", data_view_information:"true", itemUnit_html:"research_result_itemUnit.html",  component:"research_result_itemUnit", link_$$$_1:"{{'name':'research_activity_itemUnit_input_info', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/OBI_0000011', 'ontology_ID':'OBI', 'edit_results_in':'edited_itemUnit', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'ResearchActivityItemUnitKGBB_URI', 'instantiated_by_statementUnitKGBB':'ResearchResultActivityRelationStatementUnitKGBB_URI', 'data_item_type':'itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_results_in':'added_itemUnit', 'links_to_component':'research_activity_itemUnit', 'query_key':'from_result_cypher_code', 'placeholder_text':'specify the type of research activity', 'editable':'true'}}",
    link_$$$_2:"{{'name':'research_result_itemUnit_input_info', 'placeholder_text':'specify the type of research result', 'ontology_ID':'IAO', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000030', 'target_KGBB_URI':'ResearchResultItemUnitKGBB_URI', 'instantiated_by_statementUnitKGBB':'ResearchResultParthoodStatementUnitKGBB_URI', 'input_info_URI':'InputInfo1ResearchResultItemUnitIND_URI', 'data_item_type':'itemUnit', 'edit_results_in':'edited_itemUnit', 'edit_cypher_key':'edit_cypher', 'query_key':'from_result_cypher_code', 'links_to_component':'research_result_itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_source':'input1', 'input_results_in':'added_itemUnit'}}", link_$$$_3:"{{'name':'material_entity_itemUnit_input_info', 'placeholder_text':'specify the type of material entity', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/BFO_0000040', 'edit_results_in':'edited_itemUnit', 'edit_cypher_key':'edit_cypher', 'ontology_ID':'UBERON,OBI,IDO', 'target_KGBB_URI':'MaterialEntityItemUnitKGBB_URI', 'instantiated_by_statementUnitKGBB':'ResearchResultMaterialEntityRelationStatementUnitKGBB_URI', 'data_item_type':'itemUnit', 'query_key':'from_result_cypher_code', 'links_to_component':'material_entity_itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_results_in':'added_itemUnit'}}", link_$$$_4:"{{'name':'research_objective_itemUnit_input_info', 'placeholder_text':'specify the type of research objective', 'ontology_ID':'AGRO,IAO,ERO,OBI', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/IAO_0000005', 'target_KGBB_URI':'ResearchObjectiveItemUnitKGBB_URI', 'instantiated_by_statementUnitKGBB':'ResearchResultObjectiveRelationStatementUnitKGBB_URI', 'data_item_type':'itemUnit', 'edit_cypher_key':'edit_cypher', 'edit_results_in':'edited_itemUnit', 'query_key':'from_result_cypher_code', 'links_to_component':'research_objective_itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_results_in':'added_itemUnit'}}"}})
    CREATE (ResearchResultItemUnitkgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about a research result documented in a particular research paper.", itemUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchResultItemUnitKGBB_URI", data_view_name:"{data_view_name}", target_KGBB_URI:"ResearchResultItemUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_result_cypher_code", input_results_in:"added_itemUnit", instantiated_by_statementUnitKGBB:"ResearchResultParthoodStatementUnitKGBB_URI"}}]->(ResearchResultItemUnitkgbb)
    CREATE (ResearchResultItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of research result parthood statementUnits in its entry.", statementUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchResultItemUnitKGBB_URI", target_KGBB_URI:"ResearchResultParthoodStatementUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_result_cypher_code", instantiates_itemUnitKGBB:"ResearchResultItemUnitKGBB_URI"}}]->(researchResultParthoodStatementUnitkgbb)
    CREATE (ResearchResultItemUnitkgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about a research activity step of a research activity.", itemUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchResultItemUnitKGBB_URI", target_KGBB_URI:"ResearchActivityItemUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_result_cypher_code", instantiated_by_statementUnitKGBB:"ResearchResultActivityRelationStatementUnitKGBB_URI"}}]->(ResearchActivityItemUnitkgbb)
    CREATE (ResearchResultItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of research result activity relation statementUnits in its entry.", statementUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchResultItemUnitKGBB_URI", target_KGBB_URI:"ResearchResultActivityRelationStatementUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_result_cypher_code", instantiates_itemUnitKGBB:"ResearchActivityItemUnitKGBB_URI"}}]->(researchResultActivityRelationStatementUnitkgbb)
    CREATE (ResearchResultItemUnitkgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about a particular material entity as it is documented in a particular research paper.", itemUnit_object_URI:"object$_$URI",KGBB_URI:"ResearchResultItemUnitKGBB_URI", data_view_name:"{data_view_name}", target_KGBB_URI:"MaterialEntityItemUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_result_cypher_code", input_results_in:"added_itemUnit", instantiated_by_statementUnitKGBB:"ResearchResultMaterialEntityRelationStatementUnitKGBB_URI"}}]->(materialEntityItemUnitkgbb)
    CREATE (ResearchResultItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of research result material entity relation statementUnits in its entry.", statementUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchResultItemUnitKGBB_URI", target_KGBB_URI:"ResearchResultMaterialEntityRelationStatementUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_result_cypher_code", instantiates_itemUnitKGBB:"MaterialEntityItemUnitKGBB_URI"}}]->(researchResultMaterialEntityRelationStatementUnitkgbb)
    CREATE (ResearchResultItemUnitkgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about a research objective that is part of the research method.", itemUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchResultItemUnitKGBB_URI", target_KGBB_URI:"ResearchObjectiveItemUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_result_cypher_code", instantiated_by_statementUnitKGBB:"ResearchResultObjectiveRelationStatementUnitKGBB_URI"}}]->(ResearchObjectiveItemUnitkgbb)
    CREATE (ResearchResultItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of research result objective relation statementUnits in its entry.", statementUnit_object_URI:"object$_$URI", KGBB_URI:"ResearchResultItemUnitKGBB_URI", target_KGBB_URI:"ResearchResultObjectiveRelationStatementUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_result_cypher_code", instantiates_itemUnitKGBB:"ResearchObjectiveItemUnitKGBB_URI"}}]->(researchResultObjectiveRelationStatementUnitkgbb)
    CREATE (ResearchResultItemUnitkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(researchResultInputInfo1KGBBelement:ResearchResultInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of research result itemUnit", input_name:"research_result_input", description:"User input information 1 for the specification of the research result resource for a research result itemUnit.", placeholder_text:"specify the type of research result", URI:"InputInfo1ResearchResultItemUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"ResearchResultItemUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1ResearchResultItemUnitIND_URI", ontology_ID:"IAO", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/IAO_0000030", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})
    // MATERIAL ENTITY ITEM_UNIT KGBB RELATIONS
    CREATE (materialEntityItemUnitkgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(materialEntityItemUnitRepresentation1KGBBelement:MaterialEntityItemUnitRepresentationKGBBElement_IND:ItemUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Material entity itemUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing data about a particular material entity from a research paper entry in the user interface in a human-readable form using the material entity itemUnit Knowledge Graph Building Block.", data_view_name:"{data_view_name}", node_type:"itemUnit representation", URI:"MaterialEntityItemUnitRepresentation1KGBBElementIND_URI", type:"ItemUnitRepresentationKGBBElement_URI", data_item_type_URI:"material_entity_itemUnit_URI",  KGBB_URI:"MaterialEntityItemUnitKGBB_URI", itemUnit_html:"material_entity_itemUnit.html", category:"NamedIndividual", data_view_information:"true", component:"material_entity_itemUnit", link_$$$_1:"{{'name':'material_entity_itemUnit_input_info', 'placeholder_text':'specify the type of material entity', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/BFO_0000040', 'ontology_ID':'UBERON,OBI,IDO', 'target_KGBB_URI':'MaterialEntityItemUnitKGBB_URI', 'instantiated_by_statementUnitKGBB':'MaterialEntityParthoodStatementUnitKGBB_URI', 'data_item_type':'itemUnit', 'edit_results_in':'edited_itemUnit', 'edit_cypher_key':'edit_cypher', 'query_key':'from_material_entity_cypher_code', 'links_to_component':'material_entity_itemUnit', 'itemUnit_object_URI':'object$_$URI', 'input_results_in':'added_itemUnit'}}", link_$$$_2:"{{'name':'quality_relation_identification_statementUnit_input_info', 'placeholder_text':'select a quality', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/BFO_0000019', 'ontology_ID':'PATO,OMIT', 'edit_results_in':'edited_statementUnit', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'QualityIdentificationStatementUnitKGBB_URI', 'data_item_type':'statementUnit', 'query_key':'quality_cypher_code', 'links_to_component':'quality_identification_statementUnit', 'statementUnit_object_URI':'object$_$URI', 'input_results_in':'added_statementUnit', 'edit_results_in':'edited_statementUnit'}}", link_$$$_3:"{{'name':'material_entity_parthood_granularity_tree_info', 'target_KGBB_URI':'MatEntparthoodgranperspectiveKGBB', 'data_item_type':'granularity_tree', 'links_to_component':'material_entity_parthood_granularity_tree', 'granularity_tree_object_URI':'object$_$URI'}}"}})
    CREATE (materialEntityItemUnitkgbb)-[:HAS_ITEM_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_itemUnit_element_URI", description:"This itemUnit element specifies information about a particular material entity as it is documented in a particular research paper.", itemUnit_object_URI:"object$_$URI", KGBB_URI:"MaterialEntityItemUnitKGBB_URI", target_KGBB_URI:"MaterialEntityItemUnitKGBB_URI", required:"false", quantity:"m", query_key:"from_material_entity_cypher_code", input_results_in:"added_itemUnit", instantiated_by_statementUnitKGBB:"MaterialEntityParthoodStatementUnitKGBB_URI"}}]->(materialEntityItemUnitkgbb)
    CREATE (materialEntityItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of material entity parthood statementUnits in its entry.", statementUnit_object_URI:"object$_$URI", KGBB_URI:"MaterialEntityItemUnitKGBB_URI", target_KGBB_URI:"MaterialEntityParthoodStatementUnitKGBB_URI", required:"false", input_results_in:"added_itemUnit", quantity:"m", query_key:"from_material_entity_cypher_code", instantiates_itemUnitKGBB:"MaterialEntityItemUnitKGBB_URI"}}]->(materialEntityParthoodStatementUnitkgbb)
    CREATE (materialEntityItemUnitkgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of quality relation identification statementUnits in its itemUnit.", KGBB_URI:"MaterialEntityItemUnitKGBB_URI", target_KGBB_URI:"QualityIdentificationStatementUnitKGBB_URI", required:"false", quantity:"m", query_key:"quality_cypher_code", statementUnit_object_URI:"object$_$URI", input_results_in:"added_statementUnit"}}]->(qualitykgbb)
    CREATE (materialEntityItemUnitkgbb)-[:HAS_GRANULARITY_TREE_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_granularity_tree_element_URI", description:"This granularity tree element specifies information about the existence and composition of a parthood-based granularity tree of particular material entities.", KGBB_URI:"MaterialEntityItemUnitKGBB_URI", target_KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", required:"false", quantity:"m", granularity_tree_object_URI:"object$_$URI"}}]->(MatEntparthoodgranperspectiveKGBB)
    CREATE (materialEntityItemUnitkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(materialEntityInputInfo1KGBBelement:MaterialEntityInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of material entity itemUnit", input_name:"material_entity_input", description:"User input information 1 for the specification of the material entity resource for a material entity itemUnit.", placeholder_text:"specify the type of material entity", URI:"InputInfo1MaterialEntityItemUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"MaterialEntityItemUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1MaterialEntityItemUnitIND_URI", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/BFO_0000040", ontology_ID:"UBERON,OBI,IDO", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})
    // QUALITY STATEMENT_UNIT KGBB RELATIONS
    CREATE (qualitykgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(qualityStatementUnitRepresentation1KGBBelement:QualityIdentificationStatementUnitRepresentationKGBBElement_IND:StatementUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Quality relation identification statementUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the identification of a quality relation in the user interface in a human-readable form using the quality relation identification statementUnit Knowledge Graph Building Block.", URI:"QualityStatementUnitRepresentation1KGBBElementIND_URI", data_view_name:"{data_view_name}", node_type:"statementUnit representation", data_item_type_URI:"Quality_Identification_StatementUnit_URI", KGBB_URI:"QualityIdentificationStatementUnitKGBB_URI", category:"NamedIndividual", data_view_information:"true", component:"quality_relation_identification_statementUnit", link_$$$_1:"{{'name':'quality_statementUnit_relation_identification_input_info', 'component':'quality_relation_identification_statementUnit', 'input_info_URI':'InputInfo1QualityStatementUnitIND_URI', 'placeholder_text':'select a type of quality', 'input_source':'input1', 'editable':'true', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/BFO_0000019', 'ontology_ID':'PATO,OMIT', 'edit_results_in':'edited_statementUnit', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'QualityIdentificationStatementUnitKGBB_URI', 'statementUnit_object_URI':'object$_$URI', 'data_item_type':'statementUnit', 'query_key':'quality_cypher_code', 'input_results_in':'added_statementUnit'}}", link_$$$_2:"{{'name':'weight_measurement_statementUnit_input_info', 'placeholder_text_1':'value', 'user_input_data_type':'xsd:float', 'edit_results_in':'edited_statementUnit', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'WeightMeasurementStatementUnitKGBB_URI', 'data_item_type':'statementUnit', 'query_key':'weight_measurement_cypher_code', 'links_to_component':'weight_measurement_statementUnit', 'statementUnit_object_URI':'object$_$URI', 'input_results_in':'added_statementUnit', 'edit_results_in':'edited_statementUnit', 'placeholder_text_2':'select a gram-based unit', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/UO_1000021', 'ontology_ID':'UO'}}", link_$$$_3:"{{'name':'R0_measurement_statementUnit_input_info', 'placeholder_text_1':'value', 'placeholder_text_3':'upper limit', 'placeholder_text_2':'lower limit', 'user_input_data_type':'xsd:float', 'edit_results_in':'edited_statementUnit', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'R0MeasurementStatementUnitKGBB_URI', 'data_item_type':'statementUnit', 'query_key':'r0_measurement_cypher_code', 'links_to_component':'R0_measurement_statementUnit', 'statementUnit_object_URI':'object$_$URI', 'input_results_in':'added_statementUnit', 'edit_results_in':'edited_statementUnit'}}"}})
    CREATE (qualitykgbb)-[:HAS_EXPORT_MODEL {{category:"ObjectPropertyExpression", URI:"orkg_has_export_model_URI"}}]->(qualityexportModel1KGBBelement:ExportModelKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Quality relation identification statementUnit export model 1", description:"A Knowledge Graph Building Block element that provides an export model for identified quality relations. The export model 1 is based on the OBO/OBI data model.", URI:"QualityExportModel1KGBBElementIND_URI", type:"ExportModelKGBBElement_URI", KGBB_URI:"QualityIdentificationStatementUnitKGBB_URI", export_scheme:"OBO", category:"NamedIndividual", export_model_cypher_code:"cypherQuery"}})
    CREATE (qualitykgbb)-[:HAS_EXPORT_MODEL {{category:"ObjectPropertyExpression", URI:"orkg_has_export_model_URI"}}]->(exportModel2KGBBelement:ExportModelKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Quality relation identification statementUnit export model 2", description:"A Knowledge Graph Building Block element that provides an export model for identified quality relations. The export model 2 is based on the OBOE ontology data model.", URI:"QualityExportModel2KGBBElementIND_URI", type:"ExportModelKGBBElement_URI", KGBB_URI:"QualityIdentificationStatementUnitKGBB_URI", export_scheme:"OBOE", category:"NamedIndividual", export_model_cypher_code:"cypherQuery"}})
    CREATE (qualitykgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(qualityInputInfo1KGBBelement:QualityInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of quality relation identification statementUnit", description:"User input information 1 for the specification of the quality resource for a quality relation identification statementUnit.", input_name:"quality_identification_input", placeholder_text:"select a type of quality", URI:"InputInfo1QualityStatementUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"QualityIdentificationStatementUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1QualityStatementUnitIND_URI", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/BFO_0000019", ontology_ID:"PATO,OMIT", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})
    CREATE (qualitykgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of weight measurement statementUnits in its statementUnit.", KGBB_URI:"QualityIdentificationStatementUnitKGBB_URI", target_KGBB_URI:"WeightMeasurementStatementUnitKGBB_URI", required:"false", quantity:"m", query_key:"weight_measurement_cypher_code", input_results_in:"added_statementUnit"}}]->(weightkgbb)
    CREATE (qualitykgbb)-[:HAS_STATEMENT_UNIT_ELEMENT {{category:"ObjectPropertyExpression", URI:"orkg_has_statementUnit_element_URI", description:"This statementUnit element specifies information about the use of basic reproduction number measurement statementUnits in its statementUnit.", KGBB_URI:"QualityIdentificationStatementUnitKGBB_URI", target_KGBB_URI:"R0MeasurementStatementUnitKGBB_URI", required:"false", quantity:"m", query_key:"r0_measurement_cypher_code", input_results_in:"added_statementUnit"}}]->(R0Measurementkgbb)
    // WEIGHT MEASUREMENT STATEMENT_UNIT KGBB
    CREATE (weightkgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(weightMeasStatementUnitRepresentation1KGBBelement:WeightMeasurementStatementUnitRepresentationKGBBElement_IND:StatementUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Weight measurement statementUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the weight measurement statementUnit in the user interface in a human-readable form using the weight measurement statementUnit Knowledge Graph Building Block.", URI:"WeightMeasurementStatementUnitRepresentation1KGBBElementIND_URI", data_view_name:"{data_view_name}", node_type:"statementUnit representation", data_item_type_URI:"weight_measurement_statementUnit_URI", KGBB_URI:"WeightMeasurementStatementUnitKGBB_URI", category:"NamedIndividual", data_view_information:"true", component:"weight_measurement_statementUnit", link_$$$_1:"{{'name':'weight_measurement_statementUnit_input_info', 'placeholder_text_1':'value', 'user_input_data_type':'xsd:float', 'edit_results_in':'edited_statementUnit', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'WeightMeasurementStatementUnitKGBB_URI', 'data_item_type':'statementUnit', 'query_key':'weight_measurement_cypher_code', 'links_to_component':'weight_measurement_statementUnit', 'statementUnit_object_URI':'object$_$URI', 'input_results_in':'added_statementUnit', 'edit_results_in':'edited_statementUnit', 'placeholder_text_2':'select a gram-based unit', 'input_restricted_to_subclasses_of':'http://purl.obolibrary.org/obo/UO_1000021', 'ontology_ID':'UO'}}"}})
    CREATE (weightkgbb)-[:HAS_EXPORT_MODEL {{category:"ObjectPropertyExpression", URI:"orkg_has_export_model_URI"}}]->(weightMeasurementexportModel1KGBBelement:ExportModelKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Weight measurement statementUnit export model 1", description:"A Knowledge Graph Building Block element that provides an export model for weight measurements. The export model 1 is based on the OBO/OBI data model.", URI:"WeightMeasurementExportModel1KGBBElementIND_URI", type:"ExportModelKGBBElement_URI", KGBB_URI:"WeightMeasurementStatementUnitKGBB_URI", export_scheme:"OBO", category:"NamedIndividual", export_model_cypher_code:"cypherQuery"}})
    CREATE (weightkgbb)-[:HAS_EXPORT_MODEL {{category:"ObjectPropertyExpression", URI:"orkg_has_export_model_URI"}}]->(weightMeasurementexportModel2KGBBelement:ExportModelKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Weight measurement statementUnit export model 2", description:"A Knowledge Graph Building Block element that provides an export model for weight measurements. The export model 2 is based on the OBOE ontology data model.", URI:"WeightMeasurementExportModel2KGBBElementIND_URI", type:"ExportModelKGBBElement_URI", KGBB_URI:"WeightMeasurementStatementUnitKGBB_URI", export_scheme:"OBOE", category:"NamedIndividual", export_model_cypher_code:"cypherQuery"}})
    CREATE (weightkgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(weightMeasurementStatementUnit)
    CREATE (weightkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(weightMeasurementInputInfo1KGBBelement:WeightMeasurementInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of weight measurement statementUnit", description:"User input information 1 for the specification of the weight measurement value for a weight measurement statementUnit.", placeholder_text:"value", input_name:"weight_value_input", URI:"InputInfo1WeightMeasurementStatementUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"WeightMeasurementStatementUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1WeightMeasurementStatementUnitIND_URI", user_input_data_type:"xsd:float", data_view_information:"true", input_target_property:["value"]}})
    CREATE (weightkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(weightMeasurementInputInfo2KGBBelement:WeightMeasurementInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 2 element of weight measurement statementUnit", description:"User input information 2 for the specification of the weight measurement unit resource for a weight measurement statementUnit.", input_name:"weight_unit_input", placeholder_text:"select a gram-based unit", URI:"InputInfo2WeightMeasurementStatementUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input2", KGBB_URI:"WeightMeasurementStatementUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo2WeightMeasurementStatementUnitIND_URI", input_restricted_to_subclasses_of:"http://purl.obolibrary.org/obo/UO_1000021", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})
    // R0 MEASUREMENT STATEMENT_UNIT KGBB
    CREATE (R0Measurementkgbb)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(R0MeasStatementUnitRepresentation1KGBBelement:BasicReproductionNumberMeasurementStatementUnitRepresentationKGBBElement_IND:StatementUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Basic reproduction number measurement statementUnit representation element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the basic reproduction number measurement statementUnit in the user interface in a human-readable form using the basic reproduction number measurement statementUnit Knowledge Graph Building Block.", URI:"R0MeasurementStatementUnitRepresentation1KGBBElementIND_URI", data_view_name:"{data_view_name}", node_type:"statementUnit representation", data_item_type_URI:"r0_measurement_statementUnit_URI", KGBB_URI:"R0MeasurementStatementUnitKGBB_URI", category:"NamedIndividual", data_view_information:"true", component:"R0_measurement_statementUnit", link_$$$_1:"{{'name':'R0_measurement_statementUnit_input_info', 'placeholder_text_1':'value', 'placeholder_text_3':'upper limit', 'placeholder_text_2':'lower limit', 'user_input_data_type':'xsd:float', 'edit_results_in':'edited_statementUnit', 'edit_cypher_key':'edit_cypher', 'target_KGBB_URI':'R0MeasurementStatementUnitKGBB_URI', 'data_item_type':'statementUnit', 'query_key':'r0_measurement_cypher_code', 'links_to_component':'R0_measurement_statementUnit', 'statementUnit_object_URI':'object$_$URI', 'input_results_in':'added_statementUnit', 'edit_results_in':'edited_statementUnit'}}"}})
    CREATE (R0Measurementkgbb)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(r0MeasurementStatementUnit)
    CREATE (R0Measurementkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(R0MeasurementInputInfo1KGBBelement:R0MeasurementInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 1 element of R0 measurement statementUnit", description:"User input information 1 for the specification of the R0 measurement value for a basic reproduction number measurement statementUnit.", placeholder_text:"value", input_name:"R0_value_input", URI:"InputInfo1R0MeasurementStatementUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"R0MeasurementStatementUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1R0MeasurementStatementUnitIND_URI", user_input_data_type:"xsd:float", data_view_information:"true", input_target_property:["value"]}})
    CREATE (R0Measurementkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(R0UpperConfLimitMeasurementInputInfo1KGBBelement:R0UpperConfidenceLimitMeasurementInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 2 element of upper confidence limit for R0 measurement statementUnit", description:"User input information 2 for the specification of the upper confidence limit value for an R0 measurement for a basic reproduction number measurement statementUnit.", placeholder_text:"upper limit", input_name:"upper_confidence_limit_value_input", URI:"InputInfo2UpperConfLimitR0MeasurementStatementUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input2", KGBB_URI:"R0MeasurementStatementUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo2UpperConfLimitR0MeasurementStatementUnitIND_URI", user_input_data_type:"xsd:float", data_view_information:"true", input_target_property:["value"]}})
    CREATE (R0Measurementkgbb)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(R0LowerConfLimitMeasurementInputInfo1KGBBelement:R0LowerConfidenceLimitMeasurementInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"User Input 3 element of lower confidence limit for R0 measurement statementUnit", description:"User input information 3 for the specification of the lower confidence limit value for an R0 measurement for a basic reproduction number measurement statementUnit.", placeholder_text:"lower limit", input_name:"lower_confidence_limit_value_input", URI:"InputInfo3LowerConfLimitR0MeasurementStatementUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input3", KGBB_URI:"R0MeasurementStatementUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo3LowerConfLimitR0MeasurementStatementUnitIND_URI", user_input_data_type:"xsd:float", data_view_information:"true", input_target_property:["value"]}})
    // RESEARCH TOPIC KGBB RELATIONS
    CREATE (researchTopicStatementUnitKGBB)-[:HAS_INPUT_INFO {{category:"ObjectPropertyExpression", URI:"orkg_has_input_info_URI"}}]->(researchTopicInputInfo1KGBBelement:ResearchTopicInputInfoKGBBElement_IND:InputInfoKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"research_topic_input", description:"User input information 1 for the specification of the research topic resource for a research topic statementUnit.", input_name:"research_topic_input", URI:"InputInfo1ResearchTopicStatementUnitIND_URI", type:"InputInfoKGBBElement_URI", data_view_name:"{data_view_name}", node_type:"input1", KGBB_URI:"ResearchTopicStatementUnitKGBB_URI", category:"NamedIndividual", input_info_URI:"InputInfo1ResearchTopicStatementUnitIND_URI", input_restricted_to_subclasses_of:"http://edamontology.org/topic_0003", ontology_ID:"EDAM", user_input_data_type:"ClassExpression", data_view_information:"true", input_target_property:["type", "name"]}})
    CREATE (researchTopicStatementUnitKGBB)-[:HAS_EXPORT_MODEL {{category:"ObjectPropertyExpression", URI:"orkg_has_export_model_URI"}}]->(researchtopicexportModel1KGBBelement:ExportModelKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research topic statementUnit export model 1", description:"A Knowledge Graph Building Block element that provides an export model for research topic relations. The export model 1 is based on the XXX data model.", URI:"ResearchTopicExportModel1KGBBElementIND_URI", export_scheme:"OBO", type:"ExportModelKGBBElement_URI", KGBB_URI:"ResearchTopicStatementUnitKGBB_URI", category:"NamedIndividual", export_model_cypher_code:"cypherQuery"}})
    CREATE (researchTopicUnitKGBB)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(researchTopicStatementUnitRepresentation1KGBBelement:ResearchTopicStatementUnitRepresentationKGBBElement_IND:StatementUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Research topic statementUnit representation 1 element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the research topic statementUnit in the user interface in a human-readable form using the research topic statementUnit Knowledge Graph Building Block.", data_view_name:"{data_view_name}", URI:"ResearchTopicRepresentation1KGBBElementIND_URI", type:"StatementUnitRepresentationKGBBElement_URI", component:"research_topic_statementUnit", data_item_type_URI:"ResearchTopicStatementUnit_URI", node_type:"statementUnit_representation", KGBB_URI:"ResearchTopicStatementUnitKGBB_URI", data_view_information:"true", category:"NamedIndividual", link_$$$_1:"{{'name':'research_topic_input', 'component':'research_topic_statementUnit', 'input_info_URI':'InputInfo1ResearchTopicStatementUnitIND_URI', 'placeholder_text':'specify the research topic', 'input_source':'input1', 'editable':'true'}}"}})
    // CONFIDENCE LEVEL STATEMENT_UNIT KGBB
    CREATE (confidenceLevelStatementUnitKGBB)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(confidenceLevelStatementUnit)
    CREATE (confidenceLevelStatementUnitKGBB)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(confidenceLevelStatementUnitKGBBelement:ConfidenceLevelStatementUnitRepresentationKGBBElement_IND:StatementUnitRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Confidence level specification statementUnit representation 1 element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the confidence level specification statementUnit in the user interface in a human-readable form using the confidence level specification statementUnit Knowledge Graph Building Block.", data_view_name:"{data_view_name}", URI:"ConfLevelSpecStatementUnitRepresentation1KGBBElementIND_URI", type:"StatementUnitRepresentationKGBBElement_URI", data_item_type_URI:"ConfidenceLevelStatementUnit_URI", node_type:"statementUnit_representation", KGBB_URI:"ConfidenceLevelStatementUnitKGBB_URI", data_view_information:"true", category:"NamedIndividual", itemUnit_html:"", component:"confidence_level_statementUnit"}})
    // MATERIAL ENTITY PARTHOOD GRANULARITY PERSPECTIVE KGBB RELATIONS
    CREATE (MatEntparthoodgranperspectiveKGBB)-[:MANAGES {{category:"ObjectPropertyExpression", URI:"orkg_manages_URI"}}]->(MatEntParthoodGranTree)
    CREATE (MatEntparthoodgranperspectiveKGBB)-[:HAS_DATA_REPRESENTATION {{category:"ObjectPropertyExpression", URI:"orkg_has_data_representation_URI"}}]->(materialEntityParthoodGranularityTreeRepresentation1KGBBelement:MaterialEntityParthoodGranularityTreeRepresentationKGBBElement_IND:GranularityTreeRepresentationKGBBElement_IND:RepresentationKGBBElement_IND:KGBBElement_IND:NamedIndividual:Entity {{name:"Material entity parthood granularity tree representation 1 element", description:"A Knowledge Graph Building Block element that provides information for the front end for representing the data associated with the parthood-based granularity tree of material entities in the user interface in a human-readable form using the material entity parthood granularity perspective Knowledge Graph Building Block.", data_view_name:"{data_view_name}", URI:"MatEntParthoodGranTreeRepresentation1KGBBElementIND_URI", type:"GranularityTreeRepresentationKGBBElement_URI", data_item_type_URI:"MatEnt_Parthood_based_Granularity_tree_URI", node_type:"granularity_tree_representation", KGBB_URI:"MatEntParthoodGranularityPerspectiveKGBB_URI", data_view_information:"true", category:"NamedIndividual", itemUnit_html:"granularity_tree.html", component:"material_entity_parthood_granularity_tree"}})
    '''.format(creator = 'ORKGuserORCID', createdWith = 'ORKG', entryURI = 'entry_URIX', itemUnit_uri = 'itemUnit_URIX', statementUnitURI = 'statementUnit_URIX', doiEntry = 'Entry_DOI', data_view_name = 'ORKG')

get_entry_data_query_string = '''MATCH (n {{URI:"{entry_URI}"}}) RETURN count(n);'''.format(entry_URI="URI")





@app.route("/")

def index():
    global entry_uri
    global entry_dict
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
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
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name



    if request.method == "POST":

        entry_uri = request.form['entry_uri']
        print("----------------------NEW ENTRY URI------------------------")
        print(entry_uri)

        entry_data = EntryRepresentation(entry_uri)

        return render_template("/entry.html", entry_uri=entry_uri, itemUnit_data=itemUnit_data, entry_name=entry_data.entry_label, itemUnit_types_count=itemUnit_types_count, itemUnit_kgbb_uri=itemUnit_kgbb_uri)

    else:
        return render_template("entry.html", itemUnit_data=itemUnit_data, entry_name=entry_data.entry_label, itemUnit_types_count=itemUnit_types_count)









@app.route("/certainty", methods=['POST', 'GET'])
# certainty information for an statementUnit provided by a user

def certainty():
    global entry_uri
    global entry_dict
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name

    if request.method == "POST":

        if request.form:

            try:
                statementUnit_uri = request.form['input_name']
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print("++++++++++++++++++ STATEMENT_UNIT URI +++++++++++++++++++++")
                print(statementUnit_uri)

            except:
                pass

            try:
                certainty = request.form[statementUnit_uri + '_certainty']
                print("-------------------------- CERTAINTY -----------------------------")
                print(certainty)
            except:
                certainty = None


            try:
                itemUnit_uri = request.form[statementUnit_uri + '_itemUnit_uri']
                print("-------------------------- ITEM_UNIT URI ------------------------------")
                print(itemUnit_uri)
            except:
                itemUnit_uri = None


            try:
                entry_uri = request.form[statementUnit_uri + '_entry_uri']
                print("-------------------------- ENTRY URI -----------------------------")
                print(entry_uri)
            except:
                entry_uri = None

            try:
                parent_uri = request.form[statementUnit_uri + '_parent_uri']
                print("-------------------------- PARENT URI ----------------------------")
                print(parent_uri)
            except:
                parent_uri = None

            try:
                parent_item_type = request.form[statementUnit_uri + '_parent_type']
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
                certainty_statementUnit_uri = str(uuid.uuid4())

                # cypher query to specify or update the confidence level of the statementUnit
                statementUnit_confidence_query_string = '''MATCH (statementUnit {{URI:"{statementUnit_uri}"}})
                WITH statementUnit
                OPTIONAL MATCH (statementUnit)-[:STATEMENT_UNIT_CONFIDENCE_LEVEL]->(confidence {{current_version:"true"}})
                OPTIONAL MATCH (statementUnit)-[:HAS_ASSOCIATED_SEMANTIC_UNIT]->(certaintyStatementUnit:orkg_CertaintyStatementUnit {{current_version:"true"}})
                WITH statementUnit, confidence, certaintyStatementUnit
                FOREACH (i IN CASE WHEN confidence IS NULL THEN [1] ELSE [] END |
                CREATE (statementUnit)-[:STATEMENT_UNIT_CONFIDENCE_LEVEL {{category:"ObjectPropertyExpression", URI:"http://purl.obolibrary.org/obo/SEPIO_0000167", entry_URI:"{entry_uri}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnit_uri}", description:"A relation between an statementUnit and a value that indicates the degree of confidence that the Proposition it puts forth is true."}}]->(certainty{label}:NamedIndividual:Entity {{URI:"{certainty_uri}", type:"{type}", name:"{name}", ontology_ID:"{ontology_ID}", description:"{description}", current_version:"true", entry_URI:"{entry_uri}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnit_uri}", created_on:localdatetime(), last_updated_on:localdatetime(), contributed_by:["{creator}"], created_by:"{creator}", created_with:"{createdWith}", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual"}})
                CREATE (statementUnit)-[:HAS_ASSOCIATED_SEMANTIC_UNIT {{category:"ObjectPropertyExpression", URI:"orkg_contains_uri", entry_URI:"{entry_uri}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnit_uri}"}}]->(confidenceLevelStatementUnit_ind:orkg_ConfidenceLevelStatementUnit_IND:orkg_StatementUnit_IND:iao_DocumentPart_IND:iao_InformationContentEntity_IND:NamedIndividual:Entity {{name:"Confidence level specification statementUnit", URI:"{certainty_statementUnit_uri}", description:"This statementUnit models the specification of the confidence level for a given statementUnit, itemUnit, or entry in the orkg. As such, it is a statement about a statement or a collection of statements.", type:"ConfidenceLevelStatementUnit_URI", object_URI:"{certainty_uri}", entry_URI:"{entry_uri}", itemUnit_URI:"{itemUnit_uri}", KGBB_URI:"ConfidenceLevelStatementUnitKGBB_URI", node_type:"statementUnit", created_on:localdatetime(), last_updated_on:localdatetime(), created_by:"{creator}", contributed_by:["{creator}"], created_with:"{createdWith}", current_version:"true", versioned_doi:["NULL"], dataset_doi:["NULL"], category:"NamedIndividual", statementUnit_label:"{name} [{ontology_ID}]"}})
                CREATE (confidenceLevelStatementUnit_ind)-[:HAS_SEMANTIC_UNIT_SUBJECT {{category:"ObjectPropertyExpression", URI:"orkg_hasSemanticUnitSubject", entry_URI:"{entry_uri}", itemUnit_URI:"{itemUnit_uri}", statementUnit_URI:"{statementUnit_uri}"}}]->(certainty)
                )
                WITH statementUnit, confidence, certaintyStatementUnit
                FOREACH (i IN CASE WHEN confidence IS NOT NULL THEN [1] ELSE [] END |
                SET confidence.name="{name}"
                SET confidence.type="{type}"
                SET confidence.description="{description}"
                SET confidence.last_updated_on=localdatetime()
                SET confidence{label}:NamedIndividual:Entity
                SET certaintyStatementUnit.statementUnit_label="{name} [{ontology_ID}]"
                SET certaintyStatementUnit.last_updated_on = localdatetime()
                )
                RETURN statementUnit
                '''.format(statementUnit_uri=statementUnit_uri, certainty_uri = certainty_uri, name=name, type=type, label=label, description=description, ontology_ID=ontology_ID, entry_uri=entry_uri, itemUnit_uri=itemUnit_uri, creator='ORKGuserORCID', createdWith='ORKG', certainty_statementUnit_uri=certainty_statementUnit_uri)

                # query result
                result = connection.query(statementUnit_confidence_query_string, db='neo4j')
                print("---------------------------------------------------------------------------------")
                print("------------------------------------- RESULT ------------------------------------")
                print(result)


            else:
                # cypher query to delete the confidence level specification of the statementUnit
                statementUnit_confidence_query_string = '''OPTIONAL MATCH (statementUnit {{URI:"{statementUnit_uri}"}})-[:STATEMENT_UNIT_CONFIDENCE_LEVEL]->(certainty {{current_version:"true"}})
                SET certainty.current_version = "false"
                RETURN certainty.current_version
                '''.format(statementUnit_uri=statementUnit_uri)

                # query result
                result = connection.query(statementUnit_confidence_query_string, db='neo4j')
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
            if parent_item_type == "statementUnit":
                for parent in entry_dict:
                    if parent.get('id') == parent_uri:
                        parent_node_type = parent.get('node_type')
                        if parent_node_type == "statementUnit":
                            grand_parent_uri = parent.get('parent')
                            for grand_parent in entry_dict:
                                if grand_parent.get('id') == grand_parent_uri:
                                    grand_parent_node_type = grand_parent.get('node_type')
                                    if grand_parent_node_type == 'itemUnit':
                                        entry_dict = getEntryDict(entry_uri, data_view_name)

                                        entry_dict = updateEntryDict(entry_dict, grand_parent_uri)



                                        return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                        else:

                            entry_dict = getEntryDict(entry_uri, data_view_name)
                            entry_dict = updateEntryDict(entry_dict, parent_uri)
                            return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


            else:

                entry_dict = getEntryDict(entry_uri, data_view_name)
                entry_dict = updateEntryDict(entry_dict, parent_uri)
                return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

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
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
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

            itemUnit_uri = request.form[input_uri + '_itemUnit_uri']
            print("------------------------------ ITEM_UNIT URI ---------------------------------")
            print(itemUnit_uri)

            parent_item_type = request.form[input_uri + '_parent_item_type']
            print("--------------------------- PARENT ITEM TYPE ----------------------------")
            print(parent_item_type)

            query_key = "label_cypher"

            # cypher query to edit the label of the resource
            editInstanceLabel(parent_uri, kgbb_uri, entry_uri, itemUnit_uri, input_label, query_key, input_uri)

        flash('resource label updated', 'good')



        if parent_uri == entry_uri:
            print("---------------------------------------------------------------")
            print("----------------------- GOES TO ENTRY -------------------------")
            entry_dict = getEntryDict(entry_uri, data_view_name)


            return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


        if parent_uri != entry_uri:
            if parent_item_type == "statementUnit":
                for parent in entry_dict:
                    if parent.get('id') == parent_uri:
                        parent_node_type = parent.get('node_type')
                        if parent_node_type == "statementUnit":
                            grand_parent_uri = parent.get('parent')
                            for grand_parent in entry_dict:
                                if grand_parent.get('id') == grand_parent_uri:
                                    grand_parent_node_type = grand_parent.get('node_type')
                                    if grand_parent_node_type == 'itemUnit':
                                        entry_dict = getEntryDict(entry_uri, data_view_name)

                                        entry_dict = updateEntryDict(entry_dict, grand_parent_uri)



                                        return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                        else:

                            entry_dict = getEntryDict(entry_uri, data_view_name)
                            entry_dict = updateEntryDict(entry_dict, parent_uri)
                            return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


            else:

                entry_dict = getEntryDict(entry_uri, data_view_name)
                entry_dict = updateEntryDict(entry_dict, parent_uri)
                return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

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
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
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
                itemUnit_uri = answer[6]
                statementUnit_uri = answer[7]
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
                itemUnit_uri = answer[6]
                statementUnit_uri = answer[7]
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



            if input_result == 'added_statementUnit' or input_result == 'added_itemUnit':
                added_resource = addResource(parent_uri, kgbb_uri, entry_uri, itemUnit_uri, statementUnit_uri, description, bioportal_full_id, bioportal_preferred_name, bioportal_ontology_id, input_result, query_key, input_value, input_value1, input_value2)
                print("------------------------------------------------------------------")
                print("----------------------- ADDED RESOURCE ---------------------------")
                print(added_resource)
                resource_uri = added_resource[0]
                parent_uri = added_resource[1]
                result = added_resource[2]

                if result == "added_statementUnit":
                    statementUnit_uri = resource_uri
                    message = "StatementUnit has been added"
                    print("---------------------------------------------------------------")
                    print("------------------------ STATEMENT_UNIT URI ------------------------")
                    print(statementUnit_uri)

                elif result == "added_itemUnit":
                    itemUnit_uri = resource_uri
                    message = "ItemUnit has been added"
                    print("---------------------------------------------------------------")
                    print("-------------------------- ITEM_UNIT URI ---------------------------")
                    print(itemUnit_uri)


                if parent_uri == entry_uri:
                    print("---------------------------------------------------------------")
                    print("----------------------- GOES TO ENTRY -------------------------")
                    entry_dict = getEntryDict(entry_uri, data_view_name)


                    flash(message, 'good')

                    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


                if parent_uri != entry_uri:
                    if parent_item_type == "statementUnit":
                        for child in entry_dict:
                            if child.get('id') == parent_uri:
                                select_uri = child.get('parent')
                                entry_dict = getEntryDict(entry_uri, data_view_name)
                                entry_dict = updateEntryDict(entry_dict, select_uri)

                                flash(message, 'good')

                                return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                    elif parent_item_type == "itemUnit":
                        entry_dict = getEntryDict(entry_uri, data_view_name)
                        entry_dict = updateEntryDict(entry_dict, parent_uri)

                        flash(message, 'good')
                        return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))




            elif input_result == 'edited_statementUnit' or input_result == 'edited_itemUnit':
                added_resource = addResource(parent_uri, kgbb_uri, entry_uri, itemUnit_uri, statementUnit_uri, description, bioportal_full_id, bioportal_preferred_name, bioportal_ontology_id, input_result, query_key, input_value, input_value1, input_value2)
                print("------------------------------------------------------------------")
                print("----------------------- ADDED/EDITED RESOURCE --------------------")
                print(added_resource)
                resource_uri = added_resource[0]
                parent_uri = added_resource[1]
                result = added_resource[2]

                if result == "added_statementUnit":
                    statementUnit_uri = resource_uri
                    message = "StatementUnit has been added"
                    print("---------------------------------------------------------------")
                    print("------------------------ STATEMENT_UNIT URI ------------------------")
                    print(statementUnit_uri)

                if result == "edited_statementUnit":
                    statementUnit_uri = resource_uri
                    message = "StatementUnit has been successfully edited"
                    print("---------------------------------------------------------------")
                    print("------------------------ STATEMENT_UNIT URI ------------------------")
                    print(statementUnit_uri)

                elif result == "added_itemUnit":
                    itemUnit_uri = resource_uri
                    message = "ItemUnit has been added"
                    print("---------------------------------------------------------------")
                    print("-------------------------- ITEM_UNIT URI ---------------------------")
                    print(itemUnit_uri)

                elif result == "edited_itemUnit":
                    itemUnit_uri = resource_uri
                    message = "ItemUnit has been successfully edited"
                    print("---------------------------------------------------------------")
                    print("-------------------------- ITEM_UNIT URI ---------------------------")
                    print(itemUnit_uri)


                if parent_uri == entry_uri:
                    print("---------------------------------------------------------------")
                    print("----------------------- GOES TO ENTRY -------------------------")
                    entry_dict = getEntryDict(entry_uri, data_view_name)


                    flash(message, 'good')

                    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


                if parent_uri != entry_uri:
                    if parent_item_type == "statementUnit":
                        for parent in entry_dict:
                            if parent.get('id') == parent_uri:
                                parent_node_type = parent.get('node_type')
                                if parent_node_type == "statementUnit":
                                    grand_parent_uri = parent.get('parent')
                                    for grand_parent in entry_dict:
                                        if grand_parent.get('id') == grand_parent_uri:
                                            grand_parent_node_type = grand_parent.get('node_type')
                                            if grand_parent_node_type == 'itemUnit':
                                                entry_dict = getEntryDict(entry_uri, data_view_name)

                                                entry_dict = updateEntryDict(entry_dict, grand_parent_uri)

                                                flash(message, 'good')

                                                return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                                else:
                                    flash(message, 'good')
                                    entry_dict = getEntryDict(entry_uri, data_view_name)
                                    entry_dict = updateEntryDict(entry_dict, parent_uri)
                                    return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


                    else:
                        flash(message, 'good')
                        entry_dict = getEntryDict(entry_uri, data_view_name)
                        entry_dict = updateEntryDict(entry_dict, parent_uri)
                        return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                else:
                    entry_dict = getEntryDict(entry_uri, data_view_name)
                    entry_dict = updateEntryDict(entry_dict, entry_uri)

                    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

        else:
            return render_template("/entry.html", entry_data=entry_data, itemUnits_length=itemUnits_length, itemUnits_elements_length=itemUnits_elements_length, itemUnit_types_count=itemUnit_types_count, navi_dict=navi_dict, itemUnit_view_tree=itemUnit_view_tree)

    return render_template("/entry.html", entry_data=entry_data, itemUnit_types_count=itemUnit_types_count, navi_dict=navi_dict, itemUnit_view_tree=itemUnit_view_tree)








@app.route("/delete_input", methods=['POST', 'GET'])
# process information provided by a user

def delete_input():
    global entry_uri
    global entry_dict
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name


    if request.method == "POST":

        if request.form:
            try:
                request.form['delete_statementUnit']
                response = request.form['delete_statementUnit_uri']
                # response is a list of statementUnit_uri and parent_uri as a string
                response = response.replace("['","")
                response = response.replace("']","")

                parent_uri = response.partition("', '")[0]
                print("-----------------------------------------------------")
                print("------------------- PARENT URI ----------------------")
                print(parent_uri)

                statementUnit_uri = response.partition("', '")[2]
                print("-----------------------------------------------------")
                print("------------------ STATEMENT_UNIT URI --------------------")
                print(statementUnit_uri)

                deleteStatementUnit(statementUnit_uri, 'userID')

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
                            if parent_node_type == "statementUnit":
                                grand_parent_uri = parent.get('parent')
                                for grand_parent in entry_dict:
                                    if grand_parent.get('id') == grand_parent_uri:
                                        grand_parent_node_type = grand_parent.get('node_type')
                                        if grand_parent_node_type == 'itemUnit':
                                            entry_dict = updateEntryDict(entry_dict, grand_parent_uri)

                                            return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                            else:
                                entry_dict = updateEntryDict(entry_dict, parent_uri)
                                return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))



                else:
                    entry_dict = updateEntryDict(entry_dict, entry_uri)

                    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))




            except:
                pass
            try:
                request.form['delete_itemUnit']
                response = request.form['delete_itemUnit_uri']
                # response is a list of statementUnit_uri and parent_uri as a string
                response = response.replace("['","")
                response = response.replace("']","")

                parent_uri = response.partition("', '")[0]
                print("-----------------------------------------------------")
                print("------------------- PARENT URI ----------------------")
                print(parent_uri)

                itemUnit_uri = response.partition("', '")[2]
                print("-----------------------------------------------------")
                print("------------------ ITEM_UNIT URI -------------------------")
                print(itemUnit_uri)

                deleteItemUnit(itemUnit_uri, 'userID')

                entry_dict = getEntryDict(entry_uri, data_view_name)

                entry_dict = updateEntryDict(entry_dict, parent_uri)

                flash('ItemUnit has been deleted', 'good')

                if parent_uri != entry_uri:
                    return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))
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
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name


    if request.method == "POST":
        if request.form['entry_uri']:
            entry_uri = request.form['entry_uri']

            entry_dict = getEntryDict(entry_uri, data_view_name)



            return render_template("/entry.html", naviJSON=getJSON(entry_dict), entry_dict=entry_dict)

        else:
            return render_template("/entry.html", entry_data=entry_data, itemUnits_length=itemUnits_length, itemUnits_elements_length=itemUnits_elements_length, itemUnit_types_count=itemUnit_types_count, navi_dict=navi_dict, itemUnit_view_tree=itemUnit_view_tree, entry_view_tree=entry_view_tree)

    return render_template("/entry.html", entry_data=entry_data, itemUnits_length=itemUnits_length, itemUnits_elements_length=itemUnits_elements_length, itemUnit_types_count=itemUnit_types_count, navi_dict=navi_dict, itemUnit_view_tree=itemUnit_view_tree, entry_view_tree=entry_view_tree)









# navigating through an entry via the navi-tree
@app.route("/navi", methods=['POST', 'GET'])
def navi():
    global entry_uri
    global entry_dict
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name

    if request.method == 'POST':
        if request.form:
            data = json.loads(request.form['node_data'])
            print(data)
            itemUnit_uri = data['node_data'][0].get('original').get('id')
            node_type = data['node_data'][0].get('original').get('node_type')
            parent_uri = data['node_data'][0].get('original').get('parent')
            entry_uri = entry_dict[0].get('id')
            #itemUnit_uri = itemUnit_uri.decode("utf-8")
            print("---------------------------------------------------------------")
            print("---------------------------------------------------------------")
            print("-------------------------- ITEM_UNIT URI ---------------------------")
            print(itemUnit_uri)
            print(type(itemUnit_uri))
            print("---------------------------------------------------------------")
            print("---------------------------------------------------------------")
            print("-------------------------- NODE TYPE ---------------------------")
            print(node_type)


            if itemUnit_uri == entry_uri:
                entry_dict = updateEntryDict(entry_dict, itemUnit_uri)

                return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

            if node_type == "statementUnit" or node_type == "granularity_tree":
                if parent_uri != entry_uri:
                    for parent in entry_dict:
                        if parent.get('id') == parent_uri:
                            parent_node_type = parent.get('node_type')
                            if parent_node_type == "statementUnit":
                                grand_parent_uri = parent.get('parent')
                                for grand_parent in entry_dict:
                                    if grand_parent.get('id') == grand_parent_uri:
                                        grand_parent_node_type = grand_parent.get('node_type')
                                        if grand_parent_node_type == 'itemUnit':
                                            entry_dict = updateEntryDict(entry_dict, grand_parent_uri)

                                            return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

                            else:
                                entry_dict = updateEntryDict(entry_dict, parent_uri)
                                return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))



                else:
                    entry_dict = updateEntryDict(entry_dict, entry_uri)

                    return render_template("/entry.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))


            entry_dict = updateEntryDict(entry_dict, itemUnit_uri)

            return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

        else:
            return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

    return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))







# navigating to a particular itemUnit via a itemUnit resource
@app.route("/itemUnit", methods=['POST', 'GET'])
def itemUnit():
    global entry_uri
    global entry_dict
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name

    if request.method == 'POST':

        if request.form['itemUnit_uri']:
            itemUnit_uri = request.form['itemUnit_uri']

            entry_dict = updateEntryDict(entry_dict, itemUnit_uri)

            return render_template("/itemUnit.html", entry_dict=entry_dict, naviJSON=getJSON(entry_dict))

        else:
            return render_template("/itemUnit.html", navi_dict=navi_dict, itemUnit_view_tree=itemUnit_view_tree, entry_view_tree=entry_view_tree, naviJSON=getJSON(naviJSON))

    return render_template("/itemUnit.html", navi_dict=navi_dict, itemUnit_view_tree=itemUnit_view_tree, entry_view_tree=entry_view_tree, naviJSON=getJSON(naviJSON))







# getting versions of item back
@app.route("/_versioning", methods=['POST', 'GET'])
def versioning():
    global entry_uri
    global entry_dict
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
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
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
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
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
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
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
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
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
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
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
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
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
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
            statementUnit_class_list = getStatementUnitClassList()
            itemUnit_class_list = getItemUnitClassList()
            entry_class_list = getEntryClassList()

            return render_template("search.html", ontology_class_list=ontology_class_list, statementUnit_class_list=statementUnit_class_list, itemUnit_class_list=itemUnit_class_list, entry_class_list=entry_class_list)


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
    global itemUnit_data
    global itemUnit_kgbb_uri
    global itemUnit_types_count
    global statementUnit_kgbb_uri
    global entry_name
    global itemUnit_name
    global statementUnit_name
    global statementUnit_elements_dict
    global navi_dict
    global itemUnits_length
    global entry_node
    global connection
    global itemUnit_view_tree
    global statementUnit_view_tree
    global entry_view_tree
    global naviJSON
    global data_view_name



    if request.method == "POST":

        try:
            class_uri = request.form['itemUnit_class_uri']
            print("---------------------- ITEM_UNIT CLASS URI ---------------------------")
            print(class_uri)

            instances_list = getInstanceList(class_uri)
            print("---------------------- INSTANCES LIST ---------------------------")
            print(instances_list)

        except:
            pass

        itemUnit_nodes_list = []

        for i in range (0, len(instances_list)):
            itemUnit_uri = instances_list[i].get('URI')
            itemUnit_dict = getItemUnitRepresentation(itemUnit_uri, "ORKG")
            print("-------------------------------------------ITEM_UNIT_DICT----------------")
            print(itemUnit_dict)
            itemUnit_nodes_list.append(itemUnit_dict)

        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("+++++++++++++++++++++ FINAL ITEM_UNIT NODES LIST ++++++++++++++++++++++++++")
        print(itemUnit_nodes_list)
        print(len(itemUnit_nodes_list))

        return render_template("/search_result.html", itemUnit_nodes_list=itemUnit_nodes_list)




    else:
        return render_template("entry.html", itemUnit_data=itemUnit_data, entry_name=entry_data.entry_label, itemUnit_types_count=itemUnit_types_count)





if __name__ == "__main__":
    app.run()
