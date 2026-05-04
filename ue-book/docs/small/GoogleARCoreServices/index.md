# Google ARCore Services

> Provide functionality in Google cross-platform ARCore services.

| 属性 | 值 |
|---|---|
| 分类 | Augmented Reality |
| 默认启用 | ❌ No |
| 包含内容 | Yes |
| 模块 | GoogleARCoreServices (Runtime) |
| 创建时间 | 2018-07-27 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AR/Google/GoogleARCoreServices) | |

## 用途

GoogleARCoreServices 是一个围绕 **Google ARCore Cloud Anchors** 功能的 UE5 封装插件。它解决的核心问题是：**让多个设备共享同一个 AR 锚点（Anchor），实现跨设备 AR 协作体验**。

具体来说，这个插件做了两件事：

1. **Host（托管）**：将设备上创建的 ARPin 上传到 Google 云端，获得一个 CloudID
2. **Resolve（解析）**：通过 CloudID 从云端下载锚点，在本地设备上重建 ARPin

底层通过 ARCore C API 直接与 Google AR Cloud Service 通信。Android 平台使用 `arcore_c_api.h`，iOS 平台使用 `arcore_ios_c_api.h`（跨平台支持）。

> ⚠️ 这个插件需要 Google Cloud API Key 且需要联网。启用后会增加 feature/IMU 测量缓冲区的开销。

## 使用场景

- **多人 AR 游戏**：多个手机看到同一个虚拟物体出现在真实世界的同一位置
- **AR 导览/标记**：在一个设备上放置虚拟标记，其他设备扫描后能看到
- **远程协作**：用户 A 扫描环境并上传锚点，用户 B 下载后能在同一位置看到虚拟内容
- **持久化 AR 内容**：将 AR 物体"钉"在真实世界位置，下次回来仍然存在（锚点有 Lifetime 配置）

## 蓝图用法

### 配置节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Config Google ARCore Services` | 配置 AR 会话，启用/禁用 Cloud Anchor 模式 | `UGoogleARCoreServicesFunctionLibrary` |

### Cloud ARPin 节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create and Host Cloud ARPin (Latent)` | 将本地 ARPin 托管到云端，等待完成（Latent 异步） | `UGoogleARCoreServicesFunctionLibrary` |
| `Create and Resolve Cloud ARPin (Latent)` | 通过 CloudID 从云端解析锚点，等待完成（Latent 异步） | `UGoogleARCoreServicesFunctionLibrary` |
| `Create and Host Cloud ARPin` | 立即启动托管流程，不等待结果 | `UGoogleARCoreServicesFunctionLibrary` |
| `Create and Resolve Cloud ARPin` | 立即启动解析流程，不等待结果 | `UGoogleARCoreServicesFunctionLibrary` |
| `Remove Cloud ARPin` | 移除一个 Cloud ARPin | `UGoogleARCoreServicesFunctionLibrary` |
| `Get All Cloud ARPin` | 获取当前会话中所有 Cloud ARPin | `UGoogleARCoreServicesFunctionLibrary` |

### Cloud ARPin 查询节点（UCloudARPin 上）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cloud ID` | 获取云端锚点 ID（成功后非空） | `UCloudARPin` |
| `Get ARPin Cloud State` | 获取云端状态（每帧更新一次） | `UCloudARPin` |

### 使用示例（蓝图描述）

**基本 Host 流程：**

1. 使用 `Start AR Session` 启动 AR 会话
2. 调用 `Config Google ARCore Services`，设置 `ARPinCloudMode = Enabled`
3. 当 ARPin 追踪质量良好时，调用 `Create and Host Cloud ARPin (Latent)`
   - 输入：`ARPinToHost`（要托管的 ARPin）、`LifetimeInDays`（默认 1 天）
   - 输出：`OutHostingResult`（结果枚举）、`OutCloudARPin`（云端锚点对象）
4. 完成后检查 `OutHostingResult == Success`
5. 调用 `Get Cloud ID` 获取 CloudID 字符串，发送给其他设备

**基本 Resolve 流程：**

1. 收到其他设备发来的 CloudID 字符串
2. 调用 `Create and Resolve Cloud ARPin (Latent)`
   - 输入：`CloudId`（字符串）
   - 输出：`OutAcquiringResult`、`OutCloudARPin`
3. 完成后检查 `OutAcquiringResult == Success`
4. 使用 `OutCloudARPin` 的 Transform 在相同位置放置虚拟物体

**非 Latent 版本用法：**

非 Latent 版本（`Create and Host Cloud ARPin` / `Create and Resolve Cloud ARPin`）会立即返回 `UCloudARPin*`，你需要在每帧轮询 `Get ARPin Cloud State` 来检查是否完成。适合需要自定义轮询逻辑的场景。

## C++ 用法

### 头文件引入

```cpp
#include "GoogleARCoreServicesFunctionLibrary.h"
#include "GoogleARCoreServicesTypes.h"
```

### 基本用法

**配置 Cloud Anchors：**

