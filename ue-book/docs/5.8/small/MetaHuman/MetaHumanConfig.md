# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置数据资产） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanConfig` (Runtime) 等众多子模块 |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（年龄未知） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个完整的、专业级的 MetaHuman 动画制作工具链。它提供从面部视频捕捉、面部追踪、动画解算到最终动画序列生成的端到端工作流程。该插件旨在解决使用真实演员表演为 MetaHuman 数字人创建高保真、可驱动面部动画的核心需求。它不是一个简单的转换工具，而是一个集成在引擎内的复杂解算和追踪系统，用于制作电影级或高品质的实时数字人内容。

## 使用场景

- 你在制作虚拟制片或电影项目，需要基于演员表演为 MetaHuman 角色生成逼真的面部动画。
- 你是一名技术美术或动画师，拥有演员的面部捕捉视频（如 iPhone 录制），并希望将其应用到你的 UE5 项目中的 MetaHuman 角色上。
- 你需要批量处理大量表演数据，将其转化为可用的动画资产。
- 你需要精确控制面部动画解算的参数，或者对特定面部区域进行手动调整。
- 你的项目需要支持实时或离线的高保真数字人驱动。

## 蓝图用法

由于插件模块众多且复杂，蓝图 API 主要集中在资产管理和工作流启动。核心的 `UMetaHumanConfig` 类提供了一组蓝图节点用于读取和管理解算器所需的配置数据。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ReadFromDirectory` | 从指定目录路径读取加密的配置数据文件，并更新资产状态。 | `UMetaHumanConfig` |
| `GetSolverTemplateData` | 获取用于面部动画解算的模板数据。 | `UMetaHumanConfig` |
| `GetSolverConfigData` | 获取解算器的配置参数。 | `UMetaHumanConfig` |
| `GetFittingTemplateData` | 获取用于网格拟合的模板数据。 | `UMetaHumanConfig` |
| `GetPredictiveTrainingData` | 获取用于预测性解算器的训练数据。 | `UMetaHumanConfig` |

### 使用示例（蓝图描述）

1.  **创建配置资产**：在内容浏览器中右键 -> Animation -> MetaHuman Config，创建一个新的 `UMetaHumanConfig` 资产。
2.  **加载配置**：在蓝图中，获取该资产的引用，调用 `ReadFromDirectory` 节点。将存放有 `solver_template.json`、`fitting_template.json` 等数据的目录路径作为输入。成功后，`Type` 属性会根据加载的数据自动设置（如 `Solver`, `Fitting`）。
3.  **使用配置数据**：在需要使用解算器或拟合器的其他 MetaHuman 工具蓝图节点（如面部追踪或动画解算节点）中，将此 `UMetaHumanConfig` 资产作为输入参数传入。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanConfig.h"
```

### 基本用法

`UMetaHumanConfig` 是管理 MetaHuman 解算器和拟合器所需加密配置数据的核心资产类。它内部使用 `FByteBulkData` 存储加密后的 JSON 或二进制配置数据，并提供透明的加解密接口。

**来源文件：** `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanConfig/Public/MetaHumanConfig.h`

```cpp
// 加载或创建一个 MetaHumanConfig 资产
UMetaHumanConfig* Config = NewObject<UMetaHumanConfig>();

// 从指定目录加载所有关联的配置文件
const FString ConfigDir = FPaths::ProjectContentDir() / TEXT("MetaHuman/Config");
if (Config->ReadFromDirectory(ConfigDir))
{
    UE_LOG(LogMetaHumanConfig, Log, TEXT("成功加载配置，类型: %s"), *UEnum::GetValueAsString(Config->Type));

    // 根据配置类型，获取相应的解算数据（自动解密）
    if (Config->Type == EMetaHumanConfigType::Solver)
    {
        FString SolverConfigJson = Config->GetSolverConfigData();
        // 将 SolverConfigJson 解析后用于面部动画解算器...
    }
    else if (Config->Type == EMetaHumanConfigType::Fitting)
    {
        FString FittingTemplateJson = Config->GetFittingTemplateData();
        // 将 FittingTemplateJson 用于网格拟合过程...
    }
}
else
{
    UE_LOG(LogMetaHumanConfig, Error, TEXT("从目录加载配置失败: %s"), *ConfigDir);
}
```

