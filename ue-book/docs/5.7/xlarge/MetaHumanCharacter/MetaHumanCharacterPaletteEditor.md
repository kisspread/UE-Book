# MetaHuman Character Palette Editor

> MetaHuman Character Asset Creator and Editor.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、编辑器界面） |
| 模块 | `MetaHumanCharacter` (Runtime), `MetaHumanCharacterEditor` (Runtime), `MetaHumanCharacterMigrationEditor` (Runtime), `MetaHumanCharacterPalette` (Runtime), `MetaHumanCharacterPaletteEditor` (Runtime), `MetaHumanDefaultEditorPipeline` (Runtime), `MetaHumanDefaultPipeline` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter) | |

## 用途

MetaHumanCharacterPaletteEditor 模块是 MetaHuman 角色创建与编辑工作流的核心编辑器组件。它解决的核心问题是：在 Unreal Engine 编辑器中，为 MetaHuman 角色提供一个可视化的、基于部件（部件如发型、服装、配饰）的资产管理和组装界面。

该模块并非一个独立的运行时功能，而是 MetaHuman 角色编辑器的“大脑”和“画布”。它负责：
1.  **资产工厂**：提供创建 `UMetaHumanWardrobeItem`（衣橱物品）资产的工厂，这是构成角色部件的基础资产类型。
2.  **编辑器界面**：提供类似内容浏览器的 `SCharacterPartsView` 控件，用于以平铺视图（Tile View）的方式展示、选择和拖放角色部件。
3.  **材质处理**：提供工具函数，用于在解包（Unpack）调色板资产时，智能地复制材质实例，避免不必要的参数覆盖。
4.  **预览演员接口**：定义了 `IMetaHumanCharacterEditorActorInterface`，这是所有用于在编辑器中预览 MetaHuman 角色的 Actor 必须实现的接口，确保预览 Actor 能正确响应编辑器的 LOD、材质和动画控制。

## 使用场景

-   你正在为 MetaHuman 项目创建自定义的服装、发型或配饰资产 → 使用 `UMetaHumanWardrobeItemFactory` 来创建标准的衣橱物品资产。
-   你需要在编辑器中构建一个 MetaHuman 角色，从不同的调色板（Palette）中挑选部件进行组装 → 使用 `SCharacterPartsView` 控件来浏览和选择部件。
-   你正在开发一个自定义的 MetaHuman 角色 Pipeline，并需要一个能在编辑器中预览最终效果的 Actor → 实现 `IMetaHumanCharacterEditorActorInterface` 接口。
-   你需要将 MetaHuman 调色板资产解包成独立的材质实例，用于进一步编辑或优化 → 使用 `PaletteUnpackHelpers::CreateMaterialInstanceCopy` 函数。

## 蓝图用法

本模块主要提供 C++ 编辑器扩展和接口，直接暴露给蓝图的节点较少。核心的蓝图交互通过 `IMetaHumanCharacterEditorActorInterface` 接口实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InitializeMetaHumanCharacterEditorActor` | 由角色编辑器调用，用于初始化预览 Actor，传入角色数据、网格体和 LOD 映射信息。 | `IMetaHumanCharacterEditorActorInterface` |
| `SetForcedLOD` | 强制预览 Actor 显示指定的 LOD 级别。 | `IMetaHumanCharacterEditorActorInterface` |
| `SetFaceMaterialOverride` | 设置面部网格体的材质覆盖。 | `IMetaHumanCharacterEditorActorInterface` |
| `SetBodyMaterialOverride` | 设置身体网格体的材质覆盖。 | `IMetaHumanCharacterEditorActorInterface` |
| `SetHairVisibility` | 控制头发部件的显示/隐藏状态。 | `IMetaHumanCharacterEditorActorInterface` |
| `SetClothingVisibility` | 控制服装部件的显示/隐藏状态，支持使用覆盖材质。 | `IMetaHumanCharacterEditorActorInterface` |
| `SetDrivingAnimationMode` | 设置动画驱动模式（来自重定向源或手动播放）。 | `IMetaHumanCharacterEditorActorInterface` |

### 使用示例（蓝图描述）

由于 `IMetaHumanCharacterEditorActorInterface` 是一个 C++ 接口，无法直接在蓝图中实现。通常，你需要创建一个继承自 `AActor` 的 C++ 类或蓝图类，并在 C++ 中实现该接口。在蓝图中，你可以调用实现了该接口的 Actor 的上述函数。

例如，在角色编辑器的逻辑中，当用户更改了 LOD 设置时，编辑器会获取当前预览场景中实现了 `IMetaHumanCharacterEditorActorInterface` 的 Actor，并调用其 `SetForcedLOD` 函数。

## C++ 用法

### 头文件引入

```cpp
// 用于创建衣橱物品资产
#include "MetaHumanWardrobeItemFactory.h"

