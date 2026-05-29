# XR Visualization

> Visualization Library for XR HMDs and controllers（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | XR设备可视化 |
| 分类 | Mixed Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `XRVisualization` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/XR/XRVisualization) | |

## 用途

该插件为 Unreal Engine 提供一套用于在非原生 XR 设备上**可视化**头戴显示器（HMD）和运动控制器状态的工具。它主要解决 XR 开发和调试过程中的一个常见问题：开发者并非总是在拥有完整 XR 硬件的环境下工作，但需要测试或演示与 XR 设备交互相关的逻辑（如位置追踪、手柄状态）。此插件通过渲染预制的网格模型（如 Oculus、HTC Vive 控制器），在普通桌面端模拟出 XR 设备的空间存在，使得开发、调试和演示无需真实硬件即可进行。

## 使用场景

- **XR 逻辑开发与调试**：开发者在编辑器或没有连接 XR 头显的电脑上，调试与 HMD 或手柄输入相关的游戏逻辑。
- **创建 XR 体验原型**：在项目早期，无需搭建完整硬件环境，即可向团队或客户展示基本的交互概念。
- **自动化测试**：在持续集成（CI）流水线中，对依赖 XR 输入的逻辑进行自动化可视化验证。

## 蓝图用法

该插件主要通过蓝图函数库 `UXRVisualizationFunctionLibrary` 暴露功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Render HMD` | 根据提供的 XR 头显数据，在场景中渲染一个可视化的头显模型。 | `UXRVisualizationFunctionLibrary` |
| `Render Motion Controller 2` | 根据提供的运动控制器状态数据，在场景中渲染一个可视化的手柄模型（支持 Oculus、Vive 等）。 | `UXRVisualizationFunctionLibrary` |
| `Render Hand Tracking` | 根据提供的手部追踪状态数据，在场景中渲染可视化的手指模型。 | `UXRVisualizationFunctionLibrary` |

### 使用示例（蓝图描述）

1.  在一个Actor的蓝图中，通过 `Get XRHMD Data` 或 `Get Motion Controller Data` 等节点获取 `FXRHMDData` 或 `FXRMotionControllerState` 结构体。
2.  将这些数据传递给 `Render HMD` 或 `Render Motion Controller 2` 节点。这些节点会自动在场景中创建和更新对应的静态网格体Actor，模拟设备的位置和旋转。
3.  你可以将这些节点放在 `Event Tick` 中以实现持续更新，或仅在需要时调用以进行状态快照。

## C++ 用法

### 头文件引入

```cpp
#include "XRVisualizationFunctionLibrary.h"
```

### 基本用法

```cpp
// 假设你已经获得了 XR 设备的数据
FXRHMDData HMDData;
FXRMotionControllerState ControllerData;

// 填充 HMDData 和 ControllerData...
// 例如，可以手动设置一个位置用于测试
HMDData.DeviceName = TEXT("Test HMD");
HMDData.Position = FVector(100.0f, 0.0f, 100.0f);
HMDData.Rotation = FRotator(0.0f, 0.0f, 0.0f);

// 在场景中渲染可视化
UXRVisualizationFunctionLibrary::RenderHMD(HMDData);
UXRVisualizationFunctionLibrary::RenderMotionController2(ControllerData);
```

### 进阶用法

可以结合定时器或 Tick 事件来持续更新可视化设备的位置，模拟真实的追踪。
```cpp
// 在 Actor 的 Tick 函数中
void AMyXRDebugActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 模拟一个不断移动的 HMD
    CurrentHMDData.Position.X += DeltaTime * 100.0f;
    UXRVisualizationFunctionLibrary::RenderHMD(CurrentHMDData);
}
```

## Demo 示例

以下是一个简单的 Actor，它在游戏开始时渲染一个 HMD 和一个控制器。

```cpp
// MyXRDebugActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "XRVisualizationFunctionLibrary.h" // 需要包含插件头文件
#include "MyXRDebugActor.generated.h"

UCLASS()
class AMyXRDebugActor : public AActor
{
    GENERATED_BODY()

public:
    AMyXRDebugActor();

protected:
    virtual void BeginPlay() override;

private:
    FXRHMDData TestHMDData;
    FXRMotionControllerState TestControllerData;
};
```

```cpp
// MyXRDebugActor.cpp
#include "MyXRDebugActor.h"

AMyXRDebugActor::AMyXRDebugActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyXRDebugActor::BeginPlay()
{
    Super::BeginPlay();

    // 准备测试数据
    TestHMDData.DeviceName = TEXT("Debug HMD");
    TestHMDData.Position = FVector(0.0f, 0.0f, 170.0f); // 假设玩家身高
    TestHMDData.Rotation = FRotator::ZeroRotator;

    TestControllerData.DeviceName = TEXT("Debug Controller");
    TestControllerData.Hand = EControllerHand::Right;
    TestControllerData.GripPosition = FVector(50.0f, 20.0f, 120.0f);
    TestControllerData.GripRotation = FRotator(-30.0f, 0.0f, 0.0f);

    // 调用可视化函数库进行渲染
    UXRVisualizationFunctionLibrary::RenderHMD(TestHMDData);
    UXRVisualizationFunctionLibrary::RenderMotionController2(TestControllerData);
}
```

## 模块依赖

从插件描述和源码分析，该插件依赖于以下特定模块：

| 模块 | 用途 |
|---|---|
| `XRBase` | 提供 XR 子系统的基础类和数据结构，是本插件的基础。 |
| `ProceduralMeshComponent` | 用于在运行时动态创建网格（特别是手部追踪），以渲染手指等复杂形状。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化字符串在不同位宽下的兼容性问题，确保日志准确。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏更新为新的 `UE_LOGF` 格式，跟随引擎日志系统改进。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件重命名为标准的 `Default` 前缀，符合新规范。 |
| 2025-07-22 | `c10efd7e` | Fixed GetHMDData TrackingStatus field. | 修复了获取 HMD 数据时 `TrackingStatus` 字段可能返回错误值的问题。 |
| 2025-05-21 | `269aeb1b` | Replaced bool arguments with EFindObjectFlags. | 在内部查找对象时，将布尔参数替换为更安全的 `EFindObjectFlags` 枚举。 |

### 维护评价

- **年龄与实验性**：插件创建于约 6 年前，且 `.uplugin` 中 `IsBetaVersion = true`，属于实验性功能。
- **更新频率**：最近一年内有多次更新，但主要是代码格式修复、日志系统迁移和小 bug 修复（如 `GetHMDData` 修复），**无重大新功能添加**。
- **活跃度**：处于**低频维护状态**，基本只保证其能在最新引擎版本中编译运行，没有活跃的功能开发。
- **建议**：可以用于**开发调试和原型展示**。由于它是实验性的且功能基础，不建议在需要高度可靠或复杂 XR 可视化的正式项目中作为核心依赖。使用时需关注其与最新引擎版本的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/XR/XRVisualization)