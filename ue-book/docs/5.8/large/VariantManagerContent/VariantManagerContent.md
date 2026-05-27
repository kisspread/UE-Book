# Variant Manager Content

> Data classes and assets for the Variant Manager plugin

| 属性 | 值 |
|---|---|
| 中文名 | 变体管理器内容 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `VariantManagerContent` (Runtime), `VariantManagerContentEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-09-04 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent) | |

## 用途

Variant Manager Content 插件为 UE5 的 Variant Manager（变体管理器）系统提供底层的数据结构和运行时支持。它并非直接面向用户的编辑器工具，而是 Variant Manager 功能的**核心数据层**，负责存储、管理和应用“变体”相关的所有数据。

其核心解决的问题是：如何高效、灵活地管理一个 Actor（或对象）在不同“状态”（变体）下的属性集合。例如，一个展示汽车的项目，可以将“车门关闭”、“车门打开”、“引擎盖打开”等分别定义为不同的变体，每个变体捕获并存储了车门、引擎盖等部件的旋转、位置、材质等属性值。当用户切换变体时，系统能快速将这些预存的属性值应用到对应的物体上，实现状态切换。

## 使用场景

- **产品配置器**：如汽车、家具、家电的在线定制，用户选择不同配置（颜色、材质、部件组合）时实时更新 3D 模型。
- **建筑可视化（ArchViz）**：切换室内的日/夜光照、家具布局、材质风格等不同场景状态。
- **工业仿真与培训**：模拟设备的不同操作状态（如阀门开/关、仪表盘指示灯变化）。
- **交互式叙事或游戏**：管理场景中物体的关键状态变化，如解谜后场景元素的变化。

## 蓝图用法

本插件的核心数据类（如 `ULevelVariantSets`, `UVariant`, `UVariantSet`）均为蓝图类型，提供了丰富的蓝图可用接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLevelVariantSets` | 获取关卡变体集资产（可选择是否加载） | `ALevelVariantSetsActor` |
| `SwitchOnVariantByName` | 通过变体集名称和变体名称激活指定变体 | `ALevelVariantSetsActor` |
| `SwitchOnVariantByIndex` | 通过索引激活指定变体 | `ALevelVariantSetsActor` |
| `SwitchOn` | 激活此变体，将其捕获的属性应用到关联对象 | `UVariant` |
| `IsActive` | 检查此变体是否处于激活状态（其属性值未被修改） | `UVariant` |
| `GetNumActors` | 获取此变体关联的 Actor 数量 | `UVariant` |
| `GetActor` | 通过索引获取此变体关联的 Actor | `UVariant` |
| `GetDisplayText` / `SetDisplayText` | 获取/设置变体或变体集的显示名称 | `UVariant`, `UVariantSet` |
| `SetThumbnailFromFile` | 从文件路径设置变体或变体集的缩略图 | `UVariant`, `UVariantSet` |
| `GetVariantSetByName` | 从关卡变体集中按名称查找变体集 | `ULevelVariantSets` |
| `GetVariantByName` | 从变体集中按名称查找变体 | `UVariantSet` |
| `SelectOption` | 用于 `ASwitchActor`，切换其子 Actor 的可见性 | `ASwitchActor` |

### 使用示例（蓝图描述）

1.  **创建与切换变体**：
    - 在蓝图中，首先获取 `ALevelVariantSetsActor` 的引用。
    - 使用 `GetLevelVariantSets` 节点加载或获取其关联的 `ULevelVariantSets` 数据资产。
    - 通过 `GetVariantSet` 和 `GetVariant` 节点定位到具体的变体。
    - 最终调用 `SwitchOn` 节点应用该变体，或通过 `ALevelVariantSetsActor` 的 `SwitchOnVariantByName` 一步到位。

2.  **使用 SwitchActor**：
    - 将 `ASwitchActor` 放置在场景中，并将其子 Actor 设置为互斥的显示状态。
    - 在蓝图中，获取该 `ASwitchActor` 引用，调用 `GetOptions` 获取所有可选子 Actor。
    - 调用 `SelectOption` 并传入索引，即可切换当前显示的子 Actor。

## C++ 用法

在 C++ 中，可以通过 `#include` 相应的头文件来使用这些数据类，构建、查询和操作变体数据。

### 头文件引入

```cpp
#include "LevelVariantSets.h"
#include "Variant.h"
#include "VariantSet.h"
#include "VariantObjectBinding.h"
#include "PropertyValue.h"
#include "LevelVariantSetsActor.h"
#include "SwitchActor.h"
```

### 基本用法

**1. 遍历变体数据结构**

以下代码展示了如何从 `ALevelVariantSetsActor` 开始，遍历其关联的所有变体集和变体，并打印名称。

```cpp
// 来源：概念示例，基于 LevelVariantSets.h 和 Variant.h 的 API
void PrintAllVariants(ALevelVariantSetsActor* Actor)
{
    if (!Actor) return;

    // 获取并可能加载 LevelVariantSets 数据资产
    ULevelVariantSets* LevelVariantSets = Actor->GetLevelVariantSets(true);
    if (!LevelVariantSets) return;

    for (int32 i = 0; i < LevelVariantSets->GetNumVariantSets(); ++i)
    {
        UVariantSet* VarSet = LevelVariantSets->GetVariantSet(i);
        if (!VarSet) continue;

        UE_LOG(LogTemp, Log, TEXT("VariantSet: %s"), *VarSet->GetDisplayText().ToString());

        for (int32 j = 0; j < VarSet->GetNumVariants(); ++j)
        {
            UVariant* Var = VarSet->GetVariant(j);
            if (Var)
            {
                UE_LOG(LogTemp, Log, TEXT("  - Variant: %s (Actors: %d)"), *Var->GetDisplayText().ToString(), Var->GetNumActors());
            }
        }
    }
}
```

