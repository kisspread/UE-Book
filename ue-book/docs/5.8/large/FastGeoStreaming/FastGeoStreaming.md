# Fast Geo Streaming

> A system that extracts and converts a partitioned world's geometry to optimize world streaming performance.

| 属性 | 值 |
|---|---|
| 中文名 | 快速几何体流送 |
| 分类 | World Building |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FastGeoStreaming` (Runtime), `FastGeoStreamingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming) | |

## 用途
FastGeoStreaming 是一个用于优化大型开放世界（World Partition）中静态几何体（如 StaticMesh、InstancedStaticMesh、StaticLight 等）流式加载性能的运行时系统。它通过在编辑器阶段（World Partition Cell 转换时）将原始 Actor 及其组件提取并转换为一种轻量级的、非 UObject 的数据结构（`FFastGeoContainer`），从而在运行时避免常规 Actor/Component 的开销。运行时，该系统异步处理渲染状态（Render State）和物理状态（Physics State）的创建与销毁，显著减少了主线程的阻塞时间，提升了世界加载和卸载的流畅度。它与 World Partition 的其他特性（如 Data Layers、HLOD）兼容。

## 使用场景
- **大型开放世界游戏**：当使用 World Partition 进行世界划分，并且存在大量静态环境物体（岩石、建筑、植被实例、灯光、贴花等）时，此插件可以大幅提升加载性能和内存效率。
- **需要异步流式加载/卸载几何体**：对于希望将几何体的渲染和物理状态创建/销毁从 GameThread 移出，实现真正异步流式加载的项目。
- **优化 HLOD 性能**：系统原生支持将 HLOD 对象作为 `FFastGeoHLOD` 进行管理，优化 HLOD 的流式加载。

## 蓝图用法
FastGeoStreaming 主要在 C++ 层面工作，通过蓝图暴露的接口有限，主要用于状态查询和系统控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is FastGeo Enabled` | 检查 FastGeo 系统是否全局启用 | `FFastGeoStreamingModule` |
| `Is Waiting For Completion` | 检查子系统是否正在等待异步任务完成（如关卡添加/移除） | `UFastGeoWorldSubsystem` |
| `Push Async Precache PSOs Job` | 向子系统提交一个 PSO 预缓存异步任务 | `UFastGeoWorldSubsystem` |
| `Push Async Create Render State Job` | 向子系统提交一个渲染状态创建异步任务 | `UFastGeoWorldSubsystem` |
| `Push Async Destroy Render State Job` | 向子系统提交一个渲染状态销毁异步任务 | `UFastGeoWorldSubsystem` |

### 使用示例（蓝图描述）
1.  **查询系统状态**：在需要知道流式加载是否阻塞的逻辑（如等待加载完成）前，可以调用 `Is Waiting For Completion` 节点。
2.  **提交自定义异步任务**（高级用法）：通常由系统内部调用。如果你有一个 `UFastGeoContainer` 对象，可以通过 `Push Async Create Render State Job` 等节点手动触发其异步状态更新。

## C++ 用法
该插件的主要用户接口是 `UFastGeoContainer` 及其相关的组件集群系统。

### 头文件引入
```cpp
#include "FastGeoStreaming/Internal/FastGeoContainer.h"
#include "FastGeoStreaming/Internal/FastGeoComponentCluster.h"
#include "FastGeoStreaming/Internal/FastGeoStaticMeshComponent.h"
// 根据需要引入其他具体组件头文件
```

### 基本用法
以下代码演示了如何在运行时创建一个 `FastGeoContainer` 并向其添加组件。

**Source: 推断自 `UFastGeoContainer::CreateRuntime` 静态方法**

```cpp
// 在某个地方（例如一个管理器类）获取 UWorld 指针
UWorld* World = GetWorld();

// 定义一个初始化回调，用于向容器的组件集群中添加具体的几何体组件
auto InitCluster = [](FFastGeoComponentCluster& Cluster)
{
    // 向集群中添加一个静态网格体组件
    FFastGeoStaticMeshComponent& StaticMeshComp = Cluster.AddComponent(FFastGeoStaticMeshComponent::Type)
        .CastToRef<FFastGeoStaticMeshComponent>();

    // 初始化该组件（通常需要填充网格体、材质、变换等数据）
    // StaticMeshComp.Initialize(...);
};

// 创建一个运行时 FastGeo 容器
FFastGeoCreateRuntimeResult Result = UFastGeoContainer::CreateRuntime(
    World,
    TEXT("MyFastGeoContainer"),
    InitCluster,
    true // 是否收集资产引用
);

