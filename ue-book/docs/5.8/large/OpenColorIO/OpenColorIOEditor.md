# OpenColorIO (OCIO)

> Provides support for OpenColorIO

| 属性 | 值 |
|---|---|
| 中文名 | 色彩空间管理 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `OpenColorIO` (Runtime), `OpenColorIOEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/OpenColorIO) | |

## 用途

该插件将 **OpenColorIO** (OCIO) 库集成到虚幻引擎中。其主要目的是为引擎提供一套标准化的、可配置的色彩管理系统，用于精确地进行色彩空间转换。它解决了在不同软件（如 DCC 工具、合成软件）和工作流程（如影视、虚拟制片）之间保持色彩一致性的问题，确保资产在不同阶段（创建、引擎内预览、最终合成）拥有统一且准确的色彩表现。

## 使用场景

-   **虚拟制片 (Virtual Production)**：在 LED 墙或绿幕拍摄时，使用该插件确保摄像机拍摄的画面色彩与虚幻引擎中渲染的背景场景色彩空间一致，实现无缝融合。
-   **影视预览与合成**：在引擎内为资产（模型、贴图）应用正确的色彩空间转换，在视口或最终输出时获得符合影视行业标准（如 ACES）的色彩结果。
-   **资产颜色校正**：在蓝图或 C++ 中，对纹理或颜色值进行实时的色彩空间转换，用于后期处理效果或动态材质调整。

## 蓝图用法

插件在编辑器模块中提供了一个蓝图函数库，用于在编辑器环境下进行操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Active Viewport Configuration` | 设置活动编辑器视口的显示配置（色彩变换）。 | `UOpenColorIOEditorBlueprintLibrary` |
| `Apply Color Space Transform To Color` | 对一个颜色值应用色彩空间转换。 | `UOpenColorIOEditorBlueprintLibrary` |
| `Apply Color Space Transform To Texture` | 对一个纹理资产应用色彩空间转换。 | `UOpenColorIOEditorBlueprintLibrary` |
| `Apply Color Space Transform To Texture Compressed` | 对一个纹理资产应用色彩空间转换，并指定目标压缩格式。 | `UOpenColorIOEditorBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **创建配置资产**：在内容浏览器中右键，选择 “Miscellaneous” -> “OpenColorIO Configuration” 创建一个 `UOpenColorIOConfiguration` 资产。在该资产的详情面板中，配置 OCIO 配置文件（.ocio）和颜色空间映射。
2.  **设置视口显示**：创建一个蓝图，在事件图表中，获取一个 `FOpenColorIODisplayConfiguration` 结构体，设置其 `ConfigurationObject` 为你创建的 OCIO 配置资产，并指定源与目标颜色空间。然后，调用 `Set Active Viewport Configuration` 节点，并将此结构体传入，即可改变当前活动编辑器视口的色彩显示。
3.  **转换颜色/纹理**：使用 `Apply Color Space Transform To Color` 节点，传入一个 `FOpenColorIOColorConversionSettings` 结构体（同样需要指定 OCIO 配置和转换路径）以及一个颜色，节点会输出转换后的颜色。转换纹理节点用法类似，直接传入纹理对象进行原地修改。

## C++ 用法

在 C++ 中，该插件主要用于运行时色彩处理和编辑器功能扩展。

### 头文件引入

```cpp
// 引入运行时模块头文件，用于核心的色彩转换功能
#include "OpenColorIO.h"

// 引入编辑器模块头文件，用于编辑器内的工具和蓝图函数库
#include "OpenColorIOEditor.h"
#include "OpenColorIOEditorBlueprintLibrary.h"
```

### 基本用法

以下示例展示了如何在 C++ 中应用颜色空间转换（基于 `UOpenColorIOEditorBlueprintLibrary` 的 C++ 等效调用）：

```cpp
// 假设已经创建并加载了一个 UOpenColorIOConfiguration 资产
UOpenColorIOConfiguration* OCIOConfig = LoadObject<UOpenColorIOConfiguration>(nullptr, TEXT("/Game/MyOCIOConfig"));

