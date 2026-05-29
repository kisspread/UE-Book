# NNERuntimeIREE

> A runtime implementing the Neural Network Engine (NNE) API which is based on IREE, MLIR and LLVM and compiles neural networks directly to game code.

| 属性 | 值 |
|---|---|
| 中文名 | IREE 神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeIREE` (Runtime), `NNERuntimeIREEEditor` (Runtime), `NNERuntimeIREEShader` (Runtime), `IREEDriverRDG` (Runtime), `IREETracing` (Runtime), `IREEUtils` (Runtime), `IREE` (External), `NNEMlirTools` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-22 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE) | |

---

## 用途

NNERuntimeIREE 是 Unreal Engine 神经网络引擎（NNE）的 **IREE 后端运行时实现**。它解决了在游戏运行时高性能执行小型神经网络的核心问题。

**核心机制**：基于 Google 的 IREE（Intermediate Representation Execution Environment）框架，利用 MLIR 和 LLVM 编译工具链，将训练好的神经网络模型编译为可直接在游戏进程中执行的原生代码——既可以编译为 CPU 指令，也可以编译为 GPU Compute Shader（HLSL）。

**与 ONNX Runtime CPU 的对比**：该插件的创建目标是替代原有的 ORTCpu 运行时。根据首次提交记录，IREE 后端在小型网络上的推理性能更优，并且跨平台支持范围更广。

**模块架构总览**：

| 模块 | 职责 |
|---|---|
| `NNERuntimeIREE` | 核心运行时，对接 NNE API，管理模型加载与推理调度 |
| `NNERuntimeIREEShader` | GPU 侧编译管线——将 IREE 生成的计算内核编译为 HLSL Compute Shader，管理 Shader Map 缓存与生命周期 |
| `IREEDriverRDG` | 基于 UE5 RDG（Render Dependency Graph）的 GPU 执行驱动，负责将推理操作编排为渲染图 |
| `IREEUtils` | IREE 运行时工具函数与通用辅助代码 |
| `IREETracing` | IREE 运行时追踪/性能分析支持 |
| `NNERuntimeIREEEditor` | 编辑器支持（模型导入、编译配置等） |
| `IREE` (External) | 第三方 IREE 运行时库封装 |
| `NNEMlirTools` (External) | 第三方 MLIR 工具链封装（负责模型编译为 IREE IR） |

---

## 使用场景

- 你在游戏中需要实时运行小型神经网络（如动作识别、AI 行为决策、风格迁移等），且需要跨平台高性能支持 → 用 NNERuntimeIREE 替代 ONNX Runtime CPU
- 你的推理任务适合 GPU 加速（大张量运算、批处理推理）→ 利用 `NNERuntimeIREEShader` 模块将网络编译为 Compute Shader
- 你需要将神经网络推理整合进 UE5 渲染管线（与 RDG 同步执行）→ 利用 `IREEDriverRDG` 模块

---

## 蓝图用法

> ⚠️ NNERuntimeIREE 是底层运行时实现，**不直接暴露蓝图节点**。游戏逻辑应通过 UE5 的通用 NNE API（`UNNEModelData`、`INNERuntime` 等）进行交互，NNE 框架会自动选择 NNERuntimeIREE 作为后端。

如需在蓝图中进行神经网络推理，请参阅 NNE 主插件文档，使用 `UNNEModelT*` 类型的蓝图节点。

---

## C++ 用法

NNERuntimeIREEShader 模块是该插件中最核心的 GPU 编译基础设施，负责将 IREE 生成的计算内核编译为 HLSL Compute Shader 并管理其生命周期。以下从源码头文件中提取关键用法。

### 头文件引入

```cpp
#include "NNERuntimeIREEShaderShared.h"      // Shader Map、Resource 核心类
#include "NNERuntimeIREEShaderType.h"        // 自定义 Shader 类型
#include "NNERuntimeIREEShaderCompileResult.h" // 编译结果结构
#include "NNERuntimeIREEShader.h"            // FNNERuntimeIREEShader 着色器类
#include "NNERuntimeIREEShaderFillBufferCS.h" // 缓冲区填充工具 Shader
#include "NNERuntimeIREEShaderMetadataAllocations.h" // 参数元数据管理
```

### 基本用法：设置与缓存 Shader 资源

`FNNERuntimeIREEResource` 是核心资源类，代表一个神经网络内核的 GPU 着色器资源。它管理从 HLSL 源码到编译后 Shader Map 的完整生命周期。

```cpp
// 来源: Internal/NNERuntimeIREEShaderShared.h — FNNERuntimeIREEResource::SetupResource()

