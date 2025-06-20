# 产品需求文档 (PRD): Markdown 文件转 Word API 服务

## 1. 文档信息

### 1.1 版本历史

| 版本 | 日期       | 作者 | 变更说明         |
| ---- | ---------- | ---- | ---------------- | 
| 0.1  | (今天日期) | Trae AI | 初稿             |

### 1.2 文档目的

本文档旨在明确定义“Markdown 文件转 Word API 服务”的产品需求，作为产品设计、开发、测试和上线的基础依据，确保各团队对产品目标和功能有一致的理解。

### 1.3 相关文档引用

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- 项目内部 `tools/md2docx.py` 功能说明 (如有)

## 2. 产品概述

### 2.1 产品名称与定位

- **产品名称**: MD2Word API
- **产品定位**: 一个轻量级、高效的API服务，提供将用户上传的Markdown文件实时转换为Word (.docx) 格式的功能。

### 2.2 产品愿景与使命

- **愿景**: 简化文档格式转换流程，提高用户处理Markdown文档的效率。
- **使命**: 提供一个稳定、易于集成的API接口，赋能开发者和应用快速实现Markdown到Word的转换能力。

### 2.3 价值主张与独特卖点 (USP)

- **价值主张**: 快速、便捷地将Markdown内容转换为专业排版的Word文档，无需手动操作或安装复杂软件。
- **独特卖点 (USP)**:
    - **API驱动**: 方便集成到现有工作流或应用中。
    - **基于FastAPI**: 高性能，自动生成交互式API文档。
    - **利用现有工具**: 复用项目内成熟的 `md2docx` 转换逻辑，保证转换质量。

### 2.4 目标平台列表

- Web API (可通过HTTP请求访问)

### 2.5 产品核心假设

- 用户有将Markdown文件转换为Word文档的需求。
- 用户偏好通过API方式进行集成，而不是手动转换。
- 现有的 `tools/md2docx.py` 脚本功能稳定且能满足基本的转换需求。

### 2.6 商业模式概述 (如适用)

- 初期作为内部工具或免费服务。未来可考虑基于调用量、高级功能（如自定义模板）等进行扩展。

## 3. 用户研究

### 3.1 目标用户画像 (详细)

- **用户类型1: 开发者/技术团队**
    - **人口统计特征**: 22-45岁，软件工程师、技术文档撰写者。
    - **行为习惯与偏好**: 习惯使用Markdown编写文档、笔记、博客；追求自动化和效率；熟悉API调用和集成。
    - **核心需求与痛点**: 需要将Markdown格式的技术文档、报告等转换为Word格式，以便与非技术人员共享或用于正式场合；手动转换耗时且容易出错。
    - **动机与目标**: 快速将Markdown内容集成到需要Word输出的系统中；减少手动转换工作量。

- **用户类型2: 内容创作者/运营人员**
    - **人口统计特征**: 20-35岁，内容编辑、市场专员、博主。
    - **行为习惯与偏好**: 可能使用Markdown进行内容创作，但最终交付物可能需要Word格式。
    - **核心需求与痛点**: 需要将Markdown草稿转换为Word进行排版、审阅或发布。
    - **动机与目标**: 简化从Markdown到Word的转换步骤，提高内容生产效率。

### 3.2 用户场景分析

- **核心使用场景1: 自动化文档生成系统**
    - 描述: 某公司内部系统自动从代码注释或版本控制中提取信息生成Markdown格式的更新日志或技术文档。该系统需要将这些Markdown文件自动转换为Word文档，供项目经理或客户审阅。
    - 流程: 系统后台服务定时或按需调用MD2Word API，上传生成的Markdown文件，获取转换后的Word文档并存储或分发。

- **核心使用场景2: 个人博客/内容管理平台**
    - 描述: 一个内容管理平台允许用户使用Markdown写作。平台希望提供一个“导出为Word”的功能。
    - 流程: 用户在平台上点击“导出为Word”按钮，平台后端调用MD2Word API，上传用户的Markdown内容，并将返回的Word文件提供给用户下载。

### 3.3 用户调研洞察 (如适用)

- 调研显示，许多用户认为现有的在线转换工具广告多、隐私性差或转换效果不理想。
- API方式的转换服务对于需要批量处理或集成的用户具有吸引力。

## 4. 市场与竞品分析

### 4.1 市场规模与增长预测

- 文档处理和格式转换是办公和内容创作领域的持续需求。随着Markdown的普及，其与其他格式转换的需求也在增加。

### 4.2 行业趋势分析

- API化服务是趋势，便于集成和自动化。
- 云端处理逐渐取代本地软件安装。

### 4.3 竞争格局分析

- **直接竞争对手**: 
    - Pandoc (命令行工具，功能强大但集成略复杂)
    - 各种在线Markdown转Word网站 (易用性好，但可能存在隐私、广告或批量处理限制问题)
    - 其他提供类似转换API的服务。
- **间接竞争对手**: 
    - Office Word等本地编辑软件 (用户直接在Word中编辑)

### 4.4 竞品功能对比矩阵

| 特性         | MD2Word API (本项目) | Pandoc CLI | 在线转换网站 | 其他API服务 |
| ------------ | -------------------- | ---------- | ------------ | ----------- |
| 部署方式     | API (FastAPI)        | 本地命令行 | Web          | API         |
| 易用性 (集成)| 高 (HTTP)            | 中         | 低 (手动)    | 高          |
| 转换核心     | `tools/md2docx.py`   | Pandoc引擎 | 各自实现     | 各自实现    |
| 批量处理     | 支持                 | 支持       | 可能受限     | 通常支持    |
| 交互式文档   | 是 (Swagger/ReDoc)   | 否         | 否           | 可能有      |
| 定制化       | 有限 (基于现有工具)  | 高         | 低           | 不一        |

### 4.5 市场差异化策略

- **专注与集成**: 提供一个简单、稳定、易于集成的API，专注于做好Markdown到Word的转换。
- **利用现有优势**: 复用项目内已验证的 `md2docx.py` 核心逻辑，保证转换质量和开发效率。
- **开发者友好**: 基于FastAPI，提供良好的API文档和开发体验。

## 5. 产品功能需求

### 5.1 功能架构与模块划分


- **文件接收与验证模块**: 处理文件上传，校验文件类型和大小。
- **Markdown转Word核心处理模块**: 调用 `md2docx.py` 执行转换。
- **文件响应模块**: 将生成的 .docx 文件作为HTTP响应返回给客户端。
- **错误处理模块**: 处理各种异常情况并返回合适的错误信息。

### 5.2 核心功能详述

#### 5.2.1 [功能模块1] Markdown文件上传与转换API

- **功能描述 (用户故事格式)**:
    - 作为 API 调用者, 我想要通过一个HTTP POST请求上传一个Markdown文件, 以便将其转换为Word文档。
    - 作为 API 调用者, 我想要在成功转换后接收到一个Word (.docx) 文件供下载, 以便我可以使用转换后的文档。
    - 作为 API 调用者, 我想要在上传无效文件或转换失败时收到明确的错误提示, 以便我了解问题所在。

- **用户价值**: 
    - 自动化Markdown到Word的转换流程。
    - 方便地将转换功能集成到其他应用程序或脚本中。

