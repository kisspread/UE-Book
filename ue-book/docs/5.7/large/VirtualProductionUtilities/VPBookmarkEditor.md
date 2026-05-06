# VPBookmarkEditor

> Utility classes and functions for Virtual Production

| 属性 | 值 |
|---|---|
| 中文名 | VP 书签编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器 UI、蓝图函数库） |
| 模块 | `VPBookmark` (Runtime), `VPBookmarkEditor` (Runtime), `VPUtilities` (Runtime), `VPUtilitiesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities) | |

## 用法

### 用途

VPBookmarkEditor 模块扩展了 Unreal Editor 内置的书签系统，为虚拟制作工作流提供专门的书签管理功能。它解决了以下问题：

- 在编辑器视口中快速创建、跳转和激活/取消激活虚拟制作书签（`UVPBookmark`）
- 提供一个 Slate UI 控件（`SVPBookmarkListView`），以列表形式展示当前关卡中的所有 VP 书签，并支持点击跳转
- 通过蓝图暴露常用的编辑器书签操作，方便美术或导演在脚本中调用

该模块与 `VPBookmark` 运行时模块紧密配合，后者定义了书签数据结构和上下文。

### 使用场景

- 虚拟拍摄过程中，需要在多个摄像机预设位（机位、云台参数）之间快速切换，可以将每个机位保存为一个 VP 书签，并在 `SVPBookmarkListView` 中集中管理。
- 在定序器（Sequencer）或蓝图逻辑中，需要根据条件跳转到特定书签视角，可以使用 `UVPBookmarkEditorBlueprintLibrary` 提供的蓝图函数。
- 开发者希望让编辑器视口自动跟随某个书签，或者响应书签的激活/取消激活事件，可以监听 `FVPBookmarkTypeActions::OnBookmarkActivated` 等委托。

## 蓝图用法

本模块提供了 `UVPBookmarkEditorBlueprintLibrary` 蓝图函数库，包含四个可直接在蓝图图表中调用的静态函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `JumpToBookmarkInLevelEditor` | 跳转到指定书签对应的视口位置（即激活该书签） | `UVPBookmarkEditorBlueprintLibrary` |
| `JumpToBookmarkInLevelEditorByIndex` | 按索引跳转到当前关卡队列中的第 `BookmarkIndex` 个书签 | `UVPBookmarkEditorBlueprintLibrary` |
| `AddBookmarkAtCurrentLevelEditorPosition` | 在当前水平编辑器视口位置创建一个新的 VP 书签，并返回生成的书签 Actor | `UVPBookmarkEditorBlueprintLibrary` |
| `GetAllActorsClassThamImplementsVPBookmarkInterface` | 获取所有实现了 `VPBookmarkInterface` 的 Actor 类（用于创建书签时选择类型） | `UVPBookmarkEditorBlueprintLibrary` |

### 使用示例（蓝图描述）

以“在关卡蓝图中为当前视口添加书签”为例：

1. 在关卡蓝图或自定义 Blueprint Function Library 中，拖出 `AddBookmarkAtCurrentLevelEditorPosition` 节点。
2. 连接 `ActorClass` 引脚：使用 `GetAllActorsClassThamImplementsVPBookmarkInterface` 的输出，或直接选择一个具体的 Actor 子类（如 `VPBookmarkActor`）。
3. 设置 `CreationContext`：创建一个 `FVPBookmarkCreationContext` 结构体（可从 VPBookmark 模块获取），填入必要信息（如创建者、意图等）。
4. 设置 `Offset`（相对视口位置的偏移向量）和 `bFlattenRotation`（是否展平旋转，通常为 true）。
5. 执行节点后，书签 Actor 会出现在当前视口位置，并自动添加到书签列表。

## C++ 用法

### 头文件引入

```cpp
#include "VPBookmarkEditorBlueprintLibrary.h"
#include "VPBookmarkEditorModule.h"
#include "VPBookmarkTypeActions.h"
#include "SVPBookmarkListView.h"
```

### 基本用法

**1. 跳转到书签（C++）**

```cpp
#include "VPBookmark.h"
#include "VPBookmarkEditorBlueprintLibrary.h"

