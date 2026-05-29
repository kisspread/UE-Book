# OpenCV

> Plugin initializing OpenCV library to be used in engine.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 计算机视觉 |
| 分类 | Computer Vision |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `OpenCVHelper` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-11-22 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenCV) | |

## 用途

此插件为虚幻引擎集成了知名的 OpenCV 计算机视觉库。虽然其描述为“初始化 OpenCV 库”，但其核心价值在于 `FOpenCVHelper` 类中封装的一系列实用计算机视觉函数。它解决了在虚幻引擎项目中直接使用 OpenCV 的复杂性和底层集成问题，提供了开箱即用的蓝图节点和 C++ 接口，用于处理常见的视觉任务，如相机标定、标记检测和坐标转换。

## 使用场景

-   **虚拟制作与影视制作**：你需要实时校准物理相机与虚拟相机的参数，或将虚拟物体精确对齐到绿幕/实体标记点上。
-   **增强现实 (AR) 或混合现实 (MR)**：你需要在游戏运行时识别现实世界中的特定视觉标记（如 ArUco 码），并基于其位置和姿态生成虚拟内容。
-   **机器人视觉或模拟**：你需要在模拟环境中使用计算机视觉算法来处理来自模拟相机的图像数据，例如检测棋盘格进行系统标定。
-   **任何需要在蓝图或 C++ 中进行基础计算机视觉处理的场景**，例如图像变换、特征点匹配等。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenCV Chessboard Detect Corners` | 在输入图像中检测相机标定棋盘格，并返回角点坐标。 | `UOpenCVBlueprintFunctionLibrary` |
| `OpenCV ArUco Detect Markers` | 在输入图像中检测所有 ArUco 标记，可估计其 3D 姿态。 | `UOpenCVBlueprintFunctionLibrary` |
| `FOpenCVLensDistortionParametersBase` | 用于存储镜头畸变参数（K1-K6, P1-P2 等）的结构体，是 ArUco 姿态估计等功能的输入。 | 结构体 |

### 使用示例（蓝图描述）

1.  **棋盘格检测**：
    *   创建一个 `Render Target 2D` 作为输入图像。
    *   从变量或常量创建 `PatternSize` (X, Y) 来描述你的物理棋盘格内部角点数量。
    *   连接 `OpenCV Chessboard Detect Corners` 节点。
    *   勾选 `bDebugDrawCorners` 可获得一张标记了角点的调试纹理。
    *   从 `OutDetectedCorners` 输出引脚获得 `TArray<Vector2D>` 角点坐标，可用于后续的相机标定计算。

2.  **ArUco 标记检测与姿态估计**：
    *   同样准备 `Render Target 2D` 输入。
    *   设置 `Dictionary` 和 `DictionarySize` 参数，必须与你使用的物理标记一致。
    *   若需估计标记的 6DOF 位姿，需设置 `bEstimatePose` 为真，并提供标记的实际边长（米）以及镜头的 `FOpenCVLensDistortionParametersBase`。
    *   连接 `OpenCV ArUco Detect Markers` 节点。
    *   从 `OutDetectedMarkers` 输出的 `TArray<FOpenCVArucoDetectedMarker>` 中，每个元素都包含标记的 `Id`、图像 `Corners` 和计算得到的 `Pose`。

## C++ 用法

### 头文件引入

```cpp
#include "OpenCVHelper.h"
#include "IOpenCVHelperModule.h"
```

### 基本用法

以下代码演示如何使用 `FOpenCVHelper` 检测棋盘格角点。这是相机标定流程的第一步。

```cpp
// 假设 `ImageColors` 是一个包含图像数据的 TArray<FColor>
TArray<FColor> ImageColors;
FIntPoint ImageSize(1920, 1080);
// 物理棋盘格的内部角点数（列，行）
FIntPoint CheckerboardSize(9, 6);
TArray<FVector2f> DetectedCorners;

