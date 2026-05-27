# Fast Geo Streaming

> A system that extracts and converts a partitioned world's geometry to optimize world streaming performance.

| 属性 | 值 |
|---|---|
| 中文名 | 快速几何流送 |
| 分类 | World Building |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、设置资产） |
| 模块 | `FastGeoStreaming` (Runtime), `FastGeoStreamingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming) | |

## 用途

FastGeoStreaming 解决的核心问题是 **大世界中静态几何体的流送性能瓶颈**。

传统 World Partition 流送时，每个 RuntimeCell 加载后需要为所有 StaticMeshActor 创建 UObject、注册组件、初始化渲染状态和物理状态——这些操作全部在 GameThread 上串行执行，当一个 Cell 包含成百上千个静态网格体时，会严重阻塞游戏线程，造成可感知的卡顿。

FastGeoStreaming 的方案是：

1. **烘焙时转换**：在 Cook/Cell 转换阶段，将世界分区 Cell 中的不可变静态几何体（StaticMesh、InstancedStaticMesh、SkinnedMesh、Decal、Light 等）提取出来，转换为**非 UObject 的轻量级数据结构**（`FFastGeoComponent` / `FFastGeoComponentCluster`），序列化到 FastGeoContainer 中。
2. **异步流送**：运行时加载 Cell 时，渲染状态（SceneProxy 创建/销毁）和物理状态（BodyInstance 创建/销毁）都在 **Worker 线程**上异步完成，仅在必要时同步回 GameThread，大幅减少游戏线程阻塞时间。
3. **PSO 预缓存集成**：与 PSO Precaching 系统深度集成，支持延迟创建代理（DelayUntilPSOPrecached）和回退材质（UseFallbackMaterialUntilPSOPrecached）两种策略。
4. **代理物理**：通过 Surrogate Actor/Component 机制，将物理碰撞实例挂载到少量代理 Actor 上，使 HitResult/OverlapResult 能正确返回 FastGeo 几何体信息。

简而言之：**把静态几何体从"AActor + UActorComponent"体系中抽离出来，用专门的轻量结构替代，实现离线构建 + 异步注册，从而大幅加速大世界的流送性能。**

## 使用场景

- 你在做一个**大世界开放世界游戏**，World Partition Cell 包含大量静态网格体，流送时出现明显卡顿 → 用 FastGeoStreaming 优化
- 你的关卡中有**成百上千的 ISM 实例**（如植被、碎石、建筑装饰），加载开销很大 → 用 FastGeoStreaming 将其转为轻量结构
- 你需要与 **HLOD 系统**配合，同时保持数据层（Data Layers）兼容 → FastGeoStreaming 已内置支持
- 你的项目启用了 **PSO Precaching**，希望静态几何体也能受益 → FastGeoStreaming 内置 PSO 集成
- 你需要对**烘焙后的静态几何体**进行高性能物理查询（射线检测、重叠检测）→ 通过 Surrogate 代理机制实现

> ⚠️ **前提条件**：需要启用 `p.Chaos.EnableAsyncInitBody` 控制台变量。

## 蓝图用法

FastGeoStreaming 主要是一个**编译期/运行时系统插件**，不提供常规蓝图节点。它的核心工作在 World Partition Cell 转换和异步流送管线中自动完成。

### 编辑器配置

转换器设置通过 `UFastGeoTransformerSettings` 数据资产配置：

| 属性 | 说明 |
|---|---|
| `AllowedActorClasses` | 允许转换的 Actor 类（递归匹配子类） |
| `AllowedExactActorClasses` | 允许转换的 Actor 类（精确匹配） |
| `DisallowedActorClasses` | 禁止转换的 Actor 类（递归） |
| `AllowedComponentClasses` | 允许转换的组件类（递归） |
| `DisallowedComponentClasses` | 禁止转换的组件类（递递归） |
| `bGenerateSurrogateComponents` | 是否生成代理组件用于碰撞查询 |
| `InstanceStorageMode` | 实例变换存储模式（Auto/Compressed/Full） |

### 运行时碰撞查询

通过 `FFastGeoPhysicsBodyInstanceOwner` 静态方法从 HitResult/OverlapResult 中提取 FastGeo 信息：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FromHitResult` | 从射线检测结果中获取 FastGeo 物理体实例所有者 | `FFastGeoPhysicsBodyInstanceOwner` |
| `FromOverlapResult` | 从重叠检测结果中获取 FastGeo 物理体实例所有者 | `FFastGeoPhysicsBodyInstanceOwner` |

### 控制台变量

| CVar | 说明 |
|---|---|
| `FastGeo.Enabled` | 启用/禁用 FastGeo 系统 |
| `FastGeo.AllowAsyncRenderWork` | 允许异步渲染工作（仅非编辑器） |

## C++ 用法

### 头文件引入

```cpp
#include "FastGeoStreamingModule.h"
#include "FastGeoWorldSubsystem.h"
#include "FastGeoContainer.h"
#include "FastGeoComponent.h"
#include "FastGeoPrimitiveComponent.h"
#include "FastGeoStaticMeshComponent.h"
#include "FastGeoInstancedStaticMeshComponent.h"
```

