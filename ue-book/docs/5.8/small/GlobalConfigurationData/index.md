# Global Configuration Data

> A system that is used to query configuration data that can come from many different sources without knowing specifically which one.

| 属性 | 值 |
|---|---|
| 中文名 | 全局配置数据 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GlobalConfigurationData` (Runtime), `GlobalConfigurationDataCore` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GlobalConfigurationData) | |

## 用途

该插件提供了一个抽象层，允许游戏运行时从多个不同来源（如控制台命令、热修复数据、资产配置等）查询配置数据，而游戏逻辑代码无需关心数据具体来自哪个源。这实现了配置来源与配置使用逻辑的解耦，便于管理、扩展和热更新配置数据。

## 使用场景

- **运行时配置切换**：游戏需要支持通过控制台命令或外部输入在运行时修改特定配置参数。
- **热修复与紧急设置**：需要在不发布补丁的情况下，通过后端服务动态推送高优先级的配置更新。
- **统一配置管理**：希望将来自不同系统（如本地文件、网络服务、开发者控制台）的配置数据统一在一个接口下查询。
- **调试与调试信息可视化**：需要方便地查看当前生效的配置值及其来源。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Configuration Router` | 添加一个配置数据路由器，用于向系统注册一个新的配置数据源。 | `UGlobalConfigurationData` |
| `Remove Configuration Router` | 移除一个已注册的配置数据路由器。 | `UGlobalConfigurationData` |
| `Query Configuration Data` | 查询指定键名的配置数据，返回一个可等待的查询句柄。 | `UGlobalConfigurationData` |

### 使用示例（蓝图描述）

1.  **初始化**：在游戏模式或某个管理器中，调用 **Add Configuration Router** 节点，传入您自定义的配置路由器（例如一个基于`UGCDConfigRouter`的蓝图子类实例）。
2.  **查询数据**：在任何需要配置数据的地方，调用 **Query Configuration Data** 节点，传入如 `“Game.MaxPlayers”` 这样的键名。该节点返回一个`UGCDQueryHandle`。
3.  **等待结果**：使用蓝图的`Await`或延迟节点等待查询完成。查询完成后，可以从句柄中获取到`bool`、`int`、`float`、`string`等类型的值。
4.  **清理**：在适当的时机（如对象销毁时），调用 **Remove Configuration Router** 节点来注销您的路由器。

## C++ 用法

### 头文件引入

```cpp
#include "GlobalConfigurationData.h"
#include "GlobalConfigurationDataSubsystem.h"
```

### 基本用法

```cpp
// 获取全局配置数据子系统
UGlobalConfigurationDataSubsystem* GCSSubsystem = UGlobalConfigurationDataSubsystem::Get(GetWorld());
if (!GCSSubsystem) return;

// 定义一个回调来处理查询结果
auto OnQueryComplete = FGCDSimpleQueryCallback::CreateLambda([](const FGCDQueryResult& Result)
{
    if (Result.HasSucceeded())
    {
        bool bValue = false;
        if (Result.GetValueAsBool(bValue))
        {
            // 使用配置值 bValue
            UE_LOG(LogTemp, Log, TEXT("Config value: %s"), bValue ? TEXT("true") : TEXT("false"));
        }
    }
});

// 查询一个布尔值配置
GCSSubsystem->QueryConfigurationData(TEXT("Game.EnableTutorial"), OnQueryComplete);
```
*(来源：推测自 `GlobalConfigurationDataSubsystem` 公共接口)*

### 进阶用法