// 1. 创建资源并配置内核参数
FNNERuntimeIREEResource ShaderResource;

// SetupResource 接收：Feature Level、友好名称、入口函数、Hash Key、
// HLSL 源码、参数元数据分配器、参数元数据指针、资产路径、缓冲区绑定索引
ShaderResource.SetupResource(
    ERHIFeatureLevel::SM5,          // 目标特性级别
    TEXT("MyNetworkKernel"),         // 友好名称
    TEXT("MainCS"),                  // Shader 入口函数名
    TEXT("shader_hash_key_12345"),   // Shader 代码的唯一 Hash
    HLSLSourceCode,                 // IREE 编译生成的 HLSL 源码
    MoveTemp(ParameterAllocations), // FNNERuntimeIREEShaderParametersMetadataAllocations
    &ShaderParamMetadata,           // FShaderParametersMetadata*
    AssetPath,                      // 使用该资源的资产路径
    BufferBindings                  // 存储缓冲区绑定索引数组（IREE command buffer 需要）
);

// 2. 缓存 Shader — 触发编译并存储结果
// bSynchronous=true 同步编译；bApplyCompletedShaderMapForRendering=true 立即可用于渲染
ShaderResource.CacheShaders(
    ERHIFeatureLevel::SM5,
    TargetPlatform,
    /*bApplyCompletedShaderMapForRendering=*/ true,
    /*bSynchronous=*/ true
);

// 3. 获取编译后的 Shader
TShaderRef<FNNERuntimeIREEShader> Shader = ShaderResource.GetShader(/*PermutationId=*/ 0);

// 4. 获取缓冲区绑定索引（用于 RDG dispatch 时的 buffer 别名处理）
uint32 BindingIdx = ShaderResource.GetBindingIndex(/*BufferIdx=*/ 0);
```

> **来源文件**: `Source/NNERuntimeIREEShader/Internal/NNERuntimeIREEShaderShared.h`

### 进阶用法：Shader Map 管理与编译管线

对于需要精细控制 Shader 编译的场景（如批量预编译、DDC 集成），可直接操作 `FNNERuntimeIREEShaderMap`：

```cpp
// 来源: Internal/NNERuntimeIREEShaderShared.h — FNNERuntimeIREEShaderMap

// 1. 构造 Shader Map ID（唯一标识一组编译参数）
FNNERuntimeIREEShaderMapId ShaderMapId;
ShaderMapId.FeatureLevel = ERHIFeatureLevel::SM5;
ShaderMapId.ShaderCodeHash = ShaderCodeHash;  // 由内核代码计算得出

// 2. 查找已缓存的 Shader Map
FNNERuntimeIREEShaderMap* CachedMap = FNNERuntimeIREEShaderMap::FindId(
    ShaderMapId, 
    GMaxRHIShaderPlatform
);

if (!CachedMap)
{
    // 3. 编译新的 Shader Map
    CachedMap = new FNNERuntimeIREEShaderMap();
    
    CachedMap->Compile(
        &ShaderResource,              // 关联的 FNNERuntimeIREEResource
        ShaderMapId,                  // 编译 ID
        CompilationEnvironment,       // 共享编译环境
        CompilationOutput,            // FNNERuntimeIREECompilationOutput
        GMaxRHIShaderPlatform,
        /*bSynchronousCompile=*/ true,
        /*bApplyCompletedShaderMapForRendering=*/ true
    );
}

