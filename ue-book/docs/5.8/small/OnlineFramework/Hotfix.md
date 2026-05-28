# Online Framework Plugin

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 中文名 | 在线框架插件 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Hotfix` (Runtime), `Lobby` (Runtime), `LoginFlow` (Runtime), `Party` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Qos` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途

`OnlineFramework` 插件是一个**在线游戏服务功能的基础设施层**。它提供了一组运行时模块，旨在简化与后端在线服务交互的通用功能开发。它不直接绑定到某个特定的在线子系统（如 Steam、EOS 等），而是提供实现通用在线功能（如热修复、组队、大厅、登录流程等）的框架和管理器。

其核心价值在于：
1.  **标准化在线功能实现**：为热修复（Hotfix）、更新管理、玩家组队（Party）、游戏大厅（Lobby）等常见在线功能提供标准化的实现方案。
2.  **解耦与扩展**：将通用逻辑与特定的在线子系统实现分离，允许游戏项目在此基础上进行扩展或适配。
3.  **提供完整工作流**：例如，`Hotfix` 和 `UpdateManager` 模块共同构成了一套从后端检查更新、下载文件到应用热修复（包括 INI 合并、PAK 文件挂载、资产热修复）的完整流程。

## 使用场景

-   你需要为游戏实现一套**从后端动态更新游戏配置或资产**的机制（例如平衡性调整、活动配置），而不希望发布客户端补丁 → 使用 `Hotfix` 和 `UpdateManager` 模块。
-   你的多人在线游戏需要一套**独立于具体在线子系统的玩家组队、邀请和匹配准备功能** → 使用 `Party` 模块。
-   你需要为游戏创建和管理**临时性的游戏会话（房间）**，包括玩家加入、离开、状态同步 → 使用 `Lobby` 模块。
-   你的游戏需要处理**平台特定的登录授权流程** → 使用 `LoginFlow` 模块。
-   你需要在登录或启动时**检查客户端版本是否需要更新** → 使用 `PatchCheck` 模块。
-   你需要实现**针对未成年玩家的游戏时长限制和休息提醒功能** → 使用 `PlayTimeLimit` 模块。
-   你需要在游戏启动或定期**测量连接到指定服务器的网络质量（延迟、丢包）** → 使用 `Qos` 模块。
-   你的游戏需要支持玩家在**断线后重新加入正在进行的游戏会话** → 使用 `Rejoin` 模块。

## 蓝图用法

该插件主要提供 C++ 类和接口，蓝图集成点主要集中在 `Hotfix` 和 `UpdateManager` 模块的状态查询和流程控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Hotfix Process` | 启动从在线服务获取并应用热修复数据的流程。 | `UOnlineHotfixManager` |
| `Start Update Check` | 使用指定的上下文定义（`ContextName`）启动一次完整的更新检查（包括补丁检查、热修复检查、预加载等）。 | `UUpdateManager` |
| `Get Update State` | 获取更新管理器的当前状态（空闲、检查中、完成等）。 | `UUpdateManager` |
| `Get Completion Result` | 获取上一次更新检查的最终结果（成功、失败原因等）。 | `UUpdateManager` |
| `Get Load Progress` | 获取异步加载资源的进度（0.0 到 1.0）。 | `UUpdateManager` |
| `Is Hotfixing Enabled` | 查询当前是否启用了热修复功能。 | `UUpdateManager` |

**使用示例（蓝图描述）**

1.  **启动更新检查**：在游戏主菜单或启动流程中，调用 `Start Update Check` 节点，并传入配置的 `ContextName`。绑定 `On Update Status Changed` 和 `On Update Check Complete` 委托来监听状态变化和最终结果。
2.  **处理更新结果**：根据 `Get Completion Result` 返回的 `EUpdateCompletionStatus` 枚举，决定后续操作。例如，如果是 `UpdateSuccess_NeedsReload`，则提示玩家重启游戏或重新加载关卡；如果是 `UpdateFailure_PatchCheck`，则可能显示错误信息或禁用“开始游戏”按钮。
3.  **显示热修复进度**：绑定 `On Update Hotfix Progress` 委托，获取 `NumDownloaded`、`TotalFiles` 等参数，在 UI 上显示下载进度条。
4.  **单独启动热修复**：在开发或测试阶段，可以绑定 `UOnlineHotfixManager` 的实例，直接调用 `Start Hotfix Process` 来快速测试热修复逻辑，而不必经过完整的更新检查流程。

## C++ 用法

### 头文件引入

```cpp
#include "OnlineHotfixManager.h"
#include "UpdateManager.h"
// 根据需要引入其他模块头文件，如 Party、Lobby 等
```

### 基本用法

`OnlineFramework` 的核心类通常在 `UWorld` 或 `UGameInstance` 的生命周期内进行管理。开发者更多是继承并重写其虚函数来定制行为。

**示例：自定义热修复管理器并启动流程**
(基于 `UOnlineHotfixManager` 接口分析)

```cpp
// MyGameHotfixManager.h
#pragma once
#include "OnlineHotfixManager.h"
#include "MyGameHotfixManager.generated.h"

