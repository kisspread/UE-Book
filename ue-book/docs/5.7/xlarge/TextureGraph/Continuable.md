# Texture Graph

> Texture creation tool using graphs.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `TextureGraph` (Runtime), `TextureGraphEditor` (Runtime), `TextureGraphEngine` (Runtime), `TextureGraphInsight` (Runtime), `TextureGraphInsightEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-12-20 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph) | |

## 用途

TextureGraph 是一个深度集成于 Unreal Engine 5 的**程序化纹理生成系统**。它提供了一个基于节点的可视化编辑器（类似于材质编辑器或蓝图），允许美术师和开发者通过连接各种数学运算、噪声生成、图像处理等节点，来程序化地创建复杂的纹理、材质函数和数据资产。

它解决的核心问题是：**在引擎内部提供一个强大、灵活且可扩展的程序化纹理创作环境**，从而减少对外部工具（如 Substance Designer）的依赖，并允许纹理生成逻辑与游戏逻辑（蓝图、C++）进行深度集成和动态交互。

## 使用场景

-   **程序化地形材质**：创建随地形高度、坡度、生物群系动态变化的复杂地表纹理。
-   **动态角色外观**：根据游戏状态（如生命值、装备、技能）实时生成或修改角色皮肤、盔甲纹理。
-   **UI 与 HUD 元素**：生成动态的、数据驱动的 UI 背景、进度条、技能图标等。
-   **技术美术工具链**：构建可复用的纹理生成图库，用于快速原型设计或批量生产。
-   **数据可视化**：将游戏数据（如热力图、高度图）转换为可视化的纹理。

## 蓝图用法

TextureGraph 提供了丰富的蓝图 API，用于在运行时创建、修改和查询纹理图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Texture Graph` | 创建一个新的纹理图实例。 | `UTextureGraphBlueprintLibrary` |
| `Add Node` | 向纹理图中添加一个指定类型的节点。 | `UTextureGraphBlueprintLibrary` |
| `Connect Nodes` | 连接两个节点的输入输出引脚。 | `UTextureGraphBlueprintLibrary` |
| `Set Node Parameter` | 设置节点的特定参数值（如常量、纹理资产）。 | `UTextureGraphBlueprintLibrary` |
| `Execute Graph` | 执行纹理图，生成最终的纹理输出。 | `UTextureGraphBlueprintLibrary` |
| `Get Output Texture` | 获取纹理图执行后生成的 `UTexture2D` 资产。 | `UTextureGraphBlueprintLibrary` |
| `Find Node By Name` | 在图中按名称查找节点。 | `UTextureGraphBlueprintLibrary` |
| `Save Graph To Asset` | 将当前纹理图保存为 `.uasset` 文件。 | `UTextureGraphBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **创建并执行一个简单图**：
    *   使用 `Create Texture Graph` 节点创建一个新图。
    *   使用 `Add Node` 节点添加一个 `Constant` 节点（输出纯色）和一个 `Output` 节点。
    *   使用 `Connect Nodes` 节点将 `Constant` 的输出连接到 `Output` 的输入。
    *   调用 `Execute Graph` 节点执行图。
    *   调用 `Get Output Texture` 节点获取生成的纹理，并将其应用到一个动态材质实例上。

2.  **动态修改纹理**：
    *   在游戏逻辑中，通过 `Find Node By Name` 找到图中的 `Constant` 节点。
    *   使用 `Set Node Parameter` 节点，根据游戏变量（如玩家分数）动态改变其颜色值。
    *   重新调用 `Execute Graph`，纹理将实时更新。

## C++ 用法

### 头文件引入

```cpp
#include "TextureGraphEngine.h"
#include "TextureGraph.h"
#include "TextureGraphBlueprintLibrary.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个简单的纹理图并执行。
（来源：`Engine/Plugins/TextureGraph/Source/TextureGraphEngine/Tests/` 目录下的测试用例）

```cpp
// 创建一个纹理图实例
UTextureGraph* MyGraph = NewObject<UTextureGraph>();

// 添加一个常量节点
UTextureGraphNode* ConstantNode = MyGraph->AddNode(FName("Constant"));
// 设置其颜色为红色
ConstantNode->SetParameter(FName("Value"), FLinearColor::Red);

// 添加一个输出节点
UTextureGraphNode* OutputNode = MyGraph->AddNode(FName("Output"));

// 连接节点：常量 -> 输出
MyGraph->ConnectNodes(ConstantNode, FName("Value"), OutputNode, FName("Input"));

// 执行图
FTextureGraphRenderResult Result = MyGraph->Execute();

// 获取输出纹理
UTexture2D* GeneratedTexture = Result.GetTexture();
```

### 进阶用法

创建一个自定义的纹理生成器类，封装复杂的图逻辑。
（来源：结合 `TextureGraphEngine` 模块的架构设计）

