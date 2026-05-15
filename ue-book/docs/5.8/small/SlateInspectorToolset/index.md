# Slate Inspector Toolset

> Slate UI automation and inspection tools.

| 属性 | 值 |
|---|---|
| 中文名 | Slate检查工具集 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateInspectorToolset` (Editor), `SlateInspectorToolsetTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SlateInspectorToolset) | |

## 用途
SlateInspectorToolset 是一个实验性的编辑器插件，为 UE5 编辑器提供一套用于自动化检查和调试 Slate UI 界面的工具集。它主要服务于引擎和编辑器 UI 的开发与测试，允许开发者程序化地创建、检查和验证 Slate 控件的行为与属性。该插件旨在作为一套“工具集”（Toolset）集成到更宏大的 AI Assistant 工具集框架中，用于支持自动化 UI 测试和检查任务。

## 使用场景
- 你需要开发、调试或测试自定义的 Slate UI 控件或编辑器面板。
- 你需要自动化验证 Slate UI 的层级结构、可见性、布局或交互逻辑。
- 你正在为引擎的 AI 辅助工具集（Toolset）系统添加新的 UI 检查与自动化能力。

## 蓝图用法
该插件主要提供 C++ API，蓝图可直接调用的接口较少。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateToolsetInstance` | 创建并获取一个 `USlateInspectorToolset` 工具集实例，用于执行后续的检查操作。 | `USlateInspectorToolset` |

## C++ 用法
### 头文件引入
```cpp
#include "SlateInspectorToolset.h"
```

### 基本用法
从工具集系统中获取一个 Slate 检查器实例并开始使用。
```cpp
// 获取工具集管理器（通常通过全局访问点）
UToolsetSubsystem* ToolsetSubsystem = GEditor->GetEditorSubsystem<UToolsetSubsystem>();
// 查找或创建 SlateInspectorToolset 实例
USlateInspectorToolset* SlateToolset = Cast<USlateInspectorToolset>(ToolsetSubsystem->FindToolset(USlateInspectorToolset::StaticClass()));
// 使用工具集进行检查
if (SlateToolset)
{
    // ... 执行 Slate UI 的自动化检查操作 ...
}
```

## Demo 示例
一个最小的示例，展示如何在编辑器工具中集成并调用该工具集。
```cpp
// MyEditorTool.h
#pragma once
#include "CoreMinimal.h"
#include "SlateInspectorToolset.h"

class FMyEditorTool
{
public:
    void RunSlateCheck();
};

// MyEditorTool.cpp
#include "MyEditorTool.h"
#include "ToolsetSubsystem.h"
#include "SlateInspectorToolset.h"

void FMyEditorTool::RunSlateCheck()
{
    UToolsetSubsystem* Subsystem = GEditor->GetEditorSubsystem<UToolsetSubsystem>();
    if (USlateInspectorToolset* Inspector = Cast<USlateInspectorToolset>(Subsystem->FindToolset(USlateInspectorToolset::StaticClass())))
    {
        // 此处可以使用 Inspector 实例执行具体的检查逻辑
        UE_LOG(LogTemp, Log, TEXT("Slate Inspector Toolset found and ready."));
    }
}
```

## 模块依赖
无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-18 | `6471b168` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | 修改工具集定义识别工具函数的逻辑。 |
| 2026-04-17 | `8c911af5` | [Backout] - CL52878047 | 撤销了一次代码提交。 |
| 2026-04-17 | `9404cd3e` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | 同上，一次被回退的修改。 |
| 2026-04-13 | `69570138` | [SlateInspectorToolset] Move `SlateInspectorToolset` tests from `Editor` to `AI.Toolsets` category. | 将测试类别的分类从“Editor”移至“AI.Toolsets”。 |
| 2026-04-03 | `7f02bd73` | [AI Toolsets]: Move all toolsets to load at post engine init to simplify registration when toolset r | 调整工具集加载阶段至引擎初始化后，以简化注册流程。 |

### 维护评价
该插件**处于活跃的初期开发阶段**。创建于 2026 年 4 月，并在创建后的一周内有多次提交。提交内容集中在调整加载时序、测试分类以及核心的工具定义逻辑。由于是实验性插件（`IsExperimentalVersion=true` 且 `EnabledByDefault=false`），其 API 和行为可能发生较大变化。目前推荐用于内部实验和开发，不建议在正式生产项目中稳定依赖。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SlateInspectorToolset)
- 官方文档：无
- 测试用例：无明确公开路径