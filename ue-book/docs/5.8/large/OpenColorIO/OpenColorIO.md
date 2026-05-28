# OpenColorIO (OCIO)

> Provides support for OpenColorIO

| 属性 | 值 |
|---|---|
| 中文名 | 颜色空间转换 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `OpenColorIO` (Runtime), `OpenColorIOEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/OpenColorIO) | |

## 用途

该插件的核心是将电影和视觉效果行业标准的 OpenColorIO (OCIO) 库集成到虚幻引擎中。它主要解决**跨应用程序、跨设备的颜色一致性**问题。通过在渲染管线的最后阶段（后处理）应用基于 OCIO 配置文件的颜色空间转换，确保在虚幻引擎中看到的颜色与在 Adobe Photoshop、DaVinci Resolve、Nuke 等专业软件中制作的颜色完全一致。

它不仅仅是简单的色调映射，而是能够定义和执行精确的、可复现的颜色转换流程（例如：从场景工作空间 ACEScg 转换到特定监视器的输出显示空间 Rec.709），这对于虚拟制片、实时合成和最终输出至关重要。

## 使用场景

-   **虚拟制片 (Virtual Production)**：在现场 LED 墙或监视器上进行实时拍摄时，确保摄影机捕捉到的画面与后续在调色软件（如 DaVinci Resolve）中处理的画面颜色一致。
-   **后期制作流程**：在虚幻引擎中渲染的序列帧需要与 Nuke、After Effects 等合成软件无缝对接，保证颜色信息无损传递。
-   **团队协作与交付**：为整个项目或部门建立一个统一的 OCIO 配置文件，确保美术、灯光、合成等不同环节的人员在各自软件中看到的“电影级”颜色效果完全相同。
-   **资产检查与审核**：为引擎编辑器的视口应用特定的显示变换，以模拟最终输出设备的颜色表现。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create OpenColorIO Display Extension` | 创建一个 OCIO 显示扩展包装器，用于在蓝图中控制视口的 OCIO 效果。 | `UOpenColorIODisplayExtensionWrapper` |
| `Create In-Game OpenColorIO Display Extension` | 创建一个专门用于运行时（游戏）的 OCIO 显示扩展。 | `UOpenColorIODisplayExtensionWrapper` |
| `Set OpenColorIO Configuration` | 为显示扩展设置具体的颜色转换配置。 | `UOpenColorIODisplayExtensionWrapper` |
| `Set Scene Extension IsActive Functions` | 设置激活函数，决定此 OCIO 效果在何种上下文下生效（例如：特定的玩家视口、过场动画序列）。 | `UOpenColorIODisplayExtensionWrapper` |
| `Apply Color Space Transform` | 核心节点。将指定的 OCIO 颜色转换直接应用到一张输入纹理，并输出到渲染目标。 | `UOpenColorIOBlueprintLibrary` |
| `Get/Set Configuration File` | 读取或设置 `UOpenColorIOConfiguration` 资产所引用的 `.ocio` 配置文件路径。 | `UOpenColorIOConfiguration` |

### 使用示例（蓝图描述）

**示例：为特定视口应用电影调色**
1.  在蓝图中，创建一个 `UOpenColorIOConfiguration` 资产的引用变量。
2.  使用 “**Create In-Game OpenColorIO Display Extension**” 节点，传入一个 `FOpenColorIODisplayConfiguration` 结构体。该结构体包含了 OCIO 配置资产和具体的转换设置（如：源颜色空间为 “ACES - ACEScg”，目标显示为 “sRGB”）。
3.  将创建出的 `UOpenColorIODisplayExtensionWrapper` 对象保存为变量。
4.  （可选）使用 “**Set Scene Extension IsActive Functions**” 节点，传入一个自定义的委托，控制该效果仅在某个特定的 `UViewportClient` 或游戏模式下激活。

