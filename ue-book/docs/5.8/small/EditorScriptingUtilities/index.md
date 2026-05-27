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

Editor Scripting Utilities 提供了一组蓝图可调用的静态工具函数库，将编辑器中常见的资产管理、关卡操作、网格体编辑、对象过滤和对话框创建等操作暴露给脚本系统。它的存在是为了解决蓝图和 Python 脚本难以直接访问编辑器内部操作的问题——比如批量重命名资产、在场景中生成 Actor、管理静态网格体的 LOD 和碰撞体、以及弹出用户确认对话框等。

**重要提示**：该插件在 UE 5.0 中大部分功能已被废弃，相关功能迁移到了各编辑器子系统中：

| 原始类 | 替代方案 |
|---|---|
| `UEditorLevelLibrary` | `EditorActorUtilitiesSubsystem` / `LevelEditorSubsystem` / `UnrealEditorSubsystem` |
| `UDEPRECATED_EditorStaticMeshLibrary` | `UStaticMeshEditorSubsystem` |
| `UDEPRECATED_EditorSkeletalMeshLibrary` | `SkeletalMeshEditorSubsystem` |
| `UEditorAssetLibrary` | 仍然可用（未废弃） |
| `UEditorFilterLibrary` | 仍然可用（未废弃） |
| `UEditorDialogLibrary` | 仍然可用（未废弃） |

## 使用场景

- 你需要在蓝图或 Python 脚本中批量加载、保存、重命名、删除内容浏览器中的资产 → 使用 `UEditorAssetLibrary`
- 你需要在关卡编辑器中通过脚本生成、销毁、选择 Actor → 使用 `UEditorLevelLibrary`（已废弃，建议迁移到子系统）
- 你需要为静态网格体批量设置 LOD、碰撞体、UV 通道 → 使用 `UEditorStaticMeshLibrary`（已废弃）
- 你需要根据类、名称、标签、层级等条件筛选 Actor 列表 → 使用 `UEditorFilterLibrary`
- 你需要在编辑器工具中弹出消息框或属性编辑对话框 → 使用 `UEditorDialogLibrary`

## 蓝图用法

### 资产管理（UEditorAssetLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadAsset` | 从内容浏览器加载资产，若已加载则直接返回 | `UEditorAssetLibrary` |
| `LoadBlueprintClass` | 加载蓝图资产并返回其生成的类 | `UEditorAssetLibrary` |
| `DoesAssetExist` | 检查资产是否存在于内容浏览器中 | `UEditorAssetLibrary` |
| `DuplicateAsset` | 复制资产到新路径 | `UEditorAssetLibrary` |
| `RenameAsset` | 重命名资产（等同于移动操作） | `UEditorAssetLibrary` |
| `DeleteAsset` | 强制删除资产（不检查引用） | `UEditorAssetLibrary` |
| `SaveAsset` | 保存资产包，可选仅保存脏资产 | `UEditorAssetLibrary` |
| `CheckoutAsset` | 从版本控制签出资产 | `UEditorAssetLibrary` |
| `FindPackageReferencersForAsset` | 查找引用指定资产的所有包 | `UEditorAssetLibrary` |
| `ConsolidateAssets` | 合并资产，将所有引用替换为单一资产 | `UEditorAssetLibrary` |
| `ListAssets` | 列出目录下所有资产路径 | `UEditorAssetLibrary` |
| `MakeDirectory` | 在内容浏览器中创建目录 | `UEditorAssetLibrary` |
| `SyncBrowserToObjects` | 在内容浏览器中定位并选中指定资产 | `UEditorAssetLibrary` |

### 元数据操作（UEditorAssetLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMetadataTagValues` | 获取资产的所有元数据标签和值 | `UEditorAssetLibrary` |
| `GetMetadataTag` | 获取指定标签的元数据值 | `UEditorAssetLibrary` |
| `SetMetadataTag` | 设置资产的元数据标签值 | `UEditorAssetLibrary` |
| `RemoveMetadataTag` | 移除资产的元数据标签 | `UEditorAssetLibrary` |

