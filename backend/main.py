from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict
import asyncio
from agents import GeminiAgent, MistralAgent, GroqAgent

app = FastAPI(title="LLM Council API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
chairman = GeminiAgent()
council_members = [
    MistralAgent(),
    GroqAgent("Council Member 2 (Llama 3.3)", "llama-3.3-70b-versatile"),
    GroqAgent("Council Member 3 (Llama 3.1)", "llama-3.1-8b-instant"),
    GeminiAgent(),
]

class CouncilRequest(BaseModel):
    topic: str
    rounds: int = 2

class RoundResponse(BaseModel):
    round: int | str
    responses: Dict[str, str]

class CouncilResponse(BaseModel):
    topic: str
    rounds: List[RoundResponse]

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LLM Council</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; }
            .form-group { margin: 20px 0; }
            input, textarea, button { padding: 10px; font-size: 14px; }
            button { background: #007bff; color: white; border: none; cursor: pointer; }
            button:hover { background: #0056b3; }
            .results { margin-top: 30px; }
            .round { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .member { margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #007bff; }
        </style>
    </head>
    <body>
        <h1>LLM Council Discussion</h1>
        <div class="form-group">
            <label>Topic for Discussion:</label><br>
            <textarea id="topic" rows="3" style="width: 100%; margin-top: 5px;"></textarea>
        </div>
        <div class="form-group">
            <label>Number of Rounds:</label>
            <input type="number" id="rounds" value="2" min="1" max="5" style="width: 100px;">
        </div>
        <button onclick="startDiscussion()">Start Discussion</button>
        <div id="results" class="results"></div>
        
        <script>
            async function startDiscussion() {
                const topic = document.getElementById('topic').value;
                const rounds = parseInt(document.getElementById('rounds').value);
                
                if (!topic.trim()) {
                    alert('Please enter a topic');
                    return;
                }
                
                document.getElementById('results').innerHTML = '<p>Discussion in progress...</p>';
                
                try {
                    const response = await fetch('/council/discuss', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ topic, rounds })
                    });
                    
                    const data = await response.json();
                    displayResults(data);
                } catch (error) {
                    document.getElementById('results').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
                }
            }
            
            function displayResults(data) {
                let html = '<h2>' + data.topic + '</h2>';
                if (!data.rounds || !Array.isArray(data.rounds)) {
                    document.getElementById('results').innerHTML = '<p style="color: red;">Unexpected response format</p>';
                    return;
                }
                data.rounds.forEach(round => {
                    html += '<div class="round"><h3>Round ' + round.round + '</h3>';
                    if (round.responses) {
                        for (let member in round.responses) {
                            html += '<div class="member"><strong>' + member + ':</strong><br>' + round.responses[member] + '</div>';
                        }
                    }
                    html += '</div>';
                });
                document.getElementById('results').innerHTML = html;
            }
        </script>
    </body>
    </html>
    """

@app.post("/council/discuss", response_model=CouncilResponse)
async def discuss_topic(request: CouncilRequest):
    """
    Orchestrate a council discussion where multiple LLMs debate a topic.
    """
    try:
        discussion_rounds = []
        current_context = f"Topic: {request.topic}\n\n"
        
        for round_num in range(request.rounds):
            round_responses = {}
            
            # Chairman introduces or moderates
            if round_num == 0:
                chairman_prompt = f"""You are the chairman of an LLM council. Introduce the following topic for discussion and provide initial thoughts:

{request.topic}

Keep your response concise (2-3 sentences)."""
            else:
                chairman_prompt = f"""You are moderating a council discussion. Summarize the previous round and guide the discussion forward.

Topic: {request.topic}

Previous discussion:
{current_context}

Provide a brief moderation (1-2 sentences) to guide the next round."""
            
            chairman_response = await chairman.generate(chairman_prompt)
            round_responses["Chairman"] = chairman_response
            current_context += f"Chairman: {chairman_response}\n\n"
            
            # Council members respond
            member_prompt = f"""You are a council member in a discussion. Provide your perspective on the topic.

Topic: {request.topic}

Current discussion context:
{current_context}

Provide your thoughtful response (2-4 sentences). Be concise but insightful."""
            
            # Get responses from all council members in parallel
            member_tasks = [member.generate(member_prompt) for member in council_members]
            member_responses = await asyncio.gather(*member_tasks)
            
            for member, response in zip(council_members, member_responses):
                round_responses[member.name] = response
                current_context += f"{member.name}: {response}\n\n"
            
            discussion_rounds.append({
                "round": round_num + 1,
                "responses": round_responses
            })
        
        # Final summary from chairman
        summary_prompt = f"""As the chairman, provide a brief summary of the council discussion.

Topic: {request.topic}

Full discussion:
{current_context}

Provide a concise summary (3-4 sentences) of the key points discussed."""
        
        final_summary = await chairman.generate(summary_prompt)
        
        return CouncilResponse(
            topic=request.topic,
            rounds=discussion_rounds + [{
                "round": "Summary",
                "responses": {"Chairman": final_summary}
            }]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in council discussion: {str(e)}")

@app.get("/council/members")
async def get_council_members():
    """Get list of council members"""
    return {
        "chairman": chairman.name,
        "members": [member.name for member in council_members]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)