**示例：实时转换纹理**
1.  使用 “**Apply Color Space Transform**” 节点。
2.  将需要转换的源 `UTexture`（例如一张场景截图）连接到 `Input Texture` 引脚。
3.  设置好 `Conversion Settings`，指定 `UOpenColorIOConfiguration` 资产和源/目标颜色空间。
4.  将一个 `UTextureRenderTarget2D` 连接到 `Output Render Target` 引脚。
5.  执行该蓝图节点，即可在渲染目标上看到经过颜色空间转换后的图像。

## C++ 用法

### 头文件引入

```cpp
#include “OpenColorIOBlueprintLibrary.h” // 用于静态工具函数
#include “OpenColorIOConfiguration.h”    // 用于 OCIO 配置资产
#include “OpenColorIORendering.h”         // 用于渲染相关的功能
```

### 基本用法

从 `OpenColorIOBlueprintLibrary.h` 提取的用法，用于在 C++ 中执行颜色转换。
```cpp
// 假设您已经拥有一个有效的 UOpenColorIOConfiguration 指针 ‘OcioConfigAsset’。
// 以及一个源纹理 ‘SourceTexture’ 和一个输出渲染目标 ‘OutputRT’。

FOpenColorIOColorConversionSettings ConversionSettings;
ConversionSettings.ConfigurationSource = OcioConfigAsset;
// 您需要从 OcioConfigAsset 中找到有效的颜色空间并设置
// ConversionSettings.SourceColorSpace = ...;
// ConversionSettings.DestinationColorSpace = ...;

// 调用蓝图库函数（本质上是静态函数）
UOpenColorIOBlueprintLibrary::ApplyColorSpaceTransform(
    GetWorld(),
    ConversionSettings,
    SourceTexture,
    OutputRT
);
```
（来源：`Public/OpenColorIOBlueprintLibrary.h`）

### 进阶用法

在渲染线程上更精细地控制 OCIO 的应用，适用于自定义后处理管线。
```cpp
#include “OpenColorIORendering.h”
#include “SceneRendering.h”

// 1. 在游戏线程上获取渲染资源（线程安全地拷贝数据）
FOpenColorIORenderPassResources PassResources = FOpenColorIORendering::GetRenderPassResources(
    ConversionSettings,
    FeatureLevel
);

// 2. 在渲染线程的后处理阶段，使用 Render Dependency Graph (RDG) 添加 OCIO 通道
FRDGBuilder& GraphBuilder = ...; // 从后处理上下文获取
FScreenPassViewInfo ViewInfo = ...; // 当前视图信息
FScreenPassTexture InputTexture = ...; // 上一个后处理通道的输出
FScreenPassRenderTarget OutputTarget = ...; // 最终输出目标

FOpenColorIORendering::AddPass_RenderThread(
    GraphBuilder,
    ViewInfo,
    FeatureLevel,
    InputTexture,
    OutputTarget,
    PassResources,
    InGamma, // 显示 Gamma 值
    EOpenColorIOTransformAlpha::None // 是否处理 Alpha 通道
);
```
（来源：`Public/OpenColorIORendering.h`）

## Demo 示例

一个完整的、可编译的最小示例，展示如何在 C++ 中创建一个简单的 OCIO 配置并执行图像转换。

### .h 文件
```cpp
// MyOcioTestActor.h
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “OpenColorIOConfiguration.h”
#include “MyOcioTestActor.generated.h”

UCLASS()
class AMyOcioTestActor : public AActor
{
    GENERATED_BODY()

public:
    AMyOcioTestActor();

protected:
    virtual void BeginPlay() override;

    // 在编辑器中指定 OCIO 配置资产
    UPROPERTY(EditAnywhere, Category = “OCIO”)
    TObjectPtr<UOpenColorIOConfiguration> OcioConfigAsset;

    // 输入图像（在编辑器中指定）
    UPROPERTY(EditAnywhere, Category = “OCIO”)
    TObjectPtr<UTexture2D> InputImage;

    // 输出渲染目标（在BeginPlay中创建或编辑器指定）
    UPROPERTY(VisibleAnywhere, Category = “OCIO”)
    TObjectPtr<UTextureRenderTarget2D> OutputRT;

    // 执行转换
    UFUNCTION(BlueprintCallable, Category = “OCIO”)
    void ExecuteColorTransform();

private:
    FOpenColorIOColorConversionSettings CachedSettings;
};
```

