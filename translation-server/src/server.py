import logging
import json
import os
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent
from .tools import (
    get_tools,
    translate_text,
    translate_with_detection,
    detect_language,
    get_supported_languages,
    check_api_health,
)

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Setup logging configuration."""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    logger.info('Logging initialized at level: %s', log_level)


def _json_content(payload: dict) -> list[TextContent]:
    """Wrap a structured payload as a JSON TextContent result."""
    return [TextContent(
        type='text',
        text=json.dumps(payload, ensure_ascii=False),
    )]


def create_server() -> Server:
    """Create and configure MCP server."""
    logger.info('Creating MCP Translation Server')

    server = Server('translation-server')

    @server.list_tools()
    async def list_tools() -> list:
        """List available tools."""
        tools = get_tools()
        logger.info('Listed %d tools', len(tools))
        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Execute tool by name."""
        logger.info(
            'Tool execution started: name=%s, arguments=%s',
            name,
            json.dumps(arguments, indent=2)
        )

        try:
            if name == 'translate_text':
                result = translate_text(
                    text=arguments['text'],
                    source_lang=arguments['source_lang'],
                    target_lang=arguments['target_lang'],
                )
            elif name == 'translate_with_detection':
                result = translate_with_detection(
                    text=arguments['text'],
                    target_lang=arguments['target_lang'],
                )
            elif name == 'detect_language':
                result = detect_language(text=arguments['text'])
            elif name == 'get_supported_languages':
                result = get_supported_languages()
            elif name == 'check_api_health':
                result = check_api_health()
            else:
                logger.error('Unknown tool: %s', name)
                return _json_content({
                    'status': 'error',
                    'tool': name,
                    'error': f'Unknown tool: {name}',
                })

            logger.info('Tool execution succeeded: name=%s', name)
            return _json_content(result)

        except Exception as e:
            logger.error(
                'Tool execution failed: name=%s, error=%s',
                name,
                str(e)
            )
            return _json_content({
                'status': 'error',
                'tool': name,
                'error': str(e),
            })

    logger.info('MCP Translation Server created successfully')
    return server


async def main() -> None:
    """Main entry point."""
    setup_logging()
    logger.info('Starting MCP Translation Server')

    server = create_server()
    logger.info('MCP server listening on stdio')

    async with stdio_server() as (read_stream, write_stream):
        logger.info('Server streams established')
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
