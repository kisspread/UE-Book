# Mobile Patching Utilities

> Blueprint exposed functionality for downloading and patching content on mobile platforms

| 属性 | 值 |
|---|---|
| 中文名 | 移动内容更新 |
| 分类 | Mobile |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MobilePatchingUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-10-08 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MobilePatchingUtils) | |

## 用途

该插件为移动端游戏提供了一套蓝图可调用的接口，用于实现游戏内容的按需下载、增量更新（Patching）以及挂载。它主要解决了移动端游戏安装包过大、需要分包发布或后续更新的问题，允许玩家只下载他们需要的或更新的游戏内容，从而节省流量和设备存储空间。其核心是基于 UE 的构建补丁服务（`BuildPatchServices`）封装的蓝图友好的操作层。

## 使用场景

- **移动游戏内容分包**：将非核心游戏内容（如可选的高清资源包、额外关卡、故事章节）从主包中分离，玩家可以在游戏内根据需求选择性下载。
- **游戏版本增量更新**：游戏发布后，通过下载增量补丁文件来更新游戏内容，无需玩家重新下载完整安装包。
- **CDN内容管理**：通过指定清单文件（Manifest）和云存储URL，从自定义的CDN服务器下载和更新游戏资源，实现灵活的内容管理。
- **网络状态检测**：在下载大量内容前，检查设备是否连接WiFi，以便提示用户避免使用移动数据。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Installed Content` | 获取指定安装目录下已安装内容的句柄。若内容已安装，返回一个可用于挂载的对象。 | `UMobilePatchingLibrary` |
| `Request Content` | 通过指定的清单文件URL和云存储URL，请求下载并安装远程内容。成功时返回代表待下载内容的对象。 | `UMobilePatchingLibrary` |
| `Has Active WiFi Connection` | 检测当前设备是否连接到WiFi网络。 | `UMobilePatchingLibrary` |
| `Get Download Size` | 获取待下载内容的总大小（MB）。 | `UMobilePendingContent` |
| `Get Install Progress` | 获取当前安装的进度（0-1之间），小于0表示进度未知。 | `UMobilePendingContent` |
| `Start Install` | 开始下载并安装远程内容，并监听成功/失败回调。 | `UMobilePendingContent` |
| `Mount` | 将已安装的内容Pak文件挂载到游戏文件系统中，使其生效。 | `UMobileInstalledContent` |

### 使用示例（蓝图描述）

1.  **检查并加载已下载内容**：
    - 使用 `Get Installed Content` 节点，传入内容安装的相对目录（例如 `“MyGame/DLC1”`）。
    - 判断返回的对象是否有效。如果有效，可以直接调用其 `Mount` 函数将内容挂载到游戏。

2.  **下载并安装新内容**：
    - 首先，调用 `Request Content` 节点，传入清单文件URL（`RemoteManifestURL`）、云存储URL（`CloudURL`）和本地安装目录（`InstallDirectory`）。
    - 连接成功回调 `On Succeeded`。在回调中，你将获得一个 `Mobile Pending Content` 对象。
    - 调用该对象的 `Get Download Size` 节点向用户显示所需流量。
    - 调用 `Start Install` 节点开始实际下载和安装，并连接 `On Succeeded` 和 `On Failed` 回调。
    - 在 `Start Install` 的进行中，可以轮询 `Get Install Progress` 和 `Get Download Speed` 来更新UI显示下载进度和速度。

3.  **网络检查**：
    - 在发起大体积下载前，使用 `Has Active WiFi Connection` 节点检查网络。若返回 `False`，可弹出UI提示用户当前为移动数据网络，询问是否继续。

## C++ 用法

### 头文件引入

```cpp
#include "MobilePatchingLibrary.h"
```

### 基本用法

```cpp
// 检查指定目录的已安装内容并挂载
FString ContentDirectory = TEXT("MyGame/AwesomeContent");
UMobileInstalledContent* InstalledContent = UMobilePatchingLibrary::GetInstalledContent(ContentDirectory);
if (InstalledContent)
{
    // 内容已存在，直接挂载，PakOrder为优先级
    InstalledContent->Mount(1, TEXT(""));
    UE_LOG(LogTemp, Log, TEXT("Content mounted from: %s"), *ContentDirectory);
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("No installed content found at: %s"), *ContentDirectory);
}
```

### 进阶用法

```cpp
// 定义回调委托
FOnRequestContentSucceeded OnManifestReady;
FOnRequestContentFailed OnManifestFailed;

