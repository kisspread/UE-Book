# MetaHuman Face Animation Solver

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 面部动画解算器 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（UI资产、配置数据） |
| 模块 | `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceFittingSolver` (Runtime) 等 |
| 实验性 | 否 |
| 创建时间 | 待补充（需执行 Git 命令） |
| 年龄标签 | 待补充 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Face Animation Solver 模块是 MetaHuman Animator 工具链的核心组件之一，其核心职责是**将捕获的面部视频数据（如来自 iPhone 或专业摄像机）转换为 MetaHuman 骨骼网格体可用的面部动画参数**。它不仅仅是一个简单的转换工具，更是一个高度可配置的“解算器”。该模块解决的主要问题是：

1.  **动作捕捉数据到动画的映射**：将原始的面部特征点轨迹或深度图数据，通过预定义的算法（Solver）映射到 MetaHuman 脸部的控制器（Controls）上，生成最终的动画序列。
2.  **可配置性与质量控制**：通过 `UMetaHumanFaceAnimationSolver` 对象暴露一系列参数（如深度图影响权重、牙齿处理模式、平滑度），允许艺术家根据不同表演场景和质量需求调整解算行为。
3.  **数据标准化**：为下游系统（如 MetaHuman Sequencer、动画重定向）提供标准化、可用于动画蓝图的解算结果。

它的存在是为了自动化且可控地完成从原始表演数据到高质量数字人面部动画的复杂生产流程。

## 使用场景

-   **影视与过场动画制作**：使用 iPhone TrueDepth 相机或专业动作捕捉设备录制演员表演后，通过此解算器批量或单帧生成 MetaHuman 角色的面部动画，用于电影或游戏过场。
-   **实时虚拟直播（VTuber）**：结合实时面部捕捉流（通过 `MetaHumanCaptureSource` 等模块），使用此解算器的实时配置，驱动 MetaHuman 角色进行直播。
-   **动画质量迭代与精修**：在动画制作流程中，艺术家通过调整解算器的参数（如提高深度图影响以获得更精确的唇形，或增加平滑度以消除抖动），对同一段表演数据进行多次解算，直至获得满意结果。
-   **批处理（Batch Processing）**：通过关联的 `MetaHumanBatchProcessor` 模块，使用统一的解算器配置对大量捕获数据进行无人值守的批量解算。

## 蓝图用法

核心功能通过 `UMetaHumanFaceAnimationSolver` 类暴露。该类通常作为一个可配置的资产（如 Data Asset 或嵌入在更大的 MetaHuman Identity 中）存在，并在处理管线中被引用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bOverrideDeviceConfig` / `DeviceConfig` | 是否覆盖默认设备配置，及指定自定义的 `UMetaHumanConfig` 对象 | `UMetaHumanFaceAnimationSolver` |
| `DepthMapInfluence` | 设置深度图对解算结果的影响程度（无/低/高） | `UMetaHumanFaceAnimationSolver` |
| `EyeSolveSmoothness` | 控制眼睛视线解算结果的平滑程度 (0.0 - 1.0) | `UMetaHumanFaceAnimationSolver` |
| `TeethMode` | 选择牙齿解算模式：使用跟踪点还是估算位置 | `UMetaHumanFaceAnimationSolver` |
| `CanProcess()` | 检查当前配置是否足以进行解算 | `UMetaHumanFaceAnimationSolver` |
| `SettingsOverridden()` | 检查是否有任何默认设置被覆盖 | `UMetaHumanFaceAnimationSolver` |
| `GetSolverConfigData()` | 获取当前解算器配置的 JSON 字符串表示（可导出或用于调试） | `UMetaHumanFaceAnimationSolver` |
| `OnInternalsChanged` | 委托，当解算器内部配置发生变化时广播，用于驱动 UI 更新 | `UMetaHumanFaceAnimationSolver` |

### 使用示例（蓝图描述）

1.  **创建与配置解算器**：
    *   在内容浏览器中右键 -> `Animation` -> `MetaHuman` -> `Face Animation Solver` 创建一个新的 `UMetaHumanFaceAnimationSolver` 资产。
    *   在资产详情面板中，根据需求勾选并设置“Parameters”分类下的参数，例如将 `DepthMapInfluence` 改为 `High`，微调 `EyeSolveSmoothness` 滑块。

2.  **在动画处理流程中使用**：
    *   假设你有一个 `UMetaHumanPerformance`（表演）资产，它包含了捕获的视频和初始解算设置。
    *   在该表演资产的细节面板中，找到解算器配置部分，将其指向你之前创建的 `Face Animation Solver` 资产。
    *   点击“Generate Animation”或类似按钮，流程将使用你配置的解算器来生成最终动画序列。

3.  **响应配置变化**：
    *   如果在一个自定义编辑器工具中动态修改解算器属性，可以绑定到 `OnInternalsChanged` 委托，以便在参数变化时触发UI刷新或验证逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanFaceAnimationSolver.h"
```

