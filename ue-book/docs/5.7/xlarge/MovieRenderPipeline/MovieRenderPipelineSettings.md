# Movie Render Queue

> Advanced movie rendering pipeline for use in creating rendered cinematics or other multi-media creation.

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `MovieRenderPipelineCore` (Runtime), `MovieRenderPipelineEditor` (Runtime), `MovieRenderPipelineMP4Encoder` (Runtime), `MovieRenderPipelineRenderPasses` (Runtime), `MovieRenderPipelineSettings` (Runtime), `UEOpenExrRTTI` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-30 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline) | |

## 用途

Movie Render Pipeline (MRQ) 是 UE5 中用于高质量电影渲染的核心系统。它解决了传统 Sequencer 渲染器（`MovieSceneCapture`）在功能、灵活性和可扩展性上的局限性。MRQ 提供了一个完整的、可配置的渲染管线，允许用户：

1.  **定义复杂的渲染任务**：通过“作业”（Job）和“镜头”（Shot）的概念，精确控制要渲染的序列、关卡、配置和输出设置。
2.  **支持多通道渲染**：可以同时输出多种渲染通道（如 Final Image、World Position、Object ID 等），并支持多层 EXR 文件。
3.  **高度可定制**：通过“设置”（Settings）和“渲染通道”（Render Passes）系统，用户可以添加自定义的渲染逻辑、后处理效果、UI 叠加（Burn-in）等。
4.  **批处理与队列管理**：提供“渲染队列”（Render Queue）编辑器窗口，可以一次性设置和提交多个渲染作业，并支持命令行渲染。
5.  **集成控制台变量**：允许在渲染期间临时覆盖控制台变量（CVars），以确保渲染结果的一致性和质量。

简而言之，MRQ 是 UE5 中用于生成最终交付级渲染内容（如游戏过场动画、建筑可视化、产品展示视频）的专业工具。

## 使用场景

-   你需要为游戏制作一段高质量的过场动画视频，需要输出 4K 分辨率、60fps，并包含多个摄像机角度的镜头。
-   你需要渲染一个建筑可视化的漫游视频，并希望同时输出深度通道（World Position Pass）用于后期合成。
-   你需要在渲染的视频上叠加时间码、帧号、项目名称等信息（Burn-in）。
-   你需要批量渲染一个序列中的多个镜头，并希望它们使用不同的配置（如不同的分辨率或后期处理）。
-   你需要在渲染时强制启用或禁用某些图形特性（如光线追踪、Lumen），以确保渲染结果与预期一致。

## 蓝图用法

MRQ 的蓝图 API 主要集中在 `MovieRenderPipelineSettings` 模块中，用于在运行时或编辑器脚本中配置渲染设置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetConsoleVariables` | 获取当前设置中所有的控制台变量覆盖项。 | `UMoviePipelineConsoleVariableSetting` |
| `AddConsoleVariable` | 添加或更新一个控制台变量覆盖项。 | `UMoviePipelineConsoleVariableSetting` |
| `RemoveConsoleVariable` | 根据名称移除一个或多个控制台变量覆盖项。 | `UMoviePipelineConsoleVariableSetting` |
| `OnOutputFrameStarted` | **事件**：当输出帧开始渲染时调用，用于更新 Burn-in Widget 的内容。 | `UMoviePipelineBurnInWidget` |

### 使用示例（蓝图描述）

**示例1：配置控制台变量设置**
1.  在你的 `UMoviePipeline` 配置资产中，找到或添加一个 `UMoviePipelineConsoleVariableSetting`。
2.  在蓝图中，获取对该设置对象的引用。
3.  使用 `AddConsoleVariable` 节点，传入 CVar 名称（如 `r.ScreenPercentage`）和期望的值（如 `150.0`）。
4.  使用 `RemoveConsoleVariable` 节点，传入 CVar 名称来移除之前的覆盖。

**示例2：创建自定义 Burn-in Widget**
1.  创建一个新的蓝图类，父类选择 `UMoviePipelineBurnInWidget`。
2.  在该蓝图中，重写 `OnOutputFrameStarted` 事件。
3.  在该事件中，你可以访问传入的 `UMoviePipeline` 对象，获取当前帧信息（如时间码、镜头名称），并更新 Widget 上的文本或图形。
4.  将这个自定义 Widget 类设置到 `UMoviePipelineBurnInSetting` 的 `BurnInClass` 属性中。

## C++ 用法

### 头文件引入

```cpp
#include "MoviePipelineBurnInWidget.h"
#include "MoviePipelineConsoleVariableSetting.h"
```

### 基本用法

**创建自定义 Burn-in Widget (C++)**
```cpp
// MyBurnInWidget.h
#pragma once
#include "MoviePipelineBurnInWidget.h"
#include "MyBurnInWidget.generated.h"

UCLASS()
class UMyBurnInWidget : public UMoviePipelineBurnInWidget
{
    GENERATED_BODY()
public:
    // 重写蓝图可实现事件
    UFUNCTION(BlueprintImplementableEvent)
    void OnOutputFrameStarted(UMoviePipeline* ForPipeline);
};
```

**配置控制台变量设置 (C++)**
```cpp
// 假设你已经有一个 UMoviePipelineConsoleVariableSetting* ConsoleVarSetting
// 添加一个 CVar 覆盖
ConsoleVarSetting->AddConsoleVariable(TEXT("r.ScreenPercentage"), TEXT("150.0"));

