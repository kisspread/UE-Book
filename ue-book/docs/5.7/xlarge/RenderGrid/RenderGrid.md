# Render Grid

> Advanced pipeline for use in creating rendered cinematics.

| 属性 | 值 |
|---|---|
| 中文名 | 渲染网格 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RenderGrid` (Runtime), `RenderGridDeveloper` (Runtime), `RenderGridEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RenderGrid) | |

---

## 用途

Render Grid 是一个面向影视级渲染的作业调度和管理管线。它允许你在一个可视化“网格”中定义多个渲染作业（Job），每个作业可以拥有不同的属性（如相机位置、材质、灯光等），并通过**本地预设**或**远程控制（Remote Control）预设**来驱动这些属性。插件内置了基于 Movie Render Queue 的批处理渲染引擎，能够自动对一组作业进行渲染，并输出预览帧或最终成品。

该插件解决了以下问题：
- 如何在一次操作中批量渲染同一场景的多种变体（如不同时间、不同镜头角度）；
- 如何利用 Remote Control Preset 在运行时修改关卡属性并记录为不同的 Job；
- 如何在不弹出 UI 的情况下，在后台（Headless）执行渲染任务（可用于自动化测试或构建管线）。

## 使用场景

- **影视短片批量渲染**：定义多个镜头（Camera）、材质替换变体（通过 Remote Control），一键渲染所有组合。
- **自动化测试与CI**：在自动化脚本中创建 RenderGrid，设置多个 Job 并触发无头渲染，验证画面正确性。
- **动态属性驱动的渲染**：通过 Remote Control Preset 控制场景参数，每个 Job 保存不同的参数快照，批量输出。

## 蓝图用法

> 以下节点均来自 `RenderGrid` 运行模块（Runtime）。由于插件包含三个子模块（Editor 模块提供 UI），蓝图运行时仅需依赖 `RenderGrid` 模块即可使用核心功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ParseJsonAs<Type>` 系列 | 将 JSON 字符串解析为指定类型（Byte/Int32/Float/Boolean/Vector 等），用于反序列化远程控制属性值 | `URenderGridRemoteControlUtils` |
| `<Type>ToJson` 系列 | 将指定类型的值序列化为 JSON 字符串 | `URenderGridRemoteControlUtils` |
| `ParseJsonAsStruct` / `StructToJson` | 结构和 JSON 的互转，支持 `FInstancedStruct` | `URenderGridRemoteControlUtils` |
| **创建作业**（需通过 C++ 或编辑器创建 `URenderGrid` 和 `URenderGridJob` 实例） | 蓝图侧主要通过操作已存在的 `URenderGrid` 对象来管理作业 | `URenderGrid` / `URenderGridJob` |
| `SetRemoteControlValue` / `GetRemoteControlValue`（位于 `URenderGridPropRemoteControl` 类） | 设置/获取某个远程控制属性的值（JSON 格式） | `URenderGridPropRemoteControl` |
| `RenderPreviewFrame`（通过 `URenderGridQueue` 的蓝图事件） | 触发单个作业的预览帧渲染 | `URenderGridQueue` |

### 使用示例（蓝图描述）

1. **解析远程控制属性值**  
   从某个 `URenderGridJob` 的 Remote Control Data 中获取 JSON，使用 `ParseJsonAsVector` 节点取出 `FVector` 表示的位置值，然后应用到场景中的 Actor。

2. **批量渲染作业**  
   获取一个 `URenderGrid` 对象（来自编辑器资产或运行时创建），遍历其 `Jobs` 数组，为每个 `Job` 调用 `CreateBatchRenderQueue`（C++ 函数，蓝图侧建议通过自定义事件封装），然后监听队列的 `OnFinished` 事件。

## C++ 用法

### 头文件引入

```cpp
#include "RenderGrid/RenderGrid.h"
#include "RenderGrid/RenderGridManager.h"
#include "RenderGrid/RenderGridQueue.h"
#include "RenderGrid/RenderGridPropsSource.h"
#include "Utils/RenderGridRemoteControlUtils.h"
#include "Utils/RenderGridUtils.h"
```

### 基本用法

**1. 获取模块和 Manager**

```cpp
#include "IRenderGridModule.h"

UE::RenderGrid::IRenderGridModule& Module = UE::RenderGrid::IRenderGridModule::Get();
UE::RenderGrid::FRenderGridManager& Manager = Module.GetManager();
```

**2. 创建一个本地属性源（PropSource）并生成一个 Job**

```cpp
// 创建本地属性源（不需要外部预设）
UObject* Origin = nullptr; // 本地源不需要 Origin
URenderGridPropsSourceBase* PropsSource = Module.CreatePropsSource(ERenderGridPropsSourceType::Local, Origin);

// 创建 RenderGrid 对象（通常从资产加载，这里演示运行时创建）
URenderGrid* Grid = NewObject<URenderGrid>();
Grid->PropsSource = PropsSource;

// 创建一个 Job
URenderGridJob* Job = NewObject<URenderGridJob>(Grid);
Job->JobId = Manager.GenerateJobId(Grid);
// 设置 Job 的属性（如要渲染的 Level）
Job->Level = TSoftObjectPtr<UWorld>(FSoftObjectPath(TEXT("/Game/Maps/MyMap.MyMap")));

Grid->Jobs.Add(Job);
```

**3. 执行预览帧渲染**

```cpp
UE::RenderGrid::FRenderGridManagerRenderPreviewFrameArgs Args;
Args.bHeadless = true;                  // 后台运行
Args.RenderGrid.Reset(Grid);
Args.RenderGridJob.Reset(Job);
Args.Resolution = FIntPoint(1920, 1080);
Args.Callback.BindLambda([](bool bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Preview render finished: %s"), bSuccess ? TEXT("Success") : TEXT("Failed"));
});

URenderGridQueue* Queue = Manager.RenderPreviewFrame(Args);
// Queue 会自动运行，无需手动 Tick
```

**4. 批量渲染多个 Job**

```cpp
TArray<URenderGridJob*> Jobs = { Job1, Job2, Job3 };
URenderGridQueue* BatchQueue = Manager.CreateBatchRenderQueue(Grid, Jobs);
// 监听队列完成事件
BatchQueue->OnFinished.AddLambda([](URenderGridQueue* Queue, bool bSuccess)
{
    // 处理所有作业渲染完成后的逻辑
});
```

### 进阶用法

**与 Remote Control Preset 集成**

```cpp
// 假设已有一个 RemoteControlPreset 资产
URemoteControlPreset* Preset = LoadObject<URemoteControlPreset>(nullptr, TEXT("/Game/Presets/MyPreset.MyPreset"));

// 创建 RemoteControl 属性源
URenderGridPropsSourceBase* RCPropsSource = Module.CreatePropsSource(ERenderGridPropsSourceType::RemoteControl, Preset);
URenderGridPropsRemoteControl* RCProps = Cast<URenderGridPropsRemoteControl>(RCPropsSource->GetProps());

// 遍历所有远程控制属性
for (URenderGridPropRemoteControl* Prop : RCProps->GetAll())
{
    // 获取默认值（JSON）
    FString DefaultJson = Prop->GetDefaultValue();
    // 设置一个新值（例如从某个 Job 的 RemoteControlData 中读取）
    TArray<uint8> Bytes;
    // ... 反序列化 JSON 到 Bytes
    Prop->Bytes = Bytes;
    Prop->Apply();
}
```

**自定义渲染输出设置**

```cpp
UE::RenderGrid::FRenderGridQueueCreateArgs QueueArgs;
QueueArgs.RenderGrid.Reset(Grid);
QueueArgs.RenderGridJobs = { TStrongObjectPtr<URenderGridJob>(Job) };
QueueArgs.bForceOutputImage = true;              // 确保输出图像文件
QueueArgs.bForceUseSequenceFrameRate = true;     // 使用序列帧率
QueueArgs.bEnsureSequentialFilenames = true;     // 强制连续文件名

URenderGridQueue* CustomQueue = URenderGridQueue::Create(nullptr, QueueArgs);
CustomQueue->Execute();
```

## Demo 示例

以下是一个完整的、可编译的最小示例（假设已在模块的 `Build.cs` 中添加了 `RenderGrid` 依赖）。

**RenderGridDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "RenderGrid/RenderGrid.h"
#include "RenderGrid/RenderGridManager.h"
#include "RenderGrid/RenderGridQueue.h"
#include "IRenderGridModule.h"

class FRenderGridDemo
{
public:
    void Run();
};
```