// 用于材质实例处理
#include "MetaHumanCharacterPaletteUnpackHelpers.h"

// 用于实现预览 Actor 接口
#include "MetaHumanCharacterEditorActorInterface.h"

// 用于集成部件浏览控件
#include "Widgets/SCharacterPartsView.h"
```

### 基本用法

**1. 创建衣橱物品资产 (来自 `MetaHumanWardrobeItemFactory.h`)**

```cpp
// 假设你正在编写一个编辑器工具，需要程序化创建衣橱物品
UMetaHumanWardrobeItemFactory* Factory = NewObject<UMetaHumanWardrobeItemFactory>();
UObject* NewAsset = Factory->FactoryCreateNew(
    UMetaHumanWardrobeItem::StaticClass(), // 要创建的类
    InParent, // 外部对象（通常是包）
    TEXT("MyNewWardrobeItem"), // 资产名称
    RF_NoFlags, // 对象标志
    nullptr, // 上下文
    GWarn // 反馈上下文
);
// NewAsset 现在是一个新创建的 UMetaHumanWardrobeItem 对象，可以进一步设置其属性。
```

**2. 智能复制材质实例 (来自 `MetaHumanCharacterPaletteUnpackHelpers.h`)**

```cpp
// 在解包调色板时，需要复制材质实例但避免覆盖所有参数
UMaterialInstanceConstant* SourceMaterial = /* ... */;
UObject* OuterForCopy = /* ... */; // 通常是目标包

UMaterialInstanceConstant* CopiedMaterial = UE::MetaHuman::PaletteUnpackHelpers::CreateMaterialInstanceCopy(
    SourceMaterial,
    OuterForCopy
);
// CopiedMaterial 只包含了与基础材质不同的参数，更“干净”。
```

**3. 实现预览 Actor 接口 (来自 `MetaHumanCharacterEditorActorInterface.h`)**

```cpp
// MyPreviewActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MetaHumanCharacterEditorActorInterface.h"
#include "MyPreviewActor.generated.h"

UCLASS()
class AMyPreviewActor : public AActor, public IMetaHumanCharacterEditorActorInterface
{
    GENERATED_BODY()
public:
    // 实现接口函数
    virtual void InitializeMetaHumanCharacterEditorActor(
        TNotNull<const UMetaHumanCharacterInstance*> InCharacterInstance,
        TNotNull<UMetaHumanCharacter*> InCharacter,
        TNotNull<USkeletalMesh*> InFaceMesh,
        TNotNull<USkeletalMesh*> InBodyMesh,
        int32 InNumLODs,
        const TArray<int32>& InFaceLODMapping,
        const TArray<int32>& InBodyLODMapping) override;

    virtual void SetForcedLOD(int32 InLOD) override;
    // ... 实现其他接口函数
};
```

### 进阶用法

**集成 `SCharacterPartsView` 控件到自定义编辑器面板**

```cpp
// 在自定义的 Slate 面板或编辑器模式中
void SMyCharacterEditorPanel::Construct(const FArguments& InArgs)
{
    // ... 其他构造代码

    // 创建部件浏览视图
    PartsView = SNew(SCharacterPartsView)
        .CharacterPalette(InArgs._CharacterPalette) // 传入要编辑的调色板资产
        .IsPaletteEditable(true) // 允许编辑
        .OnSelectionChanged(this, &SMyCharacterEditorPanel::OnPartSelected) // 绑定选择变更回调
        .OnPaletteModified(this, &SMyCharacterEditorPanel::OnPaletteChanged); // 绑定调色板修改回调

    // 将视图添加到布局
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        [
            PartsView.ToSharedRef()
        ]
        // ... 其他控件
    ];
}

