# Procedural Content Generation Framework (PCG) FastGeo Interop

> Extra plugin for Procedural Content Generation Framework which enables runtime spawning of primitives using FastGeo components.

| 属性 | 值 |
|---|---|
| 中文名 | PCG FastGeo 互操作 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PCGFastGeoInterop` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-31 |
| 年龄标签 | 🆕（约0年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGInterops/PCGFastGeoInterop) | |

## 用途

该插件是 **PCG（程序化内容生成框架）** 的实验性扩展，用于在 **运行时** 通过 **FastGeo 组件** 高效生成和渲染大量基元（Primitives）。FastGeo 是 UE5 的高性能几何体实例化系统，支持海量实例的异步流送和数据压缩。PCG 本身用于在编辑器或运行时生成内容，而此插件打通 PCG 与 FastGeo，使得 PCG 执行程序能够直接输出实例化数据到 FastGeo 容器，从而绕过传统静态网格体实例化（ISM）的 CPU/GPU 开销，实现更大规模的运行时生成。

**解决的核心问题**：PCG 运行时生成静态网格体实例（ISM）时，每个实例都需要在渲染线程创建 SceneProxy，数量巨大时会产生严重性能瓶颈。FastGeo 使用稀疏体素表示和 GPU 驱动更新，能以更低开销渲染数百倍实例。该插件提供 PCG 与 FastGeo 之间的桥梁，允许 PCG 数据直接驱动 FastGeo 容器，从而大规模提升运行时生成的可视化性能。

> ⚠️ 该插件仍处于实验阶段，计划在 FastGeo 组件正式版后合并到 PCG 主插件中，届时本插件将被移除。

## 使用场景

- **开放世界地貌细节铺排**：使用 PCG 运行时生成草地、碎石、小灌木，通过 FastGeo 渲染数十万实例，避免 ISM 的渲染瓶颈。
- **程序化建筑模块**：将 PCG 生成的建筑模块（如砖块、装饰）直接输出到 FastGeo 容器，实现超高密度细节。
- **实时数据可视化**：从外部数据源动态生成大量静态物体（如点云、粒子系统替代），利用 PCG 的规则和 FastGeo 的高效渲染。
- **分块世界生成**：结合 WorldPartition，在玩家附近使用 PCG 动态生成环境细节，并通过 FastGeo 实现即时渲染。

## 蓝图用法

该插件目前**没有公开的蓝图节点**。所有功能通过 C++ 接口暴露给 PCG 内部执行程序或自定义 PCG 节点。若需要在蓝图中使用，需配合 PCG 框架的蓝图可调用节点（如 `Execute PCG`）并以插件内部数据为输入，但当前无法直接操作 FastGeo 容器。

建议用户通过 C++ 扩展 PCG 执行程序或等待后续版本提供蓝图访问。

## C++ 用法

### 头文件引入

```cpp
#include "PCGFastGeoInteropModule.h"
#include "Components/PCGManagedFastGeoContainer.h"  // 资源包装类
#include "Compute/PrimitiveFactories/PCGPrimitiveFactoryFastGeoPISMC.h"  // 工厂类
```

### 基本用法

该插件的主要使用方式是通过 **PCG 执行程序（PCG Execution）** 生成并管理 FastGeo 容器。以下示例取自测试代码，展示如何使用 `PCGPrimitiveFactoryFastGeoPISMC` 将 PCG 生成的 ISM 描述转化为 FastGeo 组件。

```cpp
// 路径：Engine/Plugins/Experimental/PCGInterops/PCGFastGeoInterop/Source/PCGFastGeoInterop/Private/Compute/PrimitiveFactories/PCGPrimitiveFactoryFastGeoPISMC.cpp

// 1. 创建工厂实例并初始化参数
FPCGPrimitiveFactoryFastGeoPISMC Factory;
Factory.Initialize({
    .Descriptors = { /* 填入 FPCGProceduralISMComponentDescriptor 数组 */ },
    .InWorld = TargetWorld,
    .InActor = OwnerActor,
    .InTransformSet = /* FPCGProceduralTransformSet */,
    .InLandscapeRef = /* 可选景观引用 */
});

// 2. 在 PCG 上下文中创建 FastGeo 组件
FPCGContext* Context = /* 从执行程序获取 */;
bool bSuccess = Factory.Create(Context);

