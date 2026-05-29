# VirtualCameraCore

> Code for actors, components, and utilities for controlling and viewing cameras via physical devices. See VirtualCamera for content.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟相机核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、代码） |
| 模块 | `DecoupledOutputProvider` (Runtime), `PixelStreamingVCam` (Runtime), `VCamBlueprintNodes` (Runtime), `VCamCore` (Runtime), `VCamCoreEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-18 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore) | |

## 用途
VirtualCameraCore 是 Epic Games 为虚拟制片（Virtual Production）工作流开发的核心插件。它主要解决通过物理设备（如平板电脑、手机或专用硬件）远程控制和监视虚幻引擎中虚拟相机的问题。该插件提供了底层框架，包括 Actor、组件和工具，用于接收输入、驱动相机移动和输出相机画面。其核心价值在于为虚拟相机系统提供了一个可扩展的、解耦的架构，使得不同的输入设备和输出方式（如 Pixel Streaming、直接显示）可以模块化地接入。

## 使用场景
- 你在进行虚拟制片拍摄时，希望导演或摄影师能通过 iPad 实时查看并操控场景中的虚拟相机。
- 你需要构建一个自定义的虚拟相机解决方案，要求后端（相机控制逻辑）与前端（设备显示和输入）解耦。
- 你正在开发一个通过 Pixel Streaming 向远程设备输出虚拟相机画面的系统。
- 你需要扩展虚拟相机的功能，例如添加新的输入协议或输出方式。

## 蓝图用法
本模块 (`VCamBlueprintNodes`) 主要为虚拟相机系统提供编辑器扩展，特别是为“连接”（Connections）和“连接点”（Connection Points）系统提供蓝图节点。这些节点主要用于创建动态的 switch 语句。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Switch On Widget Connections` | 根据目标 `VCamWidget` 的连接动态生成分支节点。用于在蓝图中根据 widget 的不同连接状态执行不同的逻辑。 | `UVCamK2Node_SwitchOnWidgetConnections` |
| `Switch On Modifier Connection Points` | 根据 `VCamModifier` 的连接点动态生成分支节点。用于在蓝图中根据修改器拥有的连接点执行不同的逻辑。 | `UVCamK2Node_SwitchOnModifierConnectionPoints` |

### 使用示例（蓝图描述）
1.  在蓝图编辑器中，右键点击并搜索 “Switch On Widget Connections”。
2.  将节点放置在图表中。你需要在节点的细节面板中指定一个 `Target Widget`（从当前蓝图的子 VCamWidget 中选择）。
3.  该节点会自动根据所选 widget 上可用的“连接”生成对应的输出引脚（Case 引脚）。
4.  为每个可能的连接情况（引脚）连接后续的执行逻辑。例如，当 widget 连接了 “InputAction1” 时，执行一套逻辑；当连接了 “InputAction2” 时，执行另一套逻辑。
5.  这个 switch 节点是自动更新的：如果你在目标 widget 的连接面板中添加或删除了连接，蓝图中的节点引脚会自动刷新。

## C++ 用法
本模块 (`VCamBlueprintNodes`) 主要为蓝图节点编辑器提供扩展，其核心 `UK2Node` 子类通常在 C++ 中被引擎或插件其他部分调用，而不是直接由最终用户派生。要创建自定义的 switch 节点，你需要继承自 `UVCamK2Node_SwitchConnectionSystemBase` 并实现其虚函数。

### 头文件引入
```cpp
#include "VCamBlueprintNodes.h"
// 或具体到子类
#include "SwitchNode/VCamK2Node_SwitchConnectionSystemBase.h"
```

### 基本用法
创建一个自定义的 switch 节点基类，用于处理你自己的连接系统。

```cpp
// 基于 VCamK2Node_SwitchConnectionSystemBase.h 源码推断
#pragma once
#include "K2Node_Switch.h"
#include "VCamK2Node_SwitchConnectionSystemBase.h"
#include "MyConnectionSystemNode.generated.h"

UCLASS()
class UMyConnectionSystemNode : public UVCamK2Node_SwitchConnectionSystemBase
{
	GENERATED_BODY()

protected:
	// 声明此节点支持哪个蓝图类（通常是 UVCamWidget 或 UVCamModifier 的子类）
	virtual bool SupportsBlueprintClass(UClass* Class) const override
	{
		// 仅当蓝图包含 UMyConnectionWidget 时才支持
		return Class->IsChildOf(UMyConnectionWidget::StaticClass());
	}

	// 实现获取需要生成的引脚（连接）名称的逻辑
	virtual TArray<FName> GetPinsToCreate() const override
	{
		TArray<FName> PinNames;
		// 这里应该添加获取你自定义连接系统中所有连接点的名称的逻辑
		// PinNames.Add(TEXT("ConnectionA"));
		// PinNames.Add(TEXT("ConnectionB"));
		return PinNames;
	}

	// 重写节点标题和提示文本
	virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override
	{
		return NSLOCTEXT("MyConnectionSystem", "NodeTitle", "Switch On My Connections");
	}

	virtual FText GetTooltipText() const override
	{
		return NSLOCTEXT("MyConnectionSystem", "Tooltip", "Switches based on the connections of a MyConnectionWidget.");
	}

private:
	// 访问蓝图CDO以获取连接信息的辅助方法，根据基类模式实现
	void AccessBlueprintCDO(TFunctionRef<void(UMyConnectionWidget*)> Func) const
	{
		if (UBlueprint* BP = GetBlueprint())
		{
			if (UMyConnectionWidget* CDO = Cast<UMyConnectionWidget>(BP->GeneratedClass->ClassDefaultObject))
			{
				Func(CDO);
			}
		}
	}
};
```

