from jinja2 import Environment, PackageLoader, FileSystemLoader
from rich import print
from rich.text import Text
from rich.console import Console
from pathlib import Path
from gensim import corpora, models, similarities
from .helpers import escape_json
from .helpers import convert_to_yaml
from .helpers import find_keys

import jieba
import openai
import sys
import json
import os


class aisnippet:
    def __init__(self, **kwargs):
        """initiate object with provided options."""
        self.verbose = kwargs.get("verbose")
        self.outputfile = kwargs.get("outputfile")
        self.playbook = kwargs.get("playbook")
        self.opts = kwargs
        self.dirpath = os.getcwd()
        self.snippets = self.__load_snippets__(os.path.join(os.path.dirname(__file__),"snippets.json"))
        self.analyzed_snippets = [
            jieba.lcut(snippet.lower()) for snippet in self.snippets
        ]
        self.dictionary = corpora.Dictionary(self.analyzed_snippets)
        self.corpus = [
            self.dictionary.doc2bow(snippet) for snippet in self.analyzed_snippets
        ]
        self.tfidf = models.TfidfModel(self.corpus)
        self.feature_cnt = len(self.dictionary.token2id)

    def __load_snippets__(self, file):
        with open(file) as json_file:
            return json.load(json_file)

    def __find_similar__(self, text):
        kw_vector = self.dictionary.doc2bow(jieba.lcut(text))
        index = similarities.SparseMatrixSimilarity(
            self.tfidf[self.corpus], num_features=self.feature_cnt
        )
        sim = list(index[self.tfidf[kw_vector]])
        index = sim.index(max(sim))
        return self.snippets[list(self.snippets)[index]]

    def generate_task(self, text):
        """
        Render The snippet
        """
        snippet = self.__find_similar__(text)
        if self.verbose:
            print(snippet)
        openai.api_key = os.getenv("OPENAI_KEY")
        system_message = (
            "You are an Ansible expert. Use ansible FQCN. No comment. Json:"
        )
        system_user = (
            "You have to generate an ansible task with name %s using all the options of the provided template #template 1 %s. No comment. json:"
            % (text.capitalize(), snippet)
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=[
                {
                    "role": "system",
                    "content": system_message,
                },
                {"role": "user", "content": system_user},
            ],
            temperature=0,
        )
        result = {}
        chatgpt_repsonse = json.loads(
            escape_json(response["choices"][0]["message"]["content"])
        )
        if "tasks" in chatgpt_repsonse:
            result = chatgpt_repsonse["tasks"]
        else:
            result = chatgpt_repsonse
        if self.verbose:
            print(convert_to_yaml(result))
        if type(result) is list:
            return result[0]
        else:
            return result

    def generate_tasks(self, tasks):
        output_tasks = []
        for d in tasks:
            if "task" in d:
                result = self.generate_task(d["task"])
                if "register" in d:
                    result["register"] = d["register"]
                output_tasks.append(result)

            else:
                if "block" in d:
                    block = {}
                    if "name" in d:
                        block["name"] = d["name"]
                    if "when" in d:
                        block["when"] = d["when"]
                    block["block"] = self.generate_tasks(d["block"])
                if "rescue" in d:
                    block["rescue"] = self.generate_tasks(d["rescue"])
                if "always" in d:
                    block["always"] = self.generate_tasks(d["always"])
                output_tasks.append(block)

        return output_tasks
