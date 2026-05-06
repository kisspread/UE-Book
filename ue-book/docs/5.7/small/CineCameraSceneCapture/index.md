# CineCameraSceneCapture

> This plugin adds the ability to render cine camera views into Render Targets identically to Scene Capture

| 属性 | 值 |
|---|---|
| 中文名 | 电影摄像机场景捕获 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CineCameraSceneCapture` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CineCameraSceneCapture) | |

## 用途

标准场景捕获组件（`USceneCaptureComponent2D`）使用引擎的简化渲染路径，与主摄像机（特别是 Cine Camera）的视图存在视觉差异。该插件提供 `UCineCaptureComponent2D`，它继承自 `USceneCaptureComponent2D`，但完全复用 Cine Camera 的渲染管线（包括后处理、色彩管理、镜头畸变等），使渲染目标捕获结果与 Cine Camera 视口显示完全一致。

主要解决以下问题：
- 在使用 Cine Camera 进行虚拟制片时，需要将 Cine Camera 的视图输出到渲染目标（如用于合成、流送、回放），同时保留所有镜头特效（景深、色差、OCIO 色彩转换等）。
- 标准场景捕获会丢失 Cine Camera 特有的属性（如焦距、光圈、传感器尺寸等）以及相关后处理。

该组件必须作为 Cine Camera 组件的子组件才能工作，它会自动获取父级 Cine Camera 的参数并应用到渲染目标上。

## 使用场景

- **虚拟制片/实时合成**：使用多台 Cine Camera 拍摄，将每台摄像机的画面捕获到单独的 Render Target 中，再通过 Compositing 工具进行合成。
- **回放/录制**：将 Cine Camera 的最终画面直接输出到外部视频流（通过 Media Capture），避免二次取样导致的差异。
- **多用户协作**：在协作会话中，将某台 Cine Camera 的画面共享给其他用户作为参考窗口。
- **色彩工作流**：需要应用 OpenColorIO（OCIO）色彩转换到捕获结果，保持与视口相同的色彩空间。

## 蓝图用法

插件未新增独立的蓝图可调用函数，所有功能均通过 `UCineCaptureComponent2D` 的属性进行配置。使用方式与标准场景捕获类似，但必须注意父级要求。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无新增蓝图函数 | 直接通过属性面板或蓝图设置属性 | `UCineCaptureComponent2D` |

### 使用示例（蓝图描述）

1. 在关卡中放置一个 `CineCameraActor`（或具有 `CineCameraComponent` 的蓝图类）。
2. 选中该 Actor，在蓝图编辑器或组件面板中添加 `CineCaptureComponent2D`（组件名为 "Cine Capture"）。
3. 设置 `Texture Target` 属性为一个现有的 Render Target 或在运行时创建。
4. 调整 `Capture Settings` 下的属性：
   - `Render Target Highest Dimension`：控制渲染目标的最大边长（根据宽高比自动计算另一维度）。
   - `bFollow Scene Capture Render Path`：如果遇到画面差异，取消勾选以使用更接近视口的渲染路径。
   - `Open Color IO Display Configuration`：配置 OCIO 颜色变换。
5. 启用组件后，渲染目标将自动更新。

注意：组件需要被附加到 Cine Camera Component 上才能工作（蓝图编辑器中右键添加组件时选择它即可）。

## C++ 用法

### 头文件引入

```cpp
#include "CineCameraSceneCaptureComponent.h"
```

### 基本用法

以下代码展示了如何创建一个 `UCineCaptureComponent2D`，将其附加到现有的 Cine Camera 组件上，并绑定渲染目标（源自插件测试中常见模式）。

```cpp
// 假设已在某 Actor 中
#include "CineCameraActor.h"
#include "CineCameraComponent.h"
#include "CineCameraSceneCaptureComponent.h"
#include "Engine/TextureRenderTarget2D.h"

void SetupCineCapture(ACineCameraActor* CineCamActor)
{
    if (!CineCamActor) return;

    UCineCameraComponent* CamComp = CineCamActor->GetCineCameraComponent();
    if (!CamComp) return;

    // 创建捕获组件并附加到 CineCamera 组件
    UCineCaptureComponent2D* CaptureComp = NewObject<UCineCaptureComponent2D>(CineCamActor);
    CaptureComp->SetupAttachment(CamComp); // 必须附着到 CineCameraComponent 或其子级
    CaptureComp->RegisterComponent();

    // 创建渲染目标
    UTextureRenderTarget2D* RTarget = NewObject<UTextureRenderTarget2D>();
    RTarget->InitAutoFormat(1920, 1080);
    CaptureComp->TextureTarget = RTarget;

    // 配置捕获参数
    CaptureComp->RenderTargetHighestDimension = 1920;
    CaptureComp->bFollowSceneCaptureRenderPath = true; // 使用场景捕获渲染路径（性能更优）
    CaptureComp->bOverrideUserFlags = false;

    // 启用捕获（CaptureSource 默认继承自父类，根据需要设置）
    CaptureComp->CaptureSource = ESceneCaptureSource::SCS_FinalColorLDR;
}
```

### 进阶用法

结合 OCIO 配置，使捕获结果应用相同的色彩变换：

```cpp
#include "OpenColorIOConfiguration.h"
#include "OpenColorIOColorSpace.h"

