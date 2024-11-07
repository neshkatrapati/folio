from typing import List, Optional, Union
from uuid import UUID
import os
from pydantic import BaseModel
from tinydb import TinyDB, Query
import uuid
from datetime import datetime
from .template_renderer import render_prompt

DATETIME_FMT = "%m/%d/%Y %H:%M:%S"


class Prompt(BaseModel):
    id: str
    name: str
    version: int
    text: Optional[str] = "None"
    created_at: str


class PromptAggregate(BaseModel):
    name: str
    num_versions: int


class Folio:
    def __init__(self, folio_path: Optional[str] = "folio"):
        self.folio_path = folio_path
        self.db_file_path = os.path.join(folio_path, "folio.db")
        self.prompts_path = os.path.join(folio_path, "prompts")

        self.db = TinyDB(self.db_file_path)
        self.tables = self.db.tables
        self.prompts = self.db.table('prompts')

    @staticmethod
    def init(folio_path: Optional[str] = "folio"):
        prompts_path = os.path.join(folio_path, "prompts")

        if not os.path.exists(folio_path):
            os.mkdir(folio_path)
        if not os.path.exists(prompts_path):
            os.mkdir(prompts_path)

        return Folio(folio_path)


    def get_latest_prompt(self, prompt_name) -> Optional[Prompt]:
        prompt_query = Query()
        try:
            prompts = self.prompts.search((prompt_query.name == prompt_name))
            prompts = sorted(prompts, key=lambda p: p['version'], reverse=True)
            return Prompt(**prompts[0])
        except Exception as e:
            #print(e)
            return None

    def list_prompts(self) -> Optional[List[PromptAggregate]]:
        prompt_query = Query()
        try:

            prompts = self.prompts.all()
            prompt_dict = {}
            for prompt in prompts:
                prompt = Prompt(**prompt)
                if prompt.name not in prompt_dict:
                    prompt_dict[prompt.name] = {"name": prompt.name, "num_versions": 0}
                prompt_dict[prompt.name]["num_versions"] += 1

            return [PromptAggregate(**x) for x in prompt_dict.values()]

        except Exception as e:
            # print(e)
            return None

    def list_versions_by_prompt(self, prompt_name: str) -> Optional[List[Prompt]]:
        prompt_query = Query()
        try:
            prompts = self.prompts.search((prompt_query.name == prompt_name))
            prompts = sorted(prompts, key=lambda p: p['version'], reverse=True)
           # print(prompts)
            return [Prompt(**x) for x in prompts]
        except Exception as e:
            print(e)
            return None

    def get_prompt(self, prompt_name: str, version: Optional[int] = None, render: Optional[dict] = None) -> Optional[Prompt]:
        prompt_query = Query()
        try:
            if version is None:
                prompt = self.get_latest_prompt(prompt_name)
            else:
                prompts = self.prompts.search(
                    (prompt_query.name == prompt_name) and
                    (prompt_query.version == version))

                prompt = Prompt(**prompts[0])

            prompt_file = os.path.join(self.prompts_path, prompt.name, f"{prompt.version}")
            if not os.path.exists(prompt_file):
                raise Exception(f"{prompt_file} not found under {self.prompts_path}")

            if not render:
                prompt_text = open(prompt_file, "r").read()
                prompt.text = prompt_text
            else:
                prompt_template_path = os.path.join(prompt_name, str(prompt.version))
                prompt.text = render_prompt(prompt_template_path, render)

            return prompt
        except Exception as e:
            return None

    def add_prompt(self, prompt_name, prompt_text) -> Optional[Prompt]:
        prompt_id = str(uuid.uuid4())
        prompt = self.get_latest_prompt(prompt_name)
        prompt_path = os.path.join(self.prompts_path, prompt_name)
        if prompt is None:
            prompt = Prompt(id=prompt_id, name=prompt_name, version=1, created_at=datetime.now().strftime(DATETIME_FMT))
            if not os.path.exists(prompt_path):
                os.mkdir(prompt_path)
        else:
            prompt = Prompt(id=prompt_id, name=prompt_name, version=prompt.version + 1,
                            created_at=datetime.now().strftime(DATETIME_FMT))

        self.prompts.insert(prompt.model_dump())
        prompt.text = prompt_text

        # Add version name and meta info into comments in the file
        with open(os.path.join(prompt_path, f"{prompt.version}"), "w") as f:
            f.write(prompt.text)

        with open(os.path.join(prompt_path, "latest"), "w") as f:
            f.write(prompt.text)

        return prompt

    def delete_version(self, prompt_name, version: Union[str, int]):
        prompt = None
        if version == "latest":
            prompt = self.get_latest_prompt(prompt_name)
        elif isinstance(version, int):
            prompt = self.get_prompt(prompt_name, version)
        else:
            raise Exception(f"{version} not found / bad version")

        if prompt:
            prompt_query = Query()
            latest_prompt = self.get_latest_prompt(prompt_name)

            self.prompts.remove((prompt_query.name == prompt.name) and (prompt_query.version == prompt.version))

            prompt_path = os.path.join(self.prompts_path, prompt.name, f"{prompt.version}")
            if os.path.exists(prompt_path):
                os.remove(prompt_path)

            if latest_prompt:
                # Remove the prompt if this is the latest version.
                latest_version = latest_prompt.version
                if latest_version == 1 and prompt.version == 1:
                    prompt_path = os.path.join(self.prompts_path, prompt.name, "latest")
                    if os.path.exists(prompt_path):
                        os.remove(prompt_path)

                    os.rmdir(os.path.join(self.prompts_path, prompt.name))

            if version == "latest":
                # If this is NOT the latest version, shift "latest"
                prev_prompt = self.get_prompt(prompt_name, prompt.version - 1)
                if prev_prompt:
                    prompt_path = os.path.join(self.prompts_path, prompt.name, "latest")
                    with open(prompt_path, "w") as f:
                        f.write(prev_prompt.text)

        else:
            raise Exception(f"{version} not found / bad version")



