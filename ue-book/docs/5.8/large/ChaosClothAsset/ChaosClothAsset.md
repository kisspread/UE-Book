# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 基于样片的布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有布料资产、编辑器工具 |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

ChaosClothAsset 插件为 UE5 的 Chaos 布料模拟系统提供了一套基于“样片”（Pattern）的资产创建和管理工作流。它解决的核心问题是：如何将传统的 3D 布料建模过程（在 2D 软件中绘制衣片/Pattern，然后缝合）与 UE 的物理模拟无缝集成。

与简单的布料模拟不同，该插件允许：
1.  **分离模拟网格与渲染网格**：开发者可以为物理模拟使用简化的拓扑结构，同时为视觉渲染使用高细节网格。
2.  **精确的物理属性控制**：支持定义面料（Fabric）参数（如弯曲刚度、拉伸刚度）、模拟求解器设置、缝合（Seam）信息等。
3.  **与 Dataflow 节点集成**：允许通过数据流图表进行程序化布料资产的构建和修改。
4.  **复杂的布料编辑功能**：如蒙皮权重绘制、最大距离约束、背面停止（Backstop）设置，以及更高级的代理变形器（Proxy Deformer）和形态目标（Morph Target）支持。

该插件是连接艺术家布料建模工具（如 Marvelous Designer）和 UE 运行时布料模拟的桥梁。

## 使用场景

-   你正在开发一个需要高质量服装模拟的游戏（如 MMORPG、开放世界游戏），需要导入从 Marvelous Designer 等软件创建的布料模型并精确控制其物理表现。
-   你需要为窗帘、旗帜、帐篷等物件创建复杂的、基于物理的动画，并希望将其作为可管理的资产而非纯代码实现。
-   你的团队使用 Dataflow 进行程序化内容生成，希望将布料资产的创建和修改也纳入该工作流。
-   你需要为不同 LOD 设置不同的布料模拟细节，并希望统一管理它们的物理属性。

## 蓝图用法

该插件主要提供底层的 C++ API 和编辑器工具，供引擎内部或高级插件调用。其数据结构（`FManagedArrayCollection`）和 Facade 类通常在编辑器扩展或资产处理代码中操作，而非直接在蓝图事件图表中暴露为节点。

蓝图用户主要通过以下方式与之交互：
1.  **创建和编辑 ChaosClothAsset 资产**：在内容浏览器中右键创建 `ChaosClothAsset` 资产，并使用属性编辑器调整其参数。
2.  **在 Skeletal Mesh 或 Groom Asset 中引用**：将布料资产分配给骨骼网格的布料部分。
3.  **通过 Dataflow 图表操作**：使用与 ChaosClothAsset 相关的 Dataflow 节点来程序化生成或修改布料数据。

### 核心节点
该插件的核心是数据结构和 C++ Facade 类，没有直接暴露可调用的蓝图函数节点。其功能通过资产系统和编辑器工具链体现。

### 使用示例（蓝图描述）
1.  在内容浏览器中右键，选择 `Physics` -> `ChaosClothAsset` 创建新资产。
2.  双击打开资产编辑器。
3.  在“材质”部分指定用于渲染的材质。
4.  在“模拟网格”和“渲染网格”部分，导入或关联你的 2D/3D 网格数据（通常通过编辑器工具或 Dataflow 流程完成）。
5.  调整“求解器”和“面料”组中的物理参数。
6.  将配置好的布料资产应用到角色的 Skeletal Mesh 组件上。

## C++ 用法

该插件的核心是 `FCollectionClothFacade` 和一系列子 Facade 类，它们封装了底层的 `FManagedArrayCollection`，提供了结构化、类型安全的接口来操作布料集合的各个部分（模式、顶点、面、面料、缝合线等）。

### 头文件引入

```cpp
#include "ChaosClothAsset/CollectionClothFacade.h"
#include "ChaosClothAsset/ClothGeometryTools.h"
// 根据需要引入其他 Facade 头文件，如：
// #include "ChaosClothAsset/CollectionClothSimPatternFacade.h"
// #include "ChaosClothAsset/CollectionClothFabricFacade.h"
```

### 基本用法
以下示例展示了如何创建一个简单的布料集合并添加一个模拟模式。

*来源: `CollectionClothFacade.h`, `CollectionClothSimPatternFacade.h` 中的类定义和方法推断。*

