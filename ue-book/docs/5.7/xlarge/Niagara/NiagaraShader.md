# NiagaraShader（Niagara 着色器模块）

| 属性 | 值 |
|---|---|
| 中文名 | Niagara 着色器 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（GPU 着色器代码、头文件、编译管理工具） |
| 模块 | `NiagaraShader` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara/Source/NiagaraShader) | |

---

## 用途

`NiagaraShader` 模块是 Niagara 粒子系统的**GPU 计算着色器核心基础设施**。它提供：

- 仿真着色器的基类（`FNiagaraShader`）及全局参数结构（时间、系统、所有者参数）
- 无状态（Stateless）粒子模拟的着色器实现（`NiagaraStatelessEmitterShaders.h`）
- 异步 GPU 光线追踪支持（`FNiagaraAsyncGpuTraceProvider` 及 Gsdf / Hwrt 实现）
- 着色器参数自动构建工具（`FNiagaraShaderParametersBuilder`），用于数据接口自定义参数
- 计数缓冲区清零、调试绘制、Mip 生成、GPU 场景粒子更新等实用工具
- 丝带（Ribbon）计算着色器、稀疏体积纹理（SVT）变换着色器

该模块不直接包含粒子系统的编辑或运行时逻辑，而是作为**底层着色器层**，被 `Niagara`（Runtime）和 `NiagaraEditor` 模块使用。

---

## 使用场景

- 你需要**编写自定义 Niagara 数据接口**并在 GPU 上运行 → 使用 `FNiagaraShaderParametersBuilder` 注册着色器参数
- 你需要**实现自定义 GPU 追踪**（例如基于距离场或硬件光线追踪）→ 继承 `FNiagaraAsyncGpuTraceProvider`
- 你需要**在渲染过程中操作 Niagara GPU 缓冲区**（如清零计数、生成 Mip）→ 使用 `NiagaraClearCounts` / `NiagaraGenerateMips` 命名空间函数
- 你需要**使用无状态 GPU 模拟**（Stateless 模式）→ 该模块提供 `FSimulationShaderDefaultCS` 等全套着色器
- 你需要**调试 Niagara 粒子可视化** → 使用 `NiagaraDebugShaders` 中的绘制和纹理可视化功能

---

## 蓝图用法

该模块主要面向 C++ 和着色器，蓝图直接暴露的 API 较少。以下是在蓝图中可能用到的枚举和结构（部分来自 `NiagaraShader` 包含的头文件）：

| UENUM / USTRUCT | 说明 | 所在文件 |
|---|---|---|
| `ENiagaraGpuDispatchType` | GPU 分发类型（OneD / TwoD / ThreeD / Custom） | `NiagaraScriptBase.h` |
| `ENiagaraDirectDispatchElementType` | 元素计数类型（线程数 / 线程数无裁剪 / 组数） | `NiagaraScriptBase.h` |
| `ENiagaraSimStageExecuteBehavior` | 模拟阶段执行策略（Always / OnReset / NotOnReset） | `NiagaraScriptBase.h` |
| `FSimulationStageMetaData` | 模拟阶段的元数据（名称、元素计数、迭代源等） | `NiagaraScriptBase.h` |
| `FNiagaraCompileEvent` | 编译事件（严重度、消息、节点 GUID） | `NiagaraShared.h` |
| `ENiagaraMipMapGenerationType` | Mip 生成滤波器类型（Unfiltered / Linear / Blur1-4） | `NiagaraGenerateMips.h` |

这些类型通常用于**自定义 Niagara 脚本**或**数据接口**的 Blueprint 可访问属性，但本身没有单独的 BlueprintCallable 函数节点。

