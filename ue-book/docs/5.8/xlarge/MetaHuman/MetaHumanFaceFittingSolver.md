# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、配置资源） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MeshTrackerInterface` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-01-01（估计） |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色动画制作工具集。它解决的核心问题是：**如何将真实世界中的人脸表演（面部捕捉数据）转换为 MetaHuman 角色的高质量面部动画**。

该插件提供了一套完整的面部动画制作流水线：

1. **面部捕捉数据导入**：支持从 iPhone 深度摄像头、专业面捕设备等多种来源导入面部表演数据
2. **面部轮廓追踪**（`MetaHumanFaceContourTracker`）：自动追踪面部关键特征点
3. **面部拟合求解**（`MetaHumanFaceFittingSolver`）：将追踪到的面部特征拟合到 MetaHuman 面部网格上
4. **面部动画求解**（`MetaHumanFaceAnimationSolver`）：将拟合结果转换为骨骼控制驱动的动画
5. **深度图生成**（`MetaHumanDepthGenerator`）：从 2D 图像生成深度信息辅助追踪
6. **语音驱动面部**（`MetaHumanSpeech2Face`）：通过音频直接生成面部动画
7. **序列器集成**（`MetaHumanSequencer`）：将生成的动画无缝集成到 Sequencer 时间线中
8. **批量处理**（`MetaHumanBatchProcessor`）：支持批量处理多个动画片段

## 使用场景

- 你有一段 iPhone 深度摄像头拍摄的面部表演视频 → 用 MetaHuman Animator 的捕捉导入和面部拟合流程转换为 MetaHuman 动画
- 你只有一段音频录音，想快速生成面部动画 → 用 Speech2Face 模块直接从音频驱动面部
- 你需要为大量采访片段批量生成 MetaHuman 面部动画 → 用 MetaHumanBatchProcessor 批量处理
- 你有专业面捕设备（如 Live Link Face）的实时数据 → 用 MetaHumanCaptureProtocolStack 接收实时捕捉流
- 你需要将面部动画精确匹配到已有的 MetaHuman 角色身份 → 用 MetaHumanIdentity 模块管理角色身份，再用面部拟合精确适配
- 你需要在 Sequencer 中编辑和混合面部动画 → 用 MetaHumanSequencer 模块集成

## 蓝图用法

> ⚠️ 由于该插件主要为编辑器内工作流设计，大部分功能通过自定义编辑器 UI 面板暴露，直接的蓝图节点较少。以下是从公开头文件中提取的可用接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadFaceFittingSolvers` | 加载面部拟合所需的求解器数据 | `UMetaHumanFaceFittingSolver` |
| `LoadPredictiveSolver` | 加载预测性求解器（用于表演准备阶段的训练） | `UMetaHumanFaceFittingSolver` |
| `CanProcess` | 检查当前配置是否满足处理条件 | `UMetaHumanFaceFittingSolver` |
| `GetConfigDisplayName` | 获取与指定捕捉数据匹配的配置名称 | `UMetaHumanFaceFittingSolver` |
| `GetFittingTemplateData` | 获取拟合模板数据（JSON 格式） | `UMetaHumanFaceFittingSolver` |
| `GetFittingConfigData` | 获取拟合配置数据（JSON 格式） | `UMetaHumanFaceFittingSolver` |
| `GetFittingControlsData` | 获取拟合控制参数数据（JSON 格式） | `UMetaHumanFaceFittingSolver` |

### 使用示例（蓝图描述）

面部拟合求解器的典型蓝图使用流程：

1. 创建 `UMetaHumanFaceFittingSolver` 对象
2. 设置 `DeviceConfig` 属性指向正确的设备配置（如 iPhone TrueDepth）
3. 设置 `PredictiveSolver` 属性指向预测性求解器配置
4. 调用 `LoadFaceFittingSolvers()` 加载求解器
5. 调用 `CanProcess()` 检查是否就绪
6. 通过 `GetFittingTemplateData()` / `GetFittingConfigData()` 等获取拟合参数，传递给处理管线

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanFaceFittingSolver.h"
```

### 基本用法

```cpp
// 创建面部拟合求解器实例
UMetaHumanFaceFittingSolver* FaceFittingSolver = NewObject<UMetaHumanFaceFittingSolver>();

// 配置设备配置（如需覆盖默认设备设置）
FaceFittingSolver->bOverrideDeviceConfig = true;
FaceFittingSolver->DeviceConfig = SomeMetaHumanConfig;

// 配置预测性求解器
FaceFittingSolver->PredictiveSolver = SomePredictiveSolverConfig;

// 加载求解器数据
FaceFittingSolver->LoadFaceFittingSolvers();
FaceFittingSolver->LoadPredictiveSolver();

// 检查是否可以开始处理
if (FaceFittingSolver->CanProcess())
{
    // 获取拟合所需的各类配置数据
    FString TemplateData = FaceFittingSolver->GetFittingTemplateData(CaptureData);
    FString ConfigData = FaceFittingSolver->GetFittingConfigData(CaptureData);
    FString ConfigTeethData = FaceFittingSolver->GetFittingConfigTeethData(CaptureData);
    FString IdentityModelData = FaceFittingSolver->GetFittingIdentityModelData(CaptureData);
    FString ControlsData = FaceFittingSolver->GetFittingControlsData(CaptureData);

    // 这些 JSON 字符串数据将传递给拟合管线进行处理
}
```

### 进阶用法

```cpp
// 监听求解器内部数据变化
FDelegateHandle Handle = FaceFittingSolver->OnInternalsChanged().AddLambda([]()
{
    // 当求解器配置发生变化时，可能需要重新加载或更新 UI
    UE_LOG(LogMetaHuman, Log, TEXT("Face fitting solver internals changed, reloading..."));
});

// 获取配置显示名称（根据捕捉数据自动选择合适的设备配置）
FString DisplayName;
if (FaceFittingSolver->GetConfigDisplayName(CaptureData, DisplayName))
{
    UE_LOG(LogMetaHuman, Log, TEXT("Using config: %s"), *DisplayName);
}

// 获取预测性训练数据（用于自定义训练流程）
TArray<uint8> GlobalTeethTrainingData = FaceFittingSolver->GetPredictiveGlobalTeethTrainingData();
TArray<uint8> TrainingData = FaceFittingSolver->GetPredictiveTrainingData();
```

## Demo 示例

```cpp
// MetaHumanFittingExample.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanFittingExample.generated.h"

class UMetaHumanFaceFittingSolver;
class UCaptureData;

UCLASS()
class AMetaHumanFittingExample : public AActor
{
    GENERATED_BODY()

public:
    AMetaHumanFittingExample();

    UPROPERTY(EditAnywhere, Category = "MetaHuman")
    TObjectPtr<UMetaHumanFaceFittingSolver> FaceFittingSolver;

    UPROPERTY(EditAnywhere, Category = "MetaHuman")
    TObjectPtr<UCaptureData> CaptureData;

    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void RunFaceFitting();

    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    bool IsReady() const;

private:
    FDelegateHandle InternalsChangedHandle;

    void OnSolverInternalsChanged();
};
```

```cpp
// MetaHumanFittingExample.cpp
#include "MetaHumanFittingExample.h"
#include "MetaHumanFaceFittingSolver.h"

AMetaHumanFittingExample::AMetaHumanFittingExample()
{
    FaceFittingSolver = CreateDefaultSubobject<UMetaHumanFaceFittingSolver>(TEXT("FaceFittingSolver"));
}

void AMetaHumanFittingExample::RunFaceFitting()
{
    if (!FaceFittingSolver)
    {
        UE_LOG(LogTemp, Error, TEXT("FaceFittingSolver is null"));
        return;
    }

    // 加载求解器
    FaceFittingSolver->LoadFaceFittingSolvers();
    FaceFittingSolver->LoadPredictiveSolver();

    if (!FaceFittingSolver->CanProcess())
    {
        UE_LOG(LogTemp, Warning, TEXT("FaceFittingSolver cannot process - check configuration"));
        return;
    }

    // 监听变化
    InternalsChangedHandle = FaceFittingSolver->OnInternalsChanged().AddUObject(
        this, &AMetaHumanFittingExample::OnSolverInternalsChanged);

    // 获取拟合参数
    FString TemplateData = FaceFittingSolver->GetFittingTemplateData(CaptureData);
    FString ConfigData = FaceFittingSolver->GetFittingConfigData(CaptureData);
    FString ControlsData = FaceFittingSolver->GetFittingControlsData(CaptureData);

    UE_LOG(LogTemp, Log, TEXT("Fitting data ready: Template=%d chars, Config=%d chars, Controls=%d chars"),
        TemplateData.Len(), ConfigData.Len(), ControlsData.Len());

    // 获取配置名称
    FString ConfigName;
    if (FaceFittingSolver->GetConfigDisplayName(CaptureData, ConfigName))
    {
        UE_LOG(LogTemp, Log, TEXT("Using device config: %s"), *ConfigName);
    }

    // 此处将数据传递给 MetaHumanPipeline 管线执行实际拟合
}

bool AMetaHumanFittingExample::IsReady() const
{
    return FaceFittingSolver && FaceFittingSolver->CanProcess();
}

void AMetaHumanFittingExample::OnSolverInternalsChanged()
{
    UE_LOG(LogTemp, Log, TEXT("Solver internals changed, consider reloading"));
}
```

## 模块依赖

该插件包含 28 个模块，以下列出各核心模块的独特依赖（省略 Core/Engine/Slate 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库（底层算法） |
| `ControlRigDeveloper` | ControlRig 开发者工具，用于面部骨骼控制 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器工具 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格通用工具 |
| `MetaHumanCaptureDataEditor` | 捕捉数据编辑器 |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器 |

**注意**：该插件默认未启用（`Installed: false`），需要在项目设置中手动启用，或通过 MetaHuman Creator 工具自动启用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 的渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有网格导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存问题 |

### 维护评价

**🟢 活跃维护**

MetaHuman Animator 是 Epic Games 官方维护的核心工具之一，处于**非常活跃**的维护状态：

- **持续更新**：最近的提交集中在 2026 年 5 月，几乎每天都有更新
- **功能迭代**：不断添加新功能（如身体追踪集成、动画序列导出改进）
- **Bug 修复**：持续修复渲染、缓存等各类问题
- **官方支持**：作为 MetaHuman 生态系统的核心组件，Epic 会长期维护
- **大型工程**：544 个源文件、28 个模块，表明这是一个成熟的、经过大量投入的工具集

**推荐使用**：如果你的项目需要将真人面部表演转换为 MetaHuman 动画，这是官方推荐且唯一完整的解决方案。建议使用最新版本以获得最佳兼容性和功能支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman-animator/)（MetaHuman Animator 官方文档）
- [MetaHuman 官网](https://www.unrealengine.com/en-US/metahuman)