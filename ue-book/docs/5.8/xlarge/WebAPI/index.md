# WebAPI

> Automated generation of web based APIs

| 属性 | 值 |
|---|---|
| 中文名 | Web API 生成器 |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（API 模板、蓝图节点、OpenAPI 定义） |
| 模块 | `WebAPI` (Runtime), `WebAPIBlueprintGraph` (Runtime), `WebAPIEditor` (Runtime), `WebAPILiquidJS` (Runtime), `WebAPIOpenAPI` (Runtime), `PLUGIN_NAMEGenerated` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-07-11 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Web/WebAPI) | |

## 用途

WebAPI 是 Epic 开发的实验性插件，用于从 Unreal Engine 项目自动生成基于 Web 的 API 服务。它允许开发者在引擎内定义 Web API 端点，并通过模板引擎（LiquidJS）和 OpenAPI 规范自动生成可部署的 API 代码。插件提供蓝图集成，使得非 C++ 开发者也能通过蓝图节点定义和暴露 Web 服务接口。核心目的是将 UE 项目的业务逻辑快速转化为可访问的 Web API，适用于后端服务、数据接口或微服务场景。

## 使用场景

- 你需要将 UE 游戏服务器的业务逻辑暴露为 HTTP REST API → 用 WebAPI 自动生成 API 框架
- 你需要基于 OpenAPI/Swagger 规范定义和生成标准化的 Web 服务 → 用 WebAPIOpenAPI 模块
- 你想通过蓝图而非纯 C++ 来定义 Web API 端点 → 用 WebAPIBlueprintGraph 模块
- 你需要使用 LiquidJS 模板引擎自定义 API 代码的生成格式 → 用 WebAPILiquidJS 模块
- 你想快速搭建一个与 UE 项目集成的后端服务原型 → 用 WebAPI 的完整流程

## 模块列表

| 模块 | 类型 | 说明 | 文档 |
|---|---|---|---|
| `WebAPI` | Runtime | 核心模块，提供 Web API 定义、路由、请求处理的基础架构 | [WebAPI.md](WebAPI.md) |
| `WebAPIBlueprintGraph` | Runtime | 蓝图图编辑器集成，允许通过可视化节点定义 Web API 端点 | [WebAPIBlueprintGraph.md](WebAPIBlueprintGraph.md) |
| `WebAPIEditor` | Runtime | 编辑器工具集，提供 API 管理、预览和配置界面 | [WebAPIEditor.md](WebAPIEditor.md) |
| `WebAPILiquidJS` | Runtime | LiquidJS 模板引擎集成，用于 API 代码的模板化生成 | [WebAPILiquidJS.md](WebAPILiquidJS.md) |
| `WebAPIOpenAPI` | Runtime | OpenAPI/Swagger 规范支持，实现 API 定义的标准化导入导出 | [WebAPIOpenAPI.md](WebAPIOpenAPI.md) |
| `PLUGIN_NAMEGenerated` | Runtime | 模板模块，作为生成 API 项目的代码脚手架参考 | [PLUGIN_NAMEGenerated.md](PLUGIN_NAMEGenerated.md) |

## 工作流程概览

```
API 定义（蓝图/C++/OpenAPI）
        ↓
  WebAPI 核心处理
        ↓
  WebAPILiquidJS 模板渲染
        ↓
  生成可部署的 API 代码
        ↓
  WebAPIOpenAPI 输出规范文档
```

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Web/WebAPI)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 FSharedString |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移，从 UE_LOG 更新为 UE_LOGF |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的重复字符串以释放内存 |
| 2026-02-18 | `516817d0` | PR #13954: fix(deps): on-headers is vulnerable to http response header manipulation | 修复 on-headers 依赖的 HTTP 响应头篡改漏洞 |

### 维护评价

**活跃维护**：WebAPI 插件在 2026 年持续收到更新，最近一次提交距今不到一个月。近期改动涵盖编译警告修复、性能优化（内存释放）、API 重构（FJsonObject 双字符串支持）和安全漏洞修复，表明该插件仍在积极开发中。

**注意事项**：
- 该插件仍处于 **实验性阶段**（IsExperimentalVersion=true），且默认不启用，API 可能在未来版本发生 breaking changes
- 源码规模较大（206 个文件），包含 6 个模块，架构较为复杂
- 虽然创建于 2022 年，但持续有实质性更新，适合对 Web API 自动生成有强需求的项目使用
- 建议在生产环境中谨慎使用，关注后续版本的 API 稳定性公告