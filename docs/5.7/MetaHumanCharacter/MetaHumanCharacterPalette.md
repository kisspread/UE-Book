# MetaHuman Creator

> MetaHuman Character Asset Creator and Editor.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaHuman 角色资产、管线配置） |
| 模块 | `MetaHumanCharacter` (Runtime), `MetaHumanCharacterEditor` (Runtime), `MetaHumanCharacterMigrationEditor` (Runtime), `MetaHumanCharacterPalette` (Runtime), `MetaHumanCharacterPaletteEditor` (Runtime), `MetaHumanDefaultEditorPipeline` (Runtime), `MetaHumanDefaultPipeline` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter) | |

## 用途

MetaHumanCharacter 插件实现了一套**模块化角色组装框架**，用于从可组合的部件（服装、发型、配饰等）构建完整的 MetaHuman 角色。

它解决的核心问题是：如何将大量独立的角色资产（网格体、材质、纹理）通过可扩展的管线系统组合成一个可渲染的角色，同时支持：

- **槽位（Slot）驱动的组装**：角色部件通过槽位分配，而非硬编码的网格体替换
- **管线（Pipeline）架构**：构建（Build）和组装（Assembly）逻辑通过可替换的管线实现，允许自定义处理流程
- **质量分级构建**：支持 Production（生产）和 Preview（预览）两种质量级别
- **虚拟槽位**：通过转发机制实现槽位的可扩展性，无需修改管线
- **固定选择（Pinned Selection）**：在构建时锁定某些槽位的分配
- **实例参数**：组装后仍可通过参数进行运行时自定义（如材质颜色、纹理分辨率）
- **嵌套物品**：物品可以包含子物品，形成树状结构

简而言之，这不是一个简单的"换装系统"，而是一个完整的**角色资产管线框架**，覆盖从编辑器构建到运行时组装的全流程。

## 使用场景

- 你在构建 MetaHuman 角色的自定义编辑器工具 → 使用 `UMetaHumanCollection` 管理角色部件集合
- 你需要将服装、发型等资产组装成可渲染的角色 → 使用 `UMetaHumanCharacterInstance` 进行组装
- 你要实现自定义的角色构建流程（如特殊的身体适配逻辑） → 继承 `UMetaHumanCollectionPipeline` 和 `UMetaHumanItemPipeline`
- 你需要在运行时动态切换角色外观 → 通过 `UMetaHumanCharacterInstance` 的槽位选择和实例参数
- 你要将 MetaHuman 角色集成到已有的 Actor 蓝图中 → 实现 `IMetaHumanCharacterActorInterface`

## 架构概览

### 模块职责

| 模块 | 职责 |
|---|---|
| `MetaHumanCharacter` | 核心运行时类型定义和基础接口 |
| `MetaHumanCharacterEditor` | 角色编辑器 UI 和编辑功能 |
| `MetaHumanCharacterMigrationEditor` | 旧版 MetaHuman 资产迁移工具 |
| `MetaHumanCharacterPalette` | 调色板/集合系统：物品、管线、槽位、实例的核心逻辑 |
| `MetaHumanCharacterPaletteEditor` | 调色板编辑器 UI |
| `MetaHumanDefaultEditorPipeline` | 默认编辑器管线实现 |
| `MetaHumanDefaultPipeline` | 默认运行时管线实现 |

### 核心概念

```
┌─────────────────────────────────────────────────────┐
│                  UMetaHumanCollection                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │ WardrobeItem │ │ WardrobeItem │ │ WardrobeItem │ │
│  │  (服装)      │ │  (发型)      │ │  (配饰)      │ │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ │
│         │                │                │         │
│    ItemPipeline     ItemPipeline     ItemPipeline   │
└─────────┼────────────────┼────────────────┼─────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────┐
│              CollectionPipeline                      │
│         (组装所有物品 → 渲染角色)                      │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│            UMetaHumanCharacterInstance               │
│  - 选择槽位分配                                       │
│  - 设置实例参数                                       │
│  - 调用 Assemble() → 产出可渲染角色                    │
└─────────────────────────────────────────────────────┘
```

**关键类关系**：

- **`UMetaHumanCollection`**：角色部件的容器，持有多个 `FMetaHumanCharacterPaletteItem`
- **`UMetaHumanWardrobeItem`**：单个衣柜物品，关联一个主资产（PrincipalAsset）和一个 ItemPipeline
- **`UMetaHumanCharacterPipeline`** → **`UMetaHumanCollectionPipeline`** / **`UMetaHumanItemPipeline`**：管线层次结构
- **`UMetaHumanCharacterPipelineSpecification`**：定义管线接受的槽位及其类型
- **`UMetaHumanCharacterInstance`**：运行时组装器，从 Collection 中选择物品并组装
- **`FMetaHumanPipelineSlotSelection`**：槽位选择，将物品分配到槽位
- **`FMetaHumanPaletteItemPath`**：物品在嵌套层次中的路径

