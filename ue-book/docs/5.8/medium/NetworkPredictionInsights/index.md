# Network Prediction Insights

> Allows debugging of NetworkPrediction via Unreal Insights（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 网络预测调试器 |
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NetworkPredictionInsights` (EditorAndProgram) |
| 实验性 | 否 |
| 创建时间 | 2020-03-16 |
| 年龄标签 | 🏛️ 文物（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/NetworkPredictionInsights) | |

## 用途

该插件是 UE5 **网络预测系统** 的专用调试工具，通过集成到 Unreal Insights 中，为开发者提供网络预测状态的可视化分析能力。它解决了网络预测调试复杂、缺乏可视化工具的问题，允许开发者：

1. **追踪网络预测事件**：记录模拟帧创建、Tick、网络接收、状态同步等所有关键事件。
2. **可视化模拟时间线**：在时间轴上直观显示预测、确认、回滚、重新预测等状态。
3. **分析用户状态变更**：追踪输入命令、同步状态、物理状态等的来源和变化历史。
4. **调试回滚机制**：清晰展示网络接收导致的状态回滚、重新预测等过程。
5. **支持多网络角色**：区分显示自治代理、模拟代理、权威端等不同网络角色的预测状态。

该插件**不会被默认启用**，需要手动在 UnrealInsights 程序中加载，专门用于分析网络预测系统的运行时行为。

## 使用场景

- 你在开发一个**多人在线游戏**，网络预测系统出现了不可预期的状态回滚 → 使用 Network Prediction Insights 分析回滚原因
- 你需要调试**玩家输入的同步问题**，但传统日志信息不足以理解状态变化顺序 → 可视化查看输入命令的处理流程
- 你的网络预测系统出现**性能问题**，需要分析不同模拟帧的耗时分布 → 在时间线上查看帧处理时间
- 你需要验证**权威端状态**与客户端预测状态的一致性 → 对比显示不同网络角色的模拟帧
- 你正在优化网络预测的**回滚逻辑**，需要理解回滚触发的具体条件和影响范围 → 查看网络接收和回滚事件的关联

## 蓝图用法

该插件是**纯编辑器/工具插件**，没有运行时蓝图节点。它通过 Unreal Insights 界面进行操作，不提供蓝图可调用的函数。

**Insights 工具用法**：

1. 启动时添加命令行参数：`-trace=NetworkPrediction`
2. 打开 Unreal Insights 工具，加载跟踪数据
3. 在 Insights 窗口中，选择 "Network Prediction" 选项卡
4. 使用以下 UI 功能：

| 功能 | 说明 |
|---|---|
| 模拟帧时间线 | 显示所有网络预测模拟的帧状态时间线 |
| 内容面板 | 显示选中模拟帧的详细状态信息 |
| 网络角色过滤 | 按权威端/自治代理/模拟代理筛选显示 |
| 用户状态搜索 | 搜索特定用户状态的变更历史 |
| 自动滚动 | 开启后自动滚动到最新的模拟帧 |
| PIE 会话选择 | 选择要分析的 PIE 游戏实例 |

## C++ 用法

该插件主要作为 Unreal Insights 的扩展模块，C++ 用法主要涉及数据分析和 UI 扩展。以下是核心的提供者接口用法：

### 头文件引入

```cpp
#include "INetworkPredictionProvider.h"
```

### 基本用法 - 读取分析数据

```cpp
// 获取网络预测数据提供者（在 Insights 分析环境中）
TraceServices::IAnalysisSession& Session = /* 获取分析会话 */;
INetworkPredictionProvider* Provider = Session.ReadProvider<INetworkPredictionProvider>("NetworkPredictionProvider");

if (Provider)
{
    // 读取所有已跟踪的模拟数据
    TArrayView<const TSharedRef<FSimulationData>> Simulations = Provider->ReadSimulationData();
    
    for (const TSharedRef<FSimulationData>& SimData : Simulations)
    {
        // 获取模拟的常量信息
        const FSimulationData::FConst& ConstInfo = SimData->Const;
        
        // 遍历模拟帧（使用受限制的视图访问）
        auto RestrictedView = SimData->GetRestrictedView();
        auto TickIterator = RestrictedView->GetTickIterator();
        
        while (TickIterator)
        {
            const FSimulationData::FTick& Tick = *TickIterator;
            // 处理每个模拟帧数据
            ++TickIterator;
        }
    }
}
```
*来源：`INetworkPredictionProvider.h` 中的接口定义*

### 进阶用法 - 访问用户状态历史

```cpp
// 在模拟数据中追踪特定用户状态的历史变更
void TrackUserStateHistory(const FSimulationData& SimData, int32 TargetFrame)
{
    // 获取用户状态存储（例如输入命令）
    const FSimulationData::FUserStateStore& UserStateStore = SimData->UserData.UserStates;
    
    // 查找特定帧的用户状态，排除网络接收来源
    const FSimulationData::FUserState* State = UserStateStore.Get(
        TargetFrame, 
        UINT64_MAX,  // 最大引擎帧（无限制）
        (uint8)ENP_UserStateSource::NetRecv,  // 排除 NetRecv 来源
        false        // 非稀疏访问模式
    );
    
    if (State)
    {
        // 追溯状态变更历史
        const FSimulationData::FUserState* Current = State;
        while (Current)
        {
            // 获取状态信息
            UE_LOG(LogTemp, Log, TEXT("Frame %d, Source: %s, Content: %s"), 
                Current->SimFrame,
                LexToString(Current->Source),
                Current->UserStr ? Current->UserStr : TEXT("null"));
            
            Current = Current->Prev;
        }
    }
}
```
*来源：`INetworkPredictionProvider.h` 中的 `FSimulationData::FUserStateStore` 定义*

### 高级用法 - 分析网络接收状态

```cpp
// 分析网络接收事件及其对模拟的影响
void AnalyzeNetworkReceives(const FSimulationData& SimData)
{
    auto NetRecvView = SimData->GetNetRecvRestrictedView();
    auto NetRecvIterator = NetRecvView.GetIterator();
    
    while (NetRecvIterator)
    {
        const FSimulationData::FNetSerializeRecv& NetRecv = *NetRecvIterator;
        
        // 检查接收状态
        switch (NetRecv.Status)
        {
        case ENetSerializeRecvStatus::Confirm:
            UE_LOG(LogTemp, Log, TEXT("Confirm at frame %d"), NetRecv.Frame);
            break;
            
        case ENetSerializeRecvStatus::Rollback:
            UE_LOG(LogTemp, Warning, TEXT("Rollback triggered at frame %d"), NetRecv.Frame);
            // 分析关联的重新预测帧
            if (NetRecv.NextTick)
            {
                UE_LOG(LogTemp, Log, TEXT("Repredicted frame %d"), 
                    NetRecv.NextTick->OutputFrame);
            }
            break;
            
        case ENetSerializeRecvStatus::Fault:
            UE_LOG(LogTemp, Error, TEXT("Network fault at frame %d"), NetRecv.Frame);
            // 输出系统故障信息
            for (const FSimulationData::FSystemFault& Fault : NetRecv.SystemFaults)
            {
                UE_LOG(LogTemp, Error, TEXT("  System fault: %s"), Fault.Str);
            }
            break;
        }
        
        ++NetRecvIterator;
    }
}
```
*来源：`INetworkPredictionProvider.h` 中的 `FSimulationData::FNetSerializeRecv` 定义*

## Demo 示例

以下是一个最小的 Insights 分析模块示例，演示如何扩展网络预测分析：

```cpp
// MyNetworkPredictionAnalyzer.h
#pragma once

