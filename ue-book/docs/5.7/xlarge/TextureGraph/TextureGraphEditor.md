# Texture Graph

> Texture creation tool using graphs.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、纹理图资产） |
| 模块 | `TextureGraph` (Runtime), `TextureGraphEditor` (Runtime), `TextureGraphEngine` (Runtime), `TextureGraphInsight` (Runtime), `TextureGraphInsightEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-12-20 |
| 年龄标签 | 🆕（约 1.5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph) | |

## 用途

TextureGraph 是一个基于节点的程序化纹理生成系统。它允许用户通过连接各种功能节点（如数学运算、噪声生成、图像处理等）来创建复杂的纹理，类似于材质编辑器，但专注于纹理的生成而非材质属性。该插件提供了一个完整的编辑器环境，支持实时预览、参数调整和纹理导出，旨在为美术和技术美术提供一种高效、灵活且可复用的纹理创作工作流。

## 使用场景

- 你需要为游戏或项目程序化生成大量变体纹理（如地形、岩石、木头、金属表面）。
- 你希望创建一个可参数化、可复用的纹理生成模板，以便快速调整风格或生成系列纹理。
- 你需要一个可视化的工具来组合各种图像处理算法和数学函数，以探索和创造独特的纹理效果。
- 你希望将复杂的纹理生成逻辑封装成资产，并在不同项目或团队成员间共享。

## 蓝图用法

TextureGraph 主要通过其资产类型（`UTextureGraph` 和 `UTextureGraphInstance`）在编辑器中使用。蓝图可直接交互的公开接口较少，主要集中在参数暴露和实例化上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Parameters` (属性) | 获取纹理图实例的可编辑参数列表。 | `UTG_Parameters` |

### 使用示例（蓝图描述）

1.  **创建纹理图资产**：在内容浏览器中右键，选择 `Texture Graph` -> `Texture Graph` 创建一个基础纹理图资产。
2.  **创建实例**：基于基础纹理图创建 `Texture Graph Instance` 资产。实例继承基础图的结构，但允许覆盖参数值。
3.  **在蓝图中访问参数**：在蓝图中持有对 `Texture Graph Instance` 的引用，通过其 `Parameters` 属性（类型为 `UTG_Parameters`）可以访问和修改 `TArray<FTG_ParameterInfo>` 中的参数值，从而动态控制纹理生成。

## C++ 用法

TextureGraph 的 C++ 用法主要集中在编辑器扩展和引擎集成层面，普通游戏逻辑中较少直接使用。

### 头文件引入

```cpp
#include "TextureGraphEditorModule.h"
#include "EdGraph/TG_EdGraph.h"
#include "EdGraph/TG_EdGraphNode.h"
```

### 基本用法

以下代码展示了如何在编辑器工具中初始化一个纹理图的编辑器图形表示。

```cpp
// 假设你有一个 UTextureGraph* TextureGraphAsset
// 以及一个指向编辑器实例的 TWeakPtr<FTG_Editor> EditorPtr

// 创建并初始化编辑器图形
UTG_EdGraph* EdGraph = NewObject<UTG_EdGraph>();
EdGraph->InitializeFromTextureGraph(TextureGraphAsset, EditorPtr);

// 之后，EdGraph 将包含与 TextureGraphAsset 中节点对应的 UTG_EdGraphNode
```

### 进阶用法

通过 `UTG_EdGraph` 和 `UTG_EdGraphNode` 可以监听图形变化和节点求值事件，用于实现自定义的预览或同步逻辑。

```cpp
// 绑定节点求值后的回调，用于更新自定义预览
UTG_EdGraphNode* SomeNode = ...;
SomeNode->OnNodePostEvaluateDelegate.AddLambda([](const FTG_EvaluationContext* Context) {
    // 节点求值完成，可以在此获取结果并更新UI或预览
    // Context 中包含求值上下文信息
});

// 绑定图形变化回调
EdGraph->OnGraphChanged.AddLambda([](UTG_Graph* InGraph, UTG_Node* InNode, bool bTweaking) {
    // 图形结构或参数发生变化
});
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在编辑器模块中创建一个纹理图编辑器。

**MyTextureGraphTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "ITG_Editor.h"

class UTextureGraph;

UCLASS()
class UMyTextureGraphTool : public UObject
{
    GENERATED_BODY()

public:
    void OpenEditorForTextureGraph(UTextureGraph* TextureGraphToEdit);

private:
    TSharedPtr<ITG_Editor> ActiveEditor;
};
```

**MyTextureGraphTool.cpp**
```cpp
#include "MyTextureGraphTool.h"
#include "TextureGraphEditorModule.h"

void UMyTextureGraphTool::OpenEditorForTextureGraph(UTextureGraph* TextureGraphToEdit)
{
    if (!TextureGraphToEdit) return;

    // 通过编辑器模块创建纹理图编辑器实例
    FTextureGraphEditorModule& EditorModule = FModuleManager::LoadModuleChecked<FTextureGraphEditorModule>("TextureGraphEditor");
    ActiveEditor = EditorModule.CreateTextureGraphEditor(
        EToolkitMode::Standalone, // 或 EToolkitMode::WorldCentric
        nullptr, // ToolkitHost
        TextureGraphToEdit
    );
}
```

## 模块依赖

要使用 TextureGraph 插件的功能，你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `TextureGraph` | 核心运行时数据结构和资产类型。 |
| `TextureGraphEngine` | 纹理图的求值引擎和计算后端。 |
| `TextureGraphEditor` | 编辑器UI、图形编辑器和资产操作。 |

## 维护状态

### 近期更新

```
- bea1a69af8a7 修复了 TextureGraph Instance 在更改父图时跳过失效的问题。
- 563b73821a65 修复了 TG Export 的崩溃问题。
- 6f23619b61a2 重构了资产引用过滤逻辑，使其在拖放到图形、节点和引脚时都能正确工作，并提供了更相关的工具提示。
```

### 维护评价

TextureGraph 是一个相对较新的插件（创建于2023年底），目前仍在积极维护中。从近期提交记录看，开发团队正在修复关键bug（如崩溃、失效逻辑错误）并改进编辑器用户体验（如拖放过滤）。该插件功能完整，提供了从核心引擎到编辑器工具的全套解决方案。虽然标记为“Beta”版本，但已具备生产可用性。推荐需要程序化纹理生成工作流的项目评估和使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph)
- [官方文档]()（暂无）
- [测试用例]()（暂未在插件目录内发现标准测试文件）