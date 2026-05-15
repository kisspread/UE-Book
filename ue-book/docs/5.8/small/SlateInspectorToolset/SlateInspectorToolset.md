# SlateInspectorToolset

> Slate UI automation and inspection tools.

| 属性 | 值 |
|---|---|
| 中文名 | Slate 检查器工具集 |
| 分类 | Toolsets |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateInspectorToolset` (Editor), `SlateInspectorToolsetTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SlateInspectorToolset) | |

## 用途

这是一个为 Unreal Editor 的 Slate UI 系统打造的 **Playwright 风格自动化工具集**，专为 AI Agent 与编辑器 UI 交互而设计。

核心解决的问题：AI Agent（通过 ModelContextProtocol 插件）需要能够"看到"和"操作"编辑器 UI，就像浏览器自动化工具（Playwright/Puppeteer）操作网页一样。该插件提供了：

1. **UI 快照（Snapshot）**：将 Slate 控件树渲染为带缩进的文本表示（类似 Playwright 的 Accessibility Snapshot），AI Agent 可以从中发现可交互元素的 ref 标识符
2. **UI 交互（Actions）**：通过 ref 标识符对控件执行点击、输入文字、拖拽、选择下拉选项等操作
3. **UI 截图（Screenshot）**：对特定控件或整个窗口截图，提供视觉反馈
4. **持续观察（Observe）**：注册观察者持续遍历控件子树（约 100ms 一次），保持 ref 缓存与 UI 变化同步

该插件通过 `UToolsetRegistry` 注册工具集，MCP 插件自动发现并暴露给 AI Agent。与传统的自动化测试不同，它直接使用 Slate 事件 API（`ProcessKeyCharEvent`、`ProcessMouseButtonDownEvent` 等），而非 `AutomationDriver`，因为后者在游戏线程（MCP 工具调用执行的线程）上同步调用会导致死锁。

## 使用场景

- 你正在开发 AI 辅助编辑器工具，需要 AI Agent 能够自动操作编辑器 UI → 使用此工具集通过 MCP 暴露 UI 自动化能力
- 你需要对 Slate UI 进行程序化测试或自动化脚本操作 → 使用 Snapshot + Click/Type/Hover 组合
- 你需要监控编辑器某个面板的 UI 变化 → 使用 Observe 注册观察者，定期获取缓存快照
- 你需要批量填写编辑器中的表单 → 使用 FillForm 一次设置多个字段

## AI 工具 API 用法

该插件的函数标记为 `UFUNCTION(meta = (AICallable))`，专门供 AI Agent 通过 MCP（ModelContextProtocol）系统调用，**不直接暴露为蓝图节点**。所有函数定义在 `USlateInspectorToolset` 类上，均为 `static` 方法。

### 工作流程概览

典型的 AI Agent 操作流程：

```
1. Snapshot("")          → 获取所有顶层窗口的控件树，发现 ref
2. Observe("win1", 30)   → 对目标窗口注册深度观察者
3. Snapshot("win1", 30)  → 获取该窗口的详细控件树
4. Click("b3")           → 点击按钮 b3
5. Type("tb1", "Hello")  → 在文本框 tb1 中输入文字
6. Screenshot("")        → 截图确认当前状态
7. Unobserve("obs-1")    → 完成后移除观察者
```

### 核心工具节点

| 工具函数 | 说明 | 参数 |
|---|---|---|
| `Snapshot` | 获取控件树的文本快照，发现可交互元素的 ref | `Ref`（子树根，空=全部窗口），`MaxDepth`，`bIncludeSourceLocations` |
| `Observe` | 注册观察者持续跟踪控件子树变化 | `Ref`（根控件 ref），`MaxDepth` |
| `Unobserve` | 移除观察者 | `Identifier`（Observe 返回的标识符） |
| `ListObservers` | 列出所有活跃观察者（JSON） | 无 |
| `Screenshot` | 对控件或窗口截图 | `Ref`（空=活动窗口） |
| `Click` | 点击控件 | `Ref`，`Button`（left/right/middle），`DoubleClick`，`Modifiers` |
| `Hover` | 悬停在控件上 | `Ref` |
| `Type` | 向文本输入框输入文字 | `Ref`，`Text`，`Submit`（完成后按回车） |
| `PressKey` | 按下键盘按键（支持修饰键前缀） | `Key`（如 `"Ctrl+C"`、`"Enter"`） |
| `SelectOption` | 选择下拉框选项 | `Ref`，`Value`（选项文本） |
| `Drag` | 从一个控件拖拽到另一个 | `StartRef`，`EndRef`，`Modifiers` |
| `Windows` | 列表/选中/关闭顶层编辑器窗口 | `Action`（list/select/close），`Index` |
| `WaitFor` | 检查文本是否存在于控件树中 | `Text`（必须存在），`TextGone`（必须不存在） |
| `FillForm` | 批量填写多个表单字段 | `Fields`（Ref/Value/FieldType 数组） |