#include "NetworkPredictionAnalyzer.h"

class FMyNetworkPredictionAnalyzer : public FNetworkPredictionAnalyzer
{
public:
    FMyNetworkPredictionAnalyzer(TraceServices::IAnalysisSession& InSession, 
                                  FNetworkPredictionProvider& InProvider)
        : FNetworkPredictionAnalyzer(InSession, InProvider)
    {
    }
    
    virtual bool OnEvent(uint16 RouteId, EStyle Style, const FOnEventContext& Context) override
    {
        // 先调用基类处理
        bool bHandled = FNetworkPredictionAnalyzer::OnEvent(RouteId, Style, Context);
        
        // 添加自定义分析逻辑
        if (RouteId == RouteId_Tick)
        {
            // 获取当前线程状态
            FThreadState& ThreadState = GetThreadState(Context.ThreadId());
            
            // 自定义统计
            if (ThreadState.bInsideSimulation)
            {
                // 记录额外的性能数据
                int64 StartTime = Context.Timestamp();
                // ... 自定义逻辑
            }
        }
        
        return bHandled;
    }
};
```

```cpp
// MyNetworkPredictionAnalyzer.cpp
#include "MyNetworkPredictionAnalyzer.h"

// 注册到分析系统
void RegisterMyAnalyzer(TraceServices::IAnalysisSession& Session)
{
    // 获取或创建网络预测提供者
    FNetworkPredictionProvider& Provider = Session.EditProvider<FNetworkPredictionProvider>("NetworkPredictionProvider");
    
    // 创建并注册自定义分析器
    auto Analyzer = MakeShared<FMyNetworkPredictionAnalyzer>(Session, Provider);
    Session.AddAnalyzer(Analyzer);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NetworkPredictionInsights` | 核心模块，提供 UI 和分析功能 |
| `NetworkPrediction` | 网络预测系统核心模块（运行时依赖） |
| `TraceAnalysis` | 跟踪数据分析框架 |
| `TraceServices` | 跟踪服务接口 |
| `Insights` | Unreal Insights 工具框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的类型转换警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统迁移到 UE_LOGF 宏 |
| 2025-09-18 | `3445e96a` | * Removed deprecated code (toggled off by UE_DEPRECATED_PROFILER_ENABLED or by UE_STATS_MEMORY_PROFI | 移除废弃代码和旧版分析器支持 |
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 修复忽略返回值警告问题 |
| 2025-04-08 | `855b561a` | Fixed some wrongly-sized printf specifiers. | 修复格式化字符串规格符错误 |

### 维护评价

**维护状态：活跃维护中**

该插件自 2020 年创建以来持续维护，最近 1 年内有多次功能性更新和代码质量改进。虽然更新主要是编译修复、警告消除和代码规范化，但表明 Epic 仍在积极维护该模块。

**优点**：
- 专为网络预测系统设计，提供深度的可视化调试能力
- 集成到标准的 Unreal Insights 工具链中
- 数据结构设计合理，支持多线程分析和大规模数据
- 持续维护，兼容最新的 UE 版本

**限制**：
- 仅在 UnrealInsights 程序中可用，不能用于运行时调试
- 需要手动启用（EnabledByDefault=false）
- 调试信息专业性强，学习曲线较陡
- 对网络预测系统的内部实现有较强依赖

**推荐使用**：✅ 强烈推荐
对于正在开发基于 UE5 网络预测系统的多人游戏项目，特别是遇到复杂的预测、回滚或同步问题时，这是一个**必不可少**的调试工具。它能显著降低网络预测系统的调试难度，提供传统日志无法提供的可视化洞察。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/NetworkPredictionInsights)
- [官方文档]()（无）
- [测试用例]()（未找到公开测试用例）