### 数据流

```
编辑器阶段（Build）:
  Collection + WardrobeItems + PinnedSelections
    → CollectionEditorPipeline.BuildCollection()
    → FMetaHumanCollectionBuiltData（缓存的构建产物）

运行时阶段（Assembly）:
  Collection + SlotSelections + InstanceParameters
    → CollectionPipeline.AssembleCollection()
    → AssemblyOutput（网格体、材质等可渲染资产）
```

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Assemble` | 使用当前槽位选择组装角色，异步回调 | `UMetaHumanCharacterInstance` |
| `GetAssemblyOutput` | 获取最近一次组装的输出（FInstancedStruct） | `UMetaHumanCharacterInstance` |
| `ClearAssemblyOutput` | 清除组装输出（不清除实例参数） | `UMetaHumanCharacterInstance` |
| `SetMetaHumanCollection` | 设置要组装的 Collection（传 nullptr 清除） | `UMetaHumanCharacterInstance` |
| `GetMetaHumanCollection` | 获取当前关联的 Collection | `UMetaHumanCharacterInstance` |
| `SetSlotSelection` | 为指定槽位设置物品选择 | `UMetaHumanCharacterInstance` |
| `GetSlotSelection` | 获取指定槽位的当前选择 | `UMetaHumanCharacterInstance` |
| `ClearSlotSelection` | 清除指定槽位的选择 | `UMetaHumanCharacterInstance` |
| `GetSlotSelections` | 获取所有槽位选择 | `UMetaHumanCharacterInstance` |
| `SetInstanceParameter` | 设置运行时实例参数 | `UMetaHumanCharacterInstance` |
| `GetInstanceParameter` | 获取实例参数值 | `UMetaHumanCharacterInstance` |
| `SetCharacterInstance` | 从 CharacterInstance 初始化 Actor（蓝图原生事件） | `IMetaHumanCharacterActorInterface` |

### 使用示例（蓝图描述）

**基本组装流程**：

1. 创建 `UMetaHumanCharacterInstance` 对象
2. 拖入一个 `UMetaHumanCollection` 资产，调用 `SetMetaHumanCollection` 设置
3. 对每个需要分配的槽位，创建 `FMetaHumanPipelineSlotSelection` 结构体：
   - 设置 `SlotName`（如 `"Body"`、`"Top"`、`"Hair"`）
   - 设置 `SelectedItem`（`FMetaHumanPaletteItemKey`，引用主资产和变体名）
4. 调用 `SetSlotSelection` 将选择应用到实例
5. 调用 `Assemble`，选择质量级别（Production 或 Preview）
6. 在回调中检查 `Result`，成功后通过 `GetAssemblyOutput` 获取组装结果

**Actor 集成**：

1. 创建一个 Actor 蓝图，实现 `IMetaHumanCharacterActorInterface` 接口
2. 实现 `SetCharacterInstance` 事件：接收 `UMetaHumanCharacterInstance`，提取组装输出并应用到组件
3. 该 Actor 可作为 Character 编辑器中的预览 Actor 使用

## C++ 用法

### 头文件引入

```cpp
// 核心类型
#include "MetaHumanCharacterInstance.h"
#include "MetaHumanCollection.h"
#include "MetaHumanWardrobeItem.h"

// 槽位与选择
#include "MetaHumanPipelineSlotSelection.h"
#include "MetaHumanPipelineSlotSelectionData.h"
#include "MetaHumanPaletteItemKey.h"
#include "MetaHumanPaletteItemPath.h"

// 管线（自定义管线时需要）
#include "MetaHumanCollectionPipeline.h"
#include "MetaHumanItemPipeline.h"
#include "MetaHumanCharacterPipelineSpecification.h"

// 固定选择与参数
#include "MetaHumanPinnedSlotSelection.h"
#include "MetaHumanParameterMappingTable.h"
```

### 基本用法

从 `MetaHumanCharacterInstance` 的 API 提取的核心用法：

```cpp
// 创建一个 Character Instance（可以是编辑器资产或运行时瞬态对象）
UMetaHumanCharacterInstance* Instance = NewObject<UMetaHumanCharacterInstance>();

// 设置要使用的 Collection
Instance->SetMetaHumanCollection(MyCollection);

// 为槽位设置物品选择
FMetaHumanPipelineSlotSelection BodySelection;
BodySelection.SlotName = FName("Body");
BodySelection.SelectedItem = FMetaHumanPaletteItemKey(BodyMeshAsset, NAME_None);
Instance->SetSlotSelection(BodySelection);

