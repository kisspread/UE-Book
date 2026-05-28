# SlateIM

> An immediate mode wrapper for Slate. Intended for building debugging tools.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 即时模式 Slate |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateIM` (Runtime), `SlateIMEngine` (Runtime), `SlateIMInGame` (Runtime), `SlateIMBlueprint` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateIM) | |

## 用途

SlateIM 是一个实验性插件，它为 Unreal Engine 的 Slate UI 框架提供了一个“即时模式”（Immediate Mode）的包装层。与 Slate 的传统“保留模式”（需要显式创建、管理和更新 Widget 树）不同，即时模式 UI 的核心思想是：每帧通过简单的函数调用来描述 UI 的外观和行为，无需关心 UI 元素的生命周期和状态管理。

这个插件的核心价值在于**快速构建调试和开发工具**。它简化了创建临时性、数据驱动的覆盖层（Overlay）的过程，开发者可以用更少的代码和更直观的逻辑来显示实时状态、变量和控件，特别适合用于：
- 快速原型化 UI
- 创建游戏内调试控制台或监视器
- 为编辑器或运行时工具提供轻量级的用户界面

## 使用场景

- **场景一：实时游戏状态监控** — 你需要一个不编译为正式 UI、能快速显示玩家生命值、坐标、FPS 等信息的调试覆盖层。
- **场景二：简单的调试按钮** — 你想在游戏运行时临时添加几个按钮来触发特定的游戏逻辑（如重置关卡、无敌模式），而不想动用 UMG 或创建正式的菜单 Widget。
- **场景三：绘制调试线条与文本** — 你希望在屏幕上直接绘制一些文本、线条或形状来可视化 AI 路径、物理检测范围等。

## 蓝图用法

SlateIM 的蓝图节点主要集中在 `SlateIMBlueprint` 模块中，提供了构建即时模式 UI 的基本积木。使用时，你需要在一个持续执行的蓝图（如 `Event Tick` 或一个按钮的按下事件）中调用这些节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Begin Window` | 开始一个即时模式窗口或面板。后续的 UI 元素都将包含在这个窗口内。 | `USlateIMBlueprintLibrary` |
| `End Window` | 结束当前即时模式窗口的定义。必须与 `Begin Window` 配对使用。 | `USlateIMBlueprintLibrary` |
| `Text` | 绘制一段静态文本。 | `USlateIMBlueprintLibrary` |
| `Button` | 绘制一个按钮，并在当帧返回其是否被点击的布尔值。 | `USlateIMBlueprintLibrary` |
| `Slider` | 绘制一个滑块，通过引用传递一个浮点值，用户操作会实时修改该值。 | `USlateIMBlueprintLibrary` |
| `Separator` | 绘制一个分隔线。 | `USlateIMBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  创建一个新的 **Actor** 蓝图。
2.  在其 **Event Graph** 中，添加一个 **Event Tick** 节点。
3.  从 `Event Tick` 引出执行线，连接到一个 **`Begin Window`** 节点（例如，窗口名设为 “Debug Tools”）。
4.  从 `Begin Window` 的输出引脚，依次连接到 **`Text`** 节点（显示 “Health:”），一个 **`Slider`** 节点（其 Value 引脚绑定到 Actor 的某个代表生命值的变量），以及一个 **`Button`** 节点（文本为 “Reset”）。
5.  将 `Button` 节点的 “Clicked” 布尔输出连接到一个 **Branch** 节点。如果为真，则执行你的重置逻辑。
6.  最后，连接到 **`End Window`** 节点。

每帧执行此图表，就会在屏幕上绘制一个带有文本、滑块和按钮的简单调试面板，且能与滑块和按钮进行交互。

## C++ 用法

SlateIM 的 C++ API 旨在通过一套简单的函数调用来构建 UI，避免了创建和管理 Widget 指针。

### 头文件引入

```cpp
#include "SlateIM.h"
```

### 基本用法

以下示例展示了如何在 `UObject` 或 `AActor` 的某个函数（例如 `Tick`）中创建一个简单的即时模式窗口。

```cpp
// 假设在 AMyDebugActor::Tick 中
#include "SlateIM.h"

void AMyDebugActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 开始一个名为 “Debug Info” 的窗口
    FSlateIM::BeginWindow(TEXT("Debug Info"));

    // 在窗口中添加文本，显示玩家的生命值
    FSlateIM::Text(FString::Printf(TEXT("Health: %.1f"), CurrentHealth));

    // 添加一个分隔线
    FSlateIM::Separator();

    // 添加一个按钮，并检查是否在这一帧被点击
    if (FSlateIM::Button(TEXT("Heal 50")))
    {
        CurrentHealth = FMath::Min(CurrentHealth + 50.f, MaxHealth);
    }

    // 结束窗口定义
    FSlateIM::EndWindow();
}
```

### 进阶用法

可以嵌套使用以创建更复杂的布局，并利用 `FSlateIMEngineCanvasDrawCommandList` 来管理更底层的绘制命令（用于自定义渲染，如绘制线条、形状）。

```cpp
// 自定义绘制命令列表的使用示例
void AMyDebugActor::DrawDebugCanvas()
{
    // 确保命令列表已初始化 (通常在 BeginPlay 或构造函数中)
    if (!DrawCommandList)
    {
        DrawCommandList = NewObject<USlateIMEngineCanvasDrawCommandList>();
        DrawCommandList->SetUpdateType(ESlateIMEngineCanvasUpdateType::EveryFrame);
    }

    // 清空上一帧的命令
    DrawCommandList->ClearCommands();

    // 入队一个绘制命令：在屏幕上绘制一条从左上角到鼠标位置的红线
    DrawCommandList->EnqueueCommand([this](UCanvas* Canvas, int32 Width, int32 Height)
    {
        if (Canvas)
        {
            FVector2D MousePos;
            GetWorld()->GetFirstPlayerController()->GetMousePosition(MousePos.X, MousePos.Y);
            Canvas->SetDrawColor(FColor::Red);
            Canvas->DrawLine(0, 0, MousePos.X, MousePos.Y);
        }
    });

    // 处理命令，将其提交给 SlateIM 的画布进行渲染
    // 注意：需要在合适的渲染回调中调用 ProcessCommands
    // 这通常由 SlateIM 的框架或你需要实现的 FSlateIMCanvasRenderer 来处理
}
```

## Demo 示例

一个完整的、可编译的最小 Actor 示例，用于在屏幕上显示一个带有按钮和变量的即时模式调试面板。

**MyDebugActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDebugActor.generated.h"

UCLASS()
class MYPROJECT_API AMyDebugActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDebugActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

private:
    /** 玩家生命值，用于演示绑定到滑块 */
    UPROPERTY(VisibleAnywhere, Category = "Debug")
    float PlayerHealth = 75.0f;

    /** 最大生命值 */
    UPROPERTY(VisibleAnywhere, Category = "Debug")
    float MaxHealth = 100.0f;

    /** 是否启用无敌模式 */
    bool bIsInvincible = false;
};
```

**MyDebugActor.cpp**
```cpp
#include "MyDebugActor.h"
#include "SlateIM.h" // 核心头文件

AMyDebugActor::AMyDebugActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyDebugActor::BeginPlay()
{
    Super::BeginPlay();
}

void AMyDebugActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 使用 SlateIM 构建即时模式 UI
    FSlateIM::BeginWindow(TEXT("Player Debug Panel"));

    // 显示生命值滑块
    FSlateIM::Text(FString::Printf(TEXT("Health: %.0f / %.0f"), PlayerHealth, MaxHealth));
    FSlateIM::Slider(PlayerHealth, 0.0f, MaxHealth);

    FSlateIM::Separator();

    // 无敌模式开关按钮
    if (FSlateIM::Button(bIsInvincible ? TEXT("Disable God Mode") : TEXT("Enable God Mode")))
    {
        bIsInvincible = !bIsInvincible;
        UE_LOG(LogTemp, Warning, TEXT("God Mode: %s"), bIsInvincible ? TEXT("ON") : TEXT("OFF"));
    }

    // 治疗按钮
    if (FSlateIM::Button(TEXT("Heal 25")))
    {
        PlayerHealth = FMath::Min(PlayerHealth + 25.0f, MaxHealth);
    }

    FSlateIM::EndWindow();
}
```

**使用方法**：将 `AMyDebugActor` 放入你的关卡中，运行游戏。屏幕上会出现一个可交互的调试面板，包含生命值滑块、治疗按钮和无敌模式开关。

## 模块依赖

要使用 SlateIM，你的模块需要依赖以下模块（根据你使用的功能选择）：

| 模块 | 用途 |
|---|---|
| `SlateIM` | 基础的即时模式 Slate 框架，提供 `FSlateIM` 命名空间下的核心 API。 |
| `SlateIMEngine` | 提供与引擎深度集成的功能，如画布绘制命令列表（`USlateIMEngineCanvasDrawCommandList`）和渲染参数结构体。 |
| `SlateIMBlueprint` | 提供蓝图可调用的静态库函数，用于在蓝图中构建即时模式 UI。 |
| `SlateIMInGame` | 可能包含针对游戏内（In-Game）场景的特定实现或辅助功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下 double 常量截断为 float 时产生的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到 `UE_LOGF`。 |
| 2026-04-02 | `82179cc5` | Remove parameters from constructor in SlateIM in game widgets and update all existing in widgets | 移除了游戏内 SlateIM 控件构造函数的参数，并更新了所有现有控件。 |
| 2026-04-01 | `097a8aca` | SlateIM: Major changes | SlateIM：重大更新。 |
| 2026-04-01 | `9016fa55` | [Backout] - CL52349724 | [回滚] - CL52349724。 |

### 维护评价

- **活跃维护**：插件在近期（2026年4-5月）有多次提交，包括功能更新、API 清理（移除构造函数参数、迁移日志宏）和编译警告修复，表明它正在被积极维护和优化。
- **实验性状态**：`IsExperimentalVersion` 为 `true`，且默认未启用（`EnabledByDefault: false`）。这意味着 API 可能不稳定，未来版本可能会有 breaking changes。
- **推荐度**：**推荐用于开发和调试目的**。它非常适合快速搭建调试工具和原型 UI。**不建议**将其用于最终发布的、需要高度稳定性的生产级游戏 UI 中，除非你愿意承担后续可能需要进行 API 适配的风险。由于是实验性插件，使用时请密切关注 Epic 的更新日志和版本迁移说明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateIM)
- [官方文档]() (无)
- [测试用例]() (插件目录内未发现独立的测试文件)