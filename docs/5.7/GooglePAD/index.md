# GooglePAD

> Google Play Asset Delivery for Android.

| 属性 | 值 |
|---|---|
| 分类 | Android |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | GooglePAD (Runtime), GooglePADEditor (Editor) |
| 创建时间 | 2020-04-21 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GooglePAD) | |

## 用途

GooglePAD plugin 封装了 Google Play Asset Delivery (PAD) API，允许 Android 应用将大型资产包（Asset Pack）从 Google Play Store 按需下载，而不是全部打包进初始 APK。

PAD 解决的核心问题是：Android 应用的 APK 大小受 Google Play 限制（初始安装包上限 150MB）。通过 PAD，游戏可以将关卡、高清纹理、音视频等资产拆分为独立的 Asset Pack，用户安装基础包后在游戏内按需下载，大幅降低首次安装体积。

Plugin 内部使用 Google 的 `play-core-native-sdk`，通过 JNI 与 Android 原生 AssetPackManager 交互，向上层暴露蓝图可用的静态函数。

## 使用场景

- 你的 Android 游戏总资产超过 150MB，需要分包下载 → 用 GooglePAD
- 你有可选的高清材质包/语言包，想让用户按需下载 → 用 GooglePAD
- 你需要在游戏内显示下载进度并处理网络状态 → 用 GooglePAD

## 蓝图用法

所有节点都属于 `GooglePAD` 分类，通过 `UGooglePADFunctionLibrary` 的静态函数暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Request Info` | 查询一组 Asset Pack 的信息 | `UGooglePADFunctionLibrary` |
| `Request Download` | 请求下载一组 Asset Pack | `UGooglePADFunctionLibrary` |
| `Cancel Download` | 取消正在下载的 Asset Pack | `UGooglePADFunctionLibrary` |
| `Get Download State` | 获取某个 Asset Pack 的下载状态句柄（int32） | `UGooglePADFunctionLibrary` |
| `Release Download State` | 释放下载状态句柄资源 | `UGooglePADFunctionLibrary` |
| `Get Download Status` | 从下载状态句柄获取当前状态枚举 | `UGooglePADFunctionLibrary` |
| `Get Bytes Downloaded` | 获取已下载字节数 | `UGooglePADFunctionLibrary` |
| `Get Total Bytes To Download` | 获取总下载字节数 | `UGooglePADFunctionLibrary` |
| `Request Removal` | 请求移除已下载的 Asset Pack | `UGooglePADFunctionLibrary` |
| `Get AssetPack Location` | 获取 Asset Pack 的存储位置句柄 | `UGooglePADFunctionLibrary` |
| `Release AssetPack Location` | 释放存储位置句柄资源 | `UGooglePADFunctionLibrary` |
| `Get Storage Method` | 获取存储方式（文件 / APK） | `UGooglePADFunctionLibrary` |
| `Get Assets Path` | 获取资产文件路径 | `UGooglePADFunctionLibrary` |
| `Show Confirmation dialog` | 显示确认对话框（Wi-Fi / 流量下载） | `UGooglePADFunctionLibrary` |

### 使用示例（蓝图描述）

**下载 Asset Pack 并查询进度：**

1. 调用 `Request Info`，传入 Asset Pack 名称数组（如 `["level_2", "hd_textures"]`）
2. 调用 `Request Download`，传入相同数组
3. 用 `Get Download State` 获取某个 Pack 的 State handle（int32）
4. 用 `Get Download Status` 检查状态，轮询直到返回 `AssetPack_DOWNLOAD_COMPLETED`
5. 用 `Get Bytes Downloaded` / `Get Total Bytes To Download` 计算进度百分比
6. 下载完成后调用 `Get AssetPack Location` → `Get Storage Method` 和 `Get Assets Path` 获取文件路径
7. 使用完毕后调用 `Release Download State` 和 `Release AssetPack Location` 释放资源

## C++ 用法

### 头文件引入

```cpp
#include "GooglePADFunctionLibrary.h"
```

### 基本用法

```cpp
// 查询 Asset Pack 信息
TArray<FString> Packs = { TEXT("level_2"), TEXT("hd_textures") };
EGooglePADErrorCode Error = UGooglePADFunctionLibrary::RequestInfo(Packs);

