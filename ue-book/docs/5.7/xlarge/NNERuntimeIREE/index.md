# NNERuntimeIREE

> A runtime implementing the Neural Network Engine (NNE) API which is based on IREE, MLIR and LLVM and compiles neural networks directly to game code.

| 属性 | 值 |
|---|---|
| 中文名 | IREE 神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `IREEUtils` (Runtime), `IREEDriverRDG` (Runtime), `NNERuntimeIREE` (Runtime), `NNERuntimeIREEEditor` (Editor), `NNERuntimeIREEShader` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE) | |

---

## 总体用途

NNERuntimeIREE 是 Unreal Engine  Neural Network Engine (NNE) 的一个运行时实现。它基于 **IREE**（Intermediate Representation Execution Environment）、**MLIR** 和 **LLVM**，能够将训练好的神经网络模型直接编译为游戏代码（GPU/CPU），从而在游戏中高效地进行实时推理。该插件解决了在 Unreal 中集成机器学习推理时对性能、跨平台兼容性和低延迟的需求，特别适合需要自定义模型部署且希望深度优化运行时的场景。

---

## 模块概览

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `IREEUtils` | Runtime | IREE 工具函数与实用工具集，提供公共基础设施。 |
| `IREEDriverRDG` | Runtime | 基于 Render Dependency Graph (RDG) 的 IREE 驱动，负责模型在 GPU 上的执行调度。 |
| `NNERuntimeIREE` | Runtime | 核心运行时模块，实现 NNE API，管理模型加载、编译与推理流程。 |
| `NNERuntimeIREEEditor` | Editor | 编辑器扩展，提供模型导入、配置面板与蓝图节点生成支持。 |
| `NNERuntimeIREEShader` | Runtime | Shader 模块，处理 GPU 推理所需的 HLSL/SPIR-V 生成与缓存。 |
| `IREE` (ThirdParty) | External | 封装 IREE 运行时库，包括编译器和运行时 API。 |
| `NNEMlirTools` (ThirdParty) | External | 封装 MLIR 工具，用于模型转换与优化。 |

每个子模块的详细 API 和用法请参考对应文档：
- [IREEDriverRDG](./IREEDriverRDG.md)
- [IREEUtils](./IREEUtils.md)
- [NNERuntimeIREE](./NNERuntimeIREE.md)
- [NNERuntimeIREEEditor](./NNERuntimeIREEEditor.md)
- [NNERuntimeIREEShader](./NNERuntimeIREEShader.md)
- [IREE](./IREE.md)
- [NNEMlirTools](./NNEMlirTools.md)

---

## 使用场景

- **游戏 AI 推理**：在运行时运行神经网络（如目标检测、语音识别、行为预测），要求低延迟和跨平台支持。
- **实时图像/音频处理**：利用 GPU 加速的模型对游戏画面或音频流进行后处理。
- **自定义模型部署**：使用 ONNX/Pytorch 等框架训练模型，通过 IREE 编译后无缝集成到 UE 管线。
- **编辑器内预览与调试**：在编辑器中导入模型、配置输入输出，并快速测试推理结果。
- **性能敏感型项目**：需要直接控制推理优化（如 Wave32 模式、内存布局）的 AAA 或移动端项目。

---

## 模块依赖

使用本插件时需要依赖以下独特模块（标准 Core/Engine/Slate 等已省略）：

| 模块 | 用途 |
|---|---|
| `IREE` | 第三方 IREE 编译与运行时库。 |
| `NNEMlirTools` | MLIR 工具链，用于模型转换与图优化。 |
| `RDG` | 渲染依赖图，用于 GPU 指令排布（仅 `IREEDriverRDG` 需要）。 |
| `NNE` | 神经网络引擎框架接口（NNERuntimeIREE 实现此接口）。 |

> 注意：以上依赖已经自动处理，使用者只需在 `Build.cs` 中添加 `NNERuntimeIREE` 模块即可。

---

## 维护状态

### 近期更新

- 2025-09-26 — [NNE] NNERuntime IREE support of path with spaces on RelTest build on Mac for RDG.
- 2025-09-24 — [NNE] NNERuntimeIREERdg always prefer wave32 to be consistent with used GPU profiles from IREE.
- 2025-09-24 — [NNE] NNERuntimeIREE fix typo in Linux build script.
- 2025-09-24 — [NNE] NNERuntime IREE support of path with spaces on RelTest build on Mac.
- 2025-09-12 — [NNE] NNERuntimeIREE fix onnx importer dependencies not staged for Engine installed build.

### 维护评价

- **创建时间**：2025-09-12，至今不足一个月，属于全新开发中的插件。
- **更新频率**：几乎每天都有提交，修复和功能改进同步进行，开发活跃。
- **实验性**：标记为实验性版本，API 和功能可能在未来发生变化。
- **推荐度**：对于需要前沿机器学习推理能力的 UE 项目，值得尝试；但由于仍在快速迭代，建议预留回滚方案，并关注后续稳定版本发布。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE)
- [NNE 官方文档](https://docs.unrealengine.com/5.7/en-US/neural-network-engine-in-unreal-engine/)（待补充）
- [IREE 项目官网](https://iree.dev/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE/Source/NNERuntimeIREE/Tests)