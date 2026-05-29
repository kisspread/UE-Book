# Render Trace

> The Render Trace plugin provides a way to have pixel perfect sampling of physical materials on meshes.

| 属性 | 值 |
|---|---|
| 中文名 | 渲染追踪 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RenderTrace` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-07-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/RenderTrace) | |

## 用途

RenderTrace 插件通过利用 GPU 渲染管线，实现了对网格体（Mesh）表面物理材质（Physical Material）的像素级精确采样。它主要用于替代传统的基于物理的射线检测（Async Line Trace），后者在复杂材质表面上只能返回一个笼统的材质类型。RenderTrace 通过渲染一个特殊的材质图（Material Graph）到一个 Render Target，并回读 GPU 数据，从而在指定的点上获取由材质图中定义的、可能混合的多种物理材质及其权重。这种技术适用于需要高精度材质反馈的场景，例如实现精确的脚步声、粒子碰撞效果或游戏逻辑判断，但会引入数帧的延迟以避免阻塞渲染管线。

## 使用场景

- 你需要根据角色踩踏的**精确物理材质**（如木板、金属、泥地）来播放不同的脚步声或生成不同的粒子特效。
- 你在制作一个射击游戏，希望子弹击中墙面或物体时，根据**弹孔位置**的材质类型来决定是否产生火花、烟雾或留下不同的痕迹。
- 你在开发一个赛车游戏，需要精确检测轮胎接触的**路面材质**（沥青、草地、沙石），以计算最真实的抓地力和摩擦力。
- 你的游戏逻辑需要基于场景中某个动态网格体表面**特定区域**的材质类型来触发事件，而普通的射线检测无法提供所需的精度。

## 蓝图用法

此插件的核心功能通过 C++ 类 `FRenderTraceQueue` 暴露，它是一个可勾选（Tickable）的游戏对象，用于异步管理检测任务。蓝图中通常通过自定义蓝图函数库或 Actor 组件来封装和调用这些功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AsyncRenderTraceComponents` | 异步发起一次针对指定组件列表的渲染追踪检测。返回任务 ID。 | `FRenderTraceQueue` |
| `CancelAsyncSample` | 根据任务 ID 取消一个尚未完成的检测请求。 | `FRenderTraceQueue` |

### 使用示例（蓝图描述）

由于核心类是纯 C++ 类，无法直接在蓝图中拖拽使用。典型的封装方式如下：
1.  创建一个 `UBlueprintFunctionLibrary` 或 `UActorComponent` 子类。
2.  在其中创建一个类型为 `FRenderTraceQueue` 的成员变量（通常用 `TUniquePtr` 或作为子对象管理生命周期）。
3.  暴露一个蓝图可调用函数，例如 `RequestPhysicalMaterialAtLocation`，其内部实现为：准备组件列表、射线起始点和方向，然后调用 `AsyncRenderTraceComponents`，并绑定一个自定义的委托（Delegate）用于在检测完成后处理结果（`FRenderTraceDelegate`）。
4.  在蓝图中，调用你封装的函数，并在委托绑定的函数中根据返回的 `UPhysicalMaterial*` 执行后续逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "RenderTrace.h"
```

### 基本用法

以下示例展示了如何创建一个 `FRenderTraceQueue` 实例并发起一次异步检测。
（示例基于 `FRenderTraceQueue` 的公开接口和 `FRenderTraceDelegate` 定义推断）

```cpp
// 假设在一个 Actor 或管理器类中
#include "RenderTrace.h"

class AMyActor : public AActor
{
    // ... 其他代码 ...
private:
    // 渲染追踪队列实例，用于管理异步任务
    FUniquePtr<FRenderTraceQueue> RenderTraceQueue;

    // 异步检测完成后的回调
    void OnRenderTraceComplete(uint32 TaskID, const UPhysicalMaterial* PhysMat, int64 UserData);
};

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    // 初始化队列
    RenderTraceQueue = MakeUnique<FRenderTraceQueue>();
}

void AMyActor::SampleMaterialAtPoint(UPrimitiveComponent* TargetComponent, FVector RayOrigin, FVector RayDirection)
{
    if (!RenderTraceQueue || !TargetComponent) return;

    // 将单个组件放入数组
    TArray<const UPrimitiveComponent*> Components;
    Components.Add(TargetComponent);

    // 创建完成委托
    FRenderTraceDelegate CompletionDelegate;
    CompletionDelegate.BindUObject(this, &AMyActor::OnRenderTraceComplete);

    // 发起异步检测
    uint32 TaskID = RenderTraceQueue->AsyncRenderTraceComponents(
        Components,
        RayOrigin,
        RayDirection,
        CompletionDelegate,
        0 // UserData，可自定义传递数据
    );

    if (TaskID == 0)
    {
        UE_LOG(LogRenderTrace, Warning, TEXT("Render Trace request failed (no valid primitives?)."));
    }
}