if (OCIOConfig)
{
    // 设置转换参数
    FOpenColorIOColorConversionSettings ConversionSettings;
    ConversionSettings.ConfigurationSource = OCIOConfig;
    ConversionSettings.SourceColorSpace.SetColorSpace(LOCTEXT("sRGB", "sRGB"), TEXT("sRGB"));
    ConversionSettings.DestinationColorSpace.SetColorSpace(LOCTEXT("Linear sRGB", "Linear sRGB"), TEXT("Linear sRGB"));

    // 1. 转换一个颜色值
    FLinearColor InputColor(1.0f, 0.5f, 0.0f, 1.0f);
    FLinearColor OutputColor;
    bool bSuccess = UOpenColorIOEditorBlueprintLibrary::ApplyColorSpaceTransformToColor(ConversionSettings, InputColor, OutputColor);

    // 2. 转换一个纹理 (修改资产，请谨慎使用)
    UTexture* TextureToConvert = LoadObject<UTexture>(nullptr, TEXT("/Game/MyTexture"));
    if (TextureToConvert)
    {
        bSuccess = UOpenColorIOEditorBlueprintLibrary::ApplyColorSpaceTransformToTexture(ConversionSettings, TextureToConvert);
    }
}
```

### 进阶用法

对于视口配置，可以参考 `FDisplayClusterViewport_OCIO` 类的实现或通过 `FOpenColorIOEditorModule` 的 `SetActiveViewportConfiguration` 方法进行设置。更复杂的用法通常涉及监听编辑器事件（如 `OnDisplayConfigurationChanged`）并联动更新场景中的相关组件。

## Demo 示例

下面是一个最小化的 C++ 示例，演示如何创建一个简单的 OCIO 配置并应用到颜色。

```cpp
// OCIOBasicDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OCIOBasicDemo.generated.h"

UCLASS()
class AOCIOBasicDemo : public AActor
{
    GENERATED_BODY()

public:
    AOCIOBasicDemo();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "OCIO Demo")
    FOpenColorIOColorConversionSettings ConversionSettings;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "OCIO Demo")
    void DemoConvertColor();
};

// OCIOBasicDemo.cpp
#include "OCIOBasicDemo.h"
#include "OpenColorIOBlueprintLibrary.h"
#include "OpenColorIOConfiguration.h"

AOCIOBasicDemo::AOCIOBasicDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AOCIOBasicDemo::BeginPlay()
{
    Super::BeginPlay();
    // 可以在编辑器属性面板中设置 ConversionSettings.ConfigurationSource
}

void AOCIOBasicDemo::DemoConvertColor()
{
    FLinearColor TestColor(1.0f, 0.8f, 0.6f, 1.0f);
    FLinearColor ConvertedColor;

    // 注意：运行时转换通常使用 `UOpenColorIOBlueprintLibrary`，编辑器内使用 `UOpenColorIOEditorBlueprintLibrary`
    // 此处假设在编辑器环境或使用编辑器蓝图库
    if (UOpenColorIOEditorBlueprintLibrary::ApplyColorSpaceTransformToColor(ConversionSettings, TestColor, ConvertedColor))
    {
        UE_LOG(LogTemp, Log, TEXT("Original Color: %s"), *TestColor.ToString());
        UE_LOG(LogTemp, Log, TEXT("Converted Color: %s"), *ConvertedColor.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Color conversion failed. Check OCIO configuration."));
    }
}
```

## 模块依赖

要使用此插件，你的模块通常需要链接以下模块：

| 模块 | 用途 |
|---|---|
| `OpenColorIO` | 引用核心的运行时色彩转换功能。 |
| `OpenColorIOEditor` | 在编辑器模块中使用编辑器特定功能（如蓝图库、自定义界面）。 |
| `DerivedDataCache` | OCIO 着色器编译依赖于 DDC 系统。 |

*对于包含 `OpenColorIOEditor` 模块的依赖，请确保你的模块构建类型为 `Editor`。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the... | 将虚拟制片资产移至新的资产分类，可能影响资产查找和组织方式。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 更新日志宏，使用新的格式化函数。 |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored... | 重构了着色器编译作业结构，优化了编译流程的状态管理。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 为即将到来的头文件清理工作提前添加必要的头文件包含。 |
| 2026-03-13 | `ac816610` | OCIO: Fix for linear floating point (SDR) backbuffer. | 修复了关于线性浮点（SDR）后缓冲的 OCIO 显示问题。 |

### 维护评价

该插件仍在**积极维护**中。尽管创建于 2019 年，但在 2026 年仍有功能性更新（如虚拟制片集成优化）和底层重构。最近的提交记录表明 Epic 持续在改进其与引擎其他部分（如着色器编译、虚拟制片系统）的集成。

**需要注意**：该插件在 `.uplugin` 中标记为 `IsBetaVersion: true`，且默认未启用 (`EnabledByDefault: false`)。这意味着它仍被视为实验性功能，其 API 和功能在未来版本中可能发生不兼容的变更。**不建议在需要高度稳定性的生产项目中过度依赖**，但非常适合用于研究、测试和虚拟制片工作流探索。

**推荐使用**：如果你的项目涉及虚拟制片或需要严格遵循行业色彩标准（如 ACES），并且可以接受实验性功能的风险，那么该插件是必选的。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/OpenColorIO)
-   [官方文档]() （.uplugin 中的 DocsURL 为空）
-   [OpenColorIO 官方网站](https://opencolorio.org/)