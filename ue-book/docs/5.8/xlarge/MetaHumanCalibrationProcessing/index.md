# MetaHuman Animator Calibration Processing

> The official MetaHuman Calibration Processing Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 校准处理工具 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `MetaHumanCalibrationCore` (Runtime), `MetaHumanCalibrationGenerator` (Runtime), `MetaHumanCalibrationLib` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-04-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing) | |

## 用途

`MetaHumanCalibrationProcessing` 是 MetaHuman Animator 工具链中的核心数据处理插件。它主要用于将从 iPhone 捕获的面部表演数据（视频、深度信息、相机参数）转化为精确的面部校准结果。校准是确保 MetaHuman 数字角色面部动画能够高度还原真实演员表演的关键步骤，此插件负责执行整个复杂的校准计算流程。

## 使用场景

- 你正在使用 MetaHuman Animator 为 MetaHuman 角色制作高品质的面部动画。
- 你使用 iPhone 等设备捕获了演员的面部表演原始数据。
- 你需要将这些捕获数据处理并校准，以生成可驱动 MetaHuman 骨骼的精确动画数据。
- 你的项目涉及影视、游戏或虚拟制片中对数字人面部表情的真实感要求极高的场景。

## 蓝图用法

核心功能通过 `MetaHumanCalibrationGenerator` 模块暴露。以下按功能分组：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartCalibration` | 从输入的视频和相机数据启动校准生成流程 | `UCalibrationGenerator` |
| `GetCalibrationState` | 查询当前校准流程的状态（进行中、完成、失败等） | `UCalibrationGenerator` |
| `ExecuteCalibration` | 将生成的校准结果应用到目标 MetaHuman 角色骨骼上 | `UCalibrationGenerator` |

### 使用示例（蓝图描述）

1.  创建一个 `UCalibrationGenerator` 的实例（例如通过 `CreateCalibrationGenerator` 节点）。
2.  将从 MetaHuman Animator 工具获得的视频路径、相机参数等数据连接到 `StartCalibration` 节点的相应输入引脚。
3.  将 `StartCalibration` 的输出（校准结果数据）连接到 `ExecuteCalibration` 节点，并指定要驱动的 MetaHuman 角色。
4.  使用一个定时器或事件节点，周期性调用 `GetCalibrationState` 来监控流程状态，并在完成时执行后续逻辑（如播放动画）。

## C++ 用法

### 头文件引入

```cpp
#include “MetaHumanCalibrationGenerator.h”
```

### 基本用法

```cpp
// 来源于测试用例: MetaHumanCalibrationProcessing/Tests/MetaHumanCalibrationGeneratorTest.cpp
// 创建一个校准生成器实例
UCalibrationGenerator* CalibrationGenerator = NewObject<UCalibrationGenerator>();

// 配置输入数据（此处为示意，实际参数需从捕获数据中获取）
FString VideoPath = TEXT(“path/to/captured/video.mp4”);
FCameraIntrinsics CameraIntrinsics; // 相机内参

// 启动校准过程（同步版本）
bool bSuccess = CalibrationGenerator->StartCalibration(VideoPath, CameraIntrinsics);

if (bSuccess)
{
    // 获取校准结果
    FCalibrationResult Result = CalibrationGenerator->GetCalibrationResult();
    // ... 应用结果
}
```

### 进阶用法

```cpp
// 来源于测试用例: MetaHumanCalibrationProcessing/Tests/MetaHumanCalibrationGeneratorTest.cpp
// 异步校准通常更适合游戏或应用程序线程
UCalibrationGenerator* AsyncCalibrationGenerator = NewObject<UCalibrationGenerator>();

// 绑定完成委托
AsyncCalibrationGenerator->OnCalibrationComplete.AddLambda([this](bool bSuccess, const FCalibrationResult& Result)
{
    if (bSuccess)
    {
        // 校准成功，在游戏线程上应用结果
        AsyncTask(ENamedThreads::GameThread, [this, Result]()
        {
            ApplyCalibrationToCharacter(Result);
        });
    }
});

// 在后台线程启动校准
AsyncCalibrationGenerator->StartCalibrationAsync(VideoPath, CameraIntrinsics);
```

## Demo 示例

一个最小的 C++ 类，用于演示如何使用校准生成器。

```cpp
// MyCalibrationHandler.h
#pragma once
#include “CoreMinimal.h”
#include “UObject/NoExportTypes.h”
#include “MetaHumanCalibrationGenerator.h”
#include “MyCalibrationHandler.generated.h”

UCLASS()
class MYGAME_API UMyCalibrationHandler : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY()
    TObjectPtr<UCalibrationGenerator> CalibrationGenerator;

    UFUNCTION(BlueprintCallable)
    void StartCharacterCalibration(const FString& VideoDataPath);
};
```

```cpp
// MyCalibrationHandler.cpp
#include “MyCalibrationHandler.h”

void UMyCalibrationHandler::StartCharacterCalibration(const FString& VideoDataPath)
{
    if (!CalibrationGenerator)
    {
        CalibrationGenerator = NewObject<UCalibrationGenerator>(this);
    }

    // 绑定完成回调
    CalibrationGenerator->OnCalibrationComplete.AddDynamic(this, &UMyCalibrationHandler::OnCalibrationFinished);

    // 开始异步校准
    CalibrationGenerator->StartCalibrationAsync(VideoDataPath, FCameraIntrinsics());
}

void UMyCalibrationHandler::OnCalibrationFinished(bool bSuccess, const FCalibrationResult& Result)
{
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT(“Calibration succeeded for frame %d”), Result.FrameIndex);
        // 在此将 Result 应用到你的 MetaHuman 角色 Actor 上
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT(“Calibration failed.”));
    }

    // 解绑
    CalibrationGenerator->OnCalibrationComplete.RemoveDynamic(this, &UMyCalibrationHandler::OnCalibrationFinished);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCalibrationLib` | 提供底层的校准算法和数学计算库 |
| `MediaUtils` | 处理输入的视频媒体数据 |
| `OpenCV` | 用于图像处理和计算机视觉操作 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | 升级至Titan核心库版本9.0.8 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | 升级至Titan核心库版本9.0.7 |
| 2026-05-21 | `e936df4b` | [MetaHuman] Titan v9.0.6 | 升级至Titan核心库版本9.0.6 |
| 2026-05-14 | `52cbd20d` | [MetaHuman] titan v9.0.5 | 升级至Titan核心库版本9.0.5 |
| 2026-05-13 | `df646fb2` | Use infinity as limit for initial distance, to not overflow float in calculations | 修复浮点数计算溢出问题，提高计算稳定性 |

### 维护评价

- **活跃维护**：该插件处于**非常活跃**的维护状态。创建于2025年4月，至今约1年，但近期更新极为频繁（最近一周内多次更新）。
- **更新内容**：近期的更新主要集中在与 MetaHuman 内部核心库 `Titan` 的版本同步升级，以及修复核心计算的数值稳定性问题。这表明 Epic 正在积极迭代其底层算法。
- **推荐使用**：作为 MetaHuman 工具链的官方组成部分，且更新频繁、修复及时，**强烈推荐**在使用 MetaHuman Animator 工作流时集成此插件。它是实现高品质面部动画的关键环节。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing/Tests/)
- [MetaHuman Animator 官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/) (校准处理是其工作流的一部分)