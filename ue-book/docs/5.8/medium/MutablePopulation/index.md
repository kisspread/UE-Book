# Mutable Population

> Extend the Mutable plugin to support Population assets.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 人群定制化插件 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据表等） |
| 模块 | `CustomizableObjectPopulation` (Runtime), `CustomizableObjectPopulationEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2024-09-13 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutablePopulation) | |

## 用途

此插件是 **Mutable** 插件的扩展，专门用于支持 **Population（人群）** 资产。它解决的核心问题是：如何在基于 Mutable 系统生成大量、多样化的可定制角色实例（例如游戏中的 NPC 群体）。

**存在意义**：将原 Mutable 插件中关于“人群”的功能（如定义人群模板、实例化配置）分离出来，形成一个独立的实验性插件。这样做使得主 Mutable 插件保持核心功能的纯粹，而人群相关的复杂功能和资产（如 `UCustomizableObjectPopulation`、`UCustomizableObjectPopulationGenerator`）可以在需要时被选择性地启用和独立开发。

## 使用场景

- 你在开发一个需要生成大量外观各异的 NPC 的开放世界或 MMORPG 游戏。
- 你需要基于一个基础角色模型，通过规则（如年龄、性别、服装风格）快速随机生成成千上万个外观独特的角色实例。
- 你希望用数据驱动（Data Table）的方式管理人群生成规则，方便美术和策划配置。

## 蓝图用法

该插件的核心蓝图功能在于定义和生成人群。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Population` | 根据人口描述生成一组可定制化对象实例。 | `UCustomizableObjectPopulation` |
| `Generate Population` | 使用生成器从指定的 `UCustomizableObjectPopulation` 资产生成角色实例。 | `UCustomizableObjectPopulationGenerator` |
| `Apply Character Tags` | 将特定的角色标签（如“平民”、“士兵”）应用到人口生成过程中，以影响外观组合。 | `UCustomizableObjectPopulation` |

### 使用示例（蓝图描述）

1.  **创建人口资产**：在内容浏览器中右键，创建一个 `CustomizableObjectPopulation` 资产。在此资产中，通过 `人口类` 和 `属性权重` 等数据表来定义人群的构成规则。
2.  **在关卡中生成**：放置一个 `CustomizableObjectPopulationGenerator` Actor，并将之前创建的 `Population` 资产赋予它。
3.  **触发生成**：在游戏逻辑（如关卡加载时或玩家进入区域时）调用该 Actor 的 `Generate Population` 节点，引擎将根据规则在指定区域生成一系列随机外观的角色实例。

## C++ 用法

### 头文件引入

```cpp
#include "CustomizableObjectPopulation.h"
#include "CustomizableObjectPopulationGenerator.h"
```

### 基本用法

创建一个简单的人群生成流程。
（来源：基于 `UCustomizableObjectPopulationGenerator` 的测试逻辑推断）

```cpp
// 1. 获取或创建人口生成器 Actor
UCustomizableObjectPopulationGenerator* PopulationGenerator = ...; // 通常从场景中获取或动态创建

// 2. 设置人口资产
UCustomizableObjectPopulation* PopulationAsset = LoadObject<UCustomizableObjectPopulation>(nullptr, TEXT("/Game/Data/DA_CivilianPopulation"));
PopulationGenerator->Population = PopulationAsset;

// 3. 在需要时触发生成
PopulationGenerator->GeneratePopulation();
```

### 进阶用法

动态修改人口生成参数，并响应生成事件。
（来源：结合 `UCustomizableObjectPopulation` 属性和 `Generator` 委托推断）

```cpp
// 动态调整人口属性权重（影响外观组合概率）
if (PopulationGenerator->Population)
{
    PopulationGenerator->Population->SetAttributeWeight(FName("Age"), 0.8f); // 增加“年龄”属性的影响权重
}

// 绑定生成完成委托
PopulationGenerator->OnPopulationGenerated.AddDynamic(this, &AMyGameMode::HandlePopulationGenerated);

// 在回调中处理生成的角色实例
void AMyGameMode::HandlePopulationGenerated(const TArray<UCustomizableObjectInstance*>& GeneratedInstances)
{
    for (UCustomizableObjectInstance* Instance : GeneratedInstances)
    {
        // 对每个生成的实例进行初始化，例如分配AI行为
        if (Instance)
        {
            // ...
        }
    }
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何在 GameMode 中集成人口生成。

**MyGameMode.h**
```cpp
#pragma once
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

