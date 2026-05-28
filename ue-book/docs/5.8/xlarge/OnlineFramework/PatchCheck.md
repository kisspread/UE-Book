# Online Framework Plugin

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 中文名 | 在线框架 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Hotfix` (Runtime), `Lobby` (Runtime), `LoginFlow` (Runtime), `Party` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Qos` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途

OnlineFramework 是 Epic 为在线游戏提供的**基础设施框架层**，它在具体平台的 OnlineSubsystem（如 Steam、PSN、Xbox Live）之上，提供与平台无关的通用在线功能模块。

这个插件解决的核心问题是：不同平台的在线子系统各不相同，但游戏逻辑层需要一致的抽象。OnlineFramework 提供了以下通用能力：

- **补丁检查（PatchCheck）**：在游戏启动前检测是否有强制更新需要下载
- **大厅（Lobby）**：多人游戏的房间管理抽象
- **派对（Party）**：跨平台的组队/社交功能
- **QoS**：网络质量检测，帮助匹配到最佳服务器
- **热修复（Hotfix）**：无需完整客户端更新即可推送修复
- **重连（Rejoin）**：断线后重新加入会话
- **登录流程（LoginFlow）**：标准化的登录流程管理
- **游玩时间限制（PlayTimeLimit）**：家长控制/防沉迷

默认禁用是因为它通常由具体项目的 OnlineSubsystem 配置决定是否需要。

## 使用场景

- 你在开发需要强制补丁检查的多人游戏 → 使用 **PatchCheck** 模块
- 你需要跨平台组队和社交功能 → 使用 **Party** + **Lobby** 模块
- 你需要在不发版的情况下推送紧急修复 → 使用 **Hotfix** 模块
- 你需要测量玩家到各服务器的延迟以做匹配 → 使用 **Qos** 模块
- 你需要实现断线重连机制 → 使用 **Rejoin** 模块

## 蓝图用法

本插件主要为 C++ 框架层，大部分功能通过 C++ API 使用。部分模块（如 Hotfix）暴露了蓝图可用的接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartPatchCheck` | 发起一次补丁检查流程 | `FPatchCheck` |
| `GetOnComplete` | 获取补丁检查完成的委托 | `FPatchCheck` |
| `GetLastPatchCheckResult` | 获取上次补丁检查结果 | `FPatchCheck` |

## C++ 用法

### 头文件引入

```cpp
#include "PatchCheck.h"
#include "PatchCheckModule.h"
```

### 基本用法 — 补丁检查

从 `Public/PatchCheck.h` 和 `Public/PatchCheckModule.h` 提取：

```cpp
// 获取 PatchCheck 单例（通过模块接口）
IPatchCheckModule* PatchCheckModule = FModuleManager::GetModulePtr<IPatchCheckModule>("PatchCheck");
if (PatchCheckModule)
{
    FPatchCheck* PatchCheck = PatchCheckModule->GetPatchCheck();
    if (PatchCheck)
    {
        // 监听补丁检查结果
        PatchCheck->GetOnComplete().AddLambda([](EPatchCheckResult Result)
        {
            switch (Result)
            {
            case EPatchCheckResult::NoPatchRequired:
                // 无需补丁，可以继续
                break;
            case EPatchCheckResult::PatchRequired:
                // 需要更新，提示玩家
                break;
            case EPatchCheckResult::NoLoggedInUser:
                // 需要登录才能检查
                break;
            case EPatchCheckResult::PatchCheckFailure:
                // 检查失败，处理错误
                break;
            }
        });

        // 发起检查
        PatchCheck->StartPatchCheck();
    }
}
```

### 进阶用法 — 注册统计收集器

实现 `IPatchCheckStatsCollector` 接口来收集补丁检查的性能/状态数据：

```cpp
class FMyPatchCheckStats : public IPatchCheckStatsCollector
{
public:
    // 整体流程回调
    virtual void OnPatchCheckStarted() override
    {
        UE_LOG(LogTemp, Log, TEXT("Patch check started"));
    }

    virtual void OnPatchCheckComplete(EPatchCheckResult Result) override
    {
        UE_LOG(LogTemp, Log, TEXT("Patch check complete: %s"), LexToString(Result));
    }

    // 各阶段回调
    virtual void OnPatchCheckStep_DetectEnvironmentStarted() override {}
    virtual void OnPatchCheckStep_DetectEnvironmentComplete(bool bSuccess, const FString& Error) override {}
    virtual void OnPatchCheckStep_CheckPlatformPatchStarted() override {}
    virtual void OnPatchCheckStep_CheckPlatformPatchComplete(bool bSuccess, const FString& Error) override {}
    virtual void OnPatchCheckStep_CheckOnlineServicePatchStarted() override {}
    virtual void OnPatchCheckStep_CheckOnlineServicePatchComplete(bool bSuccess, const FString& Error) override {}
};

