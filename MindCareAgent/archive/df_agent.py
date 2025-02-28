from dotenv import load_dotenv
import os
import pandas as pd

from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

# Load environment variables
load_dotenv('.env')
api_key = os.getenv("GROQ_API_KEY")

# Load dataset
df = pd.read_csv('data/anxiety_attack_dataset.csv')

# Setup Groq's LLM
llm = ChatGroq(
    temperature=0, 
    groq_api_key=api_key, 
    model_name="gemma2-9b-it"
)

# Setup Pandas DataFrame Agent with Groq
agent = create_pandas_dataframe_agent(
    llm,  # Use the ChatGroq model here
    df,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    allow_dangerous_code=True
)

# Test the agent
agent.invoke('Quantas colunas tem no dataset?')