```cpp
// 启用 Cloud ARPin 模式
FGoogleARCoreServicesConfig Config;
Config.ARPinCloudMode = EARPinCloudMode::Enabled;
bool bSuccess = UGoogleARCoreServicesFunctionLibrary::ConfigGoogleARCoreServices(Config);
```

**Host 一个 ARPin（Latent）：**

```cpp
// 在蓝图 Latent Action 中使用，C++ 中通常用非 Latent 版本
EARPinCloudTaskResult TaskResult;
UCloudARPin* CloudPin = UGoogleARCoreServicesFunctionLibrary::CreateAndHostCloudARPin(
    MyARPin,          // UARPin* 要托管的锚点
    1,                 // int32 存活天数
    TaskResult         // EARPinCloudTaskResult& 输出结果
);

if (TaskResult == EARPinCloudTaskResult::Started)
{
    // 托管任务已启动，每帧检查状态
    ECloudARPinCloudState State = CloudPin->GetARPinCloudState();
    if (State == ECloudARPinCloudState::Success)
    {
        FString CloudID = CloudPin->GetCloudID();
        // 发送 CloudID 给其他设备
    }
}
```

**Resolve 一个 CloudID：**

```cpp
EARPinCloudTaskResult TaskResult;
UCloudARPin* CloudPin = UGoogleARCoreServicesFunctionLibrary::CreateAndResolveCloudARPin(
    CloudIDString,     // FString 从其他设备获取的 CloudID
    TaskResult
);

if (TaskResult == EARPinCloudTaskResult::Started)
{
    // 等待解析完成...
    // CloudPin->GetARPinCloudState() == ECloudARPinCloudState::Success 时
    // 可以使用 CloudPin->GetLocalToWorldTransform() 获取位置
}
```

### 进阶用法

**管理所有 Cloud ARPin：**

```cpp
// 获取当前会话中所有 Cloud ARPin
TArray<UCloudARPin*> AllPins = UGoogleARCoreServicesFunctionLibrary::GetAllCloudARPin();

for (UCloudARPin* Pin : AllPins)
{
    ECloudARPinCloudState State = Pin->GetARPinCloudState();
    if (State == ECloudARPinCloudState::Success)
    {
        UE_LOG(LogTemp, Log, TEXT("Cloud Pin %s at %s"), 
            *Pin->GetCloudID(), 
            *Pin->GetLocalToWorldTransform().GetLocation().ToString());
    }
}

// 移除不再需要的 Cloud ARPin
UGoogleARCoreServicesFunctionLibrary::RemoveCloudARPin(PinToRemove);
```

**错误处理：**

```cpp
// ECloudARPinCloudState 的常见错误状态：
// - ErrorNotAuthorized: API Key 无效
// - ErrorServiceUnavailable: 网络不可达
// - ErrorResourceExhausted: API 配额用尽
// - ErrorHostingDatasetProcessingFailed: 环境数据不足，需要多扫描
// - ErrorResolvingCloudIDNotFound: CloudID 不存在
// - ErrorSDKVersionTooOld/TooNew: SDK 版本不匹配

EARPinCloudTaskResult Result;
UCloudARPin* Pin = UGoogleARCoreServicesFunctionLibrary::CreateAndHostCloudARPin(
    MyARPin, 1, Result);

switch (Result)
{
case EARPinCloudTaskResult::CloudARPinNotEnabled:
    // 未调用 ConfigGoogleARCoreServices 启用 Cloud 模式
    break;
case EARPinCloudTaskResult::SessionPaused:
    // AR 会话未运行
    break;
case EARPinCloudTaskResult::NotTracking:
    // 设备未在追踪（质量不足）
    break;
case EARPinCloudTaskResult::Started:
    // 成功启动，等待 CloudPin 状态更新
    break;
}
```

## Demo 示例

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "GoogleARCoreServices",
    "AugmentedReality",
    "HeadMountedDisplay"
});
```

**最小 C++ 示例 — Host 和 Resolve：**

```cpp
// MyARCloudAnchorManager.h
#pragma once
#include "CoreMinimal.h"
#include "GoogleARCoreServicesTypes.h"

class FMyARCloudAnchorManager
{
public:
    void EnableCloudAnchors();
    void HostPin(UARPin* PinToHost);
    void ResolvePin(const FString& CloudID);
    void Tick(float DeltaTime);

private:
    UCloudARPin* PendingHostPin = nullptr;
    UCloudARPin* PendingResolvePin = nullptr;
};

// MyARCloudAnchorManager.cpp
#include "MyARCloudAnchorManager.h"
#include "GoogleARCoreServicesFunctionLibrary.h"

void FMyARCloudAnchorManager::EnableCloudAnchors()
{
    FGoogleARCoreServicesConfig Config;
    Config.ARPinCloudMode = EARPinCloudMode::Enabled;
    UGoogleARCoreServicesFunctionLibrary::ConfigGoogleARCoreServices(Config);
}

