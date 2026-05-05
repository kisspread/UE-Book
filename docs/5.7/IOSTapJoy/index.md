# IOS TapJoy Advertising Provider

> IOS TapJoy Provider

| 属性 | 值 |
|---|---|
| 分类 | Advertising |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | IOSTapJoy (Runtime) |
| 创建时间 | 2014-05-07 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Advertising/IOSTapJoy) | |

## 用途

IOSTapJoy 是 UE5 内置的 [Tapjoy](https://www.tapjoy.com/) 广告 SDK 集成插件，为 iOS 平台提供广告展示能力。

它通过实现 `IAdvertisingProvider` 接口，将 Tapjoy 的展示广告（Display Ad）和插屏广告（Interstitial Ad）功能接入 UE 的通用广告框架。插件本身是一个极薄的桥接层——将 UE 侧的 C++ 调用转发到 Tapjoy 原生 Objective-C SDK，所有广告逻辑由 Tapjoy SDK 处理。

该插件属于 UE4 时代的遗留代码。Tapjoy SDK 的 `.embeddedframework.zip` 早在 2016 年打包，Objective-C 代码使用的是过时的 Tapjoy API（如 `TJC_CONNECT_SUCCESS` 通知、`TJCAdView`、`TJC_DISPLAY_AD_SIZE_320X50` 等），且插屏广告相关方法全部为空实现。**这意味着插件已经基本不可用。**

## 使用场景

- 你在做一个 iOS 游戏，需要通过 Tapjoy 进行广告变现 → 考虑使用（但建议检查 SDK 版本是否仍然可用）
- 你需要跨平台广告支持（Android、PC 等）→ 不适用，此插件仅限 iOS
- 你需要插屏广告 → 不可用，插屏接口全部为空实现
- 你需要现代广告 SDK（如 AdMob、ironSource、AppLovin MAX）→ 使用其他方案

> ⚠️ **重要提示**：此插件默认未启用（`EnabledByDefault: false`），且只在 iOS 平台可用（`PlatformAllowList: ["IOS"]`）。Tapjoy SDK 已非常陈旧，插屏广告功能完全未实现。在生产环境中使用前，请务必验证 SDK 的兼容性。

## 蓝图用法

此插件 **没有暴露任何蓝图接口**。没有 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。

广告的展示通过 UE 的通用 `IAdvertisingProvider` 接口管理，但该接口本身也未提供蓝图节点。

## C++ 用法

### 头文件引入

```cpp
// 使用 Advertising 模块的通用接口
#include "Interfaces/IAdvertisingProvider.h"
```

> 注意：没有独立的 IOSTapJoy 公开头文件。该插件通过模块注册机制自动加载，使用者通过 `IAdvertisingProvider` 接口间接调用。

### 配置

插件通过 `Engine.ini` 配置文件读取 Tapjoy 的连接参数：

```ini
[TapJoy]
AppID=YOUR_TAPJOY_APP_ID
SecretKey=YOUR_TAPJOY_SECRET_KEY
CurrencyString=CURRENCY_ID
```

这些配置在模块启动时（`StartupModule`）通过 `GConfig->GetString` 从 `GEngineIni` 读取。

### 工作原理

插件的核心是一个 Objective-C 桥接类 `IOSTapJoy` 和一个 C++ 模块类 `FTapJoyProvider`：

**启动流程**：
1. `FTapJoyProvider::StartupModule()` 从配置文件读取 AppID、SecretKey、CurrencyString
2. 在主线程调用 `[Tapjoy requestTapjoyConnect:secretKey:options:]` 连接 Tapjoy 服务
3. 连接结果通过 `NSNotificationCenter` 的 `TJC_CONNECT_SUCCESS` / `TJC_CONNECT_FAILED` 通知返回

**广告展示流程**：
1. 调用 `ShowAdBanner(bShowOnBottomOfScreen, adID)`
2. 通过 `[Tapjoy getDisplayAdWithDelegate:]` 请求广告
3. 广告到达后 `didReceiveAd:` 回调将 `TJCAdView` 添加到 iOS 根视图
4. 使用 UIView 动画淡入展示（0.4 秒过渡）

**隐藏广告**：
1. 调用 `HideAdBanner()` / `CloseAdBanner()`
2. 遍历根视图找到 `TJCAdView` 子视图
3. 使用 UIView 动画淡出（0.4 秒过渡），完成后隐藏

### 关键实现细节

```cpp
// FTapJoyProvider 实现了 IAdvertisingProvider 接口
class FTapJoyProvider : public IAdvertisingProvider
{
    virtual void StartupModule() override;   // 初始化 Tapjoy SDK
    virtual void ShutdownModule() override;  // 空实现

    // 广告横幅
    virtual void ShowAdBanner(bool bShowOnBottomOfScreen, int32 adID) override;  // 已实现
    virtual void HideAdBanner() override;   // 已实现（带动画淡出）
    virtual void CloseAdBanner() override;  // 转发到 HideAdBanner
    virtual int32 GetAdIDCount() override;  // 始终返回 1

    // 插屏广告 - 全部为空实现
    virtual void LoadInterstitialAd(int32 adID) override;       // 空
    virtual bool IsInterstitialAdAvailable() override;           // 始终返回 false
    virtual bool IsInterstitialAdRequested() override;           // 始终返回 false
    virtual void ShowInterstitialAd() override;                  // 空
};
```

### 基本用法

由于插件通过 `IAdvertisingProvider` 接口注册，实际使用时需要通过 `FAdvertising` 子系统（如果存在）来调用。直接使用示例：

```cpp
// 插件会在启动时自动注册为广告提供者
// 通过 Advertising 模块调用（如果项目启用了 IOSTapJoy 插件）
// 注意：bShowOnBottomOfScreen 参数在当前实现中未被使用
// adID 参数也被忽略，GetAdIDCount() 固定返回 1
```

> 来源：`Engine/Plugins/Runtime/Advertising/IOSTapJoy/Source/IOSTapJoy/Private/IOSTapJoy.cpp`

## Demo 示例

由于此插件是纯底层 SDK 桥接，且没有公开 API，无法提供独立的编译示例。使用此插件的基本步骤：

1. 在 iOS 设备上配置 Tapjoy 开发者账号
2. 在项目的 `Engine.ini` 中添加 Tapjoy 配置
3. 在项目设置中启用 IOSTapJoy 插件
4. 打包 iOS 项目

```ini
; DefaultEngine.ini
[TapJoy]
AppID=your_app_id_here
SecretKey=your_secret_key_here
CurrencyString=virtual_currency_id
```

## 模块依赖

从 `Build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心模块 |
| `Advertising` | 广告框架接口（私有依赖） |
| `ApplicationCore` | 应用核心功能（私有依赖） |

### iOS Framework 依赖

插件还链接了以下 iOS 原生框架：

| Framework | 用途 |
|---|---|
| `EventKit` | 事件日历访问 |
| `MediaPlayer` | 媒体播放 |
| `AdSupport` | 广告标识符（IDFA） |
| `CoreLocation` | 位置信息 |
| `SystemConfiguration` | 网络状态检测 |
| `MessageUI` | 邮件/短信 |
| `Security` | 安全存储 |
| `CoreTelephony` | 蜂窝网络信息 |
| `Twitter` | Twitter 集成（已废弃） |
| `Social` | 社交框架 |

### 第三方 SDK

| SDK | 位置 |
|---|---|
| Tapjoy Embedded Framework | `ThirdPartyFrameworks/Tapjoy.embeddedframework.zip` |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2022-11-07 | `0a10c21f` | Update Release-Engine-Staging from UE5/Main | 批量同步更新，非针对性改动 |
| 2022-09-09 | `3377a914` | Pass 3 on cleaning up build.cs files | Build.cs 清理重构，非功能更新 |
| 2021-10-04 | `666e90e9` | Updated .uplugin and .uproject to use AllowList/DenyList keys | 全局 API 重命名，非针对性改动 |

### 维护评价

**评级：可能废弃 / 不推荐使用**

- **年龄**：12 年以上（2014 年创建），属于 UE4 早期遗留代码
- **最后实质性更新**：2014-2015 年间，此后无任何功能更新
- **近 3 次 commit**：全部是全局性批量改动（Build 清理、API 重命名、分支同步），没有针对 Tapjoy 功能的任何维护
- **SDK 陈旧**：捆绑的 Tapjoy SDK 是 2016 年打包的版本，Tapjoy 的 API 已经大幅变更
- **插屏广告未实现**：`LoadInterstitialAd`、`ShowInterstitialAd`、`IsInterstitialAdAvailable`、`IsInterstitialAdRequested` 全部为空实现
- **`ShutdownModule()` 为空**：没有做任何清理
- **缺少头文件**：没有 `.h` 文件，无法在 C++ 中直接引用该模块的类
- **Tapjoy 平台现状**：Tapjoy 在 2022 年被 Unity 收购后已逐步整合到 Unity Ads 生态，独立 SDK 的长期可用性存疑

> ⚠️ **警告**：此插件超过 10 年没有实质性更新，绑定的 SDK 版本已严重过时。不建议在生产环境中使用。如需 iOS 广告功能，建议使用现代广告聚合平台（如 AdMob、ironSource、AppLovin MAX）并自行集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Advertising/IOSTapJoy)
- [IAdvertisingProvider 接口](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/Advertising/Advertising/Public/Interfaces/IAdvertisingProvider.h)
- [Tapjoy 官网](https://www.tapjoy.com/)
