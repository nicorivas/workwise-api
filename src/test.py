from fastapi import FastAPI
import duckdb as db
from mimesis.agent.agent import Agent
import logging

con = db.connect(database='db/dev.duckdb', read_only=False)
agent_schema = Agent.model_json_schema()

def create_table_from_schema(class_name: str, schema: dict):
    # Construct the CREATE TABLE SQL command
    create_table_command = f"CREATE TABLE {class_name} ("

    # iterate over fields
    for field_name, field_dict in schema["properties"].items():
        # DuckDB uses 'VARCHAR' for string data types, so we need to convert 'str' to 'VARCHAR'
        if field_dict.get("type") == 'string':
            field_type_name = 'VARCHAR'
        else:
            logging.warning("Unsupported type")
            continue
        # add field name and type to SQL command
        create_table_command += f"{field_name} {field_type_name}, "

    # remove the last comma and space, add the closing parenthesis
    create_table_command = create_table_command[:-2] + ")"

    return create_table_command

create_table_command = create_table_from_schema("Agent", agent_schema)
con.execute(query=create_table_command)
