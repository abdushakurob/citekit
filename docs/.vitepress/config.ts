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
                        { text: 'Quick Start', link: '/guide/getting-started' },
                    ]
                },
                {
                    text: 'Core Concepts',
                    items: [
                        { text: 'Architecture', link: '/guide/concepts/architecture' },
                        { text: 'Ingestion Process', link: '/guide/concepts/ingestion' },
                        { text: 'Resource Maps', link: '/guide/concepts/resource-mapping' },
                        { text: 'Content Resolution', link: '/guide/concepts/content-resolution' },
                        { text: 'Virtual Resolution (Serverless)', link: '/guide/concepts/virtual-mode' }
                    ]
                },
                {
                    text: 'Deployment',
                    items: [
                        { text: 'System Requirements', link: '/guide/requirements' },
                        { text: 'Deployment Guide', link: '/guide/deployment' },
                        { text: 'Troubleshooting', link: '/guide/troubleshooting' }
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
                    text: 'API Reference',
                    items: [
                        { text: 'Python SDK', link: '/api/python' },
                        { text: 'JavaScript SDK', link: '/api/javascript' },
                        { text: 'CLI Reference', link: '/api/cli' },
                        { text: 'Data Models', link: '/api/models' },
                        { text: 'Virtual Resolution', link: '/guide/concepts/virtual-mode' }
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
