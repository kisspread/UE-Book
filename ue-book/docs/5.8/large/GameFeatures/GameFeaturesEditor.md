# Game Features

> Support for modular Game Feature Plugins（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 游戏功能 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameFeatures` (Runtime), `GameFeaturesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-31 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameFeatures) | |

## 用途

Game Features 插件提供了一套运行时框架，用于管理**游戏功能插件 (Game Feature Plugins)** 的生命周期。其核心目的是实现**模块化的游戏开发架构**。它允许开发者将新的游戏内容（如关卡、角色、游戏模式、资产和逻辑）打包成独立的插件，并在运行时动态加载、激活和停用这些插件，而无需修改主游戏代码。这使得游戏的扩展、DLC 发布、A/B 测试和不同平台的差异化构建变得更加灵活和安全。编辑器模块（`GameFeaturesEditor`）则提供了创建、管理和调试这些游戏功能插件的工具。

## 使用场景

-   **大型游戏/DLC 开发**：将后续发布的游戏内容、扩展包或 DLC 制作成游戏功能插件，实现与核心游戏的解耦和按需加载。
-   **平台/配置差异化**：为不同平台（PC、主机、移动设备）或不同硬件配置创建特定的游戏功能插件，主游戏根据平台加载对应插件。
-   **模块化架构与团队并行开发**：不同团队可以并行开发各自负责的游戏功能模块，最终作为独立插件集成。
-   **运行时功能切换与 A/B 测试**：通过动态启用或禁用特定的游戏功能插件，可以快速切换游戏功能或进行线上 A/B 测试。
-   **自定义插件模板**：利用编辑器设置（`UGameFeaturesEditorSettings`）创建项目特定的游戏功能插件模板，加速开发流程。

## 蓝图用法

Game Features 插件的核心运行时逻辑由引擎内部管理，其蓝图节点主要用于与运行时状态交互。由于提供的代码片段主要为编辑器侧，以下节点基于此类插件的通用 API 推导：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Game Feature State` | 异步设置指定游戏功能插件的当前状态（如加载、激活、停用）。 | `UGameFeaturesSubsystem` |
| `Get Game Feature State` | 查询指定游戏功能插件的当前状态。 | `UGameFeaturesSubsystem` |
| `Get All Game Feature Plugins` | 获取所有已注册的游戏功能插件列表。 | `UGameFeaturesSubsystem` |
| `Is Game Feature Plugin Active` | 检查指定游戏功能插件当前是否处于激活状态。 | `UGameFeaturesSubsystem` |

### 使用示例（蓝图描述）

1.  **激活一个游戏功能**：
    在需要启动新游戏内容（如新关卡模式）的地方，调用 `Set Game Feature State` 节点，传入目标插件的 URL（或资产引用）和目标状态 `EGameFeaturePluginState::Active`。使用该节点的 `On Completed` 或 `On Failed` 输出执行引脚来处理异步结果。

2.  **检查功能是否就绪**：
    在尝试使用某个游戏功能提供的角色或武器前，先使用 `Is Game Feature Plugin Active` 节点进行检查。若返回 `false`，则可以提示玩家该功能未解锁或正在加载。

## C++ 用法

Game Features 的 C++ API 主要集中在 `UGameFeaturesSubsystem` 类上，用于程序化地管理插件生命周期。

### 头文件引入

```cpp
#include "GameFeaturesSubsystem.h"
```

### 基本用法

以下示例展示了如何通过代码加载并激活一个游戏功能插件。此模式通常在需要程序化控制功能解锁或内容的场景下使用。
*（来源：基于 `GameFeaturesSubsystem` 公共接口及生命周期回调推导）*

```cpp
#include "GameFeaturesSubsystem.h"

void UMyGameInstance::ActivateNewContent()
{
    // 获取游戏功能子系统单例
    UGameFeaturesSubsystem& GFS = UGameFeaturesSubsystem::Get();

    // 定义要激活的游戏功能插件URL (可以是本地路径或 .uplugin 文件名)
    const FString PluginURL = TEXT("/Game/Features/NewWeapons/NewWeapons.uplugin");

    // 定义激活状态改变时的回调
    FGameFeaturePluginStateChangeDelegate StateChangeDelegate;
    StateChangeDelegate.BindLambda([this](const UE::GameFeatures::FResult& Result, const FString& PluginURL, EGameFeaturePluginState NewState)
    {
        if (Result.HasValue())
        {
            UE_LOG(LogTemp, Log, TEXT("Game Feature '%s' state changed to %s"), *PluginURL, *UEnum::GetValueAsString(NewState));
            // 插件已激活，可以安全地访问其提供的资产或子系统
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to change state of Game Feature '%s': %s"), *PluginURL, *Result.GetError());
        }
    });

    // 请求激活插件
    GFS.ChangeGameFeaturePluginState(PluginURL, EGameFeaturePluginState::Active, StateChangeDelegate);
}
```

### 进阶用法

结合编辑器扩展，在编辑器中为自定义的游戏功能数据资产提供定制的检查器界面。`FGameFeatureDataDetailsCustomization` 展示了如何为 `UGameFeatureData` 创建自定义细节面板，允许开发者直接在编辑器中控制游戏功能插件的初始状态（如默认加载状态）。
*（来源：`Private/GameFeatureDataDetailsCustomization.h`）*

```cpp
#include "GameFeatureDataDetailsCustomization.h"
#include "DetailLayoutBuilder.h"
#include "GameFeatureData.h"

