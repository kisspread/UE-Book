# Hair Card Generator

> Procedurally generate hair cards from hair strands

| 属性 | 值 |
|---|---|
| 中文名 | 发卡生成器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HairCardGeneratorDataflow` (Runtime), `HairCardGeneratorEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairCardGenerator) | |

## 用途

传统流程中，从高精度毛发发丝（Groom）生成可用于实时渲染的头发卡片（Hair Cards）需要大量手动建模、UV 拆分和纹理制作，耗时且难以迭代。  
该插件基于 **Epic Dataflow 系统**，提供一套程序化节点管道，将 `UGroomAsset` 中的发丝数据（曲线、簇组）自动转换为 **头发卡片几何体、UV 和纹理**，并可直接输出为静态网格体（`UStaticMesh`）或毛发资产（`UHairCardGenerationAsset`）。  
**核心目标**：将“发丝→卡片”的全流程自动化，支持 LOD 分级控制、每簇参数覆盖、自适应细分等高级功能，使得美术人员只需调整几组数值即可快速得到不同精度的卡片，大幅提升毛发资产生产效率。

## 使用场景

- 你需要为角色或生物生成**低面数、高性能的头发渲染资产**（如游戏内 NPC、实时过场）→ 用 Hair Card Generator 从白模发丝直接输出卡片。
- 你正在制作**开放世界或多人游戏**，需要大量不同发型且需控制开销 → 通过 LOD 设置快速生成多级卡片。
- 你是**技术美术或程序化内容开发者**，希望将头发管线集成到 Dataflow 图中，与其他几何处理节点（如减面、重拓扑）串联 → 该插件节点可作为 Dataflow 的中间/末端节点。
- 你需要对特定发簇（如刘海、长辫）单独调整卡片密度或纹理数量 → 使用每 LOD 的“Override Settings”数组进行精准控制。

## 蓝图用法

该插件所有逻辑封装为 **Dataflow 节点**，不提供直接的 `BlueprintCallable` 函数。你需要在 **Dataflow Blueprint** 或 **Dataflow 编辑器** 中连接节点使用。

### 核心节点

