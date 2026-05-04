# OpenColorIO (OCIO)

> Provides support for OpenColorIO

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（OCIO 配置文件、LUT 文件、编辑器图标） |
| 模块 | `OpenColorIO` (Runtime), `OpenColorIOEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/OpenColorIO) | |

## 用途

OpenColorIO (OCIO) 是一个由电影和视觉特效行业广泛使用的开源色彩管理框架。UE5 的 OpenColorIO 插件将 OCIO 库集成到引擎中，解决了以下核心问题：

1. **行业色彩空间标准化**：影视制作管线通常使用 ACES、LogC、REDWideGamut 等专业色彩空间，需要在不同软件之间保持色彩一致性。OCIO 配置文件（`.ocio`）定义了这些色彩空间之间的转换规则。

2. **视口色彩管理**：在编辑器视口中实时应用 OCIO 色彩变换，使美工和调色师能在 UE5 中看到与 Nuke、DaVinci Resolve 等合成/调色软件一致的色彩效果。

3. **GPU 加速的色彩变换**：OCIO 插件会将 OCIO 配置中的色彩变换编译为 GPU shader（HLSL），利用 DDC（Derived Data Cache）缓存编译结果，实现高效的实时渲染色彩变换。

4. **LUT 纹理支持**：对于无法用纯 shader 代码表达的复杂变换（如 3D LUT），插件会生成 Volume Texture 或 1D Texture 作为查找表。

5. **蓝图和 C++ 双向接口**：既可以在蓝图中通过节点完成色彩变换，也可以在 C++ 中通过 API 精确控制。

**为什么需要手动启用**：由于 OCIO 依赖第三方库 `OpenColorIOWrapper`，且其 shader 编译系统独立于引擎主 shader 编译管线，Epic 将其标记为 Beta 且默认禁用，避免影响不需要色彩管理的项目。

## 使用场景

- **影视虚拟制片 (Virtual Production)**：你的 LED Volume 摄影棚使用 ACES 色彩管线 → 在 UE5 编辑器中启用 OCIO 显示配置，让视口颜色与摄影机监看一致
- **VFX 预览 (Previs)**：你在 UE5 中做预演，需要与下游 Nuke 合成保持色彩空间一致 → 用 OCIO 配置文件定义相同的 ACES transform
- **游戏内色彩分级**：你需要在运行时根据场景应用不同的色彩空间变换（如不同关卡的色调） → 用蓝图节点 `ApplyColorSpaceTransform` 动态变换 RenderTarget
- **调色师工作流**：调色师需要在 UE5 中查看 LogC/ARRI Wide Gamut 画面 → 配置 OCIO Display View 将视口输出变换到 sRGB/Rec.709 监看空间
- **多软件管线统一**：你的工作室在 Maya、Houdini、Nuke 之间共享 OCIO 配置 → 在 UE5 中使用同一个 `.ocio` 文件保持一致

## 蓝图用法

### 运行时蓝图节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyColorSpaceTransform` | 将输入纹理从源色彩空间变换到目标色彩空间，输出到 RenderTarget | `UOpenColorIOBlueprintLibrary` |
| `Create OpenColorIO Display Extension` | 创建带激活函数的 OCIO 显示扩展对象 | `UOpenColorIODisplayExtensionWrapper` |
| `Create In-Game OpenColorIO Display Extension` | 创建游戏内使用的 OCIO 显示扩展 | `UOpenColorIODisplayExtensionWrapper` |
| `Get OpenColorIO Configuration` | 获取显示扩展的 OCIO 配置 | `UOpenColorIODisplayExtensionWrapper` |
| `Set OpenColorIO Configuration` | 设置显示扩展的 OCIO 配置 | `UOpenColorIODisplayExtensionWrapper` |
| `Set Scene Extension IsActiveFunction` | 设置场景扩展的激活条件函数 | `UOpenColorIODisplayExtensionWrapper` |
| `Remove Scene Extension` | 移除场景扩展 | `UOpenColorIODisplayExtensionWrapper` |
| `Reload Existing Colorspaces` | 强制重新加载色彩空间和 shader | `UOpenColorIOConfiguration` |

