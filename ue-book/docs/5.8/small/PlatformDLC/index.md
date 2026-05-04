# Platform DLC

> Experimental support for native platform DLC (on supported platforms)

| 属性 | 值 |
|---|---|
| 分类 | Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PlatformDLC` (RuntimeNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlatformDLC) | |

## 用途

PlatformDLC 插件旨在为 Unreal Engine 提供一个统一的、跨平台的 DLC（可下载内容）管理抽象层。它解决了在不同游戏平台（如 Steam、Epic Games Store、PlayStation、Xbox 等）上处理 DLC 的复杂性，为开发者提供了一套标准化的 API 来查询、下载、挂载、卸载和管理 DLC 内容。其核心价值在于将平台特定的 DLC 实现细节封装起来，使游戏逻辑能够以平台无关的方式与 DLC 交互。此外，它通过自定义的 `IPlatformFile` 实现，将 DLC 内容无缝集成到引擎的虚拟文件系统中，使得游戏可以像访问本地资产一样访问 DLC 中的文件。

## 使用场景

- 你的游戏需要在多个发行平台（PC、主机）上销售和管理 DLC 内容。
- 你需要动态地加载或卸载游戏内容（如新地图、角色、任务包），而无需重启游戏。
- 你希望游戏代码能够统一地检查玩家是否拥有某个 DLC 的权限（Entitlement），并根据状态执行相应逻辑。
- 你需要获取 DLC 的下载大小信息，以便向玩家展示下载进度或存储空间需求。

## 蓝图用法

当前插件的 `IPlatformDLC` 接口主要设计为 C++ 使用，未在提供的头文件中暴露 `BlueprintCallable` 函数。DLC 的状态查询和操作建议在 C++ 层实现，并通过自定义的蓝图接口或事件将结果暴露给蓝图系统。

## C++ 用法

### 头文件引入

```cpp
#include "PlatformDLCModule.h"
```

### 基本用法

以下代码展示了如何初始化插件、查询 DLC 状态并发起挂载操作。

```cpp
// 来源: 基于 PlatformDLC.h 和 PlatformDLCModule.h 接口推断的用法
#include "PlatformDLCModule.h"

void UMyGameInstance::Init()
{
    // 获取平台 DLC 模块的单例
    IPlatformDLCModule& PlatformDLCModule = IPlatformDLCModule::Get();
    TSharedPtr<IPlatformDLC> PlatformDLC = PlatformDLCModule.GetPlatformDLC();

    if (PlatformDLC.IsValid())
    {
        // 初始化 DLC 系统
        PlatformDLC->Initialize();

        // 查询名为 “SeasonPass” 的 DLC 状态
        const FName DLCName = TEXT(“SeasonPass”);
        bool bHasEntitlement = PlatformDLC->HasEntitlement(DLCName);
        bool bIsMounted = PlatformDLC->IsMounted(DLCName);
        bool bIsDownloaded = PlatformDLC->IsDownloaded(DLCName);

        UE_LOG(LogTemp, Log, TEXT(“DLC %s: Entitlement=%d, Mounted=%d, Downloaded=%d”),
            *DLCName.ToString(), bHasEntitlement, bIsMounted, bIsDownloaded);

        // 如果有权限但未挂载，则尝试挂载
        if (bHasEntitlement && !bIsMounted)
        {
            bool bMountStarted = PlatformDLC->Mount(DLCName);
            if (bMountStarted)
            {
                UE_LOG(LogTemp, Log, TEXT(“Mount operation started for %s.”), *DLCName.ToString());
            }
        }
    }
}
```

### 进阶用法

以下代码展示了如何监听 DLC 状态变化的通知，并处理多个 DLC。

```cpp
// 来源: 基于 IPlatformDLC::FOnDLCNotification 委托的用法
#include "PlatformDLCModule.h"

class FDLCManager
{
public:
    void Initialize()
    {
        IPlatformDLCModule& PlatformDLCModule = IPlatformDLCModule::Get();
        PlatformDLC = PlatformDLCModule.GetPlatformDLC();

        if (PlatformDLC.IsValid())
        {
            PlatformDLC->Initialize();

            // 绑定通知委托
            NotificationHandle = PlatformDLC->OnNotification().AddRaw(this, &FDLCManager::HandleDLCNotification);

            // 获取所有已知的 DLC 并检查状态
            TArray<FName> AllDLCNames = PlatformDLC->GetAllDLCNames();
            for (const FName& Name : AllDLCNames)
            {
                if (PlatformDLC->HasEntitlement(Name) && !PlatformDLC->IsMounted(Name))
                {
                    // 尝试挂载所有有权限但未挂载的 DLC
                    PlatformDLC->Mount(Name);
                }
            }
        }
    }

