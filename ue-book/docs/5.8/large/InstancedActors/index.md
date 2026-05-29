# InstancedActors

> 无描述

| 属性 | 值 |
|---|---|
| 中文名 | 实例化Actor |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `InstancedActors` (Runtime), `InstancedActorsTestSuite` (UncookedOnly), `InstancedActorsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-10 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InstancedActors) | |

## 用途

InstancedActors 是 Unreal Engine Mass Entity 框架的一个配套插件，其核心目的是提供一种高性能、可扩展的方式来管理和渲染场景中**大量的、静态的环境物体**。它解决的主要问题是：当场景中存在成千上万个相似的静态物体（如树木、岩石、路灯、建筑部件）时，为每个物体都创建一个独立的 Actor 会带来巨大的内存开销和渲染开销。

通过将这类物体转换为“实例化Actor”，系统可以将它们的数据统一存储在 Mass 实体中，并通过**实例化静态网格体（Instanced Static Mesh）** 技术进行批量渲染，从而极大地提升性能和可扩展性。它本质上是 Mass Gameplay 框架在静态环境物体优化上的具体应用。

## 使用场景

- **开放世界场景**：你需要高效渲染整个地图上的树木、灌木、岩石等自然物体。
- **城市模拟**：场景中包含大量重复的路灯、长椅、垃圾桶、建筑外墙模块等装饰物。
- **大型关卡设计**：关卡中密集摆放了同一种类的静态道具，需要优化渲染和内存。
- **使用 Mass 框架**：你的游戏逻辑已经基于 Mass Entity 构建，需要一种统一的方式来处理这些静态环境实体。

## 蓝图用法

蓝图主要通过编辑器工具和运行时子系统与实例化Actor交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Instanced Actors Subsystem` | 获取当前世界的实例化Actor管理子系统 | `UGameInstance` |
| `Create Instance Collection` | 基于一个Actor模板，创建一个实例化Actor集合 | `UInstancedActorsSubsystem` |
| `Destroy Instance Collection` | 销毁一个实例化Actor集合及其所有实例 | `UInstancedActorsSubsystem` |
| `Add Instances` | 向一个集合中动态添加实例（位置、旋转等） | `UInstancedActorsSubsystem` |
| `Remove Instances` | 从集合中移除指定实例 | `UInstancedActorsSubsystem` |
| `Convert Actor` | (编辑器) 将选中的单个Actor转换为实例化Actor表示 | `UInstancedActorsEditorSubsystem` |
| `Convert Actors` | (编辑器) 批量转换场景中的多个Actor | `UInstancedActorsEditorSubsystem` |

### 使用示例（蓝图描述）

**场景：动态放置树木**
1.  在 BeginPlay 中，使用 `Get Instanced Actors Subsystem` 节点获取子系统引用。
2.  调用 `Create Instance Collection` 节点，将一个树的 Blueprint Actor 作为模板传入，创建一个集合。
3.  通过循环和 `Add Instances` 节点，根据你需要的分布规则（如随机位置）向集合中添加大量树木实例。
4.  如果需要移除部分树木，可以调用 `Remove Instances`。

**场景：编辑器内优化场景**
1.  在编辑器中，选中一个区域内所有同类型的静态网格体Actor。
2.  通过编辑器工具菜单或右键上下文菜单，调用 `Convert Actors` 功能。
3.  插件会分析这些Actor，并将它们转换为一个或多个实例化Actor集合，从而优化场景。

## C++ 用法

### 头文件引入

```cpp
#include "InstancedActorsSubsystem.h"
```

### 基本用法

从子系统获取管理器并创建实例集合（来源于子系统测试用例）。

```cpp
// 假设你已经有一个UWorld指针（World）
UInstancedActorsSubsystem* Subsystem = UWorld::GetSubsystem<UInstancedActorsSubsystem>(World);
if (Subsystem)
{
    // 定义实例化配置（可选）
    FInstancedActorsConfig Config;
    
    // 基于一个Actor类（如ATree）创建集合
    FInstancedActorsCollectionHandle CollectionHandle = Subsystem->CreateInstanceCollection(
        ATree::StaticClass(), 
        Config
    );
    
    // 手动添加一个实例
    FTransform InstanceTransform(FRotator::ZeroRotator, FVector(1000.f, 500.f, 0.f));
    Subsystem->AddInstances(CollectionHandle, {InstanceTransform});
}
```

### 进阶用法

结合数据表（DataTable）或数据注册表（DataRegistry）批量定义实例布局。