// 注册
auto StatsCollector = MakeShared<FMyPatchCheckStats>();
FPatchCheck::Get().RegisterStatsCollector(StatsCollector);
```

### 进阶用法 — 环境补丁检查委托（向后兼容）

```cpp
// 注册一个向后兼容的环境检查委托（标记为 BackCompat，新代码不推荐使用）
FPatchCheck::Get().AddEnvironmentWantsPatchCheckBackCompatDelegate(
    FName("MyGame"),
    FEnvironmentWantsPatchCheck::CreateLambda([]() -> bool
    {
        // 返回 true 表示当前环境需要补丁检查
        return true;
    })
);

// 移除
FPatchCheck::Get().RemoveEnvironmentWantsPatchCheckBackCompatDelegate(FName("MyGame"));
```

## Demo 示例

```cpp
// MyPatchCheckManager.h
#pragma once

#include "CoreMinimal.h"
#include "PatchCheck.h"

class FMyPatchCheckManager
{
public:
    void Initialize();
    void Shutdown();

private:
    void OnPatchCheckComplete(EPatchCheckResult Result);
    FDelegateHandle CompleteHandle;
};
```

```cpp
// MyPatchCheckManager.cpp
#include "MyPatchCheckManager.h"
#include "PatchCheckModule.h"
#include "Modules/ModuleManager.h"

void FMyPatchCheckManager::Initialize()
{
    // 通过模块获取 PatchCheck 实例
    IPatchCheckModule* Module = FModuleManager::GetModulePtr<IPatchCheckModule>("PatchCheck");
    if (!Module)
    {
        UE_LOG(LogTemp, Warning, TEXT("PatchCheck module not loaded"));
        return;
    }

    FPatchCheck* PatchCheck = Module->GetPatchCheck();
    if (PatchCheck)
    {
        CompleteHandle = PatchCheck->GetOnComplete().AddRaw(
            this, &FMyPatchCheckManager::OnPatchCheckComplete);

        PatchCheck->StartPatchCheck();
    }
}

void FMyPatchCheckManager::Shutdown()
{
    IPatchCheckModule* Module = FModuleManager::GetModulePtr<IPatchCheckModule>("PatchCheck");
    if (Module)
    {
        FPatchCheck* PatchCheck = Module->GetPatchCheck();
        if (PatchCheck)
        {
            PatchCheck->GetOnComplete().Remove(CompleteHandle);
        }
    }
    CompleteHandle.Reset();
}

void FMyPatchCheckManager::OnPatchCheckComplete(EPatchCheckResult Result)
{
    if (Result == EPatchCheckResult::NoPatchRequired)
    {
        UE_LOG(LogTemp, Log, TEXT("No patch needed, proceeding to main menu"));
    }
    else if (Result == EPatchCheckResult::PatchRequired)
    {
        UE_LOG(LogTemp, Warning, TEXT("Patch required! Prompting user to update."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemGDK` | Party 模块依赖，Xbox GDK 平台在线子系统支持 |

> 注：各子模块还隐式依赖 `OnlineSubsystem` 基础模块，这是所有在线功能的基石。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exist | 修复内置热修复在无后端热修复时不生效的问题 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | Epic 派对镜像启用时保护邀请和加入社交派对调用 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platform | 为 PartyPlatformSessionMonitor 添加钩子，允许游戏派对向平台会话注入特殊键 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复 HotfixManager 在加载时的摘要日志输出 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 在处理首次更新后广播派对初始化事件 |

### 维护评价

**活跃维护** ✅

该插件创建于 2016 年，至今已有约 10 年历史，属于 UE 在线功能的核心基础设施。从 git 历史来看，最近一个月内有多次实质性更新（2026-04-28 至 2026-05-12），主要集中在：

1. **Hotfix 模块**：持续修复热修复系统在边缘情况下的行为
2. **Party 模块**：活跃改进派对系统与平台会话的集成

作为 Epic 自家多人游戏（如 Fortnite）的核心依赖，该插件会持续得到维护。但由于 `EnabledByDefault=false`，说明它不是通用插件，仅在明确需要在线功能时启用。

**建议**：如果你的项目需要跨平台在线功能，这是一个可靠的基础设施层。如果你只需要简单的 Steam 集成，可能直接使用 `OnlineSubsystemSteam` 就够了。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework)
- [OnlineSubsystem 基础模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystem)