# Google Play Asset Delivery

> Google Play Asset Delivery for Android.

| 属性 | 值 |
|---|---|
| 中文名 | Play 资源分发 |
| 分类 | Android |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GooglePAD` (Runtime), `GooglePADEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-04-21 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GooglePAD) | |

## 用途

该插件封装了 Google Play Asset Delivery (PAD) API，为 Android 平台上的游戏提供动态资源包下载与管理功能。其核心解决的问题是：游戏安装包体积过大，用户需要一次性下载整个应用。通过 PAD，游戏可以将非核心资源（如额外关卡、高清素材包）拆分为独立的“资源包”，在用户安装后按需下载，显著减少初始下载大小，优化用户体验。

插件提供了完整的蓝图和 C++ 接口，用于查询资源包信息、启动下载、监控下载进度、处理网络切换（如蜂窝数据确认）以及管理已下载资源包的存储路径。

## 使用场景

- **大型 Android 游戏**：需要将游戏分割为核心安装包和多个可选的资源包（例如语言包、高清材质、扩展关卡）。
- **按需内容分发**：游戏内的 DLC 或扩展内容可以通过 PAD 在运行时下载，无需重新提交应用更新。
- **优化网络体验**：支持仅在 Wi-Fi 环境下下载大型资源包，并在用户尝试使用蜂窝数据下载时显示确认对话框。

## 蓝图用法

蓝图节点集中在 `GooglePAD` 类别下，主要操作流程为：请求信息 -> 请求下载 -> 监控状态 -> 获取路径。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Request Info` | 向 Play 商店查询指定资源包的最新信息（大小、状态等）。 | `UGooglePADFunctionLibrary` |
| `Request Download` | 启动一个或多个资源包的下载。 | `UGooglePADFunctionLibrary` |
| `Get Download State` | 获取指定资源包的下载状态句柄（整数）。此句柄用于后续查询。 | `UGooglePADFunctionLibrary` |
| `Release Download State` | 释放下载状态句柄，避免内存泄漏。 | `UGooglePADFunctionLibrary` |
| `Get Download Status` | 根据状态句柄查询具体的下载阶段（如下载中、已完成、等待Wi-Fi）。 | `UGooglePADFunctionLibrary` |
| `Get Bytes Downloaded` / `Get Total Bytes To Download` | 获取下载进度，可用于显示进度条。 | `UGooglePADFunctionLibrary` |
| `Get AssetPack Location` | 获取已下载资源包的存储路径句柄。 | `UGooglePADFunctionLibrary` |
| `Release AssetPack Location` | 释放路径句柄。 | `UGooglePADFunctionLibrary` |
| `Get Assets Path` | 根据路径句柄获取资源包在设备上的实际路径字符串。 | `UGooglePADFunctionLibrary` |
| `Show Confirmation Dialog` | 弹出一个对话框，让用户确认是否开始下载所有需要确认的资源包（例如等待Wi-Fi的）。 | `UGooglePADFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **检查并下载资源包**：
    - 使用 `Make Array` 节点创建一个包含资源包名称（如 `"level2_pack"`）的 `TArray<FString>`。
    - 将其连接到 `Request Info` 节点，查询资源包信息。
    - 在后续逻辑中，检查 `Get Download Status` 返回的状态。如果为 `AssetPack_NOT_INSTALLED` 或 `AssetPack_DOWNLOAD_FAILED`，则调用 `Request Download` 启动下载。
    - 在 Tick 事件中，周期性调用 `Get Download Status` 和 `Get Bytes Downloaded` 来更新 UI 进度条。

2.  **获取已下载资源路径**：
    - 当 `Get Download Status` 返回 `AssetPack_DOWNLOAD_COMPLETED` 后，调用 `Get AssetPack Location` 获取位置句柄。
    - 立即调用 `Get Assets Path` 获取路径字符串。
    - 使用该路径加载资源（例如使用 `LoadObject` 或 `OpenLevel`）。
    - 最后，记得调用 `Release AssetPack Location` 和 `Release Download State`。

## C++ 用法

该插件的核心是一个静态函数库 `UGooglePADFunctionLibrary`，所有方法均为静态，可直接在 C++ 中调用。

### 头文件引入

```cpp
#include "GooglePADFunctionLibrary.h"
```

### 基本用法

以下代码片段展示了如何查询资源包信息并处理结果（基于 `UGooglePADFunctionLibrary` 接口推断）。

