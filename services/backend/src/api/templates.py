from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.services.template_service import list_templates, render_template

router = APIRouter(prefix="/templates", tags=["templates"])


class TemplateRenderRequest(BaseModel):
    template_name: str
    project_name: str = "Untitled Project"


class TemplateRenderResponse(BaseModel):
    source_code: str


@router.get("", response_model=list[str])
async def get_templates():
    return list_templates()


@router.post("/render", response_model=TemplateRenderResponse)
async def render_template_endpoint(data: TemplateRenderRequest):
    result = render_template(data.template_name, project_name=data.project_name)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Template '{data.template_name}' not found")
    return TemplateRenderResponse(source_code=result)
