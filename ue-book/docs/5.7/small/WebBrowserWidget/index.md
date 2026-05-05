# Web Browser

> Allows the user to create a Web Browser Widget

| 属性 | 值 |
|---|---|
| 分类 | UI |
| 默认启用 | ❌ 否（`EnabledByDefault: false`） |
| 包含内容 | ✅ 是（3 个默认材质贴图） |
| 模块 | WebBrowserWidget (Runtime, LoadingPhase: PreDefault) |
| 平台 | Win64, Mac, Linux, Android, iOS |
| 创建时间 | 2015-05-14 |
| 年龄标签 | 🏛️ 文物（>10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/WebBrowserWidget) | |

## 用途

WebBrowserWidget 为 UMG 提供了一个 **`UWebBrowser`** 控件，让你可以在游戏 UI 中嵌入一个完整的网页浏览器。它底层封装了 `SWebBrowser` Slate 控件（位于独立的 `WebBrowser` 运行时模块），该模块在各平台上使用 CEF（Chromium Embedded Framework，桌面端）、WKWebView（Apple 平台）或 Android WebView 来渲染网页。

这个 plugin 解决的核心问题是：**在游戏运行时显示网页内容**。无论是加载远程 URL、展示本地 HTML 字符串、还是执行 JavaScript，都可以通过 UMG 蓝图或 C++ 完成。

> ⚠️ **必须手动启用**：此插件默认未开启。在编辑器中通过 Edit → Plugins 搜索 "Web Browser" 启用，或在项目的 `.uproject` 中添加 `"WebBrowserWidget": { "Enabled": true }`。

## 使用场景

- 你需要在游戏内嵌入一个 HTML5 界面（如公告板、排行榜、商城页面）→ 用 `UWebBrowser` 加载 URL 或 HTML 字符串
- 你需要用 WebView 做登录/OAuth 流程（如第三方平台登录）→ 用 `LoadURL` + `OnUrlChanged` 监听回调跳转
- 你想在游戏 HUD 中显示动态网页数据（如地图、仪表盘）→ 用 `ExecuteJavascript` 与页面双向交互
- 你需要一个内嵌的 HTML 帮助/教程系统 → 用 `LoadString` 加载本地构建的 HTML 内容

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load URL` | 加载指定 URL（需包含协议，如 `https://`） | `UWebBrowser` |
| `Load String` | 将字符串作为 HTML 页面加载，需提供一个虚拟 URL | `UWebBrowser` |
| `Execute JavaScript` | 在当前页面上下文中执行 JavaScript 代码 | `UWebBrowser` |
| `Get Title Text` | 获取当前页面标题 | `UWebBrowser` |
| `Get Url` | 获取当前加载的 URL，未加载则返回空字符串 | `UWebBrowser` |

### 核心事件（BlueprintAssignable）

| 事件 | 签名 | 说明 |
|---|---|---|
| `OnUrlChanged` | `(Text)` | URL 发生变化时触发 |
| `OnBeforePopup` | `(URL, Frame)` | 弹出窗口即将打开时触发，可在此拦截 |
| `OnConsoleMessage` | `(Message, Source, Line)` | 页面输出 console 日志时触发（JS `console.log` 等） |

### 设计时属性（Details 面板）

| 属性 | 类型 | 说明 |
|---|---|---|
| `Initial URL` | String | 控件创建时自动导航到的初始 URL |
| `Supports Transparency` | Bool | 是否启用透明背景支持 |

### 使用示例（蓝图描述）

**在 UMG Widget 中显示网页：**

1. 在 UMG Widget Blueprint 中，从面板拖入 **Web Browser** 控件（位于 Experimental 分类下）
2. 在 Details 面板设置 **Initial URL** 为你的目标地址（如 `https://example.com`）
3. 如需动态切换页面，在 Event Graph 中获取该 Web Browser 控件引用，调用 **Load URL** 节点

**监听 URL 变化实现登录回调：**

1. 将 Web Browser 控件拖入画布
2. 在 Details → Events 中点击 **OnUrlChanged** 创建事件绑定
3. 在事件处理中用 **Get Url** 检查当前 URL 是否包含登录成功的回调 token
4. 若匹配，提取 token 并关闭页面

**与 JavaScript 交互：**

