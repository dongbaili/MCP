tools = [
    {
        "type": "function",
        "function": {
            "name": "run_cmd",
            "description": "Run a command in the shell",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to run in the shell, e.g. 'ls /home/user'",
                    }
                },
                "required": ["command"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ping",
            "description": "Test if a host is reachable by pinging it",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The IP address or hostname to ping, e.g. 'www.google.com'",
                    }
                },
                "required": ["address"]
            },
        }
    },
]