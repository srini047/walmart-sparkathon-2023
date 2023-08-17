from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np

import pandas as pd
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain.agents import create_pandas_dataframe_agent
from sklearn.decomposition import TruncatedSVD
from langchain import Cohere
from langchain.llms import Cohere
from scipy.stats import pearsonr
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.agents import Tool
from langchain.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent

OPENAI_API_KEY = "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"
COHERE_API_KEY = "CggzsdnWH6QXtnGJvKYe4IRZyGZ8UkTSykpmAigW"
SERPAPI_API_KEY = "dbc53dd88c7b0957548a81fa162e2d547e03cc19267162a9166e52d4e882f361"


# Function to generate product recommendations
def generate_recommendations(data):
    # Prepare data for recommendation system
    amazon_ratings1 = data.head(10000)
    
    ratings_utility_matrix = amazon_ratings1.pivot_table(values='rating', index='id', columns='name', fill_value=0)
    X = ratings_utility_matrix.T
    
    SVD = TruncatedSVD(n_components=10)
    decomposed_matrix = SVD.fit_transform(X)
    
    # Calculate correlation matrix using Pearson correlation
    correlation_matrix = np.zeros((decomposed_matrix.shape[1], decomposed_matrix.shape[1]))

    for i in range(decomposed_matrix.shape[1]):
        for j in range(decomposed_matrix.shape[1]):
            corr, _ = pearsonr(decomposed_matrix[:, i], decomposed_matrix[:, j])
            correlation_matrix[i, j] = corr
    
    # Load product names for identification
    product_names_df = pd.read_csv("./unique_category.csv")
    i = product_names_df["product_name"].tolist()

    # Prepare recommendation list based on correlations
    product_names = list(X.index)
    product_IDs = [product_names.index(product) for product in i]
    correlation_product_ID = correlation_matrix[product_IDs[-1]]
    Recommend = list(X.index[correlation_product_ID > 0.90])
    
    # Remove items already in the input set
    for item in i:
        if item in Recommend:
            Recommend.remove(item)
    
    recommended_items = Recommend[:20]
    
    return recommended_items

# Define required functions for the routes
def chat_with_categorized_data(prompt: str):
    agent = create_csv_agent(
        OpenAI(temperature=0.7, openai_api_key=OPENAI_API_KEY),
        "./unique_category.csv",
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )

    response = agent.run(
        prompt
        + "If the answer is generic then return: general else return the closest match to the user interaction. I need only the closest match of the category or general as the output and nothing else..."
    )
    return response


def filter_dataframe_by_category(data, input_category):
    if isinstance(input_category, str):
        # If input is a string, filter by that single category
        filtered_df = data[data["category"] == input_category]
    elif isinstance(input_category, list):
        # If input is a list, filter by multiple categories
        filtered_df = data[data["category"].isin(input_category)]
    else:
        raise ValueError("Input must be a string or a list")

    return filtered_df


def chat_with_filtered_data(filtered_df: pd.DataFrame, category: str):
    OPENAI_API_KEY = "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"

    agent = create_pandas_dataframe_agent(
        ChatOpenAI(
            temperature=0, model="gpt-3.5-turbo-0613", openai_api_key=OPENAI_API_KEY
        ),
        filtered_df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
    )

    response = agent.run(
        "Give a convincing answer to the user in such a way assuming that this is the latest trend as well as of the future."
    )
    return response

# Function to generate recommendations
def generate_recommendations(data):
    amazon_ratings1 = data.head(10000)

    ratings_utility_matrix = amazon_ratings1.pivot_table(
        values="rating", index="id", columns="name", fill_value=0
    )
    X = ratings_utility_matrix.T

    SVD = TruncatedSVD(n_components=10)
    decomposed_matrix = SVD.fit_transform(X)

    correlation_matrix = np.corrcoef(decomposed_matrix)

    # Load the product names from a CSV file
    product_names_df = pd.read_csv("./unique_category.csv")
    i = product_names_df["product_name"].tolist()

    product_names = list(X.index)
    product_IDs = [product_names.index(product) for product in i]

    correlation_product_ID = correlation_matrix[
        product_IDs[-1]
    ]  # Using the last product ID from your list

    Recommend = list(X.index[correlation_product_ID > 0.90])

    for item in i:
        if item in Recommend:
            Recommend.remove(item)

    recommended_items = Recommend[:20]

    return recommended_items


# Flask app starts here
app = Flask(__name__)
CORS(app, origins="*")


# Base route
@app.route("/", methods=["GET"])
def keep_alive():
    return {"message": "Server is running..."}


# Used to fetch the chat output make users understand the latest trends based on chat prompts
@app.route("/api/getChat", methods=["GET"])
# def get_chat_output():
# try:
#     prompt = request.args.get("prompt")
#     data = pd.read_csv("./data.csv")
#     data.drop(["asin", "id"], axis=1, inplace=True)
#     data["category"] = data["purl"].apply(lambda x: x.split("/")[-5])

#     ans = chat_with_categorized_data(prompt)

#     filtered_df = filter_dataframe_by_category(data, ans)
#     filtered_df.drop(["img", "purl"], axis=1, inplace=True)

#     final_response = chat_with_filtered_data(filtered_df, ans)

#     return jsonify(final_response)
# except:
#     return jsonify("Facing errors, please try again...")
def get_chat_output():
    try:
        prompt = request.args.get("prompt")
        search = SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)
        tools = [
            Tool(
                name="Current search",
                func=search.run,
                description="useful for when you need to answer questions about current events or the current state of the world",
            ),
        ]
        memory = ConversationBufferMemory(memory_key="chat_history")
        input = prompt + " Answer in no more than 200 words."
        llm = Cohere(cohere_api_key=COHERE_API_KEY, model="command-xlarge-nightly")
        agent_chain = initialize_agent(
            tools,
            llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            # verbose=True,
            memory=memory,
            handle_parsing_errors=True,
        )
        response = agent_chain.run(input=input)
        return {"response": response}

    except:
        return jsonify({"error": "Facing errors, please try again..."})


# Used to fetch the closest product recommendations based on previous purchase history for a particular buyer
@app.route("/api/getRecommendations", methods=["GET"])
def get_close_recommendations():
    try:
        data = pd.read_csv("./data.csv")
        
        # Generate product recommendations
        recommendations = generate_recommendations(data)
        
        return jsonify({"recommendations": recommendations})
    except:
        return jsonify("An error occurred, please try again.")


if __name__ == "__main__":
    app.run(port=5001, debug=True)