// 绑定成功回调
OnManifestReady.BindDynamic(this, &UMyGameClass::OnRequestContentSucceeded);
// 绑定失败回调
OnManifestFailed.BindDynamic(this, &UMyGameClass::OnRequestContentFailed);

// 请求下载清单
FString ManifestURL = TEXT("http://my-cdn.com/gamecontent.manifest");
FString CloudDataURL = TEXT("http://my-cdn.com/gamecontent/chunks");
FString LocalInstallDir = TEXT("MyGame/UpdatedContent");

UMobilePatchingLibrary::RequestContent(
    ManifestURL,
    CloudDataURL,
    LocalInstallDir,
    OnManifestReady,
    OnManifestFailed
);

// 成功回调处理函数示例
void UMyGameClass::OnRequestContentSucceeded(UMobilePendingContent* PendingContent)
{
    if (PendingContent)
    {
        float DownloadSize = PendingContent->GetDownloadSize();
        UE_LOG(LogTemp, Log, TEXT("Content ready. Download size: %.2f MB"), DownloadSize);
        
        // 在此处可以保存PendingContent指针，以便后续调用StartInstall
        // 或者直接开始安装，并绑定安装回调
        FOnContentInstallSucceeded OnInstallSucceeded;
        FOnContentInstallFailed OnInstallFailed;
        OnInstallSucceeded.BindDynamic(this, &UMyGameClass::OnInstallSucceeded);
        OnInstallFailed.BindDynamic(this, &UMyGameClass::OnInstallFailed);
        PendingContent->StartInstall(OnInstallSucceeded, OnInstallFailed);
    }
}

// 失败回调处理函数示例
void UMyGameClass::OnRequestContentFailed(FText ErrorText, int32 ErrorCode)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to request content: %s (%d)"), *ErrorText.ToString(), ErrorCode);
}

// 安装成功后挂载内容
void UMyGameClass::OnInstallSucceeded()
{
    // 安装完成后，通常需要重新调用GetInstalledContent来获取已安装内容句柄，再进行挂载
    // 或者可以直接在安装前保存的UMobilePendingContent对象上调用Mount（因为它继承自UMobileInstalledContent）
}
```

## Demo 示例

**MyGamePatchingManager.h**
```cpp
// Fill out your copyright notice in the Description page of Project Settings.
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MobilePatchingLibrary.h"
#include "MyGamePatchingManager.generated.h"

UCLASS(Blueprintable)
class UMyGamePatchingManager : public UObject
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = "Game Patching")
    void CheckAndDownloadDLC(const FString& ManifestURL, const FString& CloudURL, const FString& DLCName);

private:
    UPROPERTY()
    UMobilePendingContent* CurrentPendingContent;

    UFUNCTION()
    void OnRequestContentSuccess(UMobilePendingContent* PendingContent);
    UFUNCTION()
    void OnRequestContentFailed(FText ErrorText, int32 ErrorCode);
    UFUNCTION()
    void OnInstallSuccess();
    UFUNCTION()
    void OnInstallFailed(FText ErrorText, int32 ErrorCode);
};
```

**MyGamePatchingManager.cpp**
```cpp
// Fill out your copyright notice in the Description page of Project Settings.
#include "MyGamePatchingManager.h"
#include "MobilePatchingLibrary.h"

