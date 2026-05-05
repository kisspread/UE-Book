# SlateInspectorToolset

> Slate UI automation and inspection tools.

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateInspectorToolset` (Editor), `SlateInspectorToolsetTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SlateInspectorToolset) | |

## 用途

SlateInspectorToolset 提供了一套 **Playwright 风格的 Slate UI 自动化工具**，用于以编程方式驱动 Unreal Editor 的界面操作。它解决的核心问题是：**如何让 AI Agent 或自动化脚本像人类一样"看到"和"操作"编辑器 UI**。

具体来说，它做了三件事：

1. **快照（Snapshot）**：将 Slate 控件树渲染为文本格式的可访问性快照，包含控件角色、标签、状态和短引用标识符（ref），让 AI 能理解当前 UI 结构
2. **交互（Interaction）**：通过直接调用 Slate 事件 API（`ProcessKeyCharEvent`、`ProcessMouseButtonDownEvent` 等）模拟点击、输入、拖拽等操作，而非使用 AutomationDriver（后者在游戏线程上会死锁）
3. **观察（Observation）**：通过 Observer 机制持续追踪控件子树变化，保持 ref 缓存实时更新

该插件通过 `UToolsetRegistry` 注册，供 ModelContextProtocol（MCP）插件自动发现和调用。

## 使用场景

- 你正在开发 AI Agent 来自动操作 Unreal Editor → 用 SlateInspectorToolset 提供 UI 感知和交互能力
- 你需要编写编辑器 UI 的自动化测试脚本 → 用 Snapshot 获取控件树，用 Click/Type 等模拟用户操作
- 你需要调试 Slate 控件的层级结构 → 用 Snapshot 生成可读的控件树文本

## 蓝图用法

所有工具函数均标记为 `UFUNCTION(meta = (AICallable))`，主要供 AI/MCP 系统调用，也可在蓝图中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Snapshot` | 捕获 Slate 控件树的文本快照，返回带缩进的控件列表 | `USlateInspectorToolset` |
| `Observe` | 注册观察者持续追踪控件子树变化（~100ms 刷新） | `USlateInspectorToolset` |
| `Unobserve` | 移除观察者 | `USlateInspectorToolset` |
| `Click` | 模拟鼠标点击指定 ref 的控件 | `USlateInspectorToolset` |
| `Type` | 模拟键盘输入文本 | `USlateInspectorToolset` |
| `Hover` | 模拟鼠标悬停 | `USlateInspectorToolset` |
| `FillForm` | 批量填写表单字段（文本框、复选框、下拉框） | `USlateInspectorToolset` |
| `Scroll` | 模拟滚轮滚动 | `USlateInspectorToolset` |
| `PressKey` | 模拟按键事件 | `USlateInspectorToolset` |
| `Drag` | 模拟鼠标拖拽操作 | `USlateInspectorToolset` |
| `Screenshot` | 截取当前 UI 截图 | `USlateInspectorToolset` |

### 使用示例（蓝图描述）

典型的 AI Agent 操作流程：

1. 调用 `Snapshot`（Ref 为空）获取所有顶层窗口列表
2. 调用 `Observe`（Ref 为目标窗口 ref）开始深度观察该窗口
3. 再次调用 `Snapshot`（Ref 为窗口 ref）获取窗口内部控件树
4. 根据快照中的 ref 标识符，调用 `Click`、`Type` 等进行交互
5. 操作完成后调用 `Unobserve` 停止观察

## C++ 用法

### 头文件引入

```cpp
#include "SlateInspectorToolset.h"
#include "SlateInspectorToolsetRefCache.h"
#include "SlateInspectorToolsetSnapshotRenderer.h"
#include "SlateInspectorToolsetObserverManager.h"
```

### 基本用法：获取控件快照

```cpp
// 捕获所有顶层窗口的快照
FString AllWindowsSnapshot = USlateInspectorToolset::Snapshot("", 30, false);

// 捕获指定子树的快照（使用之前获取的 ref）
FString SubtreeSnapshot = USlateInspectorToolset::Snapshot("w1", 30, true);
// bIncludeSourceLocations=true 会在每个控件后附加 [src=File:Line] 标签
```

### 基本用法：模拟交互

```cpp
// 模拟点击按钮（ref 为 "b3"）
FSlateInspectorToolsetModifierKeys Mods;
Mods.bShift = false;
Mods.bCtrl = false;
USlateInspectorToolset::Click("b3", Mods);

// 模拟在文本框中输入
USlateInspectorToolset::Type("tb1", TEXT("Hello World"));

// 模拟鼠标悬停
USlateInspectorToolset::Hover("b5");
```

### 进阶用法：批量填写表单

```cpp
// 使用 FillForm 一次性填写多个表单字段
TArray<FSlateInspectorToolsetFormField> Fields;

FSlateInspectorToolsetFormField NameField;
NameField.Ref = "tb1";
NameField.Value = "MyProject";
NameField.FieldType = "textbox";
Fields.Add(NameField);

