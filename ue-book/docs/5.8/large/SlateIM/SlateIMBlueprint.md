# SlateIM

> An immediate mode wrapper for Slate. Intended for building debugging tools.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Slate即时模式UI |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateIM` (Runtime), `SlateIMEngine` (Runtime), `SlateIMInGame` (Runtime), `SlateIMBlueprint` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateIM) | |

## 用途

SlateIM 为 Unreal Engine 的 Slate UI 框架提供了一个**即时模式（Immediate Mode）** 的包装层。与传统的声明式 Slate 不同，SlateIM 允许开发者通过一系列函数调用来直接描述每帧的 UI 结构和内容，无需预先定义复杂的 Widget 层次树。

**解决的问题**：传统 Slate 开发在创建临时、动态或用于调试的 UI 时较为繁琐，需要管理 Widget 的生命周期和状态。SlateIM 通过即时模式简化了这一过程，特别适合用于快速构建原型、调试工具和性能监控界面，因为它允许开发者以更直接、更线性的代码方式描述 UI，状态管理更简单。

**存在意义**：它提供了一种更灵活、更适合工具开发的 UI 构建方式，降低了调试工具和数据可视化界面的开发门槛。

## 使用场景

- **游戏内调试工具**：在游戏运行时，需要快速创建一个显示变量、性能数据或游戏状态的 HUD 面板。
- **编辑器扩展**：为自定义资产或编辑器工具创建复杂的、动态的数据查看器或编辑器面板。
- **独立程序**：在不需要完整引擎（如 `FEngineLoop`）的独立程序或命令行工具中，使用 Slate 构建简单的用户界面。
- **快速原型验证**：需要快速验证一个 UI 交互想法，而不想过早投入正式 Widget 的开发。

## 蓝图用法

SlateIM 提供了完整的蓝图函数库 (`USlateIMBlueprintFunctionLibrary`)，所有功能都封装在蓝图类别 `SlateIM` 下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Begin Window Root` | 开始一个浮动窗口根。返回窗口当前是否打开。 | `USlateIMBlueprintFunctionLibrary` |
| `Begin Viewport Client Root` | 在游戏视口中开始一个 UI 根。 | `USlateIMBlueprintFunctionLibrary` |
| `Begin Viewport Player Root` | 在指定玩家的视口中开始一个 UI 根。 | `USlateIMBlueprintFunctionLibrary` |
| `End Root` | 结束任何根（必须与 Begin 成对调用）。 | `USlateIMBlueprintFunctionLibrary` |
| `Text` | 显示一行文本。 | `USlateIMBlueprintFunctionLibrary` |
| `Editable Text` | 创建一个文本输入框。返回文本是否被修改。 | `USlateIMBlueprintFunctionLibrary` |
| `Image` | 显示一个纹理、命名画刷或纯色块。 | `USlateIMBlueprintFunctionLibrary` |
| `Begin Horizontal Stack` | 开始一个水平堆叠容器。 | `USlateIMBlueprintFunctionLibrary` |
| `Begin Vertical Stack` | 开始一个垂直堆叠容器。 | `USlateIMBlueprintFunctionLibrary` |
| `Begin Table` | 开始一个表格容器。 | `USlateIMBlueprintFunctionLibrary` |
| `Begin Scroll Box` | 开始一个可滚动的容器。 | `USlateIMBlueprintFunctionLibrary` |
| `Slider` | 创建一个滑动条。 | `USlateIMBlueprintFunctionLibrary` |
| `Check Box` | 创建一个复选框。 | `USlateIMBlueprintFunctionLibrary` |
| `Button` | 创建一个按钮。 | `USlateIMBlueprintFunctionLibrary` |
| `Draw Text` | 在画布上绘制文本。 | `USlateIMBlueprintFunctionLibrary` |
| `Draw Box` | 在画布上绘制一个未填充的方框。 | `USlateIMBlueprintFunctionLibrary` |

### 使用示例（蓝图描述）

