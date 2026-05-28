# ScreenReader

> A plugin that contains accessibility classes and frameworks that can be extended to offer vision accessibility services.

| 属性 | 值 |
|---|---|
| 中文名 | 屏幕阅读器 |
| 分类 | Accessibility |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ScreenReader` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-06-09 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ScreenReader) | |

## 用途

这个插件提供了一个可扩展的框架，用于实现视觉无障碍辅助功能，主要是为视障用户提供屏幕阅读服务。它解决了视障用户无法直接看到屏幕内容的问题。

插件的核心功能是拦截应用程序的输入事件（如键盘、鼠标操作），并允许开发者为 UI 控件定义无障碍信息。当屏幕阅读器处于活动状态时，它可以根据焦点变化或用户操作，通过语音合成（Text-to-Speech， TTS）将界面信息朗读出来。它支持多用户（例如本地多人游戏）、自定义导航策略以及不同优先级的语音播报队列管理。

## 使用场景

- 你在开发一款需要支持无障碍访问的游戏或应用程序（例如教育软件、公共服务界面）。
- 你需要为视障玩家提供语音导航和界面信息朗读功能。
- 你的 UI 基于 Slate 构建，需要集成标准的无障碍支持框架。
- 你需要实现自定义的界面导航逻辑（例如，只朗读当前可见且可交互的控件）。

## 蓝图用法

此插件主要提供 C++ 框架和接口。其核心结构体（`FScreenReaderAnnouncement`, `FScreenReaderAnnouncementInfo`, `FScreenReaderReply`）被标记为 `BlueprintType`，意味着可以在蓝图中创建和操作。然而，主要的驱动逻辑（如屏幕阅读器的激活、用户管理）仍需通过 C++ 代码完成。

### 核心结构体

| 结构体/枚举 | 说明 |
|---|---|
| `FScreenReaderAnnouncement` | 表示一条需要朗读的语音播报信息，包含文本和优先级等行为信息。 |
| `FScreenReaderAnnouncementInfo` | 控制语音播报行为的配置，如优先级、是否可被中断、是否排队。提供 `DefaultWidgetAnnouncement()`、`Important()`、`UserFeedback()` 等静态工厂函数。 |
| `FScreenReaderReply` | 表示操作是否成功的应答结构体，包含 `Handled()` 和 `Unhandled()` 静态函数。 |
| `EScreenReaderAnnouncementPriority` | 语音播报的优先级枚举：`High`, `Medium`, `Low`。 |

### 使用示例（蓝图描述）

1.  **创建播报信息**：在蓝图中创建一个 `FScreenReaderAnnouncement` 变量。
2.  **设置配置**：为其 `AnnouncementInfo` 成员赋予一个预设配置，例如使用 `FScreenReaderAnnouncementInfo::UserFeedback()` 静态函数获取适合用户反馈的配置。
3.  **设置文本**：将需要朗读的文本字符串（建议本地化）赋值给 `AnnouncementString` 成员。
4.  **请求朗读**：通过 C++ 暴露的接口或自定义蓝图函数库，将这个 `FScreenReaderAnnouncement` 对象传递给 `FScreenReaderUser::RequestSpeak()` 函数。

## C++ 用法

### 头文件引入

```cpp
#include "ScreenReader.h"
// 以及具体的子模块头文件，如：
#include "GenericPlatform/ScreenReaderBase.h"
#include "GenericPlatform/ScreenReaderUser.h"
#include "Announcement/ScreenReaderAnnouncement.h"
```

### 基本用法

基于 `FScreenReaderUser` 类的注释和示例，以下是如何使用屏幕阅读器请求语音播报。

```cpp
// 假设已经通过某种方式（如全局访问点或所属 Actor）获取了屏幕阅读器实例和用户索引
TSharedPtr<FScreenReaderBase> MyScreenReader = GetScreenReader();
int32 MyUserIndex = 0;

