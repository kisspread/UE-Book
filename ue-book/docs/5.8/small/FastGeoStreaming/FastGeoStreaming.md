# Fast Geo Streaming

> A system that extracts and converts a partitioned world's geometry to optimize world streaming performance.

| 属性 | 值 |
|---|---|
| 中文名 | 快速几何流式加载 |
| 分类 | World Building |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `FastGeoStreaming` (Runtime), `FastGeoStreamingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming) | |

## 用途

FastGeoStreaming 是一个实验性插件，旨在**优化大型开放世界游戏的流式加载性能**。它通过将世界分区中的不可变静态几何体（StaticMeshes 和 InstanceStaticMeshes，包括有无碰撞的情况）提取并转换为一种轻量级的、非 UObject 的数据结构来实现性能提升。

该插件的核心价值在于：
1. **减少主线程阻塞**：将几何体的创建、销毁和渲染状态管理等耗时操作移出游戏线程，在后台工作线程中异步执行。
2. **优化内存布局**：使用轻量级数据结构替代传统的 UObject 组件，减少内存占用和垃圾回收开销。
3. **无缝集成**：作为关卡流式加载过程的一部分，完全兼容世界分区功能，如数据层（Data Layers）和分层细节层级（HLOD）。
4. **物理状态管理**：支持异步的物理状态创建和销毁，配合 Chaos 物理引擎。

简而言之，这个插件解决了在大型开放世界中，传统 UObject 组件流式加载时带来的性能瓶颈问题，通过将其转换为更高效的数据结构并异步处理，显著提升流式加载的平滑度和性能。

## 使用场景

- **大型开放世界游戏**：当你有一个基于世界分区的大地图，并且地图中包含大量静态几何体（如建筑、岩石、植被实例）时，FastGeoStreaming 可以显著改善加载卡顿和内存压力。
- **需要高精度碰撞的几何体**：插件支持将带碰撞的静态网格体和实例化静态网格体转换，确保物理交互正常。
- **优化 HLOD 系统**：与 HLOD 系统集成，为 HLOD 对象提供轻量级的流式加载方案。
- **多线程渲染准备**：插件通过 PSO（Pipeline State Object）预缓存和异步渲染状态管理，为渲染线程的并行工作做好准备。

## 蓝图用法

由于 FastGeoStreaming 主要是一个底层优化系统，它不直接暴露大量蓝图节点给设计师使用。其主要配置和控制发生在编辑器（通过 `FastGeoStreamingEditor` 模块）和 C++ 代码层面。

### 核心节点

在 `FastGeoStreamingEditor` 模块中，提供了用于配置转换规则的资产。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Settings` | 一个 `UFastGeoTransformerSettings` 数据资产，用于配置哪些 Actor 和 Component 类可以/不能被转换为 FastGeo。 | `UFastGeoWorldPartitionRuntimeCellTransformer` |
| `Convert settings to reusable Asset` | 编辑器中的一个按钮，用于将当前转换设置保存为可重用的资产。 | `UFastGeoWorldPartitionRuntimeCellTransformer` |

### 使用示例（蓝图描述）

FastGeoStreaming 的使用主要通过编辑器中的设置资产来配置，而非蓝图图表连接。典型流程如下：

1.  在项目设置或插件设置中，找到 `FastGeoWorldPartitionRuntimeCellTransformer`。
2.  在其 `Settings` 属性中，配置允许或禁止转换的 Actor 类和 Component 类。
3.  当世界分区单元（Cell）被加载或卸载时，系统会根据这些设置自动将符合条件的几何体转换为 FastGeo 数据结构。
4.  开发者可以通过 `bGenerateSurrogateComponents` 选项来控制是否生成用于物理查询的代理组件。

## C++ 用法

FastGeoStreaming 的核心是 `UFastGeoContainer` 和 `UFastGeoWorldSubsystem`。

### 头文件引入

```cpp
#include "FastGeoContainer.h"
#include "FastGeoWorldSubsystem.h"
```

### 基本用法

