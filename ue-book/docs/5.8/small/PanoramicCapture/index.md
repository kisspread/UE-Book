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

这个插件用于从 UE 场景中捕获全景图像序列。它通过围绕相机位置按指定角度步进旋转，使用 `USceneCaptureComponent2D` 逐片（slice）拍摄场景，然后将这些片段拼接成球面投影的全景图。

**核心解决的问题**：UE 原生的截图功能只捕获普通透视图像，无法直接生成 VR/全景内容所需的 360° 球面投影图像。此插件自动化了这个复杂的多角度拼接流程，支持：
- **立体全景**（stereoscopic）：分别渲染左右眼视角，输出上下排列的立体全景图
- **单目全景**（monoscopic）：只渲染单眼视角
- **多渲染通道**：除了最终颜色，还可以输出世界法线、场景深度、粗糙度、金属度、基础颜色、环境遮蔽等 GBuffer 数据
- **动画序列**：连续捕获多帧，生成全景视频序列

由 Kite & Lightning（一家 VR 内容公司）最初开发。

## 使用场景

- 你需要为 VR 应用生成 360° 全景截图或预渲染视频
- 你需要从 UE 场景中导出多通道全景数据（法线、深度等），用于后期合成或 AI 训练
- 你需要在编辑器中快速预览场景在全景设备上的效果
- 你需要为全景视频平台（如 YouTube 360、Meta Quest）生成内容素材

**注意**：此插件仅支持 Win64 平台，且仅在未打包（UncookedOnly）状态下可用，即只能在编辑器中使用。

## 蓝图用法

### 核心类

插件暴露了一个蓝图可用的 Pawn 类 `AStereoCapturePawn`，用于在蓝图中发起立体全景捕获并读取结果。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UpdateStereoAtlas` | 触发立体全景捕获，完成后自动更新左右眼纹理（Latent 异步节点） | `AStereoCapturePawn` |
| `LeftEyeAtlas` | 只读属性，捕获完成后的左眼全景纹理（`UTexture2D*`） | `AStereoCapturePawn` |
| `RightEyeAtlas` | 只读属性，捕获完成后的右眼全景纹理（`UTexture2D*`） | `AStereoCapturePawn` |

### 使用示例（蓝图描述）

1. **创建 StereoCapturePawn**：在关卡中放置一个 `StereoCapturePawn`（或通过 SpawnActor 蓝图节点生成）
2. **触发全景捕获**：调用 `UpdateStereoAtlas` 节点。这是一个 Latent 节点，连接到你的事件图后，会在捕获完成后继续执行后续引脚
3. **读取结果**：捕获完成后，从 `LeftEyeAtlas` 和 `RightEyeAtlas` 属性获取生成的全景纹理，可以用于材质、UI 显示或保存到文件

**StereoCameraLayer 组件**：插件还提供了 `UStereoStaticMeshComponent`，可以设置 `EyeToRender` 属性为 `LeftEye`、`RightEye` 或 `BothEyes`，控制网格体仅对特定眼睛渲染，用于立体场景的差异化内容。

## C++ 用法

### 控制台命令（主要使用方式）

插件通过控制台命令驱动，这是最直接的使用方式：

```cpp
// 在编辑器控制台或代码中执行：

// 捕获单帧全景截图
SP.PanoramicScreenshot

// 捕获全景动画序列（从当前帧开始）
SP.PanoramicMovie

// 设置捕获质量: preview | average | improved
SP.PanoramicQuality preview

// 暂停/恢复游戏（用于精确控制捕获时机）
SP.TogglePause
```

### 头文件引入

```cpp
#include "StereoPanorama.h"
#include "SceneCapturer.h"
```

### 基本用法：通过控制台变量调整参数

```cpp
// 来源: Source/PanoramicCapture/Private/StereoPanoramaManager.h
// 
// 插件注册了大量控制台变量来控制捕获行为。
// 可以在代码中通过 IConsoleManager 设置：

// 设置水平角度增量（度），决定水平方向的采样密度
IConsoleVariable* CVarHAng = IConsoleManager::Get().FindConsoleVariable(TEXT("SP.HorizontalAngularIncrement"));
if (CVarHAng) CVarHAng->Set(TEXT("15"));  // 每15度采样一次

