# UserToolBoxCore

> Core functionnality to create custom editor tab

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

UserToolBoxCore 是一个用于创建可配置编辑器选项卡的实验性框架。它解决的问题是：让开发者能够在编辑器中快速构建自定义的工具面板，将常用的操作、命令、工具以可视化的方式组织在选项卡中，从而提升工作效率。

**核心功能**：
1.  **可配置的选项卡**：通过资产（UUserToolBoxBaseTab）定义选项卡的结构和内容。
2.  **分段与命令**：选项卡包含多个“分段”（Section），每个分段包含一系列“命令”（Command）。
3.  **命令框架**：提供了命令的基类（UUTBBaseCommand），支持定义命令的名称、图标、快捷键等属性，并执行具体操作。
4.  **灵活的 UI**：支持多种预设的 UI 模板（如工具栏、调色板、垂直工具栏），也允许通过接口或蓝图自定义单个命令的 UI。
5.  **编辑器集成**：提供了专门的资产编辑器（FUTBTabEditor）和子系统（UUserToolboxSubsystem）来管理和展示这些自定义选项卡。

它不仅仅是一个简单的 UI 容器，而是一个完整的、可扩展的“命令容器”框架，将命令的定义、UI 表现和执行逻辑解耦。

## 使用场景

*   **自定义工作流工具栏**：如果你是关卡设计师，经常需要执行一系列固定的 Actor 操作（如对齐、复制、特定设置），可以创建一个“关卡设计工具箱”选项卡，将这些操作封装为命令按钮。
*   **美术资产批处理**：如果你是技术美术，需要对资产进行批量修改或检查，可以创建一个“资产批处理工具”选项卡，集成各种自定义的检查和处理脚本。
*   **蓝图开发辅助**：如果你是蓝图开发者，可以将常用的调试节点、工具宏、节点模板等封装为命令，通过自定义选项卡快速调用。
*   **团队自定义工具发布**：项目组可以开发一套通用的 UserToolBoxCore 命令和 UI 模板，以资产的形式分发，团队成员可以自行拖拽组合，创建符合自己习惯的工具面板。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterTabData` | 注册当前可用的工具箱选项卡数据，刷新子系统列表 | `UUserToolboxSubsystem` |
| `GetAvailableTabList` | 获取所有已注册的可用工具箱选项卡资产列表 | `UUserToolboxSubsystem` |
| `PickAnIcon` | 弹出一个图标选择对话框，返回选中的图标路径 | `UUserToolboxSubsystem` |
| `RefreshIcons` | 刷新外部图标样式的注册 | `UUserToolboxSubsystem` |
| `GetBrushById` | 根据名称（ID）获取一个 Slate 画刷（Brush） | `UUserToolBoxFunctionLibrary` |
| `GetAllSlateStyle` | 获取所有可用的 Slate 样式集名称 | `UUserToolBoxFunctionLibrary` |
| `GetBrushByStyleAndId` | 根据样式集名称和画刷ID获取一个 Slate 画刷 | `UUserToolBoxFunctionLibrary` |
| `ExecuteCommand` | （在命令UI中）执行当前命令关联的操作 | `UUTBCommandUMGUI` |

### 使用示例（蓝图描述）

1.  **创建自定义命令（蓝图实现）**:
    *   创建一个新的蓝图类，父类选择 `UserToolBoxBaseBlueprint`。
    *   在蓝图中，重写 `Command` 事件（Blueprint Implementable Event），编写你希望这个命令执行的逻辑。
    *   为这个蓝图资产设置 `Name`, `IconPath` 等属性。

2.  **配置工具箱选项卡资产**:
    *   在内容浏览器中右键 -> User Toolbox -> User Toolbox Tab，创建一个 `UUserToolBoxBaseTab` 资产。
    *   打开该资产，设置 `Name`。
    *   在 `Sections` 数组中添加分段。
    *   在某个分段的 `Commands` 数组中，将你之前创建的命令蓝图类的实例（对象）拖拽进去。
    *   根据需要调整 `TabUI` 选择不同的 UI 模板（如 `UTBToolBarTabUI`）。

3.  **在编辑器中使用**:
    *   `UUserToolboxSubsystem` 会自动管理这些资产。在“窗口”菜单或视口覆盖层中（取决于选项卡资产的可见性设置 `bIsVisibleInWindowsMenu`, `bIsVisibleInViewportOverlay`）找到你的自定义选项卡并打开。
    *   选项卡会按照你配置的分段和命令渲染出来，点击按钮即可执行蓝图中定义的逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "UserToolBoxCore.h"
// 根据需要引入特定头文件
#include "UTBBaseCommand.h"
#include "UTBBaseTab.h"
#include "UserToolBoxSubsystem.h"
```

