# CineCameraRigs

> Extended camera rigs for cinematic workflow

| 属性 | 值 |
|---|---|
| 中文名 | 电影级相机轨道 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、C++类） |
| 模块 | `CineCameraRigs` (Runtime), `CineCameraRigsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-16 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CineCameraRigs) | |

## 用途

CineCameraRigs 插件为虚拟制片（Virtual Production）流程提供了扩展的相机辅助工具，主要包含两大核心功能：

- **CineCameraRigRail**：一种沿样条（Spline）运行的相机轨道 Actor，可让相机沿着预设路径移动，同时支持驱动模式（自动/手动）和绝对的轨道位置控制，适合在关卡中实现复杂而平滑的相机运动。
- **CineSplineComponent**：对标准样条组件的增强，允许为样条点附加电影元数据（焦距、光圈、对焦距离）以及独立的点旋转控制，并支持在视口中直接编辑这些参数。

插件并非简单的样条相机，而是专门为高精度、可复用的电影镜头运动而设计，填补了普通相机轨道在电影化参数控制上的空白。

## 使用场景

- **虚拟拍摄中的相机路径规划**：在 VR 或 LED 墙摄制环境中，需要预先设定相机运动轨迹，且能在运行时动态调整绝对位置。
- **电影级镜头运动**：需要沿样条移动相机的同时，在每个样条点设置不同的焦距、光圈和对焦距离，模拟真实镜头的呼吸效应或焦点变化。
- **多机位编排**：配合 Sequencer 和 Level Sequence，可以快速创建多台沿不同轨道运动的虚拟相机，进行预演或录制。

## 蓝图用法

> **注意**：大部分编辑器功能（如细节面板控制、样条可视化）不暴露给蓝图，但运行时组件和 Actor 可直接在蓝图编辑器中拖放使用。

### 核心 Actor / 组件

| 蓝图节点 / 类型 | 说明 |
|---|---|
| `ACineCameraRigRail` | 放置在关卡中的相机轨道 Actor，内部包含 `UCineSplineComponent`，可附加任意相机 |
| `UCineSplineComponent` | 继承自 `USplineComponent`，为每个样条点提供 `FocalLength`、`Aperture`、`FocusDistance`、`PointRotation` 元数据 |

### 常用操作方法

- **在蓝图中使用 RigRail**  
  1. 从菜单 `Place Actors` → `CineCameraRigs` → `CineCameraRigRail` 放置到关卡。  
  2. 选中 RigRail，在细节面板中找到 **Rail Control** 分类，可设置 **Drive Mode**（`Manual` / `Velocity` / `Speed`）。  
  3. 将任意 CineCameraActor 的子级附加到 RigRail 的根或通过 `Attach Actor` 节点连接。

- **通过蓝图控制轨道位置（Manual 模式）**  
  - 使用 `Set Absolute Position` 节点（通过 `ACineCameraRigRail` 暴露的 `SetAbsolutePosition(float)` 函数）直接设置轨道在样条上的归一化位置（0~1）。  
  - 通过 `Get Current Position` 获取当前位置。

- **读取样条点电影数据**  
  - `UCineSplineComponent` 提供了 `GetFloatPropertyAtSplinePoint(PoinIdx, "FocalLength")` 等类似函数（需检查实际 API，但通常通过 SplineMetadata 访问）。  
  - 在蓝图中可尝试 `SplineComponent` → `Get Spline Metadata` 节点（需要启用实验性功能）。

## C++ 用法

### 头文件引入

```cpp
#include "CineCameraRigs.h"          // 主模块头
#include "CineCameraRigRail.h"       // 轨道 Actor
#include "CineSplineComponent.h"     // 增强样条组件
#include "CineSplineMetadata.h"      // 样条点元数据
```

### 基本用法

**创建并配置 CineCameraRigRail**

```cpp
// 在关卡中生成轨道
ACineCameraRigRail* RigRail = GetWorld()->SpawnActor<ACineCameraRigRail>(FVector::ZeroVector, FRotator::ZeroRotator);

// 获取其内部的 CineSplineComponent
UCineSplineComponent* SplineComp = RigRail->GetCineSplineComponent();

// 添加样条点（引擎会自动创建元数据）
FVector PointLocation = FVector(100, 0, 0);
FSplinePoint Point(1, PointLocation, ESplinePointType::Curve);
SplineComp->AddSplinePoint(PointLocation, ESplineCoordinateSpace::World, /*bUpdateSpline*/ true);

// 设置该样条点的电影属性（通过元数据）
if (UCineSplineMetadata* Metadata = SplineComp->GetCineSplineMetadata())
{
    // 注意：样条点索引是动态的，通常使用 AddSplinePoint 后最后点为最大索引
    int32 PointIdx = SplineComp->GetNumberOfSplinePoints() - 1;
    Metadata->FocalLength.Points[PointIdx].OutVal = 35.0f;  // 35mm 焦距
    Metadata->Aperture.Points[PointIdx].OutVal = 2.8f;
    Metadata->FocusDistance.Points[PointIdx].OutVal = 500.0f; // 0.5m 对焦距离
}
```

**运行时改变轨道位置（Manual 模式）**

```cpp
// 设置驱动器为手动模式
RigRail->SetDriveMode(ECineCameraRigRailDriveMode::Manual);

// 将相机移到样条的中点（归一化位置 0.5）
RigRail->SetAbsolutePosition(0.5f);

