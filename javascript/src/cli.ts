#!/usr/bin/env node
import { Command } from 'commander';

const program = new Command();

program
    .name('citekit')
    .description('CiteKit CLI for managing local resources')
    .version('0.1.7');

program.command('serve')
    .description('Start the MCP server')
    .action(async () => {
        const { runMcpServer } = await import('./mcp-server.js');
        await runMcpServer();
    });

program.parse(process.argv);
