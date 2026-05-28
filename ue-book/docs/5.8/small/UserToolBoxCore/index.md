# UserToolBoxCore

> Core functionnality to create custom editor tab（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 用户工具箱核心 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UserToolBoxCore` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-18 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UserToolBoxCore) | |

## 用途

UserToolBoxCore 是一个用于在虚幻编辑器中创建**可配置的自定义工具箱标签页**的实验性框架。它解决的核心问题是：如何让开发者（包括蓝图开发者）能够快速、可定制地将一系列常用工具（“命令”）组织成一个可停靠的编辑器面板。

这个插件的价值在于它提供了一个完整的、可序列化的资产系统（`UUserToolBoxBaseTab`）和运行时的子系统（`UUserToolboxSubsystem`）来管理这些标签页。用户可以创建命令，将它们分组到不同的“节”中，并选择不同的UI布局模板（如工具栏、垂直列表等），从而无需编写大量重复的UI代码即可构建出功能丰富的自定义编辑器工具集。

## 使用场景

- **你是一个技术美术或工具程序员**，需要为团队创建一个包含“批量重命名资产”、“清理材质参数”、“自动生成LOD”等一系列常用工具的快捷面板，不想为每个工具都创建一个独立的编辑器模块。
- **你正在开发一个编辑器插件**，希望为用户提供一个可扩展、可配置的界面来暴露自定义功能，让用户自己决定工具的排列和组合。
- **你需要快速原型化编辑器工具**，利用蓝图实现的命令可以快速迭代，而无需重新编译C++。

## 蓝图用法

该插件的核心蓝图交互通过 `UUserToolboxSubsystem` 编辑器子系统和 `UUserToolBoxBaseCommand` 基类进行。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Register Tab Data` | 初始化并注册所有可用的工具箱标签页资产，通常在编辑器启动时调用。 | `UUserToolboxSubsystem` |
| `Get Available Tab List` | 获取所有已注册的 `UUserToolBoxBaseTab` 资产数据。 | `UUserToolboxSubsystem` |
| `Pick an Icon` | 弹出一个图标选择对话框，返回所选图标的路径。 | `UUserToolboxSubsystem` |
| `Refresh Icons` | 刷新图标缓存列表，通常在图标资产改变后调用。 | `UUserToolboxSubsystem` |

**创建自定义命令（蓝图）**：
1.  右键在内容浏览器中，选择 **蓝图类**。
2.  在父类选择窗口中，搜索并选择 `UserToolBoxBaseBlueprint`。
3.  在新创建的蓝图中，重写 `Command` 事件。这是命令被点击时执行的核心逻辑。

### 使用示例（蓝图描述）

1.  **创建命令蓝图**：创建一个继承自 `UserToolBoxBaseBlueprint` 的蓝图类 `BP_MyCommand`。在事件图表中，重写 `Command` 事件，并连接你的业务逻辑节点（例如，选择所有静态网格体）。
2.  **创建工具箱资产**：在内容浏览器中右键，选择 **杂项** -> **用户工具箱标签页**，创建一个 `UUserToolBoxBaseTab` 资产（例如 `MyTools`）。
3.  **配置标签页**：打开 `MyTools` 资产。在“命令标签页”类别下，你可以设置标签页名称、UI模板（如 `ToolbarTabUI` 代表工具栏样式）。
4.  **添加命令**：在资产的 `Sections` 数组中添加一个 `UUTBTabSection`，设置 `SectionName`（如“常用操作”）。将 `BP_MyCommand` 拖入该节的 `Commands` 数组中。
5.  **使用**：在编辑器主菜单的“窗口”下拉菜单中，应该能找到你的“MyTools”标签页，点击即可打开包含你命令的工具面板。

## C++ 用法

主要面向需要创建**C++实现**的高性能自定义命令，或需要深度定制标签页行为的开发者。

### 头文件引入

```cpp
#include "UTBBaseCommand.h"
#include "UTBBaseTab.h"
#include "UserToolBoxSubsystem.h"
```

### 基本用法

创建一个简单的自定义命令。

```cpp
// MyCleanupCommand.h
#pragma once
#include "UTBBaseCommand.h"
#include "MyCleanupCommand.generated.h"

UCLASS(Blueprintable)
class UMyCleanupCommand : public UUTBBaseCommand
{
	GENERATED_BODY()

public:
	UMyCleanupCommand();

	virtual void Execute() override;
};

// MyCleanupCommand.cpp
#include "MyCleanupCommand.h"
#include "Editor.h" // For FScopedTransaction

UMyCleanupCommand::UMyCleanupCommand()
{
	Name = TEXT("清理未使用资产");
	Tooltip = TEXT("检查并提示清理项目中未引用的资产");
	Category = TEXT("资产管理");
}

void UMyCleanupCommand::Execute()
{
	// 开启一个撤销事务，使此操作可撤销
	FScopedTransaction Transaction(NSLOCTEXT("MyPlugin", "CleanupUnusedAssets", "清理未使用资产"));

	// 在此处实现具体的清理逻辑...
	// 例如，扫描资产注册表，找到未引用的资产并提示用户
}
```
*来源参考: `UTBBaseCommand.h` 中的 `Execute()` 和事务相关函数*

