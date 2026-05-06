# Mass Insights

> Plugin to gather insights into Mass execution

| 属性 | 值 |
|---|---|
| 中文名 | Mass 执行洞察 |
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MassInsightsAnalysis` (EditorAndProgram), `MassInsightsUI` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MassInsights) | |

## 用途

Mass Insights 是一个专为 Unreal Engine 的 **Mass（大规模智能体系统）** 设计的性能分析插件。它通过 Trace 系统采集 Mass 执行过程中的关键事件，包括：

- Fragment 注册与属性信息
- Archetype（原型）的创建与构成
- 实体批量添加、移动和销毁
- 执行阶段（Phase）的开始与结束（Timing Region）

这些数据被组织为 **Provider**，可在 **Unreal Insights**（性能分析工具）中展示为自定义时间线、统计表格和事件列表，帮助开发者深入理解 Mass 系统的运行时行为，定位性能瓶颈和逻辑错误。

## 使用场景

- **性能调优**：观察实体在 Archetype 间的迁移频率，分析 Fragments 的分布，发现不必要的实体操作。
- **调试复杂系统**：追踪特定实体在多个 Phase 中的状态变化，验证 Mass 处理器执行顺序。
- **自定义分析仪表板**：利用 Provider 提供的枚举接口，在 Unreal Insights 中构建自定义可视化面板（如实体密度热图、Phase 耗时统计）。

## 蓝图用法

该插件**不暴露任何蓝图可调用函数或属性**。所有功能均通过 C++ 接口和 Unreal Insights 的 Trace 分析管道实现，仅适用于编辑器/程序（UnrealInsights）环境。

## C++ 用法

### 头文件引入

```cpp
#include "MassInsightsAnalysis/Model/MassInsights.h"
```

### 基本用法

以下示例展示如何在自定义分析模块中获取 `IMassInsightsProvider`，并枚举所有 Fragment 信息。

```cpp
// 假设已在分析会话中获取 Provider
MassInsightsAnalysis::IMassInsightsProvider* MassProvider = 
    Session.ReadProvider<MassInsightsAnalysis::IMassInsightsProvider>(FName("MassInsightsProvider"));

if (MassProvider)
{
    // 读取模式
    MassProvider->BeginRead();

    // 枚举所有 Fragment
    int32 FragmentCount = MassProvider->GetFragmentCount();
    MassProvider->EnumerateFragments(
        [](const MassInsightsAnalysis::FMassFragmentInfo& FragmentInfo, int32 Index)
        {
            // 输出 Fragment 名称和类型
            UE_LOG(LogTemp, Display, TEXT("Fragment [%d]: Name=%s, Type=%d, Size=%u"),
                Index, FragmentInfo.GetName(), (uint8)FragmentInfo.Type, FragmentInfo.Size);
        });

    // 按 ID 查找特定 Fragment
    const MassInsightsAnalysis::FMassFragmentInfo* Found = MassProvider->FindFragmentById(SomeFragmentId);
    if (Found)
    {
        // 处理查找结果
    }

    MassProvider->EndRead();
}
```

### 进阶用法：枚举实体事件与时间区域

结合时间范围查询，分析指定时间窗口内的实体操作：

```cpp
MassProvider->BeginRead();

// 枚举所有实体事件
uint64 EventCount = MassProvider->GetEntityEventCount();
MassProvider->EnumerateEntityEvents(0, EventCount,
    [](const MassInsightsAnalysis::FMassEntityEventRecord& Record, uint64 Index)
    {
        // 根据事件类型处理
        switch (Record.Operation)
        {
        case MassInsightsAnalysis::EMassEntityEventType::Created:
            // 实体创建
            break;
        case MassInsightsAnalysis::EMassEntityEventType::ArchetypeChange:
            // 实体迁移 Archetype
            break;
        case MassInsightsAnalysis::EMassEntityEventType::Destroyed:
            // 实体销毁
            break;
        }
    });

// 枚举时间交叉区域（例如整个会话区间）
double SessionStart = 0.0, SessionEnd = 100.0;
int32 LaneCount = MassProvider->GetLaneCount();
for (int32 LaneIndex = 0; LaneIndex < LaneCount; ++LaneIndex)
{
    const MassInsightsAnalysis::FMassInsightsLane* Lane = MassProvider->GetLane(LaneIndex);
    if (Lane)
    {
        Lane->EnumerateRegions(SessionStart, SessionEnd,
            [](const MassInsightsAnalysis::FMassInsights& Region)
            {
                UE_LOG(LogTemp, Display, TEXT("Region: %s [%.3f - %.3f]"),
                    Region.Text, Region.BeginTime, Region.EndTime);
                return true; // 继续枚举
            });
    }
}

