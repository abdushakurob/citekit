import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(defineConfig({
    title: 'CiteKit',
    description: 'Local-first AI resource mapping SDK for multimodal agents',
    base: '/citekit/',

    markdown: {
        math: true
    },

    mermaid: {
        // mermaid config
    },

    vite: {
        optimizeDeps: {
            include: ['mermaid'],
        },
        ssr: {
            noExternal: ['mermaid', 'vitepress-plugin-mermaid'],
        },
    },

    themeConfig: {
        logo: '/logo.svg',

        nav: [
            { text: 'Guide', link: '/guide/' },
            { text: 'API', link: '/api/python' },
            { text: 'MCP', link: '/integration/mcp' },
            { text: 'GitHub', link: 'https://github.com/abdushakurob/citekit' }
        ],

        sidebar: {
            '/guide/': [
                {
                    text: 'Introduction',
                    items: [
                        { text: 'Overview', link: '/guide/' },
                        { text: 'The Modern Stack', link: '/guide/modern-stack' },
                        { text: 'Quick Start', link: '/guide/getting-started' },
                    ]
                },
                {
                    text: 'Usage Guide',
                    items: [
                        { text: 'CLI', link: '/guide/usage/cli' },
                        { text: 'Python SDK', link: '/guide/usage/python' },
                        { text: 'Node.js SDK', link: '/guide/usage/node' },
                        { text: 'MCP Agent', link: '/guide/usage/mcp' }
                    ]
                },
                {
                    text: 'Core Concepts',
                    items: [
                        { text: 'Architecture', link: '/guide/concepts/architecture' },
                        { text: 'Ingestion Process', link: '/guide/concepts/ingestion' },
                        { text: 'Resource Maps', link: '/guide/concepts/resource-mapping' },
                        { text: 'Content Resolution', link: '/guide/concepts/content-resolution' },
                        { text: 'Virtual Resolution (Serverless)', link: '/guide/concepts/virtual-mode' },
                        { text: 'Map Adapters', link: '/guide/adapters' },
                        { text: 'Custom Mappers (Local LLMs)', link: '/guide/custom-mappers' },
                        { text: 'Technical Deep Dive (Internals)', link: '/guide/technical-deep-dive' }
                    ]
                },
                {
                    text: 'Deployment',
                    items: [
                        { text: 'System Requirements', link: '/guide/requirements' },
                        { text: 'Deployment Guide', link: '/guide/deployment' },
                        { text: 'Troubleshooting', link: '/guide/troubleshooting' },
                        { text: 'Changelog', link: '/changelog' }
                    ]
                },
                {
                    text: 'Real-World Examples',
                    items: [
                        { text: 'Research App (Node.js)', link: '/guide/examples/research-app' },
                        { text: 'Video Search CLI (Python)', link: '/guide/examples/video-search-cli' },
                        { text: 'Study Companion (MCP)', link: '/guide/examples/study-companion' },
                        { text: 'Hybrid RAG (Diagrams)', link: '/guide/examples/rag-fusion' }
                    ]
                }
            ],
            '/integration/': [
                {
                    text: 'Integration',
                    items: [
                        { text: 'MCP (Claude/Cline)', link: '/integration/mcp' },
                        { text: 'Agent Frameworks', link: '/integration/agents' },
                        { text: 'Virtual Resolution', link: '/guide/concepts/virtual-mode' }
                    ]
                }
            ],
            '/api/': [
                {
                    text: 'Python SDK',
                    collapsed: false,
                    items: [
                        { text: 'Introduction', link: '/api/python' },
                        { text: 'CiteKitClient', link: '/api/python/client' },
                        { text: 'Mappers', link: '/api/python/mappers' },
                        { text: 'Resolvers & Adapters', link: '/api/python/resolvers' },
                        { text: 'Data Models', link: '/api/models#python-models' }
                    ]
                },
                {
                    text: 'JavaScript SDK',
                    collapsed: false,
                    items: [
                        { text: 'Introduction', link: '/api/javascript' },
                        { text: 'CiteKitClient', link: '/api/javascript/client' },
                        { text: 'Mappers', link: '/api/javascript/mappers' },
                        { text: 'Resolvers', link: '/api/javascript/resolvers' },
                        { text: 'Core Interfaces', link: '/api/models#js-interfaces' }
                    ]
                },
                {
                    text: 'CLI Reference',
                    collapsed: true,
                    items: [
                        { text: 'Overview', link: '/api/cli/' },
                        { text: 'ingest', link: '/api/cli/ingest' },
                        { text: 'resolve & inspect', link: '/api/cli/resolve' },
                        { text: 'Resource Management', link: '/api/cli/manage' },
                        { text: 'Adapters', link: '/api/cli/adapt' }
                    ]
                },
                {
                    text: 'MCP Protocol',
                    collapsed: true,
                    items: [
                        { text: 'Overview', link: '/api/mcp/' },
                        { text: 'Tool Reference', link: '/api/mcp/tools' },
                        { text: 'Configuration', link: '/api/mcp/config' }
                    ]
                },
                {
                    text: 'Global Reference',
                    items: [
                        { text: 'ResourceMap Schema', link: '/api/models' },
                        { text: 'Virtual Address Format', link: '/api/virtual' }
                    ]
                }
            ]
        },

        socialLinks: [
            { icon: 'github', link: 'https://github.com/abdushakurob/citekit' }
        ],

        footer: {
            message: 'Released under the MIT License.',
            copyright: 'Copyright © 2026 Abdushakurob'
        },

        search: {
            provider: 'local'
        }
    },

    head: [
        ['link', { rel: 'icon', href: '/favicon.ico' }],
        ['meta', { name: 'theme-color', content: '#42b883' }],
        ['meta', { name: 'og:type', content: 'website' }],
        ['meta', { name: 'og:locale', content: 'en' }],
        ['meta', { name: 'og:site_name', content: 'CiteKit' }]
    ]
}))