// 使用 FOpenCVHelper 静态函数进行检测
bool bSuccess = FOpenCVHelper::IdentifyCheckerboard(
    ImageColors,
    ImageSize,
    CheckerboardSize,
    DetectedCorners
);

if (bSuccess)
{
    // 成功检测到角点，可以进行后续操作，例如绘制调试视图
    UTexture2D* DebugTexture = ...; // 需要一个现有的纹理对象
    FOpenCVHelper::DrawCheckerboardCorners(DetectedCorners, CheckerboardSize, DebugTexture);
    // 或者使用检测到的角点进行相机标定 (SolvePnP)
}
```
*来源参考: `FOpenCVHelper::IdentifyCheckerboard` 函数原型及一般计算机视觉标定流程。*

### 进阶用法

以下代码演示如何结合 Charuco 板进行更精确的相机标定，以及如何在 UE 和 OpenCV 坐标系间进行转换。

```cpp
// 1. 配置 Charuco 板
FCharucoBoardConfig CharucoBoardConfig;
CharucoBoardConfig.SquaresX = 5;
CharucoBoardConfig.SquaresY = 7;
CharucoBoardConfig.SquareSize = 4.0f; // cm
CharucoBoardConfig.MarkerSize = 3.0f; // cm
CharucoBoardConfig.Dictionary = EArucoDictionary::DICT_4X4_50;

// 2. 检测 Charuco 角点
TArray<FColor> ImageData = ...;
FIntPoint ImageRes = ...;
FCharucoCorners DetectedCharucoCorners;

bool bFound = FOpenCVHelper::IdentifyCharucoCorners(
    ImageData,
    ImageRes,
    CharucoBoardConfig,
    DetectedCharucoCorners
);

// 3. 使用检测到的 3D-2D 点对应关系求解相机位姿 (例如，使用 SolvePnP)
// 这里假设你已经通过其他方法得到了 ObjectPoints 和 ImagePoints
TArray<FVector> ObjectPoints;
TArray<FVector2f> ImagePoints;
FVector2D FocalLength, ImageCenter;
TArray<float> DistortionParams; // 来自标定过程
FTransform OutCameraPose;

bool bPoseSolved = FOpenCVHelper::SolvePnP(
    ObjectPoints,
    ImagePoints,
    FocalLength,
    ImageCenter,
    DistortionParams,
    OutCameraPose
);

// 4. 坐标转换 (OpenCV坐标系: X右, Y下, Z前 -> UE坐标系: X前, Y右, Z上)
if (bPoseSolved)
{
    // 直接转换一个 OpenCV 坐标系下的 Transform 到 UE 坐标系
    FOpenCVHelper::ConvertOpenCVToUnreal(OutCameraPose);

    // 或者分别转换一个位置向量
    FVector OpenCVPosition = ...;
    FVector UEPosition = FOpenCVHelper::ConvertOpenCVToUnreal(OpenCVPosition);
}
```
*来源参考: `FOpenCVHelper::IdentifyCharucoCorners`, `FOpenCVHelper::SolvePnP`, `FOpenCVHelper::ConvertOpenCVToUnreal` 函数。*

## Demo 示例

以下是一个最小的、可编译的 C++ 示例，演示如何在 Actor 中使用 OpenCV 插件检测棋盘格。

**MyOpenCVActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyOpenCVActor.generated.h"

class UTextureRenderTarget2D;

UCLASS()
class AMyOpenCVActor : public AActor
{
    GENERATED_BODY()

public:
    AMyOpenCVActor();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(EditAnywhere, Category = "OpenCV Demo")
    UTextureRenderTarget2D* SceneRenderTarget;

    UPROPERTY(EditAnywhere, Category = "OpenCV Demo", Meta = (ClampMin = "2"))
    FIntPoint CheckerboardSize = FIntPoint(9, 6);

private:
    void PerformCheckerboardDetection();
    UTexture2D* DebugTexture;
};
```

