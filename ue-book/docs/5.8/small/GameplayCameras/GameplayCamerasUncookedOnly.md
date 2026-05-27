# Gameplay Cameras

> A modular and data-driven camera system for Unreal

| 属性 | 值 |
|---|---|
| 中文名 | 游戏摄像机系统 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 是 Epic 为 Unreal Engine 设计的**下一代模块化、数据驱动摄像机系统**，旨在替代传统基于 `UCineCameraComponent` + 手动蓝图编排的方式。

该插件解决以下核心问题：

1. **数据驱动**：摄像机行为通过资产（CameraRigAsset）定义，而非硬编码，美术/策划可直接编辑
2. **模块化组合**：摄像机由多个可复用的 CameraRig 组合而成，支持参数暴露与外部数据注入
3. **蓝图深度集成**：通过 K2 蓝图节点，可在运行时动态读写 CameraRig 的暴露参数（Blendable 参数和 Data 参数）
4. **与 EnhancedInput 联动**：依赖 EnhancedInput 插件，将玩家输入映射到摄像机控制参数

目前该插件仍标记为实验性（`IsExperimentalVersion=true`），API 可能在未来版本发生变化。

## 使用场景

- 你需要一个**策划可编辑**的摄像机系统，而非在 C++ 中硬编码摄像机逻辑
- 游戏有多种摄像机模式（战斗、探索、过场），需要**模块化切换和混合**
- 需要在蓝图中**动态设置或读取**正在运行的 CameraRig 的参数
- 需要将玩家输入（摇杆、鼠标）无缝映射到摄像机旋转/缩放等参数

## 蓝图用法

当前分析的 `GameplayCamerasUncookedOnly` 模块提供了自定义 K2 蓝图节点，用于与 CameraRig 的暴露参数交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Camera Rig Parameters` | 设置指定 CameraRig 的所有暴露参数值 | `UK2Node_SetCameraRigParameters` |
| `Get Camera Rig Parameters` | 获取指定 CameraRig 的所有暴露参数值（纯函数） | `UK2Node_GetCameraRigParameters` |
| `Set Camera Rig Parameter` | 设置指定 CameraRig 的单个暴露参数值 | `UK2Node_SetCameraRigParameter` |
| `Get Camera Rig Parameter` | 获取指定 CameraRig 的单个暴露参数值（纯函数） | `UK2Node_GetCameraRigParameter` |

### 参数类型

节点支持两种参数类型：

- **Blendable 参数**（`ECameraVariableType`）：浮点、向量、旋转、颜色等可混合的值
- **Data 参数**（`ECameraContextDataType` + `ECameraContextDataContainerType`）：上下文数据，支持单值和容器类型

### 使用示例（蓝图描述）

**读写单个 CameraRig 参数：**

1. 在蓝图中搜索 "Set Camera Rig Parameter"，选择目标 CameraRig 资产
2. 节点自动暴露出该 CameraRig 定义的所有参数引脚
3. 连接目标参数的输入引脚到你的数据源（如 EnhancedInput 的轴值）
4. "Get Camera Rig Parameter" 节点可读取当前运行中的参数值

**批量读写多个参数：**

1. 使用 "Set Camera Rig Parameters" 节点，一次性设置某个 CameraRig 的全部暴露参数
2. 使用 "Get Camera Rig Parameters" 节点，一次性读取所有暴露参数
3. 这两个节点在重建时自动同步参数引脚（`ReallocatePinsDuringReconstruction`）

## C++ 用法

> **注意**：当前模块 `GameplayCamerasUncookedOnly` 主要提供蓝图编译期节点（K2Node），C++ 用法应关注 `GameplayCameras` 主运行时模块。以下示例基于公开的辅助类。

### 头文件引入

```cpp
#include "Helpers/CameraVariablePinTypeHelper.h"
#include "Helpers/CameraContextDataPinTypeHelper.h"
```

### 基本用法

根据源码中的辅助类，可以在自定义蓝图节点中创建正确的引脚类型：

```cpp
// 来源: Public/Helpers/CameraVariablePinTypeHelper.h
// 将摄像机变量类型转换为蓝图引脚类型
FEdGraphPinType PinType = UE::Cameras::FCameraVariablePinTypeHelper::GetPinType(
    ECameraVariableType::Float,  // 变量类型
    nullptr                       // Blendable 结构体类型（非结构体时为 nullptr）
);
```

```cpp
// 来源: Public/Helpers/CameraContextDataPinTypeHelper.h
// 将摄像机上下文数据类型转换为蓝图引脚类型
FEdGraphPinType PinType = UE::Cameras::FCameraContextDataPinTypeHelper::GetPinType(
    ECameraContextDataType::SomeType,           // 数据类型
    ECameraContextDataContainerType::Single,     // 容器类型
    nullptr                                      // 数据类型对象
);
```

### 进阶用法

自定义 K2 节点来操作 CameraRig 参数，基于源码中的基类继承模式：

```cpp
// 继承 UK2Node_SingleCameraRigParameterBase 来创建自定义单参数节点
UCLASS()
class UMyCustomCameraParamNode : public UK2Node_SingleCameraRigParameterBase
{
    GENERATED_BODY()
public:
    // 初始化节点，绑定到特定 CameraRig 和参数名
    void SetupNode(UCameraRigAsset* CameraRig, const FString& ParamName)
    {
        Initialize(CameraRig, ParamName, ECameraVariableType::Float, nullptr);
    }
};
```

## Demo 示例

> **注意**：`GameplayCamerasUncookedOnly` 模块的类主要是编辑器/编译期蓝图节点（`UK2Node`），不适用于运行时示例。实际使用中，开发者主要通过蓝图编辑器操作这些节点，无需编写 C++ 代码。

如需在 C++ 中创建自定义蓝图节点来操作摄像机参数，可参考以下最小示例：

```cpp
// MyCameraParamBlueprintNode.h
#pragma once

