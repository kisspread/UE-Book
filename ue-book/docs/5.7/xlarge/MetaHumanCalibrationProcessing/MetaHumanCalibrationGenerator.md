# MetaHuman Animator Calibration Processing

> The official MetaHuman Calibration Processing Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（校准数据资产、处理配置） |
| 模块 | `MetaHumanCalibrationCore` (Runtime), `MetaHumanCalibrationGenerator` (Runtime), `MetaHumanCalibrationLib` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-04-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing) | |

---

## 用途

MetaHumanCalibrationProcessing 是 MetaHuman Animator 工作流中的核心校准处理插件。它负责将面部捕捉的原始视频素材（单目或双目）转换为精确的相机校准数据，为后续的面部动画驱动提供几何基础。

**核心问题**：MetaHuman Animator 需要知道相机的精确内参（焦距、畸变）和外参（位置、旋转）才能将 2D 面部特征点正确映射到 3D 空间。这个插件自动化了整个校准流程。

**为什么存在**：
- 手动校准相机参数繁琐且容易出错
- 需要支持单目（monocular）和双目（stereo）两种捕捉模式
- 校准质量直接影响最终面部动画的精度
- 需要与 MetaHuman 的面部骨骼系统精确对齐

## 使用场景

- **MetaHuman 面部动画制作**：你使用 iPhone 或专业相机捕捉面部表演 → 用此插件处理校准数据 → 驱动 MetaHuman 角色
- **单目视频处理**：你只有一台相机拍摄的面部视频 → 插件自动推断相机参数
- **双目立体捕捉**：你使用双相机设置 → 插件利用立体视觉提高校准精度
- **批量校准处理**：你有大量已录制的面部素材需要统一处理 → 使用生成器模块批量生成校准数据

## 模块架构

```
MetaHumanCalibrationProcessing/
├── MetaHumanCalibrationCore      ← 核心数据结构和接口定义
├── MetaHumanCalibrationGenerator ← 校准数据生成器（本模块）
└── MetaHumanCalibrationLib       ← 底层算法库（相机标定、优化）
```

### MetaHumanCalibrationGenerator（当前模块）

校准数据生成器，负责协调整个校准流程：
- 读取原始视频/图像序列
- 调用 MetaHumanCalibrationLib 进行相机标定
- 生成可用于 MetaHuman Animator 的校准资产
- 支持单目和双目模式
- 包含相机匹配（Camera Matching）功能

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GenerateCalibration` | 从视频素材生成校准数据 | `UMetaHumanCalibrationGenerator` |
| `MatchCamera` | 执行相机匹配以优化校准结果 | `UMetaHumanCalibrationGenerator` |
| `ValidateCalibration` | 验证生成的校准数据质量 | `UMetaHumanCalibrationGenerator` |

### 使用示例（蓝图描述）

**基本校准流程**：
1. 创建 `MetaHumanCalibrationGenerator` 对象
2. 设置输入源（视频文件路径或图像序列）
3. 配置校准参数（单目/双目模式、目标分辨率）
4. 调用 `GenerateCalibration` 节点
5. 获取输出的校准资产，传递给 MetaHuman Animator

**带相机匹配的流程**：
1. 执行基本校准流程
2. 调用 `MatchCamera` 节点进行额外优化
3. 检查匹配质量指标
4. 保存最终校准结果

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCalibrationGenerator.h"
```

### 基本用法

```cpp
// 创建校准生成器实例
UMetaHumanCalibrationGenerator* Generator = NewObject<UMetaHumanCalibrationGenerator>();

// 配置输入
FCalibrationGenerationSettings Settings;
Settings.InputPath = TEXT("/Game/CapturedFootage/face_video.mp4");
Settings.bIsMonocular = true;  // 单目模式
Settings.TargetResolution = FIntPoint(1920, 1080);

// 执行校准生成
FCalibrationResult Result = Generator->GenerateCalibration(Settings);

if (Result.bSuccess)
{
    // 获取生成的校准资产
    UMetaHumanCalibrationAsset* CalibrationAsset = Result.CalibrationAsset;
    
    // 保存到磁盘
    FString SavePath = TEXT("/Game/Calibrations/MyCalibration");
    Generator->SaveCalibration(CalibrationAsset, SavePath);
}
```

### 进阶用法

```cpp
// 双目模式 + 相机匹配优化
FCalibrationGenerationSettings Settings;
Settings.InputPath = TEXT("/Game/CapturedFootage/stereo_left.mp4");
Settings.SecondaryInputPath = TEXT("/Game/CapturedFootage/stereo_right.mp4");
Settings.bIsMonocular = false;  // 双目模式
Settings.bEnableCameraMatching = true;

// 异步执行校准
Generator->GenerateCalibrationAsync(Settings, 
    FOnCalibrationComplete::CreateLambda([](const FCalibrationResult& Result)
    {
        if (Result.bSuccess)
        {
            UE_LOG(LogMetaHuman, Log, TEXT("校准完成，质量分数: %.2f"), Result.QualityScore);
        }
    })
);
```

## Demo 示例

### MetaHumanCalibrationGenerator.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanCalibrationGenerator.generated.h"

UCLASS(BlueprintType)
class UMyCalibrationProcessor : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, Category = "Calibration")
    FString VideoFilePath;

    UPROPERTY(BlueprintReadWrite, Category = "Calibration")
    bool bUseMonocularMode = true;

    UFUNCTION(BlueprintCallable, Category = "Calibration")
    bool ProcessCalibration();

private:
    UPROPERTY()
    UMetaHumanCalibrationGenerator* Generator;
};
```

### MetaHumanCalibrationGenerator.cpp

```cpp
#include "MyCalibrationProcessor.h"
#include "MetaHumanCalibrationGenerator.h"

bool UMyCalibrationProcessor::ProcessCalibration()
{
    if (!Generator)
    {
        Generator = NewObject<UMetaHumanCalibrationGenerator>();
    }

    FCalibrationGenerationSettings Settings;
    Settings.InputPath = VideoFilePath;
    Settings.bIsMonocular = bUseMonocularMode;

    FCalibrationResult Result = Generator->GenerateCalibration(Settings);
    
    if (Result.bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("校准成功: %s"), *Result.OutputPath);
        return true;
    }

    UE_LOG(LogTemp, Error, TEXT("校准失败: %s"), *Result.ErrorMessage);
    return false;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCalibrationCore` | 核心数据结构和接口定义 |
| `MetaHumanCalibrationLib` | 底层相机标定算法 |
| `UnrealEd` | 编辑器集成（仅 MetaHumanCalibrationLib 依赖） |

## 维护状态

### 近期更新

```
- ae9eb3421810 [MetaHuman] Fix crash when running calibration generation on monocular footage
- b31cabbf2cc5 Adding permissions for MetaHuman Calibration window
- 7e20d2160278 Camera matching on calibration generation
```

### 维护评价

**活跃维护中** 🟢

- **创建时间**：2025-04-01，非常新的插件（约 1 年）
- **更新频率**：近期有多次实质性更新，包括功能添加（Camera Matching）和 Bug 修复（单目模式崩溃）
- **维护状态**：Epic Games 官方维护，作为 MetaHuman 工具链的核心组件
- **已知问题**：单目模式曾有崩溃问题（已修复）
- **推荐程度**：**强烈推荐** - 这是 MetaHuman Animator 工作流的必要组件，官方维护质量有保障

**注意事项**：
- 该插件依赖 MetaHuman 生态系统的其他组件
- 需要配合 MetaHuman Animator 使用
- 单目模式的校准精度低于双目模式

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing)
- [MetaHuman 官方文档](https://docs.unrealengine.com/en-US/metahuman/)
- [MetaHuman Animator 文档](https://docs.unrealengine.com/en-US/metahuman-animator/)