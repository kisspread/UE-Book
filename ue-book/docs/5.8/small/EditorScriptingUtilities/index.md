# Editor Scripting Utilities

> Helper functions to script your own UE editor functionalities with Blueprint or other scripting tools.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器脚本工具 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `EditorScriptingUtilities` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EditorScriptingUtilities) | |

## 用途

`EditorScriptingUtilities` 插件为通过蓝图或 Python 脚本（如 Commandlet）自动化编辑器任务提供了一组基础函数库。它封装了编辑器中常见的操作，如资产的加载、保存、重命名、删除，角色的生成、销毁、选择，以及静态网格/骨骼网格的LOD、碰撞、UV管理等。**重要提示：在 UE 5.0 中，此插件已被标记为废弃（Deprecated）**，其功能已被拆分并迁移到更具体的子系统中（例如 `UStaticMeshEditorSubsystem`、`UEditorActorSubsystem` 等）。此插件主要作为旧有蓝图或脚本的兼容层而存在。

## 使用场景

- **历史场景**：在 UE 4.2x 时代，开发者需要通过蓝图或Python脚本批量处理资产、管理关卡中的角色或修改网格属性。
- **当前场景**：**不推荐在新项目中使用**。如果你正在维护一个旧项目并发现蓝图中大量使用了此插件的节点，你可以继续使用它们以避免大规模重构。对于新项目，应直接使用对应的编辑器子系统。

## 蓝图用法

**警告：以下所有函数均已废弃，新项目应使用其 DeprecationMessage 中指向的替代函数。**

### 核心节点

以下为该插件提供的主要功能类别及示例函数：

#### 资产管理 (`UEditorAssetLibrary`)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadAsset` | 加载内容浏览器中的资产 | `UEditorAssetLibrary` |
| `DuplicateAsset` | 复制一个资产 | `UEditorAssetLibrary` |
| `RenameAsset` | 重命名（移动）资产 | `UEditorAssetLibrary` |
| `DeleteAsset` | 删除资产 | `UEditorAssetLibrary` |
| `SaveAsset` | 保存资产 | `UEditorAssetLibrary` |
| `FindPackageReferencersForAsset` | 查找资产的引用者 | `UEditorAssetLibrary` |

#### 关卡与角色操作 (`UEditorLevelLibrary`)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAllLevelActors` | 获取当前关卡中所有角色 | `UEditorLevelLibrary` |
| `SpawnActorFromClass` | 在指定位置生成一个角色 | `UEditorLevelLibrary` |
| `DestroyActor` | 销毁一个角色 | `UEditorLevelLibrary` |
| `ReplaceSelectedActors` | 用另一种类型替换选中的角色 | `UEditorLevelLibrary` |
| `GetLevelViewportCameraInfo` | 获取编辑器视口摄像机位置和旋转 | `UEditorLevelLibrary` |

#### 静态网格编辑 (`UDEPRECATED_EditorStaticMeshLibrary`)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLods` | 为静态网格设置LOD级别 | `UDEPRECATED_EditorStaticMeshLibrary` |
| `AddSimpleCollisions` | 为网格添加简单碰撞 | `UDEPRECATED_EditorStaticMeshLibrary` |
| `SetConvexDecompositionCollisions` | 设置凸分解碰撞 | `UDEPRECATED_EditorStaticMeshLibrary` |
| `RemoveCollisions` | 移除所有碰撞 | `UDEPRECATED_EditorStaticMeshLibrary` |
| `ImportLOD` | 导入LOD模型文件 | `UDEPRECATED_EditorStaticMeshLibrary` |

#### 骨骼网格编辑 (`UDEPRECATED_EditorSkeletalMeshLibrary`)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegenerateLOD` | 重新生成LOD | `UDEPRECATED_EditorSkeletalMeshLibrary` |
| `ImportLOD` | 导入LOD模型文件 | `UDEPRECATED_EditorSkeletalMeshLibrary` |
| `RemoveLODs` | 移除指定的LOD | `UDEPRECATED_EditorSkeletalMeshLibrary` |
| `CreatePhysicsAsset` | 为骨骼网格创建物理资产 | `UDEPRECATED_EditorSkeletalMeshLibrary` |

#### 实用工具
| 节点 | 说明 | 所在类 |
|---|---|---|
| `ByClass` / `ByIDName` / `ByActorLabel` | 根据各种条件过滤对象/角色数组 | `UEditorFilterLibrary` |
| `ShowMessage` | 显示一个模态消息对话框 | `UEditorDialogLibrary` |
| `SyncBrowserToObjects` | 在内容浏览器中定位并显示资产 | `UEditorAssetLibrary` |

### 使用示例（蓝图描述）

**场景：批量重命名一组选中的资产。**
1.  **获取资产路径列表**：使用 `Get Selected Assets` 节点获取当前内容浏览器选中的资产对象数组。
2.  **循环处理**：使用 `For Each Loop` 遍历数组。
3.  **生成新路径并重命名**：在循环内，使用字符串操作节点生成新的资产路径，然后调用 `Editor Asset Library -> Rename Asset` 节点。`Source Asset Path` 输入当前资产的路径，`Destination Asset Path` 输入新路径。
4.  **注意**：此操作需要资产已被加载，且会尝试签出文件（如果使用版本控制）。

## C++ 用法

**重要：以下 API 已废弃，请查阅头文件中的 `UE_DEPRECATED` 注释以获取替代 API。**

### 头文件引入

```cpp
#include "EditorAssetLibrary.h"
#include "EditorLevelLibrary.h"
// 根据需要包含其他库的头文件
```