FMetaHumanPipelineSlotSelection HairSelection;
HairSelection.SlotName = FName("Hair");
HairSelection.SelectedItem = FMetaHumanPaletteItemKey(HairMeshAsset, NAME_None);
Instance->SetSlotSelection(HairSelection);

// 异步组装
Instance->Assemble(
    EMetaHumanCharacterPaletteBuildQuality::Production,
    FMetaHumanCharacterAssembledNative::CreateLambda(
        [](EMetaHumanCharacterAssemblyResult Result)
        {
            if (Result == EMetaHumanCharacterAssemblyResult::Succeeded)
            {
                UE_LOG(LogTemp, Log, TEXT("Character assembled successfully"));
            }
        })
);

// 获取组装输出
const FInstancedStruct& Output = Instance->GetAssemblyOutput();
```

### 进阶用法

**使用实例参数进行运行时自定义**：

```cpp
// 组装完成后，查询可用的实例参数
FPropertyBagPropertyDesc OutDesc;
// 通过 GetAvailableInstanceParameters 获取参数描述

// 设置实例参数（如材质颜色）
FMetaHumanParameterValue ParamValue;
ParamValue.Type = EMetaHumanParameterValueType::Color;
ParamValue.ColorValue = FLinearColor::Red;
// Instance->SetInstanceParameter(ParameterName, ParamValue);
```

**使用固定选择（Pinned Selections）锁定槽位**：

```cpp
// 在构建 Collection 时，可以固定某些槽位的选择
TArray<FMetaHumanPinnedSlotSelection> PinnedSelections;

FMetaHumanPinnedSlotSelection PinnedBody;
PinnedBody.Selection.SlotName = FName("Body");
PinnedBody.Selection.SelectedItem = FMetaHumanPaletteItemKey(BodyAsset, NAME_None);
// 可选：设置烘焙时使用的实例参数
PinnedBody.InstanceParameters.SetValueFloat(FName("SkinTone"), 0.5f);
PinnedSelections.Add(PinnedBody);

// 排序后传入 Build
PinnedSelections.Sort();
Collection->Build(BuildInput, Quality, TargetPlatform, OnComplete, PinnedSelections);
```

**使用物品路径处理嵌套物品**：

```cpp
// 物品可以嵌套，使用 FMetaHumanPaletteItemPath 表示完整路径
FMetaHumanPaletteItemPath ItemPath;
// 简单情况：直接在 Collection 中的物品
FMetaHumanPaletteItemPath SimplePath(FMetaHumanPaletteItemKey(Asset, NAME_None));

// 嵌套情况：物品包含子物品
TArray<FMetaHumanPaletteItemKey> Parents;
Parents.Add(FMetaHumanPaletteItemKey(ParentAsset, NAME_None));
FMetaHumanPaletteItemPath NestedPath(Parents, FMetaHumanPaletteItemKey(ChildAsset, NAME_None));

// 检查路径关系
bool bIsChild = NestedPath.IsDirectChildPathOf(SimplePath);  // true
bool bIsRelated = NestedPath.IsEqualOrChildPathOf(SimplePath); // true
```

**实现自定义 Actor 接口**：

```cpp
// .h
UCLASS()
class AMyMetaHumanActor : public AActor, public IMetaHumanCharacterActorInterface
{
    GENERATED_BODY()
public:
    virtual void SetCharacterInstance_Implementation(UMetaHumanCharacterInstance* CharacterInstance) override;
};

// .cpp
void AMyMetaHumanActor::SetCharacterInstance_Implementation(UMetaHumanCharacterInstance* CharacterInstance)
{
    if (!CharacterInstance)
    {
        return;
    }

    // 获取组装输出并应用到组件
    const FInstancedStruct& AssemblyOutput = CharacterInstance->GetAssemblyOutput();
    // 根据 AssemblyOutput 设置 SkeletalMeshComponent 等
}
```

## Demo 示例

以下是一个完整的最小示例，展示如何创建 Character Instance、设置槽位选择并组装角色。

### MyMetaHumanAssembler.h

```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "MetaHumanCharacterInstance.h"
#include "MetaHumanCollection.h"
#include "MetaHumanPipelineSlotSelection.h"
#include "MetaHumanPaletteItemKey.h"
#include "Components/ActorComponent.h"
#include "MyMetaHumanAssembler.generated.h"

/**
 * 一个简单的组件，演示如何使用 MetaHumanCharacter 系统组装角色。
 */