// 1. 获取或注册屏幕阅读器用户
if (!MyScreenReader->IsUserRegistered(MyUserIndex))
{
    MyScreenReader->RegisterUser(MyUserIndex);
}
TSharedRef<FScreenReaderUser> MyUser = MyScreenReader->GetUserChecked(MyUserIndex);
MyUser->Activate(); // 新注册的用户默认未激活，需要显式激活

// 2. 创建并请求一条关键播报（不可中断，会排队）
static const FText CriticalText = LOCTEXT("SystemAlert", "电量不足，连接充电器。");
FScreenReaderAnnouncement CriticalAnnouncement(CriticalText.ToString(), FScreenReaderAnnouncementInfo::Important());
FScreenReaderReply Reply = MyUser->RequestSpeak(CriticalAnnouncement);
if (Reply.IsHandled())
{
    // 请求已处理
}

// 3. 创建并请求一条用户操作反馈播报（可中断，中等优先级）
FScreenReaderAnnouncement FeedbackAnnouncement(LOCTEXT("ButtonPressed", "按钮已按下。").ToString(), FScreenReaderAnnouncementInfo::UserFeedback());
MyUser->RequestSpeak(FeedbackAnnouncement);

// 4. 导航到下一个同级控件并朗读其信息
MyUser->NavigateToNextSibling(); // 焦点移动
// 焦点变化可能会触发自动朗读，或手动请求朗读当前焦点控件
MyUser->RequestSpeakWidget(MyUser->GetFocusedWidget()); // 假设有方法获取当前焦点控件
```
*(来源：`ScreenReaderUser.h` 中的注释和函数签名)*

### 进阶用法

自定义屏幕阅读器导航策略。

```cpp
#include "Navigation/ScreenReaderNavigationPolicy.h"

// 实现一个自定义的导航策略接口
class FMyCustomNavigationPolicy : public IScreenReaderNavigationPolicy
{
public:
    // 在所有实现中，根据自定义逻辑（例如，只导航到可见且启用的控件）返回下一个合适的控件。
    virtual TSharedPtr<IAccessibleWidget> GetNextSiblingFrom(const TSharedRef<IAccessibleWidget>& Source) const override
    {
        // 自定义查找下一个兄弟控件的逻辑
        // 例如：跳过不可见的控件
        TSharedPtr<IAccessibleWidget> Next = Source->GetNextSibling();
        while (Next.IsValid() && !Next->IsVisible())
        {
            Next = Next->GetNextSibling();
        }
        return Next;
    }
    // ... 实现其他五个纯虚函数 ...
    virtual TSharedPtr<IAccessibleWidget> GetPreviousSiblingFrom(const TSharedRef<IAccessibleWidget>& Source) const override { /* ... */ }
    virtual TSharedPtr<IAccessibleWidget> GetFirstAncestorFrom(const TSharedRef<IAccessibleWidget>& Source) const override { /* ... */ }
    virtual TSharedPtr<IAccessibleWidget> GetFirstChildFrom(const TSharedRef<IAccessibleWidget>& Source) const override { /* ... */ }
    virtual TSharedPtr<IAccessibleWidget> GetNextWidgetInHierarchyFrom(const TSharedRef<IAccessibleWidget>& Source) const override { /* ... */ }
    virtual TSharedPtr<IAccessibleWidget> GetPreviousWidgetInHierarchyFrom(const TSharedRef<IAccessibleWidget>& Source) const override { /* ... */ }
};

// 将自定义策略应用到屏幕阅读器用户
TSharedRef<FScreenReaderUser> MyUser = MyScreenReader->GetUserChecked(MyUserIndex);
MyUser->SetNavigationPolicy(MakeShared<FMyCustomNavigationPolicy>());
```
*(来源：`ScreenReaderNavigationPolicy.h` 中的接口定义和默认实现示例)*

## Demo 示例

一个最小化的屏幕阅读器初始化和使用框架。

```cpp
// MyGameModule.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
private:
    TSharedPtr<class FMyScreenReader> MyScreenReader;
};

// MyGameModule.cpp
#include "MyGameModule.h"
#include "GenericPlatform/ScreenReaderBase.h"
#include "GenericPlatform/IScreenReaderBuilder.h"

