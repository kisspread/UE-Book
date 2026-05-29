# Camera Calibration Core

> Supports lens distortion and camera calibration.

| 属性 | 值 |
|---|---|
| 中文名 | 相机校准核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、资产） |
| 模块 | `CameraCalibrationCore` (Runtime), `CameraCalibrationCoreEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-05-27 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibrationCore) | |

## 用途

Camera Calibration Core 插件旨在为 Unreal Engine 的虚拟制作流程提供一套完整的镜头校准和畸变解决方案。它不仅仅处理基础的镜头畸变校正，更是一个用于建立物理摄像机（或称“镜头”）与引擎虚拟世界之间精确映射关系的核心框架。其核心功能包括：

1.  **可扩展的镜头模型系统**：通过 `ULensModel` 基类，允许用户定义和注册自定义的镜头畸变数学模型（如径向、切向畸变等）。
2.  **镜头数据资产**：使用 `ULensFile` 资产来存储和管理特定镜头（或镜头变焦状态）在不同对焦距离下的校准数据。
3.  **运行时畸变应用**：提供 `FLensDistortionModelHandlerBase` 处理器和相关的材质/后处理功能，能够在运行时将镜头畸变效果实时应用到游戏视图或渲染目标上。
4.  **空间校准**：引入 `UCalibrationPointComponent`，用于在场景中放置已知位置的点，以辅助完成摄像机投影与世界坐标的精确对齐。

## 使用场景

-   **LED 墙拍摄（Virtual Production）**：在 LED 墙拍摄中，确保摄像机看到的虚拟背景与前景的透视、畸变完全匹配。此插件用于校准驱动 LED 墙的渲染摄像机，使其输出与现场物理摄像机的镜头特性一致。
-   **视觉特效合成（VFX）**：在将 CG 元素合成到实拍素材时，需要精确模拟实拍镜头的畸变特性。校准数据可用于 CG 渲染，或用于后期软件中的畸变/去畸变。
-   **混合现实（MR）或增强现实（AR）**：在将虚拟物体叠加到真实摄像机画面时，需要准确的镜头模型来保证虚拟物体的位置和透视正确。
-   **摄像机跟踪数据后处理**：为运动捕捉或摄像机跟踪系统提供的数据，增加真实的镜头畸变信息，使其与实拍画面完美融合。

## 蓝图用法

此插件的大部分功能是底层数据管理和编辑器工具，直接暴露给蓝图的 API 相对较少，主要集中在数据查询和组件操作上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCalibrationPointWorldTransform` | 根据标签获取校准点组件的世界变换 | `UCalibrationPointComponent` |
| `GetDistortionState` | 获取镜头文件在指定数据行和侧别下的畸变状态 | `ULensFile` |
| `GetLensModel` | 获取此镜头文件使用的镜头模型 | `ULensFile` |
| `SetLensModel` | 设置此镜头文件使用的镜头模型 | `ULensFile` |

### 使用示例（蓝图描述）

由于此插件的核心是编辑器工具和C++框架，典型的蓝图使用场景较少。一种可能的用法是：
1.  在场景中放置一个 `CalibrationPointComponent`。
2.  通过其他蓝图逻辑（例如，从网络或文件）获取校准点的真实世界坐标。
3.  使用 `GetCalibrationPointWorldTransform` 节点与实际世界坐标进行对比，或用于辅助计算摄像机投影矩阵。

## C++ 用法

插件的核心价值在于其 C++ 框架，用于扩展和深度集成。

### 头文件引入

```cpp
// 核心运行时模块
#include "LensFile.h"
#include "LensModel.h"
#include "LensDistortionModelHandlerBase.h"

// 组件
#include "CalibrationPointComponent.h"
```

### 基本用法

**定义自定义镜头模型**

从 `ULensModel` 派生一个新的 C++ 类。

