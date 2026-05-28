# Online Framework Plugin

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 中文名 | 在线框架 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Qos` (Runtime), `Party` (Runtime), `Lobby` (Runtime), `Hotfix` (Runtime), `LoginFlow` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途

**OnlineFramework** 插件不是一个独立的功能模块，而是一个 **Runtime 模块集合**，旨在为在线游戏功能提供共享的、平台无关的框架代码。它封装了在线游戏服务中常见且复杂的交互逻辑，避免每个游戏项目或 Online Subsystem 插件重复实现这些底层功能。

它主要解决以下问题：
1.  **热修复（Hotfix）管理**：提供 `UOnlineHotfixManager`，用于从后端（如 IOnlineTitleFile）下载并应用热修复数据（如 INI 配置、PAK 文件、本地化资源），在不重启游戏的情况下修复问题或调整游戏参数。
2.  **更新检查与管理**：提供 `UUpdateManager`，用于协调和执行游戏启动时的更新检查流程，包括补丁检查、热修复检查、资产预加载等，并提供状态通知。
3.  **社交功能框架**：提供玩家派对（Party）、大厅（Lobby）、重连（Rejoin）等功能的通用管理框架，供具体的平台 Online Subsystem 实现。
4.  **连接质量监控**：提供 QoS (Quality of Service) 检测模块，用于监控和报告玩家与服务器之间的网络连接质量。
5.  **登录与版本检查**：提供登录流程（LoginFlow）和补丁检查（PatchCheck）的通用逻辑。

简单来说，这个插件是 Unreal 在线游戏生态系统的 **“基础设施层”**，为上层具体的平台集成（如 OnlineSubsystemSteam, OnlineSubsystemEOS）提供标准化的服务。

## 使用场景

- **你需要一个游戏内热修复系统**：能够动态修改 `DataTable`、`CurveTable`、INI 配置等，用于在线平衡性调整或紧急 Bug 修复。 → 使用 `UOnlineHotfixManager`。
- **你的游戏需要一个标准化的启动更新流程**：需要在进入主菜单前检查游戏版本、下载热更新、预加载资源。 → 使用 `UUpdateManager`。
- **你正在开发一个多人在线游戏，并希望复用派对、大厅等社交功能逻辑**：你的平台特定 OSS（如 GDK、EOS）可以基于此框架实现具体功能。 → 依赖 `Party`、`Lobby` 模块。
- **你需要监控玩家的网络连接质量**：用于自动匹配合适的服务器或在网络状况不佳时提示玩家。 → 使用 `Qos` 模块。

## 蓝图用法

本插件主要提供后台管理功能，其蓝图接口集中在 `UUpdateManager`，用于控制和监控更新流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Update Check` | 使用指定的上下文名称开始一次更新检查流程（包括补丁和热修复检查）。 | `UUpdateManager` |
| `Get Update State` | 获取当前更新管理器的状态（空闲、检查中、等待等）。 | `UUpdateManager` |
| `Get Completion Result` | 获取上一次更新检查的完成结果（成功、失败原因等）。 | `UUpdateManager` |
| `Is Hotfixing Enabled` | 检查当前是否启用了热修复功能。 | `UUpdateManager` |
| `Is Updating` | 检查更新管理器是否正在执行更新检查。 | `UUpdateManager` |
| `Set Pending` | 将更新管理器设置为“待定”状态，提示游戏即将开始检查。 | `UUpdateManager` |
| `Start Hotfix Process` | 直接启动热修复流程（非通过UpdateManager的完整流程）。 | `UOnlineHotfixManager` |
| `Check Hotfix Availability` | 检查是否有可用的热修复文件，但不应用它们。 | `UOnlineHotfixManager` |

### 使用示例（蓝图描述）

**场景：游戏启动时检查更新**

1.  在你的 `GameInstance` 或 `GameMode` 的 `BeginPlay` 中，获取 `UUpdateManager` 实例（通常通过 `UOnlineHotfixManager::Get` 间接关联或直接获取配置的实例）。
2.  调用 `Start Update Check` 节点，传入一个上下文名称（例如 `"GameStartup"`），该名称对应于 `DefaultEngine.ini` 中 `[UpdateManager]` 配置节里定义的 `UpdateContextDefinitions`。
3.  绑定 `On Update Status Changed` 和 `On Update Check Complete` 代理，以便在蓝图中接收状态变化和最终结果的通知。
4.  在结果回调中，根据 `EUpdateCompletionStatus` 决定后续行为：如果成功 (`UpdateSuccess`)，则允许进入主菜单；如果需要补丁 (`UpdateSuccess_NeedsPatch`)，则提示玩家前往商店更新；如果失败，则显示错误信息。

