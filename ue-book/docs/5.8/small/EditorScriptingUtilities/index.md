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
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EditorScriptingUtilities) | |

## 用途

EditorScriptingUtilities 提供了一组蓝图可用的函数库，用于在编辑器环境下通过脚本（蓝图）批量操作资产、关卡、网格体和 Actor。它封装了编辑器的常见工作流——如加载/保存/复制/删除资产、查询和过滤 Actor、管理静态网格体和骨骼网格体的 LOD 与碰撞、以及弹出编辑器对话框。

**重要提示：自 UE 5.0 起，该插件中的大部分功能已被标记为废弃（Deprecated）**，功能已迁移至新的编辑器子系统中。非废弃的部分主要是 `UEditorAssetLibrary`（资产操作）、`UEditorFilterLibrary`（过滤器）和 `UEditorDialogLibrary`（对话框）。

## 使用场景

- 你需要通过蓝图批量导入、复制、重命名或删除内容浏览器中的资产 → 用 `UEditorAssetLibrary`
- 你需要在编辑器脚本中根据类、名称、标签、图层等条件过滤 Actor 列表 → 用 `UEditorFilterLibrary`
- 你需要在编辑器脚本中弹出消息框或对象属性编辑对话框 → 用 `UEditorDialogLibrary`
- 你需要在编辑器中通过脚本创建/删除 Actor、操控关卡 → **已废弃**，请改用 `EditorActorSubsystem` / `ULevelEditorSubsystem`
- 你需要脚本化静态网格体/骨骼网格体的 LOD、碰撞等操作 → **已废弃**，请改用 `UStaticMeshEditorSubsystem` / `USkeletalMeshEditorSubsystem`

## 蓝图用法

所有类均继承自 `UBlueprintFunctionLibrary`，函数可直接在蓝图中调用。

### 资产操作（UEditorAssetLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadAsset` | 从路径加载资产（已加载则跳过） | `UEditorAssetLibrary` |
| `LoadBlueprintClass` | 加载蓝图资产并返回其生成类 | `UEditorAssetLibrary` |
| `FindAssetData` | 根据路径获取 FAssetData 信息 | `UEditorAssetLibrary` |
| `DoesAssetExist` | 检查资产是否存在 | `UEditorAssetLibrary` |
| `DuplicateAsset` | 复制资产到新路径 | `UEditorAssetLibrary` |
| `RenameAsset` | 重命名资产（相当于移动） | `UEditorAssetLibrary` |
| `DeleteAsset` | 强制删除资产 | `UEditorAssetLibrary` |
| `SaveAsset` | 保存资产包 | `UEditorAssetLibrary` |
| `ListAssets` | 列出目录下所有资产路径 | `UEditorAssetLibrary` |
| `MakeDirectory` | 在内容浏览器中创建目录 | `UEditorAssetLibrary` |
| `ConsolidateAssets` | 将多个资产的所有引用合并到一个目标资产 | `UEditorAssetLibrary` |
| `FindPackageReferencersForAsset` | 查找资产的所有引用者 | `UEditorAssetLibrary` |
| `GetMetadataTag` | 获取资产元数据标签值 | `UEditorAssetLibrary` |
| `SetMetadataTag` | 设置资产元数据标签值 | `UEditorAssetLibrary` |
| `SyncBrowserToObjects` | 在内容浏览器中定位并选中资产 | `UEditorAssetLibrary` |

### 过滤器（UEditorFilterLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ByClass` | 按对象类过滤 | `UEditorFilterLibrary` |
| `ByIDName` | 按对象 ID 名称过滤 | `UEditorFilterLibrary` |
| `ByActorLabel` | 按 Actor 标签过滤 | `UEditorFilterLibrary` |
| `ByActorTag` | 按 Actor Tag 过滤 | `UEditorFilterLibrary` |
| `ByLayer` | 按图层名过滤 | `UEditorFilterLibrary` |
| `ByLevelName` | 按关卡名过滤 | `UEditorFilterLibrary` |
| `BySelection` | 按选中状态过滤 | `UEditorFilterLibrary` |

### 对话框（UEditorDialogLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ShowMessage` | 显示消息框，返回用户选择 | `UEditorDialogLibrary` |
| `ShowSuppressableWarningDialog` | 显示可抑制的警告对话框 | `UEditorDialogLibrary` |
| `ShowObjectDetailsView` | 弹出单个 UObject 属性编辑对话框 | `UEditorDialogLibrary` |
| `ShowObjectsDetailsView` | 弹出多个 UObject 属性编辑对话框 | `UEditorDialogLibrary` |

