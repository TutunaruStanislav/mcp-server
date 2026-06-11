#!/usr/bin/env python3
"""End-to-end MCP check over the real stdio transport.

Starts the server via run.py, performs the MCP handshake, then calls all
five tools. Tool results (structured JSON) are printed to stdout; the
server-side logs are captured to verification.log as the call trace.

Run from the translation-server directory:

    python verify_mcp.py
"""
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

CALLS = [
    ('check_api_health', {}),
    ('get_supported_languages', {}),
    ('translate_text',
     {'text': 'Hello, world!', 'source_lang': 'ENG', 'target_lang': 'RUS'}),
    ('translate_with_detection',
     {'text': 'Good morning', 'target_lang': 'RUS'}),
    ('detect_language', {'text': 'Привіт, світ'}),
]


async def main() -> None:
    params = StdioServerParameters(command='python', args=['run.py'])
    with open('verification.log', 'w', encoding='utf-8') as errlog:
        async with stdio_client(params, errlog=errlog) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                print('Registered tools:', [t.name for t in tools.tools])
                print('-' * 60)
                for name, args in CALLS:
                    res = await session.call_tool(name, args)
                    print(f'{name}({args})')
                    print(f'  -> {res.content[0].text}')


if __name__ == '__main__':
    asyncio.run(main())
