# Mover Integrations

> Mover Integrations is a Unreal Engine plugin acting as an umbrella to cover a variety of modules supporting Mover's integration with other plugins, such as animation, AI, and other gameplay systems.

| 属性 | 值 |
|---|---|
| 中文名 | 移动集成 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Mass实体Trait） |
| 模块 | `MoverIntegrations` (Runtime), `MoverMassIntegration` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MoverIntegrations) | |

## 用途

该插件是 **Mover 移动系统** 与 Unreal Engine 其他子系统之间的集成桥梁。Mover 是 UE5 的新一代角色移动框架，而 Mass 是基于 ECS（实体组件系统）的高性能实体管理框架。两者架构差异巨大，无法直接通信。

MoverIntegrations 通过 **Translator（翻译器）** 模式在两个系统之间双向同步数据：
- **位置与速度**：将 Mover 的运动模拟结果写入 Mass 实体的 Fragment，或反过来从 Mass 实体读取意图驱动 Mover 模拟
- **朝向旋转**：同步 Mover 的旋转状态与 Mass 实体的 Transform Fragment
- **输入桥接**：通过 `UMassMoverInputComponent` 将 Mass 实体的运动意图转化为 `FCharacterDefaultInputs`，供 Mover 的 CharacterMoverComponent 消费

这个插件存在的原因是：当你使用 Mass 框架批量管理大量实体（如 AI 群体、NPC 集群）时，每个实体仍然需要精确的碰撞检测和物理移动能力，而这正是 Mover 擅长的。MoverIntegrations 让你可以同时利用两者的优点。

## 使用场景

- 你在用 Mass 框架管理大量 AI 角色，同时需要它们通过 Mover 系统进行精确的导航移动 → 用 `UMoverMassAgentTrait`
- 你需要将 Mass 实体的运动意图（速度、朝向）传递给基于 Mover 的角色 Actor → 用 `UMassMoverInputComponent`
- 你需要双向同步：Mover 模拟结果写回 Mass 实体，Mass 的运动决策驱动 Mover → 配置对应的 Translator

## 蓝图用法

### Mass 实体 Trait

该插件提供的主要蓝图接口是 Mass Entity Trait，可在 Mass Entity 配置中直接添加：

| Trait 名称 | 显示名 | 说明 | 所在类 |
|---|---|---|---|
| `Agent Mover Sync` | Agent Mover Sync | 为实体初始化 NavMoverComponent，同步 Mover 与 Mass 之间的移动意图和速度。可选同步 Transform | `UMoverMassAgentTrait` |
| `Agent Mover Orientation Sync` | Agent Mover Orientation Sync | 同步 Mover 与 Mass 之间的朝向旋转 | `UMoverMassAgentOrientationSyncTrait` |
| `Mover Input Trait` | Mover Input Trait | 为实体添加读写速度和 Transform 的 Fragment，桥接 Mover 驱动的 Actor 输入 | `UMoverInputTrait` |

### 蓝图可生成组件

| 组件 | 说明 | 所在类 |
|---|---|---|
| `MassMoverInputComponent` | 桥接 Mass 实体与 Mover 角色的输入组件，每帧产生 `FCharacterDefaultInputs` | `UMassMoverInputComponent` |

### 使用示例（蓝图描述）

**场景：为 Mass 实体启用 Mover 移动同步**

1. 在 Mass Entity Config 资产中，添加 `Agent Mover Sync` Trait
2. 在 Trait 的属性面板中，根据需求勾选 `bSyncTransform`（是否同步位置旋转）
3. 确保对应 Actor 挂载了 `NavMoverComponent` 和 `MoverComponent`
4. 根据 Mass 的同步方向（Entity→Actor 或 Actor→Entity），Translator 会自动注册并运行

**场景：通过输入组件桥接 Mass 实体到 Mover 角色**

1. 在 Mass Entity Config 中添加 `Mover Input Trait`
2. 在角色蓝图中添加 `MassMoverInputComponent` 组件
3. `MassMoverInputComponent` 会自动实现 `IMoverInputProducerInterface`，每帧读取实体的期望速度和旋转，产生 Mover 输入

## C++ 用法

### 头文件引入

```cpp
#include "MoverMassTranslators.h"
#include "MassMoverInputTranslator.h"
#include "MoverMassAgentTraits.h"
#include "MassMoverInputComponent.h"
#include "MoverInputTrait.h"
```

### 基本用法：理解 Translator 数据流

该插件的核心是四组双向 Translator，分别处理两种 Mover 后端（NavMoverComponent 和 MoverComponent）：

```cpp
// 来源: Public/MoverMassTranslators.h
// 
// NavMoverComponent 路径（传统 AI 导航移动）:
//   UMassNavMoverToMassTranslator          → Mover → Mass（位置/速度）
//   UMassToNavMoverTranslator              → Mass → Mover（移动意图）
//   UMassNavMoverActorOrientationToMassTranslator → Mover → Mass（朝向）
//   UMassOrientationToNavMoverActorOrientationTranslator → Mass → Mover（朝向）
//
// MoverComponent 路径（新一代 Mover 输入桥接）:
//   UMassToMoverInputTranslator   → Mass → Mover（通过 UMassMoverInputComponent）
//   UMoverInputToMassTranslator   → Mover → Mass（读取 MoverComponent 输出）
```

