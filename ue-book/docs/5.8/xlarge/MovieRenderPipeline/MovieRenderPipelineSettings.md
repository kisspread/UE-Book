# Movie Render Queue Settings

> Advanced movie rendering pipeline for use in creating rendered cinematics or other multi-media creation.

| 属性 | 值 |
|---|---|
| 中文名 | 影片渲染队列设置 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、设置类） |
| 模块 | `MovieRenderPipelineSettings` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-30 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline) | |

## 用途

`MovieRenderPipelineSettings` 是 `MovieRenderPipeline` 插件的核心配置模块。它提供了一系列用于精细化控制电影渲染过程的可插拔设置项。其主要解决的问题是：在通过 Sequencer 驱动、渲染高质量电影级序列时，如何方便地批量应用和管理一系列渲染参数（如抗锯齿、控制台变量、后处理效果、画面叠加信息等），并确保这些参数在渲染前后能够自动保存和恢复，避免对编辑器状态造成污染。

与直接在渲染前手动执行控制台命令或调整参数相比，这个模块将配置资产化，实现了可复用、可组合的渲染设置工作流，是电影渲染管线中可定制性的基石。

## 使用场景

- **批量渲染不同质量的镜头**：你正在为一个过场动画创建多个不同LOD（细节层次）或分辨率的版本，可以创建多个配置了不同抗锯齿方法、分辨率、或控制台变量（如 `r.ScreenPercentage`）的设置资产，并在渲染队列中快速切换。
- **需要在渲染输出中添加信息覆盖**：你想在最终渲染的视频或图像序列上叠加渲染进度、序列时间、公司标识等信息，可以使用“Burn In”或“UI Renderer”设置来实现。
- **临时调整渲染质量参数**：渲染高分辨率输出时，需要临时调整一些引擎的全局渲染设置（如阴影质量、后处理），渲染完成后又希望恢复原状，可以使用“Console Variables”设置来安全地应用和恢复这些参数。

## 蓝图用法

蓝图主要用于在运行时动态修改渲染队列任务的设置，或从设置资产中获取数据。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetConsoleVariables` | 获取此设置中定义的所有控制台变量覆盖的副本。 | `UMoviePipelineConsoleVariableSetting` |
| `RemoveConsoleVariable` | 根据名称移除一个控制台变量覆盖。 | `UMoviePipelineConsoleVariableSetting` |
| `AddOrUpdateConsoleVariable` | 添加或更新一个控制台变量覆盖。如果已存在同名变量，则更新其值。 | `UMoviePipelineConsoleVariableSetting` |
| `AddConsoleVariable` | 添加一个新的控制台变量覆盖，允许存在同名变量。 | `UMoviePipelineConsoleVariableSetting` |
| `UpdateConsoleVariableEnableState` | 更新指定名称控制台变量的启用/禁用状态。 | `UMoviePipelineConsoleVariableSetting` |
| `OnOutputFrameStarted` | 蓝图可实现事件，当每一输出帧开始时在 Burn In Widget 上调用，传入当前的管线对象。 | `UMoviePipelineBurnInWidget` |

### 使用示例（蓝图描述）

**示例 1：动态添加/更新控制台变量**
1. 获取你的 `UMoviePipeline` 对象（通常来自渲染队列作业）。
2. 调用 `FindSettingsByClass` 函数，传入 `UMoviePipelineConsoleVariableSetting::StaticClass()`，以获取当前作业关联的控制台变量设置对象。
3. 从该对象上调用 `AddOrUpdateConsoleVariable` 节点，输入变量名（如 `"r.DefaultFeature.AntiAliasing"`）和新的值（如 `0.0`），即可在渲染时临时关闭抗锯齿。

**示例 2：创建自定义的 Burn In Widget**
1. 创建一个新的 Widget 蓝图，继承自 `UMoviePipelineBurnInWidget`。
2. 在该蓝图中，重写 `OnOutputFrameStarted` 事件。
3. 在该事件中，通过传入的 `ForPipeline` 参数（`UMoviePipeline*`）获取当前渲染作业和镜头信息，使用这些信息来更新你 Widget 上的文本内容（如显示当前镜头名称、总进度百分比）。
4. 在渲染队列的配置中，将 `Burn In` 设置的 `Burn In Class` 属性指向你创建的这个 Widget 蓝图类。

## C++ 用法

本模块主要为蓝图和编辑器提供设置，直接的 C++ 编程较少。通常的用法是在自定义的 `UMoviePipelineSetting` 子类中引用或集成这些设置。

### 头文件引入

```cpp
#include "MoviePipelineConsoleVariableSetting.h"
#include "MoviePipelineBurnInSetting.h"
// 包含需要使用的具体设置类的头文件
```

### 基本用法

假设你需要在一个自定义的渲染管线设置中，检查或修改控制台变量设置。以下是一个概念性的示例，展示了如何与 `UMoviePipelineConsoleVariableSetting` 交互。

```cpp
// 假设你已经获得了一个 UMoviePipeline* InPipeline 对象
// 获取所有已配置的设置
TArray<UMoviePipelineSetting*> AllSettings = InPipeline->GetSettings()->GetAllSettings();

// 查找控制台变量设置
UMoviePipelineConsoleVariableSetting* CVarSetting = nullptr;
for (UMoviePipelineSetting* Setting : AllSettings)
{
    CVarSetting = Cast<UMoviePipelineConsoleVariableSetting>(Setting);
    if (CVarSetting)
    {
        break;
    }
}

