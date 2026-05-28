# Editor Performance

> Plugin that provides Editor Performance feedback to developers（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器性能监控 |
| 分类 | Performance |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EditorPerformance` (Editor), `StallLogSubsystem` (Editor), `CrashDiagnostics` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorPerformance) | |

## 用途

该插件是一个综合性的编辑器性能监控与诊断工具。它旨在帮助开发者识别和定位导致 Unreal Editor 卡顿、崩溃或运行缓慢的根本原因。它通过多个子系统协同工作，收集关键性能指标、记录卡顿事件，并提供崩溃时的诊断信息，最终以状态栏提示和专用诊断面板的形式向开发者反馈，从而提升编辑器的稳定性和响应速度。

## 使用场景

- 当你感觉编辑器在特定操作（如加载资产、蓝图编译）后变得卡顿时，使用此插件分析性能瓶颈。
- 当你需要监控编辑器的长期健康指标，例如磁盘空间剩余量时，可以利用其内置的 KPI 跟踪功能。
- 当编辑器意外崩溃时，希望收集崩溃前的关键诊断信息以帮助定位问题。

## 模块列表

| 模块 | 用途说明 |
|---|---|
| `EditorPerformance` | 插件主模块，负责集成诊断信号（如 TEDS）、驱动状态栏反馈和管理整体诊断流程。 |
| `StallLogSubsystem` | 卡顿日志子系统，负责检测、记录和报告编辑器的卡顿事件。 |
| `CrashDiagnostics` | 崩溃诊断子系统，负责在编辑器崩溃前收集关键上下文信息，并提供诊断面板展示。 |

## 蓝图用法

本插件主要提供编辑器后台监控和诊断功能，不提供面向游戏逻辑的蓝图节点。其诊断信息通过编辑器状态栏和专用的“编辑器诊断”窗口进行展示。

## C++ 用法

本插件的 C++ API 主要面向引擎内部和需要扩展诊断功能的编辑器工具开发者。核心用法包括注册诊断信号处理器和查询性能指标。

### 基本用法

编辑器性能子系统通常在插件或模块启动时初始化，并订阅来自引擎的性能信号。

```cpp
// 来自模块启动逻辑（示例）
void FEditorPerformanceModule::StartupModule()
{
    // 订阅来自 TEDS (Telemetry Data System) 的性能诊断信号
    FEditorPerformanceDiagnostics::Get().SubscribeToDiagnostics();
}
```

## Demo 示例

以下示例展示了如何在一个编辑器工具模块中，通过 C++ 响应来自编辑器性能子系统的诊断信号。

```cpp
// MyEditorToolModule.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyEditorToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    // 用于保存委托句柄，以便在关闭时取消绑定
    FDelegateHandle DiagnosticsHandle;
};
```

```cpp
// MyEditorToolModule.cpp
#include "MyEditorToolModule.h"
#include "EditorPerformanceSubsystem.h" // 假设的主子系统头文件

void FMyEditorToolModule::StartupModule()
{
    // 获取编辑器性能子系统实例
    UEditorPerformanceSubsystem* Subsystem = GEditor->GetEditorSubsystem<UEditorPerformanceSubsystem>();
    if (Subsystem)
    {
        // 绑定一个自定义函数来处理性能诊断事件
        DiagnosticsHandle = Subsystem->OnPerformanceDiagnostic.AddLambda([](const FPerformanceDiagnosticData& Data)
        {
            // 在这里处理诊断数据，例如记录日志或触发自定义警告
            UE_LOG(LogTemp, Warning, TEXT("性能诊断: %s"), *Data.ToString());
        });
    }
}

void FMyEditorToolModule::ShutdownModule()
{
    // 清理时取消事件绑定
    UEditorPerformanceSubsystem* Subsystem = GEditor->GetEditorSubsystem<UEditorPerformanceSubsystem>();
    if (Subsystem && DiagnosticsHandle.IsValid())
    {
        Subsystem->OnPerformanceDiagnostic.Remove(DiagnosticsHandle);
    }
}
```

## 模块依赖

你的模块需要依赖此插件提供的模块才能使用其接口。

| 模块 | 用途 |
|---|---|
| `EditorPerformance` | 主要接口和性能监控逻辑。 |
| `StallLogSubsystem` | 如果你需要查询或扩展卡顿日志功能。 |
| `CrashDiagnostics` | 如果你需要访问或扩展崩溃诊断信息。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `e9acc6db` | EditorPerformance: TEDS-based diagnostic signaling for the status bar | 使用遥测数据系统为状态栏提供诊断信号，提升反馈实时性。 |
| 2026-04-13 | `f5d68e93` | [Crash Diagnostics] Add Crash Diagnostics panel to the Editor Diagnostics window | 新增“崩溃诊断”面板，集中展示崩溃前收集的诊断信息。 |
| 2026-03-30 | `e0fedb7b` | Editor Diagnostics | 新增或增强编辑器诊断框架功能。 |
| 2026-03-30 | `dc530088` | Editor Diagnostics | 新增或增强编辑器诊断框架功能。 |
| 2025-12-19 | `ff7b39f1` | Added Free Disk Space KPIs and removed the free disk space check on editor startup | 增加磁盘空间关键性能指标，并移除了启动时的检查逻辑。 |

### 维护评价

- **活跃维护**：该插件近期（2026年）有密集的功能性更新，包括架构升级（TEDS集成）、新增诊断面板和核心功能（磁盘空间KPI），表明正在积极开发和增强。
- **创建时间**：约1年历史，相对较新。
- **状态**：尽管目录位于 `Experimental`，但根据首次提交信息和后续更新，其功能正在快速完善。已默认启用，表明 Epic 认为其基本可用。
- **推荐使用**：**是**。对于遇到编辑器性能问题的开发者，这是一个强大的内置诊断工具。虽然可能伴随未来 API 的调整，但其核心监控能力已可投入使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorPerformance)
- 官方文档：暂无
- 测试用例：暂无明确公开路径