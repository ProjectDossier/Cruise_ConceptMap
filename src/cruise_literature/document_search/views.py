import time
from datetime import datetime
from django.http import HttpResponseBadRequest, JsonResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from concept_search.taxonomy import TaxonomyRDFCSO
from concept_search.concept_rate import ConceptRate
from concept_search.concept_classification import CSOClassification
from django.template.defaulttags import register
from django.shortcuts import redirect
from .search_documents import search, paginate_results
from .search_wikipedia import search_wikipedia
from django.urls import reverse
from .engine_logger import EngineLogger, get_query_type
import logging

engine_logger = EngineLogger()


# Taxonomy instantiation
taxonomies = {
    "CSO": TaxonomyRDFCSO("../../data/external/"),
    #"CCS": TaxonomyRDFCCS("../../data/external/"),
    #"Wikipedia": TaxonomyRDFCCS(
    #   "../../data/external/",
    #   filename="wikipedia_taxonomy.xml",
    #   taxonomy_name="wikipedia",
    #),
}

concept_rate = ConceptRate()
cso_concept_clasifier = CSOClassification()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def keywords_threshold(keyword_score):
    if keyword_score > 0.95:
        return 'is-success'
    elif 0.7 < keyword_score <= 0.95:
        return 'is-warning'
    elif 0 < keyword_score <= 0.7:
        return 'is-danger'
    else:
        return ''

# Without Concept Map: True else put it false
without = False
    #request.GET.get("search_check")
# Task Opinion Mining True else put it false
task = False

