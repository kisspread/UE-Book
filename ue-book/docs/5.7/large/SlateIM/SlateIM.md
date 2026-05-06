# SlateIM

> An immediate mode wrapper for Slate. Intended for building debugging tools.

| 属性 | 值 |
|---|---|
| 中文名 | Slate 即时模式封装 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateIM` (Runtime), `SlateIMInGame` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SlateIM) | |

## 用途

SlateIM 为 Unreal Engine 的 Slate UI 框架提供了一个**即时模式（Immediate Mode）** 封装。传统 Slate 采用保留模式（保留 Widget 树结构并由框架管理生命周期），而 SlateIM 允许开发者以类似 ImGui 的方式，在每帧的绘制回调中声明式地创建和布局 UI 控件，无需手动维护 Widget 的创建、更新和销毁。

该插件主要面向**调试工具**和**开发者 UI** 的快速构建，尤其适合需要频繁迭代、状态简单的工具界面。它通过按帧重建 Widget 树、利用哈希比较机制最小化实际 Slate Widget 的更新开销。

## 使用场景

- 在游戏中或编辑器中创建调试叠加层（Overlay），显示 FPS、内存、网络状态等实时数据
- 快速搭建开发工具窗口（如参数调节面板、日志浏览器、材质预览器）
- 在视口内嵌入交互式 UI（如属性调整、坐标轴显示）
- 需要临时 UI 而不想维护复杂 Widget 层次结构的场景

## 蓝图用法

该插件无蓝图暴露的 API，纯 C++ 使用。

## C++ 用法

### 头文件引入

```cpp
#include "SlateIM.h"
#include "SlateIMWidgetBase.h"  // 基类
```

### 基本用法

#### 1. 创建窗口工具（推荐方式）

继承 `FSlateIMWindowBase`，在 `DrawWindow` 中声明 UI。窗口会自动绑定控制台命令。

```cpp
#include "SlateIM.h"
#include "SlateIMWidgetBase.h"

class FMyDebugWindow : public FSlateIMWindowBase
{
public:
    FMyDebugWindow()
        : FSlateIMWindowBase(
            TEXT("My Debug Window"),   // 窗口标题
            FVector2f(400, 300),       // 初始大小
            TEXT("MyPlugin.ToggleDebug"), // 控制台命令
            TEXT("Toggle My Debug Window") // 命令帮助
          )
    {}

protected:
    virtual void DrawWindow(float DeltaTime) override
    {
        // 在窗口中添加内容
        SlateIM::Text(TEXT("Hello SlateIM!"));

        static bool bCheck = false;
        SlateIM::CheckBox(TEXT("Enable Feature"), bCheck);

        static float Value = 0.5f;
        SlateIM::Slider(TEXT("Parameter"), Value, 0.0f, 1.0f);
    }
};

// 全局实例（通常在 .cpp 中定义）
static FMyDebugWindow MyDebugWindow;
```

#### 2. 在视口内嵌入 UI（FSlateIMWidgetBase）

若需要将 UI 直接绘制到游戏视口（Game Viewport）中，使用 `FSlateIMWidgetBase` 并调用 `BeginViewportRoot`。

```cpp
#include "SlateIM.h"
#include "SlateIMWidgetBase.h"

class FMyViewportWidget : public FSlateIMWidgetBase
{
public:
    explicit FMyViewportWidget()
        : FSlateIMWidgetBase(TEXT("MyViewportWidget"))
    {
        EnableWidget(); // 立即启用
    }

protected:
    virtual void DrawWidget(float DeltaTime) override
    {
        UGameViewportClient* GVC = GetWorld()->GetGameViewport();
        if(!GVC) return;

        // 定义布局（锚点、偏移、对齐）
        SlateIM::FViewportRootLayout Layout;
        Layout.Anchors = FAnchors(0.0f, 0.0f); // 左上角
        Layout.Offset = FVector2f(10, 10);
        Layout.Alignment = FVector2f(0, 0);
        Layout.ZOrder = 10000;

        if (SlateIM::BeginViewportRoot(TEXT("MyRoot"), GVC, Layout))
        {
            SlateIM::Text(TEXT("FPS: 60"));
            static bool bDebug = false;
            SlateIM::CheckBox(TEXT("Debug"), bDebug);
            SlateIM::EndRoot();
        }
    }
};