// 这是一个编辑器自定义类的示例片段，展示了如何读取和修改关联插件的状态
void FGameFeatureDataDetailsCustomization::SetDefaultGameFeatureState(EGameFeaturePluginState DesiredState)
{
    if (PluginPtr.IsValid() && ObjectsBeingCustomized.Num() > 0)
    {
        // 通过插件元数据设置其默认初始状态
        FPluginDescriptor& Descriptor = PluginPtr->GetDescriptor();
        // ... (修改描述符中与游戏功能状态相关的字段)
        // 提交编辑
        if (IPlugin* PluginInterface = PluginPtr.Get())
        {
            // 将修改保存到 .uplugin 文件
        }
    }
}
```

## Demo 示例

一个最小化的 C++ 类，演示如何查询游戏功能插件状态。

**MyFeatureChecker.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFeaturesSubsystem.h"
#include "MyFeatureChecker.generated.h"

UCLASS()
class UMyFeatureChecker : public UObject
{
    GENERATED_BODY()

public:
    // 检查指定功能是否已激活
    UFUNCTION(BlueprintCallable, Category = "GameFeatures")
    bool IsFeatureActive(const FString& PluginURL) const;

    // 请求激活功能并等待结果
    UFUNCTION(BlueprintCallable, Category = "GameFeatures")
    void RequestFeatureActivation(const FString& PluginURL, FGameFeaturePluginStateChangeDelegate OnCompleted);
};
```

**MyFeatureChecker.cpp**
```cpp
#include "MyFeatureChecker.h"
#include "GameFeaturesSubsystem.h"

bool UMyFeatureChecker::IsFeatureActive(const FString& PluginURL) const
{
    UGameFeaturesSubsystem& GFS = UGameFeaturesSubsystem::Get();
    EGameFeaturePluginState CurrentState;
    if (GFS.GetGameFeaturePluginState(PluginURL, CurrentState))
    {
        return CurrentState == EGameFeaturePluginState::Active;
    }
    return false;
}

void UMyFeatureChecker::RequestFeatureActivation(const FString& PluginURL, FGameFeaturePluginStateChangeDelegate OnCompleted)
{
    UGameFeaturesSubsystem& GFS = UGameFeaturesSubsystem::Get();
    GFS.ChangeGameFeaturePluginState(PluginURL, EGameFeaturePluginState::Active, OnCompleted);
}
```

## 模块依赖

根据 `GameFeaturesEditor` 的 `Build.cs` 文件推断，该插件主要依赖引擎核心和编辑器框架。

| 模块 | 用途 |
|---|---|
| `GameFeaturesSubsystem` | （推断）提供游戏功能插件生命周期管理的核心运行时子系统。 |
| `DeveloperSettings` | 用于定义可配置的编辑器设置 (`UGameFeaturesEditorSettings`)。 |

**说明**：该插件大量依赖 Unreal Engine 的核心模块（如 Core, CoreUObject, Engine）和插件/编辑器框架（如 Plugins, UnrealEd），这些均为常见依赖，此处省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `f604c6dd` | CollectDepends when AddOrUpdateRef, skip dep walk for deps already counted at >= target state in this | 优化插件依赖收集逻辑，避免对已满足条件的依赖重复遍历，提升性能。 |
| 2026-05-12 | `a7ff6fd5` | [GameFeatures] Added optional CVar property gating for AddWorldPartitionContent activation. | 为“添加世界分区内容”功能添加了可选的CVar属性门控，增强了灵活性和配置能力。 |
| 2026-04-30 | `3f194f64` | Only load verse path mapper bin in cooked non editor builds. Cooked editor still requires all plugin | 调整了Verse路径映射器的加载策略，仅在打包的非编辑器版本中加载，优化了打包编辑器版本的资源。 |
| 2026-04-29 | `2353b745` | [Backout] - CL53308230 | 回滚了之前的某个变更（CL53308230）。 |
| 2026-04-29 | `fa918b28` | Only load verse path mapper bin in cooked non editor builds. Cooked editor still requires all plugin | （同 `3f194f64`，为同一功能的两次提交） |

### 维护评价

-   **活跃维护**：插件处于**活跃维护**状态。虽然其核心从Experimental移到Runtime是2024年初，但最近的Git历史显示，在2026年4-5月仍有频繁的功能性更新和优化提交。
-   **实验性状态**：`.uplugin` 文件明确标记 `IsBetaVersion: true`，表明官方仍将其视为**测试版或实验性功能**。这意味着其API和行为在未来版本中可能会发生变化，不建议在需要长期稳定性的核心生产环境中深度依赖。
-   **功能增长**：近期的提交涉及依赖管理优化、新功能（CVar门控）添加以及打包策略调整，表明该插件正在根据项目需求不断成熟和扩展。
-   **推荐使用**：**推荐用于**新项目或希望采用模块化架构的项目进行原型开发和功能隔离。对于已上线或即将上线的项目，使用前需充分评估其测试版状态可能带来的风险，并做好应对未来API变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameFeatures)
- [官方文档]() （暂无）
- [测试用例]() （暂未在提供的片段中明确识别，通常位于插件目录的 `Tests/` 子目录或 `Engine/Tests/` 下）