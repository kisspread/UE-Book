# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、蓝图资产、测试资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | 🆕（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一套完整的工具链，用于从视频或深度数据驱动 MetaHuman 角色面部动画。它解决了从原始面部捕捉数据（如 iPhone 原深感摄像头的深度数据或标准视频）到最终动画的自动化流程问题。其核心流程包括：捕捉数据管理、面部轮廓追踪、面部拟合求解器、面部动画求解器、预测性求解器（用于从音频生成面部动画）以及性能数据管理。

本模块 `MetaHumanConfig` 是该工具链的配置核心。它负责管理和存储MetaHuman Animator流程中各组件（如Fitting、Solver）所需的加密配置数据模板和参数。这些配置数据定义了求解器如何工作、使用哪些模型和参数，是保证动画质量和流程一致性的关键。

## 使用场景

- 你需要从 iPhone 原深感摄像头拍摄的深度数据创建面部动画 → 使用 MetaHuman Animator 的 `MetaHumanPerformance` 和 `MetaHumanDepthGenerator` 模块。
- 你想要基于音频文件自动驱动一个 MetaHuman 角色说话 → 使用 `MetaHumanSpeech2Face` 模块。
- 你是 MetaHuman 工具链的开发者或高级用户，需要自定义或更新面部拟合、动画求解器的参数和模型 → 需要理解并可能修改 `MetaHumanConfig` 中加载的配置数据。
- 你在开发一个自动化处理大量MetaHuman动画资产的流水线 → 使用 `MetaHumanBatchProcessor` 模块。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ReadFromDirectory` | 从指定目录读取并加载MetaHuman配置资产文件。这是初始化配置资产的主要蓝图节点。 | `UMetaHumanConfig` |

### 使用示例（蓝图描述）

1.  **创建配置资产**：在内容浏览器中右键 → `Miscellaneous` → `Data Asset` → 选择 `MetaHumanConfig` 类型。
2.  **蓝图中加载配置**：
    *   使用 `ReadFromDirectory` 节点，将配置资产的变量连接到 `Target` 引脚。
    *   在 `InPath` 引脚输入包含配置文件（如 `.json`, `.bin`）的目录路径。
    *   调用该节点后，配置资产会从该目录读取并解析所有配置数据。
3.  **查询配置数据**：配置加载后，虽然蓝图公开的函数有限，但内部流程（如拟合、求解）会自动使用这些数据。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanConfig.h"
```

### 基本用法

```cpp
// 加载或创建一个 MetaHumanConfig 资产
UMetaHumanConfig* Config = NewObject<UMetaHumanConfig>();

// 从目录读取配置数据
FString ConfigPath = TEXT("/Game/MetaHuman/Config/MySolverConfig");
bool bSuccess = Config->ReadFromDirectory(ConfigPath);

if (bSuccess)
{
    // 检查配置类型
    if (Config->Type == EMetaHumanConfigType::Solver)
    {
        // 获取求解器模板数据（已解密的JSON字符串）
        FString SolverTemplate = Config->GetSolverTemplateData();
        UE_LOG(LogMetaHumanConfig, Log, TEXT("Solver Template Loaded: %s"), *SolverTemplate.Left(100));
    }
}
```

### 进阶用法

在自定义的MetaHuman流程组件中，验证和使用特定的配置数据：

```cpp
// 假设在某个自定义求解器类中
void UMyCustomSolver::InitializeSolver()
{
    UMetaHumanConfig* SolverConfig = LoadObject<UMetaHumanConfig>(nullptr, TEXT("/Game/MetaHuman/Config/AdvancedSolver"));
    if (!SolverConfig)
    {
        UE_LOG(LogMySolver, Error, TEXT("Failed to load solver config."));
        return;
    }

    // 获取所有求解器相关数据进行内部验证或初始化
    FString TemplateData = SolverConfig->GetSolverTemplateData();
    FString ConfigData = SolverConfig->GetSolverConfigData();
    FString Definitions = SolverConfig->GetSolverDefinitionsData();
    // ... 使用这些数据进行自定义逻辑 ...
}
```
**来源**: 基于 `Public/MetaHumanConfig.h` 中的 `UMetaHumanConfig` 类接口推导。

## Demo 示例

**MetaHumanConfigLoader.h**
```cpp
// 版权所有 Epic Games, Inc. 保留所有权利。

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanConfigLoader.generated.h"

class UMetaHumanConfig;

UCLASS()
class AMetaHumanConfigLoader : public AActor
{
	GENERATED_BODY()
	
public:	
	AMetaHumanConfigLoader();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MetaHuman")
	FString ConfigDirectoryPath;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MetaHuman")
	UMetaHumanConfig* LoadedConfig;

	UFUNCTION(BlueprintCallable, Category = "MetaHuman")
	bool LoadConfig();

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "MetaHuman")
	FString GetSolverConfigJson() const;
};
```

**MetaHumanConfigLoader.cpp**
```cpp
// 版权所有 Epic Games, Inc. 保留所有权利。

#include "MetaHumanConfigLoader.h"
#include "MetaHumanConfig.h"

AMetaHumanConfigLoader::AMetaHumanConfigLoader()
{
	PrimaryActorTick.bCanEverTick = false;
}

bool AMetaHumanConfigLoader::LoadConfig()
{
	if (ConfigDirectoryPath.IsEmpty())
	{
		return false;
	}

	// 如果已有配置，重新加载；否则创建新实例
	if (!LoadedConfig)
	{
		LoadedConfig = NewObject<UMetaHumanConfig>(this, UMetaHumanConfig::StaticClass(), TEXT("DemoConfig"));
	}

	return LoadedConfig->ReadFromDirectory(ConfigDirectoryPath);
}

FString AMetaHumanConfigLoader::GetSolverConfigJson() const
{
	if (LoadedConfig && LoadedConfig->Type == EMetaHumanConfigType::Solver)
	{
		return LoadedConfig->GetSolverConfigData();
	}
	return TEXT("");
}
```

## 模块依赖

从 `MetaHumanConfig.Build.cs` 分析，使用者需要以下独特依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | 提供MetaHuman核心算法和技术库，用于配置数据的加密、解密以及与底层技术栈的交互。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复MetaHuman角色的渲染伪影问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时，过滤可视化对象以优化性能或显示。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器的缓存问题。 |

### 维护评价

**活跃维护**。MetaHuman Animator是一个大型、活跃维护的Epic Games官方工具包。从最近的提交记录（2026年5月）可以看出，开发团队仍在持续修复bug、增加功能（如身体追踪支持）并优化性能。`MetaHumanConfig`模块作为核心配置模块，其内部依赖和加密机制很可能随着主插件一起更新。该插件是Epic的旗舰内容创作工具，推荐在MetaHuman相关项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() (未在 .uplugin 中提供)
- [测试用例]() (待定位)