在蓝图的 `Event Tick` 或自定义事件中：
1.  调用 `Begin Window Root` 并传入一个唯一名称（如 “MyDebugWindow”）和参数结构体，获取一个布尔值表示窗口是否打开。
2.  如果窗口打开（返回 True），则可以使用 `Begin Vertical Stack` 布局容器。
3.  在垂直容器内，调用 `Text` 节点显示一行字符串 “Player Health:”。
4.  接着调用 `Slider` 节点，将 `Ref Value` 参数连接到一个代表玩家生命值的变量（如 `PlayerHealth`），以实时显示和调整生命值。
5.  调用 `Button` 节点创建一个按钮，当按钮被点击时（输出引脚 `bPressed` 为 True），执行一些调试逻辑（如打印日志）。
6.  最后，调用 `End Vertical Stack` 和 `End Root` 来正确结束布局和根。整个结构用 `Branch` 或流程控制包裹在根窗口打开的检查之内。

## C++ 用法

SlateIM 的 C++ API 主要通过 `SlateIM` 命名空间下的函数提供。其设计风格类似于传统的即时模式 GUI 库。

### 头文件引入

```cpp
#include "SlateIM.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个简单的调试窗口。代码结构是线性的，没有回调或事件委托。

```cpp
// 来源： Engine/Plugins/Experimental/SlateIM/Source/SlateIMEngine/Private/Tests/SlateIMTest.cpp
#include "SlateIM.h"
#include "SlateIMTypes.h"

// 在某个每帧更新的地方（例如 UObject::Tick 或 AActor::Tick）
void DrawMyDebugWindow()
{
    // 1. 开始窗口。传入唯一名称和参数。检查窗口是否应该绘制。
    static const FName DebugWindowName(TEXT("C++ Debug Window"));
    FSlateIMWindowParams WindowParams;
    WindowParams.WindowTitle = FText::FromString(TEXT("My Debug Info"));
    if (SlateIM::BeginWindowRoot(DebugWindowName, WindowParams))
    {
        // 2. 开始垂直布局
        SlateIM::BeginVerticalStack();

        // 3. 显示静态文本
        SlateIM::Text(TEXT("Current Frame Rate:"), FSlateIMTextParams());

        // 4. 显示动态变量（例如 FPS）
        const float CurrentFPS = 1.0f / FApp::GetDeltaTime();
        SlateIM::Text(FString::Printf(TEXT("%.2f FPS"), CurrentFPS), FSlateIMTextParams());

        // 5. 创建一个交互按钮
        if (SlateIM::Button(TEXT("Reset Level"), FSlateIMButtonParams()))
        {
            // 按钮被点击的逻辑
            UE_LOG(LogTemp, Warning, TEXT("Reset Level button pressed!"));
        }

        // 6. 结束布局
        SlateIM::EndVerticalStack();
    }
    // 7. 无论窗口是否打开，都必须调用 EndRoot
    SlateIM::EndRoot();
}
```

### 进阶用法

结合表格（`BeginTable`）和滚动框（`BeginScrollBox`）来显示复杂数据。

```cpp
// 来源：综合 SlateIM API 设计模式
void DrawActorListWindow()
{
    if (SlateIM::BeginWindowRoot(FName(TEXT("ActorList")), FSlateIMWindowParams()))
    {
        // 创建一个可滚动的容器
        FSlateIMScrollBoxParams ScrollParams;
        SlateIM::BeginScrollBox(ScrollParams);

        // 开始一个表格
        FSlateIMTableParams TableParams;
        SlateIM::BeginTable(TableParams);

        // 定义表头
        SlateIM::BeginTableHeader();
        SlateIM::AddTableColumn(FName(TEXT("Name")), FSlateIMTableColumnParams());
        SlateIM::AddTableColumn(FName(TEXT("Location")), FSlateIMTableColumnParams());
        SlateIM::EndTableHeader();

        // 定义表体
        SlateIM::BeginTableBody();

        // 假设遍历场景中的所有Actor
        for (AActor* Actor : AllActors)
        {
            // 进入下一行的一个单元格
            bool bRowSelected = false;
            if (SlateIM::NextTableCell(bRowSelected))
            {
                // 显示Actor名称
                SlateIM::Text(Actor->GetName(), FSlateIMTextParams());
            }

            // 进入下一行的下一个单元格（位置）
            if (SlateIM::NextTableCell(bRowSelected))
            {
                // 格式化位置向量为字符串
                FString LocString = Actor->GetActorLocation().ToString();
                SlateIM::Text(LocString, FSlateIMTextParams());
            }
        }

        SlateIM::EndTableBody();
        SlateIM::EndTable();
        SlateIM::EndScrollBox();
    }
    SlateIM::EndRoot();
}
```

## Demo 示例

一个最小的 C++ 示例，创建一个显示帧时间的窗口。

```cpp
// MyDebugComponent.h
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyDebugComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UMyDebugComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
};
```

```cpp
// MyDebugComponent.cpp
#include "MyDebugComponent.h"
#include "SlateIM.h"

void UMyDebugComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // 唯一的窗口名称
    static const FName WindowName = FName(TEXT("FrameTimeDebug"));

    // 设置窗口参数
    FSlateIMWindowParams Params;
    Params.WindowTitle = FText::FromString(TEXT("Frame Time"));
    Params.bInitiallyOpen = true;

    // 开始/检查窗口
    if (SlateIM::BeginWindowRoot(WindowName, Params))
    {
        // 开始垂直布局
        SlateIM::BeginVerticalStack();

        // 显示标签
        SlateIM::Text(TEXT("Last Frame DeltaTime:"), FSlateIMTextParams());

        // 显示当前 DeltaTime
        FString DeltaStr = FString::Printf(TEXT("%.4f ms"), DeltaTime * 1000.0f);
        FSlateIMTextParams TextParams;
        TextParams.TextStyle = FSlateIMStyle::Get().GetWidgetStyle<FTextBlockStyle>("NormalText"); // 使用一个基础文本样式
        SlateIM::Text(DeltaStr, TextParams);

        // 一个简单的按钮
        if (SlateIM::Button(TEXT("Close Window"), FSlateIMButtonParams()))
        {
            // 实际上，窗口的“关闭”通常由窗口标题栏的X按钮处理。
            // 这个按钮可以用于其他逻辑。
        }

        // 结束布局
        SlateIM::EndVerticalStack();
    }
    // **关键**：必须调用 EndRoot，无论窗口是否打开
    SlateIM::EndRoot();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SlateIM` | 核心API和类型定义 |
| `SlateIMEngine` | 与引擎集成的底层实现 |
| `SlateIMInGame` | 面向游戏运行时的特定功能 |
| `SlateIMBlueprint` | 蓝图接口封装 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数时产生的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到新的UE_LOGF宏。 |
| 2026-04-02 | `82179cc5` | Remove parameters from constructor in SlateIM in game widgets and update all existing in widgets | 移除了SlateIM游戏内Widget构造函数的参数，并更新了所有现有Widget。 |
| 2026-04-01 | `097a8aca` | SlateIM: Major changes | SlateIM：进行了重大改动。 |
| 2026-04-01 | `9016fa55` | [Backout] - CL52349724 | [回滚] - CL52349724。 |

### 维护评价

**综合评价**：活跃维护中。

- **创建时间**：创建于 2025 年 1 月，至今约 1 年。
- **更新频率**：近期（2026年4月至5月）有持续的实质性更新，包括API重构（重大改动）、代码清理（构造函数参数变更）、警告修复和日志系统迁移。这表明该插件处于**积极开发和迭代期**。
- **状态**：插件标记为实验性 (`IsExperimentalVersion: true`)，且默认未启用 (`EnabledByDefault: false`)。这意味着 Epic 认为该 API 尚未稳定，未来可能会有不兼容的更改。
- **推荐使用**：**推荐用于开发和调试工具**。对于生产环境的最终用户界面，建议谨慎评估。它非常适合内部工具、原型和快速迭代，可以显著提高工具开发效率。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateIM)
- [官方文档]() (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateIM/Source/SlateIMEngine/Private/Tests)