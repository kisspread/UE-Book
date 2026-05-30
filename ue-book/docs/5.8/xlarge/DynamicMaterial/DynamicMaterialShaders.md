# Material Designer

> Compact dynamic material creator and editor, similar in style to other DDCs.

| 属性 | 值 |
|---|---|
| 中文名 | 材质设计器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、纹理集资产） |
| 模块 | `DynamicMaterial` (RuntimeAndProgram), `DynamicMaterialTextureSet` (RuntimeAndProgram), `DynamicMaterialEditor` (Editor), `DynamicMaterialTextureSetEditor` (Editor), `DynamicMaterialShaders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DynamicMaterial) | |

## 用途

DynamicMaterial（材质设计器）是 Motion Design / Virtual Production 工具链中的动态材质系统。它提供了一套**运行时材质创建与编辑**框架，允许用户通过类似 DDC（Data-Driven Components）的模式，在运行时程序化地构建、修改和应用材质。

核心能力包括：
- **动态材质实例管理**：运行时创建和编辑 UMaterialInstanceDynamic，无需预先烘焙材质资产
- **纹理集（Texture Set）系统**：独立的纹理集模块，用于管理一组关联纹理（如法线贴图、粗糙度、金属度等），可作为材质参数的整体输入
- **自定义着色器**：内置专用的全局着色器（如 Alpha OneMinus），用于材质处理管线中的特殊运算
- **编辑器可视化设计**：Editor 模块提供类似蓝图节点图的材质设计界面，用户可在编辑器中可视化构建材质逻辑，然后在运行时实例化

该插件从 Epic 的 Motion Design（动态设计）实验性工具演变而来，是虚拟制片场景中快速迭代材质效果的关键基础设施。

## 使用场景

- 你在做虚拟制片/VFX 现场调色 → 用 Material Designer 在运行时动态调整材质参数
- 你需要程序化生成大量相似但参数不同的材质实例 → 用 DynamicMaterial 批量创建
- 你需要将一组关联纹理（BaseColor、Normal、ORM 等）作为一个整体管理 → 用 TextureSet 模块
- 你在 Motion Design 工具链中工作，需要 DDC 风格的材质编辑器 → 使用 Editor 模块的可视化设计器

## 蓝图用法

> ⚠️ 由于当前分析范围限于 DynamicMaterialShaders 子模块，以下为基于源码结构推断的核心蓝图 API。完整 API 需查阅 `DynamicMaterial` 主模块的公共头文件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AllocateAndSetParameters` | 分配着色器参数并绑定输入/输出纹理 | `FDMAlphaOneMinusPS` |

### 使用示例（蓝图描述）

材质设计器的典型蓝图工作流：
1. 创建一个 `DynamicMaterialInstance` 对象
2. 通过纹理集（Texture Set）将一组纹理绑定到材质参数
3. 在运行时通过材质参数接口修改颜色、标量、纹理等属性
4. 将动态材质应用到目标 Mesh Component

## C++ 用法

### 头文件引入

```cpp
// 主运行时模块
#include "DynamicMaterialModule.h"

// 着色器模块
#include "DMAlphaOneMinusPS.h"

// 纹理集模块
#include "DynamicMaterialTextureSetModule.h"
```

### 基本用法

自定义全局着色器的使用——通过 `FDMAlphaOneMinusPS` 执行纹理的 Alpha 反转运算：

```cpp
// 来源: Engine/Plugins/VirtualProduction/DynamicMaterial/Source/DynamicMaterialShaders/Public/DMAlphaOneMinusPS.h

#include "DMAlphaOneMinusPS.h"
#include "RenderGraphBuilder.h"
#include "RenderGraphUtils.h"

void MyMaterialPass(FRDGBuilder& GraphBuilder, FRDGTextureRef InputTexture, FRDGTextureRef OutputTexture)
{
    // 检查着色器是否应在当前平台编译
    // ShouldCompilePermutation 会根据平台特性判断是否可用

    // 分配参数并设置输入/输出绑定
    FDMAlphaOneMinusPS::FParameters* Parameters =
        FDMAlphaOneMinusPS::AllocateAndSetParameters(
            GraphBuilder,
            InputTexture,    // RGBA 输入纹理
            OutputTexture    // 渲染目标输出
        );

    // 使用 GraphBuilder 执行着色器 Pass
    TShaderMapRef<FDMAlphaOneMinusPS> PixelShader(
        GetGlobalShaderMap(GMaxRHIFeatureLevel)
    );

    FPixelShaderUtils::AddFullscreenPass(
        GraphBuilder,
        RDG_EVENT_NAME("DMAlphaOneMinus"),
        PixelShader,
        Parameters,
        FIntRect(0, 0, OutputTexture->Desc.GetSize().X, OutputTexture->Desc.GetSize().Y)
    );
}
```

