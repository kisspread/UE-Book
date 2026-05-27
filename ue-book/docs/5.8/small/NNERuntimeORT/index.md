# NNERuntimeORT

> ONNX Runtime backed runtime for the Neural Network Engine (NNE), accelerated by the CPU and DirectML execution providers.

| 属性 | 值 |
|---|---|
| 中文名 | ONNX 运行时后端 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeORT` (Runtime), `NNEOnnxruntime` (External) |
| 实验性 | ⚦ 是 (Beta) |
| 创建时间 | 2023-11-07 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT) | |

## 用途

`NNERuntimeORT` 是 Unreal Engine 5 神经网络引擎 (NNE) 的一个插件，提供了基于 ONNX Runtime 的推理后端。它允许开发者在 UE5 游戏和应用程序中直接加载、运行 ONNX 格式的人工智能模型，并利用 CPU 或 DirectML 进行硬件加速。它解决了在 UE5 环境中高效执行标准 ONNX 模型进行实时推理的问题，是游戏内 AI 应用（如物体识别、NPC 行为决策、实时风格迁移等）的核心基础设施之一。

## 使用场景

- 你需要在 UE5 中运行 ONNX 格式的人工智能模型进行实时推理。
- 你正在开发一个需要集成计算机视觉、自然语言处理或预测性 AI 功能的游戏或应用。
- 你希望利用 PC 的 CPU 或支持 DirectML 的 GPU 对神经网络推理进行加速。
- 你已使用 PyTorch、TensorFlow 等框架训练了模型，并已将其导出为 ONNX 格式。

## 蓝图用法

此插件主要通过 NNE 核心系统的蓝图接口进行使用，其本身并不直接暴露特定的蓝图节点。核心节点位于 `UNNEModelData` 和 `UNNEModelInstance` 等类中，以下为典型用法概览：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Model Instance` | 从模型数据资产创建一个可执行的模型实例。 | `UNNEModelInstance` |
| `Run Sync` / `Run Async` | 同步或异步执行模型推理，输入数据，输出结果。 | `UNNEModelInstance` |
| `Set Input Data` / `Get Output Data` | 设置模型的输入张量数据或获取输出张量数据。 | `UNNEModelInstance` |

### 使用示例（蓝图描述）

1.  **加载与创建**: 在内容浏览器中创建一个 `NNEModelData` 资产并导入你的 ONNX 文件。在蓝图中，通过 `Create Model Instance` 节点，使用该资产创建一个 `UNNEModelInstance` 对象。
2.  **准备数据**: 根据你的模型输入规格，创建或填充一个包含输入数据的数组（如 `TArray<float>`）。
3.  **执行推理**: 将准备好的数据通过 `Set Input Data` 设置到模型实例，然后调用 `Run Sync`（同步）或 `Run Async`（异步）执行推理。
4.  **获取结果**: 推理完成后，通过 `Get Output Data` 获取模型输出的张量数据，用于后续的游戏逻辑或渲染。

## C++ 用法

### 头文件引入

```cpp
#include "NNECore.h"
#include "NNERuntimeORT.h"
```

### 基本用法

基于插件提供的典型使用流程，以下是一个简化的 C++ 模型加载与推理示例。