## C++ 用法

核心用法在于理解并可能扩展 `UOnlineHotfixManager` 和 `UUpdateManager`。

### 头文件引入

```cpp
#include "OnlineHotfixManager.h"
#include "UpdateManager.h"
```

### 基本用法：应用自定义热修复处理

`UOnlineHotfixManager` 的设计鼓励通过继承来扩展。游戏或平台插件可以创建子类，并重写特定的虚函数来实现自定义的文件处理逻辑。

```cpp
// 来源: 根据 Engine/Plugins/Online/OnlineFramework/Source/Hotfix/Public/OnlineHotfixManager.h 中的虚函数设计
class UMyGameHotfixManager : public UOnlineHotfixManager
{
    GENERATED_BODY()

protected:
    // 重写虚函数以处理自定义的文件类型
    virtual bool WantsHotfixProcessing(const FCloudFileHeader& FileHeader) override
    {
        // 检查文件后缀或名称，决定是否需要我们自定义处理
        if (FileHeader.FileName.EndsWith(TEXT(".gamedata")))
        {
            return true;
        }
        return Super::WantsHotfixProcessing(FileHeader);
    }

    virtual bool ApplyHotfixProcessing(const FCloudFileHeader& FileHeader) override
    {
        // 在这里实现对.gamedata文件的解析和应用逻辑
        UE_LOG(LogHotfix, Log, TEXT("Applying custom game data hotfix: %s"), *FileHeader.FileName);
        // ... 自定义逻辑 ...
        return true; // 返回true表示处理成功
    }

    // 可选：自定义INI文件的处理方式
    virtual bool HotfixIniFile(const FString& FileName, const FString& IniData) override
    {
        UE_LOG(LogHotfix, Log, TEXT("Custom handling for INI hotfix: %s"), *FileName);
        // 可以记录、分析或修改IniData
        // 然后调用默认实现来完成实际合并
        return Super::HotfixIniFile(FileName, IniData);
    }
};
```

要使用你的自定义管理器，需要在项目的 `DefaultEngine.ini` 中进行配置：
```ini
[/Script/Hotfix.Hotfix]
; 指定要使用的热修复管理器类名
HotfixManagerClassName = "/Script/MyGameModule.MyGameHotfixManager"
```

### 进阶用法：集成更新管理器与自定义游戏流程

`UUpdateManager` 提供了丰富的委托和可重写的虚函数，以便深度集成到游戏的生命周期中。

```cpp
// 来源: 根据 Engine/Plugins/Online/OnlineFramework/Source/Hotfix/Public/UpdateManager.h 设计
// 在你的GameInstance中
class UMyGameInstance : public UGameInstance
{
public:
    virtual void Init() override
    {
        Super::Init();

        // 绑定更新状态委托
        if (UUpdateManager* UpdateMgr = UUpdateManager::Get(GetWorld()))
        {
            UpdateMgr->OnUpdateStatusChanged().AddUObject(this, &UMyGameInstance::HandleUpdateStatusChanged);
            UpdateMgr->OnUpdateCheckComplete().AddUObject(this, &UMyGameInstance::HandleUpdateCheckComplete);
        }
    }

private:
    void HandleUpdateStatusChanged(EUpdateState NewState)
    {
        switch (NewState)
        {
        case EUpdateState::CheckingForPatch:
            UE_LOG(LogMyGame, Log, TEXT("Update Manager: 开始检查补丁..."));
            // 可以显示一个加载界面或状态提示
            break;
        case EUpdateState::CheckingForHotfix:
            UE_LOG(LogMyGame, Log, TEXT("Update Manager: 开始检查热修复..."));
            break;
        // ... 处理其他状态
        }
    }

    void HandleUpdateCheckComplete(EUpdateCompletionStatus Result)
    {
        UE_LOG(LogMyGame, Log, TEXT("Update Manager: 更新检查完成，结果: %s"), *LexToString(Result));
        // 根据结果决定游戏流程
        if (Result == EUpdateCompletionStatus::UpdateSuccess || Result == EUpdateCompletionStatus::UpdateSuccess_NoChange)
        {
            // 更新成功，可以开始预加载或进入游戏
            StartMainMenuLoading();
        }
        else if (Result == EUpdateCompletionStatus::UpdateSuccess_NeedsPatch)
        {
            // 需要下载补丁，提示玩家或打开商店
            ShowPatchRequiredUI();
        }
        // ... 处理其他失败情况
    }
};
```

## Demo 示例

以下是一个最小化的热修复管理器子类示例，展示了如何重写核心虚函数。

