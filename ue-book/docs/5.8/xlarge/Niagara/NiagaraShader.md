# Niagara

> Niagara effect systems.

| 属性 | 值 |
|---|---|
| 中文名 | 尼亚加拉粒子系统 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（粒子系统资产、蓝图节点、编辑器工具） |
| 模块 | `Niagara` (Runtime), `NiagaraAnimNotifies` (Runtime), `NiagaraBlueprintNodes` (Runtime), `NiagaraCore` (Runtime), `NiagaraEditor` (Runtime), `NiagaraEditorWidgets` (Runtime), `NiagaraShader` (Runtime), `NiagaraVertexFactories` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-28 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara) | |

## 用途

Niagara 是 Unreal Engine 的**下一代 GPU 粒子系统**，旨在取代旧版 Cascade 粒子系统。它提供了一个基于节点图（Node Graph）的可视化编辑器，用于创建复杂的粒子效果，支持 CPU 和 GPU 两种模拟路径。

Niagara 的核心设计理念是**模块化和可扩展性**。与 Cascade 的固定功能管线不同，Niagara 允许开发者通过堆叠模块（Modules）来自定义粒子的发射、更新、渲染等各个阶段。它支持：

- **GPU 计算着色器模拟**：在 GPU 上执行大规模粒子模拟，支持数百万粒子
- **数据接口（Data Interface）**：允许粒子系统与其他引擎系统（如网格体、距离场、LWC 等）交互
- **蓝图与 C++ 扩展**：通过蓝图节点和 C++ 数据接口实现自定义逻辑
- **Ribbons（丝带）与 Mesh 粒子**：支持多种渲染模式
- **Stateless 仿真**：优化的无状态 GPU 仿真路径，适用于简单效果
- **GPU 光线追踪碰撞查询**：粒子可以与场景进行光线追踪级别的交互

## 使用场景

- 你需要创建大规模 GPU 粒子效果（烟、火、爆炸、魔法特效）→ 用 Niagara 系统
- 你需要粒子与场景进行碰撞检测（网格体碰撞或 GPU 光线追踪）→ 用 Niagara 的 Collision Query Data Interface
- 你需要自定义粒子行为逻辑（蓝图或 C++）→ 用 Niagara 的模块化编辑器和 Data Interface 扩展
- 你需要将 Sparse Volume Texture 应用于粒子效果 → 用 Niagara SVT 相关功能
- 你需要在动画蒙太奇事件中触发粒子效果 → 用 NiagaraAnimNotifies 模块

## 蓝图用法

Niagara 的蓝图 API 主要分布在 `NiagaraBlueprintNodes` 模块中，以下是从源码中提取的核心节点（`UNiagaraFunctionLibrary` 提供）：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SpawnSystemAtLocation` | 在指定世界位置生成 Niagara 系统实例 | `UNiagaraFunctionLibrary` |
| `SpawnSystemAttached` | 将 Niagara 系统附加到组件上生成 | `UNiagaraFunctionLibrary` |
| `SpawnSystemAtLocationWithParams` | 使用参数结构体在指定位置生成系统 | `UNiagaraFunctionLibrary` |
| `Set NiagaraIntVariable` | 设置 Niagara 系统中的整数参数 | `UNiagaraFunctionLibrary` |
| `Set NiagaraFloatVariable` | 设置 Niagara 系统中的浮点参数 | `UNiagaraFunctionLibrary` |
| `Set NiagaraVectorVariable` | 设置 Niagara 系统中的向量参数 | `UNiagaraFunctionLibrary` |
| `Set NiagaraColorVariable` | 设置 Niagara 系统中的颜色参数 | `UNiagaraFunctionLibrary` |
| `Override System User Variable Component` | 覆盖系统用户变量中的特定组件 | `UNiagaraFunctionLibrary` |
| `Get Niagara Effect Position` | 获取 Niagara 效果的世界位置 | `UNiagaraFunctionLibrary` |

### 使用示例（蓝图描述）

在蓝图中生成一个 Niagara 粒子系统：

1. **拖放生成**：在任意蓝图中，使用 `SpawnSystemAtLocation` 节点
2. **连接参数**：将 `World Context`（通常是 Self）、`System Template`（Niagara 系统资产）、`Spawn Location`（世界坐标）和 `Rotation` 连接
3. **保存引用**：将返回的 `NiagaraComponent` 保存为变量，后续可用于修改参数或停止效果
4. **动态修改**：使用 `Set NiagaraFloatVariable` 等节点在运行时修改粒子参数

附加到角色骨骼上的粒子效果：
1. 使用 `SpawnSystemAttached` 节点
2. `Attach To Component` 连接到 SkeletalMeshComponent
3. `Attach Point Name` 设置骨骼名称
4. `Location Type` 选择 `SnapToTarget` 或 `KeepRelative`

## C++ 用法

NiagaraShader 模块主要面向**引擎内部和高级用户**，提供 GPU 着色器编译和管理基础设施。

### 头文件引入

```cpp
#include "NiagaraShader.h"
#include "NiagaraShared.h"
#include "NiagaraShaderType.h"
#include "NiagaraShaderCompilationManager.h"
```

### 基本用法

**着色器编译管理器的使用**（来自 `NiagaraShaderCompilationManager.h`）：

```cpp
#include "NiagaraShaderCompilationManager.h"

