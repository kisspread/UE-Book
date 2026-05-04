# Editor Scripting Utilities

> Helper functions to script your own UE editor functionalities with Blueprint or other scripting tools.

| 属性 | 值 |
|---|---|
| 分类 | Scripting |
| 默认启用 | ❌ `EnabledByDefault = false` |
| 包含内容 | ❌ `CanContainContent = false` |
| 模块 | EditorScriptingUtilities (Editor) |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Editor/EditorScriptingUtilities) | |

> ⚠️ **实验性插件**：`.uplugin` 中 `IsBetaVersion = true`，且 `EnabledByDefault = false`。
> ⚠️ **大部分功能已在 UE 5.0 标记为废弃**，建议迁移到对应的 Editor Subsystem。

## 用途

EditorScriptingUtilities 是一组**蓝图友好的编辑器脚本工具函数库**，让开发者可以在蓝图或 Python 脚本中执行常见的编辑器操作——管理资产（加载、复制、删除、重命名、保存）、操控关卡中的 Actor（生成、销毁、选择、替换）、处理 StaticMesh/SkeletalMesh（LOD、碰撞、UV 通道）、过滤 Actor 列表、以及弹出编辑器对话框。

这个 plugin 存在的意义是：**UE 的编辑器功能通常分散在各种 Subsystem 和 Editor 模块中，对蓝图并不友好**。此插件将这些功能包装成 `BlueprintCallable` 的静态函数，让设计师和技术美术也能通过蓝图实现自动化编辑器工作流。

### ⚠️ 废弃状态

自 UE 5.0 起，大部分功能已迁移至以下 Subsystem，本插件的函数保留为向后兼容的废弃重定向：

| 原类 | 迁移目标 |
|---|---|
| `UEditorLevelLibrary`（关卡/Actor 操作） | `EditorActorUtilitiesSubsystem`、`LevelEditorSubsystem`、`UnrealEditorSubsystem` |
| `UEditorStaticMeshLibrary`（静态网格操作） | `UStaticMeshEditorSubsystem` |
| `UEditorSkeletalMeshLibrary`（骨骼网格操作） | `SkeletalMeshEditorSubsystem` |
| `UEditorAssetLibrary`（资产操作） | **未废弃，仍可正常使用** |
| `UEditorFilterLibrary`（过滤器） | **未废弃，仍可正常使用** |
| `UEditorDialogLibrary`（对话框） | **未废弃，仍可正常使用** |

## 使用场景

- 你需要在蓝图中批量导入、复制、重命名或删除 Content Browser 中的资产 → 用 `UEditorAssetLibrary`
- 你需要在编辑器脚本中按类名、标签、图层等条件过滤 Actor 列表 → 用 `UEditorFilterLibrary`
- 你需要在自动化流程中弹出消息确认框或对象属性编辑对话框 → 用 `UEditorDialogLibrary`
- 你有旧蓝图使用了 `EditorStaticMeshLibrary` 或 `EditorLevelLibrary` → 它们仍然可以工作，但应逐步迁移到对应 Subsystem

## 蓝图用法

所有函数均为 `BlueprintCallable` 的静态函数，可直接在蓝图中拖拽使用。

### 核心节点：EditorAssetLibrary

`UEditorAssetLibrary` 提供 Content Browser 的全套操作，是最常用的类。

#### 资产加载与查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadAsset` | 按路径加载资产（已加载则跳过） | `UEditorAssetLibrary` |
| `LoadBlueprintClass` | 加载蓝图资产并返回生成的 UClass | `UEditorAssetLibrary` |
| `DoesAssetExist` | 检查资产是否存在于 Content Browser | `UEditorAssetLibrary` |
| `DoAssetsExist` | 批量检查资产是否存在 | `UEditorAssetLibrary` |
| `FindAssetData` | 获取 FAssetData，可配合 AssetRegistryHelpers 使用 | `UEditorAssetLibrary` |
| `GetPathNameForLoadedAsset` | 获取已加载资产的路径名 | `UEditorAssetLibrary` |
| `FindPackageReferencersForAsset` | 查找引用某资产的其他包 | `UEditorAssetLibrary` |

