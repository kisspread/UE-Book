# CompositeCore

> Extensible core plugin for real-time compositing, with a default (holdout) composite pipeline through post-processing.

| 属性 | 值 |
|---|---|
| 分类 | Compositing |
| 默认启用 | `false` |
| 包含内容 | `false` |
| 模块 | CompositeCore (Runtime) |
| 创建时间 | 2025-09-23 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/CompositeCore) | |

> ⚠️ **实验性插件**：此插件标记为 `IsExperimentalVersion = true`，且 `EnabledByDefault = false`。使用前需手动在 Plugins 面板中启用。

## 用途

CompositeCore 是 UE5 的实时合成（Compositing）核心框架插件。它提供了一个可扩展的后处理管线（Post-Processing Pipeline），允许你将 Holdout 对象（即用作遮罩/挖空的几何体）与主场景渲染分开处理，然后通过可编程的合成 Pass 系统将它们重新合并。

核心解决的问题是：**如何在 UE5 的后处理阶段中，将 3D 场景中特定物体的渲染与主渲染分离，进行独立处理后再合成回来**。典型应用场景是虚拟制片（Virtual Production）中的 LED 墙内容与前景演员的合成，或者将 CG 内容与实拍画面混合。

插件基于 UE5 的 Scene View Extension 机制，在后处理管线的多个阶段插入自定义渲染 Pass。内置了一个默认的 Holdout 合成管线，同时允许通过 `FCompositeCorePassProxy` 扩展自定义 Pass。

## 使用场景

- 你在做虚拟制片（Virtual Production），需要将 LED 墙内容与前景演员合成 → 使用 Holdout Composite
- 你需要将特定 3D 物体从主渲染中"挖空"（Holdout），单独渲染后再合并 → 在 Actor 上添加 HoldoutCompositeComponent
- 你需要自定义合成管线，在合成阶段加入自己的 FXAA、色彩空间转换、混合模式等处理 → 扩展 FCompositeCorePassProxy
- 你需要将外部纹理（如实拍视频画面）与 3D 场景合成 → 使用 FRenderWork 的 ExternalInputs

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Register Primitive` | 注册一个 Primitive Component 参与合成渲染 | `UCompositeCoreSubsystem` |
| `Unregister Primitive` | 取消一个 Primitive Component 的合成注册 | `UCompositeCoreSubsystem` |
| `Is Enabled` | 获取 Holdout 组件是否启用 | `UHoldoutCompositeComponent` |
| `Set Enabled` | 设置 Holdout 组件的启用状态 | `UHoldoutCompositeComponent` |

### 使用示例（蓝图描述）

#### 基本 Holdout 设置

1. 在需要参与合成的 Actor 上添加 `HoldoutCompositeComponent`（在组件面板搜索 "Holdout Composite"）
2. 确保项目设置中启用了必要的渲染特性（插件会在不满足条件时弹出通知提示）
3. `HoldoutCompositeComponent` 会在 `OnRegister` 时自动将自身 Actor 的 Primitive 注册到 `UCompositeCoreSubsystem`
4. 通过组件的 `bIsEnabled` 属性（可在 Details 面板编辑，或通过蓝图 `Set Enabled` 节点）控制是否参与合成

#### 动态注册 Primitive

1. 获取 World 的 `UCompositeCoreSubsystem`（通过 `Get World Subsystem` 节点，选择 `CompositeCoreSubsystem`）
2. 调用 `Register Primitive` 节点，传入目标 `PrimitiveComponent` 引用
3. 该 Primitive 的渲染将从主场景分离，在后处理阶段进行独立合成
4. 不再需要时调用 `Unregister Primitive` 取消注册

## C++ 用法

### 头文件引入

```cpp
#include "CompositeCoreSubsystem.h"
#include "HoldoutCompositeComponent.h"
#include "CompositeCoreSettings.h"
#include "Passes/CompositeCorePassProxy.h"
```

### 基本用法：注册/取消 Primitive

```cpp
// 获取 CompositeCore 子系统
UCompositeCoreSubsystem* Subsystem = GetWorld()->GetSubsystem<UCompositeCoreSubsystem>();

// 注册一个 Primitive 参与合成
Subsystem->RegisterPrimitive(MyPrimitiveComponent);

