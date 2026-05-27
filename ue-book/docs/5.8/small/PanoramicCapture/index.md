# Panoramic Capture

> A plugin to capture a sequence of panoramic images in monoscopic or stereoscopic (top/bottom).

| 属性 | 值 |
|---|---|
| 中文名 | 全景捕获 |
| 分类 | Movie Capture |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质） |
| 模块 | `PanoramicCapture` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-06-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PanoramicCapture) | |

## 用途
此插件的核心功能是在游戏或应用运行时，从场景中捕获一系列的二维图像切片，然后将这些切片拼接、投影成一张完整的全景图像或视频序列。它主要用于生成用于虚拟现实（VR）体验的立体（左右眼）全景内容，也支持单目模式。插件通过精确控制相机在多个水平和垂直角度的旋转来完成多角度拍摄，并提供了丰富的控制台变量来自定义拍摄参数（如视角、分辨率、质量等）和输出通道（如最终颜色、深度、法线、材质属性等）。其设计目的是服务于VR内容创作者，以便在引擎内直接生成可用于全景播放器或后期合成的素材。

## 使用场景
- 你正在开发一个VR应用或游戏，需要为其生成高质量的立体全景环境地图（Skybox）。
- 你需要为一个360度视频项目在UE场景中拍摄源素材。
- 你需要获取场景在多个渲染通道（如深度、法线、材质ID）下的数据，用于后期合成或机器学习数据集生成。
- 你在编辑器中需要快速预览当前场景在全景模式下的视觉效果。

## 蓝图用法
该插件主要通过控制台命令进行控制，但提供了一个蓝图可用的Pawn类用于在关卡中进行交互和结果预览。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UpdateStereoAtlas` | 异步执行立体全景图的更新与拼接操作。这是一个延迟（Latent）节点。 | `AStereoCapturePawn` |
| `LeftEyeAtlas` | 获取拼接完成后的左眼全景纹理（`UTexture2D`）。 | `AStereoCapturePawn` |
| `RightEyeAtlas` | 获取拼接完成后的右眼全景纹理（`UTexture2D`）。 | `AStereoCapturePawn` |

### 使用示例（蓝图描述）
1.  在你的场景中放置一个 `AStereoCapturePawn` 或其子类。
2.  在某个事件（如关卡蓝图中的 `BeginPlay` 或一个按键事件）中，调用该Pawn的 `UpdateStereoAtlas` 节点。该节点将启动后台捕获流程，并在流程完成后（通过Latent节点的输出引脚通知）自动更新Pawn的纹理属性。
3.  你可以在其他地方（如UMG界面）直接读取该Pawn的 `LeftEyeAtlas` 和 `RightEyeAtlas` 属性，以获取最终生成的全景纹理用于显示或保存。

## C++ 用法
核心控制通过控制台命令和 `FStereoPanoramaManager` 单例完成。

### 头文件引入
```cpp
// 通常不需要直接包含，使用控制台命令即可。若需管理类，可包含：
#include "StereoPanoramaManager.h"
```

### 基本用法
通过控制台命令触发拍摄。
```cpp
// 在控制台输入或通过代码执行命令，进行单帧全景截图
// 命令格式：SP.PanoramicScreenshot [参数]
// 示例代码：在某个函数中执行控制台命令
GEngine->Exec(nullptr, TEXT("SP.PanoramicScreenshot"));

// 进行序列拍摄（生成多帧用于视频）
GEngine->Exec(nullptr, TEXT("SP.PanoramicMovie"));
```
**控制台变量说明（通过命令行或代码设置）**：
- `SP.HorizontalAngularIncrement`: 水平方向切片间的角度增量。
- `SP.VerticalAngularIncrement`: 垂直方向切片间的角度增量。
- `SP.EyeSeparation`: 立体模式下的双眼间距。
- `SP.MonoscopicMode`: 设为1启用单目模式，0为立体模式。
- `SP.OutputDir`: 设置输出图像序列的目录。
- `SP.PanoramicQuality [preview|average|improved]`: 设置渲染质量预设。

### 进阶用法
通过 `FStereoPanoramaManager` 管理器进行更精细的控制，例如获取捕获完成的委托。
```cpp
#include "StereoPanoramaManager.h"

