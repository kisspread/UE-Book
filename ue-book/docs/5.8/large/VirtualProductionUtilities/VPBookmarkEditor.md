# Virtual Production Utilities

> Utility classes and functions for Virtual Production

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制作工具集 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `VPBookmark` (Runtime), `VPBookmarkEditor` (Runtime), `VPUtilities` (Runtime), `VPUtilitiesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProductionUtilities) | |

## 用途

Virtual Production Utilities 是 Epic Games 为虚拟制作工作流提供的工具集插件。它主要用于扩展 Unreal Engine 在虚拟制作场景下的功能，特别是书签系统和相关的编辑器工具。

从源码分析来看，该插件的核心功能围绕 **VPBookmark 系统**展开，它扩展了引擎内置的书签功能，使其更适合虚拟制作环境。主要功能包括：
- 自定义书签类型，可以在关卡中创建和管理书签位置
- 提供蓝图接口，方便在虚拟制作流程中快速导航和定位
- 包含编辑器扩展，为书签提供更好的编辑器集成和UI体验
- 与其他虚拟制作工具（如时间码管理、全屏控件等）集成

这个插件存在的目的是为了满足虚拟制作团队在拍摄、预览和后期制作过程中需要频繁保存、切换和管理不同摄像机位置和场景配置的需求。

## 使用场景

- 你在使用 Unreal Engine 进行虚拟制作，需要保存和快速切换多个摄像机位置 → 使用 VPBookmark 系统
- 你需要为虚拟制作流程创建自定义的书签管理界面 → 使用 VPBookmarkEditor 模块
- 你需要在蓝图中控制虚拟制作的书签导航 → 使用 VPBookmarkEditorBlueprintLibrary
- 你需要将时间码自定义时间步进功能移至其他模块 → 使用 VPUtilities 中的时间管理功能

## 蓝图用法

### 核心节点

基于 `VPBookmarkEditorBlueprintLibrary` 中的 BlueprintCallable 函数：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `JumpToBookmarkInLevelEditor` | 在关卡编辑器中跳转到指定的书签位置 | `UVPBookmarkEditorBlueprintLibrary` |
| `JumpToBookmarkInLevelEditorByIndex` | 根据书签索引在关卡编辑器中跳转 | `UVPBookmarkEditorBlueprintLibrary` |
| `AddBookmarkAtCurrentLevelEditorPosition` | 在当前关卡编辑器位置添加书签 | `UVPBookmarkEditorBlueprintLibrary` |
| `GetAllActorsClassThamImplementsVPBookmarkInterface` | 获取所有实现了 VPBookmark 接口的 Actor 类 | `UVPBookmarkEditorBlueprintLibrary` |

### 使用示例（蓝图描述）

**创建书签并跳转：**
1. 使用 `AddBookmarkAtCurrentLevelEditorPosition` 节点创建一个新书签，指定 Actor 类（如 AActor 或其子类）
2. 设置偏移量（Offset）和是否平展旋转（FlattenRotation）
3. 将返回的书签 Actor 保存为变量
4. 后续使用 `JumpToBookmarkInLevelEditor` 节点，传入保存的书签变量即可快速跳转

**遍历所有书签类：**
1. 使用 `GetAllActorsClassThamImplementsVPBookmarkInterface` 节点获取所有书签 Actor 类
2. 使用 ForEach 循环遍历输出数组
3. 对每个类进行操作（如创建实例、查询信息等）

## C++ 用法

### 头文件引入

```cpp
#include "VPBookmarkEditorBlueprintLibrary.h"
#include "VPBookmarkTypeActions.h"
```

### 基本用法

从 `VPBookmarkEditorBlueprintLibrary.h` 提取的基本用法示例：

```cpp
// 跳转到指定书签
UVPBookmark* Bookmark = /* 获取或创建书签 */;
bool bSuccess = UVPBookmarkEditorBlueprintLibrary::JumpToBookmarkInLevelEditor(Bookmark);

// 在当前位置创建书签
TSubclassOf<AActor> ActorClass = AActor::StaticClass();
FVPBookmarkCreationContext CreationContext;
FVector Offset(100.0f, 0.0f, 0.0f);
AActor* BookmarkActor = UVPBookmarkEditorBlueprintLibrary::AddBookmarkAtCurrentLevelEditorPosition(
    ActorClass, CreationContext, Offset, true);

// 获取所有书签 Actor 类
TArray<TSubclassOf<AActor>> BookmarkClasses;
UVPBookmarkEditorBlueprintLibrary::GetAllActorsClassThamImplementsVPBookmarkInterface(BookmarkClasses);
```

### 进阶用法

结合 `VPBookmarkTypeActions.h` 中的自定义书签类型操作：

```cpp
// 监听书签激活/停用事件
FVPBookmarkTypeActions* TypeActions = /* 获取类型操作实例 */;
TypeActions->OnBookmarkActivated.AddLambda([](UVPBookmark* Bookmark) {
    UE_LOG(LogTemp, Log, TEXT("书签已激活: %s"), *Bookmark->GetName());
});

TypeActions->OnBookmarkDeactivated.AddLambda([](UVPBookmark* Bookmark) {
    UE_LOG(LogTemp, Log, TEXT("书签已停用: %s"), *Bookmark->GetName());
});

// 手动生成书签
FEditorViewportClient* ViewportClient = /* 获取视口客户端 */;
AActor* NewBookmark = FVPBookmarkTypeActions::SpawnBookmark(
    ViewportClient,
    AActor::StaticClass(),
    FVPBookmarkCreationContext(),
    FVector::ZeroVector,
    true);
