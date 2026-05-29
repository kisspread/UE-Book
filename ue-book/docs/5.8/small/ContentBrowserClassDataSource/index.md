# Content Browser - Class Data Source

> Data Source plugin providing Class Data to the Content Browser

| 属性 | 值 |
|---|---|
| 中文名 | 内容浏览器类数据源 |
| 分类 | Content Browser |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ContentBrowserClassDataSource` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ContentBrowser/ContentBrowserClassDataSource) | |

## 用途

此插件是 **UE 内容浏览器（Content Browser）** 的一个**数据源（Data Source）**扩展。它的核心作用是将引擎的**原生 C++ 类层次结构（Native Class Hierarchy）** 以虚拟文件夹和文件的形式呈现在内容浏览器中，使得开发者可以像浏览普通资产（如蓝图、材质）一样，方便地浏览、搜索和过滤 C++ 类。

它解决了在大型项目中，快速定位和理解复杂 C++ 类继承关系的痛点，提供了直观的可视化导航。

## 使用场景

- **C++ 开发者**：需要浏览整个引擎或项目中所有 C++ 类的继承树时。
- **寻找父类**：想要查看某个特定类（如 `AActor`）有哪些直接子类或所有子类时。
- **代码导航**：希望在内容浏览器中通过双击一个“类文件”直接跳转到对应的 C++ 源代码头文件（`.h`）。
- **过滤与搜索**：需要在内容浏览器中使用现有的资产过滤条件（如路径、类型）来过滤 C++ 类时。

## 蓝图用法

此插件主要作为编辑器后端的数据提供者，其核心类 `UContentBrowserDataSource` 并未暴露 `BlueprintCallable` 函数。其功能完全集成在内容浏览器的 UI 中，无需直接使用蓝图调用。

## C++ 用法

### 头文件引入

```cpp
#include "ContentBrowserClassDataSource.h"
#include "ContentBrowserClassDataPayload.h"
#include "ContentBrowserClassDataCore.h"
```

### 基本用法

主要通过 `ContentBrowserClassData` 命名空间下的辅助函数与数据载荷（Payload）交互。

```cpp
// 来源: ContentBrowserClassDataSource.h, ContentBrowserClassDataCore.h
// 假设你已通过某种方式获得了 FContentBrowserItemData InItem（例如从内容浏览器回调中）

// 获取文件（类）项的数据载荷
TSharedPtr<const FContentBrowserClassFileItemDataPayload> ClassPayload = 
    ContentBrowserClassData::GetClassFileItemPayload(nullptr, InItem); // 第一个参数 OwnerDataSource 可为 null，如果已知

if (ClassPayload.IsValid())
{
    // 获取代表的类
    UClass* MyClass = ClassPayload->GetClass();
    UE_LOG(LogTemp, Log, TEXT("Found class: %s"), *MyClass->GetName());

    // 获取该项的虚拟路径
    FName InternalPath = ClassPayload->GetInternalPath();

    // 获取该类对应的物理文件路径（磁盘上的.h文件路径）
    FString DiskPath;
    if (ContentBrowserClassData::GetClassFileItemPhysicalPath(*ClassPayload, DiskPath))
    {
        UE_LOG(LogTemp, Log, TEXT("Header file at: %s"), *DiskPath);
    }
}

// 获取文件夹项的数据载荷
TSharedPtr<const FContentBrowserClassFolderItemDataPayload> FolderPayload = 
    ContentBrowserClassData::GetClassFolderItemPayload(nullptr, InItem);

if (FolderPayload.IsValid())
{
    FName FolderInternalPath = FolderPayload->GetInternalPath();
    UE_LOG(LogTemp, Log, TEXT("In folder: %s"), *FolderInternalPath.ToString());
}
```

### 进阶用法

监听类层次结构的变化，以便在自定义编辑器工具中响应类添加/移除事件。

```cpp
// 来源: NativeClassHierarchy.h, ContentBrowserClassDataSource.h
#include "NativeClassHierarchy.h"

// 假设你通过某种方式（如插件）获取了 FNativeClassHierarchy 的实例。
// 通常，这个实例由 UContentBrowserClassDataSource 内部持有，但你可以通过模块间通信或单例获取引用。

// 监听新类被添加
FNativeClassHierarchy::FOnNodesChanged& OnClassesAdded = MyNativeClassHierarchy->OnClassesAdded();
OnClassesAdded.AddLambda([](const TArrayView<TSharedRef<const FNativeClassHierarchyNode>>& AddedClasses)
{
    for (const TSharedRef<const FNativeClassHierarchyNode>& Node : AddedClasses)
    {
        if (Node->Type == ENativeClassHierarchyNodeType::Class)
        {
            UE_LOG(LogTemp, Log, TEXT("New class added to hierarchy: %s (in module: %s)"), 
                   *Node->EntryName.ToString(), 
                   *Node->ClassModuleName.ToString());
        }
    }
});

// 监听文件夹被移除
FNativeClassHierarchy::FOnNodesChanged& OnFoldersRemoved = MyNativeClassHierarchy->OnFoldersRemoved();
OnFoldersRemoved.AddLambda([](const TArrayView<TSharedRef<const FNativeClassHierarchyNode>>& RemovedFolders)
{
    for (const TSharedRef<const FNativeClassHierarchyNode>& Node : RemovedFolders)
    {
        UE_LOG(LogTemp, Log, TEXT("Folder removed from hierarchy: %s"), *Node->EntryPath);
    }
});

