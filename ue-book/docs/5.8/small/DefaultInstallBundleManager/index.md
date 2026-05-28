# Default Install Bundle Manager

> Default engine handler for downloading, patching, and mounting content bundles while the game is running.

| 属性 | 值 |
|---|---|
| 中文名 | 默认安装包管理器 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DefaultInstallBundleManager` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-05-11 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DefaultInstallBundleManager) | |

## 用途

本插件提供 `IInstallBundleManager` 接口的默认引擎实现（`FDefaultInstallBundleManager`），用于在游戏运行时管理内容包（Bundle）的下载、补丁、挂载和卸载生命周期。

它的核心解决的问题是：大型游戏（特别是手游和主机平台游戏）需要将内容分拆为多个可独立下载和管理的包（Bundle），在运行时按需下载、缓存、挂载和卸载。本插件协调多种内容源（平台 Chunk 安装、DLC、Bulk/IoStore 按需内容），统一管理这些 Bundle 的状态机（`NotInstalled` → `NeedsUpdate` → `NeedsMount` → `Mounted`），并处理缓存淘汰、Shader PSO 缓存等待、分析上报等复杂逻辑。

插件本身默认禁用（`EnabledByDefault=false`），且标记为实验性。它依赖 `OnlineSubsystem`、`OnlineFramework`、`PlatformDLC` 等插件，适用于需要运行时内容管理的商业游戏项目。

## 使用场景

- 你的游戏需要按需下载关卡/角色皮肤等附加内容 → 使用本插件管理 Bundle 的下载和挂载
- 你需要在游戏运行时动态补丁内容而不需要重启客户端 → 本插件提供完整的运行时补丁流程
- 你的游戏需要支持多种内容分发渠道（DLC、IoStore 按需、Chunk 安装）→ 本插件的多 Bundle Source 架构统一管理
- 你需要缓存管理策略（LRU 淘汰、缓存预留）来优化磁盘使用 → 本插件内置缓存系统
- 你需要详细的分析数据来监控内容下载/安装性能 → 本插件集成了完整的 Analytics 事件

## 蓝图用法

本插件为纯 C++ Runtime 模块，不暴露 BlueprintCallable 节点。所有操作通过 C++ API 进行。

## C++ 用法

### 头文件引入

```cpp
#include "DefaultInstallBundleManager.h"
```

### 基本用法

本插件的核心类 `FDefaultInstallBundleManager` 实现了 `IInstallBundleManager` 接口。以下为基本初始化和 Bundle 请求流程。

*（基于 `Source/Public/DefaultInstallBundleManager.h` 中的类定义）*

```cpp
// 创建 Bundle 管理器，可选传入自定义 Bundle Source 工厂
FDefaultInstallBundleManager BundleManager;

// 初始化管理器（异步过程，包含多个步骤：初始化 Bundle Sources、缓存、查询 Bundle 信息等）
BundleManager.Initialize();

// 请求下载/更新一个 Bundle
// 通过 IInstallBundleManager 接口调用，需要传入 Bundle 名称、标志位和完成回调
// Bundle 名称需要在 InstallBundle.ini 配置中预定义
FName BundleName = TEXT("MyGame_Maps_Chapter1");
EInstallBundleRequestFlags RequestFlags = EInstallBundleRequestFlags::None;

// 请求更新内容（异步操作）
// RequestUpdateContent 会经历以下状态机步骤：
//   ReservingCache → FinishingCache → UpdatingBundleSources → Mounting → WaitingForShaderCache → Finishing
// 管理器会自动处理缓存预留、源更新、Pak 挂载、Shader 预编译等待等
BundleManager.RequestUpdateContent(BundleName, RequestFlags, 
    FInstallBundleCompleteDelegate::CreateLambda([](FName BundleName, EInstallBundleResult Result)
    {
        if (Result == EInstallBundleResult::OK)
        {
            UE_LOG(LogTemp, Log, TEXT("Bundle %s 已就绪"), *BundleName.ToString());
        }
    }));
```

### 查询 Bundle 内容状态

```cpp
// 查询指定 Bundle 的内容状态（是否已安装、是否需要更新等）
TArray<FName> BundleNames = { TEXT("MyGame_Maps_Chapter1"), TEXT("MyGame_Characters") };
EInstallBundleGetContentStateFlags ContentStateFlags = EInstallBundleGetContentStateFlags::None;

