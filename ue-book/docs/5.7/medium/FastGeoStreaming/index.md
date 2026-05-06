# FastGeo Streaming

> A system that extracts and converts a partitioned world's geometry to optimize world streaming performance.

| 属性 | 值 |
|---|---|
| 中文名 | 快速几何流送 |
| 分类 | World Building |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器配置） |
| 模块 | `FastGeoStreaming` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/FastGeoStreaming) | |

## 用途

FastGeo Streaming 是一个实验性插件，用于**在大型开放世界（World Partition）中优化几何体的流送性能**。它通过将分区世界的几何体提取并转换为专用的轻量级数据表示（`UFastGeoContainer`），在运行时以异步方式创建/销毁渲染状态和物理状态，从而减少主线程卡顿，提升世界加载和卸载期间的帧率稳定性。

核心思路是：在编辑器中将原始 Actor/Component 的数据（网格、实例、材质、碰撞等）预先烘焙到自定义的“FastGeo”容器中，运行时由专用子系统（`UFastGeoWorldSubsystem`）托管这些容器，并利用多线程和异步流水线处理渲染与物理状态的创建/销毁。

## 使用场景

- 使用 **World Partition** 的大世界项目，需要在玩家移动时快速加载/卸载大块几何体，但希望避免主线程因大量组件注册/销毁而造成的性能尖峰。
- 需要支持高密度实例化几何体（如集群树木、岩石）的流送，利用 `FFastGeoInstancedStaticMeshComponent` 等专用组件降低开销。
- 希望将 HLOD 替换为更高效的自定义 HLOD（`FFastGeoHLOD`）以提升远处物体的加载速度。
- 需要对同一几何体复用运行时数据（如多个关卡加载同一容器），减少重复创建成本。

## 蓝图用法

该插件**未暴露任何蓝图可调用节点**。所有主要功能由 C++ 接口和编辑器流程驱动。蓝图无法直接操作 FastGeo 容器或转换子系统。

## C++ 用法

### 头文件引入

```cpp
#include "FastGeoWorldSubsystem.h"
#include "FastGeoContainer.h"
```

### 基本用法

获取世界子系统并触发异步渲染状态创建：

```cpp
void UMyFunctionLibrary::RequestFastGeoStreaming(UWorld* World, UFastGeoContainer* Container)
{
    if (World)
    {
        UFastGeoWorldSubsystem* Subsystem = UWorld::GetSubsystem<UFastGeoWorldSubsystem>(World);
        if (Subsystem && Container)
        {
            // 异步创建渲染状态（不会阻塞主线程）
            Subsystem->PushAsyncCreateRenderStateJob(Container);
        }
    }
}
```

如需等待所有异步任务完成（如关底卸载时）：

```cpp
Subsystem->ProcessAsyncRenderStateJobs(/*bWaitForCompletion = */true);
```

### 进阶用法

1. **自定义转换规则**：继承 `UFastGeoWorldPartitionRuntimeCellTransformer` 并重写 `IsActorTransformable` / `IsComponentTransformable` 来控制哪些 Actor/Component 可以被转换为 FastGeo 容器。

2. **组件类型支持**：插件内置了多种轻量级组件类，均继承自 `FFastGeoPrimitiveComponent`：
   - `FFastGeoStaticMeshComponent` – 静态网格体
   - `FFastGeoInstancedStaticMeshComponent` – 实例化静态网格体
   - `FFastGeoSkinnedMeshComponent` – 蒙皮网格体
   - `FFastGeoInstancedSkinnedMeshComponent` – 实例化蒙皮网格体
   - `FFastGeoProceduralISMComponent` – 程序化实例化网格体
   - `FFastGeoHLOD` – HLOD 容器（实现了 `IWorldPartitionHLODObject`）

3. **弱引用管理**：使用 `FWeakFastGeoComponent` 或 `FWeakFastGeoComponentCluster` 安全地引用容器内的元素，即使容器被销毁也能优雅失效。

## Demo 示例

以下是一个最小 C++ 示例，展示如何在世界初始化后为加载的 FastGeo 容器异步创建渲染状态。

**FastGeoStreamingDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "FastGeoStreamingDemo.generated.h"

class UFastGeoContainer;

UCLASS(Blueprintable, meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UFastGeoStreamingDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    // 在 BeginPlay 中为指定的容器触发异步流送
    UFUNCTION(BlueprintCallable, Category = "FastGeo Streaming")
    void StreamContainerAsync(UFastGeoContainer* Container);
};
```

**FastGeoStreamingDemo.cpp**
```cpp
#include "FastGeoStreamingDemo.h"
#include "FastGeoWorldSubsystem.h"
#include "FastGeoContainer.h"

void UFastGeoStreamingDemoComponent::StreamContainerAsync(UFastGeoContainer* Container)
{
    UWorld* World = GetWorld();
    if (!World)
        return;

    UFastGeoWorldSubsystem* Subsystem = UWorld::GetSubsystem<UFastGeoWorldSubsystem>(World);
    if (Subsystem && Container)
    {
        Subsystem->PushAsyncCreateRenderStateJob(Container);
        UE_LOG(LogTemp, Log, TEXT("FastGeo Streaming: Async render state job pushed for container '%s'."), *Container->GetName());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器工具支持（用于 World Partition 转换、属性编辑、代理组件等） |

> 注意：`FastGeoStreaming` 模块虽然标记为 Runtime，但依赖 `UnrealEd`，因此不能在 Shipping 包中直接使用（编辑器功能被剥离）。如果需要在运行时纯使用，请评估依赖并自行剥离编辑器相关代码。

## 维护状态

### 近期更新

- 2025-10-15 `c5b4ab7f` — [PCG] Fix monochrome instances when using PerInstanceRandom MG node
- 2025-09-12 `d9bdf175` — [FastGeo] Allow runtime use cases to opt out of automatic object reference collection to avoid cost
- 2025-09-11 `46819911` — [FastGeo] Fix crash on mac caused by TArray relocation of FFastGeoPrimitiveComponent which contains
- 2025-09-11 `efd417b7` — [FastGeo] Fixed FFastGeoPrimitiveComponent BodyInstance not properly copied (regression caused by CL)
- 2025-09-04 `6bb8c39d` — [HLOD] Custom HLOD support

### 维护评价

- **创建时间**：2025年9月，距今不足2个月。
- **更新频率**：两周内多次功能性修复和优化，非常活跃。
- **稳定性**：实验性阶段，API 和架构可能大幅变动；存在已知 bug（如 Mac 崩溃、BodyInstance 拷贝问题）已快速修复。
- **推荐使用**：适合愿意跟进最新代码、积极参与反馈的团队。不建议用于已发版的生产项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/FastGeoStreaming)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/fastgeo-streaming-plugin/)（暂缺，实验性插件通常无独立文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/FastGeoStreaming/Tests)（可能位于`Engine/Tests`目录，但当前未提供）