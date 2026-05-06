# Panoramic Capture

> A plugin to capture a sequence of panoramic images in monoscopic or stereoscopic (top/bottom).

| 属性 | 值 |
|---|---|
| 中文名 | 全景截图 |
| 分类 | Movie Capture |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `PanoramicCapture` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-06 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PanoramicCapture) | |

## 用途

Panoramic Capture（全景截图）插件提供在编辑器或游戏中捕获全景（360°）截图或序列帧的功能，支持单目（Monoscopic）和双目立体（Stereoscopic Top/Bottom）两种模式。其核心目标是为开发者快速生成高质量的全景图像，用于 VR 预览、环境贴图（Cubemap）烘焙、360° 视频录制等场景。

插件通过控制场景摄像机在预设的方位角/仰角步进捕捉画面，将多张切片拼接为全景图，并支持输出多种渲染通道（如 BaseColor、WorldNormal、SceneDepth 等），为后期合成提供素材。同时提供蓝图节点和 C++ 接口，方便集成到自动化工作流中。

## 使用场景

- **VR 内容创作**：捕获全景截图用于 VR 应用中的背景环境或菜单界面。
- **虚拟制片**：在编辑器中快速生成 360° 参考图，供美术人员评估光照和布局。
- **自动化测试**：通过控制台命令实现批量全景截图，校验渲染一致性。
- **后期合成**：输出带材质属性（如 Metallic、Roughness、AO）的全景图，用于 PBR 烘焙。
- **全景视频录制**：设置起止帧，配合序列截图生成连续帧，可转制为 360° 视频。

## 蓝图用法

插件提供了 `AStereoCapturePawn` 蓝图节点，用于触发全景截图并获取结果纹理。此外，控制台命令可在编辑器运行时直接调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Update Stereo Atlas` (Latent) | 异步执行一次全景截图，完成后更新 `LeftEyeAtlas` / `RightEyeAtlas` 纹理 | `AStereoCapturePawn` |
| `Left Eye Atlas` (Get) | 读取左眼全景纹理（单目模式时仅左眼有效） | `AStereoCapturePawn` |
| `Right Eye Atlas` (Get) | 读取右眼全景纹理（双目模式） | `AStereoCapturePawn` |

### 使用示例（蓝图描述）

1. **触发全景截图**：在关卡中放置 `Stereo Capture Pawn`（蓝图类 `AStereoCapturePawn`）。在事件图表中通过 `Spawn Actor from Class (Stereo Capture Pawn)` 生成 pawn 对象。调用 `Update Stereo Atlas` 节点（需要 `World Context` 对象和 `Latent Info`）。当捕获完成后，可以访问该 pawn 的 `LeftEyeAtlas` 和 `RightEyeAtlas` 属性，将它们赋值给 UI 图像控件或保存为文件。

2. **控制台调试**：按 `~` 打开控制台，输入以下命令：
   - `SP.PanoramicScreenshot` – 截取当前视角的全景截图并保存到项目 Saved 目录。
   - `SP.PanoramicMovie` – 开始连续截图（用于全景电影），可指定起止帧。
   - `SP.PanoramicQuality [preview/average/improved]` – 设置截图质量。
   - `SP.TogglePause` – 暂停/恢复游戏循环以稳定捕捉。

## C++ 用法

### 头文件引入

```cpp
#include "StereoPanorama.h"         // 模块接口
#include "StereoCapturePawn.h"      // 蓝图捕获 pawn
#include "SceneCapturer.h"          // 底层场景捕获器
```

### 基本用法

通过控制台命令触发全景截图（推荐用于自动化）：

```cpp
// 文件：Engine/Plugins/Experimental/PanoramicCapture/Source/PanoramicCapture/Private/StereoPanoramaManager.cpp
// 在任意模块执行控制台命令
void UMyFunctionLibrary::CapturePanorama(UWorld* World)
{
    // 调用 SP.PanoramicScreenshot，参数可选：StartFrame EndFrame
    IConsoleManager::Get().ProcessUserConsoleInput(
        TEXT("SP.PanoramicScreenshot 0 0"), 
        *GLog, 
        World
    );
}
```

或者使用 `FStereoPanoramaManager` 直接调用：

```cpp
// 文件：Engine/Plugins/Experimental/PanoramicCapture/Source/PanoramicCapture/Private/StereoPanoramaManager.cpp
void UMyFunctionLibrary::CapturePanoramaWithDelegate(UWorld* World)
{
    TSharedPtr<FStereoPanoramaManager> Manager = FStereoPanoramaModule::Get();
    if (Manager.IsValid())
    {
        // 准备委托，接收左右眼像素数据
        FStereoCaptureDoneDelegate Delegate;
        Delegate.BindLambda([](const TArray<FLinearColor>& LeftData, const TArray<FLinearColor>& RightData)
        {
            // 处理像素数据，例如保存为 EXR 或 PNG
        });
        // 参数：起始帧, 结束帧, 委托, 世界
        Manager->PanoramicScreenshot(0, 0, Delegate, World);
    }
}
```

### 进阶用法

设置捕获质量和其他参数（通过控制台变量）：

```cpp
// 设置水平角步进（度），默认 1.0
IConsoleManager::Get().FindConsoleVariable(TEXT("SP.HorizontalAngularIncrement"))->Set(0.5f);
// 设置垂直角步进（度），默认 1.0
IConsoleManager::Get().FindConsoleVariable(TEXT("SP.VerticalAngularIncrement"))->Set(1.0f);
// 启用单目模式（不生成右眼）
IConsoleManager::Get().FindConsoleVariable(TEXT("SP.MonoscopicMode"))->Set(1);
// 设置输出目录（默认项目 Saved/StereoPanorama）
IConsoleManager::Get().FindConsoleVariable(TEXT("SP.OutputDir"))->Set(TEXT("D:/PanoramaOutput"));
```

更多 CVar 前缀为 `SP.` 的变量可在控制台输入 `SP.` 按 Tab 查看。

## Demo 示例

以下是一个最小 C++ 示例，用于在编辑器按下快捷键时触发全景截图并保存。

### MyActor.h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    void CapturePanoramic();
};
```