void UMyGamePatchingManager::CheckAndDownloadDLC(const FString& ManifestURL, const FString& CloudURL, const FString& DLCName)
{
    // 先检查本地是否已存在
    FString LocalDir = FString::Printf(TEXT("DLC/%s"), *DLCName);
    UMobileInstalledContent* ExistingContent = UMobilePatchingLibrary::GetInstalledContent(LocalDir);
    if (ExistingContent)
    {
        UE_LOG(LogTemp, Log, TEXT("DLC '%s' already installed, mounting."), *DLCName);
        ExistingContent->Mount(100, TEXT(""));
        return;
    }

    // 检查网络并开始下载
    if (!UMobilePatchingLibrary::HasActiveWiFiConnection())
    {
        UE_LOG(LogTemp, Warning, TEXT("Not on WiFi. Download may incur data charges."));
        // 实际项目中这里应弹出UI提示
    }

    // 请求内容
    FOnRequestContentSucceeded SuccessDelegate;
    FOnRequestContentFailed FailedDelegate;
    SuccessDelegate.BindDynamic(this, &UMyGamePatchingManager::OnRequestContentSuccess);
    FailedDelegate.BindDynamic(this, &UMyGamePatchingManager::OnRequestContentFailed);

    UMobilePatchingLibrary::RequestContent(ManifestURL, CloudURL, LocalDir, SuccessDelegate, FailedDelegate);
}

void UMyGamePatchingManager::OnRequestContentSuccess(UMobilePendingContent* PendingContent)
{
    CurrentPendingContent = PendingContent;
    if (CurrentPendingContent)
    {
        UE_LOG(LogTemp, Log, TEXT("Manifest downloaded. Total size: %.2f MB"), CurrentPendingContent->GetDownloadSize());
        
        // 开始安装
        FOnContentInstallSucceeded InstallSuccessDelegate;
        FOnContentInstallFailed InstallFailedDelegate;
        InstallSuccessDelegate.BindDynamic(this, &UMyGamePatchingManager::OnInstallSuccess);
        InstallFailedDelegate.BindDynamic(this, &UMyGamePatchingManager::OnInstallFailed);
        CurrentPendingContent->StartInstall(InstallSuccessDelegate, InstallFailedDelegate);
    }
}

void UMyGamePatchingManager::OnRequestContentFailed(FText ErrorText, int32 ErrorCode)
{
    UE_LOG(LogTemp, Error, TEXT("Content request failed: %s"), *ErrorText.ToString());
    CurrentPendingContent = nullptr;
}

void UMyGamePatchingManager::OnInstallSuccess()
{
    UE_LOG(LogTemp, Log, TEXT("DLC installed successfully."));
    if (CurrentPendingContent)
    {
        // 安装成功后，PendingContent对象也持有已安装信息，可以直接挂载
        CurrentPendingContent->Mount(100, TEXT(""));
    }
    CurrentPendingContent = nullptr;
}

void UMyGamePatchingManager::OnInstallFailed(FText ErrorText, int32 ErrorCode)
{
    UE_LOG(LogTemp, Error, TEXT("DLC installation failed: %s"), *ErrorText.ToString());
    CurrentPendingContent = nullptr;
}
```

## 模块依赖

此插件无特殊依赖（仅标准 Core/Engine/Slate 等）。但其功能**强依赖于引擎内部的 `BuildPatchServices` 模块**，该模块在插件的 `Build.cs` 中被隐式依赖。如果你在项目模块中使用此插件的C++功能，无需显式添加额外依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的UE_LOGF格式。 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied 172 of 185 changes) | 添加了内联生成代码的宏，优化编译。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 调整符号的DLL导出/导入属性，以适配构建系统。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 对Engine/Plugins目录下的多个插件进行了批量维护性提交。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将插件的内部链接更新为安全协议（HTTPS）。 |

### 维护评价

该插件创建于 **2016年**，历史悠久。从最近的提交记录来看，过去几年的更新**全部是引擎维护性、编译优化和代码规范方面的调整**，没有增加新功能或修复特定业务bug。最后一次实质性功能更新（添加WiFi检测等）可能发生在其创建初期（2016年）。

- **活跃度**：**维护不活跃**。最近一次提交是2026年，但属于自动化维护，无新功能或Bug修复。
- **推荐度**：该插件功能稳定且边界清晰，适用于传统的移动端内容分包场景。然而，它依赖于较老的 `BuildPatchServices` 框架，且长期没有功能更新。对于新项目，建议评估最新的、可能更符合当前平台和引擎版本的官方或社区解决方案。如果项目已使用该插件且功能满足需求，可以继续使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MobilePatchingUtils)