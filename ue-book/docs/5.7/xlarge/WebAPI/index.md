# WebAPI

> Automated generation of web based APIs

| 属性 | 值 |
|---|---|
| 中文名 | Web API 生成工具 |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（模板资产、蓝图节点） |
| 模块 | `WebAPI` (Runtime), `WebAPIBlueprintGraph` (Runtime), `WebAPIEditor` (Runtime), `WebAPILiquidJS` (Runtime), `WebAPIOpenAPI` (Runtime), `PLUGIN_NAMEGenerated` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI) | |

---

## 总体用途

WebAPI 插件是一个**实验性**工具集，用于从 OpenAPI 规范自动生成 UE 的 Web API 客户端代码。它让开发者能够：

- 导入标准的 OpenAPI 文档（JSON/YAML）
- 自动解析 API 端点、模型、参数
- 生成类型安全的 C++ 类和蓝图可调用节点
- 在编辑器内预览和导出生成的代码
- 通过 LiquidJS 模板引擎自定义代码生成样式

该插件解决了手动编写 HTTP 请求、序列化/反序列化、错误处理的重复劳动，特别适合需要与 RESTful 或 GraphQL 等 Web 服务深度集成的项目。

---

## 模块列表

| 模块 | 类型 | 一句话总结 | 详细文档 |
|------|------|------------|----------|
| `WebAPI` | Runtime | 核心运行时：HTTP 请求/响应处理、模型基类、异步支持 | [WebAPI.md](./WebAPI.md) |
| `WebAPIBlueprintGraph` | Runtime | 蓝图图节点：暴露生成的 API 供蓝图调用 | [WebAPIBlueprintGraph.md](./WebAPIBlueprintGraph.md) |
| `WebAPIEditor` | Runtime | 编辑器工具：资产类型、设置面板、导入向导 | [WebAPIEditor.md](./WebAPIEditor.md) |
| `WebAPILiquidJS` | Runtime | 模板引擎：使用 LiquidJS 语法生成代码 | [WebAPILiquidJS.md](./WebAPILiquidJS.md) |
| `WebAPIOpenAPI` | Runtime | OpenAPI 解析：读取规范并转换为内部数据结构 | [WebAPIOpenAPI.md](./WebAPIOpenAPI.md) |
| `PLUGIN_NAMEGenerated` | Runtime | 生成的 API 代码模板（需按项目重命名） | [PLUGIN_NAMEGenerated.md](./PLUGIN_NAMEGenerated.md) |

---

## 使用场景

- **游戏后端对接**：你的游戏需要调用外部排行榜、商店、用户认证等 REST API，只需提供 OpenAPI 规范，一键生成类型安全的客户端。
- **工具链集成**：自动化 CI/CD 流程中从最新 API 文档生成 UE 代码，减少手工同步成本。
- **快速原型验证**：不需要手动写 HTTP 请求和 JSON 解析，开发者可以专注于业务逻辑。
- **蓝图友好**：非程序员可以拖拽蓝图节点调用生成的 API，无需编写 C++。

---

## 相关链接

- [源码（5.7 分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI)
- 官方文档：暂无（实验性插件）
- 测试用例：未在 git log 中发现独立测试目录，建议直接参考插件源码中的测试代码（若有）