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

这是一个面向虚拟制片（Virtual Production）流程的**基础设施插件**。它提供了一系列核心工具和功能，旨在解决虚拟制片场景中的通用性问题，例如：
- **场景导航与标记**：提供书签（Bookmark）系统，用于在复杂虚拟制片场景（如大型LED墙环境、多机位演播室）中快速保存和跳转到关键视角或设置。
- **实用工具与调试**：包含日志记录、视口截图、全屏显示等常用功能，方便现场技术人员进行监控、调试和资产检查。
- **时间码与同步**：为虚拟制片流程提供自定义时间步长（Timestep）支持，处理复杂的时间码同步需求。
- **编辑器扩展**：为上述运行时功能提供配套的编辑器UI和工具，提升制作效率。

简而言之，它是构建特定虚拟制片工作流（如DMX控制、实时合成、多节点同步）之前的**通用工具库**。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `VPBookmark` | Runtime | 核心的虚拟制片书签系统，提供场景标记、导航和状态保存功能。 |
| `VPBookmarkEditor` | Runtime | 为书签系统提供编辑器内的用户界面和交互逻辑。 |
| `VPUtilities` | Runtime | 核心的运行时实用工具库，包含日志、截图、全屏视口、时间码管理等通用功能。 |
| `VPUtilitiesEditor` | Runtime | 为运行时工具提供编辑器内的扩展和UI支持。 |

## 使用场景

- 你正在搭建一个包含大型LED墙和多个摄像机机位的**虚拟制片演播室** → 使用 `VPBookmark` 系统快速标记和切换不同的摄像机预设、光照方案或虚拟场景状态。
- 现场技术总监需要**实时查看和调试**特定视口的画面，或快速捕获屏幕截图发送给远端团队 → 使用 `VPUtilities` 中的全屏视口和截图工具。
- 你的虚拟制片流程需要与**外部设备（如灯光、跟踪系统）进行精确的时间码同步**，并且需要自定义的时间步长逻辑 → 使用 `VPUtilities` 中的时间码相关功能。
- 你正在开发一个复杂的虚拟制片工具链，需要一个**稳定的基础设施**来处理常见的视图管理、状态保存和调试需求，而非从零开始构建 → 将此插件作为底层依赖引入。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Bookmark` | 在当前摄像机位置添加一个新的虚拟制片书签。 | `UVPBookmarkSubsystem` |
| `Jump To Bookmark` | 将当前视图跳转到指定的书签位置。 | `UVPBookmarkSubsystem` |
| `Get All Bookmarks` | 获取场景中所有已保存的书签列表。 | `UVPBookmarkSubsystem` |
| `Get VPUtilitiesWorldSubsystem` | 获取当前世界的 `UVPUtilitiesWorldSubsystem` 实例，用于访问工具函数。 | `UVPUtilitiesLibrary` |
| `Capture Viewport Screenshot` | 捕获当前游戏视口的截图。 | `UVPUtilitiesWorldSubsystem` |

### 使用示例（蓝图描述）

**创建一个快速标记/跳转书签的系统：**
1.  在你的角色或管理器蓝图中，使用 `Get VPUtilitiesWorldSubsystem` 获取子系统引用。
2.  当你需要标记一个摄像机位时（例如，按下一个键），调用该子系统对象的 `Add Bookmark` 函数。你可以通过输入参数为书签命名（如“主舞台-正面”）。
3.  创建一个UI列表（例如使用`ListView`），通过 `Get All Bookmarks` 获取所有书签名称并显示。
4.  当用户在UI中选择一个书签时，调用 `Jump To Bookmark` 函数，摄像机将平滑移动到该位置。
5.  为了调试，你可以绑定一个按键事件，按下时调用 `Capture Viewport Screenshot` 并将图片保存到指定路径。

## C++ 用法

### 头文件引入

```cpp
#include "VPBookmarkSubsystem.h"
#include "VPUtilitiesWorldSubsystem.h"
```

### 基本用法

**操作书签系统：**
```cpp
// 假设在拥有World上下文的Actor中
UVPBookmarkSubsystem* BookmarkSubsystem = GetWorld()->GetSubsystem<UVPBookmarkSubsystem>();
if (BookmarkSubsystem)
{
    // 添加一个书签
    FVPBookmarkCreationParams Params;
    Params.BookmarkName = TEXT("MyNewBookmark");
    BookmarkSubsystem->AddBookmark(Params);

    // 跳转到第一个书签
    TArray<UVPBookmark*> AllBookmarks;
    BookmarkSubsystem->GetAllBookmarks(AllBookmarks);
    if (AllBookmarks.Num() > 0)
    {
        BookmarkSubsystem->JumpToBookmark(AllBookmarks[0]);
    }
}
```

**访问工具子系统：**
```cpp
UVPUtilitiesWorldSubsystem* VPUtilsSubsystem = GetWorld()->GetSubsystem<UVPUtilitiesWorldSubsystem>();
if (VPUtilsSubsystem)
{
    // 请求捕获一帧截图
    VPUtilsSubsystem->CaptureViewportScreenshot(FPaths::ProjectSavedDir() / TEXT("Debug"));
}
```

### 进阶用法

结合书签系统和自定义事件，构建一个状态机：
```cpp
void AMyProductionManager::SaveProductionState(const FString& StateName)
{
    UVPBookmarkSubsystem* BookmarkSubsystem = GetWorld()->GetSubsystem<UVPBookmarkSubsystem>();
    if (BookmarkSubsystem)
    {
        // 删除同名旧状态
        UVPBookmark* ExistingBookmark = BookmarkSubsystem->FindBookmarkByName(StateName);
        if (ExistingBookmark)
        {
            BookmarkSubsystem->RemoveBookmark(ExistingBookmark);
        }
        // 保存新状态（包含当前摄像机位置、旋转等）
        FVPBookmarkCreationParams Params;
        Params.BookmarkName = StateName;
        BookmarkSubsystem->AddBookmark(Params);
        // 你还可以将其他自定义参数（如灯光设置、虚拟场景参数）序列化保存在你自己的系统中，并与此书签名关联。
    }
}
```

## Demo 示例

以下示例展示了如何在C++中创建一个简单的Actor，用于保存和恢复虚拟制片状态。
```cpp
// MyProductionStateActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyProductionStateActor.generated.h"

