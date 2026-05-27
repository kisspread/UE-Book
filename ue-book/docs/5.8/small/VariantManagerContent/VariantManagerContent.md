# Variant Manager Content

> Data classes and assets for the Variant Manager plugin

| 属性 | 值 |
|---|---|
| 中文名 | 变体管理数据 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `VariantManagerContent` (Runtime), `VariantManagerContentEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-09-04 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent) | |

## 用途

VariantManagerContent 为 **Variant Manager（变体管理器）** 提供底层数据类和运行时支持。它不是一个独立的编辑器工具，而是 Variant Manager 编辑器插件所依赖的数据层。

这个插件解决的核心问题是：**如何在运行时高效地切换场景中大量对象的属性状态**。它建立了一套完整的数据模型来存储"变体"——即一组对象属性的快照，可以在运行时一键切换。

**典型应用场景**：建筑可视化中，客户想在同一个场景里切换不同的地板材质、家具布局、灯光方案。Variant Manager 让你预先录制这些状态变体，运行时通过一行蓝图代码即可切换整套配置。

## 使用场景

- **建筑/产品可视化（AEC / Product Viz）**：需要在运行时切换产品的颜色、材质、配件组合
- **Datasmith 工作流**：从 CAD/BIM 软件导入的模型需要展示多种配置方案
- **交互式演示**：在 VR/实时演示中让客户自己选择不同的设计方案
- **场景快速切装**：同一场景需要展示多种状态（如不同时间段的灯光氛围）
- **ASwitchActor 特殊用途**：快速切换子 Actor 的可见性，一次只显示一个选项

## 蓝图用法

本插件提供大量 `BlueprintCallable` 和 `BlueprintPure` 函数，核心 API 按数据层级组织。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SwitchOnVariantByName` | 通过名称切换到指定变体 | `ALevelVariantSetsActor` |
| `SwitchOnVariantByIndex` | 通过索引切换到指定变体 | `ALevelVariantSetsActor` |
| `GetLevelVariantSets` | 获取关联的 LevelVariantSets 资产 | `ALevelVariantSetsActor` |
| `SetLevelVariantSets` | 设置关联的 LevelVariantSets 资产 | `ALevelVariantSetsActor` |
| `GetNumVariantSets` | 获取变体集数量 | `ULevelVariantSets` |
| `GetVariantSet` | 按索引获取变体集 | `ULevelVariantSets` |
| `GetVariantSetByName` | 按名称获取变体集 | `ULevelVariantSets` |
| `SwitchOn` | 应用当前变体（激活所有绑定的属性和函数） | `UVariant` |
| `IsActive` | 检查变体当前是否处于激活状态 | `UVariant` |
| `GetNumActors` | 获取变体绑定的 Actor 数量 | `UVariant` |
| `GetActor` | 获取变体绑定的第 N 个 Actor | `UVariant` |
| `SetDisplayText` | 设置变体的显示名称 | `UVariant` |
| `GetDisplayText` | 获取变体的显示名称 | `UVariant` |
| `AddDependency` | 添加变体依赖 | `UVariant` |
| `GetNumDependencies` | 获取依赖数量 | `UVariant` |
| `GetOptions` | 获取 SwitchActor 的所有子选项 | `ASwitchActor` |
| `SelectOption` | 选择 SwitchActor 的某个选项 | `ASwitchActor` |
| `GetSelectedOption` | 获取 SwitchActor 当前选中的选项索引 | `ASwitchActor` |
| `GetPropertyTooltip` | 获取属性的提示文本 | `UPropertyValue` |
| `GetFullDisplayString` | 获取属性的完整显示字符串 | `UPropertyValue` |
| `HasRecordedData` | 检查属性是否已录制数据 | `UPropertyValue` |
| `SetThumbnailFromTexture` | 从纹理设置缩略图 | `UVariant` / `UVariantSet` |
| `SetThumbnailFromFile` | 从文件路径设置缩略图 | `UVariant` / `UVariantSet` |
| `SetThumbnailFromCamera` | 从指定相机位置渲染缩略图 | `UVariant` / `UVariantSet` |
| `SetThumbnailFromEditorViewport` | 从当前编辑器视口设置缩略图 | `UVariant` / `UVariantSet` |

### 使用示例（蓝图描述）

**运行时切换变体**：

1. 在场景中放置 `ALevelVariantSetsActor`（通常是 Variant Manager 编辑器自动生成的）
2. 蓝图中获取该 Actor 引用
3. 调用 `SwitchOnVariantByName`，传入变体集名称（如 "FloorMaterial"）和变体名称（如 "Marble"）
4. 场景中所有绑定的 Actor 的属性会自动切换到录制的状态

