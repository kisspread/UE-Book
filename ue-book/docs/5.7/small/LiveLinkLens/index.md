# LiveLinkLens

> Adds a new LiveLink LensRole and LensController to support streaming of pre-calibrated lens data

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | false（仅限 LiveLinkHub） |
| 包含内容 | true |
| 模块 | LiveLinkLens (Runtime) |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkLens) | |

## 用途

LiveLinkLens 为 LiveLink 框架添加了一个专门的 **Lens Role**，用于实时传输镜头畸变（distortion）校准数据。标准的 LiveLink Camera Role 只传输相机的位置、旋转、FOV 等基本参数，而 Lens Role 在此基础上增加了镜头畸变模型参数（distortion parameters）、归一化焦距（FxFy）和图像中心点（principal point）。

该 plugin 的核心价值在于：它打通了外部镜头校准系统（如 Lens Distortion Kit、实体镜头编码器等）与 UE5 的 CameraCalibration / LensComponent 系统之间的数据通道。通过 LiveLink 的流式传输机制，校准后的镜头畸变数据可以实时应用到虚拟相机上，实现物理镜头与虚拟渲染的精确匹配——这是虚拟制片（Virtual Production）中的关键需求。

## 使用场景

- **虚拟制片 LED 墙场景**：你有一台物理摄影机通过 LiveLink 连接到 UE5，需要实时将镜头畸变数据应用到虚拟相机，使得 LED 墙上渲染的画面与物理镜头完美匹配
- **实时镜头编码器**：你在使用 Cooke /i 或 Zeiss eXtended Data 等镜头元数据协议，希望通过 LiveLink 将镜头焦距、畸变参数实时送入 UE5
- **后期镜头校准回放**：你在 Sequencer 中录制了带镜头畸变的 LiveLink 数据，需要在 Sequencer 回放时重现这些畸变效果
- **LiveLink Hub 多源管理**：你在使用 LiveLinkHub 集中管理多个 LiveLink 源，其中包括镜头畸变数据源

## 蓝图用法

### 数据结构

该 plugin 定义了三组数据结构，均标记为 `BlueprintType`，可在蓝图中直接使用：

#### 静态数据：`FLiveLinkLensStaticData`

继承自 `FLiveLinkCameraStaticData`，额外字段：

| 属性 | 类型 | 说明 |
|---|---|---|
| `LensModel` | `FName` | 镜头畸变模型类型（如 Anamorphic、Spherical 等），需与 CameraCalibrationSubsystem 中注册的模型匹配 |

#### 逐帧数据：`FLiveLinkLensFrameData`

继承自 `FLiveLinkCameraFrameData`，额外字段：

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `DistortionParameters` | `TArray<float>` | — | 畸变模型参数数组，参数含义取决于所使用的 LensModel |
| `FxFy` | `FVector2D` | (1.0, 1.78) | 归一化焦距，分别对应水平和垂直方向 |
| `PrincipalPoint` | `FVector2D` | (0.5, 0.5) | 归一化图像中心点，范围 [0, 1] |

#### 蓝图数据包装：`FLiveLinkLensBlueprintData`

继承自 `FLiveLinkBaseBlueprintData`，组合了静态数据和逐帧数据：

| 属性 | 类型 | 说明 |
|---|---|---|
| `StaticData` | `FLiveLinkLensStaticData` | 不随帧变化的静态镜头信息 |
| `FrameData` | `FLiveLinkLensFrameData` | 每帧更新的畸变数据 |

### 核心节点

该 plugin 没有暴露额外的 `BlueprintCallable` 函数。蓝图中的使用方式是通过 LiveLink 框架的标准蓝图节点（如 `GetLiveLinkSubjects`、`EvaluateLiveLinkFrameData` 等），选择 **Lens Role** 作为目标 Role 即可获取上述数据结构。

### 使用示例（蓝图描述）