### 基本用法

**创建一个 C++ 命令类**:
这是扩展 UserToolBoxCore 的核心方式。你需要继承 `UUTBBaseCommand` 并重写 `Execute` 方法。

```cpp
// MyCustomeCommand.h
#pragma once
#include "UTBBaseCommand.h"
#include "MyCustomeCommand.generated.h"

UCLASS()
class MYPROJECT_API UMyCustomeCommand : public UUTBBaseCommand
{
	GENERATED_BODY()
public:
	UMyCustomeCommand();

	// 重写执行函数，定义命令的具体逻辑
	virtual void Execute() override;

	// 可选：重写拷贝函数，用于在编辑器中拖拽复制等操作
	virtual UUTBBaseCommand* CopyCommand(UObject* Owner) const override;
};
```

```cpp
// MyCustomeCommand.cpp
#include "MyCustomeCommand.h"
#include "Engine/World.h"

UMyCustomeCommand::UMyCustomeCommand()
{
	Name = TEXT("Spawn Cube");
	IconPath = TEXT("SlateStyleSet::Graph.ConnectorFeedback.OK"); // 使用内置图标路径
	Tooltip = TEXT("在原点生成一个立方体");
	Category = TEXT("Spawning");
}

void UMyCustomeCommand::Execute()
{
	// 在关卡中生成一个立方体
	UWorld* World = GEditor->GetEditorWorldContext().World();
	if (World)
	{
		AStaticMeshActor* Actor = World->SpawnActor<AStaticMeshActor>();
		if (Actor)
		{
			// 设置网格体为立方体 (需要替换为实际的网格体资产路径)
			static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube"));
			if (CubeMesh.Succeeded())
			{
				Actor->GetStaticMeshComponent()->SetStaticMesh(CubeMesh.Object);
			}
		}
	}
}

UUTBBaseCommand* UMyCustomeCommand::CopyCommand(UObject* Owner) const
{
	UMyCustomeCommand* NewCommand = NewObject<UMyCustomeCommand>(Owner);
	NewCommand->Name = Name;
	NewCommand->IconPath = IconPath;
	// ... 复制其他需要的属性
	return NewCommand;
}
```

**通过 C++ 创建和配置工具箱选项卡**:
通常在编辑器模块的启动函数中完成。

```cpp
// MyEditorModule.cpp
#include "UserToolBoxSubsystem.h"
#include "UTBBaseTab.h"
#include "MyCustomeCommand.h"

void FMyEditorModule::StartupModule()
{
	// 获取工具箱子系统
	UUserToolboxSubsystem* ToolboxSubsystem = GEditor->GetEditorSubsystem<UUserToolboxSubsystem>();
	if (ToolboxSubsystem)
	{
		// 创建一个新的工具箱选项卡资产
		UUserToolBoxBaseTab* MyTab = NewObject<UUserToolBoxBaseTab>(GetTransientPackage(), FName("MyC++Toolbox"));
		MyTab->Name = TEXT("C++ 工具箱");

		// 创建一个命令实例
		UMyCustomeCommand* SpawnCubeCommand = NewObject<UMyCustomeCommand>(MyTab);
		// 可以在这里动态修改命令属性
		SpawnCubeCommand->Name = TEXT("动态生成立方体");

		// 将命令添加到默认分段
		MyTab->InsertCommand(SpawnCubeCommand, UUserToolBoxBaseTab::PlaceHolderSectionName);

		// 注册选项卡数据，使其在编辑器中可见
		// 注意：通常，将 UUserToolBoxBaseTab 作为资产保存到磁盘后，子系统会通过资产注册表自动发现它。
		// 以下代码仅为演示动态创建和注册的原理。
		// ToolboxSubsystem->RegisterTabData(); // 调用此函数会扫描资产并更新内部列表。
	}
}
```

