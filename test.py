def resolveValue(input_node, data_item_type, data_item_node, object_node, input_nodes_dict):


    i = 1
    # build the label based on information from various key-value pairs of the representation node
    while i < 40:

        key = "{a}_value{i}".format(a=data_item_type, i=i)

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
                    while m < 40:
                        if input_nodes_dict[m]["input_source"] == target_node:
                            label = input_nodes_dict[m].get(target_key)
                            input_node[key] = label
                            m += 1
                        else:
                            m += 1
        except:
            pass

        i += 1


    return input_node






input_node = {'entry_label1': 'Entry Metadata:', 'entry_label2': '       creator:', 'entry_label3': ';     created on:', 'entry_label4': ';     last updated on:', 'KGBB_URI': 'ScholarlyPublicationEntryKGBB_URI', 'type': 'ContainerRepresentationKGBBElement_URI', 'URI': 'MetadataEntryContainerKGBBElement_URI', 'entry_value3': 'node$_$last_updated_on', 'entry_value2': 'node$_$created_on', 'entry_value1': 'node$_$created_by', 'node_type': 'container', 'name': 'metadata entry container element', 'data_view_name': 'orkg', 'data_view_information': 'true', 'category': 'NamedIndividual', 'order': 1}

data_item_type = "entry"

data_item_node = {'entry_doi': 'Entry_DOI', 'dataset_doi': ['NULL'], 'research_simpleDescriptionUnit_URI': ['NULL'], 'current_version': 'true', 'KGBB_URI': 'ScholarlyPublicationEntryKGBB_URI', 'type': 'scholarly_publication_entry_URI', 'created_by': 'ORKGuserORCID', 'URI': '1570871f-ee66-444f-a9c9-d8d987d56564', 'entry_URI': '1570871f-ee66-444f-a9c9-d8d987d56564', 'versioned_doi': ['NULL'], 'contributed_by': ['ORKGuserORCID'], 'node_type': 'entry', 'created_on': "2021, 4, 12, 10, 8, 52.669", 'object_URI': '30f7bc19-8bd6-48b3-9fbe-505aede6c4c5', 'publication_doi': '10.1145/3331166', 'name': 'Publication', 'publication_title': 'Industry-scale knowledge graphs', 'last_updated_on': "2021, 4, 12, 10, 8, 52.669", 'created_with': 'ORKG', 'category': 'NamedIndividual', 'order_max': 5}

object_node = {'publication_publisher': 'Association for Computing Machinery (ACM)', 'current_version': 'true', 'type': 'http://orkg???????2', 'URI': '30f7bc19-8bd6-48b3-9fbe-505aede6c4c5', 'entry_URI': '1570871f-ee66-444f-a9c9-d8d987d56564', 'data_node_type': 'entry_object', 'publication_year': 2019, 'publication_journal': 'Communications of the ACM', 'publication_authors': 'Natasha Noy, Yuqing Gao, Anshu Jain, Anant Narayanan, Alan Patterson, Jamie Taylor', 'publication_doi': '10.1145/3331166', 'name': 'Industry-scale knowledge graphs', 'category': 'NamedIndividual'}

input_nodes_dict =  None



output = resolveValue(input_node, data_item_type, data_item_node, object_node, input_nodes_dict)



print (output)
