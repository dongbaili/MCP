# server.py
import asyncio
import json
import subprocess
import os
from typing import Dict, Any
import aiohttp

# Configuration for LLM API
LLM_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
#  LLM_API_TOKEN = os.getenv("LLM_API_TOKEN")  # Set this in your environment
LLM_API_TOKEN = "sk-evidbkorgcqmhkpnzlmafgeiioyxgjlucfzcwiivvzaengnb"

# Define available local tools
TOOLS = {
    "run_cmd": lambda cmd: subprocess.check_output(cmd, shell=True, text=True),
    "ping": lambda ip: subprocess.check_output(
        f"ping -c 4 {ip}", shell=True, text=True
    ),
}

FORWARD_PROMPT = """
Following are the available tools you can use:
1. TOOL: run_cmd, ARGS: ["cmd",]
2. TOOL: ping, ARGS: ["ip",]

First determine which tool to use based on the user's request. Then respond in the following format:
{"TOOL": "tool_name", "ARG1": "", "ARG2": "", ...}

For example, if the user asks to list files in "/home/pictures", you should exclusively respond with:
{"TOOL": "run_cmd", "cmd": "ls /home/pictures"}

Now, you can start processing the user's request.
"""

BACKWARD_PROMPT = f"""
User's original request was: {{prompt}}.

You have invoked a tool and received the following response: {{response}}.

Now, please provide a final response to the user based on the tool's output.
"""
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
        "messages": messages
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(LLM_API_URL, headers=headers, json=payload) as resp:
            resp_json = await resp.json()
            # Adjust depending on your API's response format
            return resp_json["choices"][0]["message"]["content"]

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    data = await reader.read(1024)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    print("======New Task Started======")
    print(f"Received {message!r} from {addr}")

    # 1. Call LLM
    request = json.loads(message)
    forward_prompt = FORWARD_PROMPT + request.get("prompt", "")
    messages = [
        {"role": "user", "content": forward_prompt}
    ]
    llm_response = await call_llm(messages)
    print(f"@@LLM Response@@: {llm_response.strip()}")

    # 2. Tool Invocation
    try:
        tool_request = json.loads(llm_response)
        tool_name = tool_request.get("TOOL")
        args = {k: v for k, v in tool_request.items() if k != "TOOL"}
        if tool_name in TOOLS:
            try:
                # Call the specified tool with its arguments
                result = TOOLS[tool_name](**args)
                response = {"success": result}
            except Exception as e:
                response = {"error": str(e)}
        else:
            response = {"error": f"Unknown tool: {tool_name}"}
    except:
        response = {"error": "Invalid LLM response format"}

    print(f"@@Tool Invocation@@: {response}")
    # 3. Send response back to client
    backward_prompt = BACKWARD_PROMPT.format(
        prompt=request.get("prompt", ""),
        response=json.dumps(response, ensure_ascii=False)
    )
    messages = [
        {"role": "user", "content": backward_prompt},
    ]
    final_response = await call_llm(messages)
    print(f"@@Final Response@@: {final_response}")
    # response_data = json.dumps(response)
    # writer.write(response_data.encode())
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