// 移除一个 CVar 覆盖
ConsoleVarSetting->RemoveConsoleVariable(TEXT("r.ScreenPercentage"));

// 获取所有覆盖项
TArray<FMoviePipelineConsoleVariableEntry> AllCVars = ConsoleVarSetting->GetConsoleVariables();
```
*（代码逻辑基于 `MoviePipelineConsoleVariableSetting.h` 中的函数声明）*

### 进阶用法

**在渲染前动态应用 CVar 预设**
```cpp
// 假设你有一个 ConsoleVariablesEditor 的资产 (UConsoleVariablesAsset)
// 并且你的 UMoviePipelineConsoleVariableSetting 有一个 ConsoleVariablePresets 数组
TScriptInterface<IMovieSceneConsoleVariableTrackInterface> PresetInterface;
PresetInterface.SetObject(MyConsoleVariablesAsset);
ConsoleVarSetting->ConsoleVariablePresets.Add(PresetInterface);

// 在渲染开始时，MRQ 会按顺序应用这些预设，然后再应用 ConsoleVariable 数组中的覆盖。
```

## Demo 示例

**自定义 Burn-in Widget (C++)**

```cpp
// SimpleBurnInWidget.h
#pragma once
#include "MoviePipelineBurnInWidget.h"
#include "SimpleBurnInWidget.generated.h"

UCLASS(Blueprintable)
class USimpleBurnInWidget : public UMoviePipelineBurnInWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, Category = "Burn In")
    FString CurrentTimeCode;

    UPROPERTY(BlueprintReadWrite, Category = "Burn In")
    FString CurrentShotName;

    // 重写蓝图可实现事件，在蓝图中实现 UI 更新
    UFUNCTION(BlueprintImplementableEvent)
    void OnOutputFrameStarted(UMoviePipeline* ForPipeline);
};
```

```cpp
// SimpleBurnInWidget.cpp
#include "SimpleBurnInWidget.h"
#include "MoviePipeline.h"
#include "MoviePipelineOutputBuilder.h"

void USimpleBurnInWidget::OnOutputFrameStarted_Implementation(UMoviePipeline* ForPipeline)
{
    if (ForPipeline)
    {
        // 获取当前帧的时间码和镜头信息
        FTimecode Timecode = ForPipeline->GetOutputBuilder()->GetTimecode();
        CurrentTimeCode = Timecode.ToString();

        // 获取当前正在渲染的镜头名称（需要从 Pipeline 的上下文中获取）
        // 这里仅为示例，实际实现可能更复杂
        CurrentShotName = TEXT("Shot_001");

        // 在蓝图中，你可以将这些变量绑定到 Text Block 控件上
    }
}
```

## 模块依赖

`MovieRenderPipelineSettings` 模块依赖于 `ConsoleVariablesEditor` 模块，以支持从控制台变量编辑器资产中加载预设。其他模块的依赖关系未在提供的信息中明确，但整个插件通常依赖于 `MovieScene`, `LevelSequence`, `RenderCore` 等核心模块。

| 模块 | 用途 |
|---|---|
| `ConsoleVariablesEditor` | 用于集成控制台变量编辑器资产（预设）功能。 |

## 维护状态

### 近期更新

```
- 2025-10-03 ef5c9d1 Added MinPriority to SetWithCurrentPriority and ReplaceCurrentPriorityAndTag, it represents the minimum priority we will set that cvar. Improve the log reporting when SetWithCurrentPriority and ReplaceCurrentPriorityAndTag are used to replace SetByConstructor values Fix usage in the MRQ pipeline that was triggering the log #jira UE-319254 #rb Josh.Adams
- 2025-09-15 8bbf8cb MoviePipeline: Fixed an issue where a long job comment in the burn-in would not perform a layout properly on the first frame (fixed in both the graph and presets).
- 2025-08-20 5809ddf MovieGraph: Add support for boolean cvar values in Console Variable Preset assets. These were supported by the Console Variable Editor, but would fail to apply in an MRQ/MRG job.
```

### 维护评价

Movie Render Pipeline 是 UE5 中**活跃维护**的核心功能之一。
-   **创建时间**：约 6 年前（2019年），已相当成熟。
-   **近期更新**：最近 3 次提交均发生在 2025 年，内容涉及功能增强（CVar 优先级控制）、Bug 修复（Burn-in 布局）和兼容性改进（布尔型 CVar 支持）。这表明 Epic 仍在持续投入开发。
-   **状态**：作为官方推荐的电影渲染解决方案，它取代了旧的 `MovieSceneCapture`，是生产环境中的标准工具。
-   **推荐**：**强烈推荐使用**。对于任何需要高质量、可控渲染输出的项目，MRQ 都是首选。尽管它默认禁用，但启用和配置后，其功能远超基础渲染器。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/rendering-high-quality-frames-with-movie-render-queue-in-unreal-engine/) (UE5 官方文档链接，非 .uplugin 提供)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline/Tests) (推测路径，实际测试可能位于 `Engine/Tests/` 下)