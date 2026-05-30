# Web Browser

> Allows the user to create a Web Browser Widget

| 属性 | 值 |
|---|---|
| 中文名 | 网页浏览器控件 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WebBrowserWidget` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2015-05-14 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WebBrowserWidget) | |

## 用途

本插件提供了一个基于 Slate/UMG 的网页浏览器控件 (`UWebBrowser`)，允许开发者在 Unreal Engine 的用户界面（主要是 UMG 蓝图）中嵌入并显示网页内容。它解决了在游戏或应用程序 UI 中直接集成网络内容（如帮助文档、新闻、外部服务界面）的需求，而无需跳出应用。插件封装了底层的浏览器渲染实现（通常基于 Chromium 或系统 WebView），提供了加载 URL、执行 JavaScript、处理导航事件等核心功能。

## 使用场景

-   你需要在游戏菜单、HUD 或专门的 UI 界面中内嵌一个动态更新的网页（如官方公告、玩家排行榜）。
-   你的应用程序需要与基于 Web 的后端服务或第三方 API 进行交互，并希望直接在应用内展示其 Web 界面。
-   你正在开发一个工具或编辑器扩展，需要内嵌一个功能完整的浏览器窗口来查看文档或在线资源。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load URL` | 加载指定的网页 URL。 | `UWebBrowser` |
| `Load String` | 将一个字符串作为网页内容加载，可指定虚拟 URL。 | `UWebBrowser` |
| `Execute Javascript` | 在当前加载的网页上下文中执行一段 JavaScript 代码。 | `UWebBrowser` |
| `Get Title Text` | 获取当前网页的标题。 | `UWebBrowser` |
| `Get Url` | 获取当前加载的网页 URL。 | `UWebBrowser` |
| `OnUrlChanged` (事件) | 网页 URL 发生变化时触发。 | `UWebBrowser` |
| `OnBeforePopup` (事件) | 网页即将弹出新窗口时触发，可用于拦截或处理弹窗。 | `UWebBrowser` |
| `OnConsoleMessage` (事件) | 网页控制台输出消息时触发（如 JavaScript 的 `console.log`）。 | `UWebBrowser` |

### 使用示例（蓝图描述）

1.  **创建并加载网页**：
    *   在 UMG 设计器中，从调色板找到 “Web Browser” 控件并拖放到画布上。
    *   在控件的细节面板中，设置 `Initial URL` 属性为你想要加载的网址。
    *   或者，通过蓝图逻辑，在事件图表中，获取该控件的引用，然后调用 `Load URL` 节点，传入动态获取的 URL 字符串。

2.  **响应网页事件**：
    *   选中画布上的 Web Browser 控件，在细节面板的事件部分，点击 `OnUrlChanged` 旁的“+”号来创建事件处理函数。
    *   在生成的事件函数中，你可以将新的 URL (`Text` 参数) 显示在 UI 的某个文本块上。
    *   同理，可以为 `OnConsoleMessage` 创建处理函数，将网页控制台的日志信息输出到游戏的调试窗口或 UI 中。

## C++ 用法

### 头文件引入

```cpp
#include "WebBrowser.h"
#include "Widgets/Input/SWebBrowser.h"
```

### 基本用法

以下代码演示如何在 C++ 中创建并初始化一个 WebBrowser 控件。

```cpp
// 来源：基于 UWebBrowser 和 SWebBrowser 的公开接口

// 在某个 UWidget 子类或 UUserWidget 中
UPROPERTY(meta = (BindWidget))
TObjectPtr<UWebBrowser> MyWebBrowser;

// 初始化时设置 URL
void UMyWidget::NativeConstruct()
{
    Super::NativeConstruct();
    if (MyWebBrowser)
    {
        MyWebBrowser->LoadURL(TEXT("https://www.unrealengine.com"));
        // 绑定 URL 变化事件
        MyWebBrowser->OnUrlChanged.AddDynamic(this, &UMyWidget::OnMyWebBrowserUrlChanged);
    }
}

// 事件回调
void UMyWidget::OnMyWebBrowserUrlChanged(const FText& Text)
{
    UE_LOG(LogTemp, Log, TEXT("Web browser navigated to: %s"), *Text.ToString());
    // 更新 UI 中显示 URL 的文本
}
```

