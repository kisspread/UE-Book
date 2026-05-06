# NiagaraVertexFactories

> Niagara effect systems.

| 属性 | 值 |
|---|---|
| 中文名 | 尼亚加拉顶点工厂 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（渲染资源、着色器、顶点工厂） |
| 模块 | `NiagaraVertexFactories` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara/Source/NiagaraVertexFactories) | |

## 用途

`NiagaraVertexFactories` 是 Niagara 粒子系统的底层渲染模块。它提供了一系列 **GPU 顶点工厂（Vertex Factory）** 和 **计算着色器（Compute Shader）**，用于将粒子数据转换为 GPU 可渲染的几何体。该模块不参与 Niagara 系统的编辑或逻辑，而是专注于高性能的渲染管线集成。

具体功能包括：

- **顶点工厂**：定义粒子渲染时的顶点布局和缓冲区绑定，支持 Sprite（精灵）、Ribbon（丝带）、Mesh（网格）三种渲染类型。
- **GPU 排序与剔除**：提供计算着色器用于粒子排序（按键值、距离等）和视锥剔除，减少无效绘制。
- **间接绘制参数生成**：生成 GPU 驱动的间接绘制参数，提升绘制调用的批量处理能力。
- **射线追踪支持**：将粒子实例变换传递给顶层加速结构（TLAS），用于硬件光线追踪。
- **Cutout 纹理处理**：支持粒子裁剪 UV 数据。
- **基础参数结构**：定义了大量着色器参数结构体（如 `FNiagaraSpriteUniformParameters`、`FNiagaraMeshUniformParameters`），供材质和着色器使用。

为什么存在？因为 Niagara 需要一种高效、可扩展的方式在 GPU 上渲染数百万粒子，而标准网格或精灵渲染无法满足其动态属性。该模块将粒子数据与顶点工厂松耦合，允许 Niagar 粒子系统在 GPU 上运行时直接驱动渲染，避免 CPU-GPU 之间频繁的数据传输。

## 使用场景

- 你正在创建使用 Niagara 粒子系统的项目，希望渲染 Sprite、Ribbon 或 Mesh 类型的粒子，该模块自动被引擎加载。
- 需要编写自定义 Niagara 渲染器或着色器，需要了解粒子顶点工厂的绑定方式。
- 调试或优化粒子渲染性能时，需要分析间接绘制参数的生成逻辑或 GPU 排序行为。
- 开发支持 Niagara 粒子变换的自定义光线追踪场景。

## 蓝图用法

由于该模块是底层渲染模块，**不提供任何可直接在蓝图中调用的函数**。所有的 API 都是 C++ 类或着色器声明，用于引擎内部和插件开发。

不过，Niagara 粒子系统的 Sprite、Ribbon、Mesh 渲染器可以在编辑器的 Niagara 组件中选择，并绑定相关材质。这些渲染器内部即使用本模块的顶点工厂。

**对于大多数蓝图用户**，仅需在 Niagara 系统编辑器中选择渲染器类型（Sprite/Ribbon/Mesh），其余由引擎自动处理。

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraVertexFactory.h"
#include "NiagaraSpriteVertexFactory.h"
#include "NiagaraRibbonVertexFactory.h"
#include "NiagaraMeshVertexFactory.h"
#include "NiagaraSortingGPU.h"
#include "NiagaraDrawIndirect.h"
#include "NiagaraDispatchIndirect.h"
#include "NiagaraGPURayTracingTransformsShader.h"
#include "NiagaraCutoutVertexBuffer.h"
```

### 基本用法

#### 1. 访问 Niagara 顶点工厂基础类

`FNiagaraVertexFactoryBase` 是所有 Niagara 顶点工厂的基类，派生自 `FVertexFactory`。通常不需要手动创建，Niagara 渲染器会在每帧自动创建。

```cpp
// 在自定义渲染器中获取顶点工厂
ENiagaraVertexFactoryType FactoryType = NVFT_Sprite; // 或 NVFT_Ribbon, NVFT_Mesh
ERHIFeatureLevel::Type FeatureLevel = GMaxRHIFeatureLevel;
TUniquePtr<FNiagaraVertexFactoryBase> Factory;

switch (FactoryType)
{
case NVFT_Sprite:
    Factory = MakeUnique<FNiagaraSpriteVertexFactory>(NVFT_Sprite, FeatureLevel);
    break;
case NVFT_Ribbon:
    Factory = MakeUnique<FNiagaraRibbonVertexFactory>(NVFT_Ribbon, FeatureLevel);
    break;
case NVFT_Mesh:
    Factory = MakeUnique<FNiagaraMeshVertexFactory>(NVFT_Mesh, FeatureLevel);
    break;
}
```

#### 2. 使用 GPU 排序计算着色器

`FNiagaraSortKeyGenCS` 负责为粒子生成排序键并执行视锥剔除。通常由 `FNiagaraGPUSortManager` 调用，但也可以手动触发。

```cpp
// 来自: Source/NiagaraVertexFactories/Public/NiagaraSortingGPU.h
FNiagaraSortKeyGenCS::FParameters SortParams;
SortParams.NiagaraParticleDataFloat = ParticleDataFloatSRV;
SortParams.NiagaraParticleDataHalf = ParticleDataHalfSRV;
SortParams.NiagaraParticleDataInt = ParticleDataIntSRV;
SortParams.GPUParticleCountBuffer = ParticleCountSRV;
SortParams.FloatDataStride = FloatStride;
SortParams.ParticleCount = NumParticles;
SortParams.SortMode = static_cast<uint32>(ENiagaraSortMode::SortAscending);
// ... 填写其他参数

