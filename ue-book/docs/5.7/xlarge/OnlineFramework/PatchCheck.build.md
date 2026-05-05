# Online Framework Plugin

> Shared code for interacting with online gameplay services.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Qos` (Runtime), `Party` (Runtime), `Lobby` (Runtime), `LoginFlow` (Runtime), `Hotfix` (Runtime), `PlayTimeLimit` (Runtime), `PatchCheck` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-12 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework) | |

## 用途

OnlineFramework 插件并非一个具体的在线服务实现（如 EOS 或 Steam），而是一个**通用的在线服务交互框架**。它提供了一套标准化的、可扩展的接口和子系统，用于处理在线游戏开发中常见的、与具体平台无关的通用功能。这些功能包括：玩家组队（Party）、大厅/房间管理（Lobby）、游戏补丁检查（PatchCheck）、网络质量探测（QoS）、登录流程（LoginFlow）、游戏时间限制（PlayTimeLimit）、热修复（Hotfix）以及重连（Rejoin）。

它的存在是为了解决一个核心问题：让游戏开发者能够以统一的方式实现复杂的在线功能，而无需为每个在线子系统（如 EOS、Steam、PSN、Xbox Live）重复编写大量样板代码。游戏可以依赖此框架提供的抽象接口，而具体的平台实现则由各个在线子系统插件提供。

## 使用场景

- 你正在开发一款需要**多人在线功能**（如组队、创建/加入房间、匹配）的游戏 → 使用 `Party` 和 `Lobby` 模块。
- 你的游戏需要**在启动时检查并强制玩家更新到最新版本** → 使用 `PatchCheck` 模块。
- 你需要**评估不同服务器或玩家之间的网络连接质量**以进行最佳匹配 → 使用 `Qos` 模块。
- 你的游戏需要实现一个**标准化的、可配置的登录流程**（如先显示隐私政策，再登录平台账号） → 使用 `LoginFlow` 模块。
- 你需要**限制未成年玩家的游戏时长**或实施防沉迷系统 → 使用 `PlayTimeLimit` 模块。
- 你的游戏需要**从服务器动态下载并应用配置或代码修复**，而无需重新发布整个游戏 → 使用 `Hotfix` 模块。
- 你的游戏支持**断线后重新加入同一局游戏** → 使用 `Rejoin` 模块。

## 蓝图用法

此插件主要为 C++ 设计，但部分模块（如 `PatchCheck`）通过其管理类暴露了蓝图可调用的函数。以下是从 `PatchCheck` 模块提取的核心蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Patch Check` | 获取全局唯一的 `FPatchCheck` 实例。 | `FPatchCheck` (静态函数) |
| `Start Patch Check` | 启动补丁检查流程。 | `FPatchCheck` |
| `Get Last Patch Check Result` | 获取上一次补丁检查的结果（`EPatchCheckResult` 枚举）。 | `FPatchCheck` |
| `Get On Complete` | 获取补丁检查完成时的委托（`FOnPatchCheckComplete`）。 | `FPatchCheck` |

### 使用示例（蓝图描述）

1.  **在游戏启动时检查补丁**：
    *   在你的 `GameInstance` 或 `PlayerController` 的 `BeginPlay` 事件中。
    *   调用 `Get Patch Check` 节点获取 `FPatchCheck` 对象。
    *   调用 `Start Patch Check` 节点。
    *   绑定 `Get On Complete` 返回的委托到一个自定义事件。
    *   在该自定义事件中，检查 `Result` 参数。如果是 `PatchRequired`，则可以显示一个提示框告知玩家需要更新游戏。

## C++ 用法

### 头文件引入

```cpp
#include "PatchCheck.h"
```

### 基本用法

以下代码展示了如何启动一次补丁检查并处理结果。

```cpp
// 在你的 GameInstance 或合适的初始化位置
#include "PatchCheck.h"

void UMyGameInstance::Init()
{
    Super::Init();

    // 获取全局 PatchCheck 实例
    FPatchCheck& PatchCheck = FPatchCheck::Get();

    // 绑定完成回调
    PatchCheck.GetOnComplete().AddUObject(this, &UMyGameInstance::OnPatchCheckComplete);

    // 启动检查
    PatchCheck.StartPatchCheck();
}

void UMyGameInstance::OnPatchCheckComplete(EPatchCheckResult Result)
{
    switch (Result)
    {
    case EPatchCheckResult::NoPatchRequired:
        UE_LOG(LogTemp, Log, TEXT("游戏版本最新，无需更新。"));
        // 继续正常游戏流程
        break;
    case EPatchCheckResult::PatchRequired:
        UE_LOG(LogTemp, Warning, TEXT("检测到新版本，需要更新。"));
        // 显示更新提示，或跳转到商店页面
        break;
    case EPatchCheckResult::NoLoggedInUser:
        UE_LOG(LogTemp, Error, TEXT("补丁检查需要已登录的用户。"));
        // 引导用户登录
        break;
    case EPatchCheckResult::PatchCheckFailure:
        UE_LOG(LogTemp, Error, TEXT("补丁检查失败。"));
        // 根据策略决定是重试还是继续（Fail Open）
        break;
    }
}
```

