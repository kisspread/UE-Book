# Chunk Downloader

> Implements a streaming install client

| 属性 | 值 |
|---|---|
| 中文名 | 分块下载器 |
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChunkDownloader` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ChunkDownloader) | |

## 用途

`ChunkDownloader` 是一个用于管理游戏内容按需下载、缓存和挂载的运行时系统。它解决了大型游戏（如开放世界、持续更新服务型游戏）无法将所有内容一次性打包进初始安装包的问题。

其核心功能是：
1.  **流式安装**：允许玩家先启动游戏的核心部分，然后根据需要（如进入特定关卡、下载DLC）再从内容分发网络（CDN）下载额外的内容包（Pak 文件）。
2.  **分块管理**：将内容组织成逻辑上的“块”（Chunk），每个块对应一个或多个 Pak 文件。可以独立下载、缓存和管理这些块。
3.  **状态跟踪**：精确追踪每个内容块的下载和挂载状态（如 `Remote`、`Downloading`、`Cached`、`Mounted`）。
4.  **加载模式**：支持进入“加载模式”，暂停后台下载，优先完成特定块的下载和挂载以显示加载界面。
5.  **缓存管理**：管理本地缓存，支持清理、校验缓存文件。

简而言之，它是一个客户端内容管理系统，实现了完整的“下载 -> 缓存 -> 校验 -> 挂载（挂载Pak文件到引擎）”流程。

## 使用场景

-   **大型开放世界游戏**：初始包只包含基础地图和核心玩法，玩家进入新区域时按需下载该区域的资源包。
-   **可下载内容（DLC）管理**：DLC 以“块”的形式存在，玩家购买后自动下载并挂载。
-   **游戏启动优化**：优先下载和挂载最常使用的内容（如主菜单资源），提高启动速度。
-   **多平台分发**：通过 `PlatformName` 配置，适配不同平台的 CDN 地址和存储路径。

## 蓝图用法

`ChunkDownloader` 主要是一个 C++ 系统，其核心类 `FChunkDownloader` 并非 `UObject`，因此不能直接暴露给蓝图。但是，你可以通过 C++ 创建一个蓝图函数库或游戏子系统（Subsystem）来封装其常用功能（如检查状态、触发下载），从而在蓝图中调用。

### 核心节点（概念封装）

以下概念可以通过封装在蓝图中实现：

| 功能描述 | 对应的 C++ API | 所在类 |
|---|---|---|
| 获取下载器实例 | `FChunkDownloader::GetOrCreate()` | `FChunkDownloader` |
| 初始化下载系统 | `Initialize()` | `FChunkDownloader` |
| 更新内容版本（触发下载新清单） | `UpdateBuild()` | `FChunkDownloader` |
| 下载并挂载特定内容块 | `MountChunk()` / `MountChunks()` | `FChunkDownloader` |
| 仅下载内容块（不挂载） | `DownloadChunk()` / `DownloadChunks()` | `FChunkDownloader` |
| 查询内容块状态 | `GetChunkStatus()` | `FChunkDownloader` |
| 获取所有内容块 ID | `GetAllChunkIds()` | `FChunkDownloader` |
| 进入加载模式 | `BeginLoadingMode()` | `FChunkDownloader` |
| 获取加载统计信息 | `GetLoadingStats()` | `FChunkDownloader` |

### 使用示例（蓝图描述）

假设你创建了一个名为 `UChunkDownloaderBPLibrary` 的蓝图函数库来封装 `FChunkDownloader`。

1.  **初始化**：在游戏开始时（如 `GameInstance` 的初始化函数中），调用封装后的“初始化下载器”节点，传入目标平台名称（如 “Windows”）和最大并发下载数。
2.  **更新内容版本**：从后端或本地配置获取当前游戏的 `ContentBuildId`，调用“更新构建版本”节点。该节点会检查是否需要下载新的内容清单。
3.  **触发下载**：当玩家接近一个需要新内容的区域（如传送门），或者购买 DLC 后，调用“下载并挂载块”节点，传入对应的 `ChunkId`。
4.  **显示加载**：在调用“下载并挂载块”后，可以立即调用“进入加载模式”节点，并绑定“完成”回调。在加载模式期间，可以在 UI 上显示来自 `GetLoadingStats` 的下载进度。
5.  **状态检查**：在 UI 或逻辑中，使用“获取块状态”节点来检查某个块是否已就绪。

## C++ 用法

### 头文件引入

```cpp
#include "ChunkDownloader.h"
```

### 基本用法

以下示例展示了典型的初始化、更新构建版本和下载挂载流程。代码逻辑基于插件源码中的核心API。

```cpp
// 假设在某个管理类（如 GameInstance）中

