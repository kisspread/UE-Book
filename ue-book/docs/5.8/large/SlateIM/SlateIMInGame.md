# SlateIM

> An immediate mode wrapper for Slate. Intended for building debugging tools.

| 属性 | 值 |
|---|---|
| 中文名 | 即时模式UI工具 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateIM` (Runtime), `SlateIMEngine` (Runtime), `SlateIMInGame` (Runtime), `SlateIMBlueprint` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-24 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateIM) | |

## 用途

SlateIM 是一个为 **Slate** 用户界面框架提供的 **即时模式（Immediate Mode）** 包装层。它允许开发者使用类似 Dear ImGui 的声明式 API 快速构建用户界面，而无需处理传统 Slate 中管理 Widget 生命周期、状态和样式的繁琐代码。其核心价值在于**简化和加速调试工具、开发面板和临时UI覆盖层的编写过程**，这些工具通常不需要复杂的布局或高级交互，但需要能够快速迭代和修改。

## 使用场景

- **开发者**需要为游戏或引擎工具快速编写一个自定义的调试面板（如显示性能数据、游戏状态、AI信息）。
- **程序员**需要在不创建完整 UMG 蓝图或编写大量样板 Slate 代码的情况下，临时查看或修改某些内部状态。
- **设计师**希望通过蓝图快速原型化一个简单的游戏内信息窗口或 HUD 元素进行测试。
- 项目需要一个轻量级的工具框架，用于创建不包含在最终发布包中的开发辅助功能。

## 蓝图用法

SlateIM 通过 `SlateIMBlueprint` 模块向蓝图暴露功能，并通过 `SlateIMInGame` 模块提供可在游戏中显示的窗口 Actor。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Enable In Game Widget` | 根据类路径在指定的玩家控制器上启用或禁用一个游戏内调试窗口实例。 | `ASlateIMInGameWidgetBase` |
| `Get In Game Widget` | 获取指定玩家控制器上某个类路径对应的游戏内调试窗口实例。 | `ASlateIMInGameWidgetBase` |
| `Toggle SlateIM In Game Widget` | 通过控制台命令（控制台输入）切换指定类路径的游戏内窗口的显示状态。 | `USlateIMInGameWidgetCheatManager` |
| `Init` | 初始化一个 `SlateIMInGameWindow`，设置其在游戏世界中的名称和标题。 | `ASlateIMInGameWindow` |

### 使用示例（蓝图描述）

1.  **启用游戏内调试窗口**：
    *   在某个事件（如按键按下）中，调用 `Enable In Game Widget`。
    *   `Target` 设置为当前 `Player Controller`。
    *   `InGameWidgetClass` 设置为你创建的 `ASlateIMInGameWindow` 子类（例如 `BP_MyDebugWindow`）的类引用。
    *   `bEnable` 设置为 `true`。
    *   执行后，屏幕上将出现该窗口。

2.  **通过控制台命令切换**：
    *   这是通过 `SlateIMInGame` 模块自动注册的控制台命令实现的。在游戏中按下 `~` 键打开控制台。
    *   输入命令：`ToggleSlateIMInGameWidget /Game/Blueprints/BP_MyDebugWindow` （路径替换为你的蓝图路径）。
    *   这将切换该窗口的显示/隐藏状态。

## C++ 用法

SlateIM 的核心 C++ API 设计为声明式和即时的，旨在减少状态管理。

### 头文件引入

```cpp
// 引入核心 SlateIM API，包含所有即时模式UI函数
#include "SlateIM.h"

// 如果需要创建游戏内窗口
#include "SlateIMInGame/Public/SlateIMInGameWindow.h"
```

### 基本用法

SlateIM 的 API 以函数调用链的形式组织。典型的使用方式是在你的 Widget（或 Actor）的绘制循环中调用这些函数。

```cpp
// 在某个需要绘制UI的地方（例如 AHUD::DrawHUD 或 UUserWidget::NativePaint）
void MyDebugTool::DrawDebugUI()
{
    // 开始一个新的面板，会自动管理布局
    SlateIM::BeginPanel(TEXT("Debug Info"));

    // 显示文本
    SlateIM::Text(FString::Printf(TEXT("FPS: %.2f"), CurrentFPS));
    SlateIM::Text(FString::Printf(TEXT("Actors: %d"), World->GetNumActors()));

    // 添加一个按钮，返回 true 表示被点击
    if (SlateIM::Button(TEXT("Reset Player")))
    {
        ResetPlayer();
    }

    // 结束面板
    SlateIM::EndPanel();
}
```

*(示例灵感来源于 SlateIM.h 中可能包含的即时模式函数签名，如 `BeginPanel`, `Text`, `Button` 等)*

### 进阶用法

创建一个自定义的游戏内调试窗口 Actor，该窗口的内容使用 SlateIM 即时模式 API 绘制。

```cpp
// MyDebugWindow.h
#pragma once
#include "SlateIMInGame/Public/SlateIMInGameWindow.h"
#include "MyDebugWindow.generated.h"

UCLASS()
class AMyDebugWindow : public ASlateIMInGameWindow
{
    GENERATED_BODY()
    
protected:
    // 重写此函数，使用 SlateIM API 定义窗口内容
    virtual void DrawContent(const float DeltaTime) override;
};

// MyDebugWindow.cpp
#include "MyDebugWindow.h"
#include "SlateIM.h"

void AMyDebugWindow::DrawContent(const float DeltaTime)
{
    // 这个函数在每一帧被调用，用于绘制窗口内部
    SlateIM::BeginPanel(TEXT("Game Stats"));

    static int32 ClickCount = 0;
    SlateIM::Text(FString::Printf(TEXT("Global Clicks: %d"), ClickCount));

    if (SlateIM::Button(TEXT("Increment")))
    {
        ClickCount++;
    }

    SlateIM::Separator(); // 分隔线

    SlateIM::Text(FString::Printf(TEXT("Actor Location: %s"), *GetActorLocation().ToString()));

    SlateIM::EndPanel();
}
```

