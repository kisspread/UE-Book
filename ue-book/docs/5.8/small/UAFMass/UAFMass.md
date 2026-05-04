# UAF Mass

> Mass integration for UAF.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMass` (Runtime), `UAFMassTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFMass) | |

## 用途

UAFMass 插件是 Unreal Animation Framework (UAF) 与 Mass 实体系统之间的桥梁。它解决了在需要处理大量实体（如人群、NPC 群体）的场景中，如何让每个 Mass 实体都能驱动并使用 UAF 动画系统的问题。

该插件的核心作用是：
1.  **数据桥接**：定义了特定的 Mass Fragment（数据片段），用于存储与 UAF 系统实例相关的引用和配置数据。
2.  **逻辑处理**：提供了 Mass Processor（处理器），负责将 Mass 实体中的轨迹等数据（如来自 `CharacterTrajectory` 插件）转换并写入到对应 UAF 系统实例的变量中，从而驱动动画。
3.  **模板配置**：提供了 Mass Entity Trait（实体特征），允许开发者在编辑器中方便地为实体模板配置 UAF 资产和相关变量名，简化了集成流程。

简而言之，它让基于 Mass 框架构建的大量实体能够利用 UAF 强大的动画状态机和动画图能力，实现动画驱动的移动和行为。

## 使用场景

-   你正在开发一个大型开放世界游戏，需要同时模拟成百上千个 NPC 的动画驱动移动（如巡逻、逃跑、聚集）。
-   你希望为 Mass 实体系统中的每个角色实例应用复杂的、基于动画蓝图的动画逻辑，而不是简单的骨骼网格体动画。
-   你需要将 Mass 系统中的角色轨迹预测数据（目标位置、方向）无缝传递给 UAF 动画系统，以实现平滑的转向和步态动画。

## 蓝图用法

该插件的蓝图接口主要通过 Mass Entity Trait 暴露，用于在编辑器中配置实体模板。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Mass UAF Trait` | 为实体模板添加 UAF 动画系统支持，需指定 UAF 资产。 | `UMassUAFTrait` |
| `Character Trajectory UAF Setup` | 为实体模板配置角色轨迹到 UAF 变量的映射关系。 | `UCharacterTrajectoryUAFTrait` |

### 使用示例（蓝图描述）

1.  **创建实体模板**：
    *   在内容浏览器中创建一个新的 `Mass Entity Template` 资产。
    *   在模板的 `Traits` 列表中，添加 `Mass UAF Trait`。
    *   在 `Mass UAF Trait` 的细节面板中，设置 `Asset` 属性为你想要使用的 UAF 系统资产（例如，一个包含移动状态机的 UAF 资产）。

2.  **配置轨迹驱动**：
    *   继续在同一个实体模板的 `Traits` 列表中，添加 `Character Trajectory UAF Setup`。
    *   在该 Trait 的细节面板中，配置 `UAF Data` 下的变量名，确保它们与你的 UAF 资产中定义的输入变量名一致（例如，`PoseVariableName` 对应 UAF 中接收轨迹点的变量）。

3.  **生成实体**：
    *   使用 `Mass Spawner` 或其他方式，基于配置好的实体模板在世界中生成大量实体。这些实体将自动拥有 UAF 动画能力，并根据其轨迹数据驱动动画。

## C++ 用法

### 头文件引入

```cpp
#include "UAFMassModule.h"
// 根据需要引入具体的 Fragment 或 Trait 头文件
#include "Fragments/MassUAFFragment.h"
#include "Fragments/CharacterTrajectoryUAFFragments.h"
#include "Traits/MassUAFTrait.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个包含 UAF 支持的 Mass 实体模板。

```cpp
// 假设在某个构建实体模板的函数中
#include "MassEntityTemplateSubsystem.h"
#include "Traits/MassUAFTrait.h"
#include "Traits/CharacterTrajectoryUAFTrait.h"

void BuildMyUAFEntityTemplate(UMassEntityTemplateSubsystem* TemplateSubsystem)
{
    FMassEntityTemplateBuildContext BuildContext;
    
    // 1. 添加基础 UAF Trait，指定动画资产
    UMassUAFTrait* UAFTrait = NewObject<UMassUAFTrait>();
    UAFTrait->AssetData = /* 加载或设置你的 FUAFSystemFactoryAsset */;
    BuildContext.AddTrait(*UAFTrait);
    
    // 2. 添加轨迹到 UAF 的映射 Trait
    UCharacterTrajectoryUAFTrait* TrajectoryTrait = NewObject<UCharacterTrajectoryUAFTrait>();
    // 可以在这里修改默认的变量名
    // TrajectoryTrait->UAFData.PoseVariableName = TEXT("MyTrajectoryVar");
    BuildContext.AddTrait(*TrajectoryTrait);
    
    // 3. 注册模板
    TemplateSubsystem->CreateTemplate(TEXT("MyUAFCharacter"), BuildContext);
}
```

### 进阶用法

你可以通过继承 `UMassProcessor` 来创建自定义处理器，与 UAF 系统进行更深度的交互。例如，读取 UAF 系统输出的动画根运动数据，并将其应用到 Mass 实体的移动中。

