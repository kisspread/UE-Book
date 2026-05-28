# Game Features

> Support for modular Game Feature Plugins

| 属性 | 值 |
|---|---|
| 中文名 | 游戏特性系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameFeatures` (Runtime), `GameFeaturesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-31 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameFeatures) | |

## 用途

Game Features 插件提供了一套完整的模块化游戏功能（Game Feature Plugin, GFP）管理系统。它解决的核心问题是：如何在不重启游戏的情况下，动态地、按需地加载、激活、卸载和管理游戏内容模块。这套系统为大型游戏（特别是需要支持DLC、赛季内容、热更新、AB测试等场景）提供了基础设施。

**主要功能**：
1.  **状态机管理**：为每个 Game Feature Plugin 维护一个复杂的状态机，控制其生命周期（从 `Installed` -> `Registered` -> `Loaded` -> `Active`）。
2.  **异步操作与回调**：所有加载、激活等操作都是异步的，并通过委托（Delegate）通知调用方完成状态。
3.  **协议支持**：支持不同的插件来源协议，如本地文件（`file:`）和安装包（`installbundle:`）。
4.  **依赖管理**：自动处理插件间的依赖关系，确保依赖插件按正确顺序加载。
5.  **生命周期钩子**：提供 `UGameFeatureAction` 基类，允许开发者在插件注册、加载、激活、停用、卸载等生命周期阶段执行自定义逻辑。
6.  **观察者模式**：通过 `IGameFeatureStateChangeObserver` 接口，允许外部系统监听插件状态变化。
7.  **项目策略**：通过 `UGameFeaturesProjectPolicies` 类，允许项目自定义GFP的加载、过滤、解析等行为。

**为什么存在**：
在传统的UE开发中，所有功能模块都是作为引擎插件或游戏模块静态编译和打包的。Game Features 系统打破了这种静态依赖，使得游戏内容可以像应用商店的App一样被动态管理。这是构建现代服务型游戏（Games as a Service）的关键技术。

## 使用场景

-   你需要为游戏制作可下载的DLC内容包，玩家购买后无需重启游戏即可解锁新角色、地图或模式。
-   你的游戏采用赛季制，每个赛季都需要更新新的战斗通行证、任务和奖励系统。
-   你希望对不同的玩家群体进行A/B测试，动态加载不同的游戏功能或配置。
-   你需要实现游戏的热修复，远程修复Bug或调整游戏平衡性。
-   你的游戏规模庞大，希望按需加载资源以减少内存占用和启动时间。
-   你需要在编辑器中迭代开发独立的功能模块，并能够独立于主游戏进行测试。

## 蓝图用法

核心功能主要在C++层面暴露，蓝图可用的功能主要集中在**数据资产配置**和**状态查询**上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Game Feature Data` | 从 `UGameFeatureData` 资产中获取插件名称 | `UGameFeatureData` (静态函数) |
| `Is Game Feature Plugin Active` | 查询指定插件是否处于激活状态 | `UGameFeaturesSubsystem` |
| `Is Game Feature Plugin Registered` | 查询指定插件是否已注册 | `UGameFeaturesSubsystem` |
| `Is Game Feature Plugin Loaded` | 查询指定插件是否已加载 | `UGameFeaturesSubsystem` |

### 使用示例（蓝图描述）

**查询插件状态**：
1.  节点：`Get Game Features Subsystem`
2.  连接：`Is Game Feature Plugin Active` 节点。
3.  在 `Plugin URL` 输入引脚填入目标插件的URL字符串（例如 `file:../../../MyPlugins/MyFeature.uplugin`）。
4.  从输出引脚获取一个布尔值，用于分支判断。

**配置 GameFeatureData**：
1.  在内容浏览器中右键创建一个新的 `GameFeatureData` 资产。
2.  打开该资产，在 `Actions` 数组中添加 `UGameFeatureAction` 的子类实例（例如 `Add Components` 或 `Add Cheats`），并配置相应的属性。
3.  这个 `GameFeatureData` 资产就是你的GFP的核心数据资产，它定义了当该插件被激活时应该执行哪些操作。

## C++ 用法

Game Features 系统主要通过C++ API进行控制和扩展。

### 头文件引入

```cpp
#include "GameFeaturesSubsystem.h"
#include "GameFeatureData.h"
#include "GameFeatureAction.h"
```

### 基本用法

**加载并激活一个 Game Feature Plugin**

```cpp
// 来自引擎测试代码的用法简化
void ActivateMyGameFeature()
{
    UGameFeaturesSubsystem& Subsystem = UGameFeaturesSubsystem::Get();
    
    // 1. 构造插件URL
    FString PluginURL = UGameFeaturesSubsystem::GetPluginURL_FileProtocol(
        FPaths::ProjectPluginsDir() / TEXT("MyGameFeature/MyGameFeature.uplugin")
    );
    
    // 2. 定义加载完成回调
    FGameFeaturePluginLoadComplete LoadCompleteDelegate;
    LoadCompleteDelegate.BindLambda([](const UE::GameFeatures::FResult& Result)
    {
        if (Result.HasValue())
        {
            UE_LOG(LogTemp, Log, TEXT("Game Feature Plugin loaded and activated successfully!"));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to load Game Feature Plugin: %s"), *Result.GetError());
        }
    });
    
    // 3. 调用加载并激活
    Subsystem.LoadAndActivateGameFeaturePlugin(PluginURL, LoadCompleteDelegate);
}
```

**实现自定义的 GameFeatureAction**

```cpp
// MyGameFeatureAction.h
UCLASS(meta=(DisplayName="My Custom Action"))
class UMyGameFeatureAction : public UGameFeatureAction
{
    GENERATED_BODY()
    
public:
    virtual void OnGameFeatureActivating(FGameFeatureActivatingContext& Context) override;
    virtual void OnGameFeatureDeactivating(FGameFeatureDeactivatingContext& Context) override;
    
private:
    // 你的自定义数据
    UPROPERTY(EditAnywhere)
    FString MyCustomConfig;
};
```

### 进阶用法

**使用 StateHandle 管理插件引用计数**

```cpp
// 来自引擎测试代码的用法
void ManagePluginReferences()
{
    // 1. 创建一个状态句柄，用于跟踪多个GFP的引用
    FGameFeatureStateHandle StateHandle(TEXT("MyFeatureManager"), EGameFeatureStateHandleOptions::TrackDependencies);
    
    // 2. 通过句柄加载插件，系统会自动管理依赖
    FGameFeatureProtocolOptions Options;
    Subsystem.LoadAndActivateGameFeaturePlugin(
        StateHandle,
        PluginURL,
        Options,
        UGameFeatureStateHandleLoadComplete()
    );
    
    // 3. 当不再需要时，句柄析构时会自动清理引用
}
```

## Demo 示例

一个最小化的自定义 Game Feature Action 示例。

**MySimpleAction.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFeatureAction.h"
#include "MySimpleAction.generated.h"

UCLASS(meta=(DisplayName="Simple Notification"))
class UMySimpleAction : public UGameFeatureAction
{
    GENERATED_BODY()
    
public:
    virtual void OnGameFeatureActivating() override
    {
        UE_LOG(LogTemp, Log, TEXT("Game Feature Activated: %s"), *GetGameFeatureData()->GetName());
    }
    
    virtual void OnGameFeatureDeactivating(FGameFeatureDeactivatingContext& Context) override
    {
        UE_LOG(LogTemp, Log, TEXT("Game Feature Deactivated: %s"), *GetGameFeatureData()->GetName());
    }
};
```

