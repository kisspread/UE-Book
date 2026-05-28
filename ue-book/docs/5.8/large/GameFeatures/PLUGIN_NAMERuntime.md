# Game Features

> Support for modular Game Feature Plugins

| 属性 | 值 |
|---|---|
| 中文名 | 游戏功能 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameFeatures` (Runtime), `GameFeaturesEditor` (Runtime), `PLUGIN_NAMERuntime` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-31 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameFeatures) | |

## 用途

`GameFeatures` 插件是 Unreal Engine 模块化游戏功能（Game Features）的核心框架。它并非一个具体的功能，而是一套**基础设施**，用于创建、管理和动态激活独立的“游戏功能插件”（Game Feature Plugins, GFPs）。

**它解决的核心问题是**：在大型或需要持续扩展的游戏项目中，如何将新地图、新角色、新玩法机制、DLC 内容等功能模块化，使其能够独立于主游戏项目开发、测试、打包和动态加载/卸载，从而实现更高效的团队协作和内容管理。

此插件提供了定义 GFP 生命周期、处理资产引用、管理依赖关系以及在运行时激活/停用功能的核心类和系统。

## 使用场景

- 你的游戏计划发布多个 DLC，每个 DLC 包含新地图、任务和装备 → 使用 `GameFeatures` 为每个 DLC 创建一个 GFP。
- 你的游戏需要一个复杂的活动系统，赛季更新时更换整个玩法模式 → 使用 `GameFeatures` 管理每个赛季的玩法插件。
- 你的团队非常大，需要并行开发不同的游戏功能模块（如战斗系统、载具系统） → 使用 `GameFeatures` 作为模块边界，解耦开发。
- 你需要一个可选的教育模式或辅助功能模块，希望用户可以自由开关 → 使用 GFP 来封装这些可选功能。

## 蓝图用法

`GameFeatures` 提供了蓝图管理 Game Feature 插件状态（加载、激活）的节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load Game Feature Plugin` | 异步加载指定的 Game Feature 插件。加载完成后可以激活它。 | `UAsyncAction_LoadGameFeaturePlugin` |
| `Activate Game Feature Plugin` | 激活一个已加载的 Game Feature 插件，使其功能在游戏世界中生效。 | `UAsyncAction_LoadGameFeaturePlugin` |
| `Deactivate Game Feature Plugin` | 停用一个已激活的 Game Feature 插件，尝试将其功能从游戏世界移除。 | `UAsyncAction_LoadGameFeaturePlugin` |
| `Unload Game Feature Plugin` | 卸载一个已加载的 Game Feature 插件，释放其占用的内存和资源。 | `UAsyncAction_LoadGameFeaturePlugin` |
| `Get Game Feature Plugin State` | 获取指定 Game Feature 插件的当前状态（已卸载、已加载、已激活等）。 | `UGameFeaturesSubsystem` |
| `Get Loaded Game Feature Plugins` | 获取当前所有已加载的 Game Feature 插件名称列表。 | `UGameFeaturesSubsystem` |

### 使用示例（蓝图描述）

1.  **加载并激活一个 GFP**：
    *   在你的 UI 或关卡蓝图中，调用 `Load Game Feature Plugin` 节点。
    *   输入你的 GFP 插件名称（例如 “GFP_Season1”）。
    *   `OnLoaded` 引脚连接到一个 `Activate Game Feature Plugin` 节点，使用相同的插件名称。
    *   `OnActivated` 引脚后可以执行加载完成后的逻辑，如显示“赛季1内容已加载”提示。

2.  **切换 GFP（停用旧的，加载新的）**：
    *   首先调用 `Deactivate Game Feature Plugin` 节点停用当前的 GFP（例如 “GFP_Season1”）。
    *   `OnDeactivated` 引脚连接到一个新的 `Load Game Feature Plugin` 节点，加载新 GFP（例如 “GFP_Season2”）。
    *   这样可以实现运行时的功能热切换。

## C++ 用法

C++ 接口提供了对 GFP 生命周期更底层、更灵活的控制。

### 头文件引入

```cpp
#include "GameFeaturesSubsystem.h"
#include "GameFeaturePluginOperationResult.h"
```