### 进阶用法

创建自定义的UI模板和使用子系统生成UI。

```cpp
// 假设我们创建了一个自定义的UI模板类
#include "UTBBaseUITab.h"

UCLASS()
class UMyCustomTabUITemplate : public UUTBDefaultUITemplate
{
	GENERATED_BODY()
public:
	virtual TSharedPtr<SWidget> BuildTabUI(UUserToolBoxBaseTab* Tab, const FUITemplateParameters& Params) override;
};

// 在某个编辑器工具或菜单命令中，手动生成一个标签页的UI
void FMyEditorModule::OpenCustomToolbox()
{
	// 获取编辑器子系统
	UUserToolboxSubsystem* ToolboxSubsystem = GEditor->GetEditorSubsystem<UUserToolboxSubsystem>();
	if (ToolboxSubsystem)
	{
		// 假设我们有一个名为“MyAdvancedTools”的Tab资产数据
		FAssetData TabAssetData = /* 通过资产注册表找到 */;
		// 使用自定义的UI模板生成UI
		TSharedPtr<SWidget> ToolboxUI = ToolboxSubsystem->GenerateTabUI(TabAssetData, UMyCustomTabUITemplate::StaticClass());
		// 将这个UI添加到你想要的地方，例如一个SDockTab
	}
}
```
*来源参考: `UserToolBoxSubsystem.h` 中的 `GenerateTabUI` 函数和 `UTBBaseUITab.h` 中的模板类结构*

## Demo 示例

一个最小的可编译C++自定义命令示例。

```cpp
// SimpleRotateCommand.h
#pragma once

#include "CoreMinimal.h"
#include "UTBBaseCommand.h"
#include "SimpleRotateCommand.generated.h"

UCLASS(Blueprintable)
class USimpleRotateCommand : public UUTBBaseCommand
{
	GENERATED_BODY()

public:
	USimpleRotateCommand();

	virtual void Execute() override;
};
```

```cpp
// SimpleRotateCommand.cpp
#include "SimpleRotateCommand.h"
#include "Editor.h"
#include "Engine/Selection.h"
#include "GameFramework/Actor.h"

USimpleRotateCommand::USimpleRotateCommand()
{
	Name = TEXT("旋转90度");
	Tooltip = TEXT("将选中的Actors绕Z轴旋转90度");
	Category = TEXT("变换");
	IconPath = TEXT("EditorStyle|Icons.Rotate90");
}

void USimpleRotateCommand::Execute()
{
	// 开启一个撤销事务
	FScopedTransaction Transaction(NSLOCTEXT("SimpleRotate", "RotateActors", "旋转选中Actors"));

	USelection* SelectedActors = GEditor->GetSelectedActors();
	for (FSelectionIterator It(*SelectedActors); It; ++It)
	{
		AActor* Actor = Cast<AActor>(*It);
		if (Actor)
		{
			Actor->Modify(); // 标记Actor已修改以支持撤销
			FRotator NewRotation = Actor->GetActorRotation();
			NewRotation.Yaw += 90.0f;
			Actor->SetActorRotation(NewRotation);
		}
	}
}
```

## 模块依赖

从 `Build.cs` 分析，该插件的独特依赖如下。

| 模块 | 用途 |
|---|---|
| `SlateScripting` | 提供Slate的脚本化支持，用于插件中的某些UI交互或扩展。 |

其余依赖为 `Editor`、`UnrealEd`、`Slate`、`SlateCore`、`InputCore`、`UMG`、`Kismet`、`ToolWidgets` 等编辑器和UI相关常见模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量转换为浮点数时产生的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件内的日志输出从 `UE_LOG` 迁移为 `UE_LOGF`。 |
| 2026-03-17 | `d3ddc7a1` | UserToolbox - Icon creation crashes engine | 修复了图标创建功能导致引擎崩溃的严重bug。 |
| 2025-09-16 | `7b6911d5` | restore UserToolBoxTab | 恢复了某个与 `UserToolBoxTab` 相关的功能或资产。 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 将引擎中（包括本插件）的 `IsValid(this)` 调用替换为更安全的方式。 |

### 维护评价

该插件创建于2023年初，至今约3年，属于较新的实验性插件。从提交历史看，最近一年（2025-2026）仍有零星的更新，主要集中在**编译警告修复、日志规范、以及关键的稳定性bug修复（如图标崩溃）**，没有看到大的新功能添加。

**综合评价**：
- **维护状态**：**低活跃度维护**。更新频率低，且多为技术债务清理和bug修复。
- **推荐度**：作为 `Experimental`（实验性）插件，其API和功能集可能不完整且未来有变更风险。它提供了一个有价值的概念验证和框架。如果你需要快速搭建编辑器工具原型，并且能接受其不稳定性，可以尝试使用。对于生产环境，建议等待其脱离实验状态，或评估其核心设计思想后自行构建更稳定的实现。

**警告**：该插件为实验性 (`IsExperimentalVersion`)，默认未启用 (`EnabledByDefault=false`)。请在项目设置中手动启用后方可使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UserToolBoxCore)
- [官方文档]()（无）