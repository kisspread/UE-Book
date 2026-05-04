# Material Validation

> Additional validation options for materials.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MaterialValidation` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/MaterialValidation) | |

## 用途

Material Validation 插件旨在通过验证材质实例的属性来限制“静态排列”（Static Permutations）的数量。过多的静态排列会导致着色器数量爆炸式增长，严重影响游戏性能和打包大小。该插件通过以下方式解决此问题：

1.  **定义“材质验证组”**：允许用户将一组材质资产（UMaterial）及其所有子实例（UMaterialInstance）归为一个组进行管理。
2.  **记录与验证排列**：记录每个材质层级中所有已批准的排列组合（基于静态属性、用法标志、静态开关等）。当用户创建或修改材质实例时，验证器会检查其是否引入了新的、未批准的排列。
3.  **提供管理工具**：提供命令行工具（Commandlet）和编辑器内工具来更新、同步和分析材质组中的排列数据。
4.  **相似性浏览器**：当验证失败时，提供一个浏览器，帮助用户在已批准的排列中查找与当前实例最相似的材质实例，以便复用或参考。

## 使用场景

-   你的项目拥有大量材质实例，且美术人员频繁创建新实例，需要控制材质复杂度以避免着色器编译时间和内存占用失控。
-   你需要在资产提交（Check-in）前自动验证材质变更，确保不会意外引入新的、昂贵的材质排列。
-   你希望在编辑材质实例时，能快速找到已存在的、属性相似的实例，以避免重复工作或创建不必要的排列。

## 蓝图用法

蓝图功能主要通过 `UMaterialValidationLibrary` 暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get All Groups` | 获取所有已配置的材质验证组。 | `UMaterialValidationLibrary` |
| `Reset Group` | 清空指定材质验证组中的所有材质。 | `UMaterialValidationLibrary` |
| `Add Missing Materials to Group` | 将材质搜索路径下找到的所有新材质添加到指定组中。 | `UMaterialValidationLibrary` |
| `Remove Invalid Materials from Group` | 从指定组中移除所有在磁盘上已不存在的材质。 | `UMaterialValidationLibrary` |
| `Update Material Permutations in Group` | 重新计算并更新指定组中所有材质的排列信息。 | `UMaterialValidationLibrary` |
| `Get Material Paths` | 获取指定材质验证组中所有材质的软引用路径。 | `UMaterialValidationGroup` |
| `Update Materials` | (CallInEditor) 更新材质验证组中的材质列表。 | `UMaterialValidationGroup` |
| `Update Material Permutations` | (CallInEditor) 更新材质验证组中所有材质的排列信息。 | `UMaterialValidationGroup` |

### 使用示例（蓝图描述）

1.  **获取并操作材质组**：
    *   使用 `Get All Groups` 节点获取项目中所有的 `UMaterialValidationGroup` 资产。
    *   对其中一个组调用 `Add Missing Materials to Group`，确保组内包含了所有需要验证的材质。
    *   调用 `Update Material Permutations in Group` 来初始化或刷新该组的排列数据。

2.  **在编辑器工具中**：
    *   在内容浏览器中右键点击一个 `UMaterialValidationGroup` 资产，选择“编辑”可以打开其专属的编辑器工具包（Toolkit），其中包含材质列表、排列信息和变更列表（Changelist）视图。
    *   在该工具包中，可以直接点击“Update Materials”和“Update Material Permutations”按钮来更新数据。

## C++ 用法

### 头文件引入

```cpp
#include "MaterialValidationModule.h"
```

### 基本用法

以下示例展示了如何通过模块接口打开相似性浏览器。

```cpp
// 假设你有一个 UMaterialInstanceConstant* MyMaterialInstance
// 以及一个 UMaterialValidationGroup* MyGroup (可选，用于指定搜索范围)

#include "MaterialValidationModule.h"
#include "Materials/MaterialInstanceConstant.h"

void OpenSimilarityBrowserForMaterial(UMaterialInstanceConstant* InMaterialInstance)
{
    // 获取材质验证模块
    FMaterialValidationModule& MaterialValidationModule = FModuleManager::GetModuleChecked<FMaterialValidationModule>(TEXT("MaterialValidation"));

    // 打开相似性浏览器窗口，传入要比较的材质实例
    // 浏览器会自动查找该实例所属的基础材质，并在其层级内搜索相似实例
    TSharedPtr<SWindow> BrowserWindow = MaterialValidationModule.OpenSimilarityBrowser(*InMaterialInstance);

    if (BrowserWindow.IsValid())
    {
        // 窗口已创建并显示
        FSlateApplication::Get().AddWindow(BrowserWindow.ToSharedRef());
    }
}
```

