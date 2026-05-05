# Texture Graph

> Texture creation tool using graphs.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `TextureGraph` (Runtime), `TextureGraphEditor` (Runtime), `TextureGraphEngine` (Runtime), `TextureGraphInsight` (Runtime), `TextureGraphInsightEditor` (Runtime), `Continuable` (External), `Function2` (External) |
| 实验性 | 否 |
| 创建时间 | 2023-12-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph) | |

## 用途

TextureGraph 是一个基于节点图的程序化纹理创建与处理系统。它提供了一个完整的、集成在虚幻编辑器中的工作流，允许美术和技术美术通过连接各种功能节点（如噪声生成、颜色调整、混合、滤镜等）来程序化地生成和编辑纹理，而无需编写代码或依赖外部软件。其核心目标是提升纹理资产的创作效率、可复用性和迭代速度，特别适用于需要大量变体或动态生成纹理的项目。

## 使用场景

- 你需要为开放世界游戏程序化生成大量地形纹理、岩石或植被的变体。
- 你希望美术团队能够在编辑器内通过可视化方式快速原型化和迭代材质贴图（如漫反射、法线、粗糙度）。
- 你需要创建动态的、运行时可修改的纹理效果（如基于游戏状态变化的UI或特效纹理）。
- 你希望将复杂的纹理处理流程（如从高度图生成法线图）封装成可复用的节点图资产。

## 蓝图用法

TextureGraph 的蓝图接口主要通过 `TextureGraph` 模块暴露，允许在运行时或编辑器中操作纹理图资产。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Texture Graph Instance` | 从 `UTextureGraph` 资产创建一个可执行的实例。 | `UTextureGraphBlueprintLibrary` |
| `Execute Texture Graph` | 执行一个纹理图实例，生成输出纹理。 | `UTextureGraphBlueprintLibrary` |
| `Set Input Parameter` | 设置纹理图实例的输入参数（如标量、向量、纹理引用）。 | `UTextureGraphBlueprintLibrary` |
| `Get Output Texture` | 获取纹理图执行后生成的输出纹理对象。 | `UTextureGraphBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **创建并执行纹理图**：
    - 使用 `Create Texture Graph Instance` 节点，传入一个在编辑器中创建的 `UTextureGraph` 资产引用。
    - 将实例输出连接到 `Execute Texture Graph` 节点的输入。
    - （可选）在执行前，使用 `Set Input Parameter` 节点动态设置图的参数。
    - 执行后，使用 `Get Output Texture` 节点获取生成的 `UTexture2D` 对象，可将其应用于材质或UI。

## C++ 用法

TextureGraph 的 C++ API 主要用于深度集成、自定义节点开发或性能关键的批量处理。

### 头文件引入

```cpp
#include "TextureGraphEngine.h"
#include "TextureGraph.h"
```

### 基本用法

以下示例展示了如何在 C++ 中加载并执行一个纹理图资产。
*（注：基于 TextureGraph 模块的典型 API 模式推断）*

```cpp
// 假设 UTextureGraph* MyGraphAsset 已通过资产加载获得
UTextureGraph* MyGraphAsset = LoadObject<UTextureGraph>(nullptr, TEXT("/Game/MyGraphs/TG_GrassVariation"));

if (MyGraphAsset)
{
    // 创建实例
    UTextureGraphInstance* GraphInstance = UTextureGraphBlueprintLibrary::CreateTextureGraphInstance(MyGraphAsset);
    
    // 设置一个输入参数（例如，一个颜色值）
    FTextureGraphParameter Param;
    Param.Name = TEXT("BaseColor");
    Param.Value = FLinearColor(0.2f, 0.8f, 0.1f);
    UTextureGraphBlueprintLibrary::SetInputParameter(GraphInstance, Param);
    
    // 执行图
    UTextureGraphBlueprintLibrary::ExecuteTextureGraph(GraphInstance);
    
    // 获取结果
    UTexture2D* ResultTexture = UTextureGraphBlueprintLibrary::GetOutputTexture(GraphInstance, TEXT("Color"));
    if (ResultTexture)
    {
        // 使用生成的纹理，例如设置到动态材质实例上
        DynamicMaterialInstance->SetTextureParameterValue(TEXT("GrassTexture"), ResultTexture);
    }
}
```

### 进阶用法

开发自定义纹理图节点需要继承 `UTextureGraph节点` 基类并实现其 `Evaluate` 方法。这通常在 `TextureGraphEngine` 模块中进行。

