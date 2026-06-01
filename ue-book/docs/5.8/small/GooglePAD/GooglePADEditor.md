# GooglePAD

> Google Play Asset Delivery for Android.

| 属性 | 值 |
|---|---|
| 中文名 | 谷歌资源分发 |
| 分类 | Android |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GooglePAD` (Runtime), `GooglePADEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-04-21 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GooglePAD) | |

## 用途

GooglePAD 插件是对 **Google Play Asset Delivery (PAD)** API 的 UE 封装，用于 Android 平台上按需下载游戏资产（纹理、音频、关卡等）。它解决的核心问题是：**将大型游戏包拆分为按需下载的资产包，减少初始安装体积**。

Google Play 在 2020 年用 PAD 取代了之前的 OBB 扩展文件机制，要求开发者将超过 150MB 的资产拆分为可按需分发的 Asset Packs。本插件提供了从 UE 打包流水线到运行时下载管理的完整集成，使开发者无需直接处理 JNI 调用和 Android Gradle 配置。

插件同时在 Win64/Mac/Linux 编辑器上提供编辑器模块，用于配置和构建流程集成。

## 使用场景

- 你的 Android 游戏包体超过 150MB，需要拆分资产以通过 Google Play 审核 → 用 GooglePAD
- 你需要实现"先下载核心包，进入游戏后再按需下载高清纹理/DLC 关卡" → 配置 GooglePAD Asset Packs
- 你只想在发行版/正式版构建中启用 PAD，开发阶段仍用本地资产 → 使用 `bOnlyDistribution` 或 `bOnlyShipping` 设置

## 蓝图用法

GooglePAD 提供了运行时蓝图 API 用于管理 Asset Pack 的下载和状态查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RequestInfo` | 请求 Asset Pack 信息 | `UGooglePADFunctionLibrary` |
| `RequestDownload` | 请求下载指定 Asset Pack | `UGooglePADFunctionLibrary` |
| `GetDownloadStatus` | 获取 Asset Pack 下载状态 | `UGooglePADFunctionLibrary` |
| `GetDownloadState` | 获取下载状态枚举值 | `UGooglePADFunctionLibrary` |
| `GetDownloadTotalBytes` | 获取下载总字节数 | `UGooglePADFunctionLibrary` |
| `GetDownloadReceivedBytes` | 获取已下载字节数 | `UGooglePADFunctionLibrary` |
| `GetShowCellularDataConfirmationStatus` | 获取蜂窝数据确认状态 | `UGooglePADFunctionLibrary` |
| `ShowCellularDataConfirmation` | 弹出蜂窝数据使用确认 | `UGooglePADFunctionLibrary` |
| `CancelDownload` | 取消进行中的下载 | `UGooglePADFunctionLibrary` |
| `ReleaseDownloadState` | 释放下载状态资源 | `UGooglePADFunctionLibrary` |
| `ReleaseAssetPackLocation` | 释放 Asset Pack 位置资源 | `UGooglePADFunctionLibrary` |

### 使用示例（蓝图描述）

**基础下载流程：**

1. 使用 `RequestInfo` 节点，传入 Asset Pack 名称（如 `"highres_textures"`），获得请求 Request ID
2. 轮询或绑定事件，通过 Request ID 查询获取信息结果
3. 使用 `RequestDownload` 发起下载
4. 使用 `GetDownloadStatus` 循环查询状态，当返回 `Downloaded` 时下载完成
5. 使用 `GetAssetPackPath` 获取已下载资产的磁盘路径，用于加载资产
6. 完成后调用 `ReleaseDownloadState` 释放资源

**蜂窝数据确认：**

1. 下载前调用 `ShowCellularDataConfirmation` 让用户确认是否使用移动数据
2. 通过 `GetShowCellularDataConfirmationStatus` 查询用户选择结果
3. 根据结果决定是否继续下载

## C++ 用法

### 头文件引入

```cpp
#include "GooglePAD.h"
```

### 基本用法

```cpp
// 在 Android 设备上请求 Asset Pack 信息
#include "GooglePAD.h"

// 请求资产包信息
int32 RequestId = FGooglePAD::RequestInfo({TEXT("game_assets")});
// RequestId 用于后续查询结果状态

// 查询信息请求结果
EGooglePADStatus InfoStatus = FGooglePAD::GetRequestStatus(RequestId);
if (InfoStatus == EGooglePADStatus::Available)
{
    // 发起下载
    int32 DownloadRequestId = FGooglePAD::RequestDownload({TEXT("game_assets")});
}

