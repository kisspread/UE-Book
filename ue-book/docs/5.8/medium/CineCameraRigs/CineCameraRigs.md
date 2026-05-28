# Cine Camera Rigs

> Extended camera rigs for cinematic workflow（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 电影相机轨道 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、纹理） |
| 模块 | `CineCameraRigs` (Runtime), `CineCameraRigsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-31 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CineCameraRigs) | |

## 用途

该插件为电影制片流程扩展了 `CameraRig_Rail`（轨道相机）功能。它不仅仅是一个简单的相机轨道，而是提供了一套完整的、可参数化的电影级相机运动控制方案。核心解决的问题是：**在虚拟制片中，如何精确、可控地让相机沿着轨道运动，同时还能独立控制相机自身的焦距、光圈等属性，并提供丰富的视觉化调试工具。**

与原生 `CameraRig_Rail` 相比，它主要增加了：
1.  **参数化位置控制**：不使用传统的基于轨道长度的百分比，而是使用自定义的“绝对位置”参数，使得在定序器中控制位置变化更直观（如匀速运动）。
2.  **继承式相机属性控制**：相机的焦距、光圈、对焦距离可以作为元数据点存储在轨道的每个控制点上，并在运动过程中自动插值并应用到挂载的相机上。
3.  **驱动模式**：支持手动、按速度、按时长驱动，配合循环和反弹模式，可以创建复杂的自动巡游动画。
4.  **速度热力图可视化**：直观显示轨道上各点的运动速度，便于艺术调整。
5.  **挂载附件管理**：对挂载在轨道上的相机（或其他物体）提供更精细的位置/旋转轴向继承控制。

## 使用场景

-   **电影级虚拟制片镜头设计**：当你需要一个相机沿着预设轨道平稳移动，并且希望随距离或时间自动调整焦距、光圈以获得电影感的画面时。
-   **自动化巡游动画**：为场景制作自动播放的巡游或展示镜头，可设置速度、循环、反弹。
-   **复杂的相机运镜**：结合定序器（Sequencer），实现轨道上相机参数与运动轨迹分离的精确关键帧动画。
-   **实时视觉预览**：在编辑器视口中通过速度热力图，直观评估镜头运动的节奏感。

## 蓝图用法

### 核心节点

#### 驱动控制（`ACineCameraRigRail`）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetDriveMode` | 设置轨道的驱动模式（手动/速度/时长） | `ACineCameraRigRail` |
| `SetAbsolutePositionOnRail` | 设置轨道上的绝对位置（参数化） | `ACineCameraRigRail` |
| `SetDisplaySpeedHeatmap` | 开关速度热力图显示 | `ACineCameraRigRail` |
| `GetVelocityAtPosition` | 计算轨道上指定位置的瞬时速度 | `ACineCameraRigRail` |
| `GetCineSplineComponent` | 获取其内部的电影样条组件 | `ACineCameraRigRail` |

#### 附件控制（`ACineCameraRigRail` 属性）

| 属性 | 说明 |
|---|---|
| `bAttachLocationX/Y/Z` | 控制挂载物体是否继承轨道的位移（各轴独立） |
| `bAttachRotationX/Y/Z` | 控制挂载物体是否继承轨道的旋转（各轴独立） |
| `bInheritFocalLength/Aperture/FocusDistance` | 控制是否将样条点的相机属性应用到挂载的相机上 |

#### 样条数据操作（`UCineSplineComponent`）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetFocalLengthAtSplinePoint` | 在指定样条点设置焦距 | `UCineSplineComponent` |
| `SetApertureAtSplinePoint` | 在指定样条点设置光圈 | `UCineSplineComponent` |
| `SetFocusDistanceAtSplinePoint` | 在指定样条点设置对焦距离 | `UCineSplineComponent` |
| `SetAbsolutePositionAtSplinePoint` | 在指定样条点设置自定义绝对位置 | `UCineSplineComponent` |
| `GetSplineDataAtPosition` | 根据自定义绝对位置获取完整的样条点数据 | `UCineSplineComponent` |
| `AddSplineDataAtPosition` | 在指定的自定义位置添加一个新的样条点及其数据 | `UCineSplineComponent` |

### 使用示例（蓝图描述）

