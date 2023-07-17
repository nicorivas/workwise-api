from typing import Union
from mangum import Mangum
from mimesis.agent.agent import Agent
#import mimesis

from fastapi import FastAPI
import duckdb as db

con = db.connect(database='db/dev.duckdb', read_only=False)

BACKEND = "dev"

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/agents/")
def get_agents():
    
    if BACKEND == "dev":
        con.execute("SELECT * FROM Agent")

    return con.df().to_dict(orient="index")

@app.post("/agents/")
async def create_agent(agent: Agent):

    if BACKEND == "dev":
        con.execute(f"INSERT INTO Agent VALUES ('{agent.name}','{agent.definition}')")

    return con.fetchall()

@app.put("/agents/{agent_id}/do/{action_id}")
def agent_do(agent_id: str, action_id: str, params: dict):
    
    # Get agent
    if BACKEND == "dev":
        con.execute(f"SELECT * FROM Agent WHERE name = '{agent_id}' LIMIT 1")
    agent_json = con.df().to_dict(orient="index")[0]

    # Create agent
    agent = Agent(**agent_json)

    # Do the action
    if action_id == "answer":
        from mimesis.actions.reply import Reply
        action_reply = Reply()
        action_reply.prompt = params["prompt"]
        effect = agent.do(action_reply)

    return effect

handler = Mangum(app)