# Agent Frameworks

CiteKit is designed to be the "Context Layer" for autonomous agents. Here is how to integrate it with popular frameworks.

## LangChain (Python)

You can create a custom Tool for LangChain that wraps CiteKit.

```python
from langchain.tools import tool
from citekit import CiteKitClient

client = CiteKitClient()

@tool
async def get_video_context(query: str, video_id: str):
    """
    Useful for getting specific context from a video file.
    Args:
        query: What user is asking about
        video_id: The ID of the video resource
    """
    # 1. Get Map
    structure = client.get_structure(video_id)
    
    # 2. Ask LLM which node is relevant (Simplified logic here)
    # In production, you'd pass the structure to an LLM chain
    relevant_node = structure.nodes[0] 
    
    # 3. Resolve
    evidence = await client.resolve(video_id, relevant_node.id)
    return f"I have watched the clip. You can find it at {evidence.output_path}"

# Usage
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(temperature=0)
tools = [get_video_context]
agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS)

agent.run("What does the video 'tutorial' say about installation?")
```

## CrewAI

In CrewAI, CiteKit can be a tool assigned to a specific "Researcher" agent.

```python
from crewai import Agent, Task, Crew, Process
from langchain.tools import tool
from citekit import CiteKitClient

# Define Tool
class CiteKitTools:
    @tool("Video Inspector")
    def inspect_video(video_path: str):
        """Analyzes a video file and returns its structure map."""
        client = CiteKitClient()
        # Note: CrewAI tools are often sync, so you might need a sync wrapper
        # or use asyncio.run()
        import asyncio
        map = asyncio.run(client.ingest(video_path, "video"))
        return map.model_dump_json()

    @tool("Image Inspector")
    def inspect_image(image_path: str):
        """Analyzes an image and returns regions of interest (charts, objects)."""
        client = CiteKitClient()
        # Note: CrewAI tools are often sync, so you might need a sync wrapper
        # or use asyncio.run()
        import asyncio
        map = asyncio.run(client.ingest(image_path, "image"))
        return map.model_dump_json()

# Define Agent
researcher = Agent(
    role='Video Researcher',
    goal='Find specific answers in video content',
    backstory='You are an expert at navigating video archives.',
    tools=[CiteKitTools.inspect_video],
    verbose=True
)

# Define Task
task = Task(
    description='Find the segment about "Deployment" in tutorial.mp4',
    agent=researcher
)

# Execution
crew = Crew(
    agents=[researcher],
    tasks=[task],
    process=Process.sequential
)

result = crew.kickoff()
```

## General Pattern

Can't find your framework? The pattern is always the same:

1.  **Expose `ingest` / `get_structure` as a Tool**: Allow the agent to "see" the Table of Contents.
2.  **Expose `resolve` as a Tool**: Allow the agent to "fetch" a specific page or clip.
3.  **Prompt Engineering**: Tell the agent "Always check the map first before asking for content."
