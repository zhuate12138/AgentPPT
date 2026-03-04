# AgentPPT API 文档

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **Content-Type**: `application/json`
- **Swagger UI**: `http://localhost:8000/docs`

---

## 项目管理

### 创建项目

**POST** `/projects`

创建一个新的 PPT 项目。

**请求体**:
```json
{
  "topic": "人工智能在教育领域的应用",
  "mode": "no_template",
  "additional_context": "重点关注中国教育市场"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| topic | string | ✅ | PPT 主题 |
| mode | string | ❌ | 创建模式：`no_template` 或 `with_template` |
| template_id | string | ❌ | 模板 ID（mode 为 with_template 时） |
| additional_context | string | ❌ | 补充说明 |

**响应**:
```json
{
  "project_id": "abc12345",
  "version": 1,
  "slide_count": 6,
  "summary": {
    "total_slides": 6,
    "slides": [
      {"index": 0, "title": "封面", "body_text": null, "has_image": false, "has_chart": false}
    ]
  }
}
```

---

### 获取项目列表

**GET** `/projects`

**响应**:
```json
[
  {
    "id": "abc12345",
    "name": "人工智能在教育领域的应用",
    "created_at": "2026-03-04T10:00:00",
    "updated_at": "2026-03-04T11:00:00",
    "current_version": 2,
    "total_versions": 2,
    "topic": "人工智能在教育领域的应用"
  }
]
```

---

### 获取项目详情

**GET** `/projects/{project_id}`

**响应**:
```json
{
  "meta": {
    "id": "abc12345",
    "name": "项目名称",
    "created_at": "2026-03-04T10:00:00",
    "updated_at": "2026-03-04T11:00:00",
    "current_version": 2,
    "total_versions": 2
  },
  "versions": [
    {"version": 1, "created_at": "...", "description": "Initial creation", "is_confirmed": true},
    {"version": 2, "created_at": "...", "description": "Edit from version 1", "is_confirmed": true}
  ],
  "current_summary": {
    "total_slides": 6,
    "slides": [...]
  }
}
```

---

## 幻灯片与预览

### 获取幻灯片预览

**GET** `/projects/{project_id}/versions/{version}/slides`

**响应**:
```json
{
  "project_id": "abc12345",
  "version": 1,
  "slides": [
    {"index": 0, "image_url": "/api/v1/projects/abc12345/versions/1/previews/slide_0.png"},
    {"index": 1, "image_url": "/api/v1/projects/abc12345/versions/1/previews/slide_1.png"}
  ]
}
```

---

### 获取单张预览图

**GET** `/projects/{project_id}/versions/{version}/previews/slide_{index}.png`

返回 PNG 图片。

---

### 获取幻灯片详情

**GET** `/projects/{project_id}/versions/{version}/slides/{slide_index}`

**响应**:
```json
{
  "index": 0,
  "shapes": [
    {
      "name": "TextBox 1",
      "type": "TEXT_BOX",
      "text": "标题文本",
      "paragraphs": ["标题文本"],
      "left": 457200,
      "top": 457200
    }
  ]
}
```

---

### 下载 PPT

**GET** `/projects/{project_id}/versions/{version}/download`

返回 `.pptx` 文件下载。

---

## 编辑操作

### 编辑 PPT

**POST** `/projects/{project_id}/edit`

**请求体**:
```json
{
  "version": 1,
  "prompt": "把第三页的标题改成「人工智能的发展历程」",
  "current_slide_index": 2
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| version | int | ✅ | 基于哪个版本编辑 |
| prompt | string | ✅ | 编辑指令（自然语言） |
| current_slide_index | int | ❌ | 当前查看的幻灯片索引 |

**响应**:
```json
{
  "project_id": "abc12345",
  "old_version": 1,
  "new_version": 2,
  "is_confirmed": false,
  "instructions_executed": [
    {"type": "set_title", "slide_index": 2, "content": "人工智能的发展历程"}
  ],
  "preview_images": ["/api/v1/projects/.../previews/slide_0.png", ...]
}
```

---

### 确认编辑

**POST** `/projects/{project_id}/confirm`

**请求体**:
```json
{
  "version": 2
}
```

**响应**:
```json
{"status": "confirmed", "version": 2}
```

---

### 取消编辑

**POST** `/projects/{project_id}/cancel`

**请求体**:
```json
{
  "version": 2
}
```

**响应**:
```json
{"status": "cancelled", "version": 2}
```

---

## 版本管理

### 恢复版本

**POST** `/projects/{project_id}/restore`

**请求体**:
```json
{
  "target_version": 1
}
```

**响应**:
```json
{"status": "restored", "new_version": 3}
```

---

## 材料上传

### 上传材料

**POST** `/projects/{project_id}/materials`

Content-Type: `multipart/form-data`

| 字段 | 类型 | 说明 |
|------|------|------|
| file | File | 上传的文件 |
| material_type | string | 类型：`document` 或 `template` |

**响应**:
```json
{
  "filename": "document.docx",
  "material_type": "document",
  "size_bytes": 12345
}
```

---

## 错误响应

所有错误响应格式：

```json
{
  "detail": "错误描述信息"
}
```

常见 HTTP 状态码：

| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |