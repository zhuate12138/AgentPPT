"""LangChain agents for PPT creation and editing."""

import json
from typing import List, Optional
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.core.config import get_settings
from app.models.ppt import EditInstruction, EditInstructionType, SlideSummary


# === Output Models ===

class SlideContent(BaseModel):
    """Content for a single slide."""
    title: str = Field(description="Slide title")
    body: List[str] = Field(default_factory=list, description="Bullet points or paragraphs")
    notes: Optional[str] = Field(None, description="Speaker notes (optional)")


class PPTOutline(BaseModel):
    """Outline for entire PPT."""
    title: str = Field(description="Overall presentation title")
    slides: List[SlideContent] = Field(description="List of slides with their content")


class EditInstructionsOutput(BaseModel):
    """Output from edit agent."""
    instructions: List[EditInstruction] = Field(description="List of edit instructions to apply")


# === LLM Setup ===

def get_llm():
    """Get configured LLM instance."""
    settings = get_settings()
    
    if settings.llm_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=settings.anthropic_model,
            anthropic_api_key=settings.anthropic_api_key,
        )
    else:
        # Default to OpenAI
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.openai_model,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_api_base,
        )


# === Creation Agent ===

CREATION_PROMPT = """你是一个专业的PPT内容设计师。根据用户提供的主题，创建一份结构清晰、内容丰富的演示文稿大纲。

用户主题: {topic}

{context_section}

要求:
1. 创建5-10页幻灯片（根据主题复杂度调整）
2. 每页幻灯片有明确的标题
3. 正文内容用要点列表形式呈现，每页3-6个要点
4. 内容要专业、有条理、有逻辑
5. 第一页是封面（标题页）
6. 最后一页是总结或感谢页

请以JSON格式输出大纲。

{format_instructions}
"""

CONTEXT_SECTION = """
辅助材料内容:
{additional_context}
"""

def create_ppt_chain():
    """Create a chain for generating PPT outline."""
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=PPTOutline)
    
    prompt = ChatPromptTemplate.from_template(
        CREATION_PROMPT,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = (
        {
            "topic": RunnablePassthrough(),
            "additional_context": RunnablePassthrough(),
            "context_section": lambda x: CONTEXT_SECTION.format(
                additional_context=x.get("additional_context", "")
            ) if x.get("additional_context") else ""
        }
        | prompt
        | llm
        | parser
    )
    
    return chain


async def generate_ppt_outline(
    topic: str,
    additional_context: Optional[str] = None
) -> PPTOutline:
    """Generate PPT outline from topic."""
    chain = create_ppt_chain()
    
    result = await chain.ainvoke({
        "topic": topic,
        "additional_context": additional_context or ""
    })
    
    return result


# === Edit Agent ===

EDIT_PROMPT = """你是一个PPT编辑助手。用户会描述他们想要的修改，你需要理解当前PPT内容并生成具体的编辑指令。

当前PPT概览:
{ppt_summary}

{current_slide_detail}

用户编辑请求: {user_prompt}

请分析用户的需求，生成具体的编辑指令。每个指令需要指定:
- type: 指令类型 (set_title, set_body, set_bullets, add_bullet, set_text, add_text_box, delete_shape)
- slide_index: 幻灯片索引 (从0开始)
- shape_id: 形状标识符 (可选，用于定位特定元素)
- content: 新内容文本
- bullets: 列表项 (用于set_bullets)
- position: 位置信息 (用于add_text_box)

注意:
1. slide_index 从0开始计数
2. 一次请求可以生成多个编辑指令
3. 保持修改简洁明确
4. 不要修改用户未提及的内容

{format_instructions}
"""

CURRENT_SLIDE_SECTION = """
当前操作的幻灯片详情 (第{slide_index}页):
{slide_detail}
"""

def create_edit_chain():
    """Create a chain for generating edit instructions."""
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=EditInstructionsOutput)
    
    prompt = ChatPromptTemplate.from_template(
        EDIT_PROMPT,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    return chain


async def generate_edit_instructions(
    ppt_summary: str,
    user_prompt: str,
    current_slide_index: Optional[int] = None,
    slide_detail: Optional[str] = None
) -> List[EditInstruction]:
    """Generate edit instructions from user prompt."""
    chain = create_edit_chain()
    
    # Build current slide section if provided
    if current_slide_index is not None and slide_detail:
        current_slide_section = CURRENT_SLIDE_SECTION.format(
            slide_index=current_slide_index,
            slide_detail=slide_detail
        )
    else:
        current_slide_section = ""
    
    result = await chain.ainvoke({
        "ppt_summary": ppt_summary,
        "current_slide_detail": current_slide_section,
        "user_prompt": user_prompt
    })
    
    return result.instructions


# === Summary Helper ===

def format_summary_for_llm(summary) -> str:
    """Format PPT summary for LLM context."""
    lines = [f"总页数: {summary.total_slides}"]
    
    for slide in summary.slides:
        lines.append(f"\n第 {slide.index + 1} 页:")
        if slide.title:
            lines.append(f"  标题: {slide.title}")
        if slide.body_text:
            lines.append(f"  内容: {slide.body_text[:200]}...")
        if slide.notes:
            lines.append(f"  备注: {slide.notes[:100]}...")
        if slide.has_image:
            lines.append("  [包含图片]")
        if slide.has_chart:
            lines.append("  [包含图表]")
    
    return "\n".join(lines)


def format_slide_detail_for_llm(detail) -> str:
    """Format slide detail for LLM context."""
    lines = [f"幻灯片索引: {detail.index}"]
    lines.append(f"形状数量: {len(detail.shapes)}")
    
    for i, shape in enumerate(detail.shapes):
        lines.append(f"\n形状 {i + 1}:")
        lines.append(f"  名称: {shape.get('name', 'unknown')}")
        if "text" in shape:
            text = shape["text"][:300]
            lines.append(f"  文本: {text}")
        if "paragraphs" in shape:
            lines.append(f"  段落数: {len(shape['paragraphs'])}")
    
    return "\n".join(lines)