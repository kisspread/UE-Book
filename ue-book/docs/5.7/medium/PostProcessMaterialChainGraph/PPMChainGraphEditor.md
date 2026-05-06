# Post Process Material Chain Graph

> Post Process Material Chain Graph allows users to stack post process materials and render those into render targets separate from Scene Color.  
> This can operate on textures other than scene color without writing those into scene color.

| 属性 | 值 |
|---|---|
| 中文名 | 后处理材质链图 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PPMChainGraph` (Runtime), `PPMChainGraphEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PostProcessMaterialChainGraph) | |

## 用途

在默认管线中，后处理材质只能作用于 Scene Color，且多个后处理材质无法独立输出到不同渲染目标。Post Process Material Chain Graph 允许用户定义一条**材质链**，每个节点（材质）可以输出到独立的 Render Target，并且可以指定输入来自之前的输出或任意纹理（如场景深度、法线等）。最终用户可以灵活组合后处理效果，而不污染 Scene Color，适用于复杂的后处理叠加、调试可视化或自定义渲染管线。

## 使用场景

- 你需要在一帧内应用多个后处理材质（如模糊→描边→色调映射），每个材质使用不同纹理作为输入，且不想写入 Scene Color。
- 你想将后处理中间结果（例如深度、法线）输出到不同的 Render Target 供后续使用（如屏幕空间反射、自定义体积光）。
- 你要构建一个可配置的后处理链，在编辑器中可视化调整每个材质节点的输入/输出，并实时查看结果。

## 蓝图用法

该插件主要提供资产类型 `UPPMChainGraph`（蓝图类）和 Actor `APPMChainGraphActor`。蓝图节点暂无公开的 BlueprintCallable 函数，但资产可以直接在蓝图中创建和配置。

- 在内容浏览器中右键 → 杂项 → 后处理材质链图（资产类型名称为 `PPMChainGraph`）。
- 打开资产编辑器，添加材质链节点，设置每个节点的输入输出。
- 将 `PPMChainGraph` 资产拖放到关卡中生成 `APPMChainGraphActor`，Actor 会自动在运行时空渲染并应用效果。

### 核心资产

| 资产类型 | 说明 |
|---|---|
| `UPPMChainGraph` | 存储材质链图配置（材质节点、输入/输出绑定） |

### 蓝图节点

无公开蓝点调用节点。如需动态创建或修改链图，请使用 C++。

## C++ 用法

### 头文件引入

```cpp
#include "PPMChainGraph.h"
#include "PPMChainGraphActor.h"
```

### 基本用法

以下示例演示如何通过代码创建一个材质链图资产并设置节点。

```cpp
// 创建 UPPMChainGraph 对象
UPPMChainGraph* ChainGraph = NewObject<UPPMChainGraph>(GetTransientPackage(), NAME_None, RF_Public | RF_Standalone);

// 添加一个材质节点（假设有材质 MI_Blur）
UMaterialInterface* BlurMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/MI_Blur.MI_Blur"));
ChainGraph->AddNode(BlurMaterial, TEXT("Blur"));

// 设置输入纹理（例如使用场景深度）
ChainGraph->SetNodeInput(0, TEXT("Depth"), EInputType::SceneDepth);

// 标记资产需要保存
ChainGraph->MarkPackageDirty();
```

### 进阶用法

结合 Actor 在运行时部署链图：

```cpp
// 在世界中生成 Actor
APPMChainGraphActor* GraphActor = World->SpawnActor<APPMChainGraphActor>();

// 指定要使用的链图资产
GraphActor->SetChainGraph(MyChainGraphAsset);

// 启用（Actor 会在 Tick 期间渲染）
GraphActor->SetActive(true);
```

> 注：实际 API 名称可能因版本略有差异，请参考引擎头文件 `PPMChainGraph.h` 和 `PPMChainGraphActor.h`。

## Demo 示例

以下是一个最小可编译的测试，模拟编辑器工厂创建链图并生成 Actor。

```cpp
// MyTest.cpp
#include "PPMChainGraph.h"
#include "PPMChainGraphActor.h"
#include "Engine/World.h"
#include "Engine/Engine.h"

void SpawnChainGraphDemo()
{
    UWorld* World = GEngine->GetWorldContexts()[0].World();
    if (!World) return;

    // 创建链图资产
    UPPMChainGraph* ChainGraph = NewObject<UPPMChainGraph>(
        GetTransientPackage(),
        TEXT("DemoChainGraph"),
        RF_Public | RF_Standalone
    );

    // 添加一个后处理材质（需确保该材质存在）
    UMaterialInterface* PostMat = LoadObject<UMaterialInterface>(
        nullptr,
        TEXT("/Engine/EngineMaterials/DefaultPostProcessMaterial.DefaultPostProcessMaterial")
    );
    if (PostMat)
    {
        ChainGraph->AddNode(PostMat, TEXT("DefaultPP"));
    }

    // 生成 Actor 并关联
    APPMChainGraphActor* Actor = World->SpawnActor<APPMChainGraphActor>();
    if (Actor)
    {
        Actor->SetChainGraph(ChainGraph);
        Actor->SetActive(true);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PPMChainGraph` | 运行时核心：定义资产、Actor、渲染逻辑 |
| `PPMChainGraphEditor` | 编辑器支持：资产定义、工厂、自定义 UI |

使用此插件时，你的模块需要依赖：

- 运行时：`PPMChainGraph`（自动包含其内部依赖 `UnrealEd`，后者为跨模块引用，无需额外操作）
- 编辑器：`PPMChainGraphEditor`（若需编辑器扩展，则添加此依赖）

> 注意：`PPMChainGraph` 运行时模块依赖了 `UnrealEd`（用于某些编辑器功能），这是不常见的做法，使用时注意链接配置。

## 维护状态

### 近期更新

- 2025-02-18 `8c3ee882` PPMChainGraph: Export public classes & structs, per third-party request.
- 2025-02-13 `ec3fb596` Replaced `IsValid(this)` under the rest of Engine/.
- 2024-11-25 `af0eb101` Removed pure virtual requirement for scene extension methods...
- 2024-09-19 `b34ed3b3` [Engine] (大规模合并更新)
- 2024-09-02 `9fb339dd` Fix macros for RDG GPU stats...

### 维护评价

该插件创建于 2024 年 9 月，至今约 1 年，仍处于实验阶段。最近 6 个月内有功能更新（导出公共类），表明团队正在将其成熟化。但仍有较多未公开的细节，且依赖 `UnrealEd` 的运行时模块可能带来风险。推荐在项目中谨慎使用，并及时关注后续更新。如果追求稳定性，可等其脱离实验期。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PostProcessMaterialChainGraph)
- [官方文档](https://docs.unrealengine.com/5.7/zh-CN/PostProcessMaterialChainGraph)（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/PostProcessMaterialChainGraph/Tests/)（可能为空）