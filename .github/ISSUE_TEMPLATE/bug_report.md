name: Bug Report
description: Report a bug to help us improve
title: "[BUG] "
labels: ["bug"]

body:
  - type: markdown
    attributes:
      value: |
        Thank you for reporting a bug! Please fill in as much detail as possible.

  - type: checkboxes
    id: checklist
    attributes:
      label: Checklist
      options:
        - label: I've searched existing issues and found nothing related
          required: true
        - label: I'm using the latest version
          required: false
        - label: I've tested on testnet first
          required: false

  - type: textarea
    id: description
    attributes:
      label: Description
      description: A clear and concise description of the bug
      placeholder: "Describe what happened..."
    validations:
      required: true

  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      description: Steps to reproduce the behavior
      placeholder: |
        1. Go to...
        2. Click on...
        3. See error...
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What should happen instead?
      placeholder: "Expected..."
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: Actual Behavior
      description: What actually happened?
      placeholder: "Actually..."
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Logs/Screenshots
      description: Share error messages, logs, or screenshots
      placeholder: "Paste logs or screenshots here..."

  - type: input
    id: environment
    attributes:
      label: Environment
      description: |
        e.g., macOS, Linux, Windows
        Python version, Docker version, etc.
      placeholder: "macOS 12.x, Python 3.11, Docker 4.x"

  - type: textarea
    id: additional
    attributes:
      label: Additional Context
      description: Any other context about the problem?
      placeholder: "Add any other context here..."