// 使用过滤器查询匹配的类
FNativeClassHierarchyFilter Filter;
Filter.ClassPaths.Add(FName(TEXT("/Classes_Game/MyGame/Characters")));
Filter.bRecursivePaths = true; // 包含子文件夹

TArray<UClass*> MatchingClasses;
MyNativeClassHierarchy->GetMatchingClasses(Filter, MatchingClasses);
UE_LOG(LogTemp, Log, TEXT("Found %d matching classes"), MatchingClasses.Num());
```

## Demo 示例

一个在编辑器中访问并打印类层次信息的最小示例。

```cpp
// MyEditorUtils.h
#pragma once
#include "CoreMinimal.h"

class FMyEditorUtils
{
public:
    static void PrintClassHierarchyInfo();
};
```

```cpp
// MyEditorUtils.cpp
#include "MyEditorUtils.h"
#include "ContentBrowserClassDataSource.h"
#include "ContentBrowserClassDataCore.h"
#include "NativeClassHierarchy.h"
#include "Modules/ModuleManager.h"

void FMyEditorUtils::PrintClassHierarchyInfo()
{
    // 1. 获取类数据源实例（假设它是单例或可以通过模块获取）
    // 注意：这是一个简化示例。实际中可能需要通过编辑器子系统或模块接口获取。
    UContentBrowserClassDataSource* ClassDataSource = nullptr;
    // ... 通常通过 UContentBrowserSubsystem 或类似方式间接访问
    
    if (!ClassDataSource)
    {
        UE_LOG(LogTemp, Warning, TEXT("Cannot find ContentBrowserClassDataSource"));
        return;
    }

    // 2. 访问其内部的原生类层次结构（这是一个内部实现细节，仅为演示）
    // 在实际插件或编辑器扩展中，你可能需要自己维护或订阅事件。
    // 这里我们直接从数据源获取信息的方式通常是通过其公开的枚举接口。

    // 3. 枚举根文件夹（例如 Classes_Engine, Classes_Game）
    auto EnumerateCallback = [](FContentBrowserItemData&& ItemData) -> bool
    {
        if (ItemData.IsFolder())
        {
            TSharedPtr<const FContentBrowserClassFolderItemDataPayload> Payload = 
                ContentBrowserClassData::GetClassFolderItemPayload(nullptr, ItemData);
            if (Payload)
            {
                UE_LOG(LogTemp, Log, TEXT("Root Class Folder: %s"), *Payload->GetInternalPath().ToString());
            }
        }
        else // IsFile (Class)
        {
            TSharedPtr<const FContentBrowserClassFileItemDataPayload> Payload = 
                ContentBrowserClassData::GetClassFileItemPayload(nullptr, ItemData);
            if (Payload)
            {
                UE_LOG(LogTemp, Log, TEXT("  - Class: %s (Path: %s)"), 
                       *Payload->GetClass()->GetName(),
                       *Payload->GetInternalPath().ToString());
            }
        }
        return true; // 继续枚举
    };

    // 枚举所有根路径下的项目
    ClassDataSource->EnumerateItemsAtPath(FName(TEXT("/")), EContentBrowserItemTypeFilter::IncludeFolders | EContentBrowserItemTypeFilter::IncludeFiles, EnumerateCallback);
    
    UE_LOG(LogTemp, Log, TEXT("Class Hierarchy Info Printed to Output Log."));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ContentBrowser` | 内容浏览器核心框架，提供 `UContentBrowserDataSource` 基类和相关数据结构。 |
| `AssetDefinition` | 提供资产类型定义框架（`UAssetDefinition`），本插件用其定义类文件的编辑操作。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 `UE_LOG` 迁移为更先进的 `UE_LOGF`。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introduced new versions. | 废弃了旧的 `GetObjects*`/`ForEachObjectWithOuter` 接口，引入了新版本。 |
| 2025-09-02 | `9dbc2df4` | The asset view will now display, filter and sort by Verse paths, object paths or package paths in the class view. | 资产视图现在可以在类视图中通过Verse路径、对象路径或包路径进行显示、过滤和排序。 |
| 2025-08-19 | `916ed529` | Updated the Content Browser navigation bar so clicking in the empty space edits a friendly user facing path. | 更新了内容浏览器导航栏，点击空白处可编辑用户友好的路径。 |
| 2025-08-18 | `2380e892` | Added support for navigating to script package name folders entered in the content browser navigation bar. | 新增了在导航栏中输入脚本包名以直接导航到对应文件夹的支持。 |

### 维护评价

该插件**仍在活跃维护中**。从提交记录看，最近一年内有多次更新，涉及功能增强（支持Verse路径、UI改进）和底层维护（日志迁移、API废弃）。作为内容浏览器的核心数据源之一，其重要性高，因此获得了持续的关注。

**推荐使用**。它是UE编辑器原生体验的一部分，稳定可靠，对于需要浏览C++类层次结构的开发者不可或缺。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ContentBrowser/ContentBrowserClassDataSource)
- [官方文档]()（无）
- [测试用例]()（未在插件目录内发现独立测试文件）