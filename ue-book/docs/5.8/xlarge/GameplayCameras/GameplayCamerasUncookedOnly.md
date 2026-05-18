# Gameplay Cameras

> A modular and data-driven camera system for Unreal（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 游戏摄像机系统 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、Camera Rig 资产） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 是 Unreal 引擎新一代模块化、数据驱动的摄像机系统，旨在替代传统的 `UCameraComponent` + `UCameraAnim` 模式。它的核心设计思想是：

1. **Camera Rig（摄像机架）**：一种资产类型，定义摄像机行为的蓝图（非 UE Blueprint，而是摄像机专用节点图），支持模块化组合和参数暴露
2. **数据驱动**：摄像机行为通过 Camera Variable（可混合变量）和 Camera Context Data（上下文数据）进行参数化，运行时可动态调整
3. **蓝图集成**：通过自定义 K2Node，蓝图可以直接读写 Camera Rig 的暴露参数，实现游戏逻辑与摄像机行为的解耦

**解决的问题**：传统 UE 摄像机系统中，复杂的摄像机动画和混合逻辑往往需要硬编码在 C++ 或冗长的蓝图中，难以复用和维护。GameplayCameras 通过资产化和参数化的方式，让摄像机设计师可以在编辑器中可视化地构建复杂摄像机行为。

## 使用场景

- 你需要一个可复用的第三人称跟随摄像机，且支持不同状态（战斗/探索/对话）的平滑切换 → 用 Camera Rig 定义各状态摄像机，通过参数控制混合
- 你需要摄像机动画（如过场、击杀特写）能在运行时动态调整角度和距离 → 用 Camera Variable 暴露可混合参数
- 你的项目有多个角色，每个角色需要略微不同的摄像机行为（如不同 FOV、臂长）→ 用参数化 Camera Rig + 蓝图设置参数
- 你需要在蓝图中实时获取/设置摄像机参数来响应游戏事件（如受伤时摄像机震动）→ 用 K2Node_GetCameraRigParameter / K2Node_SetCameraRigParameter

## 蓝图用法

本模块（GameplayCamerasUncookedOnly）提供蓝图图节点（K2Node）用于在蓝图中与 Camera Rig 交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Camera Rig Parameter` | 获取指定 Camera Rig 暴露的单个参数值 | `UK2Node_GetCameraRigParameter` |
| `Get Camera Rig Parameters` | 获取指定 Camera Rig 的所有暴露参数值 | `UK2Node_GetCameraRigParameters` |
| `Set Camera Rig Parameter` | 设置指定 Camera Rig 的单个暴露参数值 | `UK2Node_SetCameraRigParameter` |
| `Set Camera Rig Parameters` | 设置指定 Camera Rig 的所有暴露参数值 | `UK2Node_SetCameraRigParameters` |

### 节点说明

**Get Camera Rig Parameter（纯函数节点）**
- 纯函数（`IsNodePure() = true`），无执行引脚，可直接连接到数据引脚
- 从指定的 Camera Rig 资产中读取一个暴露参数的当前值
- 参数类型自动匹配：根据 Camera Variable 类型（Float、Rotator 等）或 Camera Context Data 类型自动设置输出引脚类型

**Get Camera Rig Parameters（纯函数节点）**
- 一次性读取 Camera Rig 上所有暴露的参数
- 输出引脚包括所有 Blendable 参数和 Data 参数

**Set Camera Rig Parameter（执行节点）**
- 需要执行引脚
- 设置运行中 Camera Rig 的某个暴露参数值
- 设置的值会影响正在使用该 Camera Rig 的摄像机组件

**Set Camera Rig Parameters（执行节点）**
- 一次性设置所有暴露参数
- 需要在重建期间重新分配引脚（`ReallocatePinsDuringReconstruction`）

### 使用示例（蓝图描述）

**场景：动态调整摄像机臂长**

1. 创建一个 Camera Rig 资产，定义第三人称摄像机，在其中暴露一个 Float 类型的 Blendable 参数 "ArmLength"
2. 在蓝图中使用 `Set Camera Rig Parameter` 节点：
   - Camera Rig Pin → 引用你的 Camera Rig 资产
   - 参数下拉选择 "ArmLength"
   - Value Pin → 连接一个 Float 变量（如根据角色速度动态计算的臂长）
3. 在 Tick 事件中调用该节点，摄像机臂长会随游戏逻辑实时变化

**场景：读取摄像机当前状态**

1. 在蓝图中使用 `Get Camera Rig Parameter` 节点（纯函数，可在任何地方使用）
2. 选择 Camera Rig 和参数名
3. 输出 Pin 自动匹配参数类型，可直接连接到 Print String 或其他逻辑

## C++ 用法

本模块主要提供蓝图图节点基础设施，C++ 使用场景较少。以下是相关的类型系统 API：

### 头文件引入

```cpp
#include "Helpers/CameraContextDataPinTypeHelper.h"
#include "Helpers/CameraVariablePinTypeHelper.h"
```

### 基本用法

**获取 Camera Variable 对应的蓝图引脚类型**

```cpp
#include "Helpers/CameraVariablePinTypeHelper.h"

