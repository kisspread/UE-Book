# OpenXRViveTracker

> OpenXR Vive Tracker provides XR_HTCX_vive_tracker_interaction.

| 属性 | 值 |
|---|---|
| 中文名 | Vive追踪器扩展 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（插件依赖声明） |
| 模块 | `OpenXRViveTracker` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-11-03 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXRViveTracker) | |

## 用途

该插件为 OpenXR 运行时提供了对 HTC Vive Tracker 设备的扩展支持。它实现了 `XR_HTCX_vive_tracker_interaction` 扩展，允许 Unreal Engine 5 通过 OpenXR 标准接口访问 Vive Tracker 的位置、旋转和触觉反馈数据。这解决了标准 OpenXR 配置中 Vive Tracker 可能无法被识别或交互的问题，是实现全身追踪、大型空间追踪或追踪多个物理对象等高级 VR 功能的关键组件。

## 使用场景

- **全身追踪（Full Body Tracking）**：你需要使用多个 Vive Tracker 绑定在用户身体的关键部位（如手肘、膝盖、脚部），以实现更自然的虚拟化身动画。
- **大型空间与物体追踪**：你在为线下 VR 体验、主题公园或工业模拟构建应用，需要精确追踪大型空间内的物体或道具位置。
- **多设备交互**：你希望用脚部控制器、专属枪械模型等外设与 VR 环境交互，这些外设使用了 Vive Tracker。

## 蓝图用法

此插件主要通过标准的 Motion Controller 接口和 OpenXR 扩展机制工作，没有直接暴露给蓝图的独特节点。其功能通过 Unreal Engine 内置的 `MotionController` 组件和相关蓝图节点来访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Motion Controller Position and Rotation` | 获取指定 Motion Source 的追踪数据。当 `MotionSource` 参数设置为 Vive Tracker 识别的特定名称时，数据将来自该插件。 | `UInputComponent` |
| `Set Haptic Feedback` | 对指定的控制器发送触觉/振动反馈。对于支持振动的 Vive Tracker（如 Tracker (2018) 或更新版本），可通过此节点触发。 | `AHapticFeedbackEffect_Base` |

### 使用示例（蓝图描述）

1.  **创建一个 Actor 并添加 `MotionController` 组件**。
2.  在 `MotionController` 组件的详情面板中，将 `Motion Source` 属性设置为插件注册的特定源名称。这些名称通常在 OpenXR 扩展中定义，可能包括类似 `ViveTrackerHTCX/role/vive_tracker_handed/left` 或 `ViveTrackerHTCX/role/vive_tracker_handed/right` 等（具体名称需参考 HTC 的 OpenXR 扩展文档和插件运行时注册信息）。
3.  在 Tick 事件中，使用 `Get Motion Controller Position and Rotation` 节点，输入相应的 `Motion Source` 名称，即可获得该 Tracker 的世界位置和旋转。
4.  要触发振动，可以使用 `Set Haptic Feedback` 节点，指定对应的控制器和振动模式。

## C++ 用法

该插件的核心功能通过 OpenXR 扩展和输入设备系统集成，C++ 用法侧重于检查模块状态和底层扩展交互。

### 头文件引入

```cpp
#include "IOpenXRViveTrackerModule.h"
```

### 基本用法

从模块接口获取信息并检查其可用性。

```cpp
// 来源：IOpenXRViveTrackerModule.h
// 检查 OpenXR Vive Tracker 模块是否可用
if (IOpenXRViveTrackerModule::IsAvailable())
{
    // 获取模块引用（如果模块已加载）
    IOpenXRViveTrackerModule& ViveTrackerModule = IOpenXRViveTrackerModule::Get();
    
    // 获取与该模块关联的输入设备指针（通常用于内部或高级操作）
    TSharedPtr<IInputDevice> InputDevice = ViveTrackerModule.GetInputDevice();
}
```

### 进阶用法

由于 `FOpenXRViveTracker` 类是私有实现，通常不需要直接操作。其功能通过 Unreal 的 `IMotionController` 接口（由 `FXRMotionControllerBase` 实现）和标准 `IInputDevice` 接口与引擎的其他部分交互。开发者主要通过蓝图或 C++ 中标准的 MotionController 接口来使用由插件提供数据的追踪功能。

## Demo 示例

```cpp
// MyViveTrackerActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyViveTrackerActor.generated.h"

UCLASS()
class AMyViveTrackerActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyViveTrackerActor();
    virtual void Tick(float DeltaTime) override;

protected:
    virtual void BeginPlay() override;

private:
    void CheckViveTrackerSupport();

    // 存储通过 MotionController 组件或接口获取的 Tracker 位置
    FVector TrackerPosition;
    FRotator TrackerRotation;
};
```

```cpp
// MyViveTrackerActor.cpp
#include "MyViveTrackerActor.h"
#include "IOpenXRViveTrackerModule.h"

AMyViveTrackerActor::AMyViveTrackerActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyViveTrackerActor::BeginPlay()
{
    Super::BeginPlay();
    CheckViveTrackerSupport();
}

void AMyViveTrackerActor::CheckViveTrackerSupport()
{
    // 在运行时检查 Vive Tracker 支持是否可用
    if (IOpenXRViveTrackerModule::IsAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("OpenXRViveTracker 模块已加载。Vive Tracker 支持可用。"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("OpenXRViveTracker 模块不可用。请确保插件已启用且 OpenXR 运行时支持 HTC 扩展。"));
    }
}

void AMyViveTrackerActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    // 注意：实际获取 Tracker 数据通常通过 MotionController 组件完成。
    // 此处仅为演示模块可用性检查。
    // 例如，你可以在蓝图中创建一个 MotionController 组件，
    // 并在 C++ 中通过接口查询其数据，或者直接使用蓝图。
}
```

## 模块依赖

从 Build.cs 的依赖分析，该插件依赖编辑器功能，这可能与配置或开发工具相关。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 用于编辑器集成和配置支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-24 | `06731a03` | PR #13472: Crash fix with Vive trackers in viewport | 修复了在编辑器视口中使用 Vive Trackers 时发生的崩溃问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出宏从 UE_LOG 迁移到 UE_LOGF，是代码规范的一部分更新。 |
| 2026-02-09 | `0c8ae810` | OpenXR all platform cleanup. | 对 OpenXR 相关插件进行了跨平台代码清理。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复了微不足道的不可达代码警告，属于代码质量维护。 |
| 2025-01-28 | `22b72707` | FPlatformString and FCString: Deprecate Strcpy and Strcat that take a DestLen, because some platform | 跟随引擎平台字符串 API 的废弃更新，移除了对已废弃函数的使用。 |

### 维护评价

该插件创建于2022年底，目前仍在接受维护和更新。最近的提交记录（截至2026年）显示，维护重点包括**功能修复**（如修复视口崩溃）、**代码现代化**（迁移日志宏）和**跨平台兼容性清理**。虽然它标记为实验性（IsBetaVersion=true）且默认禁用，但持续的更新表明它仍在被支持和改进，特别是在修复用户遇到的实际问题（如崩溃）方面。考虑到其依赖的 OpenXR 生态和 Vive Tracker 市场仍在活跃，此插件是用于相关项目的一个**可考虑使用**的选项，但需注意其“实验性”状态可能意味着未来API或行为有变动的可能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXRViveTracker)
- [XR_HTCX_vive_tracker_interaction 扩展规范 (OpenXR Registry)](https://registry.khronos.org/OpenXR/specs/1.0/html/xrspec.html#XR_HTCX_vive_tracker_interaction)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXRViveTracker) (插件自身目录下未发现公开的独立测试用例文件)