---

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraShader.h"                     // FNiagaraShader 及其参数结构
#include "NiagaraShaderParametersBuilder.h"    // 数据接口参数构建器
#include "NiagaraAsyncGpuTraceProvider.h"      // 异步 GPU 追踪
#include "NiagaraClearCounts.h"                // 计数清零
#include "NiagaraDebugShaders.h"               // 调试绘制
#include "NiagaraGenerateMips.h"               // Mip 生成
#include "NiagaraGPUSceneUtils.h"              // GPU 场景粒子更新
#include "NiagaraRibbonCompute.h"              // 丝带计算着色器
#include "NiagaraSVTShaders.h"                 // 稀疏体积纹理
```

### 基本用法

#### 1. 使用着色器构建器注册数据接口参数

```cpp
// 在数据接口的 GetParameterDefinitionHLSL 或相关函数中调用
void UMyNiagaraDataInterface::BuildShaderParameters(FNiagaraShaderParametersBuilder& ShaderParametersBuilder) const
{
    // 添加一个作用域浮点参数（最终名称为 "UniqueName_MyFloat"）
    ShaderParametersBuilder.AddLooseParam<float>(TEXT("MyFloat"));

    // 添加一个作用域向量参数
    ShaderParametersBuilder.AddLooseParam<FVector3f>(TEXT("MyVector"));

    // 添加嵌套结构体（结构体中的成员自动带上作用域前缀）
    ShaderParametersBuilder.AddNestedStruct<FMyStruct>();

    // 添加全局结构体（无作用域）
    ShaderParametersBuilder.AddIncludedStruct(FMyGlobalParameters::FTypeInfo::GetStructMetadata());
}
```
*来源: `Public/NiagaraShaderParametersBuilder.h`*

#### 2. 异步 GPU 追踪提供者

```cpp
// 创建一个距离场追踪提供者（需在支持距离场的平台上）
FNiagaraAsyncGpuTraceProviderGsdf Provider(ShaderPlatform, Dispatcher);
if (Provider.IsAvailable())
{
    FNiagaraAsyncGpuTraceProvider::FDispatchRequest Request;
    Request.TracesBuffer = &TracesBuffer;
    Request.ResultsBuffer = &ResultsBuffer;
    Request.TraceCountsBuffer = &TraceCountsBuffer;

    Provider.IssueTraces(RHICmdList, Request, SceneUniformBuffer, CollisionGroupHashMap);
}
```
*来源: `Private/NiagaraAsyncGpuTraceProviderGsdf.h`, `Public/NiagaraAsyncGpuTraceProvider.h`*

#### 3. 清零计数缓冲区

```cpp
FRDGBuilder& GraphBuilder; // 假设已存在
FRDGBufferUAVRef CountUAV = GraphBuilder.CreateUAV(CountBuffer);

TArray<TPair<uint32, int32>> IndexValues;
IndexValues.Emplace(0, 0);   // 将索引 0 的值设为 0
IndexValues.Emplace(1, 100); // 将索引 1 的值设为 100

NiagaraClearCounts::ClearCountsInt(GraphBuilder, CountUAV, IndexValues);
```
*来源: `Public/NiagaraClearCounts.h`*

#### 4. 生成 Mip 链

```cpp
FRDGTextureRef InputTexture; // 假设已有
ENiagaraMipMapGenerationType GenType = ENiagaraMipMapGenerationType::Linear;
NiagaraGenerateMips::GenerateMips(GraphBuilder, InputTexture, GenType);
```
*来源: `Public/NiagaraGenerateMips.h`*

#### 5. 更新 GPU 场景粒子实例

```cpp
FNiagaraGPUSceneUtils::FUpdateMeshParticleInstancesParams Params;
// ...填充参数
FNiagaraGPUSceneUtils::AddUpdateMeshParticleInstancesPass(GraphBuilder, Params, FeatureLevel, bPreciseMotionVectors);
```
*来源: `Public/NiagaraGPUSceneUtils.h`*

---

### 进阶用法

**自定义光线追踪提供者**：继承 `FNiagaraAsyncGpuTraceProvider`，实现 `IssueTraces()`，并使用 `FCollisionGroupHashMap` 进行碰撞组映射。参考 `Private/NiagaraAsyncGpuTraceProviderHwrt.h`（硬件光线追踪）或 `NiagaraAsyncGpuTraceProviderGsdf.h`（全局距离场）。

**无状态仿真着色器**：在 `Internal/Stateless/NiagaraStatelessEmitterShaders.h` 中提供了完整的仿真着色器 `FSimulationShaderDefaultCS`，其参数结构包含初始化、预求解、后求解等多个模块的着色器参数。你可以通过宏 `ADD_STATELESS_MODULE` 组合这些模块。

---

## Demo 示例

以下示例演示如何在一个自定义数据接口中注册着色器参数，并使用 `NiagaraClearCounts` 清零一个 GPU 计数器。

### MyCustomInterface.h

```cpp
#pragma once