static FMyViewportWidget MyViewportWidget;
```

#### 3. 使用现有 Slate Widget（通过 BeginCustomWidget）

若需要在即时模式中插入一个已有的 Slate Widget（例如编辑框、图像控件），使用 `BeginCustomWidget`。

```cpp
// 创建自定义文本块
TSharedRef<STextBlock> MyText = SNew(STextBlock)
    .Text(FText::FromString(TEXT("Custom")));

// 在即时模式中包裹
SlateIM::BeginCustomWidget(MyText);
SlateIM::EndWidget();
```

#### 4. 容器与布局

支持多种容器（水平/垂直堆叠、滚动框、换行框、表格等）。

```cpp
// 垂直堆叠（默认）
SlateIM::VerticalBox([]()
{
    SlateIM::Button(TEXT("Click Me"), []()
    {
        UE_LOG(LogTemp, Log, TEXT("Button clicked!"));
    });
    SlateIM::Separator();
    SlateIM::Text(TEXT("Some text"));
});

// 水平排列
SlateIM::HorizontalBox([]()
{
    SlateIM::Text(TEXT("Name:"));
    SlateIM::SameLine(); // 等价于水平 Box 内的元素
    SlateIM::EditableTextBox(MyString);
});
```

#### 5. 表格（树形表格）

```cpp
SlateIM::BeginTable(TEXT("Item"), TEXT("Value"));
{
    SlateIM::TableRow();
    {
        SlateIM::Text(TEXT("Health"));
        SlateIM::NextColumn();
        SlateIM::Text(FString::Printf(TEXT("%d"), Health));
    }
    SlateIM::EndTableRow();

    SlateIM::TableRow();
    {
        SlateIM::Text(TEXT("Position"));
        SlateIM::NextColumn();
        SlateIM::Text(Location.ToString());
    }
    SlateIM::EndTableRow();
}
SlateIM::EndTable();
```

#### 6. 弹出窗口（Context Menu）

```cpp
if (SlateIM::BeginContextMenu()) // 需要鼠标右键或按下自定义触发键
{
    SlateIM::MenuButton(TEXT("Copy"), [](){ /*...*/ });
    SlateIM::MenuCheckButton(TEXT("Auto Sync"), bSync);
    SlateIM::EndContextMenu();
}
```

### 进阶用法

#### 自定义窗口/视口根节点的生命周期

使用 `BeginWindowRoot` / `EndRoot` 手动管理窗口。适用于复杂场景，如不继承 `FSlateIMWindowBase`。

```cpp
bool bWindowOpen = true;
if (SlateIM::BeginWindowRoot(TEXT("MyWindow"), TEXT("Settings"), FVector2f(500, 400), bWindowOpen))
{
    SlateIM::Text(TEXT("This window is open"));
    SlateIM::Button(TEXT("Close"), [&](){ bWindowOpen = false; });
    SlateIM::EndRoot();
}
```

#### 使用 FSlateIMExposedBase 将即时 UI 嵌入现有 Slate 层次

`FSlateIMExposedBase` 生成一个 `SWidget` 引用，可放置在任意 Slate 容器中。

```cpp
class FEmbeddedTool : public FSlateIMExposedBase
{
public:
    FEmbeddedTool() : FSlateIMExposedBase(TEXT("Embedded"))
    {
        EnableWidget();
    }

protected:
    virtual void DrawContent(float DeltaTime) override
    {
        SlateIM::Text(TEXT("I am inside another Slate widget!"));
        static int Count = 0;
        if (SlateIM::Button(TEXT("Click")))
            Count++;
        SlateIM::Text(FString::Printf(TEXT("Clicked %d times"), Count));
    }
};

