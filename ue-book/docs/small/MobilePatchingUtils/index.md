# Mobile Patching Utilities

> Blueprint exposed functionality for downloading and patching content on mobile platforms

| 属性 | 值 |
|---|---|
| 分类 | Mobile |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | MobilePatchingUtils (Runtime) |
| 创建时间 | 2016-10-07 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MobilePatchingUtils) | |

## 用途

MobilePatchingUtils 是 UE5 移动平台 **热更新/内容补丁** 的蓝图封装层。它把底层的 `BuildPatchServices` 模块（负责 chunk 级差分下载、manifest 管理、pak 挂载）包装成蓝图友好的异步 API，让开发者无需编写 C++ 就能实现：

1. **检查已安装的补丁内容** — 读取本地 manifest，获取已安装内容大小
2. **请求远程补丁** — 从服务器下载 manifest，对比本地版本计算差分下载量
3. **下载并安装** — 异步下载 chunk 数据，安装到本地目录
4. **挂载 pak 文件** — 安装完成后将 pak 挂载到引擎文件系统

本质上它是 `BuildPatchServices`（Epic 用于 Epic Games Launcher 自身更新的技术）面向移动端的简化接口。

## 使用场景

- 你的手游需要把基础包体做小，后续按需下载关卡/资源包 → 用此 plugin 实现"边玩边下"
- 你需要频繁更新游戏资源（如每周新活动素材），但不想让玩家每次重新下载完整包 → 用差分补丁只下载变化的 chunk
- 你需要在蓝图中实现补丁下载进度条和 WiFi 检测 → 此 plugin 的所有节点都暴露给蓝图

## 蓝图用法

所有功能通过 `UMobilePatchingLibrary`（静态函数库）和两个核心对象类暴露给蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RequestContent` | 异步下载远程 manifest，成功后返回 `UMobilePendingContent` 对象 | `UMobilePatchingLibrary` |
| `GetInstalledContent` | 检查指定目录是否有已安装的补丁内容，返回 `UMobileInstalledContent`（或 null） | `UMobilePatchingLibrary` |
| `HasActiveWiFiConnection` | 检测当前设备是否有 WiFi 连接 | `UMobilePatchingLibrary` |
| `GetActiveDeviceProfileName` | 获取当前设备的 Device Profile 名称 | `UMobilePatchingLibrary` |
| `GetSupportedPlatformNames` | 获取当前设备支持的平台名列表（如 Android_ETC2, Android_ASTC） | `UMobilePatchingLibrary` |

### 安装内容查询节点（UMobileInstalledContent）

| 节点 | 说明 |
|---|---|
| `GetInstalledContentSize` | 已安装内容大小（MB） |
| `GetDiskFreeSpace` | 安装目录所在磁盘的剩余空间（MB） |
| `Mount` | 挂载已安装的 pak 文件，可指定 PakOrder 和 MountPoint |

### 待安装内容节点（UMobilePendingContent，继承 UMobileInstalledContent）

| 节点 | 说明 |
|---|---|
| `GetDownloadSize` | 需要下载的差分大小（MB），如有本地版本则为增量大小 |
| `GetRequiredDiskSpace` | 远程版本完整构建大小（MB） |
| `StartInstall` | 开始下载并安装，通过回调返回结果 |
| `GetInstallProgress` | 安装进度（0~1），小于 0 表示未知 |
| `GetTotalDownloadedSize` | 已下载大小（MB），安装过程中有效 |
| `GetDownloadSpeed` | 当前下载速度（MB/s），安装过程中有效 |

### 使用示例（蓝图描述）

**典型补丁下载流程：**

1. **检测 WiFi** — 调用 `HasActiveWiFiConnection`，如果无 WiFi 则提示用户
2. **请求内容** — 调用 `RequestContent`，传入 Manifest URL、Cloud URL、安装目录
3. **成功回调** — `OnSucceeded` 触发后获得 `UMobilePendingContent` 引用
4. **展示信息** — 调用 `GetDownloadSize` 和 `GetRequiredDiskSpace` 显示给用户
5. **开始安装** — 调用 `StartInstall`，绑定成功/失败回调
6. **轮询进度** — 每帧调用 `GetInstallProgress` 更新进度条
7. **挂载内容** — 安装成功后调用 `Mount` 将 pak 挂载到引擎

**检查已安装内容：**

1. 调用 `GetInstalledContent`，传入安装目录
2. 如果返回有效对象，说明已有补丁 → 调用 `Mount` 挂载
3. 如果返回 null，说明没有已安装补丁 → 走下载流程

## C++ 用法

此 plugin 设计上主要面向蓝图，C++ 用法与蓝图 API 一一对应。

### 头文件引入

```cpp
#include "MobilePatchingLibrary.h"
```

### 基本用法

```cpp
// 检查是否已安装补丁内容
UMobileInstalledContent* InstalledContent = UMobilePatchingLibrary::GetInstalledContent(TEXT("MyContent/Patch"));
if (InstalledContent)
{
    UE_LOG(LogTemp, Log, TEXT("已安装内容大小: %.2f MB"), InstalledContent->GetInstalledContentSize());
    UE_LOG(LogTemp, Log, TEXT("磁盘剩余: %.2f MB"), InstalledContent->GetDiskFreeSpace());
    
    // 挂载已安装的 pak
    InstalledContent->Mount(1, TEXT(""));
}

