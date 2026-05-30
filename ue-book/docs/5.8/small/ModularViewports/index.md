# Modular Viewports

> Viewport Client implementations that provide more flexibility and granularity than Game Viewport Client.

| 属性 | 值 |
|---|---|
| 中文名 | 模块化视口 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ModularViewports` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModularViewports) | |

## 用途

本插件的核心用途是**在已有的主游戏世界旁，创建并管理独立的、并行的游戏世界和视口**。它解决了一个特定问题：传统的 `UGameViewportClient` 是单例且与主游戏循环紧密耦合，难以在其之外安全地渲染第二份游戏内容（例如，用于画中画、第二窗口或编辑器内的独立预览）。

本插件通过提供可组合的、更轻量级的 `FViewportClient` 实现（如 `FCameraViewportClient`、`UPlayerViewportClient`）以及一个用于辅助游戏实例的管理框架（`FAuxiliaryGameInstance`），允许开发者以模块化的方式挂载额外的游戏视口。这些视口可以有自己的世界、相机、甚至玩家，并且它们的更新和渲染可以独立于主游戏循环进行，从而实现更灵活的多视口或多租户渲染场景。

## 使用场景

*   你需要在游戏主界面的一个角落显示另一个独立运行的游戏世界的实时画面（画中画）。
*   你需要为游戏创建一个独立的第二窗口，用于显示地图、监控摄像机或其他辅助视图。
*   你正在开发一个编辑器工具，需要在同一个编辑器窗口内嵌入一个独立、可控的游戏视口进行实时预览或调试。
*   你需要在一个游戏中并行运行多个独立的游戏逻辑和渲染上下文（多租户），例如后台模拟一个场景的同时在前台展示另一个场景。

## 蓝图用法

该插件主要通过 `USceneViewport` UMG 控件和 `UAuxiliaryGameInstance` 对象提供蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Show Game` | 加载指定的世界资产，并将其显示在视口中。 | `USceneViewport` |
| `Show Camera` | 绑定一个摄像机组件作为视口的渲染源。 | `USceneViewport` |
| `Show Player` | 绑定一个本地玩家及其摄像机管理器到视口。 | `USceneViewport` |
| `Unbind` | 解除当前视口客户端的所有绑定。 | `USceneViewport` |
| `Get Inner Game Instance` | 获取由 `Show Game` 自动创建的内部游戏实例。 | `USceneViewport` |
| `Make` | 创建一个新的 `UAuxiliaryGameInstance` 包装器，用于管理一个辅助游戏实例。 | `UAuxiliaryGameInstance` |
| `Get Game Instance` | 获取此包装器内部的 `UGameInstance`。 | `UAuxiliaryGameInstance` |

### 使用示例（蓝图描述）

1.  **画中画示例**:
    *   在 UMG Widget 蓝图中，放置一个 `USceneViewport` 控件。
    *   在某个事件（如按键按下）触发时，调用该控件的 `Show Game` 函数，并传入你预先准备好的小场景的世界资产（SoftObjectPath）。
    *   视口将加载该世界并开始渲染。你可以通过 `Get Inner Game Instance` 获取实例来进一步控制它。
    *   当需要关闭时，调用 `Unbind`。

2.  **第二窗口摄像机视图**:
    *   使用 `UAuxiliaryGameInstance::Make` 创建一个辅助游戏实例，并获取其 `GameInstance`。
    *   从该实例的 `World` 中获取或生成一个带有 `UCameraComponent` 的 Actor。
    *   创建一个新的 `SWindow`（可使用 `UE::Engine::NoControlsWindow` 等辅助函数配置窗口样式）。
    *   在窗口内创建一个 `SViewport`，然后通过 `UE::Engine::SetupRendering` 函数，将基于该摄像机创建的 `FCameraViewportClient` 与这个 `SViewport` 关联并注册到引擎。
    *   新窗口将显示该摄像机的实时画面。

## C++ 用法

### 头文件引入

```cpp
#include "Camera/CameraViewportClient.h"
#include "Components/SceneViewportWidget.h"
#include "Engine/AuxiliaryGameInstance.h"
#include "GameFramework/PlayerViewportClient.h"
#include "ViewportFunctions.h"
```

### 基本用法

**1. 创建一个纯摄像机视口（非 UObject，轻量级）**

```cpp
// 来源：基于源码推断，无特定测试文件
// 假设你有一个有效的 UCameraComponent* MyCamera
UE::FCameraViewportClient CameraViewportClient(*MyCamera);

// 假设你有一个 SViewport 控件 MyViewportWidget
TSharedRef<SViewport> ViewportWidget = MyViewportWidget;

// 设置并注册渲染
TSharedRef<FSceneViewport> SceneViewport = UE::Engine::SetupRendering(CameraViewportClient, ViewportWidget);

// CameraViewportClient 现在会驱动渲染，并接收输入（如果配置了触摸）。
// 当 MyCamera 或其所在 Actor 被销毁时，摄像机指针将失效，视口将变为空白。
```

**2. 创建一个辅助游戏实例并使用其视口客户端**