    void Shutdown()
    {
        if (PlatformDLC.IsValid())
        {
            PlatformDLC->OnNotification().Remove(NotificationHandle);
            PlatformDLC->Shutdown();
        }
    }

private:
    void HandleDLCNotification(FName DLCName, IPlatformDLC::ENotification NotificationType, bool bSuccess)
    {
        switch (NotificationType)
        {
        case IPlatformDLC::ENotification::Mounted:
            if (bSuccess)
            {
                UE_LOG(LogTemp, Log, TEXT(“DLC %s mounted successfully. Root dir: %s”),
                    *DLCName.ToString(), *PlatformDLC->GetRootDirectory(DLCName));
                // DLC 挂载成功，可以加载其中的资产
            }
            break;
        case IPlatformDLC::ENotification::Downloaded:
            UE_LOG(LogTemp, Log, TEXT(“DLC %s downloaded. Auto-mount may be pending.”), *DLCName.ToString());
            break;
        case IPlatformDLC::ENotification::Entitlement:
            if (!bSuccess)
            {
                UE_LOG(LogTemp, Warning, TEXT(“Entitlement lost for DLC %s.”), *DLCName.ToString());
                // 权限丢失，可能需要卸载 DLC 或提示玩家
            }
            break;
        // 处理其他通知类型...
        }
    }

    TSharedPtr<IPlatformDLC> PlatformDLC;
    FDelegateHandle NotificationHandle;
};
```

## Demo 示例

以下是一个最小化的游戏模块集成示例，展示了如何在游戏实例中管理 PlatformDLC 插件的生命周期。

**MyGameDLCManager.h**
```cpp
// Copyright Your Company. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "PlatformDLC.h"
#include "MyGameDLCManager.generated.h"

UCLASS()
class UMyGameDLCManager : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    /** 查询指定DLC是否已就绪（已挂载） */
    UFUNCTION(BlueprintCallable, Category = “DLC”)
    bool IsDLCReady(FName DLCName) const;

private:
    void HandleDLCNotification(FName DLCName, IPlatformDLC::ENotification NotificationType, bool bSuccess);

    TSharedPtr<IPlatformDLC> PlatformDLC;
    FDelegateHandle NotificationDelegateHandle;
};
```

**MyGameDLCManager.cpp**
```cpp
// Copyright Your Company. All Rights Reserved.

#include “MyGameDLCManager.h”
#include “PlatformDLCModule.h”

void UMyGameDLCManager::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    IPlatformDLCModule& DLCModule = IPlatformDLCModule::Get();
    PlatformDLC = DLCModule.GetPlatformDLC();

    if (PlatformDLC.IsValid())
    {
        PlatformDLC->Initialize();
        NotificationDelegateHandle = PlatformDLC->OnNotification().AddUObject(this, &UMyGameDLCManager::HandleDLCNotification);

        UE_LOG(LogTemp, Log, TEXT(“PlatformDLC subsystem initialized.”));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT(“PlatformDLC not available.”));
    }
}

void UMyGameDLCManager::Deinitialize()
{
    if (PlatformDLC.IsValid())
    {
        PlatformDLC->OnNotification().Remove(NotificationDelegateHandle);
        PlatformDLC->Shutdown();
        PlatformDLC.Reset();
    }

    Super::Deinitialize();
}

bool UMyGameDLCManager::IsDLCReady(FName DLCName) const
{
    if (PlatformDLC.IsValid())
    {
        return PlatformDLC->IsMounted(DLCName);
    }
    return false;
}

void UMyGameDLCManager::HandleDLCNotification(FName DLCName, IPlatformDLC::ENotification NotificationType, bool bSuccess)
{
    if (NotificationType == IPlatformDLC::ENotification::Mounted && bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT(“DLC %s is now ready to use.”), *DLCName.ToString());
        // 可以在这里广播蓝图事件，通知UI或其他系统
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF. (将日志宏迁移到新的 UE_LOGF 格式)
- 2026-03-25 `5b63810e` Add extra IPlatformFile functions to PlatformDLCFile (为 PlatformDLCFile 添加额外的 IPlatformFile 函数)
- 2026-03-25 `9977baae` Add a LexToString for IPlatformDLC ENotifications (为 IPlatformDLC::ENotification 添加 LexToString 转换函数)

### 维护评价

该插件创建于 2026 年 3 月，是一个非常新的实验性插件（`IsBetaVersion: true`）。从 git 历史看，在创建后的一个月内有多次功能性更新（如添加文件系统支持、枚举转换函数），表明它正处于**早期活跃开发阶段**。由于是实验性插件，其 API 明确声明“may be subject to change”，因此**不推荐在需要稳定性的生产项目中直接使用**。它非常适合用于技术预研、原型开发或作为学习跨平台 DLC 集成的参考。建议关注其后续版本，等待 API 趋于稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlatformDLC)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlatformDLC/Tests) (如果存在)