### 基本用法

创建并配置一个解算器实例，查询其状态。
*（注：以下代码为基于类接口的示例，并非直接来自测试用例，因为未提供具体测试文件路径。）*

```cpp
// 创建解算器实例 (通常通过 NewObject<UMetaHumanFaceAnimationSolver>)
UMetaHumanFaceAnimationSolver* Solver = NewObject<UMetaHumanFaceAnimationSolver>();

// 检查默认配置是否足够开始处理
if (Solver->CanProcess())
{
    UE_LOG(LogTemp, Log, TEXT("Solver is ready to process with default settings."));
}

// 覆盖默认配置
Solver->bOverrideDepthMapInfluence = true;
Solver->DepthMapInfluence = EDepthMapInfluenceValue::Low;
Solver->bOverrideEyeSolveSmoothness = true;
Solver->EyeSolveSmoothness = 0.3f;

// 检查是否有自定义设置
bool bCustomized = Solver->SettingsOverridden(); // 应为 true

// 获取当前配置的 JSON 字符串，可用于日志或传递给其他系统
FString ConfigJSON = Solver->GetSolverConfigData();
UE_LOG(LogTemp, Log, TEXT("Solver Config:\n%s"), *ConfigJSON);
```

### 进阶用法

在实际的处理管线（Pipeline）中，解算器通常与捕获数据（`UCaptureData`）结合使用，并可能根据数据动态调整配置。

```cpp
// 假设已有 UCaptureData* CaptureData

// 根据捕获数据获取对应的设备配置名称
FString ConfigName;
if (Solver->GetConfigDisplayName(CaptureData, ConfigName))
{
    UE_LOG(LogTemp, Log, TEXT("Effective config for this capture: %s"), *ConfigName);
}

// 获取用于实际解算的数据字符串，这些数据可能被传递给本地或云端的解算服务
FString SolverTemplate = Solver->GetSolverTemplateData(CaptureData);
FString SolverConfig = Solver->GetSolverConfigData(CaptureData);

// 将“易于编辑”的约束条件应用到解算配置数据中（例如，简化用于UI编辑的复杂参数）
FString EasyConfigData = UMetaHumanFaceAnimationSolver::SetEasyToEditControlConstraints(SolverConfig);
```

## Demo 示例

以下是一个最小的、展示如何创建和配置 `UMetaHumanFaceAnimationSolver` 的 C++ 类示例。

**MyFaceSolverUser.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyFaceSolverUser.generated.h"

class UMetaHumanFaceAnimationSolver;

UCLASS()
class MYPROJECT_API AMyFaceSolverUser : public AActor
{
	GENERATED_BODY()

public:
	AMyFaceSolverUser();

	virtual void BeginPlay() override;

	// 在编辑器中可配置的解算器资产引用
	UPROPERTY(EditAnywhere, Category = "MetaHuman")
	TObjectPtr<UMetaHumanFaceAnimationSolver> SolverAsset;

	// 运行时动态创建的解算器
	UPROPERTY(Transient)
	TObjectPtr<UMetaHumanFaceAnimationSolver> RuntimeSolver;
};
```

**MyFaceSolverUser.cpp**
```cpp
#include "MyFaceSolverUser.h"
#include "MetaHumanFaceAnimationSolver.h"