### 对象过滤（UEditorFilterLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ByClass` | 按对象类过滤数组 | `UEditorFilterLibrary` |
| `ByIDName` | 按对象 ID 名称过滤（支持通配符） | `UEditorFilterLibrary` |
| `ByActorLabel` | 按 Actor 显示名称过滤 | `UEditorFilterLibrary` |
| `ByActorTag` | 按 Actor 标签过滤 | `UEditorFilterLibrary` |
| `ByLayer` | 按 Actor 所属层级过滤 | `UEditorFilterLibrary` |
| `ByLevelName` | 按 Actor 所属关卡名过滤 | `UEditorFilterLibrary` |
| `BySelection` | 按当前选中状态过滤 | `UEditorFilterLibrary` |

### 对话框（UEditorDialogLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ShowMessage` | 显示模态消息框（支持 Yes/No/Cancel 等按钮） | `UEditorDialogLibrary` |
| `ShowSuppressableWarningDialog` | 显示可抑制的警告对话框，状态持久化到 INI | `UEditorDialogLibrary` |
| `ShowObjectDetailsView` | 弹出单个 UObject 的属性编辑对话框 | `UEditorDialogLibrary` |
| `ShowObjectsDetailsView` | 弹出多个 UObject 的属性编辑对话框 | `UEditorDialogLibrary` |

### 关卡操作（UEditorLevelLibrary）— 已废弃

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAllLevelActors` | 获取当前世界中所有已加载的 Actor | `UEditorLevelLibrary` |
| `GetSelectedLevelActors` | 获取当前选中的 Actor | `UEditorLevelLibrary` |
| `SpawnActorFromObject` | 从资产/类/蓝图生成 Actor | `UEditorLevelLibrary` |
| `SpawnActorFromClass` | 从类生成 Actor | `UEditorLevelLibrary` |
| `DestroyActor` | 销毁 Actor 并通知编辑器 | `UEditorLevelLibrary` |
| `GetEditorWorld` | 获取编辑器世界对象 | `UEditorLevelLibrary` |

### 使用示例（蓝图描述）

**批量重命名资产**：
1. 使用 `ListAssets` 获取 `/Game/MyFolder/` 下所有资产路径
2. 对每个路径调用 `RenameAsset`，将源路径替换为目标路径
3. 使用 `SaveDirectory` 保存整个目录

**条件筛选 Actor 并操作**：
1. 使用 `GetAllLevelActors` 获取所有 Actor
2. 连接 `ByClass` 节点，设置 `ObjectClass` 为 `AStaticMeshActor`，`FilterType` 为 `Include`
3. 连接 `ByActorTag` 节点，设置 `Tag` 为 `"Foliage"`
4. 对筛选结果执行批量操作（如 `DestroyActor`）

**弹出确认对话框**：
1. 使用 `ShowMessage` 节点
2. 设置 `Title` 为 `"确认删除"`，`Message` 为 `"是否删除选中的资产？"`
3. 设置 `MessageType` 为 `YesNo`
4. 根据返回的 `EAppReturnType` 分支处理

## C++ 用法

### 头文件引入

```cpp
#include "EditorAssetLibrary.h"
#include "EditorFilterLibrary.h"
#include "EditorDialogLibrary.h"
#include "EditorLevelLibrary.h"    // 已废弃，仅作参考
```

### 基本用法

```cpp
// 检查资产是否存在
bool bExists = UEditorAssetLibrary::DoesAssetExist(TEXT("/Game/MyFolder/MyMesh"));

// 加载资产
UObject* Asset = UEditorAssetLibrary::LoadAsset(TEXT("/Game/MyFolder/MyMesh"));

// 复制资产
UObject* Duplicated = UEditorAssetLibrary::DuplicateAsset(
    TEXT("/Game/Source/Original"),
    TEXT("/Game/Dest/Copy")
);

// 保存资产（仅脏资产）
UEditorAssetLibrary::SaveAsset(TEXT("/Game/MyFolder/MyMesh"), true);

// 获取资产的元数据标签值
FString Value = UEditorAssetLibrary::GetMetadataTag(Asset, FName("CustomTag"));

// 设置元数据
UEditorAssetLibrary::SetMetadataTag(Asset, FName("Author"), TEXT("MyName"));
```

### 进阶用法

```cpp
// 批量查找并替换材质
TArray<AActor*> Actors = UEditorLevelLibrary::GetAllLevelActors();
TArray<AActor*> Filtered = UEditorFilterLibrary::ByClass(
    Actors, AStaticMeshActor::StaticClass(), EEditorScriptingFilterType::Include
);
Filtered = UEditorFilterLibrary::ByActorTag(Filtered, FName("ReplaceMe"));

