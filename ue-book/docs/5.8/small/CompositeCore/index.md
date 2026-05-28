# CompositeCore

> Extensible core plugin for real-time compositing, with a default (holdout) composite pipeline through post-processing.

| 属性 | 值 |
|---|---|
| 中文名 | 合成核心 |
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CompositeCore` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/CompositeCore) | |

## 用途

CompositeCore 插件为 Unreal Engine 的实时合成提供了一个可扩展的核心框架。它的主要作用是实现 **Holdout（遮挡/排除）材质** 技术，使得在渲染中被标记为 Holdout 的物体（如绿幕前的演员）能够被排除出主场景的渲染通道，然后在后期处理阶段，通过一个通用的合成管道，将这些物体与另一份专门渲染的 Pass 结果进行合成。这解决了虚拟制作和影视特效中，将 CG 元素无缝融合到实景画面的核心需求。

除了默认的 Holdout 合成流程，该插件还提供了一个基于 `FCompositeCorePassProxy` 的通道代理系统，允许开发者自定义、组合和扩展合成处理步骤（如混合、锐化等）。

## 使用场景

- **虚拟制作/影视特效**：将真人绿幕表演（通过 Holdout 材质排除背景）与 CG 虚拟场景进行实时或离线合成。
- **AR/VR 应用**：将虚拟物体无缝集成到摄像头捕捉的现实世界画面中。
- **编辑器内预览**：快速预览合成效果，而无需离开编辑器或运行完整游戏。

## 蓝图用法

### 核心节点

该插件的蓝图接口主要通过 `UCompositeCoreSubsystem` 和 `UHoldoutCompositeComponent` 提供。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterPrimitive` | 将一个 Primitive Component 注册到合成系统，使其参与 Holdout 渲染。 | `UCompositeCoreSubsystem` |
| `UnregisterPrimitive` | 将一个已注册的 Primitive Component 从合成系统中移除。 | `UCompositeCoreSubsystem` |
| `IsEnabled` | 获取 `HoldoutCompositeComponent` 的启用状态。 | `UHoldoutCompositeComponent` |
| `SetEnabled` | 设置 `HoldoutCompositeComponent` 的启用状态。 | `UHoldoutCompositeComponent` |

### 使用示例（蓝图描述）

1.  **手动注册/注销**：
    在关卡蓝图或任意 Actor 蓝图中，获取 `CompositeCoreSubsystem`（通过 `Get Game Subsystem` 节点），然后调用 `Register Primitive` 或 `Unregister Primitive`，传入需要控制的 `PrimitiveComponent` 引用。

2.  **使用组件控制**：
    在 Actor 上添加一个 `HoldoutCompositeComponent`。通过它的 `SetEnabled` 函数或蓝图的 `bIsEnabled` 属性来动态控制该 Actor 及其子物体是否参与合成渲染。当组件注册时，会自动将其所属 Actor 的所有 Primitive 注册到合成系统。

## C++ 用法

### 头文件引入

```cpp
#include "CompositeCoreModule.h"
#include "CompositeCoreSubsystem.h"
#include "HoldoutCompositeComponent.h"
#include "Passes/CompositeCorePassProxy.h"
#include "Passes/CompositeCorePassMergeProxy.h"
```

### 基本用法

获取合成子系统并注册/注销组件。

```cpp
// 在某个 Actor 或 Manager 类中
void AMyActor::EnableCompositingForMesh(UStaticMeshComponent* MeshComp)
{
    if (UCompositeCoreSubsystem* Subsystem = UCompositeCoreSubsystem::Get(GetWorld()))
    {
        // 自动管理模式
        Subsystem->RegisterPrimitive(MeshComp);
    }
}

void AMyActor::DisableCompositingForMesh(UStaticMeshComponent* MeshComp)
{
    if (UCompositeCoreSubsystem* Subsystem = UCompositeCoreSubsystem::Get(GetWorld()))
    {
        Subsystem->UnregisterPrimitive(MeshComp);
    }
}
```

### 进阶用法