class UVPBookmarkSubsystem;

UCLASS()
class AMyProductionStateActor : public AActor
{
    GENERATED_BODY()
public:
    AMyProductionStateActor();

    UFUNCTION(BlueprintCallable, Category = "Virtual Production")
    void SaveCurrentState(const FString& StateName);

    UFUNCTION(BlueprintCallable, Category = "Virtual Production")
    void LoadState(const FString& StateName);

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UVPBookmarkSubsystem* BookmarkSubsystem;
};

// MyProductionStateActor.cpp
#include "MyProductionStateActor.h"
#include "VPBookmarkSubsystem.h"

AMyProductionStateActor::AMyProductionStateActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyProductionStateActor::BeginPlay()
{
    Super::BeginPlay();
    BookmarkSubsystem = GetWorld()->GetSubsystem<UVPBookmarkSubsystem>();
}

void AMyProductionStateActor::SaveCurrentState(const FString& StateName)
{
    if (BookmarkSubsystem)
    {
        FVPBookmarkCreationParams Params;
        Params.BookmarkName = StateName;
        BookmarkSubsystem->AddBookmark(Params);
        UE_LOG(LogTemp, Log, TEXT("Saved production state: %s"), *StateName);
    }
}

void AMyProductionStateActor::LoadState(const FString& StateName)
{
    if (BookmarkSubsystem)
    {
        UVPBookmark* Bookmark = BookmarkSubsystem->FindBookmarkByName(StateName);
        if (Bookmark)
        {
            BookmarkSubsystem->JumpToBookmark(Bookmark);
            UE_LOG(LogTemp, Log, TEXT("Loaded production state: %s"), *StateName);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("State '%s' not found."), *StateName);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | 用于处理自定义时间步长和时间码相关的序列化逻辑。 |
| `LevelSequence` | 与关卡序列集成，用于虚拟制片中的场景动画和触发。 |
| `TakeRecorder` | 集成到拍摄记录器中，可能用于在录制过程中添加书签或标记。 |

（*依赖分析基于模块代码和功能推断，实际依赖可能包含更多通用引擎模块。*）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `02b15f1b` | Remove redundant texture update call so that snapshot texture is always updated properly | 优化了视口截图的纹理更新逻辑，确保快照纹理能正确刷新。 |
| 2026-04-20 | `766d0ed3` | [VPUtilities & TimeManagement] Moved Timecode custom timestep to the TimeManagement engine module so | 将自定义时间码步长功能从本插件迁移到了引擎的核心时间管理模块。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件内的日志输出统一迁移到新的UE_LOGF宏。 |
| 2026-03-09 | `8afaf39f` | Move UVPFullScreenWidget into new non-experimental plugin VirtualProduction/ViewportWidgetOverlay. | 将全屏视口控件重构并迁移到了一个新的、非实验性的`ViewportWidgetOverlay`插件中。 |
| 2026-02-05 | `25fe0362` | Deprecate FViewportFrame | 标记`FViewportFrame`结构体为已废弃。 |

### 维护评价

- **活跃维护**：该插件在**最近2个月内**有持续的功能更新、优化和重构，表明仍在积极维护。
- **功能演进**：近期更新显示了清晰的**架构优化**趋势，例如将通用功能（如全屏控件、时间码管理）拆分或迁移到更合适的核心模块，提升了代码的长期可维护性。
- **实验性状态**：插件仍标记为`IsBetaVersion=true`，意味着API和功能未来可能发生变更，不推荐用于最终发布项目。
- **推荐使用**：**推荐**在**开发环境或内部项目**中用于构建虚拟制片工具链的基础。对于需要高度稳定性的生产环境，建议等待其正式毕业（移除Beta标签）或仅依赖其已成熟的子模块（如书签系统）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProductionUtilities)
- **模块文档**：
  - [VPBookmark](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/VirtualProductionUtilities/Source/VPBookmark/VPBookmark.md)
  - [VPBookmarkEditor](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/VirtualProductionUtilities/Source/VPBookmarkEditor/VPBookmarkEditor.md)
  - [VPUtilities](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/VirtualProductionUtilities/Source/VPUtilities/VPUtilities.md)
  - [VPUtilitiesEditor](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/VirtualProductionUtilities/Source/VPUtilitiesEditor/VPUtilitiesEditor.md)