```cpp
using namespace UE::Chaos::ClothAsset;

// 1. 创建一个空的 FManagedArrayCollection
TSharedRef<FManagedArrayCollection> ClothData = MakeShared<FManagedArrayCollection>();

// 2. 创建一个 FCollectionClothFacade 来操作这个集合
FCollectionClothFacade ClothFacade(ClothData);

// 3. 定义布料数据结构 (初始化 Schema)
ClothFacade.DefineSchema(EClothCollectionExtendedSchemas::None);

// 4. 添加一个模拟模式 (Sim Pattern)
int32 PatternIndex = ClothFacade.AddSimPattern();
FCollectionClothSimPatternFacade PatternFacade = ClothFacade.GetSimPattern(PatternIndex);

// 5. 初始化该模式：提供 2D 位置、3D 位置和三角形索引
TArray<FVector2f> Positions2D = { /* ... */ };
TArray<FVector3f> Positions3D = { /* ... */ };
TArray<FIntVector3> Indices = { /* ... */ };
PatternFacade.Initialize(Positions2D, Positions3D, Indices);

// 6. 设置面料属性 (可选)
int32 FabricIndex = ClothFacade.AddFabric();
FCollectionClothFabricFacade FabricFacade = ClothFacade.GetFabric(FabricIndex);
FabricFacade.Initialize(
    FCollectionClothFabricConstFacade::FAnisotropicData(100.f, 100.f, 100.f), // BendingStiffness
    0.5f,   // BucklingRatio
    FCollectionClothFabricConstFacade::FAnisotropicData(50.f, 50.f, 50.f),   // BucklingStiffness
    FCollectionClothFabricConstFacade::FAnisotropicData(100.f, 100.f, 100.f), // StretchStiffness
    0.35f,  // Density
    0.8f,   // Friction
    0.1f,   // Damping
    0.0f,   // Pressure
    INDEX_NONE, // Layer
    1.0f    // CollisionThickness
);

// 7. 将模式与面料关联
PatternFacade.SetFabricIndex(FabricIndex);
```

### 进阶用法
以下示例演示如何操作缝合线和使用 `FClothGeometryTools` 来清理网格。

*来源: `CollectionClothFacade.h`, `CollectionClothSeamFacade.h`, `ClothGeometryTools.h`。*

```cpp
using namespace UE::Chaos::ClothAsset;

// 假设已有一个 ClothFacade 和对应的 PatternFacade

// --- 操作缝合线 (Seam) ---
// 添加一个缝合线
int32 SeamIndex = ClothFacade.AddSeam();
FCollectionClothSeamFacade SeamFacade = ClothFacade.GetSeam(SeamIndex);

// 定义针脚 (Stitches)：每对 (Index2D_A, Index2D_B) 表示将 2D 顶点 A 和 B 缝合
TArray<FIntVector2> Stitches;
Stitches.Add(FIntVector2(0, 5));
Stitches.Add(FIntVector2(1, 6));
// ... 添加更多针脚
SeamFacade.Initialize(Stitches);

// 清理缝合线中无效的索引
SeamFacade.CleanupAndCompact();

// --- 使用几何工具 ---
TSharedRef<FManagedArrayCollection> ConstClothData = ClothData;

// 检查是否有有效的模拟网格
bool bHasSim = FClothGeometryTools::HasSimMesh(ConstClothData);

// 清理网格：移除退化三角形、孤立顶点，并压缩数据
FClothGeometryTools::CleanupAndCompactMesh(ClothData);

// 反转模拟网格的法线（例如，如果布料内外穿反了）
FClothGeometryTools::ReverseMesh(
    ClothData,
    true,  // bReverseSimMeshNormals
    false, // bReverseSimMeshWindingOrder
    false, // bReverseRenderMeshNormals
    false, // bReverseRenderMeshWindingOrder
    TArray<int32>(), // SimPatternSelection (空则处理所有)
    TArray<int32>()  // RenderPatternSelection
);
```

## Demo 示例

一个创建基本布料集合并读取数据的最小示例。

*ChaosClothDemo.h*
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/EngineSubsystem.h"
#include "ChaosClothDemo.generated.h"