#include "NiagaraDataInterface.h"
#include "NiagaraDataInterface.generated.h"

UCLASS()
class UMyCustomInterface : public UNiagaraDataInterface
{
    GENERATED_BODY()

public:
    // 着色器参数构建
    virtual void BuildShaderParameters(FNiagaraShaderParametersBuilder& ShaderParametersBuilder) const override;
};
```

### MyCustomInterface.cpp

```cpp
#include "MyCustomInterface.h"
#include "NiagaraShaderParametersBuilder.h"

void UMyCustomInterface::BuildShaderParameters(FNiagaraShaderParametersBuilder& ShaderParametersBuilder) const
{
    // 添加一个作用域浮点数参数
    ShaderParametersBuilder.AddLooseParam<float>(TEXT("MyFloat"));
    // 添加一个作用域向量参数
    ShaderParametersBuilder.AddLooseParam<FVector3f>(TEXT("MyVector"));
}
```

### 使用计数清零（在渲染线程）

```cpp
#include "NiagaraClearCounts.h"

void MyFunc(FRDGBuilder& GraphBuilder, FRDGBufferRef CountBuffer)
{
    FRDGBufferUAVRef CountUAV = GraphBuilder.CreateUAV(CountBuffer);
    
    // 将索引 0 和 1 分别清零和设为 42
    TArray<TPair<uint32, uint32>> IndexValues;
    IndexValues.Emplace(0, 0);
    IndexValues.Emplace(1, 42);
    
    NiagaraClearCounts::ClearCountsUInt(GraphBuilder, CountUAV, IndexValues);
}
```

该示例需要你的模块依赖 `NiagaraShader` 和 `RenderCore`。`Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "NiagaraShader", "RenderCore", "RHI" });
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NiagaraCore` | GPU 参数信息（`FNiagaraDataInterfaceGPUParamInfo`）、数据接口基础结构 |
| `NiagaraVertexFactories` | 网格粒子顶点工厂（用于 GPU 场景更新） |
| `RenderCore` | 全局着色器、渲染图、RHI 资源 |
| `Renderer` | 场景统一缓冲区、距离场参数 |

其余均为标准引擎模块（Core, Engine, RHI 等），已省略。

---

## 维护状态

### 近期更新

- 2025-10-22 `5d0cd83c` — Fix for issue with access to freed Niagara Components during cleanup.（修复清理时访问已释放 Niagara 组件的问题）
- 2025-10-22 `3f549682` — Fixed issue with lingering NDC data when there are updates with no data from the CPU.（修复 CPU 无数据时残留 NDC 数据的问题）
- 2025-10-21 `6ac05a79` — Added off-by-default workaround for Niagara crash we hit in internal testing.（添加默认关闭的内部测试崩溃规避方案）
- 2025-10-17 `f6546371` — Fix issue caused by mis-matched GT and RT ticks causing NDC data to be effectively lost.（修复 GT/RT 节拍不匹配导致 NDC 数据丢失的问题）
- 2025-10-16 `566219ca` — [Backout] - CL47013072（回退某个提交）

### 维护评价

该模块近期更新非常频繁且聚焦于修复崩溃和数据一致性问题，表现出**活跃维护**状态。创建时间虽然标注为 2025-10-16（最新 git 记录），但实际模块可能早已存在（Niagara 在 UE4 早期已引入）。从提交内容看，开发者正积极解决边缘情况，模块质量稳定。推荐在生产环境中使用。

---

## 相关链接

- [源码（模块根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara/Source/NiagaraShader)
- [官方文档（Niagara 总文档）](https://docs.unrealengine.com/5.3/en-US/niagara-effects-system-in-unreal-engine/)
- [测试用例（Niagara 整体测试）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara/Tests)