### 编辑器蓝图节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Active Viewport Configuration` | 设置当前活动编辑器视口的 OCIO 显示配置 | `UOpenColorIOEditorBlueprintLibrary` |
| `Apply Color Space Transform To Color` | 对单个颜色值应用色彩空间变换 | `UOpenColorIOEditorBlueprintLibrary` |
| `Apply Color Space Transform To Texture` | 对纹理资产应用色彩空间变换（就地修改） | `UOpenColorIOEditorBlueprintLibrary` |
| `Apply Color Space Transform To Texture Compressed` | 对纹理应用色彩变换，指定目标压缩格式 | `UOpenColorIOEditorBlueprintLibrary` |

### 蓝图结构体

| 结构体 | 说明 |
|---|---|
| `FOpenColorIOColorSpace` | OCIO 色彩空间标识（名称、家族、描述） |
| `FOpenColorIODisplayView` | OCIO Display-View 标识（Display 名称 + View 名称） |
| `FOpenColorIOColorConversionSettings` | 完整的色彩转换配置（源/目标色彩空间、配置源） |
| `FOpenColorIODisplayConfiguration` | 显示配置（启用开关 + 色彩转换设置） |
| `EOpenColorIOViewTransformDirection` | 变换方向枚举：Forward（正向）/ Inverse（反向） |

### 使用示例（蓝图描述）

**运行时色彩变换**：
1. 创建一个 `UOpenColorIOConfiguration` 资产，设置 `.ocio` 配置文件路径
2. 在 `DesiredColorSpaces` 中添加源色彩空间（如 "ACES - ACEScg"）和目标色彩空间（如 "Output - sRGB"）
3. 在蓝图中，获取输入纹理 → 调用 `ApplyColorSpaceTransform` 节点 → 连接 `FOpenColorIOColorConversionSettings`（指定配置源、源/目标色彩空间）→ 输出到 RenderTarget

**视口 OCIO 显示**：
1. 在编辑器视口的 View 菜单中找到 "Color Management > OCIO Display" 子菜单
2. 选择 OCIO 配置文件
3. 选择 Display（如 "sRGB"）和 View（如 "ACES 1.0 - SDR Video"）
4. 勾选 "Enable OCIO" 启用

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块
#include "OpenColorIOConfiguration.h"
#include "OpenColorIOColorTransform.h"
#include "OpenColorIOColorSpace.h"
#include "OpenColorIORendering.h"
#include "OpenColorIOBlueprintLibrary.h"
#include "OpenColorIODisplayExtensionWrapper.h"

// Editor 模块
#include "OpenColorIOEditorBlueprintLibrary.h"
```

### 基本用法：色彩空间变换

以下代码演示如何在 C++ 中对颜色值应用 OCIO 变换：

```cpp
// 来源: OpenColorIOConfiguration.h, OpenColorIOColorSpace.h

// 1. 加载 OCIO 配置资产
UOpenColorIOConfiguration* Config = LoadObject<UOpenColorIOConfiguration>(nullptr, TEXT("/Game/OCIO/MyOCIOConfig"));

// 2. 构建色彩转换设置
FOpenColorIOColorConversionSettings Settings;
Settings.ConfigurationSource = Config;
Settings.SourceColorSpace = FOpenColorIOColorSpace(TEXT("ACES - ACEScg"), INDEX_NONE, TEXT("ACES"));
Settings.DestinationColorSpace = FOpenColorIOColorSpace(TEXT("Output - sRGB"), INDEX_NONE, TEXT("Output"));

// 3. 变换单个颜色值
FLinearColor Color(1.0f, 0.5f, 0.2f, 1.0f);
Config->TransformColor(Settings, Color);
// Color 现在已经从 ACEScg 变换到 sRGB
```

### 基本用法：GPU 渲染管线中的色彩变换

```cpp
// 来源: OpenColorIORendering.h

// 方式 1：简单的纹理到 RenderTarget 变换
FOpenColorIORendering::ApplyColorTransform(
    World,
    ConversionSettings,
    InputTexture,
    OutputRenderTarget
);