### 进阶用法

以下代码展示如何执行 JavaScript 并处理弹窗拦截。

```cpp
// 在某个交互逻辑中执行 JavaScript
void UMyWidget::ExecuteScriptOnPage()
{
    if (MyWebBrowser)
    {
        FString Script = TEXT("document.title = 'Hello from UE5!'; console.log('Script executed');");
        MyWebBrowser->ExecuteJavascript(Script);
    }
}

// 绑定并拦截弹窗事件
void UMyWidget::NativeConstruct()
{
    // ... (接上文)
    if (MyWebBrowser)
    {
        MyWebBrowser->OnBeforePopup.AddDynamic(this, &UMyWidget::OnMyBeforePopup);
    }
}

bool UMyWidget::OnMyBeforePopup(FString URL, FString Frame)
{
    UE_LOG(LogTemp, Warning, TEXT("Blocked popup to URL: %s"), *URL);
    // 返回 true 表示阻止弹窗，返回 false 表示允许
    return true; 
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何在 UUserWidget 中内嵌 WebBrowser 控件。

**MyWebBrowserWidget.h**
```cpp
// MyWebBrowserWidget.h
#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "MyWebBrowserWidget.generated.h"

class UWebBrowser;

UCLASS()
class YOURPROJECT_API UMyWebBrowserWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    virtual void NativeConstruct() override;

    UFUNCTION(BlueprintCallable, Category = "Web Browser")
    void NavigateToUrl(const FString& Url);

protected:
    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UWebBrowser> EmbeddedWebBrowser;

    UFUNCTION()
    void OnUrlChanged(const FText& NewUrlText);
};
```

**MyWebBrowserWidget.cpp**
```cpp
// MyWebBrowserWidget.cpp
#include "MyWebBrowserWidget.h"
#include "WebBrowser.h"

void UMyWebBrowserWidget::NativeConstruct()
{
    Super::NativeConstruct();

    if (EmbeddedWebBrowser)
    {
        EmbeddedWebBrowser->OnUrlChanged.AddDynamic(this, &UMyWebBrowserWidget::OnUrlChanged);
        EmbeddedWebBrowser->LoadURL(TEXT("https://docs.unrealengine.com"));
    }
}

void UMyWebBrowserWidget::NavigateToUrl(const FString& Url)
{
    if (EmbeddedWebBrowser)
    {
        EmbeddedWebBrowser->LoadURL(Url);
    }
}

void UMyWebBrowserWidget::OnUrlChanged(const FText& NewUrlText)
{
    // 可以在这里更新 UI 或进行日志记录
    UE_LOG(LogTemp, Log, TEXT("Current URL: %s"), *NewUrlText.ToString());
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-12-09 | `f7b9eee8` | Including moved WebBrowser assets in build when using WebBrowserWidget | 修复构建，确保使用插件时包含相关的 WebBrowser 资源。 |
| 2025-12-01 | `2f80d817` | moving 3D browser assets into engine to allow ApplePlatformWebBrowser to use indirect rendering path | 将 3D 浏览器资源移入引擎，以支持 Apple 平台的间接渲染路径。 |
| 2024-08-01 | `fc8a99af` | Fixed some implicit FSoftObjectPath construction. | 修复了一些隐式的 FSoftObjectPath 构造问题。 |

### 维护评价

该插件自 2015 年创建以来，已有超过 10 年的历史，是一个非常成熟的组件。近期的提交记录（最近一次在 2025 年 12 月）显示它仍在持续维护中，主要修复构建问题和适配不同平台（如 Apple、OpenXR Android）的渲染路径。虽然 `EnabledByDefault` 为 `false`，需要手动启用，但作为 Epic 官方维护的运行时 UI 组件，其稳定性和可靠性有保障。

**总结**：这是一个 **活跃维护中的成熟插件**。对于需要在 UI 中内嵌网页功能的需求，它是一个稳定可靠的选择。需要注意的是，其跨平台支持依赖于各平台底层 WebView 的能力，功能可能因平台而异。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WebBrowserWidget)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WebBrowserWidget/Tests) (如果存在)