```cpp
// 注册一个自定义的配置路由器
class UMyCustomConfigRouter : public UGCDConfigRouter
{
    // ... 实现您的配置数据提供逻辑
};

// 在某个初始化函数中
UMyCustomConfigRouter* MyRouter = NewObject<UMyCustomConfigRouter>(this);
GCSSubsystem->AddConfigurationRouter(MyRouter);

// 使用高级查询功能，可能包含默认值或超时
FGCDQueryOptions Options;
Options.DefaultValue = true;
Options.TimeoutSeconds = 5.0f;

GCSSubsystem->QueryConfigurationData(TEXT("Game.ComplexSetting"), OnQueryComplete, Options);

// 在测试或特定流程中，可以同步等待查询完成
FGCDQueryHandle Handle = GCSSubsystem->QueryConfigurationData(TEXT("Game.ServerAddress"));
// 使用测试宏或特定等待逻辑同步获取结果
// WAIT_FOR_GCD_QUERY(Handle); // 假设存在这样的辅助宏
```
*(来源：结合模块功能描述与测试用例模式推断)*

## Demo 示例

**MyGameConfigManager.h**
```cpp
#pragma once
#include "Subsystems/WorldSubsystem.h"
#include "GlobalConfigurationDataTypes.h"
#include "MyGameConfigManager.generated.h"

UCLASS()
class UMyGameConfigManager : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollection& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable, Category = "Config")
    void RequestPlayerName();

private:
    FGCDSimpleQueryCallback OnPlayerNameReceived;
    void HandlePlayerNameQuery(const FGCDQueryResult& Result);
};
```

**MyGameConfigManager.cpp**
```cpp
#include "MyGameConfigManager.h"
#include "GlobalConfigurationDataSubsystem.h"

void UMyGameConfigManager::Initialize(FSubsystemCollection& Collection)
{
    Super::Initialize(Collection);
    OnPlayerNameReceived = FGCDSimpleQueryCallback::CreateUObject(this, &UMyGameConfigManager::HandlePlayerNameQuery);
}

void UMyGameConfigManager::Deinitialize()
{
    OnPlayerNameReceived = nullptr;
    Super::Deinitialize();
}

void UMyGameConfigManager::RequestPlayerName()
{
    UGlobalConfigurationDataSubsystem* GCSSubsystem = UGlobalConfigurationDataSubsystem::Get(GetWorld());
    if (GCSSubsystem)
    {
        GCSSubsystem->QueryConfigurationData(TEXT("Player.DefaultName"), OnPlayerNameReceived);
    }
}

void UMyGameConfigManager::HandlePlayerNameQuery(const FGCDQueryResult& Result)
{
    FString PlayerName;
    if (Result.GetValueAsString(PlayerName))
    {
        UE_LOG(LogTemp, Log, TEXT("Retrieved player name: %s"), *PlayerName);
        // 将玩家名称应用到游戏中...
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to retrieve player name config."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CommonUI` | 可能用于某些与UI相关的配置处理或调试界面 |
| `GameplayTags` | 用于基于标签的配置系统或查询过滤 |
| `Json` | 处理来自JSON格式（如资产文件或网络数据）的配置数据 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-10 | `79a1090c` | [GCD] Add support to auto flatten json objects with a single entry | 增强了JSON配置的处理能力，支持自动展平单属性的JSON对象。 |
| 2025-07-18 | `10de61f9` | [GCD] Make console command router debug only, add a 'hotfix' config router for high priority setting | 将控制台路由器设为调试专用，新增用于高优先级设置的“热修复”配置路由器。 |
| 2025-06-23 | `bfa3140f` | [Misc] Fix GlobalConfigurationData test ensures | 修复了该插件的单元测试中的确保（Assert）问题。 |
| 2025-06-17 | `8a2ca4d6` | [UE] Add experimental Global Configuration Data | 首次提交，添加了实验性的全局配置数据插件。 |

### 维护评价

**活跃维护**。该插件创建于2025年6月，非常新，并且在此后几个月内持续收到功能更新和修复（最近一次为2025年9月）。提交记录表明 Epic 的开发团队正在积极开发和迭代此插件。作为“实验性”插件，它可能仍在完善API和功能，接口可能会变动。目前推荐用于研究、学习或在非生产环境中测试新的配置管理范式，暂不建议直接用于对稳定性要求极高的正式项目核心逻辑中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GlobalConfigurationData)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GlobalConfigurationData/Tests)