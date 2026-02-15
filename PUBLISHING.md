# Publishing Guide

This document outlines the process for publishing CiteKit to PyPI (Python) and npm (JavaScript).

## Prerequisites

- **Python**: `twine` installed (`pip install twine build`)
- **Node.js**: `npm` logged in
- **Accounts**:
    - [PyPI Account](https://pypi.org/)
    - [NPM Account](https://www.npmjs.com/)

## 1. Versioning

Ensure version numbers are consistent across both packages.

- **Python**: `python/pyproject.toml` -> `version = "0.1.x"`
- **JavaScript**: `javascript/package.json` -> `"version": "0.1.x"`

## 2. Python (PyPI)

1.  **Build**
    ```bash
    cd python
    # Clean previous builds
    rm -rf dist/
    # Build source and wheel
    python -m build
    ```

2.  **Upload**
    ```bash
    python -m twine upload dist/*
    ```

## 3. JavaScript (npm)

1.  **Build**
    ```bash
    cd javascript
    npm run build
    ```

2.  **Publish**
    ```bash
    # Dry run to verify properties
    npm publish --dry-run
    
    # Official publish
    npm publish --access public
    ```

## 4. Documentation

After publishing code, deploy the latest documentation:

```bash
# Root directory
npm run docs:build
# Deploy contents of docs/.vitepress/dist to your host (e.g. Vercel/Netlify)
```

## Checklist

- [ ] Tests passed (`pytest`, `npm test`)
- [ ] Version numbers bumped
- [ ] Changelog updated (if applicable)
- [ ] Documentation reflects new features
