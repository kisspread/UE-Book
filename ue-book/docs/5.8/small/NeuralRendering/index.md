# Neural Rendering

> Enable neural rendering features including: neural post processing（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 神经后处理 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NeuralPostProcessing` (RuntimeAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-10-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NeuralRendering) | |

## 用途

该插件提供了一个在 Unreal Engine 渲染管线的后处理阶段集成神经网络推理的框架。其核心目标是让开发者能够在像素着色器执行之后，利用训练好的神经网络模型对渲染结果进行进一步处理，从而实现传统着色器难以实现的复杂图像变换效果，例如高级的风格迁移、超分辨率、去噪、特定视觉效果生成等。

插件通过提供一个 `UNeuralPostProcessModelInstance` 类来管理神经网络模型的加载、输入/输出缓冲区的创建以及推理执行。它支持通过后处理材质（Post Process Material）来指定要使用的神经网络配置文件（Neural Profile），并允许在材质中通过 `Neural Input` 和 `Neural Output` 节点来控制数据的流向。

## 使用场景

- 你正在开发一款需要实时、风格化视觉效果的游戏，希望用神经网络实现电影级别的滤镜或艺术风格 → 使用此插件结合自定义的后处理材质和训练好的模型。
- 你的项目涉及医学影像、科学可视化或工业检测，需要对渲染出的 2D 图像进行基于神经网络的分析或增强 → 通过此插件将推理流程集成到渲染管线中。
- 你正在研究或原型开发 AI 与实时图形结合的交互式应用，需要一个稳定且易于集成的推理执行框架。

## 蓝图用法

从当前提供的源码分析，该插件的核心功能（神经网络配置文件的创建、模型实例管理）主要通过编辑器配置（材质编辑器中的 `Neural Profile`）和 C++ 代码控制，**未在公开头文件中暴露 `BlueprintCallable` 函数**。其使用流程更多是在材质编辑器和 C++ 层面进行配置。

## C++ 用法

### 头文件引入

```cpp
#include "NeuralPostProcessing/Public/NeuralPostProcessing.h"
// 核心功能类位于 Private 头文件中，通常不需要直接包含
// #include "NeuralPostProcessing/Private/NeuralPostProcessModelInstance.h"
```

### 基本用法

神经网络后处理的核心是通过后处理材质系统驱动的。你需要在材质编辑器中完成大部分配置。在 C++ 侧，你需要为后处理场景设置（`FPostProcessSettings`）指定一个包含神经配置文件（`NeuralProfile`）的材质。该插件内部会实例化并管理对应的 `UNeuralPostProcessModelInstance`。

（以下为概念性代码，展示插件内部 `UNeuralPostProcessModelInstance` 的典型交互流程，实际使用由引擎后处理系统调度）

```cpp
// 假设我们有一个后处理材质实例，其参数已经设置好神经配置文件
// 在渲染线程中，引擎后处理系统会找到该材质，并创建/更新对应的模型实例

// 1. 更新模型（如果模型数据或运行时名称变化，会自动重建）
ModelInstance->Update(ModelData, RuntimeName);

// 2. 在 RDG (Render Dependency Graph) 构建阶段，创建或更新必要的缓冲区
ModelInstance->CreateRDGBuffersIfNeeded(GraphBuilder);

// 3. 配置分块和重叠区域参数（如果模型支持/需要）
ModelInstance->UpdateTileDimension(FIntPoint(64, 64));
ModelInstance->UpdateTileOverlap(FIntPoint(8, 8));
ModelInstance->UpdateTileOverlapResolveType(ETileOverlapResolveType::Feathering);

// 4. 执行神经网络推理
ModelInstance->Execute(GraphBuilder);

// 5. 获取输入/输出缓冲区，用于材质中的采样或写入
FRDGBufferRef InputBuffer = ModelInstance->GetInputBuffer();
FRDGBufferRef OutputBuffer = ModelInstance->GetOutputBuffer();
```
*（注：以上代码为基于 `UNeuralPostProcessModelInstance.h` 头文件的功能性示例，说明其 API 接口）*

## Demo 示例

由于该插件的核心用法是通过后处理材质和编辑器配置进行驱动，一个最小的可编译 C++ 示例会依赖完整的材质和渲染管线设置，难以独立展示。其典型应用流程如下：

1.  **在项目设置中启用插件**：在 `Plugins` 面板中搜索并启用 `NeuralRendering`。
2.  **准备神经网络模型**：使用 `UNNEModelData` 资产导入一个 ONNX 格式的模型。
3.  **创建或编辑后处理材质**：
    - 在材质编辑器中，将材质的 `Material Domain` 设为 `Post Process`。
    - 启用材质细节面板中的 `Used with Neural Network` 选项。
    - 从右键菜单中添加 `Neural Input` 和 `Neural Output` 节点。
    - 通过 `Neural Profile` 参数资产指定要使用的 `UNNEModelData` 和其他配置。
4.  **在场景中应用**：将包含神经配置文件的材质实例赋给后处理体积（`Post Process Volume`）或摄像机的后处理设置中。

## 模块依赖

该插件的 `.uplugin` 文件明确声明了对另一个插件的依赖，这是使用者必须启用的关键依赖。

| 模块 | 用途 |
|---|---|
| `NNERuntimeORT` | 提供 ONNX Runtime 的神经网络推理后端，是神经网络模型执行的实际引擎。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 重构GPU同步API调用，替换旧的等待函数为新的组合函数。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移到UE_LOGF，可能是格式化改进或适配新的日志系统。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃旧的GPU性能分析宏，进行代码清理。 |
| 2025-10-27 | `581ba7ee` | [Neural post processing] Fix typo | 修复代码中的拼写错误。 |
| 2025-10-24 | `260f58f8` | [Neural post processing] Fix cooking fail in editor. | 修复编辑器中的烹饪失败问题，提升稳定性。 |

### 维护评价

该插件处于**实验性**状态，且**默认未启用**。从提交历史看，它仍在被维护，最近一次实质性活动在2026年4月（API重构和日志迁移），最近一次功能/稳定性修复在2025年10月。这些更新主要是内部重构、适配引擎更新和修复小问题，表明它可能处于一个相对稳定但功能尚未完全扩展的阶段。

**注意**：由于 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，此插件应视为前沿技术预览或研究用途。其API和功能可能会在未来版本中发生重大变化或被移除。建议仅在实验性项目或研究环境中使用，并关注其后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NeuralRendering)
- 官方文档：无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NeuralRendering/Tests)（如果存在）