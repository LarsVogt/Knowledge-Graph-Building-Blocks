# A Minimum Viable Product for Knowledge Graph Building Blocks and Semantic Units
Currently, Knowledge-Graph-Building-Blocks exist only as a concept that I have been working on for several years (for a brief description, see below). I always wanted to develop a working prototype, a minimum viable product (MVP), as a proof of concept, but my lack of programming skills prevented me from doing so. Therefore, I decided to learn programming and started with learning Python during my Easter vacation 2021. I started to develop a MVP that implemented the concept of KGBBs. What you see here is the result of 3 months of development time spent in my spare time. Since I am an absolute beginner without any programming experience and taught everything myself, the code certainly leaves something to be desired and also leaves ample room for improvement. Anyhow, I nevertheless think that the application I developed demonstrates the potential of Knowledge Graph Building Blocks.

If you want to run this application on your local machine, you must copy all files onto your machine. You also have to install Neo4j desktop (at least Version 4.2.4 with APOC plugin) and add a user with username:python, password:useCaseKGBB, and the roles admin and PUBLIC. Connection should be possible via uri: bolt://localhost:7687. You can then access the app via localhost:5000.


# Knowledge-Graph-Building-Blocks

The basis of the concept of Knowledge Graph Building Blocks is the organization and structuring of the overall data graph of a knowledge graph into semantically meaningful subgraphs, i.e. semantic units, each of which is represented in the graph by its own resource (i.e. node). Currently, the following basic types of semantic unit are distinguished (of which only a view are used in the prototype):

![Fig5](https://user-images.githubusercontent.com/32734975/150550485-6a7522c0-149e-4fb8-8450-fd8de5030020.jpg)
Basic taxonomy of different types of semantic units

Basic units partition a knowledge graph into subgraphs, each of which is a unit of information that represents the smallest independent proposition (statement) that is semantically meaningful for a human reader. A compound unit, on the other hand, is a container of at least two semantic units. 

Partitioning a knowledge graph into smaller manageable semantic units provides solutions to seven problems that many knowledge graph applications must face and help to enforce machine-actionability and human-readability and thus FAIRness of data and metadata in a knowledge graph.

1) Machines need more information than human readers and human readers don't want to look at complex graphs
2) Many software developers do not know SPARQL/Cypher query language and do not want to learn it
3) Using knowledge graphs is not a guarantee for interoperability and FAIRness of their contents
4) Different communities often follow different data standards, even for the same type of data!
5) Making statements about statements can be challenging 
6) Knowledge graphs may not scale well with continuously incoming streams of data
7) Importing semantically unstructured (legacy) data from a tabular format (CSV, Excell sheets) into a FAIR knowledge graph is not a trivial task

In order to meet the requirements of findability and interoperability of data and metadata, it is crucial that the same graph pattern is applied for modeling the same type of information. This can be achieved using languages for describing patterns, such as the Shapes Constraint Language SHACL and DASH or the Reasonable Ontology Templates ottr, with which graph patterns can be defined. Unfortunately, these languages do not fully provide the functionality that we often need for efficiently managing our data. Moreover, they have been developed for RDF and not for labeled property graphs such as Neo4j (although translations tools exist). This is one of the reasons why we developed the concept of a Knowledge Graph Building Block (KGBB), which represents a construct that provides information for a knowledge graph application regarding graph patterns, data queries, and the representation of data for human-readability. 

You can also take a look at the pdf "Vogt_Retreat_2021_extended.pdf" that you can find in the project files. This is an extended version of a presentation I gave that introduces the concepts of semantic units and knowledege graph building blocks and how they can improve the explorability of FAIR knowledge graphs (FAIR+E). It also shows some screenshots from the prototype. However, especially the concept of semantic units developed quite a bit since I gave this presentation, so you will find a different terminology and classification of semantic units in this presentation compared to the figure above.

