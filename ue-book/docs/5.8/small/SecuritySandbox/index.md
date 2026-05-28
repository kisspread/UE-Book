# Security Sandbox

> Provides features to help reduce the operating system permissions your game client runs with and therefore reduce the impact to players if an attacker takes control of it through a vulnerability.

| 属性 | 值 |
|---|---|
| 中文名 | 安全沙箱 |
| 分类 | Security |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SecuritySandbox` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2023-12-01 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SecuritySandbox) | |

## 用途

**SecuritySandbox** 插件旨在为运行在 Windows 平台上的游戏客户端提供操作系统级别的权限限制。其核心目的是解决游戏客户端在联网游戏或处理用户生成内容（UGC）时可能被恶意攻击者利用漏洞控制的安全问题。通过降低游戏进程的操作系统权限，即使攻击者成功入侵客户端，其可执行的恶意操作范围也被大幅缩小，从而保护玩家的数据和系统安全。它并非用于防御游戏逻辑层面的作弊，而是专注于降低安全事件发生后的影响面。

## 使用场景

-   你正在开发一个**多人在线竞技（MMO）或竞技游戏**，需要防范通过游戏客户端漏洞进行的远程攻击。
-   你的游戏支持**加载用户生成内容（UGC）**，例如自定义模型、地图或模组，需要限制这些内容可能带来的系统级风险。
-   你希望为 Windows 平台客户端提供一个**纵深防御**的安全层，作为游戏内安全措施（如反作弊）的补充。

## 蓝图用法

该插件的主要功能通过 C++ 和项目设置进行配置，不提供直接的蓝图节点。其核心交互发生在编辑器项目设置中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `USecuritySandboxSettings` (资产) | 在项目设置中配置沙箱的各项限制规则，这是与该插件交互的主要蓝图接口。 | `USecuritySandboxSettings` |

### 使用示例（蓝图描述）

1.  在 Unreal Editor 中，前往 **编辑 -> 项目设置**。
2.  在左侧分类中找到 **Plugins -> Security Sandbox**。
3.  在右侧面板中，你可以配置诸如 `bIsEnabledByDefault`（是否默认启用）、`bAutoRestrictSelf`（是否在引擎初始化后自动应用限制）等选项。
4.  这些设置会保存在项目的 `DefaultEngine.ini` 配置文件中。

## C++ 用法

插件的核心逻辑和配置通过 C++ 接口提供。主要用法包括检查沙箱状态和主动触发限制。

### 头文件引入

```cpp
#include "ISecuritySandboxModule.h"
#include "SecuritySandboxSettings.h"
```

### 基本用法

检查安全沙箱是否可用并已启用，然后根据配置决定是否手动触发限制。
*(来源: `ISecuritySandboxModule.h`, `ISecuritySandbox.h`)*

```cpp
// 检查模块是否已加载
if (ISecuritySandboxModule::IsAvailable())
{
    // 获取模块接口的引用
    ISecuritySandboxModule& SandboxModule = ISecuritySandboxModule::Get();

    // 检查沙箱整体是否启用（受配置和命令行参数控制）
    if (SandboxModule.IsEnabled())
    {
        UE_LOG(LogSecuritySandbox, Log, TEXT("Security Sandbox is active."));
        
        // 如果没有设置“自动限制”(bAutoRestrictSelf=false)，则需要在合适的时机（如初始化网络连接前）手动调用
        // 注意：此操作是永久性的，会降低进程权限。
        SandboxModule.RestrictSelf();
    }
    else
    {
        UE_LOG(LogSecuritySandbox, Warning, TEXT("Security Sandbox is disabled via settings or command line."));
    }
}
```

### 进阶用法

在游戏初始化后，结合项目设置进行更精细的控制。例如，你可能只想在进入在线模式时才应用限制。
*(来源: `USecuritySandboxSettings.h`, `ISecuritySandbox.h`)*

```cpp
// 获取安全沙箱的设置对象（在编辑器/开发构建中可用）
const USecuritySandboxSettings* Settings = GetDefault<USecuritySandboxSettings>();
if (Settings)
{
    // 根据项目设置判断是否应该启用沙箱
    // 注意：还需要考虑命令行参数 `-WithSecuritySandbox`
    bool bShouldBeEnabled = Settings->bIsEnabledByDefault; // 简化逻辑，实际需结合命令行
    // ... 这里可以加入更复杂的逻辑，比如只在 Shipping 构建中启用
    
    if (bShouldBeEnabled && ISecuritySandboxModule::IsAvailable())
    {
        // 如果设置为自动限制（bAutoRestrictSelf=true），则插件会在引擎初始化完成后自动调用 RestrictSelf()。
        // 如果为 false，则需要我们手动在合适的时机调用，例如在玩家选择“在线游戏”之后。
        if (!Settings->bAutoRestrictSelf)
        {
            // 假设在玩家登录在线服务器前调用
            // OnPlayerRequestingOnlinePlay() {
            ISecuritySandboxModule::Get().RestrictSelf();
            // }
        }
    }
}

