# Variant Manager Content

> Data classes and assets for the Variant Manager plugin（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 变体管理器数据 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `VariantManagerContent` (Runtime), `VariantManagerContentEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-09-04 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent) | |

## 用途

本插件为 **Variant Manager** 编辑器插件提供了底层的**数据类**和**资产管理**框架。它本身不是直接操作的编辑器界面，而是存储和管理“变体”数据的核心。Variant Manager 允许设计师和可视化专家创建、组织和快速切换同一场景或产品的不同配置状态，例如汽车的不同内饰方案、建筑的不同灯光场景、或产品展示中的不同组件组合。这些配置状态（变体）被序列化为资产（`ULevelVariantSets`），并可在运行时通过蓝图或 C++ 控制加载和切换。

## 使用场景

- **产品配置器**：在汽车销售、家具展示等应用中，用户通过点击按钮切换材质、颜色、部件等组合。
- **建筑可视化（ArchViz）**：一键切换白天/夜晚场景、不同家具布局、或不同的装修风格。
- **虚拟样机/设计评审**：在设计评审中，快速展示产品的不同设计方案或视角。
- **交互式演示**：在路演或展览中，通过预定义的变体序列引导观众体验产品的不同功能。

## 蓝图用法

蓝图功能主要集中在 `ALevelVariantSetsActor`、`ULevelVariantSets`、`UVariantSet` 和 `UVariant` 类上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SwitchOnVariantByName` | 通过变体集和变体名称激活特定的变体配置。 | `ALevelVariantSetsActor` |
| `SwitchOnVariantByIndex` | 通过索引激活变体。 | `ALevelVariantSetsActor` |
| `GetLevelVariantSets` | 获取或加载关联的 Level Variant Sets 资产。 | `ALevelVariantSetsActor` |
| `GetVariantSetByName` | 根据名称获取变体集。 | `ULevelVariantSets` |
| `GetVariant` | 根据索引获取变体集中的特定变体。 | `UVariantSet` |
| `SwitchOn` | 激活此变体，将其关联对象的所有捕获属性设置为记录值。 | `UVariant` |
| `IsActive` | 检查此变体是否处于激活状态（所有属性值与记录值一致）。 | `UVariant` |
| `SetThumbnailFromEditorViewport` | 从当前编辑器视口设置变体的缩略图。 | `UVariant` |

### 使用示例（蓝图描述）

1.  **在场景中放置 Actor**：从内容浏览器将 `LevelVariantSets` 资产拖入场景，或手动放置一个 `ALevelVariantSetsActor` 并指定资产。
2.  **获取并激活变体**：
    - 使用 `Get Level Variant Sets` 节点获取资产引用。
    - 连接到 `Get Variant Set by Name` 或 `Get Variant Set` 节点，通过名称或索引获取一个 `UVariantSet`。
    - 连接到 `Get Variant` 节点，通过索引获取一个 `UVariant`。
    - 最后调用 `Switch On` 节点激活该变体。
3.  **直接通过 Actor 激活**：更简单的方式是直接在 `ALevelVariantSetsActor` 上调用 `Switch On Variant by Name`，传入变体集和变体的名称字符串。

## C++ 用法

### 头文件引入

```cpp
#include "LevelVariantSets.h"
#include "VariantSet.h"
#include "Variant.h"
#include "VariantObjectBinding.h"
#include "PropertyValue.h"
```

### 基本用法

**创建和配置 LevelVariantSets 资产**
此示例展示了如何通过 C++ 动态构建一个变体资产。注意：在实际项目中，这些资产通常通过 Variant Manager 编辑器创建和序列化。
（来源：概念推断，编辑器交互代码通常在 `VariantManagerContentEditor` 模块）

```cpp
// 假设我们已经有了一个运行时世界上下文
UWorld* World = GetWorld();

// 创建一个新的 LevelVariantSets 资产 (通常在编辑器模块中完成)
ULevelVariantSets* LevelVariantSets = NewObject<ULevelVariantSets>(GetTransientPackage(), FName("MyLVS"));

// 创建并添加一个变体集
UVariantSet* CarInteriorVariantSet = NewObject<UVariantSet>(LevelVariantSets);
CarInteriorVariantSet->SetDisplayText(FText::FromString(TEXT("内饰方案")));
LevelVariantSets->AddVariantSets({CarInteriorVariantSet});

// 在变体集中创建一个变体
UVariant* LeatherVariant = NewObject<UVariant>(CarInteriorVariantSet);
LeatherVariant->SetDisplayText(FText::FromString(TEXT("皮革内饰")));
CarInteriorVariantSet->AddVariants({LeatherVariant});

// 为变体捕获属性（在编辑器中通过GUI完成，C++中需要手动解析属性路径并构建FCapturedPropSegment数组，较为复杂）
// 此处省略具体的属性捕获过程，通常涉及 UPropertyValue::Init
```

**运行时激活变体**
一旦资产准备就绪并放置在场景中（通过 `ALevelVariantSetsActor`），可以在运行时切换。
（来源：`ALevelVariantSetsActor::SwitchOnVariantByName` 实现）

```cpp
// 获取场景中的 LevelVariantSetsActor
ALevelVariantSetsActor* LVSActor = /* ... */;
if (LVSActor)
{
    // 通过名称激活变体
    LVSActor->SwitchOnVariantByName(TEXT("内饰方案"), TEXT("皮革内饰"));
}
```

### 进阶用法

**监听变体切换事件**
你可以绑定到变体切换事件来执行自定义逻辑。
（来源：`UVariant` 和 `ASwitchActor` 中定义的委托）

```cpp
// 假设我们有一个指向特定变体的指针
UVariant* MyVariant = /* ... */;

// 绑定到属性应用后的事件 (通常在 VariantManager 模块中定义)
MyVariant->GetOnPropertyApplied().AddLambda([](UPropertyValue* PropertyValue)
{
    UE_LOG(LogTemp, Log, TEXT("Property '%s' was applied"), *PropertyValue->GetFullDisplayString());
});

// 对于 SwitchActor，还可以监听切换事件
ASwitchActor* SwitchActor = /* ... */;
SwitchActor->GetOnSwitchDelegate().AddLambda([](int32 NewSelectedOption)
{
    UE_LOG(LogTemp, Log, TEXT("Switch Actor selected option index: %d"), NewSelectedOption);
});
```

## Demo 示例

一个最小的 C++ 示例，展示如何在 BeginPlay 时通过已有的 Actor 切换变体。

**MyGameMode.h**
```cpp
#pragma once
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

class ALevelVariantSetsActor;

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category="Demo")
    ALevelVariantSetsActor* TargetLVSActor;

    UPROPERTY(EditAnywhere, Category="Demo")
    FString VariantSetName = TEXT("DefaultSet");

    UPROPERTY(EditAnywhere, Category="Demo")
    FString VariantName = TEXT("VariantA");
};
```

**MyGameMode.cpp**
```cpp
#include "MyGameMode.h"
#include "LevelVariantSetsActor.h"

void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    if (TargetLVSActor)
    {
        bool bSuccess = TargetLVSActor->SwitchOnVariantByName(VariantSetName, VariantName);
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("Successfully switched to variant '%s' in set '%s'"), *VariantName, *VariantSetName);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Failed to switch variant. VariantSet '%s' or Variant '%s' not found."), *VariantSetName, *VariantName);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VariantManager` | 核心的 Variant Manager 编辑器模块，提供交互式 UI 和资产创建逻辑。 |
| `LevelSequence` | 用于处理变体切换时可能涉及的动画序列（如摄像机动画）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `0a77223b` | Fixed crash in LevelVariantSet.cpp | 修复了 LevelVariantSet.cpp 中的一个崩溃问题。 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 内容浏览器新增数据菜单，可能影响资产创建流程。 |
| 2026-04-14 | `50042443` | TLazyObjectPtr Deprecation: | 处理了 TLazyObjectPtr 的弃用警告，更新了相关序列化代码。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，统一日志格式。 |
| 2026-03-20 | `c5bb9adf` | [AutoViz] Minor updates to Variant Manager | 对变体管理器进行了小规模更新，推测为自动化可视化功能适配。 |

### 维护评价

- **活跃维护**：虽然插件创建于 2018 年，但截至 2026 年 5 月仍有实质性更新（包括崩溃修复和功能适配），表明它仍被 Epic Games 用于内部的企业级项目（如 AutoViz），并持续维护。
- **实验性状态**：`.uplugin` 标记为 `IsBetaVersion: true`，这意味着其 API 可能仍会发生变化，不建议在需要高度稳定性的生产项目中直接依赖其内部实现细节。
- **推荐使用**：对于需要复杂产品配置、建筑可视化或交互式演示的项目，**推荐使用** Variant Manager 系统。它提供了成熟的蓝图接口，足以应对大多数运行时切换场景。但需要注意其“实验性”标签，并关注官方更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent/Tests) （注意：测试用例可能位于 Editor 模块或独立测试目录）