### 基本用法

以下示例展示如何在 C++ 中加载、激活和查询 GFP 状态。

```cpp
// (示例代码，基于UE5 GameFeatures子系统典型用法)
#include "GameFeaturesSubsystem.h"

// 1. 加载一个 Game Feature 插件
FString MyGFPName = TEXT("GFP_MyNewContent");
UGameFeaturesSubsystem& Subsystem = UGameFeaturesSubsystem::Get();

Subsystem.LoadGameFeaturePlugin(MyGFPName, FGameFeaturePluginLoadComplete::CreateLambda(
    [MyGFPName](const UE::GameFeatures::FResult& Result)
    {
        if (Result.HasValue())
        {
            UE_LOG(LogTemp, Log, TEXT("GFP '%s' loaded successfully."), *MyGFPName);
            // 加载成功后可以进一步激活
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to load GFP '%s': %s"), *MyGFPName, *Result.GetError());
        }
    }
));

// 2. 检查 GFP 状态
EGameFeaturePluginState CurrentState = Subsystem.GetGameFeaturePluginState(MyGFPName);
if (CurrentState == EGameFeaturePluginState::Loaded)
{
    // 插件已加载，可以激活
    Subsystem.ActivateGameFeaturePlugin(MyGFPName, FGameFeaturePluginLoadComplete::CreateLambda(
        [MyGFPName](const UE::GameFeatures::FResult& Result)
        {
            if (Result.HasValue())
            {
                UE_LOG(LogTemp, Log, TEXT("GFP '%s' activated."), *MyGFPName);
            }
        }
    ));
}
```

### 进阶用法

在 `UObject` 或 `AActor` 中管理 GFP 的生命周期，确保在对象销毁时正确清理。

```cpp
// MyActor.h
UCLASS()
class AMyContentManagerActor : public AActor
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable)
    void LoadAndActivateFeature(const FString& FeatureName);

protected:
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    FString ActiveFeatureName;
    FDelegateHandle ActivationDelegateHandle;
};

// MyActor.cpp
void AMyContentManagerActor::LoadAndActivateFeature(const FString& FeatureName)
{
    UGameFeaturesSubsystem& Subsystem = UGameFeaturesSubsystem::Get();

    // 先停用旧的（如果有）
    if (!ActiveFeatureName.IsEmpty())
    {
        Subsystem.DeactivateGameFeaturePlugin(ActiveFeatureName);
    }

    // 加载新的
    Subsystem.LoadGameFeaturePlugin(FeatureName, FGameFeaturePluginLoadComplete::CreateLambda(
        [this, FeatureName, &Subsystem](const UE::GameFeatures::FResult& Result)
        {
            if (Result.HasValue())
            {
                // 保存引用以便清理
                ActiveFeatureName = FeatureName;
                ActivationDelegateHandle = Subsystem.AddOnGameFeaturePluginActivationChangeDelegate(
                    FGameFeaturePluginActivationChange::FDelegate::CreateLambda(
                        [this](const FString& PluginName, bool bActive)
                        {
                            if (bActive && PluginName == ActiveFeatureName)
                            {
                                UE_LOG(LogTemp, Log, TEXT("Feature %s is now active in the world."), *PluginName);
                            }
                        }
                    )
                );
                // 激活
                Subsystem.ActivateGameFeaturePlugin(FeatureName, FGameFeaturePluginLoadComplete());
            }
        }
    ));
}

void AMyContentManagerActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Super::EndPlay(EndPlayReason);

    // 清理：停用并移除委托
    UGameFeaturesSubsystem& Subsystem = UGameFeaturesSubsystem::Get();
    if (!ActiveFeatureName.IsEmpty())
    {
        Subsystem.DeactivateGameFeaturePlugin(ActiveFeatureName);
    }
    Subsystem.RemoveOnGameFeaturePluginActivationChangeDelegate(ActivationDelegateHandle);
}
```

## Demo 示例

一个最小示例，展示如何创建一个简单的 GFP 并用 C++ 加载它。

**1. 创建 GFP 插件结构**
在你的项目或引擎插件目录下，创建一个新插件 `GFP_DemoFeature`。其 `.uplugin` 文件需包含 `"GameFeatures"` 在 `Plugins` 依赖数组中。