**RenderGridDemo.cpp**
```cpp
#include "RenderGridDemo.h"
#include "Engine/World.h"
#include "UObject/StrongObjectPtr.h"

void FRenderGridDemo::Run()
{
    using namespace UE::RenderGrid;

    // 1. 获取模块
    IRenderGridModule& Module = IRenderGridModule::Get();
    FRenderGridManager& Manager = Module.GetManager();

    // 2. 创建 RenderGrid 和 Job
    URenderGrid* Grid = NewObject<URenderGrid>();
    Grid->AddToRoot(); // 防止 GC

    // 使用本地属性源
    URenderGridPropsSourceBase* LocalSource = Module.CreatePropsSource(ERenderGridPropsSourceType::Local, nullptr);
    Grid->PropsSource = LocalSource;

    URenderGridJob* Job = NewObject<URenderGridJob>(Grid);
    Job->JobId = Manager.GenerateJobId(Grid);
    Job->Level = TSoftObjectPtr<UWorld>(FSoftObjectPath(TEXT("/Game/Maps/MyMap.MyMap"))); // 必须指向有效关卡
    Job->OutputSettings = NewObject<URenderGridJobOutputSettings>(Job);
    // 简化的输出设置：输出 PNG
    Job->OutputSettings->bWriteImage = true;
    Job->OutputSettings->ImageFormat = EImageFormat::PNG;
    Grid->Jobs.Add(Job);

    // 3. 设置渲染参数
    UE::RenderGrid::FRenderGridManagerRenderPreviewFrameArgs Args;
    Args.bHeadless = true;
    Args.RenderGrid.Reset(Grid);
    Args.RenderGridJob.Reset(Job);
    Args.Resolution = FIntPoint(640, 480);
    bool bFinished = false;
    bool bResult = false;
    Args.Callback.BindLambda([&](bool bSuccess)
    {
        bResult = bSuccess;
        bFinished = true;
    });

    // 4. 开始渲染（注意：此函数是异步的，需要 Tick 等待）
    URenderGridQueue* Queue = Manager.RenderPreviewFrame(Args);

    // 简单等待（在真实项目中应使用更优雅的等待或协程）
    while (!bFinished)
    {
        FPlatformProcess::Sleep(0.1f);
    }

    // 清理
    Grid->RemoveFromRoot();
    UE_LOG(LogTemp, Log, TEXT("Demo finished: %s"), bResult ? TEXT("OK") : TEXT("FAIL"));
}
```

## 模块依赖

以下依赖信息基于 `RenderGrid` 运行模块（`Source/RenderGrid/RenderGrid.Build.cs` 未提供完整内容，从代码中推断得出）。其他两个子模块（`RenderGridDeveloper`、`RenderGridEditor`）可能有额外依赖。

| 模块 | 用途 |
|---|---|
| `RemoteControl` | 提供 `URemoteControlPreset` 和远程控制属性系统 |
| `MoviePipeline` | 渲染管线执行（`UMoviePipelineExecutorBase` 等） |
| `MoviePipelineRenderPass` | 渲染输出设置 |
| `LevelSequence` | 支持序列帧率、帧范围 |
| `CinematicCamera`（可能） | 相机属性处理 |
| `JsonUtilities` | JSON 序列化/反序列化 |
| `ImageWrapper` | 图片读写（`IImageWrapper`） |

**其他注意事项**：插件自身包含三个模块，如果要在你的项目中引用，请在 `Build.cs` 中添加：

```cpp
PublicDependencyModuleNames.AddRange(new string[] {
    "RenderGrid",
    // 如果要用到编辑器 UI，还需要 "RenderGridEditor"
});
```

## 维护状态

### 近期更新

- 2025-09-15 `0fcf72f1` Render Grid: fixed crash when passing in an empty string when setting remote control values
- 2025-06-11 `b57e00bc` Replace some usages of FORCEINLINE with inline in Rendering modules.
- 2025-04-15 `45a9eb59` [Truncation Warnings] Deprecate FVector2D delegates in GraphEditor module
- 2025-04-09 `3ffb1588` Header unit / c++ modules compile fixes
- 2024-08-30 `df1cc540` Gather text from source, resolve macro has an empty source text (.cpp files)

### 维护评价

- **创建时间**：2024-08-30（约 1 年）
- **最近更新**：最近 6 个月内有实际功能修复（2025-09-15 的空字符串崩溃修复），说明仍在维护。
- **活跃度**：中等，更新频率不高但关键 Bug 得到及时修复。
- **已知问题**：在设置远程控制值为空字符串时曾崩溃（已修复）。无其他明显限制。
- **推荐度**：推荐使用。尽管标记为实验性，但核心功能稳定，且是 Epic 官方支持的工具，适合作为电影渲染管线的补充。建议在项目初期集成并测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RenderGrid)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RenderGrid/Tests)（可能位于 Engine/Tests/Plugins/RenderGrid 下）
- [官方文档](https://docs.unrealengine.com/5.7/en-US/render-grid-in-unreal-engine/)（预计未来会添加，当前为空）