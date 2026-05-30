# Motion Design

> Compositing, designer and broadcasting tool.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), ... (共 42 个模块) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design 是一个集成在虚幻引擎虚拟制作 (Virtual Production) 工作流中的高级视觉设计与广播工具套件。它并非单一功能插件，而是一个庞大的模块集合（42个模块），旨在提供一套完整的工具链，用于在 UE 内部完成传统上由 After Effects、Cinema 4D 等软件承担的动态图形、视觉合成和实时广播内容制作任务。它集成了场景合成、动态材质、几何脚本、远程控制、SVG 导入、3D文字生成等众多子系统，并支持与 Sequencer 联动进行动画和播出控制。该插件从实验阶段 (Experimental) 迁移至虚拟制作分类，表明其功能已趋于稳定并成为虚拟制作管线的重要组成部分。

## 使用场景

- **电视/流媒体直播包装**：实时创建并控制虚拟演播室中的动态图形、Logo动画、比分板和新闻滚动条。
- **虚拟演唱会/活动**：设计和控制舞台视觉特效、全息投影和实时生成的艺术元素。
- **沉浸式体验与主题公园**：开发并管理大型实时视觉内容序列，支持交互和触发。
- **产品发布与可视化**：创建高质量的动态产品展示动画，并集成实时数据驱动。

## 蓝图用法

由于插件规模巨大且当前提供的核心源码为功能性测试类，典型的业务蓝图节点分散在众多子模块中。以下示例基于提供的 `AvalancheFunctionalTest` 模块，展示其为 Motion Design 级别场景定制的测试功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Wait For Actor Ready` | 在截图前等待指定的 Actor（尤其是包含 Niagara 系统的 Actor）完全初始化，避免截取未就绪状态。 | `AScreenshotFunctionalTestAvalanche` |
| `Actor To Wait For` | 指定需要等待就绪的 Actor 引用。 | `AScreenshotFunctionalTestAvalanche` |
| `Max Actor Wait Time` | 设置等待 Actor 就绪的最大超时时间（秒）。 | `AScreenshotFunctionalTestAvalanche` |

### 使用示例（蓝图描述）

在功能性测试关卡中：
1. 放置一个 `Screenshot Functional Test Motion Design` Actor。
2. 设置 `Wait For Actor Ready` 为 `true`。
3. 将 `Actor To Wait For` 拖拽指定为场景中一个包含复杂 Niagara 粒子系统的关键 Actor。
4. 设置 `Max Actor Wait Time` 为一个合理值（如 5.0 秒）。
5. 测试开始时，该 Actor 会先检查目标 Actor 及其组件是否就绪，就绪后才进行截图，确保测试截图的稳定性。

## C++ 用法

以下示例展示了如何在 C++ 中创建一个针对 Motion Design 级别场景优化的截图功能测试，解决常规测试在该场景下遇到的 CVar 优先级和 PIE 截图代理问题。

### 头文件引入

```cpp
#include "ScreenshotFunctionalTestAvalanche.h"
```

### 基本用法

这个类主要作为基类被蓝图继承使用。在 C++ 中，你可以通过继承它来创建更定制化的测试。

```cpp
// 示例：继承自 Avalanche 截图测试，添加自定义逻辑
// 来源: 基于 Public/ScreenshotFunctionalTestAvalanche.h 的推断用法
UCLASS()
class AMyMotionDesignTest : public AScreenshotFunctionalTestAvalanche
{
    GENERATED_BODY()

protected:
    virtual void PrepareTest() override
    {
        Super::PrepareTest();
        // 可以在此处为特定 Motion Design 场景添加额外的准备逻辑
    }