if (Error == EGooglePADErrorCode::AssetPack_NO_ERROR)
{
    // 请求下载
    UGooglePADFunctionLibrary::RequestDownload(Packs);
}
```

### 进阶用法

```cpp
// 获取下载状态并轮询进度
int32 State = 0;
EGooglePADErrorCode Error = UGooglePADFunctionLibrary::GetDownloadState(TEXT("level_2"), State);

if (Error == EGooglePADErrorCode::AssetPack_NO_ERROR && State != 0)
{
    EGooglePADDownloadStatus Status = UGooglePADFunctionLibrary::GetDownloadStatus(State);
    
    if (Status == EGooglePADDownloadStatus::AssetPack_DOWNLOAD_COMPLETED)
    {
        // 获取资产路径
        int32 Location = 0;
        UGooglePADFunctionLibrary::GetAssetPackLocation(TEXT("level_2"), Location);
        
        if (Location != 0)
        {
            EGooglePADStorageMethod Method = UGooglePADFunctionLibrary::GetStorageMethod(Location);
            FString Path = UGooglePADFunctionLibrary::GetAssetsPath(Location);
            
            // 使用完毕释放
            UGooglePADFunctionLibrary::ReleaseAssetPackLocation(Location);
        }
    }
    
    // 获取下载进度
    int32 BytesDownloaded = UGooglePADFunctionLibrary::GetBytesDownloaded(State);
    int32 TotalBytes = UGooglePADFunctionLibrary::GetTotalBytesToDownload(State);
    float Progress = (TotalBytes > 0) ? (float)BytesDownloaded / (float)TotalBytes : 0.0f;
    
    // 用完释放
    UGooglePADFunctionLibrary::ReleaseDownloadState(State);
}
```

## Demo 示例

```cpp
// MyAssetDownloadManager.h
#pragma once

#include "CoreMinimal.h"
#include "GooglePADFunctionLibrary.h"
#include "MyAssetDownloadManager.generated.h"

UCLASS(BlueprintType)
class UMyAssetDownloadManager : public UObject
{
    GENERATED_BODY()

public:
    /** 开始下载指定 Asset Pack */
    UFUNCTION(BlueprintCallable)
    void StartDownload(const FString& PackName);

    /** 轮询下载进度（应在 Tick 中调用） */
    UFUNCTION(BlueprintCallable)
    EGooglePADDownloadStatus PollProgress(const FString& PackName, float& OutProgress);

private:
    TMap<FString, int32> PackStates;
};
```

```cpp
// MyAssetDownloadManager.cpp
#include "MyAssetDownloadManager.h"

void UMyAssetDownloadManager::StartDownload(const FString& PackName)
{
    TArray<FString> Packs = { PackName };
    
    // 先查询信息
    EGooglePADErrorCode Error = UGooglePADFunctionLibrary::RequestInfo(Packs);
    if (Error != EGooglePADErrorCode::AssetPack_NO_ERROR)
    {
        UE_LOG(LogTemp, Error, TEXT("RequestInfo failed for %s: %d"), *PackName, (int32)Error);
        return;
    }

    // 请求下载
    Error = UGooglePADFunctionLibrary::RequestDownload(Packs);
    if (Error != EGooglePADErrorCode::AssetPack_NO_ERROR)
    {
        UE_LOG(LogTemp, Error, TEXT("RequestDownload failed for %s: %d"), *PackName, (int32)Error);
        return;
    }

    // 获取状态句柄
    int32 State = 0;
    UGooglePADFunctionLibrary::GetDownloadState(PackName, State);
    if (State != 0)
    {
        PackStates.Add(PackName, State);
    }
}

