"""API routes for projects."""

from datetime import datetime
from typing import List
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse

from app.models.ppt import (
    CreatePPTRequest,
    CreatePPTResponse,
    EditPPTRequest,
    EditPPTResponse,
    GetProjectResponse,
    GetSlidesResponse,
    RestoreVersionRequest,
    ConfirmEditRequest,
    CancelEditRequest,
    ProjectMeta,
    VersionMeta,
)
from app.services.ppt_service import PPTService
from app.services.preview_service import PreviewService
from app.agents.ppt_agents import (
    generate_ppt_outline,
    generate_edit_instructions,
    format_summary_for_llm,
    format_slide_detail_for_llm,
)

router = APIRouter(prefix="/projects", tags=["projects"])

ppt_service = PPTService()
preview_service = PreviewService()


@router.post("", response_model=CreatePPTResponse)
async def create_project(request: CreatePPTRequest, background_tasks: BackgroundTasks):
    """Create a new PPT project."""
    # Generate outline using LLM
    outline = await generate_ppt_outline(
        topic=request.topic,
        additional_context=request.additional_context
    )
    
    # Create project
    project_id, _ = ppt_service.create_project(
        name=outline.title or request.topic[:50],
        topic=request.topic
    )
    
    # Convert outline to slides content
    slides_content = []
    for slide in outline.slides:
        slides_content.append({
            "title": slide.title,
            "body": slide.body,
            "notes": slide.notes
        })
    
    # Create PPT
    version, slide_count = ppt_service.create_pptx(
        project_id=project_id,
        slides_content=slides_content,
        template_path=None  # TODO: support templates
    )
    
    # Generate previews in background
    pptx_path = ppt_service.get_pptx_path(project_id, version)
    if pptx_path:
        background_tasks.add_task(
            preview_service.generate_previews,
            pptx_path, project_id, version
        )
    
    # Get summary
    summary = ppt_service.get_ppt_summary(project_id, version)
    
    return CreatePPTResponse(
        project_id=project_id,
        version=version,
        slide_count=slide_count,
        summary=summary
    )


@router.get("", response_model=List[ProjectMeta])
async def list_projects():
    """List all projects."""
    return ppt_service.list_projects()