UCLASS(Config=Game)
class UMyGameHotfixManager : public UOnlineHotfixManager
{
    GENERATED_BODY()

public:
    // 重写以处理游戏特定的热修复逻辑
    virtual bool ApplyHotfixProcessing(const FCloudFileHeader& FileHeader) override
    {
        // 调用基类处理默认的 INI、PAK、locres 文件
        bool bSuperResult = Super::ApplyHotfixProcessing(FileHeader);
        
        // 添加自定义文件类型的处理逻辑（例如 JSON 数据文件）
        if (FileHeader.FileName.EndsWith(TEXT(".json")))
        {
            // 处理 JSON 热修复数据...
            return true;
        }
        return bSuperResult;
    }

    // 重写以在热修复完成后触发游戏特定的通知
    virtual void FinalizeHotfixProcess(EHotfixResult HotfixResult) override
    {
        Super::FinalizeHotfixProcess(HotfixResult);
        
        if (HotfixResult == EHotfixResult::Success || HotfixResult == EHotfixResult::SuccessNeedsReload)
        {
            // 通知游戏系统热修复已应用
            OnMyGameHotfixAppliedDelegate.Broadcast();
        }
    }

    DECLARE_MULTICAST_DELEGATE(FOnMyGameHotfixApplied);
    FOnMyGameHotfixApplied OnMyGameHotfixAppliedDelegate;
};

// 在合适的地方（如 GameInstance 初始化后）启动热修复流程
void UMyGameInstance::Init()
{
    Super::Init();
    // 获取或创建热修复管理器实例
    UMyGameHotfixManager* HotfixManager = GetMutableDefault<UMyGameHotfixManager>();
    if (HotfixManager)
    {
        HotfixManager->StartHotfixProcess();
    }
}
```

**示例：使用更新管理器检查更新**
(基于 `UUpdateManager` 接口分析)

```cpp
// 在某个需要检查更新的函数中
void AMyGameMode::CheckForUpdates()
{
    UUpdateManager* UpdateManager = GetGameInstance()->GetSubsystem<UUpdateManager>();
    if (UpdateManager)
    {
        // 绑定委托以监听更新结果
        UpdateManager->OnUpdateCheckComplete().AddUObject(this, &AMyGameMode::OnUpdateCheckFinished);
        
        // 启动检查，使用配置中定义的上下文“MainMenu”
        UpdateManager->StartUpdateCheck(TEXT("MainMenu"));
    }
}

