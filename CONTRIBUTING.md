# Contributing to dbt-central-app

Welcome to dbt-central-app! We appreciate your interest in contributing to our project. Before you start, please take a moment to review this document to understand how you can contribute effectively.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
   - [Fork the Repository](#fork-the-repository)
   - [Set Up a Development Environment](#set-up-a-development-environment)
3. [Development Guidelines](#development-guidelines)
   - [Coding Standards](#coding-standards)
   - [Branching Strategy](#branching-strategy)
   - [Commit Message Conventions](#commit-message-conventions)
   - [Testing](#testing)
4. [Submitting Changes](#submitting-changes)
   - [Creating a Pull Request](#creating-a-pull-request)
   - [Review and Feedback](#review-and-feedback)
5. [Additional Resources](#additional-resources)

## Code of Conduct

Please review our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing. We are committed to creating a welcoming and inclusive community for all contributors.

## Getting Started

### Fork the Repository

1. Click the "Fork" button on the top right of the [repository page](https://github.com/yourusername/your-repo).
2. Clone your forked repository to your local machine:

   ```bash
   git clone https://github.com/infinitelambda/dbt-streamlit-dashboards
   ```
## Setting up an environment

There are some tools that will be helpful to you in developing locally. While this is the list relevant for development, many of these tools are used commonly across open-source python projects.

### Tools

These are the tools used in development and testing:

- [`tox`](https://tox.readthedocs.io/en/latest/) to manage virtualenvs across python versions. We currently target the latest patch releases for Python 3.8, 3.9, 3.10 and 3.11
- [`pytest`](https://docs.pytest.org/en/latest/) to define, discover, and run tests
- [`flake8`](https://flake8.pycqa.org/en/latest/) for code linting
- [`black`](https://github.com/psf/black) for code formatting
- [`mypy`](https://mypy.readthedocs.io/en/stable/) for static type checking
- [`pre-commit`](https://pre-commit.com) to easily run those checks
- [GitHub Actions](https://github.com/features/actions) for automating tests and checks, once a PR is pushed to the repository

A deep understanding of these tools in not required to effectively contribute to `dbt-core`, but we recommend checking out the attached documentation if you're interested in learning more about each one.
  
#### Virtual environments

To develop or contribute to dbt-central-app, you will need to set up a development environment. We recommend using [Python virtual environments](https://docs.python.org/3/library/venv.html) to isolate your project dependencies.

1. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:

   - **Windows**:

     ```bash
     venv\Scripts\activate
     ```

   - **Linux/macOS**:

     ```bash
     source venv/bin/activate
     ```

3. Install project dependencies:

   ```bash
   pip install -r requirements.txt
   ```

Now, you are ready to start developing.

## Development Guidelines

### Coding Standards

Please follow our coding standards to maintain code consistency:

- Use [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code.
- Use meaningful variable and function names.
- Write clear and concise comments.

### Branching Strategy

- Create a new feature or bugfix branch off the `main` branch:

  ```bash
  git checkout -b feature/my-new-feature
  ```

- Make your changes and commit them.

- When your work is complete, push the branch to your fork:

  ```bash
  git push origin feature/my-new-feature
  ```

### Commit Message Conventions

We follow the conventional commit message format. Please use meaningful commit messages that convey the purpose of your changes. For example:

```
feat: add new functionality to do X
fix: resolve issue with Y
docs: update documentation for Z
```

### Testing

We encourage writing tests for new features and bug fixes. Ensure that all tests pass before submitting a pull request.

## Submitting Changes

### Creating a Pull Request

1. Go to the [Pull Requests](https://github.com/yourusername/your-repo/pulls) tab of the original repository.
2. Click the "New Pull Request" button.
3. Select the base branch (usually `main`) and your feature branch.
4. Describe your changes and provide any necessary context in the pull request description.
5. Click the "Create Pull Request" button.

### Review and Feedback

Your pull request will be reviewed by maintainers and contributors. Be open to feedback and willing to make changes if necessary. Once your changes are approved, they will be merged into the main repository.

## Additional Resources

- [Project Wiki](https://github.com/yourusername/your-repo/wiki)
- [Issue Tracker](https://github.com/yourusername/your-repo/issues)
- [Code of Conduct](CODE_OF_CONDUCT.md)

Thank you for contributing to dbt-central-app! We appreciate your time and effort in making this project better.
