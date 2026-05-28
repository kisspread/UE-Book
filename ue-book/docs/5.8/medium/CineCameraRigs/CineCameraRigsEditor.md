# CineCameraRigs

> Extended camera rigs for cinematic workflow

| 属性 | 值 |
|---|---|
| 中文名 | 电影摄像机轨道 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `CineCameraRigs` (Runtime), `CineCameraRigsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-31 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CineCameraRigs) | |

## 用途

CineCameraRigs 是 Epic 为虚拟制片/影视动画工作流打造的**扩展样条摄像机轨道系统**。它解决了标准 Spline + CinematicCamera 组合中缺失的关键问题：

1. **摄像机参数逐点存储**：标准样条只存储位置/旋转，而 CineSpline 允许在每个样条点上独立设置焦距（FocalLength）、光圈（Aperture）、焦点距离（FocusDistance）等摄像机参数，并沿轨道自动插值。
2. **自定义参数化驱动**：CineCameraRigRail 提供了绝对位置（AbsolutePosition）和驱动模式（DriveMode）控制，让 Sequencer 动画可以精确控制摄像机在轨道上的运动。
3. **速度可视化**：内置速度曲线可视化，帮助导演/动画师直观判断摄像机运动节奏。
4. **切线类型控制**：每个样条点支持自定义插值切线类型（ECineSplineMetadataTangentType），实现更细腻的运动曲线控制。

这个插件本质上是一个**影视级样条摄像机导轨**，填补了 Unreal Engine 在电影/广告制作中精确控制运动镜头的空白。

## 使用场景

- 你在做电影/广告级别的虚拟制片，需要摄像机沿轨道平滑运动的同时自动变焦 → 用 CineCameraRigRail
- 你需要在 Sequencer 中精确控制镜头运动，每个关键帧设置不同的焦距/光圈 → 用 CineSplineComponent 的逐点摄像机参数
- 你需要可视化摄像机在轨道上的速度分布，判断运动节奏是否合理 → 用 CineSpline 的速度可视化功能
- 你希望在样条编辑器中直接编辑摄像机参数，而不是分别操作多个 Actor → 用 CineSplineMetadataDetails 面板

## 蓝图用法

> ⚠️ 本插件为实验性功能（IsBetaVersion=true），API 可能在后续版本中变更。

### 核心节点

基于源码中的公开 API 分析，CineCameraRigs 提供以下核心蓝图功能：

| 节点 | 说明 | 所在类 |
|---|---|---|
| 设置样条点焦距 | 在指定样条点设置 FocalLength | `UCineSplineMetadata` |
| 设置样条点光圈 | 在指定样条点设置 Aperture | `UCineSplineMetadata` |
| 设置样条点焦点距离 | 在指定样条点设置 FocusDistance | `UCineSplineMetadata` |
| 设置样条点旋转 | 在指定样条点设置 PointRotation（四元数） | `UCineSplineMetadata` |
| 设置样条点插值类型 | 切换切线插值模式（线性/曲线等） | `UCineSplineMetadata` |
| 设置绝对位置 | 控制摄像机在轨道上的绝对位置 | `ACineCameraRigRail` |
| 设置驱动模式 | 切换驱动模式 | `ACineCameraRigRail` |

### 使用示例（蓝图描述）

**基本用法——创建摄像机轨道：**

1. 在场景中放置一个 `ACineCameraRigRail` Actor
2. 在 Details 面板中编辑样条点，设置每个点的位置和旋转
3. 对每个样条点设置摄像机参数（焦距、光圈、焦点距离）
4. 在 Sequencer 中对 `AbsolutePosition` 属性做关键帧动画，摄像机将沿轨道平滑运动并自动插值摄像机参数

**进阶用法——逐点变焦轨道：**

1. 创建 CineCameraRigRail，在第一个样条点设置 FocalLength=35mm（广角）
2. 在最后一个样条点设置 FocalLength=85mm（长焦）
3. 摄像机沿轨道运动时会自动在两个焦距之间平滑插值
4. 使用速度可视化功能检查运动节奏

## C++ 用法

### 头文件引入

```cpp
#include "CineSplineComponent.h"
#include "CineCameraRigRail.h"
```

### 基本用法

从源码结构推断的基本操作方式：

```cpp
// 获取 CineCameraRigRail 的样条组件
ACineCameraRigRail* RigRail = /* 获取或 SpawnActor */;
UCineSplineComponent* CineSpline = Cast<UCineSplineComponent>(RigRail->GetSplineComponent());