// 查询下载状态
EGooglePADStatus DownloadStatus = FGooglePAD::GetDownloadStatus(DownloadRequestId);
if (DownloadStatus == EGooglePADStatus::Downloaded)
{
    // 获取下载路径并加载资产
    FString AssetPath = FGooglePAD::GetAssetPackPath(TEXT("game_assets"));
    // 使用 AssetPath 加载本地资产
}
```

### 进阶用法

```cpp
// 带进度追踪的下载管理
void UMyGameInstance::StartAssetPackDownload(const FString& PackName)
{
    // 先请求信息
    int32 InfoRequest = FGooglePAD::RequestInfo({PackName});
    
    // 在 Tick 或定时器中轮询（PAD API 是异步的）
    GetWorld()->GetTimerManager().SetTimer(PollTimerHandle, [this, InfoRequest, PackName]()
    {
        EGooglePADStatus Status = FGooglePAD::GetRequestStatus(InfoRequest);
        
        switch (Status)
        {
        case EGooglePADStatus::Available:
        {
            // 信息就绪，开始下载
            int32 DownloadRequest = FGooglePAD::RequestDownload({PackName});
            // 继续轮询下载进度...
            break;
        }
        case EGooglePADStatus::Unavailable:
            UE_LOG(LogTemp, Warning, TEXT("Asset pack %s is not available"), *PackName);
            break;
        case EGooglePADStatus::Downloading:
        case EGooglePADStatus::Downloaded:
            break;
        }
    }, 0.5f, true);  // 每 0.5 秒轮询
}
```

## Demo 示例

```cpp
// GooglePADExample.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "GooglePAD.h"
#include "GooglePADExample.generated.h"

UCLASS()
class UGooglePADExample : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    // 请求并下载指定资产包
    UFUNCTION(BlueprintCallable, Category = "GooglePAD|Example")
    void DownloadAssetPack(const FString& PackName);

    // 获取下载进度 (0.0 ~ 1.0)
    UFUNCTION(BlueprintPure, Category = "GooglePAD|Example")
    float GetProgress() const { return Progress; }

    UFUNCTION(BlueprintPure, Category = "GooglePAD|Example")
    bool IsDownloaded() const { return bDownloaded; }

    // 获取已下载资产包的路径
    UFUNCTION(BlueprintPure, Category = "GooglePAD|Example")
    FString GetDownloadedPath() const { return DownloadedPath; }

private:
    void OnInfoReceived();
    void OnDownloadComplete();

    FString CurrentPackName;
    int32 InfoRequestId = -1;
    int32 DownloadRequestId = -1;
    float Progress = 0.0f;
    bool bDownloaded = false;
    FString DownloadedPath;
};
```

```cpp
// GooglePADExample.cpp
#include "GooglePADExample.h"

void UGooglePADExample::DownloadAssetPack(const FString& PackName)
{
    CurrentPackName = PackName;
    bDownloaded = false;
    Progress = 0.0f;
    InfoRequestId = FGooglePAD::RequestInfo({PackName});
}

void UGooglePADExample::OnInfoReceived()
{
    EGooglePADStatus Status = FGooglePAD::GetRequestStatus(InfoRequestId);
    if (Status == EGooglePADStatus::Available)
    {
        DownloadRequestId = FGooglePAD::RequestDownload({CurrentPackName});
    }
}

void UGooglePADExample::OnDownloadComplete()
{
    EGooglePADStatus Status = FGooglePAD::GetDownloadStatus(DownloadRequestId);
    if (Status == EGooglePADStatus::Downloaded)
    {
        bDownloaded = true;
        Progress = 1.0f;
        DownloadedPath = FGooglePAD::GetAssetPackPath(CurrentPackName);
        FGooglePAD::ReleaseDownloadState(DownloadRequestId);
    }
    else if (Status == EGooglePADStatus::Downloading)
    {
        int64 Total = FGooglePAD::GetDownloadTotalBytes(DownloadRequestId);
        int64 Received = FGooglePAD::GetDownloadReceivedBytes(DownloadRequestId);
        if (Total > 0)
        {
            Progress = static_cast<float>(Received) / static_cast<float>(Total);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AndroidRuntimeSettings` | 读取 Android 平台构建配置（仅 Editor 模块） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新 API UE_LOGF |
| 2025-09-17 | `2e280ccd` | Update GooglePAD to 1.15.4 / 2.3.0 | 升级 GooglePAD SDK 到 1.15.4 / 2.3.0 |
| 2025-09-02 | `7d7255e0` | Registered JNI functions. Made JNI classes for Java classes. Added thread_local Ue::Jni::Env global. | 重构 JNI 层：注册 JNI 函数、封装 Java 类、添加线程局部 JNI 环境 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 添加内联生成宏优化编译 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar | 统一导出符号声明格式 |

### 维护评价

GooglePAD 插件**维护活跃**，最近一次更新在 2026 年 4 月，且近期有多次实质性功能更新（SDK 升级、JNI 层重构）。作为 Android 平台上 Google Play 分发的核心集成插件，Epic 持续跟进 Google 的 API 变更。

- ✅ 持续更新，最近 6 个月内有活跃提交
- ✅ SDK 版本更新至较新版本（1.15.4 / 2.3.0）
- ✅ JNI 层在 2025 年进行了现代化重构
- ⚠️ 仅限 Android 平台运行时功能，编辑器模块提供构建集成
- ⚠️ 需要 Google Play Services 环境，模拟器无法完整测试

**推荐使用**：如果你的目标平台包含 Android 且需要控制包体大小，这是标准方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GooglePAD)
- [Google Play Asset Delivery 官方文档](https://developer.android.com/guide/playcore/asset-delivery)
- [运行时模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GooglePAD/Source/GooglePAD)
- [编辑器模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GooglePAD/Source/GooglePADEditor)