if (Result.Container)
{
    // 容器创建成功，异步注册过程已开始
    UFastGeoContainer* FastGeoContainer = Result.Container;

    // 监听注册完成事件
    FastGeoContainer->GetOnRegistered().AddLambda([FastGeoContainer]()
    {
        UE_LOG(LogFastGeoStreaming, Log, TEXT("FastGeo container registered!"));
    });

    // ... 在某个时刻需要销毁时
    UFastGeoContainer::DestroyRuntime(FastGeoContainer);
}
```

### 进阶用法
处理物理和导航系统的交互。

**Source: 推断自 `FFastGeoPhysicsBodyInstanceOwner` 及相关接口**

```cpp
// 当发生物理碰撞或射线检测命中 FastGeo 几何体时
void OnHit(const FHitResult& HitResult)
{
    // 尝试从命中结果获取 FastGeo 的物理体所有者信息
    const FFastGeoPhysicsBodyInstanceOwner* PhysicsOwner = FFastGeoPhysicsBodyInstanceOwner::FromHitResult(HitResult);
    if (PhysicsOwner)
    {
        // 成功命中 FastGeo 几何体
        UFastGeoContainer* Container = PhysicsOwner->GetOwnerContainer();
        FFastGeoPrimitiveComponent* HitComponent = PhysicsOwner->GetOwnerComponent();
        // 可以通过 HitResult.Item 或 HitResult.ItemIndex 获取更精确的实例索引（对于 ISM 等）
        UE_LOG(LogTemp, Log, TEXT("Hit FastGeo Component: %s"), *HitComponent->GetName());
    }
}
```

## Demo 示例
一个最小化的运行时创建 FastGeo 容器的示例。

**FastGeoDemoManager.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "FastGeoDemoManager.generated.h"

class UFastGeoContainer;

UCLASS()
class AFastGeoDemoManager : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    TObjectPtr<UFastGeoContainer> MyFastGeoContainer;
};
```

**FastGeoDemoManager.cpp**
```cpp
#include "FastGeoDemoManager.h"
#include "FastGeoStreaming/Internal/FastGeoContainer.h"
#include "FastGeoStreaming/Internal/FastGeoComponentCluster.h"
#include "FastGeoStreaming/Internal/FastGeoStaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"

void AFastGeoDemoManager::BeginPlay()
{
    Super::BeginPlay();

    if (UWorld* World = GetWorld())
    {
        auto InitCluster = [](FFastGeoComponentCluster& Cluster)
        {
            // 添加一个简单的静态网格体组件
            FFastGeoStaticMeshComponent& SMComp = Cluster.AddComponent(FFastGeoStaticMeshComponent::Type)
                .CastToRef<FFastGeoStaticMeshComponent>();

            // 注意：以下代码是示意，实际需要根据 FFastGeoStaticMeshComponent 的具体 API 填充数据。
            // SMComp.SetStaticMesh(SomeStaticMeshAsset);
            // SMComp.SetMaterial(0, SomeMaterial);
            // SMComp.SetTransform(FTransform::Identity);
        };

        FFastGeoCreateRuntimeResult Result = UFastGeoContainer::CreateRuntime(
            World,
            TEXT("DemoContainer"),
            InitCluster
        );

        if (Result.Container)
        {
            MyFastGeoContainer = Result.Container;
            UE_LOG(LogTemp, Log, TEXT("Demo FastGeo container created and registration started."));
        }
    }
}

void AFastGeoDemoManager::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MyFastGeoContainer)
    {
        UFastGeoContainer::DestroyRuntime(MyFastGeoContainer);
        MyFastGeoContainer = nullptr;
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | `FastGeoStreaming` (Runtime) 模块依赖编辑器模块以支持序列化、资产引用收集等编辑器阶段的功能。这是一个非标准的依赖，表明该运行时模块包含编辑器相关代码（通过 `WITH_EDITOR` 宏隔离）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d478e533` | [CodeClarity] CVar description and naming cleanup for FastGeo / SSAM / Async Physics | 整理 CVar 描述和命名，提升代码清晰度。 |
| 2026-05-12 | `8b5eabf3` | FastGeo: Support GPU animated instanced skinned meshes. | 为 FastGeo 添加对 GPU 动画实例化蒙皮网格体的支持。 |
| 2026-05-12 | `10c54c93` | [FastGeo] Harden surrogate component physics queries | 加强代理组件（Surrogate Component）物理查询的健壮性。 |
| 2026-05-12 | `6fa3ba35` | [FastGeo] Fix world transform for unregistered components in runtime cell transformer | 修复运行时单元转换器中未注册组件的世界变换问题。 |
| 2026-05-12 | `8ce6709d` | [FastGeo] Resolve WalkableSlopeOverride from BodySetup when building surrogate descriptor | 构建代理描述符时，从 BodySetup 解析可行走斜坡覆盖设置。 |

### 维护评价
- **状态**：**活跃维护中**。插件创建于 2025 年 3 月，近期（2026 年 5 月）仍有频繁的功能增强和 Bug 修复提交。
- **特点**：该插件是 Epic Games 官方开发的实验性技术，代码质量高，设计复杂，专注于解决特定领域的核心性能问题。
- **风险**：由于是实验性（`IsExperimentalVersion=true`）且默认禁用（`EnabledByDefault=false`），API 和功能在未来版本中可能发生 breaking changes。`FastGeoStreaming` (Runtime) 模块对 `UnrealEd` 的依赖比较特殊，需要留意。
- **推荐**：对于有明确大世界性能优化需求，并且愿意跟进实验性 API 变化的项目，**推荐评估和使用**。它代表了 UE5 在静态几何体流式加载方面的前沿优化方向。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Tests.FastGeo/)