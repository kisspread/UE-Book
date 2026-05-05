# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（配置资产、蓝图资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色动画制作工具包。它不仅仅是一个简单的插件，而是一个完整的、端到端的面部动画制作流程解决方案。该插件的核心目的是将真实的面部表演（通常来自 iPhone 或其他设备拍摄的视频）转换为驱动 MetaHuman 角色的高质量动画数据。

它解决的问题包括：
1.  **面部捕捉与追踪**：从视频源中检测和追踪面部特征点、轮廓。
2.  **动画解算**：将追踪到的 2D 面部运动数据解算为 MetaHuman 骨骼控制所需的 3D 动画曲线。
3.  **身份适配**：将通用的动画数据适配到特定 MetaHuman 角色的面部拓扑和骨骼结构上。
4.  **流程自动化**：提供批量处理、流水线集成和 Sequencer 集成，以支持专业动画制作工作流。

## 使用场景

-   你正在使用 MetaHuman Creator 创建了角色，并希望为其制作逼真的面部动画 → 使用 MetaHuman Animator 从 iPhone 拍摄的视频中生成动画。
-   你的项目需要大量角色对话动画，且追求高效率和高保真度 → 使用 MetaHuman Batch Processor 模块批量处理表演数据。
-   你需要将面部动画数据集成到游戏引擎的过场动画系统中 → 使用 MetaHuman Sequencer 模块在 Sequencer 中直接编辑和混合面部动画。
-   你正在开发一个需要实时语音驱动面部动画的系统 → 可以研究 MetaHumanSpeech2Face 模块的功能。

## 蓝图用法

由于 MetaHuman Animator 是一个大型工具包，其蓝图 API 分散在多个模块中。以下是从核心模块 `MetaHumanConfig` 中提取的典型节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ReadFromDirectory` | 从指定目录路径读取并加载 MetaHuman 配置数据。 | `UMetaHumanConfig` |
| `GetSolverTemplateData` | 获取求解器模板数据（JSON 字符串）。 | `UMetaHumanConfig` |
| `GetFittingConfigData` | 获取适配配置数据（JSON 字符串）。 | `UMetaHumanConfig` |
| `GetPredictiveTrainingData` | 获取预测性求解器的训练数据（字节数组）。 | `UMetaHumanConfig` |

### 使用示例（蓝图描述）

1.  **加载配置**：首先，使用 `ReadFromDirectory` 节点，将包含 MetaHuman 配置文件的目录路径（例如从 MetaHuman Creator 导出的目录）作为输入。该节点会返回一个布尔值表示是否成功。
2.  **获取数据**：成功加载后，可以使用 `GetSolverConfigData`、`GetFittingTemplateData` 等节点获取特定的配置数据字符串。这些数据通常用于初始化或配置其他 MetaHuman 处理节点（如动画求解器）。
3.  **集成到流程**：将获取到的配置数据传递给 `MetaHumanPipeline` 或 `MetaHumanFaceAnimationSolver` 等模块中的相应节点，以驱动后续的动画生成流程。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanConfig.h"
```

### 基本用法

以下代码展示了如何以编程方式加载和查询 MetaHuman 配置。

```cpp
// 假设 InCaptureData 是一个有效的 UCaptureData* 对象
// InComponent 是组件名称，例如 “Face”
FString DisplayName;
UMetaHumanConfig* ConfigAsset = nullptr;

// 静态方法：根据捕获数据和组件名获取配置资产和显示名称
if (FMetaHumanConfig::GetInfo(InCaptureData, InComponent, DisplayName, ConfigAsset))
{
    UE_LOG(LogTemp, Log, TEXT("Found config: %s for component: %s"), *DisplayName, *InComponent);
    
    // 现在可以使用 ConfigAsset
    if (ConfigAsset)
    {
        // 获取求解器配置数据
        FString SolverConfigJson = ConfigAsset->GetSolverConfigData();
        // ... 将 SolverConfigJson 用于后续处理
    }
}
```

### 进阶用法

直接实例化 `UMetaHumanConfig` 对象并从磁盘加载。

