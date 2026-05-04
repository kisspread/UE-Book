# Online Services

> Shared code for interacting with online services implementations.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesInterface` (Runtime), `OnlineServicesCommon` (Runtime), `OnlineServicesCommonEngineUtils` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-06-24 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServices) | |

## 用途

`OnlineServices` 插件是 Unreal Engine 5 中用于与各种在线服务（如 EOS、Steam、PlayStation Network、Xbox Live 等）进行交互的**统一抽象层和通用实现框架**。它并非一个具体的在线服务实现，而是定义了一套标准化的接口（`IAuth`, `ISessions`, `ISocial` 等），并提供了这些接口的通用（Common）实现逻辑。

**核心目的**是解决多平台适配的复杂性。开发者可以使用一套与平台无关的 API 来编写游戏逻辑，而具体的平台实现（如 `OnlineServicesEOS`）只需继承并实现这些接口。该插件还提供了组件化架构、异步操作管理、配置加载、控制台命令调试等基础设施，极大地简化了在线功能的开发和维护。

## 使用场景

- **开发需要跨平台在线功能的游戏**：例如，需要统一的用户认证、好友列表、排行榜、会话管理等功能，且希望代码能轻松适配不同平台。
- **构建自定义的在线服务后端**：如果你的服务不直接对应 Epic 支持的平台，可以基于此框架实现自己的 `IOnlineServices`。
- **需要高级在线功能**：如大厅（Lobbies）、成就、统计数据、用户文件、商城等，并希望使用经过良好设计的异步 API。
- **调试和测试在线功能**：插件内置了强大的控制台命令系统，可以方便地模拟和测试各种在线操作。

## 蓝图用法

此插件主要为 C++ 框架，蓝图可直接调用的函数较少，主要集中在 `OnlineServicesCommonEngineUtils` 模块中提供的工具函数。核心的在线服务接口（如 `IAuth`）通常通过 C++ 代码访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Online Services` | 获取指定实例名称的在线服务实例 | `UOnlineServicesEngineUtils` |
| `Get Auth Interface` | 从在线服务实例获取认证接口 | `UOnlineServicesEngineUtils` |
| `Get User Info Interface` | 从在线服务实例获取用户信息接口 | `UOnlineServicesEngineUtils` |
| `Get Sessions Interface` | 从在线服务实例获取会话接口 | `UOnlineServicesEngineUtils` |

### 使用示例（蓝图描述）

1.  **获取在线服务实例**：使用 `Get Online Services` 节点，传入实例名称（如 `DefaultInstance`）来获取一个 `UOnlineServices` 对象。
2.  **获取特定接口**：从上一步的对象，使用 `Get Auth Interface` 等节点获取具体的接口对象。
3.  **调用接口方法**：虽然大部分接口方法是 C++ 异步的，但蓝图可以通过 `UOnlineServicesEngineUtils` 中的辅助函数或通过 C++ 暴露的蓝图可调用函数来使用部分功能。例如，查询用户信息可能需要先通过 C++ 代码发起异步请求，然后通过委托将结果返回给蓝图。

## C++ 用法

### 头文件引入

```cpp
#include "Online/OnlineServices.h"
#include "Online/Auth.h"
#include "Online/Sessions.h"
// 根据需要引入其他接口头文件，如 Online/Social.h, Online/Presence.h 等
```

### 基本用法

以下示例展示了如何获取在线服务实例并执行用户登录。