#### 资产 CRUD 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DuplicateAsset` / `DuplicateLoadedAsset` | 复制资产 | `UEditorAssetLibrary` |
| `DuplicateDirectory` | 复制整个目录 | `UEditorAssetLibrary` |
| `RenameAsset` / `RenameLoadedAsset` | 重命名/移动资产 | `UEditorAssetLibrary` |
| `RenameDirectory` | 重命名/移动目录 | `UEditorAssetLibrary` |
| `DeleteAsset` / `DeleteLoadedAsset` | 删除资产（强制删除） | `UEditorAssetLibrary` |
| `DeleteDirectory` | 递归删除目录 | `UEditorAssetLibrary` |
| `ConsolidateAssets` | 合并资产引用（会删除源资产） | `UEditorAssetLibrary` |

#### 资产保存与版本控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SaveAsset` / `SaveLoadedAsset` | 保存资产 | `UEditorAssetLibrary` |
| `SaveDirectory` | 保存目录内所有资产 | `UEditorAssetLibrary` |
| `CheckoutAsset` / `CheckoutLoadedAsset` | 签出资产（用于版本控制） | `UEditorAssetLibrary` |
| `CheckoutDirectory` | 签出目录内所有资产 | `UEditorAssetLibrary` |

#### 目录与列表操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DoesDirectoryExist` | 检查目录是否存在 | `UEditorAssetLibrary` |
| `DoesDirectoryHaveAssets` | 检查目录是否有资产 | `UEditorAssetLibrary` |
| `MakeDirectory` | 创建目录 | `UEditorAssetLibrary` |
| `ListAssets` | 列出目录内所有资产路径 | `UEditorAssetLibrary` |
| `ListAssetByTagValue` | 按 Tag/Value 查找资产 | `UEditorAssetLibrary` |

#### 元数据操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMetadataTagValues` | 获取资产所有元数据标签 | `UEditorAssetLibrary` |
| `GetMetadataTag` | 获取指定元数据标签值 | `UEditorAssetLibrary` |
| `SetMetadataTag` | 设置元数据标签 | `UEditorAssetLibrary` |
| `RemoveMetadataTag` | 移除元数据标签 | `UEditorAssetLibrary` |

#### Content Browser 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SyncBrowserToObjects` | 在 Content Browser 中定位并选中资产 | `UEditorAssetLibrary` |

### 核心节点：EditorFilterLibrary

`UEditorFilterLibrary` 提供 Actor 列表的过滤功能。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ByClass` | 按对象类过滤 | `UEditorFilterLibrary` |
| `ByIDName` | 按对象 ID 名称过滤（支持通配符） | `UEditorFilterLibrary` |
| `ByActorLabel` | 按 Actor 显示名称过滤 | `UEditorFilterLibrary` |
| `ByActorTag` | 按 Actor Tag 过滤 | `UEditorFilterLibrary` |
| `ByLayer` | 按图层过滤 | `UEditorFilterLibrary` |
| `ByLevelName` | 按关卡名称过滤 | `UEditorFilterLibrary` |
| `BySelection` | 按选中状态过滤 | `UEditorFilterLibrary` |

### 核心节点：EditorDialogLibrary

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ShowMessage` | 弹出消息对话框（OK/Yes/No/Cancel 等） | `UEditorDialogLibrary` |
| `ShowSuppressableWarningDialog` | 弹出可抑制的警告对话框 | `UEditorDialogLibrary` |
| `ShowObjectDetailsView` | 弹出单个 UObject 属性编辑对话框 | `UEditorDialogLibrary` |
| `ShowObjectsDetailsView` | 弹出多个 UObject 属性编辑对话框 | `UEditorDialogLibrary` |

### 使用示例（蓝图描述）

**示例 1：批量重命名资产**

1. 使用 `ListAssets` 节点，输入目录路径 `/Game/OldFolder`，获取所有资产路径列表
2. 用 `ForEach` 循环遍历资产路径
3. 对每个路径，使用 `RenameAsset` 节点，将源路径替换为新路径
4. 循环结束，所有资产完成重命名

**示例 2：按类型过滤选中的 Actor 并显示确认对话框**

