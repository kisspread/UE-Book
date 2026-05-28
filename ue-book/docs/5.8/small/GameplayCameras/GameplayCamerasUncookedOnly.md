# Gameplay Cameras

> A modular and data-driven camera system for Unreal（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 游戏摄像机 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 插件是一个**模块化、数据驱动的摄像机系统**，旨在替代或增强 Unreal Engine 的传统摄像机系统。它通过定义摄像机资产（Camera Rig Assets）和参数化摄像机行为，让设计师能够以可视化、数据驱动的方式创建复杂的摄像机动画和行为，而无需编写大量 C++ 代码。该系统允许将摄像机逻辑分解为可复用的摄像机节点（Camera Nodes），这些节点可以像蓝图节点一样在编辑器中组合和连接，从而创建出电影级或游戏化的摄像机视角。

## 使用场景

*   你需要快速原型设计一个带有复杂镜头切换、跟踪、抖动、景深变化的游戏摄像机 → 用 GameplayCameras 的摄像机资产编辑器。
*   你的游戏需要多种摄像机模式（如过场动画、第三人称跟随、瞄准镜视角）并希望它们能平滑过渡 → 使用摄像机混合器（Camera Rig）和求值器（Evaluator）。
*   你希望美术和策划能够独立调整摄像机行为，而不需要程序员介入 → 数据驱动的参数系统完美解决。
*   你正在开发一个需要精确控制摄像机轨迹和特效（如慢动作、颜色分级）的电影式游戏或应用。

## 蓝图用法

该插件主要提供一组用于在蓝图中与摄像机资产交互的**自定义蓝图节点（K2Node）**，这些节点允许你动态地设置或获取摄像机资产的参数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Camera Rig Parameters` | 为一个运行中的摄像机混合器（Camera Rig）设置其所有公开参数的值。 | `UK2Node_SetCameraRigParameters` |
| `Get Camera Rig Parameters` | 从一个摄像机混合器获取其所有公开参数的当前值。这是一个纯节点。 | `UK2Node_GetCameraRigParameters` |
| `Set Camera Rig Parameter` | 为一个运行中的摄像机混合器设置其单个公开参数的值。 | `UK2Node_SetCameraRigParameter` |
| `Get Camera Rig Parameter` | 从一个摄像机混合器获取其单个公开参数的当前值。这是一个纯节点。 | `UK2Node_GetCameraRigParameter` |

### 使用示例（蓝图描述）

1.  **设置摄像机参数**：
    *   在蓝图图表中，右键搜索并添加一个 `Set Camera Rig Parameter` 节点。
    *   在节点的 `Camera Rig` 引脚，连接一个有效的摄像机混合器对象引用（通常从摄像机求值器或摄像机管理器中获取）。
    *   节点会动态列出该摄像机混合器中所有已公开的参数引脚。将需要设置的参数引脚连接到变量或计算节点。
    *   执行该节点，即可将新值写入对应的摄像机参数。

2.  **获取摄像机参数**：
    *   添加一个 `Get Camera Rig Parameter` 节点。
    *   同样需要提供一个 `Camera Rig` 对象引用。
    *   选择你想要获取的参数名称，节点将输出一个 `Value` 引脚，其类型与参数定义匹配（如 Float, Vector, Blendable Struct 等）。
    *   将这个值用于其他蓝图逻辑，比如根据摄像机距离改变 UI 透明度。

## C++ 用法

该插件的运行时和编辑器功能通过 C++ 类暴露，但 `GameplayCamerasUncookedOnly` 模块主要提供编辑器扩展（蓝图节点）。要使用核心摄像机系统，应主要关注 `GameplayCameras` 模块。

### 头文件引入

```cpp
#include "GameplayCameras/Public/GameplayCamerasModule.h"
// 或者包含特定功能的头文件，如：
#include "GameplayCameras/Public/CameraRigAsset.h"
#include "GameplayCameras/Public/CameraNodeEvaluator.h"
```

### 基本用法

由于该插件以资产和蓝图节点为核心，典型的 C++ 用法涉及创建自定义摄像机节点求值器（Camera Node Evaluator）来扩展系统功能。以下是一个简化的自定义求值器示例结构：

```cpp
// 自定义摄像机节点求值器头文件
class FMyCustomCameraNodeEvaluator : public FCameraNodeEvaluator
{
public:
    FMyCustomCameraNodeEvaluator();

    // 当求值器初始化时调用，用于解析参数
    virtual void OnInitialize(const FCameraNodeEvaluatorInitializeParams& Params) override;

    // 每帧摄像机求值时调用，计算最终摄像机数据
    virtual void OnRun(const FCameraNodeEvaluationParams& Params, FCameraNodeEvaluationResult& OutResult) override;
};
```

```cpp
// 自定义摄像机节点求值器实现文件
#include "MyCustomCameraNodeEvaluator.h"

FMyCustomCameraNodeEvaluator::FMyCustomCameraNodeEvaluator()
{
    // 构造函数
}

void FMyCustomCameraNodeEvaluator::OnInitialize(const FCameraNodeEvaluatorInitializeParams& Params)
{
    // 从 FCameraNode 参数中读取自定义数据，例如：
    // const UMyCustomCameraNode* MyNode = Cast<UMyCustomCameraNode>(Params.CameraNode);
    // if (MyNode) { /* 读取节点属性 */ }
}

