# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源、编辑器资产） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

本插件为 Unreal Engine 提供了完整的 **Pixar USD (Universal Scene Description)** 工作流支持，远不止于简单的文件导入。它解决的核心问题是：**如何在游戏引擎中非破坏性地引用、编辑和协作由数字内容创建（DCC）工具（如 Maya, Houdini）生成的复杂 USD 场景、资产和动画**。

通过“USD Stage”作为场景参考层，开发者可以在不复制原始资产数据的情况下，在 UE 中进行布局、灯光和镜头设置，并将改动保存回 USD 格式或烘焙为引擎原生资产。这实现了与影视/VFX 领域的标准化管线无缝集成。

## 使用场景

- **在 UE 中引用完整的 USD 场景进行预览和布局**：艺术家从 Maya 导出一个包含多个角色、道具的 USD 场景文件（.usd/.usda/.usdc），设计师在 UE 的关卡编辑器中将其作为“USD Stage Actor”打开，进行虚拟拍摄或游戏关卡布局，无需导入所有资产。
- **将 USD 资产转换并烘焙为 UE 原生资产**：对于需要深度引擎集成（如用于游戏逻辑）的部分，可以使用 `USDStageImporter` 将 USD 资产（网格、材质、动画）一次性烘焙为 UE 的 Static Mesh, Skeletal Mesh, Animation Sequence 等。
- **利用 Geometry Cache 播放复杂的 USD 动画或模拟**：对于复杂的刚体或流体动画缓存，`GeometryCacheUSD` 模块允许直接将 USD 的动画数据作为 Geometry Cache 资产在引擎中回放。
- **在 UE 中创建和编辑 USD 数据并导出**：使用 `USDExporter` 模块，可以将 UE 中的内容（如关卡布局、静态网格）导出为 USD 格式，用于在其他 DCC 或渲染器中进一步加工。
- **为 USD 资产设置并应用独立的控制 Rig**：最新更新支持将蓝图无关的 Control Rig 应用于 USD 骨骼动画，实现更灵活的动画重定向和编辑。

## 蓝图用法

### 核心节点 (USD Stage 交互)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenStage` | 从文件路径打开一个 USD Stage 资产 | `UUSDStageAsset` |
| `ImportUSDAsset` | 将 USD Stage 中的资产烘焙并导入为 UE 原生资产 | `UUSDStageImporter` |
| `CreateStageActor` | 在关卡中创建一个 USD Stage Actor 引用指定的 USD 文件 | `AUSDStageActor` |
| `ExportToUSD` | 将 UE 资产（如关卡、网格）导出为 USD 文件 | `UUSDExporter` |
| `SetLayerOffset` | 设置 USD Stage 中某一层的变换偏移（平移、旋转、缩放） | `AUSDStageActor` |

### 使用示例（蓝图描述）
1.  **引用场景**: 从内容浏览器拖拽一个 `.usd` 文件到关卡视口，自动生成一个 `AUSDStageActor`。
2.  **烘焙资产**: 右键点击 `USDStageActor` -> “Import to Content Browser”，在对话框中选择需要导入的资产类型（网格、材质、动画等），完成一次性烘焙。
3.  **蓝图控制**: 在蓝图中，通过 `AUSDStageActor` 的节点动态修改 Stage 的根变换、设置可见性、或者调用 `SetLayerOffset` 来动态调整某个图层在世界中的位置。
4.  **导出**: 使用 `UUSDExporter::ExportToUSD` 节点，可以将当前关卡的 Actor 导出为一个新的 USD 文件。

## C++ 用法

### 头文件引入
```cpp
#include “USDStage.h” // 核心Stage操作
#include “USDExporter.h” // 导出功能
#include “USDStageImporter.h” // 烘焙导入功能
```

### 基本用法
```cpp
// 加载一个 USD Stage 资产并查询其根层信息
// 来自：USDStage/Private/USDStageAsset.cpp 相关测试用例
FString StageFilePath = TEXT(“/Game/MyScene.usd”);
UUSDStageAsset* StageAsset = LoadObject<UUSDStageAsset>(nullptr, *StageFilePath);
if (StageAsset)
{
    // 获取 Stage 的根 Prims
    UsdStageRefPtr UsdStage = StageAsset->GetUsdStage();
    if (UsdStage)
    {
        UsdPrim RootPrim = UsdStage->GetDefaultPrim();
        UE_LOG(LogTemp, Log, TEXT(“USD Stage Root Prim: %s”), *RootPrim.GetPath().GetString());
    }
}
```

### 进阶用法
```cpp
// 组合使用：将USD Stage中的特定Prim烘焙为UStaticMesh
// 来自：USDStageImporter 和 USDSchemas 模块的逻辑
FString PrimPath = TEXT(“/MyModel/Ground”);
FString PackagePath = TEXT(“/Game/Imported/Ground”);

// 配置烘焙选项
FUSDImportContext ImportContext;
ImportContext.Purpose = EUsdPurpose::Default;
ImportContext.bImportGeometry = true;
ImportContext.MaterialSearchLocation = EMaterialSearchLocation::UnderRoot;

// 执行烘焙导入
UUSDStageImporter* Importer = NewObject<UUSDStageImporter>();
UStaticMesh* ImportedMesh = Importer->ImportStaticMesh(StageAsset, PrimPath, PackagePath, ImportContext);
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何在C++中加载USD Stage并创建其Actor：

```cpp
// USDStageExample.h
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “USDStageExample.generated.h”

UCLASS()
class YOURPROJECT_API AUSDStageExample : public AActor
{
    GENERATED_BODY()

public:
    AUSDStageExample();

    // 在编辑器中设置USD文件路径
    UPROPERTY(EditAnywhere, Category = “USD”)
    FString USDFilePath;

    // 生成的USD Stage Actor引用
    UPROPERTY(VisibleAnywhere, Category = “USD”)
    AUSDStageActor* StageActor;

    // 在构造函数或BeginPlay中创建Stage Actor
    virtual void BeginPlay() override;
};
```

```cpp
// USDStageExample.cpp
#include “USDStageExample.h”
#include “USDStageActor.h”

AUSDStageExample::AUSDStageExample()
{
    PrimaryActorTick.bCanEverTick = false;
    USDFilePath = TEXT(“/Game/MyScene.usd”);
}

void AUSDStageExample::BeginPlay()
{
    Super::BeginPlay();

    if (!USDFilePath.IsEmpty() && GetWorld())
    {
        // 使用引擎服务创建USD Stage Actor
        FActorSpawnParameters SpawnParams;
        SpawnParams.Owner = this;
        SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

        StageActor = GetWorld()->SpawnActor<AUSDStageActor>(AUSDStageActor::StaticClass(), GetActorTransform(), SpawnParams);
        if (StageActor)
        {
            // 打开指定的USD Stage
            StageActor->SetUSDPath(USDFilePath);
        }
    }
}
```

## 模块依赖

该插件依赖 OpenUSD 库以及大量 UE 内部模块。使用此插件时，你的 `Build.cs` 文件需要添加以下关键依赖：

| 模块 | 用途 |
|---|---|
| `USDClasses` | 提供 USD 与 UE 类型系统之间的转换核心类 |
| `USDExporter` | 提供将 UE 内容导出为 USD 的功能 |
| `USDStage` | 提供 USD Stage 的加载、管理、编辑和渲染核心逻辑 |
| `USDStageImporter` | 提供将 USD Stage 内容烘焙为 UE 原生资产的功能 |
| `USDSchemas` | 定义和解析 USD 的自定义 Schema（如 UnrealStage, UnrealActor），实现 USD 与 UE 特性映射 |
| `USDGeometryCache` | 提供对 USD 动画缓存数据的支持 |
| `USDStageEditor` | 提供编辑器 UI 和操作，用于在编辑器中交互 USD Stage |
| `USDStageEditorViewModels` | 为 USDStageEditor 的 UI 提供数据视图模型（MVVM模式） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 为 USD 资产添加对蓝图无关的控制 Rig 的支持。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | 针对 USD 26.03 更新导致动画查询在 LOD 变化时内部引用失效的问题提供变通方案。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32 位/64 位格式说明符与参数位宽不匹配的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 支持烘焙曝光动画轨道的所有帧。 |

### 维护评价
该插件创建于2018年，最初为实验性功能。从近期提交记录看（2026年4月-5月），它仍在被**积极维护和开发**，新增了对 Control Rig 的集成，并持续修复兼容性问题和底层 Bug。作为 UE 与影视工业流程对接的关键桥梁，其功能在不断深化。虽然状态标记为“实验性”（`IsBetaVersion=true`），但考虑到 Epic Games 在 Houdini、Maya 等 DCC 工具集成上的投入，该插件是可靠且推荐在专业管线中使用的。主要限制是其默认不启用（`EnabledByDefault=false`），需要用户手动在插件设置中开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)