### 使用示例（蓝图描述）

**批量复制资产：**
1. 使用 `Make Directory` 节点创建目标目录 `/Game/Backup/`
2. 使用 `List Assets` 节点列出 `/Game/Original/` 下所有资产路径
3. 对每个路径执行 `Duplicate Asset`，目标路径设为 `/Game/Backup/AssetName`

**按标签过滤 Actor 后弹出确认对话框：**
1. 使用 `Get All Level Actors` 获取所有 Actor（注意：此函数已废弃，推荐使用 Editor Actor Subsystem）
2. 将结果传入 `Filter by Actor Tag`，Tag 设为 `"NeedsCleanup"`
3. 将过滤结果传入 `Show Message` 对话框，确认后执行后续操作

## C++ 用法

### 头文件引入

```cpp
#include "EditorAssetLibrary.h"
#include "EditorFilterLibrary.h"
#include "EditorDialogLibrary.h"
```

### 基本用法

```cpp
// 检查资产是否存在并加载
if (UEditorAssetLibrary::DoesAssetExist(TEXT("/Game/MyFolder/MyAsset")))
{
    UObject* Asset = UEditorAssetLibrary::LoadAsset(TEXT("/Game/MyFolder/MyAsset"));
    UE_LOG(LogTemp, Log, TEXT("Loaded asset: %s"), *Asset->GetName());
}

// 复制资产
UObject* Duplicated = UEditorAssetLibrary::DuplicateAsset(
    TEXT("/Game/Source/Template"),
    TEXT("/Game/NewFolder/MyCopy")
);

// 保存资产
UEditorAssetLibrary::SaveAsset(TEXT("/Game/NewFolder/MyCopy"), true);
```

### 进阶用法

```cpp
// 批量查找引用者后确认是否合并
TArray<FString> Referencers = UEditorAssetLibrary::FindPackageReferencersForAsset(
    TEXT("/Game/MyFolder/OldAsset"), true
);

if (Referencers.Num() > 0)
{
    // 弹出对话框让用户确认
    EAppReturnType::Type Result = UEditorDialogLibrary::ShowMessage(
        NSLOCTEXT("Cleanup", "Confirm", "确认合并"),
        FText::Format(
            NSLOCTEXT("Cleanup", "Msg", "发现 {0} 个引用者，是否合并到新资产？"),
            FText::AsNumber(Referencers.Num())
        ),
        EAppMsgType::YesNo,
        EAppReturnType::No
    );
    
    if (Result == EAppReturnType::Yes)
    {
        UObject* Target = UEditorAssetLibrary::LoadAsset(TEXT("/Game/NewFolder/Replacement"));
        TArray<UObject*> SourceAssets;
        SourceAssets.Add(UEditorAssetLibrary::LoadAsset(TEXT("/Game/MyFolder/OldAsset")));
        UEditorAssetLibrary::ConsolidateAssets(Target, SourceAssets);
    }
}

// 使用过滤器筛选 Actor
TArray<AActor*> AllActors = UEditorLevelLibrary::GetAllLevelActors();
TArray<AActor*> TaggedActors = UEditorFilterLibrary::ByActorTag(
    AllActors, FName("Important"), EEditorScriptingFilterType::Include
);
TArray<AActor*> FinalSelection = UEditorFilterLibrary::ByClass(
    CastArray<UObject*>(TaggedActors), AStaticMeshActor::StaticClass(), EEditorScriptingFilterType::Include
);
```

## Demo 示例

```cpp
// EditorBatchOperations.h
#pragma once

#include "CoreMinimal.h"
#include "EditorSubsystem.h"
#include "EditorBatchOperations.generated.h"

UCLASS()
class UEditorBatchOperationsSubsystem : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    /** 批量复制目录下所有资产到备份位置 */
    UFUNCTION(BlueprintCallable, Category = "Batch Operations")
    bool BackupAssetDirectory(const FString& SourcePath, const FString& BackupPath);

    /** 清理未使用的资产（基于元数据标签） */
    UFUNCTION(BlueprintCallable, Category = "Batch Operations")
    int32 CleanupTaggedAssets(FName Tag, const FString& TagValue);
};
```