void FMyCustomCameraNodeEvaluator::OnRun(const FCameraNodeEvaluationParams& Params, FCameraNodeEvaluationResult& OutResult)
{
    // 在这里计算摄像机变换（Location, Rotation, FOV 等）
    OutResult.CameraPose.Location = FVector::ZeroVector;
    OutResult.CameraPose.Rotation = FRotator::ZeroRotator;
    OutResult.CameraPose.FieldOfView = 90.0f;
    // ... 应用自定义逻辑
}
```

**来源文件**: 该模式基于 Unreal Engine 摄像机系统的常见扩展方式，具体类定义可参考 `GameplayCameras` 模块中 `CameraNodeEvaluator.h` 相关文件。

### 进阶用法

与蓝图节点交互，可能需要在 C++ 中动态创建或查询摄像机资产及其参数。这通常通过 `UCameraRigAsset` 和相关的参数类来实现。

```cpp
// 获取一个摄像机混合器资产
UCameraRigAsset* CameraRig = LoadObject<UCameraRigAsset>(nullptr, TEXT("/Game/Cameras/MyCameraRig.MyCameraRig"));

if (CameraRig)
{
    // 遍历其所有公开的混合参数（Blendable Parameters）
    for (const FCameraRigBlendableParameter& BlendableParam : CameraRig->GetBlendableParameters())
    {
        UE_LOG(LogTemp, Log, TEXT("Parameter Name: %s"), *BlendableParam.ParameterName.ToString());
    }
}
```

## Demo 示例

由于 GameplayCameras 系统的核心是资产编辑器和蓝图节点，一个最小的“Demo”通常是在编辑器中创建一个摄像机资产并使用蓝图节点控制它。下面是一个极简的 C++ 类，用于在运行时获取并设置一个摄像机混合器参数，以演示 C++ 如何与系统交互。

```cpp
// MyCameraController.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCameraController.generated.h"

class UCameraRigAsset;
class UCameraRigComponent;

UCLASS()
class AMyCameraController : public AActor
{
    GENERATED_BODY()

public:
    AMyCameraController();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

public:
    // 引用一个在编辑器中创建的摄像机混合器资产
    UPROPERTY(EditAnywhere, Category = "Camera")
    TSoftObjectPtr<UCameraRigAsset> CameraRigAsset;

    // 用于运行时控制摄像机混合器的组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
    TObjectPtr<UCameraRigComponent> CameraRigComponent;

    // 想要设置的参数值
    UPROPERTY(EditAnywhere, Category = "Camera")
    float TargetFieldOfView = 60.0f;
};
```

```cpp
// MyCameraController.cpp
#include "MyCameraController.h"
#include "GameplayCameras/Public/CameraRigAsset.h"
#include "GameplayCameras/Public/Components/CameraRigComponent.h"

AMyCameraController::AMyCameraController()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建摄像机混合器组件
    CameraRigComponent = CreateDefaultSubobject<UCameraRigComponent>(TEXT("CameraRigComponent"));
    RootComponent = CameraRigComponent;
}

void AMyCameraController::BeginPlay()
{
    Super::BeginPlay();

    // 在运行时加载并应用摄像机混合器资产
    if (!CameraRigAsset.IsNull())
    {
        UCameraRigAsset* LoadedAsset = CameraRigAsset.LoadSynchronous();
        if (LoadedAsset)
        {
            CameraRigComponent->SetCameraRig(LoadedAsset);
        }
    }
}

void AMyCameraController::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 示例：在 Tick 中通过组件接口设置参数值
    // 具体方法名和参数获取方式需根据实际 API 调整
    // 假设有一个设置 FOV 参数的方法：
    // CameraRigComponent->SetBlendableParameter(TEXT("FOV"), TargetFieldOfView);
}
```

**说明**：此示例仅展示结构和可能的交互模式。`UCameraRigComponent` 和参数设置的具体 API 需要查阅插件的头文件或文档（如存在）。

## 模块依赖

从插件模块和常见用法推断，使用此插件可能需要以下依赖：

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 插件显式依赖，用于高级输入绑定 |
| `GameplayTags` | 很可能用于标记摄像机状态或事件 |
| `PropertyEditor`, `GraphEditor` | `GameplayCamerasEditor` 模块依赖，用于自定义属性和图表编辑 |
| `BlueprintGraph` | `GameplayCamerasUncookedOnly` 模块依赖，用于自定义蓝图节点（K2Node） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复了摄像机变量覆盖在编辑器内预览（PIE）中不生效的问题。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下 double 常量截断为 float 产生的编译警告。 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 为一些追踪通道添加或更新了描述信息，属于文档和注释改进。 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | 通用的摄像机系统更新，具体细节未在消息中说明。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移到新的 UE_LOGF 格式，属于代码现代化和维护。 |

### 维护评价

*   **年龄与状态**：该插件创建于 2020 年，已有约 5 年历史。虽然标记为**实验性**，但从最近的 Git 提交（2026 年 5 月）来看，**仍在积极维护**。
*   **更新频率**：在 2026 年 4 月至 5 月间有多次提交，包括功能修复、编译警告修复和代码维护，表明团队在持续改进。
*   **已知限制**：`.uplugin` 中明确标记 `IsExperimentalVersion: true`，这意味着它可能缺乏完整的功能集、文档，并且 API 可能在未来版本中发生不兼容的变化。用户需要承担使用风险。
*   **推荐度**：尽管是实验性的，但作为 Epic Games 官方推出的现代化摄像机系统，对于有复杂摄像机需求且愿意接受潜在不稳定性的项目来说，它是**值得尝试和关注的**。它代表了引擎摄像机系统的未来方向。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [官方文档]() (暂无)
- [测试用例]() (暂未在提供的路径中发现标准测试文件)