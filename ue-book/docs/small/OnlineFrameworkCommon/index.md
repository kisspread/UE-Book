# Online Framework Common

> Common functionality for Online Frameworks

| 属性 | 值 |
|---|---|
| 分类 | Online |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | `CanContainContent: true` |
| 模块 | `OnlineFrameworkCommon` (Runtime) |
| 创建时间 | 2025-07-17 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFrameworkCommon) | |

> ⚠️ **Beta / 实验性**: 此插件 `IsBetaVersion: true`，API 可能在未来版本中发生变化。

## 用途

OnlineFrameworkCommon 是 UE5 **新旧 Online 系统之间的桥梁层**。UE 的在线服务正在从旧版 `OnlineSubsystem` (V1) 迁移到新版 `OnlineServices` (V2)，但这个迁移不是一蹴而就的——很多项目和引擎子系统仍然同时使用两套 API。

这个插件解决的核心问题是：**如何在同一个玩家身上统一管理来自不同 Online 框架的多个 Account ID？**

具体来说，它提供：

1. **`FCommonAccount`** — 一个"通用账户"对象，内部持有多个框架的 Account ID（如 Steam 的 V2 `FAccountId` 和旧版 `FUniqueNetId`），通过异步查找机制自动关联。
2. **`FCommonAccountManager`** — 管理所有 `FCommonAccount` 的生命周期、查找注册和冲突解决（当发现两个 CommonAccount 其实是同一个玩家时会自动合并）。
3. **`FCommonConfig`** — 配置系统，通过 INI 配置将"框架实例名称"（如 `DefaultPlatform`）映射到具体的 `OnlineServices` 类型和实例，支持按上下文类型（Client/Server/Editor）区分配置。
4. **`CommonAccountUtils`** — V1/V2 之间的 ID 互转工具函数。

简单说：如果你的游戏需要同时支持新旧两套 Online 系统，或者你需要一个统一的方式来处理跨平台账号关联，这个插件就是为此而设计的。

## 使用场景

- 你的项目从旧版 `OnlineSubsystem` 迁移到新版 `OnlineServices`，但中间过渡期两套系统共存 → 用这个插件统一管理玩家身份
- 你需要让一个玩家同时拥有 Steam (V2) 和旧版 OSS (V1) 的账号 ID，并在代码中通过一个统一对象访问 → 用 `FCommonAccount`
- 你在做 PIE 多人测试，需要为每个 PIE 实例维护独立的 Online 配置 → `FCommonConfig` 通过 `WorldContextName` 自动区分
- 你正在为引擎编写一个需要兼容新旧 Online 系统的子系统（如 Session、Friends） → 依赖此插件作为基础设施

## 蓝图用法

此插件为纯 C++ Runtime 模块，**不暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性**。所有 API 均为 C++ 层面使用。

## C++ 用法

### 头文件引入

```cpp
#include "OnlineFramework/CommonAccount.h"
#include "OnlineFramework/CommonAccountManager.h"
#include "OnlineFramework/CommonAccountUtils.h"
#include "OnlineFramework/CommonConfig.h"
```

所有类位于 `UE::OnlineFramework` 命名空间下。

### 基本用法：获取 CommonAccountManager 并创建账户

`FCommonAccountManager` 通过 `FCommonConfig` 获取，内部按 WorldContext 缓存，无需手动管理生命周期。

```cpp
using namespace UE::OnlineFramework;

// 创建配置（通常从 UObject 自动推断上下文）
FCommonConfig Config(MyUObject);  // 隐式构造，自动判断 Client/Server/Editor

// 获取（或创建）AccountManager —— 同一 WorldContext 下全局唯一
FCommonAccountManagerPtr AccountManager = FCommonAccountManager::Get(Config);
if (!AccountManager)
{
    return;
}

// 根据已知的 V2 AccountId 获取或创建一个 CommonAccount
UE::Online::FAccountId AccountId = /* 从 OnlineServices 获取 */;
FCommonAccountPtr Account = AccountManager->GetAccount(AccountId, TEXT("DefaultPlatform"));
```

> 来源：`CommonAccountManager.cpp` 中 `GetAccount()` 和 `Get()` 的实现

### 基本用法：异步查找跨框架 Account ID

当你只知道某个框架的 Account ID，想获取另一个框架的对应 ID 时，使用异步查找：