// 设置垂直角度增量
IConsoleVariable* CVarVAng = IConsoleManager::Get().FindConsoleVariable(TEXT("SP.VerticalAngularIncrement"));
if (CVarVAng) CVarVAng->Set(TEXT("15"));

// 设置瞳距（用于立体全景）
IConsoleVariable* CVarEyeSep = IConsoleManager::Get().FindConsoleVariable(TEXT("SP.EyeSeparation"));
if (CVarEyeSep) CVarEyeSep->Set(TEXT("3.5"));

// 设置单目模式（只捕获一只眼）
IConsoleVariable* CVarMono = IConsoleManager::Get().FindConsoleVariable(TEXT("SP.MonoscopicMode"));
if (CVarMono) CVarMono->Set(TEXT("1"));

// 设置输出目录
IConsoleVariable* CVarOutputDir = IConsoleManager::Get().FindConsoleVariable(TEXT("SP.OutputDir"));
if (CVarOutputDir) CVarOutputDir->Set(TEXT("C:/PanoramicOutput"));

// 控制输出通道
IConsoleVariable* CVarDepth = IConsoleManager::Get().FindConsoleVariable(TEXT("SP.OutputSceneDepth"));
if (CVarDepth) CVarDepth->Set(TEXT("1"));  // 同时输出场景深度图
```

### 进阶用法：直接调用 PanoramicScreenshot API

```cpp
// 来源: Source/PanoramicCapture/Private/StereoPanoramaManager.h
//
// 可以通过代码直接调用全景截图，指定起始帧和结束帧：

// 获取管理器实例
TSharedPtr<FStereoPanoramaManager> Manager = FStereoPanoramaModule::Get();

// 定义完成回调
FStereoCaptureDoneDelegate DoneDelegate;
DoneDelegate.BindLambda([](const TArray<FLinearColor>& LeftEyeData, const TArray<FLinearColor>& RightEyeData)
{
    UE_LOG(LogTemp, Log, TEXT("全景捕获完成: 左眼 %d 像素, 右眼 %d 像素"),
        LeftEyeData.Num(), RightEyeData.Num());
    // 在这里处理捕获到的全景数据
});

// 调用捕获（指定帧范围）
UWorld* World = GEditor->GetEditorWorldContext().World();
Manager->PanoramicScreenshot(/*InStartFrame=*/100, /*InEndFrame=*/120, DoneDelegate, World);
```

## 控制台变量参考

所有参数均通过 `SP.*` 前缀的控制台变量控制：

| 控制台变量 | 类型 | 说明 |
|---|---|---|
| `SP.HorizontalAngularIncrement` | Float | 水平角度步进（度），默认约 5° |
| `SP.VerticalAngularIncrement` | Float | 垂直角度步进（度） |
| `SP.EyeSeparation` | Float | 左右眼间距（用于立体全景） |
| `SP.CaptureHorizontalFOV` | Float | 每个切片的水平视场角 |
| `SP.CaptureSlicePixelWidth` | Int | 每个切片的像素宽度 |
| `SP.EnableBilerp` | Bool | 启用双线性插值（拼接平滑度） |
| `SP.SuperSamplingMethod` | Int | 超采样方法选择 |
| `SP.ForceAlpha` | Bool | 强制输出 Alpha 通道 |
| `SP.OutputDir` | String | 输出目录路径 |
| `SP.MonoscopicMode` | Bool | 单目模式（禁用立体） |
| `SP.ShouldOverrideInitialYaw` | Bool | 是否覆盖初始偏航角 |
| `SP.ForcedInitialYaw` | Float | 强制的初始偏航角（度） |
| `SP.FadeStereoToZeroAtSides` | Bool | 在两侧渐变立体效果为零 |
| `SP.UseCameraRotation` | Int | 使用相机旋转轴（Pitch=1, Yaw=2, Roll=4, All=7） |
| `SP.OutputFinalColor` | Bool | 输出最终颜色通道 |
| `SP.OutputSceneDepth` | Bool | 输出场景深度 |
| `SP.OutputWorldNormal` | Bool | 输出世界法线 |
| `SP.OutputRoughness` | Bool | 输出粗糙度 |
| `SP.OutputMetalic` | Bool | 输出金属度 |
| `SP.OutputBaseColor` | Bool | 输出基础颜色 |
| `SP.OutputAmbientOcclusion` | Bool | 输出环境遮蔽 |
| `SP.OutputBitDepth` | Int | 输出位深度 |
| `SP.ConcurrentCaptures` | Int | 并发捕获数量 |
| `SP.GenerateDebugImages` | Bool | 生成调试图像 |

## Demo 示例

### 自定义全景捕获 Actor

```cpp
// PanoramicDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StereoPanorama.h"
#include "SceneCapturer.h"
#include "PanoramicDemoActor.generated.h"