### 进阶用法

**实现自定义命令 UI（通过 IUTBUICommand 接口）**:
这是最灵活的 UI 定制方式，适合完全自定义的渲染和交互。

```cpp
// MyCustomCommandUI.h
#pragma once
#include "UTBBaseUICommandInterface.h"
#include "UTBBaseCommand.h"
#include "MyCustomCommandUI.generated.h"

UCLASS()
class UMyCustomCommandUI : public UObject, public IUTBUICommand
{
	GENERATED_BODY()
public:
	// IUTBUICommand 接口实现
	virtual bool IsSupportingCommandClass(TSubclassOf<UUTBBaseCommand> CommandClass) override;
	virtual void SetCommand(UUTBBaseCommand* Command) override;
	virtual void ExecuteCurrentCommand() override;
	virtual TSharedRef<SWidget> GetUI() override;

private:
	UPROPERTY()
	TObjectPtr<UUTBBaseCommand> BoundCommand;
	TSharedPtr<SVerticalTextBlock> NameWidget; // 使用插件自带的垂直文本块
};
```

```cpp
// MyCustomCommandUI.cpp
#include "MyCustomCommandUI.h"
#include "SVerticalTextBlock.h"
#include "Widgets/Text/STextBlock.h"

bool UMyCustomCommandUI::IsSupportingCommandClass(TSubclassOf<UUTBBaseCommand> CommandClass)
{
	// 可以指定这个UI只支持特定命令类，或支持所有命令类
	return true; 
}

void UMyCustomCommandUI::SetCommand(UUTBBaseCommand* Command)
{
	BoundCommand = Command;
	// 更新UI
	if (NameWidget.IsValid() && Command)
	{
		NameWidget->SetText(FText::FromString(Command->Name));
	}
}

void UMyCustomCommandUI::ExecuteCurrentCommand()
{
	if (BoundCommand)
	{
		BoundCommand->Execute();
	}
}

TSharedRef<SWidget> UMyCustomCommandUI::GetUI()
{
	// 创建一个完全自定义的UI，例如一个带有图标的垂直文本块
	SAssignNew(NameWidget, SVerticalTextBlock)
		.Text(FText::FromString(BoundCommand ? BoundCommand->Name : TEXT("No Command")));

	return SNew(SHorizontalBox)
		+ SHorizontalBox::Slot()
		.AutoWidth()
		[
			SNew(STextBlock)
			.Text(FText::FromString(TEXT("✅"))) // 简易图标
		]
		+ SHorizontalBox::Slot()
		.FillWidth(1.0f)
		[
			NameWidget.ToSharedRef()
		];
}
```

## Demo 示例

一个完整的最小示例：创建一个包含单个“打印日志”命令的工具箱选项卡。

**1. 命令类 (LogMessageCommand.h / .cpp):**
```cpp
// LogMessageCommand.h
#pragma once
#include "UTBBaseCommand.h"
#include "LogMessageCommand.generated.h"

UCLASS()
class ULogMessageCommand : public UUTBBaseCommand
{
	GENERATED_BODY()
public:
	ULogMessageCommand();
	virtual void Execute() override;

	UPROPERTY(EditAnywhere, Category = "Command")
	FString Message = TEXT("Hello from UserToolBoxCore!");
};
```
```cpp
// LogMessageCommand.cpp
#include "LogMessageCommand.h"

ULogMessageCommand::ULogMessageCommand()
{
	Name = TEXT("Print Log");
	IconPath = TEXT("SlateStyleSet::MessageLog");
	Tooltip = TEXT("在输出日志中打印一条消息");
}

void ULogMessageCommand::Execute()
{
	UE_LOG(LogTemp, Warning, TEXT("UTB Command Executed: %s"), *Message);
}
```

