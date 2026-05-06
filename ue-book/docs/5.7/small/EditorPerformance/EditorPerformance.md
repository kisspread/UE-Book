# Editor Performance

> Plugin that provides Editor Performance feedback to developers

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器性能反馈 |
| 分类 | Performance |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EditorPerformance` (Editor), `StallLogSubsystem` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-09-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorPerformance) | |

## 用途

Editor Performance 插件为编辑器开发者提供实时性能反馈。它会在编辑器状态栏中显示当前编辑器性能状态（正常 / 警告），并通过诊断面板展示关键性能指标（KPI），如启动时间、加载时间、内存占用等。同时支持记录性能快照（Unreal Insights）和遥测事件，帮助开发者追踪和优化编辑器整体性能。它是编辑器性能调优的集成工具。

## 使用场景

- 你正在开发编辑器插件或自定义编辑器功能，希望监控编辑器自身的性能状态。
- 你需要跟踪编辑器的启动、加载地图、PIE（Play In Editor）等阶段的耗时。
- 你想快速查看当前编辑器的内存压力、FPS 等指标，并在状态栏得到视觉反馈。
- 你需要将性能数据记录到 Unreal Insights 或自定义遥测系统进行进一步分析。

## 蓝图用法

无。该插件为纯 C++ 插件，所有功能通过 Slate UI 和模块接口提供，不暴露蓝图表面的节点。

## C++ 用法

### 头文件引入

```cpp
#include "EditorPerformanceModule.h"
```

### 基本用法

在自定义编辑器模块中获取 `FEditorPerformanceModule` 实例，并通过它创建状态栏 Widget 或弹出性能报告选项卡。

```cpp
// 在你的模块 StartupModule 中
void FMyEditorModule::StartupModule()
{
    // 获取 EditorPerformance 模块
    FEditorPerformanceModule& PerfModule = FModuleManager::LoadModuleChecked<FEditorPerformanceModule>("EditorPerformance");

    // 创建状态栏小部件（可添加到编辑器状态栏）
    TSharedRef<SWidget> StatusBarWidget = PerfModule.CreateStatusBarWidget();
    // ... 将 StatusBarWidget 放入你的状态栏布局

    // 注册快捷键 Ctrl+Shift+P 打开性能报告选项卡
    // 实际快捷键由 EditorPerformance 内部注册，你也可以手动调用：
    // PerfModule.ShowPerformanceReportTab();
}
```

### 进阶用法

1. **获取当前 KPI 注册表与数值**

```cpp
FEditorPerformanceModule& PerfModule = FModuleManager::GetModuleChecked<FEditorPerformanceModule>("EditorPerformance");
const FKPIRegistry& Registry = PerfModule.GetKPIRegistry();

// 遍历所有 KPI
for (const auto& Pair : Registry.GetAllValues())
{
    const FKPIValue& Value = Pair.Value;
    // 读取名称、当前值、状态等
    FString Name = Value.DisplayName.ToString();
    float Current = Value.CurrentValue;
    FKPIValue::EState State = Value.GetState();
}
```

2. **记录性能快照到 Unreal Insights**

```cpp
FKPIValue SnapshotValue = /* 从某处获得 */;
PerfModule.RecordInsightsSnaphshot(SnapshotValue);
```

3. **监听编辑器性能状态变化**

```cpp
PerfModule.GetOnPerformanceStateChanged().AddLambda([]()
{
    // 状态更新时执行自定义逻辑
});
```

## Demo 示例

以下是一个最小示例，展示如何在自定义编辑器模块中使用 Editor Performance 插件的状态栏 Widget。

**MyEditorModule.h**
```cpp
#pragma once
#include "Modules/ModuleInterface.h"
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<class SWidget> StatusBarWidget;
};
```

**MyEditorModule.cpp**
```cpp
#include "MyEditorModule.h"
#include "EditorPerformanceModule.h"
#include "Widgets/Docking/SDockTab.h"
#include "Framework/Docking/TabManager.h"

IMPLEMENT_MODULE(FMyEditorModule, MyEditorModule);

void FMyEditorModule::StartupModule()
{
    // 加载 EditorPerformance 模块
    FEditorPerformanceModule& PerfModule = FModuleManager::LoadModuleChecked<FEditorPerformanceModule>("EditorPerformance");

    // 创建状态栏 Widget
    StatusBarWidget = PerfModule.CreateStatusBarWidget();

    // 将 Widget 添加到自定义状态栏（示例：假设存在某个全局状态栏容器）
    // 实际代码需根据你的编辑器布局调整
    // SStatusBar::AddSlot()...
}

void FMyEditorModule::ShutdownModule()
{
    StatusBarWidget.Reset();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ToolMenus` | 注册设置菜单（用于性能报告对话框） |
| `Slate` | 创建 Slate UI 组件 |
| `SlateCore` | Slate 基础类型 |
| `UnrealEd` | 编辑器通用功能（如通知、选项卡） |

> 无其他特殊依赖（标准 Core/Engine 等已省略）。

## 维护状态

### 近期更新

- 2025-09-24 `fe567f78` Editor Diagnostics: Made the status and notification more reactive
- 2025-09-24 `193e083c` Editor Diagnostics
- 2025-09-23 `5c90eb49` Editor Diagnostics status bar styling
- 2025-09-15 `b017b708` Editor Performance Dialog:
- 2025-09-15 `f0e8d613` Enable Editor Performance Tools by default

### 维护评价

该插件于 2025 年 9 月创建，近一个月内持续进行活跃更新，包括 UI 改进、状态栏样式、通知响应等。当前处于早期开发阶段，功能稳定且直接集成到编辑器状态栏，推荐编辑器性能调优场景使用。鉴于其刚刚发布，未来可能会有更多特性添加（如自定义 KPI 阈值、导出报告等）。目前没有发现已知问题或弃用标记。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorPerformance)
- [官方文档](https://docs.unrealengine.com/en-US/EditorPerformance/)（暂缺，.uplugin 中未设置 DocsURL）