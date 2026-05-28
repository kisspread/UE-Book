# Led Wall Calibration

> Tools for Led Wall calibration

| 属性 | 值 |
|---|---|
| 中文名 | LED墙校准 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `LedWallCalibration` (Runtime), `LedWallCalibrationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-08-03 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProduction/LedWallCalibration) | |

## 用途

该插件是 **Virtual Production (虚拟制作)** 工作流的一部分，专门用于 **LED 虚拟拍摄**场景中的 **LED 墙校准**。它解决了在大型 LED Volume（如 xR/虚拟制片影棚）中，精确校准物理 LED 面板与虚拟相机视角之间的几何映射关系的问题。

核心功能是利用 **ArUco 标记**（一种常用于计算机视觉的二维码标记）和 **OpenCV** 库，为 LED 墙的物理面板生成对应的校准图案。通过分析这些图案，可以计算出 LED 面板在世界空间中的精确位置和方向，从而实现虚拟相机与物理 LED 屏幕的完美对齐，确保演员看到的虚拟环境透视关系正确无误。

它依赖于 `CameraCalibrationCore` 插件来提供底层的相机校准点组件系统，并使用 `OpenCV` 插件来实现图像处理和 ArUco 标记的生成。

## 使用场景

- **虚拟制片（Virtual Production）**：当你使用一个由多块 LED 面板组成的大型 LED 墙来充当虚拟背景时，需要精确校准每块面板，以避免画面撕裂、透视错误或视觉伪影。
- **扩展现实（xR）**：在 AR/VR/MR 的拍摄或实时渲染中，需要将真实摄像机看到的虚拟物体与 LED 墙渲染的背景精确对齐。
- **舞台设计与预览**：在规划大型 LED 屏幕的安装布局时，可以使用此工具模拟和预览不同配置下的校准效果。

## 蓝图用法

插件主要提供了一个蓝图可用的数据结构，用于配置校准过程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FLedWallArucoGenerationOptions` | (结构体) ArUco 标记生成的所有配置选项，包括纹理尺寸、字典类型、起始ID等。 | `FLedWallArucoGenerationOptions` |
| `ArucoDictionaryAsString` | (函数) 获取当前选择的 ArUco 字典的可读名称（编辑器内使用显示名，运行时使用枚举名）。 | `FLedWallArucoGenerationOptions` |

### 使用示例（蓝图描述）

1.  在你的 Actor 或蓝图中，添加一个 `UCalibrationPointComponent`。
2.  使用 `FLedWallArucoGenerationOptions` 结构体变量来配置校准参数：
    - 设置 `TextureWidth` 和 `TextureHeight` 为你 LED 灯墙渲染目标的分辨率（例如 3840x2160）。
    - 选择一个 `ArucoDictionary`（默认 `DICT_6X6_1000` 通常足够）。
    - 设置起始 `MarkerId`。
    - 调整 `PlaceModulus` 来控制标记在网格中的稀疏程度。
3.  将配置好的选项结构体传递给 `FLedWallCalibration::GenerateArucosForCalibrationPoint` 函数（C++ 环境，蓝图中可能通过其他节点封装调用）来生成校准纹理。

## C++ 用法

### 头文件引入

```cpp
#include "LedWallCalibration/Public/LedWallCalibration.h"
#include "LedWallCalibration/Public/LedWallArucoGenerationOptions.h"
```

### 基本用法

核心的静态函数 `GenerateArucosForCalibrationPoint` 负责实际的校准数据生成。

```cpp
// 引用自 Public/LedWallCalibration.h 和相关头文件

// 假设你已经有一个 UCalibrationPointComponent* CalibrationPointComp
// 例如：在某个 Actor 中获取

FLedWallArucoGenerationOptions Options;
Options.TextureWidth = 3840; // 你的LED墙渲染目标宽度
Options.TextureHeight = 2160; // 你的LED墙渲染目标高度
Options.MarkerId = 1; // 起始标记ID

int32 NextMarkerId = 0;
cv::Mat GeneratedMat;

// 调用生成函数
bool bSuccess = FLedWallCalibration::GenerateArucosForCalibrationPoint(
    CalibrationPointComp,
    Options,
    NextMarkerId, // 输出下一个可用的标记ID，可用于为多个网格连续生成
    GeneratedMat  // 输出生成的OpenCV Mat，包含ArUco标记图像
);

if (bSuccess)
{
    // GeneratedMat 现在包含了校准图案。
    // 你可以将其转换为 UTexture2D 并应用到 LED 墙的渲染目标上。
    // 使用 cv::imwrite 可以将其保存为文件用于调试。
    // cv::imwrite("D:\\CalibrationPattern.png", GeneratedMat);
}
```

### 进阶用法

`GetTypedParentComponent` 模板函数是一个有用的工具，用于在组件层级中查找特定类型的父组件，这在处理复杂的 Actor 结构时很方便。

```cpp
// 查找 CalibrationPointComp 的父级中，第一个是 UStaticMeshComponent 的组件
// 这在 GenerateArucosForCalibrationPoint 内部逻辑中有所体现，它期望父组件是网格体
UStaticMeshComponent* ParentMesh = FLedWallCalibration::GetTypedParentComponent<UStaticMeshComponent>(CalibrationPointComp);

if (ParentMesh)
{
    // 可以对父网格体进行操作，例如获取其材质、渲染状态等
    UE_LOG(LogLedWallCalibration, Log, TEXT("Found parent static mesh: %s"), *ParentMesh->GetName());
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何集成 LED 墙校准功能。

**LedWallCalibrationDemoActor.h**
```cpp
// LedWallCalibrationDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LedWallArucoGenerationOptions.h"
#include "LedWallCalibrationDemoActor.generated.h"

