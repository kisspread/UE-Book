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
| 创建时间 | 2022-10-21 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ScreenReader) | |

## 用途

ScreenReader 插件提供了构建屏幕阅读器（读屏软件）所需的框架和基础类，使开发者能够为视障用户提供语音反馈和无障碍导航。它封装了文本转语音（TTS）请求、公告优先级管理、可访问焦点跟踪以及自定义导航策略等核心功能。通过该插件，你可以：

- 向用户播报界面元素内容（如按钮文本、数值变化）
- 支持多个屏幕阅读器用户（本地多人场景）
- 定义公告的优先级、可中断性和排队行为
- 自定义在可访问控件层级中的导航逻辑

该插件本身不包含开箱即用的完整屏幕阅读器，而是提供了可扩展的基类（`FScreenReaderBase`、`FScreenReaderUser`）和设计模式（建造者、策略），供开发者继承并实现专属平台的无障碍服务。

## 使用场景

- 你正在开发一款需要无障碍支持的游戏或工具，希望视障玩家能通过语音提示了解界面状态
- 你需要为游戏内的菜单、HUD 元素提供文字转语音朗读功能
- 你想要支持本地多人分屏时，每位玩家独立控制语音反馈
- 你希望实现自定义的焦点遍历规则（例如跳过不可交互的装饰性控件）

## 蓝图用法

该插件主要面向 C++ 扩展，但提供了两个可在蓝图中使用的结构体，用于创建和传递公告信息与回复状态。

### 核心结构体

| 结构体 | 说明 | 所在头文件 |
|---|---|---|
| `FScreenReaderAnnouncementInfo` | 公告行为信息：是否排队、是否可中断、优先级 | `ScreenReaderAnnouncement.h` |
| `FScreenReaderReply` | 操作结果：是否成功处理 | `ScreenReaderReply.h` |

**使用示例（蓝图）**：

1. 通过 `Make ScreenReaderAnnouncementInfo` 节点创建公告信息（设置优先级为 `Low`、不排队、可中断）。
2. 将该结构体传入自定义的 C++ 函数（如 `RequestSpeak`），该函数需通过蓝图函数库暴露。
   *注意：默认插件未暴露 `FScreenReaderUser` 的蓝图节点，如果需要蓝图调用，建议自行封装蓝图函数库。*

## C++ 用法

### 头文件引入

```cpp
#include "GenericPlatform/ScreenReaderBase.h"
#include "GenericPlatform/ScreenReaderUser.h"
#include "Announcement/ScreenReaderAnnouncement.h"
```

### 基本用法

以下代码展示如何激活屏幕阅读器、注册用户并请求语音播报。

```cpp
// 通常在游戏实例或主模块启动时执行
// 1. 获取 GenericApplication
TSharedRef<GenericApplication> PlatformApplication = FSlateApplication::Get().GetPlatformApplication();

// 2. 创建屏幕阅读器（使用自定义派生类或默认实现）
// 插件未提供默认实现，需继承 FScreenReaderBase 并实现 OnAccessibleEventRaised。
// 此处假设已有 MyScreenReader 类。
TSharedRef<FScreenReaderBase> ScreenReader = MakeShared<MyScreenReader>(PlatformApplication);

// 3. 激活屏幕阅读器
ScreenReader->Activate(); // 拦截输入事件并分发可访问事件

// 4. 注册用户（例如用户索引0）
int32 UserId = 0;
ScreenReader->RegisterUser(UserId);

// 5. 获取用户实例
TSharedRef<FScreenReaderUser> User = ScreenReader->GetUserChecked(UserId);

// 6. 请求语音播报
FText MyText = LOCTEXT("Hello", "欢迎使用无障碍屏幕阅读器");
User->RequestSpeak(FScreenReaderAnnouncement(
    MyText.ToString(),
    FScreenReaderAnnouncementInfo::Important() // 高优先级、不可中断、会排队
));

// 7. 停止播报（如果需要）
User->StopSpeaking();
```

**来源**：`ScreenReaderUser.h` 中的注释示例。

### 进阶用法

#### 自定义导航策略

插件默认提供了 `FScreenReaderDefaultNavigationPolicy`，仅允许焦点在可接受焦点的控件间移动。你可以通过实现 `IScreenReaderNavigationPolicy` 接口覆盖导航行为。

