# Web Browser to Native Proxying

> Maintains the browser to native proxy and provides hooks for registering UObjects bindings

| 属性 | 值 |
|---|---|
| 中文名 | 浏览器原生代理 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WebBrowserNativeProxy` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-02-27 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WebBrowserNativeProxy) | |

## 用途

该插件提供了一个**浏览器到原生（Native）的代理层**。其核心功能是为在原生应用程序（例如 iOS 或 Android 应用）中嵌入虚幻引擎（UE）作为库（dylib/so）的场景，管理一个单一的浏览器窗口实例。

它主要解决以下问题：
1.  **统一管理浏览器实例**：在嵌入式场景中，UE 引擎需要一个共享的、单一的浏览器窗口来渲染 UI 内容。此模块负责创建、持有和访问该实例。
2.  **提供绑定钩子**：通过 `OnBrowserAvailable` 事件，允许其他模块在浏览器窗口准备就绪时注册它们的 UObject 绑定（可能用于 JavaScript 到 C++ 的通信桥接）。

简而言之，它是一个基础设施插件，为需要**在原生容器中使用 Web 技术进行 UI 渲染**的复杂集成场景提供底层支持。

## 使用场景

-   你正在开发一个原生移动应用（iOS/Android），并将 UE 引擎作为动态库嵌入其中，同时需要使用 UE 的 WebBrowser 控件或类似功能来显示混合 UI。
-   你正在构建一个将 UE 视图嵌入到其他平台原生窗口的应用程序，并需要统一管理其中一个关键的浏览器渲染窗口。
-   你需要一个中心点来注册和管理 UObject 与浏览器内 JavaScript 环境的绑定关系。

## 蓝图用法

该插件未暴露任何蓝图可调用 (`BlueprintCallable`) 函数或可读写 (`BlueprintReadWrite`) 属性。它主要提供 C++ 模块接口，供其他系统模块调用。

## C++ 用法

### 头文件引入

```cpp
#include "WebBrowserNativeProxyModule.h"
```

### 基本用法

该插件的核心是一个单例模块，用于获取浏览器窗口实例。以下是获取浏览器窗口并监听其可用性的基本模式。

```cpp
// 检查模块是否可用（已加载）
if (IWebBrowserNativeProxyModule::IsAvailable())
{
    // 获取模块实例
    IWebBrowserNativeProxyModule& ProxyModule = IWebBrowserNativeProxyModule::Get();

    // 获取浏览器窗口，如果不存在则创建一个
    TSharedPtr<IWebBrowserWindow> BrowserWindow = ProxyModule.GetBrowser(true);

    if (BrowserWindow.IsValid())
    {
        // 浏览器窗口已就绪，可以使用它进行操作
        // 例如，导航到某个 URL
        BrowserWindow->LoadURL(TEXT("https://www.example.com"));
    }

    // 另一种方式：监听浏览器窗口创建完成的事件
    ProxyModule.OnBrowserAvailable().AddLambda([](const TSharedRef<IWebBrowserWindow>& Browser)
    {
        // 浏览器窗口现在可用，可以安全地使用
        UE_LOG(LogTemp, Log, TEXT("Browser window is now available and ready."));
        // 在此注册绑定或执行其他初始化
    });
}
```

**说明**：`GetBrowser(bCreate)` 方法根据 `bCreate` 参数决定在窗口不存在时是否创建。这对于确保在使用前有可用的浏览器窗口至关重要。

### 进阶用法

在实际的嵌入式引擎应用中，你可能会在一个管理类（如 `FNativeApplicationManager` 或类似的子系统）中集成此代理。

```cpp
// 在某个管理器类的初始化函数中
void FMyNativeAppManager::Initialize()
{
    // 确保代理模块在需要时被加载
    IWebBrowserNativeProxyModule::Get();

    // 注册事件，以便在浏览器窗口可用时执行应用特定的初始化
    IWebBrowserNativeProxyModule::Get().OnBrowserAvailable().AddRaw(this, &FMyNativeAppManager::OnBrowserReady);
}

