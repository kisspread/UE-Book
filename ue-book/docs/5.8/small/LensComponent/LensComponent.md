# Lens Component

> Implements the Lens Component for adding distortion to a cinematic camera（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 镜头组件 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（镜头数据资产） |
| 模块 | `LensComponent` (Runtime), `LensComponentEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-12-21 |
| 年龄标签 | 👴 老古董（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LensComponent) | |

## 用途

`LensComponent` 是一个运行时组件，用于将基于真实镜头校准数据（存储在 `LensFile` 资产中）的镜头畸变（Distortion）效果应用到同 Actor 上的 `CineCameraComponent`。

它解决了在虚拟制片（Virtual Production）工作流中，将真实镜头的光学特性（包括畸变、节点偏移和焦距变化）准确映射到虚拟摄像机上的问题。该组件通常与 `CameraCalibrationCore`、`LiveLink` 等插件协同工作，实现：
1.  **实时镜头畸变**：根据校准数据，实时扭曲摄像机画面，模拟真实镜头的光学畸变。
2.  **节点偏移补偿**：自动计算并应用由镜头旋转引起的节点偏移（Nodal Offset），避免虚拟摄像机在旋转时出现不必要的平移。
3.  **自动胶片背面（Filmback）控制**：可以根据校准数据自动调整摄像机的传感器尺寸，或应用裁剪设置。
4.  **多种输入源支持**：支持从 LiveLink 实时接收 FIZ（Focus, Iris, Zoom）数据、使用摄像机自身设置、或从关卡序列回放中读取记录值来评估镜头文件。

**核心价值**：为虚拟制作提供了一种将物理镜头特性无缝集成到数字摄像机工作流中的标准化方式，确保了虚拟与实拍画面在视觉属性上的一致性。

## 使用场景

-   你在进行**虚拟制片（Virtual Production）**，使用 LED 墙（LED Volume）进行拍摄，需要让虚拟摄像机的渲染结果与现场使用的真实电影镜头（如 Arri Signature Prime）的光学畸变完全匹配。
-   你正在搭建一个**虚拟摄像机（Virtual Camera）** 系统，希望它能实时反映真实镜头对焦和变焦时的画面畸变变化。
-   你需要在后期制作或实时渲染中，**同步并应用**通过镜头校准套件（Lens Calibration Toolkit）生成的镜头校准数据。
-   你希望**自动化**摄像机设置，例如根据校准数据自动调整焦距或应用胶片背面裁剪。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Lens File` / `Set Lens File` | 获取或设置组件使用的镜头校准文件（`ULensFile`）资产。 | `ULensComponent` |
| `Get FIZ Evaluation Mode` / `Set FIZ Evaluation Mode` | 获取或设置评估镜头文件所用的 FIZ（焦点、光圈、变焦）数据来源模式（如 `UseLiveLink`, `UseCameraSettings` 等）。 | `ULensComponent` |
| `Get Filmback Override Setting` / `Set Filmback Override Setting` | 获取或设置组件是否以及如何覆盖摄像机的胶片背面（Filmback）设置。 | `ULensComponent` |
| `Get Distortion Source` / `Set Distortion Source` | 获取或设置畸变状态的数据来源（镜头文件、LiveLink 或手动设置）。 | `ULensComponent` |
| `Should Apply Distortion` / `Set Apply Distortion` | 获取或设置是否将畸变效果应用到目标摄像机上。 | `ULensComponent` |
| `Get Lens Model` / `Set Lens Model` | 获取或设置当前使用的镜头畸变数学模型（当源为“手动”时生效）。 | `ULensComponent` |
| `Get Distortion State` / `Set Distortion State` / `Clear Distortion State` | 获取、设置或重置镜头的畸变状态参数。 | `ULensComponent` |
| `Apply Nodal Offset` | **关键节点**。手动将节点偏移应用到指定的场景组件上。可以指定使用组件当前模式评估镜头文件，或提供手动的焦点和变焦值。 | `ULensComponent` |
| `Get Lens Distortion Handler` | 获取当前镜头模型对应的畸变处理器实例。 | `ULensComponent` |