// 方式 2：通过 RDG（Render Dependency Graph）添加渲染 pass
FOpenColorIORenderPassResources PassResources = 
    FOpenColorIORendering::GetRenderPassResources(Settings, FeatureLevel);

// 在渲染线程中：
FOpenColorIORendering::AddPass_RenderThread(
    GraphBuilder,
    View,
    InputScreenPassTexture,
    OutputRenderTarget,
    PassResources,
    EOpenColorIOTransformAlpha::None
);
```

### 进阶用法：Display Extension（视口级 OCIO）

```cpp
// 来源: OpenColorIODisplayExtensionWrapper.h

// 创建一个游戏内 OCIO 显示扩展
FOpenColorIODisplayConfiguration DisplayConfig;
DisplayConfig.bIsEnabled = true;
DisplayConfig.ColorConfiguration.ConfigurationSource = MyConfig;
DisplayConfig.ColorConfiguration.SourceColorSpace = FOpenColorIOColorSpace(TEXT("lin_srgb"), INDEX_NONE, TEXT(""));
DisplayConfig.ColorConfiguration.DestinationDisplayView = FOpenColorIODisplayView(TEXT("sRGB"), TEXT("ACES 1.0 - SDR Video"));
DisplayConfig.ColorConfiguration.DisplayViewDirection = EOpenColorIOViewTransformDirection::Forward;

UOpenColorIODisplayExtensionWrapper* Extension = 
    UOpenColorIODisplayExtensionWrapper::CreateInGameOpenColorIODisplayExtension(DisplayConfig);

// 设置激活条件（可选）
FSceneViewExtensionIsActiveFunctor IsActiveFunc;
IsActiveFunc.IsActiveFunction = [](const FSceneViewExtensionContext& Context) -> bool
{
    // 仅在特定条件下激活
    return true;
};
Extension->SetSceneExtensionIsActiveFunction(IsActiveFunc);
```

### 进阶用法：OCIO Context（上下文变量）

```cpp
// 来源: OpenColorIOConfiguration.h
// OCIO Context 允许你用键值对覆盖配置文件中的变量，常用于镜头级别的色彩调整

UOpenColorIOConfiguration* Config = ...;
Config->Context.Add(TEXT("SHOT"), TEXT("shot_0010"));
Config->Context.Add(TEXT("CDL_SAT"), TEXT("1.2"));

// 重新加载以应用上下文变更
Config->ReloadExistingColorspaces(true);
```

### 进阶用法：Display-View 变换方向

```cpp
// 来源: OpenColorIOColorSpace.h
// Forward: 从场景空间变换到显示空间（用于监看）
// Inverse: 从显示空间变换回场景空间（用于输入 LUT 解码）

FOpenColorIOColorConversionSettings Settings;
Settings.ConfigurationSource = Config;
Settings.SourceColorSpace = FOpenColorIOColorSpace(TEXT("lin_srgb"), INDEX_NONE, TEXT(""));
Settings.DestinationDisplayView = FOpenColorIODisplayView(TEXT("sRGB"), TEXT("Filmic"));
Settings.DisplayViewDirection = EOpenColorIOViewTransformDirection::Inverse;
```

## Demo 示例

### 最小可运行示例：运行时色彩变换

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "OpenColorIO"
});
```

**MyColorTransformActor.h**：

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OpenColorIOColorSpace.h"
#include "MyColorTransformActor.generated.h"

class UOpenColorIOConfiguration;
class UTextureRenderTarget2D;
class UTexture2D;

UCLASS()
class AMyColorTransformActor : public AActor
{
    GENERATED_BODY()

public:
    AMyColorTransformActor();

    UPROPERTY(EditAnywhere, Category = "OCIO")
    TObjectPtr<UOpenColorIOConfiguration> OCIOConfig;

    UPROPERTY(EditAnywhere, Category = "OCIO")
    TObjectPtr<UTexture2D> InputTexture;

    UPROPERTY(EditAnywhere, Category = "OCIO")
    TObjectPtr<UTextureRenderTarget2D> OutputRenderTarget;