class UCalibrationPointComponent;

UCLASS()
class ALedWallCalibrationDemoActor : public AActor
{
	GENERATED_BODY()

public:
	ALedWallCalibrationDemoActor();

protected:
	virtual void BeginPlay() override;

public:
	UPROPERTY(EditAnywhere, Category = "Calibration")
	FLedWallArucoGenerationOptions CalibrationOptions;

private:
	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<UCalibrationPointComponent> CalibrationPoint;
};
```

**LedWallCalibrationDemoActor.cpp**
```cpp
// LedWallCalibrationDemoActor.cpp
#include "LedWallCalibrationDemoActor.h"
#include "Components/CalibrationPointComponent.h"
#include "LedWallCalibration/Public/LedWallCalibration.h"
#include "LedWallCalibration/Public/LedWallArucoGenerationOptions.h"
#include "OpenCVHelper.h" // 通常来自 OpenCV 插件
#include "opencv2/core.hpp"
#include "opencv2/imgcodecs.hpp"

ALedWallCalibrationDemoActor::ALedWallCalibrationDemoActor()
{
	PrimaryActorTick.bCanEverTick = false;

	CalibrationPoint = CreateDefaultSubobject<UCalibrationPointComponent>(TEXT("CalibrationPoint"));
	RootComponent = CalibrationPoint;

	// 为演示设置一些默认值
	CalibrationOptions.TextureWidth = 1920;
	CalibrationOptions.TextureHeight = 1080;
	CalibrationOptions.MarkerId = 100;
}

void ALedWallCalibrationDemoActor::BeginPlay()
{
	Super::BeginPlay();

	if (CalibrationPoint)
	{
		int32 NextMarkerId;
		cv::Mat CalibrationMat;

		bool bSuccess = FLedWallCalibration::GenerateArucosForCalibrationPoint(
			CalibrationPoint,
			CalibrationOptions,
			NextMarkerId,
			CalibrationMat
		);

		if (bSuccess)
		{
			// 在实际项目中，你需要将 CalibrationMat 转换为 UTexture2D。
			// 这里我们仅将其保存到磁盘作为示例。
			// 确保路径可写，并注意 cv::imwrite 的编码格式支持。
			std::string SavePath = TCHAR_TO_UTF8(*FPaths::ProjectSavedDir()) + "/CalibrationPattern.png";
			cv::imwrite(SavePath, CalibrationMat);
			UE_LOG(LogTemp, Log, TEXT("Calibration pattern saved to: %hs"), SavePath.c_str());
		}
		else
		{
			UE_LOG(LogTemp, Warning, TEXT("Failed to generate calibration pattern."));
		}
	}
}
```

## 模块依赖

使用此插件，你的模块需要在 `Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `CameraCalibrationCore` | 提供校准点组件 (`UCalibrationPointComponent`) 的核心功能，是本插件的基础。 |
| `OpenCVHelper` | 提供 OpenCV 的 UE 封装，包括 `EArucoDictionary` 枚举等。 |
| `OpenCV` | 底层的 OpenCV 计算机视觉库。 |

**注意**：由于此插件 `EnabledByDefault` 为 `false`，你还需要在项目的 `.uproject` 文件或插件设置中显式启用 `LedWallCalibration` 和它的依赖项 `CameraCalibrationCore` 和 `OpenCV`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 更新日志系统，将UE_LOG宏迁移到新的UE_LOGF格式。 |
| 2026-01-22 | `ad8a0de1` | Update BuildVersionSettings that are out of date | 更新过时的构建版本设置，确保编译配置与引擎版本匹配。 |
| 2025-05-21 | `269aeb1b` | Replaced bool arguments with EFindObjectFlags. | 改进查找逻辑，用枚举标志替代布尔参数，代码更清晰健壮。 |
| 2023-08-29 | `3a058044` | CameraCalibration: Refactor opencv implementation details out of the camera calibration plugins and ... | 重大重构，将OpenCV实现细节从相机校准插件中抽离，提升模块化。 |
| 2023-07-19 | `574e8e6e` | Add a ShortName to modules that generated paths over the 200 chars limit and a few modules that were ... | 为路径过长的模块添加简短名称，解决潜在的构建和引用问题。 |

### 维护评价

- **创建时间**：2021 年 8 月，作为 UE5 早期实验性功能发布。
- **最近更新**：最近几次更新（2025-2026）主要是**编译修复和内部重构**（如日志系统迁移、构建设置更新），并未增加新功能。最后一次**功能性更新**（ArUco 校准核心逻辑的重构）发生在 **2023 年 8 月**。
- **活跃度**：插件处于 **维护不活跃** 状态。虽然近期有代码维护，但已有超过 **2 年**没有新的功能特性提交。
- **状态**：插件标记为 **实验性（IsBetaVersion: true）** 且 **默认未启用**，表明 Epic 可能认为其功能和 API 尚未完全稳定。
- **推荐使用**：**谨慎推荐**。对于**新项目**或需要稳定长期支持的功能，应考虑寻找替代方案或自行实现。对于**研究、实验或短期项目**，且确实需要快速集成基于 OpenCV 的 LED 墙校准功能，该插件仍可作为有价值的参考或起点。使用前务必评估其与当前 UE 版本的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProduction/LedWallCalibration)
- 官方文档：（暂无）
- 测试用例：（在提供的源码路径中未找到独立的测试文件）