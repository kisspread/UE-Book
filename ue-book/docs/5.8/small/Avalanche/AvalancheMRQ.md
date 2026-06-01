# Motion Design

> Compositing, designer and broadcasting tool.
> 
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheMRQ` (Runtime), ... (共 43 个模块) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design（Avalanche）是一个集成化的运动设计工具集，专为虚拟制片和实时广播场景打造。它将场景构建、动态图形（Motion Graphics）、序列编排、材质设计、过渡效果等功能整合到UE的编辑器中。该插件的核心价值在于提供了一套端到端的解决方案，用于在虚幻引擎内创建、编排和播放复杂的动态图形和实时广播内容（如新闻包装、体育转播图形），并支持通过Sequencer和Movie Render Queue进行高质量的离线渲染。

## 使用场景

-   **虚拟制片/直播**：在新闻、体育、演唱会等直播场景中，实时创建、控制和播出动态图形、字幕条、比分板等视觉元素。
-   **动态图形制作**：在UE中像使用专业Motion Graphics软件（如After Effects）一样，设计基于3D文本、形状、特效的动画序列。
-   **复杂场景排版**：利用内置的场景树和节点系统，管理和组织大量动态生成的UI元素、3D资产和特效。
-   **高质量离线渲染**：通过集成Movie Render Queue，将精心设计的动态图形序列渲染成电影级质量的最终输出文件。

## 蓝图用法

该插件主要通过编辑器内工具和资产驱动，直接暴露给蓝图的公共函数相对较少。核心的蓝图交互通常围绕 `UAvaRundown`（节目单）资产展开，用于在运行时或编辑器中控制页面、播放和切换。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Rundown` (属性) | 用于引用一个节目单（UAvaRundown）资产。 | `FAvaMRQRundownPage` |
| `PageId` (属性) | 指定节目单中的页面ID。 | `FAvaMRQRundownPage` |

### 使用示例（蓝图描述）

在 **Movie Pipeline** 的配置资产中：
1. 添加一个 `Rundown Page` 类型的设置（`UAvaMRQRundownPageSetting`）。
2. 在该设置的细节面板中，找到 `Motion Design Sequence` 分类。
3. 在 `Rundown` 属性中，指定你想要渲染的 `UAvaRundown` 资产。
4. 在 `PageId` 属性中，输入该节目单中具体要渲染的页面ID。
这样，当你使用Movie Render Queue渲染序列时，它会自动加载并渲染指定节目单页面的动态图形内容。

## C++ 用法

该插件的C++使用主要集中在编辑器工具开发和自定义模块功能扩展上。运行时功能的访问通常通过 `UObject` 和 `FAva...` 系列结构体进行。

### 头文件引入

```cpp
// 引入AvalancheMRQ模块的核心设置类
#include "AvaMRQRundownPageSetting.h"
```

### 基本用法

从测试案例（若有）或核心类中提取，设置Movie Pipeline的Rundown页面配置。

```cpp
// 来源：基于 UAvaMRQRundownPageSetting 的设计
#include "AvaMRQRundownPageSetting.h"
#include "MoviePipeline.h"

void SetupMotionDesignMRQRender(UMoviePipeline* InPipeline)
{
    if (!InPipeline)
    {
        return;
    }

    // 获取或添加一个 Rundown Page 设置到 Movie Pipeline 配置中
    UAvaMRQRundownPageSetting* RundownPageSetting = InPipeline->FindOrAddSettingForShot<UAvaMRQRundownPageSetting>();
    if (RundownPageSetting)
    {
        // 配置节目单和页面
        FAvaMRQRundownPage& PageConfig = RundownPageSetting->RundownPage;
        // PageConfig.Rundown = /* 你的 UAvaRundown 资产软引用 */;
        // PageConfig.PageId = 0;
    }
}
```

### 进阶用法

结合整个Motion Design插件，通过C++创建和操作动态设计元素（假设存在更底层的管理器类）。

