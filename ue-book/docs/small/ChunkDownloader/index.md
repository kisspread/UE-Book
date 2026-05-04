# Chunk Downloader

> Implements a streaming install client

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | 否 |
| 模块 | ChunkDownloader (Runtime, PostConfigInit) |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董 (>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ChunkDownloader) | |

## 用途

ChunkDownloader 是 UE5 内置的**流式安装（Streaming Install）客户端**，用于在游戏运行时从 CDN 按需下载 Pak 文件并挂载到引擎的虚拟文件系统中。

它解决的核心问题是：**大型游戏不需要等待全部内容下载完成才能启动**。通过将游戏内容分割成多个 Chunk（每个 Chunk 由一个或多个 Pak 文件组成），客户端可以先下载最小启动集，然后在后台逐步下载其余内容。用户在加载屏幕期间下载关键 Chunk，非关键 Chunk 则在后台静默下载。

整个流程包括：从 CDN 获取 BuildManifest → 按需下载 Pak 文件 → 验证完整性（SHA1） → 异步挂载到引擎。

## 使用场景

- 你在做一个需要快速首屏启动的大型游戏（如手游、主机游戏） → 用 ChunkDownloader 实现流式安装
- 你需要将游戏内容分成多个 Chunk，按优先级下载 → ChunkDownloader 支持优先级和加载模式
- 你希望支持断点续传和自动重试 → 内置 HTTP Range 请求和指数退避重试
- 你有内容需要打包后从 CDN 分发 → 配合 `BuildPakFiles.js` 脚本生成清单和 CDN 目录结构

## 蓝图用法

ChunkDownloader **没有暴露任何蓝图接口**。它是一个纯 C++ 运行时模块，通过 `FChunkDownloader` 类的静态方法访问。如需在蓝图中触发下载，需要通过自定义的 BlueprintCallable 函数包装 C++ 调用。

## C++ 用法

### 头文件引入

```cpp
#include "ChunkDownloader.h"
```

### 基本用法

以下模式基于源码中 `FChunkDownloader` 的公共 API 设计：

```cpp
// 1. 获取或创建 ChunkDownloader 实例
TSharedRef<FChunkDownloader> Downloader = FChunkDownloader::GetOrCreate();

// 2. 初始化（通常在 GameInstance 启动时调用一次）
//    参数: 平台名称, 最大并发下载数
Downloader->Initialize(FPlatformProperties::PlatformName(), 4);

// 3. 尝试加载缓存的 Build（避免不必要的 CDN 请求）
bool bHasCachedBuild = Downloader->LoadCachedBuild(TEXT("MyDeployment"));

// 4. 更新 Build（如果 BuildId 变化，会自动从 CDN 拉取新 Manifest）
Downloader->UpdateBuild(TEXT("MyDeployment"), TEXT("v1.0.0-r12345"), 
    [](bool bSuccess) {
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("Build manifest loaded successfully"));
        }
    });

// 5. 查询 Chunk 状态
FChunkDownloader::EChunkStatus Status = Downloader->GetChunkStatus(1);
// 状态枚举: Mounted, Cached, Downloading, Partial, Remote, Unknown

// 6. 下载并挂载一个 Chunk
Downloader->MountChunk(1, [](bool bSuccess) {
    UE_LOG(LogTemp, Log, TEXT("Chunk 1 mount: %s"), bSuccess ? TEXT("OK") : TEXT("FAILED"));
});

// 7. 仅下载不挂载（后台预缓存）
Downloader->DownloadChunk(2, [](bool bSuccess) {
    UE_LOG(LogTemp, Log, TEXT("Chunk 2 download: %s"), bSuccess ? TEXT("OK") : TEXT("FAILED"));
}, /*Priority=*/0);
```

### 进阶用法

#### 加载屏幕模式

在显示加载屏幕时，可以进入"加载模式"暂停后台下载，集中带宽下载关键内容：

```cpp
// 进入加载模式（暂停后台下载，计算进度统计）
Downloader->BeginLoadingMode([](bool bSuccess) {
    // 所有前台下载+挂载完成后回调
    UE_LOG(LogTemp, Log, TEXT("Loading complete: %s"), bSuccess ? TEXT("OK") : TEXT("FAILED"));
});

// 在加载屏幕中轮询进度
const FChunkDownloader::FStats& Stats = Downloader->GetLoadingStats();
float Progress = Stats.TotalBytesToDownload > 0 
    ? (float)Stats.BytesDownloaded / Stats.TotalBytesToDownload 
    : 1.0f;
```

