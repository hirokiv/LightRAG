import os
import json
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, gpt_4o_complete, openai_embed
from os.path import join, dirname
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)



class LightRAGHandler():
    def __init__(self):
        self.WORKING_DIR = os.environ.get("WORKING_DIR")
        rag = LightRAG(
            working_dir=self.WORKING_DIR,
            embedding_func=openai_embed,
            llm_model_func=gpt_4o_mini_complete,
            # graph_storage='Neo4JStorage',
            graph_storage='NetworkXStorage',
            log_level='DEBUG'
        )
        self.rag = rag
        
    # Insert text
    def text_insert(self, filepath, timestamp=None):
        with open(filepath, "r", encoding="utf-8") as f:
            self.rag.insert(f.read(), timestamp=datetime.now())
    
    def rag_query(self, query="What are the top themes in this story?",  mode='naive', save_json=True):
        content = self.rag.query(
            query,
            param=QueryParam(mode=mode)
            )

        if save_json:
            self._stuck_json(mode, query, content)
        
        return content

    def _stuck_json(self, mode, query, content):
        new_data = [
                { "mode": mode, "query": query,"content": content}
                ]

        # Overwrite JSON file
        json_file = join(self.WORKING_DIR, "query_data.json")

        if os.path.exists(json_file):
            with open(json_file, "r") as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = []  # Handle empty or invalid JSON
        else:
            existing_data = []
        
        # Step 2: Ensure it's a list
        if not isinstance(existing_data, list):
            existing_data = []
        
        # Step 3: Check if the new entry already exists
        if new_data not in existing_data:
            existing_data.append(new_data)  # Append only if unique
        
            # Step 4: Save the updated data back to JSON
            with open(json_file, "w") as file:
                json.dump(existing_data, file, indent=4)
        
            print("New data added to JSON!")
        else:
            print("Duplicate data. Not added.")
           

if __name__ == '__main__':

    # filepath = "./docs/chord_progress/var1.txt"
    filepath = "./docs/chord_progress/var1.txt"

    handler = LightRAGHandler()
    handler.text_insert(filepath)


    # # Perform naive search
    # mode="naive"
    # # Perform local search
    # mode="local"
    # # Perform global search
    # mode="global"
    # # Perform hybrid search
    # mode="hybrid"
    # # Mix mode Integrates knowledge graph and vector retrieval.
    # mode="mix"

    mode_list = ["naive", "hybrid", "mix", "local" , "global"]
 
    for mode in mode_list:
        query = 'What is written about Mozart'
        content = handler.rag_query(query=query, mode=mode)
        print("=== mode: {} ===".format(mode ) )
        print(content)
    
    