所有节点属于 `Groom` 分类，具有相同的端口约定：输入/输出为 `FManagedArrayCollection`（数据流通用容器）和一个 `TArray<FGroomCardsSettings>`（生成设置）。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BuildCardsSettings` | 构建卡片生成的主配置对象，包含 LOD 组、过滤规则、高级生成选项。通常作为第一个节点，提供全局设置。 | `UBuildCardsSettingsNode`（实际为 `FGroomCardsSettings` 结构体，在 `BuildCardsSettingsNode.h` 定义） |
| `GenerateCardsClumps` | 从发丝曲线生成卡片簇（Clumps）。可覆盖每 LOD 的卡片数量和飞发数量。 | `FGenerateCardsClumpsNode` |
| `GenerateCardsGeometry` | 根据簇形状生成卡片几何体（顶点、三角面）。支持自适应细分。 | `FGenerateCardsGeometryNode` |
| `GenerateCardsTextures` | 为卡片生成纹理（UV、覆盖贴图、方向贴图等）。 | `FGenerateCardsTexturesNode` |
| `CardsAssetTerminal` | 数据流终点节点，将管道计算结果输出为最终资产（如 `UStaticMesh` 或自定义卡片资产）。 | `FCardsAssetTerminalNode` |

### 使用示例（蓝图描述）

假设你想从一根发丝资源快速生成 LOD0/1 两组卡片：

1. 打开 **Dataflow 编辑器**，创建新的 Dataflow 资产。
2. 拖入 `BuildCardsSettings` 节点，在细节面板中：
   - `GroomAsset`：指定目标 `UGroomAsset`。
   - `GenerationFlags`：勾选需要生成的资产类型（如网格、纹理）。
   - `PipelineFlags`：选择要执行的步骤（Clumps, Geometry, Textures）。
   - 在 `Filter Settings` 数组中添加两个条目，分别命名为 `LOD0` 和 `LOD1`，设置不同的 `NumClumps`、`NumTriangles`、`NumTextures`。
3. 拖入 `GenerateCardsClumps` 节点，将 `BuildCardsSettings` 的 `Collection` 输出连接到其 `Collection` 输入，`CardsSettings` 输出连接到其 `CardsSettings` 输入。可在 `Override Settings` 中为每个 LOD 单独调整簇数量。
4. 类似连接 `GenerateCardsGeometry` 和 `GenerateCardsTextures`，形成链式管道。
5. 最终放置 `CardsAssetTerminal`，将其 `Collection` 输入连接到前一根管的输出。在终端节点的 `CardsSettings` 端口传入最终的设置数组。
6. 运行 Dataflow，终端节点会自动生成并保存资产（需预先在终端细节面板设置输出路径等属性）。

## C++ 用法

### 头文件引入

```cpp
#include "HairCardGeneratorDataflowModule.h"
#include "BuildCardsSettingsNode.h"
#include "GenerateCardsClumpsNode.h"
#include "GenerateCardsGeometryNode.h"
#include "GenerateCardsTexturesNode.h"
#include "CardsAssetTerminalNode.h"
// Dataflow 基础
#include "Dataflow/DataflowCore.h"
#include "Dataflow/DataflowEngine.h"
```

### 基本用法

通过 Dataflow 的图构建 API 创建并连接节点。示例来自插件内部测试（路径：`Engine/Plugins/Experimental/HairCardGenerator/Source/HairCardGeneratorDataflow/Private/*.cpp`）：

```cpp
// 1. 创建数据流上下文
UE::Dataflow::FContext Context;
FManagedArrayCollection Collection;

// 2. 创建节点实例（通过 FDataflowNode 工厂或直接 new）
FGenerateCardsClumpsNode ClumpsNode(UE::Dataflow::FNodeParameters());
FGenerateCardsGeometryNode GeometryNode(UE::Dataflow::FNodeParameters());

// 3. 准备设置数据
FGroomCardsSettings MainSettings;
MainSettings.GroomAsset = LoadObject<UGroomAsset>(nullptr, TEXT("/Game/Hair/MyHair.MyHair"));
MainSettings.GenerationFlags = 0xFF; // 全开
MainSettings.PipelineFlags = 0x07;   // Clumps|Geometry|Textures

// 4. 构建设置节点（使用 FGroomAdvancedGenerationSettings 辅助）
// 注意：BuildCardsSettings 不是一个独立节点，而是通过结构体传递。通常由终端节点消费。
// 更典型的用法：直接构造 TArray<FGroomCardsSettings> 并绑定到输入端口。

TArray<FGroomCardsSettings> CardsSettings = { MainSettings };

// 5. 连接节点（伪代码，实际需通过 FDataflowConnection 接口）
ClumpsNode.SetInput("Collection", Collection);
ClumpsNode.SetInput("CardsSettings", CardsSettings);
GeometryNode.SetInput("Collection", ClumpsNode.GetOutput("Collection"));
GeometryNode.SetInput("CardsSettings", ClumpsNode.GetOutput("CardsSettings"));

// 6. 执行评估
ClumpsNode.Evaluate(Context, /* out */);
GeometryNode.Evaluate(Context, /* out */);
```

### 进阶用法

**多 LOD 设置**：填充 `FGroomFilterSettings` 数组，每个元素对应一个 LOD 级别：

```cpp
TArray<FGroomFilterSettings> FilterSettings;
FGroomFilterSettings LOD0;
LOD0.FilterName = TEXT("LOD0");
LOD0.NumClumps = 200;
LOD0.NumTriangles = 8000;
LOD0.NumTextures = 150;
FilterSettings.Add(LOD0);

FGroomFilterSettings LOD1;
LOD1.FilterName = TEXT("LOD1");
LOD1.NumClumps = 50;
LOD1.NumTriangles = 2000;
LOD1.NumTextures = 75;
FilterSettings.Add(LOD1);

FGroomAdvancedGenerationSettings AdvSettings;
AdvSettings.FilterSettings = FilterSettings;
// AdvSettings 其他选项可在此设置

// 然后构造 FGroomCardsSettings 并赋值 GenerationSettings->AdvancedSetup = AdvSettings;
```

**自定义渲染管线注册**：在模块启动时，你可以调用 `UE::CardGen::Private::RegisterCollectionRenderableTypes()` 来注册自定义渲染类型，这样数据流中生成的几何体能在编辑器视口中正确高亮显示。

## Demo 示例

以下是一个完整的 C++ 函数，演示如何通过 Dataflow 生成卡片几何并保存为 `UStaticMesh`。假设已在模块的 `StartupModule` 中注册了必要节点。

**HairCardGenDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "HairCardGenDemo.generated.h"

UCLASS()
class UHairCardGenDemo : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION()
    void GenerateHairCardsDemo();
};
```

