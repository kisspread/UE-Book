# Chaos Visual Debugger

> Enables support for Visual debugging of Chaos Physics simulations

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、独立程序） |
| 模块 | `ChaosVD` (EditorAndProgram), `ChaosVDBlueprint` (RuntimeAndProgram), `ChaosVDBuiltInExtensions` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-03-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosVD) | |

## 用途

Chaos Visual Debugger (CVD) 是一个用于 **记录、回放和可视化分析** Chaos 物理模拟数据的强大工具。它解决了物理调试中“黑盒”的问题，允许开发者在模拟运行时或事后，以可视化的方式检查物理世界的内部状态，包括碰撞几何体、约束、轨迹、力场等。其核心价值在于将瞬时的、复杂的物理交互过程转化为可暂停、可逐帧分析的“录像”，极大地提升了定位和解决物理相关问题的效率。

## 使用场景

-   **调试物理模拟问题**：当物体出现异常穿透、抖动或不符合预期的运动时，使用 CVD 录制模拟过程，然后逐帧回放，检查碰撞检测、接触点和约束的实时状态。
-   **分析碰撞事件**：可视化查看碰撞对（Collision Pairs）、接触法线、冲击点，理解复杂的多体碰撞是如何发生的。
-   **优化物理性能**：通过回放查看物理场景的复杂度，识别不必要的碰撞检测或过于复杂的几何体，为性能优化提供依据。
-   **教学与演示**：录制物理模拟过程，用于内部培训或向团队成员展示物理系统的工作原理。
-   **独立分析程序**：CVD 支持生成独立的 `ChaosVisualDebugger` 程序，可以在没有完整编辑器的情况下加载和分析录制的 `.cvd` 文件。

## 蓝图用法

`ChaosVDBlueprint` 模块提供了在运行时（包括打包后的游戏）向 CVD 录制中添加自定义调试信息的蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CVD Record Debug Draw Box` | 在指定世界位置录制一个调试用的盒体形状。 | `UChaosVDRuntimeBlueprintLibrary` |
| `CVD Record Debug Draw Line` | 录制一条从起点到终点的调试线段。 | `UChaosVDRuntimeBlueprintLibrary` |
| `CVD Record Debug Draw Vector` | 录制一个从起点出发、具有方向和长度的调试向量。 | `UChaosVDRuntimeBlueprintLibrary` |
| `CVD Record Debug Draw Sphere` | 在指定中心点录制一个调试用的球体。 | `UChaosVDRuntimeBlueprintLibrary` |
| `CVD Set Trace Relevancy Volume` | 设置一个空间体积（盒体），CVD 将只录制此体积内的物理数据，用于过滤无关信息。 | `UChaosVDRuntimeBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **录制自定义调试形状**：在你的角色蓝图或任何 Actor 的事件图表中，当某个物理事件发生时（例如 `OnComponentHit`），调用 `CVD Record Debug Draw Sphere` 节点。将 `World Context` 引脚连接到 `Self`，`In Center` 设置为碰撞点位置，`Radius` 设置一个合适的值，`Color` 设置为醒目的颜色（如红色）。这样，在回放 CVD 录制时，你就能在碰撞点看到这个红色球体。
2.  **设置数据过滤区域**：在游戏开始或关卡加载时，调用 `CVD Set Trace Relevancy Volume`。将 `Relevancy Volume` 设置为一个覆盖你主要游戏区域（如竞技场）的盒体。这可以显著减小录制文件的大小，并让回放时的视图更聚焦。

## C++ 用法

### 头文件引入

```cpp
#include “ChaosVDRuntimeBlueprintLibrary.h”
```

### 基本用法

以下代码展示了如何在 C++ 中调用蓝图库函数来记录调试数据。这些函数通常用于在关键的物理逻辑点插入调试信息。