1. 在蓝图中调用 **Execute JavaScript**，传入 JS 代码如 `document.title = 'Hello from UE'`
2. 页面中的 JS 可通过 `window.ue` 绑定对象与引擎通信（需要 C++ 层的 `BindUObject`）

## C++ 用法

### 头文件引入

```cpp
#include "WebBrowser.h"
```

同时需要在 `Build.cs` 中添加依赖模块：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "WebBrowserWidget"
});
```

### 基本用法

**创建 Web Browser 控件并加载 URL：**

```cpp
// 在 UWidget 子类或 HUD 中获取 UWebBrowser 引用
UWebBrowser* WebBrowser = /* 通过 UMG 或 CreateWidget 创建 */;

// 加载远程页面
WebBrowser->LoadURL(TEXT("https://www.example.com"));

// 加载本地 HTML 字符串
WebBrowser->LoadString(
    TEXT("<html><body><h1>Hello from UE5!</h1></body></html>"),
    TEXT("https://dummy")  // 虚拟 URL，用于同源策略判定
);

// 获取当前 URL
FString CurrentUrl = WebBrowser->GetUrl();

// 获取页面标题
FText Title = WebBrowser->GetTitleText();
```

### 进阶用法

**绑定事件与 JavaScript 执行：**

```cpp
// 监听 URL 变化
WebBrowser->OnUrlChanged.AddDynamic(this, &UMyClass::OnUrlChanged);

// 监听弹出窗口拦截
WebBrowser->OnBeforePopup.AddDynamic(this, &UMyClass::OnBeforePopup);

// 监听 JS console 输出
WebBrowser->OnConsoleMessage.AddDynamic(this, &UMyClass::OnConsoleMessage);

// 在 C++ 中执行 JavaScript
WebBrowser->ExecuteJavascript(TEXT("alert('Hello from C++!')"));

// 事件处理函数示例
void UMyClass::OnUrlChanged(const FText& NewUrl)
{
    UE_LOG(LogTemp, Log, TEXT("URL changed to: %s"), *NewUrl.ToString());
}

void UMyClass::OnBeforePopup(const FString& URL, const FString& Frame)
{
    // 返回 true 表示阻止弹出窗口（在蓝图中此委托自动阻止）
    UE_LOG(LogTemp, Log, TEXT("Popup blocked: %s"), *URL);
}

void UMyClass::OnConsoleMessage(const FString& Message, const FString& Source, int32 Line)
{
    UE_LOG(LogTemp, Log, TEXT("JS Console [%s:%d]: %s"), *Source, Line, *Message);
}
```

> **注意**：`OnBeforePopup` 委托绑定后会自动阻止弹出窗口（返回 `true`）。如果在非 Game Thread 触发，会自动调度到 Game Thread 执行。

## Demo 示例

以下是一个最小可编译示例，展示如何在 C++ 中创建 Web Browser 控件并监听事件。

### MyWebBrowserWidget.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "MyWebBrowserWidget.generated.h"

class UWebBrowser;
class UEditableTextBox;

UCLASS()
class UMyWebBrowserWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(meta = (BindWidget))
    UWebBrowser* WebBrowser;

    UPROPERTY(meta = (BindWidget))
    UEditableTextBox* UrlInput;

protected:
    virtual void NativeConstruct() override;

    UFUNCTION()
    void OnUrlChanged(const FText& Text);

    UFUNCTION()
    void OnConsoleMessage(const FString& Message, const FString& Source, int32 Line);
};
```

### MyWebBrowserWidget.cpp