// 根据 Camera Variable 类型获取对应的 EdGraph 引脚类型
// 用于在自定义 K2Node 中创建参数引脚
FEdGraphPinType PinType = UE::Cameras::FCameraVariablePinTypeHelper::GetPinType(
    ECameraVariableType::Float,           // 变量类型
    nullptr                                // Blendable Struct 类型（如果变量类型是 Struct）
);
```

**获取 Camera Context Data 对应的蓝图引脚类型**

```cpp
#include "Helpers/CameraContextDataPinTypeHelper.h"

// 根据上下文数据类型获取对应的 EdGraph 引脚类型
FEdGraphPinType PinType = UE::Cameras::FCameraContextDataPinTypeHelper::GetPinType(
    ECameraContextDataType::Object,                        // 数据类型
    ECameraContextDataContainerType::Single,               // 容器类型（单值）
    UMyActor::StaticClass()                                 // 类型对象（对于 UObject 类型）
);
```

### 进阶用法

**自定义 Camera Rig 参数节点的引脚类型推断**

在 `UK2Node_CameraRigBase` 基类中，提供了静态方法用于根据参数元数据创建正确的引脚类型：

```cpp
// 根据 Blendable 参数元数据创建引脚类型
FEdGraphPinType BlendablePinType = UK2Node_CameraRigBase::MakeBlendableParameterPinType(
    BlendableParameter  // UCameraObjectInterfaceBlendableParameter*
);

// 根据 Data 参数元数据创建引脚类型
FEdGraphPinType DataPinType = UK2Node_CameraRigBase::MakeDataParameterPinType(
    DataParameter       // UCameraObjectInterfaceDataParameter*
);

// 也可以直接使用枚举值
FEdGraphPinType PinType = UK2Node_CameraRigBase::MakeBlendableParameterPinType(
    ECameraVariableType::Rotator,
    nullptr
);
```

**在编译期间验证 Camera Rig**

```cpp
// K2Node_CameraRigBase 提供了编译期验证方法
// 在 ExpandNode 中调用，确保 Camera Rig 资产有效
bool bValid = ValidateCameraRigBeforeExpandNode(CompilerContext);
if (!bValid)
{
    // 编译器会自动输出错误信息
    return;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayCameras` | 核心摄像机运行时模块，提供 CameraRig 资产、变量表、上下文数据表等基础类型 |

## 维护状态

### 近期更新

```
- 2026-04-14 35e60df1 Migrate UE_LOG to UE_LOGF（日志宏迁移）
- 2026-04-13 6f1ea925 State Tree: Updated state tree reference struct details（关联模块更新）
- 2026-04-08 81eea83d [ContentBrowser] New Add Menu Gameplay Menu（编辑器集成改进）
- 2026-03-03 76a32825 [PostProcessing] Replace FilmGrainTexelSize with float2 FilmGrainScale
- 2026-03-03 ea1a72ff Cameras: make playback mode only affect whether a GPC component writes to the output component
```

### 维护评价

- **活跃维护** ✅：创建于 2026-03-03，至今约 1 个月，已有多次更新
- **实验性插件** ⚠️：`IsExperimentalVersion=true`，API 可能会发生变化
- **版本号 0.1**：明确处于早期开发阶段
- **Epic 官方维护**：由 Epic Games 直接开发和维护
- **依赖 EnhancedInput**：使用了新一代输入系统，表明其现代化设计取向
- **推荐使用**：适合新项目采用，但需要注意 API 可能变化；生产项目建议等待正式版

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [官方文档]()（暂无）

---

> **文档版本说明**：本文档基于 GameplayCamerasUncookedOnly 模块的源码编写。GameplayCameras 是一个大型插件（729 个源文件），完整文档请参阅各子模块文档：
>
> - `GameplayCameras`（Runtime）— 核心摄像机系统，包含 Camera Rig 资产、摄像机求值器、变量表等
> - `GameplayCamerasEditor`（Editor）— 编辑器工具，包含 Camera Rig 编辑器、节点图编辑器等
> - `GameplayCamerasUncookedOnly`（UncookedOnly）— 蓝图图节点（本文档）