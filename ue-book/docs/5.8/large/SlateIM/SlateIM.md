# SlateIM

> An immediate mode wrapper for Slate. Intended for building debugging tools.

| 属性 | 值 |
|---|---|
| 中文名 | 即时模式UI |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateIM` (Runtime), `SlateIMEngine` (Runtime), `SlateIMInGame` (Runtime), `SlateIMBlueprint` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateIM) | |

## 用途

SlateIM 是 Slate UI 框架的**即时模式（Immediate Mode）封装层**。传统 Slate 采用保留模式（Retained Mode），你需要先创建 Widget 树、绑定委托、管理生命周期——这对于快速构建调试工具来说过于繁琐。SlateIM 解决了这个问题：你可以用类似 Dear ImGui 的方式，在每帧的 `Draw` 函数中按顺序声明 UI 元素，框架自动处理 Widget 的创建、复用和销毁。

**核心设计理念**：
- **声明式布局**：每帧调用 `BeginXxx` / `EndXxx` 描述 UI 结构，框架通过哈希对比自动复用已有的 Widget
- **零样板代码**：不需要手动管理 TSharedPtr 生命周期、不需要绑定委托、不需要手动构建 Widget 树
- **多场景支持**：可以在浮动窗口、游戏视口、编辑器视口、可停靠标签页、甚至内嵌到现有 Slate 层级中使用
- **非引擎程序可用**：设计上支持不依赖完整引擎的程序使用（基于无引擎模式）

## 使用场景

- 你需要快速搭建一个**调试窗口**来显示运行时变量 → 用 `FSlateIMWindowBase` 子类
- 你想在**游戏视口**中叠加 HUD 调试信息 → 用 `SlateIM::BeginViewportRoot`
- 你需要一个**可停靠的编辑器工具面板** → 用 `FSlateIMNomadTabBase` 子类
- 你想构建一个**实时数据图表**来监控性能指标 → 用 `SlateIM::GraphLinePoints` / `GraphLineValues`
- 你要做一个**表格/树形结构**的数据浏览器 → 用 `SlateIM::BeginTable` + `BeginTableRowChildren`
- 你想在现有 Slate 层级中**嵌入即时模式 UI** → 用 `FSlateIMExposedBase` 子类
- 你需要快速原型验证某个 UI 布局 → 直接在 Tick 中调用 SlateIM API

## 蓝图用法

SlateIM 通过 `SlateIMBlueprint` 模块提供了完整的蓝图支持，参数结构体均标记为 `BlueprintType`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BeginWindowRoot` | 创建浮动调试窗口 | `SlateIMBlueprint` (蓝图函数库) |
| `EndRoot` | 结束当前根节点，必须与 Begin 配对 | `SlateIMBlueprint` |
| `BeginVerticalStack` | 开始垂直堆叠布局 | `SlateIMBlueprint` |
| `BeginHorizontalStack` | 开始水平堆叠布局 | `SlateIMBlueprint` |
| `EndVerticalStack` / `EndHorizontalStack` | 结束布局容器 | `SlateIMBlueprint` |
| `Text` | 显示文本 | `SlateIMBlueprint` |
| `Button` | 创建按钮，返回是否被点击 | `SlateIMBlueprint` |
| `CheckBox` | 创建复选框 | `SlateIMBlueprint` |
| `Slider` | 创建滑块 | `SlateIMBlueprint` |
| `SpinBox` | 创建数值输入框 | `SlateIMBlueprint` |
| `EditableText` | 创建可编辑文本框 | `SlateIMBlueprint` |
| `Image` | 显示图片 | `SlateIMBlueprint` |
| `BeginTable` / `EndTable` | 创建表格容器 | `SlateIMBlueprint` |
| `BeginScrollBox` / `EndScrollBox` | 创建可滚动容器 | `SlateIMBlueprint` |
| `BeginBorder` / `EndBorder` | 创建带背景的容器 | `SlateIMBlueprint` |
| `GraphLinePoints` | 绘制基于点坐标数组的折线图 | `SlateIMBlueprint` |
| `GraphLineValues` | 绘制基于值数组的折线图 | `SlateIMBlueprint` |
| `Padding` | 设置下一个控件的内边距 | `SlateIMBlueprint` |
| `HAlign` / `VAlign` | 设置下一个控件的对齐方式 | `SlateIMBlueprint` |
| `Fill` / `AutoSize` | 设置下一个控件的尺寸策略 | `SlateIMBlueprint` |

### 参数结构体

所有参数结构体均为 `USTRUCT(BlueprintType)`，可在蓝图中直接设置：

