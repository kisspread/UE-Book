# Editor Performance

> Plugin that provides Editor Performance feedback to developers

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器性能监控 |
| 分类 | Performance |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EditorPerformance` (Editor), `StallLogSubsystem` (Editor), `CrashDiagnostics` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorPerformance) | |

## 用途

Editor Performance 插件为 Unreal 编辑器提供**实时性能诊断与反馈系统**。它解决的核心问题是：开发者在使用编辑器时，无法直观感知编辑器的性能状态（如启动耗时、内存压力、DDC 缓存效率、卡顿率等），导致性能问题被忽视。

该插件通过 **KPI（关键性能指标）注册表** 系统，持续采集编辑器各阶段的性能数据，包括：

- **编辑器启动阶段**：Boot 时间、初始化时间、资产注册表扫描时间、插件加载数量
- **地图操作阶段**：地图加载时间
- **PIE 阶段**：PIE 启动耗时、首次转场时间、PIE 关闭时间
- **运行时质量指标**：卡顿率（Hitch Rate）、停顿率（Stall Rate）、帧率监控
- **资源与缓存**：Cloud DDC 延迟/读速、DDC 效率、虚拟资产效率
- **系统资源**：可用内存、内存压力、磁盘剩余空间（Engine/Project/User 目录）

所有指标通过状态栏图标和性能报告面板向开发者展示，当指标超过阈值时触发警告或严重告警。

## 使用场景

- 你在开发大型项目，编辑器启动缓慢需要定位瓶颈 → 查看 Editor Boot / Initialize / LoadMap / AssetRegistryScan 等 KPI
- 你在 PIE 中频繁卡顿，需要确认是编辑器侧还是游戏侧问题 → 查看 Editor/PIE 的 Hitch Rate 和 Stall Rate
- 你的项目使用大量 Virtual Assets，需要评估缓存命中率 → 查看 VirtualAssetEfficiency 和 DDC 相关 KPI
- 你需要对比不同场景/配置下的编辑器性能 → 使用 KPI Profile 按地图名存储和切换不同的阈值配置
- 编辑器出现崩溃或长时间停顿 → 通过 StallLogSubsystem 和 CrashDiagnostics 面板获取诊断信息

## 蓝图用法

本插件为 Editor 模块，**不暴露 BlueprintCallable 节点**。所有功能通过 C++ API 调用。

## C++ 用法

### 头文件引入

```cpp
#include "EditorPerformanceModule.h"
#include "KPIValue.h"
```

### 基本用法

**获取模块实例并读取编辑器状态**：

```cpp
// 获取 EditorPerformance 模块
FEditorPerformanceModule& EditorPerfModule = FModuleManager::GetModuleChecked<FEditorPerformanceModule>("EditorPerformance");

// 查询当前编辑器状态
FEditorPerformanceModule::EEditorState State = EditorPerfModule.GetEditorState();
// 可能的值: Editor_Boot, Editor_Initialize, Editor_Interact, PIE_Startup, PIE_Interact, PIE_Shutdown

// 获取 KPI 注册表，读取所有监控指标
const FKPIRegistry& Registry = EditorPerfModule.GetKPIRegistry();
const FKPIValues& AllValues = Registry.GetKPIValues();

for (const auto& Pair : AllValues)
{
    FKPIValue Value;
    if (Registry.GetKPIValue(Pair.Key, Value))
    {
        // Value.Category / Value.Name 标识指标
        // Value.CurrentValue 当前值
        // Value.State: Good / Bad / NotSet
        // Value.Severity: Minor / Major / Critical
    }
}
```

### 进阶用法

**自定义注册 KPI 并设置阈值**：

```cpp
FKPIRegistry& Registry = EditorPerfModule.GetKPIRegistry(); // 需要非 const 引用

// 声明一个新的 KPI
FGuid MyKPI = Registry.DeclareKPIValue(
    FName("Custom"),                          // Category
    FText::FromString(TEXT("自定义指标")),       // DisplayCategory
    FName("LoadTime"),                        // Name
    FText::FromString(TEXT("加载时间")),         // DisplayName
    0.0f,                                     // InitialValue
    TOptional<float>(5.0f),                   // ThresholdValue (5秒)
    FKPIValue::ECompare::GreaterThan,         // Compare: 超过阈值则为 Bad
    FKPIValue::EDisplayType::Seconds          // DisplayType: 秒
);

// 动态更新值
Registry.SetKPIValue(MyKPI, 3.2f);  // 3.2秒，低于阈值 → Good

// 动态修改阈值（如通过 Profile 切换）
Registry.SetKPIThreshold(MyKPI, 2.0f); // 收紧阈值

// 加载 Profile 配置（从 ini 文件）
Registry.LoadKPIProfiles(TEXT("KPIProfiles"), TEXT("EditorPerformance.ini"));