if (CVarSetting)
{
    // 获取当前的控制台变量列表（只读）
    TArray<FMoviePipelineConsoleVariableEntry> CVars = CVarSetting->GetConsoleVariables();
    
    // 程序化地添加一个新的变量覆盖
    CVarSetting->AddConsoleVariable(TEXT("r.MyCustomCVar"), 1.0f);
    
    // 移除一个变量
    CVarSetting->RemoveConsoleVariable(TEXT("r.AnotherCVar"));
}
```

### 进阶用法

更高级的用法是创建自己的 `UMoviePipelineSetting` 子类，并在其中利用其他设置。例如，你可能想在渲染开始前，根据某个自定义设置的值来动态修改控制台变量设置。

```cpp
// MyCustomSetting.h
UCLASS()
class UMyCustomSetting : public UMoviePipelineSetting
{
    GENERATED_BODY()
    
    virtual void SetupForPipelineImpl(UMoviePipeline* InPipeline) override
    {
        // 在管线设置阶段，找到并修改控制台变量设置
        UMoviePipelineConsoleVariableSetting* CVarSetting = InPipeline->GetSettings()->FindSetting<UMoviePipelineConsoleVariableSetting>();
        if (CVarSetting)
        {
            // 根据我自己的设置，决定应用什么CVar
            FString TargetCVar = (bUseHighQuality ? TEXT("r.PresetQuality") : TEXT("r.PresetQuality.Low"));
            CVarSetting->AddOrUpdateConsoleVariable(TargetCVar, 1.0f);
        }
    }
    // ... 其他成员和函数
};
```

## Demo 示例

一个简单的自定义 Burn In Widget，用于在渲染输出上显示作业名称。

**文件：MyCustomBurnInWidget.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MoviePipelineBurnInWidget.h"
#include "MyCustomBurnInWidget.generated.h"

UCLASS()
class UMyCustomBurnInWidget : public UMoviePipelineBurnInWidget
{
    GENERATED_BODY()

public:
    // 蓝图可实现事件，在这里获取管线信息并更新UI
    virtual void OnOutputFrameStarted_Implementation(UMoviePipeline* ForPipeline) override;
};
```

**文件：MyCustomBurnInWidget.cpp**
```cpp
#include "MyCustomBurnInWidget.h"
#include "MoviePipeline.h"
#include "MoviePipelineExecutor.h"
#include "Components/TextBlock.h"

void UMyCustomBurnInWidget::OnOutputFrameStarted_Implementation(UMoviePipeline* ForPipeline)
{
    // 检查管线和作业是否有效
    if (!ForPipeline || !ForPipeline->GetActiveExecutorJob())
    {
        return;
    }

    // 获取作业名称
    FString JobName = ForPipeline->GetActiveExecutorJob()->JobName;

    // 假设你的Widget蓝图中有一个名为“JobNameText”的TextBlock控件
    // 注意：这里需要通过FindBinding或直接引用获取控件指针，具体取决于你的Widget实现
    UTextBlock* JobNameTextWidget = Cast<UTextBlock>(GetWidgetFromName(TEXT("JobNameText")));
    if (JobNameTextWidget)
    {
        JobNameTextWidget->SetText(FText::FromString(FString::Printf(TEXT("Rendering: %s"), *JobName)));
    }
}
```
*注：要使用此Widget，你需要在UMG设计器中创建对应的Widget蓝图，继承自`UMyCustomBurnInWidget`（或直接使用`UMoviePipelineBurnInWidget`并添加名为`JobNameText`的TextBlock），然后在渲染队列的Burn In设置中引用这个蓝图类。*

## 模块依赖

本模块的依赖已在 `MovieRenderPipelineSettings.Build.cs` 中指定。

| 模块 | 用途 |
|---|---|
| `ConsoleVariablesEditor` | 用于与控制台变量编辑器交互，支持 `ConsoleVariablePresets`（控制台变量预设）功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为图形式管线和nDisplay添加了EXR多图层支持。 |
| 2026-05-26 | `353f4079` | MoviePipeline: Fixed an issue with layer warm-ups in the graph that could cause some skeletal meshes | 修复了图形式管线中图层预热可能导致骨骼网格体显示异常的问题。 |
| 2026-05-26 | `5b4aedd1` | MoviePipeline: Reverting a change made to letterboxing, which was meant to correct it when it's comb | 回退了对“信箱模式”的修改，该修改旨在组合渲染时进行校正。 |
| 2026-05-21 | `a1446fbd` | MoviePipeline: Added an "Anti Aliasing Method" property to the Basic configuration type for the Defe | 为确定性的渲染管线基本配置类型添加了“抗锯齿方法”属性。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为动态设计模块在使用“节目单”设置时添加了影片渲染队列分析。 |

### 维护评价

该模块是 UE5 电影渲染管线（MRQ）的核心组件，自 2019 年创建以来一直是活跃开发的重点。从近期的提交记录可以看出，开发团队持续为其添加新功能（如新的抗锯齿方法配置选项、EXR多图层支持）并修复 bug，以适配更复杂的渲染场景（如 nDisplay、图形式管线）。虽然标记为默认不启用（`EnabledByDefault=false`），但它是创建高质量电影级渲染输出的标准和推荐方式。**该模块处于积极维护状态，是进行专业渲染工作的可靠选择，推荐使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/rendering-high-quality-frames-with-movie-render-queue-in-unreal-engine/)（Movie Render Queue 官方文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline/Tests)（位于插件目录下的Tests文件夹）