void FMyARCloudAnchorManager::HostPin(UARPin* PinToHost)
{
    EARPinCloudTaskResult Result;
    PendingHostPin = UGoogleARCoreServicesFunctionLibrary::CreateAndHostCloudARPin(
        PinToHost, 1, Result);
    
    if (Result != EARPinCloudTaskResult::Started)
    {
        UE_LOG(LogTemp, Error, TEXT("Host failed: %d"), (int)Result);
        PendingHostPin = nullptr;
    }
}

void FMyARCloudAnchorManager::ResolvePin(const FString& CloudID)
{
    EARPinCloudTaskResult Result;
    PendingResolvePin = UGoogleARCoreServicesFunctionLibrary::CreateAndResolveCloudARPin(
        CloudID, Result);
    
    if (Result != EARPinCloudTaskResult::Started)
    {
        UE_LOG(LogTemp, Error, TEXT("Resolve failed: %d"), (int)Result);
        PendingResolvePin = nullptr;
    }
}

void FMyARCloudAnchorManager::Tick(float DeltaTime)
{
    // 检查 Host 结果
    if (PendingHostPin && PendingHostPin->GetARPinCloudState() != ECloudARPinCloudState::InProgress)
    {
        if (PendingHostPin->GetARPinCloudState() == ECloudARPinCloudState::Success)
        {
            UE_LOG(LogTemp, Log, TEXT("Hosted! CloudID: %s"), *PendingHostPin->GetCloudID());
            // TODO: 发送 CloudID 给其他设备
        }
        PendingHostPin = nullptr;
    }
    
    // 检查 Resolve 结果
    if (PendingResolvePin && PendingResolvePin->GetARPinCloudState() != ECloudARPinCloudState::InProgress)
    {
        if (PendingResolvePin->GetARPinCloudState() == ECloudARPinCloudState::Success)
        {
            FTransform WorldTransform = PendingResolvePin->GetLocalToWorldTransform();
            UE_LOG(LogTemp, Log, TEXT("Resolved at: %s"), *WorldTransform.GetLocation().ToString());
            // TODO: 在该位置放置虚拟物体
        }
        PendingResolvePin = nullptr;
    }
}
```

## 模块依赖

从 `GoogleARCoreServices.Build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `HeadMountedDisplay` | XR 追踪系统基础接口 |
| `AugmentedReality` | UE AR 框架（UARPin、ARSession 等） |
| `Core` | UE 核心库（私有依赖） |
| `CoreUObject` | UObject 系统（私有依赖） |
| `Engine` | 引擎核心（私有依赖） |
| `GoogleARCoreSDK` | Google ARCore C API 封装（私有依赖） |
| `XRBase` | XR 基础设施（插件依赖） |

> ⚠️ 你的模块如果要使用此插件，至少需要依赖 `GoogleARCoreServices` 和 `AugmentedReality`。

## 平台支持

| 平台 | 支持 | 说明 |
|---|---|---|
| Android | ✅ | 主要目标平台，通过 `arcore_c_api.h` |
| iOS | ✅ | 通过 `arcore_ios_c_api.h`，需要单独的 ARCore iOS API Key |
| Win64 | ⚠️ | 编译通过但实际功能在 Android/iOS 上 |
| Mac | ⚠️ | 同上 |
| Linux | ⚠️ | 同上 |

## 编辑器设置

在 **Project Settings → Plugins → GoogleARCoreServices** 中可配置：

| 设置项 | 说明 |
|---|---|
| `AndroidAPIKey` | Android 平台的 Google Cloud Anchor API Key |
| `IOSAPIKey` | iOS 平台的 Google Cloud Anchor API Key |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-03-27 | `7a3b70c` | ARCoreServices breaks ARCore with Vulkan | 修复 Vulkan 下启用 Cloud Anchors 丢失其他设置的 bug；移除了已废弃的 ARCoreCloudAnchors 框架 |
| 2024-05-15 | `443aafd` | Non unity fixes | Unity 构建模式兼容性修复 |
| 2023-06-01 | `1d6cbf1` | GoogleARCoreServices iOS compile fixes | iOS 编译修复，标注了旧代码需要更新但尚未完成 |

### 维护评价

- **创建时间**：2018-07-27，已存在约 7 年
- **最近更新**：2025-03-27 有实质性修复（Vulkan 兼容性），说明仍在维护
- **更新频率**：较低（2023、2024、2025 各一次），但每次都是实际问题修复
- **状态**：**维护中但不活跃** — 核心功能稳定，偶尔修复兼容性问题
- **已知限制**：
  - `EnabledByDefault = false`，需要手动启用
  - iOS 平台使用旧的 Cloud Anchor 异步 API（`ARCORE_USE_OLD_CLOUD_ANCHOR_ASYNC`），代码注释提到需要更新
  - `UCloudARPin` 类标记为 `Experimental`
- **推荐**：如果你的项目需要跨设备 AR 协作，这是 UE5 中唯一的选择。功能完整但处于维护模式。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AR/Google/GoogleARCoreServices)
- [Google ARCore Cloud Anchors 文档](https://developers.google.com/ar/develop/cloud-anchors)
- [Google ARCore Services 官网](https://developers.google.com/ar/)
