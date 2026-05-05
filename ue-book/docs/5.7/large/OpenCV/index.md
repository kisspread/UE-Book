# OpenCV

> Plugin initializing OpenCV library to be used in engine.

| 属性 | 值 |
|---|---|
| 分类 | Computer Vision |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python pip 包声明） |
| 模块 | `OpenCVHelper` (Runtime), `OpenCV` (External/ThirdParty) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-11-22 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OpenCV) | |

## 用途

这个 plugin 将 OpenCV 4.5.5 计算机视觉库集成到 Unreal Engine 中，提供相机标定、ArUco 标记检测、姿态估计等计算机视觉功能。

它主要面向 **虚拟制片 (Virtual Production)** 和 **增强现实 (AR)** 场景——当你需要让 UE 与真实摄像头交互时（例如用棋盘格标定真实相机、用 ArUco 标记追踪物理物体的位置），就需要这个 plugin。

plugin 本身是一个薄包装层，核心工作是：
1. 加载 OpenCV 的预编译二进制（opencv_world455）
2. 提供 UE 坐标系 ↔ OpenCV 坐标系的转换工具
3. 封装常用的视觉算法为 UE 友好的 API（包括蓝图可调用版本）

**注意**：这是实验性 (Beta) 插件，且默认不启用。需要在插件管理器中手动启用，或在 .uproject 中添加 `"Enabled": true`。

## 使用场景

- **虚拟制片中的相机标定**：你需要标定一个真实摄像机的内参（焦距、畸变系数），然后在 UE 中模拟相同的镜头效果 → 使用棋盘格检测 + SolvePnP
- **AR 标记追踪**：你在真实场景中放置了 ArUco 标记板，需要让 UE 中的虚拟物体精确对齐到标记位置 → 使用 ArUco 检测 + 姿态估计
- **镜头畸变校正/模拟**：你有一组镜头畸变参数，需要在 UE 中应用或去除畸变 → 使用 `FOpenCVLensDistortionParametersBase`
- **3D-2D 点对应计算**：你需要将 3D 世界坐标投影到 2D 图像平面，或反过来从 2D 像素坐标反算 3D 姿态 → 使用 `SolvePnP` / `ProjectPoints`

## 蓝图用法