设置自定义的合成渲染工作（RenderWork）和通道代理（Pass Proxy）。这通常用于构建更复杂的合成管线。

```cpp
// 来自 FCompositeCorePassProxy 的子类示例
class FMyCustomPass : public FCompositeCorePassProxy
{
public:
    IMPLEMENT_COMPOSITE_PASS(FMyCustomPass);

    FMyCustomPass() : FCompositeCorePassProxy({ MakeInternalInput(0) }) {} // 声明一个内部输入

    virtual FPassTexture Add(
        FRDGBuilder& GraphBuilder,
        const FSceneView& InView,
        const FPassInputArray& Inputs,
        const FPassContext& PassContext) const override
    {
        // 在此使用 RDG 添加自定义的计算或渲染通道
        // 使用 Inputs[0].Texture 获取输入纹理
        // 使用 PassContext 获取场景信息
        // ... 实现你的合成逻辑 ...
        FScreenPassRenderTarget Output = /* 创建输出 */;
        return { Output.GetOutputTexture(), {} };
    }
};

// 配置并提交渲染工作
void ConfigureCompositingPipeline(UWorld* World)
{
    if (UCompositeCoreSubsystem* Subsystem = UCompositeCoreSubsystem::Get(World))
    {
        // 创建渲染工作
        FRenderWork Work;

        // 添加一个后期处理通道 (在 DOF 之前)
        FMyCustomPass* MyPass = new FMyCustomPass(); // 内存由 FrameAllocator 管理
        Work.FramePasses.FindOrAdd(EPostProcessingPass::BeforeDOF).Add(MyPass);

        // 设置工作
        Subsystem->SetRenderWork(MoveTemp(Work));
    }
}
```

## Demo 示例

一个简单的自定义后期处理通道代理，用于将输入纹理的颜色反转。

**MyInvertPass.h**
```cpp
#pragma once
#include "Passes/CompositeCorePassProxy.h"

class FMyInvertPassProxy : public FCompositeCorePassProxy
{
public:
    IMPLEMENT_COMPOSITE_PASS(FMyInvertPassProxy);

    FMyInvertPassProxy();
    virtual ~FMyInvertPassProxy() = default;

    virtual FPassTexture Add(
        FRDGBuilder& GraphBuilder,
        const FSceneView& InView,
        const FPassInputArray& Inputs,
        const FPassContext& PassContext) const override;
};
```

**MyInvertPass.cpp**
```cpp
#include "MyInvertPass.h"
#include "ScreenPass.h"
#include "DataDrivenShaderPlatformInfo.h"

// 着色器声明
class FMyInvertPS : public FGlobalShader
{
    DECLARE_GLOBAL_SHADER(FMyInvertPS);
    SHADER_USE_PARAMETER_STRUCT(FMyInvertPS, FGlobalShader);

    BEGIN_SHADER_PARAMETER_STRUCT(FParameters, )
        SHADER_PARAMETER_RDG_TEXTURE_SRV(Texture2D<float4>, InputTexture)
        SHADER_PARAMETER_SAMPLER(SamplerState, InputSampler)
        RENDER_TARGET_BINDING_SLOTS()
    END_SHADER_PARAMETER_STRUCT()
};
IMPLEMENT_GLOBAL_SHADER(FMyInvertPS, "/MyShaders/Private/MyInvert.usf", "MainPS", SF_Pixel);

FMyInvertPassProxy::FMyInvertPassProxy()
    : FCompositeCorePassProxy({ MakeInternalInput(0) }) // 声明接受一个内部输入纹理
{
}

FPassTexture FMyInvertPassProxy::Add(
    FRDGBuilder& GraphBuilder,
    const FSceneView& InView,
    const FPassInputArray& Inputs,
    const FPassContext& PassContext) const
{
    const FScreenPassTexture& Input = Inputs[0].Texture;
    FScreenPassRenderTarget Output = CreateOutputRenderTarget(
        GraphBuilder, InView, PassContext.OutputViewRect,
        Input.Texture->Desc, TEXT("MyInvertPassOutput"));

    // 设置着色器参数
    TShaderMapRef<FMyInvertPS> PixelShader(InView.ShaderMap);
    FMyInvertPS::FParameters* PassParameters = GraphBuilder.AllocParameters<FMyInvertPS::FParameters>();
    PassParameters->InputTexture = GraphBuilder.CreateSRV(FRDGTextureSRVDesc(Input.Texture));
    PassParameters->InputSampler = TStaticSamplerState<SF_Bilinear>::GetRHI();
    PassParameters->RenderTargets[0] = Output.GetRenderTargetBinding();

    // 添加渲染通道
    GraphBuilder.AddPass(
        RDG_EVENT_NAME("MyInvertPass"),
        PassParameters,
        ERDGPassFlags::Raster,
        [PixelShader, PassParameters, Input, Output](FRHICommandListImmediate& RHICmdList)
    {
        DrawScreenPass(RHICmdList, FScreenPassInput(Input), FScreenPassOutput(Output), *PixelShader, *PassParameters);
    });

    return { Output.GetOutputTexture(), {} };
}
```

