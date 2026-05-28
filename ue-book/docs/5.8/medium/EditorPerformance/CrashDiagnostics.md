# Editor Performance

> Plugin that provides Editor Performance feedback to developers

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器性能诊断 |
| 分类 | Performance |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EditorPerformance` (Editor), `StallLogSubsystem` (Editor), `CrashDiagnostics` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorPerformance) | |

## 用途

EditorPerformance 是一个面向编辑器开发者的性能与稳定性诊断插件。它解决的核心问题是：**开发者在使用 UE5 编辑器时，如何及时了解编辑器的性能状况和崩溃历史**。

该插件包含三个子模块：

1. **CrashDiagnostics（崩溃诊断）**：从 `Saved` 目录收集崩溃报告数据，将其导入编辑器数据存储（TEDS）系统，并提供可视化面板供开发者浏览、搜索和分析历史崩溃记录。支持检测上一次会话是否崩溃，以及是否存在未读崩溃报告。
2. **EditorPerformance（编辑器性能）**：提供编辑器级别的性能反馈机制（如状态栏性能指标）。
3. **StallLogSubsystem（卡顿日志子系统）**：记录编辑器卡顿事件。

该插件依赖 `EditorDataStorageFeatures` 插件，使用 TEDS（The Editor Data Storage）架构来存储和查询崩溃数据。

## 使用场景

- 你是一名引擎开发者或技术美术 → 需要监控编辑器运行时的性能和稳定性
- 你的编辑器频繁崩溃 → 用 CrashDiagnostics 面板查看崩溃历史，分析崩溃模式和调用栈
- 你需要知道上次编辑器会话是否正常退出 → 用 `HasCrashedLastSession()` 检测
- 你需要在编辑器状态栏展示性能指标 → 使用 EditorPerformance 模块的 TEDS 诊断信号
- 你需要跟踪编辑器卡顿事件 → 使用 StallLogSubsystem

## 蓝图用法

该插件为 Editor 类型模块，主要提供 C++ API 和 Slate UI，不暴露蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "CrashDiagnosticsModule.h"
```

### 基本用法

获取崩溃诊断模块单例并检查上次会话状态：

```cpp
#include "CrashDiagnosticsModule.h"

using namespace UE::Editor::CrashDiagnostics;

// 获取模块实例
FCrashDiagnosticsModule& CrashModule = FCrashDiagnosticsModule::GetChecked();

// 检查上次会话是否发生崩溃
if (CrashModule.HasCrashedLastSession())
{
    UE_LOG(LogTemp, Warning, TEXT("Editor crashed during the last session!"));
}

// 检查是否有未读的崩溃报告
if (CrashModule.HasUnreadCrashes())
{
    UE_LOG(LogTemp, Warning, TEXT("There are unread crash reports."));
}
```

### 进阶用法

从磁盘检索崩溃报告并添加到数据存储系统：

```cpp
#include "CrashDiagnosticsModule.h"
#include "Columns/TedsCrashColumns.h"

using namespace UE::Editor::CrashDiagnostics;

// 方式一：异步加载（推荐，在后台线程读取文件后在 GameThread 写入 TEDS）
FCrashDiagnosticsModule::GetChecked().AddCrashesToDataStorageAsync();

// 方式二：手动控制 — 先同步检索，再手动添加
TArray<TSharedRef<FPrimaryCrashProperties>> Crashes = FCrashDiagnosticsModule::RetrieveSavedCrashes();

// 可以对 Crashes 进行过滤或处理后再写入
FCrashDiagnosticsModule::GetChecked().AddCrashesToDataStorage(DataStorage, Crashes);
```

### 数据列查询

使用崩溃数据列进行查询（配合 TEDS 查询系统）：

```cpp
#include "Columns/TedsCrashColumns.h"

// 崩溃数据包含以下列，可用于 TEDS 查询：
// FEditorCrashTimeColumn        - 崩溃时间
// FEditorCrashGUIDColumn        - 崩溃唯一标识
// FEditorCrashErrorMessageColumn - 错误信息
// FEditorCrashCallStackColumn   - 调用栈
// FEditorCrashSourceContextColumn - 源码上下文
// FEditorCrashTypeColumn        - 崩溃类型
// FEditorCrashFileReportsColumn - 关联的文件报告路径
// FEditorCrashUserActivityHintColumn - 用户操作提示

// 标签（Tags）用于标记状态：
// FEditorCrashIsEnsureTag       - 是 Ensure 而非崩溃
// FEditorCrashIsOOMTag          - 内存不足导致
// FEditorCrashIsNewTag          - 新崩溃（未读）
// FEditorCrashLastSessionTag    - 上次会话的崩溃
```