// 批量注册
TArray<UPrimitiveComponent*> Primitives = { Prim1, Prim2, Prim3 };
Subsystem->RegisterPrimitives(Primitives);

// 取消注册
Subsystem->UnregisterPrimitive(MyPrimitiveComponent);
```

### 进阶用法：自定义合成 Pass

CompositeCore 的核心扩展点是 `FCompositeCorePassProxy`。你可以继承它来创建自定义的渲染 Pass：

```cpp
// 声明自定义 Pass
class FMyCustomPassProxy : public FCompositeCorePassProxy
{
public:
    IMPLEMENT_COMPOSITE_PASS(FMyCustomPassProxy);  // 必须：提供 RTTI 支持

    using FCompositeCorePassProxy::FCompositeCorePassProxy;

    // 核心：实现 Add 方法，在 RDG 中添加自定义渲染 Pass
    virtual UE::CompositeCore::FPassTexture Add(
        FRDGBuilder& GraphBuilder,
        const FSceneView& InView,
        const UE::CompositeCore::FPassInputArray& Inputs,
        const UE::CompositeCore::FPassContext& PassContext
    ) const override
    {
        // 获取输入纹理
        const UE::CompositeCore::FPassInput& Input = Inputs[0];
        
        // 创建输出 Render Target
        FScreenPassRenderTarget Output = CreateOutputRenderTarget(
            GraphBuilder, InView, PassContext.OutputViewRect,
            Input.Texture.Target->GetDesc(), TEXT("MyCustomPass"));
        
        // ... 在这里添加你的 RDG Pass ...
        
        return { Output, Input.Metadata };
    }
};
```

### 内置 Pass Proxy 类

插件提供了两个内置的 Pass Proxy 供直接使用或参考：

| 类 | 说明 | 头文件 |
|---|---|---|
| `UE::CompositeCore::FMergePassProxy` | 合并/混合 Pass，支持 20 种混合模式 | `Passes/CompositeCorePassMergeProxy.h` |
| `UE::CompositeCore::FFXAAPassProxy` | FXAA 抗锯齿 Pass，质量可配置 | `Passes/CompositeCorePassFXAAProxy.h` |

### Merge 混合模式

`FMergePassProxy` 支持以下混合模式（`ECompositeCoreMergeOp`），均假设输入为 Alpha 预乘格式：

| 模式 | 说明 |
|---|---|
| `None` | 直接替换 |
| `Over` | A + B × (1 - a)，标准 Alpha 合成 |
| `Under` | A × (1 - b) + B |
| `Add` | A + B |
| `Subtract` | A - B |
| `Multiply` | A × B |
| `Divide` | A / B（安全除法） |
| `Min` / `Max` | 逐分量最小/最大值 |
| `In` | A × b，用 B 的 Alpha 遮罩 A |
| `Mask` | B × a，用 A 的 Alpha 遮罩 B |
| `Screen` / `Overlay` / `Darken` / `Lighten` | 标准 PS 风格混合模式 |
| `ColorDodge` / `ColorBurn` / `HardLight` / `SoftLight` | 高级混合模式 |
| `Difference` / `Exclusion` | 差值/排除混合 |

### 设置渲染工作（Render Work）

```cpp
#include "Passes/CompositeCorePassProxy.h"

// 构建本帧的渲染工作
UE::CompositeCore::FRenderWork Work;

// 添加外部纹理输入
UE::CompositeCore::FExternalTexture ExtTex;
ExtTex.Texture = MyVideoTexture;
ExtTex.Metadata.bInvertedAlpha = false;
ExtTex.Metadata.Encoding = UE::CompositeCore::EEncoding::sRGB;
Work.ExternalInputs.Add(ExtTex);

// 添加后处理 Pass（例如在 Tonemap 之后）
FCompositeCorePassProxy* MergePass = new UE::CompositeCore::FMergePassProxy(
    UE::CompositeCore::GetDefaultInputDeclArray(),
    ECompositeCoreMergeOp::Over,
    TEXT("MyMergePass"));
Work.FramePasses.FindOrAdd(ISceneViewExtension::EPostProcessingPass::AfterTonemapping).Add(MergePass);

