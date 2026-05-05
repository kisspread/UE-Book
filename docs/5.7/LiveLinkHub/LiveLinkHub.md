# Live Link Hub

> LiveLink Hub allows streaming of animated data into Unreal Engine or UEFN

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkHub` (Runtime), `LiveLinkHubEditor` (Runtime), `LiveLinkHubMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkHub) | |

## 用途

LiveLinkHub 是一个独立的桌面应用程序，充当 LiveLink 数据的中央枢纽。它解决了在复杂制作流程中，需要集中管理、路由和录制来自多个动画数据源（如动作捕捉设备、虚拟摄像机等）并将其分发给多个 Unreal Engine 或 UEFN 客户端的问题。它不仅仅是一个插件，而是一个完整的应用程序框架，提供了独立的 UI、会话管理、客户端连接管理和录制功能。

## 使用场景

- 你正在领导一个大型虚拟制片项目，需要将来自不同供应商的多个动捕设备的数据统一接收、管理，并分发给场景中不同的 UE 实例。
- 你需要一个独立的工具来录制和回放 LiveLink 数据，而不依赖于某个特定的 UE 编辑器实例。
- 你的工作流程需要一个中央控制点，用于监控所有连接的 LiveLink 源和客户端的状态。
- 你需要为 LiveLinkHub 创建自定义的布局和功能模块，以适应特定的制作管线。

## 蓝图用法

LiveLinkHub 主要是一个 C++ 和 Slate 驱动的应用程序，其核心功能通过 C++ 接口和模块化特性（Modular Features）暴露。直接在蓝图中使用的节点非常有限，主要集中在会话控制和数据查询上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Session Name` | 获取当前录制会话的名称 | `ILiveLinkRecordingSession` |
| `Set Session Name` | 设置当前录制会话的名称 | `ILiveLinkRecordingSession` |
| `Get Slate Name` | 获取当前 Slate 名称 | `ILiveLinkRecordingSession` |
| `Set Slate Name` | 设置当前 Slate 名称 | `ILiveLinkRecordingSession` |
| `Get Take Number` | 获取当前 Take 编号 | `ILiveLinkRecordingSession` |
| `Set Take Number` | 设置当前 Take 编号 | `ILiveLinkRecordingSession` |
| `Is Recording` | 查询当前是否正在录制 | `ILiveLinkRecordingSession` |
| `Start Recording` | 开始录制会话 | `ILiveLinkRecordingSession` |
| `Stop Recording` | 停止录制会话 | `ILiveLinkRecordingSession` |

### 使用示例（蓝图描述）

由于 LiveLinkHub 是独立应用，蓝图通常用于在 UE 编辑器或游戏内与 Hub 交互。例如，你可以在一个 UE 编辑器工具中，通过获取 `ILiveLinkRecordingSession` 的模块化特性实例，来远程控制 Hub 的录制会话。

1.  在你的蓝图中，使用 `Get Modular Feature` 节点，特性名称为 `"LiveLinkRecordingSession"`。
2.  将返回的对象转换为 `ILiveLinkRecordingSession` 接口。
3.  调用 `Start Recording` 或 `Stop Recording` 来控制录制。
4.  绑定 `On Recording Started` 和 `On Recording Stopped` 委托来响应状态变化。

## C++ 用法

### 头文件引入

```cpp
#include "ILiveLinkRecordingSession.h"
#include "ILiveLinkHubModule.h"
#include "LiveLinkHubApplicationMode.h"
#include "LiveLinkHubSessionExtraData.h"
```

### 基本用法：控制录制会话

通过模块化特性接口与 LiveLinkHub 的录制会话交互。

```cpp
// 来源: Engine/Plugins/Animation/LiveLinkHub/Source/LiveLinkHub/Public/ILiveLinkRecordingSession.h
#include "Features/IModularFeatures.h"
#include "ILiveLinkRecordingSession.h"

