# CineCameraSceneCapture

> This plugin adds the ability to render cine camera views into Render Targets identically to Scene Capture

| 属性 | 值 |
|---|---|
| 中文名 | 电影摄像机场景捕获 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `CineCameraSceneCapture` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-05-23 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CineCameraSceneCapture) | |

## 用途

本插件解决了虚拟制片流程中的一个核心痛点：**如何将电影摄像机（Cine Camera）的精确渲染结果捕获到渲染目标（Render Target）中**。

传统的 `USceneCaptureComponent2D` 使用简化的渲染路径，与 Cine Camera 在视口中的实际显示效果可能存在差异。`UCineCaptureComponent2D` 继承自 `USceneCaptureComponent2D`，但会从关联的 `UCineCameraComponent` 获取实际的相机参数（焦距、光圈、镜头畸变等），使捕获结果与 Cine Camera 的视口输出保持一致。

典型应用场景：
- **虚拟制片**：将 Cine Camera 的画面实时输出到渲染目标，用于 LED 墙或合成工作流
- **色彩管理**：通过内置的 OpenColorIO 支持，在捕获阶段就应用正确的色彩变换
- **材质调试**：通过 `UserFlags` 实现基于视图的材质行为覆盖

## 使用场景

- 你在做虚拟制片，需要将 Cine Camera 的画面捕获到纹理用于 LED 墙显示
- 你需要将电影级镜头参数（焦距、光圈、镜头畸变）应用到场景捕获中
- 你需要在场景捕获中应用 OpenColorIO 色彩变换
- 你想通过材质中的 `TestPostVolumeUserFlag` 节点对不同视图做差异化处理

## 蓝图用法

### 核心节点

| 属性/节点 | 说明 | 所在类 |
|---|---|---|
| `RenderTargetHighestDimension` | 渲染目标最大边长，会根据 Cine Camera 宽高比自动计算实际分辨率 | `UCineCaptureComponent2D` |
| `bFollowSceneCaptureRenderPath` | 是否使用 Scene Capture 的优化渲染路径（默认 true，如捕获结果与视口差异大可关闭） | `UCineCaptureComponent2D` |
| `bOverrideUserFlags` | 是否覆盖材质中的 per-view user flags | `UCineCaptureComponent2D` |
| `UserFlags` | 材质中可通过 `TestPostVolumeUserFlag` 节点读取的自定义标志位 | `UCineCaptureComponent2D` |
| `OCIOConfiguration` | OpenColorIO 显示配置，用于在捕获时应用色彩变换 | `UCineCaptureComponent2D` |

### 使用示例（蓝图描述）

1. 在 Actor 上添加一个 `UCineCameraComponent`（必须）
2. 作为该 CineCameraComponent 的子组件，添加 `UCineCaptureComponent2D`
3. 设置一个 `TextureRenderTarget2D` 作为捕获目标
4. 调整 `RenderTargetHighestDimension` 控制输出分辨率（例如设为 1920 则根据宽高比自动计算另一维度）
5. 如需色彩管理，在 `OCIOConfiguration` 中配置 OCIO 配置文件和变换
6. 组件会在 Tick 时自动捕获 Cine Camera 的渲染结果到 Render Target

> **重要**：`UCineCaptureComponent2D` 必须挂载在 `UCineCameraComponent` 或其子类的下面，否则会验证失败。

## C++ 用法

### 头文件引入

```cpp
#include "CineCameraSceneCaptureComponent.h"
```

### 基本用法

创建一个挂载在 CineCameraComponent 下的捕获组件，并配置渲染目标：

```cpp
// 假设 Actor 上已有 UCineCameraComponent* CineCameraComp

// 创建 CineCaptureComponent2D 作为 CineCameraComponent 的子组件
UCineCaptureComponent2D* CaptureComp = NewObject<UCineCaptureComponent2D>(CineCameraComp);
CaptureComp->SetupAttachment(CineCameraComp);
CaptureComp->RegisterComponent();

// 配置渲染目标
UTextureRenderTarget2D* RenderTarget = NewObject<UTextureRenderTarget2D>();
RenderTarget->InitAutoFormat(1920, 1080);
CaptureComp->TextureTarget = RenderTarget;

// 设置最大边长为 1920，组件会根据 CineCamera 的宽高比自动调整实际分辨率
CaptureComp->RenderTargetHighestDimension = 1920;
```

### 进阶用法

启用 OpenColorIO 色彩变换和材质用户标志覆盖：