// 请求远程补丁
UMobilePatchingLibrary::RequestContent(
    TEXT("http://my-server.com/patch.manifest"),   // Manifest URL
    TEXT("http://my-server.com/patch/clouddir"),    // Cloud URL
    TEXT("MyContent/Patch"),                         // 安装目录
    FOnRequestContentSucceeded::CreateLambda([](UMobilePendingContent* PendingContent)
    {
        UE_LOG(LogTemp, Log, TEXT("下载大小: %.2f MB"), PendingContent->GetDownloadSize());
        UE_LOG(LogTemp, Log, TEXT("需要磁盘: %.2f MB"), PendingContent->GetRequiredDiskSpace());
        
        // 开始安装
        PendingContent->StartInstall(
            FOnContentInstallSucceeded::CreateLambda([]()
            {
                UE_LOG(LogTemp, Log, TEXT("安装成功!"));
            }),
            FOnContentInstallFailed::CreateLambda([](FText ErrorText, int32 ErrorCode)
            {
                UE_LOG(LogTemp, Error, TEXT("安装失败: %s (Code: %d)"), *ErrorText.ToString(), ErrorCode);
            })
        );
    }),
    FOnRequestContentFailed::CreateLambda([](FText ErrorText, int32 ErrorCode)
    {
        UE_LOG(LogTemp, Error, TEXT("请求失败: %s (Code: %d)"), *ErrorText.ToString(), ErrorCode);
    })
);
```

> 来源：`Engine/Plugins/Runtime/MobilePatchingUtils/Source/MobilePatchingUtils/Private/MobilePatchingLibrary.h`

### 进阶用法

**WiFi 检测 + 设备平台判断：**

```cpp
// 下载前检查 WiFi
if (!UMobilePatchingLibrary::HasActiveWiFiConnection())
{
    UE_LOG(LogTemp, Warning, TEXT("无 WiFi 连接，建议在 WiFi 环境下下载"));
}

// 获取设备支持的纹理格式，按格式选择不同的补丁
TArray<FString> Platforms = UMobilePatchingLibrary::GetSupportedPlatformNames();
for (const FString& Platform : Platforms)
{
    UE_LOG(LogTemp, Log, TEXT("支持平台: %s"), *Platform);
}

// 获取当前 Device Profile
FString ProfileName = UMobilePatchingLibrary::GetActiveDeviceProfileName();
```

**增量更新（差分下载）：**

当 `UMobilePendingContent` 检测到本地已有旧版 manifest 时，`GetDownloadSize()` 会自动返回差分大小（通过 `GetDeltaDownloadSize`），而非全量下载。这意味着：
- 首次安装：下载大小 = 完整包大小
- 更新已有内容：下载大小 = 仅变化 chunk 的大小

此行为自动处理，无需开发者额外编码。

## Demo 示例

### Build.cs 依赖配置

```csharp
using UnrealBuildTool;

public class MyGame : ModuleRules
{
    public MyGame(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "MobilePatchingUtils"  // 添加此依赖
        });
    }
}
```

### 完整的蓝图替代 C++ 示例

```cpp
// MyPatchManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MobilePatchingLibrary.h"
#include "MyPatchManager.generated.h"

UCLASS()
class AMyPatchManager : public AActor
{
    GENERATED_BODY()

public:
    /** 开始检查并下载补丁 */
    UFUNCTION(BlueprintCallable)
    void CheckAndDownloadPatch();

private:
    void OnRequestContentSucceeded(UMobilePendingContent* PendingContent);
    void OnRequestContentFailed(FText ErrorText, int32 ErrorCode);
    void OnInstallSucceeded();
    void OnInstallFailed(FText ErrorText, int32 ErrorCode);

    UPROPERTY()
    UMobilePendingContent* CurrentPendingContent = nullptr;
};
```

```cpp
// MyPatchManager.cpp
#include "MyPatchManager.h"

