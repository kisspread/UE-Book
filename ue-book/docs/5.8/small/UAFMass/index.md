# UAF Mass

> Mass integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF Mass 集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMass` (Runtime), `UAFMassTests` (Runtime) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2025-11-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass) | |

## 用途

此插件为 UAF (Unreal Animation Framework) 提供了与 Mass 框架的集成。其核心目的是让 Mass 实体能够与 UAF 的动画系统进行协调，具体通过添加一种新的“Mass 处理阶段”事件依赖选项来实现。这允许开发者在使用 Mass 框架处理大规模实体（如角色、单位）时，能够精细地控制动画处理的时机，将其与 Mass 的处理流水线（如移动、生成、销毁等）对齐，从而优化性能并确保动画状态与实体逻辑的正确同步。该插件是连接高性能实体管理（Mass）与高级动画系统（UAF）的桥梁。

## 使用场景

- 你正在开发一个需要同屏显示大量具有复杂动画的角色（如 MMO、RTS、战术游戏）的项目，并使用了 Mass 框架来管理这些实体。
- 你需要让这些实体的动画播放（例如行走、攻击、死亡）能够精确地发生在 Mass 处理流水线的特定阶段（例如在移动计算之后，生成视觉表现之前）。
- 你希望利用 Mass 的性能优势，同时不让动画成为瓶颈或出现不同步的问题。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `UAFMass` | Runtime | 插件的核心模块，实现了 UAF 与 Mass 的集成接口。 |
| `UAFMassTests` | Runtime | 包含针对 `UAFMass` 模块的自动化测试用例。 |

## 蓝图用法

此插件的核心功能主要面向 C++ 模块集成，蓝图节点相对有限。提供的节点主要用于运行时查询状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsMassProcessingPhaseEventEnabled` | 检查当前是否启用了 Mass 处理阶段事件依赖。 | `UMassEntityConfigAsset` (可能需要通过蓝图上下文获取) |

### 使用示例（蓝图描述）

1.  **在实体配置中检查状态**：在某个 Mass 实体的配置蓝图或相关逻辑中，可以调用 `IsMassProcessingPhaseEventEnabled` 节点来判断是否采用了 UAFMass 提供的处理阶段同步机制，从而决定后续的动画驱动逻辑。

## C++ 用法

用法主要涉及配置 Mass 实体以使用 UAF 的处理阶段，并可能创建包含 UAF 处理器的实体类型。

### 头文件引入

```cpp
// 核心集成头文件
#include "Mass/UAFMassIntegration.h"

// 如果需要直接使用测试用例中的实体类型，可能还需要
#include "Mass/UAFMassTestTypes.h"
```

### 基本用法

设置一个 Mass 实体配置使用 UAF 的处理阶段。

*(来源: 模块文档 `UAFMass.md` 中描述的接口)*

```cpp
// 获取或创建一个 Mass 实体配置资产 (UMassEntityConfigAsset)
UMassEntityConfigAsset* MyEntityConfig = /* ... */;

// 启用 Mass 处理阶段事件依赖
// 这会让该配置下的实体，其 UAF 动画事件与 Mass 处理阶段绑定
MyEntityConfig->SetEnableMassProcessingPhaseEvent(true);
```

### 进阶用法

结合测试用例，演示如何定义和使用一个集成了 UAF 处理器的实体类型。

*(来源: 测试模块 `UAFMassTests` 及其 `UAFMassTestTypes`)*

```cpp
#include "MassEntityTypes.h"
#include "Mass/UAFMassIntegration.h"
#include "Mass/UAFMassTestTypes.h" // 来自 UAFMassTests 模块的测试类型

// 步骤 1: 定义一个实体类型，该类型包含 UAF 的动画处理器 (Processor)
// 通常在你的项目模块中定义
USTRUCT()
struct FMyGameEntityWithUAFProcessor : public FMassEntityConfigBase
{
    GENERATED_BODY()

    // FMassEntityConfigBase 已包含基础结构
    // 在此处可以添加你游戏特定的 Fragment 或 Tag 定义
};

// 步骤 2: 在某个配置上下文中使用这个实体类型，并设置处理阶段
void SetupEntityWithUAFAnimation()
{
    // 获取一个实体管理器 (例如从子系统)
    UMassEntitySubsystem* MassSubsystem = GetWorld()->GetSubsystem<UMassEntitySubsystem>();
    FMassEntityManager& EntityManager = MassSubsystem->GetMutableEntityManager();

    // 创建一个实体模板 (Archetype)
    FMassArchetypeHandle Archetype = EntityManager.CreateArchetype(/* ... */);

    // 创建实体
    FMassEntityHandle NewEntity = EntityManager.CreateEntity(Archetype);

    // 获取并配置该实体的配置
    if (UMassEntityConfigAsset* EntityConfig = /* ... */)
    {
        // 关键步骤：为这个配置启用 Mass 处理阶段事件
        EntityConfig->SetEnableMassProcessingPhaseEvent(true);

        // 现在，与该实体关联的 UAF 动画处理器
        // 将会在 Mass 的特定处理阶段（如 `EMassProcessingPhase::PrePhysics`）被调用
    }
}
```