```cpp
// 假设性示例，用于说明模块间的协同
#include "AvaSceneTree.h"
#include "AvaText3DActor.h"
// ... 其他Avalanche模块头文件

void CreateAndAnimateMotionDesignElement(UWorld* World)
{
    if (!World) return;

    // 1. 通过场景树系统创建一个新的3D文本元素
    // AAvaText3DActor* TextActor = ... 创建或生成一个文本Actor ...

    // 2. 使用Property Animator（如果公开API）为其添加动画
    // UAvaPropertyAnimator* Animator = ... 获取组件 ...

    // 3. 将其添加到序列中（通过AvaSequence模块）
    // UAvaSequence* Sequence = ... 获取或创建序列 ...
    // Sequence->AddObjectToSequence(TextActor);
}
```

## Demo 示例

一个最小化的示例，演示如何在C++中配置 `AvalancheMRQ` 模块的设置。

**AvaMRQDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AvaMRQDemoActor.generated.h"

class UAvaRundown;
class UMoviePipeline;

UCLASS()
class AAvaMRQDemoActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AAvaMRQDemoActor();

	// 配置MRQ渲染指定的节目单页面
	void ConfigureMRQForRundownPage(UMoviePipeline* Pipeline, UAvaRundown* InRundown, int32 InPageId);

protected:
	virtual void BeginPlay() override;
};
```

**AvaMRQDemoActor.cpp**
```cpp
#include "AvaMRQDemoActor.h"
#include "AvaMRQRundownPageSetting.h"
#include "MoviePipeline.h"

AAvaMRQDemoActor::AAvaMRQDemoActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AAvaMRQDemoActor::BeginPlay()
{
	Super::BeginPlay();
}

void AAvaMRQDemoActor::ConfigureMRQForRundownPage(UMoviePipeline* Pipeline, UAvaRundown* InRundown, int32 InPageId)
{
	if (!Pipeline) return;

	// 在流水线中查找或添加我们的自定义设置
	UAvaMRQRundownPageSetting* Setting = Pipeline->FindOrAddSettingForShot<UAvaMRQRundownPageSetting>();
	if (Setting)
	{
		Setting->RundownPage.Rundown = InRundown; // 设置软引用
		Setting->RundownPage.PageId = InPageId;
		UE_LOG(LogTemp, Log, TEXT("MRQ Rundown page setting configured for page %d"), InPageId);
	}
}
```

## 模块依赖

使用 `AvalancheMRQ` 模块，你的项目或模块的 `Build.cs` 文件需要添加以下依赖（除了标准依赖外）：

| 模块 | 用途 |
|---|---|
| `Sequencer` | 核心序列器模块，用于动画和编排，是Motion Design序列功能的基础。 |

**注意**：这只是当前文档所关注的 `AvalancheMRQ` 模块的直接依赖。整个Motion Design插件拥有庞大的依赖网络（如描述中所列），要使用其完整功能，你的项目可能需要依赖更多的 `Avalanche*` 模块以及外部插件（如 `Text3D`, `RemoteControl` 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将Motion Design相关编辑器标签页分组，优化UI组织。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为MRQ的节目单页面设置添加了使用分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde... | 增强节目控制工具栏，增加页面加载选项（全部、下一个、选定）。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用3D文本和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a context | 重构视口相关代码，改进客户端通知逻辑。 |

### 维护评价

**活跃维护**。Motion Design插件创建于2025年5月，历史不到一年，属于较新的插件。从近期的Git提交历史看，开发团队在持续进行功能增强（如添加分析、新UI选项）、bug修复和代码重构，维护频率很高。作为虚拟制片的核心工具之一，它显然是Epic重点投入的项目。对于需要在UE中实现高质量、可编程动态图形和实时广播图形的项目，这是一个非常值得采用且处于积极演进中的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档]() (暂无直接对应链接，通常包含在UE虚拟制片文档中)