1. 在蓝图中使用 `Evaluate Live Link Frame (Subject)` 节点
2. 将 Role 设置为 `Lens Role`
3. 输出引脚将包含 `FLiveLinkLensBlueprintData`
4. 可通过 Break 节点提取 `DistortionParameters`、`FxFy`、`PrincipalPoint` 等字段

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkLensRole.h"
#include "LiveLinkLensTypes.h"
#include "LiveLinkLensController.h"
```

### 基本用法：读取 LiveLink 镜头数据

从 LiveLink Subject 获取镜头畸变数据：

```cpp
// 来源: LiveLinkLensController.cpp Tick()
// 获取 LiveLink Subject 的帧数据
const FLiveLinkLensStaticData* StaticData = SubjectData.StaticData.Cast<FLiveLinkLensStaticData>();
const FLiveLinkLensFrameData* FrameData = SubjectData.FrameData.Cast<FLiveLinkLensFrameData>();

if (StaticData && FrameData)
{
    // 从静态数据获取镜头畸变模型名称
    FName LensModelName = StaticData->LensModel;
    
    // 从逐帧数据获取畸变参数
    TArray<float> Parameters = FrameData->DistortionParameters;
    FVector2D FxFy = FrameData->FxFy;
    FVector2D Center = FrameData->PrincipalPoint;
}
```

### 进阶用法：驱动 LensComponent

Controller 内部展示了如何将 LiveLink 镜头数据应用到 `ULensComponent`：

```cpp
// 来源: LiveLinkLensController.cpp Tick()
// 需要 LensComponent 设置 DistortionSource 为 LiveLinkLensSubject

if (ULensComponent* LensComponent = Cast<ULensComponent>(GetAttachedComponent()))
{
    if (LensComponent->GetDistortionSource() == EDistortionSource::LiveLinkLensSubject)
    {
        // 通过 CameraCalibrationSubsystem 查找注册的镜头模型
        UCameraCalibrationSubsystem* SubSystem = GEngine->GetEngineSubsystem<UCameraCalibrationSubsystem>();
        const TSubclassOf<ULensModel> LensModel = SubSystem->GetRegisteredLensModel(StaticData->LensModel);
        
        if (LensComponent->GetLensModel() != LensModel)
        {
            LensComponent->SetLensModel(LensModel);
        }
        
        // 构建畸变状态并应用到 LensComponent
        FLensDistortionState DistortionState;
        DistortionState.DistortionInfo.Parameters = FrameData->DistortionParameters;
        DistortionState.FocalLengthInfo.FxFy = FrameData->FxFy;
        DistortionState.ImageCenter.PrincipalPoint = FrameData->PrincipalPoint;
        
        LensComponent->SetDistortionState(DistortionState);
    }
}
```

### Sequencer 录制与回放

`UMovieSceneLiveLinkSubSectionLensRole` 负责在 Sequencer 中处理 Lens Role 数据的录制和回放：

```cpp
// 来源: MovieSceneLiveLinkSubSectionLensRole.cpp
// 该类自动处理以下工作：
// 1. Initialize: 根据 LensModel 创建对应参数数量的 MovieScene Float Channel
// 2. CreateChannelProxy: 为 Sequencer 编辑器创建可编辑的通道代理
// 3. RecordFrame: 每帧将 DistortionParameters 写入 Sequencer 轨道
// 4. FinalizeSection: 完成录制，优化关键帧数据
```

## Demo 示例

该 plugin 没有独立的测试用例。以下是一个最小使用示例的骨架代码：

```cpp
// MyLensReceiver.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "LiveLinkLensTypes.h"
#include "MyLensReceiver.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyLensReceiver : public UActorComponent
{
    GENERATED_BODY()

public:
    // 处理收到的 LiveLink 镜头数据
    void ProcessLensData(const FLiveLinkLensStaticData& InStaticData, 
                         const FLiveLinkLensFrameData& InFrameData)
    {
        // 读取畸变模型名称
        FName ModelName = InStaticData.LensModel;
        
        // 读取当前帧的畸变参数
        const TArray<float>& Params = InFrameData.DistortionParameters;
        FVector2D FocalLength = InFrameData.FxFy;
        FVector2D Center = InFrameData.PrincipalPoint;
        
        // TODO: 应用到你的系统中
    }
};
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "LiveLinkLens",
    "CameraCalibrationCore",
    "LiveLinkInterface"
});
```

## 模块依赖

### Plugin 依赖（.uplugin）

| Plugin | 用途 |
|---|---|
| `LiveLink` | LiveLink 框架基础 |
| `CameraCalibrationCore` | 镜头校准子系统、镜头模型定义 |
| `LensComponent` | 镜头组件，负责应用畸变效果 |

### 公共模块依赖（PublicDependencyModuleNames）

| 模块 | 用途 |
|---|---|
| `CameraCalibrationCore` | `UCameraCalibrationSubsystem`、`ULensModel`、`FLensDistortionState` |
| `CinematicCamera` | 电影相机相关类型 |
| `LiveLinkComponents` | LiveLink 组件框架 |
| `LiveLinkInterface` | LiveLink 接口定义（Role、Subject、FrameData 等） |

### 私有模块依赖（PrivateDependencyModuleNames）

| 模块 | 用途 |
|---|---|
| `Core` / `CoreUObject` / `Engine` | UE 基础模块 |
| `LensComponent` | `ULensComponent`，Controller 驱动的目标组件 |
| `LiveLinkMovieScene` | LiveLink 与 Sequencer 集成 |
| `MovieScene` / `MovieSceneTracks` | Sequencer 轨道和通道系统 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-05-01 | `41cc7cb77fd4` | Fix crash when take recording Live Link and Lens Model does not exist | 修复了在 Take 录制时，如果镜头模型不存在导致崩溃的问题——增加了防御性检查 |
| 2024-05-16 | `1a3350183e59` | Remove the feature where a LiveLink Lens Controller will automatically set the distortion source property of the lens component that it controls | 不再自动设置 LensComponent 的 DistortionSource，改为由用户手动配置（行为变更） |
| 2023-12-21 | `c2472ab2d987` | Move LensComponent into its own plugin | 将 LensComponent 拆分为独立 plugin，LiveLinkLens 作为私有依赖引用它 |

### 维护评价

- **创建时间**：2021 年 3 月，已超过 5 年
- **活跃状态**：维护中。最近一次更新（2025-05-01）是 bug 修复，说明仍在被使用和维护
- **代码规模**：8 个源文件（3 个 Public .h + 3 个 Private .h/cpp + 1 个 Build.cs + 1 个 .uplugin），结构简洁
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion: true`，说明 Epic 仍将其视为实验性功能
- **平台限制**：`ProgramAllowlist: ["LiveLinkHub"]`，模块仅在 LiveLinkHub 程序中加载，标准编辑器/游戏不会加载此模块
- **已知限制**：
  - 没有 BlueprintCallable 函数暴露，蓝图使用完全依赖 LiveLink 框架的标准节点
  - 没有独立的自动化测试
  - 5.1 版本有大量废弃属性和迁移代码，说明该 plugin 经历过较大的架构调整
- **推荐**：如果你在做虚拟制片并且使用 LiveLinkHub，这个 plugin 是必需的。如果只是在标准编辑器中使用 LiveLink，注意该 plugin 默认不会加载

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkLens)
- [LiveLinkLensRole.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/LiveLinkLens/Source/LiveLinkLens/Public/LiveLinkLensRole.h) — Lens Role 定义
- [LiveLinkLensTypes.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/LiveLinkLens/Source/LiveLinkLens/Public/LiveLinkLensTypes.h) — 数据结构定义
- [LiveLinkLensController.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/LiveLinkLens/Source/LiveLinkLens/Public/LiveLinkLensController.h) — Controller 定义
