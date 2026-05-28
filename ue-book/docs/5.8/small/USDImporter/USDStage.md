# USD Importer

> Adds support for importing the USD file format into Unreal Engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD资产） |
| 模块 | 多个模块（见详解） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

**USD Importer** 插件不仅仅是导入工具，更是 Unreal Engine 与 Pixar 的 Universal Scene Description (USD) 生态系统深度集成的**运行时**和**编辑器**核心组件。其主要解决以下问题：

1.  **USD 资产导入与序列化**：将 USD 文件（`.usd`, `.usda`, `.usdc`）解析并转换为 UE 的原生资产（Static Mesh, Skeletal Mesh, Material, Animation 等）。
2.  **运行时 USD 阶段管理**：通过 `AUsdStageActor` 在游戏世界中打开、加载、显示和交互式操作 USD 阶段，实现动态资产加载和场景合成。
3.  **双向数据同步与序列化动画**：将 USD 阶段的动画数据转换为 UE 的 Level Sequence，支持在 Sequencer 中编辑并可能同步回 USD。
4.  **编辑器内可视化与编辑**：为 USD 阶段提供专业的编辑器界面（USD Stage Editor），用于浏览 prim 层级、检查属性、控制导入设置和实时预览。
5.  **资产缓存与优化**：通过智能缓存机制（`UUsdAssetCache3`）避免重复生成相同资产，并支持 Nanite、材质合并等优化。

## 使用场景

-   **影视与虚拟制片**：将影视流程中的 USD 场景资产（模型、材质、灯光、动画）无损导入 UE 用于实时渲染和虚拟拍摄。
-   **跨DCC工具协作**：从 Maya, Houdini, Blender 等支持 USD 的 DCC 软件导出场景，在 UE 中进行最终合成和交互。
-   **动态资产流送**：在游戏或实时应用中，根据运行时需求动态加载 USD 资产的特定部分或 LOD。
-   **大规模场景合成**：使用 `AUsdStageActor` 组合多个 USD 文件，构建复杂的游戏或可视化场景。
-   **程序化内容生成**：通过 C++ 或蓝图动态创建和操控 USD 阶段，实现程序化场景生成。

## 蓝图用法

蓝图交互主要通过 `AUsdStageActor` 实现。以下按功能分组列出核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Root Layer` | 设置要打开的 USD 文件路径，是启动所有操作的第一步。 | `AUsdStageActor` |
| `Set Stage State` | 控制 USD 阶段的生命周期（关闭、打开、打开并加载资产）。 | `AUsdStageActor` |
| `Get Generated Component` | 根据 USD Prim 路径获取其在 UE 中生成的对应场景组件（如 StaticMeshComponent）。 | `AUsdStageActor` |
| `Get Generated Assets` | 根据 USD Prim 路径获取其生成的所有资产（如 UStaticMesh, UMaterialInterface）。 | `AUsdStageActor` |
| `Get Source Prim Path` | 反向查询：给定一个生成的 UE 对象，返回其对应的 USD Prim 路径。 | `AUsdStageActor` |
| `Set Time` / `Get Time` | 设置或获取 USD 阶段的当前评估时间，用于预览动画。 | `AUsdStageActor` |
| `Get Level Sequence` | 获取为当前 USD 阶段生成的主 Level Sequence 资产，可在 Sequencer 中打开编辑。 | `AUsdStageActor` |
| `Set Purposes To Load` | 按位掩码设置要加载的 Prim 的用途（如 Default, Proxy, Guide, Render）。 | `AUsdStageActor` |
| `Set Kinds To Collapse` | 按位掩码设置要折叠的 Prim 类型（如 Model, Group），以优化导入结构。 | `AUsdStageActor` |
| `Set Nanite Triangle Threshold` | 设置自动启用 Nanite 的三角形数量阈值。 | `AUsdStageActor` |

### 使用示例（蓝图描述）

1.  **基本导入与加载**：
    - 在关卡中放置一个 `AUsdStageActor`。
    - 在其 `Details` 面板中，设置 `Root Layer` 属性为你的 USD 文件路径。
    - 将 `Stage State` 从 `Closed` 改为 `Opened And Loaded`。此时，USD 文件中的资产将被转换并加载到关卡中。

2.  **动态查询生成的资产**：
    - 在蓝图中，使用 `Get Actor Of Class` 节点找到 `AUsdStageActor` 实例。
    - 调用 `Get Generated Assets` 节点，`Prim Path` 输入类似 `"/root/MyMesh"` 的字符串。
    - 返回的数组包含生成的 `UStaticMesh` 等对象，可对其进行操作（如应用新材质）。

3.  **控制动画播放**：
    - 通过 `Set Time` 节点，根据游戏逻辑（如角色位置）动态改变 USD 阶段的时间，以预览动画或变形效果。
    - 使用 `Get Level Sequence` 获取序列后，可以将其添加到 `Level Sequence Actor` 中以获得更复杂的 Sequencer 控制。

## C++ 用法

### 头文件引入

```cpp
#include "USDStageActor.h"          // 核心舞台Actor
#include "USDStageModule.h"         // 模块接口
#include "USDLevelSequenceHelper.h" // 序列辅助类
#include "USDPrimTwin.h"            // Prim与组件的映射关系
```

### 基本用法

来自 `USDStage` 模块的头文件，展示了如何访问和配置 `AUsdStageActor`。

```cpp
// USDStageActor.h 中的核心用法示例
// 假设在某个Actor或函数中已经获取了 AUsdStageActor* StageActor 指针

// 1. 设置根层并打开阶段
FString UsdFilePath = TEXT("/Game/Scenes/MyScene.usd");
StageActor->SetRootLayer(UsdFilePath);

// 2. 配置导入选项 (可以在蓝图中设置，也可在C++中动态设置)
StageActor->SetStageState(EUsdStageState::OpenedAndLoaded);
StageActor->SetPurposesToLoad(static_cast<int32>(EUsdPurpose::Default) | static_cast<int32>(EUsdPurpose::Render));
StageActor->SetNaniteTriangleThreshold(10000);
StageActor->SetKindsToCollapse(static_cast<int32>(EUsdDefaultKind::Model));

// 3. 查询生成的组件和资产
FString PrimPath = TEXT("/root/Characters/hero");
USceneComponent* GeneratedComp = StageActor->GetGeneratedComponent(PrimPath);
if (GeneratedComp)
{
    // 对组件进行操作
}

TArray<UObject*> GeneratedAssets = StageActor->GetGeneratedAssets(PrimPath);
for (UObject* Asset : GeneratedAssets)
{
    if (UStaticMesh* Mesh = Cast<UStaticMesh>(Asset))
    {
        // 操作网格体资产
    }
}

// 4. 控制动画
StageActor->SetTime(1.5f); // 设置到1.5秒
ULevelSequence* Seq = StageActor->GetLevelSequence();
```

### 进阶用法

结合 `USDLevelSequenceHelper` 和 `USDPrimTwin` 进行更底层的控制。

```cpp
// USDLevelSequenceHelper.h 和 USDPrimTwin.h 中的高级概念
// 通常用于自定义导入或扩展插件功能

// FUsdLevelSequenceHelper 管理着USD动画到LevelSequence的转换
// 在 AUsdStageActor 内部使用，通常不需要直接创建，但可以响应其事件
// 例如，监听骨骼动画烘焙事件：
FUsdLevelSequenceHelper& SeqHelper = StageActor->GetLevelSequenceHelper(); // 假设有访问器
SeqHelper.GetOnSkelAnimationBaked().AddLambda([](const FString& SkeletonPrimPath)
{
    UE_LOG(LogTemp, Log, TEXT("骨骼动画已烘焙: %s"), *SkeletonPrimPath);
});

// UUsdPrimTwin 代表了USD Prim到UE组件/资产的“双胞胎”映射
// 可以通过它遍历阶段Actor生成的组件树
UUsdPrimTwin* RootTwin = StageActor->GetRootPrimTwin(); // 假设有访问器
if (RootTwin)
{
    RootTwin->Iterate([](UUsdPrimTwin& Twin)
    {
        USceneComponent* Comp = Twin.GetSceneComponent();
        if (Comp)
        {
            // 找到与USD Prim对应的UE组件
            // Twin.PrimPath 包含USD路径
        }
    }, true); // true 表示递归遍历
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建一个 `AUsdStageActor` 并在 BeginPlay 时加载一个 USD 文件。

**USDStageActorDemo.h**
```cpp
// Fill out your copyright description in the Description page of your plugin.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "USDStageActorDemo.generated.h"

class AUsdStageActor;

UCLASS()
class YOURPROJECT_API AUSDStageActorDemo : public AActor
{
	GENERATED_BODY()
	
public:	
	AUSDStageActorDemo();

protected:
	virtual void BeginPlay() override;

public:	
	virtual void Tick(float DeltaTime) override;

private:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "USD", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<AUsdStageActor> USDStageActor;

	UPROPERTY(EditAnywhere, Category = "USD")
	FFilePath USDFileToLoad;
};
```

**USDStageActorDemo.cpp**
```cpp
#include "USDStageActorDemo.h"
#include "USDStageActor.h"
#include "Engine/World.h"

AUSDStageActorDemo::AUSDStageActorDemo()
{
	PrimaryActorTick.bCanEverTick = true;
	// 创建默认的USDStageActor子组件
	USDStageActor = CreateDefaultSubobject<AUsdStageActor>(TEXT("USDStageActor"));
}

void AUSDStageActorDemo::BeginPlay()
{
	Super::BeginPlay();

	if (USDStageActor && !USDFileToLoad.FilePath.IsEmpty())
	{
		// 设置USD文件路径
		USDStageActor->SetRootLayer(USDFileToLoad.FilePath);
		// 设置阶段状态为“打开并加载”，触发资产生成
		USDStageActor->SetStageState(EUsdStageState::OpenedAndLoaded);
		
		// 可选：等待加载完成
		// FPlatformProcess::Sleep(1.0f);
		
		// 查询第一个加载的Prim的组件（示例路径，需根据实际USD文件调整）
		USceneComponent* ExampleComp = USDStageActor->GetGeneratedComponent(TEXT("/root"));
		if (ExampleComp)
		{
			UE_LOG(LogTemp, Log, TEXT("USD Stage loaded. Root component found: %s"), *ExampleComp->GetName());
		}
	}
}

void AUSDStageActorDemo::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// 示例：动态改变USD阶段的时间以播放动画
	if (USDStageActor)
	{
		float NewTime = USDStageActor->GetTime() + DeltaTime;
		USDStageActor->SetTime(FMath::Fmod(NewTime, 10.0f)); // 假设动画总长为10秒，循环播放
	}
}
```

## 模块依赖

从 `USDStage` 模块的 `Build.cs` 分析，以下是该插件（尤其是核心 Stage 功能）独特的依赖：

| 模块 | 用途 |
|---|---|
| `UnrealUSDWrapper` | Epic 封装的底层 USD C++ 库 (pxr) 的接口层，是核心依赖。 |
| `USDClasses` | 提供 USD 相关的 UObject 和数据结构定义（如 `UUsdAssetCache3`, `FUsdPrimLinkCache`）。 |
| `USDSchemas` | 定义 USD Schema 到 UE 类型/资产的转换逻辑（例如，将 UsdGeomMesh 转换为 UStaticMesh）。 |
| `SequencerCore`, `MovieScene`, `LevelSequence` | 用于处理 USD 动画到 UE Level Sequence 的转换和编辑。 |
| `UniversalObjectLocator` | 提供 `FUsdPrimLocatorFragment` 等功能，用于在 Sequencer 等系统中定位 USD 生成的资产/组件。 |
| `AssetRegistry` | 用于注册和管理动态生成的 USD 资产。 |

**注意**：该插件还依赖标准的 UE 模块（如 Core, Engine, Slate 等），此处已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数产生的编译警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD: 新增支持分配独立于蓝图的 Control Rig。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | USD: 解决 UE 26.03 更新导致 AnimQuery 内部引用在 LOD 变化时失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式说明符与参数位数不匹配（32位格式符用于64位参数等）的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD: 烘焙曝光动画轨道的所有帧。 |

### 维护评价

-   **年龄与状态**：插件创建于 2018 年，已有约 8 年历史，但仍处于 **Beta (实验性)** 状态。
-   **活跃度**：**活跃维护中**。从近期提交记录看，在 2026 年 4-5 月间仍有持续的功能增强、兼容性修复和 Bug 修复。
-   **重要性与推荐**：作为 UE 与影视级 USD 工作流集成的核心，该插件**强烈推荐**给所有需要涉及 USD 资产的项目使用。其 Beta 状态可能意味着 API 或行为在未来版本中仍可能发生变更，但 Epic 持续投入维护表明其是受支持的关键功能。
-   **注意事项**：由于功能复杂且仍为 Beta，建议在项目初期进行充分测试，特别是涉及复杂的资产结构、动画和材质绑定时。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests) (位于插件内部的 USDTests 模块)
-   [官方文档]：暂无链接（.uplugin 中 DocsURL 为空）