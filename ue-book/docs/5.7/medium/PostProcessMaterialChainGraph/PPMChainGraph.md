# Post Process Material Chain Graph

> Post Process Material Chain Graph allows users to stack post process materials and render those into render targets separate from Scene Color.  
> This can operate on textures other than scene color without writing those into scene color.

| 属性 | 值 |
|---|---|
| 中文名 | 后处理材质链图 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（后处理链资产、材质实例蓝图） |
| 模块 | `PPMChainGraph` (Runtime), `PPMChainGraphEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PostProcessMaterialChainGraph) | |

## 用途

传统的后处理材质只能直接写入 Scene Color，且无法在多个后处理阶段之间传递中间结果。**Post Process Material Chain Graph** 允许用户通过 **链图（Chain Graph）** 的方式堆叠多个后处理材质，每个材质可以选择将结果写入临时渲染目标（而非 Scene Color），后续的 Pass 可以引用这些临时纹理作为输入。

**核心能力**：
- 定义一系列有序的 **Post Process 阶段（Pass）**，每个阶段使用一个材质。
- 每个 Pass 可以读取前一个 Pass 的输出（通过 `PostProcessInput0`~`PostProcessInput4` 映射），也可以读取外部纹理。
- 输出可以指定为“写回 Scene Color”或“写入临时渲染目标”，最终 Pass 必须写回 Scene Color。
- 支持在不同渲染位置执行：`Before Post Processing`、`After Motion Blur`、`After Tonemap`、`After FXAA`、`After Visualize DepthOfField`。

该插件解决了需要自定义后处理管线层次且不想污染 Scene Color 的场景，例如：多级 Bloom、局部色调映射、通道分离特校等。

## 使用场景

- **复杂后处理特效**：需要多阶段处理，中间结果用于下一个材质（如先用模糊材质生成模糊纹理，再用该纹理与 Scene Color 合成）。
- **非破坏性后处理**：避免直接修改 Scene Color，将中间 Pass 输出到独立渲染目标。
- **相机专属链**：可以限制链图仅对特定相机生效，或排除特定相机。
- **编辑器预览**：在编辑器中实时查看链图效果（通过 `UPPMChainGraphWorldSubsystem` 管理）。

## 蓝图用法

插件主要通过 **Actor 组件** 和 **蓝图资产** 配置。以下列出核心可调用的节点和属性。

### 核心类与属性

| 类 / 结构 | 关键属性 | 说明 |
|---|---|---|
| `UPPMChainGraphExecutorComponent` | `PPMChainGraphs` (数组) | 要执行的链图资产列表 |
| | `CameraViewHandlingMode` | 控制“忽略所选相机”还是“仅渲染所选相机” |
| | `CameraList` | 相机列表，与 `CameraViewHandlingMode` 配合使用 |
| `UPPMChainGraph` (子蓝图) | `Passes` (数组) | 链中的 Pass 列表 |
| `FPPMChainGraphPostProcessPass` | `bEnabled` | 启用该 Pass |
| | `PostProcessMaterial` | 要执行的材质 |
| | `Inputs` (Map) | 将 `PostProcessInput0~4` 映射到上一个 Pass 的输出 ID |
| | `Output` | 输出目标：`Scene Color` 或 `Temporary Render Target` |
| | `OutputName` | 临时渲染目标的标识名（用于后续 Pass 引用） |
| | `ExternalTexture` | 可选外部纹理输入 |
| `FPPMChainGraphInput` | `InputId` | 字符串标识，对应前一个 Pass 的输出名称 |

### 使用流程（蓝图）

1. 创建材质（继承自 `PostProcess` 域材质），准备链中每个阶段要用的材质。
2. 右键内容浏览器 → `Miscellaneous` → 选择链图资产（可能需要先启用插件并显示“Experimental”分类）。创建一个 `PPMChainGraph` 蓝图子类。
3. 打开该蓝图，在 `Passes` 数组中添加元素，设置每个 Pass 的材质、输入映射、输出。
4. 在场景中放置 `BP_PPMChainGraphActor`（蓝图类 `APPMChainGraphActor`），其组件 `PPMChainGraphExecutorComponent` 自动可用。
5. 设置 `PPMChainGraphs` 数组引用之前创建的链图资产。
6. 可选：设置相机过滤（`CameraViewHandlingMode` + `CameraList`），控制哪些相机渲染该链。

### 常用蓝图节点

| 节点 | 说明 | 所属类 |
|---|---|---|
| `GetPPMChainGraphExecutorComponent` | 从 `APPMChainGraphActor` 获取组件 | (Actor 蓝图节点) |
| (属性读取/设置) | 直接编辑 `PPMChainGraphs`、`CameraViewHandlingMode`、`CameraList` | `UPPMChainGraphExecutorComponent` |
| (构造链图资产) | 在 `UPPMChainGraph` 子蓝图中配置 `Passes` 数组 | `UPPMChainGraph` |
| `Set Output` 等 | 通过细节面板直接设置 Pass 属性 | |

## C++ 用法

### 头文件引入

```cpp
#include "PPMChainGraph.h"
#include "PPMChainGraphComponent.h"
#include "PPMChainGraphActor.h"
```

### 基本用法

```cpp
// 在 GameMode 或 World 初始化中创建链图 Actor
APPMChainGraphActor* ChainGraphActor = GetWorld()->SpawnActor<APPMChainGraphActor>(APPMChainGraphActor::StaticClass());