    virtual bool IsReady_Implementation() override
    {
        // 先调用基类的就绪检查（会检查 Actor）
        if (!Super::IsReady_Implementation())
        {
            return false;
        }
        // 添加自定义的“就绪”条件，例如等待某个特定数据流加载完成
        return IsMyCustomDataReady();
    }

private:
    bool IsMyCustomDataReady() const { /* ... */ return true; }
};
```

### 进阶用法

`AScreenshotFunctionalTestAvalanche` 的核心价值在于其内部逻辑，解决了以下两个关键问题，确保测试在 Motion Design 场景下可靠工作：

1.  **CVar 优先级覆盖**：它使用 `ECVF_SetByConsole` 优先级强制设置渲染 CVar（如抗锯齿、动态模糊），覆盖了 `AvaGameViewportClient` 在更高优先级设置的值。
2.  **PIE 截图代理兼容**：它同时注册了实例级 (`UGameViewportClient::OnScreenshotCaptured`) 和静态级 (`FScreenshotRequest::OnScreenshotCaptured`) 的截图完成代理，确保在 PIE 和独立运行模式下都能正确接收截图完成通知。

在自定义测试中，你可能需要理解其 `PrepareTest` 和 `RequestScreenshot` 中的处理逻辑，以确保你的自定义逻辑不会干扰这些关键修复。

## Demo 示例

以下是一个完整的、基于 `AScreenshotFunctionalTestAvalanche` 的最小化功能测试类定义，展示了如何针对 Motion Design 场景配置一个可靠的截图测试。

**MyMotionDesignScreenshotTest.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "ScreenshotFunctionalTestAvalanche.h"
#include "MyMotionDesignScreenshotTest.generated.h"

/**
 * 自定义的 Motion Design 截图测试，用于验证包含复杂粒子特效的场景。
 * 它继承了父类对 CVar 优先级和 PIE 代理的修复。
 */
UCLASS(Blueprintable, DisplayName = "My Custom Motion Design Test")
class AMyMotionDesignScreenshotTest : public AScreenshotFunctionalTestAvalanche
{
	GENERATED_BODY()

public:
	// 默认配置：等待主角（如一个复杂的粒子发射器）就绪
	AMyMotionDesignScreenshotTest()
	{
		bWaitForActorReady = true;
		MaxActorWaitTime = 8.0f;
	}

	// 可选：在测试开始前进行额外设置
	virtual void PrepareTest() override
	{
		Super::PrepareTest();
		// 禁用一些不必要的性能监控工具以获得更稳定的帧率
	}
};
```

**MyMotionDesignScreenshotTest.cpp**
```cpp
#include "MyMotionDesignScreenshotTest.h"

// 实现使用默认的父类行为，无需额外编写 .cpp 代码
// 所有关键逻辑（CVar覆盖、PIE代理、Actor就绪等待）均已由 AScreenshotFunctionalTestAvalanche 处理。
```

## 模块依赖

该插件的描述列出了大量依赖，表明它是一个高度集成的“超级插件”。要在你自己的模块中使用 Motion Design 的特定功能，你需要根据所使用的子功能添加对应的模块依赖。

| 模块 | 用途 |
|---|---|
| `Geometry Scripting` | 用于程序化几何体操作和生成 |
| `Remote Control` | 用于外部应用程序（如自定义UI或设备）远程控制引擎参数 |
| `Text3D` | 用于生成和操控 3D 文字 |
| `SVG Importer` | 用于导入 SVG 矢量图形文件 |
| `Dynamic Material` | 动态材质创建与编辑工具 |
| `Media IO Framework` | 处理媒体输入输出的核心框架 |
| `Media Compositing` | 提供视频合成与图层混合功能 |
| `AvalanchePropertyAnimator` | 依赖 `Sequencer` 模块，用于将属性动画化并集成到序列器中 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 的编辑器选项卡（场景设置、大纲视图）移动到独立的选项卡组，优化编辑器布局。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在使用播出清单页面设置时，增加了对 Movie Render Queue 的数据统计功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在播出控制工具栏中添加了页面加载选项（全部、下一个、已选），并增强了相关功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 增加了项目设置，可强制禁用 Text3D 和形状体的碰撞，简化流程并提高性能。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构了视口客户端关联逻辑，通过通知机制减少冗余代码。 |

### 维护评价

**活跃维护**。Motion Design 插件从实验阶段迁移至正式版虚拟制作目录，表明 Epic Games 对其有明确的长期规划。近期的 Git 提交记录显示，该插件在功能上仍处于**积极开发阶段**，频繁添加新特性（如 MRQ 分析、播出控制增强）和优化现有工作流（如编辑器布局调整）。创建时间虽不足两年，但已成为虚拟制作管线的关键组件。**推荐使用**，尤其对于从事虚拟制作、广播和实时视觉设计的团队。需要注意其庞大的依赖关系和模块数量。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/motion-design-in-unreal-engine/) (虚幻引擎官方文档库)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest) (包含本文档分析的核心测试类)