## 模块依赖

该插件自身模块依赖较为基础，但其功能高度依赖引擎渲染管线和 Composure 相关模块。对于插件使用者，通常需要在自己的 Build.cs 中添加对 `CompositeCore` 的依赖，并可能间接需要以下模块：

| 模块 | 用途 |
|---|---|
| `Composure` | 上层的 Composure 插件，提供了更易用的蓝图层面的合成 Actor 和通道，CompositeCore 为其提供底层支持。 |
| `ComposureLayersEditor` | （编辑器插件）用于编辑器内的合成预览和调试。 |

**注意**：`CompositeCore` 本身的 `Build.cs` 文件未在提供的信息中，但其代码表明它是一个 Runtime 模块。使用者如果只调用 `UCompositeCoreSubsystem` 或 `UHoldoutCompositeComponent` 的简单 API，可能只需要依赖 `CompositeCore`。如果要自定义 `FCompositeCorePassProxy` 子类并深度集成渲染管线，则需要包含更丰富的引擎渲染头文件（如 `RenderGraphUtils.h`, `ScreenPass.h`）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-18 | `36271df5` | CompositeCore: Fix to protect passes against PF_Unknown scene color format. | 修复在场景颜色格式未知时，合成通道可能出错的问题。 |
| 2026-05-13 | `8f42dec9` | Composure: Adds a "Restrict to Active Viewport" option on the composite actor, which lets users avoid rendering for inactive viewports. | 为 Composure Actor 增加了“仅限活动视口”选项，避免在非活动视口进行无效渲染。 |
| 2026-05-13 | `c10480d9` | CompositeCore: Fix recurring issue where toast-notification-changed project settings are not version controlled. | 修复了通过 Toast 通知修改项目设置后，设置无法被版本控制持续生效的反复出现的问题。 |
| 2026-05-13 | `544ccc5e` | CompositeCore: Validation fix for temporary reference returned after ternary operator. | 修复了三元运算符返回临时引用导致的验证错误。 |
| 2026-05-13 | `03b70509` | CompositeCore: Various Claude-suggested fixes & improvements. | 集成了多项 Claude 建议的代码修复与改进。 |

### 维护评价

- **创建时间**：2025年9月，是一个相对年轻的插件。
- **更新频率**：近期（2026年5月）有密集的提交，表明该插件正处于**活跃开发和维护**阶段。更新内容包括关键 bug 修复、新功能（视口限制）和代码质量改进。
- **状态**：`.uplugin` 文件标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，表明它仍处于**实验性阶段**，但持续更新显示其开发工作正在积极进行。
- **推荐度**：虽然标记为实验性，但鉴于其由 Epic Games 维护且近期活跃，对于需要实时合成（尤其是虚拟制作领域）的项目，**推荐进行评估和尝试使用**。使用者需注意其 API 可能在未来版本中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/CompositeCore)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/CompositeCore/Tests) (如果存在)