### 进阶用法

你可以通过继承 `FPatchCheck` 来实现自定义的补丁检查逻辑，并通过模块系统注册。

```cpp
// MyCustomPatchCheck.h
#pragma once
#include "PatchCheck.h"

class FMyCustomPatchCheck : public FPatchCheck
{
protected:
    // 重写平台特定的补丁检查逻辑
    virtual void StartPlatformOSSPatchCheck() override
    {
        // 实现你的自定义检查逻辑，例如调用特定的API
        // 完成后调用 PatchCheckComplete(EPatchCheckResult::NoPatchRequired);
    }
};

// MyCustomPatchCheckModule.h
#pragma once
#include "PatchCheckModule.h"

class FMyCustomPatchCheckModule : public TPatchCheckModule<FMyCustomPatchCheck>
{
    // 模块会自动处理实例化
};
```

然后在你的模块 `.Build.cs` 中依赖 `PatchCheck` 模块，并在 `.uplugin` 中注册你的模块。

## Demo 示例

以下是一个最小化的示例，展示如何在 `GameInstance` 中集成补丁检查。

**MyGameInstance.h**
```cpp
#pragma once
#include "Engine/GameInstance.h"
#include "PatchCheck.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;

private:
    UFUNCTION()
    void OnPatchCheckComplete(EPatchCheckResult Result);
};
```

**MyGameInstance.cpp**
```cpp
#include "MyGameInstance.h"
#include "PatchCheck.h"

void UMyGameInstance::Init()
{
    Super::Init();

    FPatchCheck& PatchCheck = FPatchCheck::Get();
    PatchCheck.GetOnComplete().AddUObject(this, &UMyGameInstance::OnPatchCheckComplete);
    PatchCheck.StartPatchCheck();
}

void UMyGameInstance::OnPatchCheckComplete(EPatchCheckResult Result)
{
    if (Result == EPatchCheckResult::PatchRequired)
    {
        // 在此处处理需要更新的情况，例如显示UI
        UE_LOG(LogTemp, Warning, TEXT("Game requires an update!"));
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("Patch check passed. Result: %s"), *LexToString(Result));
    }
}
```

## 模块依赖

使用此插件中的任何模块，你的项目模块通常需要依赖对应的在线子系统。具体依赖取决于你使用的功能。

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 所有在线功能的基础接口。使用 `Party`, `Lobby`, `Qos`, `LoginFlow`, `Rejoin` 等模块时必须依赖。 |
| `OnlineSubsystemUtils` | 提供在线子系统的实用工具函数。常与 `OnlineSubsystem` 一起使用。 |
| `Json` | `Hotfix` 模块可能用于解析热修复数据。 |
| `HTTP` | `Hotfix` 和 `PatchCheck` 模块可能用于从服务器获取更新信息。 |

**注意**：`PatchCheck` 模块本身可能还需要依赖特定的平台 SDK 模块（如 `OnlineSubsystemSteam`, `OnlineSubsystemEOS` 等）来执行实际的平台补丁检查。

## 维护状态

### 近期更新

```
- 82a11a817a0d Add an accessor for the result of the most recent patch check.
- 93a13080d9ef Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
- b18d4e011ee2 [PatchCheck] Fail open on patch check error.
```

*   `82a11a817a0d`：为 `PatchCheck` 添加了获取最近一次检查结果的访问器，提升了易用性。
*   `93a13080d9ef`：这是一次大规模的代码维护，将 DLL 导出宏从类型定义转移到方法和静态变量上，以提高跨模块兼容性。
*   `b18d4e011ee2`：修改了 `PatchCheck` 的错误处理策略，从“失败则阻断”改为“失败则放行”（Fail Open），提高了游戏的容错性。

### 维护评价

OnlineFramework 是一个**历史悠久且仍在维护中**的核心框架插件。它创建于 2016 年，是 UE 在线功能的基石之一。从近期的提交记录看，Epic 仍在对其进行维护和改进，包括功能增强（如添加访问器）、代码现代化（DLL 导出重构）和策略调整（Fail Open）。

**优点**：
*   提供了一套经过验证的、标准化的在线功能抽象。
*   仍在被 Epic 自己的项目（如 Lyra）使用和维护。
*   最近的更新表明其设计仍在演进以适应现代开发需求。

**注意事项**：
*   由于其历史较长，部分代码风格和模式可能不是最新的。
*   `EnabledByDefault: false` 表明它不是一个“开箱即用”的插件，需要开发者主动启用并集成。
*   作为框架层，其具体行为高度依赖于底层实现的在线子系统插件。

**推荐**：如果你的项目需要实现复杂的、跨平台的在线功能，并且希望遵循 Epic 的最佳实践，那么使用和扩展 OnlineFramework 是一个**强烈推荐**的选择。它能为你节省大量重复工作，并确保与引擎的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/online-subsystem-in-unreal-engine/) (通用在线子系统文档，涵盖此框架的使用场景)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework/Tests) (如果存在)