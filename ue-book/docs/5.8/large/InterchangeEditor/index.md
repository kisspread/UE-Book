# Interchange Editor

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | Interchange编辑器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditor` (Runtime), `InterchangeEditorPipelines` (Runtime), `InterchangeEditorUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-01-01 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor) | |

## 用途

这个插件是UE5资产导入系统（Interchange）的**编辑器端实现**。它解决的核心问题是：如何将通用的Interchange导入框架（定义格式解析、数据转换逻辑）与虚幻编辑器的具体操作（如文件浏览器拖放、导入对话框、内容浏览器集成）连接起来。

简单来说，Interchange框架是底层的"翻译引擎"，而这个插件是引擎的"驾驶舱"，负责：
1.  **暴露UI**：在编辑器菜单、内容浏览器右键菜单中添加导入选项。
2.  **管理管道**：将Interchange框架定义的抽象导入管道（Pipeline）实例化并应用到实际资产上。
3.  **提供工具**：为开发者提供编辑器脚本和工具，用于调试、测试和扩展导入流程。

## 使用场景

-   你需要从FBX、glTF、USD等格式导入静态网格、骨骼网格、动画、材质等资产到UE编辑器中 → Interchange Editor是这个流程的UI入口和管道协调者。
-   作为插件开发者，你想为新的文件格式创建自定义导入器，并需要将其集成到编辑器的UI中 → 你需要使用此插件的框架来注册你的Translator和Pipeline。
-   你需要通过编辑器脚本（蓝图或Python）自动化资产导入流程 → 可以使用此插件提供的脚本库功能。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `InterchangeEditor` | Runtime | 核心编辑器模块，负责注册编辑器菜单项、处理导入对话框、协调导入流程。 |
| `InterchangeEditorPipelines` | Runtime | 提供一组默认的编辑器导入管道（Pipeline），将Interchange解析出的节点图转换为具体的UE资产（如UStaticMesh， USkeleton）。 |
| `InterchangeEditorUtilities` | Runtime | 提供实用工具函数和脚本库（`UInterchangeEditorScriptLibrary`），方便在编辑器蓝图或Python中查询和操作Interchange场景图和导入结果。 |

## 源码结构概览

```
Engine/Plugins/Interchange/Editor/
├── Source/
│   ├── InterchangeEditor/         # 核心编辑器模块
│   ├── Pipelines/                 # 默认的编辑器导入管道
│   └── Utilities/                 # 工具与脚本库
└── InterchangeEditor.uplugin
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `fb1426e8` | [PackageAutoSaver] Add the ability to temporarily suspend the autosaver. | 修复与自动保存包的冲突，允许临时挂起自动保存器。 |
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 简化动画导入逻辑，移除了特定的帧对齐器。 |
| 2026-04-22 | `cc360b1e` | Add accessor to InterchangeEditorScriptLibrary that returns actors in a level instance without loading the whole level. | 新增脚本库API，可无负载地获取关卡实例中的Actor。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统迁移至UE_LOGF，提高日志输出的结构化和过滤能力。 |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings. | 重构静态网格和骨骼网格的导入设置，优化工作流和用户体验。 |

### 维护评价

-   **维护状态**：**活跃维护**。插件由Epic Games官方维护，最近一次更新在2026年5月，更新频繁，内容涵盖功能新增、Bug修复和架构优化。
-   **稳定性**：作为UE资产导入流水线的核心编辑器组件，经过长期迭代，趋于稳定。
-   **推荐度**：**强烈推荐**。这是UE官方推荐的现代化资产导入框架的编辑器实现，取代了旧的FBX导入流程。对于新项目或需要处理复杂导入场景的项目，应优先考虑使用Interchange。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor)
-   [官方文档](https://docs.unrealengine.com/5.0/en-US/interchange-framework-in-unreal-engine/) (Interchange 框架概述)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Tests) (位于 `Engine/Plugins/Interchange/Tests` 目录)