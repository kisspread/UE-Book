# Performance Capture Workflow

> Performance Capture In-Editor Workflow tools. Provides access to the Mocap Manager panel.

| 属性 | 值 |
|---|---|
| 中文名 | 性能捕获工作流 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、蓝图资产） |
| 模块 | `PerformanceCaptureWorkflow` (Runtime), `PerformanceCaptureWorkflowRuntime` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PerformanceCaptureWorkflow) | |

## 用途

本插件为 Unreal Engine 的虚拟制片流程提供了一套在编辑器内进行表演捕捉（Performance Capture）的工具集。其核心目标是简化和优化现场表演数据（如动作捕捉、面部捕捉数据）的录制、同步与管理工作流。插件通过提供 “Mocap Manager” 专用面板，让艺术家和技术人员能够在编辑器内直接监控、控制和管理表演捕获过程，而不是依赖于外部复杂的管线。

## 使用场景

- **虚拟制片现场拍摄**：在 LED 墙或绿幕前进行表演捕获时，使用 Mocap Manager 面板实时监控时间码同步、触发录制、并管理捕获的数据流。
- **数据表与时间码管理**：需要通过编辑器工具对表演捕获过程中生成的数据表（PCapDataTable）进行快速编辑和更新，或维护复杂的时间码同步关系。
- **集成自定义 Mocap 设备**：当需要将特定的动捕或面捕设备（如 OptiTrack, Xsens 等）集成到 UE 的虚拟制片工作流中，并需要自定义数据预处理时，可以使用此插件提供的运行时模块作为基础。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `PerformanceCaptureWorkflow` | Runtime | 核心编辑器模块。提供 Mocap Manager 面板、数据表编辑工具及工作流蓝图节点。 |
| `PerformanceCaptureWorkflowRuntime` | Runtime | 运行时支持模块。包含与表演捕获数据处理、时间码管理、设备连接相关的核心运行时逻辑。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `6738ae86` | [Performance Capture Workflow] - Add telemetry to the Mocap Manager panel invocation. | 为 Mocap Manager 面板的调用添加了遥测功能。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 调整了虚拟制片资产的分类与迁移。 |
| 2026-05-12 | `cb548ae0` | [Performance Capture Workflow] - Add multicast BP delegates that fire on changes to the timecode and ... | 添加了在时间码等数据变化时触发的多播蓝图委托。 |
| 2026-05-01 | `e5ecc8a9` | [PerformanceCaptureWorkflow] - Adds editor only BP function to update a specific row in a PCapDataTable. | 新增了用于更新 PCapDataTable 特定行的仅编辑器蓝图函数。 |
| 2026-04-20 | `12bc1b78` | [PerformanceCaptureWorkflow] ... | 性能捕获工作流相关更新。 |

### 维护评价

该插件于 **2025年4月** 首次提交，并在近期（2026年4-5月）有多次活跃更新。更新内容主要集中在功能增强（如添加新节点、委托）和工具完善（如数据表操作、遥测）上。作为标记为 **Beta** 的虚拟制片核心工具，目前处于**积极开发与维护**状态。鉴于其版本号（0.2）和近期的提交频率，建议在生产环境中谨慎评估其稳定性，但非常适合用于早期技术验证和内部流程开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PerformanceCaptureWorkflow)
- [模块文档 - PerformanceCaptureWorkflow](PerformanceCaptureWorkflow.md)
- [模块文档 - PerformanceCaptureWorkflowRuntime](PerformanceCaptureWorkflowRuntime.md)