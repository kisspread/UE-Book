# Lens Component

> Implements the Lens Component for adding distortion to a cinematic camera

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | Hidden / IsBetaVersion=true |
| 包含内容 | true |
| 模块 | LensComponent (Runtime), LensComponentEditor (Editor) |
| 创建时间 | 2023-12-21 |
| 年龄标签 | 🆕 (~2年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LensComponent) | |

## 用途

LensComponent 是从 `CameraCalibrationCore` plugin（UE 5.4）中拆分出来的独立模块，专门负责将**镜头畸变后处理效果**应用到 `CineCameraComponent` 上。

它的核心职责是作为一个「桥接组件」，连接三个系统：
1. **LensFile**（镜头标定数据资产）— 提供畸变参数、nodal offset、焦距校正等标定数据
2. **LiveLink** — 从物理摄影机实时接收 Focus/Iris/Zoom (FIZ) 数据和追踪数据
3. **Sequencer** — 支持在 Level Sequence 中录制和回放镜头畸变参数

简单来说：你在虚拟制片中用真实摄影机拍摄，这个组件让 UE 中的虚拟摄影机产生与真实镜头完全匹配的畸变效果。

## 使用场景

- **虚拟制片 (Virtual Production)**：你用真实摄影机通过 LiveLink 连接 UE，需要虚拟摄影机产生与真实镜头匹配的畸变效果
- **镜头标定回放**：你有一个 LensFile 资产记录了镜头在不同焦距/对焦距离下的畸变参数，需要在 Sequencer 中回放
- **Nodal Offset 校正**：需要补偿镜头光学中心偏移，使追踪旋转围绕正确的光学节点旋转
- **Filmback 覆盖**：需要根据镜头标定数据自动调整摄影机的传感器尺寸（Cropped Filmback）

## 蓝图用法

