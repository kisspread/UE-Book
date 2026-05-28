# Panoramic Capture

> A plugin to capture a sequence of panoramic images in monoscopic or stereoscopic (top/bottom).

| 属性 | 值 |
|---|---|
| 中文名 | 全景捕获 |
| 分类 | Movie Capture |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `PanoramicCapture` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2019-06-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PanoramicCapture) | |

## 用途

本插件的核心功能是生成可供 VR 播放的立体全景媒体内容（如视频或图像序列）。它通过控制台命令或蓝图接口触发，自动在虚拟场景中按指定角度（水平/垂直）旋转摄像机，捕获多个视角下的渲染结果，最终拼接成一张符合等距柱状投影（Equirectangular Projection）格式的全景图像。主要解决在 Unreal Engine 内直接生成高质量、可用于 VR 头显观看的立体（左右眼）或单目光景内容的问题，省去了通过外部工具进行后期合成的步骤。

## 使用场景

-   **VR 内容预览与制作**：你在开发 VR 应用或游戏，需要快速生成一段立体的 360 度视频用于预览或展示，而不希望搭建复杂的离线渲染流程。
-   **全景媒体资产生成**：你需要为 VR 视频播放器、虚拟展厅或游戏内的全景图查看器创建素材。
-   **场景快速记录**：你需要以全景视角记录游戏场景的某个特定时刻或序列，用于存档或分析。

## 蓝图用法

插件主要通过 `AStereoCapturePawn` 提供蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UpdateStereoAtlas` | 异步执行一次全景捕获，完成后将左右眼全景图数据更新到对应的纹理属性中。 | `AStereoCapturePawn` |
| `LeftEyeAtlas` (属性) | 捕获完成后，存储左眼（或单目）全景图的 `UTexture2D` 对象。 | `AStereoCapturePawn` |
| `RightEyeAtlas` (属性) | 捕获完成后，存储右眼全景图的 `UTexture2D` 对象（立体模式下）。 | `AStereoCapturePawn` |

### 使用示例（蓝图描述）

1.  **准备工作**：
    *   在场景中放置一个 `AStereoCapturePawn` （或其子类）。
    *   通过控制台变量（例如 `SP.PanoramicQuality`）设置捕获质量、输出目录等参数。

2.  **触发捕获**：
    *   在任何蓝图中，获取到 `AStereoCapturePawn` 的引用。
    *   调用其 `UpdateStereoAtlas` 节点。
    *   该节点是 Latent 的，会输出一个 `Exec` 引脚（完成后）和一个 `StereoCaptureDone` 执行引脚。

3.  **获取结果**：
    *   当 `UpdateStereoAtlas` 完成（`Completed` 引脚触发）后，读取该 Pawn 的 `LeftEyeAtlas` 和 `RightEyeAtlas` 属性。
    *   这两个属性是 `UTexture2D*`，你可以将它们用作材质参数、渲染到 UI 控件或进行后处理。

## C++ 用法

插件的核心操作通过控制台变量和命令控制。没有直接暴露高级 C++ API，但可以通过控制台系统集成。

### 头文件引入

```cpp
#include "StereoPanoramaManager.h"
```

### 基本用法

通过控制台变量控制捕获参数，并通过控制台命令触发。

```cpp
// 获取管理器单例（假设已初始化）
TSharedPtr<FStereoPanoramaManager> Manager = FStereoPanoramaModule::Get();
if (Manager.IsValid())
{
    // 例如，通过控制台变量设置输出目录
    if (IConsoleVariable* CVar = IConsoleManager::Get().FindConsoleVariable(TEXT("SP.OutputDir")))
    {
        CVar->Set(TEXT("/Game/MyPanoramas/"));
    }
    
    // 在特定时机执行一次单帧全景截图
    // 需要一个 UWorld* 参数
    Manager->PanoramicScreenshot({}, GetWorld());
}
```
**来源文件**: `Private/StereoPanoramaManager.h`

### 进阶用法

使用带回调的版本来精确控制捕获范围并处理完成事件。

```cpp
#include "StereoPanoramaManager.h"
// ... 其他头文件

