# Material Designer

> Compact dynamic material creator and editor, similar in style to other DDCs.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质资产、编辑器工具） |
| 模块 | `DynamicMaterial` (RuntimeAndProgram), `DynamicMaterialTextureSet` (RuntimeAndProgram), `DynamicMaterialEditor` (Editor), `DynamicMaterialTextureSetEditor` (Editor), `DynamicMaterialShaders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial) | |

## 用途

Material Designer 是一个用于虚拟制片的动态材质创建与编辑系统。它提供了一个紧凑的、类似数据驱动内容（DDC）风格的界面，允许用户在编辑器中或运行时快速创建、编辑和预览材质。其核心目标是简化材质工作流程，特别是在需要频繁调整材质参数或程序化生成材质的虚拟制片场景中，提升迭代效率。

## 使用场景

- **虚拟制片现场调色**：在 LED 墙或绿幕拍摄现场，美术或技术美术需要实时调整场景中物体的材质属性（如颜色、粗糙度、金属感），以匹配实拍灯光。
- **程序化内容生成**：在游戏或影视中，需要根据游戏逻辑或数据动态生成材质（例如，根据天气变化改变地面材质）。
- **快速材质原型设计**：在项目早期，需要快速搭建和测试多种材质效果，而无需每次都手动创建复杂的材质图。

## 蓝图用法

**注意**：提供的源码信息主要集中在 `DynamicMaterialShaders` 模块（着色器），该模块主要提供底层渲染功能，不直接暴露蓝图 API。核心的材质创建与编辑蓝图节点预计位于 `DynamicMaterial` 运行时模块中。基于当前信息，无法列出具体的蓝图节点。完整的蓝图 API 需要查阅 `DynamicMaterial` 模块的头文件。

## C++ 用法

### 头文件引入

```cpp
#include "DMAlphaOneMinusPS.h"
```

### 基本用法（着色器示例）

以下示例展示了如何使用 `FDMAlphaOneMinusPS` 全局着色器来处理纹理。这是一个高级用法，通常由插件内部的材质系统调用。

```cpp
// 来源: Engine/Plugins/VirtualProduction/DynamicMaterial/Source/DynamicMaterialShaders/Public/DMAlphaOneMinusPS.h
// 假设在某个渲染函数中
FRDGBuilder& GraphBuilder = ...; // 从渲染上下文获取
FRDGTextureRef InputTexture = ...; // 输入纹理
FRDGTextureRef OutputTexture = ...; // 输出纹理

// 1. 检查着色器是否应该为当前平台编译
if (FDMAlphaOneMinusPS::ShouldCompilePermutation(FGlobalShaderPermutationParameters(ShaderPlatform)))
{
    // 2. 分配并设置着色器参数
    FDMAlphaOneMinusPS::FParameters* Parameters = FDMAlphaOneMinusPS::AllocateAndSetParameters(
        GraphBuilder,
        InputTexture,
        OutputTexture
    );

    // 3. 添加着色器 Pass (伪代码，实际需要使用 GraphBuilder 的 API)
    // GraphBuilder.AddPass(..., [Parameters](FRHICommandListImmediate& RHICmdList) { ... });
}
```

### 进阶用法

`FDMAlphaOneMinusPS` 着色器的功能是计算 `1 - Alpha`，这通常用于生成遮罩或反转透明度。它可能被用于 Material Designer 内部的材质混合或后处理流程中。要理解其完整用法，需要结合 `DynamicMaterial` 模块中调用它的材质图编译或渲染代码。

## Demo 示例

由于提供的信息有限，且核心运行时 API 未展示，这里仅提供一个基于 `DynamicMaterialShaders` 模块的、概念性的着色器使用示例。**请注意，这并非一个完整的材质创建示例，而是底层渲染技术的展示。**

```cpp
// MyShaderTest.h
#pragma once

#include "CoreMinimal.h"

class FMyShaderTest
{
public:
    static void TestAlphaInversion(UTexture2D* InSourceTexture, UTextureRenderTarget2D* InDestRT);
};
```

```cpp
// MyShaderTest.cpp
#include "MyShaderTest.h"
#include "DMAlphaOneMinusPS.h"
#include "RenderGraphUtils.h"
#include "RenderTargetPool.h"
#include "TextureResource.h"