@router.get("/{project_id}", response_model=GetProjectResponse)
async def get_project(project_id: str):
    """Get project details."""
    meta = ppt_service.get_project_meta(project_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Project not found")
    
    versions = ppt_service.get_versions(project_id)
    summary = ppt_service.get_ppt_summary(project_id, meta.current_version)
    
    return GetProjectResponse(
        meta=meta,
        versions=versions,
        current_summary=summary
    )


@router.get("/{project_id}/versions/{version}/slides", response_model=GetSlidesResponse)
async def get_slides(project_id: str, version: int):
    """Get slide preview images for a version."""
    # Check if project exists
    meta = ppt_service.get_project_meta(project_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if version exists
    pptx_path = ppt_service.get_pptx_path(project_id, version)
    if not pptx_path:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Ensure previews exist
    await preview_service.generate_previews(pptx_path, project_id, version)
    
    # Get preview URLs
    urls = preview_service.get_all_preview_urls(project_id, version)
    
    slides = [
        {"index": i, "image_url": url}
        for i, url in enumerate(urls)
    ]
    
    return GetSlidesResponse(
        project_id=project_id,
        version=version,
        slides=slides
    )


@router.get("/{project_id}/versions/{version}/previews/{filename}")
async def get_preview_image(project_id: str, version: int, filename: str):
    """Serve a preview image."""
    preview_dir = Path(ppt_service.settings.data_dir) / "projects" / project_id / f"v{version}" / "previews"
    image_path = preview_dir / filename
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Preview not found")
    
    return FileResponse(
        image_path,
        media_type="image/png",
        filename=filename
    )


@router.get("/{project_id}/versions/{version}/download")
async def download_pptx(project_id: str, version: int):
    """Download PPT file."""
    pptx_path = ppt_service.get_pptx_path(project_id, version)
    if not pptx_path:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return FileResponse(
        pptx_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"{project_id}_v{version}.pptx"
    )


@router.get("/{project_id}/versions/{version}/summary")
async def get_version_summary(project_id: str, version: int):
    """Get structured summary of a PPT version."""
    try:
        summary = ppt_service.get_ppt_summary(project_id, version)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{project_id}/versions/{version}/slides/{slide_index}")
async def get_slide_detail(project_id: str, version: int, slide_index: int):
    """Get detailed content of a specific slide."""
    try:
        detail = ppt_service.get_slide_detail(project_id, version, slide_index)
        return detail
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{project_id}/edit", response_model=EditPPTResponse)
async def edit_ppt(project_id: str, request: EditPPTRequest, background_tasks: BackgroundTasks):
    """Edit a PPT using natural language."""
    # Check for pending edits
    pending = ppt_service.has_pending_edit(project_id)
    if pending:
        raise HTTPException(
            status_code=400, 
            detail=f"Another edit is pending (version {pending}). Please confirm or cancel first."
        )
    
    # Get PPT summary for context
    summary = ppt_service.get_ppt_summary(project_id, request.version)
    summary_text = format_summary_for_llm(summary)
    
    # Get current slide detail if specified
    slide_detail_text = None
    if request.current_slide_index is not None:
        try:
            detail = ppt_service.get_slide_detail(project_id, request.version, request.current_slide_index)
            slide_detail_text = format_slide_detail_for_llm(detail)
        except:
            pass
    
    # Generate edit instructions
    instructions = await generate_edit_instructions(
        ppt_summary=summary_text,
        user_prompt=request.prompt,
        current_slide_index=request.current_slide_index,
        slide_detail=slide_detail_text
    )
    
    if not instructions:
        # No instructions generated - return empty edit
        return EditPPTResponse(
            project_id=project_id,
            old_version=request.version,
            new_version=request.version,
            is_confirmed=False,
            instructions_executed=[],
            preview_images=[]
        )
    
    # Execute instructions
    new_version, executed = ppt_service.execute_edit_instructions(
        project_id=project_id,
        version=request.version,
        instructions=instructions
    )
    
    # Generate previews for new version
    pptx_path = ppt_service.get_pptx_path(project_id, new_version)
    if pptx_path:
        await preview_service.generate_previews(pptx_path, project_id, new_version)
    
    # Get preview URLs
    preview_urls = preview_service.get_all_preview_urls(project_id, new_version)
    
    return EditPPTResponse(
        project_id=project_id,
        old_version=request.version,
        new_version=new_version,
        is_confirmed=False,
        instructions_executed=executed,
        preview_images=preview_urls
    )


@router.post("/{project_id}/confirm")
async def confirm_edit(project_id: str, request: ConfirmEditRequest):
    """Confirm a pending edit."""
    success = ppt_service.confirm_edit(project_id, request.version)
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="No pending edit found for this version"
        )
    return {"status": "confirmed", "version": request.version}


@router.post("/{project_id}/cancel")
async def cancel_edit(project_id: str, request: CancelEditRequest):
    """Cancel a pending edit."""
    success = ppt_service.cancel_edit(project_id, request.version)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="No pending edit found for this version"
        )
    return {"status": "cancelled", "version": request.version}


@router.post("/{project_id}/restore")
async def restore_version(project_id: str, request: RestoreVersionRequest):
    """Restore to a specific version."""
    success = ppt_service.restore_version(project_id, request.target_version)
    if not success:
        raise HTTPException(status_code=404, detail="Target version not found")
    
    # Get new version number
    meta = ppt_service.get_project_meta(project_id)
    return {"status": "restored", "new_version": meta.current_version}


@router.post("/{project_id}/materials")
async def upload_material(
    project_id: str,
    file: UploadFile = File(...),
    material_type: str = Form("document")
):
    """Upload a material file (document or template)."""
    # Check project exists
    meta = ppt_service.get_project_meta(project_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Save file
    materials_dir = Path(ppt_service.settings.data_dir) / "projects" / project_id / "materials"
    materials_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = materials_dir / file.filename
    content = await file.read()
    
    # Validate file size
    max_size = ppt_service.settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail=f"File too large. Max {ppt_service.settings.max_upload_size_mb}MB")
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {
        "filename": file.filename,
        "material_type": material_type,
        "size_bytes": len(content)
    }


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Delete a project."""
    import shutil
    
    project_dir = Path(ppt_service.settings.data_dir) / "projects" / project_id
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    shutil.rmtree(project_dir)
    return {"status": "deleted"}