```cpp
// 创建一个新的 UMetaHumanConfig 对象
UMetaHumanConfig* NewConfig = NewObject<UMetaHumanConfig>();

// 指定包含配置文件的目录路径
FString ConfigDirectory = FPaths::ProjectContentDir() / TEXT("MetaHumanConfigs/MyCharacter");

// 从目录读取配置
if (NewConfig->ReadFromDirectory(ConfigDirectory))
{
    UE_LOG(LogTemp, Log, TEXT("Successfully loaded MetaHuman config from: %s"), *ConfigDirectory);
    
    // 检查配置类型
    if (NewConfig->Type == EMetaHumanConfigType::Solver)
    {
        // 获取求解器定义数据
        FString Definitions = NewConfig->GetSolverDefinitionsData();
        // ... 处理求解器定义
    }
    else if (NewConfig->Type == EMetaHumanConfigType::Fitting)
    {
        // 获取适配控制数据
        FString ControlsData = NewConfig->GetFittingControlsData();
        // ... 处理适配控制
    }
    
    // 获取预测性训练数据（二进制）
    TArray<uint8> TrainingData = NewConfig->GetPredictiveTrainingData();
    // ... 将训练数据传递给预测性求解器
}
else
{
    UE_LOG(LogTemp, Error, TEXT("Failed to load MetaHuman config from: %s"), *ConfigDirectory);
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何加载 MetaHuman 配置并检查其类型。

**MyMetaHumanConfigLoader.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyMetaHumanConfigLoader.generated.h"

class UMetaHumanConfig;

UCLASS(BlueprintType)
class UMyMetaHumanConfigLoader : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    bool LoadConfigFromPath(const FString& DirectoryPath);

    UFUNCTION(BlueprintPure, Category = "MetaHuman")
    FString GetLoadedConfigName() const;

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanConfig> LoadedConfig;
};
```

**MyMetaHumanConfigLoader.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyMetaHumanConfigLoader.h"
#include "MetaHumanConfig.h"

bool UMyMetaHumanConfigLoader::LoadConfigFromPath(const FString& DirectoryPath)
{
    // 创建或重置配置对象
    LoadedConfig = NewObject<UMetaHumanConfig>(this);
    
    // 尝试从目录加载
    bool bSuccess = LoadedConfig->ReadFromDirectory(DirectoryPath);
    
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Loaded MetaHuman Config. Type: %d, Name: %s"), 
            static_cast<int32>(LoadedConfig->Type), *LoadedConfig->Name);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to load MetaHuman Config from: %s"), *DirectoryPath);
        LoadedConfig = nullptr;
    }
    
    return bSuccess;
}

FString UMyMetaHumanConfigLoader::GetLoadedConfigName() const
{
    if (LoadedConfig)
    {
        return LoadedConfig->Name;
    }
    return TEXT("No Config Loaded");
}
```

## 模块依赖

`MetaHumanConfig` 模块的直接依赖如下。使用者需要确保其模块的 `Build.cs` 文件中包含这些依赖。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | 提供 MetaHuman 核心技术库，包含底层算法和数据结构。 |

## 维护状态

### 近期更新

```
- 2024-10-03 0f2260027766 [MH-Plugin] Unify the interchange usage between plugins #rb Thales.Sabino #virtualized
- 2024-09-15 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 2024-08-20 52e3dac151e1 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 3/n
```

### 维护评价

MetaHuman Animator 是一个相对较新的插件（创建于 2024 年 2 月），目前处于**活跃维护**状态。从近期的提交记录来看，更新主要集中在代码质量改进、构建系统优化和内部重构上（如统一插件间数据交换、添加内联生成宏、修正 DLL 导出标记），这表明 Epic 团队正在积极地打磨和稳定该工具包，为未来的功能扩展和性能优化打下基础。

作为 MetaHuman 生态系统的核心组件，它得到了 Epic Games 的官方支持，是制作高品质 MetaHuman 角色动画的**推荐工具**。虽然当前版本（5.0.0）可能仍处于快速迭代期，但其架构完整，功能明确，适合在生产环境中评估和使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() (暂无)
- [测试用例]() (暂无独立测试目录，测试代码可能集成在各模块中)