这个 plugin 提供了 `UOpenCVBlueprintFunctionLibrary` 蓝图函数库，包含两个核心节点。所有蓝图函数都要求输入 `TextureRenderTarget2D` 且格式必须为 **RGBA8**。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenCV Chessboard Detect Corners` | 检测棋盘格标定图案的内角点 | `UOpenCVBlueprintFunctionLibrary` |
| `OpenCV ArUco Detect Markers` | 检测图像中所有 ArUco 标记，可选估计 3D 姿态 | `UOpenCVBlueprintFunctionLibrary` |

### 棋盘格角点检测

检测输入图像中的棋盘格标定图案，输出所有内角点的 2D 坐标。

**参数说明：**

| 参数 | 类型 | 说明 |
|---|---|---|
| `InRenderTarget` | `UTextureRenderTarget2D*` | 输入图像（必须为 RGBA8 格式） |
| `InPatternSize` | `FIntPoint` | 棋盘格内角点数（列数, 行数） |
| `bDebugDrawCorners` | `bool` | 是否输出带角点标注的调试图 |
| `OutDebugTexture` | `UTexture2D*&` | 调试图输出（仅当 bDebugDrawCorners=true） |
| `OutDetectedCorners` | `TArray<FVector2D>&` | 检测到的角点坐标 |
| **返回值** | `int32` | 检测到的角点总数 |

### ArUco 标记检测

检测图像中的 ArUco 标记，可选地估计每个标记相对于相机的 3D 位姿。

**参数说明：**

| 参数 | 类型 | 说明 |
|---|---|---|
| `InRenderTarget` | `UTextureRenderTarget2D*` | 输入图像（必须为 RGBA8 格式） |
| `InDictionary` | `EOpenCVArucoDictionary` | 字典类型：4x4 / 5x5 / 6x6 / 7x7 / Original |
| `InDictionarySize` | `EOpenCVArucoDictionarySize` | 字典大小：50 / 100 / 250 / 1000 |
| `bDebugDrawMarkers` | `bool` | 是否输出带标记框/姿态轴的调试图 |
| `bEstimatePose` | `bool` | 是否估计 3D 姿态 |
| `InMarkerLengthInMeters` | `float` | 物理标记边长（米），姿态估计时必填 |
| `InLensDistortionParameters` | `FOpenCVLensDistortionParametersBase` | 镜头畸变参数，姿态估计时使用 |
| `OutDebugTexture` | `UTexture2D*&` | 调试图输出 |
| `OutDetectedMarkers` | `TArray<FOpenCVArucoDetectedMarker>&` | 检测结果（Id + 归一化角点 + 姿态） |
| **返回值** | `int32` | 检测到的标记数 |

### 蓝图数据类型

**`FOpenCVArucoDetectedMarker`**（BlueprintType）：

| 属性 | 类型 | 说明 |
|---|---|---|
| `Id` | `int32` | 标记 ID |
| `Corners` | `TArray<FVector2D>` | 四个角点坐标（归一化到 [0,1]） |
| `Pose` | `FTransform` | 标记 3D 姿态（仅当 bEstimatePose=true） |

**`FOpenCVLensDistortionParametersBase`**（BlueprintType）：

| 属性 | 类型 | 说明 |
|---|---|---|
| `K1` - `K6` | `float` | 径向畸变系数 |
| `P1`, `P2` | `float` | 切向畸变系数 |
| `F` | `FVector2D` | 归一化焦距 (Fx, Fy) |
| `C` | `FVector2D` | 归一化主点 (Cx, Cy) |
| `bUseFisheyeModel` | `bool` | 是否使用鱼眼模型（仅用 K1-K4） |

### 使用示例（蓝图描述）

**棋盘格标定流程：**
1. 创建一个 SceneCapture2D 组件，设置为 RGBA8 格式
2. 对准物理棋盘格拍摄一帧到 RenderTarget2D
3. 调用 `OpenCV Chessboard Detect C`，传入棋盘格内角点数（如 9x6），设 `bDebugDrawCorners=true`
4. 从 `OutDetectedCorners` 获取角点坐标，`OutDebugTexture` 获取调试图
5. 多次拍摄后，用这些角点数据配合 C++ 的 `SolvePnP` 计算相机参数

**ArUco 标记追踪流程：**
1. SceneCapture2D 拍摄包含 ArUco 标记的场景
2. 调用 `OpenCV ArUco Detect Markers`，设置字典为 4x4、大小 50、`bEstimatePose=true`
3. 传入物理标记边长（如 0.1 米）和镜头畸变参数
4. 从 `OutDetectedMarkers` 获取每个标记的 ID、角点和 Pose
5. 将 Pose 应用到场景中的虚拟物体上

## C++ 用法

### 头文件引入

```cpp
#include "OpenCVHelper.h"
#include "OpenCVBlueprintFunctionLibrary.h"
```

如果需要直接调用 OpenCV API，必须用特定的头文件包裹方式：

```cpp
#include "PreOpenCVHeaders.h"
#include "opencv2/aruco.hpp"
#include "opencv2/calib3d.hpp"
#include "opencv2/imgproc.hpp"
#include "PostOpenCVHeaders.h"
```

> **重要**：不能直接 `#include <opencv2/...>`，必须用 `PreOpenCVHeaders.h` / `PostOpenCVHeaders.h` 包裹，否则会因为 UE 的宏定义与 OpenCV 头文件冲突导致编译错误。在 Linux 平台上还有 `(u)int64` 类型冲突，需要使用 `OpenCVUtils::int64`。

### 坐标系转换

UE 和 OpenCV 使用不同的坐标系，`FOpenCVHelper` 提供了转换工具：

```cpp
// UE 坐标系: X=前, Y=右, Z=上
// OpenCV 坐标系: Z=前, X=右, Y=下(取反)

// 转换 FTransform
FTransform Pose = /* ... */;
FOpenCVHelper::ConvertUnrealToOpenCV(Pose);  // UE → OpenCV
FOpenCVHelper::ConvertOpenCVToUnreal(Pose);  // OpenCV → UE

// 转换 FVector
FVector Pos(100, 200, 300);
FVector CvPos = FOpenCVHelper::ConvertUnrealToOpenCV(Pos);  // → (200, -300, 100)
```

### 棋盘格检测（C++ 版）

```cpp
// 输入：BGRA8 格式的 FColor 数组
TArray<FColor> Image = /* 从相机获取 */;
FIntPoint ImageSize(1920, 1080);
FIntPoint CheckerboardSize(9, 6); // 9列 x 6行内角点

TArray<FVector2f> Corners;
bool bFound = FOpenCVHelper::IdentifyCheckerboard(Image, ImageSize, CheckerboardSize, Corners);

if (bFound)
{
    // Corners 包含 54 个角点的 2D 坐标
    // 可以传给 DrawCheckerboardCorners 进行调试可视化
    UTexture2D* DebugTexture = /* ... */;
    FOpenCVHelper::DrawCheckerboardCorners(Corners, CheckerboardSize, DebugTexture);
}
```

支持指定感兴趣区域（ROI）：

```cpp
FIntRect ROI(100, 100, 1820, 980);
bool bFound = FOpenCVHelper::IdentifyCheckerboard(Image, ImageSize, ROI, CheckerboardSize, Corners);
```

