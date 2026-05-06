# ChaosEditor

> Destruction Tools

| 属性 | 值 |
|---|---|
| 中文名 | 破碎编辑器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `FractureEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-09 |
| 年龄标签 | 🆕（约0年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosEditor) | |

## 用途

**ChaosEditor** 插件为 Unreal Engine 提供了 **Fracture Editor Mode**（破碎编辑器模式），这是一个专门用于处理 **Geometry Collection**（几何体集合）破坏效果编辑的编辑器模式。它解决的核心问题是：在游戏或电影中高效地创建和编辑可破坏的物体（如墙壁、建筑、碎片等）。

具体功能包括：

- **切割工具**：通过平面、径向、簇Voronoi、砖块、网格等多种方式对几何体进行破碎。
- **聚类操作**：自动或手动将碎片组合成簇，控制破坏时的层次结构。
- **选择与编辑**：支持在3D视口中选择单个或多个骨骼（bone），并进行合并、拆分、隐藏/显示、删除分支等操作。
- **凸包生成与重叠移除**：为物理模拟优化碰撞体，自动或手动管理凸包的生成与重叠处理。
- **邻近检测**：计算碎片间的邻近关系，用于连接图生成和破坏模拟。
- **材质管理**：编辑几何体集合的材质槽，并为内外表面分配不同材质。
- **转换工具**：将几何体集合转换为静态网格物体，或嵌入/提取几何体。
- **初始动态状态设置**：为选中的骨骼设置初始物理状态（运动学、静态等），控制破坏行为。
- **移除断裂/小几何体**：自动合并过小的碎片，优化性能。

该插件是 **Chaos Physics** 破坏系统的重要组成部分，让艺术家和设计师无需编程即可为关卡创建丰富的可破坏场景。

## 使用场景

- **破坏场景制作**：建造一座砖墙，使用 Fracture Mode 将墙体切割为数百块砖，并设置合适的连接强度，玩家攻击时墙体碎裂。
- **建筑倒塌动画**：预先破碎一个建筑几何体，调整每个碎块的初始动态状态，实现特定顺序的倒塌效果。
- **优化性能**：将复杂几何体破碎为合理数量的簇，减少物理模拟中的碰撞体数量。
- **环境交互**：制作可破坏的玻璃窗、木箱、岩石等，为游戏增加动态反馈。
- **电影级破坏**：在过场动画中，对几何体集合进行精细的破碎编辑，控制碎片飞散路径。

## 蓝图用法

该插件主要设计为编辑器工具，**没有公开蓝图中可调用的函数**。所有操作均通过 Fracture Editor Mode 的 UI 完成。但相关工具（如 `UFractureSelectionTools`）提供了静态 C++ 函数，可被蓝图或Python间接调用，但默认未暴露。

### 核心节点（无）

> 无蓝图可调用节点。

## C++ 用法

### 头文件引入

```cpp
#include "FractureEditorMode.h"
#include "FractureSelectionTools.h"
#include "FractureTool.h"
#include "FractureToolAutoCluster.h"
#include "FractureToolConvex.h"
#include "FractureToolProximity.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "GeometryCollection/GeometryCollectionObject.h"
```

### 基本用法

以下示例展示如何在 C++ 代码中激活 Fracture Editor Mode 并选中 Geometry Collection 中的骨骼。

```cpp
// 获取 Editor 模式管理器并激活 Fracture 模式
UAssetEditorSubsystem* AssetEditorSubsystem = GEditor->GetEditorSubsystem<UAssetEditorSubsystem>();
if (AssetEditorSubsystem)
{
    AssetEditorSubsystem->OpenEditorForAsset(MyGeometryCollectionActor); // 打开 Geometry Collection 编辑器
    // 注意：Fracture Mode 需要先通过 Editor Mode Manager 激活
    FEditorModeTools& ModeTools = GEditor->GetEditorModeManager();
    ModeTools.ActivateMode(UFractureEditorMode::EM_FractureEditorModeId);
}

// 选择一个 Geometry Collection 上的骨骼
UGeometryCollectionComponent* GComp = ...; // 从 Actor 获取
TArray<int32> BonesToSelect = {3, 5, 7};
FFractureSelectionTools::ToggleSelectedBones(GComp, BonesToSelect, true, true);
```

### 进阶用法

#### 使用 FractureTool 进行程序化破碎

```cpp
// 创建 FFractureToolContext 并准备切割
FFractureToolContext Context(MyGeometryCollectionComponent);
// 自动聚类设置
UFractureAutoClusterSettings* AutoClusterSettings = NewObject<UFractureAutoClusterSettings>();
AutoClusterSettings->ClusterSizeMethod = EClusterSizeMethod::ByNumber;
AutoClusterSettings->SiteCount = 20;