```cpp
// EditorBatchOperations.cpp
#include "EditorBatchOperations.h"
#include "EditorAssetLibrary.h"
#include "EditorDialogLibrary.h"

bool UEditorBatchOperationsSubsystem::BackupAssetDirectory(const FString& SourcePath, const FString& BackupPath)
{
    if (!UEditorAssetLibrary::DoesDirectoryExist(SourcePath))
    {
        UE_LOG(LogTemp, Warning, TEXT("Source directory does not exist: %s"), *SourcePath);
        return false;
    }

    UEditorAssetLibrary::MakeDirectory(BackupPath);
    return UEditorAssetLibrary::DuplicateDirectory(SourcePath, BackupPath);
}

int32 UEditorBatchOperationsSubsystem::CleanupTaggedAssets(FName Tag, const FString& TagValue)
{
    TArray<FString> AssetPaths = UEditorAssetLibrary::ListAssetByTagValue(Tag, TagValue);

    if (AssetPaths.Num() == 0)
    {
        return 0;
    }

    EAppReturnType::Type Result = UEditorDialogLibrary::ShowMessage(
        NSLOCTEXT("Cleanup", "Title", "批量清理"),
        FText::Format(
            NSLOCTEXT("Cleanup", "Msg", "找到 {0} 个资产带有标签 {1}={2}，是否删除？"),
            FText::AsNumber(AssetPaths.Num()),
            FText::FromName(Tag),
            FText::FromString(TagValue)
        ),
        EAppMsgType::YesNo,
        EAppReturnType::No
    );

    if (Result != EAppReturnType::Yes)
    {
        return 0;
    }

    int32 DeletedCount = 0;
    for (const FString& Path : AssetPaths)
    {
        if (UEditorAssetLibrary::DeleteAsset(Path))
        {
            DeletedCount++;
        }
    }

    UE_LOG(LogTemp, Log, TEXT("Deleted %d assets tagged with %s=%s"), DeletedCount, *Tag.ToString(), *TagValue);
    return DeletedCount;
}
```

## 模块依赖

该插件的标准依赖（Core、CoreUObject、Engine、Slate、UMG、UnrealEd 等）已省略。无特殊依赖——仅使用标准编辑器模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移：UE_LOG 改为 UE_LOGF |
| 2026-03-23 | `871f4daa` | Misc module deprecation fixup for 5.4 and earlier, I did not remove anything still in use. | 清理 5.4 及更早版本的模块废弃兼容代码 |
| 2026-03-05 | `a3b601d8` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5`. Delete header files that now | 移除 UE 5.5 废弃的头文件包含守卫，删除冗余头文件 |
| 2025-10-07 | `96352708` | Renaming Base<Plugin>.ini to Default<Plugin>.ini | 配置文件重命名：Base 改为 Default |

### 维护评价

该插件自 UE 5.0 起已进入**废弃过渡期**。所有关卡操作、网格体操作、Actor 操作的函数均已标记 `DeprecatedFunction`，并指向新的编辑器子系统（`EditorActorSubsystem`、`UStaticMeshEditorSubsystem`、`USkeletalMeshEditorSubsystem`、`ULevelEditorSubsystem` 等）。

近期更新全部为编译器警告修复、日志宏迁移、头文件清理等维护性改动，**无任何功能更新**。插件仍在接收维护性提交以保持编译兼容性，但不会再有新功能。

**⚠️ 仅 `UEditorAssetLibrary`、`UEditorFilterLibrary` 和 `UEditorDialogLibrary` 未被废弃**，仍可正常使用。其余功能建议尽早迁移至对应的新子系统。

**推荐程度：仅用于资产操作和过滤/对话框等未废弃功能。已废弃的 Actor/关卡/网格体功能请勿使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EditorScriptingUtilities)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 替代方案：
  - `UActorEditorSubsystem` — 替代 `UEditorLevelLibrary` 中的 Actor 操作
  - `ULevelEditorSubsystem` — 替代 `UEditorLevelLibrary` 中的关卡操作
  - `UStaticMeshEditorSubsystem` — 替代 `UDEPRECATED_EditorStaticMeshLibrary`
  - `USkeletalMeshEditorSubsystem` — 替代 `UDEPRECATED_EditorSkeletalMeshLibrary`