### 基本用法 — 运行时创建 FastGeo Container

从 `UFastGeoContainer::CreateRuntime` 的 API 文档提取：

```cpp
// 创建一个运行时 FastGeo 容器，用于程序化生成的静态几何体
FFastGeoCreateRuntimeResult Result = UFastGeoContainer::CreateRuntime(
    GetWorld(),
    FName("MyProceduralGeo"),
    [](FFastGeoComponentCluster& Cluster)
    {
        // 向组件簇中添加组件
        auto& StaticMeshComp = Cluster.AddComponent(FFastGeoStaticMeshComponent::Type);
        auto& ISMComp = Cluster.AddComponent(FFastGeoInstancedStaticMeshComponent::Type);
        // ... 配置组件数据
    },
    true // bInCollectReferences — 自动收集资产引用
);

if (Result.Container)
{
    // 等待注册完成
    if (Result.Container->IsFullyRegistered())
    {
        // 已就绪，可以正常使用
    }
    else
    {
        // 订阅注册完成回调
        Result.Container->GetOnRegistered().AddLambda([]()
        {
            UE_LOG(LogFastGeoStreaming, Log, TEXT("FastGeo container registered successfully."));
        });
    }
}
```

> 来源：`Source/FastGeoStreaming/Internal/FastGeoContainer.h`

### 基本用法 — 销毁运行时容器

```cpp
// 销毁运行时创建的 FastGeo 容器（异步注销，子系统驱动完成）
UFastGeoContainer::DestroyRuntime(MyContainer);

// 如需等待销毁完成
MyContainer->GetOnUnregistered().AddLambda([]()
{
    UE_LOG(LogFastGeoStreaming, Log, TEXT("FastGeo container destroyed."));
});
```

### 基本用法 — 遍历组件

```cpp
// 遍历容器中所有组件簇
FastGeoContainer->ForEachComponentCluster([](FFastGeoComponentCluster& Cluster)
{
    // 遍历每个组件簇中的所有组件
    Cluster.ForEachComponent([](FFastGeoComponent& Component)
    {
        if (auto* StaticMeshComp = Component.CastTo<FFastGeoStaticMeshComponent>())
        {
            // 处理静态网格体组件
        }
        else if (auto* ISMComp = Component.CastTo<FFastGeoInstancedStaticMeshComponent>())
        {
            // 处理实例化静态网格体组件
        }
    });
});

// 可中断遍历（返回 false 提前退出）
FastGeoContainer->ForEachComponentClusterBreakable([](FFastGeoComponentCluster& Cluster) -> bool
{
    return Cluster.ForEachComponentBreakable([](FFastGeoComponent& Component) -> bool
    {
        // 返回 false 停止遍历
        return Component.IsRenderStateCreated();
    });
});
```

### 基本用法 — 碰撞查询结果提取

```cpp
FHitResult HitResult;
if (GetWorld()->GetFirstPlayerController()->GetHitResultUnderCursor(ECC_Visibility, false, HitResult))
{
    // 尝试从 HitResult 中提取 FastGeo 物理体实例信息
    const FFastGeoPhysicsBodyInstanceOwner* FastGeoOwner = 
        FFastGeoPhysicsBodyInstanceOwner::FromHitResult(HitResult);
    
    if (FastGeoOwner)
    {
        // 获取被击中的 FastGeo 组件
        FFastGeoPrimitiveComponent* HitComponent = FastGeoOwner->GetOwnerComponent();
        UFastGeoContainer* HitContainer = FastGeoOwner->GetOwnerContainer();
        
        UE_LOG(LogTemp, Log, TEXT("Hit FastGeo component in container: %s"), 
            *HitContainer->GetName());
    }
}
```

> 来源：`Source/FastGeoStreaming/Internal/FastGeoPhysicsBodyInstanceOwner.h`

### 进阶用法 — 检查异步状态

```cpp
// 获取 WorldSubsystem 引用
UFastGeoWorldSubsystem* Subsystem = GetWorld()->GetSubsystem<UFastGeoWorldSubsystem>();

// 检查是否有待处理的异步渲染状态任务
// UFastGeoContainer 提供详细的状态查询
bool bHasPendingCreate = MyContainer->HasAnyPendingCreateTasks();
bool bHasPendingDestroy = MyContainer->HasAnyPendingDestroyTasks();
bool bIsRegistering = MyContainer->IsRegistering();
bool bIsRegistered = MyContainer->IsRegistered();
bool bIsFullyRegistered = MyContainer->IsFullyRegistered();

// 获取容器中的图元组件列表
TArray<IPrimitiveComponent*> Primitives = MyContainer->GetPrimitiveComponents();
TArray<IStaticMeshComponent*> StaticMeshes = MyContainer->GetStaticMeshComponents();
```

## Demo 示例

一个最小的运行时创建 FastGeo 容器并等待注册完成的示例：

### MyFastGeoTest.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyFastGeoTest.generated.h"