### 进阶用法
更复杂的用法涉及处理动态引脚的生成和同步。基类 `UVCamK2Node_SwitchConnectionSystemBase` 已经封装了大部分逻辑，子类主要关注 `SupportsBlueprintClass` 和 `GetPinsToCreate` 的实现。节点会自动监听蓝图的修改（`PostEditChangeProperty`）并调用 `RefreshPins()` 来更新引脚。

## Demo 示例
以下是一个最小化的自定义虚拟相机 switch 节点实现。

**MyConnectionSystemNode.h**
```cpp
#pragma once
#include "K2Node_Switch.h"
#include "VCamK2Node_SwitchConnectionSystemBase.h"
#include "MyConnectionSystemNode.generated.h"

class UMyConnectionWidget;

UCLASS()
class MYPROJECT_API UMyConnectionSystemNode : public UVCamK2Node_SwitchConnectionSystemBase
{
	GENERATED_BODY()

public:
	virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override;
	virtual FText GetTooltipText() const override;

protected:
	virtual bool SupportsBlueprintClass(UClass* Class) const override;
	virtual TArray<FName> GetPinsToCreate() const override;

private:
	void AccessBlueprintCDO(TFunctionRef<void(UMyConnectionWidget*)> Func) const;
};
```

**MyConnectionSystemNode.cpp**
```cpp
#include "MyConnectionSystemNode.h"
#include "MyConnectionWidget.h" // 假设的自定义Widget类
#include "K2Node.h"
#include "EdGraphSchema_K2.h"

#define LOCTEXT_NAMESPACE "MyConnectionSystemNode"

FText UMyConnectionSystemNode::GetNodeTitle(ENodeTitleType::Type TitleType) const
{
	return LOCTEXT("NodeTitle", "Switch On My Widget Connections");
}

FText UMyConnectionSystemNode::GetTooltipText() const
{
	return LOCTEXT("Tooltip", "Provides execution pins based on the active connections of a MyConnectionWidget.");
}

bool UMyConnectionSystemNode::SupportsBlueprintClass(UClass* Class) const
{
	return Class->IsChildOf(UMyConnectionWidget::StaticClass());
}

TArray<FName> UMyConnectionSystemNode::GetPinsToCreate() const
{
	TArray<FName> PinNames;
	AccessBlueprintCDO([&PinNames](UMyConnectionWidget* Widget)
	{
		if (Widget)
		{
			// 从你的Widget上获取所有连接的标识符
			// 假设 Widget->GetAllConnectionIdentifiers() 返回一个 FName 数组
			PinNames = Widget->GetAllConnectionIdentifiers();
		}
	});
	return PinNames;
}

void UMyConnectionSystemNode::AccessBlueprintCDO(TFunctionRef<void(UMyConnectionWidget*)> Func) const
{
	if (UBlueprint* BP = GetBlueprint())
	{
		if (UMyConnectionWidget* CDO = Cast<UMyConnectionWidget>(BP->GeneratedClass->ClassDefaultObject))
		{
			Func(CDO);
		}
	}
}

#undef LOCTEXT_NAMESPACE
```

## 模块依赖
使用 `VCamBlueprintNodes` 模块，你的 Build.cs 文件需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `VCamCore` | 核心虚拟相机框架，提供了 `UVCamWidget`, `UVCamModifier` 等基础类。本模块的 switch 节点是为这些核心类设计的。 |
| `KismetCompiler` | 用于蓝图编译，`UK2Node` 的标准依赖。 |
| `BlueprintGraph` | 提供蓝图图表和节点相关的编辑器类。 |

（*注意：`Core`, `CoreUObject`, `Engine`, `UnrealEd`, `Slate`, `SlateCore` 等为常见基础依赖，已省略*）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `876d5541` | Fix the crash with PIE/Simulate | 修复了在 PIE/Simulate 模式下发生的崩溃问题。 |
| 2026-05-12 | `d6533f70` | Virtual Production: Fixed warning regarding EngineAssetDefinitions plugin not being included when it | 修复了关于 EngineAssetDefinitions 插件未被包含的警告。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 将各种虚拟制片资产移动到不同的资产分类，并进行了迁移。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移为 UE_LOGF。 |
| 2026-03-09 | `8afaf39f` | Move UVPFullScreenWidget into new non-experimental plugin VirtualProduction/ViewportWidgetOverlay. | 将 UVPFullScreenWidget 移动到新的非实验性插件中。 |

### 维护评价
VirtualCameraCore 插件创建于 2024 年 1 月，目前处于 **Beta** 状态。从 git 历史来看，它仍在由 Epic Games 进行活跃维护，最近一次更新在 2026 年 5 月，修复了 PIE 崩溃问题，并且自创建以来持续有改进和重构。虽然标记为实验性/Beta，但鉴于其来自 Epic Games 并且更新持续，它对于需要虚拟相机核心功能的项目来说是 **推荐尝试使用** 的。使用者应注意其 Beta 状态，可能会存在接口变动。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore)
- [官方文档]() （暂无）
- [测试用例]() （未在提供信息中发现）