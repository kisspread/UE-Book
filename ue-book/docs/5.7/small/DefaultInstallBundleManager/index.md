# Default Install Bundle Manager

> Default engine handler for downloading, patching, and mounting content bundles while the game is running.

| 属性 | 值 |
|---|---|
| 中文名 | 默认安装包管理器 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DefaultInstallBundleManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DefaultInstallBundleManager) | |

---

## 用途

`DefaultInstallBundleManager` 是 UE5 运行时安装包（Install Bundle）管理系统的默认实现。它将游戏内容划分为多个逻辑 Bundle（包组），并在游戏运行期间动态下载、修补和挂载这些内容。该插件主要用于解决大型游戏（尤其是移动端和分步下载游戏）的内容分发问题：

- 支持游戏在运行中后台下载新的资源包，无需重启或重新打包。
- 支持增量更新，仅下载变化的部分。
- 与平台特定的安装源（如 Google Play Asset Delivery、Apple On Demand Resources）集成，统一管理不同渠道的内容获取。
- 提供缓存管理与持久化统计，便于追踪下载进度和性能。

---

## 使用场景

- **分步下载游戏**：玩家先下载核心包，游戏开始后后台下载后续资源（如关卡、语音包、材质包）。
- **移动端热更新**：通过 Google Play / Apple 平台的分包机制，运行时下载新内容。
- **大型 PC 游戏**：启动时仅加载必要内容，后续按需流式加载或下载大型资源包。
- **多语言/多地区支持**：不同地区下载不同语言包，根据用户设置动态挂载。

---

## 蓝图用法

该插件不直接暴露蓝图函数节点。其功能通过 `IInstallBundleManager` 接口和引擎子系统 `UInstallBundleManagerSubsystem` 暴露给蓝图（需要配合 `InstallBundleManager` 模块使用）。以下为蓝图可调用的常用接口（需链接 `InstallBundleManager` 模块）。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RequestUpdateContent` | 请求下载/更新指定 Bundle 的内容 | `IInstallBundleManager` |
| `GetContentState` | 查询指定 Bundle 的当前内容状态 | `IInstallBundleManager` |
| `ReleaseContent` | 释放指定 Bundle 的内容（卸载/清理） | `IInstallBundleManager` |
| `GetInstallBundleManager` | 获取全局安装包管理器实例（蓝图节点） | `UInstallBundleManagerSubsystem` |

> 注意：`DefaultInstallBundleManager` 是 `IInstallBundleManager` 接口的默认实现类，蓝图通过子系统间接使用其功能。若要直接使用 C++ 接口，请参考下文。

---

## C++ 用法

### 头文件引入

```cpp
#include "DefaultInstallBundleManager.h"
#include "InstallBundleManagerInterface.h"
```

### 基本用法

获取全局管理器实例（通常在游戏实例或子系统初始化时调用）：

```cpp
// 获取安装包管理器
IInstallBundleManager* BundleManager = IInstallBundleManager::Get();
if (BundleManager)
{
    // 管理器已就绪
}
```

请求更新指定 Bundle（如 "HighQualityTextures"）：

```cpp
TArray<FName> BundlesToUpdate;
BundlesToUpdate.Add("HighQualityTextures");

FInstallBundleCompleteDelegate OnComplete;
OnComplete.BindLambda([](const FInstallBundleCompletedInfo& Info)
{
    if (Info.bSuccess)
    {
        // Bundle 下载并挂载完成
    }
});

// 请求更新
BundleManager->RequestUpdateContent(BundlesToUpdate, OnComplete, EInstallBundlePriority::Normal);
```

查询 Bundle 内容状态：

```cpp
TArray<FName> BundleNames = { "CoreAssets", "AudioPack" };
BundleManager->GetContentState(BundleNames, EInstallBundleGetContentStateFlags::None,
    FInstallBundleGetContentStateDelegate::CreateLambda(
        [](const FInstallBundleCombinedContentState& State)
        {
            for (const auto& Pair : State.BundleStates)
            {
                // Pair.Key: Bundle 名称
                // Pair.Value.State: 包括 NotInstalled, NeedsUpdate, NeedsMount, Mounted 等
            }
        }));
```

### 进阶用法

配置自定义安装源（如使用平台 Chunk Install）：

```cpp
// 在自定义游戏模块初始化时，可注册自定义安装源
// 例如使用 FInstallBundleSourcePlatformChunkInstall 封装平台层 chunk install
TSharedPtr<IInstallBundleSource> PlatformSource = MakeShared<FInstallBundleSourcePlatformChunkInstall>(FPlatformChunkInstall::Get());
// 然后将 PlatformSource 注册到 FDefaultInstallBundleManager 中...
// （具体注册方式需查看源码实现）
```

---

## Demo 示例

以下是一个最小示例，展示如何在游戏启动后使用 `DefaultInstallBundleManager` 请求更新指定 Bundle。假设场景：玩家首次启动时核心包已存在，需要额外下载高清纹理包。

**MyInstallBundleHandler.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "InstallBundleManagerInterface.h"
#include "InstallBundleTypes.h"

class FMyInstallBundleHandler
{
public:
    void Init();
    void RequestHighResTextures();

private:
    void OnBundleUpdated(const FInstallBundleCompletedInfo& Info);
    void OnContentStateReceived(const FInstallBundleCombinedContentState& State);
};
```

