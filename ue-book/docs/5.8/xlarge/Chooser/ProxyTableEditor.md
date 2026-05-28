# Chooser

> Use Chooser and Proxy Tables to build dynamic asset selection logic.

| 属性 | 值 |
|---|---|
| 中文名 | 选择器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `Chooser` (Runtime), `ChooserEditor` (Runtime), `ChooserUncooked` (Runtime), `ProxyTable` (Runtime), `ProxyTableEditor` (Runtime), `ProxyTableUncooked` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-16 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser) | |

## 用途

Chooser 插件提供了一套用于构建动态资产选择逻辑的系统，主要包含两个核心概念：**Chooser Table** 和 **Proxy Table**。

1.  **Chooser Table（选择器表）**：这是一个数据驱动的决策表。开发者可以定义一系列条件（如：角色状态、游戏事件、动画状态等）和对应的结果（如：动画序列、材质、声音资产等）。当需要选择资产时，系统会根据当前的上下文条件查询 Chooser Table，返回最匹配的结果。
2.  **Proxy Table（代理表）**：它允许为一组实际资产（如 `UAnimSequence`、`USkeletalMesh`）创建一个抽象的“代理”资产（`UProxyAsset`）。其他系统（如动画蓝图）可以引用这个代理资产。在运行时，通过查询 Chooser Table 来决定代理资产最终指向哪个具体的资产。这实现了资产选择的完全解耦和动态替换。

**核心解决的问题**：避免在蓝图或代码中硬编码资产引用，使得资产选择逻辑可以在编辑器中通过表格可视化配置，并能在运行时根据游戏状态动态变化，极大地提高了动画、音频、视觉资产等系统的灵活性和可维护性。

## 使用场景

-   **动态动画选择**：根据角色的速度、方向、是否在空中等状态，从不同的动画序列中选择最合适的播放。
-   **装备/外观系统**：根据装备的等级、类型，动态替换角色的网格体、材质或特效。
-   **音频管理**：根据环境（室内/室外）、时间（白天/夜晚）或玩家状态（紧张/平静），动态选择背景音乐或音效。
-   **对话系统**：根据玩家选择和剧情分支，从一系列对话资产中动态选择。

## 蓝图用法

由于 Chooser 插件主要在编辑器中配置数据，运行时通过 C++ 逻辑驱动，其蓝图节点相对较少。主要的运行时交互通过 `UChooserTable` 和 `UProxyTable` 资产的查找函数进行。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find Proxy` | 根据上下文对象，查询 Proxy Table 并返回一个代理资产。 | `UProxyTable` |
| `Find Chooser Result` | 根据上下文和 Chooser Table，返回匹配的结果对象（通常是资产引用）。 | `UChooserTable` |

### 使用示例（蓝图描述）

1.  **配置代理表**：在内容浏览器中右键创建“Proxy Table”资产。打开编辑器，添加条目，为每个条目指定一个 `UProxyAsset` 和它默认关联的源资产（如 `UAnimSequence`）。
2.  **配置选择器表**：创建“Chooser Table”资产。在编辑器中，定义列作为条件（例如：`bIsInAir`，类型为 `Bool`）和结果列（例如：`Animation`，类型为 `AnimSequence`）。添加行，填写条件值和对应的资产引用。
3.  **在动画蓝图中使用**：
    -   获取一个 `UProxyAsset` 引用（通常来自 `ProxyTable` 的查找）。
    -   将此 `UProxyAsset` 设置到动画蓝图的插槽或变量中。
    -   在运行时，动画系统会自动通过 `ProxyTable` 和 `ChooserTable` 解析出实际要播放的动画序列。

## C++ 用法

### 头文件引入

```cpp
#include "Chooser.h"
#include "ProxyTable.h"
```

### 基本用法

从 Chooser 系统的核心接口出发，在 C++ 中查找代理结果。

```cpp
// 假设 UMyContext 是你自定义的上下文类，包含了用于查询的条件字段
UMyContext* Context = NewObject<UMyContext>();
Context->SetIsInAir(true);
Context->SetMovementSpeed(600.0f);

// 1. 通过 ProxyTable 查找代理资产
UProxyTable* ProxyTable = LoadObject<UProxyTable>(nullptr, TEXT("/Game/Animation/ProxyTable_Animations"));
UProxyAsset* FoundProxy = ProxyTable->FindProxy(Context);

// 2. 如果找到了代理，通常不需要直接使用它，而是将其传递给下游系统（如动画蓝图）
// 动画蓝图内部会再次使用 ChooserTable 来解析最终资产。
if (FoundProxy)
{
    UE_LOG(LogTemp, Log, TEXT("Found proxy asset: %s"), *FoundProxy->GetName());
}
```

### 进阶用法

直接与 `ChooserTable` 交互，获取最终的结果对象。这通常用于非动画的自定义资产选择逻辑。

```cpp
#include "ChooserTable.h"

// 加载选择器表
UChooserTable* ChooserTable = LoadObject<UChooserTable>(nullptr, TEXT("/Game/Data/ChooserTable_WeaponEffects"));

// 创建一个通用的上下文对象
UChooserEvaluationContext* EvalContext = NewObject<UChooserEvaluationContext>();
// 设置上下文字段，这些字段需要与 ChooserTable 中定义的列名匹配
EvalContext->SetPropertyByName(FName("WeaponType"), FGameplayTag::RequestGameplayTag("Weapon.Sword"));
EvalContext->SetPropertyByName(FName("HitMaterial"), FGameplayTag::RequestGameplayTag("Material.Metal"));

// 查询结果
UObject* ResultObject = ChooserTable->FindResult(EvalContext);

if (UParticleSystem* HitEffect = Cast<UParticleSystem>(ResultObject))
{
    // 使用找到的粒子特效
    UGameplayStatics::SpawnEmitterAtLocation(GetWorld(), HitEffect, HitLocation);
}
```

## Demo 示例

以下示例展示了如何创建一个简单的上下文类，并在游戏模式中查询 Chooser Table 来获取一个随机的问候语音效。

**MyGameContext.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/ObjectMacros.h"
#include "MyGameContext.generated.h"

UCLASS(BlueprintType)
class UMyGameContext : public UObject
{
    GENERATED_BODY()
public:
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "Context")
    bool bIsRaining = false;

    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "Context")
    int32 TimeOfDay = 12; // 0-23
};
```

**MyGameMode.cpp**
```cpp
#include "MyGameMode.h"
#include "ChooserTable.h"
#include "MyGameContext.h"

void AMyGameMode::StartPlay()
{
    Super::StartPlay();

    // 加载预配置的 ChooserTable
    UChooserTable* GreetingTable = LoadObject<UChooserTable>(nullptr, TEXT("/Game/Audio/ChooserTable_Greetings"));
    if (GreetingTable)
    {
        // 创建并填充上下文
        UMyGameContext* Context = NewObject<UMyGameContext>();
        Context->bIsRaining = true;
        Context->TimeOfDay = 18;

        // 查询结果
        UObject* Result = GreetingTable->FindResult(Context);
        if (USoundBase* GreetingSound = Cast<USoundBase>(Result))
        {
            UGameplayStatics::PlaySound2D(this, GreetingSound);
        }
    }
}
```

## 模块依赖

从模块名称推断，使用此插件通常不需要额外的模块依赖。插件本身封装了其核心逻辑。你的项目模块通常只需要依赖 `Engine` 模块即可与 `UChooserTable` 和 `UProxyTable` 资产交互。

| 模块 | 用途 |
|---|---|
| （无特殊依赖） | 使用标准的 Core/Engine 即可访问插件暴露的资产类和运行时功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `aad6fe75` | Remove build setting making chooser internal headers public, and move most of those internal headers | 重构模块，将内部头文件移出公共范围，增强封装性。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量到单精度的转换警告。 |
| 2026-05-12 | `333cccbc` | Add profiling tag to chooser property access | 为 Chooser 的属性访问添加性能分析标记，便于优化。 |
| 2026-04-17 | `1eda8a87` | Fix chooser editor null pointer crash after native context type rename | 修复编辑器在重命名原生上下文类型后可能出现的空指针崩溃。 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 配合内容浏览器的新增菜单调整。 |

### 维护评价

Chooser 是一个相对较新的插件（约 2 年），自 2024 年 9 月从实验文件夹移出后，一直处于**活跃维护**状态。从近期（2026年5月）的提交记录可以看出，开发团队仍在进行代码质量改进（重构头文件、修复警告）、性能优化（添加 Profiling 标记）和缺陷修复（编辑器崩溃）。这表明该插件是 Epic 正在积极开发和维护的核心动画工具链的一部分。

**推荐使用**：如果你的项目有复杂的动态资产选择需求（尤其是动画系统），Choosor 提供了一套强大且数据驱动的解决方案。尽管它默认未启用，但其设计成熟，与 UE 的编辑器集成良好，且维护活跃，值得投入学习并应用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser)
-   官方文档（暂无）
-   测试用例（未在本次分析范围内）