UMaterialInterface* OldMat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/OldMaterial"));
UMaterialInterface* NewMat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/NewMaterial"));
UEditorLevelLibrary::ReplaceMeshComponentsMaterialsOnActors(Filtered, OldMat, NewMat);

// 弹出对话框让用户确认操作
EAppReturnType::Type Result = UEditorDialogLibrary::ShowMessage(
    NSLOCTEXT("MyTool", "ConfirmTitle", "批量替换确认"),
    FText::Format(NSLOCTEXT("MyTool", "ConfirmMsg", "将替换 {0} 个 Actor 的材质，是否继续？"), 
                  FText::AsNumber(Filtered.Num())),
    EAppMsgType::YesNo
);

if (Result == EAppReturnType::Yes)
{
    // 执行保存
    UEditorAssetLibrary::SaveDirectory(TEXT("/Game/MyFolder/"), true, true);
}
```

## Demo 示例

```cpp
// MyEditorTool.h
#pragma once

#include "CoreMinimal.h"
#include "EditorAssetLibrary.h"
#include "EditorFilterLibrary.h"

class FMyEditorTool
{
public:
    // 批量清理未使用资产的示例
    static void CleanupUnusedAssets(const FString& DirectoryPath)
    {
        // 列出目录下所有资产
        TArray<FString> AssetPaths = UEditorAssetLibrary::ListAssets(DirectoryPath, true, false);
        
        for (const FString& AssetPath : AssetPaths)
        {
            // 检查是否有引用者
            TArray<FString> Referencers = UEditorAssetLibrary::FindPackageReferencersForAsset(AssetPath, false);
            
            // 如果没有引用者，删除该资产
            if (Referencers.Num() == 0)
            {
                UE_LOG(LogTemp, Warning, TEXT("删除未使用资产: %s"), *AssetPath);
                UEditorAssetLibrary::DeleteAsset(AssetPath);
            }
        }
    }
    
    // 根据标签分类统计 Actor
    static TMap<FName, int32> CountActorsByTag(const FString& LevelPath)
    {
        TArray<AActor*> AllActors = UEditorLevelLibrary::GetAllLevelActors();
        TMap<FName, int32> TagCounts;
        
        // 统计各标签的 Actor 数量
        TArray<FName> TestTags = { FName("Foliage"), FName("Building"), FName("Prop") };
        
        for (const FName& Tag : TestTags)
        {
            TArray<AActor*> Filtered = UEditorFilterLibrary::ByActorTag(
                AllActors, Tag, EEditorScriptingFilterType::Include
            );
            TagCounts.Add(Tag, Filtered.Num());
        }
        
        return TagCounts;
    }
};
```

## 模块依赖

该插件作为纯编辑器工具，依赖标准编辑器模块，无特殊外部依赖。

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新宏 UE_LOGF |
| 2026-03-23 | `871f4daa` | Misc module deprecation fixup for 5.4 and earlier, I did not remove anything still in use. | 针对 5.4 及更早版本的模块弃用修复，保留仍在使用的代码 |
| 2026-03-05 | `a3b601d8` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5`. Delete header files that now… | 移除 UE 5.5 弃用的头文件包含守卫，删除过时头文件 |
| 2025-10-07 | `96352708` | Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件从 Base 前缀重命名为 Default 前缀 |

### 维护评价

⚠️ **已废弃 / 仅维护兼容性**

- **创建时间**：2018 年，已存在约 8 年
- **当前状态**：该插件在 UE 5.0 中大量核心功能（关卡操作、静态网格体、骨骼网格体）已被标记为废弃，功能迁移到对应的编辑器子系统（`EditorActorUtilitiesSubsystem`、`StaticMeshEditorSubsystem`、`SkeletalMeshEditorSubsystem` 等）
- **近期更新**：仅包含编译修复、日志宏迁移、头文件清理等维护性改动，无新功能开发
- **仍然可用的部分**：`UEditorAssetLibrary`（资产操作）、`UEditorFilterLibrary`（对象过滤）、`UEditorDialogLibrary`（对话框）尚未标记废弃，但未来版本可能会迁移
- **建议**：新项目应直接使用对应的编辑器子系统 API，仅在维护旧项目时使用此插件。**不建议在新项目中采用已废弃的 `EditorLevelLibrary` / `EditorStaticMeshLibrary` / `EditorSkeletalMeshLibrary`**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EditorScriptingUtilities)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）