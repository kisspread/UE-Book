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
| 创建时间 | 2022-08-23 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RenderGrid) | |

## 用途

RenderGrid 插件是一个用于批量管理和渲染电影级过场动画（Cinematics）的高级管线工具。它解决的核心问题是：当需要使用相同的关卡序列（Level Sequence）但通过**远程控制（Remote Control）** 修改不同的属性（如灯光颜色、材质参数、对象位置等）来渲染多个变体时，如何自动化、高效地管理这些渲染任务。

传统流程中，用户需要手动为每个变体重复修改属性并排队渲染，容易出错且低效。RenderGrid 通过引入一个“渲染网格”资产，允许用户定义一系列“渲染作业”（RenderGridJob），每个作业可以：
1.  继承一个基础关卡序列。
2.  通过远程控制预设（Remote Control Preset）覆盖特定属性。
3.  独立设置输出分辨率、帧范围和输出目录。
4.  自动批处理渲染这些作业，极大地简化了流程并减少了人为错误。

其设计将核心逻辑（`FRenderGridManager`）与 UI 分离，使其可以在不同模块甚至运行时环境中复用。

## 使用场景

- **游戏宣传材料制作**：为同一个游戏场景，通过改变天气、灯光、角色外观等参数，快速渲染一组宣传截图或视频。
- **产品可视化**：对于汽车、建筑等产品的不同配置（颜色、材质），使用同一场景动画进行批量渲染。
- **A/B 测试素材生成**：为同一个过场动画创建多个细微不同的版本，用于测试或决策。
- **自动化内容生产**：结合蓝图，在特定事件（如完成关卡设计）后自动触发对所有变体的渲染。

## 蓝图用法

RenderGrid 的蓝图 API 通过 `URenderGrid`、`URenderGridJob` 和 `URenderGridQueue` 等类暴露。

### 核心节点

#### `URenderGrid` (渲染网格资产)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateAndAddNewRenderGridJob` | 创建一个新的渲染作业并添加到当前网格中 | `URenderGrid` |
| `DuplicateAndAddRenderGridJob` | 复制一个已有的渲染作业 | `URenderGrid` |
| `RemoveRenderGridJob` | 从网格中移除一个渲染作业 | `URenderGrid` |
| `GetRenderGridJobs` | 获取网格中的所有渲染作业列表 | `URenderGrid` |
| `GetEnabledRenderGridJobs` | 获取所有启用的渲染作业 | `URenderGrid` |
| `SetRenderGridJobs` | 用提供的数组替换所有渲染作业 | `URenderGrid` |

#### `URenderGridJob` (单个渲染作业)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLevelSequence` | 为此作业指定要渲染的关卡序列 | `URenderGridJob` |
| `SetRenderPreset` | 设置用于渲染的 Movie Pipeline 配置预设 | `URenderGridJob` |
| `SetIsEnabled` | 启用或禁用此作业（控制是否参与批处理） | `URenderGridJob` |
| `SetJobName` | 设置作业的人类可读名称 | `URenderGridJob` |
| `SetJobId` | 设置作业的唯一文件名标识符 | `URenderGridJob` |
| `SetOutputDirectory` | 设置此作业的渲染输出目录 | `URenderGridJob` |
| `SetCustomResolution` | 设置自定义输出分辨率（覆盖预设） | `URenderGridJob` |
| `GetRemoteControlValue` / `SetRemoteControlValue` | 获取或设置此作业的特定远程控制属性值 | `URenderGridJob` |
| `GetRemoteControlFieldIdFromLabel` | 通过标签名查找远程控制属性的 ID | `URenderGridJob` |

#### `URenderGridQueue` (渲染队列)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateBatchRenderQueue` | 创建一个用于批量渲染指定作业的队列 | `FRenderGridManager` |
| `Execute` | 启动队列的渲染 | `URenderGridQueue` |
| `Pause` | 暂停正在渲染的队列 | `URenderGridQueue` |
| `Resume` | 恢复已暂停的队列 | `URenderGridQueue` |
| `Cancel` | 取消当前和所有剩余的作业 | `URenderGridQueue` |
| `GetCurrentlyRenderingJob` | 获取当前正在渲染的作业 | `URenderGridQueue` |
| `GetJobsRemainingCount` | 获取剩余待渲染作业的数量 | `URenderGridQueue` |
| `GetStatusPercentage` | 获取整个队列的总体进度百分比 | `URenderGridQueue` |
| `OnExecuteStarted` / `OnExecuteFinished` | 队列开始和完成的委托事件 | `URenderGridQueue` |

#### `URenderGridRemoteControlUtils` (工具库)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ParseJsonAsVector` | 将 JSON 字符串解析为 `FVector` | `URenderGridRemoteControlUtils` |
| `ColorToJson` | 将 `FColor` 转换为 JSON 字符串 | `URenderGridRemoteControlUtils` |

### 使用示例（蓝图描述）