#### 批量下载和挂载

```cpp
TArray<int32> ChunkIds = { 1, 2, 3 };

// 批量下载
Downloader->DownloadChunks(ChunkIds, [](bool bSuccess) {
    UE_LOG(LogTemp, Log, TEXT("All chunks downloaded"));
}, /*Priority=*/0);

// 批量挂载（下载 + 挂载）
Downloader->MountChunks(ChunkIds, [](bool bSuccess) {
    UE_LOG(LogTemp, Log, TEXT("All chunks mounted"));
});
```

#### 缓存管理

```cpp
// 清理未使用的缓存文件
int FilesSkipped = Downloader->FlushCache();

// 验证缓存完整性（SHA1 校验，阻塞操作）
int InvalidFiles = Downloader->ValidateCache();
if (InvalidFiles > 0)
{
    // 有文件损坏，建议重新初始化
    UE_LOG(LogTemp, Warning, TEXT("%d invalid files deleted"), InvalidFiles);
}
```

#### 监听事件

```cpp
// 被动监听 Chunk 挂载事件
Downloader->OnChunkMounted.AddLambda([](uint32 ChunkId, bool bSuccess) {
    UE_LOG(LogTemp, Log, TEXT("Chunk %d mounted: %s"), ChunkId, bSuccess ? TEXT("OK") : TEXT("FAILED"));
});

// 监听下载分析数据
Downloader->OnDownloadAnalytics = [](const FString& FileName, const FString& Url, 
    uint64 SizeBytes, const FTimespan& DownloadTime, int32 HttpStatus) {
    UE_LOG(LogTemp, Log, TEXT("Downloaded %s (%llu bytes) in %.2f seconds (HTTP %d)"),
        *FileName, SizeBytes, DownloadTime.GetTotalSeconds(), HttpStatus);
};
```

#### 清理

```cpp
// 优雅关闭（卸载所有 Chunk，取消所有下载）
Downloader->Finalize();

// 或通过静态方法关闭整个模块
FChunkDownloader::Shutdown();
```

## 配置说明

ChunkDownloader 通过 `DefaultGame.ini` 配置 CDN 地址：

```ini
; 通用配置（所有 Deployment 共享）
[/Script/Plugins.ChunkDownloader]
CdnBaseUrls=https://cdn1.example.com/game/
CdnBaseUrls=https://cdn2.example.com/game/

; 按 Deployment 配置（优先级高于通用配置）
[/Script/Plugins.ChunkDownloader MyDeployment]
CdnBaseUrls=https://my-cdn.example.com/game/
```

## 清单文件格式

ChunkDownloader 使用三种清单文件：

### BuildManifest-{Platform}.txt（CDN 上的构建清单）

```
$BUILD_ID = v1.0.0-r12345
$NUM_ENTRIES = 3
chunk1-pak1.pak	1048576	SHA1:AABBCCDD...	1	Windows/chunk1-pak1.pak
chunk2-pak1.pak	2097152	SHA1:EEFF0011...	2	Windows/chunk2-pak1.pak
chunk3-pak1.pak	524288	SHA1:22334455...	3	Windows/chunk3-pak1.pak
```

每行格式：`文件名\t文件大小\t版本标识\tChunkId\t相对URL`

### EmbeddedManifest.txt（随包分发的嵌入式 Pak 清单）

位于 `Content/EmbeddedPaks/`，格式与 BuildManifest 相同但 ChunkId 为 -1。

### LocalManifest.txt（本地缓存记录）

由 ChunkDownloader 自动维护，记录已下载到本地的 Pak 文件。

## Demo 示例

### 最小集成示例

```cpp
// MyGameInstance.h
#pragma once
#include "Engine/GameInstance.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()
public:
    virtual void Init() override;
    virtual void Shutdown() override;

private:
    void OnBuildUpdated(bool bSuccess);
    void OnChunkMounted(uint32 ChunkId, bool bSuccess);
};
```

