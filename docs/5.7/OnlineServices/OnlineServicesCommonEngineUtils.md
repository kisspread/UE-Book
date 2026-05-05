# Online Services

> Shared code for interacting with online services implementations.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesInterface` (Runtime), `OnlineServicesCommon` (Runtime), `OnlineServicesCommonEngineUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-06-24 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServices) | |

## 用途

`OnlineServices` 插件是 Unreal Engine 5 中用于与在线服务交互的新一代架构。它旨在取代旧的 `OnlineSubsystem` 架构，提供一个更清晰、更模块化、更易于测试的抽象层。该插件的核心是定义了一套统一的接口（`OnlineServicesInterface`），用于访问各种在线功能（如会话、好友、排行榜、成就等），而具体的平台实现（如 Steam、EOS、PlayStation Network 等）则通过这些接口进行对接。

`OnlineServicesCommonEngineUtils` 模块是此架构中的一个辅助模块，主要提供与 Unreal Engine 引擎系统（如网络驱动、世界上下文）集成的实用工具类，帮助在线服务实现更好地与引擎功能协同工作。

## 使用场景

- 你正在开发一款需要跨平台在线功能（如多人游戏、排行榜、成就）的游戏，并希望使用 UE5 推荐的最新架构。
- 你需要一个比旧 `OnlineSubsystem` 更易于单元测试和模拟的在线服务层。
- 你正在为自定义平台或服务编写在线服务实现，需要遵循 UE5 的标准接口。
- 你的在线服务实现需要与引擎的网络系统（NetDriver）或编辑器世界上下文（PIE）进行深度集成。

## 蓝图用法

`OnlineServicesCommonEngineUtils` 模块主要提供底层的 C++ 工具类，其公开的 API 主要面向引擎开发者和在线服务实现者，而非直接面向游戏逻辑蓝图。该模块没有暴露 `BlueprintCallable` 函数。

核心的在线服务蓝图节点（如创建会话、查找好友）通常由具体的平台实现插件（如 `OnlineServicesNull`、`OnlineServicesEOS`）或上层游戏框架提供。`OnlineServices` 插件本身主要定义了接口和基础实现。

## C++ 用法

### 头文件引入

```cpp
#include "Online/OnlineServicesCommonEngineUtils.h"
#include "Online/WorldContextScopedObjectCache.h"
#include "Online/SessionsLAN.h"
```

### 基本用法：获取网络端口

`GetPortFromNetDriver` 函数用于从指定的网络驱动实例获取端口号，这在处理 LAN 会话或自定义网络逻辑时非常有用。

```cpp
// 来源: Engine/Plugins/Online/OnlineServices/Source/OnlineServicesCommonEngineUtils/Public/Online/OnlineServicesCommonEngineUtils.h
#include "Online/OnlineServicesCommonEngineUtils.h"

// 假设 InstanceName 是一个有效的网络驱动实例名称（例如，从配置或会话信息中获取）
FName InstanceName = TEXT("GameNetDriver");
int32 Port = UE::Online::GetPortFromNetDriver(InstanceName);
if (Port != 0)
{
    UE_LOG(LogTemp, Log, TEXT("Network driver port: %d"), Port);
}
```

### 进阶用法：管理世界上下文作用域的对象缓存

`FWorldContextScopedObjectCache` 是一个模板类，用于按世界上下文（例如，PIE 中的不同玩家窗口）缓存对象。它在编辑器中会自动清理与已结束的 PIE 世界相关的对象，非常适合管理在线服务连接或会话对象。

