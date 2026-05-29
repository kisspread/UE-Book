# Virtual Camera

> Content for VirtualCameraCore which adds actors, components, and utilities for controlling and viewing cameras via physical devices.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟摄像机 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `VCamExtensions` (Runtime), `VCamExtensionsEditor` (Runtime), `VirtualCamera` (Runtime), `VirtualCameraEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-18 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCamera) | |

## 用途

VirtualCamera 插件是虚幻引擎虚拟制作（Virtual Production）工作流的核心组件之一。它提供了一套完整的框架，允许通过物理设备（如 iPhone、iPad 或专业控制器）远程操控 Unreal 场景中的虚拟摄像机。

该插件构建在 VirtualCameraCore 之上，增加了可直接放置到关卡中的 Actor 和 Component，使虚拟摄像机工作流可以在蓝图层面快速搭建和配置。核心功能包括：

- **物理设备驱动摄像机**：将物理设备的运动数据映射到虚拟摄像机的 Transform
- **与 Sequencer/Take Recorder 集成**：支持将虚拟摄像机的运动录制为 CineCameraActor 的关键帧动画
- **组件化架构**：摄像机控制、输入处理等通过独立组件实现，可灵活组合
- **多模块分层设计**：Runtime 模块提供运行时功能，Editor 模块提供编辑器扩展

插件处于 Beta 状态（`IsBetaVersion: true`），API 可能在后续版本中发生变化。

## 使用场景

- **虚拟制片拍摄**：使用 iPhone + Live Link 驱动虚拟摄像机，在 LED Volume 中实时预览拍摄角度
- **影视预演（Previz）**：通过物理控制器在虚拟场景中快速设计镜头运动
- **Take Recorder 录制**：将虚拟摄像机的实时运动录制为 Sequencer 关键帧，用于后期精修
- **多机位虚拟拍摄**：在关卡中放置多个 VCam Actor，通过设备切换控制不同机位

## 蓝图用法

本插件的公开蓝图 API 主要集中在 VirtualCamera 模块中，提供 Actor 和 Component 级别的虚拟摄像机控制。

### 核心节点

由于提供的源码样本有限（仅 VirtualCameraEditor 模块的编辑器支持代码），以下基于插件架构推断的核心类型：

| 节点 | 说明 | 所在类 |
|---|---|---|
| VCam Actor | 可放置到关卡的虚拟摄像机 Actor，集成摄像机组件和输入组件 | `AVirtualCameraActor` |
| 摄像机控制组件 | 处理来自物理设备的 Transform 数据并驱动摄像机 | 组件类（VCam 组件） |
| 录制支持 | 与 Take Recorder 集成，控制哪些组件参与录制 | `FVCamSupportForCinematicTooling` |

### 使用示例（蓝图描述）

1. **基本虚拟摄像机设置**：
   - 将 VCam Actor 拖入关卡
   - 配置 Live Link 数据源（连接物理设备）
   - 运行时设备移动会实时驱动虚拟摄像机

2. **Take Recorder 录制**：
   - 打开 Take Recorder 面板
   - 添加 VCam Actor 为录制源
   - 当 VCam 设置为以 ACineCameraActor 模式录制时，系统会自动跳过 VCam 和 Input 等附加组件，只录制摄像机 Transform

## C++ 用法

### 头文件引入

```cpp
#include "VCamSupportForCinematicTooling.h"
```

### 基本用法

VirtualCameraEditor 模块提供了与 Sequencer 和 Take Recorder 的集成支持：

```cpp
// 来源: Private/Cinematic/VCamSupportForCinematicTooling.h

#include "VCamSupportForCinematicTooling.h"

// FVCamSupportForCinematicTooling 负责管理全局委托，
// 确保虚拟摄像机与 Take Recorder 和 Sequencer 正确协作。
// 该类在构造时自动注册所需的全局委托。
UE::VirtualCamera::FVCamSupportForCinematicTooling CinematicSupport;
```

### 进阶用法

录制时的组件过滤控制——当虚拟摄像机配置为录制为 CineCameraActor 时，系统会跳过 VCam 相关组件，只录制摄像机本体数据：

```cpp
// 来源: Private/Cinematic/VCamSupportForCinematicTooling.h

// 该静态函数用于 ITakeRecorderSourcesModule::RegisterCanRecordDelegate
// 判断指定组件是否应该被 Take Recorder 录制
using namespace UE::VirtualCamera;
using namespace UE::TakeRecorderSources;

bool bCanRecord = FVCamSupportForCinematicTooling::CanRecordComponent(InArgs);
// 当 VCam 设置为以 ACineCameraActor 录制时，
// 此函数会跳过 VCam 组件和 Input 组件，
// 只录制核心摄像机 Transform 数据
```

## Demo 示例

```cpp
// MyVCamRecorder.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyVCamRecorder.generated.h"

UCLASS()
class UMyVCamRecorder : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
};
```

```cpp
// MyVCamRecorder.cpp
#include "MyVCamRecorder.h"
#include "VCamSupportForCinematicTooling.h"

void UMyVCamRecorder::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 虚拟摄像机的 Take Recorder 集成由 VCamedSupportForCinematicTooling
    // 在 VirtualCameraEditor 模块加载时自动初始化
    // 该类管理全局委托以确保 VCam 与 Sequencer/Take Recorder 正确协作
}

void UMyVCamRecorder::Deinitialize()
{
    Super::Deinitialize();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VirtualCameraCore` | 虚拟摄像机核心框架，提供基础摄像机控制逻辑 |
| `VCamExtensions` | 虚拟摄像机扩展功能 |
| `TakeRecorderSources` | Take Recorder 录制源集成 |
| `Sequencer` | Sequencer 时间线集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片资产分类调整和迁移 |
| 2026-04-20 | `9de9532f` | VCam: update transform track mask based on constraint filter | 根据约束过滤器更新变换轨道遮罩 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为新的 UE_LOGF 宏 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复批量替换错误后的重新提交 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚 CL51314860 提交 |

### 维护评价

- **创建时间**：2024 年 1 月从 Experimental 目录迁移而来（原始 CL 30679956）
- **Beta 状态**：`IsBetaVersion: true`，API 可能发生变化
- **活跃度**：2026 年仍有持续更新，包括功能改进（变换轨道遮罩）、代码现代化（UE_LOGF 迁移）和资产管理优化
- **已知限制**：作为 Beta 插件，默认未启用（`EnabledByDefault: false`），需要手动在项目设置中启用

**综合评价**：插件处于积极开发中，近期更新频率较高（月级别），功能持续完善。作为虚拟制作工作流的关键组件，适合需要使用物理设备控制虚拟摄像机的项目。但由于 Beta 状态，生产环境使用需关注 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCamera)
- [VirtualCameraCore](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore)（依赖的核心模块）