**创建一个匀速运动的相机轨道：**
1.  在场景中放置一个 `CineCameraRigRail` 对象。
2.  在其细节面板中，将 `Drive Mode` 设置为 `Speed`，并调整 `Speed` 属性（如 500 cm/s）。
3.  确保 `bPlay` 为 `true`。运行时，相机将按照设定速度沿轨道运动。
4.  通过 `bAttachLocationX/Y/Z` 和 `bAttachRotationX/Y/Z` 控制挂载相机的跟随方式。

**在定序器中手动控制相机属性和位置：**
1.  将 `CineCameraRigRail` 添加到定序器轨道。
2.  为其 `AbsolutePositionOnRail` 属性添加关键帧，控制相机在轨道上的位置。
3.  使用 `UCineSplineComponent` 的 `SetFocalLengthAtSplinePoint` 等节点，在蓝图或C++中动态设置轨道控制点的相机参数，这些参数将在相机移动到对应位置时被应用。

## C++ 用法

### 头文件引入

```cpp
#include "CineCameraRigRail.h"
#include "CineSplineComponent.h"
```

### 基本用法

获取并操作电影轨道的相机属性（来源：基于 `UCineSplineComponent` API 推断）。

```cpp
// 假设已经通过某种方式获取了 ACineCameraRigRail* 或 UCineSplineComponent* 指针
void SetupCineRail(ACineCameraRigRail* RailActor)
{
    if (RailActor)
    {
        // 获取内部样条组件
        UCineSplineComponent* CineSpline = RailActor->GetCineSplineComponent();
        if (CineSpline)
        {
            // 在轨道的第一个点设置焦距
            CineSpline->SetFocalLengthAtSplinePoint(0, 85.0f);

            // 在轨道的第二个点设置光圈
            CineSpline->SetApertureAtSplinePoint(1, 1.4f);

            // 根据自定义的“绝对位置”参数查询对应的样条点信息
            int32 FoundIndex;
            float CustomPosition = 0.75f; // 一个自定义的位置值
            if (CineSpline->FindSplineDataAtPosition(CustomPosition, FoundIndex))
            {
                FCineSplinePointData PointData = CineSpline->GetSplineDataAtPosition(CustomPosition);
                UE_LOG(LogCineSpline, Log, TEXT("Position %f: FocalLength is %f"), CustomPosition, PointData.FocalLength);
            }
        }

        // 设置轨道驱动模式为速度模式
        RailActor->SetDriveMode(ECineCameraRigRailDriveMode::Speed);
        RailActor->Speed = 300.0f; // 设置速度
    }
}
```

### 进阶用法

动态创建和配置一个完整的相机轨道，并挂载一个相机。

```cpp
#include "CineCameraRigRail.h"
#include "CineSplineComponent.h"
#include "CineCameraAttachMount.h"
#include "Camera/CineCameraActor.h"

void CreateDynamicCameraRail(UWorld* World, const FVector& Start, const FVector& End)
{
    // 1. 生成轨道
    FActorSpawnParameters SpawnParams;
    ACineCameraRigRail* RailActor = World->SpawnActor<ACineCameraRigRail>(Start, FRotator::ZeroRotator, SpawnParams);

    if (RailActor)
    {
        // 2. 获取并配置样条组件
        UCineSplineComponent* SplineComp = RailActor->GetCineSplineComponent();
        if (SplineComp)
        {
            // 添加两个样条点
            SplineComp->AddSplineWorldPoint(Start);
            SplineComp->AddSplineWorldPoint(End);

            // 为每个点设置相机参数
            SplineComp->SetFocalLengthAtSplinePoint(0, 24.0f); // 广角
            SplineComp->SetFocalLengthAtSplinePoint(1, 100.0f); // 长焦

            // 设置样条点的自定义绝对位置参数（用于非均匀参数化）
            SplineComp->SetAbsolutePositionAtSplinePoint(0, 0.0f);
            SplineComp->SetAbsolutePositionAtSplinePoint(1, 10.0f); // 表示从0到10的位置
        }

        // 3. 设置驱动模式为按速度驱动
        RailActor->SetDriveMode(ECineCameraRigRailDriveMode::Speed);
        RailActor->Speed = 200.0f;
        RailActor->LoopMode = ECineCameraRigRailLoopMode::Bounce; // 来回弹跳

        // 4. 生成一个相机并挂载到轨道上
        ACineCameraActor* Camera = World->SpawnActor<ACineCameraActor>(FVector::ZeroVector, FRotator::ZeroRotator);
        if (Camera)
        {
            // 将相机附加到轨道的相机挂载点（默认是`CameraMount`组件）
            Camera->AttachToComponent(RailActor->GetCameraMount(), FAttachmentTransformRules::SnapToTargetIncludingScale);
            RailActor->bInheritFocalLength = true; // 启用焦距继承
        }
    }
}
```