// 创建计算指令
FComputeShaderUtils::Dispatch(RHICmdList, Shader, SortParams, FIntVector(FMath::DivideAndRoundUp(NumParticles, NIAGARA_KEY_GEN_THREAD_COUNT), 1, 1));
```

#### 3. 生成间接绘制参数

`FNiagaraDrawIndirectArgsGenCS` 根据实例计数器生成用于 `DrawIndexedIndirect` 的参数。

```cpp
// 来自: Source/NiagaraVertexFactories/Public/NiagaraDrawIndirect.h
FNiagaraDrawIndirectArgsGenCS::FParameters DrawParams;
DrawParams.TaskInfos = TaskInfoSRV;
DrawParams.CulledInstanceCounts = CulledInstanceCountSRV;
DrawParams.RWInstanceCounts = InstanceCountUAV;
DrawParams.RWDrawIndirectArgs = DrawIndirectArgsUAV;
DrawParams.TaskCount = FUintVector4(NumTasks, 0, 0, 0);

auto* ShaderMap = GetGlobalShaderMap(FeatureLevel);
auto* Shader = ShaderMap->GetShader<FNiagaraDrawIndirectArgsGenCS>();
FComputeShaderUtils::Dispatch(RHICmdList, Shader, DrawParams, FIntVector(FMath::DivideAndRoundUp(NumTasks, NIAGARA_DRAW_INDIRECT_ARGS_GEN_THREAD_COUNT), 1, 1));
```

#### 4. 设置 Cutout 顶点缓冲区

`FNiagaraCutoutVertexBuffer` 用于存储粒子裁剪 UV，在渲染 Sprite 时使用。

```cpp
// 创建缓冲区并填充数据
FNiagaraCutoutVertexBuffer CutoutBuffer;
CutoutBuffer.Data.Add(FVector2f(0.0f, 0.0f));
CutoutBuffer.Data.Add(FVector2f(1.0f, 0.0f));
CutoutBuffer.Data.Add(FVector2f(1.0f, 1.0f));
CutoutBuffer.Data.Add(FVector2f(0.0f, 1.0f));

// 初始化 RHI
FRHICommandListImmediate& RHICmdList = FRHICommandListExecutor::GetImmediateCommandList();
CutoutBuffer.InitRHI(RHICmdList);
```

### 进阶用法

#### 自定义 Niagara 渲染器中使用顶点工厂

在开发自定义 Niagara 渲染器时，需要重写 `CreateVertexFactory()` 和 `Render()` 方法。以下是一个简化的 Sprite 渲染器示例：

```cpp
// 假设你继承自 UNiagaraRendererProperties
class UMyNiagaraSpriteRenderer : public UNiagaraRendererProperties
{
    TUniquePtr<FNiagaraSpriteVertexFactory> VertexFactory;

    virtual void CreateVertexFactory() override
    {
        VertexFactory = MakeUnique<FNiagaraSpriteVertexFactory>(NVFT_Sprite, GMaxRHIFeatureLevel);
        // 设置顶点声明等...
        VertexFactory->InitResource();
    }

    virtual void Render(FRHICommandList& RHICmdList, const FNiagaraRendererRenderData& Data) override
    {
        // 获取 uniform buffer 参数
        FNiagaraSpriteUniformParameters UniformParams;
        UniformParams.bLocalSpace = Data.bLocalSpace ? 1 : 0;
        // ... 填充其他参数

        // 创建 UBO
        FNiagaraSpriteUniformBufferRef UniformBuffer = FNiagaraSpriteUniformBufferRef::CreateUniformBufferImmediate(UniformParams, UniformBuffer_MultiFrame);

        // 设置顶点工厂状态
        VertexFactory->SetUniformBuffer(UniformBuffer);
        // 绑定 mesh batch 并提交绘制
        // ...
    }
};
```

#### 实现 GPU 粒子剔除的完整流程

参考 `FNiagaraSortKeyGenCS` 的用法，结合 `FNiagaraGPUSortInfo` 结构体（定义在 `NiagaraSortingGPU.h` 中），可以实现自定义的粒子排序与剔除。

```cpp
// 从 Niagara 系统获取排序信息
FNiagaraGPUSortInfo SortInfo;
// ... 填充 SortInfo