void SMyCharacterEditorPanel::OnPartSelected(TSharedPtr<FMetaHumanCharacterPaletteItem> SelectedItem, ESelectInfo::Type SelectInfo)
{
    // 处理用户选择了一个部件
    if (SelectedItem.IsValid())
    {
        // 更新预览、属性面板等
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建一个实现了 `IMetaHumanCharacterEditorActorInterface` 的简单预览 Actor。

**MySimplePreviewActor.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "GameFramework/Actor.h"
#include "MetaHumanCharacterEditorActorInterface.h"
#include "MySimplePreviewActor.generated.h"

class USkeletalMeshComponent;
class ULODSyncComponent;

UCLASS()
class AMySimplePreviewActor : public AActor, public IMetaHumanCharacterEditorActorInterface
{
    GENERATED_BODY()

public:
    AMySimplePreviewActor();

    // IMetaHumanCharacterEditorActorInterface
    virtual void InitializeMetaHumanCharacterEditorActor(
        TNotNull<const UMetaHumanCharacterInstance*> InCharacterInstance,
        TNotNull<UMetaHumanCharacter*> InCharacter,
        TNotNull<USkeletalMesh*> InFaceMesh,
        TNotNull<USkeletalMesh*> InBodyMesh,
        int32 InNumLODs,
        const TArray<int32>& InFaceLODMapping,
        const TArray<int32>& InBodyLODMapping) override;

    virtual void SetForcedLOD(int32 InLOD) override;
    virtual void SetFaceMaterialOverride(UMaterialInterface* InMaterial) override;
    virtual void SetBodyMaterialOverride(UMaterialInterface* InMaterial) override;
    virtual void SetHairVisibility(EMetaHumanHairVisibilityState InState) override;
    virtual void SetClothingVisibility(EMetaHumanClothingVisibilityState InState, UMaterialInterface* InOverrideMaterial) override;
    virtual void SetDrivingAnimationMode(EMetaHumanActorDrivingAnimationMode InMode) override;
    // End IMetaHumanCharacterEditorActorInterface

private:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USkeletalMeshComponent> FaceMeshComponent;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USkeletalMeshComponent> BodyMeshComponent;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<ULODSyncComponent> LODSyncComponent;

    UPROPERTY()
    TObjectPtr<UMetaHumanCharacter> CurrentCharacter;
};
```

**MySimplePreviewActor.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#include "MySimplePreviewActor.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/LODSyncComponent.h"
#include "MetaHumanCharacter.h"
#include "MetaHumanCharacterInstance.h"

AMySimplePreviewActor::AMySimplePreviewActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建根组件和网格体组件
    FaceMeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("FaceMesh"));
    RootComponent = FaceMeshComponent;

    BodyMeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("BodyMesh"));
    BodyMeshComponent->SetupAttachment(RootComponent);

    // 创建 LOD 同步组件
    LODSyncComponent = CreateDefaultSubobject<ULODSyncComponent>(TEXT("LODSync"));
    // 在 InitializeMetaHumanCharacterEditorActor 中配置 CustomLODMapping
}

void AMySimplePreviewActor::InitializeMetaHumanCharacterEditorActor(
    TNotNull<const UMetaHumanCharacterInstance*> InCharacterInstance,
    TNotNull<UMetaHumanCharacter*> InCharacter,
    TNotNull<USkeletalMesh*> InFaceMesh,
    TNotNull<USkeletalMesh*> InBodyMesh,
    int32 InNumLODs,
    const TArray<int32>& InFaceLODMapping,
    const TArray<int32>& InBodyLODMapping)
{
    CurrentCharacter = InCharacter;

    // 设置网格体
    FaceMeshComponent->SetSkeletalMesh(InFaceMesh);
    BodyMeshComponent->SetSkeletalMesh(InBodyMesh);

    // 配置 LOD 同步
    LODSyncComponent->NumLODs = InNumLODs;

    // 为面部组件设置自定义 LOD 映射
    FLODMappingData FaceLODMappingData;
    FaceLODMappingData.Mapping = InFaceLODMapping;
    LODSyncComponent->CustomLODMapping.Add(FaceMeshComponent, FaceLODMappingData);

    // 为身体组件设置自定义 LOD 映射
    FLODMappingData BodyLODMappingData;
    BodyLODMappingData.Mapping = InBodyLODMapping;
    LODSyncComponent->CustomLODMapping.Add(BodyMeshComponent, BodyLODMappingData);
}

void AMySimplePreviewActor::SetForcedLOD(int32 InLOD)
{
    // 通过 LODSyncComponent 强制设置 LOD
    LODSyncComponent->SetForcedLOD(InLOD);
}

void AMySimplePreviewActor::SetFaceMaterialOverride(UMaterialInterface* InMaterial)
{
    if (FaceMeshComponent)
    {
        FaceMeshComponent->SetMaterial(0, InMaterial); // 假设材质槽索引为 0
    }
}

void AMySimplePreviewActor::SetBodyMaterialOverride(UMaterialInterface* InMaterial)
{
    if (BodyMeshComponent)
    {
        BodyMeshComponent->SetMaterial(0, InMaterial);
    }
}

void AMySimplePreviewActor::SetHairVisibility(EMetaHumanHairVisibilityState InState)
{
    // 根据状态显示或隐藏头发相关的组件（示例中未具体实现头发组件）
    // 通常需要查找或管理代表头发的子组件。
    UE_LOG(LogTemp, Log, TEXT("Hair visibility set to: %s"), 
        InState == EMetaHumanHairVisibilityState::Shown ? TEXT("Shown") : TEXT("Hidden"));
}

void AMySimplePreviewActor::SetClothingVisibility(EMetaHumanClothingVisibilityState InState, UMaterialInterface* InOverrideMaterial)
{
    // 根据状态处理服装组件的可见性和材质
    // 示例逻辑：
    // Shown: 显示组件，使用原始材质
    // UseOverrideMaterial: 显示组件，使用 InOverrideMaterial
    // Hidden: 隐藏组件
    UE_LOG(LogTemp, Log, TEXT("Clothing visibility state changed."));
}

void AMySimplePreviewActor::SetDrivingAnimationMode(EMetaHumanActorDrivingAnimationMode InMode)
{
    // 根据模式配置动画蓝图或重定向器
    UE_LOG(LogTemp, Log, TEXT("Animation driving mode set to: %s"),
        InMode == EMetaHumanActorDrivingAnimationMode::FromRetargetSource ? TEXT("FromRetargetSource") : TEXT("Manual"));
}
```

## 模块依赖

从模块功能和常见依赖推断，使用 `MetaHumanCharacterPaletteEditor` 模块，你的项目模块需要依赖以下内容：

| 模块 | 用途 |
|---|---|
| `MetaHumanCharacter` | 核心运行时数据类型，如 `UMetaHumanCharacter`, `UMetaHumanCharacterInstance` |
| `MetaHumanCharacterPalette` | 调色板和部件项的数据结构，如 `UMetaHumanCollection`, `FMetaHumanCharacterPaletteItem` |
| `SkeletalMeshComponents` | 用于操作 `USkeletalMeshComponent` 和 `ULODSyncComponent` |
| `ToolMenus` | 用于扩展编辑器菜单（如调试选项菜单） |
| `AssetTools` | 用于资产创建和管理操作 |
| `ContentBrowser` | 用于与内容浏览器交互，处理资产拖放 |

## 维护状态

### 近期更新

```
- 34f11e16e539 [UEMHC] Some improvements to skeletal mesh rendering debug options menu in UEMHC, and code cleanup.
- e503a313dd83 [UEMHC] Added debug Skeletal Mesh options for drawing bones, normals and tangents to viewport toolbar as a menu.
- f887f2204c09 Inject UAF pipeline blueprint + create UAF BPs
```

### 维护评价

-   **创建时间**：2025年3月，非常新的模块。
-   **最近更新频率**：近期有活跃的提交，主要集中在编辑器调试功能的增强（骨骼、法线、切线绘制）和代码清理，以及新功能（UAF Pipeline）的注入。
-   **维护状态**：**活跃维护中**。作为 MetaHuman 工具链的核心编辑器部分，预计会随着 MetaHuman 技术栈的更新而持续迭代。
-   **已知问题/限制**：该模块标记为 `IsBetaVersion: true`，表明其 API 和功能可能尚未完全稳定，在未来版本中可能发生变更。
-   **推荐使用**：**推荐用于 MetaHuman 相关的编辑器扩展开发**。如果你需要深度定制 MetaHuman 角色的创建、编辑或预览流程，这是必须依赖的模块。但需注意其 Beta 状态，做好应对 API 变化的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter)
- [官方文档]() (暂无)
- [测试用例]() (暂未在提供的路径中发现)