**HairCardGenDemo.cpp**
```cpp
#include "HairCardGenDemo.h"
#include "BuildCardsSettingsNode.h"
#include "GenerateCardsClumpsNode.h"
#include "GenerateCardsGeometryNode.h"
#include "GenerateCardsTexturesNode.h"
#include "CardsAssetTerminalNode.h"
#include "Dataflow/DataflowCore.h"

void UHairCardGenDemo::GenerateHairCardsDemo()
{
    using namespace UE::Dataflow;

    // 1. 加载 Groom 资产
    UGroomAsset* Groom = LoadObject<UGroomAsset>(nullptr, TEXT("/Game/Hair/SimpleHair.SimpleHair"));
    if (!Groom) return;

    // 2. 创建设置
    FGroomCardsSettings CardsSettings;
    CardsSettings.GroomAsset = Groom;
    CardsSettings.GenerationFlags = 1; // 示例值
    CardsSettings.PipelineFlags = 3;   // Clumps + Geometry

    FGroomAdvancedGenerationSettings Adv;
    FGroomFilterSettings LOD;
    LOD.FilterName = TEXT("LOD0");
    LOD.NumClumps = 100;
    LOD.NumTriangles = 4000;
    LOD.NumTextures = 50;
    Adv.FilterSettings.Add(LOD);
    CardsSettings.GenerationSettings = NewObject<UHairCardGeneratorPluginSettings>();
    CardsSettings.GenerationSettings->AdvancedSetup = Adv;

    TArray<FGroomCardsSettings> SettingsArray = { CardsSettings };

    // 3. 创建并连接节点（简化：直接使用内部 Evaluate）
    FContext Context;
    FManagedArrayCollection Collection;

    // 创建节点实例（需确保模块已加载）
    FGenerateCardsClumpsNode ClumpsNode(FNodeParameters());
    ClumpsNode.SetInput("Collection", Collection);
    ClumpsNode.SetInput("CardsSettings", SettingsArray);
    ClumpsNode.Evaluate(Context, /* output references omitted for brevity */);

    FGenerateCardsGeometryNode GeoNode(FNodeParameters());
    GeoNode.SetInput("Collection", ClumpsNode.GetOutput("Collection"));
    GeoNode.SetInput("CardsSettings", SettingsArray);
    GeoNode.Evaluate(Context, /* output references omitted */);

    // 4. 使用终端节点导出静态网格
    FCardsAssetTerminalNode Terminal(FNodeParameters());
    Terminal.SetInput("Collection", GeoNode.GetOutput("Collection"));
    Terminal.SetInput("CardsSettings", SettingsArray);
    // 假设 Terminal 内部有逻辑创建并保存 UStaticMesh
    Terminal.Evaluate(Context, /* out */);

    UE_LOG(LogTemp, Log, TEXT("Hair cards generation demo completed."));
}
```

（实际终端节点需要预先设置资产保存路径，此处仅为概念演示。）

## 模块依赖

根据头文件包含的模块及常见数据流实践，该模块在 `Build.cs` 中依赖以下独特模块（省略标准 Core/Engine/Projects）：

| 模块 | 用途 |
|---|---|
| `DataflowCore` | 数据流图运行时框架 |
| `DataflowEngine` | 数据流引擎集成（资产、编辑器交互） |
| `GroomAsset` | 读取发丝曲线、簇组等毛发数据 |
| `Chaos` | 几何处理基础（向量、变换等） |
| `GeometryFramework` （推测） | 可能用于网格生成辅助 |
| `RHI` （推测） | 纹理创建相关 |

> **注意**：以上依赖为基于代码的合理推断，实际以 `HairCardGeneratorDataflow.Build.cs` 中的声明为准。通常插件自身模块的公开依赖会链式传递。

## 维护状态

### 近期更新

- 2025-11-18 1e8eb56 — Fix dataflow cards rendering crash when the generate LOD from previous is on
- 2025-10-03 b863d7a — Fix card texture rendering + add generation settings + automatic cardsgroups creation
- 2025-09-05 e6415d8 — Dataflow : fix performance issue when calling SetShadowEnabled on the dynamic mesh component
- 2025-09-04 68e03af — Geometry facade for grooms and cards + new rendering + use of curve selection
- 2025-09-04 5cb8a8b — [Backout] - CL45497446 - backout due to Main CIS issue

### 维护评价

该插件创建于 2025 年 9 月，至今（2025 年 12 月）仅 3 个月，但已有多达 5 次实质性提交，涵盖功能新增（自动卡片组创建、新渲染管线）、性能优化（修复 `SetShadowEnabled` 性能问题）和 bug 修复（卡片渲染崩溃、纹理渲染）。提交频率高，且当前没有废弃或弃用标记。**结论**：这是一个处于**活跃开发**阶段的新插件，推荐用于实验性项目；但由于仍在快速迭代，API 可能发生变动，生产环境使用时应锁定版本或进行充分测试。已知问题曾涉及渲染崩溃和性能，但已修复，目前无明确已知限制。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairCardGenerator)
- [官方文档]（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairCardGenerator/Source/HairCardGeneratorDataflow/Private/Tests)（推测路径，实际测试可能位于 `Engine/Tests/Plugins/HairCardGenerator`）