// 获取管理器实例
TSharedPtr<FStereoPanoramaManager> Manager = FStereoPanoramaModule::Get();
if (Manager.IsValid())
{
    // 定义一个回调委托，捕获完成时触发
    FStereoCaptureDoneDelegate OnCaptureDone;
    OnCaptureDone.BindLambda([](const TArray<FLinearColor>& LeftData, const TArray<FLinearColor>& RightData)
    {
        // 在这里处理捕获到的原始线性颜色数据
        UE_LOG(LogTemp, Warning, TEXT("Capture finished! Left atlas size: %d"), LeftData.Num());
    });

    // 启动捕获（示例：从第0帧到第60帧）
    UWorld* World = GEditor->GetEditorWorldContext().World();
    Manager->PanoramicScreenshot(0, 60, OnCaptureDone, World);
}
```

## Demo 示例
以下是一个最小化的C++示例，展示如何在编辑器模式下通过按钮触发全景捕获。

```cpp
// MyPanoramicCaptureActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyPanoramicCaptureActor.generated.h"

UCLASS()
class MYPROJECT_API AMyPanoramicCaptureActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AMyPanoramicCaptureActor();

	UFUNCTION(BlueprintCallable, Category = "Capture")
	void StartCapture();

private:
	void OnCaptureComplete(const TArray<FLinearColor>& LeftData, const TArray<FLinearColor>& RightData);
};
```

```cpp
// MyPanoramicCaptureActor.cpp
#include "MyPanoramicCaptureActor.h"
#include "StereoPanoramaManager.h" // 引入插件管理器头文件

AMyPanoramicCaptureActor::AMyPanoramicCaptureActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMyPanoramicCaptureActor::StartCapture()
{
	TSharedPtr<FStereoPanoramaManager> Manager = FStereoPanoramaModule::Get();
	if (!Manager.IsValid())
	{
		UE_LOG(LogTemp, Error, TEXT("PanoramicCapture Plugin is not available!"));
		return;
	}

	FStereoCaptureDoneDelegate OnDone;
	OnDone.BindUObject(this, &AMyPanoramicCaptureActor::OnCaptureComplete);

	UWorld* World = GetWorld();
	if (World)
	{
		// 捕获当前时间点附近的一个短序列（例如，捕获10帧）
		Manager->PanoramicScreenshot(0, 10, OnDone, World);
	}
}

void AMyPanoramicCaptureActor::OnCaptureComplete(const TArray<FLinearColor>& LeftData, const TArray<FLinearColor>& RightData)
{
	UE_LOG(LogTemp, Log, TEXT("Panoramic capture completed. Left eye data size: %d, Right eye data size: %d"), LeftData.Num(), RightData.Num());
	// 在这里可以将数据保存到文件或进行其他处理
}
```

## 模块依赖
该插件为 `UncookedOnly` 类型，仅在开发版本（编辑器或未打包游戏）中可用。它依赖以下编辑器框架模块：

| 模块 | 用途 |
|---|---|
| `EditorFramework` | 提供编辑器基础框架支持 |
| `UnrealEd` | 提供编辑器专用功能和API |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-12-01 | `28e633a1` | Remove Mip Bias Fade system | 移除了 Mip Bias 渐变系统，可能涉及渲染质量或LOD过渡的简化。 |
| 2025-08-08 | `40e2c8da` | Passing RHI Command Lists through to MoviePlayer and TickableObjectRenderThread functions. | 为 MoviePlayer 和 TickableObjectRenderThread 函数传递 RHI Command Lists，优化多线程渲染命令提交。 |
| 2024-10-30 | `ab20a6a9` | [Engine] | 引擎版本更新，未明确修改插件本身。 |
| 2023-06-21 | `06c082c9` | PanoramicCapture: Fix e.g. C: not recognized as a valid path. | 修复了如 “C:” 等绝对路径不被识别为有效路径的问题。 |
| 2023-04-20 | `f68fa87d` | PanoramicCapture: Fix conflict with nDisplay since CDO constructor forces display settings unnecessa | 修复了与 nDisplay 插件的冲突，原因是默认对象构造函数不必要地强制了显示设置。 |

### 维护评价
- **状态**: **维护中但非核心功能**。插件创建于2019年，作为实验性功能至今仍有更新，最近一次功能性更新在2023年（路径修复），2025年的更新更多是引擎层面的优化适配。
- **活跃度**: 维护频率较低，最近几次提交间隔较长，且主要是bug修复和引擎兼容性调整，而非新功能开发。
- **建议**: 该插件功能明确且相对稳定，适用于有特定全景内容制作需求的用户。由于其 `UncookedOnly` 的性质和实验性标签，不建议用于最终发布的项目核心逻辑。使用前应充分测试其与当前引擎版本的兼容性。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PanoramicCapture)
- 官方文档：无
- 测试用例：未在提供的文件中发现独立的测试文件。