// 1. 获取或创建 ChunkDownloader 实例
TSharedRef<FChunkDownloader> Downloader = FChunkDownloader::GetOrCreate();

// 2. 初始化，通常在游戏启动时调用一次
// PlatformName: 目标平台标识，如 "Windows", "Android"
// TargetDownloadsInFlight: 最大同时下载的Pak文件数，用于控制带宽和磁盘IO
Downloader->Initialize(FPlatformProperties::PlatformName(), 3);

// 3. 尝试加载缓存的构建ID（可选，用于快速启动）
FString CachedBuildId;
bool bHasCache = Downloader->LoadCachedBuild(TEXT("MyGame"));

// 4. 从服务器获取或本地配置确定当前内容版本
FString CurrentBuildId = TEXT("v1.2.3"); // 通常从配置文件或后端服务获取

// 5. 更新构建版本，这会触发下载新的 Manifest 清单（如果版本不同）
Downloader->UpdateBuild(TEXT("Production"), CurrentBuildId,
    FChunkDownloader::FCallback::CreateLambda([](bool bSuccess) {
        if (bSuccess) {
            UE_LOG(LogTemp, Log, TEXT("Build manifest updated successfully."));
        } else {
            UE_LOG(LogTemp, Error, TEXT("Failed to update build manifest."));
        }
    })
);
```

### 进阶用法

在构建版本更新成功后，可以查询可用块并执行下载。以下代码演示了如何下载一组块并进入加载模式以跟踪进度。

```cpp
// 假设 Manifest 已通过 UpdateBuild 更新成功

// 1. 获取所有可用的 Chunk ID
TArray<int32> AllChunkIds;
Downloader->GetAllChunkIds(AllChunkIds);

// 2. 定义需要优先下载的 Chunk ID 列表（例如，玩家即将进入的区域）
TArray<int32> PriorityChunks = {101, 102, 103};

// 3. 检查这些块的当前状态
for (int32 ChunkId : PriorityChunks) {
    FChunkDownloader::EChunkStatus Status = Downloader->GetChunkStatus(ChunkId);
    if (Status == FChunkDownloader::EChunkStatus::Remote) {
        UE_LOG(LogTemp, Log, TEXT("Chunk %d needs to be downloaded."), ChunkId);
    }
}

// 4. 进入加载模式，暂停非必要的后台下载
Downloader->BeginLoadingMode(FChunkDownloader::FCallback::CreateLambda(
    [Downloader]() {
        // 加载完成回调
        const FChunkDownloader::FStats& Stats = Downloader->GetLoadingStats();
        UE_LOG(LogTemp, Log, TEXT("Loading mode completed. Files Downloaded: %d, Bytes Downloaded: %llu"),
            Stats.FilesDownloaded, Stats.BytesDownloaded);
    }
));

// 5. 请求下载并挂载这些块，其内部会管理加载模式下的优先级
Downloader->DownloadChunks(PriorityChunks,
    FChunkDownloader::FCallback::CreateLambda([PriorityChunks](bool bSuccess) {
        if (bSuccess) {
            UE_LOG(LogTemp, Log, TEXT("Priority chunks downloaded and cached successfully."));
            // 下一步：可以调用 MountChunks 来挂载它们
        } else {
            UE_LOG(LogTemp, Error, TEXT("Failed to download priority chunks."));
        }
    }),
    /*Priority=*/ 10 // 可选，用于内部优先级排序
);
```

**注意事项**：
- `FChunkDownloader` 是单例模式，通过 `Get()`/`GetOrCreate()`/`GetChecked()` 访问。
- 所有异步操作（下载、挂载）都通过回调函数 `FCallback` 通知结果。
- `BeginLoadingMode` 会改变下载调度策略，优先处理模式开始前已排队的下载请求。

## Demo 示例

以下是一个简化的管理器类头文件和源文件，展示了如何在自己的项目中集成 `ChunkDownloader`。

```cpp
// MyChunkDownloadManager.h
#pragma once