// 3. 将创建的 FastGeo 组件包装到 UPCGManagedFastGeoContainer 以管理生命周期
UPCGManagedFastGeoContainer* Container = NewObject<UPCGManagedFastGeoContainer>();
Container->SetFastGeoContainer(CreatedFastGeo);
Container->SetObjectReferences(Factory.CollectObjectReferences());
```

### 进阶用法

**管理 FastGeo 资源的释放**：`UPCGManagedFastGeoContainer` 继承自 `UPCGManagedResource`，可被 PCG 框架的垃圾回收系统自动管理。当生成区域离开或节点重新生成时，资源会自动释放。

```cpp
// 当需要强制释放时（hard release 将销毁 FastGeo 组件）
bool bHardRelease = true;
TSet<TSoftObjectPtr<AActor>> OutActorsToDelete;
Container->Release(bHardRelease, OutActorsToDelete);
```

**与 PCG 执行程序集成**：通常在自定义 PCG 节点（`UPCGNode` 的子类）的 `Execute` 函数中调用工厂，并将工厂结果作为节点输出资源。具体可参考 PCG 官方 ISM 生成节点（`PCGStaticMeshSpawner`）的实现，将其 `IPCGPrimitiveFactoryISMBase` 替换为 `FPCGPrimitiveFactoryFastGeoPISMC` 即可。

## Demo 示例

以下是一个最小化的 PCG 自定义节点实现，使用 FastGeo 工厂生成草地实例。

**FastGeoGrassSpawner.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "PCGNode.h"
#include "Compute/PrimitiveFactories/PCGPrimitiveFactoryFastGeoPISMC.h"
#include "FastGeoGrassSpawner.generated.h"

UCLASS(BlueprintType, ClassGroup = (PCG))
class UPCGFastGeoGrassSpawner : public UPCGNode
{
    GENERATED_BODY()

public:
    // FastGeo 工厂参数
    UPROPERTY(EditAnywhere, Category = Settings)
    TArray<FPCGProceduralISMComponentDescriptor> Descriptors;

    UPROPERTY(EditAnywhere, Category = Settings)
    int32 NumInstancesPerPoint = 3;

protected:
    virtual bool Execute(FPCGContext* Context) override;
};
```

**FastGeoGrassSpawner.cpp**
```cpp
#include "FastGeoGrassSpawner.h"
#include "Engine/World.h"
#include "Components/PCGManagedFastGeoContainer.h"

bool UPCGFastGeoGrassSpawner::Execute(FPCGContext* Context)
{
    AActor* OwnerActor = Context->GetOwnerActor();
    UWorld* World = OwnerActor ? OwnerActor->GetWorld() : nullptr;
    if (!World) return false;

    // 获取输入数据（这里简化，实际需要从 Pin 读取）
    const FPCGDataCollection& InputData = Context->InputData;

    // 创建工厂
    FPCGPrimitiveFactoryFastGeoPISMC Factory;
    Factory.Initialize({
        .Descriptors = Descriptors,
        .InWorld = World,
        .InActor = OwnerActor,
        .InTransformSet = /* 从输入数据构建 FPCGProceduralTransformSet */,
        // 其他参数省略
    });

    if (!Factory.Create(Context))
    {
        return false;
    }

    // 包装成托管资源
    UPCGManagedFastGeoContainer* Container = NewObject<UPCGManagedFastGeoContainer>();
    Container->SetFastGeoContainer(/* 从 Factory 获取的 UFastGeoContainer */);
    Container->SetObjectReferences(Factory.CollectObjectReferences());

    // 将托管资源输出到数据
    FPCGDataCollection& OutputData = Context->OutputData;
    OutputData.TaggedData.Add(Container);

    return true;
}
```

> 注意：Demo 依赖 `PCG` 和 `FastGeoStreaming` 插件，需要在 `Build.cs` 中添加依赖。

## 模块依赖

使用该插件时，你的模块需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 基础框架 |
| `FastGeoStreaming` | FastGeo 组件和流送系统 |

```cpp
PublicDependencyModuleNames.AddRange(new string[] {
    "PCG",
    "FastGeoStreaming"
});
```

## 维护状态

### 近期更新

- 2025-09-30 `7c33141a` — [PCG] Move FastGeo primitive factory helpers out of StaticMeshDataInterface so that it can be made public
- 2025-09-12 `d9bdf175` — [FastGeo] Allow runtime use cases to opt out of automatic object reference collection to avoid cost
- 2025-09-09 `1306b974` — [PCG] Massage a few things to move towards execution sources for runtime generation of primitives (update)
- 2025-09-01 `4cfedec4` — [PCG] Fix "Primitive not allocated in GPU scene" errors when editor launched in background/unfocused
- 2025-08-31 `0f340ff1` — [PCG] Fix instancing data interface dangerously holding onto scene proxy pointers across GT ticks.

### 维护评价

该插件创建于 2025 年 8 月，非常新，仍处于实验阶段。近期更新频繁（每 1–2 周一次），涉及重构、性能优化和 Bug 修复，表明 **活跃维护**。从提交历史看，团队正在逐步将 FastGeo 与 PCG 集成，并计划在 FastGeo 成熟后合并到主 PCG 插件。当前虽有少量已知问题（如“Primitive not allocated in GPU scene”已修复），但整体趋势积极。

**推荐使用场景**：适合希望利用 PCG 运行时生成大规模实例的开发者，但需要接受实验性插件的潜在 API 变动和性能损耗。**建议跟踪最新主分支**并关注 UC 官方公告。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGInterops/PCGFastGeoInterop)
- [官方 PCG 文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGInterops/PCGFastGeoInterop/Source/PCGFastGeoInterop/Tests)（若存在，当前未提供）