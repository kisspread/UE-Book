# Render Grid

> Advanced pipeline for use in creating rendered cinematics.

| 属性 | 值 |
|---|---|
| 中文名 | 渲染网格队列 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RenderGrid` (Runtime), `RenderGridDeveloper` (Runtime), `RenderGridEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-23 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RenderGrid) | |

## 用途

RenderGrid 插件是一个专为电影渲染管线（Movie Render Queue， MRQ）设计的高级任务管理与批处理系统。它旨在解决为大量序列生成高质量渲染输出时，手动管理复杂设置和顺序执行的效率瓶颈。

其核心功能是提供一个**渲染网格**或**渲染队列**系统，允许用户：
1.  **批量化提交**：将基于关卡序列（Level Sequence）的渲染任务（Jobs）组织并批量提交到 MRQ。
2.  **队列化管理**：对渲染队列进行启动、暂停、恢复等控制，并支持在渲染过程中动态添加新任务。
3.  **参数化覆盖**：允许为单个任务覆盖输出分辨率等渲染设置，实现灵活的变体渲染。
4.  **蓝图集成**：通过蓝图事件（如 Begin/End Render）和公开的队列控制函数，允许通过可视化脚本驱动整个渲染流程。

它解决了在项目后期阶段，当需要为大量镜头或变体生成最终渲染时，缺乏一个集中化、可编程且与蓝图深度集成的批量渲染解决方案的问题。

## 使用场景

- 你是一个电影制作者或技术美术，正在使用 UE5 的电影渲染管线（MRQ）制作过场动画。
- 你需要同时渲染多个摄像机角度或序列的多个版本（如不同光照、天气），并希望自动化这个过程。
- 你希望通过蓝图脚本来动态控制渲染任务（例如，根据游戏内事件触发特定序列的渲染），而不是在编辑器中手动排队。
- 你的团队需要一个可复用的、配置化的渲染预设，以便标准化项目的渲染输出流程。

## 蓝图用法

蓝图功能主要通过 `RenderGrid` 运行时模块提供的事件和函数实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Begin Render` / `End Render` | 渲染队列开始或结束时调用的蓝图事件。 | `URenderGridQueue` |
| `Set Resolution Override` | 为指定的渲染任务设置覆盖的输出分辨率。 | `URenderGridJob` |
| `Add Job to Queue` | 将一个配置好的渲染任务添加到渲染队列中。 | `URenderGridQueue` |
| `Start Queue` / `Pause Queue` / `Resume Queue` | 控制渲染队列的执行。 | `URenderGridQueue` |

### 使用示例（蓝图描述）

1.  创建一个 `URenderGridJob` 对象，并为其指定一个 `ULevelSequence` 资产。
2.  （可选）调用该 Job 对象的 `Set Resolution Override` 节点，设置自定义的输出分辨率。
3.  通过 `Add Job to Queue` 节点将该 Job 添加到 `URenderGridQueue` 实例中。此步骤可在队列渲染过程中重复执行以动态添加任务。
4.  调用 `Start Queue` 节点开始渲染。队列会为每个 Job 调用电影渲染管线进行处理。
5.  在队列开始和结束时，可以绑定到 `Begin Render` 和 `End Render` 事件来执行自定义逻辑，例如通知 UI 或启动后续处理流程。

## C++ 用法

### 头文件引入

```cpp
#include "RenderGridModule.h"
// 或根据具体功能引入特定的头文件，如 RenderGridJob.h, RenderGridQueue.h
```

### 基本用法

创建和管理一个简单的渲染队列。
```cpp
// 获取渲染网格模块
IRenderGridModule& RenderGridModule = IRenderGridModule::Get();

// 创建一个新的渲染队列实例
URenderGridQueue* MyRenderQueue = NewObject<URenderGridQueue>();

// 创建一个渲染任务
URenderGridJob* NewJob = NewObject<URenderGridJob>();
NewJob->SetLevelSequence(MyLevelSequenceAsset);

// 设置该任务的输出分辨率覆盖（可选）
NewJob->SetResolutionOverride(FIntPoint(1920, 1080));

// 将任务添加到队列
MyRenderQueue->AddJob(NewJob);

// 启动渲染队列
MyRenderQueue->StartQueue();
```

### 进阶用法

结合蓝图事件回调，在 C++ 中监听渲染队列的生命周期。
```cpp
// 绑定队列的渲染事件
MyRenderQueue->OnBeginRender.AddDynamic(this, &UMyActor::HandleRenderBegin);
MyRenderQueue->OnEndRender.AddDynamic(this, &UMyActor::HandleRenderEnd);

