# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有 (配置资产、数据文件、编辑器工具) |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | unknown |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 为 MetaHuman 角色提供的完整动画创作工具包。它不仅仅是一个动画播放器，而是一个涵盖从原始视频捕捉数据导入、面部追踪、动画解算到最终模型拟合和动画序列化的端到端工作流套件。

其核心解决的问题是：如何将普通视频（如 iPhone 深度摄像头或普通单目视频）高效地转化为适用于高质量 MetaHuman 角色的逼真面部动画。它内置了专业的面部轮廓追踪器、动画解算器、拟合解算器以及用于从音频生成动画的 Speech2Face 功能，是影视级或高保真游戏 MetaHuman 角色制作的核心管道。

## 使用场景

- 你是一名虚拟制片艺术家，需要将演员的面部表演视频快速同步到 MetaHuman 角色上 → 使用 MetaHuman Animator 的视频捕捉与解算流程。
- 你需要为 MetaHuman 角色创建复杂的面部动画序列，用于过场动画 → 使用其与 Sequencer 的深度集成 (`MetaHumanSequencer`) 来编辑和混合动画。
- 你希望从一段音频对话自动生成匹配的口型动画 → 使用其内置的 Speech2Face 功能。
- 你正在开发一个需要批量处理大量面部动画数据的流水线 → 使用 `MetaHumanBatchProcessor` 模块。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ReadFromDirectory` | 从指定目录加载配置数据（解密并验证） | `UMetaHumanConfig` |
| `GetSolverTemplateData` | 获取求解器模板数据（JSON 字符串） | `UMetaHumanConfig` |
| `GetSolverConfigData` | 获取求解器配置数据（JSON 字符串） | `UMetaHumanConfig` |
| `GetFittingTemplateData` | 获取拟合模板数据（JSON 字符串） | `UMetaHumanConfig` |
| `GetFittingConfigData` | 获取拟合配置数据（JSON 字符串） | `UMetaHumanConfig` |
| `GetFittingIdentityModelData` | 获取拟合身份模型数据（JSON 字符串） | `UMetaHumanConfig` |
| `GetPredictiveTrainingData` | 获取预测性解算器的训练数据（二进制） | `UMetaHumanConfig` |

### 使用示例（蓝图描述）

在蓝图中，首先创建 `UMetaHumanConfig` 对象。然后调用 `ReadFromDirectory` 节点，传入包含 `config.json` 及相关数据文件的目录路径。成功后，即可通过 `GetSolverConfigData`、`GetFittingConfigData` 等节点获取对应的配置数据（通常是 JSON 字符串），供下游的求解器或拟合器节点使用。配置数据是加密存储的，`ReadFromDirectory` 会负责解密。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanConfig.h"
```

### 基本用法

创建并初始化一个配置资产，这是使用 MetaHuman Animator 后端功能的基础。

```cpp
// 创建 MetaHumanConfig 资产
UMetaHumanConfig* Config = NewObject<UMetaHumanConfig>();

// 从包含 MetaHuman 配置文件的目录加载数据
const FString ConfigDir = TEXT("/Game/MetaHuman/Configs/Default");
bool bSuccess = Config->ReadFromDirectory(ConfigDir);
if (bSuccess)
{
    // 加载成功，可以获取求解器或拟合器所需的配置数据
    FString SolverConfigJson = Config->GetSolverConfigData();
    // 将 SolverConfigJson 传递给相应的解算器模块
}
```
*（来源：基于 `UMetaHumanConfig` 的公开接口设计）*

### 进阶用法

结合类型查询，为不同的工作流（求解、拟合、预测性求解）提供对应的数据。

```cpp
UMetaHumanConfig* Config = LoadObject<UMetaHumanConfig>(nullptr, TEXT("/Game/MetaHuman/Configs/MyConfig"));

if (Config)
{
    // 检查配置类型
    switch (Config->Type)
    {
    case EMetaHumanConfigType::Solver:
        {
            // 获取完整的求解器相关数据
            FString Template = Config->GetSolverTemplateData();
            FString Defs = Config->GetSolverDefinitionsData();
            // ... 其他求解器数据
        }
        break;
    case EMetaHumanConfigType::Fitting:
        {
            // 获取拟合相关数据
            FString FittingIdentity = Config->GetFittingIdentityModelData();
            TArray<uint8> PredData = Config->GetPredictiveTrainingData();
            // ... 其他拟合数据
        }
        break;
    }
}
```

## Demo 示例

```cpp
// MyMetaHumanConfigExample.h
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyMetaHumanConfigExample.generated.h"

class UMetaHumanConfig;

UCLASS(BlueprintType)
class UMyMetaHumanConfigExample : public UObject
{
    GENERATED_BODY()

public:
    // 加载一个 MetaHuman 配置资产并检查其状态
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    bool InitializeFromAsset(UMetaHumanConfig* InConfigAsset);

    UPROPERTY(BlueprintReadOnly, Category = "MetaHuman")
    UMetaHumanConfig* LoadedConfig;

    UPROPERTY(BlueprintReadOnly, Category = "MetaHuman")
    FString SolverConfigData;
};
```

```cpp
// MyMetaHumanConfigExample.cpp
#include "MyMetaHumanConfigExample.h"
#include "MetaHumanConfig.h"

bool UMyMetaHumanConfigExample::InitializeFromAsset(UMetaHumanConfig* InConfigAsset)
{
    LoadedConfig = InConfigAsset;
    if (!LoadedConfig)
    {
        return false;
    }

    // 直接访问配置中的数据
    SolverConfigData = LoadedConfig->GetSolverConfigData();
    UE_LOG(LogTemp, Log, TEXT("Config Type: %d"), static_cast<int32>(LoadedConfig->Type));
    UE_LOG(LogTemp, Log, TEXT("Solver Config JSON Length: %d"), SolverConfigData.Len());

    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | 核心的技术库，提供底层的面部解算、追踪算法支持 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体通用工具，用于处理 MetaHuman 的骨骼和网格 |
| `ControlRigDeveloper` | Control Rig 开发支持，MetaHuman 的面部动画通常通过 Control Rig 驱动 |
| `MetaHumanSDKEditor` | MetaHuman 编辑器 SDK 集成 |
| `MetaHumanCaptureDataEditor` | 捕捉数据编辑器支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 身上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 进行身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**活跃维护**。尽管 `MetaHumanConfig` 模块本身近期更新不多，但从整个 `MetaHumanAnimator` 插件的 Git 历史看，其相关模块在 2026 年 5 月仍有密集的功能性更新（如修复渲染问题、增强身体追踪集成、改进动画导出）。这表明整个插件套件正在被积极维护和开发中，是生产可用的工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- 官方文档：暂无公开链接
- 测试用例：暂无独立目录