以下示例展示了如何在 C++ 中以编程方式创建和销毁一个运行时的 `FastGeoContainer`。这在需要动态生成大量静态几何体的场景（如程序化生成）中非常有用。

**来源文件路径**: `Engine/Plugins/Experimental/FastGeoStreaming/Source/FastGeoStreaming/Internal/FastGeoContainer.h`

```cpp
// 在某个游戏逻辑中，需要动态创建一组静态几何体
UWorld* World = GetWorld();

// 定义一个回调函数，用于向容器中添加组件
auto InitCluster = [](FFastGeoComponentCluster& Cluster)
{
    // 创建一个静态网格体组件并添加到集群中
    FFastGeoStaticMeshComponent& MeshComponent = Cluster.AddComponent(FFastGeoStaticMeshComponent::Type).CastToRef<FFastGeoStaticMeshComponent>();
    // 在这里配置 MeshComponent，例如设置网格体、材质等（通常通过序列化或初始化函数）
    // 注意：这是一个简化的示例，实际配置更复杂。
};

// 创建运行时 FastGeo 容器
FFastGeoCreateRuntimeResult Result = UFastGeoContainer::CreateRuntime(
    World,
    TEXT("MyProceduralGeometry"),
    InitCluster,
    true // 收集资产引用
);

if (Result.Container)
{
    // 容器创建成功，可以订阅注册完成的委托
    Result.Container->GetOnRegistered().AddLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("FastGeo container registered successfully!"));
    });

    // 当不再需要这些几何体时，可以异步销毁容器
    UFastGeoContainer::DestroyRuntime(Result.Container);
}
```

### 进阶用法

你可以通过 `UFastGeoWorldSubsystem` 来监控和控制整个系统的异步任务。

**来源文件路径**: `Engine/Plugins/Experimental/FastGeoStreaming/Source/FastGeoStreaming/Internal/FastGeoWorldSubsystem.h`

```cpp
// 获取世界子系统
UFastGeoWorldSubsystem* Subsystem = World->GetSubsystem<UFastGeoWorldSubsystem>();

// 手动触发处理异步渲染状态任务（通常由子系统自动 Tick，但在需要时可以强制处理）
Subsystem->ProcessAsyncRenderStateJobs(true); // true 表示等待完成

// 检查系统是否正在等待任务完成（例如在关卡加载时）
if (Subsystem->IsWaitingForCompletion())
{
    UE_LOG(LogTemp, Warning, TEXT("FastGeo system is busy with async tasks."));
}

// 订阅组件重创建事件（仅在编辑器中有效）
#if WITH_EDITOR
UFastGeoWorldSubsystem::ComponentsPreRecreateEvent.AddLambda([](const TArray<FFastGeoRegisteredComponent>& Components)
{
    // 在重创建组件前执行某些操作
});
#endif
```

## Demo 示例

以下是一个完整的、最小化的 C++ 示例，展示了如何创建一个运行时的 FastGeo 容器并添加一个简单的静态网格体组件。

**FastGeoDemoComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "FastGeoDemoComponent.generated.h"

class UFastGeoContainer;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UFastGeoDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UFastGeoDemoComponent();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // 要显示的静态网格体
    UPROPERTY(EditAnywhere, Category = "FastGeo Demo")
    UStaticMesh* DemoMesh;

    // 是否使用 FastGeo
    UPROPERTY(EditAnywhere, Category = "FastGeo Demo")
    bool bUseFastGeo = true;

private:
    UPROPERTY(Transient)
    UFastGeoContainer* FastGeoContainer = nullptr;

    void CreateFastGeoGeometry();
    void DestroyFastGeoGeometry();
};
```

**FastGeoDemoComponent.cpp**
```cpp
#include "FastGeoDemoComponent.h"
#include "FastGeoContainer.h"
#include "FastGeoStaticMeshComponent.h"

UFastGeoDemoComponent::UFastGeoDemoComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UFastGeoDemoComponent::BeginPlay()
{
    Super::BeginPlay();
    if (bUseFastGeo && DemoMesh)
    {
        CreateFastGeoGeometry();
    }
}

void UFastGeoDemoComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    DestroyFastGeoGeometry();
    Super::EndPlay(EndPlayReason);
}

void UFastGeoDemoComponent::CreateFastGeoGeometry()
{
    UWorld* World = GetWorld();
    if (!World) return;

    // 定义初始化集群的回调
    auto InitCluster = [this](FFastGeoComponentCluster& Cluster)
    {
        // 向集群添加一个静态网格体组件
        FFastGeoStaticMeshComponent& MeshComp = Cluster.AddComponent(FFastGeoStaticMeshComponent::Type).CastToRef<FFastGeoStaticMeshComponent>();
        
        // 注意：FastGeo 组件的数据通常通过序列化填充。
        // 在这个简化的示例中，我们假设 MeshComp 会使用我们指定的 DemoMesh。
        // 实际应用中，你需要通过一个序列化或从现有 Actor 复制数据的流程。
        // 这里仅为演示，无法直接设置 UStaticMesh*，因为 FFastGeoStaticMeshComponent 并不直接持有 UObject 引用。
    };

    // 创建运行时容器
    FFastGeoCreateRuntimeResult Result = UFastGeoContainer::CreateRuntime(
        World,
        TEXT("DemoFastGeo"),
        InitCluster,
        true
    );

    FastGeoContainer = Result.Container;
}

void UFastGeoDemoComponent::DestroyFastGeoGeometry()
{
    if (FastGeoContainer)
    {
        UFastGeoContainer::DestroyRuntime(FastGeoContainer);
        FastGeoContainer = nullptr;
    }
}
```

## 模块依赖

从 `FastGeoStreaming.Build.cs` 分析，使用者需要注意以下依赖。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | **重要警告**：运行时模块 (`FastGeoStreaming`) 依赖于 `UnrealEd`。这通常不推荐，因为 `UnrealEd` 是编辑器专用模块。这可能是因为该模块在运行时也需要某些编辑器功能（可能是条件编译的），或者这是一个实验性插件的临时做法。使用者在打包项目时需要注意此依赖可能导致的问题。 |

**说明**：由于插件处于实验阶段，且其运行时模块依赖 `UnrealEd`，**强烈建议**仅在开发编辑器环境中使用，或仔细评估在打包后是否会出现链接错误。插件本身没有其他特殊依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d478e533` | [CodeClarity] CVar description and naming cleanup for FastGeo / SSAM / Async Physics | 清理 FastGeo 相关的控制台变量描述和命名，提升代码清晰度。 |
| 2026-05-12 | `8b5eabf3` | FastGeo: Support GPU animated instanced skinned meshes. | 新增对 GPU 动画的实例化蒙皮网格体的支持。 |
| 2026-05-12 | `10c54c93` | [FastGeo] Harden surrogate component physics queries | 加强代理组件的物理查询稳定性。 |
| 2026-05-12 | `6fa3ba35` | [FastGeo] Fix world transform for unregistered components in runtime cell transformer | 修复运行时单元转换器中未注册组件的世界变换问题。 |
| 2026-05-12 | `8ce6709d` | [FastGeo] Resolve WalkableSlopeOverride from BodySetup when building surrogate descriptor | 在构建代理描述时，从 BodySetup 解析可行走坡度覆盖。 |

### 维护评价

- **活跃维护**：插件在 **2026年5月** 仍有持续的功能更新和 Bug 修复，表明其处于**积极开发**状态。
- **实验性**：插件标记为 `IsExperimentalVersion=true`，且默认未启用 (`EnabledByDefault=false`)，说明它仍处于实验和测试阶段，API 和功能可能在未来版本中发生变化。
- **依赖风险**：运行时模块依赖 `UnrealEd` 是一个显著的架构问题，可能会阻碍其在正式发布游戏中的使用。
- **推荐使用**：**仅推荐用于研究和原型开发**。由于其活跃的开发状态和实验性质，它对于探索大规模世界流式加载优化很有价值。但对于生产项目，建议等待其更加成熟并解决依赖问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/FastGeoStreaming)
- 官方文档：无
- 测试用例：未在提供的信息中明确发现专门的测试目录。