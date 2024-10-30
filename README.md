# Folio

Folio is a tool to manage your prompts and organise them under projects. It also has bult-in version control for prompts. It is lightweight, non-intrusive and llm-agnostic.

## Prerequisites

1. **Python** 3.7 or higher
2. **Folio Database Path**: Ensure the `FOLIO_DB_PATH` environment variable is set to point to the Folio database.

## Installation

Download wheel from [here](https://github.com/neshkatrapati/folio/releases/tag/v1.0.0)

Install Folio via pip:

```bash
pip install folio-x.y.z.tar.gz
```

Then, set the `FOLIO_DB_PATH` environment variable:

```bash
export FOLIO_DB_PATH=/path/to/your/database
```

## Commands

### 1. `list_projects`

Lists all projects in the database.

```bash
folio list_projects
```

### 2. `list_prompts`

Lists all prompts under a specific project.

```bash
folio list_prompts PROJECT_NAME
```

### 3. `list_versions`

Lists all versions of a specific prompt under a project.

```bash
folio list_versions PROJECT_NAME PROMPT_NAME
```

### 4. `show_prompt`

Displays the content of a specific prompt version.

```bash
folio show_prompt PROJECT_NAME PROMPT_NAME --version VERSION_NUMBER
```

If the version is not specified, the latest version will be shown.

### 5. `create_project`

Creates a new project with the specified name.

```bash
folio create_project PROJECT_NAME
```

### 6. `add_prompt`

Adds a new prompt under a specified project. Input can be provided as a file or through stdin.

```bash
folio add_prompt PROJECT_NAME PROMPT_NAME --file /path/to/prompt.txt
```

Alternatively, provide prompt text through stdin:

```bash
echo "Prompt content" | folio add_prompt PROJECT_NAME PROMPT_NAME
```

Here's the revised README section for programmatic usage with naming rules:

---

## Programmatic Usage

The `Folio` class provides programmatic access to projects and prompts in the database. Below are examples of how to create projects, add prompts, and retrieve data directly in code.

### Setup

Ensure the database path is set correctly:

```python
from folio import Folio  # Import the Folio class from the installed package

# Initialize Folio with the database path
folio = Folio(db_file_path="path/to/your/folio_db.json")
```

### Examples

#### 1. Create a Project

To create a new project:

```python
project_id = folio.create_project("my_new_project")
print(f"Created project with ID: {project_id}")
```

#### 2. List All Projects

To list all existing projects:

```python
projects = folio.list_projects()
for project in projects:
    print(f"ID: {project.id}, Name: {project.name}, Created At: {project.created_at}")
```

#### 3. Add a Prompt to a Project

To add a prompt to an existing project:

```python
prompt = folio.add_prompt("my_new_project", "sample_prompt", "This is the text of the sample prompt.")
print(f"Created prompt '{prompt.name}' under project 'my_new_project' with version {prompt.version}")
```

#### 4. List Prompts by Project Name

To list all prompts under a specific project:

```python
prompts = folio.list_prompts_by_project_name("my_new_project")
for prompt in prompts:
    print(f"Prompt Name: {prompt.name}, Versions: {prompt.num_versions}")
```

#### 5. List Versions of a Prompt

To retrieve all versions of a specific prompt under a project:

```python
versions = folio.list_versions_by_prompt("my_new_project", "sample_prompt")
for version in versions:
    print(f"Version: {version.version}, Created At: {version.created_at}")
```

#### 6. Retrieve a Specific Prompt

To retrieve a specific prompt version or the latest version:

```python
# Retrieve the latest version
prompt = folio.get_prompt("my_new_project", "sample_prompt")
print(f"Latest Version Text: {prompt.text}")

# Retrieve a specific version
prompt = folio.get_prompt("my_new_project", "sample_prompt", version=1)
print(f"Version 1 Text: {prompt.text}")
```

These examples showcase the flexibility of the `Folio` class to programmatically manage projects and prompts in the database while adhering to naming conventions.