MassProvider->EndRead();
```

> 上述代码需运行在 **UnrealInsights** 程序或支持 Trace 分析的环境中。

## Demo 示例

由于该插件主要用于 Unreal Insights 内部的数据收集与展示，无法提供独立可编译的简易示例。以下为在自定义 Trace 分析模块中集成 Mass Insights Provider 的最小框架：

**MassInsightsDemoModule.h**
```cpp
#pragma once
#include "Modules/ModuleInterface.h"
#include "TraceServices/ModuleService.h"

class FMassInsightsDemoModule : public IModuleInterface, public TraceServices::IModule
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    // TraceServices::IModule
    virtual void GetModuleInfo(TraceServices::FModuleInfo& OutModuleInfo) override;
    virtual void OnAnalysisBegin(TraceServices::IAnalysisSession& Session) override;

private:
    TSharedPtr<class IMassInsightsProvider> CachedProvider;
};
```

**MassInsightsDemoModule.cpp**
```cpp
#include "MassInsightsDemoModule.h"
#include "MassInsightsAnalysis/Model/MassInsights.h"
#include "TraceServices/Model/AnalysisSession.h"

IMPLEMENT_MODULE(FMassInsightsDemoModule, MassInsightsDemo)

void FMassInsightsDemoModule::StartupModule()
{
    // 注册自身为 Trace 模块（通常由外部框架完成）
}

void FMassInsightsDemoModule::ShutdownModule()
{
}

void FMassInsightsDemoModule::GetModuleInfo(TraceServices::FModuleInfo& OutModuleInfo)
{
    OutModuleInfo.Name = TEXT("MassInsightsDemo");
    OutModuleInfo.DisplayName = TEXT("Mass Insights Demo");
}

void FMassInsightsDemoModule::OnAnalysisBegin(TraceServices::IAnalysisSession& Session)
{
    // 假设 MassInsightsAnalysis 模块已注册了 Provider
    // 在 Session 中读取 Provider
    auto Provider = Session.ReadProvider<MassInsightsAnalysis::IMassInsightsProvider>(FName("MassInsightsProvider"));
    if (Provider)
    {
        // 使用 Provider 进行枚举（见“进阶用法”示例）
    }
}
```

> 注意：实际使用中你不需要手动实现 Provider 的创建，`FMassInsightsAnalysisModule` 会自动处理。

## 模块依赖

要使用 Mass Insights 插件，你的模块需要在 `Build.cs` 中添加以下依赖（不包括标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `TraceServices` | 提供 Trace 分析会话、Provider 基类、锁定机制 |
| `TraceAnalysis` | 提供分析器注册与事件路由 |
| `Core` | 基础类型（已省略，但必须） |
| `CoreUObject` | `FName` 等类型（已省略） |

无其他特殊依赖。

## 维护状态

### 近期更新

- 2025-05-31 `52e3dac1` 使用 UnrealCodeFixup 更新头文件，确保 DLL 存储关键字正确应用于方法和静态变量
- 2025-04-02 `46cab30d` 修复不可达代码警告
- 2025-03-25 `c90dffef` LOCTEXT 修复（MassInsights）
- 2025-03-24 `81901d1e` 修复缺失的 LOCTEXT 键
- 2025-03-20 `0690086f` 修复版权声明

### 维护评价

- **创建时间**：2025年3月，非常新的插件。
- **最近更新频率**：3个月内有多项功能性/编译修复，属于活跃维护。
- **是否还在活跃维护**：是，最近一次更新为2025年5月。
- **已知问题或限制**：Beta 版本，功能可能不完全稳定；目前仅支持 `UnrealInsights` 程序，无法在标准游戏运行时使用。
- **推荐使用**：✅ 推荐。对于使用 Mass 系统的项目，该插件能提供重要的运行时洞察，且官方持续维护。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MassInsights)
- 官方文档（暂无）
- 测试用例（未找到公开测试，内部测试可能位于 `Engine/Source/Programs/UnrealInsights/` 相关文件中）