- **功能逻辑与规则**:
    1.  **API端点**: `POST /convert/md-to-docx/`
    2.  **请求**: 
        -   Method: `POST`
        -   Content-Type: `multipart/form-data`
        -   Body: 包含一个名为 `file` 的文件字段，该字段为用户上传的Markdown文件。
    3.  **处理流程**:
        a.  API接收到请求。
        b.  验证上传的文件：
            -   文件是否存在。
            -   文件扩展名是否为 `.md`。
            -   文件大小是否在允许范围内 (例如，不超过10MB，可配置)。
            -   如果验证失败，返回相应的HTTP错误状态码 (如400 Bad Request) 和错误信息。
        c.  将上传的Markdown文件保存到服务器的临时位置。
        d.  调用 `tools.md2docx.get_markdown_to_word_tool()` 获取转换工具实例。
        e.  调用工具的 `run` 方法，传入参数：
            -   `input_path`: 临时保存的Markdown文件路径。
            -   `output_path`: 指定一个临时的Word输出文件路径。
            -   `keep_bookmarks` (可选，根据 `md2docx` 工具能力设定，默认为False或True)。
        f.  如果 `md2docx` 工具执行成功：
            -   将生成的Word (.docx) 文件作为 `FileResponse` 返回给客户端。
            -   设置 `Content-Disposition` 头部，使浏览器提示下载，文件名可以基于上传文件名或固定名称 (如 `converted_document.docx`)。
            -   HTTP状态码：200 OK。
        g.  如果 `md2docx` 工具执行失败：
            -   记录错误日志。
            -   返回相应的HTTP错误状态码 (如500 Internal Server Error) 和错误信息。
        h.  清理临时文件 (上传的.md和生成的.docx)。
    4.  **边界条件**:
        -   上传空文件。
        -   上传非Markdown文件。
        -   上传超大文件。
        -   Markdown文件内容格式错误导致转换失败。
        -   服务器磁盘空间不足无法保存临时文件。
    5.  **异常处理**:
        -   文件读写错误。
        -   `md2docx` 内部转换错误。
        -   详细记录服务端日志。

- **交互要求**:
    -   API应遵循标准的HTTP状态码和RESTful原则。
    -   FastAPI将自动生成Swagger UI和ReDoc，提供交互式API文档。

- **数据需求**:
    -   输入: Markdown文件 (`.md`)
    -   输出: Word文件 (`.docx`)
    -   临时存储: 需要临时空间存储上传和转换过程中的文件。

- **技术依赖**:
    -   FastAPI
    -   Uvicorn (或其他ASGI服务器)
    -   `python-multipart` (用于FastAPI处理文件上传)
    -   项目内 `tools.md2docx` 及其所有依赖 (如 `pypandoc`, `python-docx` 等)

- **验收标准**:
    1.  成功场景: 用户上传一个有效的 `.md` 文件，API返回一个包含正确转换内容的 `.docx` 文件，HTTP状态码为200。
    2.  失败场景 (无效输入): 
        -   用户未上传文件，API返回400错误及提示信息。
        -   用户上传非 `.md` 文件，API返回400错误及提示信息。
        -   用户上传文件过大 (超出限制)，API返回413错误 (Payload Too Large) 或400错误及提示信息。
    3.  失败场景 (转换错误): Markdown文件内容导致 `md2docx` 转换失败，API返回500错误及适当的错误信息。
    4.  API文档: `/docs` 和 `/redoc` 路径可访问，并正确显示API端点信息。
    5.  临时文件: 转换完成后，服务器上的临时文件应被清理。

### 5.3 次要功能描述 (可简化结构)

-   **健康检查端点**: `GET /health`
    -   描述: 提供一个简单的健康检查端点，返回服务状态 (如 `{"status": "ok"}` )。
    -   价值: 便于监控和部署。
    -   验收标准: 访问 `/health` 返回200 OK和指定JSON响应。

### 5.4 未来功能储备 (Backlog)

-   支持上传zip文件包含多个Markdown文件进行批量转换。
-   支持通过URL传递Markdown内容进行转换。
-   提供回调URL机制，用于异步转换大文件。
-   用户自定义转换模板或样式。
-   API密钥认证和速率限制。

## 6. 用户流程与交互设计指导

### 6.1 核心用户旅程地图

```mermaid
sequenceDiagram
    participant Client as API 调用者
    participant Server as MD2Word API

    Client->>+Server: POST /convert/md-to-docx/ (上传.md文件)
    Server->>Server: 验证文件 (类型, 大小)
    alt 文件无效
        Server-->>-Client: HTTP 400/413 (错误信息)
    else 文件有效
        Server->>Server: 保存临时.md文件
        Server->>Server: 调用 md2docx 进行转换
        alt 转换失败
            Server-->>-Client: HTTP 500 (错误信息)
        else 转换成功
            Server->>Server: 生成临时.docx文件
            Server-->>-Client: HTTP 200 (返回.docx文件供下载)
        end
        Server->>Server: 清理临时文件
    end
```

### 6.2 关键流程详述与状态转换图

(已在5.2.1功能逻辑与规则中详细描述)

### 6.3 对设计师 (UI/UX Agent) 的界面原型参考说明和要求