UCLASS()
class UChaosClothDemoSubsystem : public UEngineSubsystem
{
	GENERATED_BODY()
public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;
};
```

*ChaosClothDemo.cpp*
```cpp
#include "ChaosClothDemo.h"
#include "ChaosClothAsset/CollectionClothFacade.h"

void UChaosClothDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);

	UE_LOG(LogTemp, Log, TEXT("ChaosClothDemoSubsystem Initialized"));

	using namespace UE::Chaos::ClothAsset;

	// 创建一个示例布料集合
	TSharedRef<FManagedArrayCollection> DemoClothData = MakeShared<FManagedArrayCollection>();
	FCollectionClothFacade Facade(DemoClothData);

	// 定义 Schema
	Facade.DefineSchema();

	// 添加一个模拟模式并初始化
	int32 PatternIdx = Facade.AddSimPattern();
	auto Pattern = Facade.GetSimPattern(PatternIdx);

	TArray<FVector2f> Pos2D = { FVector2f(0, 0), FVector2f(1, 0), FVector2f(0, 1) };
	TArray<FVector3f> Pos3D = { FVector3f(0, 0, 0), FVector3f(100, 0, 0), FVector3f(0, 100, 0) };
	TArray<FIntVector3> Tri = { FIntVector3(0, 1, 2) };
	Pattern.Initialize(Pos2D, Pos3D, Tri);

	// 通过常量 Facade 读取数据
	FCollectionClothConstFacade ConstFacade(DemoClothData);
	int32 NumPatterns = ConstFacade.GetNumSimPatterns();
	UE_LOG(LogTemp, Log, TEXT("Created cloth collection with %d sim pattern(s)."), NumPatterns);

	if (NumPatterns > 0)
	{
		auto ConstPattern = ConstFacade.GetSimPattern(0);
		int32 NumVertices = ConstPattern.GetNumSimVertices2D();
		UE_LOG(LogTemp, Log, TEXT("Pattern 0 has %d sim vertices."), NumVertices);
	}
}

void UChaosClothDemoSubsystem::Deinitialize()
{
	UE_LOG(LogTemp, Log, TEXT("ChaosClothDemoSubsystem Deinitialized"));
	Super::Deinitialize();
}
```

## 模块依赖

使用此插件时，你的模块需要依赖以下模块（除了标准的 Core/Engine 等）：

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 提供核心的布料集合数据结构和 Facade 类 |
| `ChaosClothAssetEngine` | 包含布料资产引擎相关逻辑 |
| `GeometryFramework` | 提供 `FDynamicMesh3` 等几何操作工具（如果使用 `FClothGeometryTools`） |
| `MeshConversion` | 提供 `FMeshDescription` 与 `FDynamicMesh3` 之间的转换 |
| `DataflowEngine` | 提供 Dataflow 图表引擎支持（如果集成 Dataflow） |
| `ChaosCloth` | Chaos 布料模拟核心模块（插件已声明依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Blueprint reinstancing | 修复蓝图重实例化时布料组件“在编辑器中模拟”属性丢失的问题 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable. | 将并行布料模拟等待点从帧末移至最后可降级任务组，优化性能 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset. | 为 ClothAssetSKMClothingAsset 实现骨骼映射刷新功能 |
| 2026-05-22 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |

### 维护评价

**积极维护中**。该插件自 2024 年 3 月从实验阶段移出并标记为 Beta 以来，一直在持续更新。从近期（2026年5月）的提交记录看，开发团队正在积极修复 Bug（如蓝图实例化问题）和进行性能优化（模拟任务调度），表明这是一个受重视且活跃开发中的功能模块。

-   **创建时间**：2024-03-22（约 2 年）。
-   **维护频率**：近期更新非常频繁（多条在 2026-05 的提交），且包含实质性功能修复和优化。
-   **活跃状态**：**活跃维护**。
-   **已知限制**：作为相对较新的资产类型，其工具链和 Dataflow 节点集可能仍在快速迭代中。默认禁用 (`EnabledByDefault: false`) 状态也表明 Epic 可能认为其 API 尚未完全稳定。
-   **推荐使用**：**推荐**。对于需要高质量、可定制布料模拟的项目，这是目前 UE5 的官方解决方案。建议密切关注其更新日志，并将项目依赖版本锁定在经过充分测试的引擎版本上。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
-   [官方文档]() (暂无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset/Tests) (位于插件目录下的 Tests 文件夹，具体文件需查阅源码)