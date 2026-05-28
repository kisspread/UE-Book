# MetaHuman Character Palette Editor

> MetaHuman Character Asset Creator and Editor.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 调色板编辑器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产） |
| 模块 | `MetaHumanCharacterPaletteEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter) | |

## 用途

此插件模块是 MetaHuman Creator 编辑器功能的核心组成部分，专门用于在 Unreal Editor 中创建、编辑和组合 MetaHuman 角色的外观资产。它解决的核心问题是提供一个用户友好的界面，让用户能够以非破坏性的方式，从一个包含各种角色部件（如面部、身体、服装、发型）的“调色板”（Palette）中进行选择、组合和自定义，从而生成独特的 MetaHuman 角色变体（Instance）。该模块提供了资产编辑器、预览视口、拖放操作、部件管理等功能，是连接底层资产数据与艺术家创作流程的关键桥梁。

## 使用场景

-   **自定义 MetaHuman 外观**：当你需要为项目创建多个外观不同的 MetaHuman 角色时，使用此编辑器从共享的部件库（Collection）中组合出独特的实例（Instance）。
-   **服装与发型搭配**：通过拖放操作，将不同的服装和发型资产分配给 MetaHuman 的特定插槽，实时预览搭配效果。
-   **管理角色变体**：当你有一个基础的 MetaHuman 角色，并希望批量生成其不同服装或发型的变体以用于人群或不同场景时。
-   **资产开发与测试**：对于 MetaHuman 内容创作者，此编辑器用于测试和迭代他们创建的新部件资产（如新服装）与基础角色骨架的兼容性和视觉效果。

## 蓝图用法

该模块主要提供编辑器工具和资产工厂类，其核心功能通过编辑器界面暴露。关键的蓝图/编辑器可暴露节点（通过接口或资产操作）如下：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InitializeMetaHumanCharacterEditorActor` | 初始化用于编辑器预览的 Actor，设置面部/身体网格、LOD 映射等。 | `IMetaHumanCharacterEditorActorInterface` |
| `SetForcedLOD` | 强制预览 Actor 显示指定的 LOD 级别。 | `IMetaHumanCharacterEditorActorInterface` |
| `SetActorDrivingAnimationMode` | 设置预览 Actor 的动画驱动模式（来自重定向源或手动）。 | `IMetaHumanCharacterEditorActorInterface` |
| `SetHairVisibilityState` | 控制预览 Actor 上毛发组件的显示状态（显示/隐藏）。 | `IMetaHumanCharacterEditorActorInterface` |
| `SetClothingVisibilityState` | 控制服装组件的显示状态，支持覆盖材质显示。 | `IMetaHumanCharacterEditorActorInterface` |
| `WriteItemToCollection` | 将修改后的调色板项写回 Collection 资产。 | `SCollectionItemTileView` |
| `FactoryCreateNew` | 创建新的 MetaHuman Collection 或 Wardrobe Item 资产。 | `UMetaHumanCollectionFactory`, `UMetaHumanWardrobeItemFactory` |

### 使用示例（蓝图描述）

1.  **创建资产**：在内容浏览器右键，选择“MetaHuman”分类下的“Collection”或“Wardrobe Item”来创建新的资产。这会调用 `UMetaHumanCollectionFactory` 或 `UMetaHumanWardrobeItemFactory`。
2.  **编辑资产**：双击一个 Collection 或 Instance 资产，会打开 `FMetaHumanCharacterPaletteEditorToolkit` 驱动的资产编辑器。界面包含一个部件列表视图（`SCollectionItemTileView`）、一个属性细节面板和一个3D预览视口。
3.  **组合部件**：在部件列表中，通过勾选复选框或直接拖放资产到预览视口的指定插槽区域，来为 MetaHuman 的不同部分（Slot）分配资产。编辑器内部会调用 `WriteItemToCollection` 等方法来更新数据。
4.  **预览与调整**：在预览视口中，可以旋转查看角色。通过细节面板调整实例参数（如颜色、材质覆盖），预览会实时更新。可以使用 `SetForcedLOD` 来检查不同细节层次下的表现。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCharacterPaletteEditorModule.h"
#include "MetaHumanCharacterEditorActorInterface.h"
#include "MetaHumanCharacterPaletteUnpackHelpers.h"
```

### 基本用法

以下代码演示了如何以编程方式触发一次集合构建操作，这是编辑器中“应用”或“重建”按钮背后的逻辑。

```cpp
// 来源: Private/Tests/MetaHumanCharacterTestEditorPipeline.h 及一般编辑器逻辑
#include "MetaHumanCharacterTestEditorPipeline.h"
#include "MetaHumanCollection.h"

