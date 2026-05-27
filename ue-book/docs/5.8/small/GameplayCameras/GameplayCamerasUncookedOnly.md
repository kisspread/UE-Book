# Gameplay Cameras

> A modular and data-driven camera system for Unreal

| 属性 | 值 |
|---|---|
| 中文名 | 游戏摄像机系统 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、摄像机配置） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 是一个模块化、数据驱动的摄像机系统，旨在替代或补充 UE 传统的 `UCameraComponent` 和 `APlayerCameraManager` 摄像机逻辑。它解决了传统摄像机系统中逻辑与数据耦合紧密、难以复用和共享摄像机行为的问题。

该插件的核心思想是将摄像机的“行为”（如移动规则、参数混合）抽象为可配置的 **摄像机逻辑（Camera Rig）资产**，并通过蓝图节点在运行时动态组合、设置参数。这允许设计师在编辑器中创建和调整摄像机行为，而无需修改 C++ 代码，实现了摄像机逻辑的高度可配置性和可复用性。

## 使用场景

-   **第三人称游戏**：需要平滑、可配置的跟随摄像机，其行为（如弹簧臂长度、偏移、碰撞）可以按场景或游戏状态动态调整。
-   **电影化或预设镜头**：需要在过场动画或特定游戏事件中切换到预设的、带有复杂运动规则的摄像机，并可通过参数微调。
-   **需要高度定制化摄像机行为的游戏**：当基础的 `UCameraComponent` 无法满足需求，且希望将定制逻辑资产化以便于复用和团队协作时。
-   **蓝图驱动的游戏开发**：团队主要使用蓝图进行开发，需要一套完整的蓝图节点来创建和控制摄像机。

## 蓝图用法

GameplayCameras 通过自定义蓝图节点（K2Node）暴露其核心功能，允许在蓝图中直接操作摄像机逻辑资产的参数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Camera Rig Parameters` | 给定一个摄像机逻辑资产（Camera Rig），设置其所有暴露参数的运行时值。正在使用该逻辑数据进行评估的摄像机将应用这些值。 | `UK2Node_SetCameraRigParameters` |
| `Get Camera Rig Parameters` | 给定一个摄像机逻辑资产，获取其所有暴露参数的当前运行时值。 | `UK2Node_GetCameraRigParameters` |
| `Set Camera Rig Parameter` | 给定一个摄像机逻辑资产，设置其中一个特定暴露参数的运行时值。 | `UK2Node_SetCameraRigParameter` |
| `Get Camera Rig Parameter` | 给定一个摄像机逻辑资产，获取其中一个特定暴露参数的当前运行时值。 | `UK2Node_GetCameraRigParameter` |

### 使用示例（蓝图描述）

1.  **设置参数**：在事件图表中，从一个 `Camera Rig` 资产变量（如 `MyFollowCameraRig`）连出引线，到 `Set Camera Rig Parameter` 节点的 “Camera Rig” 引脚。在节点的参数下拉列表中选择一个已暴露的参数（如 “ArmLength”），然后将一个浮点数变量连入其 “Value” 引脚。
2.  **获取参数**：使用 `Get Camera Rig Parameter` 节点，以类似方式连接资产并选择参数，其输出引脚将提供该参数的当前值，可用于逻辑判断。

## C++ 用法

此插件的 Runtime 模块提供了底层的 C++ API，但对于 `GameplayCamerasUncookedOnly` 模块，其主要功能是为编辑器中的蓝图图提供支持，C++ 用法侧重于扩展编辑器。

### 头文件引入

```cpp
// 对于蓝图图相关的扩展，通常需要包含编辑器相关头文件
#include "GameplayCamerasUncookedOnlyModule.h"
```

### 基本用法

该模块的核心是蓝图节点的定义。以下示例展示了如何基于 `UK2Node_CameraRigBase` 创建一个自定义的蓝图节点，用于查询特定摄像机逻辑资产的状态（非官方示例，基于代码结构推断）。

```cpp
// MyCustomCameraRigNode.h
#include "K2Node_CameraRigBase.h"

UCLASS(MinimalAPI)
class UK2Node_GetMyCameraRigStatus : public UK2Node_CameraRigBase
{
	GENERATED_BODY()

public:
	// 实现 UEdGraphNode 接口
	virtual void AllocateDefaultPins() override;
	virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override;
	virtual FText GetTooltipText() const override;
	virtual bool IsNodePure() const override { return true; }
	virtual void ExpandNode(class FKismetCompilerContext& CompilerContext, UEdGraph* SourceGraph) override;

protected:
	// 实现 UK2Node_CameraRigBase 接口
	virtual void GetMenuActions(FBlueprintActionDatabaseRegistrar& ActionRegistrar, const FAssetData& CameraRigAssetData) const override;
};
```
*（来源：基于 `Private/BlueprintGraph/K2Node_GetCameraRigParameter.h` 结构推断）*

### 进阶用法

通过 `FCameraVariablePinTypeHelper` 和 `FCameraContextDataPinTypeHelper` 辅助类，可以正确地为不同类型的摄像机变量和上下文数据创建对应的蓝图图引脚类型。

```cpp
#include "Helpers/CameraVariablePinTypeHelper.h"
#include "Helpers/CameraContextDataPinTypeHelper.h"

