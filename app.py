from flask import Flask, jsonify, request
from flask_cors import CORS

import pandas as pd
from langchain import LLMChain, Cohere
from langchain.agents import create_csv_agent
from langchain.llms import Cohere
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain.agents import create_pandas_dataframe_agent

# OPENAI_API_KEY = "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"
COHERE_API_KEY = "CggzsdnWH6QXtnGJvKYe4IRZyGZ8UkTSykpmAigW"


def chat_with_categorized_data(prompt: str):
    agent = create_csv_agent(
        Cohere(model="command-xlarge-nightly", cohere_api_key=COHERE_API_KEY),
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
    # agent = create_pandas_dataframe_agent(
    #     ChatOpenAI(
    #         temperature=0, model="gpt-3.5-turbo-0613", openai_api_key=OPENAI_API_KEY
    #     ),
    #     filtered_df,
    #     verbose=True,
    #     agent_type=AgentType.OPENAI_FUNCTIONS,
    # )

    co = Cohere(auth_token=COHERE_API_KEY)
    agent = create_pandas_dataframe_agent(
        llm=LLMChain(llm=co),
        dataframe=filtered_df,
        agent_type="cohere-functions",
        verbose=True,
    )

    response = agent.run(
        "Give a convincing answer to the user in such a way assuming that this is the latest trend as well as of the future."
    )
    return response


app = Flask(__name__)
CORS(app, origins="*")


# Base route
@app.route("/", methods=["GET"])
def keep_alive():
    return {"response": "Server is running..."}


# Used to fetch the chat output make users understand the latest trends based on chat prompts
@app.route("/api/getChat", methods=["GET"])
def get_chat_output():
    # try:
    prompt = request.args.get("prompt")
    if len(prompt) < 0:
        return {"response": "Please provide a valid prompt."}

    data = pd.read_csv("./data.csv")
    data.drop(["asin", "id"], axis=1, inplace=True)
    data["category"] = data["purl"].apply(lambda x: x.split("/")[-5])

    ans = chat_with_categorized_data(prompt)

    filtered_df = filter_dataframe_by_category(data, ans)
    filtered_df.drop(["img", "purl"], axis=1, inplace=True)

    final_response = chat_with_filtered_data(filtered_df, ans)

    return final_response
    # except:
    #     return {"Facing errors, please try again..."}


# Used to fetch the closest product recommendations based on previous purchase history for a particular buyer
@app.route("/api/getRecommendations", methods=["GET"])
def get_close_recommendations():
    # try:
    data = pd.read_csv("./data.csv")
    # except:
    #     return {"Facing errors, please try again..."}


if __name__ == "__main__":
    app.run(port=5001, debug=True)