# The general idea
Knowledge Graph Building Blocks (KGBBs) are knowledge graph processing modules with which knowledge graphs can be managed. Each type of semantic unit that the knowledge graph application must distinguish has its own KGGB that is specified in reference to this semantic unit. The specifications of each KGBB can be used for managing and organizing all data belonging to the corresponding type of semantic unit in a knowledge graph. 

![Fig19_KGBB_overview](https://user-images.githubusercontent.com/32734975/151023736-e5d60b0f-0945-4ac1-8976-051557d38092.jpg)
General schema of the overall architecture and workflows of a knowledge graph applications based on KGBBs.

KGBBs together with a KGBB application enginge provide:

1) graph patterns for storing data and metadata in a machine-actionable way in the graph, optimized for scalability (even allowing for storing in a tabular format), 
2) input controls for restricting user input, 
3) access templates that specify different formats and data schemes for accessing and exporting the data
4) display templates to represent the data of a semantic unit in a human-readable way in a user interface (UI), 
5) pre-defined SPARQL/Cypher queries for CRUD operations, and
6) a fine-grained partition of the overall data graph that applies the concept of semantic units and partitions the data graph into semantically meaningful subgraphs which are classified and can be used for supporting data access and exploration as well as the import of unstructured data from, e.g., csv and excel files. 

Different KGBBs can be related to one another so that data newly added to one KGBB can trigger another KGBB to instantiate its corresponding data graph, thereby organizing and guiding the growth of the knowledge graph. Resources can be shared across different KGBBs for subsequent re-use in newly added semantic units and these newly added units are connected to the overall data graph through these resources. In other words, sets of KGBBs manage, organize, and structure a growing knowledge graph, resulting in an overall data graph that is organized and structured into different semantic units, allowing for making statements about statements, providing users with input forms and human-readable data representations in the UI, enforcing graph patterns for internal interoperability and machine-actionability of data and metadata, specifying multiple schemata for data access, with the possibility to add further schemata for newly upcoming standards, and providing generic predefined SPARQL/Cypher queries that can be used for searching and exploring the graph. KGBBs could even support the storage of data in a tabular format to meet the scalability requirements of large amounts of continuously incoming data such as from sensors. Moreover, with the specification of basic units, simple description units, complex description units, dataset, and granularity tree units, KGBBs can provide the basis for developing promising tools that support the import of unstructured data into a knowledge graph. KGBBs thus have the potential to provide solutions for all seven problems of knowledge graph applications mentioned above.

By relating different KGBBs to one another, the structure of the overall data graph can be specified in a highly modular and expandable way. A complex description unit KGBB specifies the simple description unit KGBBs that may be linked to a complex description unit of that type. The KGBBs also specify possible relations between resources across different simple description units and basic units. A simple description unit KGBB specifies the basic unit KGBBs that may be linked to a simple description unit of this type and whether basic units of some respective basic unit KGBBs are required for the simple description unit and thus MUST be provided (=the input form for the basic unit must be fully completed) by users for adding the simple description unit to a complex description unit. They also specify whether the simple description unit may contain only one or more basic units of a specific type and in which order they must be displayed in the UI. 

Each KGBB contains information about how the data graphs of its semantic units are instantiated by providing a generic predefined SPARQL/cypher query that allows the application to create a data graph according to a defined graph pattern. The query refers to a set of parameters that the application must provide for the query. In the same way, the corresponding basic unit, simple description unit, complex description unit, dataset unit, or granularity tree unit class provides a predefined SPARAL/cypher query for identifying the data graph belonging to a semantic unit of that type and, especially in case of basic unit KGBBs, one editing query for each node or relation in the data graph that can be edited by a user. Furthermore, KGBBs specify input-control information for possible user input.  

Each KGBB also provides information on how to translate the machine-actionable subgraphs that instantiate the KGBB into a data representation that is human-readable. A given KGBB can provide more than one such data representation (e.g., one for a smartphone app and one for an internet browser). 


