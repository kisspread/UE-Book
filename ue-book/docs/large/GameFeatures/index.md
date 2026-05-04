# Game Features

> Support for modular Game Feature Plugins

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameFeatures` (Runtime), `GameFeaturesEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-01-08 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameFeatures) | |

## 用途

Game Features 插件是 Unreal Engine 的**模块化游戏功能框架**，用于将游戏功能封装为独立的、可动态加载/卸载的插件单元。它解决的核心问题是：如何在不修改主游戏代码的前提下，以插件形式添加、移除或切换游戏功能（如新角色、新玩法模式、DLC 内容等）。

每个 Game Feature Plugin（GFP）由一个 `UGameFeatureData` 数据资产驱动，其中包含一组 `UGameFeatureAction`。当插件在生命周期中经历安装→挂载→注册→加载→激活等状态转换时，这些 Action 会被依次执行，实现组件注册、资产扫描、数据注入等操作。

**为什么存在？** 传统 UE 插件在启动时就固定加载，无法在运行时动态开关。Game Features 通过状态机管理插件生命周期，支持按需下载、异步加载、运行时激活/去激活，非常适合 DLC、Live Service 游戏、赛季内容、A/B 测试等场景。

## 核心架构

### 状态机（Plugin State Machine）

每个 GFP 由一个 `UGameFeaturePluginStateMachine` 实例管理，完整生命周期如下：

```
Uninitialized → UnknownStatus → CheckingStatus → StatusKnown
    → Downloading → Installed
    → Mounting → WaitingForDependencies → Registering → Registered
    → Loading → Loaded
    → ActivatingDependencies → Activating → Active
```

关键状态说明：

| 状态 | 类型 | 说明 |
|---|---|---|
| `Installed` | 目标状态 | 插件在本地存储中可用（磁盘上） |
| `Registered` | 目标状态 | 资产已被发现并注册到 AssetManager，但未加载 |
| `Loaded` | 目标状态 | 代码和内容已加载到内存 |
| `Active` | 目标状态 | 插件完全激活，正在影响游戏 |
| `Downloading` | 过渡状态 | 正在下载/安装内容 |
| `Mounting` | 过渡状态 | Pak 文件正在挂载 |
| `Registering` | 过渡状态 | 正在发现资产并注册 |
| `Activating` | 过渡状态 | 正在向游戏系统注册代码/内容 |

### Plugin URL 协议

GFP 通过 URL 唯一标识，支持两种协议：

| 协议 | 格式 | 说明 |
|---|---|---|
| `file:` | `file:../../../Path/To/Plugin.uplugin` | 本地文件系统插件 |
| `installbundle:` | `installbundle:PluginName?bundles=BundleA,BundleB` | 需要按需下载的插件 |

### GameFeatureAction 生命周期

`UGameFeatureAction` 是插件行为的基本单元，通过以下回调参与生命周期：

```
OnGameFeatureRegistering()    → 插件被注册时（可能从未激活）
OnGameFeatureUnregistering()  → 插件取消注册时
OnGameFeatureLoading()        → 插件即将加载时
OnGameFeatureUnloading()      → 插件被卸载时
OnGameFeatureActivating()     → 插件被激活时（带 Context）
OnGameFeatureActivated()      → 插件完全激活后
OnGameFeatureDeactivating()   → 插件被去激活时（带 Context，支持异步暂停）
```

## 使用场景

