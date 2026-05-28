# Wave Function Collapse (Experimental)

> Wave Function Collapse tools for tile-based model synthesis（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 波函数坍缩工具 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、示例） |
| 模块 | `WaveFunctionCollapse` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/WaveFunctionCollapse) | |

## 用途

该插件为 Unreal Engine 提供了一个**波函数坍缩 (Wave Function Collapse, WFC)** 算法的实现，用于**基于图块（Tile）的程序化内容合成**。它解决了程序化生成场景时，确保生成结果**符合预设空间规则和连接性约束**的问题。开发者可以定义一组图块（例如不同的墙壁、地板、路口模型）以及它们之间的相邻规则（例如“墙壁A的右边只能连接地板B或墙壁C”），然后使用此插件让算法自动推导并填充一个满足所有约束的3D网格布局。其核心目的是为需要动态、多样化且逻辑自洽的场景生成的游戏或应用提供底层工具。

## 使用场景

- 你需要程序化生成一个**地牢、迷宫或城市街区**，并确保相邻房间或建筑的出口、墙壁能够正确连接。
- 你正在开发一个**包含大量重复结构且需要变化**的游戏世界，例如科幻设施、森林、室内场景，希望自动布局并保证视觉和逻辑上的合理性。
- 你已有**一组作为“拼图碎片”的3D模型（StaticMesh或Blueprint）**，并希望它们能基于预设规则自动拼接成一个整体。
- 你需要一个**可重复、可控制的随机场景生成方案**，并且希望有算法来保证每次生成的结果都符合基本的相邻性规则。

## 蓝图用法

插件的核心蓝图逻辑分为两部分：一部分是**工具函数库**，提供算法实现和辅助功能；另一部分是**编辑器子系统**，提供可视化的求解流程控制。

### 核心节点

#### 工具函数库 (`UWaveFunctionCollapseBPLibrary`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DeriveModelFromActors` | 根据场景中一组 Actor 的布局，自动推导出 WFC 模型（约束规则）并添加到模型资产中。 | `UWaveFunctionCollapseBPLibrary` |
| `BuildInitialTile` | 构建一个初始图块，其中包含模型中所有可能的选项。这是 WFC 求解的起点。 | `UWaveFunctionCollapseBPLibrary` |
| `CalculateShannonEntropy` | 根据一组选项及其在模型中的权重，计算香农熵。熵值越低，选项越“确定”。 | `UWaveFunctionCollapseBPLibrary` |
| `GetAdjacentIndices` / `GetAdjacentPositions` | 获取给定网格索引或位置的所有有效相邻索引/位置及其方向。 | `UWaveFunctionCollapseBPLibrary` |
| `MakeEmptyOption` / `MakeBorderOption` / `MakeVoidOption` | 创建代表“空”、“边界”、“虚空”的特殊选项。 | `UWaveFunctionCollapseBPLibrary` |

#### 编辑器子系统 (`UWaveFunctionCollapseSubsystem`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Collapse` | **一键求解**。根据子系统属性中设置的模型、网格分辨率和起点，尝试求解并生成 Actor。 | `UWaveFunctionCollapseSubsystem` |
| `InitializeWFC` | 初始化 WFC 流程，设置图块数组和剩余图块数组。 | `UWaveFunctionCollapseSubsystem` |
| `Observe` | 观察阶段：从最小熵的图块中随机选择一个，并为其选择一个有效选项。 | `UWaveFunctionCollapseSubsystem` |
| `Propagate` | 传播阶段：根据观察阶段的选择，更新相邻图块的剩余选项。 | `UWaveFunctionCollapseSubsystem` |
| `ObservationPropagation` | 递归执行观察和传播，直到所有图块坍缩或遇到矛盾。 | `UWaveFunctionCollapseSubsystem` |
| `DeriveGridFromTransforms` | 从一组变换数组推导出网格的原点和范围。 | `UWaveFunctionCollapseSubsystem` |

### 使用示例（蓝图描述）

1.  **准备模型**：在内容浏览器中创建 `UWaveFunctionCollapseModel` 数据资产。
2.  **定义规则**：
    *   **方式一（手动）**：在蓝图中调用模型的 `AddConstraint` 节点，指定“当某个选项的前方是...时，其右侧可以是...”。
    *   **方式二（自动）**：在场景中摆放好符合你预期的布局（例如一个房间），选中所有相关 Actor，然后调用 `DeriveModelFromActors` 工具函数，将布局转换为规则存入模型。