// 获取样条点的元数据
UCineSplineMetadata* Metadata = Cast<UCineSplineMetadata>(CineSpline->GetSplineMetadata());

// 设置样条点的摄像机参数
const int32 PointIndex = 0;
CineSpline->SetLocationAtSplinePoint(PointIndex, NewLocation, ESplineCoordinateSpace::World);
// 摄像机参数通过 CineSplineMetadata 存储和管理
```

### 进阶用法

自定义样条点的切线类型和驱动控制：

```cpp
// 设置样条点的切线插值类型
// ECineSplineMetadataTangentType 定义了不同的插值模式

// 设置绝对位置控制摄像机在轨道上的位置
// ACineCameraRigRail 提供 DriveMode 控制
// ECineCameraRigRailDriveMode 枚举定义了不同的驱动模式
```

## Demo 示例

```cpp
// CineCameraRigsDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CineCameraRigsDemo.generated.h"

class ACineCameraRigRail;

UCLASS()
class ACineCameraRigsDemo : public AActor
{
    GENERATED_BODY()

public:
    ACineCameraRigsDemo();

    UPROPERTY(EditAnywhere, Category = "Demo")
    ACineCameraRigRail* CameraRail;
};
```

```cpp
// CineCameraRigsDemo.cpp
#include "CineCameraRigsDemo.h"
#include "CineCameraRigRail.h"
#include "CineSplineComponent.h"

ACineCameraRigsDemo::ACineCameraRigsDemo()
{
    PrimaryActorTick.bCanEverTick = false;

    // 在实际使用中，通常通过编辑器放置 CineCameraRigRail Actor
    // 然后在 Details 面板中配置样条点和摄像机参数
    // 最后在 Sequencer 中对 AbsolutePosition 做关键帧动画
}
```

> 注：CineCameraRigRail 的主要交互集中在编辑器 UI 和 Sequencer 中，C++ 运行时直接操作较少。

## 模块依赖

从 .uplugin 的 Plugins 列表和代码结构推断的依赖关系：

| 模块 | 用途 |
|---|---|
| `CinematicCamera` | 提供 CineCamera 组件和相关摄像机属性 |
| `EditorScriptingUtilities` | 编辑器脚本工具支持 |
| `ConcertSyncCore` | 多用户协作同步支持 |
| `SequencerScripting` | Sequencer 脚本化接口 |
| `LevelSequenceEditor` | 关卡序列编辑器集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `ddded373` | Fix CineSpline parallel-curve desync when metadata properties are written directly by self-healing v | 修复直接写入元数据时样条平行曲线不同步的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 UE_LOGF |
| 2026-02-03 | `4fc77002` | [Sequencer] Few small API export tweaks to allow to use these classes outside of sequencer. | 调整 API 导出以支持在 Sequencer 外部使用这些类 |
| 2025-12-19 | `a01aeeaa` | check for UObjectInitialized && !IsEngineExitRequested() before running clean-up code that involves | 在清理代码前增加对象初始化和引擎退出状态检查 |
| 2025-12-18 | `d951ccc8` | Adding metadata interpolation option for CineCameraRigRail | 为 CineCameraRigRail 添加元数据插值选项 |

### 维护评价

- **创建时间**：2023-01-31，约 3 年前
- **更新频率**：近期保持活跃维护，2025-2026 年有多次实质性更新
- **功能演进**：从初始版本持续增加新功能（元数据插值选项、API 开放化等）并修复问题
- **实验性标记**：`IsBetaVersion=true` 且 `EnabledByDefault=false`，说明 Epic 仍在迭代中，API 可能变化
- **推荐程度**：如果你在做虚拟制片/影视动画工作流，值得一试，但注意这是实验性插件，不建议用于需要长期稳定性的生产环境项目。关注版本更新时的 breaking changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CineCameraRigs)
- 官方文档：暂无（.uplugin 中 DocsURL 为空）