void MyFunction()
{
    // 假设有一个 UVPBookmark* Bookmark
    UVPBookmark* MyBookmark = ...;
    bool bSuccess = UVPBookmarkEditorBlueprintLibrary::JumpToBookmarkInLevelEditor(MyBookmark);
    // 如果成功，编辑器视口将移动到该书签保存的位置
}
```

*来源：头文件 `VPBookmarkEditorBlueprintLibrary.h`*

**2. 获取所有支持 VP 书签接口的 Actor 类**

```cpp
#include "VPBookmarkEditorBlueprintLibrary.h"

TArray<TSubclassOf<AActor>> ActorClasses;
UVPBookmarkEditorBlueprintLibrary::GetAllActorsClassThamImplementsVPBookmarkInterface(ActorClasses);
// ActorClasses 包含所有实现了 VPBookmarkInterface 的 Actor 类
```

**3. 使用自定义书签类型动作**

在模块的 `StartupModule` 中向编辑器书签系统注册：

```cpp
// 在你的 IModuleInterface::StartupModule() 中
void FMyEditorModule::StartupModule()
{
    // 获取 VPBookmarkEditor 模块的单例
    FVPBookmarkEditorModule& VPBookmarkEditorModule = FModuleManager::LoadModuleChecked<FVPBookmarkEditorModule>("VPBookmarkEditor");
    
    // 注册自定义书签类型动作（如果类型动作尚未注册，此操作通常由 VPBookmarkEditorModule 自动完成）
    if (TSharedPtr<FVPBookmarkTypeActions> BookmarkActions = VPBookmarkEditorModule.BookmarkTypeActions)
    {
        // 可以绑定自己的回调
        BookmarkActions->OnBookmarkActivated.AddLambda([](UVPBookmark* Bookmark) {
            // 书签被激活时的自定义逻辑
        });
    }
}
```

*来源：头文件 `VPBookmarkEditorModule.h`、`VPBookmarkTypeActions.h`*

### 进阶用法

**监听书签激活/取消激活事件**

`FVPBookmarkTypeActions` 公开了两个多播委托：

```cpp
DECLARE_MULTICAST_DELEGATE_OneParam(FVPBookmarkActivated, UVPBookmark*);
DECLARE_MULTICAST_DELEGATE_OneParam(FVPBookmarkDeactivated, UVPBookmark*);
```

你可以为这些委托添加回调，以获得书签切换时的通知。例如，用于同步 UI 或其他系统状态。

```cpp
#include "VPBookmarkTypeActions.h"

void RegisterBookmarkCallbacks()
{
    FVPBookmarkEditorModule& Module = FModuleManager::LoadModuleChecked<FVPBookmarkEditorModule>("VPBookmarkEditor");
    if (Module.BookmarkTypeActions.IsValid())
    {
        Module.BookmarkTypeActions->OnBookmarkActivated.AddLambda([](UVPBookmark* Bookmark) {
            UE_LOG(LogVPBookmarkEditor, Display, TEXT("书签 %s 被激活"), *Bookmark->GetName());
        });
        Module.BookmarkTypeActions->OnBookmarkDeactivated.AddLambda([](UVPBookmark* Bookmark) {
            UE_LOG(LogVPBookmarkEditor, Display, TEXT("书签 %s 被取消激活"), *Bookmark->GetName());
        });
    }
}
```

**创建书签列表控件**

```cpp
// 在 Slate UI 中放置 SVPBookmarkListView
SAssignNew(MyBookmarkList, SVPBookmarkListView);
// 控件会自动填充当前关卡的所有 VP 书签，并支持点击跳转
```

*来源：头文件 `SVPBookmarkListView.h`*

## Demo 示例

下面是一个最小的编辑器模块示例，演示如何集成 VPBookmarkEditor 的功能。假设你有一个名为 `MyVPTools` 的编辑器模块，并已正确设置依赖。

### MyVPToolsModule.h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"
#include "Modules/ModuleManager.h"

class FMyVPToolsModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### MyVPToolsModule.cpp

```cpp
#include "MyVPToolsModule.h"
#include "VPBookmarkEditorModule.h"
#include "VPBookmarkTypeActions.h"
#include "VPBookmarkEditorBlueprintLibrary.h"
#include "VPBookmark.h"

IMPLEMENT_MODULE(FMyVPToolsModule, MyVPTools)