#include "CoreMinimal.h"
#include "ChunkDownloader.h"

class UMyChunkDownloadManager : public UObject
{
public:
    void Initialize();
    void UpdateGameContent(const FString& BuildId);
    void RequestChunks(const TArray<int32>& ChunkIds);

private:
    TSharedPtr<FChunkDownloader> ChunkDownloader;
};
```

```cpp
// MyChunkDownloadManager.cpp
#include "MyChunkDownloadManager.h"

void UMyChunkDownloadManager::Initialize()
{
    ChunkDownloader = FChunkDownloader::GetOrCreate();
    ChunkDownloader->Initialize(FPlatformProperties::PlatformName(), 4); // 最多4个并行下载
}

void UMyChunkDownloadManager::UpdateGameContent(const FString& BuildId)
{
    if (ChunkDownloader.IsValid())
    {
        // 检查本地是否有缓存的构建，避免不必要的网络请求
        ChunkDownloader->LoadCachedBuild(TEXT("Default"));

        // 更新构建版本
        ChunkDownloader->UpdateBuild(TEXT("Default"), BuildId,
            FChunkDownloader::FCallback::CreateWeakLambda(this, [this](bool bSuccess)
            {
                if (bSuccess)
                {
                    UE_LOG(LogTemp, Log, TEXT("Content build update successful."));
                }
            })
        );
    }
}

void UMyChunkDownloadManager::RequestChunks(const TArray<int32>& ChunkIds)
{
    if (ChunkDownloader.IsValid())
    {
        ChunkDownloader->MountChunks(ChunkIds,
            FChunkDownloader::FCallback::CreateWeakLambda(this, [ChunkIds](bool bSuccess)
            {
                if (bSuccess)
                {
                    UE_LOG(LogTemp, Log, TEXT("Requested chunks are now mounted and ready."));
                }
            })
        );
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/HTTP 等） | 该插件依赖 UE 核心模块和 HTTP 模块来实现网络请求和文件操作，这些都是项目通常已具备的基础依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新标准 UE_LOGF。 |
| 2026-02-25 | `12a309dc` | Remove as many PVS suppressions as possible that are no longer needed | 移除不再需要的静态代码分析（PVS-Studio）抑制指令。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar | 为所有导出符号添加了 DLL 导出/导入宏（`dllexport`/`dllimport`），增强了跨模块兼容性。 |
| 2025-04-08 | `855b561a` | Fixed some wrongly-sized printf specifiers. | 修复了日志中一些类型大小不匹配的格式化说明符。 |
| 2024-11-10 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 清理了代码中关于头文件包含顺序的旧版兼容性宏。 |

### 维护评价

-   **年龄**：插件于 2020 年创建，已有约 6 年历史，属于“老古董”级别。
-   **活跃度**：最近几次提交均为编译器警告修复、代码规范统一或引擎宏迁移等**维护性更新**，**没有功能性新特性或重大修复**。最近一次功能性相关更新（DLL导出）也在一年前。可以认为**维护不活跃**。
-   **稳定性**：插件功能完整，核心逻辑稳定，最近的更新并未改变其核心行为。但其底层网络和Pak系统可能随引擎大版本更新而需要适配。
-   **建议**：**可以使用**，尤其对于理解其工作原理的项目。对于新项目，需评估其是否符合最新的项目架构（如是否考虑使用引擎更新的资产打包和管理方案）。由于长期无实质性更新，遇到特定边缘情况下的问题时，可能需要开发者自行排查和修复。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ChunkDownloader)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/OnlineSubsystem/ChunkDownloader/) (Epic Games 官方文档)