```

## Demo 示例

### BookmarkManager.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "VPBookmark.h"
#include "BookmarkManager.generated.h"

UCLASS()
class ABookmarkManager : public AActor
{
    GENERATED_BODY()

public:
    ABookmarkManager();

    UFUNCTION(BlueprintCallable, Category = "Bookmarks")
    void SaveCurrentPositionAsBookmark();

    UFUNCTION(BlueprintCallable, Category = "Bookmarks")
    void JumpToNextBookmark();

    UFUNCTION(BlueprintCallable, Category = "Bookmarks")
    void JumpToPreviousBookmark();

private:
    UPROPERTY()
    TArray<UVPBookmark*> Bookmarks;

    int32 CurrentBookmarkIndex;
};
```

### BookmarkManager.cpp
```cpp
#include "BookmarkManager.h"
#include "VPBookmarkEditorBlueprintLibrary.h"

ABookmarkManager::ABookmarkManager()
{
    CurrentBookmarkIndex = -1;
}

void ABookmarkManager::SaveCurrentPositionAsBookmark()
{
    TSubclassOf<AActor> ActorClass = AActor::StaticClass();
    FVPBookmarkCreationContext Context;
    FVector Offset = FVector::ZeroVector;
    
    AActor* BookmarkActor = UVPBookmarkEditorBlueprintLibrary::AddBookmarkAtCurrentLevelEditorPosition(
        ActorClass, Context, Offset, true);
    
    if (BookmarkActor)
    {
        if (UVPBookmark* Bookmark = BookmarkActor->FindComponentByClass<UVPBookmark>())
        {
            Bookmarks.Add(Bookmark);
            CurrentBookmarkIndex = Bookmarks.Num() - 1;
            UE_LOG(LogTemp, Log, TEXT("书签 %d 已创建，位置: %s"), 
                CurrentBookmarkIndex, *BookmarkActor->GetActorLocation().ToString());
        }
    }
}

void ABookmarkManager::JumpToNextBookmark()
{
    if (Bookmarks.Num() > 0)
    {
        CurrentBookmarkIndex = (CurrentBookmarkIndex + 1) % Bookmarks.Num();
        UVPBookmarkEditorBlueprintLibrary::JumpToBookmarkInLevelEditor(Bookmarks[CurrentBookmarkIndex]);
        UE_LOG(LogTemp, Log, TEXT("跳转到书签 %d"), CurrentBookmarkIndex);
    }
}

void ABookmarkManager::JumpToPreviousBookmark()
{
    if (Bookmarks.Num() > 0)
    {
        CurrentBookmarkIndex = (CurrentBookmarkIndex - 1 + Bookmarks.Num()) % Bookmarks.Num();
        UVPBookmarkEditorBlueprintLibrary::JumpToBookmarkInLevelEditor(Bookmarks[CurrentBookmarkIndex]);
        UE_LOG(LogTemp, Log, TEXT("跳转到书签 %d"), CurrentBookmarkIndex);
    }
}
```

## 模块依赖

从 VPBookmarkEditor 模块的头文件使用情况推断，需要以下特殊依赖：

| 模块 | 用途 |
|---|---|
| `VPBookmark` | 书签核心功能模块 |
| `LevelEditor` | 关卡编辑器集成 |
| `EditorStyle` | 编辑器界面样式 |
| `Slate` | UI 框架 |
| `InputCore` | 输入处理 |
| `UnrealEd` | 编辑器基础功能 |

**注意**：由于 VPBookmarkEditor 模块类型为 Runtime，但实际提供了编辑器功能，可能存在配置问题。实际使用时需要确保在编辑器环境下正确加载。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `02b15f1b` | Remove redundant texture update call so that snapshot texture is always updated properly | 移除冗余纹理更新调用，确保快照纹理始终正确更新 |
| 2026-04-20 | `766d0ed3` | [VPUtilities & TimeManagement] Moved Timecode custom timestep to the TimeManagement engine module so | 将时间码自定义时间步进移至 TimeManagement 引擎模块 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移 UE_LOG 到 UE_LOGF 宏 |
| 2026-03-09 | `8afaf39f` | Move UVPFullScreenWidget into new non-experimental plugin VirtualProduction/ViewportWidgetOverlay. | 将 UVPFullScreenWidget 移至新的非实验性插件 ViewportWidgetOverlay |
| 2026-02-05 | `25fe0362` | Deprecate FViewportFrame | 废弃 FViewportFrame 功能 |

### 维护评价

**综合评价**：
- **创建时间**：约 7 年前创建，属于老牌插件
- **最近更新**：最近 6 个月内有实质性更新，包括功能优化、重构和废弃标记
- **活跃度**：仍在维护中，但正在逐步将功能迁移到其他模块
- **已知限制**：
  1. 标记为实验性（IsBetaVersion=true）
  2. 默认不启用（Installed=false）
  3. 部分功能已迁移至其他插件（如 ViewportWidgetOverlay）
  4. 存在废弃功能（如 FViewportFrame）
- **推荐使用**：可以作为虚拟制作功能的参考，但生产环境使用需谨慎，建议关注 Epic 的最新虚拟制作工具更新

**警告**：该插件最近有功能迁移和废弃标记，长期使用可能存在兼容性风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProductionUtilities)
- [官方文档]()（无官方文档）
- [测试用例]()（未提供测试用例路径）