### .cpp 文件
```cpp
// MyOcioTestActor.cpp
#include “MyOcioTestActor.h”
#include “OpenColorIOBlueprintLibrary.h”

AMyOcioTestActor::AMyOcioTestActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyOcioTestActor::BeginPlay()
{
    Super::BeginPlay();

    if (OcioConfigAsset && InputImage)
    {
        // 确保配置已加载
        OcioConfigAsset->ReloadExistingColorspaces();

        // 初始化转换设置 (这里需要您知道配置文件中具体存在的颜色空间名称)
        CachedSettings.ConfigurationSource = OcioConfigAsset;
        // 示例： CachedSettings.SourceColorSpace = FOpenColorIOColorSpace(“lin_srgb”, ...);
        // CachedSettings.DestinationColorSpace = FOpenColorIOColorSpace(“srgb_texture”, ...);

        // 创建输出 RT（如果未在编辑器中设置）
        if (!OutputRT)
        {
            OutputRT = NewObject<UTextureRenderTarget2D>(this);
            OutputRT->InitAutoFormat(InputImage->GetSizeX(), InputImage->GetSizeY());
            OutputRT->UpdateResourceImmediate(true);
        }

        // 执行转换
        ExecuteColorTransform();
    }
}

void AMyOcioTestActor::ExecuteColorTransform()
{
    if (CachedSettings.IsValid() && InputImage && OutputRT)
    {
        bool bSuccess = UOpenColorIOBlueprintLibrary::ApplyColorSpaceTransform(
            GetWorld(),
            CachedSettings,
            InputImage,
            OutputRT
        );

        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT(“OCIO color transform command queued.”));
            // 输出纹理 OutputRT 现在包含了转换后的图像数据。
            // 可以将其应用到材质或进行进一步处理。
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT(“OCIO settings or textures are invalid.”));
    }
}
```

## 模块依赖

从 `Build.cs` 文件分析，除了标准的 `Core`, `CoreUObject`, `Engine`, `RHI`, `RenderCore` 等，使用此插件的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `DerivedDataCache` | 用于缓存编译后的着色器和生成的 LUT 纹理，以提高性能和加载速度。 |
| `OpenColorIO` | **使用者必须依赖**此运行时模块以使用其核心 API（如 `UOpenColorIOConfiguration`, `UOpenColorIOColorTransform`）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片：调整了资产分类，属于更大范围的VP资产整理工作。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，属于代码规范化更新。 |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored | 着色器系统重构：优化了着色器编译任务的状态管理，移除了冗余标志。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 为即将到来的头文件清理做准备，预先添加了必要的包含。 |
| 2026-03-13 | `ac816610` | OCIO: Fix for linear floating point (SDR) backbuffer. | 修复了针对线性浮点（SDR）后缓冲区的 OCIO 转换问题。 |

### 维护评价

OpenColorIO 插件自 2019 年创建以来，至今仍在**活跃维护**。
- **近期活动**：最近的提交（截至2026年5月）主要涉及**着色器系统的重构、代码规范化和特定功能修复**，这表明 Epic 官方仍在持续投入开发，优化其内部架构和稳定性。
- **实验性状态**：该插件仍被标记为 **Beta 版本** (`IsBetaVersion: true`)，且默认未启用 (`EnabledByDefault: false`)。这意味着它的 API 可能会在未来版本中发生变化，使用者需要自行承担可能的重构风险。
- **推荐使用**：尽管是实验性插件，但对于**虚拟制片和专业的颜色管理工作流**来说，它是目前虚幻引擎内**唯一且必要**的解决方案。对于有严格颜色精度要求的项目，强烈建议使用，但需密切关注后续引擎版本的更新日志，并做好跟随 API 变化进行调整的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/OpenColorIO)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/OpenColorIO/Tests)