void AMyGameMode::OnUpdateCheckFinished(EUpdateCompletionStatus Result)
{
    switch (Result)
    {
    case EUpdateCompletionStatus::UpdateSuccess:
    case EUpdateCompletionStatus::UpdateSuccess_NoChange:
        // 允许玩家继续游戏
        EnablePlayButton();
        break;
    case EUpdateCompletionStatus::UpdateSuccess_NeedsPatch:
        // 显示提示需要更新补丁的 UI
        ShowPatchRequiredScreen();
        break;
    case EUpdateCompletionStatus::UpdateFailure_HotfixCheck:
    case EUpdateCompletionStatus::UpdateFailure_PatchCheck:
        // 显示错误信息
        ShowUpdateErrorScreen();
        break;
    // ... 处理其他情况
    }
}
```

### 进阶用法

进阶用法通常涉及深度定制 `UOnlineHotfixManager` 或 `UUpdateManager` 的行为，或集成其他模块。

**示例：在资产热修复中添加自定义逻辑**
`UOnlineHotfixManager` 提供了大量虚函数，允许你在热修复流程的各个环节介入。例如，重写 `ShouldHotfixAsset` 可以控制哪些资产被热修复，重写 `OnHotfixTableValueFloatWithSource` 可以在数据表值被修改时执行游戏逻辑。

```cpp
class UMyGameHotfixManager : public UOnlineHotfixManager
{
    // ...
protected:
    // 禁止热修复某些敏感资产
    virtual bool ShouldHotfixAsset(const FString& AssetPath) const override
    {
        if (AssetPath.Contains(TEXT("/Game/Config/Critical")))
        {
            UE_LOG(LogHotfix, Warning, TEXT("Blocking hotfix for critical asset: %s"), *AssetPath);
            return false;
        }
        return Super::ShouldHotfixAsset(AssetPath);
    }

    // 当数据表中的伤害数值被热修改时，记录日志
    virtual void OnHotfixTableValueFloatWithSource(
        UObject& Asset,
        const FString& RowName,
        const FString& ColumnName,
        const float& OldValue,
        const float& NewValue,
        FName SourceTag) override
    {
        Super::OnHotfixTableValueFloatWithSource(Asset, RowName, ColumnName, OldValue, NewValue, SourceTag);
        
        if (ColumnName == TEXT("Damage"))
        {
            UE_LOG(LogGameplay, Log, TEXT("Damage value for row '%s' changed from %f to %f by hotfix source '%s'"),
                *RowName, OldValue, NewValue, *SourceTag.ToString());
        }
    }
};
```

## Demo 示例

**自定义热修复管理器（.h + .cpp）**

```cpp
// MyHotfixManager.h
#pragma once
#include "OnlineHotfixManager.h"
#include "MyHotfixManager.generated.h"

UCLASS(Config=Game)
class MYGAME_API UMyHotfixManager : public UOnlineHotfixManager
{
    GENERATED_BODY()

public:
    UMyHotfixManager();

protected:
    // 1. 自定义配置前缀，用于加载游戏特定的热修复配置段
    virtual FString GetDedicatedServerPrefix() const override;

    // 2. 在应用 INI 热修复前后插入自定义逻辑
    virtual bool HotfixIniFile(const FString& FileName, const FString& IniData) override;
    virtual void PatchAssetsFromIniFiles() override;

    // 3. 在热修复完成时进行清理和通知
    virtual void FinalizeHotfixProcess(EHotfixResult HotfixResult) override;

private:
    // 游戏特定的数据
    TMap<FString, int32> CustomGameBalanceData;
};

// MyHotfixManager.cpp
#include "MyHotfixManager.h"
#include "Misc/ConfigCacheIni.h"

UMyHotfixManager::UMyHotfixManager()
{
    // 设置默认值
    PlatformPrefix = FPlatformProperties::PlatformName();
}

FString UMyHotfixManager::GetDedicatedServerPrefix() const
{
    // 返回自定义的专用服务器前缀
    return TEXT("MyGameServer");
}