UFractureToolAutoCluster* AutoClusterTool = NewObject<UFractureToolAutoCluster>();
AutoClusterTool->Execute(TWeakPtr<FFractureEditorModeToolkit>(Toolkit)); // 需要有效的 Toolkit 引用
```

#### 程序化凸包生成

```cpp
// 调用凸包生成函数（需确保在 GameThread 运行）
UFractureConvexActions* ConvexActions = NewObject<UFractureConvexActions>();
ConvexActions->RegenerateConvexHulls(Context);  // 此函数在 FragileToolConvex.cpp 中定义
```

> 构造函数和 API 基于 `Source/FractureEditor/Private/FractureToolConvex.h` 中的声明。

## Demo 示例

以下是一个最小 C++ 示例，展示如何在插件加载时自动进入 Fracture Editor Mode 并选择骨骼。

### FractureDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FFractureDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### FractureDemo.cpp

```cpp
#include "FractureDemo.h"
#include "Editor/UnrealEdEngine.h"
#include "UnrealEdGlobals.h"
#include "EditorModeManager.h"
#include "FractureEditorMode.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "FractureSelectionTools.h"
#include "Engine/Selection.h"
#include "LevelEditorViewport.h"

IMPLEMENT_MODULE(FFractureDemoModule, FractureDemo);

void FFractureDemoModule::StartupModule()
{
    // 注册延迟回调，确保编辑器完全加载
    FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float DeltaTime)
    {
        if (GEditor && GEditor->GetEditorModeManager().GetActiveMode(UFractureEditorMode::EM_FractureEditorModeId) == nullptr)
        {
            // 激活 Fracture Mode
            GEditor->GetEditorModeManager().ActivateMode(UFractureEditorMode::EM_FractureEditorModeId);
        }

        // 选择当前选中的 Geometry Collection Actor 的骨骼
        USelection* SelectedActors = GEditor->GetSelectedActors();
        if (SelectedActors && SelectedActors->Num() == 1)
        {
            AActor* Actor = Cast<AActor>(SelectedActors->GetSelectedObject(0));
            if (Actor)
            {
                UGeometryCollectionComponent* GComp = Actor->FindComponentByClass<UGeometryCollectionComponent>();
                if (GComp)
                {
                    // 全选所有骨骼
                    TArray<int32> AllBones;
                    for (int32 Idx = 0; Idx < GComp->GetNumBones(); ++Idx)
                    {
                        AllBones.Add(Idx);
                    }
                    FFractureSelectionTools::ToggleSelectedBones(GComp, AllBones, true, true);
                }
            }
        }

        return false; // 只执行一次
    }));
}

void FFractureDemoModule::ShutdownModule()
{
}
```

### 说明

- 该模块在 `StartupModule` 中通过 ticker 延迟一帧激活 Fracture Mode。
- 然后获取当前选中的 Actor，找出其 `UGeometryCollectionComponent` 并选中所有骨骼。
- 实际使用中，应将此模块添加到编辑器插件的 Build.cs 中，并依赖 `FractureEditor` 模块。

## 模块依赖

要使用 `FractureEditor` 模块，你的模块需要在 `Build.cs` 的 `PublicDependencyModuleNames` 中添加以下模块（省略标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `FractureEditor` | 破碎编辑器核心模块（必须） |
| `PlanarCut` | 平面切割算法库 |
| `GeometryCollectionPlugin` | Geometry Collection 资产类型和运行时组件 |
| `MeshModelingToolsetExp` | 网格建模工具集（用于切割预览、噪声等） |
| `EditorScriptingUtilities` | 编辑器脚本实用工具（用于动态生成资产等） |
| `Fracture` | 底层破碎算法库（Voronoi、网格切割等） |

**注**：`GeometryCollectionPlugin` 和 `Fracture` 也是运行时模块，如果仅在编辑器中使用，也可仅依赖 `FractureEditor`，但需要确保这些插件已启用。

## 维护状态

### 近期更新

- 2025-09-23 `ae51cf3` — Fracture editor add a None option to showing selected element in a geometry collection
- 2025-08-06 `450261e` — Fracture editor : when creating a geometry collection , make sure we can clear the dataflow or physical material
- 2025-07-18 `462ec4e` — Fix warning V623: Consider inspecting the '?:' operator. A temporary object is being created and sub
- 2025-07-10 `9803c44` — Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files.
- 2025-06-09 `f202c11` — Expanded out fracture brick pattern bounds by a half-brick, to fix bricks not quite covering the intended area

### 维护评价

- **创建时间**：2025-06-09，至今约5个月。
- **更新频率**：最近4个月内已有5次提交，涉及功能改进（新选项）、Bug修复、代码质量优化，属于活跃维护。
- **内容评价**：功能更新贴合用户需求（如“None”显示选项、砖块图案边界修复），无废弃倾向。
- **推荐使用**：✅ 推荐使用。该插件是 UE5 Chaos 破坏系统的核心编辑器工具，即使标记为实验性，其稳定性已较高，且官方持续投入维护。对于任何需要可破坏物体的项目，都应启用此插件。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosEditor)
- [官方文档 - Geometry Collections](https://docs.unrealengine.com/5.7/en-US/geometry-collections-in-unreal-engine/)
- [Fracture Mode 文档（可能）](https://docs.unrealengine.com/5.7/en-US/fracture-mode-in-unreal-engine/)