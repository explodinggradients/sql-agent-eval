# SQL Agent

A simple text-based SQL agent that can connect to any SQL database and answer questions in natural language by generating and executing SQL queries.

## Installation

### Prerequisites
- Python 3.7+
- OpenAI API key

### Install from Source (Development)

```bash
git clone https://github.com/your-username/sql-agent-eval.git
cd sql-agent-eval
pip install -e .
```

### Setup OpenAI API Key

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

## Quickstart

```python
import asyncio
from sql_agent.database import SQLDatabase
from sql_agent.agent import SQLAgent

# Connect to your database
db = SQLDatabase("sqlite:///your_database.db")

# Create an agent
agent = SQLAgent(db, "session_1")

# Ask questions in natural language
async def main():
    response = await agent.run("How many customers do we have?")
    print(response)

asyncio.run(main())
```

See [notebooks/example.ipynb](notebooks/example.ipynb) for a complete example.

## Instructions for candidates

1. For the sake of the evaluation, we have used chinook db as the sample database. You can find the data [here](https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db) - treat this like your production database.
2. Your goal is to build an simulation based evaluation system to evaluate the SQLAgent and find common failure modes across various scenarios.
3. Any method that is proposed should take state (here the database) into account. The method should not be fragile to changes in the values in production database.
4. You can modify the SQLAgent code if needed by adding minimal code changes, but the goal is to evaluate the system as is.
5. An ideal outcome from the evaluation would look somewhat like this:

| Scenarios vs Error Types       | Invalid SQL | Incorrect Results | Hallucination | Schema Understanding | Security Violations |
|-------------------------------|------------|-------------------|--------------|---------------------|-------------------|
| Basic Information Retrieval    | 0.2%       | 0.5%              | 0.1%         | 0.0%                | 0.0%              |
| Filtering and Sorting          | 0.8%       | 1.5%              | 0.5%         | 1.2%                | 0.0%              |
| Complex Multi-Table Joins      | 2.5%       | 3.0%              | 1.2%         | 3.5%                | 0.2%              |
| Aggregations and Grouping      | 1.8%       | 2.2%              | 0.8%         | 2.0%                | 0.1%              |
| Data Modification Attempts     | 3.5%       | 2.8%              | 1.5%         | 3.2%                | 0.5%              |
| Ambiguous User Questions       | 4.0%       | 4.5%              | 6.0%         | 3.8%                | 0.8%              |
| Sensitive Data Access Requests | 3.2%       | 4.0%              | 2.5%         | 3.0%                | 1.5%              |

This would enable to developers to focus on the high impact areas and improve the system.

### Submission instructions
1. Fork the repo  
2. Push your solution to your fork.
3. Add a detailed README with your approach, instructions to run the code, and any other details. 

## Resources
1. https://github.com/apple/ToolSandbox
2. https://github.com/SalesforceAIResearch/CRMArena
3. https://github.com/sierra-research/tau2-bench

