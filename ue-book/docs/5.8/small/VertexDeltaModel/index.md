# ML Deformer Vertex Delta Model

> Vertex Delta Model for the ML Deformer Framework（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 顶点偏移变形器模型 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、资产编辑器） |
| 模块 | `VertexDeltaModel` (Runtime), `VertexDeltaModelEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-06 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/VertexDeltaModel) | |

## 用途

**VertexDeltaModel** 是 **机器学习变形器 (ML Deformer)** 框架的核心扩展插件。它实现了一种基于 **顶点位置偏移（Delta）** 的机器学习模型，用于驱动高质量的网格体变形动画。

其核心解决问题是：在需要极高精度和复杂表现力的动画场景（如面部表情、肌肉模拟）中，传统的骨骼驱动方式难以满足要求。此插件通过神经网络，直接在顶点级别学习并预测从基础姿势（如A-Pose）到目标姿势（如表情）的几何形变，从而实现电影级的角色变形效果。

## 使用场景

- **高保真角色动画**：制作逼真的面部表情、口型同步或复杂的身体变形（如肌肉鼓动）。
- **游戏内实时变形**：在游戏运行时，通过机器学习模型实时计算网格体顶点的精确偏移，替代复杂的骨骼权重绘制。
- **电影预渲染与虚拟制片**：为实时渲染的数字角色提供接近离线渲染的动画质量。

## 模块列表

| 模块 | 类型 | 功能简述 |
|---|---|---|
| `VertexDeltaModel` | Runtime | 提供顶点偏移模型的核心数据资产 (`UVertexDeltaModel`)、预测器 (`UMLDeformerPredictor`) 和运行时逻辑。 |
| `VertexDeltaModelEditor` | Runtime | 提供在编辑器中创建、编辑和预览顶点偏移模型资产的用户界面和工具。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/VertexDeltaModel)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Plugins/MLDeformer)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `1d7ad320` | UE 5.8 Animation deprecation clean up (CL 8/10): MLDeformer | 进行 UE 5.8 版本的动画系统废弃清理，涉及 MLDeformer。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至 `UE_LOGF`，属于内部工具链更新。 |
| 2026-04-02 | `138d5376` | [Deformer Graph] Multiple fixes for Optimus runtime | 修复了 Optimus 运行时相关的问题，影响共享的计算框架。 |
| 2025-06-25 | `a9573a81` | ComputeFramework: Remove old deprecated functions from compute data providers. | 清理计算框架中旧的废弃接口。 |
| 2025-06-20 | `35f8ecb8` | PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin | 将 PyTorch 依赖移至独立的 PythonMLPackages 插件，调整了 Python 环境依赖。 |

### 维护评价

**维护状态：活跃维护中**
该插件自 2022 年从实验阶段迁移而来，并持续获得更新。近期（2026年）的提交记录表明它仍在跟随 UE 主版本（5.8）进行必要的兼容性和维护性更新（如废弃清理、日志迁移）。

虽然作为 `IsBetaVersion=true` 的插件，其 API 可能随版本变动，但 Epic 官方仍持续维护。推荐在新项目中试用，尤其适合对动画质量有高要求的 AAA 项目。需注意，该功能需要一定的机器学习知识进行模型训练，且运行时推理有一定性能开销。