// 在其他 Slate Widget 中使用
TSharedRef<SWidget> EmbeddedWidget = MyEmbeddedTool.GetExposedWidget();
SNew(SVerticalBox)
+ SVerticalBox::Slot()
[
    EmbeddedWidget
];
```

## Demo 示例

以下是一个完整的最小示例，创建一个带窗口的调试工具，展示常用控件（按钮、复选框、滑动条、文本）的用法。

**MyTool.h**
```cpp
#pragma once

#include "SlateIMWidgetBase.h"

class FMyToolWidget : public FSlateIMWindowBase
{
public:
    FMyToolWidget();
protected:
    virtual void DrawWindow(float DeltaTime) override;

private:
    bool  bEnableFeature = true;
    float SliderValue = 0.5f;
    int   ClickCount = 0;
};
```

**MyTool.cpp**
```cpp
#include "MyTool.h"
#include "SlateIM.h"

FMyToolWidget::FMyToolWidget()
    : FSlateIMWindowBase(
        TEXT("MyTool"),
        FVector2f(350, 200),
        TEXT("MyPlugin.ToggleTool"),
        TEXT("Toggle My Debug Tool"))
{}

void FMyToolWidget::DrawWindow(float DeltaTime)
{
    SlateIM::Text(TEXT("My Debug Tool"));
    SlateIM::Separator();

    SlateIM::CheckBox(TEXT("Enable Feature"), bEnableFeature);
    SlateIM::Slider(TEXT("Parameter"), SliderValue, 0.0f, 1.0f);

    if (SlateIM::Button(TEXT("Click Me")))
    {
        ClickCount++;
        UE_LOG(LogTemp, Log, TEXT("Button clicked %d times"), ClickCount);
    }

    SlateIM::SameLine();
    SlateIM::Text(FString::Printf(TEXT("Clicked %d times"), ClickCount));

    SlateIM::Separator();
    SlateIM::Text(FString::Printf(TEXT("Feature %s"), bEnableFeature ? TEXT("Enabled") : TEXT("Disabled")));
    SlateIM::Text(FString::Printf(TEXT("Slider Value: %.2f"), SliderValue));
}

// 全局实例
static FMyToolWidget MyToolWidget;
```

编译并启动编辑器后，在控制台输入 `MyPlugin.ToggleTool` 即可打开窗口。

## 模块依赖

### SlateIM

无特殊依赖（仅标准 Core/Engine/Slate 等）。

### SlateIMInGame

该模块依赖 `SlateIM` 以及 `Engine`、`SlateCore`，无特殊外部依赖。

> **注意**：要在自己的插件中使用 SlateIM，只需在 Build.cs 的 `PublicDependencyModuleNames` 中添加 `"SlateIM"`。若需视口或 InGame 功能，还需添加 `"SlateIMInGame"`（自动包含 SlateIM）。

## 维护状态

### 近期更新

- 2025-09-09 `accbcce5` — Fixup API macros
- 2025-09-03 `3b7603db` — Fixes for SlateImInGame widgets
- 2025-09-03 `40963b9c` — SlateIM InGame widget actor for server/client debugging
- 2025-08-28 `ea3f5ec2` — SlateIM: Add an overload of SlateIM::Image that takes just a color
- 2025-07-28 `9469fd08` — SlateIM: Fix example window text not readjusting itself after the window is resized

### 维护评价

- **创建时间**：2025-07-28（约 2 个月）
- **更新频率**：截至 2025-09-09 共有多次实质性更新，包括功能添加（InGame 调试、Image 重载）和 Bug 修复（API 宏、窗口文本调整）
- **活跃度**：团队持续活跃，近期仍有提交
- **已知问题**：该插件标记为实验性（IsExperimentalVersion=true），API 可能不稳定，仅适合开发调试使用，不建议用于发布产品
- **推荐使用**：适合用于开发调试工具快速原型，但注意实验性状态，后续可能发生破坏性变更。若需要稳定调试 UI，可考虑成熟的 Slate 方式或第三方库。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SlateIM)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/)（暂无可直接指向的插件文档，请参阅 Slate 通用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SlateIM/Source/SlateIM/Private)（内部示例见 `SlateIMExamples.h/.cpp`）