// 假设你已经有了一个具体的屏幕阅读器实现（例如从 SlateScreenReader 继承）
class FMyScreenReader : public FScreenReaderBase
{
public:
    explicit FMyScreenReader(const TSharedRef<GenericApplication>& InPlatformApp) : FScreenReaderBase(InPlatformApp) {}
protected:
    virtual void OnAccessibleEventRaised(const FAccessibleEventArgs& Args) override
    {
        // 在这里处理无障碍事件，例如当焦点改变时触发语音播报
        // 具体逻辑依赖于你的框架实现
    }
};

// 一个简单的构建器
class FMyScreenReaderBuilder : public IScreenReaderBuilder
{
public:
    virtual TSharedRef<FScreenReaderBase> Create(const IScreenReaderBuilder::FArgs& InArgs) override
    {
        return MakeShared<FMyScreenReader>(InArgs.PlatformApplication);
    }
};

void FMyGameModule::StartupModule()
{
    // 注意：实际项目中，屏幕阅读器的创建和管理通常由引擎或特定子系统（如 Slate 应用）处理。
    // 这里仅为演示其生命周期。
    if (FSlateApplication::IsInitialized())
    {
        TSharedPtr<GenericApplication> PlatformApp = FSlateApplication::Get().GetPlatformApplication();
        if (PlatformApp.IsValid())
        {
            FMyScreenReaderBuilder Builder;
            IScreenReaderBuilder::FArgs Args(PlatformApp.ToSharedRef());
            MyScreenReader = Builder.Create(Args);
            MyScreenReader->Activate();
            MyScreenReader->RegisterUser(0); // 注册第一个用户
        }
    }
}

void FMyGameModule::ShutdownModule()
{
    if (MyScreenReader.IsValid())
    {
        MyScreenReader->UnregisterAllUsers();
        MyScreenReader->Deactivate();
        MyScreenReader.Reset();
    }
}

IMPLEMENT_MODULE(FMyGameModule, MyGame)
```

## 模块依赖

从 `Build.cs` 分析，使用者需要依赖 `TextToSpeech` 模块来提供实际的语音合成能力。其他依赖均为标准核心模块。

| 模块 | 用途 |
|---|---|
| `TextToSpeech` | 提供实际的文本转语音功能，是本插件语音播报的核心依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF 格式。 |
| 2025-05-12 | `d82541bf` | Fix stack use after scope issue in screen reader. | 修复了屏幕阅读器中一个作用域外栈使用的 bug。 |
| 2025-02-13 | `8eb53cc8` | [Slate] Remove deprecated "OnControllerButtonXXX" functions, which were deprecated in 5.1. | 移除了 Slate 中一些在 5.1 版本已废弃的手柄按键相关函数。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | （通用的引擎插件维护提交，无具体功能描述） |
| 2023-01-11 | `625952f8` | Fixing compile errors from running IWYU on the entire engine. | 修复因全引擎 IWYU 检查导致的编译错误。 |

### 维护评价

该插件创建于 2021 年，属于实验性功能（`IsExperimental: true`，`EnabledByDefault: false`）。从提交记录看，自 2023 年 1 月后没有新增核心功能，最近的提交（2025、2026年）主要是编译兼容性修复和引擎底层重构适配，表明插件处于**维护不活跃**状态。

插件提供了完整的框架和接口（`ScreenReaderBase`, `ScreenReaderUser`, `IScreenReaderNavigationPolicy`），架构清晰，可扩展性良好。但作为实验性项目，可能存在未完善的功能、已知问题或接口变动。其实际功能严重依赖未包含在此插件内的具体平台实现（如 `SlateScreenReader` 插件，但未在本次分析中出现）和 `TextToSpeech` 插件。

**建议**：可以作为学习无障碍框架设计的参考，或用于快速原型开发。在生产环境中使用前，需要仔细评估其稳定性、完整性以及是否有更成熟或官方支持的无障碍解决方案。由于长期无实质性功能更新，使用时应做好自行维护和扩展的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ScreenReader)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ScreenReader/Tests) （根据插件结构推断，测试可能在 `Tests` 子目录）