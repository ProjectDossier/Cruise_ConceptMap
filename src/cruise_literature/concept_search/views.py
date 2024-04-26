from django.http import JsonResponse

from .taxonomy import TaxonomyRDFCSO, TaxonomyRDFCCS

taxonomies = {
    "CSO": TaxonomyRDFCSO("../../data/external/"),
}


def search_concepts(request, query):
    """
    Search concepts relevant to the query inside taxonomies
    """
    if request.method == "GET":
        tax_results = []
        for name, taxonomy in taxonomies.items():
            concept = taxonomy.search(query=query)
            tax_results.append({
                "name": name,
                "concept": concept.to_dict(),
                "subparents": [
                    item.to_dict()
                    for sublist in concept.parents
                    for item in sublist.parents],
                "subchildren": [
                    item.to_dict()
                    for sublist in concept.children
                    for item in sublist.children],
                "parents": [x.to_dict() for x in concept.parents],
                "children": [x.to_dict() for x in concept.children], })



        return JsonResponse(tax_results, safe=False)

        # tax_results = []
        # for name, taxonomy in taxonomies.items():
        #     concept = taxonomy.search(query=query)
        #     root_concept = [{'key': concept.text, 'color': 'lavgrad'}]
        #     children = [{'key': children.text, 'dir': 'left', 'parent': concept.text, 'color': 'bluegrad'} for children in
        #                 concept.children]
        #     parents = [{'key': parent.text, 'dir': 'right', 'parent': concept.text, 'color': 'bluegrad'} for parent in
        #                concept.parents]
        #
        #     subparents = []
        #     subchildren = []
        #     for parent in parents[:5]:
        #         concept = taxonomy.search(parent['key'])
        #         parents_of_parents = subparents + [{'key': node.text, 'parent': concept.text, 'color': 'bluegrad'} for node
        #                                            in concept.parents]
        #
        #     for child in children[:5]:
        #         concept = taxonomy.search(child['key'])
        #         subchildren = children_of_childrens + [{'key': node.text, 'parent': concept.text, 'color': 'bluegrad'} for
        #                                                node in concept.children]
        #
        # tax_results[name] = root_concept + children[:5] + parents[:5] + subparents[:5] + subchildren[:5]