

# Folio

Folio is a CLI and Python-based library for managing and storing prompt templates with versioning capabilities. It supports Jinja2-based templating for dynamic prompt rendering, leveraging TinyDB for lightweight data storage and easy-to-use methods for listing, retrieving, and managing prompt versions.

## Features
* **Prompt Versioning**: Automatically manage and version prompts as you add or modify them. Folio increments version numbers for each updated prompt, keeping track of the entire prompt history.

* **LLM Agnostic** : Folio does not directly interact with any LLM. It only manages your prompts for you. So, you can use it with any LLM. 

* **Templating with Jinja2**: Folio uses Jinja2 templating syntax, enabling dynamic text generation. Easily include variables within prompts for customizable outputs. The biggest advantage is that you can create your own templates which can be composed to form new prompts leading to better organisation and reduced prompt redundancy. 

* **CLI and Python API Support**: Manage prompts directly from the command line or use Folio’s Python API for programmatic access and automation.



## Installation

```bash
pip install folioprompts
```

## CLI Commands

1. **Initialize a Folio Project**

   This command initializes the `folio` project in the current directory, creating the necessary folders and database.

   ```bash
   folio init
   ```

2. **Add a New Prompt**

   To add a prompt from a file:

   ```bash
   folio add <prompt_name> --file path/to/prompt.txt
   ```

   Or by piping from standard input:

   ```bash
   echo "Prompt text goes here" | folio add <prompt_name>
   ```

   You may add variable using the Jinja2 template format like this. 

   ```bash
   echo "Write a haiku about {{ topic }} " | folio add <prompt_name>
   ```


3. **List All Prompts**

   To list all prompts with their respective versions:

   ```bash
   folio list-prompts
   ```

4. **List All Versions of a Prompt**

   This lists all versions for a specific prompt:

   ```bash
   folio list-versions <prompt_name>
   ```

5. **Show a Prompt Version**

   Retrieve and display a specific version of a prompt:

   ```bash
   folio show <prompt_name> --version <version_number>
   ```

   If the version is omitted, it retrieves the latest version. You can also render a prompt with specific variables:

   ```bash
   folio show <prompt_name> --version <version_number> --render '{"key": "value"}'
   ```

6. **Delete a Prompt Version**

   Deletes a specified version of a prompt:

   ```bash
   folio delete-version <prompt_name> --version <version_number>
   ```

   To delete the latest version:

   ```bash
   folio delete-version <prompt_name> --latest
   ```

## Using Folio in Python

Folio also provides a Python API for managing prompts programmatically. Below is an example demonstrating how to initialize Folio, add prompts, and use templating with Jinja2 for prompt rendering.

### Example Workflow

1. **Initialize Folio**

   ```python
   from folioprompts import Folio

   # Initialize Folio and create necessary directories and files
   folio = Folio.init()
   ```

2. **Add a New Prompt with Templating**

   Folio uses Jinja2 templating syntax, allowing you to include variables in prompt templates. This example adds a prompt with a placeholder for the recipient's name.

   ```python
   from datetime import datetime

   prompt_text = "Write a haiku about {{ topic }}"
   folio.add_prompt("song", prompt_text)
   ```

3. **Retrieve and Render a Prompt**

   You can retrieve the latest version of a prompt and render it with specific values using Jinja2 syntax.

   ```python
   # Get the latest version of the prompt and render with variables
   rendered_prompt = folio.get_prompt(
       "song",
       render={"topic" : "Generative AI"}
   )
   print(rendered_prompt.text) 
   ```

4. **Add a New Version of the Prompt**

   Folio automatically increments the version when you update a prompt:

   ```python
   updated_prompt_text = "Compose a poem on {{ topic }} in {{ num_lines }} lines"
   folio.add_prompt("song", updated_prompt_text)
   ```

5. **List All Versions of a Prompt**

   Retrieve and display all versions of a specific prompt, along with their creation dates.

   ```python
   versions = folio.list_versions_by_prompt("song")
   for version in versions:
       print(f"Version {version.version} created on {version.created_at}")
   ```

6. **Delete a Specific Version of a Prompt**

   Folio allows you to delete a specific version or the latest version of a prompt:

   ```python
   folio.delete_version("song", version=1)
   ```

### Prompt Inheritance

Folio allows Jinja2 based prompt inheritance. For example

```python

{# prompt: cot/latest #}

{% block task %}
{% endblock %}

{% block problem_statement %}
{% endblock %}

{% block examples %}
Here are some examples
    {% for example in examples %}
        ** Example {{ loop.index }} ** : {{ example }}
    {% endfor %}
{% endblock %}

Let's think step by step

{% block ensure_output_format %}
{% endblock %}
```

This can be then extended in other templates

```python
{# prompt: ner/latest #}

{% extends 'cot/latest' %}

{% block task %}
Your task is to perform Named Entity Detection.
{% endblock %}

{% block problem_statement %}
Here is some text : {{ text }}
Detect the following entities:
- Name
- Organisation
- Currency
- Email
{% endblock %}

{% block ensure_output_format %}
Ensure the output is in JSON. Do not generate any markdown.
{% endblock %}

```