// 在渲染过程中动态添加新任务
void UMyActor::HandleRenderBegin()
{
    // 在渲染开始后，异步或基于某些条件创建并添加新任务
    URenderGridJob* DynamicJob = CreateDynamicRenderJob();
    MyRenderQueue->AddJob(DynamicJob);
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建并启动一个包含单个任务的渲染网格队列。
```cpp
// MyRenderDemo.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RenderGridQueue.h"
#include "RenderGridJob.h"
#include "MyRenderDemo.generated.h"

UCLASS()
class AMyRenderDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyRenderDemo();

    UFUNCTION(BlueprintCallable, Category = "RenderGridDemo")
    void StartDemoRender();

private:
    UPROPERTY()
    TObjectPtr<URenderGridQueue> RenderQueue;
};

// MyRenderDemo.cpp
#include "MyRenderDemo.h"
#include "LevelSequence.h"

AMyRenderDemo::AMyRenderDemo()
{
    PrimaryActorTick.bCanEverTick = false;
    RenderQueue = CreateDefaultSubobject<URenderGridQueue>(TEXT("DemoRenderQueue"));
}

void AMyRenderDemo::StartDemoRender()
{
    // 确保队列有效
    if (!RenderQueue) return;

    // 加载一个关卡序列资产（请替换为你的实际资产路径）
    ULevelSequence* Sequence = LoadObject<ULevelSequence>(nullptr, TEXT("/Game/Cinematics/MySequence"));

    if (Sequence)
    {
        // 创建任务并配置
        URenderGridJob* Job = NewObject<URenderGridJob>(RenderQueue);
        Job->SetLevelSequence(Sequence);
        Job->SetResolutionOverride(FIntPoint(3840, 2160)); // 4K 分辨率

        // 添加并启动队列
        RenderQueue->AddJob(Job);
        RenderQueue->StartQueue();
    }
}
```

## 模块依赖

使用此插件的功能时，你的项目或模块可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `RenderGrid` | 提供渲染队列（`URenderGridQueue`）、任务（`URenderGridJob`）等核心运行时类和蓝图 API。 |
| `RenderGridDeveloper` | 提供开发者工具或底层支持功能，供 `RenderGrid` 和 `RenderGridEditor` 使用。 |
| `RenderGridEditor` | 提供编辑器集成，如自定义 UI、资产工厂等，用于在编辑器中配置渲染网格。 |

**注意**：由于此插件默认禁用（`EnabledByDefault: false`），你需要在项目的 `.uproject` 文件或编辑器插件设置中手动启用它。作为运行时和编辑器功能的结合体，根据你的使用场景（仅运行时蓝图逻辑 vs 需要编辑器配置），可能只需依赖 `RenderGrid` 或同时需要 `RenderGridEditor`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 UE::FSharedString，优化内存。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移至新的 UE_LOGF 宏。 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复以释放内存，进行性能优化。 |
| 2025-09-15 | `60737405` | Render Grid: fixed crash when passing in an empty string when setting remote control values | 修复设置远程控制值时传入空字符串导致崩溃的问题。 |
| 2025-06-11 | `b57e00bc` | Replace some usages of FORCEINLINE with inline in Rendering modules. | 在渲染模块中将部分 FORCEINLINE 用法替换为 inline。 |

### 维护评价

- **创建时间**：插件于 2022 年 8 月创建，至今约 3 年。
- **活跃度**：插件仍在维护中。最近的提交（2026年4月）集中在**代码质量与性能优化**（如内存管理、API现代化）和**小规模 bug 修复**（如修复特定操作导致的崩溃）。这表明插件处于稳定维护期，但近期没有大的功能更新。
- **状态**：这是一个**实验性插件**（`IsExperimentalVersion: true`），且默认未启用。这意味着它的 API 和功能未来可能会有变化，目前建议用于特定需求或原型验证，而非用于需要长期稳定性的最终项目核心功能。
- **推荐**：如果你有明确的批量管理 MRQ 渲染任务的需求，并且能够接受其**实验性**状态，此插件提供了一个有价值的蓝图和 C++ 集成框架。否则，对于简单的渲染队列需求，直接使用引擎原生的 MRQ 界面可能更直接。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RenderGrid)
- [官方文档] 无
- [测试用例] 未在提供信息中找到特定路径。