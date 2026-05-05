# Online Framework Plugin

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Hotfix` (Runtime), `Lobby` (Runtime), `LoginFlow` (Runtime), `Party` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Qos` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-12 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework) | |

## 用途

OnlineFramework 是一个**在线功能框架插件**，它为 Unreal Engine 提供了一套标准化的、与具体在线子系统（如 EOS、Steam 等）解耦的在线游戏功能实现。其核心价值在于：

1.  **抽象与标准化**：它定义了诸如“派对（Party）”、“大厅（Lobby）”、“QoS（服务质量）”、“热修复（Hotfix）”等高级在线功能的通用接口和基础逻辑。游戏项目可以基于这些抽象进行开发，而无需过早绑定到某个特定的在线服务提供商。
2.  **提供开箱即用的实现**：对于一些通用的在线功能（如更新检查、热修复应用、游玩时间限制），它提供了完整的运行时实现，开发者可以直接使用或在其基础上扩展。
3.  **跨平台兼容性**：通过抽象层，帮助游戏更容易地适配不同平台（PC、主机、移动端）的在线服务要求。

简单来说，它解决了“如何为游戏构建一套稳定、可扩展且不依赖于单一在线服务的在线功能基础架构”的问题。

## 使用场景

-   **开发多人在线游戏**：需要创建和管理玩家派对、游戏大厅、匹配队列时，可以使用 `Party` 和 `Lobby` 模块。
-   **需要动态更新游戏配置或修复线上问题**：使用 `Hotfix` 模块从云端下载并应用 INI 配置、本地化资源等非代码补丁，无需重新发布客户端。
-   **确保游戏版本一致性**：使用 `PatchCheck` 模块在游戏启动时检查是否有强制更新，确保所有玩家运行相同版本。
-   **优化网络连接质量**：使用 `Qos` 模块测量和选择延迟最低的服务器或玩家进行连接。
-   **实现防沉迷或家长控制**：使用 `PlayTimeLimit` 模块跟踪和限制玩家的游戏时长。
-   **处理玩家掉线重连**：使用 `Rejoin` 模块管理游戏会话的重连逻辑。
-   **自定义登录流程**：使用 `LoginFlow` 模块构建或集成特定的用户登录和身份验证流程。

## 蓝图用法

OnlineFramework 主要提供 C++ 接口，但其核心管理器和枚举通常暴露给蓝图系统，以便在蓝图中控制在线流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Update State` | 获取当前更新检查的状态（如空闲、检查中、完成等）。 | `UUpdateManager` |
| `Check for Update` | 触发一次完整的更新检查流程（包括补丁检查和热修复检查）。 | `UUpdateManager` |
| `Get Hotfix Result` | 获取最近一次热修复操作的结果。 | `UOnlineHotfixManager` |
| `Apply Hotfix` | 应用已下载的热修复数据。 | `UOnlineHotfixManager` |

### 使用示例（蓝图描述）

1.  **监听更新状态**：
    *   在蓝图中，绑定到 `UUpdateManager` 的 `OnUpdateStatusChanged` 委托。
    *   当委托触发时，检查传入的 `EUpdateState` 枚举值。如果为 `UpdateComplete`，则进一步检查 `EUpdateCompletionStatus` 来决定后续操作（如提示重启、重新加载关卡）。

2.  **触发并等待热修复**：
    *   调用 `UOnlineHotfixManager` 的 `StartHotfixProcess` 函数。
    *   绑定到 `OnHotfixComplete` 委托来接收最终结果（`EHotfixResult`）。
    *   绑定到 `OnHotfixProgress` 委托来更新下载进度条 UI。

## C++ 用法

### 头文件引入

根据你要使用的具体功能，引入对应的模块头文件。

```cpp
// 使用更新管理器
#include "UpdateManager.h"

// 使用热修复管理器
#include "OnlineHotfixManager.h"

// 使用大厅功能
#include "Lobby.h" // 假设存在对应的公共头文件
```

### 基本用法

以下示例展示了如何使用 `UUpdateManager` 启动一次更新检查并监听结果。

```cpp
// 假设在某个 UObject（如 GameInstance）中
#include "UpdateManager.h"