// 注册着色器编译任务到管理器
TArray<FShaderCommonCompileJobPtr> NewJobs;
// ... 创建编译任务 ...
GNiagaraShaderCompilationManager.AddJobs(NewJobs);

// 在编辑器 Tick 中异步处理编译结果
GNiagaraShaderCompilationManager.ProcessAsyncResults();

// 完成特定 ShaderMap 的编译
TArray<int32> ShaderMapIds;
ShaderMapIds.Add(MyShaderMapId);
GNiagaraShaderCompilationManager.FinishCompilation(ShaderMapIds);
```

### 进阶用法

**使用 NiagaraShaderModule 接口注册着色器编译队列处理回调**（来自 `NiagaraShaderModule.h`）：

```cpp
#include "NiagaraShaderModule.h"

// 获取 Niagara Shader 模块单例
INiagaraShaderModule* ShaderModule = INiagaraShaderModule::Get();
if (ShaderModule)
{
    // 注册着色器编译队列处理回调
    auto Handle = ShaderModule->SetOnProcessShaderCompilationQueue(
        INiagaraShaderModule::FOnProcessQueue::CreateLambda([]()
        {
            // 自定义编译队列处理逻辑
        })
    );

    // 注册数据接口默认实例请求回调
    auto DIHandle = ShaderModule->SetOnRequestDefaultDataInterfaceHandler(
        INiagaraShaderModule::FOnRequestDefaultDataInterface::CreateLambda(
            [](const FString& DIClassName) -> UNiagaraDataInterfaceBase*
            {
                // 根据类名返回对应的 Data Interface CDO
                UClass* DIClass = FindObject<UClass>(nullptr, *DIClassName);
                return DIClass ? Cast<UNiagaraDataInterfaceBase>(DIClass->GetDefaultObject()) : nullptr;
            })
    );
    
    // ... 使用完毕后重置 ...
    ShaderModule->ResetOnProcessShaderCompilationQueue(Handle);
    ShaderModule->ResetOnRequestDefaultDataInterfaceHandler();
}
```

**使用 GPU 异步碰撞查询**（来自 `NiagaraAsyncGpuTraceProvider.h`）：

```cpp
#include "NiagaraAsyncGpuTraceProvider.h"

// 检查支持的 Trace Provider 类型
using EProviderType = ENDICollisionQuery_AsyncGpuTraceProvider::Type;
FNiagaraAsyncGpuTraceProvider::FProviderPriorityArray Priorities;
Priorities.Add(EProviderType::HardwareRayTracing);
Priorities.Add(EProviderType::GlobalDistanceField);

EProviderType ResolvedType = FNiagaraAsyncGpuTraceProvider::ResolveSupportedType(
    EProviderType::HardwareRayTracing, Priorities
);

// 创建支持的 Provider 实例
TArray<TUniquePtr<FNiagaraAsyncGpuTraceProvider>> Providers = 
    FNiagaraAsyncGpuTraceProvider::CreateSupportedProviders(
        ShaderPlatform, Dispatcher, Priorities
    );
```

## Demo 示例

以下示例展示如何创建一个自定义的 Niagara 计算着色器，继承自 NiagaraShader 基础设施：

### MyCustomNiagaraShader.h

```cpp
#pragma once

#include "GlobalShader.h"
#include "ShaderParameterStruct.h"

// 自定义的 Niagara 后处理 Compute Shader
class FMyCustomNiagaraProcessCS : public FGlobalShader
{
    DECLARE_EXPORTED_GLOBAL_SHADER(FMyCustomNiagaraProcessCS, NIAGARASHADER_API);
    SHADER_USE_PARAMETER_STRUCT(FMyCustomNiagaraProcessCS, FGlobalShader);

    static constexpr uint32 ThreadGroupSize = 64;

    BEGIN_SHADER_PARAMETER_STRUCT(FParameters, NIAGARASHADER_API)
        SHADER_PARAMETER(uint32, NumParticles)
        SHADER_PARAMETER(float, DeltaTime)
        SHADER_PARAMETER(FVector3f, Gravity)
        SHADER_PARAMETER_SRV(Buffer<float>, InputPositionBuffer)
        SHADER_PARAMETER_SRV(Buffer<float>, InputVelocityBuffer)
        SHADER_PARAMETER_UAV(RWBuffer<float>, OutputPositionBuffer)
        SHADER_PARAMETER_UAV(RWBuffer<float>, OutputVelocityBuffer)
    END_SHADER_PARAMETER_STRUCT()

    static bool ShouldCompilePermutation(const FGlobalShaderPermutationParameters& Parameters)
    {
        return IsFeatureLevelSupported(Parameters.Platform, ERHIFeatureLevel::SM5);
    }