// 设置到子系统
Subsystem->SetRenderWork(MoveTemp(Work));

// 完成后重置
Subsystem->ResetRenderWork();
```

### 配置项目设置

```cpp
#include "CompositeCoreSettings.h"

// 检查项目设置是否有效（必须启用特定渲染特性）
bool bValid = UCompositeCoreSubsystem::IsProjectSettingsValid();
```

设置项可在 **Project Settings → Plugins → Composite Core** 中配置：

| 设置 | 控制台变量 | 说明 |
|---|---|---|
| Apply Pre-Exposure | `CompositeCore.ApplyPreExposure` | 是否在合成渲染上应用场景的 Pre-Exposure，使曝光匹配 |
| Apply FXAA | `CompositeCore.ApplyFXAA` | 是否在合成渲染上应用 FXAA 抗锯齿（质量由 `r.FXAA.Quality` 控制） |
| Disabled Primitive Classes | — | 不支持合成管线的 Primitive 类列表 |
| Allowed Component Classes | — | 允许的组件类（不会因为找不到关联 Primitive 而报警告） |
| Scene View Extension Priority | — | 合成后处理优先级，默认在 OpenColorIO 之前 |

## Demo 示例

以下是一个最小的 C++ 示例，在 Actor 上动态启用 Holdout 合成：

### MyHoldoutActor.h

```cpp
#pragma once

#include "GameFramework/Actor.h"
#include "MyHoldoutActor.generated.h"

class UHoldoutCompositeComponent;
class UStaticMeshComponent;

UCLASS()
class AMyHoldoutActor : public AActor
{
    GENERATED_BODY()

public:
    AMyHoldoutActor();

private:
    UPROPERTY(VisibleAnywhere)
    UStaticMeshComponent* MeshComponent;

    UPROPERTY(VisibleAnywhere)
    UHoldoutCompositeComponent* HoldoutComponent;
};
```

### MyHoldoutActor.cpp

```cpp
#include "MyHoldoutActor.h"
#include "HoldoutCompositeComponent.h"
#include "Components/StaticMeshComponent.h"

AMyHoldoutActor::AMyHoldoutActor()
{
    MeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;

    // 添加 Holdout Composite 组件，此 Actor 的 Mesh 将从主场景渲染分离
    HoldoutComponent = CreateDefaultSubobject<UHoldoutCompositeComponent>(TEXT("Holdout"));
    HoldoutComponent->SetupAttachment(RootComponent);
}
```

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "CompositeCore"   // 添加此依赖
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统（反射、序列化） |
| `Engine` | 引擎核心（World、Subsystem、Component 等） |
| `DeveloperSettings` | 开发者设置基类（UDeveloperSettings） |
| `RenderCore` | 渲染核心（RDG、Pooled Render Target） |
| `Renderer` | 渲染器（Scene View Extension、Post Processing） |
| `RHI` | 渲染硬件接口 |

> 注意：`RenderCore`、`Renderer`、`RHI` 为 Private 依赖，使用者不需要额外引用。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-10-15 | `6f4bb82` | Composite: Fixed pre-processing passes incorrectly running twice | 修复预处理 Pass 被错误执行两次的 bug |
| 2025-10-15 | `7a2d3a2` | Composite: Fix unwanted transition to external on active scene capture render target(s) | 修复场景捕获 Render Target 的外部状态转换问题 |
| 2025-10-13 | `1268cb7` | Composite: Fixed RHI validation errors and preventing failing ensures | 修复 RHI 验证错误和断言失败 |

### 维护评价

- **创建时间**：2025 年 9 月，是一个非常新的插件（约 7 个月）
- **实验性状态**：标记为 `IsExperimentalVersion = true`，API 可能发生变化
- **最近更新**：最近一次更新在 2025 年 10 月，距今约 7 个月
- **维护活跃度**：维护中 — 有活跃的 bug 修复，但暂无功能性更新
- **注意事项**：作为实验性插件，`EnabledByDefault = false`，API 不稳定，不建议在生产环境中作为核心依赖
- **推荐程度**：✅ 推荐用于原型验证和虚拟制片实验场景；⚠️ 生产环境需评估稳定性风险

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/CompositeCore)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- 测试用例：未找到专用测试文件