**程序化创建变体数据**：

1. 创建 `ULevelVariantSets` 资产
2. 使用 `AddVariantSets` 添加变体集
3. 在变体集上 `AddVariants` 添加变体
4. 对变体调用 `AddBindings` 添加对象绑定
5. 在绑定上 `AddCapturedProperties` 添加属性捕获
6. 调用 `RecordDataFromResolvedObject` 录制当前状态
7. 之后通过 `SwitchOn` 恢复到录制的状态

**ASwitchActor 用法**：

1. 在场景中放置 `ASwitchActor`
2. 将多个 Actor（如不同款式的椅子）拖入其子层级
3. 通过 `SelectOption(2)` 切换显示第三个子 Actor，其他自动隐藏
4. 该操作可被 Variant Manager 捕获为属性变体

## C++ 用法

### 头文件引入

```cpp
#include "LevelVariantSets.h"
#include "VariantSet.h"
#include "Variant.h"
#include "VariantObjectBinding.h"
#include "PropertyValue.h"
#include "SwitchActor.h"
#include "LevelVariantSetsActor.h"
```

### 基本用法

以下是通过 C++ 代码操作变体系统的基本示例，展示了数据模型的层级关系：

```cpp
// 场景中已放置的 LevelVariantSetsActor
ALevelVariantSetsActor* Actor = GetLevelVariantSetsActor();
ULevelVariantSets* LevelVariantSets = Actor->GetLevelVariantSets(true);

// 获取变体集
UVariantSet* VarSet = LevelVariantSets->GetVariantSet(0);
FText VarSetName = VarSet->GetDisplayText();

// 获取变体
UVariant* Variant = VarSet->GetVariant(0);
FText VariantName = Variant->GetDisplayText();

// 检查变体是否激活
bool bActive = Variant->IsActive();

// 切换变体
Variant->SwitchOn();

// 获取变体绑定的 Actor
int32 NumActors = Variant->GetNumActors();
AActor* BoundActor = Variant->GetActor(0);
```

### 进阶用法

以下示例展示了如何遍历变体绑定的属性数据，以及如何使用 ASwitchActor：

```cpp
// 遍历变体的所有绑定和属性
UVariant* Variant = GetSomeVariant();
for (UVariantObjectBinding* Binding : Variant->GetBindings())
{
    UObject* BoundObject = Binding->GetObject();
    UE_LOG(LogTemp, Log, TEXT("Binding to: %s"), *Binding->GetDisplayText().ToString());

    // 遍历捕获的属性
    for (UPropertyValue* PropValue : Binding->GetCapturedProperties())
    {
        if (PropValue->HasRecordedData())
        {
            FText Tooltip = PropValue->GetPropertyTooltip();
            const FString& DisplayStr = PropValue->GetFullDisplayString();
            EPropertyValueCategory Category = PropValue->GetPropCategory();
        }
    }

    // 执行绑定对象上的函数调用
    Binding->ExecuteAllTargetFunctions();
}

// 变体依赖：获取依赖该变体的其他变体
ULevelVariantSets* LVS = GetLevelVariantSets();
TArray<UVariant*> Dependents = Variant->GetDependents(LVS, true /*bOnlyEnabledDependencies*/);

// ASwitchActor 用法
ASwitchActor* Switch = GetSwitchActor();
TArray<AActor*> Options = Switch->GetOptions();
int32 CurrentSelection = Switch->GetSelectedOption();
Switch->SelectOption(1); // 切换到第二个选项

// 监听切换事件
Switch->GetOnSwitchDelegate().AddLambda([](int32 NewOption) {
    UE_LOG(LogTemp, Log, TEXT("SwitchActor selected option: %d"), NewOption);
});
```

## Demo 示例

一个完整的最小示例，展示如何通过 C++ 代码与 Variant Manager 数据层交互：