void UMyGameInstance::StartGameUpdate()
{
    // 获取或创建 UpdateManager 实例
    UUpdateManager* UpdateManager = GetUpdateManager(); // 获取方式取决于项目实现

    if (UpdateManager)
    {
        // 绑定状态变化委托
        UpdateManager->OnUpdateStatusChanged.AddUObject(this, &UMyGameInstance::HandleUpdateStatusChanged);
        // 绑定完成委托
        UpdateManager->OnUpdateCheckComplete.AddUObject(this, &UMyGameInstance::HandleUpdateCheckComplete);

        // 启动更新检查
        UpdateManager->StartUpdateCheck();
    }
}

void UMyGameInstance::HandleUpdateStatusChanged(EUpdateState NewState)
{
    UE_LOG(LogTemp, Log, TEXT("Update State Changed: %s"), *LexToString(NewState));
    // 根据状态更新UI，例如显示“正在检查更新...”
}

void UMyGameInstance::HandleUpdateCheckComplete(EUpdateCompletionStatus Result)
{
    UE_LOG(LogTemp, Log, TEXT("Update Check Complete: %s"), *LexToString(Result));
    switch (Result)
    {
    case EUpdateCompletionStatus::UpdateSuccess_NeedsRelaunch:
        // 提示玩家需要重启游戏
        break;
    case EUpdateCompletionStatus::UpdateFailure_PatchCheck:
        // 处理补丁检查失败
        break;
    // ... 处理其他状态
    }
}
```

### 进阶用法

结合 `Hotfix` 模块，在更新检查后自动应用热修复。

```cpp
void UMyGameInstance::HandleUpdateCheckComplete(EUpdateCompletionStatus Result)
{
    if (Result == EUpdateCompletionStatus::UpdateSuccess || Result == EUpdateCompletionStatus::UpdateSuccess_NoChange)
    {
        // 更新检查成功，现在检查并应用热修复
        UOnlineHotfixManager* HotfixManager = GetOnlineHotfixManager(); // 获取方式取决于项目实现
        if (HotfixManager)
        {
            HotfixManager->OnHotfixComplete.AddUObject(this, &UMyGameInstance::HandleHotfixComplete);
            HotfixManager->StartHotfixProcess();
        }
    }
}

void UMyGameInstance::HandleHotfixComplete(EHotfixResult Result)
{
    if (Result == EHotfixResult::SuccessNeedsReload)
    {
        // 热修复应用成功，但需要重新加载当前关卡
        UGameplayStatics::OpenLevel(this, FName(*GetWorld()->GetName()));
    }
}
```

## Demo 示例

一个最小化的示例，展示如何创建一个使用 `UpdateManager` 的自定义游戏实例。

**MyGameInstance.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "UpdateManager.h" // 包含更新管理器头文件
#include "MyGameInstance.generated.h"

UCLASS()
class MYPROJECT_API UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;

    UFUNCTION(BlueprintCallable, Category = "Online")
    void CheckForGameUpdates();

private:
    UPROPERTY()
    TObjectPtr<UUpdateManager> UpdateManager;

    void HandleUpdateStatusChanged(EUpdateState NewState);
    void HandleUpdateCheckComplete(EUpdateCompletionStatus Result);
};
```

**MyGameInstance.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyGameInstance.h"
#include "UpdateManager.h"

void UMyGameInstance::Init()
{
    Super::Init();
    // 在初始化时创建 UpdateManager 实例
    UpdateManager = NewObject<UUpdateManager>(this);
}

void UMyGameInstance::CheckForGameUpdates()
{
    if (UpdateManager)
    {
        // 清除旧的绑定
        UpdateManager->OnUpdateStatusChanged.RemoveAll(this);
        UpdateManager->OnUpdateCheckComplete.RemoveAll(this);

        // 绑定新的委托
        UpdateManager->OnUpdateStatusChanged.AddUObject(this, &UMyGameInstance::HandleUpdateStatusChanged);
        UpdateManager->OnUpdateCheckComplete.AddUObject(this, &UMyGameInstance::HandleUpdateCheckComplete);

        // 开始检查
        UpdateManager->StartUpdateCheck();
    }
}