## Demo 示例

以下是一个最小化的C++示例，展示如何以编程方式创建一个简单的、可工作的 `CineCameraRigRail`。

```cpp
// MyCineRailDemo.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCineRailDemo.generated.h"

class ACineCameraRigRail;

UCLASS()
class AMyCineRailDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyCineRailDemo();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<ACineCameraRigRail> CineRail;
};
```

```cpp
// MyCineRailDemo.cpp
#include "MyCineRailDemo.h"
#include "CineCameraRigRail.h"
#include "CineSplineComponent.h"

AMyCineRailDemo::AMyCineRailDemo()
{
    PrimaryActorTick.bCanEverTick = false;
    CineRail = CreateDefaultSubobject<ACineCameraRigRail>(TEXT("CineRail"));
    RootComponent = CineRail;
}

void AMyCineRailDemo::BeginPlay()
{
    Super::BeginPlay();

    if (CineRail)
    {
        UCineSplineComponent* Spline = CineRail->GetCineSplineComponent();
        if (Spline)
        {
            // 在相对位置设置两个样条点
            Spline->AddSplineLocalPoint(FVector(0, 0, 0));
            Spline->AddSplineLocalPoint(FVector(1000, 0, 0));

            // 设置第一个点的焦距
            Spline->SetFocalLengthAtSplinePoint(0, 35.0f);
            // 设置第二个点的焦距
            Spline->SetFocalLengthAtSplinePoint(1, 50.0f);

            // 使用速度模式驱动
            CineRail->SetDriveMode(ECineCameraRigRailDriveMode::Speed);
            CineRail->Speed = 150.0f;
            CineRail->LoopMode = ECineCameraRigRailLoopMode::Loop;
            CineRail->bPlay = true;

            // 启用速度热力图以查看效果
            CineRail->bDisplaySpeedHeatmap = true;
        }
    }
}
```

## 模块依赖

从插件的 `.uplugin` 文件和模块构建推断，使用该插件需要以下**独特**的、不常见的模块依赖：

| 模块 | 用途 |
|---|---|
| `SequencerScripting` | 为电影轨道提供与定序器深度集成的脚本化控制能力 |
| `LevelSequenceEditor` | 在编辑器中深度集成和操作定序器资源 |
| `ConcertSyncCore` | 支持多用户编辑协同工作（在虚拟制片环境中重要） |
| `EditorScriptingUtilities` | 提供编辑器内脚本和工具开发的基础功能 |

*注意：您的模块还依赖 Core, CoreUObject, Engine, Slate 等通用模块，此处已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `ddded373` | Fix CineSpline parallel-curve desync when metadata properties are written directly by self-healing v | 修复了当直接写入元数据属性时，电影样条并行曲线不同步的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-02-03 | `4fc77002` | [Sequencer] Few small API export tweaks to allow to use these classes outside of sequencer. | 调整了少数API导出，允许在定序器外部使用这些类 |
| 2025-12-19 | `a01aeeaa` | check for UObjectInitialized  && !IsEngineExitRequested() before running clean-up code that involves | 在运行涉及UObject的清理代码前，增加了对UObject初始化状态和引擎退出请求的检查 |
| 2025-12-18 | `d951ccc8` | Adding metadata interpolation option for CineCameraRigRail | 为CineCameraRigRail添加了元数据插值选项 |

### 维护评价

**维护状态：活跃维护**

- **年龄**：约3年，属于较新的插件。
- **活跃度**：最近一次更新在2026年5月，是bug修复，且2025-2026年间有多次功能改进和API优化，表明仍在积极开发中。
- **实验性**：插件标记为 `IsBetaVersion = true` 且 `EnabledByDefault = false`，说明它功能强大但可能还在演进，API有变动风险。
- **稳定性**：近期提交显示有修复数据同步和内存管理的补丁，说明团队在关注其稳定性。
- **推荐度**：**推荐在虚拟制片项目中使用**。它是一个功能完整、针对性强的工具，尤其适合需要精细控制相机路径和属性的电影级项目。由于是实验性插件，建议在重要项目中做好版本管理和测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CineCameraRigs)
- 官方文档：无
- 测试用例：未在本插件目录内发现标准自动化测试文件