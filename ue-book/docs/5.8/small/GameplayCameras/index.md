# Gameplay Cameras

> A modular and data-driven camera system for Unreal

| 属性 | 值 |
|---|---|
| 中文名 | 游戏摄像机 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（摄像机资产、蓝图行为） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 是一个**模块化、数据驱动**的摄像机系统框架。它旨在取代或扩展传统的基于`APlayerCameraManager`和`UCameraComponent`的摄像机系统，通过“摄像机资产（Camera Asset）”和“蓝图行为节点（Camera Node）”来定义摄像机逻辑。

**它解决的核心问题**是：传统摄像机系统的逻辑与代码耦合紧密，难以复用、迭代和维护。策划人员难以通过数据和蓝图直接控制复杂的摄像机行为。此插件将摄像机行为抽象为可组合、可复用的数据资产，允许开发者和策划通过蓝图和资产创建复杂的摄像机逻辑，无需编写（或仅需少量）C++代码。

## 使用场景

- 你需要一个复杂、可重复使用的摄像机系统（例如第三人称、过场动画、驾驶摄像机），而不是在多个地方编写独立的摄像机逻辑。
- 你的项目需要策划和程序紧密协作，策划人员希望能通过蓝图或资产快速原型化和调整摄像机行为。
- 你希望摄像机行为能够被资产化管理，方便在不同角色或不同游戏模式间共享和修改。
- 你正在构建一个需要高度定制和复杂摄像机逻辑（如多目标混合、动态轨迹）的游戏。

## 蓝图用法

该系统的核心是通过蓝图行为和资产进行驱动。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Camera System` | 在指定的摄像机系统组件上启动一个摄像机资产。 | `UCameraSystemComponent` |
| `Camera System Component` | 挂载在角色（Pawn）上，负责管理摄像机资产的生命周期和更新。 | `UCameraSystemComponent` |

### 使用示例（蓝图描述）

1.  在你的`Pawn`或`Character`蓝图中，添加一个 `UCameraSystemComponent`。
2.  创建一个“摄像机资产”（例如 `UPawnCameraAsset`）。
3.  在 `BeginPlay` 事件中，调用 `Start Camera System` 节点，将你的摄像机资产和 `Camera System Component` 连接起来。
4.  系统将根据资产中定义的蓝图节点树自动更新摄像机。

## C++ 用法

核心扩展点是通过 C++ 创建自定义的摄像机节点。

### 头文件引入

```cpp
#include “GameplayCameras.h”
#include “GameplayCameraComponent.h”
```

### 基本用法

（基于常见用法模式）
```cpp
// 在你的角色类中
UPROPERTY(VisibleAnywhere)
TObjectPtr<UCameraSystemComponent> CameraSystem;

// 初始化
CameraSystem = CreateDefaultSubobject<UCameraSystemComponent>(TEXT(“CameraSystem”));

// 在开始游戏时启动一个摄像机资产
void AYourCharacter::BeginPlay()
{
    Super::BeginPlay();
    if (CameraSystem && YourCameraAsset)
    {
        CameraSystem->StartCameraSystem(YourCameraAsset);
    }
}
```

### 进阶用法

创建自定义摄像机节点需要继承 `UCameraNode` 并重写 `OnRun` 等函数，这通常用于实现插件未提供的特定摄像机行为。

## Demo 示例

由于此插件规模庞大且功能通过资产驱动，完整的最小示例通常涉及创建蓝图资产。一个基础的 C++ 角色设置如上所示，配合一个通过编辑器创建的 `CameraAsset` 即可运行。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 集成，用于基于增强输入的摄像机输入处理 |
| `GameplayAbilities` | 集成，支持与 Gameplay Ability System 联动的摄像机效果 |
| `ControlRig` | 集成，支持在摄像机节点中使用 Control Rig 进行程序化动画 |
| `LiveLinkInterface` | 集成，支持从 Live Link 驱动摄像机数据 |
| `ModularGameplay` | 集成，支持模块化 Gameplay 特性 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复在 PIE 模式下摄像机变量覆盖失效的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译器警告 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 为一些跟踪通道添加或更新描述 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | （无具体说明的提交，可能是小调整或合并） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移至 UE_LOGF 宏 |

### 维护评价

GameplayCameras 虽然创建于约 6 年前，但**仍处于活跃维护中**。最近的提交记录显示，Epic 团队在 2026 年持续对其进行 bug 修复（如修复 PIE 变量覆盖）和代码质量改进（如修复编译警告、日志宏迁移）。其标记为 `IsExperimentalVersion` 表明 API 可能尚未完全稳定，但功能已相当完备。它是一个庞大且复杂的基础系统，适合作为长期项目的核心摄像机组件，但使用者需要预期可能遇到实验性 API 的变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [官方文档]() （暂无）

---
**注意**：本文档为大型插件 GameplayCameras 的**索引汇总页**。由于其源码文件超过 500 个，已被归类为 `large` 杯型。详细的模块文档、API 说明和高级用法，请参阅各子模块文档：
- [GameplayCameras (Runtime) 模块](GameplayCameras.md)
- [GameplayCamerasEditor (Editor) 模块](GameplayCamerasEditor.md)
- [GameplayCamerasUncookedOnly (UncookedOnly) 模块](GameplayCamerasUncookedOnly.md)