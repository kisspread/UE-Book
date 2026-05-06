# NNERuntimeIREE

> A runtime implementing the Neural Network Engine (NNE) API which is based on IREE, MLIR and LLVM and compiles neural networks directly to game code.

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络IREE运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `IREEUtils` (Runtime), `IREEDriverRDG` (Runtime), `NNERuntimeIREE` (Runtime), `NNERuntimeIREEEditor` (Editor), `NNERuntimeIREEShader` (Runtime), `IREE` (External), `NNEMlirTools` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE) | |

## 用途

NNERuntimeIREEShader 是 NNERuntimeIREE 插件的核心 Shader 模块，负责将经 IREE 编译生成的神经网络 IR 转换为 UE 自有的 Shader 源码，并在 GPU 上执行推理。它实现了 NNE 后端的一套 Shader 编译与管理框架，包括：

- 自定义 Shader 类型 `FNNERuntimeIREEShader`，继承自 `FShader`，用于表示一个经过编译的神经网络 Shader 实例。
- Shader 映射管理（`FNNERuntimeIREEShaderMapId`/`FNNERuntimeIREEShaderMap`），确保不同输入/权重组合的 Shader 变体可在内容导出缓存（DDC）中唯一标识和复用。
- 编辑器下的异步编译管线（`FNNERuntimeIREEShaderCompilationManager`），支持多线程编译、结果收集与最终化。
- 辅助工具 Shader（如 `FFillBufferCS`）用于执行如缓冲区填充等通用 GPU 操作。

通过将神经网络计算下推到 UE 的渲染线程和 RDG（渲染依赖图），该模块使神经网络推理能够与游戏渲染管线无缝集成，利用已有的 GPU 资源管理和同步机制，避免额外的运行时开销。

## 使用场景

- **在游戏中运行实时神经网络推理**，如物体检测、姿态估计、画面增强等，性能关键且需要与渲染管线紧密配合。
- **需要将神经网络编译为平台原生 Shader**，获得比通用 GPU 计算库更低的执行延迟和更好的兼容性。
- **开发自定义 NNE 运行时后端**，基于 IREE 生态扩展 UE 的神经网络能力。

## 蓝图用法

该模块为纯底层渲染实现，不提供任何直接暴露给蓝图的函数或节点。要使用神经网络推理，请通过 NNERuntimeIREE 插件暴露的 NNE 接口（如 `UNNEObject` 或 `UNNEModelData`）进行操作，该模块作为内部依赖自动工作。

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeIREEShader.h"
#include "NNERuntimeIREEShaderType.h"
#include "NNERuntimeIREEShaderCompilationManager.h"
```

### 基本用法

**编译并获取一个神经网络 Shader 映射**（编辑器环境）：

```cpp
// 假设已从 IREE 编译器获得 Shader 代码哈希和参数元数据
uint64 ShaderCodeHash = GetShaderCodeHashFromIREE();
const FShaderParametersMetadata& ParamMeta = GetParamMetadata();

// 创建 Shader 映射 ID
FNNERuntimeIREEShaderMapId MapId;
MapId.FeatureLevel = GMaxRHIFeatureLevel;
MapId.ShaderCodeHash = ShaderCodeHash;
MapId.SetShaderDependencies(/* 必要依赖类型 */, GShaderPlatformForFeatureLevel[MapId.FeatureLevel]);

// 若映射尚未缓存，则发起编译
#if WITH_EDITOR
TArray<FShaderCommonCompileJobPtr> NewJobs;
// ... 构造 CompileJob 后填入 NewJobs ...
GNNERuntimeIREEShaderCompilationManager.AddJobs(NewJobs);
GNNERuntimeIREEShaderCompilationManager.Tick(0.0f); // 每帧调用以推进编译
#endif
```

**使用 FillBuffer CS 填充 RDG 缓冲区**：

```cpp
#include "NNERuntimeIREEShaderFillBufferCS.h"

