# Capture Data

> Classes releated to captured data

| 属性 | 值 |
|---|---|
| 中文名 | 捕获数据 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产定义、工厂类） |
| 模块 | `CaptureDataCore` (Runtime), `CaptureDataEditor` (Editor), `CaptureDataUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureData) | |

## 用途

CaptureData 插件为虚幻引擎的虚拟制片（Virtual Production）工作流提供**捕获数据的结构化管理框架**。

这个插件解决的核心问题是：在虚拟制片过程中，会产生大量来自真实世界的数据（网格扫描数据、视频素材、相机校准数据等），这些数据需要存储额外的元信息（时间码、帧率、相机参数、重投影误差等）。CaptureData 提供了：

1. **统一的元数据存储机制** - 通过 UE 的 Package Metadata 系统将捕获元数据嵌入到资产中
2. **专用资产类型定义** - 为 MeshCaptureData（网格捕获）、FootageCaptureData（视频素材）、CameraCalibration（相机校准）等提供标准化的资产类型
3. **编辑器集成** - 提供资产创建工厂、细节面板自定义、元数据编辑窗口等编辑器功能

该插件是 **Hidden（隐藏）** 的，说明它是作为其他虚拟制片功能（如 Capture Manager、Camera Calibration）的基础设施层存在，而非直接面向最终用户。

## 使用场景

- 你在使用 MetaHuman 或虚拟制片流程，需要管理相机标定结果 → 存储重投影误差、选择的帧范围等元数据
- 你从多相机采集系统导入网格扫描数据 → 使用 MeshCaptureData 资产类型
- 你处理来自专业拍摄的视频素材 → 使用 FootageCaptureData 管理时间码和帧率信息
- 你需要在编辑器中查看和编辑捕获数据的元信息 → 使用 ShowMetadataObjects 系列函数弹出编辑窗口

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCaptureMetadata` | 为对象设置捕获元数据 | `UCaptureMetadata` |
| `GetCaptureMetadata` | 获取对象上的捕获元数据 | `UCaptureMetadata` |
| `ClearCaptureMetadata` | 清除对象上的捕获元数据 | `UCaptureMetadata` |
| `ShowCaptureMetadataObjects` | 显示捕获元数据编辑窗口 | `UCaptureMetadata` |
| `SetCameraCalibrationMetadata` | 为对象设置相机校准元数据 | `UCameraCalibrationMetadata` |
| `GetCameraCalibrationMetadata` | 获取对象上的相机校准元数据 | `UCameraCalibrationMetadata` |
| `ClearCameraCalibrationMetadata` | 清除对象上的相机校准元数据 | `UCameraCalibrationMetadata` |
| `ShowCameraCalibrationMetadataObjects` | 显示相机校准元数据编辑窗口 | `UCameraCalibrationMetadata` |

### 使用示例（蓝图描述）

**存储相机校准数据到资产**：

1. 创建一个 `UCameraCalibrationMetadata` 对象
2. 设置其属性（`ReprojectionRMSError`、`GenerationTimecode`、`GenerationFrameRate`、`SelectedFrames`）
3. 调用 `SetCameraCalibrationMetadata`，传入目标资产和元数据对象
4. 元数据将自动写入该资产的 Package Metadata 中

**批量查看元数据**：

1. 收集需要查看的资产对象数组
2. 调用 `ShowCaptureMetadataObjects` 或 `ShowCameraCalibrationMetadataObjects`
3. 系统将弹出一个窗口显示所有选中对象的元数据信息

## C++ 用法

### 头文件引入

```cpp
#include "CaptureMetadata.h"
#include "CameraCalibrationMetadata.h"
```

### 基本用法

**设置和读取捕获元数据**：

```cpp
// 来源: Public/CaptureMetadata.h

// 创建元数据并设置到对象
UCaptureMetadata* Metadata = NewObject<UCaptureMetadata>();
Metadata->CameraId = TEXT("Camera_001");

UCaptureMetadata::SetCaptureMetadata(MyAsset, Metadata);

// 读取元数据
UCaptureMetadata* RetrievedMetadata = UCaptureMetadata::GetCaptureMetadata(MyAsset);
if (RetrievedMetadata)
{
    FString CameraId = RetrievedMetadata->CameraId;
}

// 清除元数据
UCaptureMetadata::ClearCaptureMetadata(MyAsset);
```

**设置相机校准元数据**：

```cpp
// 来源: Public/CameraCalibrationMetadata.h

UCameraCalibrationMetadata* CalibMeta = NewObject<UCameraCalibrationMetadata>();
CalibMeta->ReprojectionRMSError = 0.5;
CalibMeta->GenerationTimecode = FTimecode(10, 30, 0, 0, true);
CalibMeta->GenerationFrameRate = FFrameRate(24, 1);
CalibMeta->SelectedFrames = { 0, 10, 20, 30, 40 };

UCameraCalibrationMetadata::SetCameraCalibrationMetadata(MyCalibrationAsset, CalibMeta);
```

### 进阶用法

**自定义元数据类型**：

