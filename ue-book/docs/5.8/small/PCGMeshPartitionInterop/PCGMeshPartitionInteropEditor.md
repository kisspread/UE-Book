# PCG Mesh Partition Interop

> Interoperability of Mesh Partition with PCG.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | PCG网格分区互操作 |
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `PCGMeshPartitionInterop` (Runtime), `PCGMeshPartitionInteropEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop) | |

## 用途

这个插件为 PCG（程序化内容生成框架）和 Mesh Partition（网格分区）系统之间提供桥梁。它解决的核心问题是：**如何让 PCG 能够采样和使用 Mesh Partition 构建的网格数据（例如地形网格）**。

Mesh Partition 系统用于将大型网格（如地形）分割成多个区块（Section）进行高效处理。PCG 系统则基于空间数据（如点、线、网格表面）来程序化生成内容。这个插件通过在 Mesh Partition 构建的网格上附加特定的组件，将网格数据转换为 PCG 可以访问和采样的格式（缓存的动态网格和 AABB 树），从而实现了两个系统之间的互操作性。

## 使用场景

- 你使用 Mesh Partition 系统构建了一个可交互或动态的地形网格，并希望基于该地形的表面（如坡度、法线、位置）使用 PCG 来程序化生成植被、石头或装饰物。
- 你需要在编辑器或运行时，从 Mesh Partition 构建的最终网格上获取精确的几何信息（用于碰撞、射线检测或采样），并将其传递给 PCG 工作流。
- 你在开发一个包含程序化生成地形和内容的关卡，需要将网格构建和内容生成两个流程无缝集成。

## 蓝图用法

该插件主要通过组件（Component）而非蓝图节点进行交互。核心类 `UPCGAdapterComponent` 是一个修改器组件（ModifierComponent），需要添加到参与 Mesh Partition 的 Actor 上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PostBuildSectionMesh` | 当网格分区构建完成一个区块的网格后被调用，用于在该网格上生成 PCG 数据组件 | `UPCGAdapterComponent` |
| `ComputeBounds` | 计算该适配器组件影响的空间包围盒 | `UPCGAdapterComponent` |

### 使用示例（蓝图描述）

1. **添加组件**：在你的 Actor（例如一个网格分区 Actor）上，添加 `Mesh Partition PCG Adapter Component`。该组件会作为该 Actor 的修改器。
2. **自动工作流**：当 Mesh Partition 系统构建网格时，会调用 `UPCGAdapterComponent::PostBuildSectionMesh`。这个方法会在最终生成的网格 Actor 上自动添加一个 `UPCGDataComponent`（来自 MeshPartition 模块）。
3. **数据生成**：`UPCGDataComponent` 内部会缓存构建好的 `FDynamicMesh` 及其 AABB 树。这使得 PCG 系统可以在运行时或编辑器中通过该组件访问到精确的网格数据。
4. **PCG 采样**：在 PCG 图表中，你可以使用需要输入网格或表面数据的节点（如 `Get Surface` 或 `Sample Mesh`），并将它们连接到代表该网格数据的 PCG 数据引脚上。

## C++ 用法

### 头文件引入

```cpp
// 如果需要在运行时或编辑器中使用适配器组件
#include "MeshPartitionPCGAdapterComponent.h"

// 如果需要自定义编辑器设置或可视化
#include "PCGMeshPartitionInteropEditorSettings.h"
#include "PCGMeshTerrainSectionDataVisualization.h"
```

### 基本用法

**创建自定义 PCG 适配器组件（示例）**

这个例子展示如何创建一个继承自 `UPCGAdapterComponent` 的自定义组件，以在网格分区完成后执行额外逻辑。

```cpp
// MyCustomAdapterComponent.h
#pragma once

#include "MeshPartitionPCGAdapterComponent.h"
#include "MyCustomAdapterComponent.generated.h"

UCLASS(ClassGroup=(MeshPartition), meta=(BlueprintSpawnableComponent, DisplayName="My Custom PCG Adapter"))
class UMyCustomAdapterComponent : public UPCGAdapterComponent
{
	GENERATED_BODY()

public:
	// 重写 PostBuildSectionMesh 以添加自定义行为
	virtual void PostBuildSectionMesh(AActor* InSection, const MeshPartition::FMeshData& InBuiltMesh) override;
};

// MyCustomAdapterComponent.cpp
#include "MyCustomAdapterComponent.h"

void UMyCustomAdapterComponent::PostBuildSectionMesh(AActor* InSection, const MeshPartition::FMeshData& InBuiltMesh)
{
	// 首先，调用父类实现以确保 PCGDataComponent 被正确添加和初始化
	Super::PostBuildSectionMesh(InSection, InBuiltMesh);

	// 在这里添加你的自定义逻辑
	// 例如：记录日志，或基于新构建的网格数据设置其他属性
	UE_LOG(LogTemp, Log, TEXT("Custom PCG Adapter: Section '%s' mesh built with %d vertices."),
		*InSection->GetName(), InBuiltMesh.Vertices.Num());
}
```

### 进阶用法

**自定义编辑器设置和数据可视化（编辑器模块）**

这个例子展示如何扩展编辑器模块的功能，例如为新的 PCG 数据类型注册自定义的颜色和可视化。