EGooglePADDownloadStatus UMyAssetDownloadManager::PollProgress(
    const FString& PackName, float& OutProgress)
{
    OutProgress = 0.0f;
    
    int32* StatePtr = PackStates.Find(PackName);
    if (!StatePtr || *StatePtr == 0)
    {
        return EGooglePADDownloadStatus::AssetPack_UNKNOWN;
    }

    EGooglePADDownloadStatus Status = UGooglePADFunctionLibrary::GetDownloadStatus(*StatePtr);
    
    int32 Total = UGooglePADFunctionLibrary::GetTotalBytesToDownload(*StatePtr);
    if (Total > 0)
    {
        int32 Downloaded = UGooglePADFunctionLibrary::GetBytesDownloaded(*StatePtr);
        OutProgress = (float)Downloaded / (float)Total;
    }

    // 完成后清理
    if (Status == EGooglePADDownloadStatus::AssetPack_DOWNLOAD_COMPLETED ||
        Status == EGooglePADDownloadStatus::AssetPack_DOWNLOAD_FAILED ||
        Status == EGooglePADDownloadStatus::AssetPack_DOWNLOAD_CANCELED)
    {
        UGooglePADFunctionLibrary::ReleaseDownloadState(*StatePtr);
        PackStates.Remove(PackName);
    }

    return Status;
}
```

> **Build.cs 依赖**：使用此功能的模块无需额外依赖，GooglePAD 插件自身已处理所有底层依赖。

## 项目设置

在编辑器的 **Project Settings > Plugins > GooglePAD** 中可以配置：

| 设置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bEnablePlugin` | bool | `false` | 是否启用 GooglePAD（需在 Android 项目设置中开启） |
| `bOnlyDistribution` | bool | `true` | 仅在分发构建（Distribution Build）中启用 |
| `bOnlyShipping` | bool | `false` | 仅在 Shipping 构建中启用 |

> **注意**：`bEnablePlugin` 默认为 `false`，意味着在开发构建（Development）中 PAD 功能默认不生效。这是合理的设计——开发时通常不需要真实下载 Asset Pack。

## 模块依赖

### GooglePAD（Runtime 模块）

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心（公开依赖） |

### GooglePADEditor（Editor 模块）

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心 |
| `CoreUObject` | UObject 系统 |
| `EditorFramework` | 编辑器框架 |
| `UnrealEd` | 编辑器功能（设置面板注册） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-09-23 | `f7062e9` | Update GooglePAD to 1.15.4 / 2.3.0 | 升级 Play Core SDK 到 2.3.0，API 版本 1.15.4 |
| 2025-09-02 | `5a48f72` | Registered JNI functions. Made JNI classes for Java classes. | JNI 层重构，改进 Android 原生调用的稳定性 |
| 2025-06-26 | `a2e7518` | Added UE_INLINE_GENERATED_CPP_BY_NAME | 编译优化，减少编译时间 |

### 维护评价

- **创建时间**：2020-04-21，约 6 年前
- **最近更新**：2025-09-23，半年内有 SDK 版本升级
- **维护状态**：**活跃维护** — 作为 Epic 官方支持的 Android 核心分发功能，持续跟进 Google SDK 更新
- **已知限制**：
  - 仅在 Android 平台实际生效（Win64/Mac/Linux 编译通过但功能为空实现）
  - `ShowCellularDataConfirmation` 已废弃，内部重定向到 `ShowConfirmationDialog`
  - Download State 和 Location 句柄是 int32，需要手动 Release 避免泄漏
- **推荐使用**：✅ 如果你的游戏发布到 Google Play 且 APK 超过 150MB，这是必用的插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GooglePAD)
- [Google Play Asset Delivery 官方文档](https://developer.android.com/guide/playcore/asset-delivery)
- [play-core-native-sdk 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/GooglePAD/Source/ThirdParty/play-core-native-sdk/include)
