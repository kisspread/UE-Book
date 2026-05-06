# NNERuntimeCoreML

> CoreML backed runtime for the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | NNE CoreML 运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeCoreMLEditor` (Editor), `NNERuntimeCoreML` (RuntimeAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-08 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeCoreML) | |

## 总体用途

NNERuntimeCoreML 是 Unreal Engine 神经网络引擎（NNE）的一个**运行时后端**，基于 Apple 的 CoreML 框架。它允许在 macOS 平台（包括 Apple Silicon 和 Intel Mac）上利用 CoreML 的原生硬件加速能力（CPU/GPU/NPU）来执行神经网络推理。该插件将 NNE 的通用推理接口桥接到 CoreML，使开发者无需直接处理 CoreML 细节即可获得 Apple 平台的最佳性能。

## 模块列表

| 模块 | 类型 | 一句话总结 | 文档链接 |
|---|---|---|---|
| `NNERuntimeCoreML` | RuntimeAndProgram | 核心运行时模块，实现 NNE 与 CoreML 之间的模型加载、编译和推理逻辑。 | [NNERuntimeCoreML.md](NNERuntimeCoreML.md) |
| `NNERuntimeCoreMLEditor` | Editor | 编辑器模块，提供 CoreML 模型资产导入、配置面板及开发者工具支持。 | [NNERuntimeCoreMLEditor.md](NNERuntimeCoreMLEditor.md) |

## 使用场景

- 在 macOS 上开发使用 NNE 推理神经网络的游戏或应用时，选择 CoreML 作为后端以获得与 Apple 硬件深度绑定的性能（支持 float16/double/int32 等多数据类型）。
- 需要将已有的 CoreML 模型（`.mlmodel` 或 `.mlpackage`）无缝集成到 UE 的神经网络工作流中。
- 在支持 Apple Silicon 的设备上利用 GPU/NPU 加速推理，降低 CPU 占用。

## 相关链接

- [官方课程: Neural Network Engine (NNE)](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [支持论坛](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)
- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeCoreML)