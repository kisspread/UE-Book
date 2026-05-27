# MessageBus Tester

> Plugin to test and monitor message bus reliability

| 属性 | 值 |
|---|---|
| 中文名 | 消息总线测试器 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MessageBusTester` (Runtime), `MessageBusTesterEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester) | |

## 用途

MessageBusTester 是一个实验性插件，专门用于**测试和监控 UE5 UDP 消息总线的可靠性**。它解决了消息传输系统验证和性能分析的问题。

该插件的核心功能：
- **分布式测试协调**：允许多个 UE 实例（测试器）通过 UDP 消息总线相互发现和通信
- **测试计划管理**：定义和执行可配置的测试序列，包括负载大小、发送间隔等参数
- **可靠性监控**：跟踪消息传输的延迟、丢失率和吞吐量统计
- **连接状态管理**：监控测试器之间的连接状态，检测失联的测试器
- **结果导出**：支持将测试结果导出为 CSV 文件进行后续分析

为什么存在：消息总线是 UE5 分布式架构的核心组件，此插件提供了专门的测试框架来验证其在不同网络条件下的表现，确保生产环境中的可靠性。

## 使用场景

- **网络消息系统验证**：在开发分布式游戏或多人游戏时，需要验证 UDP 消息传输的可靠性
- **性能基准测试**：测试消息总线在不同负载下的吞吐量和延迟表现
- **故障排除**：诊断消息丢失、延迟过高或连接不稳定的问题
- **回归测试**：在消息总线系统更新后进行回归测试，确保没有引入性能退化
- **跨进程通信测试**：测试在同一台机器或网络中多个 UE 进程间的消息通信

## 蓝图用法

该插件主要是面向 C++ 的测试工具，没有暴露 `BlueprintCallable` 节点。所有操作都通过 C++ 接口进行。

## C++ 用法

### 头文件引入

```cpp
#include "IMessageBusTesterModule.h"
#include "IMessageBusTester.h"
#include "IMessageBusTesterLogger.h"
#include "MessageBusTesterCommon.h"
```

### 基本用法

#### 获取消息总线测试器实例

```cpp
// 来源：Public/IMessageBusTesterModule.h
// 获取消息总线测试器模块实例
IMessageBusTesterModule* MessageBusTesterModule = FModuleManager::GetModulePtr<IMessageBusTesterModule>("MessageBusTester");

if (MessageBusTesterModule)
{
    // 获取测试器实例
    IMessageBusTester& Tester = MessageBusTesterModule->GetMessageBusTester();
    
    // 获取日志记录器
    IMessageBusTesterLogger& Logger = MessageBusTesterModule->GetLogger();
}
```

#### 启动和停止测试系统

```cpp
// 来源：Public/IMessageBusTester.h
IMessageBusTester& Tester = MessageBusTesterModule->GetMessageBusTester();

// 启动测试系统
bool bStarted = Tester.StartSystem();

// 检查是否正在运行
bool bIsRunning = Tester.IsRunning();

// 停止测试系统
bool bStopped = Tester.StopSystem();
```

#### 管理测试计划

```cpp
// 来源：Public/MessageBusTesterCommon.h + Public/IMessageBusTester.h
// 创建测试计划项
FTestPlanItem TestItem;
TestItem.NumBytes = 1024;          // 负载大小（字节）
TestItem.IntervalSeconds = 1.0f;   // 发送间隔（秒）

// 添加到测试计划
Tester.AddTestPlanItem(TestItem);

// 移除测试计划项
Tester.RemoveTestPlanItem(0);

// 获取当前测试计划
const FMessageBusTestPlan& CurrentPlan = Tester.GetTestPlan();

// 监听测试计划变化
Tester.OnTestPlanChanged().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("测试计划已更新"));
});
```

#### 发现和监控测试器

```cpp
// 来源：Public/IMessageBusTester.h + Public/DiscoveredTester.h
// 获取已发现的测试器列表
TConstArrayView<TSharedPtr<FDiscoveredTester, ESPMode::ThreadSafe>> DiscoveredTesters = 
    Tester.GetDiscoveredTesters();

for (const TSharedPtr<FDiscoveredTester, ESPMode::ThreadSafe>& TesterInstance : DiscoveredTesters)
{
    // 获取测试器标识符
    FGuid Identifier = TesterInstance->Identifier;
    
    // 获取测试器描述信息
    const FTesterInstanceDescriptor& Descriptor = TesterInstance->Descriptor;
    FString MachineName = Descriptor.MachineName;
    uint32 ProcessId = Descriptor.ProcessId;
    
    // 获取连接状态
    EDiscoveredTesterConnectionState ConnectionState = TesterInstance->ConnectionState;
    
    // 获取统计信息
    const FMessageTransportStatistics& Stats = TesterInstance->Statistics;
}

// 监听测试器列表变化
Tester.OnDiscoveredTesterListChanged().AddLambda([&Tester]()
{
    // 重新获取测试器列表
    TConstArrayView<TSharedPtr<FDiscoveredTester, ESPMode::ThreadSafe>> Testers = 
        Tester.GetDiscoveredTesters();
    UE_LOG(LogTemp, Log, TEXT("已发现 %d 个测试器"), Testers.Num());
});

// 清除失联的测试器
bool bCleared = Tester.ClearLostTesters();
```

### 进阶用法

#### 完整的测试流程

```cpp
// 来源：基于多个头文件的综合用法
class FMyMessageBusTest
{
public:
    void RunComprehensiveTest()
    {
        IMessageBusTesterModule* Module = FModuleManager::GetModulePtr<IMessageBusTesterModule>("MessageBusTester");
        if (!Module) return;
        
        IMessageBusTester& Tester = Module->GetMessageBusTester();
        
        // 1. 配置测试计划
        ConfigureTestPlan(Tester);
        
        // 2. 启动测试系统
        if (Tester.StartSystem())
        {
            // 3. 等待测试器发现
            WaitForTesters(Tester, 3); // 等待至少3个测试器
            
            // 4. 启动测试
            if (Tester.StartTest())
            {
                // 5. 监控测试进度
                MonitorTestProgress(Tester);
                
                // 6. 停止测试
                Tester.StopTest(false);
            }
            
            // 7. 停止系统
            Tester.StopSystem();
        }
    }
    
private:
    void ConfigureTestPlan(IMessageBusTester& Tester)
    {
        // 定义一系列测试项，模拟不同负载
        TArray<FTestPlanItem> TestItems = {
            {1024, 1.0f},    // 1KB，每秒发送
            {4096, 0.5f},    // 4KB，每0.5秒发送
            {10240, 0.25f}   // 10KB，每0.25秒发送
        };
        
        for (const FTestPlanItem& Item : TestItems)
        {
            Tester.AddTestPlanItem(Item);
        }
    }
    
    void WaitForTesters(IMessageBusTester& Tester, int32 MinTesters)
    {
        // 简单的等待逻辑
        double StartTime = FPlatformTime::Seconds();
        while (Tester.GetDiscoveredTesters().Num() < MinTesters)
        {
            FPlatformProcess::Sleep(0.1f);
            
            // 5秒超时
            if (FPlatformTime::Seconds() - StartTime > 5.0)
            {
                UE_LOG(LogTemp, Warning, TEXT("等待测试器超时"));
                break;
            }
        }
    }
    
    void MonitorTestProgress(IMessageBusTester& Tester)
    {
        // 监控测试状态变化
        while (Tester.GetState() == EMessageBusTesterState::Active)
        {
            // 这里可以添加监控逻辑
            FPlatformProcess::Sleep(0.5f);
        }
    }
};
```

#### 使用日志记录器

```cpp
// 来源：Public/IMessageBusTesterLogger.h
IMessageBusTesterLogger& Logger = MessageBusTesterModule->GetLogger();

// 记录日志
Logger.Log("MyTester", TEXT("测试开始"), EMessageSeverity::Info);
Logger.Log("MyTester", TEXT("警告信息"), EMessageSeverity::Warning);
Logger.Log("MyTester", TEXT("错误信息"), EMessageSeverity::Error);

// 监听新日志
Logger.OnMessageBusTesterNewLogReceived().AddLambda([](TSharedRef<FMessageBusTesterLogEntry> LogEntry)
{
    UE_LOG(LogTemp, Log, TEXT("[%s] %s"), *LogEntry->Source.ToString(), *LogEntry->LogMessage);
});

// 监听日志清除
Logger.OnMessageBusTesterLogCleared().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("日志已清除"));
});

// 清除日志
Logger.ClearLog();
```