**MySimpleAction.cpp**
```cpp
#include "MySimpleAction.h"
// 通常 .cpp 文件中无需额外实现，因为所有方法都在头文件中实现。
```

**使用方法**：
1.  编译包含上述代码的模块。
2.  创建一个 `GameFeatureData` 资产。
3.  在其 `Actions` 数组中添加 `UMySimpleAction` 的一个实例。
4.  通过 `GameFeaturesSubsystem` 加载并激活该GFP，你将在日志中看到相应的输出。

## 模块依赖

使用 Game Features 插件时，你的项目模块通常需要依赖以下内容：

| 模块 | 用途 |
|---|---|
| `GameFeatures` | 核心运行时模块，提供所有子系统、状态机和Action基类。 |
| `ModularGameplay` | 提供 `UGameFrameworkComponentManager`，是 `Add Components` Action 的基础。 |
| `DataRegistry` | 如果使用 `GameFeatureAction_DataRegistry` 或 `GameFeatureAction_DataRegistrySource`，则需要此模块。 |
| `InstallBundleManager` | 如果使用 `installbundle:` 协议进行DLC分发，则需要此模块。 |

**注**：`GameFeaturesEditor` 模块是编辑器专用的，用于在编辑器中处理GFP的资产、验证和UI，游戏运行时不需要依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `f604c6dd` | CollectDepends when AddOrUpdateRef, skip dep walk for deps already counted at >= target state in thi | 优化了依赖收集逻辑，避免对已达到目标状态的插件重复遍历依赖。 |
| 2026-05-12 | `a7ff6fd5` | [GameFeatures] Added optional CVar property gating for AddWorldPartitionContent activation. | 为 `AddWorldPartitionContent` Action 添加了可选的CVar属性门控，用于条件激活。 |
| 2026-04-30 | `3f194f64` | Only load verse path mapper bin in cooked non editor builds. Cooked editor still requires all plugin | 调整了Verse路径映射二进制文件的加载策略：仅在非编辑器的Cooked版本中加载。 |
| 2026-04-29 | `2353b745` | [Backout] - CL53308230 | 回滚了某个提交。 |
| 2026-04-29 | `fa918b28` | Only load verse path mapper bin in cooked non editor builds. Cooked editor still requires all plugin | 与上一条相同内容的重复提交（可能是合并或修复）。 |

### 维护评价

**综合评价：活跃维护中的核心系统。**

-   **活跃度**：插件自2024年初从Experimental移至Runtime后，一直保持活跃更新。近期（2026年4-5月）仍有功能性优化和新特性添加。
-   **稳定性**：尽管标记为 `IsBetaVersion=true`，但考虑到它已从Experimental阶段毕业并作为Runtime插件，且被Epic自己的Fortnite等大型项目使用，其核心功能已相当稳定。
-   **重要性**：这是UE5面向未来游戏服务化架构的基石之一，Epic会持续投入维护。
-   **注意事项**：`IsBetaVersion=true` 的标签表明其API仍有可能在未来版本中发生变化，尤其是随着Verse语言的集成和新功能的添加。在大型项目中采用时，需要做好API版本迁移的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameFeatures)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/game-feature-plugins-in-unreal-engine/) (UE5.8 文档中的相关章节)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameFeatures/Source/GameFeatures/Private/Tests) (位于插件私有源码目录内)