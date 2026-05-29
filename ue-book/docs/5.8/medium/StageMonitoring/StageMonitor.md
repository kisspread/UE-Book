# Stage Monitor

> Plugin enabling monitoring in the context of a virtual production stage where multiple machines are in operation（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 舞台监控 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StageMonitor` (UncookedOnly), `StageMonitorEditor` (Editor), `StageDataProvider` (Runtime), `StageMonitorCommon` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StageMonitoring) | |

## 用途

Stage Monitoring 插件解决的是在大型虚拟制作现场（如使用 LED 墙、动作捕捉、多机渲染）中，对众多参与机器（数据提供者）的状态和数据进行实时监控、记录和分析的问题。它通过一个中心监控器，使用消息总线自动发现和连接舞台上的各个数据源，收集它们发送的状态和数据帧，并将其组织成“会话”进行记录。这使得技术主管能够实时观察整个舞台的健康状况、诊断问题、并在事后分析制作过程中发生的事件。

## 使用场景

- 你正在进行一个使用LED墙和多个摄像机追踪节点的虚拟制作项目 → 用 Stage Monitoring 来监控所有追踪节点、渲染机和媒体服务器的连接状态与数据流。
- 你管理一个分布式渲染农场，并需要在播放序列时观察所有机器的性能数据（如帧时间、GPU负载）→ 将各机器配置为 StageDataProvider，通过 StageMonitor 集中查看。
- 你需要记录并回放一次拍摄过程中各设备的状态变化和关键事件，用于后期分析或问题复现 → 使用其会话记录（Session）和导出/加载功能。

## 蓝图用法

该插件的核心功能通过C++接口暴露，蓝图交互主要通过获取模块和会话管理器实例来进行高级控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Stage Monitor Module` | 获取 StageMonitor 模块的单例，这是所有功能的入口 | `IStageMonitorModule` (静态方法) |
| `Enable Monitor` | 启用或禁用监控器，控制其是否开始发现并监听数据提供者 | `IStageMonitorModule` |
| `Create Session` | 创建一个新的实时监控会话，用于记录当前活动 | `IStageMonitorSessionManager` |
| `Save Session` | 请求将当前活跃会话异步保存到文件 | `IStageMonitorSessionManager` |
| `Load Session` | 请求从文件异步加载一个之前的会话记录用于分析 | `IStageMonitorSessionManager` |
| `Get All Entries` | 获取当前会话中接收到的所有数据条目 | `IStageMonitorSession` |
| `Get Latest` | 获取特定提供者的最新一条指定类型的数据 | `IStageMonitorSession` |
| `Is Stage In Critical State` | 查询舞台当前是否处于关键状态（如正在录制） | `IStageMonitorSession` |
| `On Session New Data Received` | 委托：当会话接收到新数据时触发 | `IStageMonitorSession` |
| `On Data Provider State Changed` | 委托：当某个数据提供者的连接状态改变时触发 | `IStageMonitorSession` |

### 使用示例（蓝图描述）

要开始监控，首先通过 `Get Stage Monitor Module` 节点获取模块实例。调用其 `Enable Monitor` 函数并传入 `true`。随后，通过模块的 `Get Stage Monitor Session Manager` 获取会话管理器。在开始监听数据前，通常需要调用 `Create Session` 来建立一个新的活动会话。此时，监控器将开始自动发现舞台网络上的数据提供者，并记录它们发送的所有数据。你可以在事件图表中绑定 `On Session New Data Received` 委托，每当有新数据到来时执行自定义逻辑（如更新UI显示）。当一次拍摄结束后，可以调用 `Save Session` 将数据保存下来。

## C++ 用法

核心用法涉及初始化监控器、创建会话、以及实现自己的数据提供者来向监控器发送数据。

### 头文件引入

```cpp
#include "StageMonitorModule.h"
#include "IStageMonitorSession.h"
#include "IStageDataProvider.h"
```

### 基本用法

1.  **获取并启用监控器**:
    ```cpp
    // 检查模块是否可用
    if (IStageMonitorModule::IsAvailable())
    {
        IStageMonitorModule& MonitorModule = IStageMonitorModule::Get();
        // 启用监控，开始发现和监听数据提供者
        MonitorModule.EnableMonitor(true);
        
        // 获取会话管理器
        IStageMonitorSessionManager& SessionManager = MonitorModule.GetStageMonitorSessionManager();
        // 创建一个新的活动会话
        TSharedPtr<IStageMonitorSession> ActiveSession = SessionManager.CreateSession();
    }
    ```

2.  **实现一个数据提供者**（来自 `StageDataProvider` 模块的测试逻辑推断）:
    你需要实现 `IStageDataProvider` 接口来向监控器广播数据。
    ```cpp
    // .h
    #include "IStageDataProvider.h"
    
    class FMyDataProvider : public IStageDataProvider
    {
    public:
        // IStageDataProvider interface
        virtual FStageInstanceDescriptor GetDescriptor() const override;
        virtual void HandleMonitorDiscovery(const FGuid& Identifier, const FMessageAddress& Address) override;
        virtual void HandleMonitorClosed(const FGuid& Identifier) override;
        virtual bool SendInitialData() override;
        // ... 其他接口方法
    };
    
    // .cpp
    void FMyDataProvider::HandleMonitorDiscovery(const FGuid& Identifier, const FMessageAddress& Address)
    {
        // 当监控器发现我们时，调用此方法。通常需要在这里响应，建立连接。
        // 可以向监控器发送初始数据或状态。
        // 例如，发送一个自定义的状态消息。
    }
    ```

### 进阶用法