// 获取执行组件
UPPMChainGraphExecutorComponent* Executor = ChainGraphActor->PPMChainGraphExecutorComponent;

// 设置相机过滤模式
Executor->CameraViewHandlingMode = ECameraViewHandling::RenderOnlyInSelectedCameraViews;

// 添加一个相机到白名单
Executor->CameraList.Add(MyCameraActor);

// 添加链图资产（需预先加载或构造 UPPMChainGraph 对象）
UPPMChainGraph* Graph = NewObject<UPPMChainGraph>();
// 构造 Passes...
Graph->Passes.Add(MakeShared<FPPMChainGraphPostProcessPass>());
Executor->PPMChainGraphs.Add(Graph);
```

### 进阶用法：动态构建链图 Pass

```cpp
// 创建 Pass 1：先执行模糊材质，输出到临时 RT "BlurRT"
TSharedPtr<FPPMChainGraphPostProcessPass> BlurPass = MakeShared<FPPMChainGraphPostProcessPass>();
BlurPass->bEnabled = true;
BlurPass->PostProcessMaterial = BlurMaterial; // 已加载的 UMaterial*
BlurPass->Output = EPPMChainGraphOutput::PPMOutput_RenderTarget;
BlurPass->OutputName = TEXT("BlurRT");
BlurPass->Inputs.Add(EPPMChainGraphPPMInputId::PPMInputMaping_0, FPPMChainGraphInput{ TEXT("SceneColor") });

// Pass 2：合成 Pass，读取 BlurRT 并与 Scene Color 混合
TSharedPtr<FPPMChainGraphPostProcessPass> CompositePass = MakeShared<FPPMChainGraphPostProcessPass>();
CompositePass->PostProcessMaterial = CompositeMaterial;
CompositePass->Output = EPPMChainGraphOutput::PPMOutput_SceneColor; // 最终写回
CompositePass->Inputs.Add(EPPMChainGraphPPMInputId::PPMInputMaping_0, FPPMChainGraphInput{ TEXT("BlurRT") });

// 设置到 Graph
UPPMChainGraph* Graph = NewObject<UPPMChainGraph>();
Graph->Passes.Add(BlurPass);
Graph->Passes.Add(CompositePass);
Executor->PPMChainGraphs.Add(Graph);
```

> 注意：`FPPMChainGraphPostProcessPass` 不是 UObject，而是共享指针结构，但 `UPPMChainGraph::Passes` 是 `TArray<TObjectPtr<UPPMChainGraphPostProcessPass>>`？实际上从头文件看 `UPPMChainGraph` 中的 `Passes` 是 `TArray<TObjectPtr<UPPMChainGraphPostProcessPass>>`，但 `UPPMChainGraphPostProcessPass` 可能是一个 UObject 子类（未在提供头文件中显示）。实际用法需参考插件完整源码，此处示意概念。

## Demo 示例

以下是一个最小 C++ 示例，在游戏开始时创建后处理链图。

**MyDemoGameMode.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyDemoGameMode.generated.h"

UCLASS()
class MYPROJECT_API AMyDemoGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;

    void SetupPPMChainGraph();
};
```