#include "BlueprintGraph/K2Node_SingleCameraRigParameterBase.h"
#include "MyCameraParamBlueprintNode.generated.h"

UCLASS(MinimalAPI)
class UMyCameraParamBlueprintNode : public UK2Node_SingleCameraRigParameterBase
{
    GENERATED_BODY()

public:
    UMyCameraParamBlueprintNode(const FObjectInitializer& ObjectInit)
        : Super(ObjectInit) {}

    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override
    {
        return NSLOCTEXT("MyNodes", "Title", "My Custom Camera Param");
    }

    virtual FText GetTooltipText() const override
    {
        return NSLOCTEXT("MyNodes", "Tooltip", "Custom node for camera param");
    }
};
```

## 模块依赖

从 `.uplugin` 的 Plugins 依赖：

| 插件/模块 | 用途 |
|---|---|
| `EnhancedInput` | 玩家输入映射到摄像机控制参数 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复 PIE 模式下摄像机变量覆盖不生效的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 更新部分 Trace 通道的描述信息 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | GameplayCameras 相关更新 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 格式化日志宏 |

### 维护评价

**活跃维护中** ✅

- **年龄**：约 6 年（2020 年创建），属于 UE5 早期就规划的核心摄像机系统
- **更新频率**：最近 1 个月内有多次提交，保持活跃更新
- **更新内容**：包含功能修复（PIE 变量覆盖）、代码质量改进（日志迁移、警告修复）
- **实验性状态**：仍标记为实验性（`IsExperimentalVersion=true`），API 可能变化
- **源码规模**：729 个源文件，属于大型插件，架构成熟

**注意事项**：
- 该插件目前仍为实验性，生产环境使用需谨慎
- 版本号为 `0.1`，表明 Epic 尚未将其标记为稳定
- 建议关注后续 UE 版本中该插件的正式发布时间

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [官方文档]()（暂无）
- [测试用例]()（待确认）