```cpp
// 假设已有一个持有 Steam AccountId 的 CommonAccount
FCommonAccountRef Account = /* ... */;

// 异步查找该账户在 "EOS" 框架下的 AccountId
Account->GetIdAsync(TEXT("EOS"), FCommonAccount::FOnGetIdAsyncComplete::CreateLambda(
    [](const FCommonAccountRef& ResolvedAccount, UE::Online::FAccountId FoundId)
    {
        if (FoundId.IsValid())
        {
            // 成功找到对应的 EOS AccountId
            UE_LOG(LogTemp, Log, TEXT("Found EOS AccountId: %s"), *UE::Online::ToLogString(FoundId));
        }
    }
));
```

> 来源：`CommonAccount.cpp` 中 `GetIdAsync()` 实现

### 进阶用法：注册自定义 AccountId 查找函数

`FCommonAccountManager` 支持注册自定义的查找链。当 `GetIdAsync` 在缓存中找不到目标框架的 ID 时，会依次调用所有注册的查找函数：

```cpp
// 注册一个查找函数，返回 RAII Handle（销毁时自动取消注册）
FCommonAccountLookupAccountIdFnHandle LookupHandle = AccountManager->RegisterAccountIdLookup(
    TEXT("MyCustomLookup"),
    FCommonAccountLookupAccountIdFn([](FCommonAccount& Account, FName RequestingInstance, const FCommonConfigInstance& ConfigInstance) -> TFuture<UE::Online::FAccountId>
    {
        // 你可以在这里查询数据库、调用第三方 API 等
        UE::Online::FAccountId ResultId = /* 查找逻辑 */;
        TPromise<UE::Online::FAccountId> Promise;
        auto Future = Promise.GetFuture();
        Promise.SetValue(ResultId);
        return Future;
    })
);

// Handle 离开作用域时自动 Unbind
```

> 来源：`CommonAccountManager.cpp` 中 `RegisterAccountIdLookup()` 实现

### 进阶用法：监听账户生命周期事件

```cpp
AccountManager->OnCommonAccountCreated().AddLambda(
    [](const FCommonAccountRef& NewAccount)
    {
        UE_LOG(LogTemp, Log, TEXT("New CommonAccount created: %s"), *NewAccount->ToLogString());
    }
);

AccountManager->OnCommonAccountDuplicateDetected().AddLambda(
    [](const FCommonAccountRef& KeptAccount, const FCommonAccountRef& RemovedAccount)
    {
        // 两个账户被发现是同一个玩家，需要更新引用
        UE_LOG(LogTemp, Warning, TEXT("Account merged: %s replaced by %s"),
            *RemovedAccount->ToLogString(), *KeptAccount->ToLogString());
    }
);
```

> 来源：`CommonAccountManager.h` 中声明的三个事件：`OnCommonAccountCreated`、`OnCommonAccountIdAdded`、`OnCommonAccountDuplicateDetected`

### 进阶用法：V1/V2 ID 互转

```cpp
using namespace UE::OnlineFramework;

FCommonConfig Config(MyContextObject);

// V1 → V2
FUniqueNetIdPtr V1Id = /* 旧版 ID */;
UE::Online::FAccountId V2Id = GetAccountV2FromV1(Config, V1Id, TEXT("DefaultPlatform"));

// V2 → V1
FCommonAccountRef Account = /* ... */;
FUniqueNetIdPtr ConvertedV1Id = GetV1FromCommonAccount(Account, TEXT("DefaultPlatform"));

// 从任意 ID 获取 CommonAccount
FCommonAccountPtr AccountFromV1 = GetCommonAccountFromV1(Config, V1Id, TEXT("DefaultPlatform"));
FCommonAccountPtr AccountFromV2 = GetCommonAccountFromV2(Config, V2Id, TEXT("DefaultPlatform"));
```

> 来源：`CommonAccountUtils.cpp`

## 配置

框架实例通过 Game.ini 配置，节名为 `[OnlineFrameworkCommonConfig]`：

```ini
[OnlineFrameworkCommonConfig]
+Instances=(Name=DefaultPlatform, OnlineServices=EOS, ConfigInstance=Default)
+Instances=(Name=DefaultPlatform, OnlineServices=Null, Type=Client)
+Instances=(Name=SteamPlatform, OnlineServices=Steam)
```

