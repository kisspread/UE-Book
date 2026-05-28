# NNERuntimeCoreML

> CoreML backed runtime for the Neural Network Engine (NNE).（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | CoreML神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeCoreML` (Runtime), `NNERuntimeCoreMLEditor` (Editor), `NNERuntimeCoreMLUtils` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-08 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeCoreML) | |

## 用途

该插件为 UE5 的神经网络引擎 (NNE) 提供了一个基于苹果 CoreML 框架的运行时后端。它解决了在 macOS 和 iOS 平台上利用苹果硬件（如 Neural Engine、GPU）进行高性能、低功耗 AI 推理的问题。通过集成 CoreML，开发者可以让其神经网络模型在这些苹果设备上原生且高效地运行，充分利用苹果的硬件加速特性。

## 使用场景

-   **苹果设备专属游戏 AI**：为 macOS 或 iOS 游戏中的 NPC 行为、环境感知或实时决策提供硬件加速的 AI 推理。
-   **跨平台 AI 应用开发**：当你的 UE5 项目需要支持 macOS 并利用其独特的 AI 加速能力时，此运行时是必不可少的。
-   **处理 CoreML 模型格式**：当你已有的机器学习工作流基于苹果生态，模型以 `.mlmodel` 或 `.mlpackage` 格式存在时，可以直接在 UE5 中加载并使用。

## 模块列表

| 模块 | 说明 |
|---|---|
| **NNERuntimeCoreML** | 核心运行时模块。实现了 NNE 运行时接口，负责加载 CoreML 模型、创建运行时实例并执行 CPU/Neural Engine 推理。 |
| **NNERuntimeCoreMLEditor** | 编辑器集成模块。提供 CoreML 模型资源（UAsset）的处理、烘焙支持，并确保在打包构建中正确包含模型。 |
| **NNERuntimeCoreMLUtils** | 工具与辅助模块。包含用于处理 CoreML 模型元数据、类型转换等的工具函数和数据结构。 |

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeCoreML)
-   [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/NNE)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统升级，从UE_LOG迁移到UE_LOGF。 |
| 2026-03-20 | `2724fcee` | [NNERuntimeCoreML] Fix output copy to use logical size from MLMultiArray shape | 修复了推理结果输出时使用错误尺寸的问题，确保从MLMultiArray形状中正确获取逻辑尺寸。 |
| 2026-02-09 | `7c2ef798` | [NNE] NNERuntimeCoreML add .mlpackage format support. | 新增了对`.mlpackage`模型格式的支持，扩展了可加载模型的类型。 |

### 维护评价

该插件于 **2025年1月** 创建，是一个**实验性**插件，且**默认未启用**。

**维护状态：活跃**
-   创建至今约一年半，但自 2026 年初以来有持续、实质性的功能更新（如添加新模型格式支持）和问题修复。
-   近期提交（2026年4月）表明仍在积极维护和适配引擎更新（如日志系统）。
-   作为苹果平台专用的 AI 推理后端，其价值明确。虽然仍处于实验阶段（`IsExperimentalVersion=true`），但近期的维护活动表明它是一个持续开发中的功能。

**推荐度：有条件推荐**
如果你需要将 UE5 项目部署到 macOS/iOS 并使用 AI 推理，特别是希望利用苹果硬件的 Neural Engine，那么这是一个**必须关注和测试**的插件。由于其状态为实验性且默认关闭，建议在生产环境中谨慎评估，并密切关注其后续版本更新和稳定性改进。