## Demo 示例

以下示例展示如何创建一个自定义的崩溃监控工具，检测编辑器上次会话崩溃并触发报告：

```cpp
// MyCrashMonitor.h
#pragma once

#include "CoreMinimal.h"

class FMyCrashMonitor
{
public:
    static void Initialize();
    static void CheckAndReportCrashes();

private:
    static void OnCrashPanelRequested();
};
```

```cpp
// MyCrashMonitor.cpp
#include "MyCrashMonitor.h"
#include "CrashDiagnosticsModule.h"

void FMyCrashMonitor::Initialize()
{
    using namespace UE::Editor::CrashDiagnostics;

    FCrashDiagnosticsModule& CrashModule = FCrashDiagnosticsModule::GetChecked();

    // 异步加载崩溃数据到 TEDS
    CrashModule.AddCrashesToDataStorageAsync();

    CheckAndReportCrashes();
}

void FMyCrashMonitor::CheckAndReportCrashes()
{
    using namespace UE::Editor::CrashDiagnostics;

    FCrashDiagnosticsModule& CrashModule = FCrashDiagnosticsModule::GetChecked();

    if (CrashModule.HasCrashedLastSession())
    {
        UE_LOG(LogTemp, Warning, TEXT("上次编辑器会话发生了崩溃！"));
    }

    // 创建崩溃日志面板（可嵌入自定义窗口）
    TSharedRef<SWidget> CrashPanel = CrashModule.CreateCrashLogPanel();
}

void FMyCrashMonitor::OnCrashPanelRequested()
{
    // 手动检索所有崩溃记录
    TArray<TSharedRef<FPrimaryCrashProperties>> Crashes =
        UE::Editor::CrashDiagnostics::FCrashDiagnosticsModule::RetrieveSavedCrashes();

    for (const auto& Crash : Crashes)
    {
        UE_LOG(LogTemp, Log, TEXT("Found crash: %s"), *Crash->CrashGUID);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorDataStorageFeatures` | TEDS 编辑器数据存储特性，用于存储和查询崩溃数据 |
| `ToolWidgets` | 编辑器工具栏和状态栏小部件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `e9acc6db` | EditorPerformance: TEDS-based diagnostic signaling for the status bar | 基于 TEDS 的状态栏性能诊断信号 |
| 2026-04-13 | `f5d68e93` | [Crash Diagnostics] Add Crash Diagnostics panel to the Editor Diagnostics window | 新增崩溃诊断面板到编辑器诊断窗口 |
| 2026-03-30 | `e0fedb7b` | Editor Diagnostics | 编辑器诊断功能更新 |
| 2026-03-30 | `dc530088` | Editor Diagnostics | 编辑器诊断功能更新 |
| 2025-12-19 | `ff7b39f1` | Added Free Disk Space KPIs and removed the free disk space check on editor startup | 新增磁盘空间 KPI，移除启动时磁盘检查 |

### 维护评价

该插件**活跃维护中**，自 2024 年 3 月创建以来持续有实质性更新：

- **2025-12**：添加磁盘空间 KPI 指标
- **2026-03/04**：密集更新，新增崩溃诊断面板、TEDS 状态栏信号等功能

从 commit 内容来看，该插件正在从基础功能逐步扩展为完整的编辑器诊断套件。插件目前仍在 `Experimental` 目录下，但 `EnabledByDefault=true` 且 `IsBetaVersion=false`，说明 Epic 认为其基本功能已稳定。

⚠️ **注意**：该插件位于 `Experimental` 目录，API 可能会在未来版本中发生变化。

✅ **推荐使用**：对于需要监控编辑器性能和稳定性的开发者，推荐使用。该插件功能明确、维护活跃，且默认启用无需额外配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorPerformance)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorPerformance/Tests)