### 进阶用法

着色器虚拟挂载点——插件通过自定义挂载点管理着色器路径：

```cpp
// 来源: Engine/Plugins/VirtualProduction/DynamicMaterial/Source/DynamicMaterialShaders/Private/DynamicMaterialShadersModule.h

// 所有着色器文件通过虚拟挂载点访问
// 挂载点: /Plugin/MaterialDesigner
// 对应磁盘路径: {PluginDir}/Shaders/

// 模块启动时自动注册虚拟着色器目录
// StartupModule() 中调用 AddShaderSourceDirectoryMapping
```

## Demo 示例

> ⚠️ 由于 DynamicMaterialShaders 是一个底层渲染模块，完整使用示例需要结合主模块 `DynamicMaterial` 和编辑器模块 `DynamicMaterialEditor`。以下为着色器模块的最小独立示例：

```cpp
// MyMaterialHelper.h
#pragma once

#include "RenderGraphFwd.h"

class FMyMaterialHelper
{
public:
    /** 使用 Alpha OneMinus 着色器处理纹理 */
    static void ProcessAlphaOneMinus(
        FRDGBuilder& GraphBuilder,
        FRDGTextureRef InInputTexture,
        FRDGTextureRef InOutputTexture);
};
```

```cpp
// MyMaterialHelper.cpp
#include "MyMaterialHelper.h"
#include "DMAlphaOneMinusPS.h"
#include "GlobalShader.h"
#include "ShaderParameterUtils.h"
#include "RenderGraphUtils.h"
#include "RHIStaticStates.h"
#include "PixelShaderUtils.h"

void FMyMaterialHelper::ProcessAlphaOneMinus(
    FRDGBuilder& GraphBuilder,
    FRDGTextureRef InInputTexture,
    FRDGTextureRef InOutputTexture)
{
    // 分配并绑定着色器参数
    FDMAlphaOneMinusPS::FParameters* Params =
        FDMAlphaOneMinusPS::AllocateAndSetParameters(
            GraphBuilder,
            InInputTexture,
            InOutputTexture
        );

    // 获取全局着色器映射表中的像素着色器
    TShaderMapRef<FDMAlphaOneMinusPS> PixelShader(
        GetGlobalShaderMap(GMaxRHIFeatureLevel)
    );

    const FIntPoint OutputSize = InOutputTexture->Desc.GetSize();

    // 添加全屏像素着色器 Pass
    FPixelShaderUtils::AddFullscreenPass(
        GraphBuilder,
        RDG_EVENT_NAME("MyAlphaOneMinusPass"),
        PixelShader,
        Params,
        FIntRect(0, 0, OutputSize.X, OutputSize.Y)
    );
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CustomDetailsView` | 自定义详情面板 UI（插件级依赖，用于编辑器模块的属性展示） |
| `RenderCore` | RDG（Render Dependency Graph）渲染管线核心 |
| `Renderer` | 全局着色器基础设施（FGlobalShader） |
| `RHI` | 渲染硬件接口 |

> 其余依赖为标准 Core/Engine/Slate 等，已在省略列表中。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 的场景设置和大纲面板标签移至独立分组 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口关联/脱离客户端通知的代码重构 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了一个提交 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口客户端通知机制重构（同上，回退前的版本） |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的编译警告 |

### 维护评价

- **创建时间**：2025 年 5 月从 Experimental 迁移到 Virtual Production，属于较新的插件
- **活跃度**：近期（2026 年 5 月）仍有持续更新，包括重构、Bug 修复等，属于**活跃维护**状态
- **状态**：作为 Motion Design 工具链的核心组件，由 Epic 团队持续维护
- **注意事项**：该插件默认未启用（`Installed: false`），需要手动在 Plugins 面板中启用，或在项目配置中显式添加
- **推荐程度**：✅ 如果你在做虚拟制片或 Motion Design 相关工作，推荐使用；纯游戏项目通常不需要

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DynamicMaterial)
- [CustomDetailsView 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CustomDetailsView)（依赖项）