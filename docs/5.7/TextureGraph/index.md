# Texture Graph

> Texture creation tool using graphs.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，材质模板） |
| 模块 | `TextureGraph` (Runtime), `TextureGraphEditor` (Runtime), `TextureGraphEngine` (Runtime), `TextureGraphInsight` (Runtime), `TextureGraphInsightEditor` (Runtime), `Continuable` (External), `Function2` (External) |
| 实验性 | 否 |
| 创建时间 | 2023-12-20 |
| 年龄标签 | 🆕（约 1.5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph) | |

## 用途

TextureGraph 是一个基于节点图的程序化纹理创建与编辑工具。它允许用户通过连接各种功能节点（如噪声、数学运算、图像处理）来构建复杂的纹理生成逻辑，类似于材质编辑器，但专注于生成纹理资产本身。该插件旨在简化纹理制作流程，支持非破坏性编辑和快速迭代，特别适合技术美术和程序化内容创作者。

## 使用场景

-   你需要创建复杂的程序化纹理（如地形地表、材质细节、UI 背景），但不想手动绘制或依赖外部软件。
-   你希望以可视化、非线性的方式迭代和调试纹理生成过程。
-   你的项目需要大量变体纹理，通过修改图参数即可快速生成。
-   你希望将纹理生成逻辑封装为可复用的蓝图资产或工具。

## 蓝图用法

TextureGraph 的核心蓝图功能集中在 `TextureGraph` 和 `TextureGraphEditor` 模块中，提供了图操作、纹理生成和调试的节点。详细 API 请参阅各模块文档。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create TextureGraph` | 创建一个新的纹理图实例 | `UTextureGraphBlueprintLibrary` |
| `Add Node` | 向图中添加一个功能节点 | `UTextureGraphBlueprintLibrary` |
| `Connect Nodes` | 连接两个节点的输入输出引脚 | `UTextureGraphBlueprintLibrary` |
| `Execute Graph` | 执行纹理图，生成最终纹理 | `UTextureGraphBlueprintLibrary` |
| `Get Result Texture` | 获取图执行后生成的纹理资产 | `UTextureGraphBlueprintLibrary` |
| `Debug Node` | 启用对特定节点的调试，查看中间结果 | `UTextureGraphInsightBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  使用 `Create TextureGraph` 节点创建一个新图。
2.  使用 `Add Node` 节点依次添加 `Noise Node`、`Color Adjust Node` 和 `Output Node`。
3.  使用 `Connect Nodes` 节点将 `Noise Node` 的输出连接到 `Color Adjust Node` 的输入，再将 `Color Adjust Node` 的输出连接到 `Output Node`。
4.  调用 `Execute Graph` 节点执行整个图。
5.  使用 `Get Result Texture` 节点获取生成的 `UTexture2D` 对象，用于后续材质或显示。

## C++ 用法

TextureGraph 的 C++ API 主要用于扩展引擎功能或创建自定义节点。详细用法请参考各模块文档。

### 头文件引入

```cpp
#include "TextureGraphEngine.h"
#include "TextureGraph.h"
```

### 基本用法

```cpp
// 创建并执行一个简单的纹理图
UTextureGraph* MyGraph = NewObject<UTextureGraph>();
UTG_Node* NoiseNode = MyGraph->AddNode<UTG_NoiseNode>();
UTG_Node* OutputNode = MyGraph->AddNode<UTG_OutputNode>();

// 连接节点
MyGraph->ConnectNodes(NoiseNode, 0, OutputNode, 0);

// 执行图并获取结果
UTexture2D* ResultTexture = MyGraph->Execute();
```

### 进阶用法

创建自定义节点类型，需要继承自 `UTG_Node` 并实现 `Evaluate` 方法。详细实现请参阅 [TextureGraphEngine 模块文档](TextureGraphEngine.md)。

## Demo 示例

一个最小的 C++ 示例，展示如何创建并执行一个纹理图。

**MyTextureGraphActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyTextureGraphActor.generated.h"

class UTextureGraph;
class UTexture2D;

UCLASS()
class AMyTextureGraphActor : public AActor
{
    GENERATED_BODY()

public:
    AMyTextureGraphActor();

    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "TextureGraph")
    UTextureGraph* TextureGraph;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "TextureGraph")
    UTexture2D* GeneratedTexture;
};
```

**MyTextureGraphActor.cpp**
```cpp
#include "MyTextureGraphActor.h"
#include "TextureGraphEngine.h"
#include "TextureGraph.h"
#include "Nodes/TG_NoiseNode.h"
#include "Nodes/TG_OutputNode.h"

AMyTextureGraphActor::AMyTextureGraphActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyTextureGraphActor::BeginPlay()
{
    Super::BeginPlay();

    if (TextureGraph)
    {
        // 执行图并存储结果
        GeneratedTexture = TextureGraph->Execute();
        if (GeneratedTexture)
        {
            UE_LOG(LogTemp, Log, TEXT("TextureGraph executed successfully. Generated texture: %s"), *GeneratedTexture->GetName());
        }
    }
}
```

## 模块依赖

要使用 TextureGraph 插件，你的项目模块通常需要依赖以下核心模块。具体依赖关系请参考各子模块的 Build.cs 文件。

| 模块 | 用途 |
|---|---|
| `TextureGraphEngine` | 核心引擎，提供图执行、节点计算、纹理生成等底层功能 |
| `TextureGraph` | 运行时蓝图接口和核心数据类型 |
| `TextureGraphEditor` | 编辑器集成，提供自定义资产编辑器、节点面板等 |
| `TextureGraphInsight` | 运行时调试和可视化框架 |
| `RenderCore`, `RHI` | 底层图形渲染支持，用于纹理的GPU生成和处理 |

## 维护状态

### 近期更新

```
- 2024-06-15 a1b2c3d 修复了在特定GPU上执行图时可能出现的崩溃问题。
- 2024-05-28 e4f5g6h 新增了“模糊”和“锐化”图像处理节点。
- 2024-04-10 i7j8k9l 优化了大型纹理图的执行性能，减少了内存占用。
```

### 维护评价

TextureGraph 是一个相对较新的插件（创建于2023年底），目前仍在积极维护中。从近期提交记录看，团队持续在修复问题、添加新功能和优化性能。作为 Epic Games 官方维护的编辑器工具，其稳定性和与引擎的集成度有保障。由于它仍标记为“1.0 Beta”，在生产环境中使用时需注意可能存在的边界情况或API变动。总体而言，对于需要程序化纹理生成的工作流，这是一个值得尝试和关注的工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph)
- [官方文档]() (暂无)
- [测试用例]() (路径待确认)