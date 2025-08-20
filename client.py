# client.py
import asyncio
import json

async def tcp_client(message: dict, host: str = '127.0.0.1', port: int = 8888):
    reader, writer = await asyncio.open_connection(host, port)
    data = json.dumps(message)
    writer.write(data.encode())
    await writer.drain()

    resp_data = await reader.read(4096)
    resp = resp_data.decode()
    print(f"Received: {resp}")

    writer.close()
    await writer.wait_closed()

if __name__ == '__main__':
    # prompt = "Please list the files in /bin."
    # prompt = "Run 'echo Hello World!' in the shell."
    # prompt = "Run 'mkdir test_mcp' in the shell."
    # prompt = "Make a new directory named 'test_mcp' in the current directory."
    # prompt = "Help me test if www.baidu.com is reachable."
    # prompt = "Help me test if www.google.com is reachable."
    # prompt = "Tell me if there is a folder named 'home' inside /bin"
    prompt = "Create empty.txt in the current directory and then list the files in the current directory."
    message = {"prompt": prompt}
    try:
        asyncio.run(tcp_client(message))
    except Exception as e:
        print(f"Error: {e}")