**MyGameHotfixManager.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "OnlineHotfixManager.h"
#include "MyGameHotfixManager.generated.h"

UCLASS()
class MYGAME_API UMyGameHotfixManager : public UOnlineHotfixManager
{
    GENERATED_BODY()

public:
    UMyGameHotfixManager();

protected:
    /** 自定义处理特定后缀的热修复文件 */
    virtual bool WantsHotfixProcessing(const FCloudFileHeader& FileHeader) override;

    /** 应用自定义的游戏数据热修复 */
    virtual bool ApplyHotfixProcessing(const FCloudFileHeader& FileHeader) override;

    /** 重写 INI 处理以添加额外逻辑（例如日志记录） */
    virtual bool HotfixIniFile(const FString& FileName, const FString& IniData) override;
};
```

**MyGameHotfixManager.cpp**
```cpp
#include "MyGameHotfixManager.h"
#include "Misc/FileHelper.h"

UMyGameHotfixManager::UMyGameHotfixManager()
{
    // 可以在这里设置一些自定义的默认配置
}

bool UMyGameHotfixManager::WantsHotfixProcessing(const FCloudFileHeader& FileHeader)
{
    // 如果文件扩展名为 .cfg，我们希望处理它
    if (FileHeader.FileName.EndsWith(TEXT(".cfg")))
    {
        UE_LOG(LogHotfix, Log, TEXT("UMyGameHotfixManager: Requesting custom processing for %s"), *FileHeader.FileName);
        return true;
    }
    // 其他文件类型交给父类默认处理（INI, PAK等）
    return Super::WantsHotfixProcessing(FileHeader);
}

bool UMyGameHotfixManager::ApplyHotfixProcessing(const FCloudFileHeader& FileHeader)
{
    UE_LOG(LogHotfix, Log, TEXT("Applying custom .cfg hotfix: %s"), *FileHeader.FileName);

    // 假设我们已经将文件下载到了内存中，需要根据 FileHeader 的数据进行处理
    // 这里是一个简化的示例：假设数据是 JSON 格式
    // ... 解析逻辑 ...

    // 处理完成
    return true;
}

bool UMyGameHotfixManager::HotfixIniFile(const FString& FileName, const FString& IniData)
{
    UE_LOG(LogHotfix, Log, TEXT("Custom INI Hotfix applied to: %s"), *FileName);
    // 在默认合并逻辑之前，可以记录或修改 IniData
    // 例如：IniData.ReplaceInline(TEXT("OldValue"), TEXT("NewValue"));
    
    // 调用父类实现完成实际的配置合并
    return Super::HotfixIniFile(FileName, IniData);
}
```

## 模块依赖

使用 `OnlineFramework` 插件的特定模块时，你的项目可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 所有在线功能的基石接口，`Hotfix`、`Party` 等模块都依赖它与具体的平台实现交互。 |
| `OnlineSubsystemGDK` | 如果你为 Xbox 平台开发，`Party` 模块可能需要此模块来实现平台特定的派对功能。 |
| `PakFile` | `Hotfix` 模块在处理 PAK 类型的热修复文件时需要用到此模块进行文件加载和挂载。 |
| `InstallBundleManager` | `PatchCheck` 模块可能依赖此模块来检查和管理游戏内容的安装包。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exis | 修复了在无后端热修复时，特定内置热修复无法应用的加载时问题。 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | 当启用了 Epic 派对镜像时，增加了对邀请和加入派对社交调用的防护。 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platf | 为 PartyPlatformSessionMonitor 添加了一个钩子，允许游戏派对向平台会话添加特殊密钥。 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复了用于加载时热修复的 LogHotfixManager 摘要日志。 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 在处理完首次更新后广播派对初始化事件。 |

### 维护评价

- **活跃维护**：从提交历史看，`OnlineFramework` 插件在 **2026 年 4-5 月仍有持续的功能性更新和 Bug 修复**，表明 Epic Games 对此框架仍在进行积极的维护和改进。
- **长期历史**：该插件自 2016 年创建，已历经超过 10 年，是 Unreal 在线生态中非常核心和稳定的组件。
- **推荐使用**：对于需要集成复杂在线功能（尤其是热修复和标准化更新流程）的 C++ 项目，使用此框架是推荐的选择，它可以避免大量重复开发。对于纯蓝图项目，主要通过 `UUpdateManager` 的蓝图接口使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework)
- 官方文档：无专门文档，但相关功能（如 Hotfix、Update Check）通常在关于在线子系统和版本管理的官方指南中提及。
- 测试用例：未在提供的路径中找到专门的测试文件。测试可能存在于集成测试或特定平台的 Online Subsystem 测试中。