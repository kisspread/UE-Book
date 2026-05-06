# Led Wall Calibration

> Tools for Led Wall calibration

| 属性 | 值 |
|---|---|
| 中文名 | LED 墙校准 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资源） |
| 模块 | `LedWallCalibration` (Runtime), `LedWallCalibrationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/LedWallCalibration) | |

## 用途

该插件提供工具用于 LED 虚拟墙（LED Wall）的自动校准。它利用 OpenCV 的 ArUco 标记生成技术，根据 LED 面板的几何结构（三角形排列），在每个面板上生成唯一的 ArUco 标记，并将这些标记的位置信息写入 `UCalibrationPointComponent`，从而为后续的相机校准提供精确的特征点。

解决的问题：
- 手动标记 LED 墙的校准点耗时且易出错
- 需要一种自动化的方式将 ArUco 标记与 LED 面板的物理位置对齐
- 支持大规模 LED 墙（多个面板）的批量标记生成

## 使用场景

- 虚拟制作（Virtual Production）中，搭建 LED 墙作为背景屏幕时，需要快速生成校准图案并建立相机与屏幕的空间关系。
- 当你使用 `CameraCalibrationCore` 插件进行相机内参与外参标定时，需要 LED 墙上的已知校准点。
- 需要为不同分辨率和 ArUco 字典生成包含连续 ID 的标记纹理，并导出为图片或直接应用于纹理。

## 蓝图用法

该运行时模块主要提供数据结构，核心计算函数无 `BlueprintCallable` 标记，因此无法直接在蓝图中调用。不过 `FLedWallArucoGenerationOptions` 是 `USTRUCT(BlueprintType)`，可以在蓝图中创建、修改并传递给 C++ 函数（通常由编辑器模块调用）。

### 核心结构

| 属性 | 类型 | 说明 |
|------|------|------|
| `TextureWidth` / `TextureHeight` | int32 | 生成的纹理尺寸（默认 3840×2160） |
| `ArucoDictionary` | EArucoDictionary | 使用的 ArUco 字典（默认 6x6_1000） |
| `MarkerId` | int32 | 起始标记 ID（默认 1） |
| `PlaceModulus` | int32 | 控制标记放置密度（默认 2） |

## C++ 用法

### 头文件引入

```cpp
#include "LedWallCalibration.h"
#include "LedWallArucoGenerationOptions.h"
#include "CalibrationPointComponent.h" // 来自 CameraCalibrationCore
#include "OpenCVHelper.h"             // 用于 cv::Mat
```

### 基本用法

以下示例展示如何为网格体上的校准点生成 ArUco 标记纹理：

```cpp
// 假设已经拥有一个 UCalibrationPointComponent* MyCalPoint
// 该组件挂载在一个 UStaticMeshComponent 下，该网格体代表 LED 面板

FLedWallArucoGenerationOptions Options;
Options.TextureWidth = 1920;
Options.TextureHeight = 1080;
Options.ArucoDictionary = EArucoDictionary::DICT_4X4_50;
Options.MarkerId = 0;
Options.PlaceModulus = 2;

int32 NextId = Options.MarkerId;
cv::Mat OutMat;

bool bSuccess = FLedWallCalibration::GenerateArucosForCalibrationPoint(
    MyCalPoint,
    Options,
    NextId,
    OutMat
);

if (bSuccess)
{
    // OutMat 包含生成的 ArUco 纹理，可以保存为图片或创建 UTexture2D
    // NextId 是下一个可用的标记 ID，可用于继续生成其他网格体
}
```

**来源文件**: `LedWallCalibration.h`

### 进阶用法

多面板连续生成：

```cpp
// 遍历多个网格体，每个网格体都包含一个 UCalibrationPointComponent
int32 NextAvailableId = 1;

for (UStaticMeshComponent* PanelMesh : AllPanelMeshes)
{
    UCalibrationPointComponent* CalPoint = PanelMesh->FindComponentByClass<UCalibrationPointComponent>();
    if (!CalPoint) continue;

    FLedWallArucoGenerationOptions Options;
    Options.MarkerId = NextAvailableId;
    Options.PlaceModulus = 1; // 每个三角面都放置标记

    cv::Mat MatForPanel;
    bool bOK = FLedWallCalibration::GenerateArucosForCalibrationPoint(
        CalPoint, Options, NextAvailableId, MatForPanel
    );
    // 可以保存 MatForPanel 或合并到一张大纹理中
}
```

### 辅助函数

获取校准点组件的父级网格体组件：

```cpp
UStaticMeshComponent* ParentMesh = FLedWallCalibration::GetTypedParentComponent<UStaticMeshComponent>(MyCalPoint);
if (ParentMesh)
{
    // 处理网格体数据
}
```

## Demo 示例

以下是一个完整的 C++ 函数，演示了如何为单一面板生成 ArUco 纹理并将其转换为 UTexture2D（需在游戏线程执行）：

```cpp
// MyCalibrationActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCalibrationActor.generated.h"