**MyOpenCVActor.cpp**
```cpp
#include "MyOpenCVActor.h"
#include "Kismet/KismetRenderingLibrary.h"
#include "OpenCVHelper.h"

AMyOpenCVActor::AMyOpenCVActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyOpenCVActor::BeginPlay()
{
    Super::BeginPlay();
    // 确保 RenderTarget 已设置
    if (!SceneRenderTarget)
    {
        UE_LOG(LogTemp, Warning, TEXT("Please assign a SceneRenderTarget in the editor."));
        PrimaryActorTick.bCanEverTick = false;
    }
}

void AMyOpenCVActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    PerformCheckerboardDetection();
}

void AMyOpenCVActor::PerformCheckerboardDetection()
{
    if (!SceneRenderTarget) return;

    // 从 RenderTarget 读取像素数据到 TArray<FColor>
    TArray<FColor> ImageData;
    FIntPoint ImageSize;
    // 注意：实际项目中应使用更高效的方式读取 RT 数据
    // 这里简化演示流程，可能需要异步读取
    UKismetRenderingLibrary::ReadRenderTarget(this, SceneRenderTarget, ImageData, ImageSize);

    TArray<FVector2f> OutCorners;
    bool bFound = FOpenCVHelper::IdentifyCheckerboard(
        ImageData,
        ImageSize,
        CheckerboardSize,
        OutCorners
    );

    if (bFound)
    {
        UE_LOG(LogTemp, Log, TEXT("Found checkerboard with %d corners."), OutCorners.Num());
        // 可选：绘制调试纹理
        if (!DebugTexture)
        {
            DebugTexture = UTexture2D::CreateTransient(ImageSize.X, ImageSize.Y);
            // ... 初始化纹理 ...
        }
        FOpenCVHelper::DrawCheckerboardCorners(OutCorners, CheckerboardSize, DebugTexture);
        // 此时 DebugTexture 可以保存到磁盘或用于 UI 显示
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenCV` | 第三方 OpenCV 计算机视觉库，本插件的核心依赖。其构建规则在 `Source/ThirdParty/OpenCV/OpenCV.Build.cs` 中定义。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量截断为 float 导致的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式的 `UE_LOG` 宏迁移到新的 `UE_LOGF` 宏。 |
| 2026-04-13 | `a0b7804f` | [OpenCV] Add OpenCV library for macOS | 为 macOS 平台添加了 OpenCV 库支持，扩大了跨平台能力。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理了修改纹理属性的代码，将其正确包裹在 `PreEditChange`/`PostEditChange` 中，以符合编辑器规范。 |
| 2025-11-10 | `e0906b79` | Fix for crash when OpenCV fails to load | 修复了当 OpenCV 库加载失败时会导致引擎崩溃的问题，增强了稳定性。 |

### 维护评价

该插件创建于 2021 年底，作为从 UE 内部模块剥离出的独立插件。尽管在 `.uplugin` 中被标记为 `IsBetaVersion: true`，但从 Git 历史来看，它仍处于**活跃维护**状态。最近一次更新（2026-05-13）距今较近，且近期的更新包含了跨平台支持（macOS）、代码质量改进和稳定性修复。

**主要特点与限制**：
*   **优点**：提供了清晰、易用的蓝图和 C++ API 封装了常用的 OpenCV 功能，降低了在 UE 中使用计算机视觉的门槛。跨平台支持（Win64, Linux, Mac）正在逐步完善。
*   **限制**：由于是 Beta 状态，API 可能在未来版本中发生变化。功能集主要针对基础的相机标定和标记检测，未涵盖 OpenCV 的全部算法。

**推荐**：如果你的项目需要上述基础计算机视觉功能，并且可以接受 Beta 状态的潜在风险，这个插件是一个很好的起点。对于生产环境，建议密切跟踪其更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenCV)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/OpenCV)