### 使用示例（蓝图描述）

1.  **基本设置**：将 `LensComponent` 添加到你的摄像机 Actor 上（确保该 Actor 也有 `CineCameraComponent`）。在细节面板中，将 `Lens File Picker` 指向你的 `LensFile` 资产。将 `FIZ Evaluation Mode` 设置为 `Use LiveLink` 或 `Use Camera Settings`。将 `Distortion Source` 设置为 `Lens File`。
2.  **实时畸变**：确保 `b Apply Distortion` 被勾选。组件会在 Tick 时自动评估镜头文件，并根据结果更新摄像机的畸变材质和过扫描（Overscan）。
3.  **手动触发节点偏移**：在需要时（例如，在摄像机旋转动画蓝图中），使用 `Apply Nodal Offset` 节点，传入需要偏移的组件引用（通常是摄像机组件自身或一个父级 SpringArm 组件）。设置 `b Use Manual Inputs` 为 `true`，并提供期望的焦点/变焦值，以在特定参数下计算偏移。

## C++ 用法

### 头文件引入

```cpp
#include "LensComponent.h"
```

### 基本用法

在代码中创建并配置一个 `ULensComponent`。
(基于 `ULensComponent` 的公开接口推断)
```cpp
// 假设在某个 Actor 的 .cpp 文件中
#include "LensComponent.h"
#include "LensFile.h"
#include "CineCameraComponent.h"

void AMyCameraActor::SetupLensEffect()
{
    // 1. 创建或获取组件
    ULensComponent* LensComp = FindComponentByClass<ULensComponent>();
    if (!LensComp)
    {
        LensComp = NewObject<ULensComponent>(this);
        LensComp->RegisterComponent();
    }

    // 2. 配置镜头文件
    ULensFile* MyLensFile = LoadObject<ULensFile>(nullptr, TEXT("/Game/CalibratedLensFiles/MyLens.LensFile"));
    if (MyLensFile)
    {
        LensComp->SetLensFile(MyLensFile);
    }

    // 3. 设置评估模式（例如，使用摄像机自身的 FIZ 设置）
    LensComp->SetFIZEvaluationMode(EFIZEvaluationMode::UseCameraSettings);

    // 4. 启用畸变应用
    LensComp->SetApplyDistortion(true);

    // 5. （可选）设置畸变源为手动，并直接提供状态
    // FLensDistortionState ManualState;
    // ... 填充 ManualState 数据 ...
    // LensComp->SetDistortionSource(EDistortionSource::Manual);
    // LensComp->SetDistortionState(ManualState);
}
```

### 进阶用法

手动控制节点偏移，并在特定条件下清除畸变。
(基于 `ULensComponent` 的公开接口推断)
```cpp
// 在某个需要精确控制的动画蓝图或游戏逻辑中
void AMyCameraRig::UpdateCameraRig()
{
    ULensComponent* LensComp = GetLensComponent(); // 假设存在获取方法
    if (LensComp)
    {
        // 场景1：手动应用节点偏移，使用手动输入的 FIZ 值
        USceneComponent* ComponentToAdjust = GetCameraBoom(); // 或摄像机自身
        float DesiredFocus = 5.0f; // 米
        float DesiredZoom = 35.0f; // mm
        LensComp->ApplyNodalOffset(ComponentToAdjust, true, DesiredFocus, DesiredZoom);

        // 场景2：检查并恢复默认状态
        if (bShouldResetDistortion)
        {
            LensComp->SetApplyDistortion(false);
            LensComp->ClearDistortionState();
            // 同时可能需要重置胶片背面设置
            if (LensComp->GetFilmbackOverrideSetting() != EFilmbackOverrideSource::DoNotOverride)
            {
                LensComp->SetFilmbackOverrideSetting(EFilmbackOverrideSource::DoNotOverride);
            }
        }
    }
}
```

## Demo 示例