```cpp
// 假设已有 UNNEModelData* ModelData 指向已加载的ONNX模型数据资产。
// 引擎核心模块，用于查找推理运行时
#include "NNECore.h"

void RunInferenceExample(UNNEModelData* ModelData)
{
    if (!ModelData) return;

    // 1. 获取已注册的 ONNX Runtime 后端
    TArray<UNNERuntime*> Runtimes = UNNECore::GetRuntimes();
    UNNERuntime* ORTRuntime = nullptr;
    for (UNNERuntime* Runtime : Runtimes)
    {
        // NNERuntimeORT 模块通常会注册一个名为 “NNERuntimeORT” 的运行时
        if (Runtime && Runtime->GetName() == TEXT("NNERuntimeORT"))
        {
            ORTRuntime = Runtime;
            break;
        }
    }
    if (!ORTRuntime) return;

    // 2. 创建模型实例
    TWeakObjectPtr<UNNEModelInstance> ModelInstance = ORTRuntime->CreateModelInstance(ModelData);
    if (!ModelInstance.IsValid()) return;

    // 3. 准备输入数据 (示例：一个形状为 [1, 3, 224, 224] 的浮点数组)
    TArray<float> InputData;
    InputData.SetNumZeroed(1 * 3 * 224 * 224); // 填充你的实际输入数据

    // 4. 设置输入并运行推理
    UNNEModelInstance::EStatus Status = ModelInstance->SetInputData(0, InputData);
    if (Status != UNNEModelInstance::EStatus::Ok) return;

    Status = ModelInstance->RunSync();
    if (Status != UNNEModelInstance::EStatus::Ok) return;

    // 5. 获取输出数据
    TArray<float> OutputData;
    Status = ModelInstance->GetOutputData(0, OutputData);
    if (Status == UNNEModelInstance::EStatus::Ok)
    {
        // 处理推理结果 (OutputData)
    }
}
```
*来源：此示例流程基于插件核心模块 `UNNERuntime` 和 `UNNEModelInstance` 的通用接口设计。*

### 进阶用法

更复杂的用法包括：
- **异步推理**: 使用 `RunAsync` 并绑定委托来避免游戏线程阻塞。
- **多输入/输出模型**: 通过索引为多个输入和输出端口设置和获取数据。
- **性能分析**: 利用引擎的性能分析工具跟踪推理耗时。
- **DirectML 加速**: 确保在支持的平台和硬件上，插件会自动或可配置地选择 DirectML 执行提供者以获得更优性能。

## Demo 示例

一个完整的、可编译的最小示例已集成在引擎的 NNE 测试中。建议直接参考引擎源码中的 `NNECoreTest` 和 `NNERuntimeORTTest` 模块。

## 模块依赖

要使用此插件，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `NNECore` | UE5 神经网络引擎的核心接口和模型数据类。 |
| `NNERuntime` | NNE 运行时基类接口。 |
| `NeuralNetworkEngine` | 包含 `UNNEModelData` 等核心资产类型。 |
| `NNEOnnxruntime` | 捆绑的第三方 ONNX Runtime 库（插件内部依赖）。 |

*注：根据插件设计，通常只需要在你的 `Build.cs` 中添加对 `NNECore` 的依赖即可，其他依赖会由插件模块内部处理。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `d9fee063` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 升级 ONNX Runtime 至 1.24.3，DirectML 至 1.15.4。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏，统一日志格式。 |
| 2026-03-30 | `33f008b5` | [Backout] - CL52245530 | 回滚了一次提交 (CL52245530)。 |
| 2026-03-30 | `c8c79a38` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 尝试升级运行时版本（后被回滚）。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 代码结构重构，头文件拆分，增加显式包含。 |

### 维护评价

`NNERuntimeORT` 是 Unreal Engine 5 中 `NNE (Neural Network Engine)` 框架的关键组成部分。从 git 历史看，该插件**维护非常活跃**（最后更新在 2026 年 4 月），持续进行第三方库升级、代码重构和问题修复。

**主要注意点**：
- **Beta 状态**: 插件明确标记为 `IsBetaVersion=true`，且默认未启用 (`EnabledByDefault=false`)。这意味着其 API 和功能在未来版本中可能会发生变化，不建议在追求最高稳定性的生产环境中无条件使用。
- **积极维护**: 核心开发者持续更新底层 ONNX Runtime 和 DirectML 版本，说明该插件是官方重点发展的功能。
- **平台限制**: 目前仅支持 Win64, Linux, LinuxArm64 和 Mac，不支持主机和移动平台。

**结论**：这是一个**积极维护中的 Beta 阶段核心功能插件**。如果你希望在 UE5 中进行 ONNX 模型推理，这是官方推荐且唯一原生支持的路径。建议关注其版本更新说明，并在项目中谨慎使用，做好应对 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT/Source/NNERuntimeORTTest)