# RigLogic Plugin v10.3.0

> RigLogic Plugin for Facial Animation v10.3.0

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、动画节点） |
| 模块 | `RigLogicLib` (CPlusPlus), `RigLogicModule` (Runtime), `RigLogicEditor` (Runtime), `RigLogicDeveloper` (Runtime), `RigLogicLibTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-07-20 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic) | |

## 用途

RigLogic 是一个高性能、数据驱动的面部动画系统，专为创建逼真的数字人类和复杂的面部表情而设计。它并非简单的骨骼动画，而是基于一种名为 “Rig Logic” 的专利技术，能够通过解算一组称为 “LODs” (Levels of Detail) 的控制参数，来驱动一个复杂的、基于肌肉和骨骼的面部绑定。该插件的核心价值在于：

1.  **高保真面部动画**：能够模拟真实的面部肌肉运动、皮肤褶皱和次级运动，产生电影级的动画效果。
2.  **数据驱动与高效**：动画数据（如来自面部捕捉）被压缩并存储为高效的 “Rig Logic” 格式。运行时，系统通过解算这些数据来驱动面部网格，性能极高。
3.  **与 UE5 深度集成**：提供完整的动画蓝图节点、编辑器工具和运行时组件，无缝融入 Unreal Engine 的动画工作流。

简而言之，当你的项目需要制作具有复杂、逼真面部动画的数字人类角色时，RigLogic 是 Epic Games 提供的官方解决方案。

## 使用场景

-   **数字人类项目**：制作电影、过场动画或高质量实时渲染中的数字人角色。
-   **高级角色定制**：为玩家角色或 NPC 提供丰富、细腻的面部表情系统。
-   **实时面部动画**：结合面部捕捉数据，在游戏运行时驱动角色面部。
-   **电影级动画制作**：在 Sequencer 中制作需要极高面部细节的动画序列。

## 蓝图用法

RigLogic 主要通过动画蓝图节点进行操作。其核心是 `UAnimGraphNode_RigLogic`，它在动画蓝图编辑器中提供了一个可视化的节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Rig Logic` | 动画蓝图中的核心节点，用于驱动基于 RigLogic 的面部动画。 | `UAnimGraphNode_RigLogic` |

### 使用示例（蓝图描述）

1.  **在动画蓝图中使用**：
    *   打开你的角色的动画蓝图。
    *   在动画图表中，右键搜索并添加 “Rig Logic” 节点。
    *   将该节点的输出姿势连接到最终的动画输出节点。
    *   在节点的细节面板中，配置其属性，例如指定要驱动的骨骼网格体组件。
2.  **数据输入**：通常，你需要将面部捕捉数据或自定义的控制曲线（例如，通过 `Animation Curve` 节点）连接到 RigLogic 节点的输入，以驱动面部表情。

## C++ 用法

RigLogic 的 C++ 接口主要面向需要深度集成或自定义行为的开发者。其核心运行时逻辑封装在 `RigLogicModule` 和 `RigLogicLib` 中。

### 头文件引入

```cpp
#include “RigLogicModule.h”
#include “AnimNode_RigLogic.h” // 用于动画节点
```

### 基本用法

以下示例展示了如何在 C++ 中访问和配置一个 RigLogic 动画节点。这通常在自定义的动画实例或组件中完成。

```cpp
// 假设你有一个指向 UAnimInstance 的指针 AnimInstance
// 以及一个 FAnimNode_RigLogic 节点的引用 (通常在动画蓝图中已存在)

// 获取 RigLogic 模块实例
IRigLogicModule& RigLogicModule = FModuleManager::GetModuleChecked<IRigLogicModule>(“RigLogicModule”);

// RigLogic 的核心功能通常通过动画蓝图节点暴露。
// 在 C++ 中，你更可能与 FAnimNode_RigLogic 结构体交互。
// 例如，你可以在动画实例的 NativeUpdateAnimation 中访问它。
void UMyAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);

    // 获取动画蓝图中的节点 (假设你有一个名为 RigLogicNode 的成员变量)
    // FAnimNode_RigLogic* RigLogicNode = GetNode<FAnimNode_RigLogic>(...);
    // if (RigLogicNode)
    // {
    //     // 在这里可以访问或修改节点的属性
    //     // RigLogicNode->SomeProperty = Value;
    // }
}
```

### 进阶用法

RigLogic 的强大之处在于其数据驱动的特性。进阶用法通常涉及处理其专有的数据格式（`.rl` 文件）或与外部面部捕捉系统集成。这通常需要直接使用 `RigLogicLib` 提供的底层 API。