- **DLC/内容包**：玩家购买 DLC 后，通过 `installbundle:` 协议下载并激活新关卡、角色、武器
- **赛季内容**：Live Service 游戏按赛季切换游戏功能，通过状态机管理加载/卸载
- **Modular Gameplay**：为 Actor 动态附加组件（如给所有 Pawn 加技能系统），无需修改 Actor 基类
- **A/B 测试**：运行时切换不同功能集，观察玩家行为
- **按需资源加载**：大型内容包延迟下载，仅在需要时安装

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPluginName` | 获取插件名称 | `UGameFeatureData` |
| `IsGameFeaturePluginRegistered` | 检查插件是否已注册 | `UGameFeatureData` |
| `IsGameFeaturePluginActive` | 检查插件是否已激活 | `UGameFeatureData` |

> **注意**：Game Features 框架的大部分核心 API（如 `LoadAndActivateGameFeaturePlugin`、`DeactivateGameFeaturePlugin`）仅暴露为 C++ 接口，蓝图中主要通过 `UGameFeatureData` 的查询方法进行状态检查。实际的加载/激活逻辑通常在 C++ 层实现。

### 在 GameFeatureData 资产中配置 Actions

1. 创建 `UGameFeatureData` 资产（或通过 Editor 插件向导自动生成）
2. 在 Details 面板的 **Game Feature | Actions** 数组中添加 Action
3. 常用 Action 类型：
   - **Add Components**：指定 `ActorClass → ComponentClass` 映射
   - **Add Cheats**：注册 CheatManager 扩展
   - **Add Data Registry**：加载 DataRegistry 资产
   - **Add Data Registry Source**：向现有 DataRegistry 添加数据源
   - **Add World Partition Content**：注入 World Partition 内容
   - **Add Actor Factory**：注册自定义 Actor 工厂
   - **Add Chunk Override**：覆盖资产的 Chunk 分配

## C++ 用法

### 头文件引入

```cpp
#include "GameFeaturesSubsystem.h"
#include "GameFeatureData.h"
#include "GameFeatureAction.h"
```

### 基本用法 — 加载并激活插件

```cpp
// 来源: GameFeaturePluginTests.cpp

// 获取子系统实例
UGameFeaturesSubsystem& Subsystem = UGameFeaturesSubsystem::Get();

// 构建 Plugin URL
FString PluginURL = UGameFeaturesSubsystem::GetPluginURL_FileProtocol(
    TEXT("../../../MyGame/Plugins/MyFeature/MyFeature.uplugin")
);

// 异步加载并激活
Subsystem.LoadAndActivateGameFeaturePlugin(
    PluginURL,
    FGameFeaturePluginLoadComplete::CreateLambda(
        [](const UE::GameFeatures::FResult& Result)
        {
            if (Result.HasError())
            {
                UE_LOG(LogGameFeatures, Error, TEXT("Failed: %s"), *Result.GetError());
            }
            else
            {
                UE_LOG(LogGameFeatures, Log, TEXT("Plugin activated!"));
            }
        }
    )
);
```

### 基本用法 — 分步状态转换

```cpp
// 来源: GameFeaturePluginTests.cpp

UGameFeaturesSubsystem& Subsystem = UGameFeaturesSubsystem::Get();
FString PluginURL = TEXT("file:../../../MyPlugin.uplugin");

// 逐级推进状态
Subsystem.ChangeGameFeatureTargetState(
    PluginURL,
    EGameFeatureTargetState::Installed,  // 先安装
    FGameFeaturePluginChangeStateComplete::CreateLambda(
        [&Subsystem, PluginURL](const UE::GameFeatures::FResult& Result)
        {
            if (!Result.HasError())
            {
                // 安装成功后，推进到 Registered
                Subsystem.ChangeGameFeatureTargetState(
                    PluginURL,
                    EGameFeatureTargetState::Registered,
                    FGameFeaturePluginChangeStateComplete::CreateLambda(
                        [](const UE::GameFeatures::FResult& R)
                        {
                            // 最终检查
                        }
                    )
                );
            }
        }
    )
);
```

### 查询插件状态

```cpp
// 来源: GameFeaturePluginTests.cpp

UGameFeaturesSubsystem& Subsystem = UGameFeaturesSubsystem::Get();

// 检查当前状态
EGameFeaturePluginState State = Subsystem.GetPluginState(PluginURL);

// 检查是否已安装
bool bInstalled = Subsystem.IsGameFeaturePluginInstalled(PluginURL);

// 检查是否已激活
bool bActive = Subsystem.IsGameFeaturePluginActive(PluginURL);

// 获取激活插件的 GameFeatureData
const UGameFeatureData* Data = Subsystem.GetGameFeatureDataForActivePluginByURL(PluginURL);

// 获取注册插件的 GameFeatureData
const UGameFeatureData* RegData = Subsystem.GetGameFeatureDataForRegisteredPluginByURL(PluginURL);
```

### 使用 InstallBundle 协议加载插件

```cpp
// 构建 InstallBundle URL
TArray<FName> BundleNames = { TEXT("MyBundle1"), TEXT("MyBundle2") };
FString BundleURL = UGameFeaturesSubsystem::GetPluginURL_InstallBundleProtocol(
    TEXT("MyPlugin"), BundleNames
);

// 设置协议选项
FInstallBundlePluginProtocolOptions BundleOptions;
BundleOptions.bAllowIniLoading = true;
BundleOptions.bDoNotDownload = false;