## Demo 示例

一个创建包含 UAF 处理器的实体并设置其处理阶段的最小示例。

**MyUAFMassEntity.h**
```cpp
#pragma once

#include "MassEntityTypes.h"
#include "MyUAFMassEntity.generated.h"

USTRUCT(BlueprintType)
struct FMyUAFMassEntityFragment : public FMassFragment
{
    GENERATED_BODY()

    // 可以在这里添加与动画相关的、需要被 Mass 系统读取/写入的数据
    // 例如：当前动画状态、目标姿态等
    // UPROPERTY()
    // float SomeAnimationValue;
};

// 这是一个包含 UAF 处理器配置的实体“模板”或“配置”结构
UCLASS()
class UMyUAFMassEntityConfig : public UMassEntityConfigAsset
{
    GENERATED_BODY()
public:
    UMyUAFMassEntityConfig();

    // 可以在这里重写来添加默认的 Processor
    // virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override;
};
```

**MyUAFMassEntity.cpp**
```cpp
#include "MyUAFMassEntity.h"
#include "Mass/UAFMassIntegration.h"

UMyUAFMassEntityConfig::UMyUAFMassEntityConfig()
{
    // 在构造函数中就可以设置启用 Mass 处理阶段事件依赖
    // 这使得所有使用此配置的实体，其 UAF 动画都与 Mass 阶段同步
    SetEnableMassProcessingPhaseEvent(true);
}

// 使用示例
void SpawnUAFControlledMassEntities()
{
    UWorld* World = /* ... */;
    UMassEntitySubsystem* MassSubsystem = World->GetSubsystem<UMassEntitySubsystem>();

    // 获取我们定义的配置
    UMyUAFMassEntityConfig* MyConfig = GetDefault<UMyUAFMassEntityConfig>();

    // 从配置创建实体
    FMassEntityHandle EntityHandle = MassSubsystem->CreateEntity(MyConfig);

    // 现在，这个实体内部的动画处理将遵循 Mass 的处理阶段调度。
    // 具体的动画逻辑由注册到 UAF 处理器管道 (Processor Pipeline) 中的处理器 (Processor) 实现。
    // 这些处理器现在会收到 Mass 处理阶段的通知。
}
```

## 模块依赖

要使用 `UAFMass` 插件，你的模块需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `MassGameplay` | Mass 框架的游戏玩法核心模块，提供实体和处理器的基类。 |
| `MassEntity` | Mass 框架的实体管理和处理核心。 |
| `UAF` | Unreal Animation Framework 核心模块，提供动画处理的基础架构。 |
| `MassSignals` | Mass 框架的信号系统，可能用于处理阶段事件的通知。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `746b6abb` | Move UAF-Mass trajectory bridge into engine UAFMass plugin | 将 UAF 与 Mass 之间的轨迹桥接功能迁移至引擎的 UAFMass 插件中。 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | Mass 核心头文件移至 Public/Mass/ 子目录，并移除文件名中的 Mass 前缀，是重构的一部分。 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 从 MassEntity 模块中拆分出独立的 MassCore 模块，Mass 框架持续演进。 |
| 2026-03-11 | `1d291fa1` | [Mass] Multi-fragment observer support in UMassObserverProcessor | 为 Mass 观测器处理器添加多 Fragment 支持，增强了其功能。 |
| 2026-02-17 | `baf983b4` | [SubmitTool - UAF] Add validators to build and run LowLevelTests for UAF plugins | 为 UAF 相关插件（包括此插件）的低级别测试添加了构建和运行的验证器，提升质量保证。 |

### 维护评价

- **状态**：**活跃维护**
- **创建时间**：2025年底，插件非常年轻。
- **近期活动**：在2026年上半年有多次提交，内容涉及功能迁移、核心框架重构配合以及测试基础设施加强。
- **评估**：该插件作为 Epic 官方维护的 `UAF` 和 `Mass` 框架集成组件，正处于积极开发和演进阶段。更新内容表明它与底层 Mass 框架的变动保持同步，并不断完善。由于其实验性状态 (`IsExperimentalVersion=true`) 和默认禁用 (`EnabledByDefault=false`)，其 API 可能尚未稳定，但正在被积极构建和测试。**推荐关注并在实验性项目中试用，但在生产项目中需谨慎，注意跟踪 API 变化。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass)