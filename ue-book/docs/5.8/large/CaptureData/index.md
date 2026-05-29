# Capture Data

> Classes releated to captured data

| 属性 | 值 |
|---|---|
| 中文名 | 数据捕获 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CaptureDataCore` (Runtime), `CaptureDataEditor` (Editor), `CaptureDataUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureData) | |

## 用途

本插件提供了一套标准化的框架，用于在UE5中处理虚拟制片流程中的各类捕获数据。它解决了在虚拟制片中，不同类型捕获设备（如摄像机、深度传感器）产生的数据格式不统一、处理逻辑分散的问题。通过定义核心数据模型（如`UCaptureTakeInfo`）和标准化的媒体资产（如`UCaptureMediaAsset`），它为存储、读取、校准和验证捕获数据（包括视频、深度、时间码、帧率等）提供了统一的基础，使得后期处理、编辑和合成流程更加可靠和高效。

## 使用场景

- 你在进行虚拟制片，需要管理从现场捕获的多摄像机视频、深度数据和时间码信息，以便在后期进行准确的合成和编辑。
- 你的工作流程涉及使用MetaHuman创建，需要处理和对齐面部动作捕获数据。
- 你需要在编辑器中或通过脚本，对捕获的图像序列、视频文件进行校准、时间码同步和质量验证。

## 蓝图用法

蓝图功能主要集中在`CaptureDataUtils`模块提供的工具函数中，用于数据查询和验证。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetStartTimecode` | 从捕获数据信息中获取起始时间码。 | `UCaptureDataUtils` |
| `GetTimecodeFrameRate` | 获取捕获数据的帧率（Timecode Frame Rate）。 | `UCaptureDataUtils` |
| `ValidateTimecodeAndFrameRate` | 验证捕获数据的时间码和帧率是否有效。 | `UCaptureDataUtils` |
| `ConvertToLinearColor` | 将像素数据（FColor）转换为线性颜色（FLinearColor）。 | `UCaptureDataUtils` |

### 使用示例（蓝图描述）

在蓝图中，你可以创建一个`UCaptureTakeInfo`对象，然后使用`GetStartTimecode`节点来获取这次“拍摄”的起始时间码，用于后续的时间线对齐。或者，使用`ValidateTimecodeAndFrameRate`节点对一个`UCaptureMediaAsset`资产进行验证，确保其元数据正确，避免后续处理出现同步错误。

## C++ 用法

### 头文件引入

```cpp
#include "CaptureDataCore/CaptureTakeInfo.h"
#include "CaptureDataCore/CaptureMediaAsset.h"
#include "CaptureDataUtils/CaptureDataUtils.h"
```

### 基本用法

创建和查询捕获数据的基本信息。

```cpp
// 创建一个捕获信息对象
UCaptureTakeInfo* TakeInfo = NewObject<UCaptureTakeInfo>();
TakeInfo->SetStartTimecode(FTimecode(1, 0, 0, 0)); // 设置起始时间码 01:00:00:00
TakeInfo->SetTimecodeFrameRate(FFrameRate(24, 1)); // 设置帧率为 24fps

// 使用工具函数查询
FTimecode StartTime = UCaptureDataUtils::GetStartTimecode(TakeInfo);
FFrameRate FrameRate = UCaptureDataUtils::GetTimecodeFrameRate(TakeInfo);

// 加载一个捕获媒体资产并验证
UCaptureMediaAsset* MediaAsset = LoadObject<UCaptureMediaAsset>(nullptr, TEXT("/Game/Captures/MyVideoAsset"));
bool bIsValid = UCaptureDataUtils::ValidateTimecodeAndFrameRate(MediaAsset);
```

## Demo 示例

以下是一个简单的C++示例，演示如何创建基本的捕获数据结构。

**CaptureDataDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CaptureDataDemo.generated.h"

class UCaptureTakeInfo;
class UCaptureMediaAsset;

UCLASS()
class ACaptureDataDemo : public AActor
{
    GENERATED_BODY()

public:
    ACaptureDataDemo();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(Transient)
    TObjectPtr<UCaptureTakeInfo> CurrentTakeInfo;

    UPROPERTY(Transient)
    TObjectPtr<UCaptureMediaAsset> SampleMediaAsset;
};
```

**CaptureDataDemo.cpp**
```cpp
#include "CaptureDataDemo.h"
#include "CaptureDataCore/CaptureTakeInfo.h"
#include "CaptureDataCore/CaptureMediaAsset.h"
#include "CaptureDataUtils/CaptureDataUtils.h"

ACaptureDataDemo::ACaptureDataDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ACaptureDataDemo::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建并填充捕获拍摄信息
    CurrentTakeInfo = NewObject<UCaptureTakeInfo>(this);
    CurrentTakeInfo->SetStartTimecode(FTimecode(10, 0, 0, 15)); // 10:00:00:15
    CurrentTakeInfo->SetTimecodeFrameRate(FFrameRate(30000, 1001)); // 29.97 fps

    // 2. 假设我们有一个媒体资产（通常从磁盘加载）
    SampleMediaAsset = NewObject<UCaptureMediaAsset>(this);

    // 3. 使用工具函数进行验证
    bool bTakeValid = UCaptureDataUtils::ValidateTimecodeAndFrameRate(CurrentTakeInfo);
    bool bMediaValid = UCaptureDataUtils::ValidateTimecodeAndFrameRate(SampleMediaAsset);

    UE_LOG(LogTemp, Log, TEXT("Take Info Valid: %s, Media Asset Valid: %s"),
        bTakeValid ? TEXT("true") : TEXT("false"),
        bMediaValid ? TEXT("true") : TEXT("false"));
}
```

## 模块依赖

使用者需要在自己的模块`.Build.cs`文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `CaptureDataCore` | 访问捕获数据的核心类（`UCaptureTakeInfo`, `UCaptureMediaAsset`）。 |
| `CaptureDataUtils` | 调用捕获数据相关的工具和验证函数。 |
| `CaptureDataEditor` | （仅在编辑器模块中）访问捕获数据的自定义资产编辑器和类型工厂。 |

此外，本插件还依赖以下插件，确保它们在你的项目中启用：
- `ImgMedia`
- `CameraCalibrationCore`
- `EditorScriptingUtilities`

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d3aefcf1` | Improve timecode and frame rate resolution in capture data by independently validating each value ac | 优化了时间码和帧率的解析逻辑，分别独立验证每个值以提高准确性。 |
| 2026-04-14 | `54e43b2d` | Added log messages to ImageSequenceUtils | 为图像序列工具类添加了日志输出，便于调试。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的UE_LOG日志宏迁移到新的UE_LOGF格式。 |
| 2026-04-06 | `65adeb26` | [ContentBrowser] New Add Menu MetaHuman Menu | 配合内容浏览器，新增了MetaHuman相关的添加菜单。 |
| 2026-03-31 | `99ca17a7` | [Capture Manager] Improved handling of non-integer frame rates | 改进了对非整数帧率（如29.97fps）的处理逻辑。 |

### 维护评价

该插件创建于2024年9月，年龄较新。从近期提交记录来看，更新非常活跃，最近一次更新在2026年5月。更新内容主要集中在**功能优化**（如时间码/帧率处理）、**代码质量改进**（日志标准化）以及**工作流集成**（与MetaHuman、Capture Manager联动）上。这表明该插件是Epic Games在虚拟制片领域**积极维护的核心组件**。没有发现已知废弃标记。鉴于其明确的功能定位和持续的维护，**推荐在相关的虚拟制片项目中使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureData)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureData/Tests)（如果存在）