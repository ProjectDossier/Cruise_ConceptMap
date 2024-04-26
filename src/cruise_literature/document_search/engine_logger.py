import logging
from typing import Optional

import wikipedia


def get_query_type(source: Optional[str]) -> str:
    """
    Parse value of source GET param.
    Currently, if the person clicked search button it is filled with string "source".
    - reformulation: if search bar not on a main page
    - taxonomy: if clicked on taxonomy concepts
    - keywords: if clicked on keywords from papers
    Otherwise, if source is None, returns "other".
    """
    if not source:
        return "other"
    else:
        return source


def get_wiki_logger(matched_wiki_page: Optional[wikipedia.WikipediaPage]) -> str:
    """
    Parses values of matched wiki page url, in case it was found to the query.
    Otherwise, returns string None
    """
    if matched_wiki_page:
        return matched_wiki_page.url
    else:
        return "None"


class EngineLogger:
    """Simple wrapper for python logger to get a custom user query logger."""

    def __init__(self):
        self._logger = logging.getLogger("user_queries")
        hdlr = logging.FileHandler("../../data/user_queries_Jan11.log", delay=True)
        # hdlr = logging.FileHandler("../../data/user_queries_ayah.log", delay=True)
        formatter = logging.Formatter("%(asctime)s %(message)s")
        hdlr.setFormatter(formatter)
        self._logger.addHandler(hdlr)
        self._logger.setLevel(logging.INFO)

    def log_query(
        self,
        search_query: str,
        query_type: str,
        interface_type: str,
        task_num: str,
        tax_results: dict,
        prefix = None
        #matched_wiki_page: str,
    ):
        """Method responsible for logging user queries along with some metadata."""
        # concepts = "|".join(
        #     f"{k}: {v['concept']['text']}" for k, v in tax_results.items()
        # )
        # # self._logger.info(
        #     "\t%s\t%s\t%s\t%s",
        #     query_type,
        #     # search_time,
        #     search_query,
        #     concepts,
        #     #matched_wiki_page,
        # )
        self._logger.info(f';{query_type}; {search_query}; {interface_type}; {task_num}')

    def log_query2(
        self,
        id: str,
        title:str,
        interface_type: str,
        task_num: str,
   ):
        self._logger.info(f';Click Show More; {id}; {title}; {interface_type}; {task_num};')

    def log_query3(
        self,
        url: str,
        title:str,
        interface_type: str,
        task_num: str,
   ):
        self._logger.info(f';Click title;{url}; {title};{interface_type};{task_num};')
