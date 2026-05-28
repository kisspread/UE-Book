# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置、示例数据） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-04-27 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的，用于将真实演员的面部表演捕捉数据（通常来自 iPhone 的深度摄像头或专业设备）驱动 MetaHuman 角色的完整工具集。它不是简单的单个工具，而是一个包含**数据采集、面部追踪、动画求解、批处理和 Sequencer 集成**的端到端解决方案。其核心价值在于将原始的捕捉视频流，转化为高质量、可编辑的 MetaHuman 面部动画序列，解决了从“人”到“数字人”表演迁移的技术难题。

## 使用场景

- **独立游戏/影视团队**：使用 iPhone 12 Pro 或更新的设备（具备 LiDAR）录制演员的面部表演，需要快速生成高质量的 MetaHuman 动画资产。
- **大规模内容生产**：需要批量处理数十上百个表演镜头，将它们转换为可用于游戏过场或虚拟制片的动画数据。
- **追求精确控制的动画师**：希望从初始的自动追踪结果开始，手动微调面部特征点、求解器参数或动画曲线，以获得导演要求的精确表演。
- **已有面部视频素材**：希望通过 Speech2Face 等技术，仅从音频或现有视频片段驱动 MetaHuman 角色，或为现有动画添加额外的细节。

## 蓝图用法

由于该插件模块众多，蓝图 API 分布在多个类中，以下是基于 `MetaHumanConfig` 模块分析的核心节点。其他如 `MetaHumanPerformance`，`MetaHumanIdentity` 等模块也提供了大量蓝图接口，用于驱动整个处理流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ReadFromDirectory` | 从指定目录读取并解析 MetaHuman 配置文件（包含求解器、拟合器等模型数据）。这是初始化许多功能的前提。 | `UMetaHumanConfig` |

### 使用示例（蓝图描述）

1.  **加载配置**：在蓝图中创建一个 `UMetaHumanConfig` 类型的变量。使用“Construct Object”节点创建实例，然后调用 `ReadFromDirectory` 节点，指定包含官方配置文件的路径（例如插件 Content 目录下的特定子文件夹）。
2.  **驱动求解器**：`MetaHumanFaceAnimationSolver` 和 `MetaHumanFaceFittingSolver` 等模块的蓝图节点通常会接受一个 `UMetaHumanConfig` 对象作为输入参数。将步骤1加载好的配置对象传递给它们，即可为后续的追踪、拟合和求解过程提供必要的模型和模板数据。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanConfig.h"
```

### 基本用法

从 `MetaHumanConfig.h` 中提取的配置加载示例。

```cpp
// 来源: Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanConfig/Public/MetaHumanConfig.h

// 1. 创建一个 MetaHumanConfig 对象
UMetaHumanConfig* Config = NewObject<UMetaHumanConfig>();

// 2. 指定配置文件目录路径
FString ConfigPath = FPaths::ProjectPluginsDir() / TEXT("MetaHuman/Content/Config/Default"); // 示例路径，实际路径需参考插件说明

// 3. 从目录读取配置
bool bSuccess = Config->ReadFromDirectory(ConfigPath);
if (bSuccess)
{
    UE_LOG(LogMetaHumanConfig, Log, TEXT("MetaHuman Config loaded successfully."));
    UE_LOG(LogMetaHumanConfig, Log, TEXT("Config Type: %d"), static_cast<int32>(Config->Type));
    UE_LOG(LogMetaHumanConfig, Log, TEXT("Solver Template Data Length: %d"), Config->GetSolverTemplateData().Len());
}
else
{
    UE_LOG(LogMetaHumanConfig, Error, TEXT("Failed to load MetaHuman Config from: %s"), *ConfigPath);
}
```

### 进阶用法

加载配置后，访问其内部数据以供其他系统使用。

```cpp
// 假设 Config 已经成功加载（见上文）

// 获取求解器配置数据 (JSON 字符串)
FString SolverConfigJson = Config->GetSolverConfigData();

// 获取拟合器的身份模型数据 (加密的二进制数据)
TArray<uint8> IdentityModelData; // 通常由更高级的 API 间接使用，此处仅为演示访问
// IdentityModelData 可能通过其他内部函数解密后使用

// 获取预测性求解器的全局牙齿训练数据
TArray<uint8> GlobalTeethData = Config->GetPredictiveGlobalTeethTrainingData();

// 将这些数据传递给具体的动画求解器或拟合器模块的 API
// 例如: FaceAnimationSolver->Initialize(SolverConfigJson, ...);
```

## Demo 示例

