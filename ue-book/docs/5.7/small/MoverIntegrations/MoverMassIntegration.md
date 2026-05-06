# Mover Integrations

> Mover Integrations is a Unreal Engine plugin acting as an umbrella to cover a variety of modules supporting Mover's integration with other plugins, such as animation, AI, and other gameplay systems.

| 属性 | 值 |
|---|---|
| 中文名 | Mover 集成 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MoverIntegrations` (Runtime), `MoverMassIntegration` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-07 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MoverIntegrations) | |

---

## 用途

Mover Integrations 插件为 **Mover**（UE5 新一代运动系统）与 **Mass Entity**（高性能实体框架）之间提供双向数据同步能力。  
它解决了以下问题：

- **Mass 驱动的 AI 无法直接控制 Mover 角色**：Mass 使用实体组件（Fragments）管理位置、速度等，而 Mover 使用 Actor Component 驱动角色运动。本插件提供翻译器和特性（Traits），实现 Mass → Mover（下达移动意图）和 Mover → Mass（获取运动状态）的双向同步。
- **简化集成流程**：通过预定义的 Agent Trait（`UMoverMassAgentTrait`、`UMoverMassAgentOrientationSyncTrait`），开发者只需在 Mass 配置中添加这两个特性，即可让实体与 Mover 角色同步，无需手写自定义翻译器。

本插件是“伞式”插件，当前唯一实现模块是 **MoverMassIntegration**，未来可能扩展动画、AI 等方向的集成。

## 使用场景

- **大规模 AI 角色群集**：使用 Mass 框架管理成千上万个智能体的逻辑（寻路、决策），但希望每个智能体使用 Mover 进行真实的物理运动。通过本插件，Mass 可以将目标位置转化为 Mover 的移动指令，同时实时获取 Mover 的速度、位置更新回 Mass 实体。
- **基于 Mover 的角色 + Mass 状态同步**：需要让 Mass 的系统（如 MassZoneGraphNavigation、MassLookAt）与 Mover 的运动状态对齐，例如同步朝向、地面速度等。
- **继承已有 Mover 角色的 Mass 集成**：项目中已使用 Mover 控制角色，现在希望利用 Mass 进行高级 AI 行为，无需重写移动逻辑。

## 蓝图用法

本插件主要提供 **Mass Agent Trait**，可在 Mass Agent 配置中直接添加。Trait 会自动注册必要的翻译器。

### 核心节点（蓝图类）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Agent Mover Sync` | 添加此特性后，实体与 Mover 组件建立联系，自动同步位置、速度、最大速度（Mover→Mass），并允许 Mass 向 Mover 发送移动意图（Mass→Mover）。 | `UMoverMassAgentTrait` |
| `Agent Mover Orientation Sync` | 添加此特性后，Mover 的旋转会同步到 Mass 实体（Mover→Mass），Mass 也可以将朝向修改写回 Mover。注意：Mover 目前对外部旋转修改不友好，可能产生警告。 | `UMoverMassAgentOrientationSyncTrait` |

### 使用示例（蓝图描述）

1. **创建 Mass Agent**：
   - 在关卡中放置一个 Mass Agent 角色（继承自 `AMassAgent` 或其子类）。
   - 确保该角色拥有 **NavMoverComponent** 和 **MoverComponent**（通常由角色蓝图添加）。
   - 打开该 Agent 的 `Mass Agent Component` → `Agent Traits`，点击 **+** 添加 `Agent Mover Sync` 和 `Agent Mover Orientation Sync` 特性。
   - 配置 `Agent Mover Sync` 特性的 `bSyncTransform` 属性（默认 false），如果希望 Mover 的位移由 Mass 完全控制，可设为 true；否则 Mass 只发送移动意图，实际位置仍由 Mover 计算。

2. **配置翻译器（自动完成）**：
   - 上述 Trait 会自动注册 `UMassNavMoverToMassTranslator`（Mover→Mass）和 `UMassToNavMoverTranslator`（Mass→Mover）等翻译器，无需额外手动操作。

## C++ 用法

### 头文件引入

```cpp
#include "MoverMassAgentTraits.h"
#include "MoverMassTranslators.h"
```

### 基本用法

以下示例展示如何从 C++ 动态创建 Mass Agent 并添加 Mover 集成特性（假设已有 `AMassAgent` 角色和 `NavMoverComponent`、`MoverComponent`）：