### 基本用法

以下代码演示了在C++中（例如在Editor Utility Widget或Commandlet中）使用`EditorAssetLibrary`进行资产操作。*(来源: `EditorAssetLibrary.h`)*

```cpp
#include "EditorAssetLibrary.h"

void MyEditorScript::ProcessAssets()
{
    // 加载一个资产
    const FString AssetPath = TEXT("/Game/MyFolder/MyAsset.MyAsset");
    UObject* LoadedAsset = UEditorAssetLibrary::LoadAsset(AssetPath);
    if (LoadedAsset)
    {
        UE_LOG(LogTemp, Log, TEXT("Loaded asset: %s"), *LoadedAsset->GetName());
    }

    // 检查资产是否存在
    bool bExists = UEditorAssetLibrary::DoesAssetExist(AssetPath);

    // 复制资产
    const FString DestPath = TEXT("/Game/MyFolder/MyAsset_Copy");
    UObject* DuplicatedAsset = UEditorAssetLibrary::DuplicateAsset(AssetPath, DestPath);

    // 获取资产的元数据标签
    if (LoadedAsset)
    {
        FString TagValue = UEditorAssetLibrary::GetMetadataTag(LoadedAsset, FName("MyCustomTag"));
    }
}
```

### 进阶用法

结合多个库的功能，在关卡中找到特定标签的角色，并为它们批量更换材质。*(来源: `EditorLevelLibrary.h`)*

```cpp
#include "EditorLevelLibrary.h"
#include "EditorAssetLibrary.h"

void MyEditorScript::BatchReplaceMaterial()
{
    // 1. 获取关卡中所有角色
    TArray<AActor*> AllActors = UEditorLevelLibrary::GetAllLevelActors();

    // 2. 过滤出带有特定标签的角色 (假设使用EditorFilterLibrary，但此处用C++逻辑简化)
    TArray<AActor*> TaggedActors;
    for (AActor* Actor : AllActors)
    {
        if (Actor && Actor->Tags.Contains(FName("ReplaceMaterial")))
        {
            TaggedActors.Add(Actor);
        }
    }

    // 3. 准备新材质
    const FString NewMaterialPath = TEXT("/Game/Materials/M_NewMaterial");
    UMaterialInterface* NewMaterial = Cast<UMaterialInterface>(UEditorAssetLibrary::LoadAsset(NewMaterialPath));

    // 4. 替换材质 (使用已废弃的函数，实际应用应查阅替代方案)
    if (NewMaterial && TaggedActors.Num() > 0)
    {
        // 注意：此函数已废弃
        UEditorLevelLibrary::ReplaceMeshComponentsMaterialsOnActors(TaggedActors, nullptr, NewMaterial);
    }
}
```

## Demo 示例

一个最小的编辑器工具面板，包含一个按钮，用于在点击时列出当前关卡中的所有角色名称。*(注意：此示例使用了废弃的API，仅作结构参考)*

**MyEditorToolPanel.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Editor/Blutility/Classes/BlutilityUserWidget.h"
#include "MyEditorToolPanel.generated.h"

class UButton;
class UTextBlock;

UCLASS()
class UMyEditorToolPanel : public UBlutilityUserWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(meta = (BindWidget))
    UButton* ListActorsButton;

    UPROPERTY(meta = (BindWidget))
    UTextBlock* OutputText;

    UFUNCTION(BlueprintCallable)
    void OnListActorsButtonClicked();
};
```

**MyEditorToolPanel.cpp**
```cpp
#include "MyEditorToolPanel.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"
#include "EditorLevelLibrary.h"

void UMyEditorToolPanel::OnListActorsButtonClicked()
{
    // 调用废弃的API获取所有角色
    TArray<AActor*> Actors = UEditorLevelLibrary::GetAllLevelActors();
    
    FString OutputString = TEXT("Actors in level:\n");
    for (AActor* Actor : Actors)
    {
        if (Actor)
        {
            OutputString += FString::Printf(TEXT("- %s\n"), *Actor->GetName());
        }
    }

    if (OutputText)
    {
        OutputText->SetText(FText::FromString(OutputString));
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等，以及 `UnrealEd` 编辑器模块）。
你的模块需要依赖 `UnrealEd` 才能使用此类编辑器脚本功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移为 UE_LOGF。 |
| 2026-03-23 | `871f4daa` | Misc module deprecation fixup for 5.4 and earlier, I did not remove anything still in use. | 为5.4及更早版本进行杂项模块废弃修复，未移除仍在使用的部分。 |
| 2026-03-05 | `a3b601d8` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5`. Delete header files that now... | 移除受 `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5` 保护的包含项，删除现已...的头文件。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将 Base<Plugin>.ini 重命名为 Default<Plugin>.ini。 |

### 维护评价

此插件已**明确废弃**。从 2020 年 UE 5.0 预览版开始，其功能就已被官方标记为 `UE_DEPRECATED`，并指向新的编辑器子系统（如 `UStaticMeshEditorSubsystem`, `UEditorActorSubsystem` 等）。最近的提交均属于**维护性修复**（如适配新的日志宏、修复编译警告、清理已弃用的代码），没有任何新功能开发。**强烈建议新项目不要使用此插件**。对于旧项目，可继续使用以维持兼容性，但应规划逐步迁移至新的子系统。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EditorScriptingUtilities)
- 官方文档：无（已被废弃，新文档位于各子系统页面）
- 测试用例：未在插件目录内发现独立测试用例。