    UFUNCTION(BlueprintCallable, Category = "OCIO")
    void ApplyTransform();
};
```

**MyColorTransformActor.cpp**：

```cpp
#include "MyColorTransformActor.h"
#include "OpenColorIOConfiguration.h"
#include "OpenColorIORendering.h"
#include "Engine/Texture2D.h"
#include "Engine/TextureRenderTarget2D.h"

AMyColorTransformActor::AMyColorTransformActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyColorTransformActor::ApplyTransform()
{
    if (!OCIOConfig || !InputTexture || !OutputRenderTarget)
    {
        return;
    }

    FOpenColorIOColorConversionSettings Settings;
    Settings.ConfigurationSource = OCIOConfig;
    Settings.SourceColorSpace = FOpenColorIOColorSpace(TEXT("lin_srgb"), INDEX_NONE, TEXT(""));
    Settings.DestinationColorSpace = FOpenColorIOColorSpace(TEXT("sRGB - Texture"), INDEX_NONE, TEXT(""));

    FOpenColorIORendering::ApplyColorTransform(GetWorld(), Settings, InputTexture, OutputRenderTarget);
}
```

### 最小可运行示例：编辑器视口 OCIO

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "OpenColorIO",
    "OpenColorIOEditor"
});
```

```cpp
#include "OpenColorIOEditorBlueprintLibrary.h"
#include "OpenColorIOConfiguration.h"
#include "OpenColorIOColorSpace.h"

void SetViewportOCIO(UOpenColorIOConfiguration* Config)
{
    FOpenColorIODisplayConfiguration DisplayConfig;
    DisplayConfig.bIsEnabled = true;
    DisplayConfig.ColorConfiguration.ConfigurationSource = Config;
    DisplayConfig.ColorConfiguration.SourceColorSpace = 
        FOpenColorIOColorSpace(TEXT("lin_srgb"), INDEX_NONE, TEXT(""));
    DisplayConfig.ColorConfiguration.DestinationDisplayView = 
        FOpenColorIODisplayView(TEXT("sRGB"), TEXT("ACES 1.0 - SDR Video"));
    DisplayConfig.ColorConfiguration.DisplayViewDirection = 
        EOpenColorIOViewTransformDirection::Forward;

    UOpenColorIOEditorBlueprintLibrary::SetActiveViewportConfiguration(DisplayConfig);
}
```

## 模块依赖

### OpenColorIO (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎运行时（World、Texture 等） |
| `DeveloperSettings` | 项目设置基类（UOpenColorIOSettings） |
| `OpenColorIOWrapper` | OCIO C++ 库的 UE 封装层（第三方） |
| `RHI` (Private) | 渲染硬件接口 |
| `RenderCore` (Private) | 渲染核心（Shader、RenderResource） |
| `Renderer` (Private) | 渲染器（RDG、后处理） |
| `ImageCore` (Private) | 图像处理（FImageView） |
| `Slate` / `SlateCore` (Private) | UI 框架（用于通知 Toast） |

### OpenColorIOEditor (Editor)

| 模块 | 用途 |
|---|---|
| `OpenColorIO` | Runtime 模块依赖 |
| `OpenColorIOWrapper` | OCIO 库封装 |
| `UnrealEd` | 编辑器框架 |
| `PropertyEditor` | 属性面板自定义 |
| `AssetDefinition` | 资产类型定义 |
| `LevelEditor` | 关卡编辑器（视口扩展） |
| `ToolMenus` | 工具菜单（View 菜单扩展） |
| `Settings` | 设置面板注册 |
| `Slate` / `SlateCore` | UI 组件（色彩空间选择器等） |

## 架构概览

### 核心类关系

```
UOpenColorIOConfiguration          ← 资产：管理 OCIO 配置文件和色彩空间列表
  ├── ConfigurationFile            ← .ocio 文件路径
  ├── DesiredColorSpaces[]         ← 需要使用的色彩空间列表
  ├── DesiredDisplayViews[]        ← 需要使用的 Display-View 列表
  ├── Context{}                    ← OCIO 上下文变量（镜头级别覆盖）
  └── ColorTransforms[]            ← 子对象：每个色彩变换
        └── UOpenColorIOColorTransform   ← 单个变换：shader + LUT 纹理
              ├── GeneratedShader        ← OCIO 生成的 HLSL 代码
              ├── LookupTextures[]       ← 3D/1D LUT 纹理
              └── ColorTransformResources[] ← 编译后的 shader map
```

### Shader 编译管线

1. OCIO 库根据配置文件生成 HLSL shader 代码
2. `FOpenColorIOShaderCompilationManager` 管理异步编译任务
3. 编译结果通过 `FOpenColorIOShaderMap` 缓存到 DDC
4. 渲染时从 DDC 加载已编译的 shader，避免重复编译

### 渲染管线集成

- **后处理 Pass**：`FOpenColorIODisplayExtension` 通过 `FSceneViewExtensionBase` 在 Tonemap 之后插入 OCIO 变换 pass
- **独立 RenderPass**：`FOpenColorIORendering::AddPass_RenderThread` 通过 RDG 添加自定义变换 pass
- **纹理变换**：`FOpenColorIORendering::ApplyColorTransform` 将变换渲染到指定 RenderTarget

## 编辑器功能

### 视口 OCIO 显示

编辑器模块在每个 Level Viewport 的 **View 菜单**中添加了 "Color Management > OCIO Display" 子菜单：

- 选择 OCIO 配置文件
- 选择 Display（如 sRGB、DCI-P3）
- 选择 View（如 ACES 1.0 - SDR Video、Filmic）
- 启用/禁用 OCIO 显示
- 视口配置会持久化保存到 `OpenColorIO.ini`

### 属性面板自定义

- `UOpenColorIOConfiguration` 的属性面板：自定义 Detail 面板，支持配置文件选择、色彩空间下拉选择器
- `FOpenColorIOColorConversionSettings` 的属性面板：自定义属性类型布局，级联更新色彩空间选项

### 设置面板

在 **Editor > Plugins > OpenColorIO Editor** 中可配置：
- 默认视口 OCIO 显示配置

在 **Project Settings > Engine > OpenColorIO** 中可配置：
- 启用 Legacy GPU Processor（兼容 OCIO v1）
- 使用 32-bit float LUT 纹理（更高精度，性能开销更大）
- 支持 Inverse View Transforms（默认禁用以减少 shader 变体数量）

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-10-07 | `a2b9cd58` | OpenColorIO: Restrain precise keyword to when REFACTORING_ALLOWED is defined, per specification | 编译器兼容性修复，`precise` 关键字仅在允许重构时使用 |
| 2025-08-06 | `2deb368b` | Removing some stale shader compilation debug logging (DEBUG_INFINITESHADERCOMPILE) | 清理过时的 shader 编译调试日志代码 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 代码质量改进，使用内联生成的 cpp 文件 |

### 维护评价

- **创建时间**：2019 年 1 月（约 7 年前）
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion=true`，但插件已经过多年实际使用验证
- **更新频率**：最近的 3 次 commit 都是编译器兼容性和代码清理，无功能性更新
- **活跃程度**：**维护中** — 虽然近期无重大功能更新，但仍在持续适配引擎版本变化
- **已知限制**：
  - 默认禁用，需要手动启用
  - Editor 模块仅支持 Win64/Linux/Mac
  - OCIO v1 Legacy GPU Processor 需要在设置中手动开启
  - Inverse View Transforms 默认禁用以控制 shader 变体数量
- **推荐**：**推荐使用** — 对于需要行业标准色彩管理的影视/虚拟制片项目，这是 UE5 中唯一的标准化方案。虽然标记为 Beta，但已经在 Epic 的虚拟制片管线中经过实际验证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/OpenColorIO)
- [OpenColorIO 官方网站](https://opencolorio.org/)
- [OCIO 配置文件格式文档](https://opencolorio.readthedocs.io/en/latest/guides/authoring/overview.html)
- [UE5 OCIO 官方文档](https://docs.unrealengine.com/5.0/en-US/open-color-io-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/OpenColorIO/Tests)（插件目录内无独立测试文件）
