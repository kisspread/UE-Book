# GDK Package Chunk Installer

> Allows titles to use GDK chunk installer (XPackage)（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | GDK 分块安装器 |
| 分类 | Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GDKPackageChunkInstall` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Microsoft/GDKPackageChunkInstall) | |

## 用途

此插件是微软 GDK (Xbox 开发工具包) 平台的**分块安装实现**。它解决了 Xbox 平台游戏（特别是通过微软商店发布的游戏）的按需内容下载和安装管理问题。核心功能是将游戏内容（Pak 文件）分割成可管理的“块”（Chunks），这些块可以按需下载、安装、卸载和监控进度。它支持基于**语言**和**功能特性**的命名分块，以及智能交付（Intelligent Delivery）功能，允许玩家只下载他们需要的内容（例如特定语言包或游戏功能模块），从而优化存储空间和首次安装时间。

## 使用场景

- 你正在为 Xbox 平台开发游戏，并希望通过微软商店发布。
- 你的游戏包含大量可选内容，如多种语言语音包、不同地区的特定内容、或可选的游戏模式，希望玩家按需下载。
- 你需要精细控制游戏内容的下载优先级和安装状态，并向玩家展示下载进度。
- 你计划使用 GDK 的智能交付（Intelligent Delivery）和包清单（Package Manifest）功能来管理内容。

## 蓝图用法

此插件主要工作在**平台抽象层**，实现了 `FGenericPlatformChunkInstall` 的虚函数。它**没有直接暴露 `BlueprintCallable` 节点**。游戏逻辑和蓝图通过引擎通用的 `IPlatformChunkInstall` 接口（由 `FGDKPlatformChunkInstall` 提供实现）来与分块安装系统交互。

**核心接口（通过引擎通用接口访问）：**

| 功能 | 说明 | 访问方式 |
|---|---|---|
| 查询分块位置 | 获取指定 Pak 分块（按索引）或命名分块（按名称）的当前安装位置（如本地、远程）。 | 通过引擎的 `IPlatformChunkInstall` 接口调用 `GetPakchunkLocation` 或 `GetNamedChunkLocation` |
| 查询下载进度 | 获取指定分块的下载进度（百分比）。 | 通过引擎的 `IPlatformChunkInstall` 接口调用 `GetChunkProgress` 或 `GetNamedChunkProgress` |
| 设置优先级 | 设置分块下载的优先级（高、中、低），影响下载顺序。 | 通过引擎的 `IPlatformChunkInstall` 接口调用 `PrioritizePakchunk` 或 `PrioritizeNamedChunk` |
| 请求安装/卸载 | 主动请求安装或卸载指定的命名分块。 | 通过引擎的 `IPlatformChunkInstall` 接口调用 `InstallNamedChunks` 或 `UninstallNamedChunks` |
| 取消安装 | 取消正在进行的命名分块安装。 | 通过引擎的 `IPlatformChunkInstall` 接口调用 `CancelNamedChunksInstall` |
| 查询类型 | 查询命名分块的类型（如按需分块、语言分块）。 | 通过引擎的 `IPlatformChunkInstall` 接口调用 `GetNamedChunkType` 或 `GetNamedChunksByType` |

**使用示例（蓝图概念描述）：**

在蓝图中，你无法直接访问 `FGDKPlatformChunkInstall` 类。通常，你会使用引擎提供的更高层级的系统或服务（如资产管理系统、DLC 管理器）来间接调用分块安装功能。这些系统内部会使用 `IPlatformChunkInstall` 接口。例如，当玩家在设置中切换语言时，系统可能会调用 `InstallNamedChunks` 来下载对应的语言包，并通过 `GetNamedChunkProgress` 来更新 UI 上的进度条。

## C++ 用法

此插件的代码主要是**平台后端实现**，游戏逻辑层通常不直接包含或实例化 `FGDKPlatformChunkInstall`。游戏开发者通过引擎的通用 `IPlatformChunkInstall` 接口与其交互。

### 头文件引入

如果你需要直接访问 GDK 平台特定的类型或助手函数（例如用于调试），可以包含：

```cpp
#include "GDKPlatformChunkInstall.h"
```

### 基本用法

这是一个平台实现，通常不由游戏代码直接调用。以下展示了游戏代码如何通过通用接口使用分块安装功能：

```cpp
// 假设我们有一个 IPlatformChunkInstall* PlatformChunkInstall 指针
// （通常从 FPlatformMisc::GetPlatformChunkInstall() 获得）