1.  **创建和配置作业**：
    - 使用 `CreateAndAddNewRenderGridJob` 节点创建新作业。
    - 连续调用 `SetLevelSequence` 和 `SetRenderPreset` 节点为作业分配基础资产。
    - 使用 `GetRemoteControlFieldIdFromLabel` 查找你想要覆盖的灯光颜色属性的 ID（例如 “LightColor”）。
    - 调用 `SetRemoteControlValue` 并传入该 ID 和一个 JSON 字符串（例如 `{"R":1, "G":0, "B":0, "A":1}`）来将灯光设为红色。
    - 为多个作业重复此过程，为每个作业设置不同的颜色值。

2.  **启动批处理渲染**：
    - 从 `URenderGrid` 资产对象，调用 `CreateBatchRenderQueue` 并传入你想要渲染的作业数组（或使用 `GetEnabledRenderGridJobs` 获取所有启用的作业）。
    - 将返回的 `URenderGridQueue` 对象保存到变量中。
    - 调用 `Execute` 开始渲染。
    - 可以连接 `OnExecuteFinished` 委托，在蓝图中收到渲染完成的通知。

3.  **监控进度**：
    - 在渲染过程中，可以定期（例如通过 `Tick` 事件）调用 `GetJobsRemainingCount` 和 `GetStatusPercentage` 来更新 UI 进度条。
    - 使用 `GetCurrentlyRenderingJob` 和 `GetJobStatus` 来显示当前正在处理哪个作业及其具体状态。

## C++ 用法

### 头文件引入

```cpp
#include "RenderGrid/RenderGridManager.h"
#include "RenderGrid/RenderGrid.h"
#include "RenderGrid/RenderGridQueue.h"
#include "IRenderGridModule.h"
```

### 基本用法

此示例展示了如何通过代码创建一个渲染网格、添加作业，并启动一个单帧渲染队列。

```cpp
// 获取 RenderGrid 模块的管理器
UE::RenderGrid::FRenderGridManager& Manager = UE::RenderGrid::IRenderGridModule::Get().GetManager();

// 1. 创建一个新的 RenderGrid 资产 (URenderGrid)
URenderGrid* NewGrid = NewObject<URenderGrid>();

// 2. 创建一个新作业并配置
URenderGridJob* NewJob = NewGrid->CreateAndAddNewRenderGridJob();
NewJob->SetJobName(TEXT("RedLightVariant"));
NewJob->SetJobId(TEXT("job_001"));

// 假设我们已经有了关卡序列和渲染预设的指针
ULevelSequence* MySequence = LoadObject<ULevelSequence>(...);
UMoviePipelinePrimaryConfig* MyPreset = LoadObject<UMoviePipelinePrimaryConfig>(...);
NewJob->SetLevelSequence(MySequence);
NewJob->SetRenderPreset(MyPreset);
NewJob->SetOutputDirectory(FPaths::ProjectSavedDir() / TEXT("RenderOutput"));

// 3. (可选) 通过远程控制设置一个属性
// 假设我们知道某个光源的远程控制 FieldId
FGuid LightColorFieldId = ...; // 可以通过 Manager 或其他方式获取
FLinearColor Red(1.0f, 0.0f, 0.0f, 1.0f);
FString JsonValue;
// 使用工具函数将颜色转换为 JSON
URenderGridRemoteControlUtils::LinearColorToJson(Red, JsonValue);
NewJob->SetRemoteControlValue(LightColorFieldId, JsonValue);

// 4. 创建一个单帧渲染队列并执行
int32 FrameToRender = 100;
TArray<URenderGridJob*> JobsToRender = { NewJob };
URenderGridQueue* RenderQueue = Manager.CreateBatchRenderQueueSingleFrame(NewGrid, JobsToRender, FrameToRender);
RenderQueue->Execute();

// 注意：渲染是异步的。可以通过连接委托来监听完成事件。
RenderQueue->OnExecuteFinished().AddLambda([](URenderGridQueue* FinishedQueue, bool bSuccess) {
    if (bSuccess) {
        UE_LOG(LogRenderGrid, Log, TEXT("Render completed successfully!"));
    }
});
```

### 进阶用法

此示例展示了如何在渲染前后利用 `URenderGrid` 的蓝图可实现事件（在 C++ 中称为 `Receive...` 函数）来动态修改场景。

```cpp
// 首先，你需要创建一个继承自 URenderGrid 的子类。
UCLASS()
class UMyRenderGrid : public URenderGrid
{
    GENERATED_BODY()
    
protected:
    // 重写作业开始前的事件
    virtual void ReceiveBeginJobRender_Implementation(URenderGridQueue* Queue, URenderGridJob* Job) override
    {
        Super::ReceiveBeginJobRender_Implementation(Queue, Job);
        
        // 根据作业名称或某个远程控制值，动态修改场景
        if (Job->GetJobName() == TEXT("NightTime"))
        {
            // 查找并修改天空盒，或调整后处理体积
            // ...
        }
        
        // 可以获取并应用该作业的远程控制属性
        TArray<URemoteControlPreset*> Presets = Job->GetRemoteControlPresets();
        // ... 对预设进行操作
    }
    
    // 重写作业完成后的事件
    virtual void ReceiveEndJobRender_Implementation(URenderGridQueue* Queue, URenderGridJob* Job) override
    {
        Super::ReceiveEndJobRender_Implementation(Queue, Job);
        
        // 恒复场景修改，为下一个作业做准备
        // ...
    }
};

// 使用这个子类来创建网格资产
UMyRenderGrid* MyGrid = NewObject<UMyRenderGrid>();
// ... 后续配置和渲染流程与基本用法相同
```

