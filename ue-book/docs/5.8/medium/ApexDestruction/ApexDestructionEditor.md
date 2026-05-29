# Apex Destruction

> APEX implementation of destruction

| 属性 | 值 |
|---|---|
| 中文名 | 毁灭破碎 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ApexDestruction` (Runtime), `ApexDestructionEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2017-07-26 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ApexDestruction) | |

## 用途

该插件是 NVIDIA APEX 物理引擎在虚幻引擎 4 中的**毁灭（Destruction）系统实现**。它提供了一套完整的工具链，用于创建和运行基于物理模拟的可破坏物体（Destructible Meshes）。其核心功能是将静态网格体（Static Mesh）转换为由大量“碎片”（Fractured Mesh）组成的可破坏资产，并在游戏中根据受到的冲击、爆炸或其他力作用，模拟物体破碎、飞散的真实物理效果。

该插件的存在是为了在虚幻引擎中提供高性能、可控的物体破碎解决方案，广泛应用于游戏中的环境破坏、载具损毁、特效制作等场景。**需要注意的是，自虚幻引擎 4.26 版本起，该插件已被标记为废弃（Deprecated）。** Epic Games 官方推荐使用基于 Chaos 物理框架的 **Chaos Destruction** 系统作为未来的主要破坏解决方案。因此，对于新项目，强烈建议评估并使用 Chaos Destruction。此插件主要适用于维护旧项目或有特定兼容性需求的场景。

## 使用场景

- **游戏中需要可控的物体破碎效果**：例如，用霰弹枪击中木质栅栏，使其断裂成多块；手雷爆炸时，周围的砖墙崩塌。
- **载具损毁系统**：模拟汽车碰撞时保险杠弯曲、玻璃破碎、车身变形脱落。
- **环境交互**：玩家角色撞击或踩踏物体（如桌子、雕像）时，物体根据力度以不同方式解体。
- **特效驱动的毁灭**：在电影或过场动画中，需要精确控制破坏时机和效果的场景。
- **维护使用早期 APEX 毁灭资产的旧版虚幻引擎项目**。

## 蓝图用法

该插件的蓝图 API 主要围绕 `UDestructibleMesh` 和 `UDestructibleComponent` 两个核心类。由于插件已被废弃，许多功能在蓝图中可能不可见或需谨慎使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Destructible Mesh` | 为可破坏组件设置一个可破坏网格体资产。 | `UDestructibleComponent` |
| `Apply Radius Damage` | 对一个球形区域内的可破坏物体施加伤害，模拟爆炸效果。 | `UDestructibleComponent` |
| `Apply Damage` | 对可破坏物体施加一次点状伤害。 | `UDestructibleComponent` |

### 使用示例（蓝图描述）

1.  **创建一个可破坏物体**：
    - 在场景中放置一个 `Destructible Actor`，或在 Actor 上添加 `Destructible Component`。
    - 在该组件的细节面板中，通过 `Set Destructible Mesh` 节点或直接拖放资产，指定一个已创建的 `Destructible Mesh` 资产。

2.  **在游戏运行时触发破坏**：
    - 当子弹击中物体时，获取命中组件，判断其是否为 `UDestructibleComponent`。
    - 如果是，调用 `Apply Damage` 节点，传入子弹命中的位置、法线以及伤害值。物体将在命中点附近开始破碎。

## C++ 用法

在 C++ 中使用该插件，主要涉及创建和操作 `UDestructibleComponent`。

### 头文件引入

```cpp
#include "DestructibleComponent.h"
```

### 基本用法

以下代码演示了如何在 C++ 中动态创建一个可破坏组件并应用伤害。
*（注：此为典型用法示例，非来自特定测试用例）*

```cpp
// 假设在某个 Actor 的 BeginPlay 或构造函数中
if (UDestructibleMesh* MyDestructibleMesh = LoadObject<UDestructibleMesh>(nullptr, TEXT("/Game/Path/To/Your/DestructibleMesh.DestructibleMesh")))
{
    // 创建一个可破坏组件
    UDestructibleComponent* DestructibleComp = NewObject<UDestructibleComponent>(this);
    DestructibleComp->SetDestructibleMesh(MyDestructibleMesh);
    DestructibleComp->AttachToComponent(RootComponent, FAttachmentTransformRules::KeepRelativeTransform);
    DestructibleComp->RegisterComponent();

    // 在某个事件后（如受到伤害），应用破坏
    // 示例：对组件中心施加一个径向伤害
    FVector DamageOrigin = DestructibleComp->GetComponentLocation();
    float DamageAmount = 50.0f;
    float DamageRadius = 100.0f;
    DestructibleComp->ApplyRadiusDamage(DamageAmount, DamageOrigin, DamageRadius, 1000.0f, true);
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何在 Actor 中包含一个可破坏组件。

**DestructibleDemoActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "DestructibleDemoActor.generated.h"

UCLASS()
class ADestructibleDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ADestructibleDemoActor();

protected:
    virtual void BeginPlay() override;

public:
    // 在编辑器中指定可破坏网格体资产
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Destruction")
    UDestructibleMesh* DestructibleMeshAsset;

private:
    UPROPERTY(VisibleAnywhere)
    UDestructibleComponent* DestructibleComponent;
};
```

**DestructibleDemoActor.cpp**
```cpp
#include "DestructibleDemoActor.h"
#include "DestructibleComponent.h"