BundleManager.GetContentState(BundleNames, ContentStateFlags,
    FInstallBundleGetContentStateDelegate::CreateLambda([](FInstallBundleCombinedContentState ContentState)
    {
        // ContentState 包含每个 Bundle 的安装/更新/挂载状态
        for (const auto& Pair : ContentState.States)
        {
            UE_LOG(LogTemp, Log, TEXT("Bundle %s - State: %d"), 
                *Pair.Key.ToString(), static_cast<int32>(Pair.Value));
        }
    }));
```

### 释放 Bundle 内容

```cpp
// 释放/卸载一个 Bundle（卸载 Pak 并可选清理磁盘文件）
BundleManager.RequestReleaseContent(BundleName,
    EInstallBundleReleaseRequestFlags::None,
    FInstallBundleRemovedDelegate::CreateLambda([](FName BundleName, EInstallBundleReleaseResult Result)
    {
        if (Result == EInstallBundleReleaseResult::OK)
        {
            UE_LOG(LogTemp, Log, TEXT("Bundle %s 已释放"), *BundleName.ToString());
        }
    }));
```

### 取消 Bundle 操作

```cpp
// 取消正在进行的 Bundle 操作
BundleManager.CancelBundles(BundleName);
```

### 进阶用法

#### 缓存管理

*（基于 `Source/Public/DefaultInstallBundleManager.h` 中 `FCacheFlushRequest` 结构）*

```cpp
// 刷新指定 Bundle Source 的缓存，淘汰不活跃的 Bundle 内容
// 可通过 FInstallBundleSourceOrCache 指定特定源或所有缓存
// 清理完成后通过回调通知
BundleManager.FlushBundleCache(SourceOrCache,
    FInstallBundleManagerFlushCacheCompleteDelegate::CreateLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("缓存清理完成"));
    }));
```

#### 自定义 Bundle Source 工厂

*（基于 `Source/Public/DefaultInstallBundleManager.h` 中 `FInstallBundleSourceFactoryFunction` 类型定义）*

```cpp
// 创建管理器时传入自定义的 Bundle Source 工厂函数
// 用于在不修改引擎代码的情况下注入自定义内容源
FDefaultInstallBundleManager::FInstallBundleSourceFactoryFunction Factory =
    [](FInstallBundleSourceType Type) -> TSharedPtr<IInstallBundleSource>
    {
        if (Type == FInstallBundleSourceType::Bulk)
        {
            return MakeShared<FInstallBundleSourceBulk>();
        }
        // 返回 nullptr 表示使用默认源
        return nullptr;
    };

FDefaultInstallBundleManager BundleManager(Factory);
BundleManager.Initialize();
```

#### 获取 Bundle 进度

*（基于 `Source/Public/InstallBundleSourcePlatformDLC.h` 中 `GetBundleProgress` 实现）*

```cpp
// 查询 Bundle 的下载/安装进度
TOptional<FInstallBundleSourceProgress> Progress = BundleManager.GetBundleProgress(BundleName);
if (Progress.IsSet())
{
    float Percent = Progress.GetValue().Percent;
    UE_LOG(LogTemp, Log, TEXT("Bundle 下载进度: %.1f%%"), Percent * 100.0f);
}
```

## Demo 示例

以下示例展示如何创建一个简单的 Bundle 管理器并请求内容更新。

**BundleManagerDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DefaultInstallBundleManager.h"

class FBundleManagerDemo
{
public:
    void Initialize();
    void RequestBundle(FName BundleName);
    void ReleaseBundle(FName BundleName);
    void QueryBundleState(const TArray<FName>& BundleNames);

private:
    TUniquePtr<FDefaultInstallBundleManager> BundleManager;
    bool bInitialized = false;
};
```