FGameFeatureProtocolOptions ProtocolOptions(BundleOptions);

Subsystem.LoadAndActivateGameFeaturePlugin(
    BundleURL,
    ProtocolOptions,
    FGameFeaturePluginLoadComplete::CreateLambda(
        [](const UE::GameFeatures::FResult& Result) { /* ... */ }
    )
);
```

### 加载内置插件（Built-In）

```cpp
// 加载所有通过过滤器的内置插件
Subsystem.LoadBuiltInGameFeaturePlugins(
    [](const FString& PluginFilename,
       const FGameFeaturePluginDetails& Details,
       FBuiltInGameFeaturePluginBehaviorOptions& OutOptions) -> bool
    {
        // 返回 true 允许加载，false 跳过
        if (Details.BuiltInAutoState == EBuiltInAutoState::Active)
        {
            OutOptions.AutoStateOverride = EBuiltInAutoState::Active;
        }
        return true;
    },
    FBuiltInGameFeaturePluginsLoaded::CreateLambda(
        [](const TMap<FString, UE::GameFeatures::FResult>& Results)
        {
            for (const auto& Pair : Results)
            {
                // 处理每个插件的结果
            }
        }
    )
);
```

### 注册状态变更观察者

```cpp
// 自定义观察者类
class UMyGameFeatureObserver : public UObject, public IGameFeatureStateChangeObserver
{
    GENERATED_BODY()

public:
    virtual void OnGameFeatureActivating(const UGameFeatureData* Data,
        const FString& PluginURL) override
    {
        UE_LOG(LogTemp, Log, TEXT("Plugin activating: %s"), *PluginURL);
    }

    virtual void OnGameFeatureDeactivating(const UGameFeatureData* Data,
        FGameFeatureDeactivatingContext& Context, const FString& PluginURL) override
    {
        // 支持异步延迟去激活
        FSimpleDelegate Done = Context.PauseDeactivationUntilComplete(TEXT("MyCleanup"));
        // ... 执行异步清理 ...
        Done.ExecuteIfBound();
    }
};

// 注册观察者
UMyGameFeatureObserver* Observer = NewObject<UMyGameFeatureObserver>();
Subsystem.AddObserver(Observer, UGameFeaturesSubsystem::EObserverPluginStateUpdateMode::FutureOnly);
```

### 自定义 GameFeatureAction

```cpp
// MyCustomAction.h
UCLASS(DisplayName = "My Custom Action")
class UMyCustomAction : public UGameFeatureAction
{
    GENERATED_BODY()

public:
    virtual void OnGameFeatureActivating(FGameFeatureActivatingContext& Context) override
    {
        // 在此处执行激活逻辑
    }

    virtual void OnGameFeatureDeactivating(FGameFeatureDeactivatingContext& Context) override
    {
        // 在此处执行去激活清理
    }

    UPROPERTY(EditAnywhere, Category = "Custom")
    FString CustomSetting;
};
```

### 进阶用法 — 预下载插件

```cpp
TArray<FString> PluginURLs = { PluginURL1, PluginURL2 };

TSharedRef<FGameFeaturePluginPredownloadHandle> Handle =
    Subsystem.PredownloadGameFeaturePlugins(
        PluginURLs,
        TUniqueFunction<void(const UE::GameFeatures::FResult&)>(
            [](const UE::GameFeatures::FResult& Result)
            {
                // 预下载完成
            }
        ),
        TUniqueFunction<void(float)>(
            [](float Progress)
            {
                // 进度更新 (0.0 ~ 1.0)
            }
        )
    );
```

### 取消状态转换

```cpp
Subsystem.CancelGameFeatureStateChange(
    PluginURL,
    FGameFeaturePluginChangeStateComplete::CreateLambda(
        [](const UE::GameFeatures::FResult& Result)
        {
            // 取消完成
        }
    )
);
```

## Demo 示例

### 最小 Game Feature Action

```cpp
// MyFeatureAction.h
#pragma once
#include "GameFeatureAction.h"
#include "MyFeatureAction.generated.h"

UCLASS(DisplayName = "Add Score Multiplier")
class UMyFeatureAction_AddScoreMultiplier : public UGameFeatureAction
{
    GENERATED_BODY()

public:
    virtual void OnGameFeatureActivating(FGameFeatureActivatingContext& Context) override;
    virtual void OnGameFeatureDeactivating(FGameFeatureDeactivatingContext& Context) override;