// 4. 注册到全局 Shader Map 表（使渲染线程可访问）
CachedMap->Register(GMaxRHIShaderPlatform);

// 5. 检查编译完整性
bool bComplete = CachedMap->IsComplete(&ShaderResource, /*bSilent=*/ false);
```

> **来源文件**: `Source/NNERuntimeIREEShader/Internal/NNERuntimeIREEShaderShared.h`

### 缓冲区填充工具 Shader

`FFillBufferCS` 是一个内置的工具 Compute Shader，用于用常量值快速填充 ByteAddressBuffer：

```cpp
// 来源: Internal/NNERuntimeIREEShaderFillBufferCS.h

// 该 Shader 使用 256 线程组，通过 RDG 执行
// 参数结构：
//   TargetBuffer — RWByteAddressBuffer（目标缓冲区）
//   Fill         — FUintVector4（填充值，4 个 uint32）

// 在 RDG Pass 中使用示例：
FFillBufferCS::FParameters* PassParameters = 
    GraphBuilder.AllocParameters<FFillBufferCS::FParameters>();
PassParameters->TargetBuffer = GraphBuilder.CreateUAV(TargetBuffer);
PassParameters->Fill = FUintVector4(0, 0, 0, 0);  // 清零

TShaderMapRef<FFillBufferCS> ComputeShader(GetGlobalShaderMap(GMaxRHIFeatureLevel));
FComputeShaderUtils::AddPass(
    GraphBuilder,
    RDG_EVENT_NAME("FillBuffer"),
    ComputeShader,
    PassParameters,
    FIntVector(NumElements / FFillBufferConstants::THREAD_GROUP_SIZE, 1, 1)
);
```

> **来源文件**: `Source/NNERuntimeIREEShader/Internal/NNERuntimeIREEShaderFillBufferCS.h`

---

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建一个 `FNNERuntimeIREEResource` 并完成 Shader 编译：

```cpp
// MyNNEKernelResource.h
#pragma once

#include "NNERuntimeIREEShaderShared.h"

class FMyNNEKernelResource : public FNNERuntimeIREEResource
{
public:
    void Initialize(
        ERHIFeatureLevel::Type InFeatureLevel,
        const FString& InHLSLSource,
        const FString& InEntryPoint,
        const FString& InShaderHashKey,
        FName InAssetPath);

    // 可选：自定义哪些 Shader 类型需要编译
    virtual bool ShouldCache(EShaderPlatform InPlatform, const FShaderType* InShaderType) const override
    {
        return FNNERuntimeIREEResource::ShouldCache(InPlatform, InShaderType);
    }

    // 编译完成回调
    virtual void NotifyCompilationFinished(FString const& ResultMessage) override;
};
```

```cpp
// MyNNEKernelResource.cpp
#include "MyNNEKernelResource.h"
#include "NNERuntimeIREEShaderMetadataAllocations.h"
#include "ShaderParameterStruct.h"

void FMyNNEKernelResource::Initialize(
    ERHIFeatureLevel::Type InFeatureLevel,
    const FString& InHLSLSource,
    const FString& InEntryPoint,
    const FString& InShaderHashKey,
    FName InAssetPath)
{
    // 分配参数元数据
    auto MetadataAllocations = MakeUnique<FNNERuntimeIREEShaderParametersMetadataAllocations>();
    
    // 根据实际 Shader 参数布局构造 FShaderParametersMetadata
    FShaderParametersMetadataBuilder Builder;
    Builder.AddParam(TEXT("InputBuffer"), ESamplerType::SAMPLER_TYPE_UINT);
    Builder.AddParam(TEXT("OutputBuffer"), ESamplerType::SAMPLER_TYPE_UINT);
    MetadataAllocations->ShaderParameterMetadatas = Builder.Build(TEXT("MyKernelParameters"));
    FShaderParametersMetadata* ParamMetadata = MetadataAllocations->ShaderParameterMetadatas.Get();

    // 存储缓冲区绑定索引（IREE 可能将多个张量映射到同一个 RDG buffer）
    TArray<uint32> BufferBindings = { 0, 1 };

    SetupResource(
        InFeatureLevel,
        TEXT("MyNNEKernel"),
        InEntryPoint,
        InShaderHashKey,
        InHLSLSource,
        MoveTemp(MetadataAllocations),
        ParamMetadata,
        InAssetPath,
        BufferBindings
    );

    // 异步编译 Shader
    CacheShaders(InFeatureLevel, nullptr, true, false);
}

