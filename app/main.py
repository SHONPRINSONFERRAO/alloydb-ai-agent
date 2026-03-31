import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google import genai
import asyncpg
app = FastAPI(title="AlloyDB AI Inventory Agent")
HTML_UI = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Database Agent</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; color: #333; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { background-color: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 650px; padding: 30px; max-height: 90vh; display: flex; flex-direction: column; }
        h1 { color: #1a73e8; font-size: 24px; text-align: center; margin-top: 0; }
        p { text-align: center; color: #666; font-size: 14px; margin-bottom: 20px;}
        .chat-box { border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; flex-grow: 1; overflow-y: auto; margin-bottom: 15px; background-color: #fafbfc; min-height: 400px;}
        .msg { margin-bottom: 15px; padding: 10px 15px; border-radius: 8px; max-width: 85%; }
        .user-msg { background-color: #e8f0fe; color: #1a73e8; margin-left: auto; border-bottom-right-radius: 0; font-size: 14px; }
        .bot-msg { background-color: #ffffff; color: #333; border: 1px solid #e0e0e0; margin-right: auto; border-bottom-left-radius: 0; font-size: 13px; }
        .sql-box { background-color: #f1f3f4; padding: 8px; border-radius: 4px; font-family: monospace; color: #d93025; margin-top: 5px; margin-bottom: 10px; word-break: break-all; }
        .json-box { background-color: #f8f9fa; padding: 8px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; margin-top: 5px; border: 1px solid #e8eaed; max-height: 200px; overflow-y: auto;}
        .input-area { display: flex; gap: 10px; }
        input[type="text"] { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 14px; outline: none; transition: border-color 0.2s;}
        input[type="text"]:focus { border-color: #1a73e8; }
        button { padding: 12px 20px; background-color: #1a73e8; color: white; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; font-weight: bold; transition: background-color 0.2s; white-space: nowrap; }
        button:hover { background-color: #1557b0; }
        .loading { color: #888; font-style: italic; text-align: center; font-size: 12px; margin-top: 5px;}
    </style>
</head>
<body>
    <div class="container">
        <h1>AlloyDB AI Database Agent</h1>
        <p>Chat with your e-commerce inventory using natural language.</p>
        <div class="chat-box" id="chat">
            <div class="msg bot-msg">Hello! I am your AI Database Assistant. Ask me anything about your inventory (e.g. "Which products are out of stock?" or "What is the most expensive item?")</div>
        </div>
        <div class="input-area">
            <input type="text" id="queryInput" placeholder="Type your question here..." onkeypress="if(event.key === 'Enter') sendQuery()">
            <button onclick="sendQuery()">Ask Agent</button>
        </div>
    </div>
    
    <script>
        async function sendQuery() {
            const input = document.getElementById('queryInput');
            const chat = document.getElementById('chat');
            const question = input.value.trim();
            if (!question) return;
            
            chat.innerHTML += `<div class='msg user-msg'>${question}</div>`;
            input.value = '';
            
            const loadingId = 'loading-' + Date.now();
            chat.innerHTML += `<div class='loading' id='${loadingId}'>Agent is translating to SQL and querying AlloyDB...</div>`;
            chat.scrollTop = chat.scrollHeight;
            
            try {
                const response = await fetch('/query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: question})
                });
                const data = await response.json();
                document.getElementById(loadingId).remove();
                
                let botResponseHTML = `<div class='msg bot-msg'>`;
                
                if (data.greeting) {
                    botResponseHTML += data.greeting;
                } else {
                    botResponseHTML += `<strong>Executed SQL:</strong><div class='sql-box'>${data.generated_sql || 'None'}</div>`;
                    botResponseHTML += `<strong>Database Results:</strong>`;
                    
                    if (data.database_results && data.database_results.length > 0) {
                        data.database_results.forEach(item => {
                            // Extract just the fields we care about (ignoring the massive vector embedding)
                            botResponseHTML += `
                            <div style="border: 1px solid #e0e0e0; border-radius: 6px; padding: 10px; margin-top: 8px; background-color: #fcfcfc;">
                                <div style="font-weight: bold; color: #1a73e8; font-size: 14px; margin-bottom: 4px;">${item.name || 'Unknown Item'}</div>
                                <div style="font-size: 12px; margin-bottom: 6px;">
                                    <span style="background-color: #e8eaed; padding: 2px 6px; border-radius: 4px; color: #3c4043; font-weight: 500; margin-right: 6px;">${item.category || 'N/A'}</span>
                                    <span style="color: #1e8e3e; font-weight: bold; margin-right: 6px;">$${item.price || '0.00'}</span>
                                    <span style="color: ${item.stock_quantity > 0 ? '#5f6368' : '#d93025'}; font-weight: 500;">Stock: ${item.stock_quantity || 0}</span>
                                </div>
                                <div style="font-size: 13px; color: #3c4043; line-height: 1.4;">${item.description || ''}</div>
                            </div>`;
                        });
                    } else {
                        botResponseHTML += `<div style="font-style: italic; color: #888; margin-top: 5px;">No products matched your question.</div>`;
                    }
                }
                
                botResponseHTML += `</div>`;
                
                chat.innerHTML += botResponseHTML;
            } catch (e) {
                document.getElementById(loadingId).remove();
                chat.innerHTML += `<div class='msg bot-msg' style="color:red;">Error connecting to the agent.</div>`;
            }
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
"""
@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serves the interactive chat web UI"""
    return HTML_UI
# Initialize Vertex AI native GenAI client
# Requires GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION environment variables
try:
    client = genai.Client(vertexai=True)
except Exception as e:
    print(f"Warning: Could not initialize Vertex AI client: {e}")
    client = None
class QueryRequest(BaseModel):
    query: str
SCHEMA_CONTEXT = """
You are a PostgreSQL expert working with an AlloyDB database.
The database contains a table named 'products' with the following schema:
- id: SERIAL PRIMARY KEY
- name: VARCHAR(255)
- category: VARCHAR(100)
- price: DECIMAL(10, 2)
- stock_quantity: INT
- description: TEXT
- description_embedding: vector(768)
To perform similarity search using the description_embedding, use the google_ml.embedding() function. 
Example for a search related to "listen to music":
ORDER BY description_embedding <=> google_ml.embedding('text-embedding-004', 'listen to music') LIMIT 5
CRITICAL RULE: If the user's input is just a friendly greeting (like "hello" or "hi") or completely unrelated to our e-commerce inventory, DO NOT write SQL. Instead, return the EXACT text: GREETING
Otherwise, translate the user's question into a valid read-only PostgreSQL SELECT query.
DO NOT wrapper the query in markdown blocks (e.g., no ```sql). RETURN ONLY THE RAW SQL TEXT (or 'GREETING').
"""
async def execute_query(sql_query: str):
    # Connect to AlloyDB using environment variables
    # Requires: DB_USER, DB_PASSWORD, DB_NAME, DB_HOST
    try:
        conn = await asyncpg.connect(
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password"),
            database=os.getenv("DB_NAME", "postgres"),
            host=os.getenv("DB_HOST", "127.0.0.1")
        )
        print(f"Executing SQL: {sql_query}")
        rows = await conn.fetch(sql_query)
        await conn.close()
        
        # Convert rows to a list of dicts
        result = [dict(row) for row in rows]
        # Serialize vector objects
        for r in result:
            if 'description_embedding' in r and r['description_embedding'] is not None:
                r['description_embedding'] = str(r['description_embedding'])
        return result
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database execution failed: {str(e)}")
@app.post("/query")
async def ask_agent(request: QueryRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Vertex AI client not initialized. Check credentials.")
        
    user_question = request.query
    prompt = f"{SCHEMA_CONTEXT}\n\nUser Question: {user_question}\n\nSQL Query:"
    
    try:
        # Call Gemini 2.5 Flash to generate the SQL
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        sql_query = response.text.strip()
        
        # Clean up any markdown formatting just in case the model ignores instructions
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
            
        sql_query = sql_query.strip()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate SQL from AI: {str(e)}")
        
    # Check if the AI decided this was a greeting/conversational message
    if sql_query == "GREETING" or "GREETING" in sql_query:
        return {
            "natural_language_question": user_question,
            "greeting": "<div style='font-size:14px; color:#1a73e8; margin-bottom:6px;'><strong>Agent:</strong> Hello! 👋 I am your AlloyDB AI Assistant.</div><div style='font-size:13px; color:#555;'>I can translate your English into SQL! Try asking things like:<br>• <i>Which items are out of stock?</i><br>• <i>Show me the most expensive electronics.</i><br>• <i>Find items related to music.</i></div>"
        }
        
    # Execute the SQL directly against AlloyDB
    db_results = await execute_query(sql_query)
    
    return {
        "natural_language_question": user_question,
        "generated_sql": sql_query,
        "database_results": db_results
    }
