# Shader Toolkit

> A suite of tools to analyze your projects build and shaders to help reduce shader and material permutations.

| 属性 | 值 |
|---|---|
| 中文名 | 着色器工具包 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ShaderAuditCore` (EditorAndProgram), `ShaderAudit` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2026-05-12 |
| 年龄标签 | 🆕（约 -1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ShaderToolkit) | |

## 用途

Shader Toolkit 是一个编辑器工具集，用于分析项目的着色器（Shader）编译产物。其核心目的是帮助开发者识别和优化项目中的着色器及材质变体（Permutations），通过审计减少不必要的编译组合，从而缩短项目构建时间、降低最终包体大小和运行时内存占用。

## 使用场景

- 你的项目在打包或编译时面临过长的着色器编译时间。
- 你怀疑项目中存在过多未使用的材质和着色器变体，导致资源浪费。
- 你需要在开发后期对项目的着色器资产进行系统性审计和优化。
- 你的项目目标是减少客户端的运行时着色器内存占用。

## 蓝图用法

此插件主要为编辑器内的分析和审计工具，没有公开的蓝图节点接口。其功能通常通过编辑器菜单或专用窗口触发。

## C++ 用法

此插件的核心功能为编辑器工具，未提供面向游戏逻辑的运行时C++ API。其用法主要通过插件提供的编辑器UI或命令行工具进行操作。具体的审计逻辑和核心类，请参阅子模块文档。

## 模块列表

此插件包含两个核心模块，它们协同工作以完成着色器审计功能：

- **`ShaderAuditCore`**: 核心库，包含着色器审计的基础数据结构、分析逻辑和核心算法。
  详见 [ShaderAuditCore.md](./ShaderAuditCore.md)
- **`ShaderAudit`**: 编辑器前端模块，提供用户界面、数据可视化、交互操作以及与编辑器其他部分的集成。
  详见 [ShaderAudit.md](./ShaderAudit.md)

## 模块依赖

要使用此插件，你的项目需要依赖以下插件：

| 插件 | 用途 |
|---|---|
| `MaterialValidation` | 提供材质资产的验证和分析功能，作为着色器审计的基础 |

## 维护状态

### 近期更新

该插件于创建初期（2026-05-12）经历了多次提交，旨在完善模块结构和解决初始问题。

- `c4351fff` 2026-05-12 — 创建 ShaderAuditCore 模块
- `f78afe5d` 2026-05-12 — [回滚] - CL53715516
- `0d38c80a` 2026-05-12 — 创建 ShaderAuditCore 模块
- `d843e10b` 2026-05-12 — ShaderAudit: 将剩余的内联 `#if WITH_EDITOR` 替换为用于材质层次获取的 Slate 事件
- `263d8b5e` 2026-05-12 — 移除 shaderaudit 中的内联 `WITH_EDITOR`，改为使用从 ShaderAudit 设置的 Slate 事件

### 维护评价

- **状态**：**实验性 & 活跃开发中**。
- **分析**：该插件标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，表明它仍处于实验阶段，不建议在生产环境中直接启用。从 Git 历史看，它于近期（2026-05-12）被创建，并经历了密集的初始化提交，正在快速迭代和完善中。
- **建议**：可以关注其发展，但需谨慎评估其在当前版本中的稳定性和完整性。建议在开发或测试环境中试用，等待其趋于稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ShaderToolkit)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ShaderToolkit/Tests)