### ArUco 标记检测（C++ 版）

```cpp
TArray<FColor> Image = /* ... */;
FIntPoint ImageSize(1920, 1080);
EArucoDictionary Dict = EArucoDictionary::DICT_4X4_50;

TArray<FArucoMarker> Markers;
bool bFound = FOpenCVHelper::IdentifyArucoMarkers(Image, ImageSize, Dict, Markers);

for (const FArucoMarker& Marker : Markers)
{
    int32 ID = Marker.MarkerID;
    FVector2f TopLeft  = Marker.Corners[0];
    FVector2f TopRight = Marker.Corners[1];
    FVector2f BotRight = Marker.Corners[2];
    FVector2f BotLeft  = Marker.Corners[3];
}
```

### SolvePnP：从 2D-3D 对应关系求相机姿态

```cpp
// 已知 3D 世界坐标点和对应的 2D 图像坐标点
TArray<FVector> ObjectPoints;   // 3D 点（UE 坐标系）
TArray<FVector2f> ImagePoints;  // 2D 像素坐标
FVector2D FocalLength(1000.0, 1000.0);
FVector2D ImageCenter(960.0, 540.0);
TArray<float> DistortionParams; // 畸变系数（0/4/5/8/12/14 个）

FTransform CameraPose;
bool bSuccess = FOpenCVHelper::SolvePnP(
    ObjectPoints, ImagePoints,
    FocalLength, ImageCenter, DistortionParams,
    CameraPose
);
// CameraPose 现在包含相机在 UE 世界坐标系中的位姿
```

> **注意**：SolvePnP 要求至少 **6 个** 3D/2D 点对应关系（非平面点集），畸变参数数量必须是 0、4、5、8、12 或 14 之一。

### ProjectPoints：将 3D 点投影到 2D 图像平面

```cpp
TArray<FVector> ObjectPoints = /* 3D 点 */;
FTransform CameraPose = /* 相机位姿 */;
FVector2D FocalLength(1000.0, 1000.0);
FVector2D ImageCenter(960.0, 540.0);
TArray<float> DistortionParams;

TArray<FVector2f> ImagePoints;
FOpenCVHelper::ProjectPoints(ObjectPoints, FocalLength, ImageCenter,
                              DistortionParams, CameraPose, ImagePoints);
// ImagePoints 包含投影后的 2D 像素坐标
```

### 重投影误差计算

用于评估标定质量——将 3D 点投影到 2D 后与实际检测到的 2D 点之间的欧氏距离：

```cpp
double Error = FOpenCVHelper::ComputeReprojectionError(
    ObjectPoints, ImagePoints,
    FocalLength, ImageCenter, CameraPose
);
// Error 越小表示标定越精确
```

### 镜头畸变参数

`FOpenCVLensDistortionParametersBase` 可以直接转换为 OpenCV 矩阵格式：

```cpp
FOpenCVLensDistortionParametersBase Params;
Params.K1 = -0.28f;
Params.K2 = 0.07f;
Params.F = FVector2D(1.0, 1.0);  // 归一化焦距
Params.C = FVector2D(0.5, 0.5);  // 归一化主点

#if WITH_OPENCV
cv::Mat DistortionCoeffs = Params.ConvertToOpenCVDistortionCoefficients();
cv::Mat CameraMatrix = Params.CreateOpenCVCameraMatrix(FVector2D(1920, 1080));
#endif
```

### 纹理转换：cv::Mat → UTexture2D

```cpp
#if WITH_OPENCV
cv::Mat Mat = /* OpenCV 处理结果 */;

// 创建新纹理
UTexture2D* Texture = FOpenCVHelper::TextureFromCvMat(Mat);

// 写入已有纹理（匹配尺寸和格式时复用）
UTexture2D* ExistingTexture = /* ... */;
FOpenCVHelper::TextureFromCvMat(Mat, ExistingTexture);

// 在编辑器中保存到包
FString PackagePath = TEXT("/Game/Textures/MyCvTexture");
FName TextureName = TEXT("MyCvTexture");
UTexture2D* SavedTexture = FOpenCVHelper::TextureFromCvMat(Mat, &PackagePath, &TextureName);
#endif
```

支持的像素格式：单通道 G8（灰度）和四通道 BGRA8。

## Demo 示例

### 完整的最小 ArUco 检测示例

**Build.cs：**

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "OpenCVHelper"
});
```

**MyArucoDetector.h：**

```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OpenCVHelper.h"
#include "MyArucoDetector.generated.h"

UCLASS()
class AMyArucoDetector : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "ArUco")
    EArucoDictionary Dictionary = EArucoDictionary::DICT_4X4_50;

    void DetectFromImage(TArray<FColor>& Image, FIntPoint Size);

