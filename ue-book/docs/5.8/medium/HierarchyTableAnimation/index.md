# Hierarchy Table Animation

> Animation-specific type definitions for Hierarchy Tables

| 属性 | 值 |
|---|---|
| 中文名 | 层级表动画 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产） |
| 模块 | `HierarchyTableAnimationRuntime` (Runtime), `HierarchyTableAnimationEditor` (Editor), `HierarchyTableAnimationUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-21 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/HierarchyTableAnimation) | |

## 用途

HierarchyTableAnimation 是 HierarchyTable 插件的动画扩展，为层级表数据结构提供动画相关的类型定义和功能支持。该插件的核心功能包括：

- **配置文件混合（Profile Blend）**：支持动画混合配置文件的创建与管理，包括根空间（Root Space）支持
- **骨骼层级同步**：当骨架层级发生变化时，自动更新加载的混合配置资产
- **缓存数据管理**：处理混合节点的缓存数据生成，避免运行时崩溃

该插件将动画特有逻辑从基础 HierarchyTable 插件中分离出来，遵循关注点分离原则，使核心表格结构保持通用性。

## 使用场景

- 你需要在层级化的骨骼或动画数据上执行混合操作
- 你需要管理动画混合配置文件（Blend Profiles），并希望与骨架层级保持同步
- 你正在使用 HierarchyTable 插件并需要动画扩展功能
- 你需要对动画混合节点进行根空间转换

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [HierarchyTableAnimationRuntime](HierarchyTableAnimationRuntime.md) | Runtime | 运行时动画混合逻辑、配置文件管理、层级同步 |
| [HierarchyTableAnimationEditor](HierarchyTableAnimationEditor.md) | Editor | 编辑器 UI、资产编辑器、自定义资产操作 |
| [HierarchyTableAnimationUncookedOnly](HierarchyTableAnimationUncookedOnly.md) | UncookedOnly | 仅未打包状态下的功能（如资产验证、导入导出） |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HierarchyTable` | 核心层级表数据结构，本插件的必要前置依赖 |
| `AnimationCore` | 动画核心库，提供基础动画类型和工具 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `711fdc2f` | Add root space support to profile blend | 新增配置文件混合的根空间支持 |
| 2026-03-04 | `d9a06590` | Update UAF blend profiles | 更新 UAF 混合配置文件 |
| 2025-10-20 | `beb220c7` | Fix loaded blend profile assets not updating the hierarchy when its skeleton's hierarchy has changed | 修复骨架层级变更后混合配置资产未更新的问题 |
| 2025-10-09 | `71d54d3d` | Fix profile blend node crash due to cached data not being generated in some cases | 修复混合节点因缓存数据未生成导致的崩溃 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将 Base<Plugin>.ini 重命名为 Default<Plugin>.ini |

### 维护评价

**活跃维护**。该插件在 2026 年仍有功能性更新（根空间支持、混合配置文件更新），且近期（2025-10）修复了多个稳定性问题。作为实验性插件，目前处于积极开发阶段。

⚠️ **注意**：该插件标记为实验性（`IsExperimentalVersion=true`）且默认未启用（`EnabledByDefault=false`）。API 可能发生破坏性变更，不建议在生产环境中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/HierarchyTableAnimation)
- [HierarchyTable 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HierarchyTable)（前置依赖）