```cpp
// 假设你有一个FTableRowBase子类定义了树木位置
UDataTable* TreeLayoutTable = LoadObject<UDataTable>(nullptr, TEXT("/Game/Data/DT_TreeLayout"));
if (TreeLayoutTable)
{
    UInstancedActorsSubsystem* Subsystem = UWorld::GetSubsystem<UInstancedActorsSubsystem>(World);
    
    // 使用辅助函数从数据表创建实例集合
    FInstancedActorsCollectionHandle Handle;
    Subsystem->CreateInstanceCollectionFromDataTable(TreeLayoutTable, ATree::StaticClass(), Handle);
    
    // 此后可以对该集合进行查询、调试可视化等
    #if WITH_EDITOR
    Subsystem->DebugVisualizeCollection(Handle);
    #endif
}
```

## Demo 示例

```cpp
// MyInstancedTreeSpawner.h
#pragma once
#include "GameFramework/Actor.h"
#include "InstancedActorsSubsystem.h"
#include "MyInstancedTreeSpawner.generated.h"

UCLASS()
class AMyInstancedTreeSpawner : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    FInstancedActorsCollectionHandle TreeCollectionHandle;
};

// MyInstancedTreeSpawner.cpp
#include "MyInstancedTreeSpawner.h"
#include "Engine/World.h"
#include "GameFramework/GameInstance.h"

void AMyInstancedTreeSpawner::BeginPlay()
{
    Super::BeginPlay();
    
    UInstancedActorsSubsystem* Subsystem = GetWorld()->GetSubsystem<UInstancedActorsSubsystem>();
    if (Subsystem)
    {
        // 使用蓝图中定义的树资产类
        TreeCollectionHandle = Subsystem->CreateInstanceCollection(
            LoadClass<AActor>(nullptr, TEXT("/Game/Blueprints/BP_Tree"))
        );
        
        // 在随机位置生成1000棵树
        TArray<FTransform> TreeTransforms;
        for (int32 i = 0; i < 1000; ++i)
        {
            TreeTransforms.Add(FTransform(
                FRotator(0, FMath::RandRange(0.f, 360.f), 0),
                FVector(FMath::RandRange(-5000.f, 5000.f), FMath::RandRange(-5000.f, 5000.f), 0),
                FVector(1.f)
            ));
        }
        Subsystem->AddInstances(TreeCollectionHandle, TreeTransforms);
    }
}

void AMyInstancedTreeSpawner::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    UInstancedActorsSubsystem* Subsystem = GetWorld()->GetSubsystem<UInstancedActorsSubsystem>();
    if (Subsystem && TreeCollectionHandle.IsValid())
    {
        // 销毁集合，清理所有实例
        Subsystem->DestroyInstanceCollection(TreeCollectionHandle);
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从 Build.cs 和 .uplugin 的 Plugins 部分分析，该插件除了标准依赖外，还强依赖于以下 Mass 生态系统模块：

| 模块 | 用途 |
|---|---|
| `MassEntity` | 核心的 Mass Entity 框架，用于存储和管理实体数据 |
| `MassGameplay` | Mass 框架的游戏层扩展，提供处理器（Processor）等高级功能 |
| `DataRegistry` | 用于管理和查询定义实例布局的资产（如数据表） |
| `GameFeatures` | 支持作为可选游戏功能（Game Feature）插件进行模块化加载 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `16c20541` | Update Intel OneAPI supported version to 2026.0.0 | 更新 Intel OneAPI 支持的版本至 2026.0.0 |
| 2026-05-12 | `865421ee` | [Mass] PR #12790: InstancedActors: Use Correct Collision CVar In All Net Modes | 修复了在不同网络模式下碰撞相关的控制台变量未正确使用的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏 `UE_LOG` 迁移为新式 `UE_LOGF` |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | [MassCore] 将头文件移动到 `Public/Mass/` 子目录，并移除文件名中的 Mass 前缀 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | [Mass] 从 MassEntity 中提取出 MassCore 模块 |

### 维护评价

**活跃维护**。
该插件创建于2024年初，与 Unreal Engine 5 的 Mass Entity 框架紧密绑定，是引擎现代化、高性能游戏框架的重要组成部分。从近期提交记录（截至2026年5月）来看，它持续接收到来自 Epic 官方的**功能更新、Bug 修复和架构重构**（如日志宏迁移、依赖模块重组）。最新的提交还修复了一个重要的碰撞变量问题。

**结论**：这是一个处于**积极开发和维护**状态的实验性（Experimental）插件。它不是孤立的功能，而是引擎核心 Mass 架构演进的一环。对于计划使用或已经在使用 Mass 框架进行大规模游戏开发的团队，**推荐关注和评估此插件**，但需注意其“实验性”标签，意味着API和行为在未来版本中仍可能发生变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InstancedActors)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InstancedActors/Source/InstancedActorsTestSuite)