private:
    TArray<FArucoMarker> DetectedMarkers;
};
```

**MyArucoDetector.cpp：**

```cpp
#include "MyArucoDetector.h"
#include "Engine/Texture2D.h"

void AMyArucoDetector::DetectFromImage(TArray<FColor>& Image, FIntPoint Size)
{
    if (FOpenCVHelper::IdentifyArucoMarkers(Image, Size, Dictionary, DetectedMarkers))
    {
        for (const FArucoMarker& Marker : DetectedMarkers)
        {
            UE_LOG(LogTemp, Log, TEXT("Detected ArUco marker ID: %d"), Marker.MarkerID);
            UE_LOG(LogTemp, Log, TEXT("  TopLeft: (%.1f, %.1f)"),
                Marker.Corners[0].X, Marker.Corners[0].Y);
        }
    }
}
```

### 相机标定流水线

```cpp
// 1. 从多个角度拍摄棋盘格
for (int i = 0; i < NumImages; ++i)
{
    TArray<FColor> Image = CaptureImage();
    TArray<FVector2f> Corners;

    if (FOpenCVHelper::IdentifyCheckerboard(Image, ImageSize, CheckerboardDims, Corners))
    {
        AllImageCorners.Add(Corners);
        // 生成对应的 3D 世界坐标（棋盘格平面 Z=0）
        // 然后调用 cv::calibrateCamera() 或多次 SolvePnP
    }
}

// 2. 用 SolvePnP 求每帧的相机姿态
FTransform Pose;
FOpenCVHelper::SolvePnP(ObjectPoints, ImagePoints, FocalLength, ImageCenter, {}, Pose);

// 3. 验证标定质量
double Error = FOpenCVHelper::ComputeReprojectionError(
    ObjectPoints, ImagePoints, FocalLength, ImageCenter, Pose);
UE_LOG(LogTemp, Log, TEXT("Reprojection error: %f"), Error);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Texture2D、RenderTarget 等） |
| `OpenCV` | 第三方 OpenCV 4.5.5 外部模块（提供头文件 + 预编译库） |
| `Projects` | 项目配置查询 |

如果要在自己的模块中使用 OpenCV Helper，需要在 Build.cs 中添加 `"OpenCVHelper"` 依赖。

## 平台支持

| 平台 | 状态 | 备注 |
|---|---|---|
| Win64 (x64) | ✅ 支持 | 使用 opencv_world455.dll，Debug 构建使用 455d 版本 |
| Win64 (Arm64) | ✅ 支持 | 禁用了 NEON intrinsics |
| Linux | ✅ 支持 | 使用 libopencv_world.so |
| Mac | ⚠️ 声明支持 | .uplugin 列出但未见预编译二进制 |
| 其他平台 | ❌ 不支持 | WITH_OPENCV 定义为 0 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-10 | `9803c44` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 自动化工具批量添加的代码规范化改动，无功能变化 |
| 2025-06-25 | `a64dda9` | PythonFoundationPackages: Fix for incorrect dependency specification in OpenCV | 修复 Python 依赖声明，确保 opencv-python pip 包正确安装 |
| 2025-06-20 | `35f8ecb` | Move Torch python requirements to separate PythonMLPackages plugin | Python 依赖管理重构，将 Torch 相关需求分离到独立 plugin |

### 维护评价

- **创建时间**：2021 年 11 月，约 4 年历史
- **活跃程度**：最近的更新（2025 年 6-7 月）主要是构建系统维护和 Python 依赖修复，**无功能性更新**
- **OpenCV 版本**：捆绑的是 OpenCV **4.5.5**（2021 年发布），当前 OpenCV 已到 4.10+，版本明显过时
- **Beta 状态**：`.uplugin` 标记 `IsBetaVersion: true`，4 年来一直未摘除 Beta 标签
- **API 覆盖**：仅暴露了很小一部分 OpenCV 功能（ArUco 检测、棋盘格检测、SolvePnP、ProjectPoints、FitLine），如果需要其他 OpenCV 功能需要直接调用 C++ API
- **蓝图功能**：仅有 2 个蓝图节点，C++ API 更丰富但不暴露给蓝图

**综合评价**：这是一个功能有限但对虚拟制片场景足够用的轻量封装。如果你只需要棋盘格标定和 ArUco 标记检测，它开箱即用。如果需要更广泛的 OpenCV 功能，建议直接在项目中集成 OpenCV 或使用社区维护的 UE OpenCV 插件（如 UnrealEnginePython/OpenCV）。Beta 标签和过时的 OpenCV 版本表明 Epic 将此插件视为低优先级维护项。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OpenCV)
- 官方文档：无（.uplugin 的 DocsURL 为空）