```cpp
// 伪代码示例：加载和使用 RigLogic 数据
#include “RigLogicLib.h”

// 假设你有一个 .rl 文件的路径
FString RigLogicDataPath = TEXT(“/Game/Characters/DigitalHuman/FaceData.rl”);

// 使用 RigLogicLib 的 API 加载数据
// RigLogicLib::FRigLogicData* LoadedData = RigLogicLib::LoadDataFromFile(*RigLogicDataPath);

// 然后，你可以将这些数据传递给动画节点或用于自定义的动画逻辑。
// 具体的 API 调用需要参考 RigLogicLib 的详细文档或头文件。
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建一个自定义的动画实例，该实例可以访问和操作 RigLogic 节点。

**MyRigLogicAnimInstance.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “Animation/AnimInstance.h”
#include “AnimNode_RigLogic.h”
#include “MyRigLogicAnimInstance.generated.h”

UCLASS()
class UMyRigLogicAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    // 用于在蓝图或编辑器中指定要查找的 RigLogic 节点名称
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = “RigLogic”)
    FName RigLogicNodeName = TEXT(“RigLogicNode”);

    // 一个示例属性，用于驱动面部表情强度
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = “RigLogic”)
    float ExpressionIntensity = 0.0f;

protected:
    virtual void NativeInitializeAnimation() override;
    virtual void NativeUpdateAnimation(float DeltaSeconds) override;

private:
    // 缓存找到的 RigLogic 节点指针
    FAnimNode_RigLogic* CachedRigLogicNode = nullptr;
};
```

**MyRigLogicAnimInstance.cpp**
```cpp
#include “MyRigLogicAnimInstance.h”
#include “Animation/AnimNode_StateMachine.h”

void UMyRigLogicAnimInstance::NativeInitializeAnimation()
{
    Super::NativeInitializeAnimation();

    // 在动画实例初始化时，尝试查找并缓存 RigLogic 节点
    // 注意：这需要动画蓝图中确实存在一个名为 RigLogicNodeName 的节点
    // 实际的查找逻辑可能更复杂，取决于你的动画蓝图结构
    // CachedRigLogicNode = FindAnimNode<FAnimNode_RigLogic>(RigLogicNodeName);
}

void UMyRigLogicAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);

    if (CachedRigLogicNode)
    {
        // 在这里，你可以根据游戏逻辑修改节点的属性
        // 例如，将 ExpressionIntensity 传递给节点的某个输入参数
        // CachedRigLogicNode->SetSomeInputParameter(ExpressionIntensity);
    }
}
```

## 模块依赖

要使用 RigLogic 插件，你的项目模块通常不需要直接依赖它，因为其功能主要通过动画蓝图节点暴露。但如果你需要在 C++ 中深度集成，可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `RigLogicModule` | RigLogic 的主要运行时模块，提供核心功能和动画节点。 |
| `RigLogicLib` | RigLogic 的底层 C++ 库，处理数据加载和解算。 |
| `SkeletalMeshUtilitiesCommon` | 用于骨骼网格体相关的通用工具函数。 |
| `RHI` | 渲染硬件接口，可能用于某些高级渲染或计算着色器相关的功能。 |
| `RenderCore` | 渲染核心模块。 |

## 维护状态

### 近期更新

```
- 2024-05-17 2057280165b3 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 1/n
- 2024-05-17 da92084a122a Optimized out more private modules includes and dependencies.
- 2024-05-17 91c57d395e6b Removed redundant module includes.
```

### 维护评价

RigLogic 插件创建于 2020 年，是一个相对成熟的系统。从最近的提交记录来看，近期的更新主要集中在**代码清理、依赖优化和编译兼容性修复**上（例如调整头文件以确保 DLL 导出正确），而非新功能的添加。这表明该插件已进入一个**稳定维护期**。

-   **优点**：作为 Epic Games 官方维护的数字人类技术栈核心组件，其稳定性和与引擎的兼容性有保障。代码质量高，架构清晰。
-   **现状**：最近一次实质性功能更新可能已在较早的版本中完成。当前维护重点是确保其在新版引擎（如 5.6, 5.7）中能顺利编译和运行。
-   **建议**：对于需要高质量面部动画的项目，**强烈推荐使用**。它是一个经过验证的、生产就绪的解决方案。但请注意，其学习曲线可能较陡，需要理解其数据驱动的工作流。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/RigLogic) (如果存在)