**MyInstallBundleHandler.cpp**

```cpp
#include "MyInstallBundleHandler.h"
#include "DefaultInstallBundleManager.h"

void FMyInstallBundleHandler::Init()
{
    IInstallBundleManager* BundleManager = IInstallBundleManager::Get();
    if (!BundleManager)
    {
        UE_LOG(LogTemp, Warning, TEXT("InstallBundleManager not available"));
        return;
    }

    // 首先查询 TEXTURE_HIGH 状态
    TArray<FName> QueryNames = { "TEXTURE_HIGH" };
    BundleManager->GetContentState(QueryNames, EInstallBundleGetContentStateFlags::None,
        FInstallBundleGetContentStateDelegate::CreateRaw(this, &FMyInstallBundleHandler::OnContentStateReceived));
}

void FMyInstallBundleHandler::OnContentStateReceived(const FInstallBundleCombinedContentState& State)
{
    const auto* BundleState = State.BundleStates.Find("TEXTURE_HIGH");
    if (!BundleState) return;

    switch (BundleState->State)
    {
    case EInstallBundleInstallState::NotInstalled:
    case EInstallBundleInstallState::NeedsUpdate:
        RequestHighResTextures();
        break;
    case EInstallBundleInstallState::Mounted:
        // 已经就绪，可以直接使用
        break;
    }
}

void FMyInstallBundleHandler::RequestHighResTextures()
{
    IInstallBundleManager* BundleManager = IInstallBundleManager::Get();
    if (!BundleManager) return;

    TArray<FName> Bundles = { "TEXTURE_HIGH" };
    FInstallBundleCompleteDelegate OnComplete;
    OnComplete.BindRaw(this, &FMyInstallBundleHandler::OnBundleUpdated);

    BundleManager->RequestUpdateContent(Bundles, OnComplete, EInstallBundlePriority::High);
}

void FMyInstallBundleHandler::OnBundleUpdated(const FInstallBundleCompletedInfo& Info)
{
    if (Info.BundleName == "TEXTURE_HIGH" && Info.bSuccess)
    {
        // 高清纹理已挂载，可以加载相关资源
        // 例如：StreamableManager.RequestAsyncLoad(...)
    }
}
```

---

## 模块依赖

使用 `DefaultInstallBundleManager` 的模块需要添加以下依赖（已省略标准 Engine 模块）：

| 模块 | 用途 |
|---|---|
| `InstallBundleManager` | 提供 `IInstallBundleManager` 接口、基础类型和子系统 |
| `UnifiedError` | 统一错误处理（Experimental） |
| `Json` | 序列化/反序列化构建元数据（`FContentBuildMetaData`） |
| `AnalyticsET` | 可选的统计上报（通过 `IAnalyticsProviderET`） |

> 注意：该插件本身仅包含对 `InstallBundleManager` 模块的实现，实际使用时请确保项目已启用 `InstallBundleManager` 插件（默认开启）。

---

## 维护状态

### 近期更新

| 日期 | Commit | 解读 |
|---|---|---|
| 2025-09-23 | `ef286680` | [InstallBundle] 允许仅更新请求的 Bundle，禁止为 OptionalContent 加载依赖 |
| 2025-09-12 | `ce6ff392` | 修复忽略返回值的 “nodiscard” 警告 |
| 2025-09-11 | `1c4d128c` | 重新实现 `UI.LoadToLobbyReport` 的 `bSpentTimeDownloading` 属性 |
| 2025-09-04 | `a593b616` | 增加 InstallBundleManager.CDN.ResponseTime 事件 |
| 2025-09-01 | `180658cc` | 修复 API 宏 |

### 维护评价

- **创建时间**：2025-09-01（约 1 个月前）
- **近期更新**：频繁，且包含功能新增和修复
- **活跃度**：处于 **活跃维护** 状态
- **已知问题**：无特别标注
- **推荐程度**：作为默认安装包管理器实现，如果项目需要运行时 Bundle 下载与管理，推荐使用。但插件仍处于 Experimental 分类，可能尚未完全稳定，建议关注更新日志。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DefaultInstallBundleManager)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/install-bundle-manager-in-unreal-engine/)（InstallBundleManager 系统文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DefaultInstallBundleManager/Source/DefaultInstallBundleManager.Tests)（若存在）