一个加载 MetaHuman 配置并查询其基本属性的最小控制台程序示例。

### MyMetaHumanConfigTest.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyMetaHumanConfigTest.generated.h"

UCLASS()
class UMyMetaHumanConfigTest : public UObject
{
    GENERATED_BODY()

public:
    void TestLoadConfig();
};
```

### MyMetaHumanConfigTest.cpp
```cpp
#include "MyMetaHumanConfigTest.h"
#include "MetaHumanConfig.h"
#include "Misc/FileHelper.h"

void UMyMetaHumanConfigTest::TestLoadConfig()
{
    UMetaHumanConfig* Config = NewObject<UMetaHumanConfig>();

    // 注意：此路径仅为示例，实际 MetaHuman 配置文件路径取决于插件安装和资产版本
    // 通常位于 Engine/Plugins/MetaHuman/MetaHumanAnimator/Content/Config/ 下
    FString TestConfigPath = TEXT("C:/YourProject/Plugins/MetaHuman/Content/Config/Default");

    if (Config->ReadFromDirectory(TestConfigPath))
    {
        UE_LOG(LogTemp, Display, TEXT("=== MetaHuman Config Loaded ==="));
        UE_LOG(LogTemp, Display, TEXT("Name: %s"), *Config->Name);
        UE_LOG(LogTemp, Display, TEXT("Version: %s"), *Config->Version);
        UE_LOG(LogTemp, Display, TEXT("Type Enum: %d (0=Unspecified, 1=Solver, 2=Fitting, 3=PredictiveSolver)"), static_cast<uint8>(Config->Type));

        // 检查一些数据是否存在
        if (Config->GetSolverTemplateData().Len() > 0)
        {
            UE_LOG(LogTemp, Display, TEXT("Solver Template Data Available."));
        }
        if (Config->GetFittingIdentityModelData().Len() > 0)
        {
            UE_LOG(LogTemp, Display, TEXT("Fitting Identity Model Data Available."));
        }
        if (Config->GetPredictiveTrainingData().Num() > 0)
        {
            UE_LOG(LogTemp, Display, TEXT("Predictive Training Data Available. Size: %d bytes"), Config->GetPredictiveTrainingData().Num());
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load MetaHuman config from: %s"), *TestConfigPath);
    }
}
```

## 模块依赖

该插件的核心模块依赖链复杂且自成体系。以下列出一些**关键的、非标准的依赖模块**，这些是您在二次开发或集成时可能需要引用的：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 的核心算法库，包含求解器、拟合器的底层数学和机器学习模型。是 `MetaHumanConfig` 等模块的基础。 |
| `MetaHumanFaceFittingSolver` | 执行面部网格拟合算法，将通用模板适配到特定演员的面部几何形状。 |
| `MetaHumanFaceAnimationSolver` | 核心动画求解器，将追踪到的面部特征点转换为 MetaHuman 骨骼控制器的动画数据。 |
| `MetaHumanFaceContourTracker` | 面部轮廓追踪器，负责从图像/视频中检测和追踪面部关键点。 |
| `MetaHumanPipeline` | 处理流水线框架，用于编排数据从捕获到最终输出的各个步骤。 |
| `MetaHumanIdentity` | 管理 MetaHuman 身份资产，关联面部网格、配置和动画数据。 |
| `ControlRig` | UE5 的动画控制系统，MetaHuman 动画的最终输出目标之一。 |
| `SkeletalMeshUtilitiesCommon` | 用于骨骼网格体操作的通用工具函数。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能，可能是为了规避兼容性问题。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 身体上的渲染瑕疵（artifacts），提升视觉表现。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪模式下，过滤掉不必要的可视化对象，优化视图和性能。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为已有的网格体导出动画序列，增强了工具的灵活性和可重用性。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 中的缓存问题，改善编辑器内的动画预览和编辑稳定性。 |

### 维护评价

MetaHuman Animator 插件处于**活跃维护**状态。尽管创建于约 4 年前，但从 Git 历史看，近期（2026年5月）仍有密集的功能更新和 Bug 修复。这些更新不仅限于编译适配，而是包含了新功能（如身体追踪集成）、渲染优化和工作流改进。作为 Epic 官方的主力数字人工具链，其长期维护和技术支持有保障。**推荐用于正式项目**，但需注意其功能强大，学习曲线相对较陡峭。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() (`.uplugin` 中 `DocsURL` 为空，请参考 Epic Games 官网 MetaHuman 相关文档)
- [测试用例]() (插件内包含 `MetaHumanControlsConversionTest` 等测试模块，路径示例: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest/`)