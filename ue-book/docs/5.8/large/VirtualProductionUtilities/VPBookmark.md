# Virtual Production Utilities

> Utility classes and functions for Virtual Production

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制作工具集 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（源码） |
| 模块 | `VPBookmark` (Runtime), `VPBookmarkEditor` (Runtime), `VPUtilities` (Runtime), `VPUtilitiesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProductionUtilities) | |

## 用途

此插件为虚幻引擎的虚拟制作工作流提供了一系列实用的工具类和函数。其核心功能围绕 **VPBookmark** 子系统展开，它提供了一种在关卡内为特定Actor创建“书签”的机制，这些书签不仅保存了摄像机/视口的位置、旋转和缩放信息（用于快速跳转），还存储了创建上下文（如创建者、分类、名称）并与一个Actor关联，用于在虚拟制片环境中快速定位、标记和管理场景中的关键位置或对象。它提供蓝图库和生命周期委托，方便在蓝图和C++中与之交互。其他模块（如`VPUtilities`）则可能包含处理时间码、Widget显示等相关的辅助功能。

## 使用场景

- 你正在使用虚拟制作流程（如LED墙或绿幕拍摄），需要在场景中快速标记和跳转到关键的摄像机位置或参考点。
- 你需要在多人协作（通过Concert）的虚拟制作环境中同步和查看其他人创建的场景书签。
- 你想要通过蓝图或C++自动化地管理书签的创建、查询和激活状态。
- 你需要处理自定义的时间码（Timecode）步进或与时间码相关的工具函数。

## 蓝图用法

### 核心节点

主要功能封装在 `UVPBookmarkBlueprintLibrary` 和 `IVPBookmarkProvider` 接口中。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find VP Bookmark` | 查找与指定Actor关联的VPBookmark。 | `UVPBookmarkBlueprintLibrary` |
| `Get All VP Bookmark Actors` | 获取场景中所有拥有VPBookmark的Actor。 | `UVPBookmarkBlueprintLibrary` |
| `Get All VP Bookmark` | 获取场景中所有的VPBookmark对象。 | `UVPBookmarkBlueprintLibrary` |
| `Create VP Bookmark Name` | 根据格式字符串和现有书签，生成一个唯一的书签名称（包含数字和字母后缀）。 | `UVPBookmarkBlueprintLibrary` |
| `Is Active` | 查询书签是否处于激活状态。 | `UVPBookmark` |
| `Get Bookmark Index` | 获取书签的索引号。 | `UVPBookmark` |
| `Get Associated Bookmark Actor` | 获取与书签关联的Actor。 | `UVPBookmark` |
| `Get Display Name` | 获取书签的显示名称。 | `UVPBookmark` |
| `On Bookmark Activation` | （事件）当书签被激活或停用时调用。 | `IVPBookmarkProvider` |
| `On Bookmark Changed` | （事件）当书签数据发生变化时调用。 | `IVPBookmarkProvider` |

### 使用示例（蓝图描述）

1.  **查询Actor的书签**：在任意Actor的蓝图中，使用 `Find VP Bookmark` 节点，传入 `Self` 作为Actor参数，即可获取关联的书签对象。
2.  **列出场景中所有书签**：使用 `Get All VP Bookmark` 节点（需提供世界上下文对象，如玩家控制器），输出一个 `UVPBookmark` 数组，遍历该数组即可获取每个书签的详细信息（位置、名称等）。
3.  **监听书签事件**：创建一个蓝图类（如一个空的Actor），在类设置中实现 `IVPBookmarkProvider` 接口。然后在事件图表中，你可以看到 `On Bookmark Activation` 和 `On Bookmark Changed` 等事件，可以在其中添加逻辑以响应书签状态的变化。

## C++ 用法

### 头文件引入

```cpp
#include "VPBookmark.h"
#include "VPBookmarkBlueprintLibrary.h"
#include "IVPBookmarkProvider.h"
```

### 基本用法

查询和操作书签。
（来源：基于 `VPBookmarkBlueprintLibrary.h` 和 `VPBookmark.h` 推断）

```cpp
// 假设你有一个指向当前世界上下文的指针 UObject* WorldContextObject 和一个 AActor* MyActor

// 1. 查找一个Actor关联的书签
UVPBookmark* Bookmark = UVPBookmarkBlueprintLibrary::FindVPBookmark(MyActor);
if (Bookmark)
{
    // 检查书签是否激活
    bool bActive = Bookmark->IsActive();
    
    // 获取书签的视口数据（位置、旋转）
    const FVPBookmarkViewportData& ViewportData = Bookmark->CachedViewportData;
    FVector Location = ViewportData.JumpToOffsetLocation;
    FRotator Rotation = ViewportData.LookRotation;
}

// 2. 获取场景中所有书签
TArray<UVPBookmark*> AllBookmarks;
UVPBookmarkBlueprintLibrary::GetAllVPBookmark(WorldContextObject, AllBookmarks);
for (UVPBookmark* Bk : AllBookmarks)
{
    UE_LOG(LogTemp, Log, TEXT("Bookmark Name: %s"), *Bk->GetDisplayName().ToString());
}
```