```cpp
UCineCaptureComponent2D* CaptureComp = ...;

// 启用 UserFlags 覆盖
CaptureComp->bOverrideUserFlags = true;
CaptureComp->UserFlags = 0x01; // 自定义标志位，在材质中可通过 TestPostVolumeUserFlag 读取

// 配置 OpenColorIO
FOpenColorIODisplayConfiguration OCIOConfig;
OCIOConfig.ConfigurationSource = LoadObject<UOpenColorIOConfiguration>(nullptr, TEXT("/Path/To/Your/OCIOConfig"));
OCIOConfig.ColorSpace = TEXT("scene_linear");
OCIOConfig.Display = TEXT("sRGB");
OCIOConfig.View = TEXT("Film");
CaptureComp->OCIOConfiguration = OCIOConfig;

// 如果捕获结果与 Cine Camera 视口差异较大，可关闭优化路径
CaptureComp->bFollowSceneCaptureRenderPath = false;
```

## Demo 示例

以下是一个完整的 Actor 示例，创建一个自动将 Cine Camera 画面捕获到 Render Target 的 Actor：

```cpp
// CineCameraCaptureActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CineCameraComponent.h"
#include "CineCameraSceneCaptureComponent.h"
#include "Engine/TextureRenderTarget2D.h"
#include "CineCameraCaptureActor.generated.h"

UCLASS()
class ACineCameraCaptureActor : public AActor
{
    GENERATED_BODY()

public:
    ACineCameraCaptureActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UCineCameraComponent* CineCamera;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UCineCaptureComponent2D* CineCapture;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Capture")
    int32 CaptureResolution = 1920;

    UPROPERTY(BlueprintReadOnly, Category = "Capture")
    UTextureRenderTarget2D* RenderTarget;
};
```

```cpp
// CineCameraCaptureActor.cpp
#include "CineCameraCaptureActor.h"

ACineCameraCaptureActor::ACineCameraCaptureActor()
{
    // 创建 Cine Camera Component
    CineCamera = CreateDefaultSubobject<UCineCameraComponent>(TEXT("CineCamera"));
    RootComponent = CineCamera;

    // 创建 Cine Capture Component 作为 Cine Camera 的子组件
    CineCapture = CreateDefaultSubobject<UCineCaptureComponent2D>(TEXT("CineCapture"));
    CineCapture->SetupAttachment(CineCamera);
    CineCapture->RenderTargetHighestDimension = CaptureResolution;
    CineCapture->bFollowSceneCaptureRenderPath = true;

    // 创建渲染目标
    RenderTarget = CreateDefaultSubobject<UTextureRenderTarget2D>(TEXT("RenderTarget"));
    RenderTarget->InitAutoFormat(1920, 1080);
    CineCapture->TextureTarget = RenderTarget;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenColorIO` | 色彩管理支持，提供 `FOpenColorIODisplayConfiguration` 结构体和 OCIO 变换功能 |

> **插件依赖**：本插件通过 `.uplugin` 声明了对 `OpenColorIO` 插件的启用依赖，无需在 Build.cs 中额外配置。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复 printf 格式说明符错误 |
| 2025-03-31 | `a492f271` | Fix missing virtual destructor after the base interface class had its own removed | 修复基类移除虚析构函数后缺失的虚析构函数 |
| 2025-02-27 | `3385f1fa` | First Person: Added support for first person rendering in scene capture 2D components. | 新增第一人称渲染在场景捕获组件中的支持 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 替换 Engine 目录下的 `IsValid(this)` 调用 |

### 维护评价

- **状态**：实验性插件（`IsExperimentalVersion=true`），默认未启用
- **活跃度**：持续有维护更新，2026 年仍有编译警告修复，说明引擎内部在保持其可编译性
- **功能更新**：2025-02-27 的第一人称渲染支持是一次有意义的功能增强
- **风险提示**：
  - 作为实验性插件，API 可能在引擎版本间发生变化
  - 仅有 4 个源文件，功能范围较小，属于专用工具而非通用解决方案
  - 自 2023 年创建以来从未正式移除实验性标记，可能长期保持实验状态
- **推荐程度**：如果你的虚拟制片工作流需要将 Cine Camera 输出到 Render Target，且愿意承担实验性 API 变化的风险，可以使用。否则建议关注其后续发展。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CineCameraSceneCapture)
- [OpenColorIO 插件文档](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/OpenColorIO)（依赖插件）