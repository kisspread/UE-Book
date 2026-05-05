# HTTP Chunk Installer

> Implements a streaming install client

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | ❌ |
| 模块 | HTTPChunkInstaller (Runtime, PostConfigInit) |
| 创建时间 | 2017-06-14 |
| 年龄标签 | 👴 老古董 (>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HTTPChunkInstaller) | |

## 用途

HTTPChunkInstaller 实现了 **基于 HTTP 的流式分块安装 (Streaming Install)** 功能。它解决的核心问题是：大型游戏的下载和安装不需要一次完成全部内容，而是可以将游戏拆分为多个 **Chunk（数据块）**，通过 HTTP 从远程服务器按需下载和安装。

具体来说，这个 plugin：
1. 通过 HTTP 从远程服务器获取 **manifest 文件**（描述每个 Chunk 的元数据）
2. 使用 UE 的 **BuildPatchServices** 模块下载和验证 Chunk 数据
3. 管理 Chunk 的生命周期：发现 → 下载 → 安装 → 挂载 `.pak` 文件
4. 支持 Chunk 优先级排序，让玩家可以优先下载关键内容
5. 支持本地缓存，避免重复下载已有的 manifest

这是一个 `EnabledByDefault: false` 的 plugin，需要手动启用。它主要面向**主机平台和大型 PC 游戏**的流式安装场景（类似 PlayStation/Xbox 的"边下边玩"功能）。

## 使用场景

- 你正在开发一款大型游戏（如开放世界 RPG），需要实现"先下载基础内容，后续内容在后台流式安装" → 用 HTTPChunkInstaller
- 你需要将游戏内容分成多个 Chunk，让玩家可以优先下载游戏的核心区域，其他区域后台安装 → 用 HTTPChunkInstaller
- 你希望实现类似主机平台的"可选内容下载"，玩家只下载他们需要的 DLC/关卡 → 用 HTTPChunkInstaller
- 你需要通过 HTTP CDN 分发游戏的增量更新（patch），而不是重新下载整个游戏 → 用 HTTPChunkInstaller

## 蓝图用法

此 plugin **没有暴露任何蓝图节点**。它完全是 C++ 层面的运行时系统，通过实现 `IPlatformChunkInstall` 接口被引擎内部调用。游戏代码通过 `FGenericPlatformChunkInstall` 基类的接口（如 `GetChunkLocation`、`GetChunkProgress`、`PrioritizeChunk`）与之交互，但这些接口均不在蓝图层暴露。

## C++ 用法

### 核心概念

HTTPChunkInstaller 基于 UE 的 **Chunk Install** 抽象层工作。它实现了 `FGenericPlatformChunkInstall` 接口，作为引擎的平台 Chunk 安装后端。整个系统通过 **状态机驱动**，在 `Tick()` 中推进安装流程。

#### 状态机流转

```
Setup → SetupWait → QueryRemoteManifests → RequestingTitleFiles
  → SearchTitleFiles → ReadTitleFiles → WaitingOnRead → ReadComplete
  → PostSetup → Idle → Installing → CopyToContent → Idle (循环)
```

如果网络不可用，会进入 `EnterOfflineMode`，使用本地已安装的 Chunk。

### 配置说明

通过 `Engine.ini` 配置（节名为 `[HTTPChunkInstall]`）：

```ini
[HTTPChunkInstall]
; manifest 文件来源: "Http" 或 "Local"（默认使用本地文件）
TitleFileSource=Http

; 本地 manifest 目录（TitleFileSource=Local 时使用）
LocalTitleFileDirectory=../../../MyGame/Config/Chunks

; 云存储目录
CloudDirectory=MyGame/Chunks

; 云协议和域名（拼接为 protocol://domain 格式）
CloudProtocol=https
CloudDomain=cdn.example.com

; 各阶段目录
StageDirectory=D:/ChunkStage
InstallDirectory=D:/ChunkInstall
ContentDirectory=D:/ChunkContent
BackupDirectory=D:/ChunkBackup
HoldingDirectory=D:/ChunkHold
```

当 `TitleFileSource=Http` 时，还可以配置 HTTP 文件服务：

