# LLM MCP
本仓库是调研大语言模型调用工具的python实现，支持``运行命令行指令``和``测试网络联通性``两个功能。

## 第一部分 手写实现协议
适用于任何纯文本LLM。

详见``demo_client.py``和``demo_server.py``

## 第二部分 利用function tool官方接口
仅适用于有tool call能力的LLM，即支持以"tool_calls"字段返回结果的LLM。

详见``client.py``、``server.py``和``tools.py``

本实现还支持一次用户prompt调用多个工具，并顺序执行。

## 详细文档说明（需使用华为内网访问）
- MCP实现与效果: https://clouddocs.huawei.com/wapp/public/b988fd77-0a49-4c36-99e4-785310aebcb5
- MCP相关paper: https://clouddocs.huawei.com/wapp/public/988ff763-7733-46d0-bf31-31b9fa239b82