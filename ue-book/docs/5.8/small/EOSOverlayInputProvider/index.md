# EOS Overlay Input Provider

> Responsible for providing input forwarding to the EOSSDK Overlay.

| 属性 | 值 |
|---|---|
| 中文名 | EOS叠加层输入提供 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `EOSOverlayInputProvider` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-16 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/EOSOverlayInputProvider) | |

## 用途

该插件的核心功能是作为 Epic Online Services (EOS) SDK 叠加层（Overlay）与游戏输入系统之间的桥梁。当 EOS 叠加层（例如好友列表、成就查看器、商城等）被激活时，它需要能够接收用户的鼠标、键盘和手柄输入，以便用户可以在叠加层内进行交互。与此同时，游戏通常需要停止处理这些输入，以避免误操作或冲突。

`EOSOverlayInputProvider` 通过实现一个输入预处理器（`IInputProcessor`），拦截来自 Slate 应用程序的所有原始输入事件。它会将这些输入状态信息转发给 `EOSSDK`，并根据叠加层的状态（是否处于独占输入模式）决定是否允许这些输入事件继续传递到游戏的输入系统中。这解决了集成 EOS 社交功能时，叠加层与游戏输入焦点管理的兼容性问题。

## 使用场景

- 你的游戏集成了 Epic Online Services，并且启用了其社交叠加层功能。
- 当玩家打开 EOS 叠加层时，需要确保叠加层能正常接收鼠标点击、键盘按键和手柄操作，同时游戏停止响应这些输入。
- 你正在开发一个需要与 EOS 社交功能（如邀请好友、查看成就）深度集成的在线游戏。

## 蓝图用法

无（此插件不提供蓝图接口，其功能在插件启动时自动通过输入处理器集成）。

## C++ 用法

### 头文件引入

该插件不设计为被外部模块直接调用其API，其核心功能在插件内部的输入处理器中实现。使用者通常无需引入其头文件。

### 基本用法

该插件的工作是自动化的。一旦在项目中启用，其模块（`FEOSOverlayInputProviderModule`）在启动时会创建一个输入预处理器（`FEOSOverlayInputProviderPreProcessor`）并注册到 `FSlateApplication` 中。

以下是模块注册输入处理器的核心逻辑概念（来源于 `EOSOverlayInputProviderModule.cpp`）：

```cpp
void FEOSOverlayInputProviderModule::StartupModule()
{
    // ... 省略部分初始化代码 ...
    
    // 创建输入预处理器实例
    InputPreprocessor = MakeShared<FEOSOverlayInputProviderPreProcessor>();
    InputPreprocessor->Initialize();

    // 将处理器注册到 Slate 应用程序，以便拦截输入
    if (FSlateApplication::IsInitialized())
    {
        FSlateApplication::Get().RegisterInputPreProcessor(InputPreprocessor);
    }
    // ... 其他逻辑 ...
}
```

### 进阶用法

输入处理器（`FEOSOverlayInputProviderPreProcessor`）的核心逻辑是处理各种输入事件。以下是一个处理按键按下的简化示例（来源于 `EOSOverlayInputProviderPreProcessor.cpp`）：

```cpp
bool FEOSOverlayInputProviderPreProcessor::HandleKeyDownEvent(FSlateApplication& SlateApp, const FKeyEvent& InKeyEvent)
{
    // 检查是否支持报告输入状态，以及 EOS 叠加层是否在独占输入模式
    if (!bIsReportInputStateSupported || !bIsExclusiveInput)
    {
        // 如果不处于独占输入模式，允许输入事件继续传递给游戏
        return false;
    }
    
    // 将 UE 的按键映射到 EOS SDK 的按钮标志
    const TMap<FKey, EOS_UI_EInputStateButtonFlags>& KeyMap = GetUEKeyToEOSKeyMap();
    EOS_UI_EInputStateButtonFlags* ButtonFlagPtr = KeyMap.Find(InKeyEvent.GetKey());
    
    if (ButtonFlagPtr)
    {
        // 构建并报告输入状态给 EOS SDK
        FEOSInputState& InputState = GetCurrentInputState(InKeyEvent.GetUserIndex());
        InputState.WithButtonDownFlags(static_cast<EOS_UI_EInputStateButtonFlags>(
            InputState.ButtonDownFlags | *ButtonFlagPtr));
        HandleInput(InputState);
    }
    
    // 在独占输入模式下，消费此事件，阻止其传递到游戏
    return true;
}
```

