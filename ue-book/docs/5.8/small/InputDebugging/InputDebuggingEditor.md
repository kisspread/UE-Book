# Input Debugging

> Input debugging and visualization.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 输入调试 |
| 分类 | Input |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InputDebugging` (Runtime), `InputDebuggingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-05-19 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InputDebugging) | |

## 用途

这个插件为 Unreal Engine 提供了运行时输入调试和可视化工具。它存在的核心目的是帮助开发者在开发和测试阶段，直观地查看和分析游戏运行时的输入状态，特别是触摸输入。通过该插件，开发者可以快速在屏幕上显示触摸点的位置和状态，无需编写额外的调试代码，从而加速调试输入相关问题（如多点触控、触摸响应区域等）的过程。

## 使用场景

- 你正在为移动设备或平板电脑开发游戏，需要测试多点触控和手势识别的功能是否正确。
- 你需要验证UI按钮对触摸输入的响应区域是否与视觉表现一致。
- 你希望在不暂停游戏的情况下，实时观察玩家手指在屏幕上的触摸轨迹。

## 蓝图用法

此插件主要通过控制台命令驱动，未在提供的头文件中发现标准的 `BlueprintCallable` 函数。其核心功能是通过控制台命令开启的。

### 核心功能

| 控制台命令 | 说明 |
|---|---|
| `Input.Debug.ShowTouches 1` | 在屏幕上开启触摸输入的可视化显示 |
| `Input.Debug.ShowTouches 0` | 关闭触摸输入的可视化显示 |

### 使用示例（蓝图描述）

虽然无法直接通过蓝图节点调用，但你可以在蓝图中通过 `Execute Console Command` 节点来启用此功能：

1.  从 **Palette** 搜索并添加一个 **Execute Console Command** 节点。
2.  在 **Command** 参数中输入 `Input.Debug.ShowTouches 1`。
3.  将这个节点连接到你希望触发显示的事件（如 `BeginPlay` 或一个按键输入事件）。

## C++ 用法

主要通过在代码中执行控制台命令来使用其功能。

### 头文件引入

```cpp
#include "HAL/IConsoleManager.h"
```

### 基本用法

通过 C++ 启用或禁用触摸输入的可视化显示。

```cpp
// 启用触摸点显示
static const auto ShowTouches = IConsoleManager::Get().FindConsoleVariable(TEXT("Input.Debug.ShowTouches"));
if (ShowTouches)
{
    ShowTouches->Set(1); // 1 为显示，0 为隐藏
}
```

### 进阶用法

将此调试开关集成到你的自定义调试菜单或配置系统中，实现一键切换。

```cpp
// 假设这是一个自定义的调试菜单切换函数
void UMyDebugManager::ToggleTouchVisualization()
{
    static IConsoleVariable* CVarShowTouches = IConsoleManager::Get().FindConsoleVariable(TEXT("Input.Debug.ShowTouches"));
    if (CVarShowTouches)
    {
        // 切换当前状态
        const int32 CurrentValue = CVarShowTouches->GetInt();
        CVarShowTouches->Set(CurrentValue == 0 ? 1 : 0);
    }
}
```

## Demo 示例

一个最小的可编译示例，展示如何在游戏模块启动时自动开启触摸显示。

```cpp
// MyGameMode.h
#pragma once
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    virtual void StartPlay() override;
};

// MyGameMode.cpp
#include "MyGameMode.h"
#include "HAL/IConsoleManager.h"

void AMyGameMode::StartPlay()
{
    Super::StartPlay();

    // 自动启用触摸调试显示
    if (IConsoleVariable* CVar = IConsoleManager::Get().FindConsoleVariable(TEXT("Input.Debug.ShowTouches")))
    {
        CVar->Set(1);
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `ee8a6c98` | Fix touch input debug circle position in editor by offsetting the drawn circle by the game viewport' | 修复编辑器内触摸调试圆圈位置错误，通过考虑游戏视口偏移量进行校正。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件日志输出从 `UE_LOG` 迁移到新的 `UE_LOGF` 宏。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了上一次提交中错误的查找替换，进行二次修正。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了提交 CL51314860 的更改。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复因 `FCoreDelegates` API 变更导致的初始化委托注册失败问题。 |

### 维护评价

该插件处于**活跃维护**状态。创建于2022年，但近期（2026年）有多次实质性更新，包括修复编辑器内触摸调试的位置偏移问题、适配引擎新的日志宏（`UE_LOGF`）以及修复因引擎核心委托（`FCoreDelegates`）API 变更导致的兼容性问题。这表明 Epic Games 仍在积极维护此插件，确保其与最新的引擎版本兼容并修复缺陷。推荐在需要输入调试功能的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InputDebugging)