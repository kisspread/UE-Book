# XRVisualization

> Visualization Library for XR HMDs and controllers

| 属性 | 值 |
|---|---|
| 分类 | Mixed Reality |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | XRVisualization (Runtime) |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/XR/XRVisualization) | |

## 用途

XRVisualization 是一个运行时调试工具，用于在**没有真实 XR 硬件**的系统上可视化 HMD 头显和手柄控制器的位置与旋转。它通过在场景中动态生成 3D 网格（StaticMesh 或 ProceduralMesh）来渲染 XR 设备的虚拟表示，使得开发者可以在普通桌面环境中调试 XR 追踪数据。

该 plugin 的核心思路是：从 `FXRHMDData`、`FXRMotionControllerState`、`FXRHandTrackingState` 等结构体中读取追踪数据，在场景中创建临时 Actor 并放置对应的 3D 模型，2 秒后自动销毁。这样在没有连接 VR 头显时也能看到追踪数据的空间位置。

> **注意**：此 plugin 标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，需要手动启用。

## 使用场景

- 你在开发 XR 应用但没有连接 VR 头显，需要在编辑器中调试追踪数据的位置和旋转
- 你正在测试自定义 XR 输入设备驱动，需要直观看到 HMD 和控制器的渲染效果
- 你在做一个需要手部追踪的 XR 应用，需要可视化手指关键点的连线

## 蓝图用法

该 plugin 暴露了 3 个 `BlueprintCallable` 函数，均位于 `Input|XRTracking` 分类下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RenderHMD` | 根据 HMD 追踪数据，在场景中渲染一个 HMD 头显模型 | `UXRVisualizationFunctionLibrary` |
| `RenderMotionController2` | 根据运动控制器数据，渲染对应设备的手柄模型（Oculus/Vive/STEM 自动匹配） | `UXRVisualizationFunctionLibrary` |
| `RenderHandTracking` | 根据手部追踪数据渲染手部网格（优先使用 IHandTracker 提供的网格数据，降级为 Debug 线条） | `UXRVisualizationFunctionLibrary` |

### 使用示例（蓝图描述）

1. 在你的 XR 追踪 Tick 事件中，使用 `GetXRHMDData` 节点获取 HMD 数据
2. 将其连接到 `RenderHMD` 节点，即可在场景中看到 HMD 的虚拟模型
3. 对于控制器，使用 `GetMotionControllerData` 获取状态后连接到 `RenderMotionController2`
4. 手部追踪同理，使用 `GetHandTrackingData` 后连接到 `RenderHandTracking`

## C++ 用法

### 头文件引入

```cpp
#include "XRVisualizationFunctionLibrary.h"
```

### 基本用法

所有函数都是静态的，可直接调用：

```cpp
// 渲染 HMD 头显模型
FXRHMDData HMDData;
HMDData.DeviceName = TEXT("TestHMD");
HMDData.Position = FVector(0, 0, 200);
HMDData.Rotation = FRotator::ZeroRotator;
UXRVisualizationFunctionLibrary::RenderHMD(HMDData);

// 渲染运动控制器（自动根据 DeviceName 选择 Oculus/Vive/STEM 模型）
FXRMotionControllerState ControllerState;
ControllerState.bValid = true;
ControllerState.Hand = EControllerHand::Right;
ControllerState.DeviceName = TEXT("OculusHMD");
ControllerState.GripUnrealSpaceLocation = FVector(100, 0, 150);
ControllerState.GripUnrealSpaceRotation = FRotator::ZeroRotator;
UXRVisualizationFunctionLibrary::RenderMotionController2(ControllerState);
```

> 来源：`Source/XRVisualization/Private/XRVisualizationFunctionLibrary.cpp`

### 进阶用法

手部追踪的渲染逻辑有两种路径：

1. **IHandTracker 路径**：如果存在可用的 `IHandTracker` 实现且提供网格数据，会使用 `ProceduralMeshComponent` 渲染真实的手部网格
2. **降级路径**：如果无 HandTracker 或无网格数据，使用 `DrawDebugLine` 和 `DrawDebugSphere` 绘制手指骨骼线框

控制器模型自动匹配规则（源码中硬编码）：
- `DeviceName == "OculusHMD"` → Oculus 控制器模型
- `DeviceName == "SteamVR"` → Vive 控制器模型
- 其他 → STEM 控制器模型

所有渲染的 Actor 会在 **2 秒后自动销毁**，因此需要在 Tick 中持续调用。

### 手部网格材质配置

可通过 Game.ini 配置手部网格的材质：

```ini
[/Script/EngineSettings.XRVisualizationSettings]
HandMeshMaterial=/Game/Materials/HandMeshMaterial
```

## Demo 示例

最小使用示例——在 Tick 中渲染 HMD：

```cpp
// MyXRDebugActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyXRDebugActor.generated.h"

UCLASS()
class AMyXRDebugActor : public AActor
{
    GENERATED_BODY()
public:
    AMyXRDebugActor();
    virtual void Tick(float DeltaTime) override;
};
```

```cpp
// MyXRDebugActor.cpp
#include "MyXRDebugActor.h"
#include "XRVisualizationFunctionLibrary.h"
#include "HeadMountedDisplayTypes.h"

AMyXRDebugActor::AMyXRDebugActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyXRDebugActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    FXRHMDData HMDData;
    HMDData.DeviceName = TEXT("DebugHMD");
    HMDData.Position = GetActorLocation();
    HMDData.Rotation = GetActorRotation();
    UXRVisualizationFunctionLibrary::RenderHMD(HMDData);
}
```

**Build.cs 依赖**：此 plugin 不暴露 PublicDependency，使用者无需额外依赖——只需启用 plugin 即可。所有 API 通过 `UXRVisualizationFunctionLibrary` 静态方法调用。

## 模块依赖

该 plugin 自身依赖以下模块（使用者无需关心，仅供理解内部实现）：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | Actor/Component 系统 |
| `EngineSettings` | XR 可视化配置读取 |
| `RenderCore` / `RHI` | 渲染支持 |
| `HeadMountedDisplay` | XR 数据类型定义（FXRHMDData 等） |
| `XRBase` | XR 基础设施 |
| `ProceduralMeshComponent` | 手部追踪网格渲染 |

**Plugin 依赖**（.uplugin 中声明）：
- `XRBase`
- `ProceduralMeshComponent`

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-22 | `c10efd7e` | Fixed GetHMDData TrackingStatus field; Removed deprecated GetMotionControllerData and FXRMotionControllerData (deprecated in 5.5) | 修复 HMD 追踪状态判断逻辑，清理 5.5 已废弃的 API |
| 2025-05-21 | `269aeb1b` | Replaced bool arguments with EFindObjectFlags | 代码质量改进，用枚举替代 bool 参数 |
| 2024-11-22 | `36771d79` | Updated uplugin descriptor flags | 标记从 Experimental 改为 Beta |

### 维护评价

- **年龄**：约 5.6 年（2020-09 创建）
- **状态**：**Beta**（IsBetaVersion=true），从未正式 GA
- **更新频率**：最近一年有 2 次实质更新（2025-05、2025-07），说明仍在维护
- **限制**：
  - 始终标记为 `EnabledByDefault=false`，需要手动启用
  - 控制器模型硬编码了 Oculus/Vive/STEM 三种，不支持其他设备的模型
  - 渲染使用临时 Actor + 2 秒定时销毁的模式，性能开销较大
  - 没有官方文档（DocsURL 为空）
- **推荐**：适合调试和开发阶段使用，不建议在生产代码中依赖此 plugin

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/XR/XRVisualization)
- 官方文档：无（DocsURL 为空）