```ini
[HTTPOnlineTitleFile]
BaseUrl=cdn.example.com:8080
EnumerateFilesUrl=/manifests
```

### 查询 Chunk 状态

通过引擎的 `IPlatformChunkInstall` 接口查询：

```cpp
#include "GenericPlatform/GenericPlatformChunkInstall.h"

// 获取 Chunk 安装接口
IPlatformChunkInstall* ChunkInstall = FPlatformChunkInstall::Get();

// 查询 Chunk 是否可用
EChunkLocation::Type Location = ChunkInstall->GetChunkLocation(ChunkID);
if (Location == EChunkLocation::BestLocation)
{
    // Chunk 已安装，可以安全加载
}

// 获取安装进度 (0-100%)
float Progress = ChunkInstall->GetChunkProgress(ChunkID, EChunkProgressReportingType::PercentageComplete);

// 设置优先级（让引擎优先下载该 Chunk）
ChunkInstall->PrioritizeChunk(ChunkID, EChunkPriority::High);

// 控制安装速度
ChunkInstall->SetInstallSpeed(EChunkInstallSpeed::Paused);  // 暂停
ChunkInstall->SetInstallSpeed(EChunkInstallSpeed::Fast);     // 快速
ChunkInstall->SetInstallSpeed(EChunkInstallSpeed::Normal);   // 正常
```

### 内部类说明

| 类名 | 职责 |
|---|---|
| `FHTTPChunkInstall` | 核心类，实现 `FGenericPlatformChunkInstall` 接口，驱动整个安装状态机 |
| `FOnlineTitleFileHttp` | HTTP 标题文件接口实现，通过 HTTP GET 获取 manifest 列表和文件 |
| `FLocalTitleFile` | 本地标题文件接口实现，从本地目录读取 manifest |
| `FChunkInstallTask` | 后台线程任务，负责将下载的 Chunk 复制到 Content 目录并挂载 `.pak` |
| `FChunkSetupTask` | 后台线程任务，扫描已安装的 Chunk 目录，加载 manifest |
| `FChunkMountTask` | 后台线程任务，挂载已安装的 `.pak` 文件并清理过期 Chunk |

### 安装流程详解

1. **Setup 阶段**：`FChunkSetupTask` 在后台线程扫描三个目录：
   - `InstallDir`：安装中间目录
   - `ContentDir`：内容目录（已安装的 Chunk 在此挂载）
   - `HoldingDir`：存放旧版本 Chunk 的 manifest（用于增量更新）

2. **QueryRemoteManifests 阶段**：通过 `ICloudTitleFile` 接口枚举远程 manifest 文件列表

3. **ReadTitleFiles 阶段**：逐个下载 manifest 文件，支持本地缓存（通过 hash 校验）

4. **PostSetup 阶段**：`FChunkMountTask` 挂载已安装的 `.pak` 文件，清理不需要的旧 Chunk

5. **Idle/Installing 阶段**：按优先级队列依次安装远程 Chunk，使用 `BuildPatchServices` 下载和验证

## Demo 示例

### 最小集成示例

由于 HTTPChunkInstaller 是引擎级的平台插件，不需要游戏代码直接实例化。启用后它会自动替换默认的 Chunk Install 实现。

**步骤 1：启用 Plugin**

在项目的 `.uproject` 文件中添加：
```json
{
    "Plugins": [
        {
            "Name": "HTTPChunkInstaller",
            "Enabled": true
        }
    ]
}
```

**步骤 2：配置 Engine.ini**

在 `DefaultEngine.ini` 中配置：
```ini
[HTTPChunkInstall]
TitleFileSource=Http
CloudProtocol=https
CloudDomain=cdn.example.com
CloudDirectory=MyGame/Chunks

[HTTPOnlineTitleFile]
BaseUrl=cdn.example.com:8080
EnumerateFilesUrl=/manifests
```

**步骤 3：在游戏代码中使用 Chunk 查询**