void AMyPatchManager::CheckAndDownloadPatch()
{
    // 检查是否已安装
    UMobileInstalledContent* Installed = UMobilePatchingLibrary::GetInstalledContent(TEXT("GamePatch"));
    if (Installed)
    {
        UE_LOG(LogTemp, Log, TEXT("已有安装内容: %.2f MB, 挂载中..."), Installed->GetInstalledContentSize());
        Installed->Mount(1, TEXT(""));
        return;
    }

    // 检查 WiFi
    if (!UMobilePatchingLibrary::HasActiveWiFiConnection())
    {
        UE_LOG(LogTemp, Warning, TEXT("无 WiFi，跳过补丁下载"));
        return;
    }

    // 请求远程内容
    UMobilePatchingLibrary::RequestContent(
        TEXT("http://cdn.example.com/game.manifest"),
        TEXT("http://cdn.example.com/game/chunks"),
        TEXT("GamePatch"),
        FOnRequestContentSucceeded::CreateUObject(this, &AMyPatchManager::OnRequestContentSucceeded),
        FOnRequestContentFailed::CreateUObject(this, &AMyPatchManager::OnRequestContentFailed)
    );
}

void AMyPatchManager::OnRequestContentSucceeded(UMobilePendingContent* PendingContent)
{
    CurrentPendingContent = PendingContent;
    UE_LOG(LogTemp, Log, TEXT("需要下载: %.2f MB"), PendingContent->GetDownloadSize());
    
    PendingContent->StartInstall(
        FOnContentInstallSucceeded::CreateUObject(this, &AMyPatchManager::OnInstallSucceeded),
        FOnContentInstallFailed::CreateUObject(this, &AMyPatchManager::OnInstallFailed)
    );
}

void AMyPatchManager::OnRequestContentFailed(FText ErrorText, int32 ErrorCode)
{
    UE_LOG(LogTemp, Error, TEXT("请求失败: %s (%d)"), *ErrorText.ToString(), ErrorCode);
}

void AMyPatchManager::OnInstallSucceeded()
{
    UE_LOG(LogTemp, Log, TEXT("补丁安装成功!"));
    if (CurrentPendingContent)
    {
        CurrentPendingContent->Mount(1, TEXT(""));
    }
}

void AMyPatchManager::OnInstallFailed(FText ErrorText, int32 ErrorCode)
{
    UE_LOG(LogTemp, Error, TEXT("安装失败: %s (%d)"), *ErrorText.ToString(), ErrorCode);
}
```

## 模块依赖

从 `MobilePatchingUtils.Build.cs` 提取：

| 模块 | 用途 | 依赖类型 |
|---|---|---|
| `Core` | 基础引擎核心 | Public |
| `CoreUObject` | UObject 系统 | Public |
| `Engine` | 引擎核心功能 | Public |
| `PakFile` | Pak 文件系统（挂载 pak） | Private |
| `HTTP` | HTTP 请求（下载 manifest） | Private |
| `BuildPatchServices` | 底层补丁/分块下载服务 | Private |

> 使用此 plugin 时，你的模块只需依赖 `MobilePatchingUtils`，上述 Private 依赖会自动传递。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-06-26 | `a2e7518` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 编译优化宏，自动生成 `#include` 替代旧的 gen.cpp 引用方式 |
| 2025-04-23 | `6ae5733` | Convert all files to have dllstorage on methods/staticvar | DLL 导出标记格式统一化，跨平台编译兼容性修复 |
| 2023-01-16 | `bbc37aa` | IWYU updates to reduce number of includes | 减少头文件依赖，加速编译 |

### 维护评价

- **创建时间**：2016 年 10 月，已近 10 年历史
- **功能状态**：自 2023 年起没有功能性更新，最近 3 次提交全部是编译/构建系统维护
- **API 稳定性**：API 极其稳定（实际上自 UE4 以来几乎未变），但这也意味着没有新功能
- **已知限制**：
  - `GetDownloadStatusText` 已在 UE4.21 标记为废弃
  - 仅支持移动端（Android/iOS），桌面平台需要其他方案
  - 底层依赖 `BuildPatchServices`，但该模块在打包时的行为可能因平台而异
- **推荐程度**：✅ 如果你需要移动端热更新且想用蓝图实现，这是官方推荐方案。但注意该 plugin 本质是 `BuildPatchServices` 的薄封装，如果需要更灵活的控制，可以直接使用底层模块。

⚠️ **注意**：最近 3 年（2023-2025）仅有编译系统维护更新，无功能性变更。Plugin 本身功能完整，但 Epic 似乎不再积极扩展其能力。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MobilePatchingUtils)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 底层模块：`BuildPatchServices`（Engine/Plugins 下无独立 plugin，为内置模块）