def linkClick(request):
    if without:
        interface_type = "without-Concept"
    else:
        interface_type = "with-concept"
    if task:
        task_num = "Opinion-Mining"
    else:
        task_num = "Pattern_Recognition"
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'GET':
            title = request.GET.get("title", "")
            id = request.GET.get("id", "")
            engine_logger.log_query3(
                url=id,
                title=title,
                interface_type=interface_type,
                task_num=task_num,
            )
            return JsonResponse({'url': id, 'title': title})
        return JsonResponse({'status': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')


def search_results_show_more(request):
    if without:
        interface_type = "without-Concept"
    else:
        interface_type = "with-concept"
    if task:
        task_num = "Opinion-Mining"
    else:
        task_num = "Pattern_Recognition"
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'GET':
            _id = request.GET.get("id", "")
            title = request.GET.get("title", "")
            engine_logger.log_query2(
                id=_id,
                title=title,
                interface_type=interface_type,
                task_num=task_num,
            )

            return JsonResponse({'id': _id, 'title': title})
        return JsonResponse({'status': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')


def search_results(request):
    all_CSO_keywords_set = set()
    all_CSO_keywords_list = []
    """
    Search results page
    """
    if request.method == "POST":
        key = request.POST.get("key", "")
        search_query = request.GET.get("key", None)
        return redirect(reverse("search_results_post", args=[key]))


    if request.method == "GET":
        search_query = request.GET.get("search_query", None)


            #request.GET.get("search_check2")
        if without:
            interface_type = "without-Concept"
        else:
            interface_type = "with-concept"
        if task:
            task_num = "Opinion-Mining"
        else:
            task_num = "Pattern_Recognition"
        query_type = get_query_type(source=request.GET.get("source", None))
        search_with_taxonomy = request.GET.get("search_type", True)

        if not search_query.strip():
            return HttpResponseRedirect("index")

        s_time = time.time()

        index_name = "papers"
        top_k = 10

        search_result = search(query=search_query, index=index_name, top_k=top_k)
        shown_CSO_keywords = []
        #Combine all keywords of the 10 results

        for item in search_result:
            all_CSO_keywords_set.update(item.CSO_keywords2)

        all_CSO_keywords_list = list(all_CSO_keywords_set)
        #print("all_CSO_keywords_list", all_CSO_keywords_list)
        #search_time = time.time() - s_time
        #print(len(all_CSO_keywords_list))
        search_result_list, paginator = paginate_results(
            search_result=search_result, page=request.GET.get("page", 1)
        )

        if not search_with_taxonomy and query_type in [
            "main_search",
            "reformulate_search",
        ]:
            # message = 'qyery_type,+' + query_type + search_query
            # logging.info(message)

            # # TODO: after document keyword click it will always use taxonomy
            # engine_logger.log_query(
            #     search_query=search_query,
            #     query_type=query_type,
            #     search_time=search_time,
            #     tax_results={},
            #     #matched_wiki_page=get_wiki_logger(matched_wiki_page),
            # )

            context = {
                "search_result_list": search_result_list,
                # "matched_wiki_page": matched_wiki_page,
                # "matched_wiki_page" : [],
                "unique_searches": len(search_result),
                # "search_time": f"{search_time:.2f}",
                "search_query": search_query,
                "search_type": "",
                "paginator": paginator,
            }
            return render(
                request=request,
                template_name="interfaces/plain_search.html",
                context=context,
            )
        #Prepare for double tree
        tax_results = {}
        final_tax_results = {}
        parents_of_parents = []
        children_of_childrens = []

        for name, taxonomy in taxonomies.items():
            #concept = taxonomy.search(query=search_query)
            #s_time = time.time()
            concept = taxonomy.search(query=search_query, all_CSO_keywords_list= all_CSO_keywords_list, depth=2)
            #print(time.time() -  s_time )
            s_time = time.time()
            root_concept = [{'key': concept.text,  'color': 'lavgrad'}]
            #print(len(concept.children))
            #print(len(concept.parents))

            ############____Children
            first_childrens = [ {'key': children.text, 'dir': 'left', 'parent': concept.text, 'color': 'bluegrad3'} for children in concept.children if children.text in all_CSO_keywords_list]

            if len(first_childrens)>0:

                for child in concept.children:
                    children_of_childrens = children_of_childrens + [{'key': node.text, 'parent': child.text, 'color': 'bluegrad3'} for node in child.children if node.text in all_CSO_keywords_list]

            else:
                first_childrens = [{'key': children.text, 'dir': 'left', 'parent': concept.text, 'color': 'bluegrad3'}
                                   for children in concept.children[:5]]
                for child in concept.children:
                    children_of_childrens = children_of_childrens + [
                        {'key': node.text, 'parent': child.text, 'color': 'bluegrad3'} for node in child.children[:5]]



            ############____Parents
            first_parents = [{'key': parent.text, 'dir': 'right', 'parent': concept.text, 'color': 'bluegrad2'} for parent in concept.parents ]
            if len(first_parents) > 0:
                for parent in concept.parents:
                    parents_of_parents = parents_of_parents + [
                        {'key': node.text, 'parent': parent.text, 'color': 'bluegrad2'} for node in
                        parent.parents[:5]]


            # if len(parents_of_parents) == 0 and len(parent.parents) > 0:
            #     parents_of_parents = parents_of_parents + [
            #         {'key': node.text, 'parent': parent.text, 'color': 'bluegrad2'} for node in
            #         parent.parents]

            tax_results[name] = root_concept + first_childrens + first_parents + parents_of_parents + children_of_childrens


        #end foor loop
        #print(time.time() - s_time)
        #s_time = time.time()
        #Bring wikipedia definitions
        for key, nodeList in tax_results.items():
            for node in nodeList:
                shown_CSO_keywords.append(node['key'])
                matched_wiki_page = search_wikipedia(query=node['key'])
                if matched_wiki_page:
                    matched_wiki_page.snippet = matched_wiki_page.snippet.replace('\n', '')
                    matched_wiki_page.snippet = matched_wiki_page.snippet.replace('\t', '')
                    node['snippet'] = f"{matched_wiki_page.snippet[:200]}..."
                else:
                    node['snippet'] = "No definition available..."
        #print("shown_CSO_keywords", shown_CSO_keywords)

        source_taxonomy = request.GET.get("source_taxonomy", None)
        if not source_taxonomy:
            source_taxonomy = list(taxonomies.keys())[0]


        # message= 'qyery_type,+'+ query_type + search_query
        # logging.info(message)
        #
        search_time = time.time() - s_time
        # # TODO: after document keyword click it will always use taxonomy
        engine_logger.log_query(
            search_query=search_query,
            query_type=query_type,
            interface_type=interface_type,
            task_num=task_num,
            tax_results=tax_results,

            # matched_wiki_page=get_wiki_logger(matched_wiki_page),
        )
        context = {
            "search_result_list": search_result_list,
            # "matched_wiki_page": matched_wiki_page,
            #"matched_wiki_page": [],
            "unique_searches": len(search_result),
            "search_time": f"{search_time:.2f}",
            "search_query": search_query,
            "tax_results": tax_results,
            "shown_CSO_keywords": shown_CSO_keywords,
            "search_type": "checked",
            "default_taxonomy": source_taxonomy,
            "paginator": paginator,
            "without": without,
            "task": task,
        }
        # assign value of default taxonomy based on selected javascript box...
        return render(
            request=request,
            template_name="interfaces/search_with_taxonomy.html",
            context=context,
        )
        #print(time.time() -  s_time )

#
# def search_results_v2(request):
#     pass
#
#  def common():
#      pass