FNiagaraSortKeyGenCS::FParameters SortParams;
SortParams.NiagaraParticleDataFloat = SortInfo.ParticleDataFloatSRV;
SortParams.CameraPosition = SortInfo.ViewOrigin;
SortParams.CameraDirection = SortInfo.ViewDirection;
SortParams.SortMode = static_cast<uint32>(SortInfo.SortMode);
SortParams.CullPlanes[0] = SortInfo.CullPlanes[0]; // 最多12个平面
SortParams.CullDistanceRangeSquared = FVector2f(FMath::Square(SortInfo.PreCullDistance), FMath::Square(SortInfo.PostCullDistance));
SortParams.NumCullPlanes = SortInfo.NumCullPlanes;
SortParams.RendererVisibility = SortInfo.RendererVisibility;
// ... 其他参数

auto* Shader = GetGlobalShaderMap(FeatureLevel)->GetShader<FNiagaraSortKeyGenCS>();
FComputeShaderUtils::Dispatch(RHICmdList, Shader, SortParams, 
    FIntVector(FMath::DivideAndRoundUp(SortInfo.ParticleCount, NIAGARA_KEY_GEN_THREAD_COUNT), 1, 1));
```

## Demo 示例

一个最小化的示例，展示如何在自定义渲染器中获取并使用 `FNiagaraSpriteVertexFactory` 的 Uniform 参数。

**MyNiagaraRenderer.h**
```cpp
#pragma once

#include "NiagaraRendererProperties.h"
#include "NiagaraSpriteVertexFactory.h"

class FMyNiagaraSpriteVertexFactory : public FNiagaraSpriteVertexFactory
{
public:
    FMyNiagaraSpriteVertexFactory(ERHIFeatureLevel::Type InFeatureLevel)
        : FNiagaraSpriteVertexFactory(NVFT_Sprite, InFeatureLevel) {}

    void SetCustomParameters(const FNiagaraSpriteUniformParameters& Params)
    {
        UniformBuffer = FNiagaraSpriteUniformBufferRef::CreateUniformBufferImmediate(Params, UniformBuffer_MultiFrame);
    }

    const FNiagaraSpriteUniformBufferRef& GetUniformBuffer() const { return UniformBuffer; }

protected:
    FNiagaraSpriteUniformBufferRef UniformBuffer;
};
```

**MyNiagaraRenderer.cpp**
```cpp
#include "MyNiagaraRenderer.h"

void FMyNiagaraSpriteVertexFactory::InitResource()
{
    FNiagaraSpriteVertexFactory::InitResource();
    // 还可以设置其他 ShaderParameter 绑定
}

// 在渲染循环中使用
void RenderMyParticles(FRHICommandList& RHICmdList, ERHIFeatureLevel::Type FeatureLevel, const FNiagaraSpriteUniformParameters& Params)
{
    FMyNiagaraSpriteVertexFactory VertexFactory(FeatureLevel);
    VertexFactory.SetCustomParameters(Params);

    // 假设已经准备好了 MeshBatch
    FMeshBatch MeshBatch;
    MeshBatch.VertexFactory = &VertexFactory;
    // ... 设置其他 MeshBatch 属性

    // 提交绘制
    // DrawIndexedPrimitive 等
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NiagaraCore` | 提供核心类型和基础数据结构 |
| `NiagaraShader` | 共享着色器相关定义和编译环境 |
| `Niagara` | 提供数据接口（如粒子数据访问） |
| `Renderer` | 渲染基础框架 |
| `RHI` | 图形 API 抽象层 |

**无特殊依赖**：所有依赖均为 Niagara 引擎内部模块。

## 维护状态

### 近期更新

- 2025-10-22 `5d0cd83c` — Fix for issue with access to freed Niagara Components during cleanup.
- 2025-10-22 `3f549682` — Fixed issue with lingering NDC data when there are updates with no data from the CPU.
- 2025-10-21 `6ac05a79` — Added off-by-default workaround for Niagara crash we hit in internal testing.
- 2025-10-17 `f6546371` — Fix issue caused by mis-matched GT and RT ticks causing NDC data to be effectively lost from the POV
- 2025-10-16 `566219ca` — [Backout] - CL47013072

### 维护评价

- **创建时间**：2025-10-16（约0年，全新模块）
- **最近更新频率**：每日都有修复提交，非常活跃。
- **近期内容**：主要是 Bug 修复（组件清理、数据匹配、崩溃处理），说明模块尚在快速迭代阶段。
- **是否活跃维护**：是，正在积极维护。
- **已知问题**：存在因 GameThread 和 RenderThread 不同步导致的数据丢失问题（已修复或 workaround 中）。
- **推荐使用**：作为 Niagara 的基础渲染模块，推荐与 Niagara 生态系统一起使用。但需注意其较新，可能存在未发现的边缘情况，建议保持引擎版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara/Source/NiagaraVertexFactories)
- [官方文档（Niagara 整体）](https://docs.unrealengine.com/5.0/zh-CN/niagara-effects-for-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara/Tests)