```cpp
// 来源：基于源码推断
// 创建一个管理特定世界资产的辅助实例
TUniquePtr<UE::Engine::FAuxiliaryGameInstance> AuxInstance = 
    UE::Engine::FAuxiliaryGameInstance::MakeUnique(TEXT("/Game/Maps/SubLevel"));

if (AuxInstance)
{
    UWorld* AuxWorld = AuxInstance->GetWorld();
    UGameInstance* AuxGameInstance = AuxInstance->GetGameInstance();
    
    // 通常，视口客户端由模块设置（如 UModularViewportsSettings::AuxiliaryGameInstanceClass 决定）。
    // 它会自动在视口关联时生成玩家。
    // 你可以通过 AuxGameInstance 获取更多控制。
}
```

### 进阶用法

**组合使用 `FAuxiliaryGameInstance` 和 `USceneViewport` (UObject 包装器) 在 C++ 中驱动 UMG**

```cpp
// 在某个 UObject（如 Actor 或 Widget）中持有对 UAuxiliaryGameInstance 和 USceneViewport 的引用。
UPROPERTY()
TObjectPtr<UAuxiliaryGameInstance> MyAuxInstance;

UPROPERTY()
TObjectPtr<USceneViewport> MySceneViewportWidget;

void AMyActor::SetupPipViewport()
{
    // 1. 创建辅助实例（UObject包装器，受GC管理）
    MyAuxInstance = UAuxiliaryGameInstance::Make(TEXT("/Game/Maps/PipWorld"));
    
    // 2. 假设你的UMG蓝图中已放置了USceneViewport控件，并暴露了它。
    // 通过 FindWidget 等方式获取其引用 MySceneViewportWidget。
    
    // 3. 使用ShowGame加载世界到该视口
    if (MySceneViewportWidget)
    {
        MySceneViewportWidget->ShowGame(MyAuxInstance->GetWorld()->GetSoftObjectPath());
    }
}
```

## Demo 示例

这是一个最小化示例，展示如何在 C++ Actor 中创建一个辅助游戏实例并将其视口嵌入到 UMG 的 `USceneViewport` 控件中。

**AMyPipActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyPipActor.generated.h"

class USceneViewport;
class UAuxiliaryGameInstance;

UCLASS()
class MYGAME_API AMyPipActor : public AActor
{
    GENERATED_BODY()

public:
    AMyPipActor();

    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "PIP")
    TSoftObjectPtr<UWorld> PipWorldAsset;

    // 假设此控件在关联的UMG Widget中，并通过某种方式绑定到此变量
    UPROPERTY(BlueprintReadWrite, Category = "PIP")
    TObjectPtr<USceneViewport> PipViewportWidget;

private:
    UPROPERTY()
    TObjectPtr<UAuxiliaryGameInstance> AuxiliaryInstance;
};
```

**AMyPipActor.cpp**
```cpp
#include "MyPipActor.h"
#include "Engine/AuxiliaryGameInstanceObject.h" // UAuxiliaryGameInstance
#include "Components/SceneViewportWidget.h" // USceneViewport

AMyPipActor::AMyPipActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyPipActor::BeginPlay()
{
    Super::BeginPlay();

    if (!PipWorldAsset.IsNull() && PipViewportWidget)
    {
        // 创建辅助实例
        AuxiliaryInstance = UAuxiliaryGameInstance::Make(PipWorldAsset);

        if (AuxiliaryInstance && AuxiliaryInstance->GetWorld())
        {
            // 将辅助世界加载到视口控件中
            PipViewportWidget->ShowGame(TSoftObjectPtr<UWorld>(AuxiliaryInstance->GetWorld()));
        }
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件的模块 (`ModularViewports`) 在 Build.cs 中依赖 `UnrealEd`，但这对于实现编辑器内预览功能是常见的，不影响运行时插件的独立性。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `9afeb538` | Fix crash while creating AuxiliaryGameInstance | 修复了创建辅助游戏实例时可能发生的崩溃。 |
| 2026-05-21 | `b885ccf9` | Engine: Roll back addition of projection method overloads on Local Player | 引擎回滚了对本地玩家投影方法重载的添加，可能影响相关视口投影计算。 |
| 2026-05-14 | `697042fe` | ASIS: Eliminate workarounds used to be necessary for multiple-screens touch support | 清除了为支持多屏触摸而存在的变通方案，优化了触摸输入逻辑。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 通过在视口客户端关联/解除关联时发送通知，重构了必要的重复代码。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚了之前的某次提交。 |

### 维护评价

该插件于 **2026 年 4 月创建**，至今不足一年，属于非常新的实验性插件。从近期 git 历史看，**维护非常活跃**，在最近一个月内有多次提交，内容包括**关键崩溃修复**和**代码重构优化**，表明 Epic 团队正在积极开发和打磨此功能。

**主要注意点**：
1.  **实验性标记**：插件在 .uplugin 中明确标记为 `IsExperimentalVersion: true`，这意味着其 API 可能在未来版本中发生变化，不建议在稳定的生产项目中依赖。
2.  **默认未启用**：`EnabledByDefault: false`，使用前需在项目设置中手动启用插件。
3.  **功能局限**：文档中明确说明了不支持网络、场景切换、同一资产多个实例等功能。

**综合建议**：这是一个**高潜力但高风险**的新功能。非常适合用于**原型验证、内部工具开发或研究性项目**，来实现复杂的多视口需求。如果需要在正式产品中使用，需密切关注后续版本更新，并做好 API 变动的准备。**推荐学习使用，但用于生产需谨慎评估**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModularViewports)
- 官方文档（暂无）
- 测试用例（暂未发现该插件目录内有自动化测试文件）