FSlateInspectorToolsetFormField CheckboxField;
CheckboxField.Ref = "cb2";
CheckboxField.Value = "true";
CheckboxField.FieldType = "checkbox";
Fields.Add(CheckboxField);

FSlateInspectorToolsetFormField ComboField;
ComboField.Ref = "dd3";
ComboField.Value = "Option2";
ComboField.FieldType = "combobox";
Fields.Add(ComboField);

USlateInspectorToolset::FillForm(Fields);
```

### 进阶用法：直接使用 ObserverManager 和 RefCache

```cpp
// 获取观察者管理器单例
FSlateInspectorToolsetObserverManager& ObserverMgr = FSlateInspectorToolsetObserverManager::Get();

// 手动添加观察者
TSharedPtr<SWidget> MyWidget = /* ... */;
FString ObserverId = ObserverMgr.AddObserver(MyWidget, 20);

// 获取缓存的快照
FString CachedSnapshot = ObserverMgr.GetCachedSnapshot(ObserverId);

// 移除观察者
ObserverMgr.RemoveObserver(ObserverId);

// 直接使用 RefCache 进行控件查找
FSlateInspectorToolsetRefCache& RefCache = FSlateInspectorToolsetRefCache::Get();

// 通过 ref 解析控件
TSharedPtr<SWidget> Widget = RefCache.ResolveRef("b3");

// 查找控件的 ref
FString Ref = RefCache.FindRef(MyWidget.ToSharedRef());
```

### 进阶用法：自定义快照渲染

```cpp
// 注册自定义控件类型的角色映射
FSlateInspectorToolsetSnapshotRenderer::RegisterWidgetRole(
    FName("SMyCustomWidget"), "custom", "cust");

// 注册自定义标签提取器
FSlateInspectorToolsetSnapshotRenderer::RegisterLabelExtractor(
    FName("SMyCustomWidget"),
    [](TSharedRef<SWidget> Widget) -> FString
    {
        // 从自定义控件提取显示文本
        return TEXT("MyLabel");
    });

// 注册自定义状态标志提取器
FSlateInspectorToolsetSnapshotRenderer::RegisterStateFlagsExtractor(
    FName("SMyCustomWidget"),
    [](TSharedRef<SWidget> Widget) -> TArray<FString>
    {
        return { TEXT("enabled"), TEXT("visible") };
    });
```

## Demo 示例

一个最小的编辑器子系统，注册自定义控件后获取快照：

```cpp
// MySnapshotDemoSubsystem.h
#pragma once

#include "EditorSubsystem.h"
#include "MySnapshotDemoSubsystem.generated.h"

UCLASS()
class UMySnapshotDemoSubsystem : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    /** 演示：获取当前编辑器 UI 快照 */
    UFUNCTION(Exec)
    void DemoSnapshot();
};
```

```cpp
// MySnapshotDemoSubsystem.cpp
#include "MySnapshotDemoSubsystem.h"
#include "SlateInspectorToolset.h"
#include "SlateInspectorToolsetSnapshotRenderer.h"

void UMySnapshotDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 注册自定义控件类型，使其出现在快照中
    FSlateInspectorToolsetSnapshotRenderer::RegisterWidgetRole(
        FName("SMyGamePanel"), "panel", "pnl");
}

void UMySnapshotDemoSubsystem::DemoSnapshot()
{
    // 获取所有顶层窗口的快照（包含源码位置）
    FString Snapshot = USlateInspectorToolset::Snapshot("", 30, true);

    // 输出到日志
    UE_LOG(LogTemp, Log, TEXT("=== Slate UI Snapshot ===\n%s"), *Snapshot);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 提供 `UToolsetDefinition` 基类和工具集注册机制 |
| `ToolsetRegistry` (插件依赖) | 整个插件依赖 ToolsetRegistry 插件 |

## 维护状态

### 近期更新

- 2026-04-18 `6471b168` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.
- 2026-04-17 `8c911af5` [Backout] - CL52878047
- 2026-04-17 `9404cd3e` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.
- 2026-04-13 `69570138` [SlateInspectorToolset] Move `SlateInspectorToolset` tests from `Editor` to `AI.Toolsets` category.
- 2026-04-03 `7f02bd73` [AI Toolsets]: Move all toolsets to load at post engine init to simplify registration when toolset r

### 维护评价

- **创建时间**：2026-04-03，非常新的插件
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- **维护状态**：🆕 全新插件，尚无后续更新记录
- **已知限制**：
  - 输入模拟使用直接 Slate 事件 API 而非 AutomationDriver，因为后者在游戏线程上会死锁
  - Observer 每 ~100ms 刷新一次，高频 UI 变化可能有延迟
  - Ref 在控件销毁后不会被重用（可能看到 b1, b3, b7 跳号）
- **推荐程度**：作为实验性插件，适合在 AI Agent / MCP 场景中试用，不建议用于生产环境的关键自动化流程

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SlateInspectorToolset)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SlateInspectorToolset/Source/SlateInspectorToolsetTests)