3.  **配置子系统**：获取 `WaveFunctionCollapseSubsystem`，设置其 `WFCModel` 为你创建的模型，设置 `Resolution`（网格大小，如 `(5, 5, 2)` 表示5x5x2的网格），以及 `OriginLocation`。
4.  **求解生成**：调用子系统的 `Collapse` 函数，它将尝试求解网格。成功后会返回一个新生成的 Actor，其中使用了模型里定义的网格和蓝图，并按照求解结果进行排列。你可以指定尝试次数 (`TryCount`) 和随机种子 (`RandomSeed`) 来控制过程。

## C++ 用法

### 头文件引入

```cpp
#include "WaveFunctionCollapseBPLibrary.h"
#include "WaveFunctionCollapseSubsystem.h"
#include "WaveFunctionCollapseModel.h"
```

### 基本用法

以下是基于源码中关键类和结构的核心用法示例。

**1. 创建和填充模型 (UWaveFunctionCollapseModel)**

```cpp
// 创建模型资产（通常在编辑器或运行时加载）
UWaveFunctionCollapseModel* MyModel = NewObject<UWaveFunctionCollapseModel>();

// 定义几个图块选项
FWaveFunctionCollapseOption OptionWall(TEXT("/Game/Meshes/Wall.Wall"));
FWaveFunctionCollapseOption OptionFloor(TEXT("/Game/Meshes/Floor.Floor"));

// 添加约束规则：墙壁的前方可以连接地板
MyModel->AddConstraint(OptionWall, EWaveFunctionCollapseAdjacency::Front, OptionFloor);
// 地板的后方可以连接墙壁
MyModel->AddConstraint(OptionFloor, EWaveFunctionCollapseAdjacency::Back, OptionWall);
// ... 添加更多约束

// 可选：根据贡献度设置权重
MyModel->SetWeightsFromContributions();
```

**2. 使用子系统进行求解 (UWaveFunctionCollapseSubsystem)**

```cpp
// 获取编辑器子系统
UWaveFunctionCollapseSubsystem* WFCSubsystem = GEditor->GetEditorSubsystem<UWaveFunctionCollapseSubsystem>();
if (WFCSubsystem)
{
    // 配置
    WFCSubsystem->WFCModel = MyModel;
    WFCSubsystem->Resolution = FIntVector(4, 4, 1); // 一个4x4x1的网格
    WFCSubsystem->OriginLocation = FVector(0, 0, 0);

    // 调用求解
    AActor* GeneratedActor = WFCSubsystem->Collapse(10); // 尝试10次
    if (GeneratedActor)
    {
        UE_LOG(LogTemp, Log, TEXT("WFC 成功生成 Actor: %s"), *GeneratedActor->GetName());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("WFC 求解失败"));
    }
}
```

**3. 手动控制求解循环 (高级用法)**

```cpp
// 初始化数据结构
TArray<FWaveFunctionCollapseTile> Tiles;
TArray<int32> RemainingTiles;
TMap<int32, FWaveFunctionCollapseQueueElement> ObservationQueue;
int32 PropagationCount = 0;

// 初始化 WFC
WFCSubsystem->InitializeWFC(Tiles, RemainingTiles);

// 手动执行循环，可以插入自定义逻辑
bool bSuccess = true;
while (RemainingTiles.Num() > 0 && bSuccess)
{
    // 观察
    bSuccess = WFCSubsystem->Observe(Tiles, RemainingTiles, ObservationQueue, 0 /* RandomSeed */);
    if (!bSuccess) break;

    // 传播
    bSuccess = WFCSubsystem->Propagate(Tiles, RemainingTiles, ObservationQueue, PropagationCount);
    if (!bSuccess) break;
}

if (bSuccess)
{
    // 求解成功，使用 Tiles 数组生成 Actor...
    AActor* ResultActor = WFCSubsystem->SpawnActorFromTiles(Tiles); // 注意：SpawnActorFromTiles是私有方法，此处为示意逻辑
}
```

### 进阶用法

**从现有场景推导模型并生成新布局**

```cpp
// 假设有一个数组包含了场景中组成布局的 Actor 指针
TArray<AActor*> LayoutActors;
// ... 填充 LayoutActors

// 使用工具函数推导模型
UWaveFunctionCollapseModel* DerivedModel = NewObject<UWaveFunctionCollapseModel>();
UWaveFunctionCollapseBPLibrary::DeriveModelFromActors(
    LayoutActors,
    DerivedModel,
    200.0f, // TileSize，根据场景中 Actor 间的实际距离设置
    false, // bIsBorderEmptyOption
    false, // bIsMinZFloorOption
    false, // bUseUniformWeightDistribution
    true,  // bAutoDeriveZAxisRotationConstraints，自动生成旋转变体
    TArray<FSoftObjectPath>(), // SpawnExclusionAssets
    TArray<FSoftObjectPath>()  // IgnoreRotationAssets
);

// 现在 DerivedModel 包含了从布局中学到的规则，可以用于生成新的、尺寸不同的相似布局
WFCSubsystem->WFCModel = DerivedModel;
WFCSubsystem->Resolution = FIntVector(6, 6, 1); // 生成一个更大的网格
AActor* NewLayoutActor = WFCSubsystem->Collapse();
```