### Ref 标识符格式

Ref 根据控件角色（role）使用不同前缀，例如：
- `b1`, `b2`, `b3` — 按钮（Button）
- `tb1`, `tb2` — 文本框（TextBox）
- `cb1`, `cb2` — 复选框（CheckBox）
- `cbx1` — 下拉框（ComboBox）

## C++ 用法

### 头文件引入

```cpp
#include "SlateInspectorToolset.h"
#include "SlateInspectorToolsetObserverManager.h"
#include "SlateInspectorToolsetRefCache.h"
#include "SlateInspectorToolsetSnapshotRenderer.h"
```

### 基本用法：获取控件树快照

`FSlateInspectorToolsetSnapshotRenderer::Render()` 是快照的核心函数，将 Slate 控件树渲染为缩进文本。

```cpp
// 来源: Public/SlateInspectorToolsetSnapshotRenderer.h

// 获取所有顶层窗口的控件树快照（深度 30 层）
FString SnapshotText = FSlateInspectorToolsetSnapshotRenderer::Render(
    nullptr,  // nullptr = 所有顶层窗口
    30,       // MaxDepth
    false,    // bIncludeSourceLocations
    true      // bResetCache = true，清除旧 ref 缓存后重新分配
);

// 对特定控件子树进行快照
TSharedPtr<SWidget> MyWindowWidget = /* 获取某个窗口控件 */;
FString SubtreeSnapshot = FSlateInspectorToolsetSnapshotRenderer::Render(
    MyWindowWidget,
    15,    // 只遍历 15 层深
    true,  // 包含源码位置 [src=File:Line]
    true
);
```

### 基本用法：管理 Ref 缓存

`FSlateInspectorToolsetRefCache` 负责 widget 和 ref 标识符之间的双向映射。

```cpp
// 来源: Public/SlateInspectorToolsetRefCache.h

FSlateInspectorToolsetRefCache& Cache = FSlateInspectorToolsetRefCache::Get();

// 为控件分配 ref（角色前缀由快照渲染器决定）
TSharedRef<SButton> MyButton = SNew(SButton);
FString Ref = Cache.GetOrAssignRef(MyButton, TEXT("b"));
// Ref = "b1"（第一个按钮）

// 通过 ref 反向查找活控件
TSharedPtr<SWidget> Resolved = Cache.ResolveRef(Ref);
if (Resolved.IsValid())
{
    // 控件仍然存在，可以操作
}

// 查看控件是否已有 ref（不分配新 ref）
FString ExistingRef = Cache.FindRef(MyButton);

// 清除所有映射并重置计数器（仅手动快照时使用，观察者模式不应调用）
Cache.Reset();

// 清除已销毁控件的映射条目（由 ObserverManager 定期调用）
Cache.PurgeExpired();
```

### 基本用法：注册观察者持续监控

```cpp
// 来源: Public/SlateInspectorToolsetObserverManager.h

FSlateInspectorToolsetObserverManager& Manager = FSlateInspectorToolsetObserverManager::Get();

// 注册观察者：监控某个控件子树，深度 20 层
TSharedPtr<SWidget> TargetPanel = /* 目标面板控件 */;
FString ObserverId = Manager.AddObserver(TargetPanel, 20);

// 获取观察者的缓存快照文本
FString CachedText = Manager.GetCachedSnapshot(ObserverId);

// 智能查找匹配的观察者（null RootWidget 匹配根观察者）
FString BestSnapshot = Manager.FindMatchingObserverSnapshot(nullptr, 10);

// 获取所有活跃观察者
TArray<FSlateInspectorToolsetObserver> AllObservers = Manager.GetObservers();
for (const auto& Obs : AllObservers)
{
    UE_LOG(LogTemp, Log, TEXT("Observer %s: Root=%s, Depth=%d, CachedTextLen=%d"),
        *Obs.Identifier,
        Obs.bRoot ? TEXT("ALL") : *Obs.RootWidget.Pin()->GetTypeAsString(),
        Obs.MaxDepth,
        Obs.CachedSnapshotText.Len());
}

// 移除观察者
Manager.RemoveObserver(ObserverId);
```

### 进阶用法：自定义快照渲染

你可以为自定义 Slate 控件类型注册角色、标签提取器和状态标志提取器。