// 获取当前位置
float Pos = RigRail->GetAbsolutePosition(); // 0.0 ~ 1.0
```

### 进阶用法

**自定义样条点旋转（CineSplineComponentVisualizer）**

在编辑器视口中，选中 CineSplineComponent 后，可以通过视口工具栏切换可视化模式：
- 按“V”键或右键菜单选择“Visualize Normalized Position”显示样条长度/位置。
- 开启“Manipulate Point Rotation”后，可以用变换控件独立旋转样条点（不改变样条路径）。

代码中通过 `UCineSplineMetadata` 的 `PointRotation` 数组读写每个点的旋转：

```cpp
// 读取第一个点的旋转
FQuat Rot = Metadata->PointRotation.Points[0].OutVal;
// 设置第二个点的旋转
Metadata->PointRotation.Points[1].OutVal = FQuat(FRotator(0, 45, 0));
SplineComp->UpdateSpline();
```

**在 Sequencer 中驱动轨道**

插件依赖 `SequencerScripting` 和 `LevelSequenceEditor`，可以在 Sequencer 中为 ACineCameraRigRail 的 `Absolute Position` 属性添加关键帧，实现自动化运动。编辑器还提供了右键菜单快速将轨道绑定到 Sequencer。

## Demo 示例

以下是一个最小化 C++ Actor，在 BeginPlay 时自动沿 CineCameraRigRail 移动相机并逐点设置元数据。

**MyRigRailDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyRigRailDemo.generated.h"

class ACineCameraRigRail;

UCLASS()
class AMyRigRailDemo : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "RigRail")
    ACineCameraRigRail* RigRailActor;

    UFUNCTION(BlueprintCallable, Category = "RigRail")
    void MoveCameraAlongRail(float NormalizedPos);
};
```

**MyRigRailDemo.cpp**

```cpp
#include "MyRigRailDemo.h"
#include "CineCameraRigRail.h"
#include "CineSplineComponent.h"
#include "CineSplineMetadata.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/Pawn.h"

void AMyRigRailDemo::BeginPlay()
{
    Super::BeginPlay();

    if (!RigRailActor) return;

    // 设置轨道样条点并赋予电影属性
    UCineSplineComponent* SplineComp = RigRailActor->GetCineSplineComponent();
    SplineComp->ClearSplinePoints();

    // 添加三个样条点
    SplineComp->AddSplinePoint(FVector(0, 0, 0), ESplineCoordinateSpace::World, false);
    SplineComp->AddSplinePoint(FVector(500, 0, 200), ESplineCoordinateSpace::World, false);
    SplineComp->AddSplinePoint(FVector(1000, 0, 0), ESplineCoordinateSpace::World, true);  // true 表示更新样条

    // 设置每个点的焦距/光圈/对焦距离
    UCineSplineMetadata* Metadata = SplineComp->GetCineSplineMetadata();
    if (Metadata)
    {
        Metadata->FocalLength.Points[0].OutVal = 24.0f;
        Metadata->FocalLength.Points[1].OutVal = 50.0f;
        Metadata->FocalLength.Points[2].OutVal = 85.0f;

        Metadata->Aperture.Points[0].OutVal = 4.0f;
        Metadata->Aperture.Points[1].OutVal = 2.8f;
        Metadata->Aperture.Points[2].OutVal = 1.4f;

        Metadata->FocusDistance.Points[0].OutVal = 300.0f;
        Metadata->FocusDistance.Points[1].OutVal = 600.0f;
        Metadata->FocusDistance.Points[2].OutVal = 900.0f;
    }

    // 将轨道模式设为手动
    RigRailActor->SetDriveMode(ECineCameraRigRailDriveMode::Manual);
}

void AMyRigRailDemo::MoveCameraAlongRail(float NormalizedPos)
{
    if (RigRailActor)
    {
        RigRailActor->SetAbsolutePosition(FMath::Clamp(NormalizedPos, 0.0f, 1.0f));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorScriptingUtilities` | 提供编辑器脚本辅助功能 |
| `ConcertSyncCore` | 支持多用户协作（虚拟制片常用） |
| `SequencerScripting` | 通过脚本控制 Sequencer |
| `LevelSequenceEditor` | 编辑关卡序列的编辑器集成 |
| `SplineComponentVisualizer` | 继承并扩展样条可视化和交互 |

**注**：除了上述依赖，本插件还间接依赖 Core, Engine, UnrealEd 等标准模块。

## 维护状态

### 近期更新

- 2025-10-14 `11f72ed` Constraints: fix misuse of invalid worlds（修复约束中的无效世界滥用）
- 2025-10-03 `c69ace0` CineCameraRigs: UE_API（添加 UE_API 导出宏）
- 2025-08-05 `ae82625` Sequencer: Deprecate SetObjectGuid …（弃用 Sequencer 旧接口）
- 2025-06-17 `7502b8c` Splines - Fixed bug where property change notifications…（修复样条属性变更通知问题）
- 2025-06-16 `aeaa44f` [Backout] - CL43554745（回滚变更）

### 维护评价

**综合评价**：**活跃维护**。该插件于 2025 年 6 月创建，至今（2025 年 10 月）不足 5 个月，但已在短时间内完成多次重要提交：添加 API 导出、修复约束 bug、跟随上游样条改动。开发者来自 Epic Games，且作为实验性插件，预计将持续获得更新。尚未发现已知的重大限制或废弃迹象。

**建议**：由于插件仍处于 Beta 阶段（`IsBetaVersion=true`），使用时可能遇到 API 调整或文档不足的情况，但由于其目标明确且依赖成熟组件（样条、Sequencer），当前版本已具备实用功能，适合在虚拟制片项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CineCameraRigs)
- [官方文档](https://docs.unrealengine.com/5.7/zh-CN/virtual-production-camera-rigs/)（暂无专页，可参考虚拟制片文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CineCameraRigs/Tests)（部分测试可能位于引擎测试目录）