## Demo 示例

一个最小的、可用于测试 WFC 流程的 Actor 类。

**WaveFunctionCollapseDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WaveFunctionCollapseDemoActor.generated.h"

class UWaveFunctionCollapseModel;

UCLASS()
class YOURPROJECT_API AWaveFunctionCollapseDemoActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AWaveFunctionCollapseDemoActor();

protected:
	virtual void BeginPlay() override;

public:	
	UPROPERTY(EditAnywhere, Category = "WFC Demo")
	TObjectPtr<UWaveFunctionCollapseModel> DemoModel;

	UPROPERTY(EditAnywhere, Category = "WFC Demo")
	FIntVector GridResolution = FIntVector(3, 3, 1);

	// 按下按键进行生成测试
	void GenerateLayout();
};
```

**WaveFunctionCollapseDemoActor.cpp**
```cpp
#include "WaveFunctionCollapseDemoActor.h"
#include "WaveFunctionCollapseSubsystem.h"
#include "WaveFunctionCollapseModel.h"

AWaveFunctionCollapseDemoActor::AWaveFunctionCollapseDemoActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AWaveFunctionCollapseDemoActor::BeginPlay()
{
	Super::BeginPlay();

	// 绑定输入，例如按下 'G' 键生成
	// InputComponent->BindAction("Generate", IE_Pressed, this, &AWaveFunctionCollapseDemoActor::GenerateLayout);
}

void AWaveFunctionCollapseDemoActor::GenerateLayout()
{
	if (!DemoModel)
	{
		UE_LOG(LogTemp, Error, TEXT("DemoModel is not set!"));
		return;
	}

	UWaveFunctionCollapseSubsystem* WFCSubsystem = GEditor->GetEditorSubsystem<UWaveFunctionCollapseSubsystem>();
	if (WFCSubsystem)
	{
		WFCSubsystem->WFCModel = DemoModel;
		WFCSubsystem->Resolution = GridResolution;
		WFCSubsystem->OriginLocation = GetActorLocation();

		AActor* Result = WFCSubsystem->Collapse(5); // 尝试5次
		if (Result)
		{
			UE_LOG(LogTemp, Log, TEXT("Generated: %s"), *Result->GetName());
			// 可以在此处对 Result 进行进一步操作
		}
	}
}
```

## 模块依赖

从源码结构推断，该插件主要依赖 UE 的核心和引擎模块，无特殊第三方依赖。

| 模块 | 用途 |
|---|---|
| `Core`, `Engine` 等 | 标准 UE 依赖 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移，属于引擎级代码维护性更新。 |
| 2025-05-12 | `869e8f18` | Replace short or incorrect path names in metadata with long or correct ones | 修正元数据中的路径名称，不影响功能。 |
| 2025-03-19 | `2596d96b` | [WFC] Use generated class for wave function collapse with blueprints | 重要功能更新：允许在蓝图中使用生成的类。 |
| 2024-01-25 | `f43fc1d7` | Fixed up more bool-taking calls to take EAllowShrinking instead. | 引擎 API 适配性修复。 |
| 2023-02-27 | `5f370d9b` | Fixed static analysis warnings exposed by the log macro refactor | 修复静态分析警告。 |

### 维护评价

- **创建时间**：2022年3月，是一个相对较新的实验性插件。
- **活跃度**：从更新历史看，最近的更新（2025年）包含了一项**功能性改进**（蓝图类支持），但主要更新仍围绕引擎代码迁移和兼容性修复，而非插件自身功能的大幅扩展。最近一次实质性功能更新在2025年3月。
- **状态**：**实验性 (Experimental)**，且默认未安装 (`Installed: false`)。这意味着 Epic 可能仍在评估其稳定性和 API 设计，未来版本可能发生不兼容变更。
- **结论**：该插件提供了一个完整的、可用的 WFC 实现，适合用于原型开发和实验。对于生产项目，需要谨慎评估其“实验性”状态带来的风险。建议密切关注引擎版本更新日志，以了解其状态变化。目前**推荐用于探索和原型阶段**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/WaveFunctionCollapse)
- [官方文档]( )（暂无）