### 进阶用法

使用 `UMaterialValidationLibrary` 中的静态函数进行批量操作。

```cpp
#include "MaterialValidationLibrary.h"
#include "MaterialValidationGroup.h"

void RefreshAllMaterialGroups()
{
    TArray<UMaterialValidationGroup*> AllGroups;
    // 同步加载所有组资产
    UMaterialValidationLibrary::GetAllGroups(AllGroups, true);

    for (UMaterialValidationGroup* Group : AllGroups)
    {
        if (Group)
        {
            // 先清理无效材质
            UMaterialValidationLibrary::RemoveInvalidMaterialsFromGroup(Group);
            // 再添加新发现的材质
            UMaterialValidationLibrary::AddMissingMaterialsToGroup(Group);
            // 最后更新所有排列
            UMaterialValidationLibrary::UpdateMaterialPermutationsInGroup(Group);
        }
    }
}
```

## Demo 示例

一个简单的 Actor，用于在游戏开始时打开指定材质实例的相似性浏览器。

**MaterialValidationDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MaterialValidationDemoActor.generated.h"

class UMaterialInstanceConstant;

UCLASS()
class AMyProject_API AMaterialValidationDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMaterialValidationDemoActor();

protected:
    virtual void BeginPlay() override;

    /** 要在浏览器中查看的材质实例。在编辑器中设置。 */
    UPROPERTY(EditAnywhere, Category = "Material Validation")
    TObjectPtr<UMaterialInstanceConstant> MaterialToBrowse;
};
```

**MaterialValidationDemoActor.cpp**
```cpp
#include "MaterialValidationDemoActor.h"
#include "MaterialValidationModule.h"
#include "Materials/MaterialInstanceConstant.h"

AMaterialValidationDemoActor::AMaterialValidationDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMaterialValidationDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 仅在编辑器中运行时执行
    if (GIsEditor && MaterialToBrowse)
    {
        // 获取模块并打开浏览器
        if (FModuleManager::Get().IsModuleLoaded(TEXT("MaterialValidation")))
        {
            FMaterialValidationModule& Module = FModuleManager::GetModuleChecked<FMaterialValidationModule>(TEXT("MaterialValidation"));
            TSharedPtr<SWindow> Window = Module.OpenSimilarityBrowser(*MaterialToBrowse);
            if (Window.IsValid())
            {
                FSlateApplication::Get().AddWindow(Window.ToSharedRef());
            }
        }
    }
}
```

## 模块依赖

该插件依赖于 `DataValidation` 插件以集成到引擎的资产验证流程中。

| 模块 | 用途 |
|---|---|
| `DataValidation` | 提供资产验证的基础框架（`UEditorValidatorBase`），本插件的验证器基于此实现。 |

## 维护状态

### 近期更新

-   2026-04-24 `8c14c6cd` 将 MaterialValidation 模块移动到公共头文件，以便从外部打开相似性浏览器。
-   2026-04-19 `9ad6dae8` 添加“查找相似材质实例”浏览器（SMaterialInstanceSimilarityBrowser）。
-   2026-04-14 `35e60df1` 将 UE_LOG 迁移至 UE_LOGF。

### 维护评价

-   **创建时间**：2026年3月，非常新的插件。
-   **更新频率**：近期（2026年4月）有连续的功能性更新，包括重要的新功能（相似性浏览器）。
-   **维护状态**：**活跃维护中**。Epic Games 正在积极开发和完善此插件。
-   **已知限制**：插件标记为 `IsBetaVersion=true`，且默认未启用 (`EnabledByDefault=false`)，表明它仍处于实验阶段，API 和功能可能发生变化。
-   **推荐使用**：**推荐在需要严格控制材质排列的项目中试用**。鉴于其活跃的开发状态和解决的实际问题，它是一个有价值的工具。但需注意其 Beta 状态，建议在非关键生产流程中先行评估。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/MaterialValidation)