### MyActor.cpp

```cpp
#include "MyActor.h"
#include "PanoramicCapture/Public/StereoPanorama.h"
#include "Engine/Console.h"
#include "Kismet/GameplayStatics.h"

void AMyActor::BeginPlay()
{
    // 每 10 秒自动捕获一次（演示用途）
    GetWorldTimerManager().SetTimer(
        TimerHandle,
        this,
        &AMyActor::CapturePanoramic,
        10.0f,
        true
    );
}

void AMyActor::CapturePanoramic()
{
    UWorld* World = GetWorld();
    if (World && World->IsGameWorld())
    {
        // 通过控制台命令触发
        UConsole* Console = UGameplayStatics::GetPlayerController(World, 0)->Console;
        if (Console)
        {
            Console->ConsoleCommand(TEXT("SP.PanoramicScreenshot"));
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorFramework` | 编辑器框架基础（Editor Subsystem 等） |
| `UnrealEd` | 编辑器核心功能（资源管理、命令执行等） |

## 维护状态

### 近期更新

- 2025-08-08 `40e2c8da` Passing RHI Command Lists through to MoviePlayer and TickableObjectRenderThread functions. (传递 RHI 命令列表至 MoviePlayer 和 TickableObjectRenderThread 函数)
- 2024-10-30 `ab20a6a9` [Engine] (引擎基础设施更新)
- 2023-06-21 `06c082c9` PanoramicCapture: Fix e.g. C: not recognized as a valid path. (修复路径识别问题)
- 2023-04-20 `f68fa87d` PanoramicCapture: Fix conflict with nDisplay since CDO constructor forces display settings unnecessarily (修复与 nDisplay 的冲突)
- 2023-01-06 `6a481585` [PanoramicCapture] 初始提交

### 维护评价

- **初次提交**：2023-01-06（约 2.5 年前），插件较新，但仍属于实验性插件（`IsBetaVersion=false`、`EnabledByDefault=false`）。
- **近期更新**：2025-08-08 有传递性改动，但并非针对全景捕获功能的直接修复或增强。实质性代码更新主要集中在 2023 年（修复路径、nDisplay 冲突）。
- **活跃度**：插件没有被废弃，但更新频率低，缺乏新功能增加。可能处于维护阶段，主要用于 UE 自身项目需求。
- **推荐使用**：如果只需要简单的 360° 截图功能，此插件可用。若需要更高级的全景视频编码或实时性能，建议评估其他社区方案（如 Movie Render Queue + 全景输出设置）。注意插件仅支持 Win64 平台且标记为实验性，稳定性需自行测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PanoramicCapture)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/panoramic-capture-plugin-in-unreal-engine/) (注意：官方文档可能不存在，此处占位)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PanoramicCapture/Tests) (测试文件可能随引擎一起提供，但路径不确定)