```cpp
// 来源: Public/SlateInspectorToolsetSnapshotRenderer.h

// 为自定义控件类型注册角色（出现在快照中时显示的角色名和 ref 前缀）
FSlateInspectorToolsetSnapshotRenderer::RegisterWidgetRole(
    FName("SMyCustomWidget"),   // 控件类型名
    TEXT("custom-widget"),      // 角色名
    TEXT("cw")                  // ref 前缀 → cw1, cw2, cw3...
);

// 注册自定义标签提取器（控件在快照中显示的文本标签）
FSlateInspectorToolsetSnapshotRenderer::RegisterLabelExtractor(
    FName("SMyCustomWidget"),
    [](TSharedRef<SWidget> Widget) -> FString
    {
        TSharedRef<SMyCustomWidget> Typed = StaticCastSharedRef<SMyCustomWidget>(Widget);
        return Typed->GetDisplayText().ToString();
    }
);

// 注册自定义状态标志提取器（控件在快照中显示的状态，如 [enabled] [checked]）
FSlateInspectorToolsetSnapshotRenderer::RegisterStateFlagsExtractor(
    FName("SMyCustomWidget"),
    [](TSharedRef<SWidget> Widget) -> TArray<FString>
    {
        TArray<FString> Flags;
        TSharedRef<SMyCustomWidget> Typed = StaticCastSharedRef<SMyCustomWidget>(Widget);
        if (Typed->IsActive())   Flags.Add(TEXT("active"));
        if (Typed->IsFocused())  Flags.Add(TEXT("focused"));
        return Flags;
    }
);
```

### 进阶用法：使用 AI 工具 API

所有 `UFUNCTION(meta = (AICallable))` 的函数均为 `static`，可从 C++ 直接调用。

```cpp
// 来源: Public/SlateInspectorToolset.h

// 获取所有窗口的快照
FString AllWindows = USlateInspectorToolset::Snapshot("", 30, false);

// 对特定控件子树注册深度观察
FString ObsId = USlateInspectorToolset::Observe("win1", 30);

// 对控件执行交互操作
USlateInspectorToolset::Click("b3", "left", false);           // 左键单击按钮 b3
USlateInspectorToolset::Type("tb1", "Hello World", true);     // 输入文字并按回车
USlateInspectorToolset::Hover("b2");                          // 悬停按钮 b2
USlateInspectorToolset::SelectOption("cbx1", "Option A");     // 选择下拉选项

// 带修饰键的点击
FSlateInspectorToolsetModifierKeys Mods;
Mods.bCtrl = true;
USlateInspectorToolset::Click("b5", "left", false, Mods);     // Ctrl+单击

// 拖拽操作
USlateInspectorToolset::Drag("item1", "target1");             // 从 item1 拖到 target1

// 按键操作
USlateInspectorToolset::PressKey("Ctrl+A");                   // 全选
USlateInspectorToolset::PressKey("Enter");                     // 回车

// 窗口管理
FString WindowList = USlateInspectorToolset::Windows("list");  // 列出所有窗口
USlateInspectorToolset::Windows("select", 0);                  // 选中第一个窗口
USlateInspectorToolset::Windows("close", 2);                   // 关闭第三个窗口

// 等待条件
bool bReady = USlateInspectorToolset::WaitFor("Save Complete", "Loading...");

// 截图
FToolsetImage Img = USlateInspectorToolset::Screenshot("b3"); // 截取按钮 b3

// 批量填表
TArray<FSlateInspectorToolsetFormField> Fields;
FSlateInspectorToolsetFormField Field1;
Field1.Ref = "tb1"; Field1.Value = "My Object"; Field1.FieldType = "textbox";
Fields.Add(Field1);
FSlateInspectorToolsetFormField Field2;
Field2.Ref = "cb1"; Field2.Value = "true"; Field2.FieldType = "checkbox";
Fields.Add(Field2);
USlateInspectorToolset::FillForm(Fields);
```

## 模块依赖

从源码分析，该插件的独特依赖如下：

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 提供 `UToolsetDefinition` 基类和工具注册框架，MCP 通过此发现工具 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。该插件以插件形式依赖 `ToolsetRegistry`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-18 | `6471b168` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | 修改了工具集定义中 UFunction 如何被识别为工具的机制 |
| 2026-04-17 | `8c911af5` | [Backout] - CL52878047 | 回退了上一次提交的改动 |
| 2026-04-17 | `9404cd3e` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | 修改了工具集定义中 UFunction 如何被识别为工具的机制（后被回退） |
| 2026-04-13 | `69570138` | [SlateInspectorToolset] Move `SlateInspectorToolset` tests from `Editor` to `AI.Toolsets` category. | 将测试用例从 Editor 分类迁移到 AI.Toolsets 分类 |
| 2026-04-03 | `7f02bd73` | [AI Toolsets]: Move all toolsets to load at post engine init to simplify registration when toolset r | 将所有工具集加载阶段改为 PostEngineInit，简化注册时机 |

### 维护评价

- **活跃维护中**：插件创建仅约 2 周，最近一周内有 5 次提交，处于密集开发阶段
- **实验性状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需手动启用
- **注意**：提交记录显示存在回退（backout）操作，说明工具注册机制仍在快速迭代和调整中，API 可能不稳定
- **风险提示**：该插件与 MCP/AIAssistant 基础设施紧密耦合，`UToolsetDefinition` 基类和工具发现机制可能随时变化
- **建议**：适合跟踪研究 Epic 的 AI 辅助编辑器方向，暂不建议在生产环境依赖。需额外启用 `ToolsetRegistry` 插件才能工作

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SlateInspectorToolset)
- [官方文档]()（无）