### 进阶用法

配置数据在加载时经过验证和加密存储。开发者通常不直接与底层的 `FByteBulkData` 加密字段交互，而是通过 `ReadFromDirectory` 一次性加载所有数据，并通过 `Get...Data()` 系列函数获取解密后的字符串或字节数组。这些数据随后被传递给 `MetaHumanFaceAnimationSolver`、`MetaHumanFaceFittingSolver` 等模块进行计算。

```cpp
// 在一个更完整的上下文中，配置数据可能被传递给 Pipeline 进行处理
FMetaHumanPipelineContext Context;
Context.Config = Config;

// ... 管道中某个节点需要解算器配置
FString SolverDefinitions = Context.Config->GetSolverDefinitionsData();
// 使用 SolverDefinitions 初始化或配置解算器实例
```

## Demo 示例

以下是一个最小示例，演示如何在 C++ 中创建并加载一个 `MetaHumanConfig` 资产。

**MyCharacter.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

class UMetaHumanConfig;

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MetaHuman")
    UMetaHumanConfig* LoadedConfig;

    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void LoadMyMetaHumanConfig(const FString& DirectoryPath);
};
```

**MyCharacter.cpp**
```cpp
#include "MyCharacter.h"
#include "MetaHumanConfig.h"

AMyCharacter::AMyCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCharacter::LoadMyMetaHumanConfig(const FString& DirectoryPath)
{
    // 如果已有资产，先清空
    if (LoadedConfig)
    {
        LoadedConfig->ConditionalBeginDestroy();
        LoadedConfig = nullptr;
    }

    // 创建一个新的内存中的配置资产
    LoadedConfig = NewObject<UMetaHumanConfig>(this, UMetaHumanConfig::StaticClass(), NAME_None, RF_Transient);

    // 尝试从指定目录加载配置文件
    if (!LoadedConfig->ReadFromDirectory(DirectoryPath))
    {
        UE_LOG(LogTemp, Warning, TEXT("加载 MetaHuman 配置失败。"));
        LoadedConfig = nullptr;
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("成功加载 MetaHuman 配置。类型: %s"), *UEnum::GetValueAsString(LoadedConfig->Type));
}
```

## 模块依赖

该插件包含大量子模块，彼此间依赖关系复杂。以下是 `MetaHumanConfig` 模块及其所依赖的插件特有模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，提供底层算法和工具函数。 |
| `MetaHumanFaceAnimationSolver` | 面部动画解算器，将追踪数据转化为面部骨骼驱动。 |
| `MetaHumanFaceFittingSolver` | 面部网格拟合解算器，将通用网格适配到特定面型。 |
| `MetaHumanFaceContourTracker` | 面部轮廓追踪器，从视频中提取面部特征点轨迹。 |
| `MetaHumanCaptureSource` | 捕获源管理，处理来自不同设备的输入数据。 |
| `MetaHumanPipeline` | 数据处理管道，编排从原始数据到最终动画的流程。 |
| `MetaHumanPerformance` | 表演数据资产，封装一次完整的面部捕捉表演。 |
| `MetaHumanIdentity` | 数字身份资产，管理单个 MetaHuman 的基础网格和拓扑。 |
| `MetaHumanSequencer` | 集成 Unreal Sequencer，用于编辑和播放生成的动画。 |
| `MetaHumanSpeech2Face` | 语音驱动面部动画模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 在启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象，优化性能。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为现有网格体导出动画序列，增强了工作流灵活性。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复与 Sequencer 缓存相关的问题。 |

### 维护评价

**活跃维护**。该插件是 Epic Games 的官方核心产品，受到持续的积极维护和更新。从近期提交记录看（截至2026年5月），开发团队仍在密集地修复问题（如渲染瑕疵、缓存问题）和增加功能（如新的导出选项、身体追踪支持）。这是一个稳定且推荐用于生产环境的关键插件。然而，由于其复杂性和对特定硬件/软件管道（如 MetaHuman Animator 应用）的依赖，学习曲线和集成难度较高。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/meta-humans-in-unreal-engine/) （官方 MetaHuman 总览页，包含 Animator 工作流链接）