```cpp
// MyVariantManagerHelper.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "LevelVariantSetsActor.h"
#include "LevelVariantSets.h"
#include "VariantSet.h"
#include "Variant.h"
#include "VariantObjectBinding.h"
#include "PropertyValue.h"
#include "SwitchActor.h"

#include "MyVariantManagerHelper.generated.h"

UCLASS(BlueprintType)
class MYPROJECT_API UMyVariantManagerHelper : public UObject
{
    GENERATED_BODY()

public:
    // 根据名称切换变体
    UFUNCTION(BlueprintCallable, Category = "VariantManager|Helper")
    static bool SwitchVariantByName(ALevelVariantSetsActor* Actor,
                                     const FString& VariantSetName,
                                     const FString& VariantName);

    // 列出所有可用的变体集和变体
    UFUNCTION(BlueprintCallable, Category = "VariantManager|Helper")
    static TArray<FString> ListAllVariants(ALevelVariantSetsActor* Actor);

    // 检查变体是否为当前激活状态
    UFUNCTION(BlueprintCallable, Category = "VariantManager|Helper")
    static bool IsVariantActive(ALevelVariantSetsActor* Actor,
                                 const FString& VariantSetName,
                                 const FString& VariantName);
};
```

```cpp
// MyVariantManagerHelper.cpp
#include "MyVariantManagerHelper.h"

bool UMyVariantManagerHelper::SwitchVariantByName(ALevelVariantSetsActor* Actor,
                                                    const FString& VariantSetName,
                                                    const FString& VariantName)
{
    if (!Actor)
    {
        return false;
    }
    return Actor->SwitchOnVariantByName(VariantSetName, VariantName);
}

TArray<FString> UMyVariantManagerHelper::ListAllVariants(ALevelVariantSetsActor* Actor)
{
    TArray<FString> Results;
    if (!Actor) return Results;

    ULevelVariantSets* LVS = Actor->GetLevelVariantSets(true);
    if (!LVS) return Results;

    for (int32 i = 0; i < LVS->GetNumVariantSets(); ++i)
    {
        UVariantSet* VarSet = LVS->GetVariantSet(i);
        if (!VarSet) continue;

        FString SetName = VarSet->GetDisplayText().ToString();
        for (int32 j = 0; j < VarSet->GetNumVariants(); ++j)
        {
            UVariant* Var = VarSet->GetVariant(j);
            if (Var)
            {
                Results.Add(FString::Printf(TEXT("%s / %s"),
                    *SetName, *Var->GetDisplayText().ToString()));
            }
        }
    }
    return Results;
}

bool UMyVariantManagerHelper::IsVariantActive(ALevelVariantSetsActor* Actor,
                                               const FString& VariantSetName,
                                               const FString& VariantName)
{
    if (!Actor) return false;

    ULevelVariantSets* LVS = Actor->GetLevelVariantSets(true);
    if (!LVS) return false;

    UVariantSet* VarSet = LVS->GetVariantSetByName(VariantSetName);
    if (!VarSet) return false;

    UVariant* Var = VarSet->GetVariantByName(VariantName);
    if (!Var) return false;

    return Var->IsActive();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RenderCore` | 纹理生成相关（缩略图创建） |
| `RenderCore` | 纹理创建 |
| `LevelSequence` | 可能用于与 Sequencer 集成 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等常见模块）。实际上该插件的核心运行时模块依赖非常轻量，主要依赖引擎的基础模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `0a77223b` | Fixed crash in LevelVariantSet.cpp | 修复 LevelVariantSet 的崩溃问题 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 内容浏览器新增添加菜单数据 |
| 2026-04-14 | `50042443` | TLazyObjectPtr Deprecation: | 迁移废弃的 TLazyObjectPtr 到新 API |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至新格式 UE_LOGF |
| 2026-03-20 | `c5bb9adf` | [AutoViz] Minor updates to Variant Manager | 变体管理器的小幅更新 |

### 维护评价

- **创建时间**：2018 年，至今约 8 年，属于企业级长期支持功能
- **最近更新频率**：2026 年有多次实质性更新（修复崩溃、API 迁移），说明仍在活跃维护
- **维护状态**：**活跃维护中** — 近期有 bug 修复和 API 现代化工作
- **Beta 标记**：`IsBetaVersion=true` 仍处于实验阶段，API 可能变化
- **已知限制**：
  - 仍标记为 Beta，部分 API 可能不稳定
  - 旧版使用 `TLazyObjectPtr`，正在迁移到 `FSoftObjectPath`，读取旧资产时需注意兼容性
  - 缩略图相关功能仅在编辑器环境完整可用（`SetThumbnailFromEditorViewport` 标记了 `CallInEditor`）
- **推荐使用**：✅ 推荐用于建筑/产品可视化场景。这是 Epic 官方的 Enterprise 变体管理方案，虽然标记 Beta 但已持续维护 8 年，可靠性较高。如果你需要在运行时切换复杂场景配置，这是官方唯一方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)