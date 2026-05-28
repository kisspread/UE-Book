# Material Designer Media Stream Bridge

> Integrates the Media Stream plugin with the Material Designer.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 材质设计器媒体流桥 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器扩展） |
| 模块 | `DynamicMaterialMediaStreamBridge` (Runtime), `DynamicMaterialMediaStreamBridgeEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DynamicMaterialMediaStreamBridge) | |

## 用途

该插件是一个“桥接”插件，其唯一目的是在 **DynamicMaterial**（材质设计器）插件和 **MediaStream** 插件之间建立连接。它使得材质设计器能够理解和操作媒体流（Media Stream）资产，从而实现在材质设计师中直接使用实时视频、音频或其他媒体流作为材质参数（如纹理）的功能。这解决了两个独立插件之间的数据互通问题，避免了用户手动进行复杂的集成工作。

## 使用场景

- 你正在使用 **Dynamic Material** 插件进行材质的程序化或可视化设计，并且需要将实时视频输入（如摄像头、网络流）或视频文件作为动态纹理应用于材质。
- 你希望在材质设计器的蓝图或节点中，直接引用并控制 **Media Stream** 插件管理的媒体源，而无需通过底层代码手动绑定。

## 蓝图用法

此插件的核心功能是作为编辑器内的集成桥，其提供的用户界面扩展主要体现在**材质设计器**和**媒体流源**的右键菜单中。

### 核心节点

该插件主要扩展了材质设计器的上下文菜单，提供了以下功能入口：

| 节点 | 说明 | 所在类 |
|---|---|---|
| （上下文菜单项）`Change Source to Media Stream` | 在材质设计器中，将当前材质值的源更改为媒体流。 | `FDMMediaStreamStageSourceMenuExtender` |
| （上下文菜单项）`Add Media Stream Layer` | 在材质设计器中，添加一个使用媒体流作为纹理的图层。 | `FDMMediaStreamStageSourceMenuExtender` |

### 使用示例（蓝图描述）

1.  在材质设计器的图表中，右键点击一个材质值节点。
2.  在弹出的菜单中，会新增一个 **Media Stream** 相关的分类。
3.  在该分类下，你可以选择 **Change Source to Media Stream** 来将此值与一个媒体流资产关联，或者选择 **Add Media Stream Layer** 来快速创建一个使用媒体流的新图层。
4.  随后，你可以在材质设计器的属性面板中，对媒体流的播放、纹理、缓存等属性进行精细控制。

## C++ 用法

此插件主要为编辑器提供扩展，其运行时模块提供了基础类型定义，而编辑器模块实现了具体的集成逻辑。

### 头文件引入

```cpp
// 如果需要引用编辑器扩展的类
#include "DMMaterialValueMediaStreamPropertyRowGenerator.h"
```

### 基本用法

该插件的核心功能通过编辑器模块的 `StartupModule` 函数进行注册，开发者通常不直接调用其 API。其效果体现在 UI 扩展上。以下是其模块启动的示意：

```cpp
// 来源: DynamicMaterialMediaStreamBridgeEditorModule.cpp (推断)
void FDynamicMaterialMediaStreamBridgeEditorModule::StartupModule()
{
    // 在此处，插件会初始化并注册其提供的编辑器扩展。
    // 例如：注册材质设计器的属性行生成器、扩展上下文菜单等。
    // 这使得媒体流相关的属性和操作能在材质设计器UI中正确显示。
}
```

### 进阶用法

如果你正在开发自定义的材质设计器扩展，可能需要与本插件注册的组件交互。例如，本插件提供的 `FDMMaterialValueMediaStreamPropertyRowGenerator` 负责为媒体流类型的材质值生成属性面板。

```cpp
// 来源: DMMaterialValueMediaStreamPropertyRowGenerator.h (推断)
// 该类负责为使用了MediaStream的材质值，在细节面板中生成对应的属性行（如播放控制、源设置等）。
class FDMMaterialValueMediaStreamPropertyRowGenerator : public FDMComponentPropertyRowGenerator
{
public:
    // 通过单例获取此生成器实例
    static const TSharedRef<FDMMaterialValueMediaStreamPropertyRowGenerator>& Get();

    // 向属性面板添加组件属性
    virtual void AddComponentProperties(FDMComponentPropertyRowGeneratorParams& InParams) override;

    // 以下为具体的属性类别添加方法，供 AddComponentProperties 内部调用
    // void AddControlCategory(FDMComponentPropertyRowGeneratorParams& InParams);
    // void AddSourceCategory(FDMComponentPropertyRowGeneratorParams& InParams);
    // ... 等等
};
```

## Demo 示例

以下示例展示了如何在你的编辑器模块中，**依赖** 并使用本插件提供的编辑器扩展（主要是菜单扩展）。你需要确保你的 `.Build.cs` 文件正确设置了依赖。

```cpp
// MyEditorModule.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyEditorModule.cpp
#include "MyEditorModule.h"
#include "DMMediaStreamStageSourceMenuExtender.h" // 引用本插件提供的扩展头文件

void FMyEditorModule::StartupModule()
{
    // 在此处，你可以选择性地集成或观察本插件提供的扩展。
    // 例如，获取其单例来检查其状态，或与其协作。
    // 注意：直接交互通常不是必须的，因为它的UI扩展会自动生效。
    FDMMediaStreamStageSourceMenuExtender& Extender = FDMMediaStreamStageSourceMenuExtender::Get();
    // Extender.Integrate(); // 通常插件启动时已自动调用，此处仅为演示
}

void FMyEditorModule::ShutdownModule()
{
    // 清理工作
}

IMPLEMENT_MODULE(FMyEditorModule, MyEditorModule)
```

## 模块依赖

要使用此插件的功能，你的模块需要在 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `DynamicMaterial` | 依赖材质设计器的核心模块。 |
| `MediaStream` | 依赖媒体流插件的核心模块。 |
| `DynamicMaterialMediaStreamBridge` | 依赖此插件提供的运行时类型。 |
| `DMUtilities` | 材质设计器插件的公共工具模块，可能被此插件间接使用。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `82b74724` | [MediaStream] Adding a cache setting override (like MediaPlate does) for using a local cache when us | 为媒体流添加本地缓存设置覆盖功能。 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构JSON对象以支持两种字符串类型。 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 优化内存，移除JSON对象中的字符串重复。 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回退了之前的某个提交。 |
| 2026-02-25 | `af0dfacf` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 优化内存，移除JSON对象中的字符串重复。 |

### 维护评价

此插件创建于 2025 年初，属于较新的实验性插件。从近期更新记录看，它在 2026 年仍有活跃的功能性更新（如添加缓存设置）和优化工作，表明 Epic 内部可能在持续使用和改进它。作为 `DynamicMaterial` 和 `MediaStream` 两个重要插件之间的桥梁，它虽然小众，但对于有特定集成需求的用户来说是关键组件。

**评价：** 🆕 **实验性但活跃维护中**。目前没有废弃迹象，且仍在演进。推荐有相关集成需求的开发者关注并试用，但需注意其“实验性”标签意味着API可能在未来发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DynamicMaterialMediaStreamBridge)
- [官方文档]()（无）
- [测试用例]()（未在插件目录内发现独立测试）