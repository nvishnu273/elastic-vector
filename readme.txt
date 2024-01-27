OBJECTIVE OF THIS APPLICATION
Our objective was to infuse CookBot with RAG (Elastic Basic Search), ELSER (Similarity vector search), and RRF (Ranking) technologies

TO RUN THIS APPLICATION DO THIS
1. streamlit run main.py 
2. It gives you recipes if you give main ingredient In the query for main.py change the main ingredient currently hardcoded

In the context of our recipe retrieval task, our goal is to maximize the relevance of the returned recipes based on a user’s query. We will utilize a combination of classic full-text search (via BM25), semantic search (with ELSER), and a robust rank fusion method (RRF). 

TODO: Add inputs for the recipes that you are looking and that must not incldude

Link to the chapter: https://github.com/PacktPublishing/Vector-Search-for-Practitioners-with-Elastic
https://cloud.elastic.co/home

install followig:
pip install openai streamlit elasticsearch requests`

kNN Search
----------

Elastic provides these 4 similarity

CosineSimilarity: Calculates cosine similarity
dotProduct: Calculates the dot product
l1norm: Calculates the L1 distance
l2norm: Calculates the L2 distance
doc[<field>].vectorValue: Returns a vector’s value as an array of floats
doc[<field>].magnitude: Returns a vector’s magnitude

The first 4 is recommended.

As a rule of thumb, if the number of documents after filtering is under 10,000 documents, then not indexing and using one of the similarity functions should give good performance.

to be able to use kNN search, you need to modify the mapping so that the dense vectors are indexed, as follows

Note that you also need to set the similarity function. The three options for the similarity are l2_norm, dot_product, and cosine. We recommend, when possible, to use dot_product for vector search in production. 

Model Management (Deploy else model 2)
----------------
POST _ml/trained_models/.elser_model_2/deployment/_start
After you import the model and vocabulary, you can use Kibana to view and manage their deployment across your cluster under Machine Learning > Model Management.


ELser Pipeline Setup v1
-----------------------
PUT _ingest/pipeline/elser-v1-recipes
{
  "processors": [
    {
      "inference": {
        "model_id": ".elser_model_1",
        "target_field": "ml", 
        "field_map": {
          "ingredient": "text_field"
        },
        "inference_config": {
          "text_expansion": {
            "results_field": "tokens"
          }
        }
      }
    }
  ]
}

PUT _ingest/pipeline/elser-v2-recipes
{
  "processors": [
    {
      "inference": {
        "model_id": ".elser_model_2",
        "target_field": "ml", 
        "field_map": {
          "ingredient": "text_field"
        },
        "inference_config": {
          "text_expansion": {
            "results_field": "tokens"
          }
        }
      }
    }
  ]
}

-----
sample queries


This query includes two types of search. The first uses a classic Elasticsearch Boolean search to find recipes that contain both carrot and beef as ingredients, excluding those with onion. This traditional approach ensures that the most basic constraints of the user are met.

The second sub_search employs ELSER to semantically expand the query I want a recipe from the US west coast with beef. ELSER interprets this request based on its understanding of language, enabling the system to match documents that may not contain the exact phrase but are contextually related. This allows the system to factor in the more nuanced preferences of the user.

The query then employs RRF to combine the results of the two sub_searches. The window_size parameter is set to 50, meaning the top 50 results from each sub-search are considered. The rank_constant parameter, set to 20, guides the RRF algorithm to fuse the scores from the two sub_searches.

Thus, this query exemplifies the effective combination of BM25, ELSER, and RRF. Exploiting the strengths of each allows CookBot to move beyond simple keyword matches and provide more contextually relevant recipes, improving the user experience and increasing the system’s overall utility.

-----
GET recipes/_search
{
  "_source": { "includes": [ "name", "ingredient" ] },
  "sub_searches": [
    {
      "query": {
        "bool": {
          "must": { "match": {
"ingredient": "carrot beef" } },
          "must_not": { "match": { "ingredient": "onion" }
          }
        }
      }
    },
    {
      "query": {
        "text_expansion": { "ml.tokens": {
            "model_id": ".elser_model_2",
            "model_text": "I want a recipe from the US west coast with beef"
          }
        }
      }
    }
  ],
  "rank": {
    "rrf": { "window_size": 50, "rank_constant": 20 }
  }
}

DevTools
---------
https://rag-search-using-elastic.kb.us-central1.gcp.cloud.es.io:9243/app/dev_tools#/console