// 检查具体的限制是否生效（以 Windows 低完整性级别为例）
if (Settings && Settings->bUseLowIntegrityLevel)
{
    UE_LOG(LogSecuritySandbox, Log, TEXT("Process is configured to run at low integrity level after restriction."));
}
```

## Demo 示例

一个最小的示例，演示如何在游戏模式中检查并应用安全沙箱限制。

### `MyGameMode.h`
```cpp
#pragma once
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()
    
public:
    virtual void InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage) override;
};
```

### `MyGameMode.cpp`
```cpp
#include "MyGameMode.h"
#include "ISecuritySandboxModule.h"

void AMyGameMode::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
    Super::InitGame(MapName, Options, ErrorMessage);

    // 在游戏初始化时检查并手动应用沙箱限制（假设 bAutoRestrictSelf 被设置为 false）
    if (ISecuritySandboxModule::IsAvailable() && ISecuritySandboxModule::Get().IsEnabled())
    {
        UE_LOG(LogTemp, Log, TEXT("Applying security sandbox restrictions before loading level..."));
        ISecuritySandboxModule::Get().RestrictSelf();
        
        // 限制后，进程权限将降低，后续的在线功能或UGC加载将处于受限环境中
    }
}
```

## 模块依赖

该插件的构建系统依赖以下模块。要使用此插件，你的项目通常不需要额外依赖，但如果你想在自己的模块中访问其 API，则需要：

| 模块 | 用途 |
|---|---|
| `SecuritySandbox` | 插件主模块，提供沙箱的核心功能和接口。 |

**注意**：该插件仅限 **Win64** 平台使用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至 `UE_LOGF`，属于代码规范化更新。 |
| 2024-11-10 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 移除了所有用于兼容 UE5.2 之前头文件包含顺序的废弃宏，是代码清理的一部分。 |
| 2023-12-01 | `6da87796` | Add SecuritySandbox experimental engine plugin... | 插件的首次提交，包含了完整的插件框架和 Windows 平台实现。 |

### 维护评价

**SecuritySandbox** 是一个相对较新（约 3 年）的实验性插件。自 2023 年 12 月创建以来，有两次后续维护，主要集中在代码清理和规范化上，而非新功能开发。

**总结**：
-   **实验性状态**：插件被明确标记为实验性，且默认禁用 (`EnabledByDefault: false`)，这意味着它尚未达到生产就绪状态，API 和功能可能会发生变化。
-   **平台限制**：目前仅支持 Windows (Win64) 平台。
-   **维护频率**：更新不频繁，但核心代码在 2024 年底有过清理，表明它仍在 Epic 的视线内，但不属于高优先级维护对象。
-   **推荐度**：**谨慎使用**。适合对客户端安全有极高要求、且有能力自行评估和承担实验性插件风险的 Windows 平台项目。不建议在追求稳定性的项目中默认启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SecuritySandbox)
- [测试用例] (未在提供的信息中发现明确的测试文件路径)