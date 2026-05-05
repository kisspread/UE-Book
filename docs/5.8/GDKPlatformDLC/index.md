# DLC Support for GDK

> Experimental support for DLC in GDK.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GDKPlatformDLC` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Microsoft/GDKPlatformDLC) | |

## 用途

该插件为微软 GDK 平台（主要用于 Xbox 开发）提供了 DLC（可下载内容）的完整管理功能。它实现了 `IPlatformDLC` 接口，专门处理在 GDK 环境下 DLC 的下载、安装、挂载、卸载、权限验证以及状态查询等操作。其存在是为了解决在 Xbox 平台上集成 DLC 功能时，需要与微软的 XPackage 和 XStore 等原生 API 进行交互的复杂性，为开发者提供一个统一的、引擎级别的抽象层。

## 使用场景

- 你正在使用 GDK（Game Development Kit）为 Xbox 平台开发游戏，并且需要销售和管理可下载内容（如新地图、角色、剧情章节）。
- 你需要一个标准化的接口来检查玩家是否拥有某个 DLC 的权限、触发 DLC 的下载与安装、以及将已安装的 DLC 内容挂载到游戏文件系统中。
- 你的游戏需要支持 DLC 的动态加载和卸载，并希望获得统一的状态通知。

## 蓝图用法

该插件主要提供 C++ 接口，蓝图可访问的功能通过 `IPlatformDLC` 接口暴露。核心操作通过获取平台 DLC 管理器实例来完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPlatformDLC` | 获取当前 GDK 平台的 DLC 管理器实例 | `IGDKPlatformDLCModule` |
| `HasEntitlement` | 检查玩家是否拥有指定 DLC 的权限 | `IPlatformDLC` |
| `IsMounted` | 检查指定 DLC 是否已挂载到文件系统 | `IPlatformDLC` |
| `IsDownloaded` | 检查指定 DLC 是否已下载完成 | `IPlatformDLC` |
| `Download` | 触发指定 DLC 的下载 | `IPlatformDLC` |
| `Mount` | 挂载已下载的 DLC 内容 | `IPlatformDLC` |
| `Unmount` | 卸载已挂载的 DLC 内容 | `IPlatformDLC` |
| `GetAllDLCNames` | 获取所有已知的 DLC 名称列表 | `IPlatformDLC` |
| `GetMountedDLCNames` | 获取所有已挂载的 DLC 名称列表 | `IPlatformDLC` |
| `GetDownloadSize` | 获取 DLC 的下载大小和安装大小 | `IPlatformDLC` |
| `GetRootDirectory` | 获取已挂载 DLC 内容的根目录路径 | `IPlatformDLC` |
| `OnNotification` | 获取 DLC 状态变化（如下载完成、挂载成功）的委托 | `IPlatformDLC` |

### 使用示例（蓝图描述）

1.  **获取 DLC 管理器**：在游戏初始化时，调用 `IGDKPlatformDLCModule::Get().GetPlatformDLC()` 获取 `IPlatformDLC` 接口的共享指针，并将其存储为变量。
2.  **检查并下载 DLC**：当玩家尝试访问某个 DLC 内容时，首先调用 `HasEntitlement` 检查权限。如果拥有权限但未下载，调用 `Download` 启动下载。
3.  **监听状态变化**：绑定 `OnNotification` 委托。在委托回调中，根据通知类型（`ENotification`）和成功状态（`bSuccess`）更新 UI，例如显示下载进度或提示“DLC 已就绪”。
4.  **挂载 DLC**：在收到下载成功的通知后，调用 `Mount` 将 DLC 内容挂载。挂载成功后，即可通过 `GetRootDirectory` 获取路径来加载 DLC 中的资产。

## C++ 用法

### 头文件引入

```cpp
#include "GDKPlatformDLCModule.h"
```

### 基本用法

获取 DLC 管理器并查询状态。
（来源：基于 `IGDKPlatformDLCModule` 和 `IPlatformDLC` 接口定义）

```cpp
// 获取 GDK 平台 DLC 模块实例
IGDKPlatformDLCModule& GDKDLCModule = IGDKPlatformDLCModule::Get();

// 获取平台 DLC 管理器
TSharedPtr<IPlatformDLC> PlatformDLC = GDKDLCModule.GetPlatformDLC();

if (PlatformDLC.IsValid())
{
    // 检查玩家是否拥有名为 “MapPack1” 的 DLC
    FName DLCName = FName(TEXT("MapPack1"));
    bool bHasEntitlement = PlatformDLC->HasEntitlement(DLCName);

    if (bHasEntitlement)
    {
        // 检查是否已下载
        bool bIsDownloaded = PlatformDLC->IsDownloaded(DLCName);
        if (!bIsDownloaded)
        {
            // 触发下载
            PlatformDLC->Download(DLCName);
        }
        else
        {
            // 检查是否已挂载
            bool bIsMounted = PlatformDLC->IsMounted(DLCName);
            if (!bIsMounted)
            {
                // 挂载 DLC
                PlatformDLC->Mount(DLCName);
            }
            // 获取挂载后的根目录
            FString DLCRootPath = PlatformDLC->GetRootDirectory(DLCName);
            UE_LOG(LogTemp, Log, TEXT("DLC %s mounted at: %s"), *DLCName.ToString(), *DLCRootPath);
        }
    }
}
```

### 进阶用法

监听 DLC 事件并处理状态变化。
（来源：基于 `FOnDLCNotification` 委托和 `ENotification` 枚举）