```cpp
// 假设我们定义了一种新的数据类型，并希望为其创建可视化
#include "PCGMeshPartitionInteropEditorModule.h"
#include "PCGMeshTerrainSectionDataVisualization.h"

// 在编辑器模块的 StartupModule 中注册
void FPCGMegaMeshInteropEditorModule::StartupModule()
{
	// 注册自定义的 PCG 数据引脚颜色（例如，为我们的新数据类型）
	// RegisterPinColors();

	// 注册自定义的数据可视化器
	// RegisterDataVisualizations();
}

// 一个简化的自定义可视化器示例
class FMyCustomPCGDataVisualization : public IPCGDataVisualization
{
public:
	virtual void ExecuteDebugDisplay(FPCGContext* Context, const UPCGSettingsInterface* SettingsInterface, const UPCGData* Data, AActor* TargetActor) const override
	{
		// 实现自定义的调试显示逻辑，例如在场景中绘制网格采样点
		if (const UMyCustomPCGData* MyData = Cast<UMyCustomPCGData>(Data))
		{
			// ... 绘制逻辑
		}
	}

	virtual FPCGTableVisualizerInfo GetTableVisualizerInfoWithDomain(const UPCGData* Data, const FPCGMetadataDomainID& DomainID) const override
	{
		FPCGTableVisualizerInfo Info;
		// ... 定义表格可视化器要显示哪些属性
		return Info;
	}
};
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何创建一个使用 PCG 适配器的简单网格分区 Actor。

**头文件 (MyPartitionActor.h):**
```cpp
#pragma once

#include "GameFramework/Actor.h"
#include "MyPartitionActor.generated.h"

class UPCGAdapterComponent;

UCLASS()
class AMyPartitionActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AMyPartitionActor();

protected:
	virtual void BeginPlay() override;

public:	
	virtual void Tick(float DeltaTime) override;

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mesh Partition")
	TObjectPtr<UPCGAdapterComponent> PCGAdapter;
};

**源文件 (MyPartitionActor.cpp):**
```cpp
#include "MyPartitionActor.h"
#include "MeshPartitionPCGAdapterComponent.h"

AMyPartitionActor::AMyPartitionActor()
{
	PrimaryActorTick.bCanEverTick = false;

	// 创建一个根场景组件
	USceneComponent* Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);

	// 添加 PCG 适配器组件
	PCGAdapter = CreateDefaultSubobject<UPCGAdapterComponent>(TEXT("PCGAdapter"));
	PCGAdapter->SetupAttachment(Root);
}

void AMyPartitionActor::BeginPlay()
{
	Super::BeginPlay();
	// Mesh Partition 系统会在构建网格时自动调用 PCGAdapter->PostBuildSectionMesh
}

void AMyPartitionActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}
```

## 模块依赖

从 `PCGMeshPartitionInterop.Build.cs` 和 `PCGMeshPartitionInteropEditor.Build.cs` 的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames` 中提取。该插件有明确的插件依赖，其模块主要依赖这些插件提供的模块。

| 模块 | 用途 |
|---|---|
| `PCG` | 核心 PCG 框架模块，提供数据、节点和图表运行时基础 |
| `MeshPartition` | 核心网格分区系统，提供网格构建、区块管理等基础功能 |
| `GeometryScript` | 几何脚本模块，可能用于动态网格操作 |
| `PCGGeometryScriptInterop` | PCG 与 GeometryScript 的互操作模块 |

*注：常见的 Core、Engine、Slate 等模块依赖已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `99ccb29e` | [PCG] Fix crash in BakeMeshAttr/BakeMeshTerrainSection reading RHI resources that either aren't resi | 修复烘焙网格属性时读取无效RHI资源导致的崩溃 |
| 2026-05-14 | `82d81c0e` | [PCG] Add Bake Mesh Terrain Section Mesh node | 新增烘焙网格地形区块网格的PCG节点 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告 |
| 2026-05-13 | `0fc2fa0f` | [PCG] Track Final layer key for refresh on modifier changes in Get Mesh Terrain Section node | 优化获取网格地形区块节点，跟踪最终图层键以响应修改器变化 |
| 2026-05-13 | `6cf8f045` | [PCG] Fix GPU crash arising from binding a compressed texture as a UAV which is not supported. | 修复将压缩纹理绑定为UAV（不支持）导致的GPU崩溃 |

### 维护评价

该插件处于**活跃开发**状态。
- **创建时间**：2026年3月，是一个非常新的插件。
- **更新频率**：最近一个月内有密集的提交（5次），且集中在功能性更新和关键bug修复上（如崩溃修复、新节点添加），表明其处于快速迭代期。
- **实验性标签**：插件明确标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，这确认了其**实验性**状态。这意味着其API和功能未来可能发生重大变化，不建议在核心生产项目中使用，但非常适合用于原型设计和功能验证。
- **已知问题**：从提交记录看，近期修复了多个GPU相关的崩溃问题，说明在涉及图形资源（RHI， UAV）时仍可能存在稳定性挑战。
- **推荐使用**：如果你正在探索PCG与Mesh Partition的集成，并且可以接受实验性API的风险，这是一个**值得关注和试用**的插件。对于生产环境，建议等待其API稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGMeshPartitionInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/) (PCG框架总体文档，插件特定文档可能尚未发布)
- 测试用例路径：`Engine/Plugins/Experimental/PCGMeshPartitionInterop/Tests/` (如果存在)