void ControlLiveLinkHubRecording()
{
    // 检查 LiveLinkRecordingSession 特性是否可用
    IModularFeatures& ModularFeatures = IModularFeatures::Get();
    if (ModularFeatures.IsModularFeatureAvailable(ILiveLinkRecordingSession::GetModularFeatureName()))
    {
        // 获取特性实例（通常只有一个）
        ILiveLinkRecordingSession& Session = ILiveLinkRecordingSession::Get();

        // 设置会话信息
        Session.SetSessionName(TEXT("MySession"));
        Session.SetSlateName(TEXT("Shot01"));
        Session.SetTakeNumber(1);

        // 开始录制
        if (Session.CanRecord())
        {
            Session.StartRecording();
        }

        // 绑定委托以监听状态变化
        Session.OnRecordingStarted().AddLambda([]()
        {
            UE_LOG(LogTemp, Log, TEXT("LiveLinkHub recording started!"));
        });

        Session.OnRecordingStopped().AddLambda([]()
        {
            UE_LOG(LogTemp, Log, TEXT("LiveLinkHub recording stopped!"));
        });
    }
}
```

### 进阶用法：扩展 LiveLinkHub 应用程序模式

LiveLinkHub 的核心扩展点是 `ILiveLinkHubApplicationModeFactory`，允许你注册自定义的布局和功能。

```cpp
// 来源: Engine/Plugins/Animation/LiveLinkHub/Source/LiveLinkHub/Public/LiveLinkHubApplicationMode.h
#include "LiveLinkHubApplicationMode.h"
#include "Features/IModularFeatures.h"

// 1. 定义你的自定义应用模式
class FMyCustomLiveLinkMode : public FLiveLinkHubApplicationMode
{
public:
    FMyCustomLiveLinkMode(TSharedPtr<FLiveLinkHubApplicationBase> InApp)
        : FLiveLinkHubApplicationMode(FName("MyCustomMode"), NSLOCTEXT("MyMode", "DisplayName", "My Custom Mode"), InApp)
    {
        // 在这里定义你的布局和标签页工厂
        TabLayout = FTabManager::NewLayout("MyCustomMode_v1")
            ->AddArea(FTabManager::NewPrimaryArea()
                ->Split(FTabManager::NewStack()
                    ->AddTab("MyCustomTab", ETabState::OpenedTab)
                )
            );
    }

    // 可选：覆盖图标和工具栏
    virtual FSlateIcon GetModeIcon() const override
    {
        return FSlateIcon(FAppStyle::GetAppStyleSetName(), "LevelEditor.Tabs.Viewports");
    }

    virtual TArray<TSharedRef<SWidget>> GetToolbarWidgets_Impl() override
    {
        // 返回你希望在工具栏显示的控件
        return {};
    }
};

// 2. 定义工厂来创建你的模式
class FMyCustomLiveLinkModeFactory : public ILiveLinkHubApplicationModeFactory
{
public:
    virtual TSharedRef<FLiveLinkHubApplicationMode> CreateLiveLinkHubAppMode(TSharedPtr<FLiveLinkHubApplicationBase> InApp) override
    {
        return MakeShared<FMyCustomLiveLinkMode>(InApp);
    }
};

// 3. 在你的模块启动时注册工厂
void FMyModule::StartupModule()
{
    IModularFeatures::Get().RegisterModularFeature(ILiveLinkHubApplicationModeFactory::ModularFeatureName, &MyFactory);
}

void FMyModule::ShutdownModule()
{
    IModularFeatures::Get().UnregisterModularFeature(ILiveLinkHubApplicationModeFactory::ModularFeatureName, &MyFactory);
}
```

## Demo 示例

以下示例展示如何创建一个最简单的 LiveLinkHub 自定义应用模式插件。

**MyLiveLinkHubMode.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "LiveLinkHubApplicationMode.h"

class FMyLiveLinkHubMode : public FLiveLinkHubApplicationMode
{
public:
    FMyLiveLinkHubMode(TSharedPtr<FLiveLinkHubApplicationBase> InApp);
};
```

**MyLiveLinkHubMode.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#include "MyLiveLinkHubMode.h"
#include "Styling/SlateIconFinder.h"

#define LOCTEXT_NAMESPACE "MyLiveLinkHubMode"

FMyLiveLinkHubMode::FMyLiveLinkHubMode(TSharedPtr<FLiveLinkHubApplicationBase> InApp)
    : FLiveLinkHubApplicationMode(FName("MySimpleMode"), LOCTEXT("ModeName", "Simple Mode"), InApp)
{
    // 定义一个简单的布局，只包含一个默认标签页
    TabLayout = FTabManager::NewLayout("MySimpleMode_v1")
        ->AddArea(FTabManager::NewPrimaryArea()
            ->Split(FTabManager::NewStack()
                ->AddTab(UE::LiveLinkHub::SourcesTabId, ETabState::OpenedTab)
            )
        );
}