```cpp
// 来源: Engine/Plugins/Online/OnlineServices/Source/OnlineServicesCommonEngineUtils/Public/Online/WorldContextScopedObjectCache.h
#include "Online/WorldContextScopedObjectCache.h"

// 假设我们有一个在线服务连接对象
class FMyOnlineConnection
{
public:
    void Connect() { /* ... */ }
    void Disconnect() { /* ... */ }
};

// 创建一个缓存，键为世界上下文名称（FName），值为连接对象的共享指针
FWorldContextScopedObjectCache<FMyOnlineConnection> ConnectionCache;

// 在需要连接时，尝试查找或创建连接
FName WorldContextName = TEXT("PIE_0"); // 或 NAME_None 用于非 PIE 环境
TSharedPtr<FMyOnlineConnection> Connection = ConnectionCache.FindOrAdd(
    WorldContextName,
    []() -> TSharedRef<FMyOnlineConnection>
    {
        // 创建新连接的工厂函数
        TSharedRef<FMyOnlineConnection> NewConnection = MakeShared<FMyOnlineConnection>();
        NewConnection->Connect();
        return NewConnection;
    }
);

// 在测试或需要重置时，可以显式清除
ConnectionCache.Clear(WorldContextName);
```

### 进阶用法：实现 LAN 会话

`FSessionsLAN` 和相关类提供了局域网会话的基础实现。你可以继承它来创建自定义的 LAN 会话逻辑。

```cpp
// 来源: Engine/Plugins/Online/OnlineServices/Source/OnlineServicesCommonEngineUtils/Public/Online/SessionsLAN.h
#include "Online/SessionsLAN.h"

// 假设你有一个自定义的在线服务类
class FMyOnlineServices : public UE::Online::FOnlineServicesCommon
{
    // ... 其他实现
};

// 在你的服务初始化时，创建 LAN 会话管理器
class FMySessionsLAN : public UE::Online::FSessionsLAN
{
public:
    FMySessionsLAN(UE::Online::FOnlineServicesCommon& InServices)
        : FSessionsLAN(InServices)
    {
    }

protected:
    // 必须实现的纯虚函数，用于自定义会话数据的序列化
    virtual void AppendSessionToPacket(FNboSerializeToBuffer& Packet, const UE::Online::FSessionLAN& Session) override
    {
        // 将你的自定义会话数据写入网络包
        // Packet << Session.CustomData;
    }

    virtual void ReadSessionFromPacket(FNboSerializeFromBuffer& Packet, UE::Online::FSessionLAN& Session) override
    {
        // 从网络包读取你的自定义会话数据
        // Packet >> Session.CustomData;
    }
};

// 使用示例
void CreateLANSession()
{
    // 假设 Services 是你的 FMyOnlineServices 实例
    FMyOnlineServices* Services = GetMyOnlineServices();
    TSharedRef<FMySessionsLAN> Sessions = MakeShared<FMySessionsLAN>(*Services);

    // 调用创建会话的接口
    UE::Online::FCreateSession::Params CreateParams;
    // ... 填充参数
    Sessions->CreateSession(CreateParams).Then([](UE::Online::TOnlineResult<UE::Online::FCreateSession> Result)
    {
        if (Result.IsOk())
        {
            UE_LOG(LogTemp, Log, TEXT("LAN Session Created Successfully"));
        }
    });
}
```

## Demo 示例

以下是一个使用 `FWorldContextScopedObjectCache` 管理按世界上下文缓存的在线服务对象的最小示例。

**MyOnlineServiceCache.h**
```cpp
#pragma once

#include "Online/WorldContextScopedObjectCache.h"
#include "Templates/SharedPointer.h"

// 一个简单的在线服务对象示例
class FMyCachedOnlineService
{
public:
    FMyCachedOnlineService(FName InContextName) : ContextName(InContextName)
    {
        UE_LOG(LogTemp, Log, TEXT("Online Service created for context: %s"), *ContextName.ToString());
    }

    ~FMyCachedOnlineService()
    {
        UE_LOG(LogTemp, Log, TEXT("Online Service destroyed for context: %s"), *ContextName.ToString());
    }

    void DoSomething()
    {
        UE_LOG(LogTemp, Log, TEXT("Doing something in context: %s"), *ContextName.ToString());
    }

private:
    FName ContextName;
};

// 全局或单例的缓存管理器
class FMyOnlineServiceCacheManager
{
public:
    static FMyOnlineServiceCacheManager& Get()
    {
        static FMyOnlineServiceCacheManager Instance;
        return Instance;
    }

    TSharedPtr<FMyCachedOnlineService> GetServiceForContext(FName ContextName)
    {
        return Cache.FindOrAdd(ContextName, [ContextName]()
        {
            return MakeShared<FMyCachedOnlineService>(ContextName);
        });
    }

private:
    FWorldContextScopedObjectCache<FMyCachedOnlineService> Cache;
};
```

