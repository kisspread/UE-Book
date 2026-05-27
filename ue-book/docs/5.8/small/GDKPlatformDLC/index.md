# GDK Platform DLC

> Experimental support for DLC in GDK.

| 属性 | 值 |
|---|---|
| 中文名 | GDK平台DLC支持 |
| 分类 | Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GDKPlatformDLC` (RuntimeNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-06 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Microsoft/GDKPlatformDLC) | |

## 用途

本插件是 Unreal Engine 抽象的 `PlatformDLC` 插件在**微软 GDK 平台**（主要用于 Xbox 和 Windows）上的一个具体实现。它封装了微软的 `XPackage` 和 `XStore` API，为开发者提供了一套完整的、符合平台规范的 DLC 管理功能。其存在意义在于，将底层的、平台特定的商店和包管理操作，统一到引擎通用的 `IPlatformDLC` 接口之下，使得游戏逻辑可以跨平台处理 DLC。

具体而言，它解决了以下问题：
1.  **平台原生集成**：直接与 Microsoft Store 和 Xbox Live 的服务对接，处理 DLC 的查询、购买授权、下载和安装。
2.  **包生命周期管理**：管理 DLC 包的挂载 (`Mount`) 和卸载 (`Unmount`)，使其内容对游戏引擎可见。
3.  **插件化支持**：支持将 DLC 实现为 UE 插件，并自动处理插件的加载和资产注册表的合并。
4.  **状态与进度追踪**：提供统一的 API 来查询 DLC 的授权状态、下载状态、安装大小等，并支持下载和安装进度的异步监控。

## 使用场景

-   你的游戏计划在 **Xbox** 或通过 **Microsoft Store** 在 Windows 上发行，并且需要销售可下载内容（DLC），如剧情扩展包、新地图、角色皮肤等。
-   你需要一个稳定的、经过平台认证的方式去集成 Microsoft Store 的购买流程和内容交付网络。
-   你希望将 DLC 内容打包为独立的 UE 插件，以实现更好的模块化和内容管理。

## 蓝图用法

本插件的核心功能主要通过引擎标准的 `IPlatformDLC` 接口暴露。以下蓝图节点通常可通过 `Platform DLC` 类访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HasEntitlement` | 检查玩家是否拥有指定DLC的授权（已购买）。 | `IPlatformDLC` |
| `GetState` | 获取指定DLC的当前状态（如：未下载、已购买、已挂载等）。 | `IPlatformDLC` |
| `Mount` | 挂载一个已下载的DLC，使其内容对引擎可用。 | `IPlatformDLC` |
| `Unmount` | 卸载一个已挂载的DLC。 | `IPlatformDLC` |
| `Download` | 发起一个DLC的下载和安装流程。 | `IPlatformDLC` |
| `GetAllDLCNames` | 获取所有已知的DLC名称列表。 | `IPlatformDLC` |
| `GetMountedDLCNames` | 获取当前已挂载的DLC名称列表。 | `IPlatformDLC` |
| `GetStoreId` | 获取指定DLC在Microsoft Store中的SKU ID。 | `IPlatformDLC` |
| `SetStoreUser` | 设置用于商店操作（如购买）的平台用户。 | `IPlatformDLC` |

### 使用示例（蓝图描述）

1.  **检查并挂载已购买的DLC**：
    *   获取 `Platform DLC` 引用。
    *   调用 `GetAllDLCNames` 节点获取一个DLC列表。
    *   遍历列表，对每个DLC名称调用 `HasEntitlement` 节点。
    *   如果返回 `true`（已拥有），则调用 `GetState` 节点检查状态。
    *   如果状态不是“已挂载”，则调用 `Mount` 节点进行挂载。
2.  **触发购买流程**：
    *   调用 `Download` 节点并传入目标DLC的名称。插件内部会自动处理查询、弹出商店购买界面、下载和挂载的完整异步流程。

## C++ 用法

### 头文件引入

```cpp
#include "GDKPlatformDLCModule.h"
```

### 基本用法

通过模块接口获取平台 DLC 实例，并调用其核心功能。
（来源：基于 `GDKPlatformDLCModule.h` 和 `PlatformDLC` 公共接口的通用用法）

```cpp
// 获取 GDK 平台 DLC 模块实例
IGDKPlatformDLCModule& GDKDLCModule = IGDKPlatformDLCModule::Get();

// 通过模块获取实际的 DLC 管理器
TSharedPtr<IPlatformDLC> PlatformDLC = GDKDLCModule.GetPlatformDLC();

if (PlatformDLC.IsValid())
{
    // 示例：查询名为 “MyCoolHat” 的DLC状态
    FName DLCName = FName(TEXT("MyCoolHat"));
    IPlatformDLC::EState State = PlatformDLC->GetState(DLCName);

    // 检查是否已拥有
    if (PlatformDLC->HasEntitlement(DLCName))
    {
        // 如果未挂载，则尝试挂载
        if (State != IPlatformDLC::EState::Mounted)
        {
            PlatformDLC->Mount(DLCName);
        }
    }
    else
    {
        // 触发购买和下载流程
        PlatformDLC->Download(DLCName);
    }
}
```

### 进阶用法