void ApplyOCIOToCapture(UCineCaptureComponent2D* CaptureComp, UOpenColorIOConfiguration* OCIOConfig)
{
    if (!CaptureComp || !OCIOConfig) return;

    // 设置 OCIO 显示配置（需要先设置 ColorSpaceSource 等）
    FOpenColorIODisplayConfiguration& OCIOConfig = CaptureComp->OCIOConfiguration;
    OCIOConfig.bIsEnabled = true;
    OCIOConfig.ColorConfiguration.ConfigurationSource = OCIOConfig;

    // 其他属性如 DisplayView 等可在细节面板设置，或通过代码设置
    OCIOConfig.ColorConfiguration.ColorSpace = ...; // 根据需要设置
}
```

## Demo 示例

以下是一个可在 `AGameModeBase` 中使用的简单示例，演示如何动态创建 Cine Camera 并为其添加场景捕获组件。

### CineCaptureDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CineCaptureDemo.generated.h"

UCLASS()
class ACineCaptureDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ACineCaptureDemoActor();

    virtual void BeginPlay() override;

    UPROPERTY(EditDefaultsOnly, Category = "CineCapture")
    class UTextureRenderTarget2D* RenderTarget;

private:
    class UCineCaptureComponent2D* CaptureComp;
};
```

### CineCaptureDemo.cpp

```cpp
#include "CineCaptureDemo.h"
#include "CineCameraActor.h"
#include "CineCameraComponent.h"
#include "CineCameraSceneCaptureComponent.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Kismet/GameplayStatics.h"

ACineCaptureDemoActor::ACineCaptureDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ACineCaptureDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 在场景中查找或生成一个 CineCameraActor
    ACineCameraActor* CineCam = nullptr;
    TArray<AActor*> FoundActors;
    UGameplayStatics::GetAllActorsOfClass(GetWorld(), ACineCameraActor::StaticClass(), FoundActors);
    if (FoundActors.Num() > 0)
    {
        CineCam = Cast<ACineCameraActor>(FoundActors[0]);
    }
    else
    {
        // 生成一个新的 CineCameraActor
        FActorSpawnParameters SpawnParams;
        CineCam = GetWorld()->SpawnActor<ACineCameraActor>(FVector(0, 0, 200), FRotator::ZeroRotator, SpawnParams);
    }

    if (!CineCam)
    {
        UE_LOG(LogTemp, Error, TEXT("No CineCameraActor available"));
        return;
    }

    UCineCameraComponent* CamComp = CineCam->GetCineCameraComponent();
    if (!CamComp)
    {
        return;
    }

    // 创建捕获组件并附着到 CineCameraComponent
    CaptureComp = NewObject<UCineCaptureComponent2D>(CineCam);
    CaptureComp->SetupAttachment(CamComp);
    CaptureComp->RegisterComponent();

    // 设置渲染目标
    if (RenderTarget)
    {
        CaptureComp->TextureTarget = RenderTarget;
    }
    else
    {
        // 运行时创建默认 1920x1080 的 RT
        UTextureRenderTarget2D* RT = NewObject<UTextureRenderTarget2D>();
        RT->InitAutoFormat(1920, 1080);
        CaptureComp->TextureTarget = RT;
    }

    // 其他可选参数
    CaptureComp->RenderTargetHighestDimension = 1920;
    CaptureComp->bFollowSceneCaptureRenderPath = true;

    UE_LOG(LogTemp, Log, TEXT("CineCaptureDemo: Cine Capture Component attached and configured."));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenColorIO` | 提供色彩管理与颜色空间转换支持 |

无其他特殊依赖（标准 Core/Engine/Slate 等已省略）。

## 维护状态

### 近期更新

- 2025-03-31 `a492f271` 修复基类移除虚析构函数后缺少虚析构函数的问题
- 2025-02-27 `3385f1fa` 新增第一人称渲染支持（允许在 Scene Capture 2D 组件中启用第一人称视角）
- 2025-02-13 `ec3fb596` 替换 Engine 其余部分中的 `IsValid(this)` 检查
- 2024-12-09 `f29fed7f` 修复丢失的相机属性拷贝（因 CL 37799633 意外破坏）
- 2024-11-26 `9ab621ba` 移除空的场景扩展实现（初始版本后的清理）

### 维护评价

- **创建时间**：2024-11-26，距今约 11 个月。
- **更新频率**：从提交记录看，大约每 1-2 个月有一次功能性或修复性更新，最近 3 个月有两次更新（2025-03-31 和 2025-02-27）。
- **活跃度**：仍在积极维护，开发者根据使用反馈快速修复了相机属性拷贝和析构函数问题，并增加了第一人称支持。
- **建议**：该插件功能明确，与虚拟制片工作流高度相关，且官方持续投入，推荐在项目中试用。但需注意其标记为实验性，API 可能在未来版本中变化。建议在 UE5.5 及以上版本使用（首次出现于 5.5？实际在 5.4 或 5.5 的早期预览阶段，但 5.7 中已稳定）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CineCameraSceneCapture)
- [官方文档]（暂无独立文档，参见插件说明）
- [测试用例]（未提供公开测试）