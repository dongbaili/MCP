# server.py
import asyncio
import json
import subprocess
import os
from typing import Dict, Any
import aiohttp
from tools import tools

# Configuration for LLM API
LLM_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
LLM_API_TOKEN = "sk-evidbkorgcqmhkpnzlmafgeiioyxgjlucfzcwiivvzaengnb"

# Define available local tools
TOOLS = {
    "run_cmd": lambda command: subprocess.check_output(command, shell=True, text=True),
    "ping": lambda address: subprocess.check_output(
        f"ping -c 4 {address}", shell=True, text=True
    ),
}
async def call_llm(messages) -> str:
    """
    Send prompt to LLM API and return its response as text.
    """
    headers = {
        "Authorization": f"Bearer {LLM_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "Qwen/Qwen3-8B",  # or your preferred model
        "messages": messages,
        "tools": tools
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(LLM_API_URL, headers=headers, json=payload) as resp:
            resp_json = await resp.json()
            # Adjust depending on your API's response format
            return resp_json["choices"][0]["message"]

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    data = await reader.read(1024)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    print("======New Task Started======")
    print(f"Received {message!r} from {addr}")

    # 1. Call LLM
    request = json.loads(message)
    forward_prompt = request.get("prompt", "")
    messages = [
        {"role": "user", "content": forward_prompt}
    ]
    reps = await call_llm(messages)
    tool = reps['tool_calls'][0] if 'tool_calls' in reps else None
    print(f"@@LLM Chosen Tool@@: {tool}")

    # 2. Tool Invocation
    tool_name = tool["function"]["name"]
    if tool_name in TOOLS:
        args = json.loads(tool["function"]["arguments"])
        response = tool_name + " succeed.\n" + TOOLS[tool_name](**args)
    else:
        response = f"Error: Unknown tool: {tool_name}"
    # try:
        
    # except:
        # response = "Error: Invalid LLM response format"

    print(f"@@Tool Invocation@@: {response}")
    # 3. Send response back to client
    messages.append({
        "role": "tool",
        "tool_call_id": tool["id"],
        "content": response
    })
    reps = await call_llm(messages)
    final_response = reps['content']
    print(f"@@Final Response@@: {final_response}")
    writer.write(final_response.encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()
    print("======Task Finished======\n")
    

async def main(host: str = '127.0.0.1', port: int = 8888):
    server = await asyncio.start_server(handle_client, host, port)
    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped.")