# Gameplay Cameras

> A modular and data-driven camera system for Unreal

| 属性 | 值 |
|---|---|
| 中文名 | 游戏摄像机系统 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

`GameplayCameras` 插件提供了一套**模块化、数据驱动**的摄像机系统，旨在取代或补充引擎内置的传统 `APlayerCameraManager` 机制。其核心思想是将摄像机行为（如镜头震动、视场、目标偏移等）封装为可独立配置、组合和复用的 **CameraRig** 资产。通过蓝图节点，设计师和程序员可以灵活地在运行时设置这些摄像机装备的参数，从而实现高度动态和复杂的摄像机行为，而无需编写大量硬编码的 C++ 逻辑。

## 使用场景

- 你需要根据玩家状态（如冲刺、瞄准、受伤）动态切换或混合不同的摄像机效果（如视场角变化、景深、镜头震动）。
- 你希望将摄像机行为的设计权交给关卡设计师或技术美术，让他们通过资产（而非代码）来调整和迭代摄像机效果。
- 你的游戏有多个摄像机视角或模式（如载具摄像机、自由视角、过场动画），并需要一种统一的方式来管理它们之间的过渡和混合。
- 你需要一个可扩展的摄像机系统，可以方便地添加自定义的摄像机效果或数据通道。

## 蓝图用法

该插件的核心功能是提供用于在蓝图中设置和获取 CameraRig 参数的自定义节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Camera Rig Parameters` | 给定一个摄像机装备资产，设置其所有已暴露参数的值。 | `UK2Node_SetCameraRigParameters` |
| `Get Camera Rig Parameters` | 给定一个摄像机装备资产，获取其所有已暴露参数的当前值。 | `UK2Node_GetCameraRigParameters` |
| `Set Camera Rig Parameter` | 给定一个摄像机装备资产，设置其中一个指定参数的值。 | `UK2Node_SetCameraRigParameter` |
| `Get Camera Rig Parameter` | 给定一个摄像机装备资产，获取其中一个指定参数的当前值。 | `UK2Node_GetCameraRigParameter` |

### 使用示例（蓝图描述）

1.  **创建摄像机装备资产**: 在内容浏览器中右键 -> GameplayCameras -> CameraRig Asset。
2.  **在蓝图中使用**:
    - 在事件图表中，拖拽出 `Set Camera Rig Parameters` 节点。
    - 将你的 CameraRig 资产对象连接到节点的 `CameraRig` 输入引脚。
    - 节点会根据资产中定义的参数自动生成输入引脚。将对应的值（如浮点数、向量）连接到这些引脚。
    - 当节点执行时，它会将这些值设置到指定的摄像机装备实例上。

## C++ 用法

由于该插件的模块主要是 Runtime 和 Editor，并且提供蓝图节点，其 C++ 用法更多体现在内部实现和扩展上。基于提供的头文件，可以推断出其核心 API 围绕 `UCameraRigAsset` 及其参数的访问。

### 头文件引入

```cpp
#include "GameplayCamerasModule.h" // 核心模块
// 若需操作特定资产，可能需要引入对应资产的头文件，例如：
// #include "CameraRigAsset.h"
```

### 基本用法（推测）

虽然没有直接的 C++ API 用于从游戏逻辑设置参数，但可以推断参数系统通过蓝图暴露，其底层可能涉及 `FGameplayCamerasContext` 或类似的上下文对象来传递参数。扩展摄像机系统通常涉及创建新的 `UCameraNode` 子类并将其集成到 CameraRig 资产中。

### 进阶用法（推测）

插件设计为模块化，支持通过继承 `UK2Node_CameraRigBase` 来创建自定义的蓝图节点，用于处理摄像机装备的参数。开发者可以为新的 `ECameraVariableType` 或 `ECameraContextDataType` 添加支持，通过 `FCameraVariablePinTypeHelper` 和 `FCameraContextDataPinTypeHelper` 类来定义新的引脚类型。

## Demo 示例

由于该插件的主要交互界面是蓝图资产和编辑器节点，一个典型的“使用”示例是在蓝图中完成的（如上文蓝图用法所述）。以下是一个极简的、概念性的 C++ 代码框架，说明如何可能开始与摄像机装备系统交互（注意：具体实现细节取决于插件内部 API）。

**MyCameraManager.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCameraManager.generated.h"

class UCameraRigAsset;

UCLASS()
class AMyCameraManager : public AActor
{
    GENERATED_BODY()

public:
    AMyCameraManager();

    virtual void BeginPlay() override;

    // 示例：一个存储摄像机装备资产引用的属性
    UPROPERTY(EditAnywhere, Category = "Camera")
    TObjectPtr<UCameraRigAsset> DefaultCameraRig;

    // 示例：一个在蓝图中调用的函数，用于应用摄像机装备
    UFUNCTION(BlueprintCallable, Category = "Camera")
    void ApplyCameraRig(UCameraRigAsset* RigToApply);
};
```

**MyCameraManager.cpp**
```cpp
#include "MyCameraManager.h"
#include "CameraRigAsset.h" // 假设这是摄像机装备资产的头文件

AMyCameraManager::AMyCameraManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCameraManager::BeginPlay()
{
    Super::BeginPlay();

    // 在游戏开始时应用默认摄像机装备（概念性代码）
    if (DefaultCameraRig)
    {
        ApplyCameraRig(DefaultCameraRig);
    }
}

void AMyCameraManager::ApplyCameraRig(UCameraRigAsset* RigToApply)
{
    if (RigToApply)
    {
        // 实际调用会涉及插件内部的摄像机管理器或上下文。
        // 此处为示意代码，展示调用入口。
        // 例如，可能通过一个全局的或本地玩家的摄像机管理器来激活这个装备。
        UE_LOG(LogTemp, Log, TEXT("Applying Camera Rig: %s"), *RigToApply->GetName());
        // ... 实际的插件API调用 ...
    }
}
```

## 模块依赖

从 `GameplayCamerasUncookedOnly` 模块的头文件（如 `K2Node_*.h`）来看，它深度依赖蓝图编译系统。使用者在自己的模块中若要引用 `GameplayCameras` 核心功能，可能需要依赖 `GameplayCameras` 模块本身。对于 Editor 工具开发，则需要依赖 `GameplayCamerasEditor`。

| 模块 | 用途 |
|---|---|
| `GameplayCameras` | 摄像机装备系统的核心运行时逻辑和资产类型定义 |
| `GameplayCamerasEditor` | 编辑器集成，资产编辑器、自定义节点、细节面板等 |
| `GameplayCamerasUncookedOnly` | 仅在未打包编辑器中使用的蓝图图表节点（如 `K2Node_SetCameraRigParameters`） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复了PIE中摄像机变量覆盖不生效的问题。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 为部分追踪通道添加或更新了描述信息。 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | 包含对GameplayCameras插件的常规更新。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到UE_LOGF格式化版本。 |

### 维护评价

该插件创建于约 6 年前，并被标记为**实验性** (`IsExperimentalVersion=true`)。然而，从最近的提交记录来看（最后一次更新在 2026 年 5 月），它仍在被**积极维护和更新**。近期的提交主要涉及功能修复（如PIE变量覆盖）和代码质量改进，表明 Epic 仍在对其进行投入。这是一个功能强大且在持续发展的系统，但由于其“实验性”标签，API 和功能可能在未来版本中发生变化。**推荐关注和使用，但需做好应对未来可能变更的准备**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)