## Demo 示例

此插件无需手动实例化或调用，启用后即自动工作。以下为模块初始化概念代码（实际无需用户代码）：

**EOSOverlayInputProviderModule.h** (概念)
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FEOSOverlayInputProviderModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<class FEOSOverlayInputProviderPreProcessor> InputPreprocessor;
};
```

**EOSOverlayInputProviderModule.cpp** (概念，展示注册过程)
```cpp
#include "EOSOverlayInputProviderModule.h"
#include "EOSOverlayInputProviderPreProcessor.h"
#include "Framework/Application/SlateApplication.h"

#define LOCTEXT_NAMESPACE "FEOSOverlayInputProviderModule"

void FEOSOverlayInputProviderModule::StartupModule()
{
    // 创建并初始化输入预处理器
    InputPreprocessor = MakeShared<FEOSOverlayInputProviderPreProcessor>();
    InputPreprocessor->Initialize();

    // 注册到 Slate 以开始拦截输入
    if (FSlateApplication::IsInitialized())
    {
        FSlateApplication::Get().RegisterInputPreProcessor(InputPreprocessor);
    }
}

void FEOSOverlayInputProviderModule::ShutdownModule()
{
    // 反注册并清理
    if (FSlateApplication::IsInitialized())
    {
        FSlateApplication::Get().UnregisterInputPreProcessor(InputPreprocessor);
    }
    InputPreprocessor.Reset();
}

#undef LOCTEXT_NAMESPACE
    
IMPLEMENT_MODULE(FEOSOverlayInputProviderModule, EOSOverlayInputProvider)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EOSSDK` | Epic Online Services SDK，用于调用 `EOS_UI_ReportInputState` 等API。 |
| `EOSShared` | Epic Online Services 共享模块，提供平台句柄和通用工具。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 修复忽略 `nodiscard` 属性函数返回值的编译警告。 |
| 2024-11-06 | `bc63a88d` | Redirect old cppcompilewarning properties to new *.CppCompileWarningSettings | 配置迁移：将旧的编译警告设置重定向到新属性。 |
| 2024-09-04 | `7abeaeb2` | Refactored EOSOverlayInputProviderPreProcessor to respond directly to an EOS notification instead of | 重大重构：输入处理器改为直接响应 EOS 通知，优化了叠加层状态同步逻辑。 |
| 2024-05-27 | `797c37e9` | Implemented new type priority system for InputPreProcessors in SlateApplication, refactored callsite | 适配引擎输入系统改动，实现输入处理器优先级系统。 |
| 2024-04-02 | `e3227b49` | Fix for missing EOS overlay input events. | 修复 EOS 叠加层输入事件丢失的关键问题。 |

### 维护评价

- **活跃维护**: 是的，插件在 2024 年和 2025 年均有更新。
- **最近更新内容**: 最近一次更新是修复编译警告（2025-09），此前有一次重要的功能重构（2024-09）和关键 Bug 修复（2024-04）。这表明插件不仅维护，还在进行架构优化。
- **稳定性**: 经历了重构和 Bug 修复，趋于稳定。
- **限制**: 插件被标记为 `EnabledByDefault: false`，且模块类型为 `ClientOnlyNoCommandlet`，意味着它仅在客户端构建（非 Dedicated Server）且需要手动启用。
- **推荐使用**: **推荐**。对于需要使用 EOS 社交叠加层并关注输入体验的项目，应启用此插件。它由 Epic 官方维护，功能明确且处于积极维护状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/EOSOverlayInputProvider)
- [官方文档](https://dev.epicgames.com/docs/epic-online-services) （Epic Online Services 整体文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/EOSOverlayInputProvider/Source/EOSOverlayInputProvider/Tests) （如果存在）