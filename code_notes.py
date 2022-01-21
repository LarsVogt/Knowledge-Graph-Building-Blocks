----------------------- BREAK & CONTINUE ------------------

for i in range(100):
    if i == 3:
        break

0 1 2

for i in range(100):
    if i == 2:
        continue
0 1 3 4

----------------------------- LISTS -----------------------
über alle elemente einer liste m :       for i in m:
liste m um value x erweitern:           m.append(x)
if list m is empty continue:            if not m:
delete first item in list m:            m.pop(0)
add item x in first position
of list m:                              m.insert(0, x)

----------------------------- DICTS -----------------------

nur key-value hinzufügen, wenn key
noch nicht in dict m vorhanden:          if key not in m:
                                            m[key] = value

über alle keys in einem dict m:           for key in m:
über alle values in einem dict m:         for value in m.values():
über alle key-value pairs in dict m:      for key, value in m.items():
delete key-value from dict m:             m.pop('key')
ein key-value pair zu dict m hinzufügen
oder existierenden key den value updaten:   m[key] = value
1. key in m:                                list(m.keys())[0]

checken, ob key in dict m:                 if key in m:  # wenn drin, dann true

ein key-value pair an erster position
von dict m hinzufügen:
                        to_be_added_key_value = {key: value}
                        to_be_added_key_value.update(m)
                        m = to_be_added_key_value

identify key by substring, with res as a dictionary
 with all key-value hits:
                        dictA:{'all': 1, 'good': 2, 'food': 3, 'sport': 4}
                        search_key = 'ood'
                        res = dict(filter(lambda item: search_key in item[0], dictA.items()))





------------------------ LIST OF DICTS ------------------------------------

find dictionary n in a list m of dictionaries by a particular key-value pair:

next(item for item in m if item[key] == value)

Jinja2:
{% for n in m %}
    {% for key, value in n.items() %}

    {% endfor %}
{% endfor %}


------------------- STRING REPRESENTATION OF DICT TO DICT ------------------

transform then string representation dict_string of dictionary dict to dictionary:

dict = ast.literal_eval(dict_string)


---------------------- STRING TRENNEN BEI BEST CHARACTER -------------------

variabl.partition(" ")[2] -> trennt den string bei ch " " mit [0]=alles vorher   und [2]=alles dahinter


---------------------- NEO4J DATETIME IN ISOFORMAT ÄNDERN -------------------

entry_object['created_on'] = entry_object['created_on'].isoformat()






------------------- AJAX POST EXAMPLE ----------------------
function AjaxCall (node_data) {
console.log(node_data)
$.ajax({
type: 'POST',
url: '/simpleDescriptionUnit',
data: JSON.stringify({node_data: node_data}),
success : function(text)
{
 console.log("test");
}
})
.done(function( data ) {
console.log(data)
$('.simpleDescriptionUnit_display').replaceWith($('.simpleDescriptionUnit_display'), data);
})
};
---------------------------------------------------------------

















----------------------------- TOOLTIP ---------------------

<!DOCTYPE html>
<html>
<style>
.tooltip {
  position: relative;
  display: inline-block;
  border-bottom: 1px dotted black;
}

.tooltip .tooltiptext {
  visibility: hidden;
  width: 120px;
  background-color: black;
  color: #fff;
  text-align: center;
  border-radius: 6px;
  padding: 5px 0;

  /* Position the tooltip */
  position: absolute;
  z-index: 1;
}

.tooltip:hover .tooltiptext {
  visibility: visible;
}
</style>
<body style="text-align:center;">

<p>Move the mouse over the text below:</p>

<div class="tooltip">Hover over me
  <span class="tooltiptext">Tooltip text</span>
</div>

<p>Note that the position of the tooltip text isn't very good. Go back to the tutorial and continue reading on how to position the tooltip in a desirable way.</p>

</body>
</html>







------------------------------ FÜR DARSTELLUNG VON BASIC_UNITS -----------

INCLUDING HTML IN HTML (JavaScript):
if you have to include a lot of files. Use this JS code:

$(function () {
  var includes = $('[data-include]')
  $.each(includes, function () {
    var file = 'views/' + $(this).data('include')
    $(this).load(file)
  })
})


And then to include something in the html:

<div data-include="header.html"></div>
<div data-include="footer.html"></div>

Which would include the file views/header.html and views/footer.html.



-----------------------------------------------------------------------
REQUIRED DATA STRUCTURES

ALLGEMEIN

    1) navi-baum info
    2) Title Zeile


RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
            CHANGE LOG FÜR SIMPLE_DESCRIPTION_UNIT & BASIC_UNITS NICHT VERGESSEN!
RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR

RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
        SEARCH SIMPLE_DESCRIPTION_UNIT with ONTOLOGY TERM/ENTRY/SIMPLE_DESCRIPTION_UNIT/BASIC_UNIT -> ENTRY/SIMPLE_DESCRIPTION_UNIT
                        LIST SIMPLE_DESCRIPTION_UNITS (ENTRIES,SIMPLE_DESCRIPTION_UNITS, BASIC_UNITS,KGBBs
                        all BY TYPE) AUCH NICHT VERGESSEN!
RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR




ENTRY

    [0] entry-metadata      -> entry_view_dict
    [1] publication title   -> entry_view_dict
    [2-x] key-value pairs   -> entry_view_dict
    allowed add simpleDescriptionUnits       -> add_simpleDescriptionUnits_dict

    entry_view_tree_dict:
        {order[integer]: {entry_label1:string, entry_value1:string, entry_label_tooltip1:string, entry_value_tooltip1:string, editable:Boolean, include_html:string, div_class:string, placeholder_text:string, required:Boolean, input_control:{}, quantity:"1/m", sub_view_tree:{}

        add/link to other data-item:{}}}





    add_simpleDescriptionUnits_dict:
        {order[integer]: {kgbb_uri:uri, required:Boolean, quantity:"1/m", data_item_type_label:string}, }
        1) get all simpleDescriptionUnit element nodes über :HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT



SIMPLE_DESCRIPTION_UNIT





BASIC_UNIT



ON REPRESENTATION


ON CONTAINER
    entry_label1
    entry_value1
    entry_label_tooltip1
    entry_value_tooltip1
    placeholder_text
    div_class

INPUT INFO


DATA NODE


DATA ITEM NODE (ENTRY/SIMPLE_DESCRIPTION_UNIT/BASIC_UNIT)




input_node = {'entry_label1': 'Entry Metadata:', 'entry_label2': '       creator:', 'entry_label3': ';     created on:', 'entry_label4': ';     last updated on:', 'KGBB_URI': 'ScholarlyPublicationEntryKGBB_URI', 'type': 'ContainerRepresentationKGBBElement_URI', 'URI': 'MetadataEntryContainerKGBBElement_URI', 'entry_value3': 'node$_$last_updated_on', 'entry_value2': 'node$_$created_on', 'entry_value1': 'node$_$creator', 'node_type': 'container', 'name': 'metadata entry container element', 'data_view_name': 'orkg', 'data_view_information': 'true', 'category': 'NamedIndividual', 'order': 1}

data_item_type = "entry"

data_item_node = {'entry_doi': 'Entry_DOI', 'dataset_doi': ['NULL'], 'research_topic_URI': ['NULL'], 'current_version': 'true', 'KGBB_URI': 'ScholarlyPublicationEntryKGBB_URI', 'type': 'scholarly_publication_entry_URI', 'created_by': 'ORKGuserORCID', 'URI': '1570871f-ee66-444f-a9c9-d8d987d56564', 'entry_URI': '1570871f-ee66-444f-a9c9-d8d987d56564', 'versioned_doi': ['NULL'], 'contributed_by': ['ORKGuserORCID'], 'node_type': 'entry', 'created_on': "2021, 4, 12, 10, 8, 52.669", 'object_URI': '30f7bc19-8bd6-48b3-9fbe-505aede6c4c5', 'publication_doi': '10.1145/3331166', 'name': 'Publication', 'publication_title': 'Industry-scale knowledge graphs', 'last_updated_on': "2021, 4, 12, 10, 8, 52.669", 'created_with': 'ORKG', 'category': 'NamedIndividual', 'order_max': 5}

object_node = {'publication_publisher': 'Association for Computing Machinery (ACM)', 'current_version': 'true', 'type': 'http://orkg???????2', 'URI': '30f7bc19-8bd6-48b3-9fbe-505aede6c4c5', 'entry_URI': '1570871f-ee66-444f-a9c9-d8d987d56564', 'data_node_type': 'entry_object', 'publication_year': 2019, 'publication_journal': 'Communications of the ACM', 'publication_authors': 'Natasha Noy, Yuqing Gao, Anshu Jain, Anant Narayanan, Alan Patterson, Jamie Taylor', 'publication_doi': '10.1145/3331166', 'name': 'Industry-scale knowledge graphs', 'category': 'NamedIndividual'}

input_nodes_dict =  None

resolveValue(input_node, data_item_type, data_item_node, object_node, input_nodes_dict)



!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

NEXT STEPS:

    DONE 1) addBasicUnit function
    DONE 2) BasicUnitRepresentation Class
    DONE 3) adjust addEntry function to check for required simpleDescriptionUnits and basicUnits...
4) addControl function to check whether the parent data item may display the data item to be added and whether only once or multiples





# check for required simpleDescriptionUnits
search_required_simpleDescriptionUnits_query_string = '''OPTIONAL MATCH (n {{URI:"{entry_kgbb_uri}"}})-[:HAS_SIMPLE_DESCRIPTION_UNIT_ELEMENT]->(p)
RETURN p'''.format(entry_kgbb_uri=entry_kgbb_uri)

simpleDescriptionUnits_query = connection.query(search_required_simpleDescriptionUnits_query_string, db='neo4j')
print("-------------------------------------------------------------------------------")
print("--------------------- INITIAL REQUIRED SIMPLE_DESCRIPTION_UNITS QUERY ----------------------------")
print(simpleDescriptionUnits_query)

# check for required basicUnits
search_required_basicUnits_query_string = '''OPTIONAL MATCH (n {{URI:"{entry_kgbb_uri}"}})-[:HAS_BASIC_UNIT_ELEMENT]->(a)
RETURN a'''.format(entry_kgbb_uri=entry_kgbb_uri)

basicUnit_query = connection.query(search_required_basicUnits_query_string, db='neo4j')
print("-------------------------------------------------------------------------------")
print("------------------- INITIAL REQUIRED BASIC_UNITS QUERY -------------------------")
print(basicUnit_query)