1. 使用 `GetSelectedLevelActors`（或新版 Subsystem 等效函数）获取当前选中的 Actor
2. 连接到 `ByClass` 节点，设置 `ObjectClass` 为 `StaticMeshActor`，`FilterType` 为 `Include`
3. 将过滤结果连接到 `ShowMessage` 节点，消息内容包含 Actor 数量
4. 根据用户点击 Yes/No 执行后续操作

**示例 3：弹出对象属性编辑对话框**

1. 创建一个自定义 UObject 子类实例，带有一些 `UPROPERTY` 属性
2. 连接到 `ShowObjectDetailsView` 节点，设置标题和选项（如是否允许搜索、最小尺寸等）
3. 用户在对话框中编辑属性后点击 OK，函数返回 `true`，对象属性已被修改

## C++ 用法

### 头文件引入

```cpp
#include "EditorAssetLibrary.h"
#include "EditorFilterLibrary.h"
#include "EditorDialogLibrary.h"
#include "EditorLevelLibrary.h"          // 已废弃
#include "EditorStaticMeshLibrary.h"     // 已废弃
#include "EditorSkeletalMeshLibrary.h"   // 已废弃
```

### 基本用法

**资产操作** — `UEditorAssetLibrary` 仍可正常使用：

```cpp
// 加载资产
UObject* MyAsset = UEditorAssetLibrary::LoadAsset("/Game/MyFolder/MyMesh");

// 检查资产是否存在
bool bExists = UEditorAssetLibrary::DoesAssetExist("/Game/MyFolder/MyMesh");

// 复制资产
UObject* Duplicate = UEditorAssetLibrary::DuplicateAsset(
    "/Game/MyFolder/Original", "/Game/MyFolder/Copy");

// 保存资产
UEditorAssetLibrary::SaveAsset("/Game/MyFolder/MyMesh", true); // true = 仅保存脏资产

// 列出目录内所有资产
TArray<FString> Assets = UEditorAssetLibrary::ListAssets("/Game/MyFolder/", true, false);

// 设置元数据标签
UEditorAssetLibrary::SetMetadataTag(MyAsset, FName("CustomTag"), TEXT("Value123"));
```

**过滤器** — `UEditorFilterLibrary`：

```cpp
TArray<AActor*> AllActors = /* 从某处获取的 Actor 列表 */;

// 按类过滤，只保留 StaticMeshActor
TArray<UObject*> MeshActors = UEditorFilterLibrary::ByClass(
    AllActors, AStaticMeshActor::StaticClass(), EEditorScriptingFilterType::Include);

// 按标签过滤
TArray<AActor*> TaggedActors = UEditorFilterLibrary::ByActorTag(
    AllActors, FName("Important"), EEditorScriptingFilterType::Include);
```

**对话框** — `UEditorDialogLibrary`：

```cpp
// 弹出确认对话框
EAppReturnType::Type Result = UEditorDialogLibrary::ShowMessage(
    NSLOCTEXT("MyTool", "Title", "确认操作"),
    NSLOCTEXT("MyTool", "Msg", "是否要删除选中的资产？"),
    EAppMsgType::YesNo,
    EAppReturnType::No,
    EAppMsgCategory::Warning
);

if (Result == EAppReturnType::Yes)
{
    // 用户确认，执行删除
}
```

### 进阶用法

**资产合并与引用管理**：

```cpp
// 查找引用某资产的所有包（不加载确认）
TArray<FString> Referencers = UEditorAssetLibrary::FindPackageReferencersForAsset(
    "/Game/MyFolder/OldAsset", false);

// 合并资产：将所有对 OldAsset 的引用指向 NewAsset，OldAsset 会被删除
UObject* NewAsset = UEditorAssetLibrary::LoadAsset("/Game/MyFolder/NewAsset");
UObject* OldAsset = UEditorAssetLibrary::LoadAsset("/Game/MyFolder/OldAsset");
TArray<UObject*> ToConsolidate = { OldAsset };
bool bSuccess = UEditorAssetLibrary::ConsolidateAssets(NewAsset, ToConsolidate);
```

**按标签值批量查找资产**：

```cpp
// 找出所有材质球中标记为 "Quality" = "High" 的资产
TArray<FString> HighQualityAssets = UEditorAssetLibrary::ListAssetByTagValue(
    FName("Quality"), TEXT("High"));
```