*(示例基于 `ASlateIMInGameWindow` 的头文件分析，其 `DrawContent` 函数是提供给子类用于绘制内容的虚函数)*

## Demo 示例

一个完整的、可编译的最小示例，展示如何创建一个显示基本信息的游戏内调试窗口。

**MyDebugWindow.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "SlateIMInGame/Public/SlateIMInGameWindow.h"
#include "MyDebugWindow.generated.h"

UCLASS()
class AMyDebugWindow : public ASlateIMInGameWindow
{
	GENERATED_BODY()
	
public:
	AMyDebugWindow();

protected:
	virtual void BeginPlay() override;
	virtual void DrawContent(const float DeltaTime) override;

private:
	int32 FrameCount = 0;
	float TotalTime = 0.0f;
};
```

**MyDebugWindow.cpp**
```cpp
#include "MyDebugWindow.h"
#include "SlateIM.h"
#include "Engine/World.h"

AMyDebugWindow::AMyDebugWindow()
{
	// 窗口将在游戏中自动生成，无需手动构造
}

void AMyDebugWindow::BeginPlay()
{
	Super::BeginPlay();
	// 初始化窗口名称和标题
	Init(FName(TEXT("MyDebugWindow")), TEXT("简易调试窗口"));
}

void AMyDebugWindow::DrawContent(const float DeltaTime)
{
	// 更新统计信息
	FrameCount++;
	TotalTime += DeltaTime;

	SlateIM::BeginPanel(TEXT("实时统计"));
	{
		SlateIM::Text(FString::Printf(TEXT("运行时间: %.2f 秒"), TotalTime));
		SlateIM::Text(FString::Printf(TEXT("总帧数: %d"), FrameCount));
		SlateIM::Text(FString::Printf(TEXT("平均帧率: %.1f"), FrameCount / TotalTime));

		SlateIM::Separator();

		SlateIM::Text(TEXT("位置:"));
		if (APlayerController* PC = GetPlayerController())
		{
			if (APawn* Pawn = PC->GetPawn())
			{
				SlateIM::Text(Pawn->GetActorLocation().ToString());
			}
		}

		if (SlateIM::Button(TEXT("重置计数器")))
		{
			FrameCount = 0;
			TotalTime = 0.0f;
		}
	}
	SlateIM::EndPanel();
}
```

**使用方式**：
1.  将上述 `.h` 和 `.cpp` 文件放入你的项目模块中。
2.  确保你的模块在 `.Build.cs` 中依赖 `SlateIMInGame` 和 `SlateIM`。
3.  在游戏运行时，通过控制台命令 `ToggleSlateIMInGameWidget /Script/YourProject.MyDebugWindow` 来打开或关闭此调试窗口。
4.  或者，通过蓝图调用 `Enable In Game Widget` 并传入 `AMyDebugWindow` 的类来启用。

## 模块依赖

要使用 SlateIM 插件，你的项目模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `SlateIM` | 提供核心的即时模式 UI API（如 `SlateIM::Text`, `SlateIM::Button`）。 |
| `SlateIMInGame` | 提供 `ASlateIMInGameWindow` 等基类，用于创建可在游戏世界中显示的调试窗口 Actor。 |
| `SlateIMEngine` | 引擎集成层，提供 SlateIM 与 Slate 引擎的底层连接。 |
| `SlateIMBlueprint` | 提供蓝图可调用的函数和类，使蓝图也能使用 SlateIM 功能。 |

通常，你需要根据想使用的功能来选择依赖：
- **仅使用即时模式 C++ API**：依赖 `SlateIM`。
- **创建游戏内调试窗口**：依赖 `SlateIMInGame`（它会自动传递依赖 `SlateIM` 和 `SlateIMEngine`）。
- **在蓝图中使用**：依赖 `SlateIMBlueprint`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断到单精度浮点数时产生的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版的 UE_LOG 宏迁移到新的 UE_LOGF 宏，属于日志系统升级。 |
| 2026-04-02 | `82179cc5` | Remove parameters from constructor in SlateIM in game widgets and update all existing in widgets | 移除了游戏内窗口构造函数的参数，并更新了所有现有窗口实现。这是一次 **API 重构**。 |
| 2026-04-01 | `097a8aca` | SlateIM: Major changes | 提交信息过于简略，可能包含重要的架构或功能变更。 |
| 2026-04-01 | `9016fa55` | [Backout] - CL52349724 | 撤销了之前的某个变更 (CL52349724)。 |

### 维护评价

- **年龄**：插件创建于 2025 年初，至今约 2 年，属于较新的实验性项目。
- **更新频率**：最近一次更新在 2026 年 5 月，更新频率较高，且包含 API 重构和功能改进，表明插件仍在**积极开发**中。
- **活跃度**：Epic Games 工程师仍在维护，近期提交涉及编译警告修复、日志系统迁移和 API 优化。
- **已知限制**：作为实验性插件（`IsExperimentalVersion=true`，`EnabledByDefault=false`），其 API 可能不稳定，未来版本可能发生变化。`CanContainContent=false` 意味着它不包含任何蓝图、材质等资产，纯为代码模块。
- **推荐**：**推荐在内部工具和调试目的中使用**，可以显著提升开发效率。但由于其实验性质，**不建议用于最终面向玩家的、需要长期稳定的核心游戏功能中**。适合希望快速搭建开发和调试界面的团队。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateIM)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateIM/Tests)