```cpp
// MyGameLoadingManager.h
#pragma once
#include "GenericPlatform/GenericPlatformChunkInstall.h"

class FMyGameLoadingManager
{
public:
    // 等待某个 Chunk 安装完成
    bool IsChunkReady(uint32 ChunkID) const
    {
        IPlatformChunkInstall* ChunkInstall = FPlatformChunkInstall::Get();
        if (!ChunkInstall) return false;
        return ChunkInstall->GetChunkLocation(ChunkID) == EChunkLocation::BestLocation;
    }

    // 请求优先安装某个 Chunk
    void RequestPriorityInstall(uint32 ChunkID)
    {
        IPlatformChunkInstall* ChunkInstall = FPlatformChunkInstall::Get();
        if (ChunkInstall)
        {
            ChunkInstall->PrioritizeChunk(ChunkID, EChunkPriority::High);
            ChunkInstall->SetInstallSpeed(EChunkInstallSpeed::Fast);
        }
    }

    // 获取 Chunk 安装进度
    float GetChunkInstallProgress(uint32 ChunkID) const
    {
        IPlatformChunkInstall* ChunkInstall = FPlatformChunkInstall::Get();
        if (!ChunkInstall) return 0.f;
        return ChunkInstall->GetChunkProgress(
            ChunkID, EChunkProgressReportingType::PercentageComplete);
    }
};
```

**Build.cs 依赖**：
```csharp
// 注意：HTTPChunkInstaller 的接口来自 Engine 模块
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "Engine"
});
```

## 模块依赖

HTTPChunkInstaller 自身依赖以下模块（全部为 `PrivateDependencyModuleNames`，使用者不需要额外引用）：

| 模块 | 用途 |
|---|---|
| `BuildPatchServices` | Chunk 下载、安装、manifest 管理的核心服务 |
| `Core` | UE 核心库，基础类型、文件系统、线程等 |
| `ApplicationCore` | 平台应用层抽象 |
| `Engine` | 引擎核心，`FGenericPlatformChunkInstall` 接口定义 |
| `HTTP` | HTTP 请求，用于从远程服务器下载 manifest 和 Chunk 数据 |
| `Json` | JSON 解析，用于解析服务器返回的文件列表 |
| `PakFile` | `.pak` 文件系统，Chunk 安装后通过 `FCoreDelegates::MountPak` 挂载 |

## 维护状态

### 近期更新

| 日期 | Commit | 内容 | 解读 |
|---|---|---|---|
| 2025-06-11 | `664cf2c` | Replace some usages of FORCEINLINE with inline in Foundation modules. | 纯代码风格修改，将 `FORCEINLINE` 替换为 `inline`，无功能变化 |
| 2023-10-12 | `ffb133e` | Update more code using FJsonObject to use TCHAR strings instead of ANSI strings. | 适配 FJsonObject API 变更，将 ANSI 字符串改为 TCHAR，属于编译兼容性修复 |
| 2023-08-03 | `02c422c` | Add http request progress delegate 64 bit support. | 功能性更新：为 HTTP 请求添加 64 位进度回调支持 |

### 维护评价

- **创建时间**：2017 年 6 月，已超过 8 年
- **更新频率**：最近 3 次提交跨越约 2 年（2023-2025），且均为维护性修改，无实质性功能更新
- **活跃度**：⚠️ **维护不活跃**。最近一次功能性更新在 2023 年 8 月，之后只有代码风格和编译兼容性修复
- **状态**：该 plugin 处于稳定但低活跃状态。核心功能在多年前已完成，没有重大 bug 修复或新特性
- **是否推荐使用**：如果你的项目需要 HTTP 流式安装功能，这个 plugin 仍然可用且功能完整。但需要注意：
  1. 它依赖 `BuildPatchServices` 模块（Epic 自己用于 Epic Games Store 的分发系统），配置较复杂
  2. 没有蓝图接口，所有集成需要 C++ 代码
  3. 文档稀缺，需要阅读源码理解工作流程
  4. 没有找到对应的自动化测试用例

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HTTPChunkInstaller)
- [BuildPatchServices 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/BuildPatchServices)（核心依赖）
- [FGenericPlatformChunkInstall 接口](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/Engine/Public/GenericPlatform/GenericPlatformChunkInstall.h)
