# Capture Manager Pipeline

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理管道模块 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CaptureManagerPipeline` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

`CaptureManagerPipeline` 模块提供了一个**数据处理管道（Pipeline）执行框架**，用于虚拟制片场景中的捕获数据转换工作流。

它解决的核心问题是：在从虚拟制片设备（如容积摄影棚）采集原始数据后，需要将视频、音频、深度图、标定数据等多种媒体格式进行**批量、可并行、可取消的转换处理**。该模块将每一步转换操作抽象为"节点"，通过管道编排器统一调度执行，并支持异步/同步两种执行策略。

该模块是 CaptureManagerCore 插件的一部分，与 `CaptureManagerApp` 和 `CaptureManagerEditor` 插件共享，不单独使用。

## 使用场景

- 你从虚拟制片设备批量采集了视频/音频/深度数据，需要将其转换为引擎可用的格式 → 用 CaptureManagerPipeline 编排转换流程
- 你需要同时处理多个捕获数据源（多路视频 + 音频 + 深度），且希望它们并行执行以提高效率 → 使用 Pipeline 的并行节点 + 同步节点机制
- 转换过程可能耗时很长，需要支持用户取消操作 → 使用 Pipeline 的 `Cancel()` 机制
- 你正在开发 CaptureManager 相关的 App 或 Editor 功能，需要标准化的数据转换流程 → 依赖此模块

## 蓝图用法

该模块**不暴露蓝图接口**（所有类均为纯 C++，无 `UCLASS`/`UFUNCTION(BlueprintCallable)` 宏）。这是因为管道是底层数据处理框架，由上层 App/Editor 插件在 C++ 层调用。

## C++ 用法

### 头文件引入

```cpp
#include "CaptureManagerPipeline.h"
#include "Nodes/ConvertVideoNode.h"
#include "Nodes/ConvertAudioNode.h"
#include "Nodes/ConvertDepthNode.h"
#include "Nodes/ConvertCalibrationNode.h"
```

### 核心概念

管道框架由两个核心类构成：

| 类 | 说明 |
|---|---|
| `FCaptureManagerPipeline` | 管道编排器，管理节点集合，调度执行 |
| `FCaptureManagerPipelineNode` | 节点基类，定义 `Prepare → Validate → Run` 生命周期 |

每个节点有三个阶段：
1. **Prepare()** — 准备阶段，检查输入数据有效性
2. **Validate()** — 验证阶段，确认前置条件满足
3. **Run()** — 执行阶段，执行实际转换逻辑

执行策略有两种：
- `EPipelineExecutionPolicy::Asynchronous` — 异步执行，节点在后台线程运行
- `EPipelineExecutionPolicy::Synchronous` — 同步执行，阻塞调用线程

节点添加方式：
- `AddGenericNode()` / `AddConvertVideoNode()` 等 — 添加到**并行组**，可同时执行
- `AddSyncedNode()` — 添加到**同步组**，与其他同步节点串行执行

### 基本用法

```cpp
// 创建一个异步管道
auto Pipeline = MakeShared<FCaptureManagerPipeline>(EPipelineExecutionPolicy::Asynchronous);

// 添加视频转换节点到并行组
auto VideoNode = MakeShared<FConvertVideoNode>(VideoMetadata, OutputDir);
Pipeline->AddConvertVideoNode(VideoNode);

// 添加音频转换节点到并行组
auto AudioNode = MakeShared<FConvertAudioNode>(AudioMetadata, OutputDir);
Pipeline->AddConvertAudioNode(AudioNode);

// 添加深度转换节点到并行组
auto DepthNode = MakeShared<FConvertDepthNode>(DepthMetadata, OutputDir);
Pipeline->AddConvertDepthNode(DepthNode);

// 执行管道（阻塞调用）
FCaptureManagerPipeline::FResult Results = Pipeline->Run();

// 检查结果
for (auto& [NodeId, Result] : Results)
{
    if (Result.HasError())
    {
        UE_LOG(LogTemp, Error, TEXT("Node failed: %s (Code: %d)"),
            *Result.GetError().GetMessage().ToString(),
            Result.GetError().GetCode());
    }
}
```

### 进阶用法

#### 自定义管道节点

通过继承 `FCaptureManagerPipelineNode` 实现自定义转换逻辑：

```cpp
class FMyCustomNode : public FCaptureManagerPipelineNode
{
public:
    FMyCustomNode(const FString& InInputPath, const FString& InOutputPath)
        : FCaptureManagerPipelineNode(TEXT("MyCustomNode"))
        , InputPath(InInputPath)
        , OutputPath(InOutputPath)
    {}

protected:
    // 准备阶段：检查输入文件是否存在
    virtual FResult Prepare() override
    {
        if (!FPaths::FileExists(InputPath))
        {
            return FResult(MakeError(FCaptureManagerPipelineError(
                FText::FromString(TEXT("Input file not found")), -1)));
        }
        return FResult(MakeValue());
    }

    // 验证阶段：检查输出目录是否可写
    virtual FResult Validate() override
    {
        FString OutputDir = FPaths::GetPath(OutputPath);
        if (!FPaths::DirectoryExists(OutputDir))
        {
            IFileManager::Get().MakeDirectory(*OutputDir, true);
        }
        return FResult(MakeValue());
    }

    // 执行阶段：执行实际转换
    virtual FResult Run() override
    {
        // 执行自定义转换逻辑...
        return FResult(MakeValue());
    }

private:
    FString InputPath;
    FString OutputPath;
};
```

#### 混合并行与同步节点

```cpp
auto Pipeline = MakeShared<FCaptureManagerPipeline>(EPipelineExecutionPolicy::Asynchronous);

// 第一阶段：所有数据转换并行执行
Pipeline->AddConvertVideoNode(VideoNode);
Pipeline->AddConvertAudioNode(AudioNode);
Pipeline->AddConvertDepthNode(DepthNode);

// 第二阶段：标定数据必须等所有转换完成后才能处理（同步节点）
Pipeline->AddSyncedNode(CalibrationNode);

// 执行 — 并行节点先跑，全部完成后才执行同步节点
auto Results = Pipeline->Run();
```

#### 取消执行

```cpp
auto Pipeline = MakeShared<FCaptureManagerPipeline>(EPipelineExecutionPolicy::Asynchronous);
Pipeline->AddConvertVideoNode(LongVideoNode);

// 在另一个线程/回调中取消
Async(EAsyncExecution::Thread, [&Pipeline]()
{
    FPlatformProcess::Sleep(5.0f);
    Pipeline->Cancel();
});

auto Results = Pipeline->Run();
// 已取消的节点会在结果中体现
```

## 模块依赖

从各 Build.cs 分析，该模块的主要依赖为：

| 模块 | 用途 |
|---|---|
| `CaptureManagerTakeMetadata` | 提供 `FTakeMetadata`（视频/音频/深度/标定的元数据结构） |
| `CaptureUtils` | 提供通用捕获工具函数 |

无其他特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

以下为 CaptureManagerCore 插件相关的近期提交：

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `a2e4a9e3` | Forward the stop token to third-party encoder commands so audio and video conversion can be cancelle | 将停止令牌传递给第三方编码器，使音视频转换支持取消 |
| 2026-05-12 | `218704d7` | [CaptureManager] Added missing fix from 51621159 which was dropped during conversion module move. | 修复模块迁移时丢失的一个补丁 |
| 2026-05-12 | `16e184f7` | [CaptureManager] Fix transaction ID data race causing transient download failures. | 修复事务 ID 数据竞争导致的偶发下载失败 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 JSON 对象以支持 FString 和 SharedString |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增设备蓝图模块 |

### 维护评价

- **创建时间**：2025-02-04，约 1 年前，属于较新的模块
- **活跃度**：非常活跃。最近一个月内有多次功能性更新（取消机制增强、数据竞争修复、新模块引入）
- **维护团队**：由 Epic Games 官方维护（Virtual Production 团队），质量有保障
- **推荐使用**：✅ 推荐。作为 CaptureManager 体系的核心管道模块，持续收到功能增强和 bug 修复。但注意这是一个**内部共享模块**，不建议在独立项目中直接使用，应配合 CaptureManagerApp 或 CaptureManagerEditor 插件使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Source/CaptureManagerPipeline)
- [插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- 官方文档：无（.uplugin 中 DocsURL 为空）