```cpp
// MyGameInstance.cpp
#include "MyGameInstance.h"
#include "ChunkDownloader.h"

void UMyGameInstance::Init()
{
    Super::Init();

    // 创建并初始化
    TSharedRef<FChunkDownloader> Downloader = FChunkDownloader::GetOrCreate();
    Downloader->Initialize(FPlatformProperties::PlatformName(), 4);

    // 监听挂载事件
    Downloader->OnChunkMounted.AddUObject(this, &UMyGameInstance::OnChunkMounted);

    // 尝试加载缓存 Build
    FString Deployment = TEXT("Production");
    Downloader->LoadCachedBuild(Deployment);

    // 更新到最新 Build
    Downloader->UpdateBuild(Deployment, TEXT("v1.0.0-r12345"),
        [this](bool bSuccess) { OnBuildUpdated(bSuccess); });
}

void UMyGameInstance::Shutdown()
{
    FChunkDownloader::Shutdown();
    Super::Shutdown();
}

void UMyGameInstance::OnBuildUpdated(bool bSuccess)
{
    if (!bSuccess) return;

    TSharedRef<FChunkDownloader> Downloader = FChunkDownloader::GetChecked();

    // 启动加载屏幕模式，下载 Chunk 1（启动关键内容）
    Downloader->BeginLoadingMode([](bool bSuccess) {
        UE_LOG(LogTemp, Log, TEXT("Essential content loaded: %s"),
            bSuccess ? TEXT("OK") : TEXT("FAILED"));
    });

    // 下载并挂载 Chunk 1
    Downloader->MountChunk(1, FChunkDownloader::FCallback());

    // 后台预缓存 Chunk 2 和 3
    Downloader->DownloadChunk(2, FChunkDownloader::FCallback(), 0);
    Downloader->DownloadChunk(3, FChunkDownloader::FCallback(), 0);
}

void UMyGameInstance::OnChunkMounted(uint32 ChunkId, bool bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Chunk %u mount result: %s"),
        ChunkId, bSuccess ? TEXT("Success") : TEXT("Failed"));
}
```

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "ChunkDownloader"
});
```

注意：ChunkDownloader 的依赖（Core, HTTP 等）是 Private 的，使用者只需依赖 `ChunkDownloader` 模块即可。

## CDN 部署工具

插件附带两个 Node.js 脚本用于构建 CDN 目录结构：

### BuildPakFiles.js

```bash
# 处理构建产物：复制 Pak 文件 + 生成清单
node BuildPakFiles.js process <构建输出目录> <CDN暂存目录>

# 仅复制文件
node BuildPakFiles.js move <构建输出目录> <CDN暂存目录>

# 仅生成清单（文件已复制的情况下）
node BuildPakFiles.js manifest <CDN暂存目录>
```

脚本会自动：
1. 从构建目录提取 Pak 文件并重命名为 `chunk{id}-pak{num}.pak` 格式
2. 按平台分目录组织
3. 计算 SHA1 校验和
4. 生成 `BuildManifest-{Platform}.txt` 和 `EmbeddedManifest.txt`

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础设施（文件管理、Ticker、异步任务） |
| `ApplicationCore` | 平台相关功能（磁盘空间查询、根目录注册） |
| `CoreUObject` | 垃圾回收（Manifest 更新时清理引用） |
| `HTTP` | HTTP 下载（CDN 请求、Range 断点续传） |

使用者只需依赖：`ChunkDownloader`

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-04-23 | `89df8c1` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types. | 构建系统重构，DLL 导出方式调整，无功能变化 |
| 2025-04-08 | `855b561` | Fixed some wrongly-sized printf specifiers. | 修复 printf 格式说明符大小问题，Bug 修复 |
| 2024-11-09 | `66e9bb3` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base. | 代码清理，移除废弃的 include 顺序兼容宏 |

### 维护评价

- **创建时间**：2020 年 9 月，已有 5 年以上历史
- **活跃度**：最近的更新都是编译修复和代码清理，**无功能性更新**
- **代码质量**：代码结构清晰，1862 行核心实现，注释充分
- **平台支持**：Android/iOS 的流式下载实现标记为 `#error "TODO"`（被 `#if 0` 禁用），说明移动端平台原生下载尚未实现，统一使用 HTTP 回退方案
- **测试**：未发现专门的自动化测试用例
- **状态**：**维护不活跃**。核心功能稳定，但已超过 2 年没有实质性功能更新。作为内置插件默认启用，说明 Epic 认为其仍可用。
- **建议**：适合需要流式安装的项目使用，但需注意移动端原生下载支持缺失。如果项目不需要流式安装，可以安全地忽略此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ChunkDownloader)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/Networking/ChunkDownloader/)（Epic Wiki）
