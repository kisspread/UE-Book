# Online Services Null

> Online Services implementation without an external service.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 空在线服务 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码） |
| 模块 | `OnlineServicesNull` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServicesNull) | |

## 用途

`OnlineServicesNull` 是一个“空”或“无操作”的在线服务实现。它不连接任何真实的平台服务（如 Steam、EOS、PlayStation Network 等）。它的主要目的是作为开发和测试的占位符，让开发者在没有真实平台 SDK 或网络连接的情况下，依然能够构建、运行和测试游戏中的在线功能代码逻辑（例如大厅、成就、排行榜接口）。它提供了一个符合 `OnlineServices` 插件接口的框架，但所有功能都是本地模拟或静默成功。

## 使用场景

- 你在开发一个需要多人在线功能的游戏（如大厅、匹配、成就、排行榜），但你目前没有集成任何真实的第三方在线平台 SDK，或者希望在离线环境下进行开发和调试。
- 你在编写针对在线服务接口的单元测试或自动化测试，需要一个不会触发实际网络请求的“桩”（Stub）实现。
- 你希望在 CI/CD 流水线中验证游戏编译和基本功能，而不需要配置复杂的平台凭据。

## 蓝图用法

该插件主要作为底层服务提供者，不直接暴露高层蓝图节点。游戏逻辑通过 `GetOnlineServices` 获取服务实例，然后调用 `Lobbies`、`Achievements` 等具体接口的方法。使用 `OnlineServicesNull` 时，这些调用会静默成功或返回模拟数据。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Online Services` | 获取当前在线服务实例，当配置为 Null 时返回 `FOnlineServicesNull` | `UOnlineServicesSubsystem` |

### 使用示例（蓝图描述）

1.  在“项目设置” -> “Online” -> “Online Services”中，将 `Service Name` 设置为 `Null`（或通过命令行参数 `-OnlineService=Null` 强制指定）。
2.  在蓝图中，正常使用 `Get Online Services` 节点，后续的 `Create Lobby`、`Query Achievements` 等节点调用将由 `OnlineServicesNull` 处理。在开发环境下，这些操作通常会立即返回成功。

## C++ 用法

`OnlineServicesNull` 通常不需要被游戏代码直接实例化或调用。游戏代码通过 `Online` 模块的抽象接口（如 `FLobbies`、`FAchievements`）进行操作，由底层系统根据配置选择 `OnlineServicesNull` 作为具体实现。

### 头文件引入

```cpp
#include "Online/OnlineServicesNull.h"
```

### 基本用法

一般不会直接使用此头文件。你的代码应依赖于通用的 `OnlineServices` 接口。以下展示了在测试或配置中如何强制使用 Null 实现：

```cpp
// 来源：通常由引擎配置驱动，无需手动编写
// 在 DefaultEngine.ini 中配置：
// [OnlineServices]
// ServiceName=Null

// 或者在代码中启动时指定
// FCommandLine::Append(TEXT(" -OnlineService=Null"));
```

### 进阶用法

在编写针对在线接口的自动化测试时，可以确保测试在 Null 服务下运行，避免外部依赖：

```cpp
// 来源：假设的测试场景，参考了通用测试模式
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMyLobbyTest, "MyGame.Online.Lobbies.CreateAndJoin", EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)

bool FMyLobbyTest::RunTest(const FString& Parameters)
{
    // 确保使用 Null 服务（通常通过全局配置或测试 fixture 设置）
    // ...

    // 获取 Lobbies 接口
    UE::Online::FLobbies* LobbiesInterface = UE::Online::GetServices<UE::Online::FLobbies>();
    if (!LobbiesInterface) return false;

    // 创建大厅参数
    UE::Online::FCreateLobby::Params CreateParams;
    // ... 设置参数 ...

    // 调用创建，注意：在 Null 实现下，这是一个本地操作
    TOnlineAsyncOpHandle<UE::Online::FCreateLobby> Handle = LobbiesInterface->CreateLobby(MoveTemp(CreateParams));

    // 在测试中同步等待或检查结果
    // ...
    return true;
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何通过配置和代码确保使用 `OnlineServicesNull`。此示例本身不包含业务逻辑，仅演示配置和获取过程。

```cpp
// MyOnlineTestGameMode.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyOnlineTestGameMode.generated.h"

UCLASS()
class AMyOnlineTestGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage) override;
};

// MyOnlineTestGameMode.cpp
#include "MyOnlineTestGameMode.h"
#include "Online/OnlineServices.h"
#include "Online/OnlineServicesNull.h"

void AMyOnlineTestGameMode::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
    Super::InitGame(MapName, Options, ErrorMessage);

    // 检查当前激活的在线服务是否是 Null 实现
    UE::Online::FOnlineServices* Services = UE::Online::GetServices();
    if (Services)
    {
        UE::Online::EOnlineServices Provider = Services->GetServicesProvider();
        if (Provider == UE::Online::EOnlineServices::Null)
        {
            UE_LOG(LogTemp, Warning, TEXT("Running with OnlineServicesNull. Online features are simulated locally."));
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Running with real online service: %s"), *UEnum::GetValueAsString(Provider));
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineServices` | 提供在线服务的基础接口和通用实现框架 |
| `OnlineSubsystem` | 传统在线子系统框架，该插件作为其新旧架构的桥梁之一 |
| `OnlineSubsystemUtils` | 提供在线子系统相关的工具类和函数 |

*注：该插件的 `Build.cs` 文件还声明了对 `ApplicationCore` 的依赖，但这属于引擎内部的基础设施依赖，对插件使用者透明。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `4ad1dbcc` | [OnlineSubsystem][OnlineServices] Guard SetPort callers against bogus port values from EOS:<PUID> ad | 防御性编程：修复处理来自 EOS 的无效端口值时的潜在问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 统一日志宏：将 UE_LOG 迁移到新的 UE_LOGF 格式 |
| 2026-03-03 | `96eff92b` | Compile fixes for programs that do not compile against Application Core and/or Engine. | 编译修复：解决不依赖 ApplicationCore 或 Engine 的程序编译问题 |
| 2026-02-19 | `97c6b63f` | Export FOnlineLobbyIdRegistryNull | API 导出：导出大厅 ID 注册表类 |
| 2025-09-16 | `307b1f67` | OSSv2: Adding PSN Stats interface and changes in PS5 UDS and Achievements | 功能扩展：为在线服务v2架构添加 PSN 统计接口及相关改动 |

### 维护评价

`OnlineServicesNull` 插件创建于2022年，是UE5 新在线服务架构 (`OnlineServices`) 的一部分，用于取代传统的 `OnlineSubsystem`。从 Git 记录看，插件仍处于**维护中**状态，近期（2026年）有持续的提交，但改动主要集中在**编译修复、防御性编程、代码风格统一和小范围API调整**上，没有大的功能迭代或架构变化。

这是一个基础性、框架性的插件，其稳定性比新特性更重要。它作为开发和测试的基石，被 Epic Games 自身和大量项目使用。虽然更新频率不高，但未发现废弃迹象，且最近的提交确保了其在新引擎版本中的兼容性。

**推荐在开发测试阶段使用**。不建议在最终发布版本中启用此插件（除非有特殊需求，如模拟离线模式），因为它不提供真实的网络功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServicesNull)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/online-services-in-unreal-engine/)（UE5 在线服务概述）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServices/Tests)（注意：测试通常在上一级的 `OnlineServices` 插件目录下）