**MyGameMode.cpp (使用示例)**
```cpp
#include "MyOnlineServiceCache.h"
#include "GameFramework/GameModeBase.h"

class AMyGameMode : public AGameModeBase
{
    virtual void StartPlay() override
    {
        Super::StartPlay();

        // 获取或创建当前世界上下文的服务对象
        // 在 PIE 中，每个玩家窗口会有不同的 ContextName
        FName CurrentContext = GetWorld()->GetFName();
        TSharedPtr<FMyCachedOnlineService> Service = FMyOnlineServiceCacheManager::Get().GetServiceForContext(CurrentContext);

        if (Service.IsValid())
        {
            Service->DoSomething();
        }
    }
};
```

**Build.cs 依赖**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "OnlineServicesCommonEngineUtils" // 依赖本模块
});
```

## 模块依赖

要使用 `OnlineServicesCommonEngineUtils` 模块，你的模块需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `OnlineServicesCommon` | 提供在线服务的通用基础实现，如 `FOnlineServicesCommon`、`FSessionsCommon`。 |
| `OnlineServicesInterface` | 定义在线服务的核心接口（如 `ISessions`）。 |

## 维护状态

### 近期更新

1.  `df8141fcf024` (2024-07-19): 为 `FWorldContextScopedObjectCache` 添加了显式的 `Clear` 方法，以支持底层测试的精细控制。
    *   **解读**: 这是对缓存类功能的增强，提高了其在自动化测试场景下的可用性，表明该模块仍在积极维护和改进。
2.  `dc31d7344441` (2024-07-18): 将 DLL 存储从类型移到方法/变量。这是为了支持合并模块（Merged Modules）功能。
    *   **解读**: 这是一个底层的架构调整，旨在适应 UE 构建系统的新特性，确保插件在未来的引擎版本中兼容。
3.  `301de635ebbb` (2024-07-17): 更新 LAN 会话和加入会话测试。改进了 `TryHostLANSession` 的 API 以使用 `TValueOrError`，简化了会话创建流程，并修复了测试中的等待时间问题。
    *   **解读**: 这是对 LAN 会话功能的实质性更新和优化，包括 API 设计改进、逻辑简化和测试用例完善，表明该功能模块处于活跃开发中。

### 维护评价

`OnlineServices` 插件是 UE5 在线功能的核心架构，创建于 2021 年，相对较新。从近期的 git 历史来看，该插件（特别是 `OnlineServicesCommonEngineUtils` 模块）在 2024 年 7 月仍有频繁且实质性的更新，包括功能增强、架构调整和测试完善，表明它处于**活跃维护**状态。

需要注意的是，该插件在 `.uplugin` 中默认设置为 `EnabledByDefault: false`，这意味着它可能仍被视为实验性或需要特定配置才能启用。它为新的在线服务实现提供了基础，但具体的平台实现（如 EOS、Steam）可能需要额外的插件。

**推荐使用**：如果你正在基于 UE5 开发新的多人游戏或需要在线功能，并且希望采用最新、最可维护的架构，那么 `OnlineServices` 是推荐的选择。但请注意，它可能需要更多的初始设置，并且某些功能可能仍在完善中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServices)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServices/Tests) (如果存在)