```cpp
// MyProceduralTextureGenerator.h
#pragma once
#include "TextureGraph.h"
#include "MyProceduralTextureGenerator.generated.h"

UCLASS(BlueprintType)
class UMyProceduralTextureGenerator : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    UTextureGraph* TextureGraph;

    UPROPERTY(BlueprintReadOnly)
    UTexture2D* GeneratedTexture;

    UFUNCTION(BlueprintCallable)
    void GenerateTexture(float NoiseScale, FLinearColor BaseColor);

private:
    void BuildGraph(float NoiseScale, FLinearColor BaseColor);
};

// MyProceduralTextureGenerator.cpp
#include "MyProceduralTextureGenerator.h"
#include "TextureGraphBlueprintLibrary.h"

void UMyProceduralTextureGenerator::BuildGraph(float NoiseScale, FLinearColor BaseColor)
{
    if (!TextureGraph)
    {
        TextureGraph = NewObject<UTextureGraph>();
    }
    TextureGraph->ClearGraph();

    // 构建一个更复杂的图：噪声 + 颜色混合
    UTextureGraphNode* NoiseNode = TextureGraph->AddNode(FName("Noise"));
    NoiseNode->SetParameter(FName("Scale"), NoiseScale);

    UTextureGraphNode* ColorNode = TextureGraph->AddNode(FName("Constant"));
    ColorNode->SetParameter(FName("Value"), BaseColor);

    UTextureGraphNode* MixNode = TextureGraph->AddNode(FName("Mix"));
    TextureGraph->ConnectNodes(NoiseNode, FName("Value"), MixNode, FName("A"));
    TextureGraph->ConnectNodes(ColorNode, FName("Value"), MixNode, FName("B"));

    UTextureGraphNode* OutputNode = TextureGraph->AddNode(FName("Output"));
    TextureGraph->ConnectNodes(MixNode, FName("Result"), OutputNode, FName("Input"));
}

void UMyProceduralTextureGenerator::GenerateTexture(float NoiseScale, FLinearColor BaseColor)
{
    BuildGraph(NoiseScale, BaseColor);
    FTextureGraphRenderResult Result = TextureGraph->Execute();
    GeneratedTexture = Result.GetTexture();
}
```

## Demo 示例

一个最小的、可运行的纹理图生成器。
（文件：`MyMinimalTextureGenerator.h` 和 `MyMinimalTextureGenerator.cpp`）

```cpp
// MyMinimalTextureGenerator.h
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "TextureGraph.h"
#include "MyMinimalTextureGenerator.generated.h"

UCLASS(BlueprintType)
class UMyMinimalTextureGenerator : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "TextureGraph Demo")
    UTexture2D* GenerateCheckerboard(int32 GridSize, FLinearColor ColorA, FLinearColor ColorB);
};

// MyMinimalTextureGenerator.cpp
#include "MyMinimalTextureGenerator.h"
#include "TextureGraphBlueprintLibrary.h"

UTexture2D* UMyMinimalTextureGenerator::GenerateCheckerboard(int32 GridSize, FLinearColor ColorA, FLinearColor ColorB)
{
    UTextureGraph* Graph = NewObject<UTextureGraph>();

    // 1. 创建棋盘格节点
    UTextureGraphNode* CheckerNode = Graph->AddNode(FName("Checker"));
    CheckerNode->SetParameter(FName("GridSize"), GridSize);

    // 2. 创建两个颜色常量
    UTextureGraphNode* ColorANode = Graph->AddNode(FName("Constant"));
    ColorANode->SetParameter(FName("Value"), ColorA);
    UTextureGraphNode* ColorBNode = Graph->AddNode(FName("Constant"));
    ColorBNode->SetParameter(FName("Value"), ColorB);

    // 3. 使用棋盘格作为遮罩混合颜色
    UTextureGraphNode* MixNode = Graph->AddNode(FName("Mix"));
    Graph->ConnectNodes(CheckerNode, FName("Value"), MixNode, FName("Alpha"));
    Graph->ConnectNodes(ColorANode, FName("Value"), MixNode, FName("A"));
    Graph->ConnectNodes(ColorBNode, FName("Value"), MixNode, FName("B"));

    // 4. 连接到输出
    UTextureGraphNode* OutputNode = Graph->AddNode(FName("Output"));
    Graph->ConnectNodes(MixNode, FName("Result"), OutputNode, FName("Input"));

    // 5. 执行并返回
    FTextureGraphRenderResult Result = Graph->Execute();
    return Result.GetTexture();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RenderCore` | 底层渲染核心功能，用于纹理创建和 GPU 操作。 |
| `RHI` | 渲染硬件接口，用于跨平台的 GPU 计算。 |
| `Projects` | 项目和插件管理。 |
| `ImageWriteQueue` | 用于将生成的纹理异步写入磁盘。 |
| `Json` | 用于序列化/反序列化纹理图数据。 |
| `AssetRegistry` | 用于管理和查找纹理图资产。 |

## 维护状态

### 近期更新

```
- 2024-05-17 731c336e7fff Moving texture graph to normal Engine/Plugins directory as part of the effort to reach Beta for 5.6
```

### 维护评价

-   **创建时间**：约 2 年前（2023年底），是一个相对较新的插件。
-   **近期更新**：最近一次提交（2024年5月）是将插件从 `Experimental` 目录移动到正式的 `Engine/Plugins` 目录，这是为 UE 5.6 版本达到 Beta 状态所做的准备工作。这表明 Epic 正在积极将其推向稳定版本。
-   **活跃状态**：**积极维护中**。作为 Epic 官方推进的 Beta 功能，预计会有持续的更新和 bug 修复。
-   **已知限制**：作为 Beta 版本，可能存在 API 不稳定、性能问题或功能缺失。文档和示例可能不完善。
-   **推荐使用**：**推荐用于新项目和原型开发**。它代表了 UE 内置程序化纹理工具的未来方向。对于生产环境，建议密切关注其 Beta 进度和稳定性报告。由于其深度集成和蓝图支持，非常适合需要动态、数据驱动纹理的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph/Source/TextureGraphEngine/Tests)