void BuildMyMetaHumanCollection()
{
    // 假设已经有一个 UMetaHumanCharacterTestEditorPipeline 实例
    UMetaHumanCharacterTestEditorPipeline* EditorPipeline = GetMyTestEditorPipeline();
    if (!EditorPipeline) return;

    // 准备构建参数
    FBuildCollectionParams BuildParams;
    BuildParams.Collection = GetMyMetaHumanCollection(); // 获取要构建的Collection资产
    // ... 设置其他参数，如目标文件夹等

    // 定义完成回调
    FOnBuildComplete OnBuildComplete;
    OnBuildComplete.BindLambda([](bool bSucceeded)
    {
        if (bSucceeded)
        {
            UE_LOG(LogTemp, Log, TEXT("MetaHuman Collection built successfully."));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to build MetaHuman Collection."));
        }
    });

    // 执行构建
    EditorPipeline->BuildCollection(BuildParams, OnBuildComplete);
}
```

### 进阶用法

利用 `IMetaHumanCharacterEditorActorInterface` 在自定义的编辑器工具或自动化测试中控制预览 Actor。

```cpp
// 来源: Public/MetaHumanCharacterEditorActorInterface.h 及使用示例
#include "MetaHumanCharacterEditorActorInterface.h"

void CustomizePreviewActor(AActor* PreviewActor, UMetaHumanCharacter* Character)
{
    if (!PreviewActor || !Character) return;

    // 获取接口指针
    IMetaHumanCharacterEditorActorInterface* ActorInterface = Cast<IMetaHumanCharacterEditorActorInterface>(PreviewActor);
    if (!ActorInterface) return;

    // 初始化预览 Actor (通常在Spawn后立即调用一次)
    // 注意：实际参数 (InCharacterInstance, InFaceMesh, InBodyMesh等) 需要从有效的上下文中获取
    // ActorInterface->InitializeMetaHumanCharacterEditorActor(...);

    // 强制显示 LOD 2
    ActorInterface->SetForcedLOD(2);

    // 隐藏所有服装
    ActorInterface->SetClothingVisibilityState(EMetaHumanClothingVisibilityState::Hidden);

    // 启用法线显示以进行调试
    ActorInterface->SetShowNormalsOnFace(true);
}
```

## Demo 示例

一个最小化的测试用例，演示如何设置一个用于自动化测试的简单 Pipeline 结构。

```cpp
// MetaHumanCharacterTestSetup.h
#pragma once

#include "CoreMinimal.h"
#include "Tests/MetaHumanCharacterTestPipeline.h"

// 一个简化的设置类，用于演示
class FMetaHumanTestSetup
{
public:
    static UMetaHumanCharacterTestPipeline* CreateTestPipeline(UObject* Outer)
    {
        UMetaHumanCharacterTestPipeline* TestPipeline = NewObject<UMetaHumanCharacterTestPipeline>(Outer);

        // 创建并设置运行时规范
        UMetaHumanCharacterPipelineSpecification* Spec = NewObject<UMetaHumanCharacterPipelineSpecification>(TestPipeline);
        // ... 配置 Spec 的插槽、演员类等
        TestPipeline->SetSpecification(Spec);

        // 设置对应的编辑器 Pipeline
        TestPipeline->SetDefaultEditorPipeline();

        return TestPipeline;
    }
};
```

```cpp
// MetaHumanCharacterTestSetup.cpp
#include "MetaHumanCharacterTestSetup.h"

// 实现已在头文件中内联，此处仅为完整性展示
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCharacter` | 提供核心的 `UMetaHumanCharacter`、`UMetaHumanInstance` 等资产类定义和基础逻辑。 |
| `MetaHumanCharacterPalette` | 提供 `UMetaHumanCollection`、`FMetaHumanCharacterPaletteItem` 等调色板和部件数据结构。 |
| `MetaHumanDefaultEditorPipeline` | 提供默认的 MetaHuman 编辑器管道实现，本模块的编辑器功能可能基于或扩展它。 |
| `MetaHumanDefaultPipeline` | 提供默认的 MetaHuman 运行时管道实现，用于构建和装配逻辑。 |
| `ToolMenus` | 用于扩展 Unreal Editor 的菜单和工具栏，添加编辑器命令（如“应用”、“重建”按钮）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `95d906ba` | [UEMHC] Checking for Asset Registry filter validity before using it | 修复资产注册表过滤器有效性检查，提升编辑器稳定性。 |
| 2026-05-26 | `efb27122` | [UEMHC] Duplicate face/body DNA when duplicating archetype skel meshes | 修复复制原型骨骼网格时面部/身体DNA数据丢失的问题。 |
| 2026-05-26 | `909bc538` | [MHC] Use safer weak pointers for captured objects in MHC preview delegates | 使用更安全的弱指针管理预览代理中的对象，避免野指针。 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | MetaHuman 底层技术栈（Titan）更新至 v9.0.7。 |

### 维护评价

该模块创建于 **2025年3月**，年龄约 **1年**，属于较新的组件。从最近的提交记录看，维护**非常活跃**（最近3天内有多次提交），主要集中在修复 Bug、提升稳定性和集成底层技术更新。由于其仍标记为 `IsBetaVersion=true`，表明它仍处于积极开发和功能完善阶段，可能尚未达到完全稳定的状态。

**推荐使用**：如果你的项目需要深度定制 MetaHuman 外观并创建大量变体，此插件是必要的。但鉴于其 Beta 状态，在生产环境中使用时应密切关注更新日志，并做好应对潜在兼容性问题的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter/Source/MetaHumanCharacterPaletteEditor)
- 官方文档：暂无
- 测试用例：模块内 `Private/Tests/` 目录下包含测试用 Pipeline（如 `MetaHumanCharacterTestPipeline.h`）。