UCLASS(ClassGroup=(MetaHuman), meta=(BlueprintSpawnableComponent))
class UMyMetaHumanAssembler : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyMetaHumanAssembler();

    /** 要使用的 MetaHuman Collection */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MetaHuman")
    TObjectPtr<UMetaHumanCollection> Collection;

    /** 组装质量 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MetaHuman")
    EMetaHumanCharacterPaletteBuildQuality Quality = EMetaHumanCharacterPaletteBuildQuality::Production;

    /** 执行组装 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void AssembleCharacter();

    /** 获取组装结果 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    const FInstancedStruct& GetAssemblyOutput() const;

protected:
    /** 内部的 Character Instance */
    UPROPERTY(Transient)
    TObjectPtr<UMetaHumanCharacterInstance> CharacterInstance;
};
```

### MyMetaHumanAssembler.cpp

```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyMetaHumanAssembler.h"

UMyMetaHumanAssembler::UMyMetaHumanAssembler()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyMetaHumanAssembler::AssembleCharacter()
{
    if (!Collection)
    {
        UE_LOG(LogTemp, Warning, TEXT("MyMetaHumanAssembler: No Collection set"));
        return;
    }

    // 创建或复用 Character Instance
    if (!CharacterInstance)
    {
        CharacterInstance = NewObject<UMetaHumanCharacterInstance>(this);
    }

    // 设置 Collection
    CharacterInstance->SetMetaHumanCollection(Collection);

    // 示例：为 Body 槽位选择一个物品
    // 实际使用时，槽位名称和物品 Key 取决于 Collection 和 Pipeline 的配置
    FMetaHumanPipelineSlotSelection SlotSelection;
    SlotSelection.SlotName = FName("Body");
    // SelectedItem 需要引用 Collection 中存在的物品
    // SlotSelection.SelectedItem = FMetaHumanPaletteItemKey(DesiredAsset, NAME_None);
    // CharacterInstance->SetSlotSelection(SlotSelection);

    // 执行组装
    CharacterInstance->Assemble(
        Quality,
        FMetaHumanCharacterAssembledNative::CreateLambda(
            [this](EMetaHumanCharacterAssemblyResult Result)
            {
                if (Result == EMetaHumanCharacterAssemblyResult::Succeeded)
                {
                    UE_LOG(LogTemp, Log, TEXT("Character assembled successfully"));
                    // 在此处理组装输出，如应用到 SkeletalMeshComponent
                    const FInstancedStruct& Output = CharacterInstance->GetAssemblyOutput();
                    // ...
                }
                else
                {
                    UE_LOG(LogTemp, Error, TEXT("Character assembly failed"));
                }
            })
    );
}

const FInstancedStruct& UMyMetaHumanAssembler::GetAssemblyOutput() const
{
    static const FInstancedStruct Empty;
    return CharacterInstance ? CharacterInstance->GetAssemblyOutput() : Empty;
}
```

## 模块依赖

从源码头文件推断的独特依赖（省略标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `StructUtils` | `FInstancedStruct`（管线输入/输出的类型擦除容器）、`FPropertyBag`（实例参数存储） |
| `MetaHumanTypes` | MetaHuman 通用类型定义（如 `EMetaHumanQualityLevel`） |
| `MetaHumanSDK` | MetaHuman SDK 验证规则（用于衣柜物品验证） |

> **注意**：完整的依赖列表请参考各模块的 `.Build.cs` 文件。该插件还可能依赖其他 MetaHuman 相关模块（如 MetaHumanCore、MetaHumanRuntime 等）。

## 维护状态

### 近期更新

```
- e67d33c9e2a4 [UEMHC] 允许在组装工具中设置烘焙纹理分辨率
- 6535d0f554b0 添加 UAF/AnimGraph 导出的 UI 选项
- 6e1152408cbf [UEMHC] 集成 MetaHuman SDK 的验证规则，在应用衣柜物品时进行验证
```

### 维护评价

- **创建时间**：2025-03-17，非常新的插件
- **Beta 状态**：`IsBetaVersion=true`，API 可能发生变化
- **默认未启用**：`EnabledByDefault=false`，需要手动在插件设置中启用
- **活跃开发**：近期 commit 显示持续的功能迭代（纹理分辨率配置、AnimGraph 导出、SDK 验证集成）
- **模块规模**：583 个源文件，7 个模块，架构复杂但层次清晰
- **推荐程度**：适合在 MetaHuman 相关项目中**实验性使用**，不建议在生产环境中依赖其 API 稳定性。随着 Beta 阶段推进，API 可能有 breaking changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter)
- [MetaHumanCharacterPalette 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter/Source/MetaHumanCharacterPalette)
- [MetaHumanCharacterPalette.Build.cs](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter/Source/MetaHumanCharacterPalette/MetaHumanCharacterPalette.Build.cs)