void FMyNNEKernelResource::NotifyCompilationFinished(FString const& ResultMessage)
{
    FNNERuntimeIREEResource::NotifyCompilationFinished(ResultMessage);

    if (const FNNERuntimeIREEShaderCompileResults& Results = GetCompilationResults(); !Results.Messages.IsEmpty())
    {
        for (const FNNERuntimeIREEShaderCompileMessage& Msg : Results.Messages)
        {
            if (Msg.Type == FNNERuntimeIREEShaderCompileMessage::EMessageType::Error)
            {
                UE_LOG(LogNNERuntimeIREEShader, Error,
                    TEXT("Shader compile error at %s:%d — %s"),
                    *Msg.VirtualFilePath, Msg.Line, *Msg.Text);
            }
        }
    }
}
```

---

## 模块依赖

本插件内模块众多，以下仅列出 **独特** 的、非通用的外部依赖关系（基于模块间的依赖链推断）：

| 模块 | 用途 |
|---|---|
| `NNE` | UE5 神经网络引擎核心 API 定义（INNERuntime 接口） |
| `ShaderCore` | Shader 类型系统、Shader Map 基础设施 |
| `RenderCore` | 渲染核心（FShaderMapContent、Shader 编译管线） |
| `RHICore` | RHI 核心抽象层 |
| `Renderer` | 渲染器模块（RDG 图构建与执行） |
| `IREE` (External) | IREE 运行时 C API 封装 |
| `NNEMlirTools` (External) | MLIR 工具链（模型编译为 IREE IR） |
| `IREETracing` | IREE 运行时性能追踪 |

> 使用者（游戏项目模块）通常只需依赖 `NNE` 即可，运行时后端的选择由 NNE 框架自动完成。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `9456b28d` | [NNE] NNERuntimeIREERdg fix cross-thread use-after-free during shader cook. | 修复 Shader Cook 期间跨线程的 use-after-free 内存错误 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式化字符串中 32/64 位说明符不匹配的问题 |
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 统一 GPU 等待接口，用新 API 替代旧调用 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新的 UE_LOGF 格式 |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored | 重构 Shader 编译 Job 结构体，移除冗余状态标记 |

### 维护评价

- **活跃维护中** ✅：最近 5 次提交全部集中在 2026 年 4-5 月，间距约 1-2 周，说明该插件处于高频迭代阶段
- **实验性标记**：`.uplugin` 标记为 `IsExperimentalVersion=true`，位于 `Engine/Plugins/Experimental/` 目录，API 稳定性尚无保证
- **持续改进**：最近的改动涵盖线程安全修复（use-after-free）、API 统一化、代码质量清理等，表明 Epic 正在从原型阶段走向生产就绪
- **注意事项**：
  - 作为实验性插件，API 可能在引擎版本间发生破坏性变更
  - 默认未启用，需要在项目设置中手动启用
  - 部分平台支持依赖 IREE/LLVM 后端的成熟度
- **推荐程度**：如果你的项目需要高性能跨平台神经网络推理，且可以接受实验性 API，推荐关注并试用。生产环境建议等待正式发布。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE)
- [NNE 插件源码（主插件）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE)
- [IREE 项目主页](https://iree.dev/)