**2. 创建选项卡资产 (在编辑器模块启动时，或通过工厂手动创建):**
通常，你只需要在编辑器中右键创建一个 `User Toolbox Tab` 资产，然后手动添加 `LogMessageCommand` 的实例即可。下面演示如何用 C++ 代码创建这个资产并保存到磁盘（**注意：这通常不是最佳实践，仅用于演示原理**）。

```cpp
// 在某个编辑器工具或命令中执行
void CreateDemoToolboxTab()
{
	// 1. 创建命令实例
	ULogMessageCommand* LogCmd = NewObject<ULogMessageCommand>();
	LogCmd->Message = TEXT("This is a test message from the demo toolbox!");

	// 2. 创建选项卡资产
	UUserToolBoxBaseTab* DemoTab = NewObject<UUserToolBoxBaseTab>(GetTransientPackage(), FName("DemoToolbox"));
	DemoTab->Name = TEXT("Demo Toolbox");

	// 3. 将命令添加到默认分段
	DemoTab->InsertCommand(LogCmd, UUserToolBoxBaseTab::PlaceHolderSectionName);

	// 4. 保存资产 (需要FAssetToolsModule)
	// UPackage* Package = DemoTab->GetOutermost();
	// Package->SetDirtyFlag(true);
	// FAssetToolsModule& AssetToolsModule = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools");
	// AssetToolsModule.Get().CreateUniqueAssetName(Package->GetName(), TEXT(""), Package->FileName, Package->FileName);
	// UPackage::SavePackage(Package, DemoTab, EObjectFlags::RF_Public | EObjectFlags::RF_Standalone, *Package->FileName.ToString());
}
```

**3. 使用:**
完成上述步骤并（如代码所示）保存资产后，重新打开编辑器或在子系统中调用 `RegisterTabData()`，即可在“窗口”菜单或视口覆盖层中找到名为“Demo Toolbox”的选项卡，点击“Print Log”按钮将在输出日志中看到消息。

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。
*   该插件在 `.uplugin` 中声明了对 `SlateScripting` 插件的依赖，这表明其 UI 构建部分可能使用了 Slate 脚本化功能。
*   作为编辑器插件，它必然依赖 `UnrealEd`、`EditorStyle` 等编辑器基础模块，但这些是编辑器插件的常见依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量被截断为浮点数而产生警告的代码。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 宏。 |
| 2026-03-17 | `d3ddc7a1` | UserToolbox - Icon creation crashes engine | 修复创建图标时导致引擎崩溃的问题。 |
| 2025-09-16 | `7b6911d5` | restore UserToolBoxTab | 恢复了 UserToolBoxTab 的功能。 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 将 `IsValid(this)` 替换为其他检查方式（引擎其余部分）。 |

### 维护评价

**综合评价：实验性，但仍在维护中。**

*   **年龄与状态**：插件创建于 2023 年初，至今约 3 年，仍标记为实验性（`IsExperimentalVersion: true`）且默认不启用（`Installed: false`）。这意味着它尚未达到稳定版本，API 和功能可能发生变化。
*   **维护活跃度**：从提交历史看，最近一次实质性更新是 2026 年 3 月，且 2025 年至 2026 年有多次 bug 修复和代码维护提交。这表明它**仍在被积极维护**，主要是为了保证在 UE5 新版本中的兼容性和稳定性。
*   **已知问题/限制**：作为一个实验性插件，其 API 可能不够稳定。从近期的修复记录（如图标创建崩溃）来看，它可能仍存在一些边缘情况的稳定性问题。文档和社区示例也较少。
*   **推荐使用**：
    *   **适合**：如果你需要快速构建可配置的编辑器工具面板，且愿意接受实验性 API 的变化风险，这是一个强大的框架。
    *   **不建议**：用于需要长期稳定维护的核心产品功能，或对编辑器稳定性要求极高的环境。

**建议**：在使用前，仔细阅读源码（特别是 `UTBBaseCommand`, `UUserToolBoxBaseTab`）以理解其设计，并做好应对 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UserToolBoxCore)
- [官方文档]() (无)
- [测试用例]() (未在提供信息中发现明显测试文件)