void UK2Node_GetMyCameraRigStatus::AllocateDefaultPins()
{
    Super::AllocateDefaultPins();

    // 根据摄像机变量类型创建引脚
    FEdGraphPinType FloatPinType = UE::Cameras::FCameraVariablePinTypeHelper::GetPinType(
        ECameraVariableType::Float, /* BlendableStructType */ nullptr);
    CreatePin(EGPD_Output, FloatPinType, TEXT("CurrentBlendWeight"));

    // 根据上下文数据类型创建引脚
    FEdGraphPinType ObjectPinType = UE::Cameras::FCameraContextDataPinTypeHelper::GetPinType(
        ECameraContextDataType::Object, ECameraContextDataContainerType::None, /* DataTypeObject */ AActor::StaticClass());
    CreatePin(EGPD_Output, ObjectPinType, TEXT("TargetActor"));
}
```
*（来源：基于 `Public/Helpers/CameraVariablePinTypeHelper.h` 和 `Public/Helpers/CameraContextDataPinTypeHelper.h`）*

## Demo 示例

以下是一个最小化的自定义蓝图节点实现，该节点从指定的摄像机逻辑资产中获取一个浮点型混合参数的当前值。

```cpp
// MyGetBlendableParameterNode.h
#pragma once
#include "K2Node_SingleCameraRigParameterBase.h"
#include "MyGetBlendableParameterNode.generated.h"

UCLASS(MinimalAPI)
class UK2Node_GetBlendableParameter : public UK2Node_SingleCameraRigParameterBase
{
	GENERATED_BODY()
public:
	virtual void AllocateDefaultPins() override;
	virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override;
	virtual FText GetTooltipText() const override;
	virtual bool IsNodePure() const override { return true; }
	virtual void ExpandNode(class FKismetCompilerContext& CompilerContext, UEdGraph* SourceGraph) override;
protected:
	virtual void GetMenuActions(FBlueprintActionDatabaseRegistrar& ActionRegistrar, const FAssetData& CameraRigAssetData) const override;
};
```

```cpp
// MyGetBlendableParameterNode.cpp
#include "MyGetBlendableParameterNode.h"
#include "CameraRigAsset.h"
#include "BlueprintActionDatabaseRegistrar.h"
#include "BlueprintNodeSpawner.h"

#define LOCTEXT_NAMESPACE "MyGetBlendableParameterNode"

void UK2Node_GetBlendableParameter::AllocateDefaultPins()
{
	// 创建输出引脚，类型基于已存储的参数信息
	FEdGraphPinType OutputPinType = GetParameterPinType();
	CreatePin(EGPD_Output, OutputPinType, TEXT("Value"));

	// 基类会处理“Camera Rig”输入引脚和“Evaluation Result”输出引脚的创建
	Super::AllocateDefaultPins();
}

FText UK2Node_GetBlendableParameter::GetNodeTitle(ENodeTitleType::Type TitleType) const
{
	return LOCTEXT("NodeTitle", "Get Camera Rig Blendable Parameter");
}

FText UK2Node_GetBlendableParameter::GetTooltipText() const
{
	return LOCTEXT("NodeTooltip", "Gets the current runtime value of a specific blendable parameter from a Camera Rig asset.");
}

void UK2Node_GetBlendableParameter::ExpandNode(class FKismetCompilerContext& CompilerContext, UEdGraph* SourceGraph)
{
	// 扩展节点，生成实际的蓝图逻辑。
	// 这里通常会生成调用某个函数库的蓝图节点，该函数库负责根据资产和参数名查询值。
	Super::ExpandNode(CompilerContext, SourceGraph);
	// ... 具体的展开逻辑，参考UK2Node_GetCameraRigParameter
}

void UK2Node_GetBlendableParameter::GetMenuActions(FBlueprintActionDatabaseRegistrar& ActionRegistrar, const FAssetData& CameraRigAssetData) const
{
	// 仅当资产包含可以操作的混合参数时，才在菜单中注册此节点。
	if (CameraRigAssetData.IsValid())
	{
		UClass* ActionKey = GetClass();
		if (ActionRegistrar.IsOpenForRegistration(ActionKey))
		{
			// 根据资产内的参数动态生成菜单项
			// ... 具体逻辑
		}
	}
}

#undef LOCTEXT_NAMESPACE
```
*（参考来源：`Private/BlueprintGraph/K2Node_GetCameraRigParameter.h` 与 `K2Node_SingleCameraRigParameterBase.h`）*

## 模块依赖

使用 `GameplayCameras` 插件，你的模块通常需要依赖其运行时模块。具体依赖关系请查阅各模块的 `Build.cs` 文件。

| 模块 | 用途 |
|---|---|
| `GameplayCameras` | 核心运行时模块，提供摄像机逻辑资产、评估器等基础功能 |
| `EnhancedInput` | 输入系统插件，用于处理摄像机相关的输入操作 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复在 PIE 中摄像机变量覆盖不生效的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 为一些追踪通道添加或更新描述信息 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | 插件相关的通用提交（可能为合并或小范围修复） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏 `UE_LOG` 迁移为新版 `UE_LOGF` |

### 维护评价

该插件处于**积极维护**状态。尽管标记为实验性版本（IsExperimentalVersion=true），但从近期的提交记录看，Epic 团队仍在持续修复 Bug、优化代码（如日志迁移、编译警告修复）和处理特定场景问题（如 PIE 修复）。作为 Epic 官方推出的摄像机解决方案，它在未来 UE 版本中很可能会成为主流或得到进一步完善。当前推荐在新项目中谨慎试用，以评估其稳定性和是否符合项目需求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [官方文档](https://docs.unrealengine.com/)（暂无特定文档，需查阅引擎通用摄像机文档或社区资源）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/GameplayCameras)