from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel
from tinydb import TinyDB, Query
import uuid
from datetime import datetime


DATETIME_FMT = "%m/%d/%Y %H:%M:%S"


class Project(BaseModel):
    id:str
    name:str
    created_at:str

class Prompt(BaseModel):
    id:str
    project_id:str
    name:str
    text:str
    version:int
    created_at:str

class PromptAggregate(BaseModel):
    project:Project
    name:str
    num_versions:int



class Folio:
    def __init__(self, db_file_path: str):
        self.db = TinyDB(db_file_path)
        self.tables = self.db.tables
        self.projects = self.db.table('projects')
        self.prompts = self.db.table('prompts')


    def create_project(self, project_name:str) -> str:
        project_id = str(uuid.uuid4())
        project = Project(id=project_id, name=project_name, created_at = datetime.now().strftime(DATETIME_FMT))
        self.projects.insert(project.model_dump())
        return project_id

    def list_projects(self) -> List[Project]:
        all_projects = [Project(**x) for x in self.projects.all()]
        return all_projects

    def find_project_by_name(self, project_name:str) -> Optional[Project]:
        proj_query = Query()
        try:
            project = self.projects.search(proj_query.name == project_name)
            return Project(**project[0])
        except Exception as e:
            return None

    def get_latest_prompt(self, project, prompt_name) -> Optional[Prompt]:
        prompt_query = Query()
        try:
            prompts = self.prompts.search((prompt_query.name == prompt_name) & (prompt_query.project_id == project.id))
            prompts = sorted(prompts, key=lambda p: p['version'], reverse=True)
            return Prompt(**prompts[0])
        except Exception as e:
            #print(e)
            return None

    def list_prompts_by_project_name(self, project_name:str) -> Optional[List[PromptAggregate]]:
        prompt_query = Query()
        try:
            project = self.find_project_by_name(project_name)
            prompts = self.prompts.search(prompt_query.project_id == project.id)
            prompt_dict = {}
            for prompt in prompts:
                prompt = Prompt(**prompt)
                if prompt.name not in prompt_dict:
                    prompt_dict[prompt.name] = {"project": project, "name": prompt.name, "num_versions":0}
                prompt_dict[prompt.name]["num_versions"] += 1

            return [PromptAggregate(**x) for x in prompt_dict.values()]

        except Exception as e:
            # print(e)
            return None

    def list_versions_by_prompt(self, project_name:str, prompt_name:str) -> Optional[List[Prompt]]:
        prompt_query = Query()
        try:
            project = self.find_project_by_name(project_name)
            prompts = self.prompts.search((prompt_query.project_id == project.id) and (prompt_query.name == prompt_name))
            prompts = sorted(prompts, key=lambda p: p['version'], reverse=True)
            return [Prompt(**x) for x in prompts]
        except Exception as e:
            # print(e)
            return None

    def get_prompt(self, project_name:str, prompt_name:str, version:Optional[int] = None) -> Optional[Prompt]:
        prompt_query = Query()
        try:
            project = self.find_project_by_name(project_name)

            if version is None:
                prompt = self.get_latest_prompt(project, prompt_name)
            else:
                prompts = self.prompts.search(
                    (prompt_query.project_id == project.id) and
                    (prompt_query.name == prompt_name) and
                    (prompt_query.version == version))

                prompt = Prompt(**prompts[0])
            return prompt
        except Exception as e:
            return None


    def add_prompt(self, project_name, prompt_name, prompt_text) -> Optional[Prompt]:
        prompt_id = str(uuid.uuid4())
        project = self.find_project_by_name(project_name)
        if project is not None:
            project_id = project.id
            prompt = self.get_latest_prompt(project, prompt_name)
            if prompt is None:
                prompt = Prompt(id=prompt_id, project_id=project_id, name=prompt_name, text=prompt_text, version=1, created_at = datetime.now().strftime(DATETIME_FMT))
            else:
                prompt = Prompt(id=prompt_id, project_id=project_id, name=prompt_name, text=prompt_text, version=prompt.version + 1, created_at = datetime.now().strftime(DATETIME_FMT))

            self.prompts.insert(prompt.model_dump())
            return prompt
        return None