## Demo 示例

以下是一个最小可编译的 C++ 类，演示了如何创建一个简单的渲染网格资产并添加作业。

```cpp
// MyRenderGridExample.h
#pragma once

#include "CoreMinimal.h"
#include "RenderGrid/RenderGrid.h"
#include "MyRenderGridExample.generated.h"

UCLASS(BlueprintType)
class UMyRenderGridExample : public UObject
{
    GENERATED_BODY()

public:
    /** 创建并返回一个包含示例作业的 RenderGrid 资产 */
    UFUNCTION(BlueprintCallable, Category = "RenderGrid Demo")
    static URenderGrid* CreateExampleGrid();
};

// MyRenderGridExample.cpp
#include "MyRenderGridExample.h"
#include "RenderGrid/RenderGridManager.h"
#include "IRenderGridModule.h"
#include "LevelSequence.h"
#include "MoviePipelineConfig.h"

URenderGrid* UMyRenderGridExample::CreateExampleGrid()
{
    UE::RenderGrid::FRenderGridManager& Manager = UE::RenderGrid::IRenderGridModule::Get().GetManager();

    // 创建网格
    URenderGrid* Grid = NewObject<URenderGrid>();
    Grid->AddToRoot(); // 防止被垃圾回收

    // 设置默认值（可选）
    Grid->GetDefaults()->LevelSequence = LoadObject<ULevelSequence>(nullptr, TEXT("/Game/Cinematics/MySequence.MySequence"));
    Grid->GetDefaults()->RenderPreset = LoadObject<UMoviePipelinePrimaryConfig>(nullptr, TEXT("/Game/MoviePipeline/Presets/4K_Preset.4K_Preset"));
    Grid->GetDefaults()->OutputDirectory = FPaths::ProjectSavedDir() / TEXT("RenderGridOutput");

    // 创建几个作业
    URenderGridJob* Job1 = Grid->CreateAndAddNewRenderGridJob();
    Job1->SetJobName(TEXT("BlueLight"));
    Job1->SetJobId(TEXT("blue_light"));

    URenderGridJob* Job2 = Grid->CreateAndAddNewRenderGridJob();
    Job2->SetJobName(TEXT("GreenLight"));
    Job2->SetJobId(TEXT("green_light"));
    // Job2 将继承默认的 LevelSequence 和 RenderPreset

    // 可以保存网格资产到磁盘
    // UPackage* Package = CreatePackage(TEXT("/Game/MyRenderGridAsset"));
    // Grid->Rename(*MakeUniqueObjectName(Package, URenderGrid::StaticClass(), TEXT("MyGrid")).ToString(), Package);
    // FEditorFileUtils::SaveAsset(Grid);

    return Grid;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RemoteControl` | 用于访问和操作远程控制预设及其实体，这是插件属性覆盖功能的核心依赖 |
| `LevelSequence` | 用于处理关卡序列资产，即渲染的“蓝图” |
| `MoviePipeline` | 用于实际执行电影渲染管线，配置渲染作业和执行器 |

**注意**：插件默认**未启用**。要使用它，需要在项目的 `.uproject` 文件或编辑器插件设置中手动启用 “RenderGrid” 插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构了FJsonObject以支持FString和UE::FSharedString两种字符串类型 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG日志调用迁移到了UE_LOGF |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除FJsonObject中的字符串重复以节省内存 |
| 2025-09-15 | `60737405` | Render Grid: fixed crash when passing in an empty string when setting remote control values | 修复了设置远程控制值时传入空字符串导致崩溃的问题 |
| 2025-06-11 | `b57e00bc` | Replace some usages of FORCEINLINE with inline in Rendering modules. | 在渲染模块中将一些FORCEINLINE替换为inline |

### 维护评价

RenderGrid 插件目前处于**实验性**状态，且默认未启用。尽管如此，从 Git 提交记录来看，它仍在被 Epic Games 积极维护和更新。最近一次提交（2026年4月）涉及底层依赖的重构，说明其代码库在持续优化以适应引擎其他部分的变化。2025年的提交修复了关键的崩溃问题。

这是一个相对年轻（约3年）的插件，专注于解决批量渲染和远程控制结合的特定工作流问题。其设计考虑了蓝图和 C++ 的可用性，并提供了清晰的事件系统用于在渲染前后进行自定义逻辑。

**结论**：如果你需要批量渲染带有属性变体的过场动画，并且愿意使用实验性功能，RenderGrid 是一个值得尝试的插件。但由于其“实验性”标签和默认未启用的状态，在关键生产项目中采用前应进行充分测试。它仍在活跃维护中，表明 Epic 认为其有潜在价值并持续投入。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RenderGrid)
- [官方文档](https://docs.unrealengine.com) （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RenderGrid/Tests) （未提供，但引擎内可能存在相关测试）