void FMyShaderTest::TestAlphaInversion(UTexture2D* InSourceTexture, UTextureRenderTarget2D* InDestRT)
{
    if (!InSourceTexture || !InDestRT) return;

    // 获取渲染线程资源
    FTextureResource* SrcResource = InSourceTexture->GetResource();
    FTextureResource* DestResource = InDestRT->GetResource();
    if (!SrcResource || !DestResource) return;

    ENQUEUE_RENDER_COMMAND(MyShaderTestCmd)(
        [SrcResource, DestResource](FRHICommandListImmediate& RHICmdList)
        {
            FRDGBuilder GraphBuilder(RHICmdList);

            // 创建 RDG 纹理引用
            FRDGTextureRef RDGInputTexture = GraphBuilder.RegisterExternalTexture(
                CreateRenderTarget(SrcResource->GetTextureRHI(), TEXT("InputTex"))
            );
            FRDGTextureRef RDGOutputTexture = GraphBuilder.RegisterExternalTexture(
                CreateRenderTarget(DestResource->GetTextureRHI(), TEXT("OutputTex"))
            );

            // 检查并执行着色器
            if (FDMAlphaOneMinusPS::ShouldCompilePermutation(FGlobalShaderPermutationParameters(GMaxRHIShaderPlatform)))
            {
                FDMAlphaOneMinusPS::FParameters* PassParameters =
                    FDMAlphaOneMinusPS::AllocateAndSetParameters(GraphBuilder, RDGInputTexture, RDGOutputTexture);

                // 添加渲染 Pass
                TShaderMapRef<FDMAlphaOneMinusPS> Shader(GetGlobalShaderMap(GMaxRHIShaderPlatform));
                FIntVector GroupCount = FComputeShaderUtils::GetGroupCount(
                    FIntVector(InSourceTexture->GetSizeX(), InSourceTexture->GetSizeY(), 1),
                    FIntVector(8, 8, 1) // 假设的 GroupSize
                );
                GraphBuilder.AddPass(
                    RDG_EVENT_NAME("AlphaOneMinus"),
                    PassParameters,
                    ERDGPassFlags::Compute,
                    [Shader, PassParameters, GroupCount](FRHICommandList& RHICmdList)
                    {
                        FComputeShaderUtils::Dispatch(RHICmdList, Shader, *PassParameters, GroupCount);
                    }
                );
            }

            GraphBuilder.Execute();
        }
    );
}
```

## 模块依赖

基于模块类型和常见实践推断，`DynamicMaterialShaders` 模块可能依赖以下模块。完整的依赖关系需查阅其 `Build.cs` 文件。

| 模块 | 用途 |
|---|---|
| `Renderer` | 提供 RDG (Render Dependency Graph) 和全局着色器基础设施 |
| `RenderCore` | 提供基础渲染类型和工具 |

**注意**：`DynamicMaterial` 和 `DynamicMaterialEditor` 等核心模块的依赖关系未在提供信息中列出，它们很可能依赖 `MaterialShaderQualitySettings`, `MeshDescription` 等材质相关模块。

## 维护状态

### 近期更新

- `6f3011ad3a9f` Material Designer: Shaders module is now runtime instead of editor. (将着色器模块从编辑器类型改为运行时类型)

### 维护评价

- **创建时间**：插件创建于 2024 年初，非常年轻。
- **最近更新**：提供的 git 历史仅显示一次提交，但这次提交（将着色器模块改为运行时）是一个重要的架构调整，表明插件正在积极开发和优化中。
- **活跃度**：基于单次提交和创建时间，判断为**活跃开发中**。作为 Epic Games 官方维护的虚拟制片工具，预计会持续更新。
- **已知问题**：无已知问题信息。
- **推荐使用**：**推荐**。这是一个官方的、专注于虚拟制片的材质工具，适合需要动态材质工作流的项目。由于插件较新，建议关注其后续版本更新和文档完善。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial)
- [官方文档]() (暂无)
- [测试用例]() (未在提供信息中发现)