ADestructibleDemoActor::ADestructibleDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建并配置可破坏组件
    DestructibleComponent = CreateDefaultSubobject<UDestructibleComponent>(TEXT("DestructibleComp"));
    RootComponent = DestructibleComponent;
}

void ADestructibleDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 在运行时应用资产
    if (DestructibleMeshAsset)
    {
        DestructibleComponent->SetDestructibleMesh(DestructibleMeshAsset);
    }
}
```

## 模块依赖

根据 `ApexDestruction.Build.cs` 文件，要使用此插件的功能，你的模块通常需要依赖：

| 模块 | 用途 |
|---|---|
| `ApexDestruction` | 插件核心运行时模块，包含可破坏组件和资产类。 |
| `APEX` | NVIDIA APEX 物理库的封装模块，提供底层物理模拟支持。 |

**注意**：由于 APEX 是一个第三方库，依赖它会增加项目的打包体积和潜在的平台兼容性问题。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF 格式。 |
| 2025-10-14 | `5f7283a0` | Copying a deleted file over that RoboMerge/p4 got confused about | 修复因版本控制工具混淆导致的文件删除问题。 |
| 2025-10-07 | `96352708` | Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件名从 Base* 重命名为 Default*，遵循引擎新规范。 |
| 2025-07-14 | `8c4cad91` | Changed all WITH_EDITORONLY_DATA properties in StaticMesh to have accessors... | 修改了 StaticMesh 中仅编辑器数据属性的访问器。 |
| 2024-11-23 | `04a0ec79` | Fix errors with latest compiler | 修复与最新编译器版本的兼容性错误。 |

### 维护评价

**不推荐在新项目中使用。** 这是一个已明确标记为废弃（Deprecated）的插件，自 UE 4.26 (2020年) 起不再有新功能开发。近期更新（2024-2026）仅限于基础的维护性工作，如修复编译错误、日志格式更新和配置文件命名规范调整，没有任何功能性改进或新特性。

该插件的主要价值在于**兼容旧项目**。如果你正在维护一个依赖 APEX 毁灭效果的旧版虚幻引擎项目，这个插件是必需的。但对于新项目，请务必使用官方推荐的 **Chaos Destruction** 系统，它更现代、集成度更高，并且会持续获得支持和更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ApexDestruction)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/destructible-meshes-in-unreal-engine/) (包含旧版信息，新版本指南指向 Chaos Destruction)