**BundleManagerDemo.cpp**
```cpp
#include "BundleManagerDemo.h"

void FBundleManagerDemo::Initialize()
{
    BundleManager = MakeUnique<FDefaultInstallBundleManager>();
    BundleManager->Initialize();
    bInitialized = true;
}

void FBundleManagerDemo::RequestBundle(FName BundleName)
{
    if (!bInitialized || !BundleManager.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("BundleManager 未初始化"));
        return;
    }

    BundleManager->RequestUpdateContent(
        BundleName,
        EInstallBundleRequestFlags::None,
        FInstallBundleCompleteDelegate::CreateLambda(
            [](FName Name, EInstallBundleResult Result)
            {
                if (Result == EInstallBundleResult::OK)
                {
                    UE_LOG(LogTemp, Log, TEXT("Bundle '%s' 请求成功"), *Name.ToString());
                }
                else
                {
                    UE_LOG(LogTemp, Error, TEXT("Bundle '%s' 请求失败: %d"), 
                        *Name.ToString(), static_cast<int32>(Result));
                }
            })
    );
}

void FBundleManagerDemo::ReleaseBundle(FName BundleName)
{
    if (!bInitialized || !BundleManager.IsValid())
    {
        return;
    }

    BundleManager->RequestReleaseContent(
        BundleName,
        EInstallBundleReleaseRequestFlags::None,
        FInstallBundleRemovedDelegate::CreateLambda(
            [](FName Name, EInstallBundleReleaseResult Result)
            {
                UE_LOG(LogTemp, Log, TEXT("Bundle '%s' 释放结果: %d"),
                    *Name.ToString(), static_cast<int32>(Result));
            })
    );
}

void FBundleManagerDemo::QueryBundleState(const TArray<FName>& BundleNames)
{
    if (!bInitialized || !BundleManager.IsValid())
    {
        return;
    }

    BundleManager->GetContentState(
        BundleNames,
        EInstallBundleGetContentStateFlags::None,
        FInstallBundleGetContentStateDelegate::CreateLambda(
            [](FInstallBundleCombinedContentState ContentState)
            {
                UE_LOG(LogTemp, Log, TEXT("查询到 %d 个 Bundle 的状态"), 
                    ContentState.States.Num());
            })
    );
}
```

## 模块依赖

本插件以插件形式依赖以下插件（均需启用）：

| 插件 | 用途 |
|---|---|
| `OnlineSubsystem` | 提供在线服务基础设施 |
| `OnlineFramework` | 提供 `IInstallBundleManager` / `IInstallBundleSource` 核心接口 |
| `PlatformDLC` | 提供平台 DLC 内容源支持 |

本模块的内部代码还引用了以下模块（需在你的 Build.cs 中声明依赖）：

| 模块 | 用途 |
|---|---|
| `IoStoreUtilities` | IoStore 按需内容加载支持（`UE::IoStore` 命名空间） |
| `AnalyticsET` | 分析事件上报（`IAnalyticsProviderET`） |

> 若仅使用基础 Bundle 管理功能，核心依赖为 `OnlineFramework` 和 `OnlineSubsystem`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `c8d4db69` | [PlatformDLC] Requests for operations already in progress now invoke callbacks when operation finish | 修复 DLC 源中重复请求的回调问题 |
| 2026-05-12 | `75d56ac2` | Add functionality to change the store user for platform DLC | 支持切换 DLC 商店用户身份 |
| 2026-05-12 | `40898050` | Add asynchronous initialization for Platform DLC | 为 DLC 源添加异步初始化支持 |
| 2026-05-12 | `fe06fcd0` | [PlatformDLC] Add support for using a fallback bundle source. | DLC 源支持后备内容源回退 |
| 2026-05-01 | `9f6036e6` | Add IPlatformDLC function to query the state of a DLC. | 新增 DLC 状态查询接口 |

### 维护评价

本插件仍处于**活跃维护**状态。2026 年 5 月连续有多次功能性更新，主要集中在 `PlatformDLC` Bundle Source 的增强：异步初始化、多用户支持、后备源、以及回调修复。这些改动表明 Epic 正在将此插件从实验性功能推向生产可用。

**注意事项**：
- 标记为实验性（位于 `Experimental` 目录），API 可能在未来版本发生变化
- 默认禁用（`EnabledByDefault=false`），需手动在项目配置中启用
- 依赖 `OnlineSubsystem` 和 `OnlineFramework` 等插件，项目需具备在线服务基础设施
- 5.4 版本中已废弃 `GInstallBundleManagerIni` 配置方式，改用 `InstallBundle.ini` 层级配置
- 适用于需要运行时内容管理的大型商业项目，不适合简单原型项目

**推荐使用**：✅ 如果你的项目需要运行时 Bundle 管理功能，本插件是引擎提供的官方实现，建议作为开发起点。但仍需注意其实验性状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DefaultInstallBundleManager)
- 测试用例：本插件目录内未发现独立测试文件