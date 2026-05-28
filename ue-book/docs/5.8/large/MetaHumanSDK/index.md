# MetaHuman SDK

> Utilities and tools for working with MetaHumans in Unreal Engine.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 开发套件 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `InterchangeDNA` (Runtime), `MetaHumanSDKEditor` (Editor), `MetaHumanSDKRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanSDK) | |

## 用途

MetaHuman SDK 是 MetaHuman 在 UE5 中的核心开发工具集。它提供了从 DNA 数据导入、骨骼网格体生成到运行时角色管理的完整工作流，解决了以下问题：

- **DNA 数据交换**：通过 Interchange 框架导入 MetaHuman 的 DNA 数据（面部骨骼、蒙皮权重、LOD 等），并将其转换为引擎可用的骨骼网格体资产
- **编辑器工具链**：提供 MetaHuman Manager 等编辑器面板，用于发现、组织和管理场景中的 MetaHuman 角色及其关联资产（材质、纹理、服装等）
- **运行时支持**：在运行时加载和管理 MetaHuman 角色，支持 DNA 配置切换、服装验证、骨骼兼容性检查等

该插件从实验阶段移出后正式发布（见首次提交），是 Epic 官方推荐的 MetaHuman 工作流基础设施。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `InterchangeDNA` | Runtime | 基于 Interchange 框架的 DNA 数据导入管线，负责将 MetaHuman DNA 文件转换为骨骼网格体资产 |
| `MetaHumanSDKEditor` | Editor | 编辑器工具集，包含 MetaHuman Manager 面板、资产发现与依赖关系遍历、服装验证等功能 |
| `MetaHumanSDKRuntime` | Runtime | 运行时 MetaHuman 管理，支持角色实例化、DNA 配置加载和骨骼兼容性处理 |

## 使用场景

- 你正在构建一个使用 MetaHuman 角色的项目，需要批量导入 DNA 数据 → 用 **InterchangeDNA**
- 你需要在编辑器中管理和组织大量 MetaHuman 角色及其关联资产（材质、服装、纹理） → 用 **MetaHumanSDKEditor**
- 你需要在运行时动态加载 MetaHuman 角色并切换外观配置 → 用 **MetaHumanSDKRuntime**
- 你正在开发自定义的 MetaHuman 内容管线工具 → 整个 SDK 提供了扩展基础

## 蓝图用法

MetaHuman SDK 的蓝图 API 主要集中在 `MetaHumanSDKRuntime` 模块中，提供运行时角色管理能力。详细的蓝图节点请参见 [MetaHumanSDKRuntime](MetaHumanSDKRuntime.md) 模块文档。

## C++ 用法

各模块的 C++ 用法请参见对应的子模块文档：

- [InterchangeDNA](InterchangeDNA.md) — DNA 导入管线与自定义导入器扩展
- [MetaHumanSDKEditor](MetaHumanSDKEditor.md) — 编辑器工具与资产管理系统
- [MetaHumanSDKRuntime](MetaHumanSDKRuntime.md) — 运行时角色管理 API

## 模块依赖

本插件除标准 Core/Engine/Slate 依赖外，还依赖以下模块：

| 模块 | 用途 |
|---|---|
| `InterchangeCore` / `InterchangeNodes` / `InterchangeEngine` | Interchange 资产交换框架，用于 DNA 数据导入管线 |
| `AnimationRigging` | 动画骨骼与绑定工具，用于骨骼兼容性处理 |
| `MeshDescription` | 网格体描述中间层，用于骨骼网格体生成 |
| `Persona` / `AnimationEditorLibrary` | 编辑器动画工具，用于 MetaHuman Manager 面板 |
| `AssetRegistry` | 资产注册与发现，用于 MetaHuman 角色的关联资产遍历 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体通用工具 |
| `HairStrandsCore` | 毛发系统支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `5c0dc0e5` | [MHSDK] Remove the VersionInfo.txt existence check when discovering MetaHuman character assemblies | 移除角色组装发现时的 VersionInfo.txt 检查 |
| 2026-05-21 | `418099aa` | Fix the incorrectly converted parent bones for Legacy DNAConfig case | 修复旧版 DNAConfig 父骨骼转换错误 |
| 2026-05-14 | `d477b10c` | [MHSDK] Replace path-based related-asset filtering in MetaHuman Manager with dependency walking | 用依赖遍历替换 MetaHuman Manager 中的路径过滤 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的警告 |
| 2026-05-12 | `c0e92a2b` | [MHSDK] Fix MetaHuman skeletal clothing verification reading incorrect texture dimensions | 修复服装验证读取纹理尺寸错误 |

### 维护评价

**活跃维护**。该插件创建于 2025 年 4 月，至今约 1 年，近期（2026 年 5 月）有高频率的功能更新和 Bug 修复。从 commit 记录可以看出：

- 持续改进资产发现机制（依赖遍历替代路径过滤）
- 积极修复骨骼兼容性问题（Legacy DNAConfig 父骨骼）
- 改善代码质量（浮点精度警告修复）
- 优化编辑器工具（纹理尺寸验证、版本检查简化）

作为 Epic 官方维护的 MetaHuman 基础设施，该插件处于活跃开发状态，推荐在 MetaHuman 项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanSDK)
- [子模块文档：InterchangeDNA](InterchangeDNA.md)
- [子模块文档：MetaHumanSDKEditor](MetaHumanSDKEditor.md)
- [子模块文档：MetaHumanSDKRuntime](MetaHumanSDKRuntime.md)