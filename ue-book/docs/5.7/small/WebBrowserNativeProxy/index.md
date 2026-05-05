# Web Browser to Native Proxying

> Maintains the browser to native proxy and provides hooks for registering UObjects bindings

| 属性 | 值 |
|---|---|
| 分类 | UI |
| 默认启用 | ❌ 否（`EnabledByDefault: false`） |
| 包含内容 | 否 |
| 模块 | WebBrowserNativeProxy (Runtime, LoadingPhase: PreDefault) |
| 创建时间 | 2019-02-27 |
| 年龄标签 | 👴 老古董(>5年) |
| 平台 | Win64, Mac, IOS, Android |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/WebBrowserNativeProxy) | |

## 用途

WebBrowserNativeProxy 是 WebBrowser 运行时模块的辅助插件，负责创建和维护一个**原生浏览器窗口实例**（`IWebBrowserWindow`），并提供事件回调机制，让其他模块可以在浏览器窗口就绪时注册 UObject 绑定或执行自定义初始化逻辑。

简单来说，它是引擎内部用于管理"无 UI 嵌入式浏览器代理"的基础设施层。当你需要一个不绑定到 Slate Widget 的独立原生浏览器窗口（例如用于后台 Web 通信、嵌入式应用、或 DevTools 调试）时，这个插件提供了标准化的创建和访问模式。

**注意**：此插件默认不启用。需要在项目的 `.uproject` 文件或编辑器插件设置中手动启用。

## 使用场景

- 你需要一个**无头（headless）浏览器窗口**来执行 Web 请求或运行 JavaScript，而不通过 `SWebBrowser` Slate 控件
- 你正在构建嵌入式应用（`BUILD_EMBEDDED_APP=1`），需要一个原生浏览器代理而非 Slate 渲染的浏览器
- 你需要一个**全局单例浏览器窗口**，多个系统共享同一个浏览器实例
- 你需要在浏览器窗口创建完成时获得回调，以便注册 UObject JavaScript 绑定

## 蓝图用法

此插件**没有暴露任何蓝图节点**。它是一个纯 C++ 模块接口，所有 API 都通过 `IWebBrowserNativeProxyModule` 接口在 C++ 中使用。

## C++ 用法

### 头文件引入

```cpp
#include "WebBrowserNativeProxyModule.h"
```

### 基本用法

获取模块单例并访问浏览器窗口：

```cpp
// 检查模块是否可用
if (IWebBrowserNativeProxyModule::IsAvailable())
{
    // 获取模块引用（如果模块未加载，会触发加载）
    IWebBrowserNativeProxyModule& ProxyModule = IWebBrowserNativeProxyModule::Get();

    // 获取浏览器窗口，bCreate=true 表示如果尚未创建则自动创建
    TSharedPtr<IWebBrowserWindow> Browser = ProxyModule.GetBrowser(true);

    if (Browser.IsValid())
    {
        // 使用浏览器窗口加载 URL
        Browser->LoadURL(TEXT("https://example.com"));
    }
}
```

### 监听浏览器就绪事件

如果浏览器窗口尚未创建，可以通过事件监听器等待其就绪：

```cpp
IWebBrowserNativeProxyModule& ProxyModule = IWebBrowserNativeProxyModule::Get();

// 注册浏览器就绪回调
ProxyModule.OnBrowserAvailable().AddLambda(
    [](const TSharedRef<IWebBrowserWindow>& Browser)
    {
        // 浏览器窗口已创建，可以在这里执行初始化
        Browser->LoadURL(TEXT("https://example.com"));
        UE_LOG(LogTemp, Log, TEXT("Native browser proxy is ready"));
    }
);

// 触发创建（会异步广播 OnBrowserAvailable 事件）
ProxyModule.GetBrowser(true);
```

来源：`WebBrowserNativeProxyModule.h` 第 54-60 行、`WebBrowserNativeProxyModule.cpp` 第 25-61 行

### 进阶用法：嵌入式应用模式

在 `BUILD_EMBEDDED_APP` 宏启用时（嵌入式应用场景），浏览器创建逻辑会走不同的代码路径，调用 `IWebBrowserSingleton::CreateNativeBrowserProxy()` 而非 `CreateBrowserWindow()`：

```cpp
// 当 BUILD_EMBEDDED_APP=1 时：
Browser = IWebBrowserModule::Get().GetSingleton()->CreateNativeBrowserProxy();

// 当 BUILD_EMBEDDED_APP=0 时（默认）：
FCreateBrowserWindowSettings WindowSettings;
WindowSettings.bUseTransparency = true;
WindowSettings.bInterceptLoadRequests = true;
WindowSettings.bShowErrorMessage = false;
Browser = IWebBrowserModule::Get().GetSingleton()->CreateBrowserWindow(WindowSettings);
```