### 进阶用法

实现 `IVPBookmarkProvider` 接口以响应书签事件。
（来源：基于 `IVPBookmarkProvider.h` 推断）

```cpp
// 在你的类声明中继承接口
class AMyBookmarkListener : public AActor, public IVPBookmarkProvider
{
    GENERATED_BODY()
public:
    // 实现接口函数
    virtual void OnBookmarkActivation_Implementation(UVPBookmark* Bookmark, bool bActivate) override
    {
        if (bActivate)
        {
            UE_LOG(LogTemp, Warning, TEXT("Bookmark %s activated!"), *Bookmark->GetDisplayName().ToString());
        }
    }

    virtual void OnBookmarkChanged_Implementation(UVPBookmark* Bookmark) override
    {
        UE_LOG(LogTemp, Warning, TEXT("Bookmark %s changed!"), *Bookmark->GetDisplayName().ToString());
    }
    // ... 其他接口函数的实现 ...
};
```

## Demo 示例

一个最小示例：在Actor中查询并打印关联书签的信息。

```cpp
// MyBookmarkActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyBookmarkActor.generated.h"

class UVPBookmark;

UCLASS()
class AMyBookmarkActor : public AActor
{
    GENERATED_BODY()
public:
    // 在编辑器中点击或蓝图中调用时，查询并打印书签信息
    UFUNCTION(BlueprintCallable, CallInEditor)
    void PrintAssociatedBookmarkInfo();

private:
    // 缓存找到的书签指针
    UPROPERTY(Transient)
    TObjectPtr<UVPBookmark> CachedBookmark;
};
```

```cpp
// MyBookmarkActor.cpp
#include "MyBookmarkActor.h"
#include "VPBookmarkBlueprintLibrary.h"
#include "VPBookmark.h"

void AMyBookmarkActor::PrintAssociatedBookmarkInfo()
{
    CachedBookmark = UVPBookmarkBlueprintLibrary::FindVPBookmark(this);
    if (CachedBookmark)
    {
        FText Name = CachedBookmark->GetDisplayName();
        FVector Loc = CachedBookmark->CachedViewportData.JumpToOffsetLocation;
        UE_LOG(LogTemp, Warning, TEXT("Associated Bookmark: '%s' at Location: %s"), *Name.ToString(), *Loc.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No bookmark associated with this actor."));
    }
}
```

## 模块依赖

要使用此插件的功能，你的模块通常需要依赖 `VPBookmark` 模块。在你的 `.Build.cs` 文件中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "VPBookmark" // 书签核心功能
});
```

如果需要更底层的虚拟制作功能，可能需要依赖 `VPUtilities`。

| 模块 | 用途 |
|---|---|
| `MovieScene` | `VPBookmark` 模块依赖它，用于可能与Sequencer或时间线相关的书签功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `02b15f1b` | Remove redundant texture update call so that snapshot texture is always updated properly | 移除冗余纹理更新调用，确保快照纹理能正确更新。 |
| 2026-04-20 | `766d0ed3` | [VPUtilities & TimeManagement] Moved Timecode custom timestep to the TimeManagement engine module so | 将自定义时间码步进功能从VPUtilities移至引擎的TimeManagement模块。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的UE_LOG日志宏迁移为新的UE_LOGF格式。 |
| 2026-03-09 | `8afaf39f` | Move UVPFullScreenWidget into new non-experimental plugin VirtualProduction/ViewportWidgetOverlay. | 将全屏Widget类迁移到新的非实验性插件ViewportWidgetOverlay中。 |
| 2026-02-05 | `25fe0362` | Deprecate FViewportFrame | 标记`FViewportFrame`为过时。 |

### 维护评价

该插件创建于2019年初，是一个**老古董**级别的实验性插件。尽管其 `.uplugin` 明确标记为 `IsBetaVersion: true`，但从近期的提交历史看，它在2026年初仍有**活跃的维护和重构**。近期的提交主要涉及**代码优化**（如纹理更新、日志宏迁移）和**功能迁移**（将Widget和时间码相关功能移至更合适的独立模块），这表明 Epic 团队仍在对其进行优化和整理，以融入更广泛的虚拟制作架构中。

**综合评价**：
- **状态**：维护中，但有向更成熟、非实验性架构迁移的趋势。
- **推荐度**：可以尝试使用其核心书签功能，但需注意其`Beta`状态以及API可能随架构调整而发生变化。对于生产环境，建议密切关注其未来的重构和正式发布状态。核心的`VPBookmark`功能相对稳定和实用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProductionUtilities)
- [官方文档]() （无）
- [测试用例]() （未在提供信息中发现明确测试文件路径）