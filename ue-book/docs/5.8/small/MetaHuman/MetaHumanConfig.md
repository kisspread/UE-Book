# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 数字人动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、蓝图资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanControlsConversionTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方的数字人动画制作工具套件，用于从真实世界数据驱动 MetaHuman 角色的面部和身体动画。它解决了以下核心问题：

1. **面部捕捉流程**：从 iPhone 前置摄像头视频（通过 Live Link Face）或专业面部捕捉设备中提取面部运动数据，将其转换为 MetaHuman 骨骼网格体可用的动画序列。
2. **面部拟合（Fitting）**：将捕捉到的面部特征精确匹配到 MetaHuman 头模上，通过控制点（Controls）驱动面部变形。
3. **预测求解器（Predictive Solver）**：利用机器学习训练模型，从稀疏的面部标记点预测完整的面部动画，即使输入数据不完整也能生成高质量动画。
4. **音频驱动面部动画（Speech2Face）**：从音频对话自动生成对应的面部动画。
5. **批量处理**：支持批量导入和处理大量捕捉数据。

插件由 28 个模块组成、544 个源文件，覆盖从底层数据捕获协议到上层 Sequencer 集成的完整管线。

## 使用场景

- 你使用 iPhone + Live Link Face App 进行面部表演捕捉 → 使用 MetaHumanCaptureSource 导入数据，通过 MetaHumanFaceFittingSolver 进行拟合
- 你有专业面部捕捉设备的视频素材 → 使用 MetaHumanFootageIngest 导入素材，通过 MetaHumanFaceContourTracker 追踪面部轮廓
- 你需要从音频自动生成面部动画 → 使用 MetaHumanSpeech2Face
- 你需要批量处理大量捕捉素材 → 使用 MetaHumanBatchProcessor
- 你需要在 Sequencer 中编辑和调整捕捉的动画 → 使用 MetaHumanSequencer
- 你需要为自定义 MetaHuman 角色校准求解器配置 → 使用 MetaHumanConfig 加载和验证配置数据

## 蓝图用法

### MetaHumanConfig 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ReadFromDirectory` | 从指定目录路径读取配置文件并加载到 Config 资产中 | `UMetaHumanConfig` |

### MetaHumanConfig 属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `Type` | `EMetaHumanConfigType` | 配置类型：Unspecified / Solver / Fitting / PredictiveSolver |
| `Name` | `FString` | 配置名称 |
| `Version` | `FString` | 配置版本号 |

### 使用示例（蓝图描述）

1. **读取配置**：在蓝图中创建 `MetaHumanConfig` 资产的引用 → 调用 `ReadFromDirectory` 节点 → 传入配置文件所在目录路径（如从 MetaHuman Creator 导出的校准数据目录）→ 配置数据会被加密存储到资产中。
2. **根据类型分支**：读取 `Type` 属性 → 使用 `Switch on EMetaHumanConfigType` 节点 → 根据是 Solver、Fitting 还是 PredictiveSolver 配置走不同逻辑分支。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanConfig.h"
```

### 基本用法

从目录加载 MetaHuman 配置数据：

```cpp
// 来源: Public/MetaHumanConfig.h

// 创建或获取 MetaHumanConfig 资产
UMetaHumanConfig* Config = NewObject<UMetaHumanConfig>();

// 从校准数据目录读取配置（目录通常由 MetaHuman Creator 导出）
FString CalibrationPath = TEXT("/Game/MetaHuman/CalibrationData");
bool bSuccess = Config->ReadFromDirectory(CalibrationPath);

if (bSuccess)
{
    // 根据配置类型执行不同操作
    switch (Config->Type)
    {
    case EMetaHumanConfigType::Solver:
        UE_LOG(LogMetaHumanConfig, Log, TEXT("Loaded Solver config: %s"), *Config->Name);
        break;
    case EMetaHumanConfigType::Fitting:
        UE_LOG(LogMetaHumanConfig, Log, TEXT("Loaded Fitting config: %s"), *Config->Name);
        break;
    case EMetaHumanConfigType::PredictiveSolver:
        UE_LOG(LogMetaHumanConfig, Log, TEXT("Loaded Predictive Solver config: %s"), *Config->Name);
        break;
    }
}
```

### 进阶用法

访问解密后的求解器和拟合配置数据：

```cpp
// 来源: Public/MetaHumanConfig.h - 获取各类配置的解密数据

UMetaHumanConfig* Config = /* ... 获取已加载的配置 ... */;

// --- Solver 相关数据（用于面部动画求解） ---
FString SolverTemplate = Config->GetSolverTemplateData();
FString SolverConfig = Config->GetSolverConfigData();
FString SolverDefinitions = Config->GetSolverDefinitionsData();
FString SolverHierarchicalDefs = Config->GetSolverHierarchicalDefinitionsData();
FString SolverHierarchicalPlusChin = Config->GetSolverHierarchicalDefinitionsPlusChinCompressData();
FString SolverPCAFromDNA = Config->GetSolverPCAFromDNAData();

// --- Fitting 相关数据（用于面部拟合） ---
FString FittingTemplate = Config->GetFittingTemplateData();
FString FittingConfig = Config->GetFittingConfigData();
FString FittingConfigTeeth = Config->GetFittingConfigTeethData();
FString FittingIdentityModel = Config->GetFittingIdentityModelData();
FString FittingControls = Config->GetFittingControlsData();

// --- Predictive Solver 相关数据（用于预测求解） ---
TArray<uint8> PredictiveGlobalTeethData = Config->GetPredictiveGlobalTeethTrainingData();
TArray<uint8> PredictiveTrainingData = Config->GetPredictiveTrainingData();
```

**注意**：所有 Get 方法返回的都是解密后的明文数据。配置数据在资产内部以加密形式（`FByteBulkData`）存储，通过 `Encrypt`/`Decrypt` 内部方法自动处理。这是为了保护 MetaHuman 的专有算法配置数据。

## Demo 示例

### 使用 MetaHumanConfig 加载和验证配置

```cpp
// MetaHumanConfigDemo.h
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanConfig.h"
#include "UObject/NoExportTypes.h"
#include "MetaHumanConfigDemo.generated.h"

UCLASS(BlueprintType)
class YOURPROJECT_API UMetaHumanConfigDemo : public UObject
{
    GENERATED_BODY()

public:
    /** 从指定路径加载 MetaHuman 配置并返回成功与否 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman|Demo")
    bool LoadConfig(const FString& InDirectoryPath);

    /** 获取当前加载的配置类型名称 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman|Demo")
    FString GetConfigTypeName() const;

    /** 获取求解器配置数据的长度（字节数），用于验证数据是否成功加载 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman|Demo")
    int32 GetSolverConfigDataLength() const;

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanConfig> LoadedConfig;
};
```

```cpp
// MetaHumanConfigDemo.cpp
#include "MetaHumanConfigDemo.h"
#include "MetaHumanConfigLog.h"

bool UMetaHumanConfigDemo::LoadConfig(const FString& InDirectoryPath)
{
    if (!LoadedConfig)
    {
        LoadedConfig = NewObject<UMetaHumanConfig>();
    }

    bool bSuccess = LoadedConfig->ReadFromDirectory(InDirectoryPath);

    if (bSuccess)
    {
        UE_LOG(LogMetaHumanConfig, Log,
            TEXT("Successfully loaded config '%s' (v%s), Type: %d"),
            *LoadedConfig->Name,
            *LoadedConfig->Version,
            static_cast<int32>(LoadedConfig->Type));
    }
    else
    {
        UE_LOG(LogMetaHumanConfig, Error,
            TEXT("Failed to load config from: %s"), *InDirectoryPath);
    }

    return bSuccess;
}

FString UMetaHumanConfigDemo::GetConfigTypeName() const
{
    if (!LoadedConfig)
    {
        return TEXT("None");
    }

    switch (LoadedConfig->Type)
    {
    case EMetaHumanConfigType::Solver:          return TEXT("Solver");
    case EMetaHumanConfigType::Fitting:         return TEXT("Fitting");
    case EMetaHumanConfigType::PredictiveSolver: return TEXT("PredictiveSolver");
    default:                                    return TEXT("Unspecified");
    }
}

int32 UMetaHumanConfigDemo::GetSolverConfigDataLength() const
{
    if (!LoadedConfig)
    {
        return 0;
    }

    return LoadedConfig->GetSolverConfigData().Len();
}
```

## 模块依赖

以下仅列出 MetaHumanConfig 模块的独特依赖（非通用依赖）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心算法库，提供底层面部拟合与求解的数学计算能力 |

完整插件的其他独特依赖（来自各模块 Build.cs）：

| 模块 | 用途 |
|---|---|
| `ControlRigDeveloper` | Control Rig 开发支持，用于面部骨骼驱动 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体工具，用于 MetaHuman 头模处理 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器集成 |
| `MetaHumanCaptureDataEditor` | 捕捉数据编辑器，被 MetaHumanIdentity 依赖 |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器，被 MetaHumanCaptureDataEditor 依赖 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 身体追踪启用时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

- MetaHuman Animator 由 Epic Games 官方团队持续维护，属于 MetaHuman 数字人管线的核心组件
- 最近的 commit 密集（2026 年 5 月连续多天有更新），涵盖功能增强（身体追踪集成、动画导出）和 Bug 修复（渲染瑕疵、Sequencer 缓存）
- 插件规模庞大（28 个模块、544 个源文件），覆盖从数据捕获到动画输出的完整管线
- 无 deprecated/obsolete 标记，仍在积极开发新功能
- **推荐使用**：如果你的项目需要将真实表演数据驱动到 MetaHuman 角色上，这是官方推荐的工具

**注意**：此插件默认未启用（`Installed: false`），需要在插件管理器中手动启用。部分功能（如 MetaHumanCoreTechLib 依赖）可能需要额外的专有库文件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [MetaHuman 官方文档](https://docs.unrealengine.com/en-US/metahuman/)
- [MetaHuman Animator 概述](https://docs.unrealengine.com/en-US/metahuman-animator-in-unreal-engine/)