非 Shipping 构建中，还会自动启用 DevTools 快捷键，并拦截弹出窗口事件（`OnCreateWindow`），将其作为新的 Slate 窗口显示。

## Demo 示例

### 最小可编译示例：创建原生浏览器代理并加载网页

**MyGame.Build.cs** 依赖声明：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "WebBrowser",            // WebBrowser 运行时模块
    "WebBrowserNativeProxy"  // 本插件模块
});
```

**MyBrowserManager.h**：

```cpp
#pragma once

#include "CoreMinimal.h"
#include "WebBrowserNativeProxyModule.h"

class FMyBrowserManager
{
public:
    void Initialize();

private:
    void OnBrowserReady(const TSharedRef<IWebBrowserWindow>& Browser);
    TSharedPtr<IWebBrowserWindow> BrowserWindow;
};
```

**MyBrowserManager.cpp**：

```cpp
#include "MyBrowserManager.h"
#include "IWebBrowserWindow.h"

void FMyBrowserManager::Initialize()
{
    if (!IWebBrowserNativeProxyModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("WebBrowserNativeProxy module is not available"));
        return;
    }

    IWebBrowserNativeProxyModule& ProxyModule = IWebBrowserNativeProxyModule::Get();

    // 注册就绪回调
    ProxyModule.OnBrowserAvailable().AddRaw(this, &FMyBrowserManager::OnBrowserReady);

    // 触发创建
    BrowserWindow = ProxyModule.GetBrowser(true);
}

void FMyBrowserManager::OnBrowserReady(const TSharedRef<IWebBrowserWindow>& Browser)
{
    UE_LOG(LogTemp, Log, TEXT("Browser proxy ready, loading URL..."));
    Browser->LoadURL(TEXT("https://unrealengine.com"));
}
```

**启用插件**：在 `.uproject` 中添加：

```json
{
    "Plugins": [
        {
            "Name": "WebBrowserNativeProxy",
            "Enabled": true
        }
    ]
}
```

## 模块依赖

从 `WebBrowserNativeProxy.build.cs` 提取。你的模块如果要使用此插件，需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心基础设施 |
| `CoreUObject` | UObject 系统 |
| `WebBrowser` | 浏览器运行时，提供 `IWebBrowserWindow`、`IWebBrowserSingleton` 等接口 |

插件内部私有依赖（你的模块不需要直接依赖）：

| 模块 | 用途 |
|---|---|
| `SlateCore` | Slate UI 核心（仅弹出窗口处理） |
| `Slate` | Slate 控件（仅弹出窗口处理） |

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2024-11-09 | `66e9bb39` | Removed all `#if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2` scopes | 纯清理：移除 5.2 版本的废弃兼容宏，无功能变更 |
| 2023-01-13 | `3c9aacb1` | Updated public headers with IWYU | IWYU（Include What You Use）合规性重构，移除多余 #include |
| 2023-01-12 | `2f78497e` | Updated private files with IWYU for all plugins | 同上，私有文件的 IWYU 清理 |

### 维护评价

- **创建时间**：2019-02-27，已超过 7 年
- **代码规模**：仅 2 个源文件（1 .h + 1 .cpp），约 214 行代码，逻辑非常简单
- **最近更新**：最近 3 次提交全部是全局性的 IWYU/宏清理，无任何功能性改动。最后一次实质性功能变更时间无法仅从最近 3 条记录确定，但从代码结构和内容来看，核心逻辑可能自创建以来基本未变
- **状态**：**维护不活跃**。代码本身已经很稳定，作为底层基础设施不需要频繁更新，但也表明 Epic 对此插件没有进一步的开发计划
- **已知限制**：
  - 不暴露任何蓝图接口，纯 C++ 使用
  - 默认不启用，需要手动开启
  - 仅支持 Win64/Mac/IOS/Android 四个平台
  - `BUILD_EMBEDDED_APP` 代码路径依赖特定构建配置，普通项目不会走到
- **推荐**：如果你需要一个独立的原生浏览器窗口实例（非 Slate Widget），可以使用此插件。但注意它是一个非常薄的封装层，功能有限。大多数情况下，直接使用 `IWebBrowserModule::Get().GetSingleton()->CreateBrowserWindow()` 或 `SWebBrowser` 控件可能更合适

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/WebBrowserNativeProxy)
- [WebBrowser 运行时模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/WebBrowser)
- [IWebBrowserWindow 接口](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/WebBrowser/Public/IWebBrowserWindow.h)
- [IWebBrowserSingleton 接口](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/WebBrowser/Public/IWebBrowserSingleton.h)
- 官方文档：无（`.uplugin` 中 `DocsURL` 为空）
- 测试用例：无（未发现针对此插件的自动化测试）