UCLASS()
class AMyCalibrationActor : public AActor
{
    GENERATED_BODY()
public:
    // 调用此函数以生成纹理
    void GenerateAndApplyTexture();
};

// MyCalibrationActor.cpp
#include "MyCalibrationActor.h"
#include "LedWallCalibration.h"
#include "LedWallArucoGenerationOptions.h"
#include "CalibrationPointComponent.h"
#include "CameraCalibrationCore/Private/CalibrationPointComponent.h" // 示例路径，实际需要正确 include
#include "Engine/Texture2D.h"
#include "Rendering/Texture2DResource.h"

void AMyCalibrationActor::GenerateAndApplyTexture()
{
    // 假设本 Actor 包含一个 UCalibrationPointComponent 子组件
    UCalibrationPointComponent* CalPoint = FindComponentByClass<UCalibrationPointComponent>();
    if (!CalPoint) return;

    FLedWallArucoGenerationOptions Options;
    // 默认值足够

    int32 NextMarkerId = 1;
    cv::Mat Mat;

    bool bSuccess = FLedWallCalibration::GenerateArucosForCalibrationPoint(
        CalPoint, Options, NextMarkerId, Mat
    );
    if (!bSuccess) return;

    // 将 cv::Mat 转为 UTexture2D（简化，实际需要处理颜色空间和内存）
    UTexture2D* Texture = UTexture2D::CreateTransient(Mat.cols, Mat.rows, PF_B8G8R8A8);
    if (!Texture) return;

    FTexture2DMipMap& Mip = Texture->PlatformData->Mips[0];
    void* Data = Mip.BulkData.Lock(LOCK_READ_WRITE);
    // 复制 Mat 数据（假设 8 位 BGRA）
    memcpy(Data, Mat.data, Mat.total() * Mat.elemSize());
    Mip.BulkData.Unlock();
    Texture->UpdateResource();

    // 接下来可将纹理应用到某个材质上
}
```

## 模块依赖

使用 `LedWallCalibration` 模块时，你的模块需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|------|------|
| `CameraCalibrationCore` | 提供 `UCalibrationPointComponent` 类型和校准框架 |
| `OpenCV` | 提供 ArUco 字典及 OpenCV 矩阵操作 |
| `OpenCVHelper` | 提供 `EArucoDictionary` 枚举等辅助类型 |

```cpp
// 在你的模块 Build.cs 中
PublicDependencyModuleNames.AddRange(new string[] {
    "CameraCalibrationCore",
    "OpenCV",
    "OpenCVHelper"
});
```

**其他常见依赖（省略）**：Core, CoreUObject, Engine。

## 维护状态

### 近期更新

- 2025-05-21 `269aeb1b` Replaced bool arguments with EFindObjectFlags
- 2023-08-29 `3a058044` CameraCalibration: Refactor opencv implementation details out of the camera calibration plugins
- 2023-07-19 `574e8e6e` Add a ShortName to modules that generated paths over the 200 chars limit
- 2023-04-15 `933348f8` Use the FMessageDialog overloads that pass the optional title by-value
- 2023-01-27 `f9121212` Added generated.h includes and updated enums to have underlying types

### 维护评价

该插件仍处于实验阶段（Beta），自 2023 年初创建以来，经历了多次重构（OpenCV 实现细节抽离、编码风格调整），最近一次更新在 2025 年 5 月，表明项目并非被放弃。但由于其功能与特定硬件和工作流强相关，更新频率不高。已知限制：
- 生成逻辑假设 LED 网格体以三角形面板排列（3个顶点一个面板），需确保模型符合此结构
- 编辑器模块提供了界面，但运行时模块无法直接通过蓝图调用
- 依赖于外部 OpenCV 库，可能增加编译体积

总体而言，若你正在构建虚拟制作 LED 墙校准流程，该插件可大幅减少手动工作量，推荐使用；但需注意其 Beta 状态和模型结构要求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/LedWallCalibration)
- [官方文档](https://docs.unrealengine.com/5.3/en-US/led-wall-calibration-in-unreal-engine/)（假设存在，插件描述未提供 DocsURL）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/LedWallCalibration/Tests)（若有）