# Android Fetch Background Download

> An Android plugin for enabling BackgroundHTTP requests to work while the app is backgrounded through use of the Fetch API.

| 属性 | 值 |
|---|---|
| 分类 | BackgroundHTTP |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | AndroidFetchBackgroundDownload (RuntimeNoCommandlet) |
| 创建时间 | 2021-06-14 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/Android/AndroidFetchBackgroundDownload) | |

## 用途

这是一个 **Android 平台专用** 的 BackgroundHTTP 后端实现插件。它解决了 UE5 的 BackgroundHTTP 系统在 Android 上的核心问题：**当应用被切到后台时，普通的 HTTP 下载会被系统杀死**。

该插件通过以下机制实现后台下载：
1. 利用 Android [Fetch](https://github.com/tonyofrancis/Fetch) 库（v3.2.0）在 Java 层管理下载任务
2. 通过 Android WorkManager (`AndroidBackgroundService` 插件) 将下载调度为前台服务（Foreground Service），使 Android 系统不会因应用后台化而终止下载
3. 下载进度和完成状态通过 JNI 回调桥接回 UE 的 C++ 层

插件注册为 `IBackgroundHttpModularFeature`，当条件满足（JNI 可用 + ConfigRules 未禁用）时自动接管 BackgroundHTTP 的平台实现。如果条件不满足，系统会回退到通用实现。

**依赖关系**：该插件依赖 `AndroidBackgroundService` 插件（提供 WorkManager 调度能力）和 `BackgroundHTTP` 模块（提供接口定义）。

## 使用场景

- 你的 Android 游戏需要下载大型资源包（如 DLC、热更新包），且用户可能在下载过程中切换到其他应用 → 使用此插件实现后台下载
- 你需要在下载过程中在通知栏显示进度、支持暂停/恢复/取消操作 → 此插件内置了完整的 Android 通知系统
- 你需要处理网络状态变化（飞行模式、数据节省、蜂窝网络限制）→ 此插件内置了这些场景的处理逻辑

## 蓝图用法

此插件 **没有暴露任何蓝图节点**。它是一个纯运行时后端实现，通过 BackgroundHTTP 模块的 ModularFeature 系统自动注册。用户通过 BackgroundHTTP 模块的通用接口（如 `FBackgroundHttpModule`）间接使用它。

## C++ 用法

### 头文件引入

```cpp
// BackgroundHTTP 接口
#include "BackgroundHttpModule.h"
#include "Interfaces/IBackgroundHttpManager.h"
#include "Interfaces/IBackgroundHttpRequest.h"
#include "Interfaces/IBackgroundHttpResponse.h"
```

> **注意**：通常不需要直接引用 AndroidFetchBackgroundDownload 的头文件。它作为 BackgroundHTTP 的平台后端自动工作。

### 基本用法

通过 BackgroundHTTP 模块的通用 API 创建和发送后台请求，Android 平台会自动使用 Fetch 实现：

```cpp
// 获取 BackgroundHTTP 管理器（Android 上自动使用 FAndroidPlatformBackgroundHttpManager）
FBackgroundHttpManagerPtr Manager = FBackgroundHttpModule::Get().GetBackgroundHttpManager();

// 创建后台下载请求
FBackgroundHttpRequestPtr Request = FPlatformBackgroundHttp::ConstructBackgroundRequest();

// 设置下载 URL（支持多个 URL 用于 fallback）
Request->SetURL(TEXT("https://example.com/largefile.pak"));

// 设置优先级（映射到 Android Fetch 的优先级：High=1, Normal=0, Low=-1）
Request->SetRequestPriority(EBackgroundHTTPPriority::Normal);

// 设置重试次数
Request->SetNumberOfRetries(3);

// 绑定完成回调
Request->GetOnProcessRequestComplete().BindLambda(
    [](FBackgroundHttpRequestPtr CompletedRequest, bool bSuccess)
    {
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("下载完成: %s"), *CompletedRequest->GetResponse()->GetTempFilePath());
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("下载失败"));
        }
    }
);

// 绑定进度回调（在游戏线程上触发）
Request->GetOnProgressUpdated().BindLambda(
    [](FBackgroundHttpRequestPtr InRequest, int64 TotalBytesDownloaded, int64 BytesDownloadedSinceLastUpdate)
    {
        UE_LOG(LogTemp, Log, TEXT("下载进度: %lld bytes"), TotalBytesDownloaded);
    }
);

// 发送请求 - 会通过 JNI 序列化为 JSON 并调度到 Android WorkManager
Manager->Add(Request);
Request->ProcessRequest();
```

### 进阶用法

#### 暂停与恢复

```cpp
// 暂停下载（线程安全，通过 volatile 标志 + Java 端列表实现）
Request->PauseRequest();

// 恢复下载
Request->ResumeRequest();

// 取消下载
Request->CancelRequest();
```

#### 蜂窝网络控制

```cpp
// 设置蜂窝网络偏好（通过 Console Variable 控制 Java 层的蜂窝处理）
// 0 = 仅 WiFi，1 = 允许蜂窝
IConsoleVariable* CVar = IConsoleManager::Get().FindConsoleVariable(TEXT("bgdl.EnableCellularHandling"));
if (CVar)
{
    CVar->Set(true);
}

// 或通过 Manager 设置蜂窝偏好
Manager->SetCellularPreference(1);
```

#### ConfigRules 控制

该插件支持通过 ConfigRules 远程控制开关。ConfigRules 中的 key 为 `AndroidBackgroundDownloadSetting`，可设置值：
- `Enabled` — 启用
- `Disabled` — 禁用（会取消已调度的后台工作）
- 未设置或其它值 — 默认启用

## Demo 示例

此插件是一个底层平台后端，通常不需要直接编写代码。以下是一个最小的 Build.cs 依赖配置示例：

```csharp
// YourModule.Build.cs
public class YourModule : ModuleRules
{
    public YourModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "BackgroundHTTP"  // 通过此模块间接使用 AndroidFetchBackgroundDownload
        });
    }
}
```

实际的下载代码通过 `BackgroundHTTP` 模块的 API 编写（见上方 C++ 用法章节）。AndroidFetchBackgroundDownload 插件在运行时自动注册为平台实现，无需在代码中显式引用。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心功能 |
| `Launch` | 启动相关 |
| `AndroidBackgroundService` | 提供 Android WorkManager 调度能力，用于将下载注册为前台服务 |
| `BackgroundHTTP` | 定义 BackgroundHTTP 接口（`IBackgroundHttpRequest`、`IBackgroundHttpManager` 等） |

### 第三方依赖

| 库 | 版本 | 用途 |
|---|---|---|
| [Fetch](https://github.com/tonyofrancis/Fetch) | 3.2.0 | Android 端下载管理引擎 |
| OkHttp | 4.12.0 | HTTP 客户端 |
| json-simple | 1.1.1 | JSON 解析（用于 DownloadDescription 序列化） |
| Kotlin stdlib | 2.0.20 | Fetch 库的 Kotlin 运行时依赖 |
| AndroidX Room | 2.7.1 | Fetch 库的数据库依赖 |

## 架构概览

```
┌─────────────────────────────────────────────────────┐
│                 UE Game Thread                       │
│  BackgroundHTTP API → FBackgroundHttpModule          │
│         ↓                                           │
│  FAndroidPlatformBackgroundHttpManager               │
│    - ActivatePendingRequests() → JNI 序列化为 JSON    │
│    - Tick() → 处理 Java 回调、更新进度、完成请求       │
│    - Pause/Resume/Cancel → 线程安全标志交换           │
└──────────────────┬──────────────────────────────────┘
                   │ JNI 回调
┌──────────────────▼──────────────────────────────────┐
│              Android Java Layer                      │
│  UEDownloadWorker (WorkManager Worker)               │
│    - 前台服务 + 通知栏显示进度                         │
│    - 网络状态监控（飞行模式/数据节省/无网络）           │
│  FetchManager                                        │
│    - 使用 Fetch 库管理实际下载                        │
│    - 支持暂停/恢复/重试                               │
└─────────────────────────────────────────────────────┘
```

### 关键类说明

| 类 | 文件 | 职责 |
|---|---|---|
| `FAndroidFetchBackgroundDownloadModule` | Module.cpp/h | 模块入口，启动时注册 ModularFeature |
| `FAndroidPlatformBackgroundHttpModularFeatureWrapper` | ModularFeatureWrapper.cpp/h | 包装器，将 ModularFeature 调用路由到 Fetch 实现 |
| `FAndroidFetchPlatformBackgroundHttp` | FetchPlatformBackgroundHttp.cpp/h | 工厂类，创建 Manager/Request/Response 实例 |
| `FAndroidPlatformBackgroundHttpManager` | Manager.cpp/h | 核心管理器，处理请求调度、JNI 回调、线程同步 |
| `FAndroidPlatformBackgroundHttpRequest` | Request.cpp/h | 请求实现，序列化为 JSON 供 Java 层解析 |
| `FAndroidPlatformBackgroundHttpResponse` | Response.cpp/h | 响应实现，持有临时文件路径和状态码 |
| `UEDownloadWorker` | Java | Android WorkManager Worker，前台服务执行下载 |
| `FetchManager` | Java | 封装 Fetch 库，实际执行 HTTP 下载 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-02 | `e37dc67c76e4` | Fix TargetSDK 35 compat issues with background download — 修复 Android Target SDK 35 的兼容性问题 |
| 2025-09-11 | `6312e16dd97c` | Fix crash from pending JNI exception in non-Shipping builds — 修复非 Shipping 构建中 JNI 异常导致的崩溃 |
| 2025-09-02 | `5a48f72f610f` | Registered JNI functions. Made JNI classes for Java classes. Added thread_local Ue::Jni::Env global. Various JNI bug fixes and cleanup — JNI 重构：注册 JNI 函数、创建类型安全的 JNI 类包装、线程局部 JNI 环境 |

### 维护评价

- **创建时间**：2021-06-14，约 4.8 年历史
- **活跃程度**：**活跃维护** — 最近 3 次更新集中在 2025 年 9-10 月，均为实质性修复和改进
- **维护趋势**：近期聚焦于 JNI 层的现代化改造和新 Android SDK 版本兼容
- **平台限制**：仅适用于 Android，需要 `AndroidBackgroundService` 插件配合
- **启用方式**：`EnabledByDefault: false`，需要手动在 .uproject 或插件设置中启用
- **推荐**：如果你的 Android 项目需要后台下载大文件（DLC、资源包等），推荐启用此插件。它是 Epic 官方维护的 BackgroundHTTP Android 后端，经过 Fortnite 等大型项目的实战验证

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/Android/AndroidFetchBackgroundDownload)
- [Fetch 库 (第三方)](https://github.com/tonyofrancis/Fetch)
- 依赖插件: AndroidBackgroundService、BackgroundHTTP