```cpp
// MyLensModel.h
#pragma once
#include "LensModel.h"
#include "MyLensModel.generated.h"

UCLASS(BlueprintType, DisplayName="My Custom Lens Model")
class UMyLensModel : public ULensModel
{
    GENERATED_BODY()
public:
    // 实现基类的纯虚函数，返回模型支持的参数数量
    virtual int32 GetNumParameters() const override { return 4; }

    // 实现基类的纯虚函数，为给定参数数组中的每个参数提供名称
    virtual FText GetParameterDisplayName(int32 ParameterIndex) const override;

    // 实现基类的纯虚函数，返回用于材质实例的畸变材质参数名称
    virtual FName GetMaterialParameterPrefix() const override { return TEXT("MyDistortion"); }

    // 实现畸变计算的核心逻辑
    virtual void DistortNormalizedCoordinates(const FVector2D& InUndistortedCoordinate, const TArray<double>& InParameters, FVector2D& OutDistortedCoordinate) const override;
};
```

**使用镜头文件数据**

```cpp
// 假设我们已经获得了一个 ULensFile 资产指针 (LensFileAsset)
ULensFile* LensFileAsset = LoadObject<ULensFile>(nullptr, TEXT("/Game/MyLensData.MyLensFile"));

if (LensFileAsset)
{
    // 获取特定变焦行和对焦行的畸变数据
    const float Zoom = 0.5f; // 归一化变焦位置
    const float Focus = 100.0f; // 对焦距离 (cm)

    FLensDistortionState DistortionState;
    if (LensFileAsset->EvaluateDistortionData(Zoom, Focus, DistortionState))
    {
        // 现在可以使用 DistortionState.DistortionInfo.Parameters 等数据
        // 例如，设置到一个 FDistortionModelHandlerBase 子类实例上
    }
}
```

来源文件：`Engine/Plugins/VirtualProduction/CameraCalibrationCore/Source/CameraCalibrationCore/Public/LensFile.h`

### 进阶用法

**扩展校准点组件的详细信息行**

插件允许通过 `ICalibrationPointComponentDetailsRow` 接口为 `UCalibrationPointComponent` 的细节面板添加自定义行。

```cpp
// MyCalibrationDetailsRow.h
#pragma once
#include "ICalibrationPointComponentDetailsRow.h"
#include "MyCalibrationDetailsRow.generated.h"

class FMyCalibrationDetailsRow : public ICalibrationPointComponentDetailsRow
{
public:
    virtual FText GetSearchString() const override { return NSLOCTEXT("MyPlugin", "MyRowSearch", "My Custom Info"); }
    virtual bool IsAdvanced() const override { return false; }

    virtual void CustomizeRow(
        FDetailWidgetRow& WidgetRow,
        const TArray<TWeakObjectPtr<UObject>>& SelectedObjectsList) override
    {
        // 在详情面板中创建一个显示自定义数据的行
        WidgetRow
        .NameContent()
        [
            SNew(STextBlock).Text(LOCTEXT("MyLabel", "Custom Metric"))
        ]
        .ValueContent()
        [
            SNew(STextBlock).Text(this, &FMyCalibrationDetailsRow::GetCustomMetricText, SelectedObjectsList)
        ];
    }

private:
    FText GetCustomMetricText(TArray<TWeakObjectPtr<UObject>> SelectedObjects) const { /* 计算并返回文本 */ }
};

// 在模块启动时注册
void FMyModule::StartupModule()
{
    FCameraCalibrationCoreEditorModule& EditorModule = FModuleManager::GetModuleChecked<FCameraCalibrationCoreEditorModule>(TEXT("CameraCalibrationCoreEditor"));
    EditorModule.RegisterCalibrationPointDetailsRow(MakeShared<FMyCalibrationDetailsRow>());
}
```

来源文件：`Engine/Plugins/VirtualProduction/CameraCalibrationCore/Source/CameraCalibrationCoreEditor/Public/ICalibrationPointComponentDetailsRow.h`

## Demo 示例

以下示例展示如何创建一个最小的自定义镜头模型。