```cpp
// 假设在一个 Actor 的某个函数中
void AMyPhysicsActor::OnCollisionDetected(const FHitResult& Hit)
{
    // 记录一个在碰撞点的红色球体
    UChaosVDRuntimeBlueprintLibrary::RecordDebugDrawSphere(
        this, // WorldContext
        Hit.ImpactPoint,
        25.0f, // Radius
        FName(“CollisionPoint”),
        FLinearColor::Red
    );

    // 记录碰撞法线向量
    UChaosVDRuntimeBlueprintLibrary::RecordDebugDrawVector(
        this,
        Hit.ImpactPoint,
        Hit.ImpactNormal * 100.0f, // 将法线放大以便观察
        FName(“ImpactNormal”),
        FLinearColor::Green
    );
}
```
*（代码示例基于 `ChaosVDRuntimeBlueprintLibrary.h` 中的函数签名）*

### 进阶用法

CVD 的核心功能（录制、回放、UI）主要由 `ChaosVD` 编辑器模块提供。在 C++ 中，你更可能与 `ChaosVD` 模块的类交互来扩展其功能或集成到自定义工具中。例如，你可以：
-   创建自定义的 `IChaosVDDataProcessor` 来处理和可视化特定类型的物理数据。
-   使用 `ChaosVDScene` 和 `ChaosVDPlaybackController` 来编程控制回放过程。
-   通过 `ChaosVDRecordingPolicy` 来定义更复杂的录制规则。

## Demo 示例

一个最小的 C++ 示例，展示如何在游戏逻辑中集成 CVD 调试绘制。

```cpp
// MyDebugHelper.h
#pragma once
#include “CoreMinimal.h”
#include “Kismet/BlueprintFunctionLibrary.h”
#include “MyDebugHelper.generated.h”

UCLASS()
class UMyDebugHelper : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    // 一个简单的函数，用于在指定位置绘制调试盒体并记录到 CVD
    UFUNCTION(BlueprintCallable, Category = “Debug”)
    static void DrawDebugBoxWithCVD(const UObject* WorldContext, const FVector& Center, const FVector& Extent, const FLinearColor& Color);
};

// MyDebugHelper.cpp
#include “MyDebugHelper.h”
#include “ChaosVDRuntimeBlueprintLibrary.h”
#include “DrawDebugHelpers.h”

void UMyDebugHelper::DrawDebugBoxWithCVD(const UObject* WorldContext, const FVector& Center, const FVector& Extent, const FLinearColor& Color)
{
    // 1. 在视口中绘制常规的调试盒体（仅开发版本可见）
    DrawDebugBox(WorldContext->GetWorld(), Center, Extent, FQuat::Identity, Color.ToFColor(true), false, -1.0f, 0, 2.0f);

    // 2. 同时将这个盒体记录到 CVD 录制中（打包后也可用）
    UChaosVDRuntimeBlueprintLibrary::RecordDebugDrawBox(
        WorldContext,
        FBox(Center - Extent, Center + Extent),
        FName(“DebugBox”),
        Color
    );
}
```

## 模块依赖

要使用 `ChaosVDBlueprint` 模块提供的运行时蓝图功能，你的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `ChaosVDBlueprint` | 提供 `UChaosVDRuntimeBlueprintLibrary` 等运行时蓝图函数。 |
| `Chaos` | Chaos 物理引擎核心模块，CVD 的数据源。 |

*（注：`ChaosVD` 和 `ChaosVDBuiltInExtensions` 是编辑器/程序模块，通常不需要在游戏运行时模块中直接依赖。）*

## 维护状态

### 近期更新

```
- 655af1bde991 [ChaosVD] Adding a way to only trace CVD data that is within a specific area instead of the entire world.
- a2e75189887d Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup using LyraEditor win64 development as target)
- 6ae573356bbf Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
```

### 维护评价

-   **活跃维护**：插件创建于 2023 年 3 月，属于较新的工具。从提供的有限 git 历史看，近期仍有功能性更新（如添加空间过滤功能）和代码质量改进。
-   **实验性状态**：`.uplugin` 中 `IsBetaVersion` 为 `true`，表明该插件仍处于测试阶段，API 和功能可能在未来版本中发生变化。
-   **推荐使用**：**推荐在开发和调试阶段使用**。对于需要深度调试 Chaos 物理模拟的项目，CVD 是一个非常有价值的工具。但由于其 Beta 状态，不建议在最终发布的、对稳定性要求极高的产品中依赖其运行时蓝图功能进行核心逻辑判断。主要用于开发期的调试和分析。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosVD)
-   [官方文档]() （暂无）
-   [测试用例]() （暂未在提供的信息中发现）