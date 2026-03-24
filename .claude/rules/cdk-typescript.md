---
paths:
  - "lib/**/*.ts"
---

# CDK / TypeScript Rules

- Use camelCase naming
- Enable strict mode
- Explicit types for all constructs
- Organize by AWS service in /stack
- **Construct-first pattern**: Every AWS service must have a reusable L2 construct in `/lib/construct/` before being used in a factory (`/lib/stack/<service>/`). The factory composes constructs with project-specific config — it should never create raw Cfn resources directly. Pattern: `Construct → Factory → Stack`. THIS IS AN IMMUTABLE RULE.
- **No L1 Constructs (Cfn*)**: Never use raw CloudFormation constructs (`CfnBucket`, `CfnFunction`) if an L2 construct exists (`Bucket`, `Function`).
- **Dependency Management**: Remember that changes to constructs might require updating references in multiple stacks.