void FMyNativeAppManager::OnBrowserReady(const TSharedRef<IWebBrowserWindow>& BrowserWindow)
{
    // 此时，可以将 BrowserWindow 的引用传递给负责 UI 的子系统
    UMyWebUIManager* UIManager = GetUIManager();
    if (UIManager)
    {
        UIManager->SetBrowserWindow(BrowserWindow);
        UIManager->InitializeWebViewBindings(); // 注册 UObjects 到 JS 的绑定
    }
}
```

## Demo 示例

以下是一个最小化的示例，展示如何在 UE 的 Actor 中集成该代理模块来管理浏览器窗口。

**MyNativeProxyActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WebBrowserNativeProxyModule.h"
#include "MyNativeProxyActor.generated.h"

UCLASS()
class AMyNativeProxyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyNativeProxyActor();

protected:
    virtual void BeginPlay() override;

    // 用于存储浏览器窗口的共享指针
    TSharedPtr<IWebBrowserWindow> CachedBrowserWindow;

    // 事件委托句柄，用于在销毁时解绑
    FDelegateHandle BrowserAvailableHandle;

private:
    // 响应浏览器窗口可用的回调
    void HandleBrowserAvailable(const TSharedRef<IWebBrowserWindow>& BrowserWindow);

    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
};
```

**MyNativeProxyActor.cpp**
```cpp
#include "MyNativeProxyActor.h"

AMyNativeProxyActor::AMyNativeProxyActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyNativeProxyActor::BeginPlay()
{
    Super::BeginPlay();

    // 检查代理模块是否可用
    if (IWebBrowserNativeProxyModule::IsAvailable())
    {
        IWebBrowserNativeProxyModule& ProxyModule = IWebBrowserNativeProxyModule::Get();

        // 尝试立即获取浏览器窗口
        CachedBrowserWindow = ProxyModule.GetBrowser(true);

        // 如果立即获取失败（例如，窗口需要异步创建），则订阅事件
        if (!CachedBrowserWindow.IsValid())
        {
            BrowserAvailableHandle = ProxyModule.OnBrowserAvailable().AddUObject(this, &AMyNativeProxyActor::HandleBrowserAvailable);
        }
        else
        {
            UE_LOG(LogTemp, Log, TEXT("Browser window obtained immediately."));
            // 立即执行与浏览器相关的操作
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("WebBrowserNativeProxy module is not available."));
    }
}

void AMyNativeProxyActor::HandleBrowserAvailable(const TSharedRef<IWebBrowserWindow>& BrowserWindow)
{
    CachedBrowserWindow = BrowserWindow.ToSharedPtr();
    UE_LOG(LogTemp, Log, TEXT("Browser window became available via event."));
    // 在此处执行任何需要浏览器窗口的初始化逻辑
}

void AMyNativeProxyActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理事件订阅
    if (BrowserAvailableHandle.IsValid() && IWebBrowserNativeProxyModule::IsAvailable())
    {
        IWebBrowserNativeProxyModule::Get().OnBrowserAvailable().Remove(BrowserAvailableHandle);
        BrowserAvailableHandle.Reset();
    }
    CachedBrowserWindow.Reset();
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

该插件模块依赖于提供 `IWebBrowserWindow` 接口的模块。

| 模块 | 用途 |
|---|---|
| `WebBrowser` | 提供浏览器窗口的核心接口 (`IWebBrowserWindow`)，是此代理模块功能的基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-11-10 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 移除了所有针对 UE 5.2 废弃 include 顺序的条件编译宏，属于代码清理。 |
| 2023-01-13 | `3c9aacb1` | [Engine/Plugins] | (插件配置或构建系统更新，非功能性改动) |
| 2023-01-12 | `2f78497e` | [Engine/Plugins] | (插件配置或构建系统更新，非功能性改动) |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新了内置插件的供应商链接以使用安全协议（HTTPS）。 |
| 2022-05-31 | `325c2bc0` | - Updating CEF to v90 (in prep for getting M1 version checked in) | 更新 CEF（Chromium Embedded Framework）版本至 v90，可能是为支持苹果 M1 芯片做准备。 |

### 维护评价

-   **创建时间**：该插件创建于 2019 年，已有约 6 年历史。
-   **更新频率**：从提交历史看，最后几次更新主要是**编译清理**、**配置更新**和**依赖库版本升级**，没有实质性的功能添加或 API 变更。最后一次涉及核心逻辑的更新可能在 2022 年或更早。
-   **活跃度**：**维护不活跃**。该模块的功能似乎已趋于稳定，没有迹象表明正在进行新的开发。
-   **推荐度**：这是一个针对特定嵌入式场景的**底层基础设施插件**。如果你的项目确实需要在原生应用中嵌入 UE 并管理单一的浏览器代理实例，它是必要组件。对于常规的 UE 桌面或主机游戏开发，则通常用不到此插件。由于其功能单一且稳定，在符合使用场景时可以依赖，但不应期望有新特性。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WebBrowserNativeProxy)
-   [官方文档]() (无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Plugins/WebBrowserNativeProxy) (推测路径)