**弹出对象属性编辑对话框**：

```cpp
// 创建自定义设置对象并弹出编辑对话框
UMyToolSettings* Settings = NewObject<UMyToolSettings>();
FEditorDialogLibraryObjectDetailsViewOptions Options;
Options.bShowObjectName = true;
Options.bAllowSearch = true;
Options.bAllowResizing = true;
Options.MinWidth = 600;
Options.MinHeight = 400;
Options.ValueColumnWidthRatio = 0.7f;

bool bAccepted = UEditorDialogLibrary::ShowObjectDetailsView(
    NSLOCTEXT("MyTool", "Settings", "工具设置"),
    Settings,
    Options);

if (bAccepted)
{
    // 用户点击了 OK，Settings 中的属性已被修改
}
```

## Demo 示例

一个完整的最小示例——在编辑器工具中批量保存所有脏资产：

```cpp
// MyTool.h
#pragma once

#include "CoreMinimal.h"
#include "EditorAssetLibrary.h"

class FMyBatchSaveTool
{
public:
    static void SaveAllDirtyAssetsInFolder(const FString& FolderPath)
    {
        // 列出目录下所有资产（递归）
        TArray<FString> AssetPaths = UEditorAssetLibrary::ListAssets(FolderPath, true, false);
        
        UE_LOG(LogTemp, Log, TEXT("Found %d assets in %s"), AssetPaths.Num(), *FolderPath);
        
        // 批量保存（仅保存脏资产）
        for (const FString& AssetPath : AssetPaths)
        {
            if (UEditorAssetLibrary::DoesAssetExist(AssetPath))
            {
                UEditorAssetLibrary::SaveAsset(AssetPath, true);
            }
        }
        
        UE_LOG(LogTemp, Log, TEXT("Batch save complete."));
    }
};
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "EditorScriptingUtilities",
    // 如果要直接使用 EditorAssetLibrary，需要间接依赖以下模块（已由 EditorScriptingUtilities 引入）：
    // "AssetRegistry",
    // "Core",
    // "CoreUObject",
    // "Engine",
});
```

## 模块依赖

从 `EditorScriptingUtilities.Build.cs` 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 资产注册表，查询资产元数据和引用关系 |
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统基础 |
| `Engine` | 引擎核心，World、Actor 等 |
| `StaticMeshEditor` | 静态网格编辑器功能（用于已废弃的 StaticMesh 操作） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-05-30 | `8396b18` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 2/n | 编译修复：DLL 导出符号调整，非功能性更新 |
| 2025-03-03 | `8d05b3a` | Cleaned up LODs -> lo_ds in Python exposed API | Python API 命名规范化（LODs → lo_ds），修复 Python 脚本兼容性 |
| 2024-10-22 | `98a8e0e` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 清理 UE 5.2 时代的废弃 include 宏，代码整洁性维护 |

### 维护评价

- **创建时间**：2018 年 5 月，至今约 8 年
- **废弃状态**：自 UE 5.0 起，`EditorStaticMeshLibrary`、`EditorSkeletalMeshLibrary`、`EditorLevelLibrary` 的大部分函数均已标记为 `UE_DEPRECATED`，重定向到对应的 Editor Subsystem
- **仍可用的功能**：`UEditorAssetLibrary`、`UEditorFilterLibrary`、`UEditorDialogLibrary` 未被废弃
- **更新频率**：近一年内有 3 次提交，但均为编译修复和代码清理，无新功能
- **实验性标签**：`IsBetaVersion = true`，从未"毕业"为正式插件
- **推荐**：如果是新项目，**优先使用对应的 Editor Subsystem**（如 `UStaticMeshEditorSubsystem`、`UEditorActorSubsystem`）；如果是维护旧项目，现有蓝图仍然可以继续使用，但应规划迁移

> ⚠️ 此插件在 UE 5.0 后已无实质性功能更新，大部分 API 为废弃重定向包装器。新代码不应依赖此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/EditorScriptingUtilities)
- [官方文档]()（.uplugin 中未提供 DocsURL）
- [测试用例]()（未在插件目录内找到独立测试文件）
