# NNERuntimeRDG

> A runtime implementing the Neural Network Engine (NNE) API, using the Render Dependency Graph (RDG).

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络引擎 RDG 运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNEHlslShaders` (RuntimeAndProgram), `NNERuntimeRDG` (RuntimeAndProgram), `NNERuntimeRDGData` (RuntimeAndProgram), `NNERuntimeRDGUtils` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG) | |

## 总体用途

NNERuntimeRDG 是 Unreal Engine 5 中神经⽹络引擎（NNE）的 GPU 后端实现。它利用渲染依赖图（RDG）将神经网络的前向推理过程高效地调度到 GPU 上执行，从而为需要实时 AI 推理的场景（如游戏内角色决策、物理模拟、图像/音频处理）提供低延迟、高吞吐的推理能力。该插件是 NNE 生态系统的核心运行时组件，使开发者能够在不脱离虚幻引擎渲染管线的情况下，直接运行经过工程优化的深度学习模型。

## 模块总览

| 模块名 | 类型 | 一句话总结 | 详细文档 |
|---|---|---|---|
| `NNEHlslShaders` | RuntimeAndProgram | GPU 着色器元库，包含所有神经网络运算所需的 HLSL 代码。 | [NNEHlslShaders.md](./NNEHlslShaders.md) |
| `NNERuntimeRDG` | RuntimeAndProgram | 核心运行时模块，实现 NNE 接口，通过 RDG 编排 GPU 推理流程。 | [NNERuntimeRDG.md](./NNERuntimeRDG.md) |
| `NNERuntimeRDGData` | RuntimeAndProgram | 模型数据管理层，负责加载、存储和转换神经网络权重与结构。 | [NNERuntimeRDGData.md](./NNERuntimeRDGData.md) |
| `NNERuntimeRDGUtils` | EditorAndProgram | 编辑器工具集，提供模型导入、验证、调试等辅助功能。 | [NNERuntimeRDGUtils.md](./NNERuntimeRDGUtils.md) |
| `NNERuntimeRDGOnnxEditor` | External | ONNX 模型解析支持（第三方库封装）。 | [NNERuntimeRDGOnnxEditor.md](./NNERuntimeRDGOnnxEditor.md) |
| `NNERuntimeRDGOnnxruntimeEditor` | External | ONNX Runtime 集成支持（第三方库封装）。 | [NNERuntimeRDGOnnxruntimeEditor.md](./NNERuntimeRDGOnnxruntimeEditor.md) |
| `NNERuntimeRDGProtobufEditor` | External | Protocol Buffers 序列化支持（第三方库封装）。 | [NNERuntimeRDGProtobufEditor.md](./NNERuntimeRDGProtobufEditor.md) |

## 使用场景

- **游戏 AI 决策**：在运行时加载预训练的神经网络模型（如行为选择、策略评估），利用 GPU 并行加速推理，实现毫秒级响应。
- **实时图像/音频处理**：配合 RenderTarget 或音频数据，对画面帧或音频流执行神经网络算法（如图像超分辨率、风格迁移、语音识别）。
- **物理与动画**：使用神经网络驱动角色运动、布料模拟或流体动力学，替代传统基于物理的模拟。
- **编辑器预处理**：在内容烘焙阶段调用 NNE 进行模型量化、剪枝或推理验证，构建优化的游戏内容。
- **研究原型**：作为实验性平台，快速验证 GPU 推理在虚幻项目中的可行性和性能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG)
- [NNE 文档](https://docs.unrealengine.com/5.7/en-US/neural-network-engine-in-unreal-engine/)（5.7 正式版，需参考对应版本）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG/Source/NNERuntimeRDG/Private/Tests)

## 维护状态

### 近期更新

| 日期 | 提交 | 说明 |
|---|---|---|
| 2025-07-24 | `2412ec9f` | 将 TArrayView 和 Invoke 改为 constexpr；修复 GetData 的 UB 和 TStaticArray 中废弃的 Alignment |
| 2025-06-12 | `9ce28ae0` | 更新数值限制，改用 std 库宏以解决新版 Windows 编译 |
| 2025-06-12 | `d9dba260` | [NNE] NNERuntimeRDGHlsl arm64 支持 |
| 2025-06-03 | `d31855b9` | 修复 libprotobuf-lite 构建脚本，并添加 Windows arm64 版本 |
| 2025-05-29 | `8cfef610` | 为使用 TGreater 的文件添加 Greater.h 包含，以适配即将到来的更改 |

### 维护评价

- **创建时间**：2025 年 5 月，距今不足 3 个月，属于全新插件。
- **近期更新频率**：2025 年 6‑7 月持续有修复、特性更新（arm64 支持、编译兼容性修复），开发活跃。
- **已知限制**：标记为实验性（IsExperimentalVersion=true），API 和实现可能在不兼容方向变动，不建议在生产项目中依赖。
- **推荐使用**：适合需要 GPU 加速神经网络推理的早期原型探索。建议跟踪官方更新，并准备好随时适配 API 变化。