**2. 编程式激活变体**

```cpp
// 来源：概念示例，基于 Variant.h 的 API
void ActivateSpecificVariant(ALevelVariantSetsActor* Actor)
{
    if (!Actor) return;

    // 尝试激活名为 “HighDetail” 的变体集中的 “Day” 变体
    bool bSuccess = Actor->SwitchOnVariantByName(TEXT("HighDetail"), TEXT("Day"));
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully activated variant ‘Day’ in ‘HighDetail’ set."));
    }
}
```

### 进阶用法

**1. 监听变体激活事件**

`UVariant` 提供了 `OnThumbnailUpdated` 和 `OnDependenciesUpdated` 静态委托，可用于在蓝图或 C++ 中监听变体的变化。

```cpp
// 来源：概念示例，基于 Variant.h 中声明的委托
#include "Variant.h"

void SetupVariantDelegate()
{
    UVariant::OnThumbnailUpdated.AddLambda([](UVariant* ChangedVariant)
    {
        if (ChangedVariant)
        {
            UE_LOG(LogTemp, Log, TEXT("Thumbnail updated for variant: %s"), *ChangedVariant->GetDisplayText().ToString());
        }
    });
}
```

**2. 使用 SwitchActor**

```cpp
// 来源：概念示例，基于 SwitchActor.h 的 API
#include "SwitchActor.h"

void CycleSwitchActorOptions(ASwitchActor* SwitchActor)
{
    if (!SwitchActor) return;

    TArray<AActor*> Options = SwitchActor->GetOptions();
    if (Options.Num() == 0) return;

    int32 CurrentIndex = SwitchActor->GetSelectedOption();
    int32 NextIndex = (CurrentIndex + 1) % Options.Num();

    SwitchActor->SelectOption(NextIndex);
    UE_LOG(LogTemp, Log, TEXT("Switched to option index: %d"), NextIndex);
}
```

## Demo 示例

以下是一个最小的 C++ 类，用于在运行时监听并响应变体缩略图的更新。

**MyVariantListener.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "Variant.h" // 依赖 VariantManagerContent 模块
#include "MyVariantListener.generated.h"

UCLASS()
class UMyVariantListener : public UObject
{
    GENERATED_BODY()

public:
    void Initialize();
    void Deinitialize();

private:
    FDelegateHandle OnThumbnailUpdatedHandle;

    void HandleVariantThumbnailUpdated(UVariant* ChangedVariant);
};
```

**MyVariantListener.cpp**
```cpp
#include "MyVariantListener.h"
#include "Variant.h"

void UMyVariantListener::Initialize()
{
    OnThumbnailUpdatedHandle = UVariant::OnThumbnailUpdated.AddUObject(this, &UMyVariantListener::HandleVariantThumbnailUpdated);
}

void UMyVariantListener::Deinitialize()
{
    if (OnThumbnailUpdatedHandle.IsValid())
    {
        UVariant::OnThumbnailUpdated.Remove(OnThumbnailUpdatedHandle);
        OnThumbnailUpdatedHandle.Reset();
    }
}

void UMyVariantListener::HandleVariantThumbnailUpdated(UVariant* ChangedVariant)
{
    if (ChangedVariant)
    {
        // 执行自定义逻辑，例如更新UI或记录日志
        UE_LOG(LogTemp, Warning, TEXT("监听到变体缩略图更新: %s"), *ChangedVariant->GetDisplayText().ToString());
    }
}
```

## 模块依赖

要使用本插件提供的数据类型（如 `UVariant`, `ULevelVariantSets`），你的模块需要在 `.Build.cs` 文件中添加对 `VariantManagerContent` 运行时模块的依赖。编辑器功能（如某些编译器相关类）则需要依赖 `VariantManagerContentEditor`。

| 模块 | 用途 |
|---|---|
| `VariantManagerContent` | 提供变体系统的核心数据结构（运行时必需） |
| `VariantManagerContentEditor` | 提供编辑器专用的功能，如函数调用缓存、蓝图节点绑定等（仅编辑器） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `0a77223b` | Fixed crash in LevelVariantSet.cpp | 修复了 LevelVariantSet.cpp 中的一个崩溃问题 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 配合内容浏览器的新建菜单数据结构更新 |
| 2026-04-14 | `50042443` | TLazyObjectPtr Deprecation: | 响应引擎对 TLazyObjectPtr 的弃用，进行了相关迁移或适配 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF 宏 |
| 2026-03-20 | `c5bb9adf` | [AutoViz] Minor updates to Variant Manager | 对变体管理器进行了小的功能更新 |

### 维护评价

- **活跃维护**：尽管插件创建于2018年，属于“老古董”级别，但从近期的 git 记录来看，其仍被**活跃维护**。最近的提交集中在**修复崩溃、适配引擎API变更（如 TLazyObjectPtr 弃用、日志宏迁移）** 以及**跟随相关插件（如 ContentBrowser）的更新**。这表明 Epic Games 在持续确保其与最新引擎版本的兼容性和稳定性。
- **实验性标签**：`.uplugin` 中标记为 `IsBetaVersion: true`，说明 Epic 可能仍在对其功能或 API 进行迭代和稳定化，未来可能有变动。使用时应关注引擎更新日志。
- **推荐**：作为 Variant Manager 系统的基石，如果项目需要使用变体管理器功能，此插件是**必需且推荐使用的**。它提供了稳定可靠的数据层支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/) (链接指向Datasmith，可能与该插件通用的企业功能文档相关)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent/Tests) (根据目录惯例推断)