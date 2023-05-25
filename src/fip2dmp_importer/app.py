import logging
import os
import pathlib

import fastapi
import fastapi.responses
import fastapi.staticfiles
import fastapi.templating


from .api_client import get_projects, get_project_tags, \
    get_project
from .logic import prepare_import_mapping


ROOT_DIR = pathlib.Path(__file__).parent
STATIC_DIR = ROOT_DIR / 'static'
TEMPLATES_DIR = ROOT_DIR / 'templates'
LOG = logging.getLogger(__name__)


app = fastapi.FastAPI()
app.mount(
    path='/static',
    app=fastapi.staticfiles.StaticFiles(directory=STATIC_DIR),
    name='static',
)
templates = fastapi.templating.Jinja2Templates(directory=TEMPLATES_DIR)


@app.get('/', response_class=fastapi.responses.HTMLResponse)
async def get_index(request: fastapi.Request):
    return templates.TemplateResponse(
        name='index.html.j2',
        context={
            'request': request,
            'debug': os.environ.get('FIP2DMP_DEBUG', '') == 'true',
            'development': os.environ.get('FIP2DMP_DEV', '') == 'true',
        },
    )


@app.get('/api/fips', response_class=fastapi.responses.JSONResponse)
async def list_fips(request: fastapi.Request):
    try:
        projects = await get_projects(
            query=request.query_params.get('q', ''),
            tags=request.query_params.get('tags', ''),
        )
        return fastapi.responses.JSONResponse(content=projects)
    except Exception as e:
        LOG.error(f'Error appeared: {str(e)}', exc_info=e)
        raise fastapi.HTTPException(status_code=500)


@app.get('/api/tags', response_class=fastapi.responses.JSONResponse)
async def list_tags(request: fastapi.Request):
    try:
        tags = await get_project_tags(
            query=request.query_params.get('q', ''),
            exclude=request.query_params.get('exclude', ''),
        )
        return fastapi.responses.JSONResponse(content=tags)
    except Exception as e:
        LOG.error(f'Error appeared: {str(e)}', exc_info=e)
        raise fastapi.HTTPException(status_code=500)


@app.get('/api/fips/{fip_uuid}', response_class=fastapi.responses.JSONResponse)
async def select_fip(fip_uuid: str):
    try:
        project = await get_project(
            project_uuid=fip_uuid,
        )
        result = prepare_import_mapping(project)
        return fastapi.responses.JSONResponse(content=result)
    except Exception as e:
        LOG.error(f'Error appeared: {str(e)}', exc_info=e)
        raise fastapi.HTTPException(status_code=500)