设置商店用户以处理多账户情况，这对于家庭主机上的用户切换至关重要。

```cpp
// 假设你已通过其他方式获得了有效的 FPlatformUserId
FPlatformUserId UserId = /* ... */;

if (PlatformDLC.IsValid())
{
    // 设置当前用于商店操作的用户
    PlatformDLC->SetStoreUser(UserId);

    // 之后所有的购买、授权查询都将以此用户身份进行
    PlatformDLC->Download(FName(TEXT("SeasonPass")));
}
```

## Demo 示例

一个最小的示例，展示如何在 Actor 中集成对 GDK 平台 DLC 的基本查询。

**DLCManagerActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PlatformDLC.h" // 引入平台DLC接口
#include "DLCManagerActor.generated.h"

UCLASS()
class ADLCManagerActor : public AActor
{
    GENERATED_BODY()

public:
    ADLCManagerActor();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "DLC")
    void QueryDLCStatus();

protected:
    UPROPERTY(VisibleAnywhere, Category = "DLC")
    TScriptInterface<IPlatformDLC> PlatformDLC;
};
```

**DLCManagerActor.cpp**
```cpp
#include "DLCManagerActor.h"
#include "GDKPlatformDLCModule.h"

ADLCManagerActor::ADLCManagerActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ADLCManagerActor::BeginPlay()
{
    Super::BeginPlay();

    // 在 BeginPlay 中尝试获取平台 DLC 实例
    // 注意：在 GDK 平台插件显式加载前，这可能会返回空接口
    if (IGDKPlatformDLCModule::IsAvailable())
    {
        IGDKPlatformDLCModule& Module = IGDKPlatformDLCModule::Get();
        TSharedPtr<IPlatformDLC> DLC = Module.GetPlatformDLC();
        PlatformDLC = DLC;
    }
}

void ADLCManagerActor::QueryDLCStatus()
{
    if (!PlatformDLC)
    {
        UE_LOG(LogTemp, Warning, TEXT("PlatformDLC is not available."));
        return;
    }

    TArray<FName> AllDLC = PlatformDLC->GetAllDLCNames();
    for (const FName& Name : AllDLC)
    {
        bool bOwned = PlatformDLC->HasEntitlement(Name);
        IPlatformDLC::EState CurrentState = PlatformDLC->GetState(Name);
        uint64 CurrentSize = 0, TotalSize = 0;
        PlatformDLC->GetDownloadSize(Name, CurrentSize, TotalSize);

        UE_LOG(LogTemp, Log, TEXT("DLC: %s, Owned: %s, State: %s, Size: %llu/%llu"),
            *Name.ToString(),
            bOwned ? TEXT("Yes") : TEXT("No"),
            *UEnum::GetValueAsString(CurrentState),
            CurrentSize,
            TotalSize);
    }
}
```

## 模块依赖

本插件是 `PlatformDLC` 核心插件的一个平台实现，因此强依赖于它。

| 模块 | 用途 |
|---|---|
| `PlatformDLC` | 提供平台无关的 DLC 抽象接口 (`IPlatformDLC`, `IPlatformDLCFactoryModule`)。 |

此外，本插件的构建隐式依赖于微软 GDK 的运行时库（如 `XPackage`, `XStore`），这些通过平台 SDK 和构建工具链集成，无需在游戏模块的 Build.cs 中额外声明。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `75d56ac2` | Add functionality to change the store user for platform DLC | 新增运行时动态切换商店用户的功能，以处理多账户场景。 |
| 2026-05-12 | `8af8138d` | GDK platform DLC will find the next available user for store purchasing if the current user signs out | 改进用户处理逻辑：当前用户登出时，自动选择下一个可用用户进行商店购买。 |
| 2026-05-12 | `b791ab2c` | fix potential thead safety issues | 修复了潜在的线程安全问题，提升了多线程环境下的稳定性。 |
| 2026-05-12 | `40898050` | Add asynchronous initialization for Platform DLC | 为平台DLC添加了异步初始化流程，避免阻塞主线程。 |
| 2026-05-01 | `9f6036e6` | Add IPlatformDLC function to query the state of a DLC. | 在公共接口中新增了查询DLC状态的功能函数。 |

### 维护评价

-   **活跃维护**：尽管是实验性插件（`IsBetaVersion=true`，`EnabledByDefault=false`），但从近期提交记录（2026年5月）来看，正处于**非常活跃的开发与维护期**。
-   **功能迭代**：近期提交不仅修复了线程安全等底层问题，还增加了新的公共功能（如动态切换用户、异步初始化），表明其功能正在快速完善。
-   **实验性警告**：该插件明确标记为实验性，且默认禁用。其API和实现细节在未来版本中可能发生**不兼容的变更**。
-   **平台限制**：目前仅支持 `Win64` 平台。对于Xbox平台的支持可能通过其他配置或插件变体实现。
-   **推荐使用**：如果你的项目**明确且必须**集成 Microsoft Store 的 DLC 功能，并且能够接受实验性插件可能带来的稳定性和兼容性风险，那么可以启用并试用此插件。建议密切关注其版本更新日志。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Microsoft/GDKPlatformDLC)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Microsoft/GDKPlatformDLC/Tests) (如果存在)