bool UMyHotfixManager::HotfixIniFile(const FString& FileName, const FString& IniData)
{
    // 在应用 INI 热修复前，解析特定的自定义键值
    if (FileName.Contains(TEXT("MyGameBalance")))
    {
        FConfigFile TempConfig;
        if (FConfigCacheIni::LoadGlobalIniFile(TempConfig, *FileName))
        {
            // 提取自定义数据并存储
            FString Value;
            if (TempConfig.GetString(TEXT("CustomBalance"), TEXT("DamageMultiplier"), Value))
            {
                CustomGameBalanceData.Add(TEXT("DamageMultiplier"), FCString::Atoi(*Value));
            }
        }
    }
    
    // 调用基类默认处理
    return Super::HotfixIniFile(FileName, IniData);
}

void UMyHotfixManager::PatchAssetsFromIniFiles()
{
    Super::PatchAssetsFromIniFiles();
    
    // 在资产修补后，使用我们解析的自定义数据
    if (CustomGameBalanceData.Contains(TEXT("DamageMultiplier")))
    {
        // 应用全局伤害倍率调整到游戏系统中...
        UE_LOG(LogHotfix, Log, TEXT("Applied custom damage multiplier: %d"), CustomGameBalanceData[TEXT("DamageMultiplier")]);
    }
}

void UMyHotfixManager::FinalizeHotfixProcess(EHotfixResult HotfixResult)
{
    Super::FinalizeHotfixProcess(HotfixResult);
    
    // 清理临时数据
    CustomGameBalanceData.Empty();
    
    // 向游戏日志系统发送最终状态
    UE_LOG(LogHotfix, Log, TEXT("MyHotfixManager process finalized with result: %s"), LexToString(HotfixResult));
}
```

## 模块依赖

该插件包含多个运行时模块，其相互之间以及对外部模块有依赖。以下是使用该插件时，你的项目可能需要依赖的**非通用模块**：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 几乎所有模块的底层基础，提供在线服务的抽象接口。 |
| `OnlineSubsystemUtils` | 提供在线子系统的通用工具类，被多个模块使用。 |
| `OnlineSubsystemGDK` | `Party` 模块在当前版本中存在对此模块的特定依赖。 |
| `HTTP` | 用于网络请求，`Hotfix`、`PatchCheck`、`Qos` 等模块可能依赖。 |
| `Json` | 用于解析热修复数据中的 JSON 格式。 |
| `PakFile` | 用于挂载和管理热修复 PAK 文件。 |

*注：根据模板，已省略 `Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore`, `UMG`, `InputCore`, `Projects` 等几乎所有插件都会依赖的常见模块。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exis | 修复了“加载时热修复”功能的一个缺陷：在没有后端热修复数据时，某些内置的热修复无法正确应用。 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | 在启用 Epic 派对镜像功能时，增加了对“邀请”和“加入游戏”派对调用的保护，避免异常。 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platf | 为 `PartyPlatformSessionMonitor` 添加了一个钩子，允许游戏派对向平台会话中注入特殊标识。 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复了 `LogHotfixManager` 中针对“加载时热修复”的摘要日志输出。 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 将“派对初始化完成”的广播时机调整到处理完第一次更新之后。 |

### 维护评价

**活跃维护中**。
- **创建时间**：2016年，是UE4时代就存在的老插件。
- **最近更新**：截至2026年5月仍有持续的功能修复和优化更新（如修复加载时热修复缺陷、增强派对模块健壮性），表明该插件仍在被 Epic Games 积极维护，并用于其自家项目（如《堡垒之夜》）。
- **核心地位**：作为在线游戏服务的基础框架，其稳定性对众多依赖它的项目至关重要，因此大概率会持续维护。
- **推荐使用**：对于需要一套成熟、标准化在线功能框架的UE项目，此插件是**强烈推荐**的基石。它默认不启用(`EnabledByDefault=false`)，表明它适合需要这些高级在线功能的项目主动集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework)
- 官方文档：无特定文档链接。
- 测试用例：未在提供的信息中找到明确的测试文件路径。