```cpp
// 来源：基于 OnlineServicesCommon.h 和 AuthCommon.h 的典型用法
#include "Online/OnlineServices.h"
#include "Online/Auth.h"

void AMyGameMode::LoginUser()
{
    // 1. 获取默认的在线服务实例
    UE::Online::IOnlineServicesPtr OnlineServices = UE::Online::GetServices();
    if (!OnlineServices.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get online services instance."));
        return;
    }

    // 2. 获取认证接口
    UE::Online::IAuthPtr AuthInterface = OnlineServices->GetAuthInterface();
    if (!AuthInterface.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get auth interface."));
        return;
    }

    // 3. 构造登录参数
    UE::Online::FAuthLogin::Params LoginParams;
    LoginParams.PlatformUserId = FPlatformMisc::GetPlatformUserForUserIndex(0); // 获取第一个本地用户的平台ID
    // LoginParams.CredentialsType = ...; // 根据平台设置凭证类型
    // LoginParams.Credentials = ...; // 设置凭证（如用户名密码、Token等）

    // 4. 发起异步登录操作
    UE::Online::TOnlineAsyncOpHandle<UE::Online::FAuthLogin> LoginOpHandle = AuthInterface->Login(MoveTemp(LoginParams));

    // 5. 绑定完成回调
    LoginOpHandle->OnComplete().AddWeakLambda(this, [this](const UE::Online::TOnlineAsyncOp<UE::Online::FAuthLogin>& Op, const UE::Online::TOnlineResult<UE::Online::FAuthLogin>& Result)
    {
        if (Result.IsOk())
        {
            const UE::Online::FAuthLogin::Result& LoginResult = Result.GetOkValue();
            UE_LOG(LogTemp, Log, TEXT("Login successful! AccountId: %s"), *LoginResult.AccountId.ToString());
            // 登录成功后的逻辑，例如获取本地用户信息
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Login failed: %s"), *Result.GetErrorValue().GetLogMessage());
        }
    });
}
```

### 进阶用法

**创建自定义在线服务组件**：
你可以继承 `TOnlineComponent` 来创建自己的在线服务功能模块，并将其注册到 `FOnlineServicesCommon` 中。

```cpp
// 来源：基于 OnlineComponent.h 和 OnlineServicesCommon.h 的扩展模式
#include "Online/OnlineComponent.h"
#include "Online/OnlineServicesCommon.h"

// 1. 定义你的接口（通常在单独的头文件中）
class IMyCustomService : public UE::Online::IOnlineInterface
{
public:
    virtual UE::Online::TOnlineAsyncOpHandle<UE::Online::FMyCustomOp> DoSomething(UE::Online::FMyCustomOp::Params&& Params) = 0;
};

// 2. 实现通用逻辑（Common 实现）
class FMyCustomServiceCommon : public UE::Online::TOnlineComponent<IMyCustomService>
{
public:
    using Super = IMyCustomService;

    FMyCustomServiceCommon(UE::Online::FOnlineServicesCommon& InServices)
        : TOnlineComponent<IMyCustomService>(TEXT("MyCustomService"), InServices)
    {
    }

    virtual void RegisterCommands() override
    {
        // 注册控制台命令，例如：OnlineServices MyCustomService DoSomething ...
    }

    virtual UE::Online::TOnlineAsyncOpHandle<UE::Online::FMyCustomOp> DoSomething(UE::Online::FMyCustomOp::Params&& Params) override
    {
        // 创建异步操作
        UE::Online::TOnlineAsyncOpRef<UE::Online::FMyCustomOp> Op = GetOp<UE::Online::FMyCustomOp>(MoveTemp(Params));

        // 设置执行策略（例如在游戏线程执行）
        Op->SetThen(UE::Online::FOnlineAsyncExecutionPolicy::RunOnGameThread(), [this, WeakOp = Op.ToWeakPtr()]()
        {
            TSharedPtr<UE::Online::TOnlineAsyncOp<UE::Online::FMyCustomOp>> PinnedOp = WeakOp.Pin();
            if (PinnedOp.IsValid())
            {
                // ... 执行你的自定义逻辑 ...
                // 完成操作
                PinnedOp->SetResult(UE::Online::FMyCustomOp::Result{});
            }
        });

        return Op->GetHandle();
    }
};

// 3. 在你的 FOnlineServicesCommon 子类中注册该组件
class FMyOnlineServices : public UE::Online::FOnlineServicesCommon
{
public:
    // ... 构造函数等 ...

    virtual void RegisterComponents() override
    {
        FOnlineServicesCommon::RegisterComponents();
        // 注册你的自定义组件
        Components.Register<FMyCustomServiceCommon>(*this);
    }
};
```

## Demo 示例

一个最小的可编译示例，展示如何集成并调用 `OnlineServices` 的认证接口。

**MyOnlineGame.Build.cs**
```csharp
using UnrealBuildTool;

public class MyOnlineGame : ModuleRules
{
    public MyOnlineGame(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "OnlineServices", // 依赖主插件模块
            "OnlineServicesCommon" // 依赖通用实现模块
        });
    }
}
```

**MyOnlineGameMode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "Online/OnlineAsyncOpHandle.h"
#include "MyOnlineGameMode.generated.h"

namespace UE::Online
{
    struct FAuthLogin;
}

UCLASS()
class MYONLINEGAME_API AMyOnlineGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "Online")
    void LoginWithDefaultUser();

private:
    void OnLoginComplete(const UE::Online::TOnlineAsyncOp<UE::Online::FAuthLogin>& Op, const UE::Online::TOnlineResult<UE::Online::FAuthLogin>& Result);
};
```

**MyOnlineGameMode.cpp**
```cpp
#include "MyOnlineGameMode.h"
#include "Online/OnlineServices.h"
#include "Online/Auth.h"

void AMyOnlineGameMode::BeginPlay()
{
    Super::BeginPlay();
    // 可以在游戏开始时尝试自动登录
    // LoginWithDefaultUser();
}

void AMyOnlineGameMode::LoginWithDefaultUser()
{
    UE::Online::IOnlineServicesPtr OnlineServices = UE::Online::GetServices();
    if (!OnlineServices.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Online Services not available."));
        return;
    }

    UE::Online::IAuthPtr Auth = OnlineServices->GetAuthInterface();
    if (!Auth.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Auth interface not available."));
        return;
    }

    UE::Online::FAuthLogin::Params Params;
    Params.PlatformUserId = FPlatformMisc::GetPlatformUserForUserIndex(0);

    Auth->Login(MoveTemp(Params))->OnComplete().AddUObject(this, &AMyOnlineGameMode::OnLoginComplete);
}

void AMyOnlineGameMode::OnLoginComplete(const UE::Online::TOnlineAsyncOp<UE::Online::FAuthLogin>& Op, const UE::Online::TOnlineResult<UE::Online::FAuthLogin>& Result)
{
    if (Result.IsOk())
    {
        UE_LOG(LogTemp, Log, TEXT("Login Success! Account: %s"), *Result.GetOkValue().AccountId.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Login Failed: %s"), *Result.GetErrorValue().GetLogMessage());
    }
}
```

## 模块依赖

从 `OnlineServicesCommon.Build.cs` 分析，使用此插件通常需要依赖以下模块。由于其核心是提供在线服务的抽象和通用实现，依赖项多为在线相关的基础模块。

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 提供旧版在线子系统接口，用于兼容或特定平台实现 |
| `OnlineBase` | 提供在线服务的基础类型和接口定义（如 `IOnlineServices`） |
| `Json` | 用于配置文件的解析 |
| `HTTP` | 用于可能的网络请求（如 REST API 调用） |

## 维护状态

### 近期更新

1.  **`d4236eb0ff94`** (2024-05-15): `Expand the set of SectionHierarchies we read config from`
    *   **解读**：增强了配置系统的灵活性，允许从更多的配置层级（Section Hierarchy）读取设置，这对于复杂项目或多环境配置很有用。
2.  **`6137e676e296`** (2024-05-14): `Fix for Horde Android packaging error.`
    *   **解读**：修复了与 Epic 内部构建系统（Horde）相关的 Android 平台打包错误，属于平台兼容性修复。
3.  **`efe75f3d303c`** (2024-05-13): `Use a TTransactionallySafeSpscQueue`
    *   **解读**：将内部使用的队列替换为事务安全的单生产者单消费者队列（SPSC Queue），这通常是为了提升多线程环境下的性能和安全性。

### 维护评价

- **活跃维护**：插件创建于 2021 年，至今约 3 年。从最近的提交记录看，**仍在积极维护和更新**，最近的提交集中在 2024 年 5 月，内容涉及功能增强、平台兼容性修复和底层优化。
- **核心地位**：作为 UE5 在线服务的新一代标准框架，它被 Epic 官方用于 EOS 等服务的集成，因此有持续的维护动力。
- **实验性状态**：`.uplugin` 中 `EnabledByDefault: false` 表明它目前仍被视为实验性功能，可能意味着 API 在未来版本中仍有变动的可能。
- **推荐使用**：对于新项目，尤其是目标为多平台或需要使用 EOS 的项目，**强烈推荐使用此框架**。它提供了比旧版 `OnlineSubsystem` 更现代、更清晰的架构。但需注意其“实验性”标签，关注版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServices)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/online-services-in-unreal-engine/) (UE5 在线服务概述)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServices/Tests)