UCLASS()
class APanoramicDemoActor : public AActor
{
    GENERATED_BODY()

public:
    APanoramicDemoActor();

    UPROPERTY(EditAnywhere, Category = "Panoramic")
    int32 StartFrame = 0;

    UPROPERTY(EditAnywhere, Category = "Panoramic")
    int32 EndFrame = 60;

    UFUNCTION(BlueprintCallable, Category = "Panoramic")
    void CapturePanorama();

private:
    void OnCaptureComplete(const TArray<FLinearColor>& LeftEyeData, const TArray<FLinearColor>& RightEyeData);
};
```

```cpp
// PanoramicDemoActor.cpp
#include "PanoramicDemoActor.h"
#include "StereoPanorama.h"
#include "SceneCapturer.h"

APanoramicDemoActor::APanoramicDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void APanoramicDemoActor::CapturePanorama()
{
    TSharedPtr<FStereoPanoramaManager> Manager = FStereoPanoramaModule::Get();
    if (!Manager.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("PanoramicCapture 插件未初始化"));
        return;
    }

    FStereoCaptureDoneDelegate DoneDelegate;
    DoneDelegate.BindUObject(this, &APanoramicDemoActor::OnCaptureComplete);

    UWorld* World = GetWorld();
    Manager->PanoramicScreenshot(StartFrame, EndFrame, DoneDelegate, World);
}

void APanoramicDemoActor::OnCaptureComplete(
    const TArray<FLinearColor>& LeftEyeData,
    const TArray<FLinearColor>& RightEyeData)
{
    UE_LOG(LogTemp, Log, TEXT("全景捕获完成: 左眼 %d 像素, 右眼 %d 像素"),
        LeftEyeData.Num(), RightEyeData.Num());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorFramework` | 编辑器框架，用于场景捕获组件的编辑器集成 |
| `UnrealEd` | 编辑器功能，用于 PIE 控制和编辑器内的场景操作 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-12-01 | `28e633a1` | Remove Mip Bias Fade system | 移除了 Mip Bias 渐变系统，简化代码 |
| 2025-08-08 | `40e2c8da` | Passing RHI Command Lists through to MoviePlayer and TickableObjectRenderThread functions. | 适配 RHI 命令列表 API 变更，修复编译兼容性 |
| 2024-10-30 | `ab20a6a9` | [Engine] | 引擎级改动，无具体说明 |
| 2023-06-21 | `06c082c9` | PanoramicCapture: Fix e.g. C: not recognized as a valid path. | 修复 Windows 盘符路径（如 C:）不被识别的 Bug |
| 2023-04-20 | `f68fa87d` | PanoramicCapture: Fix conflict with nDisplay since CDO constructor forces display settings unnecessa | 修复与 nDisplay 插件冲突：CDO 构造函数强制设置显示参数 |

### 维护评价

- **创建时间**：2019 年，已有约 6 年历史
- **维护频率**：每年有 1-2 次更新，但几乎都是编译兼容性修复和 bug 修复，没有功能性增强
- **活跃程度**：**维护不活跃**。自创建以来没有实质性新功能，最近的更新（2023-2025）均为引擎适配修复
- **实验性状态**：虽然 `IsBetaVersion=false`，但仍位于 `Experimental` 目录下，且 `EnabledByDefault=false`
- **已知限制**：
  - 仅支持 Win64 平台
  - 仅在编辑器（UncookedOnly）中可用
  - 捕获过程是逐切片串行/并行执行，大规模全景捕获会很慢
  - 原始作者 Kite & Lightning 是外部公司，后续维护由 Epic 内部引擎团队负责
- **推荐度**：⚠️ **谨慎使用**。适合一次性全景内容生成和原型验证。如果需要生产级全景渲染方案，建议评估 nDisplay + 后期拼接或第三方 VR 全景渲染工具。此插件在实验目录中已停留多年，未见晋升迹象。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PanoramicCapture)
- [Kite & Lightning 官网（原始作者）](https://kiteandlightning.la/)
- 测试用例：无