```cpp
#include "MyWebBrowserWidget.h"
#include "WebBrowser.h"
#include "Components/EditableTextBox.h"

void UMyWebBrowserWidget::NativeConstruct()
{
    Super::NativeConstruct();

    if (WebBrowser)
    {
        // 加载初始页面
        WebBrowser->LoadURL(TEXT("https://www.unrealengine.com"));

        // 绑定事件
        WebBrowser->OnUrlChanged.AddDynamic(this, &UMyWebBrowserWidget::OnUrlChanged);
        WebBrowser->OnConsoleMessage.AddDynamic(this, &UMyWebBrowserWidget::OnConsoleMessage);
    }
}

void UMyWebBrowserWidget::OnUrlChanged(const FText& Text)
{
    if (UrlInput)
    {
        UrlInput->SetText(Text);
    }
}

void UMyWebBrowserWidget::OnConsoleMessage(const FString& Message, const FString& Source, int32 Line)
{
    UE_LOG(LogTemp, Log, TEXT("[JS Console] %s (%s:%d)"), *Message, *Source, Line);
}
```

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "UMG",
    "WebBrowserWidget"
});
```

## 模块依赖

以下是你自己的模块需要在 `Build.cs` 中引用的模块：

| 模块 | 用途 |
|---|---|
| `WebBrowserWidget` | 本插件模块，提供 `UWebBrowser` UMG 控件 |
| `UMG` | UMG 框架（`UUserWidget` 等） |
| `Slate` | Slate UI 框架（底层控件系统） |
| `SlateCore` | Slate 核心类型 |
| `WebBrowser` | Web 运行时模块（提供 CEF/WKWebView/Android WebView 封装，会自动被 WebBrowserWidget 传递依赖） |
| `Core` / `CoreUObject` / `Engine` | 基础引擎模块 |

> 实际使用时只需在 `Build.cs` 中添加 `WebBrowserWidget`，其余模块会通过传递依赖自动包含。但如果你要使用 `SWebBrowser`（底层 Slate 控件）或高级 API（如 `BindUObject`），则需要显式依赖 `WebBrowser` 模块。

## 架构说明

本插件的分层结构如下：

```
UWebBrowser (UMG 控件, 本插件)
  └── SWebBrowser (Slate 控件, WebBrowser 模块)
        └── SWebBrowserView (视图层)
              ├── CEF (桌面端: Win64/Mac/Linux)
              ├── WKWebView (Apple: Mac/iOS)
              └── Android WebView (Android)
```

- **UWebBrowser**（本插件）：UMG 友好封装，暴露 5 个蓝图函数 + 3 个事件委托
- **SWebBrowser**（WebBrowser 模块）：完整的 Slate 控件，额外提供 `Reload`、`GoBack`、`GoForward`、`BindUObject`、`GetSource`、`IsLoaded`/`IsLoading` 等高级功能。如果 UMG 封装不够用，可以在 C++ 中直接使用 Slate 控件
- **UWebBrowserAssetManager**：内部管理默认材质贴图（`WebTexture_M`、`WebTexture_TM`），用于将网页渲染为 3D 表面的纹理

## 维护状态

### 近期更新

| 日期 | Commit | 内容 | 解读 |
|---|---|---|---|
| 2024-08-01 | `fc8a99a` | Fixed some implicit FSoftObjectPath construction | 编译兼容性修复，修正 `FSoftObjectPath` 的隐式构造（UE5 的 breaking change 适配） |
| 2023-03-15 | `9f0bd4f` | Allow WebGL and video playback in 3D WebBrowser on Android and fix issue with Oculus hardware acceleration | 功能性更新：Android 平台 3D WebView 支持 WebGL 和视频播放，修复 Oculus 硬件加速问题 |
| 2023-01-16 | `bbc37aa` | [Engine/Plugins] Another batch iwyu updates | 批量 IWYU（Include What You Use）重构，无功能变化 |

### 维护评价

- **创建时间**：2015 年，已超过 10 年，属于引擎最早的插件之一
- **维护频率**：最近一次功能性更新在 2023 年 3 月（Android/Oculus 相关），之后仅有编译修复。超过 **2 年**没有实质性功能更新
- **稳定性**：代码非常稳定，功能简单且成熟，几乎不需要修改
- **已知限制**：
  - UMG 层（`UWebBrowser`）只暴露了 5 个函数，功能远少于底层 Slate 控件 `SWebBrowser`
  - 如需 `BindUObject`（JS↔C++ 双向通信）、`GoBack`/`GoForward` 等高级功能，需在 C++ 中直接使用 `SWebBrowser`
  - 蓝图分类仍标记为 "Experimental"，但实际上已长期稳定
- **推荐使用**：✅ 推荐。插件功能简单成熟，适合在 UMG 中嵌入网页内容。如果只需要基本的网页展示和 JS 执行，UMG 层 API 完全够用

## 相关链接

- [源码（WebBrowserWidget 插件）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/WebBrowserWidget)
- [源码（WebBrowser 运行时模块）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/WebBrowser)
- 官方文档：无（.uplugin 中 DocsURL 为空）