// 应用特定 Profile
FKPIProfile Profile;
Profile.MapName = TEXT("/Game/Maps/HeavyLevel");
// Profile.Thresholds 存储各 KPI 的自定义阈值
Registry.ApplyKPIProfile(Profile);
```

**监听性能状态变化事件**：

```cpp
EditorPerfModule.GetOnPerformanceStateChanged().AddLambda([]()
{
    // 性能状态发生变化时触发（Good → Warning → Critical）
    UE_LOG(LogTemp, Log, TEXT("Editor performance state changed"));
});
```

**显示性能报告面板**：

```cpp
// 打开性能报告停靠标签页
EditorPerfModule.ShowPerformanceReportTab();
```

## Demo 示例

```cpp
// MyPerformanceMonitor.h
#pragma once

#include "CoreMinimal.h"

class FMyPerformanceMonitor
{
public:
    void Initialize();
    void Shutdown();

private:
    FDelegateHandle TickDelegateHandle;
    float AccumulatedTime = 0.0f;

    void OnEditorPerformanceStateChanged();
};

// MyPerformanceMonitor.cpp
#include "MyPerformanceMonitor.h"
#include "EditorPerformanceModule.h"
#include "KPIValue.h"

void FMyPerformanceMonitor::Initialize()
{
    FEditorPerformanceModule& EditorPerfModule =
        FModuleManager::GetModuleChecked<FEditorPerformanceModule>("EditorPerformance");

    // 订阅性能状态变化事件
    EditorPerfModule.GetOnPerformanceStateChanged().AddRaw(
        this, &FMyPerformanceMonitor::OnEditorPerformanceStateChanged);

    // 读取当前所有 KPI 状态
    const FKPIRegistry& Registry = EditorPerfModule.GetKPIRegistry();
    for (const auto& Pair : Registry.GetKPIValues())
    {
        FKPIValue Value;
        if (Registry.GetKPIValue(Pair.Key, Value) && Value.GetState() == FKPIValue::EState::Bad)
        {
            UE_LOG(LogTemp, Warning, TEXT("KPI [%s] 已超阈值: 当前值=%f, 阈值=%f"),
                *Value.Path.ToString(), Value.CurrentValue, Value.ThresholdValue.GetValue());
        }
    }
}

void FMyPerformanceMonitor::Shutdown()
{
    if (FModuleManager::Get().IsModuleLoaded("EditorPerformance"))
    {
        FEditorPerformanceModule& EditorPerfModule =
            FModuleManager::GetModuleChecked<FEditorPerformanceModule>("EditorPerformance");
        EditorPerfModule.GetOnPerformanceStateChanged().RemoveAll(this);
    }
}

void FMyPerformanceMonitor::OnEditorPerformanceStateChanged()
{
    UE_LOG(LogTemp, Log, TEXT("编辑器性能状态已变化"));
}
```

## 模块依赖

从 `.uplugin` 和模块结构分析：

| 模块 | 用途 |
|---|---|
| `EditorDataStorageFeatures` | TEDS（The Editor Data Storage）框架，用于诊断数据的查询和存储 |

其他依赖为 Core、CoreUObject、Engine、Slate 等标准编辑器模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `e9acc6db` | EditorPerformance: TEDS-based diagnostic signaling for the status bar | 使用 TEDS 框架替代状态栏的诊断信号机制 |
| 2026-04-13 | `f5d68e93` | [Crash Diagnostics] Add Crash Diagnostics panel to the Editor Diagnostics window | 在编辑器诊断窗口中新增崩溃诊断面板 |
| 2026-03-30 | `e0fedb7b` | Editor Diagnostics | 编辑器诊断功能重构 |
| 2026-03-30 | `dc530088` | Editor Diagnostics | 编辑器诊断功能更新 |
| 2025-12-19 | `ff7b39f1` | Added Free Disk Space KPIs and removed the free disk space check on editor startup | 新增磁盘剩余空间 KPI，移除启动时的磁盘检查 |

### 维护评价

该插件创建于 2024 年 3 月，标记为**实验性**（位于 Experimental 目录），但 `EnabledByDefault=true` 表明 Epic 已将其内置到默认编辑器工作流中。

**活跃维护**：2025-12 至 2026-04 期间有多次功能性更新，包括新增 KPI 指标（磁盘空间）、新增诊断面板（Crash Diagnostics）、以及架构改进（TEDS 集成）。更新频率约为每月 1-2 次，属于活跃开发状态。

**注意事项**：
- 该插件仍在 Experimental 目录中，API 可能在未来版本中发生变化
- `StallLogSubsystem` 和 `CrashDiagnostics` 作为独立模块存在，功能相对独立但紧密配合
- KPI 系统设计良好，支持 Profile、Threshold、Hint 等扩展机制，适合项目级定制

**推荐使用**：✅ 推荐。作为编辑器性能监控的基础设施，即使在 Experimental 阶段也已默认启用，表明 Epic 认为其足够稳定。适合大型项目的编辑器性能分析和团队协作中的性能基准对比。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorPerformance)
- [官方文档]（无）