格式说明：
- `Name`（必需）— 框架实例名称，代码中通过此名称引用
- `OnlineServices`（必需）— OnlineServices 类型，如 `EOS`、`Steam`、`Null`、`GooglePlay` 等
- `ConfigInstance`（可选）— OnlineServices 实例配置名，默认为 `NAME_None`
- `Type`（可选）— 上下文类型：`Default`、`Client`、`Server`、`Editor`，默认 `Default`

`FCommonConfig` 查找时会先按 `Name + Type` 匹配，找不到则回退到 `Name + Default`。

> 来源：`CommonModule.cpp` 中 `UpdateFromConfig()` 实现

## Demo 示例

以下是一个最小完整示例，展示如何获取 AccountManager 并通过 V2 ID 获取 CommonAccount：

```cpp
// MyOnlineComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "MyOnlineComponent.generated.h"

UCLASS()
class UMyOnlineComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    void OnLoginComplete(UE::Online::FAccountId AccountId);
};
```

```cpp
// MyOnlineComponent.cpp
#include "MyOnlineComponent.h"
#include "OnlineFramework/CommonAccount.h"
#include "OnlineFramework/CommonAccountManager.h"
#include "OnlineFramework/CommonConfig.h"

using namespace UE::OnlineFramework;

void UMyOnlineComponent::BeginPlay()
{
    Super::BeginPlay();

    // FCommonConfig 隐式从 UObject 构造，自动推断 Client/Server/Editor 上下文
    FCommonConfig Config(this);
    FCommonAccountManagerPtr Manager = FCommonAccountManager::Get(Config);
    if (!Manager)
    {
        UE_LOG(LogTemp, Warning, TEXT("OnlineFrameworkCommon plugin not loaded"));
        return;
    }

    // 监听账户合并事件
    Manager->OnCommonAccountDuplicateDetected().AddUObject(this, &UMyOnlineComponent::OnAccountMerged);
}

void UMyOnlineComponent::OnLoginComplete(UE::Online::FAccountId AccountId)
{
    FCommonConfig Config(this);
    FCommonAccountManagerPtr Manager = FCommonAccountManager::Get(Config);
    if (!Manager || !AccountId.IsValid())
    {
        return;
    }

    // 获取或创建 CommonAccount
    FCommonAccountPtr Account = Manager->GetAccount(AccountId, TEXT("DefaultPlatform"));
    if (Account)
    {
        UE_LOG(LogTemp, Log, TEXT("CommonAccount: %s"), *Account->ToLogString());
    }
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "OnlineFrameworkCommon" });
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreOnline` | Online 基础类型（`FAccountId`、`FUniqueNetId`） |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（World、Config 等） |
| `OnlineServicesCommonEngineUtils` | (Private) OnlineServices 引擎工具 |
| `OnlineServicesInterface` | (Private) OnlineServices 接口定义 |
| `OnlineServicesNull` | (Private) Null 实现（测试用） |
| `OnlineServicesOSSAdapter` | (Private) V1→V2 适配器 |
| `OnlineSubsystem` | (Private) 旧版 Online 子系统 |

使用此插件时，你的模块只需 `PublicDependencyModuleNames` 添加 `"OnlineFrameworkCommon"` 即可。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-23 | `7c8aa0f8530a` | Use the source account id framework instance name to get the common account + Add checks to CommonAccountManager | 修复了账号 ID 框架实例名使用错误的问题，增加了 Manager 层面的校验 |
| 2025-09-23 | `2966788188ea` | Merge conflict from 45968147. File moved in 37.50 | 合并冲突解决，文件路径调整 |
| 2025-07-21 | `cc8ea09e30bc` | Make FCommonAccount::AddId go through the resolved account | 修复了 stale CommonAccount 自行注册到 Manager 的 bug |

### 维护评价

- **创建时间**: 2025-07-17，非常年轻的插件（不到 1 年）
- **状态**: **实验性 / Beta**（`IsBetaVersion: true`，`EnabledByDefault: false`）
- **活跃度**: 活跃维护中，最近 2 个月内有多次实质性 bug 修复
- **风险**: 作为 Beta 插件，API 稳定性没有保证。`PickBestAccount` 函数中留有 `// TODO` 注释，说明冲突解决算法可能尚未最终确定
- **推荐**: 如果你正在做 Online 系统迁移，可以关注并开始集成，但要注意 API 可能变化。不建议在生产环境中作为核心依赖使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFrameworkCommon)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