void UMyGameInstance::HandleUpdateStatusChanged(EUpdateState NewState)
{
    UE_LOG(LogTemp, Display, TEXT("[Update] State: %s"), *LexToString(NewState));
    // 这里可以更新UI状态
}

void UMyGameInstance::HandleUpdateCheckComplete(EUpdateCompletionStatus Result)
{
    UE_LOG(LogTemp, Display, TEXT("[Update] Complete: %s"), *LexToString(Result));
    if (Result == EUpdateCompletionStatus::UpdateSuccess_NeedsPatch)
    {
        UE_LOG(LogTemp, Warning, TEXT("A mandatory patch is required. Please update the game."));
        // 可以在这里触发退出游戏或打开商店页面的逻辑
    }
}
```

## 模块依赖

OnlineFramework 的各个模块通常依赖于 Unreal Engine 的在线子系统抽象层。要使用此插件，你的项目模块需要依赖以下核心模块：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 提供与具体在线服务（如 EOS, Steam）交互的抽象接口。OnlineFramework 的许多功能（如 Party, Lobby）都构建于此之上。 |
| `OnlineSubsystemUtils` | 提供在线子系统的实用工具函数和类。 |

**注意**：具体依赖可能因你使用的 OnlineFramework 子模块（如 `Party`, `Lobby`）而略有不同，但 `OnlineSubsystem` 是最核心和通用的依赖。如果你的项目已经配置了在线子系统（例如在 `DefaultEngine.ini` 中设置了 `[OnlineSubsystem]`），则通常已满足此依赖。

## 维护状态

### 近期更新

```
- 00274a15ab21 Added new analytics: Online.TitleFile.EnumerateFilesComplete UpdateManager.UpdateCheckComplete Fix analytics which would not fire correctly with early login due to depdendency on PlayerController: PatchCheck.PatchCheckComplete Online.TitleFile.InitComplete Online.TitleFile.FileRequestComplete
- 50eb727f23eb Optimization to avoid reading thread heartbeat settings from config every frame.
- 25db8f5a1995 [UpdateManager] Change cached response timeout to be a hotfixable CVar with a default of 5 minutes.
```

**解读**：
1.  `00274a15ab21`：这是一次重要的功能更新，为多个在线模块（TitleFile, UpdateManager, PatchCheck）添加了分析（Analytics）事件，并修复了与早期登录相关的依赖问题。这表明插件仍在积极添加新功能和修复问题。
2.  `50eb727f23eb`：性能优化，避免每帧从配置读取设置。这是典型的维护性改进。
3.  `25db8f5a1995`：将 `UpdateManager` 的缓存响应超时时间改为可通过热修复更新的 CVar（控制台变量），默认值为 5 分钟。这增强了线上配置的灵活性。

### 维护评价

**综合评价：维护中，但需注意其“框架”属性。**

-   **年龄与活跃度**：插件创建于 2016 年，是一个“老古董”。但从最近的提交记录看，**它仍在被积极维护和更新**（最近一次提交涉及功能添加和优化），并非废弃状态。
-   **性质**：它是一个**底层框架**，而非即插即用的解决方案。它的价值在于提供标准化的接口和基础实现。实际项目中，通常需要结合具体的 `OnlineSubsystem` 插件（如 `OnlineSubsystemEOS`）并进行大量定制开发才能使用。
-   **推荐使用**：
    -   **推荐**：如果你正在开发一款需要深度集成在线功能（特别是派对、大厅、热修复）的多人游戏，并且希望代码具有更好的可移植性和可维护性，那么研究和基于此框架进行开发是有价值的。
    -   **不推荐**：如果你只需要非常简单的在线功能（如基础的排行榜、成就），或者希望快速原型开发，直接使用特定 `OnlineSubsystem` 的原生接口可能更简单直接。
-   **已知限制**：作为框架，它本身不提供任何具体的在线服务实现。你需要自行配置和集成后端服务。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/online-subsystem-and-plugins-in-unreal-engine/) (通用在线子系统文档，OnlineFramework 是其上层框架)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework/Tests) (如果存在)