-   由于是API服务，主要界面是FastAPI自动生成的Swagger UI / ReDoc。
-   确保API文档清晰易懂，参数说明完整。
-   错误信息应友好且具有指导性。

### 6.4 交互设计规范与原则建议 (如适用)

-   遵循RESTful API设计原则。
-   使用标准的HTTP状态码。
-   错误响应体格式统一 (例如 `{"detail": "error message"}` )。

## 7. 非功能需求

### 7.1 性能需求

-   **响应时间**: 对于1MB以内的Markdown文件，转换和响应时间应在5秒内 (不含网络传输时间)。
-   **并发量**: 初期支持至少5个并发请求处理能力。
-   **稳定性**: 服务应能长时间稳定运行，错误率低于0.1%。
-   **资源使用率**: 合理使用CPU和内存资源，避免泄露。

### 7.2 安全需求

-   **输入验证**: 严格验证上传文件类型、大小，防止恶意文件上传。
-   **临时文件处理**: 确保临时文件在处理完毕后被安全删除，避免数据泄露。
-   **依赖安全**: 定期更新依赖库，防止已知漏洞。
-   (未来) API密钥认证，防止未授权访问。

### 7.3 可用性与可访问性标准

-   **API文档**: FastAPI自动生成的文档应清晰、准确、易于理解。
-   **错误处理**: API返回的错误信息应明确指出问题原因。
-   **服务可用性**: 目标99.9%的可用时间。

### 7.4 合规性要求 (如 GDPR, 行业法规等)

-   不存储用户上传的原始文件和转换后的文件，仅在处理期间临时保存。
-   明确告知用户数据处理方式 (如果需要公开服务)。

### 7.5 数据统计与分析需求

-   记录API调用次数。
-   记录成功转换次数和失败转换次数。
-   统计平均转换时间。
-   (可选) 记录常见错误类型。

## 8. 技术架构考量

### 8.1 技术栈建议

-   **后端框架**: FastAPI (Python)
-   **ASGI服务器**: Uvicorn
-   **核心转换逻辑**: 复用项目内 `tools/md2docx.py`
-   **依赖管理**: `requirements.txt`

### 8.2 系统集成需求

-   API服务需要能够访问和执行 `tools/md2docx.py` 脚本及其依赖。

### 8.3 技术依赖与约束

-   依赖Python环境及 `requirements.txt` 中列出的所有包。
-   `md2docx.py` 脚本的稳定性和性能将直接影响API服务。
-   服务器需要有足够的磁盘空间处理临时文件。

### 8.4 数据模型建议

-   无持久化数据存储需求，主要处理临时文件流。

## 9. 验收标准汇总

### 9.1 功能验收标准矩阵

| 功能点                     | 验收标准                                                                                                                               |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Markdown文件上传与转换API  | 见 5.2.1 验收标准                                                                                                                      |
| 健康检查端点               | 访问 `/health` 返回HTTP 200 和 `{"status": "ok"}`                                                                                      |

### 9.2 性能验收标准

-   1MB文件转换响应时间 < 5秒。
-   支持至少5个并发请求。

### 9.3 质量验收标准

-   代码覆盖率 > 80% (针对API逻辑部分)。
-   错误率 < 0.1%。
-   无内存泄漏。

## 10. 产品成功指标

### 10.1 关键绩效指标 (KPIs) 定义与目标

-   **API调用总次数**: (目标: 上线后首月达到1000次)
-   **成功转换率**: (成功转换次数 / API调用总次数) * 100% (目标: > 98%)
-   **平均转换时间**: (目标: < 3秒)
-   **API错误率**: (失败请求数 / 总请求数) * 100% (目标: < 2%)

### 10.2 北极星指标定义与选择依据

-   **北极星指标**: **成功转换次数**
-   **选择依据**: 该指标直接反映了API的核心价值是否被用户有效利用。

### 10.3 指标监测计划

-   通过FastAPI的中间件或日志系统记录API调用相关数据。
-   定期 (如每日/每周) 分析日志生成报表。
-   使用监控工具 (如Prometheus/Grafana，如果部署规模扩大) 实时监控服务状态和性能指标。