void FillBuffer_RDG(FRDGBuilder& GraphBuilder, FRDGBufferUAVRef TargetUAV, FVector4f FillValue)
{
    using namespace UE::NNERuntimeIREEShader::Internal;

    FFillBufferCS::FParameters* Params = GraphBuilder.AllocParameters<FFillBufferCS::FParameters>();
    Params->TargetBuffer = TargetUAV;
    Params->Fill = FUintVector4(
        *reinterpret_cast<uint32*>(&FillValue.X),
        *reinterpret_cast<uint32*>(&FillValue.Y),
        *reinterpret_cast<uint32*>(&FillValue.Z),
        *reinterpret_cast<uint32*>(&FillValue.W)
    );

    FComputeShaderUtils::AddPass(
        GraphBuilder,
        RDG_EVENT_NAME("NNERuntimeIREE_FillBuffer"),
        ERDGPassFlags::Compute,
        TShaderMapRef<FFillBufferCS>(GetGlobalShaderMap(GMaxRHIFeatureLevel)),
        Params,
        FIntVector(/* 线程组数量 */));
}
```

### 进阶用法

**自定义 Shader 类型并注册编译**：

参考 `FNNERuntimeIREEShaderType` 的实现方式，通过宏 `IMPLEMENT_SHADER_TYPE` 注册新的神经网络 Shader 类型，并实现 `ShouldCompilePermutation` / `ModifyCompilationEnvironment` 以控制编译变体。之后将 Shader 类型依赖加入 `FNNERuntimeIREEShaderMapId`，即可纳入统一的编译与缓存体系。

## Demo 示例

由于该模块深度整合了 UE 的渲染线程和 DDC，在独立示例中难以完整演示。以下为一个最小的编译与执行流程片段（基于同插件中的测试用例风格）：

**Header (MyNeuralShader.h)**:

```cpp
#pragma once

#include "NNERuntimeIREEShader.h"
#include "NNERuntimeIREEShaderType.h"

class FMyNeuralShader : public FNNERuntimeIREEShader
{
    DECLARE_SHADER_TYPE(FMyNeuralShader, NNERuntimeIREE);
public:
    FMyNeuralShader() = default;
    FMyNeuralShader(const FNNERuntimeIREEShaderType::CompiledShaderInitializerType& Initializer)
        : FNNERuntimeIREEShader(Initializer) {}
};
```

**Source (MyNeuralShader.cpp)**:

```cpp
#include "MyNeuralShader.h"
#include "NNERuntimeIREEShaderShared.h"

IMPLEMENT_SHADER_TYPE(, FMyNeuralShader, TEXT("/Plugin/NNERuntimeIREE/Private/MyNeural.usf"), SF_Compute);

// 注册到编译管理器（编辑器下）
#if WITH_EDITOR
void RegisterMyNeuralShader()
{
    // 创建编译作业
    FShaderCompileJob* Job = new FShaderCompileJob(
        FNNERuntimeIREEShaderType::StaticType,
        /* PermutationId */ 0
    );
    // ... 设置编译输入 ...
    GNNERuntimeIREEShaderCompilationManager.AddJobs({Job});
}
#endif
```

> 注意：实际使用时需配合 IREE 编译器生成的 Shader 字符串，而非手动编写 `.usf` 文件。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RenderCore` | Shader 类型定义、渲染资源管理 |
| `RHI` | GPU 资源句柄（Buffer、UAV）及命令提交 |
| `RenderGraph` | RDG 集成，用于声明和管理 GPU Pass |
| `ShaderCompiler` | 编辑器下异步 Shader 编译、DDC 缓存 |

其余依赖（如 `Core`, `Engine`, `CoreUObject`）为标准通用依赖，此处省略。

## 维护状态

### 近期更新

- 2025-09-26 e0d52775 — [NNE] NNERuntime IREE support of path with spaces on RelTest build on Mac for RDG.
- 2025-09-24 ca784fe6 — [NNE] NNERuntimeIREERdg always prefer wave32 to be consistent with used GPU profiles from IREE.
- 2025-09-24 1dc2a8b6 — [NNE] NNERuntimeIREE fix typo in Linux build script.
- 2025-09-24 08183aae — [NNE] NNERuntime IREE support of path with spaces on RelTest build on Mac.
- 2025-09-12 f4a4fff3 — [NNE] NNERuntimeIREE fix onnx importer dependencies not staged for Engine installed build.

### 维护评价

该插件创建于 2025-09-12，至今不足一个月，所有提交均为近期修复与功能调整，属于**活跃维护**的实验性项目。目前无已知的废弃标记，但因其实验性质，API 可能在不预先通知的情况下变更。推荐在评估性能和稳定性后用于受控的生产环境，并关注后续版本迭代。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE)
- [官方文档](https://docs.unrealengine.com/5.4/en-US/neural-network-engine-in-unreal-engine/)（NNE 整体文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE/Source/NNERuntimeIREEShader/Private/Tests)（假设目录，实际未提供）