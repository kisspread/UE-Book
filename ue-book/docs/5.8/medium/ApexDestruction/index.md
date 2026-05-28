# Apex Destruction

> APEX implementation of destruction

| 属性 | 值 |
|---|---|
| 中文名 | APEX 破坏系统 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ApexDestruction` (Runtime), `ApexDestructionEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2017-07-26 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ApexDestruction) | |

## 用途

该插件集成了 NVIDIA APEX Destruction 技术，用于在游戏中实现高性能、基于物理的物体破坏效果。它允许开发者创建可被实时破坏的静态网格体（如墙壁、柱子），并模拟其破碎后的碎片物理行为。APEX 技术因其高效的性能优化而曾被广泛使用，但随着引擎内建物理破坏系统的发展，此插件已不再是唯一或首选方案。

## 使用场景

- **射击游戏**：创建可被子弹或爆炸摧毁的掩体、墙壁和场景物体，增强游戏交互性和真实感。
- **动作冒险游戏**：实现玩家技能（如冲击波）对环境造成的物理破坏效果。
- **模拟游戏**：模拟结构在过度负载或冲击下的真实解体过程。
- **任何需要基于物理的实时破坏效果，且项目历史原因仍需使用 APEX 技术的游戏**。

## 蓝图用法

此插件的蓝图功能主要围绕 `UDestructibleComponent` 展开，用于在蓝图中控制可破坏物体。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Apply Damage` | 对可破坏物体施加伤害，根据强度和位置引发局部破坏。 | `UDestructibleComponent` |
| `Apply Radius Damage` | 对指定球形范围内的所有可破坏物体施加伤害。 | `UDestructibleComponent` |
| `Set Material` | 覆盖可破坏物体特定部分的材质。 | `UDestructibleComponent` |
| `Get Fracture Effect` | 获取用于播放破坏特效的粒子系统资产。 | `UDestructibleComponent` |

### 使用示例（蓝图描述）

1.  **创建可破坏物体**：在场景中放置一个 `Static Mesh Actor`，将其 `Static Mesh Component` 替换为 `Destructible Component` 并赋予对应的 `Destructible Mesh` 资产。
2.  **触发破坏**：在事件图表中，通过 `Apply Damage` 节点（例如绑定到子弹碰撞事件）对该 `Destructible Component` 施加伤害。伤害值将决定破坏的程度和范围。
3.  **处理破坏后事件**：通过 `Destructible Component` 的 `On Component Fracture` 事件委托，可以监听破坏发生，并执行后续逻辑，如播放音效、产生掉落物等。

## C++ 用法

以下示例展示了在 C++ 中如何创建和操作一个可破坏组件。

### 头文件引入

```cpp
#include "DestructibleComponent.h"
```

### 基本用法

（示例基于一般用法模式编写）

```cpp
// .h 文件
#pragma once
#include "GameFramework/Actor.h"
#include "DestructibleComponent.h"
#include "MyDestructibleActor.generated.h"

UCLASS()
class AMyDestructibleActor : public AActor
{
	GENERATED_BODY()
public:
	AMyDestructibleActor();
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Destruction")
	UDestructibleComponent* DestructibleComponent;
};

// .cpp 文件
#include "MyDestructibleActor.h"

AMyDestructibleActor::AMyDestructibleActor()
{
	// 创建可破坏组件并设为根组件
	DestructibleComponent = CreateDefaultSubobject<UDestructibleComponent>(TEXT("DestructibleComp"));
	RootComponent = DestructibleComponent;
}

// 在其他位置（如伤害处理函数）触发破坏
void AMyDestructibleActor::TakeDamage(float DamageAmount)
{
	if (DestructibleComponent)
	{
		FDamageEvent DamageEvent;
		DestructibleComponent->ApplyDamage(DamageAmount, GetActorLocation(), FVector::ZeroVector, DamageAmount);
	}
}
```

## Demo 示例

一个最小的可破坏 Actor 类实现。

```cpp
// SimpleDestructibleActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "SimpleDestructibleActor.generated.h"

class UDestructibleComponent;

UCLASS()
class ASimpleDestructibleActor : public AActor
{
	GENERATED_BODY()
public:
	ASimpleDestructibleActor();

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UDestructibleComponent* DestructibleComp;
};
```

```cpp
// SimpleDestructibleActor.cpp
#include "SimpleDestructibleActor.h"
#include "DestructibleComponent.h"

ASimpleDestructibleActor::ASimpleDestructibleActor()
{
	DestructibleComp = CreateDefaultSubobject<UDestructibleComponent>(TEXT("Destructible"));
	RootComponent = DestructibleComp;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PhysX` | 底层物理引擎支持。 |
| `APEX` | NVIDIA APEX 物理破坏库的核心依赖。 |
| `PhysicsCore` | UE 物理核心模块。 |
| `UnrealEd` | (仅 ApexDestructionEditor 模块) 提供编辑器功能，如资产导入和管理。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移更新。 |
| 2025-10-14 | `5f7283a0` | Copying a deleted file over that RoboMerge/p4 got confused about | 修复因版本控制混乱导致的文件丢失问题。 |
| 2025-10-07 | `96352708` | Renaming Base<Plugin>.ini to Default<Plugin>.ini | 配置文件重命名，符合新的命名规范。 |
| 2025-07-14 | `8c4cad91` | Changed all WITH_EDITORONLY_DATA properties in StaticMesh to have accessors... | 为静态网格编辑器专用数据属性添加访问器。 |
| 2024-11-23 | `04a0ec79` | Fix errors with latest compiler | 修复在新编译器版本上的编译错误。 |

### 维护评价

**可能废弃**。该插件自 **2021 年** 后便没有实质性功能更新，近期提交均为底层维护（编译修复、日志迁移、配置调整）。APEX 物理技术已停止积极开发，且 Unreal Engine 自身的破坏系统（如 Chaos Destruction）已成为官方推荐方案。**强烈不建议在新项目中使用此插件**。对于现有依赖此插件的项目，应评估迁移至引擎内建系统的可行性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ApexDestruction)
- 官方文档：无 (DocsURL 为空)