```cpp
// 来源: Public/Metadata/MetadataHandler.h

// 创建自定义元数据类继承 UBaseCaptureMetadata
UCLASS(BlueprintType)
class UMyCustomCaptureMetadata : public UBaseCaptureMetadata
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString CaptureDeviceName;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FVector CaptureLocation;
};

// 使用模板函数操作自定义元数据
UMyCustomCaptureMetadata* CustomMeta = NewObject<UMyCustomCaptureMetadata>();
CustomMeta->CaptureDeviceName = TEXT("LiDAR Scanner");
CustomMeta->CaptureLocation = FVector(100, 200, 50);

// SetMetadataObject 是模板函数，支持任何 UBaseCaptureMetadata 派生类
UE::SetMetadataObject(MyObject, CustomMeta);

// 读取自定义元数据
UMyCustomCaptureMetadata* Retrieved = UE::GetMetadataObject<UMyCustomCaptureMetadata>(MyObject);
```

## Demo 示例

### 自定义捕获元数据管理器

```cpp
// MyCaptureManager.h
#pragma once

#include "CoreMinimal.h"
#include "CaptureMetadata.h"
#include "CameraCalibrationMetadata.h"

UCLASS(BlueprintType)
class UMyCaptureManager : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable)
    void StoreFootageMetadata(UObject* FootageAsset, const FString& InCameraId);
    
    UFUNCTION(BlueprintCallable)
    void StoreCalibrationResult(UObject* CalibAsset, double InRMSError, 
                                 const FTimecode& InTimecode, const FFrameRate& InFrameRate,
                                 const TArray<int32>& InSelectedFrames);
    
    UFUNCTION(BlueprintCallable)
    void DisplayAllMetadata(const TArray<UObject*>& InObjects);
};
```

```cpp
// MyCaptureManager.cpp
#include "MyCaptureManager.h"

void UMyCaptureManager::StoreFootageMetadata(UObject* FootageAsset, const FString& InCameraId)
{
    if (!FootageAsset)
    {
        return;
    }

    UCaptureMetadata* Metadata = NewObject<UCaptureMetadata>();
    Metadata->CameraId = InCameraId;
    
    UCaptureMetadata::SetCaptureMetadata(FootageAsset, Metadata);
}

void UMyCaptureManager::StoreCalibrationResult(UObject* CalibAsset, double InRMSError,
                                                const FTimecode& InTimecode, const FFrameRate& InFrameRate,
                                                const TArray<int32>& InSelectedFrames)
{
    if (!CalibAsset)
    {
        return;
    }

    UCameraCalibrationMetadata* CalibMeta = NewObject<UCameraCalibrationMetadata>();
    CalibMeta->ReprojectionRMSError = InRMSError;
    CalibMeta->GenerationTimecode = InTimecode;
    CalibMeta->GenerationFrameRate = InFrameRate;
    CalibMeta->SelectedFrames = InSelectedFrames;
    
    UCameraCalibrationMetadata::SetCameraCalibrationMetadata(CalibAsset, CalibMeta);
}

void UMyCaptureManager::DisplayAllMetadata(const TArray<UObject*>& InObjects)
{
    FCaptureMetadataWindowOptions Options;
    Options.bAllowEdit = true;
    
    UCaptureMetadata::ShowCaptureMetadataObjects(
        FText::FromString(TEXT("Capture Metadata Viewer")), 
        InObjects, 
        Options
    );
}
```

## 模块依赖

从插件依赖和模块结构分析：

| 模块 | 用途 |
|---|---|
| `ImgMedia` | 图像序列媒体播放（用于 FootageCaptureData） |
| `CameraCalibrationCore` | 相机校准核心功能 |
| `EditorScriptingUtilities` | 编辑器脚本工具 |

本插件模块间关系：
- `CaptureDataCore` - 核心数据类型定义
- `CaptureDataUtils` - 工具函数
- `CaptureDataEditor` - 编辑器集成（资产定义、工厂、细节面板自定义）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d3aefcf1` | Improve timecode and frame rate resolution in capture data by independently validating each value ac | 改进时间码和帧率验证，独立校验每个值 |
| 2026-04-14 | `54e43b2d` | Added log messages to ImageSequenceUtils | 为 ImageSequenceUtils 添加日志输出 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的 UE_LOGF 格式 |
| 2026-04-06 | `65adeb26` | [ContentBrowser] New Add Menu MetaHuman Menu | 内容浏览器新增 MetaHuman 菜单项 |
| 2026-03-31 | `99ca17a7` | [Capture Manager] Improved handling of non-integer frame rates | 改进非整数帧率的处理逻辑 |

### 维护评价

**活跃维护中** ✅

- 创建于 2024 年 9 月，属于较新的插件（约 2 年）
- 最近 2 个月内有多次功能性更新，集中在时间码/帧率处理改进
- 作为虚拟制片基础设施，与 MetaHuman、Capture Manager 等活跃系统紧密关联
- 作为 Hidden 插件，说明它主要被其他上层系统依赖，而非直接面向用户
- 推荐使用：如果你在做虚拟制片工作流且需要管理捕获元数据，这是官方标准方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureData)
- 官方文档（无）