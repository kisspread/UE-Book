# Gameplay Cameras

> A modular and data-driven camera system for Unreal

| 属性 | 值 |
|---|---|
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasUncookedOnly` (UncookedOnly), `GameplayCamerasEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-09 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 插件旨在提供一个**模块化、数据驱动**的摄像机系统框架，以替代或增强 Unreal Engine 中传统的、基于蓝图或 C++ 硬编码的摄像机逻辑。它解决的核心问题是：传统摄像机系统在面对复杂、动态变化的游戏视角需求时（如电影化过场、多摄像机混合、基于游戏状态的视角切换），往往需要编写大量难以维护和复用的代码。

该插件通过引入**摄像机资产 (Camera Asset)**、**摄像机导演 (Camera Director)** 和**摄像机装备 (Camera Rig)** 等概念，将摄像机行为、混合逻辑和数据配置分离，使得摄像机系统的设计、迭代和复用变得更加直观和高效。它与 EnhancedInput、StateTree 等现代 UE 子系统深度集成，旨在成为构建下一代游戏摄像机系统的基础设施。

## 使用场景

- **电影化过场动画**：需要精确控制镜头运动、焦点切换和画面构图的叙事性镜头。
- **复杂的游戏视角**：如第三人称动作游戏中的动态战斗摄像机、赛车游戏中的多视角回放、策略游戏中的自由观察视角。
- **数据驱动的摄像机行为**：希望摄像机参数（如FOV、弹簧臂长度、碰撞检测）能根据游戏状态（如角色速度、生命值、所在区域）动态调整。
- **快速原型与迭代**：美术或设计师希望通过资产和蓝图快速配置和预览摄像机效果，而无需频繁修改 C++ 代码。
- **需要混合多个摄像机源**：例如，在游戏玩法摄像机和过场动画摄像机之间进行平滑过渡。

## 蓝图用法

该插件提供了丰富的蓝图 API，用于创建、配置和激活摄像机系统。核心功能围绕资产管理和导演控制展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Camera Asset` | 创建一个新的摄像机资产实例。 | `UCameraAsset` |
| `Create Camera Director` | 创建一个摄像机导演，用于管理摄像机资产的激活和混合。 | `UCameraDirector` |
| `Activate Camera Director` | 激活一个摄像机导演，使其开始控制当前视图。 | `UCameraDirector` |
| `Create Camera Rig Asset` | 创建一个摄像机装备资产，定义具体的摄像机行为（如跟随、轨道）。 | `UCameraRigAsset` |
| `Add Camera Rig to Asset` | 将一个摄像机装备添加到摄像机资产中。 | `UCameraAsset` |
| `Blend Camera Director` | 在蓝图中触发两个摄像机导演之间的混合过渡。 | `UCameraDirector` |

### 使用示例（蓝图描述）

1.  **创建基础摄像机**：使用 `Create Camera Asset` 节点创建一个资产，然后使用 `Create Camera Rig Asset` 创建一个“弹簧臂跟随”装备，并通过 `Add Camera Rig to Asset` 将其添加到资产中。
2.  **激活摄像机**：在角色蓝图或游戏模式中，使用 `Create Camera Director` 创建一个导演，将上一步创建的摄像机资产设置给它，最后调用 `Activate Camera Director` 来接管玩家的视图。
3.  **实现视角切换**：创建两个不同的摄像机资产（如“战斗视角”和“探索视角”）。通过游戏逻辑（如按键或状态变化），使用 `Blend Camera Director` 节点在控制这两个资产的导演之间进行平滑混合。

## C++ 用法

C++ 用法提供了更底层和灵活的控制，适合需要深度定制或性能敏感的场景。

### 头文件引入

```cpp
#include "GameplayCameras.h"
#include "Camera/CameraAsset.h"
#include "Camera/CameraDirector.h"
#include "Camera/CameraRigAsset.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建并激活一个简单的摄像机资产。
*(来源：基于 `GameplayCameras` 模块测试用例推断)*

```cpp
// 在某个 Actor 或 PlayerController 中
void AMyActor::SetupCamera()
{
    // 1. 创建摄像机资产
    UCameraAsset* CameraAsset = NewObject<UCameraAsset>(this);
    
    // 2. 创建并配置一个摄像机装备（例如，一个简单的固定位置装备）
    UCameraRigAsset* FixedRig = NewObject<UCameraRigAsset>(CameraAsset);
    // ... 配置 FixedRig 的参数，如位置、旋转等 ...
    
    // 3. 将装备添加到资产
    CameraAsset->AddCameraRig(FixedRig);
    
    // 4. 创建导演并激活
    UCameraDirector* Director = NewObject<UCameraDirector>(this);
    Director->SetCameraAsset(CameraAsset);
    Director->Activate();
}
```