```cpp
// 自定义策略：跳过所有隐藏控件
class FMyNavigationPolicy : public IScreenReaderNavigationPolicy
{
public:
    virtual TSharedPtr<IAccessibleWidget> GetNextSiblingFrom(const TSharedRef<IAccessibleWidget>& Source) const override
    {
        return Source->SearchForNextSiblingFrom(Source, [](const TSharedRef<IAccessibleWidget>& Widget) {
            return Widget->IsVisible() && Widget->CanCurrentlyAcceptAccessibleFocus();
        });
    }
    // ... 其他虚函数同理
};

// 使用
TSharedRef<IScreenReaderNavigationPolicy> Policy = MakeShared<FMyNavigationPolicy>();
// 通过 FScreenReaderUser::SetNavigationPolicy 设置（需自行提供该函数，默认未暴露）
```

#### 处理可访问事件

必须重写 `FScreenReaderBase::OnAccessibleEventRaised` 以响应控件事件（如焦点改变、值变化）。

```cpp
class FMyScreenReader : public FScreenReaderBase
{
public:
    using FScreenReaderBase::FScreenReaderBase;
protected:
    virtual void OnAccessibleEventRaised(const FAccessibleEventArgs& Args) override
    {
        // 当有可访问事件时，自动朗读发生事件的控件
        TSharedPtr<IAccessibleWidget> Widget = Args.Widget;
        if (Widget.IsValid())
        {
            // 获取已注册的所有用户，并请求朗读
            ForEachUser([&](TSharedRef<FScreenReaderUser> User) {
                User->RequestSpeakWidget(Widget.ToSharedRef());
            });
        }
    }
};
```

## Demo 示例

以下是一个最小可编译的示例，演示如何创建并激活一个自定义屏幕阅读器，然后注册一个用户并请求语音播报。

**MyScreenReader.h**
```cpp
#pragma once
#include "GenericPlatform/ScreenReaderBase.h"

class FMyScreenReader : public FScreenReaderBase
{
public:
    using FScreenReaderBase::FScreenReaderBase;
protected:
    virtual void OnAccessibleEventRaised(const FAccessibleEventArgs& Args) override
    {
        // 示例：简单忽略所有事件，只输出日志
        UE_LOG(LogTemp, Log, TEXT("Accessible event received"));
    }
};
```

**MyScreenReader.cpp**（假设在某个模块的启动代码中调用）
```cpp
#include "MyScreenReader.h"
#include "GenericPlatform/ScreenReaderUser.h"
#include "Announcement/ScreenReaderAnnouncement.h"
#include "Framework/Application/SlateApplication.h"

void StartScreenReader()
{
    if (!FSlateApplication::IsInitialized()) return;

    TSharedRef<GenericApplication> PlatformApp = FSlateApplication::Get().GetPlatformApplication();
    TSharedRef<FMyScreenReader> ScreenReader = MakeShared<FMyScreenReader>(PlatformApp);
    ScreenReader->Activate();

    // 注册用户 0
    if (ScreenReader->RegisterUser(0))
    {
        TSharedRef<FScreenReaderUser> User = ScreenReader->GetUserChecked(0);
        // 播报欢迎信息
        User->RequestSpeak(FScreenReaderAnnouncement(
            FString("Screen reader demo started."),
            FScreenReaderAnnouncementInfo::Important()
        ));
    }
}
```

将上述代码放入你的模块中，并在适当位置（如游戏实例初始化）调用 `StartScreenReader()` 即可启用屏幕阅读器。

## 模块依赖

如果你的模块需要使用 ScreenReader 插件，请在 `Build.cs` 中添加以下依赖（省略通用依赖）：

| 模块 | 用途 |
|---|---|
| `TextToSpeech` | 提供文本转语音能力，ScreenReader 通过此模块发声 |

**额外注意**：运行时目标平台仅支持 Win64、Mac、Linux、LinuxArm64（配置在 .uplugin 的 PlatformAllowList），且不能在服务器上运行（TargetDenyList: Server）。

## 维护状态

### 近期更新

- 2025-05-12 — Fix stack use after scope issue in screen reader.
- 2025-02-13 — [Slate] Remove deprecated "OnControllerButtonXXX" functions, which were deprecated in 5.1.
- 2023-01-16 — [Engine/Plugins]  (批量更新，未提供具体改动)
- 2023-01-11 — Fixing compile errors from running IWYU on the entire engine.
- 2022-10-21 — Update vendor links for built-in plugins to use secure protocol. (首次出现)

### 维护评价

该插件自 2022 年创建以来，更新频率较低，最近一次实质性更新为 2025-05-12 的栈作用域修复。整体维护状态为 **维护中**（1年内有更新），但社区活跃度不高。作为实验性插件，其 API 可能在未来版本中发生变化。建议用于原型验证或自行扩展，生产环境中需谨慎评估稳定性。若需要成熟的读屏方案，可考虑集成第三方库或等待 Epic 官方完善。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ScreenReader)
- [官方文档]（无，.uplugin 中 DocsURL 为空）
- [测试用例]（未找到独立测试文件，可能位于 `Engine/Tests` 下）