// 检查平台分块安装是否可用
if (PlatformChunkInstall && PlatformChunkInstall->IsAvailable())
{
    // 查询第 1 号 Pak 分块是否已安装
    EChunkLocation::Type Location = PlatformChunkInstall->GetPakchunkLocation(1);
    bool bIsLocal = (Location == EChunkLocation::Local);

    // 查询名为 “LanguagePack_ZH” 的命名分块的下载进度
    if (PlatformChunkInstall->SupportsNamedChunkInstall())
    {
        float Progress = PlatformChunkInstall->GetNamedChunkProgress(
            FName(TEXT(“LanguagePack_ZH”)),
            EChunkProgressReportingType::PercentageComplete
        );
        UE_LOG(LogTemp, Log, TEXT(“中文语言包进度: %.2f%%“), Progress * 100.0f);

        // 请求高优先级安装该语言包
        PlatformChunkInstall->PrioritizeNamedChunk(
            FName(TEXT(“LanguagePack_ZH”)),
            EChunkPriority::High
        );
    }
}
```

### 进阶用法

结合多个功能，实现一个简单的按需内容管理器：

```cpp
// 头文件中声明
DECLARE_DELEGATE_OneParam(FOnChunkReady, FName);

// 管理器类
class FMyContentManager
{
public:
    void RequestContent(FName ContentName, FOnChunkReady OnReadyDelegate);
    void Tick(float DeltaTime);

private:
    TMap<FName, FOnChunkReady> PendingContentRequests;
};

// 实现
void FMyContentManager::RequestContent(FName ContentName, FOnChunkReady OnReadyDelegate)
{
    IPlatformChunkInstall* ChunkInstall = FPlatformMisc::GetPlatformChunkInstall();
    if (!ChunkInstall || !ChunkInstall->SupportsNamedChunkInstall())
    {
        return;
    }

    // 检查是否已本地可用
    if (ChunkInstall->GetNamedChunkLocation(ContentName) == EChunkLocation::Local)
    {
        OnReadyDelegate.ExecuteIfBound(ContentName);
        return;
    }

    // 存储委托并启动安装
    PendingContentRequests.Add(ContentName, OnReadyDelegate);
    ChunkInstall->InstallNamedChunks({&ContentName, 1});
    ChunkInstall->PrioritizeNamedChunk(ContentName, EChunkPriority::High);
}

void FMyContentManager::Tick(float DeltaTime)
{
    IPlatformChunkInstall* ChunkInstall = FPlatformMisc::GetPlatformChunkInstall();
    if (!ChunkInstall) return;

    // 轮询待定内容的安装状态
    for (auto It = PendingContentRequests.CreateIterator(); It; ++It)
    {
        FName ChunkName = It.Key();
        if (ChunkInstall->GetNamedChunkLocation(ChunkName) == EChunkLocation::Local)
        {
            // 内容已就绪，触发回调并从待定列表中移除
            It.Value().ExecuteIfBound(ChunkName);
            It.RemoveCurrent();
        }
    }
}
```

## Demo 示例

此插件是平台后端实现，通常不提供独立的可编译游戏代码示例。其核心逻辑体现在 `FGDKPlatformChunkInstall` 类中（见源码）。一个最小的“使用者”示例就是上一节“基本用法”中的代码片段，它演示了如何通过引擎通用接口查询和操作分块。

## 模块依赖

此插件的构建依赖（从 `.uplugin` 推断）：

| 模块 | 用途 |
|---|---|
| `XPackage` | GDK 的核心包管理头文件，提供 `XPackageChunkSelector`， `XPackageInstallationMonitorHandle` 等类型。这是 GDK 平台特有的依赖。 |
| `MSGameStore` | 提供与微软商店交互的基础功能。 |
| `MSGamingRuntime` | 提供 GDK 运行时环境的支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了用于格式化函数的 scoped enums，该问题会导致输出乱码。 |
| 2026-04-24 | `101f2bf3` | Enable GDK ARM64 support in plugins (requires April 2026 GDK & modern folder layout) | 在插件中启用 GDK ARM64 支持，需配合 2026 年 4 月 GDK 及新版文件夹结构。 |
| 2026-04-23 | `6042fd35` | implement download cancellation for platform chunk installers, where supported | 为平台分块安装器实现了下载取消功能（在支持的情况下）。 |
| 2026-04-22 | `fde7a117` | failure to initialize the chunk installer from the manifest is now fatal | 从清单初始化分块安装器失败现在被视为致命错误。 |
| 2026-04-21 | `9335740f` | Remove a couple of unnecessary "is packaged process" checks | 移除了几处不必要的“是否为打包进程”检查。 |

### 维护评价

该插件**正在活跃维护中**。从提交记录看，自 2026 年 2 月创建以来，在 4 月份有多次重要的功能增强和问题修复，例如添加 ARM64 支持、实现下载取消、修复格式化错误和改进初始化流程。这表明 Epic 和微软正在积极为 Xbox（GDK）平台完善内容分发功能。由于它是 `IsBetaVersion: true` 且 `EnabledByDefault: false`，目前仍处于实验阶段，主要用于 Xbox 平台项目。对于面向 Xbox 平台并需要分块安装功能的项目，**推荐使用**，但需注意其 Beta 状态，可能在后续版本中有 API 变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Microsoft/GDKPackageChunkInstall)