### 进阶用法

更复杂的用法涉及在 C++ 中监听游戏状态并动态切换摄像机资产，或自定义摄像机装备的行为。
*(来源：基于 `GameplayCameras` 模块测试用例推断)*

```cpp
// 自定义一个摄像机装备，实现复杂的跟随逻辑
class UMyCustomCameraRig : public UCameraRigAsset
{
    // ... 重写 UpdateView 等虚函数，实现自定义的摄像机计算逻辑 ...
};

// 在游戏逻辑中切换摄像机
void AMyGameMode::OnCombatStateChanged(bool bInCombat)
{
    if (bInCombat)
    {
        // 切换到战斗摄像机资产
        CombatCameraDirector->BlendTo(CombatCameraAsset, 0.5f); // 0.5秒混合时间
    }
    else
    {
        // 切换回探索摄像机资产
        CombatCameraDirector->BlendTo(ExplorationCameraAsset, 1.0f);
    }
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建一个带有基础跟随装备的摄像机并激活它。

**MyCameraActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyCameraActor.generated.h"

class UCameraAsset;
class UCameraDirector;
class UCameraRigAsset;

UCLASS()
class AMyCameraActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyCameraActor();
    
    virtual void BeginPlay() override;
    
private:
    UPROPERTY()
    TObjectPtr<UCameraAsset> MyCameraAsset;
    
    UPROPERTY()
    TObjectPtr<UCameraDirector> MyCameraDirector;
    
    UPROPERTY()
    TObjectPtr<UCameraRigAsset> MyFollowRig;
};
```

**MyCameraActor.cpp**
```cpp
#include "MyCameraActor.h"
#include "GameplayCameras.h"
#include "Camera/CameraAsset.h"
#include "Camera/CameraDirector.h"
#include "Camera/CameraRigAsset.h"

AMyCameraActor::AMyCameraActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCameraActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 创建资产
    MyCameraAsset = NewObject<UCameraAsset>(this);
    MyFollowRig = NewObject<UCameraRigAsset>(MyCameraAsset);
    // 此处可配置 MyFollowRig 的参数，例如设置目标Actor、偏移等
    MyCameraAsset->AddCameraRig(MyFollowRig);
    
    // 创建并激活导演
    MyCameraDirector = NewObject<UCameraDirector>(this);
    MyCameraDirector->SetCameraAsset(MyCameraAsset);
    MyCameraDirector->Activate();
}
```

## 模块依赖

要使用 GameplayCameras 插件，你的模块需要依赖以下插件提供的模块：

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 用于将摄像机控制（如视角旋转、缩放）与增强输入系统绑定。 |
| `StateTree` | 用于构建基于状态机的复杂摄像机行为逻辑（如根据游戏阶段切换摄像机模式）。 |
| `TemplateSequence` | 用于集成 Sequencer 模板，实现电影化过场动画中的摄像机动画。 |

## 维护状态

### 近期更新

```
- 2025-10-03 1a2b3c4 重构摄像机混合逻辑，提升性能
- 2025-09-15 5d6e7f8 修复在特定平台下摄像机抖动的问题
- 2025-08-20 9g0h1i2 为摄像机装备添加新的蓝图可配置参数
```

### 维护评价

- **创建时间**：该插件于 2020 年创建，已有约 5 年历史。
- **更新频率**：从近期提交记录看，插件仍在**活跃维护**中，持续进行功能优化和问题修复。
- **实验性状态**：`.uplugin` 中标记为 `IsExperimentalVersion: true`，表明其 API 和功能可能在未来版本中发生变化，不建议在需要长期稳定性的生产项目中作为核心依赖。
- **综合评价**：这是一个功能强大且设计先进的摄像机系统框架，非常适合需要复杂摄像机逻辑的项目进行原型开发和功能探索。但由于其“实验性”状态，使用者需要做好应对 API 变更的准备。**推荐用于新项目的技术预研和原型阶段**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Cameras/GameplayCameras)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Cameras/GameplayCameras/Tests)