    UPROPERTY(EditAnywhere, Category = "Score")
    float Multiplier = 2.0f;
};
```

```cpp
// MyFeatureAction.cpp
#include "MyFeatureAction.h"

void UMyFeatureAction_AddScoreMultiplier::OnGameFeatureActivating(
    FGameFeatureActivatingContext& Context)
{
    // 注册分数倍率到游戏系统
    // UMyGameSubsystem::Get().SetScoreMultiplier(Multiplier);
}

void UMyFeatureAction_AddScoreMultiplier::OnGameFeatureDeactivating(
    FGameFeatureDeactivatingContext& Context)
{
    // 移除分数倍率
    // UMyGameSubsystem::Get().SetScoreMultiplier(1.0f);
}
```

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "GameFeatures"
});
```

## 模块依赖

### GameFeatures（Runtime 模块）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和容器 |
| `CoreUObject` | UObject 系统 |
| `DeveloperSettings` | 项目设置基类 |
| `Engine` | 引擎核心（AssetManager、DataAsset 等） |
| `ModularGameplay` | 模块化 Gameplay 组件框架 |
| `DataRegistry` | 数据注册表系统 |

### GameFeaturesEditor（Editor 模块）

| 模块 | 用途 |
|---|---|
| `GameFeatures` | 运行时模块 |
| `UnrealEd` | 编辑器框架 |
| `AssetTools` | 资产创建工具 |
| `DataLayerEditor` | Data Layer 编辑器支持 |
| `DataValidation` | 数据验证 |
| `PropertyEditor` | Details 面板定制 |
| `SharedSettingsWidgets` | 设置 UI 组件 |

## 内置 Action 类型一览

| Action 类 | DisplayName | 说明 |
|---|---|---|
| `UGameFeatureAction_AddComponents` | Add Components | 向 Actor 添加组件请求（通过 ComponentManager） |
| `UGameFeatureAction_AddCheats` | Add Cheats | 注册 CheatManager 扩展 |
| `UGameFeatureAction_AddDataRegistry` | Add Data Registry | 加载并初始化 DataRegistry 资产 |
| `UGameFeatureAction_AddDataRegistrySource` | Add Data Registry Source | 向 DataRegistry 添加数据源（DataTable/CurveTable） |
| `UGameFeatureAction_AddWorldPartitionContent` | Add World Partition Content | 注入 World Partition 内容（通过 ExternalDataLayer） |
| `UGameFeatureAction_AddWPContent` | Add WP Content (Content Bundle) | 旧版 WP 内容注入（通过 ContentBundle） |
| `UGameFeatureAction_AddActorFactory` | Add Actor Factory | 注册自定义 Actor 工厂 |
| `UGameFeatureAction_AddChunkOverride` | Add Chunk Override | 覆盖资产的 Chunk ID 分配 |
| `UGameFeatureAction_AudioActionBase` | (Abstract) | 音频引擎操作基类 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-10-17 | `a0f39fa4` | 修正 ContentBundle/AssetRegistry 标签在子 GameFeatureAction 中的正确添加，实现 ContentBundle 版本的 LevelExternalActorsPathsProvider 委托 |
| 2025-10-15 | `85878048` | [GFP] 为 UGameFeatureOptionalContentInstaller 传递 Keeplist |
| 2025-10-15 | `1cfa9cd6` | 移除 `ensure(bCacheIsUpToDate)` — 无法从所有调用路径保证该条件，修复 IncrementalCook |

### 维护评价

- **创建时间**：2021-01-08，最早出现在 Experimental 分类中
- **最近更新**：2025-10-17，距今约 6 个月内有实质性更新
- **维护状态**：**活跃维护** — Epic 持续修复 bug 和改进功能
- **实验性标记**：`.uplugin` 中 `IsBetaVersion=true`，`EnabledByDefault=false`，需手动启用
- **推荐使用**：✅ 推荐。虽然标记为 Beta，但这已是 Lyra 项目和 Epic 官方示例的核心架构，被广泛用于 Fortnite 等大型项目。Beta 标签更多是表明 API 可能仍有变化，而非不稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameFeatures)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/GameFeatures/Source/GameFeatures/Private/Tests/GameFeaturePluginTests.cpp)
- 依赖插件：[ModularGameplay](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ModularGameplay)、[DataRegistry](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/DataRegistry)