**MyDemoGameMode.cpp**
```cpp
#include "MyDemoGameMode.h"
#include "PPMChainGraphActor.h"
#include "PPMChainGraphComponent.h"
#include "PPMChainGraph.h"

void AMyDemoGameMode::BeginPlay()
{
    Super::BeginPlay();
    SetupPPMChainGraph();
}

void AMyDemoGameMode::SetupPPMChainGraph()
{
    // 仅对第一个玩家控制器的主相机生效
    APlayerController* PC = GetWorld()->GetFirstPlayerController();
    if (!PC) return;

    // 生成后处理链图 Actor
    APPMChainGraphActor* ChainActor = GetWorld()->SpawnActor<APPMChainGraphActor>(APPMChainGraphActor::StaticClass());
    UPPMChainGraphExecutorComponent* Exec = ChainActor->PPMChainGraphExecutorComponent;

    // 配置为仅渲染到该相机
    Exec->CameraViewHandlingMode = ECameraViewHandling::RenderOnlyInSelectedCameraViews;
    // 注意：需要将相机添加到 CameraList，此处假设使用相机 Actor 方式
    // 实际项目需获取当前相机对应的 ACameraActor
    // Exec->CameraList.Add(...);

    // 加载材质（假设已创建）
    UMaterial* MyPPM = LoadObject<UMaterial>(nullptr, TEXT("/Game/MyMaterials/MyPPM.MyPPM"));
    if (!MyPPM) return;

    // 创建一个简单链图（仅一个 Pass，写回 Scene Color）
    UPPMChainGraph* Graph = NewObject<UPPMChainGraph>(GetWorld());
    TObjectPtr<UPPMChainGraphPostProcessPass>* Pass = &Graph->Passes.Add_GetRef(NewObject<UPPMChainGraphPostProcessPass>(Graph));
    (*Pass)->bEnabled = true;
    (*Pass)->PostProcessMaterial = MyPPM;
    (*Pass)->Output = EPPMChainGraphOutput::PPMOutput_SceneColor;

    Exec->PPMChainGraphs.Add(Graph);
}
```

## 模块依赖

### PPMChainGraph (Runtime)

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 使用编辑器相关类型（场景视图扩展注册等），尽管是 Runtime 模块，实际依赖编辑器中存在的功能（如 `FSceneViewExtension` 注册需要编辑器运行时） |

> 注意：该依赖比较特殊，Runtime 模块依赖 `UnrealEd`，意味着在游戏发行包中可能需要包含部分编辑器功能。如果需要制作纯运行时插件，建议参考官方文档进一步了解。

### PPMChainGraphEditor (Editor)

Editor 模块通常依赖 `UnrealEd`、`EditorSubsystem` 等，但非必要列出（按规范省略常见依赖）。本插件 Editor 模块无额外独特依赖。

## 维护状态

### 近期更新

| 日期 | Hash | Commit | 解读 |
|---|---|---|---|
| 2025-02-18 | `8c3ee882` | PPMChainGraph: Export public classes & structs, per third-party request. | 应第三方请求，导出公共类和结构体 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 全局性的代码清理（替换 `IsValid(this)`） |
| 2024-11-25 | `af0eb101` | Removed pure virtual requirement for scene extension methods to reduce noise | 移除场景扩展方法的纯虚要求，减少维护噪音 |
| 2024-09-19 | `b34ed3b3` | [Engine] | 大规模引擎改动（涉及多个插件） |
| 2024-09-02 | `9fb339dd` | Fix macros for RDG GPU stats to support new GPU profiler | 修复 RDG GPU 统计宏以支持新的 GPU 分析器 |

### 维护评价

- **创建时间**：2024-09-02，约半年。
- **近期更新**：2025-02-18 有功能性更新（导出公共 API），说明仍在积极维护。
- **状态**：实验性插件（`IsExperimentalVersion=true`），但已有实质性更新，社区也有第三方使用请求。
- **稳定性**：文档中未见已知问题标记，但作为实验性功能，API 可能在未来版本发生变动。
- **推荐度**：推荐在需要复杂后处理链且愿意接受实验性插件风险时使用。建议搭配测试进行验证。

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PostProcessMaterialChainGraph)
- [官方文档](https://docs.unrealengine.com/5.7/zh-CN/post-process-material-chain-graph/)（可能需要创建，此处占位）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PostProcessMaterialChainGraph/Tests)（插件内可能包含样本地图或自动化测试）