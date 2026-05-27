# Control Rig

> Framework for animation driven by user controls.

| 属性 | 值 |
|---|---|
| 中文名 | 控制绑定 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `ControlRig` (Runtime), `ControlRigDeveloper` (Runtime), `ControlRigEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-06-14 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ControlRig) | |

## 用途

ControlRig 是 Unreal Engine 的核心程序化动画框架。它不仅仅是一个用户控件系统，而是一个完整的、基于节点的（RigVM）系统，用于创建、驱动和编辑骨骼网格体（Skeletal Mesh）的骨骼变形。它解决的核心问题是：提供一套统一的、高性能的工具，让开发者能够通过可视化节点图（蓝图风格）或 C++ 代码，程序化地控制角色骨骼，实现复杂的动画效果、动态变形、以及精确的动画编辑工作流。

## 使用场景

- **程序化骨骼驱动**：你需要在运行时根据物理模拟、游戏逻辑或用户输入动态计算骨骼的变换（如摇晃的尾巴、物理驱动的布料、瞄准 IK）。
- **动画蓝图中的复杂动画逻辑**：你想在动画蓝图中创建比纯状态机更复杂的、基于节点的动画效果，例如高级的 IK/FK 混合、动态骨骼偏移。
- **动画编辑与修正**：你需要在动画编辑器中对导入的动画进行精细的手工调整、添加程序化效果，或者从零开始创建绑定（Rig）和动画。

## 模块概述

| 模块 | 类型 | 说明 |
|---|---|---|
| **ControlRig** | Runtime | 核心运行时库。包含绑定资产、控制、RigVM 执行器、求解器等核心逻辑，负责在游戏运行时计算骨骼变换。 |
| **ControlRigDeveloper** | Runtime | 开发者支持库。提供用于在编辑器内构建、调试 ControlRig 资产（如构建绑定图表）的底层 API 和工具。 |
| **ControlRigEditor** | Runtime | 编辑器集成模块。实现 ControlRig 编辑器 UI、图表编辑器、细节面板自定义、以及 Sequencer 集成等完整的编辑器工作流。 |

## 蓝图用法

ControlRig 的蓝图用法主要通过动画蓝图（AnimBP）和直接操作 ControlRig 资产实例进行。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Control Float / Vector / Transform` | 在运行时设置 ControlRig 中定义的用户控制变量的值，从而驱动骨骼动画。 | `UControlRig` |
| `Get Control Float / Vector / Transform` | 读取 ControlRig 中变量的当前值。 | `UControlRig` |
| `Set Initial Transform from BP` | 在动画蓝图中设置 ControlRig 中骨骼的初始变换。 | `UControlRigComponent` |
| `Set Rig VM` | 动态切换一个 ControlRig 组件所使用的 RigVM 图表资产。 | `UControlRigComponent` |

**使用示例（动画蓝图）**：
在动画蓝图的事件图表中，通过 `Get ControlRig` 节点获取动画实例中的 ControlRig 引用，然后使用 `Set Control Float` 节点，在每帧根据游戏逻辑（如玩家输入的摇杆值）设置一个名为 `AimYaw` 的控制变量。ControlRig 图表内部会读取这个变量并驱动角色上半身的旋转。

## C++ 用法

主要通过宿主类（如 AnimInstance）访问和控制 ControlRig 实例。

### 头文件引入

```cpp
#include "ControlRig.h"
#include "Units/ControlRigUnit.h" // 若需自定义Rig单元
```

### 基本用法

在动画实例（UAnimInstance）中访问和控制 ControlRig。
（源自 `ControlRig` 模块公共 API）

```cpp
// 在 AnimInstance 子类中
void UMyAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);
    
    // 从动画实例链中获取 ControlRig 实例（假设只有一个）
    UControlRig* ControlRig = GetControlRig();
    if (ControlRig)
    {
        // 获取角色在世界空间的目标位置
        FVector TargetLocation = /* ... */;
        
        // 在 ControlRig 中设置一个名为 “TargetPos” 的向量控制
        ControlRig->SetControlValue<FVector>(FName(“TargetPos”), TargetLocation, true);
    }
}
```

### 进阶用法

在 ControlRig 图表中注册自定义的求解器或单元，扩展其底层功能。
（源自 `ControlRigDeveloper` 模块）

```cpp
// 需要自定义一个用于求解复杂IK的Rig单元
UCLASS()
class UMyCustomIKUnit : public UControlRigUnit
{
    GENERATED_BODY()
    
    virtual void Execute(const FControlRigExecuteContext& Context) override
    {
        // 在此处编写自定义的IK计算逻辑
        // 可以访问输入/输出引脚，修改骨骼变换
    }
};

// 通常需要在模块启动时注册，具体方式取决于实现
```

## 模块依赖

ControlRig 模块依赖了许多动画和核心子系统。以下是用户集成时需要注意的关键依赖：

| 模块 | 用途 |
|---|---|
| `RigVM` | ControlRig 的核心虚拟机，负责执行节点图（Rig Graph）。 |
| `AnimationCore` | 提供基础的动画数学库（如解算器、约束）。 |
| `AnimationBlueprintLibrary` | 用于在编辑器中操作动画蓝图资产。 |
| `PropertyAccess` | 支持蓝图节点中的属性绑定和访问。 |
| `SkeletalMeshDescription` | 用于处理网格体描述数据。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `7fc008ea` | AutoBake: Fix crash with using Shim track editor, need to get real one in order to cast to shared po | 修复自动烘焙功能使用垫片轨道编辑器时的崩溃问题 |
| 2026-05-26 | `0f35dc86` | Animating in Engine: Marquee selection in Animation Mode picks controls by pivot in addition to mesh | 动画模式下框选功能除了选择网格体，也能按轴心点选择控件 |
| 2026-05-22 | `c09576c8` | Control Rig: Fix older rigs not creating gizmos when controls are selected | 修复旧版绑定资产在选中控件时不创建操作手柄（Gizmo）的问题 |
| 2026-05-22 | `4eed6d63` | Control Rig: Guard against invalid instance proxy. | 增加对无效实例代理的防护 |
| 2026-05-20 | `818e65b0` | Control Rig Nullptr check for static analyzer | 为静态分析器添加空指针检查 |

### 维护评价

ControlRig 处于**活跃维护**状态。它在 2021 年从 `Engine/Plugins/Experimental` 目录迁移至正式目录，标志着其成熟稳定。从近期（2026年5月）的提交记录来看，修复工作持续进行，涵盖了崩溃修复、功能增强（如改进选择逻辑）和代码健壮性提升。作为 Unreal Engine 现代动画系统的核心支柱之一，它被 Epic Games 重度使用和维护，**强烈推荐**在项目中采用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ControlRig)
- [ControlRig 子模块文档](ControlRig.md)
- [ControlRigDeveloper 子模块文档](ControlRigDeveloper.md)
- [ControlRigEditor 子模块文档](ControlRigEditor.md)