| 结构体 | 用途 |
|---|---|
| `FSlateIMWindowParams` | 浮动窗口参数（标题、大小、是否置顶、是否重新打开） |
| `FSlateIMViewportParams` | 视口根节点参数 |
| `FSlateIMTableParams` | 表格参数（选择模式） |
| `FSlateIMTextParams` | 文本参数（颜色） |
| `FSlateIMButtonParams` | 按钮参数（是否启用） |
| `FSlateIMCheckBoxParams` | 复选框参数（标签文本） |
| `FSlateIMSliderParams` | 滑块参数（最小值、最大值、步长） |
| `FSlateIMComboBoxParams` | 下拉框参数（是否强制刷新、是否可搜索） |
| `FSlateIMGraphLinePointsParams` | 折线图参数（X/Y 范围、颜色、线宽） |

### 使用示例（蓝图描述）

创建一个简单的调试窗口：

1. 新建一个 Actor 蓝图，在 `Event Tick` 中调用
2. 使用 `BeginWindowRoot` 节点，UniqueName 填 `"MyDebugWindow"`，Title 填 `"调试工具"`
3. 连接 `Branch` 节点检查返回值（窗口是否打开）
4. 在 True 分支中依次连接 `BeginVerticalStack` → `Text`（显示变量值）→ `Button`（添加操作按钮）→ `EndVerticalStack`
5. 最后连接 `EndRoot`

## C++ 用法

### 头文件引入

```cpp
#include "SlateIM.h"
```

### 基本用法

**最简单的窗口工具**（参考 `SlateIMExamples.h` 中 `FSlateIMTestWindowBase` 的模式）：

```cpp
// MyDebugTool.h
#pragma once
#include "SlateIMWidgetBase.h"

class FMyDebugTool : public FSlateIMWindowBase
{
public:
    FMyDebugTool()
        : FSlateIMWindowBase(
            TEXT("My Debug Tool"),          // 窗口标题
            FVector2f(400, 300),            // 窗口大小
            TEXT("Debug.ToggleMyTool"),     // 控制台命令
            TEXT("Toggles my debug tool"))  // 命令帮助文本
    {}

protected:
    virtual void DrawWindow(float DeltaTime) override;

private:
    float SomeValue = 0.0f;
    bool bSomeToggle = false;
    FString InputText;
};
```

```cpp
// MyDebugTool.cpp
#include "MyDebugTool.h"
#include "SlateIM.h"

void FMyDebugTool::DrawWindow(float DeltaTime)
{
    using namespace SlateIM;
    
    // 垂直布局
    BeginVerticalStack();
    
    // 显示文本
    Text(TEXT("Debug Info"));
    
    // 滑块控制浮点值
    Slider(SomeValue, 0.0f, 100.0f);
    
    // 复选框
    CheckBox(bSomeToggle, TEXT("Enable Feature"));
    
    // 按钮
    if (Button(TEXT("Reset")))
    {
        SomeValue = 0.0f;
        bSomeToggle = false;
    }
    
    EndVerticalStack();
}
```

> 来源：架构模式参考 `Private/Misc/SlateIMExamples.h` 中 `FSlateIMTestWindowWidget` / `FSlateIMTestNomadTabWidget` 的实现

### 表格与树形结构

```cpp
// 创建一个带树形展开的数据表格
SlateIM::BeginTable();

// 表头
SlateIM::BeginTableHeader();
SlateIM::AddTableColumn(FName("Name"), TEXT("名称"));
SlateIM::FixedTableColumnWidth(200.0f);
SlateIM::AddTableColumn(FName("Value"), TEXT("值"));
SlateIM::EndTableHeader();

// 表体
SlateIM::BeginTableBody();
for (int32 i = 0; i < Items.Num(); ++i)
{
    bool bSelected = false;
    if (SlateIM::NextTableCell(&bSelected))
    {
        SlateIM::Text(Items[i].Name);
    }
    if (SlateIM::NextTableCell())
    {
        SlateIM::Text(FString::Printf(TEXT("%f"), Items[i].Value));
    }
    
    // 子行（树形展开）
    if (SlateIM::BeginTableRowChildren(Items[i].Id, true))
    {
        for (const auto& Child : Items[i].Children)
        {
            if (SlateIM::NextTableCell())
                SlateIM::Text(Child.Name);
            if (SlateIM::NextTableCell())
                SlateIM::Text(FString::Printf(TEXT("%f"), Child.Value));
        }
        SlateIM::EndTableRowChildren();
    }
}
SlateIM::EndTableBody();
SlateIM::EndTable();
```

> 来源：API 设计参考 `Public/SlateIM.h` 中 Table 区域的函数声明

### 视口中叠加调试 HUD

```cpp
void DrawViewportDebug(UGameViewportClient* ViewportClient, float DeltaTime)
{
    using namespace SlateIM;
    
    FViewportParams Params;
    Params.Layout.Anchors = FAnchors(0.0f, 0.0f, 0.3f, 1.0f); // 左侧30%
    Params.Layout.ZOrder = 10000;
    Params.Layout.Scale = 1.0f;
    
    if (BeginViewportRoot(FName("DebugHUD"), ViewportClient, Params))
    {
        BeginVerticalStack();
        Text(TEXT("FPS: 60"));
        Text(TEXT("Entities: 1234"));
        EndVerticalStack();
    }
    EndRoot();
}
```