#undef LOCTEXT_NAMESPACE
```

**MyLiveLinkHubModeFactory.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "LiveLinkHubApplicationMode.h"

class FMyLiveLinkHubModeFactory : public ILiveLinkHubApplicationModeFactory
{
public:
    virtual TSharedRef<FLiveLinkHubApplicationMode> CreateLiveLinkHubAppMode(TSharedPtr<FLiveLinkHubApplicationBase> InApp) override;
};
```

**MyLiveLinkHubModeFactory.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#include "MyLiveLinkHubModeFactory.h"
#include "MyLiveLinkHubMode.h"

TSharedRef<FLiveLinkHubApplicationMode> FMyLiveLinkHubModeFactory::CreateLiveLinkHubAppMode(TSharedPtr<FLiveLinkHubApplicationBase> InApp)
{
    return MakeShared<FMyLiveLinkHubMode>(InApp);
}
```

**MyLiveLinkHubPlugin.cpp (模块启动)**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#include "Modules/ModuleManager.h"
#include "Features/IModularFeatures.h"
#include "MyLiveLinkHubModeFactory.h"

class FMyLiveLinkHubPluginModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        IModularFeatures::Get().RegisterModularFeature(ILiveLinkHubApplicationModeFactory::ModularFeatureName, &ModeFactory);
    }

    virtual void ShutdownModule() override
    {
        IModularFeatures::Get().UnregisterModularFeature(ILiveLinkHubApplicationModeFactory::ModularFeatureName, &ModeFactory);
    }

private:
    FMyLiveLinkHubModeFactory ModeFactory;
};

IMPLEMENT_MODULE(FMyLiveLinkHubPluginModule, MyLiveLinkHubPlugin)
```

## 模块依赖

要使用或扩展 LiveLinkHub，你的模块通常需要依赖以下模块。具体依赖取决于你要实现的功能。

| 模块 | 用途 |
|---|---|
| `LiveLink` | LiveLink 核心框架，提供主题、源、控制器等基础概念。 |
| `LiveLinkHub` | LiveLinkHub 应用程序核心，提供 `ILiveLinkHubModule`, `ILiveLinkRecordingSession` 等接口。 |
| `LiveLinkHubMessaging` | 处理 Hub 与客户端（UE 实例）之间的网络消息通信。 |
| `Slate`, `SlateCore` | 构建自定义 UI 和布局。 |
| `WorkflowOrientedApp` | 提供 `FWorkflowCentricApplication`, `FApplicationMode` 等应用程序框架类。 |
| `Messaging` | Epic 的消息传递框架，用于进程间通信。 |

## 维护状态

### 近期更新

```
- a7972c2de4c4 LiveLinkHub - Fix crash when trying to save over old recording in Standalone version of LiveLinkHub
- ad4d60bd3dde LiveLinkHub - Fix crash recovery prompt not being sent to the foreground
- 9b414a8dd0d0 LiveLinkHub - Fix using wrong PropertyEditorModule method to unregister struct customizations
```

近期提交均为稳定性修复，解决了独立版本保存录制时崩溃、崩溃恢复提示窗口焦点以及属性编辑器注销错误的问题。这表明团队正在积极修复用户报告的问题。

### 维护评价

LiveLinkHub 是一个相对较新的插件（创建于 2024 年初），目前仍处于 **Beta** 状态（`IsBetaVersion: true`）。从近期提交记录看，它正在被积极维护，主要集中在修复关键的崩溃和稳定性问题上。作为 Epic Games 官方推出的工具，其长期支持和更新是有保障的。

**推荐使用**：如果你需要一个独立的、功能完整的 LiveLink 数据管理中枢，LiveLinkHub 是官方推荐的选择。但需注意其 Beta 状态，可能会遇到一些不稳定或未完成的功能。建议在关键生产流程中谨慎评估，并及时更新到最新版本以获取稳定性修复。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkHub)
- 官方文档（暂无）
- 测试用例（暂未在提供的信息中发现）