```cpp
// SimpleAnamorphicLensModel.h
#pragma once
#include "LensModel.h"
#include "SimpleAnamorphicLensModel.generated.h"

/**
 * A very simple anamorphic lens model with just core distortion and squeeze.
 */
UCLASS(BlueprintType, DisplayName="Simple Anamorphic")
class USimpleAnamorphicLensModel : public ULensModel
{
	GENERATED_BODY()
public:
	USimpleAnamorphicLensModel();

	// 2 parameters: Core radial distortion coefficient, and squeeze ratio.
	virtual int32 GetNumParameters() const override { return 2; }
	virtual FText GetParameterDisplayName(int32 ParameterIndex) const override;
	virtual FName GetMaterialParameterPrefix() const override;

	virtual void DistortNormalizedCoordinates(
		const FVector2D& InUndistortedCoordinate,
		const TArray<double>& InParameters,
		FVector2D& OutDistortedCoordinate) const override;
};

// SimpleAnamorphicLensModel.cpp
#include "SimpleAnamorphicLensModel.h"

USimpleAnamorphicLensModel::USimpleAnamorphicLensModel()
{
}

FText USimpleAnamorphicLensModel::GetParameterDisplayName(int32 ParameterIndex) const
{
	switch (ParameterIndex)
	{
	case 0: return NSLOCTEXT("SimpleAnamorphic", "CoreDistortion", "Core Distortion");
	case 1: return NSLOCTEXT("SimpleAnamorphic", "SqueezeRatio", "Squeeze Ratio");
	default: return FText::GetEmpty();
	}
}

FName USimpleAnamorphicLensModel::GetMaterialParameterPrefix() const
{
	return TEXT("SimpleAnamorphic");
}

void USimpleAnamorphicLensModel::DistortNormalizedCoordinates(
	const FVector2D& InUndistortedCoordinate,
	const TArray<double>& InParameters,
	FVector2D& OutDistortedCoordinate) const
{
	if (InParameters.Num() < 2)
	{
		OutDistortedCoordinate = InUndistortedCoordinate;
		return;
	}

	const double CoreDistortion = InParameters[0];
	const double SqueezeRatio = InParameters[1];

	const double R2 = InUndistortedCoordinate.X * InUndistortedCoordinate.X + InUndistortedCoordinate.Y * InUndistortedCoordinate.Y;
	const double DistortionFactor = 1.0 + CoreDistortion * R2;

	OutDistortedCoordinate.X = InUndistortedCoordinate.X * DistortionFactor;
	OutDistortedCoordinate.Y = InUndistortedCoordinate.Y * DistortionFactor * SqueezeRatio;
}
```

## 模块依赖

**CameraCalibrationCore (Runtime) 模块**
除标准核心模块外，该模块还依赖：
| 模块 | 用途 |
|---|---|
| `GameplayCameras` | 提供 `UCineCameraComponent` 等功能扩展 |
| `ProceduralMeshComponent` | 可能用于运行时生成调试或可视化网格 |
| `UnrealEd` | （注：此依赖出现在 `CameraCalibrationCoreEditor` 模块，用于编辑器功能） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `eb68c63d` | Fix crashes and data loss when opening upgraded MetaHuman identities from older UEFN versions | 修复了打开旧版UEFN升级的MetaHuman身份数据时的崩溃和数据丢失问题。 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Pytho | 修复了当 MemberProperty 为空时（可能由 Python 交互引发）PostEditChangeProperty 重载中的崩溃。 |
| 2026-05-12 | `5e90bad9` | Composure: Warn when lens distortion rendering mode is not TSR | Composure 插件：当镜头畸变渲染模式不是 TSR 时发出警告。 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 移除了 BlockUntilGPUIdle 和 SubmitCommandsAndFlushGPU，改用 SubmitAndBlockUntilGPUIdle。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到 UE_LOGF。 |

### 维护评价

- **创建时间**：2021年，是 UE5 早期阶段引入的插件，专注于虚拟制作。
- **更新频率**：从提交历史看，该插件在**活跃维护**中，近期（2026年5月）有多次重要的崩溃修复和功能改进提交。
- **状态**：属于**实验性**（`IsBetaVersion=true`），表明其 API 和功能仍可能发生变化。`.uplugin` 中的 `Hidden: true` 和 `Installed: false` 表明它可能不是默认安装或对用户直接可见的插件，通常通过其他工具（如虚拟制片工具集）间接使用。
- **已知问题**：从提交历史看，存在数据升级兼容性和与 Python 交互时的稳定性问题。
- **推荐使用**：如果你正在进行**专业的虚拟制片、实时视觉特效或混合现实项目**，并且需要精确的镜头数据管理，那么这个插件是必要的核心工具。但对于简单的游戏开发或原型制作，通常不需要直接使用它。由于其**实验性**状态，集成时需要做好应对未来 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibrationCore)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibrationCore/Tests)