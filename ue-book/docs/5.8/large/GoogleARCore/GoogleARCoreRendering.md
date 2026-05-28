# Google ARCore

> Support for Google's AR platform.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | ARCore 渲染 |
| 分类 | Augmented Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资源） |
| 模块 | `GoogleARCoreBase` (Runtime), `GoogleARCoreRendering` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-28 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/Google/GoogleARCore) | |

## 用途

该插件并非提供完整的 AR 功能，而是为 UE 提供与 **Google ARCore 平台**对接的**渲染支持**。其核心职责是将 ARCore 设备提供的摄像头原始画面（通常以 YCbCr 格式存储）正确、高效地渲染为 UE 的游戏场景背景，并支持深度遮挡效果，使虚拟物体能被现实世界的物体正确遮挡。

简单来说，它是连接 ARCore 设备摄像头和 UE 渲染管线的桥梁，确保 AR 画面在 Android 设备上看起来正确。

## 使用场景

-   你正在为 **Android** 设备开发增强现实应用，并使用 **Google ARCore** 作为底层 AR 平台。
-   你需要将 ARCore 设备的摄像头画面作为游戏世界的背景（称为“穿透式摄像头”）。
-   你需要利用 ARCore 提供的深度信息，实现虚拟物体被真实物体遮挡的“遮挡”效果。
-   你正在使用 UE 的 AR 框架，并希望获得针对 Google ARCore 优化的渲染路径。

## 蓝图用法

此插件主要提供底层渲染支持，未直接暴露复杂的蓝图节点。其核心逻辑由引擎的 AR 系统在内部调用。开发者通常通过 UE 通用的 AR 蓝图接口（如 `Get AR Session Status`、`AR Trace Result` 等）与 AR 功能交互，而此插件负责在背后处理 Android 平台的摄像头画面渲染。

### 核心节点（引擎内部使用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UpdateCameraTextures` | 更新用于渲染的摄像头纹理（常规和深度） | `FGoogleARCorePassthroughCameraRenderer` |
| `RenderVideoOverlay_RenderThread` | 在渲染线程上执行摄像头画面的覆盖绘制 | `FGoogleARCorePassthroughCameraRenderer` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接调用此插件的类。典型用法是：
1.  创建一个 `ARSession Config` 资产，启用所需的功能（如遮挡）。
2.  使用 `Start AR Session` 节点启动 AR。
3.  引擎会自动使用此插件（如果已启用）来渲染摄像头背景。
4.  使用 `Line Trace` 节点进行 AR 射线检测，并放置虚拟物体。
5.  插件会确保放置的虚拟物体被真实世界物体正确遮挡。

## C++ 用法

此插件主要作为引擎内部模块，但可以进行深度定制或性能分析。

### 头文件引入

```cpp
#include "GoogleARCoreRenderingModule.h"
```

### 基本用法

直接使用渲染器类需要访问引擎内部 AR 系统，以下为示意性代码，展示其核心对象的生命周期。
（来源：`Public/GoogleARCorePassthroughCameraRenderer.h`）

```cpp
// 通常由引擎内部的 AR 系统创建和持有
FGoogleARCorePassthroughCameraRenderer* PassthroughRenderer = new FGoogleARCorePassthroughCameraRenderer();

// 在游戏线程中更新纹理数据
UTexture* CameraTexture = /* 从 ARCore Runtime 获取 */;
UTexture* DepthTexture = /* 从 ARCore Runtime 获取 */;
bool bEnableOcclusion = true;
PassthroughRenderer->UpdateCameraTextures(CameraTexture, DepthTexture, bEnableOcclusion);
```

### 进阶用法

在渲染线程中自定义渲染行为（需深入了解 UE 渲染管线）。
（来源：`Public/GoogleARCorePassthroughCameraRenderer.h`）

```cpp
// 假设在渲染线程回调中
void MyRenderCallback(FRHICommandListImmediate& RHICmdList, FSceneViewFamily& InViewFamily)
{
    if (PassthroughRenderer)
    {
        // 初始化渲染资源（如果需要）
        PassthroughRenderer->InitializeRenderer_RenderThread(InViewFamily);

        // 为每个视图执行渲染
        for (FSceneView* View : InViewFamily.Views)
        {
            PassthroughRenderer->RenderVideoOverlay_RenderThread(RHICmdList, *View);
        }
    }
}
```

## Demo 示例

一个最小的游戏模式示例，用于理解如何在代码层面与此插件交互。**注意：直接实例化渲染器类通常由引擎 AR 子系统管理，此示例仅为展示 API 用法。**

**MyARGameMode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "GoogleARCorePassthroughCameraRenderer.h"
#include "MyARGameMode.generated.h"

UCLASS()
class AMyARGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    AMyARGameMode();

    virtual void StartPlay() override;

private:
    // 实际项目中应由 ARSession 或其他 AR 组件持有
    TUniquePtr<FGoogleARCorePassthroughCameraRenderer> ARCoreRenderer;
};
```

**MyARGameMode.cpp**
```cpp
#include "MyARGameMode.h"
#include "ARBlueprintLibrary.h"

AMyARGameMode::AMyARGameMode()
{
    // 在构造函数中创建渲染器实例
    ARCoreRenderer = MakeUnique<FGoogleARCorePassthroughCameraRenderer>();
}

void AMyARGameMode::StartPlay()
{
    Super::StartPlay();

    // 模拟从 ARCore 获取纹理并更新（实际应由平台层调用）
    // UTexture* CameraTex = ...;
    // UTexture* DepthTex = ...;
    // ARCoreRenderer->UpdateCameraTextures(CameraTex, DepthTex, true);

    UE_LOG(LogTemp, Warning, TEXT("AR GameMode Started. Renderer created."));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GoogleARCoreBase` | 提供 ARCore 平台的基础抽象和接口，是渲染模块的数据来源。 |
| `RenderCore` | 提供底层渲染核心功能。 |
| `RHI` | 渲染硬件接口，用于创建和操作 GPU 资源。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了用于格式化函数的枚举可能导致输出乱码的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化说明符与参数位宽不匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 UE_LOG 迁移为新的 UE_LOGF 宏。 |
| 2026-04-08 | `86879cf0` | Fix unreachable code warnings | 修复了代码可达性警告。 |
| 2026-03-19 | `7662e97c` | Fix incorrect scene texture sampling uv in postprocess materials after TSR. This also caused incorre... | 修复了时序超分辨率后处理材质中场景纹理 UV 采样错误的问题。 |

### 维护评价

该插件创建于 **2019 年**，已存在 **7 年以上**。从近期提交记录看，主要改动集中于 **编译修复、代码规范迁移和底层渲染 Bug 修复**（如 UV 采样、格式化问题）。没有看到新功能的添加或架构的重大变更。

这表明该插件处于一种 **“维护模式”**：它仍在随引擎主线更新以保证兼容性，但开发重点已从 Google 转向 Epic 对 ARCore 的统一抽象层（如 `ARUtilities`）。插件本身功能稳定，但 **不推荐作为新 AR 项目的首选开发起点**，应优先使用 UE 更通用的 AR 蓝图 API。对于依赖此插件的现有项目，它依然可靠。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/Google/GoogleARCore)
-   [官方文档](https://developers.google.com/ar/)（来自 .uplugin）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/Google/GoogleARCore/Tests) （推测路径，需确认是否存在）