### 进阶用法：嵌入到现有 Slate 层级

```cpp
// FSlateIMExposedBase 允许将即时模式 UI 嵌入传统 Slate 层级
class FMyEmbeddedWidget : public FSlateIMExposedBase
{
public:
    FMyEmbeddedWidget() : FSlateIMExposedBase(TEXT("EmbeddedWidget")) {}

protected:
    virtual void DrawContent(float DeltaTime) override
    {
        using namespace SlateIM;
        BeginVerticalStack();
        Text(TEXT("Embedded Content"));
        if (Button(TEXT("Click Me")))
        {
            // 处理点击
        }
        EndVerticalStack();
    }
};

// 使用时：
FMyEmbeddedWidget EmbeddedWidget;
EmbeddedWidget.EnableWidget();
TSharedRef<SWidget> SlateWidget = EmbeddedWidget.GetExposedWidget();
// 将 SlateWidget 添加到你的 Slate 布局中
```

## Demo 示例

**最小可编译的窗口调试工具**：

```cpp
// MySimpleTool.h
#pragma once
#include "SlateIMWidgetBase.h"

class FMySimpleTool : public FSlateIMWindowBase
{
public:
    FMySimpleTool()
        : FSlateIMWindowBase(
            TEXT("Simple Tool"),
            FVector2f(300, 200),
            TEXT("Tool.ToggleSimple"),
            TEXT("Opens the simple debug tool"))
    {}

protected:
    virtual void DrawWindow(float DeltaTime) override;

private:
    int32 Counter = 0;
    float Speed = 1.0f;
};
```

```cpp
// MySimpleTool.cpp
#include "MySimpleTool.h"
#include "SlateIM.h"

void FMySimpleTool::DrawWindow(float DeltaTime)
{
    using namespace SlateIM;
    
    Counter += static_cast<int32>(Speed * DeltaTime * 100);
    
    BeginVerticalStack();
    
    Text(FString::Printf(TEXT("Counter: %d"), Counter));
    
    BeginHorizontalStack();
    HAlign(HAlign_Left);
    Text(TEXT("Speed:"));
    HAlign(HAlign_Fill);
    Slider(Speed, 0.0f, 10.0f);
    EndHorizontalStack();
    
    if (Button(TEXT("Reset")))
    {
        Counter = 0;
    }
    
    EndVerticalStack();
}

// 在某个模块 StartupModule 中创建实例并启用：
// static TUniquePtr<FMySimpleTool> MyTool;
// MyTool = MakeUnique<FMySimpleTool>();
// MyTool->EnableWidget(); // 注册 Tick 回调，开始绘制
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SlateIMEngine` | 提供引擎相关功能（游戏视口根节点、Canvas 绘制等），SlateIM 的引擎扩展层 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

四个模块的依赖关系：
- `SlateIM` → 依赖 `SlateIMEngine`
- `SlateIMEngine` → 独立（引擎核心功能）
- `SlateIMInGame` → 游戏内 Widget 支持
- `SlateIMBlueprint` → 蓝图函数库封装

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |
| 2026-04-02 | `82179cc5` | Remove parameters from constructor in SlateIM in game widgets and update all existing in widgets | 移除游戏内 Widget 构造函数中的冗余参数 |
| 2026-04-01 | `097a8aca` | SlateIM: Major changes | SlateIM 重大功能更新 |
| 2026-04-01 | `9016fa55` | [Backout] - CL52349724 | 回退了一次改动（可能是某次重大变更被部分撤销后重新提交） |

### 维护评价

SlateIM 于 2025 年 1 月创建，截至 2026 年 5 月约 1 年多历史。从最近的 commit 记录来看：

- **活跃维护**：最近 6 个月内有多次实质性更新，包括"重大功能变更"和持续的代码质量改进
- **实验性状态**：`.uplugin` 标记为 `IsExperimentalVersion=true`，且 `EnabledByDefault=false`，说明 Epic 尚未将其视为稳定 API
- **API 可能变动**：从"Major changes"和"Backout"的 commit 来看，API 仍在积极迭代中
- **推荐使用**：非常适合用于内部调试工具开发，但**不建议在生产代码中深度依赖**，因为 API 可能在未来版本中发生变化。如果仅用于开发阶段的调试和工具搭建，这是一个非常实用的插件

⚠️ **注意**：这是实验性插件，默认未启用。使用前需在项目设置中手动启用，或在 `.uproject` 文件中添加 `"Enabled": true`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateIM)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SlateIM/Source/SlateIM/Private/Misc/SlateIMExamples.h)（示例代码内置于 `SlateIMExamples.h`，需定义 `WITH_SLATEIM_EXAMPLES` 编译宏）