```cpp
// 假设在游戏某个管理器类中
#include "GooglePADFunctionLibrary.h"

// 查询资源包信息
TArray<FString> AssetPacksToQuery;
AssetPacksToQuery.Add(TEXT("optional_content_pack_1"));
AssetPacksToQuery.Add(TEXT("hd_textures"));

EGooglePADErrorCode ErrorCode = UGooglePADFunctionLibrary::RequestInfo(AssetPacksToQuery);
if (ErrorCode != EGooglePADErrorCode::AssetPack_NO_ERROR)
{
    UE_LOG(LogYourGame, Error, TEXT("GooglePAD RequestInfo failed with error: %d"), static_cast<int32>(ErrorCode));
    return;
}

// ... 在后续的轮询或回调中，检查状态
int32 DownloadStateHandle = 0;
ErrorCode = UGooglePADFunctionLibrary::GetDownloadState(TEXT("optional_content_pack_1"), DownloadStateHandle);
if (ErrorCode == EGooglePADErrorCode::AssetPack_NO_ERROR && DownloadStateHandle != 0)
{
    EGooglePADDownloadStatus Status = UGooglePADFunctionLibrary::GetDownloadStatus(DownloadStateHandle);
    int32 BytesDownloaded = UGooglePADFunctionLibrary::GetBytesDownloaded(DownloadStateHandle);
    int32 TotalBytes = UGooglePADFunctionLibrary::GetTotalBytesToDownload(DownloadStateHandle);
    
    UE_LOG(LogYourGame, Log, TEXT("Pack status: %d, Progress: %d/%d"), 
           static_cast<int32>(Status), BytesDownloaded, TotalBytes);
    
    // 重要：使用完毕后释放句柄
    UGooglePADFunctionLibrary::ReleaseDownloadState(DownloadStateHandle);
}
```

### 进阶用法

结合蜂窝数据确认和路径获取的完整流程。

```cpp
void UYourAssetManager::StartDownloadIfNeeded()
{
    // 1. 尝试启动下载
    TArray<FString> Packs = {TEXT("big_expansion")};
    EGooglePADErrorCode Error = UGooglePADFunctionLibrary::RequestDownload(Packs);
    
    if (Error == EGooglePADErrorCode::AssetPack_NETWORK_ERROR)
    {
        // 网络错误，可能需要提示用户
        UE_LOG(LogYourGame, Warning, TEXT("Network error during download request."));
        return;
    }
    
    // 2. 检查是否需要用户确认（例如等待Wi-Fi）
    EGooglePADConfirmationDialogStatus DialogStatus;
    UGooglePADFunctionLibrary::GetShowConfirmationDialogStatus(DialogStatus);
    if (DialogStatus == EGooglePADConfirmationDialogStatus::AssetPack_CONFIRMATION_DIALOG_PENDING)
    {
        // 弹出确认对话框
        UGooglePADFunctionLibrary::ShowConfirmationDialog();
    }
}

void UYourAssetManager::OnDownloadComplete(const FString& PackName)
{
    // 3. 获取资源路径
    int32 LocationHandle = 0;
    if (UGooglePADFunctionLibrary::GetAssetPackLocation(PackName, LocationHandle) == EGooglePADErrorCode::AssetPack_NO_ERROR)
    {
        FString AssetPath = UGooglePADFunctionLibrary::GetAssetsPath(LocationHandle);
        
        // 4. 使用路径，例如加载一个关卡
        UGameplayStatics::OpenLevel(this, FName(*AssetPath));
        
        // 5. 释放句柄
        UGooglePADFunctionLibrary::ReleaseAssetPackLocation(LocationHandle);
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何查询并打印资源包状态。

```cpp
// .h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GooglePADFunctionLibrary.h"
#include "GooglePADTestActor.generated.h"

UCLASS()
class AGooglePADTestActor : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    TArray<FString> PackNames = {"demo_pack"};
    int32 CurrentStateHandle = 0;
    bool bInfoRequested = false;
    bool bDownloadStarted = false;
};
```

```cpp
// .cpp
#include "GooglePADTestActor.h"
#include "GooglePAD.h" // 包含日志分类

void AGooglePADTestActor::BeginPlay()
{
    Super::BeginPlay();
    UE_LOG(LogGooglePAD, Log, TEXT("Querying info for packs..."));
    UGooglePADFunctionLibrary::RequestInfo(PackNames);
    bInfoRequested = true;
}

void AGooglePADTestActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!bInfoRequested) return;

    // 获取下载状态
    EGooglePADErrorCode Error = UGooglePADFunctionLibrary::GetDownloadState(PackNames[0], CurrentStateHandle);
    if (Error != EGooglePADErrorCode::AssetPack_NO_ERROR)
    {
        UE_LOG(LogGooglePAD, Warning, TEXT("GetDownloadState failed: %d"), static_cast<int32>(Error));
        return;
    }

    EGooglePADDownloadStatus Status = UGooglePADFunctionLibrary::GetDownloadStatus(CurrentStateHandle);
    UE_LOG(LogGooglePAD, Log, TEXT("Status for '%s': %d"), *PackNames[0], static_cast<int32>(Status));

    // 根据状态决定下一步
    if (Status == EGooglePADDownloadStatus::AssetPack_NOT_INSTALLED && !bDownloadStarted)
    {
        UE_LOG(LogGooglePAD, Log, TEXT("Starting download..."));
        UGooglePADFunctionLibrary::RequestDownload(PackNames);
        bDownloadStarted = true;
    }
    else if (Status == EGooglePADDownloadStatus::AssetPack_DOWNLOAD_COMPLETED)
    {
        UE_LOG(LogGooglePAD, Log, TEXT("Download complete! Getting path..."));
        int32 LocationHandle = 0;
        if (UGooglePADFunctionLibrary::GetAssetPackLocation(PackNames[0], LocationHandle) == EGooglePADErrorCode::AssetPack_NO_ERROR)
        {
            FString Path = UGooglePADFunctionLibrary::GetAssetsPath(LocationHandle);
            UE_LOG(LogGooglePAD, Log, TEXT("Asset path: %s"), *Path);
            UGooglePADFunctionLibrary::ReleaseAssetPackLocation(LocationHandle);
        }
        UGooglePADFunctionLibrary::ReleaseDownloadState(CurrentStateHandle);
        CurrentStateHandle = 0; // 停止 Tick
    }
    else
    {
        // 打印进度
        int32 Downloaded = UGooglePADFunctionLibrary::GetBytesDownloaded(CurrentStateHandle);
        int32 Total = UGooglePADFunctionLibrary::GetTotalBytesToDownload(CurrentStateHandle);
        UE_LOG(LogGooglePAD, Log, TEXT("Progress: %d / %d bytes"), Downloaded, Total);
    }
}
```

## 模块依赖

该插件为 Android 平台提供了特定功能，因此会依赖 Android 平台相关的底层模块。使用者无需在自己的 Build.cs 中直接依赖这些模块，只需链接 `GooglePAD` 模块即可。

| 模块 | 用途 |
|---|---|
| `Android` | 提供 Android 平台基础支持和 JNI 调用环境。 |
| `AndroidPermission` | 管理 Android 运行时权限，可能用于检查网络等权限。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新格式 UE_LOGF，属于引擎代码维护性更新。 |
| 2025-09-17 | `2e280ccd` | Update GooglePAD to 1.15.4 / 2.3.0 | 更新了底层 Google Play Asset Delivery SDK 到较新版本，可能包含新功能或修复。 |
| 2025-09-02 | `7d7255e0` | Registered JNI functions. Made JNI classes for Java classes. Added thread_local Ue::Jni::Env global. | 重构了 JNI 交互层，增强了类型安全和线程安全性，是重要的内部架构改进。 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie... | 标准化代码生成，属于代码规范维护。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i... | 为插件的导出符号添加了正确的 DLL 导出宏，修复了跨模块调用的潜在问题。 |

### 维护评价

该插件处于**活跃维护**状态。尽管自2020年创建以来已有6年历史，但最近一年内（2025年）有多次实质性更新，包括底层SDK升级和重要的内部架构重构（JNI改进），表明 Epic 和 Google 仍在持续投入。插件稳定，是 UE 在 Android 平台进行动态资源分发的官方推荐方案。

**推荐使用**：对于需要发布到 Google Play 且游戏体积较大的 Android 项目，强烈推荐启用此插件。它提供了经过验证的、集成度高的解决方案，避免了开发者自行处理复杂的资源分发逻辑。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GooglePAD)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/google-play-asset-delivery-plugin-for-unreal-engine/) （注：DocsURL字段为空，此为UE官方文档常见入口）