AMyFaceSolverUser::AMyFaceSolverUser()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMyFaceSolverUser::BeginPlay()
{
	Super::BeginPlay();

	// 方式一：使用编辑器中指定的资产
	if (SolverAsset)
	{
		UE_LOG(LogTemp, Log, TEXT("Using solver asset: %s"), *SolverAsset->GetName());
		bool bReady = SolverAsset->CanProcess();
		UE_LOG(LogTemp, Log, TEXT("Asset ready to process: %s"), bReady ? TEXT("Yes") : TEXT("No"));
	}

	// 方式二：在运行时动态创建和配置一个解算器
	RuntimeSolver = NewObject<UMetaHumanFaceAnimationSolver>(this);
	if (RuntimeSolver)
	{
		RuntimeSolver->bOverrideTeethMode = true;
		RuntimeSolver->TeethMode = ETeethMode::Estimated;
		RuntimeSolver->bOverrideEyeSolveSmoothness = true;
		RuntimeSolver->EyeSolveSmoothness = 0.5f;

		UE_LOG(LogTemp, Log, TEXT("Runtime solver created and configured."));
		UE_LOG(LogTemp, Log, TEXT(" - Teeth Mode: Estimated"));
		UE_LOG(LogTemp, Log, TEXT(" - Eye Smoothness: 0.5"));

		// 监听解算器内部变化（示例：绑定一个简单的Lambda）
		RuntimeSolver->OnInternalsChanged().AddLambda([]()
		{
			UE_LOG(LogTemp, Warning, TEXT("Solver internal settings changed!"));
		});

		// 获取解算器模板数据（示例）
		// 在实际项目中，这里会传入真正的 UCaptureData
		FString Template = RuntimeSolver->GetSolverTemplateData(nullptr);
		UE_LOG(LogTemp, Log, TEXT("Solver Template Data (partial): %s"), *Template.Left(200));
	}
}
```

## 模块依赖

`MetaHumanFaceAnimationSolver` 模块本身依赖相对聚焦。根据其用途推断，它依赖于提供核心数据类型和配置的模块。

| 模块 | 用途 |
|---|---|
| `MetaHumanConfig` | 提供 `UMetaHumanConfig` 类，用于存储设备特定的解算器配置。 |
| `MetaHumanCoreTechLib` | 提供底层的核心技术库，可能包含解算算法所需的数学、图像处理等基础功能。 |
| `MetaHumanCaptureUtils` | 可能提供捕获数据的通用工具函数和类型定义。 |
| `MetaHumanPipeline` | 提供处理管线（Pipeline）的框架，解算器是管线中的一个环节。 |

**注意**：上表基于相关模块列表和模块名称推断，实际依赖请以 `MetaHumanFaceAnimationSolver.Build.cs` 文件内容为准。使用者的模块如果要直接使用此解算器，可能需要额外依赖 `MetaHumanConfig` 等模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出，避免冲突 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了MetaHuman角色身上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象，优化性能与显示 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有的网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了定序器缓存相关的问题 |

### 维护评价

**综合评价：活跃维护**

-   **维护频率**：从最近的Git历史看，该模块在**最近一周内**有密集的更新（5次提交），且集中在功能性改进和Bug修复上。
-   **更新内容**：最近的提交涉及身体追踪集成、渲染修复、序列化功能增强和缓存优化，表明开发团队正在积极扩展其功能（如与身体追踪的结合）并解决已知问题。
-   **状态**：该模块是MetaHuman产品线的核心组成部分，**正处于活跃开发和维护中**，没有废弃迹象。
-   **已知限制**：从“Disable level sequence export when body tracking enabled”这条提交可以看出，某些高级功能（如面部+身体动画的组合导出）可能仍在完善和互操作性调试阶段。
-   **推荐使用**：**强烈推荐**。对于所有需要从捕获数据生成MetaHuman面部动画的项目，此模块是官方标准且推荐的解决方案。其活跃的维护保证了稳定性和功能的持续演进。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
-   官方文档：暂无（`.uplugin` 中 DocsURL 为空）
-   测试用例：未在提供信息中指明，可能位于 `Engine/Tests/` 目录下或插件内部的 `Tests` 文件夹中，需进一步查找。