class UCustomizableObjectPopulationGenerator;
class UCustomizableObjectInstance;

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void StartPlay() override;

private:
    UFUNCTION()
    void OnPopulationGenerated(const TArray<UCustomizableObjectInstance*>& Instances);

    UPROPERTY(Transient)
    TObjectPtr<UCustomizableObjectPopulationGenerator> PopulationGenerator;
};
```

**MyGameMode.cpp**
```cpp
#include "MyGameMode.h"
#include "CustomizableObjectPopulationGenerator.h"
#include "Engine/World.h"

void AMyGameMode::StartPlay()
{
    Super::StartPlay();

    // 动态生成人群生成器Actor
    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    PopulationGenerator = GetWorld()->SpawnActor<UCustomizableObjectPopulationGenerator>(SpawnParams);

    if (PopulationGenerator)
    {
        // 加载预定义的人口资产（假设已在编辑器中创建）
        static ConstructorHelpers::FObjectFinder<UCustomizableObjectPopulation> PopAssetFinder(TEXT("/Game/DA_Population"));
        if (PopAssetFinder.Succeeded())
        {
            PopulationGenerator->Population = PopAssetFinder.Object;
        }

        // 绑定委托
        PopulationGenerator->OnPopulationGenerated.AddDynamic(this, &AMyGameMode::OnPopulationGenerated);

        // 延迟一帧生成，确保游戏完全启动
        GetWorldTimerManager().SetTimerForNextTick([this]()
        {
            if (PopulationGenerator)
            {
                PopulationGenerator->GeneratePopulation();
            }
        });
    }
}

void AMyGameMode::OnPopulationGenerated(const TArray<UCustomizableObjectInstance*>& Instances)
{
    UE_LOG(LogTemp, Log, TEXT("Population generated with %d instances."), Instances.Num());
    // 在这里可以将生成的实例分配到场景中或进行其他初始化
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Mutable` | 核心依赖，提供底层的可定制化对象系统和实例化机制。 |
| `MessageLog` | 用于在编辑器或日志中输出人群生成相关的错误和警告信息。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-29 | `f35985aa` | Fix Customizable Object Editor viewport orbit/pan broken with new gizmos | 修复了使用新操作器（Gizmo）导致可定制化对象编辑器视口旋转/平移失效的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至 `UE_LOGF`。 |
| 2026-03-25 | `6dcf9bb4` | [Mutable] Fix CO Instances not updating. | [Mutable] 修复了可定制化对象实例（CO Instances）未能正确更新的问题。 |
| 2026-01-22 | `ad8a0de1` | Update BuildVersionSettings that are out of date | 更新了过时的 BuildVersionSettings。 |
| 2026-01-13 | `5e60b0a5` | [Mutable] Allow components having the same name. | [Mutable] 允许组件（Component）使用相同的名称。 |

### 维护评价

- **状态**：**实验性且持续维护中**。插件从 2024 年 9 月创建，至今不到两年，属于新插件。
- **更新频率**：从提交记录看，在 2026 年初至今有多次提交，表明仍在积极开发和修复问题。更新内容涉及底层编辑器集成、日志优化和核心逻辑修复。
- **实验性警告**：插件在 `.uplugin` 中明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`。这意味着其 API 可能不完整、不稳定或在未来版本中发生重大改变。**不建议在需要长期稳定性的生产项目中直接依赖它**。
- **推荐使用**：如果你正在探索基于 Mutable 系统构建大规模可定制人群的技术方案，并且能接受实验性 API 的风险，那么此插件是值得尝试的起点。否则，应谨慎评估或等待其正式发布。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutablePopulation)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/using-mutable-in-unreal-engine/) (Mutable 主插件文档，人群功能部分可能包含在内或尚无独立文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutablePopulation/Tests) (如果存在，通常位于插件目录的 `Tests` 子目录)