void UMyCaptureUtility::StartTimelapseCapture()
{
    TSharedPtr<FStereoPanoramaManager> Manager = FStereoPanoramaModule::Get();
    if (Manager.IsValid())
    {
        // 定义一个委托来处理捕获完成
        FStereoCaptureDoneDelegate CaptureDoneDelegate;
        CaptureDoneDelegate.BindLambda([this](const TArray<FLinearColor>& LeftEyeData, const TArray<FLinearColor>& RightEyeData)
        {
            UE_LOG(LogTemp, Log, TEXT("Panoramic capture finished! Left eye data size: %d"), LeftEyeData.Num());
            // 这里可以进一步处理图像数据
        });

        // 从第10帧捕获到第20帧
        Manager->PanoramicScreenshot(10, 20, CaptureDoneDelegate, GetWorld());
    }
}
```
**来源文件**: `Private/SceneCapturer.h`

## Demo 示例

一个简单的 C++ 类，用于设置并触发全景捕获。

```cpp
// MyPanoramicRecorder.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "StereoPanoramaManager.h" // 依赖插件模块
#include "MyPanoramicRecorder.generated.h"

UCLASS()
class UMyPanoramicRecorder : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Panoramic")
    void RecordPanorama(UWorld* InWorld, int32 StartFrame, int32 EndFrame);

private:
    FStereoCaptureDoneDelegate OnCaptureDone;
    void HandleCaptureComplete(const TArray<FLinearColor>& LeftEyeData, const TArray<FLinearColor>& RightEyeData);
};

// MyPanoramicRecorder.cpp
#include "MyPanoramicRecorder.h"

void UMyPanoramicRecorder::RecordPanorama(UWorld* InWorld, int32 StartFrame, int32 EndFrame)
{
    TSharedPtr<FStereoPanoramaManager> Manager = FStereoPanoramaModule::Get();
    if (Manager.IsValid() && InWorld)
    {
        // 绑定完成回调
        OnCaptureDone.BindUObject(this, &UMyPanoramicRecorder::HandleCaptureComplete);
        
        // 开始捕获
        Manager->PanoramicScreenshot(StartFrame, EndFrame, OnCaptureDone, InWorld);
        UE_LOG(LogTemp, Log, TEXT("Panoramic capture initiated for frames %d to %d."), StartFrame, EndFrame);
    }
}

void UMyPanoramicRecorder::HandleCaptureComplete(const TArray<FLinearColor>& LeftEyeData, const TArray<FLinearColor>& RightEyeData)
{
    UE_LOG(LogTemp, Warning, TEXT("Capture complete. Left Eye Pixels: %d, Right Eye Pixels: %d"), LeftEyeData.Num(), RightEyeData.Num());
    // 可以在这里保存数据到文件，或进行图像后处理
}
```

## 模块依赖

从 `Build.cs` 分析，该插件是编辑器功能插件。

| 模块 | 用途 |
|---|---|
| `EditorFramework` | 插件依赖的编辑器框架基础。 |
| `UnrealEd` | 提供场景捕获、编辑器交互等编辑器功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|--- |--- |
| 2025-12-01 | `28e633a1` | Remove Mip Bias Fade system | 移除了 Mip 偏移淡入系统，清理了相关代码。 |
| 2025-08-08 | `40e2c8da` | Passing RHI Command Lists through to MoviePlayer and TickableObjectRenderThread functions. | 将 RHI 命令列表传递给 MoviePlayer 和 TickableObject 线程函数，改进了底层渲染调用。 |
| 2024-10-30 | `ab20a6a9` | [Engine] | 引擎级的通用更新或编译修复。 |
| 2023-06-21 | `06c082c9` | PanoramicCapture: Fix e.g. C: not recognized as a valid path. | 修复了输出路径中类似 “C:” 的格式不被识别为有效路径的 bug。 |
| 2023-04-20 | `f68fa87d` | PanoramicCapture: Fix conflict with nDisplay since CDO constructor forces display settings unnecessa | 修复了与 nDisplay 插件的冲突，原因是 CDO 构造函数强制设置了不必要的显示设置。 |

### 维护评价

-   **状态**：维护中。插件创建于 2019 年，版本为 Alpha。尽管默认未启用且标记为实验性，但直到 2025 年底仍有实质性代码更新（如移除子系统、改进底层渲染），表明 Epic 或维护者仍在修复和优化。
-   **活跃度**：更新频率不算高，但近年来（2023-2025）的提交主要集中在修复路径、兼容性问题和底层渲染优化，表明其仍被关注并用于某些特定场景。
-   **已知限制**：插件为 `UncookedOnly` 类型，仅在编辑器和开发环境中可用，打包后无法运行。主要面向 Windows 64 位平台。
-   **推荐**：如果你的需求是在 **编辑器内** 生成 **VR 全景媒体素材**，并且不介意其实验性状态和相对复杂的控制台变量配置，那么此插件是一个可用的官方解决方案。对于生产环境，建议先进行充分测试。如果仅需单次截图或简单录制，引擎内置的高分辨率截图或序列器可能是更简单的选择。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PanoramicCapture)
-   官方文档（无）