**2. 主模块代码 (DemoFeatureRuntime.h)**
```cpp
// DemoFeatureRuntime.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FDemoFeatureRuntimeModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

DECLARE_LOG_CATEGORY_EXTERN(LogDemoFeature, Log, All);
```

**3. 主模块代码 (DemoFeatureRuntime.cpp)**
```cpp
// DemoFeatureRuntime.cpp
#include "DemoFeatureRuntime.h"

#define LOCTEXT_NAMESPACE "FDemoFeatureRuntimeModule"

DEFINE_LOG_CATEGORY(LogDemoFeature);

void FDemoFeatureRuntimeModule::StartupModule()
{
    // 这里可以注册你的GFP特有的资产类型、GameplayAbility、GAS组件等。
    UE_LOG(LogDemoFeature, Log, TEXT("DemoFeature module has started up. This content is now available."));
}

void FDemoFeatureRuntimeModule::ShutdownModule()
{
    // 这里进行清理。
    UE_LOG(LogDemoFeature, Log, TEXT("DemoFeature module has shut down. This content is no longer available."));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FDemoFeatureRuntimeModule, DemoFeatureRuntime)
```

**4. 主游戏代码中使用**
```cpp
// 在你的游戏模式或某个管理器中
#include "GameFeaturesSubsystem.h"

void UMyGameInstance::Init()
{
    Super::Init();
    // 在游戏初始化时加载这个演示功能
    UGameFeaturesSubsystem::Get().LoadGameFeaturePlugin(
        TEXT("GFP_DemoFeature"), // 这里使用你的GFP插件名
        FGameFeaturePluginLoadComplete::CreateLambda([](const UE::GameFeatures::FResult& Result) {
            if (Result.HasValue()) {
                // 加载成功，内容可用了（例如，新的武器、NPC已经注册）
            }
        })
    );
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 该插件主要依赖引擎核心模块，没有引入额外的独特模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `f604c6dd` | CollectDepends when AddOrUpdateRef, skip dep walk for deps already counted at >= target state in thi | 优化了依赖收集逻辑，避免重复遍历已计数的依赖项。 |
| 2026-05-12 | `a7ff6fd5` | [GameFeatures] Added optional CVar property gating for AddWorldPartitionContent activation. | 为 `AddWorldPartitionContent` 激活添加了可选的 CVar 属性门控。 |
| 2026-04-30 | `3f194f64` | Only load verse path mapper bin in cooked non editor builds. Cooked editor still requires all plugin | 调整了 Verse 路径映射器的加载逻辑，仅在非编辑器的打包版本中加载。 |
| 2026-04-29 | `2353b745` | [Backout] - CL53308230 | 回滚了之前的提交 CL53308230。 |
| 2026-04-29 | `fa918b28` | Only load verse path mapper bin in cooked non editor builds. Cooked editor still requires all plugin | 与 `3f194f64` 内容相同，可能是一次提交的重复记录或修复。 |

### 维护评价

- **创建时间**：该插件于 **2024年1月31日** 从 **Experimental** 目录移入 **Runtime** 目录，标志着其功能进入 Beta 阶段。
- **活跃度**：尽管文档生成时间为2025年，但提供的 git 历史显示在 **2026年5月** 仍有活跃的功能性更新和优化。这表明该插件在预期的时间线内处于**积极维护**状态。
- **状态**：`.uplugin` 中 `IsBetaVersion: true`，`EnabledByDefault: false`。这意味着它仍处于 Beta 测试阶段，且**默认未启用**。用户需要在项目的 `.uproject` 文件中显式启用。
- **推荐度**：**推荐在项目中使用**。它是 UE5 模块化游戏功能的官方和核心解决方案。虽然标记为 Beta，但已经过版本迭代和实际项目检验（如 Lyra 项目）。对于计划采用模块化架构或发布 DLC 的项目，这是必备的基础设施。使用时需注意其 Beta 状态可能带来的 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameFeatures)
- [官方文档]() (暂无)
- [测试用例]() (通常位于 `Engine/Tests/` 目录下)