void FMyVPToolsModule::StartupModule()
{
    // 加载 VPBookmarkEditor 模块并获取其类型动作实例
    FVPBookmarkEditorModule& VPBookmarkEditorModule = FModuleManager::LoadModuleChecked<FVPBookmarkEditorModule>("VPBookmarkEditor");
    
    if (VPBookmarkEditorModule.BookmarkTypeActions.IsValid())
    {
        // 绑定书签激活事件
        VPBookmarkEditorModule.BookmarkTypeActions->OnBookmarkActivated.AddLambda([](UVPBookmark* Bookmark)
        {
            UE_LOG(LogTemp, Log, TEXT("Demo: 书签 %s 被激活！"), *Bookmark->GetName());
        });
    }

    // 示例：在启动时获取所有支持 VP 接口的 Actor 类并打印
    TArray<TSubclassOf<AActor>> Classes;
    UVPBookmarkEditorBlueprintLibrary::GetAllActorsClassThamImplementsVPBookmarkInterface(Classes);
    for (auto& Cls : Classes)
    {
        UE_LOG(LogTemp, Log, TEXT("Demo: 支持 VP 书签的 Actor 类: %s"), *Cls->GetName());
    }
}

void FMyVPToolsModule::ShutdownModule()
{
    // 清理委托绑定等
}
```

**编译说明**：你的模块的 `Build.cs` 需要包含以下公共依赖（见“模块依赖”表格）。此示例未展示书签列表 UI，但可以类似地创建 `SVPBookmarkListView` 实例。

## 模块依赖

由于缺少原始 `Build.cs` 文件，以下是基于头文件包含和 UE 常见依赖推断的依赖项。请注意，实际依赖以引擎源码中的 `VPBookmarkEditor.Build.cs` 为准，此处仅列出非标准模块。

| 模块 | 用途 |
|---|---|
| `VPBookmark` | 提供 `UVPBookmark`、`FVPBookmarkCreationContext` 等运行时数据结构，为书签编辑功能提供基础类型 |
| `Bookmarks` | 编辑器模块，提供 `IBookmarkTypeActions` 接口和书签系统核心 |
| `UnrealEd` | 编辑器核心，用于访问 `FEditorViewportClient`、视口操作等 |
| `LevelEditor` | 提供编辑器主视口的访问和交互（`SVPBookmarkListView` 可能依赖 `SLevelViewport`） |
| `Slate` / `SlateCore` | UI 控件的渲染和输入（`SVPBookmarkListView` 使用） |

**省略的常见依赖**（已自动包含）：`Core`, `CoreUObject`, `Engine`, `InputCore`, `PropertyEditor` 等。

## 维护状态

### 近期更新

基于提供的 Git 历史（最近 5 次，来自 VirtualProductionUtilities 仓库，影响整个插件）：

- 2025-10-03 `e6b66964` — Fix full screen widget for media output providers.（修复媒体输出全屏控件，可能非本模块）
- 2025-09-25 `4b556c0e` — VPUtilities OSC Server - Allow specifying an override for the server address.（OSC 服务器功能，非本模块）
- 2025-09-23 `66f6004f` — ViewportInteraction: Deprecate ViewportInteraction module alongside VR Editor.（弃用视口交互模块，相关影响未知）
- 2025-09-10 `cb5faa0b` — VR Editor: Deprecate VR Editor mode and most associated classes.（弃用 VR 编辑器，可能与书签功能无关）
- 2025-08-27 `551d3a5b` — Address bug hawk and CIS deprecation warnings.（修复静态分析警告）

### 维护评价

- **创建时间**：2025-08-27（约 2 个月前）
- **最近更新频率**：有多次提交，集中在 2025 年 8 月至 10 月，说明项目处于活跃开发阶段。
- **目前状态**：插件标记为“实验性”（`IsBetaVersion: true`），代码仍在迭代。最近几次提交并未直接修改 VPBookmarkEditor 模块的核心逻辑，但整个插件在持续维护。
- **已知问题/限制**：实验性插件可能存在 API 不稳定的风险；当前未发现明显限制。
- **推荐使用**：可作为虚拟制作工作流的辅助工具，但建议关注未来版本可能的 API 变化。对于生产项目，建议等待正式版或自行封装。

**综合评价**：该模块较为年轻，处于快速迭代期，功能基本可用。适合测试和原型开发，但不建议在稳定性要求极高的生产环境中直接依赖，除非同步跟进引擎源更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities)
- [VPBookmark 运行时模块文档](https://docs.unrealengine.com/5.7/.../)（暂缺官方文档，建议查看引擎源代码中的 VPBookmark 模块说明）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities/Source/VPBookmarkEditor/Tests)（如果存在）