    static void ModifyCompilationEnvironment(
        const FGlobalShaderPermutationParameters& Parameters,
        FShaderCompilerEnvironment& OutEnvironment)
    {
        FGlobalShader::ModifyCompilationEnvironment(Parameters, OutEnvironment);
        OutEnvironment.SetDefine(TEXT("THREADGROUP_SIZE"), ThreadGroupSize);
    }
};
```

### MyCustomNiagaraShader.cpp

```cpp
#include "MyCustomNiagaraShader.h"

IMPLEMENT_GLOBAL_SHADER(FMyCustomNiagaraProcessCS, 
    "/Engine/Plugins/FX/Niagara/Shaders/MyCustomProcess.usf", 
    "MainCS", SF_Compute);

// 辅助函数：在 RDG 中调度自定义 Compute Pass
void AddMyCustomNiagaraProcessPass(
    FRDGBuilder& GraphBuilder,
    FRDGBufferSRVRef InPositionSRV,
    FRDGBufferSRVRef InVelocitySRV,
    FRDGBufferUAVRef OutPositionUAV,
    FRDGBufferUAVRef OutVelocityUAV,
    uint32 NumParticles,
    float DeltaTime,
    FVector3f Gravity)
{
    TShaderMapRef<FMyCustomNiagaraProcessCS> ComputeShader(
        GetGlobalShaderMap(GMaxRHIFeatureLevel));

    FMyCustomNiagaraProcessCS::FParameters* PassParameters = 
        GraphBuilder.AllocParameters<FMyCustomNiagaraProcessCS::FParameters>();

    PassParameters->NumParticles = NumParticles;
    PassParameters->DeltaTime = DeltaTime;
    PassParameters->Gravity = Gravity;
    PassParameters->InputPositionBuffer = InPositionSRV;
    PassParameters->InputVelocityBuffer = InVelocitySRV;
    PassParameters->OutputPositionBuffer = OutPositionUAV;
    PassParameters->OutputVelocityBuffer = OutVelocityUAV;

    const uint32 NumGroups = FMath::DivideAndRoundUp(NumParticles, 
        FMyCustomNiagaraProcessCS::ThreadGroupSize);

    GraphBuilder.AddPass(
        RDG_EVENT_NAME("MyCustomNiagaraProcess"),
        PassParameters,
        ERDGPassFlags::Compute,
        [ComputeShader, PassParameters, NumGroups](FRHIComputeCommandList& RHICmdList)
        {
            FComputeShaderUtils::Dispatch(RHICmdList, ComputeShader, *PassParameters,
                FIntVector(NumGroups, 1, 1));
        });
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RHI` | 渲染硬件接口，用于着色器编译和 GPU 资源管理 |
| `RenderCore` | 渲染核心基础设施，ShaderMap、Uniform Buffer 等 |
| `Renderer` | 渲染器模块，用于光追实例和场景交互 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `da97a493` | Data Hierarchy: guard SyncViewModelsToData against re-entry from OnHierarchyChanged listeners | 修复数据层级视图模型同步时的重入保护 |
| 2026-05-22 | `85c6d110` | Avoid creating an empty RHI buffer for SKM sampling data | 避免为骨骼网格体采样数据创建空 RHI 缓冲区 |
| 2026-05-20 | `119ee9ac` | [HWRT] Fix FNiagaraRendererMeshes::GetDynamicRayTracingInstances(...) corrupting GPUScene when rende... | 修复网格渲染器在获取动态光追实例时破坏 GPUScene 的问题 |
| 2026-05-19 | `5e68c5a9` | [HWRT] Fix crash due to FNiagaraRendererRibbons requesting multiple updates on the same RayTracingGe... | 修复 Ribbon 渲染器在同一光迄件上重复请求更新导致的崩溃 |
| 2026-05-14 | `4bb8e4f1` | Fix UNiagaraBakerSettings crash when AI toolset or Python writes a null entry into the Outputs array | 修复 AI 工具或 Python 写入空条目到烘焙设置输出数组时的崩溃 |

### 维护评价

Niagara 是 Unreal Engine 的**旗舰级特效系统**，自 2017 年创建以来一直是 Epic Games 重点维护的模块。

- **维护活跃度**：🟢 **非常活跃**。最近的提交记录（2026 年 5 月）显示几乎每天都有更新，涵盖光追修复、性能优化、崩溃修复等
- **代码规模**：1622 个源文件，8 个模块，是引擎中最大的插件之一
- **发展趋势**：持续增加新功能（Stateless GPU 仿真、SVT 支持、邻居查询优化等），并向 Vulkan/现代 API 兼容性持续改进
- **已知限制**：GPU 仿真路径有平台限制（不支持所有平台），部分高级功能需要 SM5+ 硬件
- **推荐程度**：🟢 **强烈推荐**。作为 UE5 的标准特效系统，Niagara 是创建粒子效果的首选方案，替代了过时的 Cascade 系统

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara/Tests)（如有）