void AMyActor::OnRenderTraceComplete(uint32 TaskID, const UPhysicalMaterial* PhysMat, int64 UserData)
{
    if (PhysMat)
    {
        UE_LOG(LogTemp, Log, TEXT("Detected Physical Material: %s"), *PhysMat->GetName());
        // 在此处基于 PhysMat 执行游戏逻辑，例如播放对应音效
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Render Trace completed but found no physical material."));
    }
}
```

### 进阶用法

1.  **批量与取消**：`AsyncRenderTraceComponents` 可以接受多个组件（`TArrayView`）进行批量检测，返回一个唯一的 `TaskID`。在检测完成前，你可以使用 `CancelAsyncSample(TaskID)` 取消该请求。
2.  **自定义用户数据**：`AsyncRenderTraceComponents` 的最后一个参数 `int64 UserData` 允许你传递一个自定义整数值，该值会在完成委托中回传，方便你关联上下文信息。
3.  **材质图设置**：要使此检测生效，被检测的 `UPrimitiveComponent` 所使用的材质**必须**包含一个 `UMaterialExpressionPhysicalMaterialOutput` 节点，并在该节点中配置一个 `FPhysicalMaterialTraceInput` 数组，将材质图的输出与具体的 `UPhysicalMaterial` 资产关联起来。

## Demo 示例

一个最小的可编译示例，展示如何集成 `FRenderTraceQueue`。

**RenderTraceDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RenderTrace.h"
#include "RenderTraceDemo.generated.h"

UCLASS()
class ARenderTraceDemo : public AActor
{
    GENERATED_BODY()

public:
    ARenderTraceDemo();

    UFUNCTION(BlueprintCallable, Category = "RenderTrace Demo")
    void PerformRenderTraceSample(UPrimitiveComponent* Component);

private:
    void HandleTraceResult(uint32 TaskID, const UPhysicalMaterial* PhysMat, int64 UserData);

    TUniquePtr<FRenderTraceQueue> TraceQueue;
};
```

**RenderTraceDemo.cpp**
```cpp
#include "RenderTraceDemo.h"
#include "Components/PrimitiveComponent.h"

ARenderTraceDemo::ARenderTraceDemo()
{
    PrimaryActorTick.bCanEverTick = false;
    TraceQueue = MakeUnique<FRenderTraceQueue>();
}

void ARenderTraceDemo::PerformRenderTraceSample(UPrimitiveComponent* Component)
{
    if (!TraceQueue || !Component) return;

    TArray<const UPrimitiveComponent*> Components = {Component};
    FVector Origin = GetActorLocation();
    FVector Direction = GetActorForwardVector();

    FRenderTraceDelegate Delegate;
    Delegate.BindUObject(this, &ARenderTraceDemo::HandleTraceResult);

    uint32 ID = TraceQueue->AsyncRenderTraceComponents(Components, Origin, Direction, Delegate);
    if (ID != 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Render Trace task %u queued."), ID);
    }
}

void ARenderTraceDemo::HandleTraceResult(uint32 TaskID, const UPhysicalMaterial* PhysMat, int64 UserData)
{
    if (PhysMat)
    {
        UE_LOG(LogTemp, Log, TEXT("Task %u found material: %s"), TaskID, *PhysMat->GetName());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Task %u found no material."), TaskID);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Renderer` | 插件的核心，用于执行基于渲染器的物理材质采样。 |
| `RenderCore` | 提供渲染核心类型和工具，如 `FRDGBuilder`。 |
| `PhysicsCore` | 提供物理材质 (`UPhysicalMaterial`) 的基础定义。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从旧版 UE_LOG 迁移至新版 UE_LOGF。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 拆分渲染相关头文件，优化编译依赖。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃旧的 GPU 性能分析相关宏。 |
| 2025-04-23 | `939cc6e5` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv | 为 API 方法添加 `dllexport` 符号导出属性。 |
| 2025-03-20 | `80c69d99` | Updated bit-width of material value types to 64-bits | 更新材质值类型的位宽至 64 位。 |

### 维护评价

RenderTrace 插件自 2022 年创建后，**维护不活跃**。最后一次包含实质性功能的更新是在创建之初（2022-07-01）。此后的所有提交均为引擎范围的维护性更新，如 API 符号导出、宏迁移、头文件重构和编译器警告修复，没有新的功能添加或 Bug 修复记录。该插件被标记为 **实验性** (`IsBetaVersion: true`) 且 **默认禁用** (`EnabledByDefault: false`)，进一步表明其尚未达到稳定状态。鉴于其接近 4 年没有功能性更新，且处于实验阶段，**不推荐**在生产项目中依赖此插件。它更适合作为一种技术验证或在特定且风险可控的场景下谨慎使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/RenderTrace)
- 官方文档：无
- 测试用例：无（在提供的信息中未发现该插件专属的测试文件）