监听会话事件并处理数据：
```cpp
if (TSharedPtr<IStageMonitorSession> Session = SessionManager.GetActiveSession())
{
    // 绑定新数据回调
    Session->OnStageSessionNewDataReceived().AddLambda(
        [](TSharedPtr<FStageDataEntry> NewData)
        {
            // 在这里处理新接收到的数据
            // NewData->Data 包含一个 FStructOnScope，可以提取实际消息
            if (NewData && NewData->Data.IsValid())
            {
                // 例如，假设我们接收的是 FMyCustomData 消息
                if (FMyCustomData* MyData = (FMyCustomData*)NewData->Data->GetStructMemory())
                {
                    // 使用 MyData 中的数据...
                }
            }
        }
    );
    
    // 查询某个提供者的最新数据
    FGuid SomeProviderID = /* ... */;
    UScriptStruct* MyDataType = FMyCustomData::StaticStruct();
    TSharedPtr<FStageDataEntry> LatestEntry = Session->GetLatest(SomeProviderID, MyDataType);
}
```

## Demo 示例

一个最小化的自定义数据提供者和监控器使用示例。

**MyDataProvider.h**
```cpp
#pragma once

#include "IStageDataProvider.h"
#include "StageMonitorTypes.h"

class FMyDataProvider : public IStageDataProvider
{
public:
    FMyDataProvider();
    virtual ~FMyDataProvider() override;

    // IStageDataProvider Interface
    virtual FStageInstanceDescriptor GetDescriptor() const override;
    virtual void HandleMonitorDiscovery(const FGuid& Identifier, const FMessageAddress& Address) override;
    virtual void HandleMonitorClosed(const FGuid& Identifier) override;
    virtual bool SendInitialData() override;
    virtual void Tick(float DeltaTime) override;

private:
    // 模拟一些需要上报的数据
    float CurrentFPS;
    int32 ActiveCameras;
};
```

**MyDataProvider.cpp**
```cpp
#include "MyDataProvider.h"
#include "StageMonitorSubsystem.h"
#include "StageMonitorMessages.h"

FMyDataProvider::FMyDataProvider()
    : CurrentFPS(60.0f)
    , ActiveCameras(1)
{
    // 向监控器注册自己，使其可被发现
    if (UStageMonitorSubsystem* Subsystem = GEngine->GetEngineSubsystem<UStageMonitorSubsystem>())
    {
        Subsystem->RegisterDataProvider(this);
    }
}

FMyDataProvider::~FMyDataProvider()
{
    if (UStageMonitorSubsystem* Subsystem = GEngine->GetEngineSubsystem<UStageMonitorSubsystem>())
    {
        Subsystem->UnregisterDataProvider(this);
    }
}

FStageInstanceDescriptor FMyDataProvider::GetDescriptor() const
{
    // 提供自己的描述信息
    FStageInstanceDescriptor Desc;
    Desc.Name = TEXT("MyCustomDataProvider");
    Desc.Type = EStageInstanceType::Custom;
    Desc.MachineName = FPlatformProcess::ComputerName();
    return Desc;
}

void FMyDataProvider::HandleMonitorDiscovery(const FGuid& Identifier, const FMessageAddress& Address)
{
    // 当监控器找到我们时，可以开始发送周期性数据
    UE_LOG(LogTemp, Log, TEXT("Discovered by Stage Monitor: %s"), *Identifier.ToString());
}

void FMyDataProvider::HandleMonitorClosed(const FGuid& Identifier)
{
    UE_LOG(LogTemp, Log, TEXT("Stage Monitor closed: %s"), *Identifier.ToString());
}

bool FMyDataProvider::SendInitialData()
{
    // 发送初始状态数据
    // 这里需要构造一个 FStageProviderMessage 并通过消息总线发送
    // 通常使用基类提供的辅助方法，但简化示例省略细节
    return true;
}

void FMyDataProvider::Tick(float DeltaTime)
{
    // 模拟数据变化
    CurrentFPS = FMath::RandRange(30.0f, 120.0f);
    ActiveCameras = FMath::RandRange(0, 4);
    
    // 在实际实现中，这里会周期性地向所有已连接的监控器发送包含 CurrentFPS 和 ActiveCameras 的消息。
    // 例如，构造一个自定义的 FMyProviderDataMessage 并通过消息总线发送。
}
```

## 模块依赖

该插件依赖于其他虚拟制作基础插件和模块。

| 模块 | 用途 |
|---|---|
| `Takes` | 用于集成影视制作中的Take（拍摄条次）管理系统，可能用于关联监控数据与特定Take。 |
| `VirtualProductionUtilities` | 提供虚拟制作通用的工具和类型，是本插件功能的基础之一。 |
| `StageMonitorCommon` | 本插件内部的公共类型和接口定义模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构了JSON对象以支持FString和UE::FSharedString，提升内存效率 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到UE_LOGF，可能是日志格式化改进 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除FJsonObject中的字符串重复以释放内存，优化性能 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了之前一次错误的全局查找替换后，进行的第二次修正 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了提交51314860，说明该次更改引入了问题 |

### 维护评价

该插件创建于2020年，已有约6年历史，但**近期（2026年）有持续的实质性更新**，主要集中在性能优化（内存管理）和代码质量改进（重构、日志迁移）上。这表明它仍在**活跃维护**中，并随着引擎的发展而更新。`.uplugin` 文件中 `IsBetaVersion: true` 表明其仍处于**测试阶段**，可能在稳定性和API完整性上存在变化，不建议在最终发布的产品中未经充分测试直接依赖。对于虚拟制作项目，它是一个有价值的内部工具，但使用时需注意其Beta状态可能带来的兼容性风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StageMonitoring)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StageMonitoring/Source/StageMonitor/Tests)