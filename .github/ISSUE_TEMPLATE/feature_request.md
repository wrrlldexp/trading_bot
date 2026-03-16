name: Feature Request
description: Suggest a new feature or improvement
title: "[FEATURE] "
labels: ["enhancement"]

body:
  - type: markdown
    attributes:
      value: |
        Thank you for suggesting a feature! Please provide as much detail as possible.

  - type: checkboxes
    id: checklist
    attributes:
      label: Checklist
      options:
        - label: I've searched existing issues and found nothing related
          required: true
        - label: This is not a duplicate of an existing feature request
          required: true

  - type: textarea
    id: problem
    attributes:
      label: Problem Statement
      description: Describe the problem or limitation
      placeholder: |
        As a [user/trader/developer], I want to...
        because...
    validations:
      required: true

  - type: textarea
    id: solution
    attributes:
      label: Proposed Solution
      description: Describe your proposed solution
      placeholder: "The feature should..."
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: Alternatives Considered
      description: Describe any alternative solutions
      placeholder: |
        - Option A: ...
        - Option B: ...

  - type: textarea
    id: usecase
    attributes:
      label: Use Case
      description: Describe the use case or benefit
      placeholder: "This would help because..."

  - type: textarea
    id: additional
    attributes:
      label: Additional Context
      description: Any additional context or references?
      placeholder: |
        - Related issues: #...
        - External links: ...
