---
paths:
  - "src/lambda/**/*.py"
  - "src/layer/**/*.py"
---

# Python Lambda Rules

- Use snake_case naming
- Add type hints and docstrings
- Keep functions under 15MB (use layers for dependencies)
- No PII in logs
- **Layer Usage**: Always package heavy dependencies (like `pandas`, `numpy`, or large SDKs) in Lambda Layers, not directly in the function deployment package, to avoid hitting the 15MB deployment limit and to speed up deployments.
- **Streaming over Memory**: When handling Apple Health XML files or other large payloads, always use streaming parsers (like `xml.etree.ElementTree.iterparse`). Do NOT read the entire file into memory using `.read()`.
- **Environment Variables**: Always retrieve configuration via environment variables, and ensure the CDK stack provisions them correctly.
