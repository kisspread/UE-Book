# nDisplay Modular Features

> Modular Features for nDisplay

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay 模块化功能 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、C++ 模块） |
| 模块 | `DisplayClusterLightCardExtender` (Runtime), `DisplayClusterModularFeaturesEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-05 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplayModularFeatures) | |

## 用途

此插件为 nDisplay 的虚拟制作（尤其是 ICVFX/LED 面板）提供了一个**可扩展的框架**。它解决了为 ICVFX 面板添加新类型卡片（如灯光卡片）或新功能时，需要修改核心 nDisplay 代码的问题。通过定义一系列“模块化功能”接口，允许其他插件在不修改 nDisplay 核心代码的情况下，注册自定义的卡片类型、UI 元素和逻辑，实现了功能的即插即用。

## 使用场景

- **电影虚拟制片 (VP)**：在 LED 面板项目中，你使用 nDisplay 进行实时渲染，并需要在 ICVFX 面板中管理各种视觉元素（如灯光卡、颜色校正卡）。
- **扩展 ICVFX 功能**：你需要为 ICVFX 面板添加一个全新的、自定义类型的卡片（例如，一个带有特殊动态效果的灯光源），但不想 fork 或修改引擎的 nDisplay 插件。
- **团队协作开发**：多个团队或第三方需要为同一个 nDisplay 虚拟制片流水线贡献不同的功能模块，此插件提供了清晰的扩展边界。

## 蓝图用法

此插件主要提供**框架和接口**，供其他模块（插件）实现。最终用户通常不会直接在蓝图中调用其节点，而是使用由其他插件（例如，您自己基于此框架开发的插件）暴露的更高级节点。核心的扩展点通过 C++ 接口暴露。

## C++ 用法

### 头文件引入

```cpp
// 若要实现新的灯光卡片类型
#include "DisplayClusterLightCardExtender.h"
```

### 基本用法

此插件的价值在于提供扩展点，而非提供具体功能。基本用法是**实现并注册自定义功能**。

1.  **创建自定义灯光卡片类**：继承自 `UDisplayClusterLightCardActor` 或相关基类，并实现自定义逻辑。
2.  **注册模块化功能**：在你的插件模块启动时，通过 `IDisplayClusterLightCardExtender` 接口注册你的自定义卡片类型。

```cpp
// 示例：在您自己插件的模块启动函数中
#include "DisplayClusterLightCardExtender.h"
#include "MyCustomLightCard.h" // 您的自定义灯光卡片类

void FMyPluginModule::StartupModule()
{
    if (IDisplayClusterLightCardExtender* LightCardExtender = FModuleManager::GetModulePtr<IDisplayClusterLightCardExtender>(TEXT("DisplayClusterLightCardExtender")))
    {
        // 注册您的自定义灯光卡片类型
        LightCardExtender->RegisterLightCardClass(UMyCustomLightCard::StaticClass(), TEXT("My Custom Card"));
    }
}
```

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `DisplayClusterLightCardExtender` | Runtime | **核心扩展模块**。定义并实现了为 nDisplay ICVFX 面板扩展灯光卡片等功能的基础接口和架构。 |
| `DisplayClusterModularFeaturesEditor` | Editor | **编辑器支持模块**。提供与编辑器UI集成相关的功能，例如自定义资产的图标、细节面板自定义等。 |

## Demo 示例

此插件本身是一个框架，无直接可运行的独立 Demo。其用法体现在你**基于它创建的插件**中。一个最小的扩展插件可能包含：
- 一个新的 `UCLASS` 继承自 `UDisplayClusterLightCardActor`。
- 在该类的构造函数或自定义函数中实现您需要的逻辑。
- 在插件的 `.uplugin` 中声明依赖 `DisplayClusterLightCardExtender`。
- 在插件的模块 `StartupModule` 中注册您的新类。

## 模块依赖

要使用此插件的扩展功能（即开发依赖此框架的插件），你的模块需要依赖以下**独特**模块：

| 模块 | 用途 |
|---|---|
| `DisplayClusterLightCardExtender` | 提供灯光卡片扩展的核心接口和类型。 |
| `DisplayCluster` | nDisplay 的核心运行时模块，是所有功能的基础。 |
| `ICVFXRuntime` | 电影虚拟制作（ICVFX）的运行时模块，提供面板、相机等核心概念。 |
| `ICVFXEditor` | (编辑器模块) 电影虚拟制作（ICVFX）的编辑器模块，提供UI和工具。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-26 | `3336c461` | [nDisplay] In-Camera VFX panel makes level dirty | 修复 ICVFX 面板操作会导致关卡被误标记为“已修改”的问题。 |
| 2024-08-01 | `1dd0608a` | nDisplay: Propagate RadialOffset changes from LC level instance to ICVFX panel proxy. | 修复灯光卡片的径向偏移属性变更无法正确同步到ICVFX面板代理的问题。 |
| 2024-05-15 | `8b89d9f4` | [nDisplay] Media tiles configuration dialog for ICVFX cameras | 为ICVFX相机新增媒体瓦片配置对话框，功能增强。 |
| 2024-03-13 | `6491e949` | [nDisplay] Media configuration improvements | 对媒体配置进行了一系列改进和优化。 |
| 2024-03-06 | `59d5a057` | [nDisplay] Fixed CIS validation issue where DisplayClusterModularFeaturesEditor artifacts have paths | 修复了模块化功能编辑器插件在持续集成验证中的路径问题。 |

### 维护评价

此插件处于**活跃维护**状态。
- **创建时间**：2022年9月，历史约3年，是相对较新的架构组件。
- **更新频率**：直至2025年9月仍有功能性提交（如修复脏标记、新增媒体配置对话框），表明它在持续配合nDisplay/ICVFX框架进行迭代。
- **维护状态**：作为nDisplay虚拟制片流水线的关键扩展点，由Epic Games官方维护，可靠性高。
- **推荐使用**：如果你的项目需要深度定制nDisplay的ICVFX面板功能，尤其是开发可复用的灯光卡片或视觉元素插件，**强烈推荐**使用此框架，而不是直接修改引擎代码。它能保证更好的升级兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplayModularFeatures)
- [官方文档](https://docs.unrealengine.com) (nDisplay 相关文档)
- [测试用例] 无公开测试用例。