```cpp
// 假设在某个 Actor 或 GameInstance 中
void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    if (TSharedPtr<IPlatformDLC> PlatformDLC = IGDKPlatformDLCModule::Get().GetPlatformDLC())
    {
        // 绑定通知委托
        PlatformDLC->OnNotification().AddUObject(this, &AMyGameMode::HandleDLCNotification);
    }
}

void AMyGameMode::HandleDLCNotification(FName DLCName, ENotification Notification, bool bSuccess)
{
    switch (Notification)
    {
    case ENotification::DownloadComplete:
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("DLC %s download completed."), *DLCName.ToString());
            // 下载完成后自动挂载
            if (TSharedPtr<IPlatformDLC> PlatformDLC = IGDKPlatformDLCModule::Get().GetPlatformDLC())
            {
                PlatformDLC->Mount(DLCName);
            }
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("DLC %s download failed."), *DLCName.ToString());
        }
        break;
    case ENotification::MountComplete:
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("DLC %s mounted successfully."), *DLCName.ToString());
            // 通知游戏逻辑 DLC 已就绪
            OnDLCReady(DLCName);
        }
        break;
    // 处理其他通知类型...
    }
}
```

## Demo 示例

一个最小化的示例，展示如何在 Actor 中初始化和使用 GDK DLC 管理器。

**MyDLCManagerActor.h**
```cpp
// MyDLCManagerActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PlatformDLC.h" // 引入 IPlatformDLC 接口
#include "MyDLCManagerActor.generated.h"

UCLASS()
class MYGAME_API AMyDLCManagerActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDLCManagerActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    // DLC 管理器实例
    TSharedPtr<IPlatformDLC> PlatformDLC;

    // 通知回调
    void OnDLCNotification(FName DLCName, ENotification Notification, bool bSuccess);

    // 示例：尝试获取并挂载一个 DLC
    void TryMountDLC(FName DLCName);
};
```

**MyDLCManagerActor.cpp**
```cpp
// MyDLCManagerActor.cpp
#include "MyDLCManagerActor.h"
#include "GDKPlatformDLCModule.h"

AMyDLCManagerActor::AMyDLCManagerActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDLCManagerActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 获取 GDK 平台 DLC 模块
    IGDKPlatformDLCModule& GDKModule = IGDKPlatformDLCModule::Get();

    // 2. 获取平台 DLC 管理器
    PlatformDLC = GDKModule.GetPlatformDLC();

    if (PlatformDLC.IsValid())
    {
        // 3. 绑定状态通知
        PlatformDLC->OnNotification().AddUObject(this, &AMyDLCManagerActor::OnDLCNotification);

        // 4. 示例：尝试挂载名为 “BonusContent” 的 DLC
        TryMountDLC(FName(TEXT("BonusContent")));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to get GDK Platform DLC manager."));
    }
}

void AMyDLCManagerActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (PlatformDLC.IsValid())
    {
        PlatformDLC->OnNotification().RemoveAll(this);
    }
    Super::EndPlay(EndPlayReason);
}

void AMyDLCManagerActor::OnDLCNotification(FName DLCName, ENotification Notification, bool bSuccess)
{
    if (Notification == ENotification::MountComplete && bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("DLC '%s' is now mounted and ready!"), *DLCName.ToString());
        // 在这里可以加载 DLC 中的特定资产
    }
}

void AMyDLCManagerActor::TryMountDLC(FName DLCName)
{
    if (!PlatformDLC.IsValid()) return;

    if (PlatformDLC->HasEntitlement(DLCName))
    {
        if (PlatformDLC->IsDownloaded(DLCName))
        {
            if (!PlatformDLC->IsMounted(DLCName))
            {
                PlatformDLC->Mount(DLCName);
            }
        }
        else
        {
            UE_LOG(LogTemp, Log, TEXT("DLC '%s' is not downloaded. Starting download..."), *DLCName.ToString());
            PlatformDLC->Download(DLCName);
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("User does not have entitlement for DLC '%s'."), *DLCName.ToString());
    }
}
```

## 模块依赖

从 Build.cs 分析，该插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `PlatformDLC` | 提供跨平台的 DLC 管理抽象接口 (`IPlatformDLC`, `IPlatformDLCFactoryModule`)，是本插件实现的基础。 |
| `GDKRuntime` | 提供 GDK 平台的运行时支持，包括与微软 XDK/Xbox 服务交互的底层功能。 |

## 维护状态

### 近期更新

- 2026-04-24 `101f2bf3` 在插件中启用 GDK ARM64 支持（需要 2026 年 4 月版 GDK 及现代文件夹布局）。
- 2026-04-22 `c4a59235` 当用户请求重新下载一个已在下载中的 DLC 时，将其优先级提升。
- 2026-04-21 `9335740f` 移除了几处不必要的“是否为打包进程”检查。
- 2026-04-20 `8e8e104d` 修复 DLC 挂载路径与资产注册表加载逻辑，以统一控制台与 PC GDK 平台的行为。
- 2026-04-17 `6c63b6ce` 在 GDK 平台 DLC 中添加购买功能。

### 维护评价

该插件处于**活跃维护**状态。近一周内提交频繁，内容涵盖了新功能开发（ARM64支持、DLC购买）、用户体验优化（下载优先级）以及重要的平台一致性修复，表明团队正在积极迭代和完善此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Microsoft/GDKPlatformDLC)
- [官方文档]() （暂无）
- [测试用例]() （插件目录内未发现标准测试文件）