class UFastGeoContainer;

UCLASS()
class AMyFastGeoTest : public AActor
{
    GENERATED_BODY()

public:
    AMyFastGeoTest();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, Category = "FastGeo")
    UStaticMesh* SampleMesh;

private:
    void CreateFastGeoContainer();

    UPROPERTY()
    TObjectPtr<UFastGeoContainer> FastGeoContainer;

    FDelegateHandle OnRegisteredHandle;
};
```

### MyFastGeoTest.cpp

```cpp
#include "MyFastGeoTest.h"

#include "FastGeoContainer.h"
#include "FastGeoComponentCluster.h"
#include "FastGeoStaticMeshComponent.h"
#include "FastGeoInstancedStaticMeshComponent.h"
#include "FastGeoPhysicsBodyInstanceOwner.h"

AMyFastGeoTest::AMyFastGeoTest()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyFastGeoTest::BeginPlay()
{
    Super::BeginPlay();
    CreateFastGeoContainer();
}

void AMyFastGeoTest::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (FastGeoContainer)
    {
        if (OnRegisteredHandle.IsValid())
        {
            FastGeoContainer->GetOnRegistered().Remove(OnRegisteredHandle);
        }
        UFastGeoContainer::DestroyRuntime(FastGeoContainer);
        FastGeoContainer = nullptr;
    }
    Super::EndPlay(EndPlayReason);
}

void AMyFastGeoTest::CreateFastGeoContainer()
{
    if (!SampleMesh || !GetWorld())
    {
        return;
    }

    FFastGeoCreateRuntimeResult Result = UFastGeoContainer::CreateRuntime(
        GetWorld(),
        FName("DemoFastGeo"),
        [this](FFastGeoComponentCluster& Cluster)
        {
            // 添加一个静态网格体组件
            auto& SMComp = Cluster.AddComponent(FFastGeoStaticMeshComponent::Type);
            // 注意：实际使用中需要通过 FFastGeoStaticMeshComponent 的具体方法设置网格体数据
            // 这里仅为展示 API 用法
        },
        true
    );

    FastGeoContainer = Result.Container;

    if (FastGeoContainer)
    {
        OnRegisteredHandle = FastGeoContainer->GetOnRegistered().AddLambda([this]()
        {
            // 注册完成后可以安全查询组件
            TArray<IPrimitiveComponent*> Primitives = FastGeoContainer->GetPrimitiveComponents();
            UE_LOG(LogTemp, Log, TEXT("FastGeo registered with %d primitive components"), 
                Primitives.Num());
        });
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理系统 — 异步物理状态创建/销毁 |
| `MeshDescription` | 网格体数据处理 |
| `PhysicsCore` | 物理系统核心接口 |
| `Engine` | World Partition、Level Streaming 集成 |
| `RenderCore` | 渲染线程命令和场景代理 |
| `RHI` | PSO Precaching 支持 |

> 注：FastGeoStreamingEditor 模块依赖 `UnrealEd`，用于编译期的 Cell 转换器功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d478e533` | [CodeClarity] CVar description and naming cleanup for FastGeo / SSAM / Async Physics | 清理控制台变量命名和描述，代码规范化 |
| 2026-05-12 | `8b5eabf3` | FastGeo: Support GPU animated instanced skinned meshes. | 新增 GPU 动画实例化骨骼网格体支持 |
| 2026-05-12 | `10c54c93` | [FastGeo] Harden surrogate component physics queries | 加固代理组件的物理查询健壮性 |
| 2026-05-12 | `6fa3ba35` | [FastGeo] Fix world transform for unregistered components in runtime cell transformer | 修复运行时单元转换器中未注册组件的世界变换问题 |
| 2026-05-12 | `8ce6709d` | [FastGeo] Resolve WalkableSlopeOverride from BodySetup when building surrogate descriptor | 修复构建代理描述符时从 BodySetup 正确解析 WalkableSlopeOverride |

### 维护评价

- **状态**：🟢 **活跃开发中** — 最近一次更新在 2026 年 5 月，距今不到 1 个月
- **创建时间**：2025 年 3 月，是一个相对年轻的插件
- **更新频率**：近期有密集的功能更新和 bug 修复，说明 Epic 内部正在积极使用和迭代
- **实验性标记**：`IsExperimentalVersion=true` 且 `EnabledByDefault=false`，API 可能在未来版本中发生变化
- **功能成熟度**：从代码深度来看，已包含完整的异步渲染/物理管线、PSO 集成、多种组件类型支持、碰撞代理机制，功能相当完善
- **已知限制**：
  - 需要启用 `p.Chaos.EnableAsyncInitBody`
  - 仅支持不可变静态几何体，不支持动态 Actor
  - 作为实验性插件，API 和行为可能随版本变化
- **推荐使用**：如果你的项目有大世界流送性能问题且愿意承担实验性 API 变更风险，**推荐试用**。对于需要稳定 API 的生产项目，建议持续关注但暂不依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming)
- [官方文档]()（暂无公开文档）