### 进阶用法：自定义 Mass Trait 注册 Translator

```cpp
// 来源: Public/MoverMassAgentTraits.h
// UMoverMassAgentTrait::BuildTemplate 的实现逻辑：

void UMoverMassAgentTrait::BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const
{
    // 根据 Mass 的同步方向（SyncDirection）决定添加哪些 Translator
    // EntityToActor: 实体驱动角色 → 添加 UMassToNavMoverTranslator
    // ActorToEntity: 角色驱动实体 → 添加 UMassNavMoverToMassTranslator
    
    // 如果 bSyncTransform 为 true，还会添加朝向同步的 Translator
    
    // 添加 FNavMoverComponentWrapperFragment 用于在 Translator 中访问 NavMoverComponent
}
```

### 使用 UMassMoverInputComponent

```cpp
// 来源: Public/MassMoverInputComponent.h
// 该组件实现了 IMoverInputProducerInterface，桥接 Mass 实体意图到 Mover 输入

void SetupMoverInputBridge(AActor* OwnerActor)
{
    // 添加组件到角色
    UMassMoverInputComponent* InputComp = NewObject<UMassMoverInputComponent>(OwnerActor);
    OwnerActor->AddInstanceComponent(InputComp);
    
    // 设置期望的速度和旋转（通常由 Mass Translator 自动设置）
    InputComp->SetDesiredVelocity(FVector(100.f, 0.f, 0.f));
    InputComp->SetDesiredRotation(FQuat::Identity);
    
    // ProduceInput_Implementation 会在每帧被 Mover 系统调用
    // 自动将 DesiredVelocity 和 DesiredRotation 转换为 FMoverInputCmdContext
}
```

## Demo 示例

```cpp
// MyMassEntity.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyMassEntity.generated.h"

class UMassMoverInputComponent;

// 示例：一个通过 Mass 实体驱动的 Mover 角色
UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMyMassDrivenCharacter : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    
    // 读取 Mover 输入组件的状态
    UFUNCTION(BlueprintCallable)
    FVector GetEntityVelocity() const;

protected:
    UPROPERTY()
    TObjectPtr<UMassMoverInputComponent> MoverInputBridge;
};
```

```cpp
// MyMassEntity.cpp
#include "MyMassEntity.h"
#include "MassMoverInputComponent.h"

void UMyMassDrivenCharacter::BeginPlay()
{
    Super::BeginPlay();
    
    // 查找或创建 Mover 输入桥接组件
    MoverInputBridge = GetOwner()->FindComponentByClass<UMassMoverInputComponent>();
    
    if (!MoverInputBridge)
    {
        MoverInputBridge = NewObject<UMassMoverInputComponent>(GetOwner(), TEXT("MassMoverBridge"));
        MoverInputBridge->RegisterComponent();
    }
}

FVector UMyMassDrivenCharacter::GetEntityVelocity() const
{
    if (MoverInputBridge)
    {
        return MoverInputBridge->GetDesiredVelocity();
    }
    return FVector::ZeroVector;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass ECS 框架核心，提供 Entity、Fragment、Tag、Translator 基类 |
| `MassSpawner` | Mass 实体生成器，Entity Template 构建 |
| `MassRepresentation` | Mass 实体表示层，`FObjectWrapperFragment` 基类 |
| `NavigationSystem` | `UNavMoverComponent` 提供基于导航系统的移动能力 |
| `AIModule` | AI 移动子系统集成 |
| `Mover` | UE5 新一代移动框架，`UMoverComponent`、`FCharacterDefaultInputs` |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c61e2782` | [Mass] Add Mover input-component bridge to MoverMassIntegration plugin | 新增 Mover 输入组件桥接，支持 Mass 实体通过 UMassMoverInputComponent 驱动 Mover 角色 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 从 MassEntity 中抽取 MassCore 模块，重构依赖关系 |
| 2025-06-10 | `675fd5ae` | CIS issue#936427: Compile errors in EngineRuntimeTests.h, MoverMassTranslators.h and MoverMassTransl | 修复编译错误，涉及 MoverMassTranslators 头文件问题 |
| 2025-05-07 | `1207fa81` | Mover: Adding UE5 Mover-Mass translators along with a Mover Integrations plugin to house various integrations between Mover and other systems | 初始提交，创建 MoverIntegrations 插件并添加 Mover-Mass 翻译器 |

### 维护评价

- **活跃维护中**：创建于 2025 年 5 月，最近一次功能性更新在 2026 年 5 月（新增输入组件桥接）
- 持续有新功能添加，说明 Epic 内部仍在积极使用和扩展此插件
- 存在已知限制：Mover 系统不支持外部直接修改旋转，可能会产生警告或回滚（源码中多处 TODO 注释）
- 作为实验性插件，API 可能在未来版本中发生变化
- **推荐使用**：如果你的项目同时使用了 Mass 框架和 Mover 移动系统，此插件是官方推荐的集成方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MoverIntegrations)
- [官方文档]()（暂无）