`ULensComponent` 继承自 `UActorComponent`，标记为 `BlueprintSpawnableComponent`，可以直接在蓝图中添加到 Actor 上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLensFile` / `SetLensFile` | 获取/设置当前使用的 LensFile 资产 | `ULensComponent` |
| `GetLensFilePicker` / `SetLensFilePicker` | 获取/设置 LensFile 选择器（支持使用默认 LensFile） | `ULensComponent` |
| `GetFIZEvaluationMode` / `SetFIZEvaluationMode` | 获取/设置 FIZ 数据源模式 | `ULensComponent` |
| `GetDistortionSource` / `SetDistortionSource` | 获取/设置畸变数据来源 | `ULensComponent` |
| `ShouldApplyDistortion` / `SetApplyDistortion` | 获取/设置是否启用畸变 | `ULensComponent` |
| `GetLensModel` / `SetLensModel` | 获取/设置当前畸变模型 | `ULensComponent` |
| `GetDistortionState` / `SetDistortionState` | 获取/设置畸变状态（参数数组） | `ULensComponent` |
| `ClearDistortionState` | 重置畸变状态为「无畸变」 | `ULensComponent` |
| `GetOverscanMultiplier` / `SetOverscanMultiplier` | 获取/设置 overscan 缩放系数 | `ULensComponent` |
| `GetFilmbackOverrideSetting` / `SetFilmbackOverrideSetting` | 获取/设置 Filmback 覆盖方式 | `ULensComponent` |
| `GetCroppedFilmback` / `SetCroppedFilmback` | 获取/设置裁切后的 Filmback | `ULensComponent` |
| `ShouldApplyNodalOffsetOnTick` / `SetApplyNodalOffsetOnTick` | 获取/设置是否在 Tick 时自动应用 Nodal Offset | `ULensComponent` |
| `ApplyNodalOffset` | 手动对指定组件应用 Nodal Offset | `ULensComponent` |
| `GetLensDistortionHandler` | 获取当前镜头模型的畸变处理器 | `ULensComponent` |
| `SetLensFileEvaluationInputs` | 手动设置 Focus/Zoom 评估输入 | `ULensComponent` |
| `WasNodalOffsetAppliedThisTick` | 查询本帧是否应用了 Nodal Offset | `ULensComponent` |
| `WasDistortionEvaluated` | 查询本帧是否评估了畸变 | `ULensComponent` |
| `GetOriginalFocalLength` | 获取原始焦距（未加 overscan） | `ULensComponent` |

### FIZ 评估模式 (`EFIZEvaluationMode`)

| 模式 | 说明 |
|---|---|
| `UseLiveLink` | 从 LiveLink 接收实时 FIZ 数据来评估 LensFile（默认） |
| `UseCameraSettings` | 使用目标摄影机当前的 FIZ 设置来评估 LensFile |
| `UseRecordedValues` | 使用 Sequencer 中录制的值（自动设置，用于回放） |
| `Manual` | 使用 Details 面板或蓝图中手动设置的值 |
| `DoNotEvaluate` | 不评估 LensFile |

### 畸变数据来源 (`EDistortionSource`)

| 来源 | 说明 |
|---|---|
| `LensFile` | 从 LensFile 评估畸变状态（默认） |
| `LiveLinkLensSubject` | 从 LiveLink 镜头 Subject 直接接收畸变状态 |
| `Manual` | 手动设置畸变参数 |

### 使用示例（蓝图描述）

**基本用法**：在 CameraActor 上添加 LensComponent

1. 在场景中放置一个 `CameraActor`
2. 在该 Actor 上添加 `LensComponent`（搜索 "Lens Component"）
3. 在 Details 面板中设置 `Lens File Picker` 指向你的 LensFile 资产
4. 勾选 `Apply Distortion` 启用畸变
5. 设置 `FIZ Evaluation Mode` 为 `UseLiveLink`（如果连接了物理摄影机）或 `UseCameraSettings`

**手动 Nodal Offset**：通过蓝图手动控制

1. 创建一个蓝图，在 Tick 或自定义事件中调用 `ApplyNodalOffset`
2. 传入目标 SceneComponent 引用（通常是追踪根组件）
3. 可选：传入手动 Focus/Zoom 值（`bUseManualInputs = true`）

## C++ 用法

### 头文件引入

```cpp
#include "LensComponent.h"

// 如果需要访问具体类型
#include "LensFile.h"
#include "CameraCalibrationTypes.h"
#include "LensDistortionModelHandlerBase.h"
```

### 基本用法

获取并配置 LensComponent：

```cpp
// 获取 Actor 上的 LensComponent
ULensComponent* LensComp = MyActor->FindComponentByClass<ULensComponent>();

// 设置 LensFile
LensComp->SetLensFile(MyLensFile);

// 启用畸变
LensComp->SetApplyDistortion(true);

// 设置 FIZ 评估模式
LensComp->SetFIZEvaluationMode(EFIZEvaluationMode::UseCameraSettings);
```

来源: `LensComponent.cpp` 中的 getter/setter 实现

### 进阶用法

**手动评估 LensFile 输入并应用 Nodal Offset**：

```cpp
// 设置手动 Focus/Zoom 输入
LensComp->SetLensFileEvaluationInputs(500.0f, 35.0f);  // Focus=500cm, Zoom=35mm

// 对指定组件手动应用 Nodal Offset
USceneComponent* TrackedRoot = MyActor->GetRootComponent();
LensComp->ApplyNodalOffset(TrackedRoot, /*bUseManualInputs=*/true, 500.0f, 35.0f);
```

来源: `LensComponent.cpp` 中的 `ApplyNodalOffset(USceneComponent*, bool, float, float)` 实现

**查询帧状态**：

```cpp
// 查询本帧是否完成了畸变评估
if (LensComp->WasDistortionEvaluated())
{
    // 获取当前畸变处理器，可用于访问 displacement map 等
    ULensDistortionModelHandlerBase* Handler = LensComp->GetLensDistortionHandler();
}

// 查询本帧是否应用了 Nodal Offset
if (LensComp->WasNodalOffsetAppliedThisTick())
{
    // 追踪组件已被偏移
}
```

来源: `LensComponent.cpp` 中的 `WasDistortionEvaluated()` 和 `WasNodalOffsetAppliedThisTick()` 实现

## Sequencer 集成

LensComponentEditor 模块提供了 Sequencer Track 的支持，可以：

- **录制**：通过 `FMovieSceneLensComponentTrackRecorderFactory` 自动录制镜头畸变参数到 Sequencer Track
- **回放**：`UMovieSceneLensComponentSection` 在 Sequencer 回放时自动驱动 LensComponent 的畸变状态
- **Nodal Offset 回放**：Section 支持 `bReapplyNodalOffset` 选项，在回放每帧重新评估 Nodal Offset
- **LensFile 覆盖**：Section 支持 `OverrideLensFile`，在回放时使用不同的 LensFile 资产

录制的数据包括畸变参数通道、FxFy（焦距像素比）通道和 Image Center 通道。

## 模块依赖

### LensComponent (Runtime)

| 模块 | 用途 |
|---|---|
| `LiveLinkComponents` | LiveLink 组件接口，用于接收实时 FIZ 数据 |
| `LiveLinkInterface` | LiveLink 基础接口 |
| `CameraCalibrationCore` (Private) | 镜头标定核心，提供 LensFile、LensModel、畸变处理器 |
| `CinematicCamera` (Private) | CineCameraComponent，被驱动的目标摄影机组件 |
| `Core` / `CoreUObject` / `Engine` (Private) | UE 基础模块 |

### LensComponentEditor (Editor)

| 模块 | 用途 |
|---|---|
| `CameraCalibrationCoreEditor` | 编辑器端镜头标定支持 |
| `LensComponent` | 运行时 LensComponent 模块 |
| `LevelSequence` / `MovieScene` / `MovieSceneTools` / `Sequencer` | Sequencer 集成 |
| `TakeTrackRecorders` | Take 录制系统集成 |
| `Slate` / `SlateCore` / `UnrealEd` | 编辑器 UI |

### Plugin 依赖

| Plugin | 用途 |
|---|---|
| `CameraCalibrationCore` | 提供 LensFile、LensModel、LensDistortionModelHandlerBase 等核心类型 |
| `LiveLink` | 实时数据传输 |
| `Takes` | Take 录制系统 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-01 | `a0f60cdbb5` | CameraCalibration: Add default distortion rendering mode option | 新增默认畸变渲染模式选项，改善用户体验 |
| 2025-07-10 | `9803c443cfa` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 代码质量改进，使用内联生成的 CPP 减少编译时间 |
| 2025-06-13 | `6bb19da9ff0` | LensComponent: Make the Lens Distortion Scene View Extension the default distortion rendering mode | 将 Scene View Extension 设为默认渲染模式（取代 Post Process Material） |

### 维护评价

- **创建时间**: 2023-12-21，约 2 年历史
- **拆分历史**: 从 `CameraCalibrationCore` 在 UE 5.4 时拆分出来（Config 中有 CoreRedirects 记录）
- **Beta 状态**: `IsBetaVersion=true`，`Hidden=true`，仅支持 `LiveLinkHub` 程序
- **活跃度**: 2025 年 6-9 月有连续的功能更新，处于**活跃维护**状态
- **注意**: 此 plugin 为 Beta 且 Hidden，不是默认可用的插件。它仅在 `SupportedPrograms` 列表中的 `LiveLinkHub` 下启用，标准 Editor 项目中不会自动加载

**推荐使用**: 如果你在做虚拟制片（Virtual Production）且使用 LiveLink 连接物理摄影机，这个组件是实现精确镜头畸变匹配的核心组件。虽然标记为 Beta，但已经是 Epic 虚拟制片工作流中不可或缺的一部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LensComponent)
- 官方文档: 无（.uplugin 中 DocsURL 为空）
- 依赖插件: [CameraCalibrationCore](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CameraCalibration)