```cpp
// MyCustomNoiseNode.h
#pragma once
#include "TextureGraphNode.h"
#include "MyCustomNoiseNode.generated.h"

UCLASS()
class UMyCustomNoiseNode : public UTextureGraphNode
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Parameters")
    float NoiseScale = 10.0f;

    virtual void Evaluate(FTextureGraphContext& Context) override;
};

// MyCustomNoiseNode.cpp
void UMyCustomNoiseNode::Evaluate(FTextureGraphContext& Context)
{
    // 获取输入纹理（如果有）
    UTexture* InputTexture = Context.GetInputTexture(TEXT("Input"));
    
    // 生成噪声纹理的逻辑...
    UTexture2D* GeneratedNoise = GeneratePerlinNoiseTexture(Context.GetTargetSize(), NoiseScale);
    
    // 设置输出
    Context.SetOutputTexture(TEXT("Output"), GeneratedNoise);
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建一个简单的纹理图节点并注册它。

```cpp
// SimpleColorFillNode.h
#pragma once
#include "TextureGraphNode.h"
#include "SimpleColorFillNode.generated.h"

UCLASS()
class USimpleColorFillNode : public UTextureGraphNode
{
    GENERATED_BODY()
public:
    USimpleColorFillNode();
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Parameters")
    FLinearColor FillColor = FLinearColor::White;

    virtual void Evaluate(FTextureGraphContext& Context) override;
};

// SimpleColorFillNode.cpp
#include "SimpleColorFillNode.h"
#include "TextureGraphContext.h"
#include "Engine/Texture2D.h"

USimpleColorFillNode::USimpleColorFillNode()
{
    // 定义输入输出引脚
    AddOutputPin(TEXT("Output"), ETextureGraphPinType::Texture);
}

void USimpleColorFillNode::Evaluate(FTextureGraphContext& Context)
{
    FIntPoint TargetSize = Context.GetTargetSize();
    
    // 创建一张纯色纹理
    UTexture2D* ColorTexture = UTexture2D::CreateTransient(TargetSize.X, TargetSize.Y, PF_B8G8R8A8);
    ColorTexture->SRGB = true;
    
    // 锁定纹理并填充颜色
    FTexture2DMipMap& Mip = ColorTexture->PlatformData->Mips[0];
    void* TextureData = Mip.BulkData.Lock(LOCK_READ_WRITE);
    FColor* DestPtr = static_cast<FColor*>(TextureData);
    
    for (int32 Y = 0; Y < TargetSize.Y; Y++)
    {
        for (int32 X = 0; X < TargetSize.X; X++)
        {
            DestPtr[Y * TargetSize.X + X] = FillColor.ToFColor(true);
        }
    }
    
    Mip.BulkData.Unlock();
    ColorTexture->UpdateResource();
    
    // 设置输出
    Context.SetOutputTexture(TEXT("Output"), ColorTexture);
}
```

## 模块依赖

从各模块的 Build.cs 分析，TextureGraph 系统依赖于虚幻引擎的渲染和材质子系统。

| 模块 | 用途 |
|---|---|
| `RenderCore` | 底层渲染资源和命令提交。 |
| `RHI` | 渲染硬件接口，用于 GPU 纹理操作。 |
| `MaterialShaderQualitySettings` | 材质着色器质量设置，可能用于优化生成的纹理。 |
| `ImageWriteQueue` | 异步图像写入，用于将生成的纹理保存到磁盘。 |
| `Json` | 可能用于序列化纹理图资产或配置。 |
| `Projects` | 插件项目系统。 |

## 维护状态

### 近期更新

```
- 2023-12-20 731c336e7fff Moving texture graph to normal Engine/Plugins directory as part of the effort to reach Beta for 5.6
```

### 维护评价

TextureGraph 插件于 2023 年底创建，目前仅有一次将其从实验性目录移至正式插件目录的提交记录。这表明该插件正处于 **早期开发或整合阶段**，目标是作为 5.6 版本的 Beta 功能。

- **创建时间**：约 1 年前。
- **最近更新**：仅有一次目录迁移提交，没有实质性的功能更新或错误修复记录。
- **活跃度**：**不活跃**。自创建后近一年没有新的代码提交。
- **已知限制**：作为 Beta 目标，其 API 和功能可能不稳定，存在重大变更的风险。
- **推荐使用**：**谨慎使用**。适合用于技术预研、原型开发或内部工具。不建议在需要长期稳定支持的生产项目中作为核心依赖。建议密切关注其后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph)
- [官方文档]() （暂无）
- [测试用例]() （暂未发现独立的测试目录，可能集成在模块内部）