```cpp
// 在角色初始化时，为 Mass Agent 添加 Trait
void AMyMassAgent::PostInitializeComponents()
{
    Super::PostInitializeComponents();

    // 获取 Mass Agent Component
    UMassAgentComponent* MassAgent = FindComponentByClass<UMassAgentComponent>();
    if (MassAgent)
    {
        // 添加 Agent Mover Sync Trait
        UMoverMassAgentTrait* MoverSyncTrait = NewObject<UMoverMassAgentTrait>(MassAgent);
        MassAgent->AddTrait(MoverSyncTrait);

        // 添加 Agent Mover Orientation Sync Trait (可选)
        UMoverMassAgentOrientationSyncTrait* OrientSyncTrait = NewObject<UMoverMassAgentOrientationSyncTrait>(MassAgent);
        MassAgent->AddTrait(OrientSyncTrait);
    }
}
```

### 进阶用法

如果需要自定义翻译逻辑，可以直接子类化翻译器并注册。例如，自定义 Mover→Mass 的速度同步频率：

```cpp
// 自定义翻译器，减少同步频率
UCLASS()
class UMyCustomToMassTranslator : public UMassNavMoverToMassTranslator
{
    GENERATED_BODY()

protected:
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override
    {
        // 仅每 5 帧执行一次
        if (Context.GetEntityManager().GetEntityCount() % 5 != 0) return;

        Super::Execute(EntityManager, Context);
    }
};
```

然后在实体构建时通过 `UMoverMassAgentTrait` 的子类或通过 `MassEntityTemplateBuildContext` 直接指定自定义翻译器。

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在 **自定义 Mass 处理器** 中使用 Mover 集成的同步数据。

### MoverSyncDemoProcessor.h

```cpp
#pragma once

#include "MassProcessor.h"
#include "MoverSyncDemoProcessor.generated.h"

UCLASS()
class UMoverSyncDemoProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMoverSyncDemoProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

### MoverSyncDemoProcessor.cpp

```cpp
#include "MoverSyncDemoProcessor.h"
#include "MassCommonFragments.h"
#include "MoverMassTranslators.h"  // 包含 FNavMoverComponentWrapperFragment 等

UMoverSyncDemoProcessor::UMoverSyncDemoProcessor()
{
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
}

void UMoverSyncDemoProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FNavMoverComponentWrapperFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddTagRequirement<FMassNavMoverCopyToMassTag>(EMassFragmentPresence::All);
}

void UMoverSyncDemoProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [](FMassExecutionContext& Context)
    {
        const TConstArrayView<FTransformFragment> Transforms = Context.GetFragmentView<FTransformFragment>();
        const TArrayView<FNavMoverComponentWrapperFragment> MoverWrappers = Context.GetMutableFragmentView<FNavMoverComponentWrapperFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            const FTransform& EntityTransform = Transforms[i].GetTransform();
            if (UNavMoverComponent* NavMover = MoverWrappers[i].Component.Get())
            {
                // 示例：输出 Mover 的当前位置
                UE_LOG(LogTemp, Log, TEXT("Entity %d Mover position: %s"), i, *NavMover->GetOwner()->GetActorLocation().ToString());
            }
        }
    });
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 实体框架核心模块 |
| `MassActors` | Mass Agent 和实体模板构建支持 |
| `Mover` (或 `NavigationMover`) | Mover 运动系统组件（`NavMoverComponent`, `MoverComponent`） |

其他模块如 `Core`, `CoreUObject`, `Engine`, `Slate` 等为标准依赖，不单独列出。

## 维护状态

### 近期更新

- 2025-06-10 `675fd5ae` 修复 CIS 编译错误（EngineRuntimeTests.h、MoverMassTranslators.h 等）
- 2025-05-07 `1207fa81` 初始提交：添加 UE5 Mover-Mass 翻译器及 Mover Integrations 插件框架

### 维护评价

该插件于 2025-05 创建，6 月即修复了编译问题，表明正处于**活跃开发期**。由于插件内容极新（年龄约 0 年），且仅为初始版本，可能存在以下注意事项：

- 目前仅包含 Mover-Mass 集成模块，其他集成模块（动画、AI）尚未发布。
- 朝向外同步（`bSyncTransform`）有已知警告，Mover 可能不接受外部旋转设置。
- 功能尚处于实验阶段，API 可能在后续版本发生变化。

**推荐使用**：如果你的项目需要将 Mass 与 Mover 结合，本插件是官方提供的唯一集成方案，但需密切关注后续更新并做好适配。对于生产环境，建议在测试充分后再启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MoverIntegrations)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MoverIntegrations/Tests)（如存在）