一个最小可编译的 Actor 示例，展示如何用 C++ 创建并初始化 `LensComponent`。

**LensDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LensDemoActor.generated.h"

class ULensComponent;
class UCineCameraComponent;

UCLASS()
class ALensDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ALensDemoActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
    TObjectPtr<UCineCameraComponent> CineCamera;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Lens")
    TObjectPtr<ULensComponent> LensComponent;

    UPROPERTY(EditAnywhere, Category = "Lens")
    TObjectPtr<class ULensFile> LensFileAsset;
};
```

**LensDemoActor.cpp**
```cpp
#include "LensDemoActor.h"
#include "CineCameraComponent.h"
#include "LensComponent.h"
#include "LensFile.h"

ALensDemoActor::ALensDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建并设置默认的 CineCamera 组件
    CineCamera = CreateDefaultSubobject<UCineCameraComponent>(TEXT("CineCamera"));
    RootComponent = CineCamera;

    // 创建并设置默认的 Lens 组件
    LensComponent = CreateDefaultSubobject<ULensComponent>(TEXT("LensComponent"));
}

void ALensDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (LensFileAsset)
    {
        // 将设计时指定的镜头文件资产赋给组件
        LensComponent->SetLensFile(LensFileAsset);
    }

    // 配置组件使用 LiveLink 数据进行评估，并启用畸变
    LensComponent->SetFIZEvaluationMode(EFIZEvaluationMode::UseLiveLink);
    LensComponent->SetDistortionSource(EDistortionSource::LensFile);
    LensComponent->SetApplyDistortion(true);
}
```

## 模块依赖

要使用 `LensComponent` 插件的功能，你的模块需要依赖以下插件或模块：

| 模块 | 用途 |
|---|---|
| `CameraCalibrationCore` | 提供镜头校准、畸变模型（`ULensModel`）和畸变处理器的基础框架。**核心依赖**。 |
| `LiveLink` | 用于从外部设备接收实时的 FIZ（焦点、光圈、变焦）数据。 |
| `CinematicCamera` | 提供 `UCineCameraComponent`，这是组件应用效果的目标。 |
| `LensDistortion` | 提供镜头畸变后处理材质和渲染相关的基础设施。 |

*注意：根据 `.uplugin` 文件，该插件本身还依赖 `Takes` 插件，这通常与序列录制相关。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-15 | `d7870116` | LensDistortion: Add new lens distortion option to apply distortion as a scene view extension pass af | 新增场景视图扩展（Scene View Extension）渲染通道作为畸变应用选项。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件从 `Base` 前缀重命名为 `Default` 前缀，符合引擎新规范。 |
| 2025-09-02 | `006bdf67` | CameraCalibration: Add default distortion rendering mode option. | 为镜头畸变添加了默认渲染模式设置选项。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 对相关源文件添加了内联生成宏，优化编译。 |
| 2025-06-13 | `6bb19da9` | LensComponent: Make the Lens Distortion Scene View Extension the default distortion rendering mode. | 将“场景视图扩展”设为镜头畸变的默认渲染模式。 |

### 维护评价

**活跃维护中**。该插件虽然标记为 `IsBetaVersion = true`（实验性），但从近期提交记录（2025年6月至2026年1月）来看，Epic Games 团队仍在**积极开发和优化**该功能。主要更新集中在：
1.  **渲染管线优化**：将渲染模式从传统的后处理材质迁移到性能更优的“场景视图扩展”（Scene View Extension）。
2.  **规范对齐**：调整配置文件命名等以适应引擎整体规范。
3.  **功能增强**：增加默认渲染模式选项。

**注意事项**：由于处于 Beta 阶段，API 和功能细节可能在未来版本中发生变化。在生产环境中使用前，请务必进行充分测试。尽管如此，它是目前 UE5 中处理镜头校准畸变的核心和推荐解决方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LensComponent)
-   [官方文档]() （暂无）
-   [测试用例]() （建议在 `Engine/Plugins/VirtualProduction/` 目录下搜索相关自动化测试）