```cpp
// 自定义处理器，读取 UAF 根运动
UCLASS()
class UMyUAFRootMotionProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMyUAFRootMotionProcessor();
protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;
    FMassEntityQuery EntityQuery;
};

// 在 ConfigureQueries 中，查询拥有 FMassUAFFragment 和移动相关 Fragment 的实体
void UMyUAFRootMotionProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FMassUAFFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FMassForceFragment>(EMassFragmentAccess::ReadWrite); // 假设的力片段
    // ... 其他需求
}

// 在 Execute 中，从 UAF 系统获取根运动并应用
void UMyUAFRootMotionProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(Context, [this](FMassExecutionContext& Context)
    {
        const TConstArrayView<FMassUAFFragment> UAFFragments = Context.GetFragmentView<FMassUAFFragment>();
        const TArrayView<FMassForceFragment> ForceFragments = Context.GetMutableFragmentView<FMassForceFragment>();
        
        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            const FMassUAFFragment& UAFFrag = UAFFragments[i];
            if (UAFFrag.SystemReference.IsValid())
            {
                // 从 UAF 系统实例获取根运动数据 (伪代码)
                FVector RootMotionDelta = GetRootMotionFromUAF(UAFFrag.SystemReference);
                // 应用到实体的力或速度上
                ForceFragments[i].Force += RootMotionDelta * SomeScale;
            }
        }
    });
}
```

## Demo 示例

以下是一个最小化的示例，展示如何定义一个使用 UAF 的自定义 Mass Fragment 和 Trait。

**MyUAFCharacterFragment.h**
```cpp
#pragma once
#include "MassEntityTypes.h"
#include "MyUAFCharacterFragment.generated.h"

// 自定义片段，存储角色特有数据
USTRUCT()
struct FMyUAFCharacterFragment : public FMassFragment
{
    GENERATED_BODY()
    
    // 例如，存储角色的当前情绪状态，可用于驱动 UAF 动画变量
    UPROPERTY()
    float Mood = 1.0f;
};
```

**MyUAFCharacterTrait.h**
```cpp
#pragma once
#include "MassEntityTraitBase.h"
#include "MyUAFCharacterFragment.h"
#include "Traits/MassUAFTrait.h" // 继承或组合 UAF Trait
#include "MyUAFCharacterTrait.generated.h"

// 自定义 Trait，组合了基础 UAF 功能和自定义数据
UCLASS(EditInlineNew, CollapseCategories, meta = (DisplayName = "My UAF Character"))
class UMyUAFCharacterTrait : public UMassEntityTraitBase
{
    GENERATED_BODY()
    
protected:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override
    {
        // 1. 添加自定义片段
        BuildContext.AddFragment<FMyUAFCharacterFragment>();
        
        // 2. 添加基础 UAF 支持 (通过组合另一个 Trait 或直接添加 Fragment)
        // 这里简化为直接添加 UAF Trait 的逻辑
        UMassUAFTrait* InnerUAFTrait = NewObject<UMassUAFTrait>();
        InnerUAFTrait->AssetData = UAFAsset; // 假设 UAFAsset 是此 Trait 的一个属性
        BuildContext.AddTrait(*InnerUAFTrait);
        
        // 3. 可以添加其他 Trait，如轨迹映射
    }
    
    UPROPERTY(EditAnywhere, Category = "UAF")
    TInstancedStruct<FUAFSystemFactoryAsset> UAFAsset;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MassGameplay` | Mass 实体系统的核心游戏逻辑框架。 |
| `UAF` | Unreal Animation Framework 核心模块，提供动画系统基础。 |
| `CharacterTrajectory` | 提供角色轨迹预测数据，是 UAF 动画驱动移动的常见输入源。 |

## 维护状态

### 近期更新

- 2026-04-23 `746b6abb` Move UAF-Mass trajectory bridge into engine UAFMass plugin
- 2026-04-01 `58888966` [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames
- 2026-03-30 `161605b0` [Mass] Extract MassCore module from MassEntity
- 2026-03-11 `1d291fa1` [Mass] Multi-fragment observer support in UMassObserverProcessor
- 2026-02-17 `baf983b4` [SubmitTool - UAF] Add validators to build and run LowLevelTests for UAF plugins

### 维护评价

-   **创建时间**：2026-02-17，非常新。
-   **维护状态**：**实验性/早期开发**。插件位于 `Experimental` 目录，且 `.uplugin` 中明确标记 `IsExperimentalVersion: true`，`EnabledByDefault: false`。这表明它是一个尚未稳定、API 可能发生重大变化的功能原型。
-   **活跃度**：作为 Epic 官方实验性插件，其更新将跟随 UE5 主版本的开发节奏。在功能稳定并移出 `Experimental` 目录前，不建议在生产项目中依赖。
-   **已知限制**：从源码注释（如 `@TODO`）可以看出，存在一些待解决的问题，例如 UAF 系统实例的所有权管理（当前使用一个临时的 `UMassUAFSubsystem` 作为 UObject 所有者）。
-   **推荐使用**：**仅用于学习和原型验证**。如果你正在探索将 UAF 与 Mass 结合的技术方案，可以研究此插件的实现思路。但对于正式项目，建议等待其成熟或寻找更稳定的替代方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFMass)
-   [官方文档]() (暂无)