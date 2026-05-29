# PCG External Data Interop

> Extra plugin for Procedural Content Generation Framework interacting with external data formats.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | PCG外部数据互操作 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PCGExternalDataInterop` (Runtime), `PCGExternalDataInteropEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-08-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGExternalDataInterop) | |

## 用途

这个插件为 UE5 的 Procedural Content Generation Framework (PCG) 提供了与外部数据格式（如 CSV、JSON、XML、Alembic 等）的互操作能力。它解决了 PCG 框架需要从外部文件或数据源读取和写入数据的问题，使得程序化内容生成工作流可以与外部数据工具链（如 DCC 软件、数据管理工具）进行集成。

## 使用场景

- 当你需要使用 PCG 框架根据外部 CSV 文件中的点、线或面数据来生成场景几何体时。
- 你需要将 PCG 框架生成的结果导出为 JSON 或其他格式，供其他软件或流水线使用。
- 你的 PCG 图表需要读取外部 Alembic 文件中的几何体数据作为生成输入。
- 在电影或视觉特效制作中，需要将 Houdini 或其他 DCC 工具生成的数据导入到 UE5 的 PCG 流程中。

## 蓝图用法

此插件为编辑器扩展，主要提供 C++ API 和数据导入/导出功能，没有直接暴露蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "PCGExternalDataInterop.h"
```

### 基本用法

此插件的 C++ 用法主要涉及通过 PCG 上下文访问外部数据资源。具体 API 需参考模块文档。

## Demo 示例

无独立的 Demo 示例。建议参考 UE5 官方文档中关于 PCG 与外部数据交互的教程和示例项目。

## 模块依赖

此插件无特殊依赖（仅标准 Core/Engine/Slate 等）。它主要依赖于 PCG 框架本身。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志系统到新版UE_LOGF宏 |
| 2026-01-09 | `49c11077` | [UObject] | UObject系统相关更新 |
| 2025-09-23 | `e22e769b` | [PCG] Better management of windows headers wrt alembic files | 改进Windows头文件与Alembic文件的兼容性管理 |
| 2025-09-23 | `68b1d8a9` | [PCG] Moved code to implementation file for better isolation. Also removed GetObject define that cou | 将代码移至实现文件以提高隔离性，并移除了可能冲突的GetObject宏定义 |
| 2025-05-14 | `6bd1bdeb` | Fix compile error because winnt.h is included by Alembic includes, which redefines MemoryBarrier, th | 修复因Alembic包含winnt.h导致MemoryBarrier宏重定义引起的编译错误 |

### 维护评价

该插件创建于2024年8月，相对较新。从提交历史看，它仍在积极维护中，最近一次更新在2026年4月。更新内容主要包括兼容性改进、编译错误修复和代码结构优化，表明 Epic Games 持续关注其稳定性和跨平台兼容性。该插件是 PCG 框架的重要补充，适合需要与外部数据流水线集成的项目使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGExternalDataInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)