## Demo 示例

以下是一个完整的最小示例，展示如何集成消息总线测试器：

```cpp
// MyMessageBusTestActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IMessageBusTester.h"
#include "IMessageBusTesterLogger.h"
#include "MyMessageBusTestActor.generated.h"

UCLASS()
class AMyMessageBusTestActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyMessageBusTestActor();
    
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    
    UFUNCTION(BlueprintCallable, Category = "MessageBusTest")
    void StartTest();
    
    UFUNCTION(BlueprintCallable, Category = "MessageBusTest")
    void StopTest();
    
private:
    void OnDiscoveredTesterListChanged();
    void OnTestPlanChanged();
    void OnLogReceived(TSharedRef<FMessageBusTesterLogEntry> LogEntry);
    
    void ConfigureDefaultTestPlan();
    
    TScriptInterface<IMessageBusTester> MessageBusTester;
    TScriptInterface<IMessageBusTesterLogger> Logger;
    
    FDelegateHandle TesterListChangedHandle;
    FDelegateHandle TestPlanChangedHandle;
    FDelegateHandle LogReceivedHandle;
};
```

```cpp
// MyMessageBusTestActor.cpp
#include "MyMessageBusTestActor.h"
#include "IMessageBusTesterModule.h"
#include "MessageBusTesterCommon.h"
#include "Modules/ModuleManager.h"

AMyMessageBusTestActor::AMyMessageBusTestActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMessageBusTestActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 获取消息总线测试器模块
    IMessageBusTesterModule* Module = FModuleManager::GetModulePtr<IMessageBusTesterModule>("MessageBusTester");
    if (Module)
    {
        // 获取测试器接口
        MessageBusTester = Module->GetMessageBusTester();
        Logger = Module->GetLogger();
        
        // 配置默认测试计划
        ConfigureDefaultTestPlan();
        
        // 设置委托
        if (MessageBusTester)
        {
            TesterListChangedHandle = MessageBusTester->OnDiscoveredTesterListChanged().AddUObject(
                this, &AMyMessageBusTestActor::OnDiscoveredTesterListChanged);
                
            TestPlanChangedHandle = MessageBusTester->OnTestPlanChanged().AddUObject(
                this, &AMyMessageBusTestActor::OnTestPlanChanged);
        }
        
        if (Logger)
        {
            LogReceivedHandle = Logger->OnMessageBusTesterNewLogReceived().AddUObject(
                this, &AMyMessageBusTestActor::OnLogReceived);
        }
        
        UE_LOG(LogTemp, Log, TEXT("消息总线测试器已初始化"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("消息总线测试器模块未找到，请确保插件已启用"));
    }
}

void AMyMessageBusTestActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理委托
    if (MessageBusTester)
    {
        MessageBusTester->OnDiscoveredTesterListChanged().Remove(TesterListChangedHandle);
        MessageBusTester->OnTestPlanChanged().Remove(TestPlanChangedHandle);
    }
    
    if (Logger)
    {
        Logger->OnMessageBusTesterNewLogReceived().Remove(LogReceivedHandle);
    }
    
    Super::EndPlay(EndPlayReason);
}

void AMyMessageBusTestActor::StartTest()
{
    if (MessageBusTester)
    {
        // 启动测试系统
        if (MessageBusTester->StartSystem())
        {
            // 短暂等待发现其他测试器
            FPlatformProcess::Sleep(2.0f);
            
            // 启动测试
            MessageBusTester->StartTest();
            
            UE_LOG(LogTemp, Log, TEXT("消息总线测试已启动"));
        }
    }
}

void AMyMessageBusTestActor::StopTest()
{
    if (MessageBusTester)
    {
        // 停止测试（不退出应用程序）
        MessageBusTester->StopTest(false);
        
        // 停止测试系统
        MessageBusTester->StopSystem();
        
        UE_LOG(LogTemp, Log, TEXT("消息总线测试已停止"));
    }
}

void AMyMessageBusTestActor::ConfigureDefaultTestPlan()
{
    if (MessageBusTester)
    {
        // 添加三个测试项：轻度、中度、重度负载
        FTestPlanItem LightLoad;
        LightLoad.NumBytes = 512;
        LightLoad.IntervalSeconds = 1.0f;
        
        FTestPlanItem MediumLoad;
        MediumLoad.NumBytes = 4096;
        MediumLoad.IntervalSeconds = 0.5f;
        
        FTestPlanItem HeavyLoad;
        HeavyLoad.NumBytes = 16384;
        HeavyLoad.IntervalSeconds = 0.25f;
        
        MessageBusTester->AddTestPlanItem(LightLoad);
        MessageBusTester->AddTestPlanItem(MediumLoad);
        MessageBusTester->AddTestPlanItem(HeavyLoad);
    }
}

void AMyMessageBusTestActor::OnDiscoveredTesterListChanged()
{
    if (MessageBusTester)
    {
        int32 TesterCount = MessageBusTester->GetDiscoveredTesters().Num();
        UE_LOG(LogTemp, Log, TEXT("已发现 %d 个测试器"), TesterCount);
    }
}

void AMyMessageBusTestActor::OnTestPlanChanged()
{
    if (MessageBusTester)
    {
        const FMessageBusTestPlan& Plan = MessageBusTester->GetTestPlan();
        UE_LOG(LogTemp, Log, TEXT("测试计划已更新，包含 %d 个测试项"), Plan.TestPlanItems.Num());
    }
}

void AMyMessageBusTestActor::OnLogReceived(TSharedRef<FMessageBusTesterLogEntry> LogEntry)
{
    // 根据日志严重级别输出到不同日志类别
    switch (LogEntry->MessageSeverity)
    {
        case EMessageSeverity::Info:
            UE_LOG(LogTemp, Log, TEXT("[%s] %s"), *LogEntry->Source.ToString(), *LogEntry->LogMessage);
            break;
        case EMessageSeverity::Warning:
            UE_LOG(LogTemp, Warning, TEXT("[%s] %s"), *LogEntry->Source.ToString(), *LogEntry->LogMessage);
            break;
        case EMessageSeverity::Error:
            UE_LOG(LogTemp, Error, TEXT("[%s] %s"), *LogEntry->Source.ToString(), *LogEntry->LogMessage);
            break;
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UdpMessaging` | UDP 消息传输实现，MessageBusTester 依赖此模块进行实际的消息收发 |
| `MessageBus` | UE5 消息总线核心框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的 UE_LOGF 格式，适配 UE5 日志系统更新 |
| 2026-01-15 | `738ab46a` | Fixed localization warnings | 修复本地化相关警告，提升代码质量 |
| 2025-11-27 | `29081f24` | Fixup API macros | 修复 API 宏定义问题，确保正确的模块导出 |
| 2025-11-20 | `f8d6103d` | Enable NDK 29 for Android, fix compilation issues | 启用 Android NDK 29 支持并修复编译问题 |
| 2025-11-10 | `248fda82` | Fix the statistics panel not updating with a remote client resets its UDP Messaging settings. | 修复当远程客户端重置 UDP 消息设置时统计面板不更新的问题 |

### 维护评价

**实验性插件，维护活跃度中等**

- **创建时间**：2025 年 10 月创建，相对较新
- **近期更新**：最近一次更新在 2026 年 4 月，主要进行代码现代化和 bug 修复
- **维护状态**：处于实验阶段，有持续的维护和修复
- **已知限制**：
  - 仅支持 UDP 消息传输
  - 主要面向测试和调试目的，不建议在生产环境中使用
  - 实验性功能，API 可能在未来版本中发生变化
- **推荐使用**：
  - ✅ 推荐用于 UDP 消息系统的开发测试和性能分析
  - ✅ 推荐用于诊断网络消息传输问题
  - ❌ 不推荐在最终产品中直接使用
  - ❌ 不推荐用于生产环境的消息监控

**警告**：该插件标记为实验性（IsBetaVersion=true），默认不启用，且 SupportedPrograms 限制为 MessageBusTesterApp。这意味着它主要设计为独立的测试应用程序，而不是集成到游戏项目中的通用工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester)
- [官方文档]()（暂无）
- [测试用例]()（暂无独立测试用例，测试逻辑集成在插件本身）