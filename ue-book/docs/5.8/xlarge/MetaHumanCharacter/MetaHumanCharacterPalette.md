# MetaHuman Character Palette

> MetaHuman Character Asset Creator and Editor.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 角色调色板 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `MetaHumanCharacter` (Runtime), `MetaHumanCharacterEditor` (Runtime), `MetaHumanCharacterMigrationEditor` (Runtime), `MetaHumanCharacterPalette` (Runtime), `MetaHumanCharacterPaletteEditor` (Runtime), `MetaHumanDefaultEditorPipeline` (Runtime), `MetaHumanDefaultPipeline` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter) | |

---

## 用途

MetaHumanCharacterPalette 模块是 MetaHuman 角色系统的核心数据管理框架，解决的是**如何以模块化、可组合的方式管理 MetaHuman 角色部件**的问题。

具体来说，它实现了一套**调色板（Palette）- 收藏集（Collection）- 实例（Instance）**的三层架构：

1. **Palette（调色板）**：管理一组角色部件（衣物、发型、面部等），每个部件通过 `FMetaHumanPaletteItemKey` 唯一标识，支持嵌套（部件中包含子部件）。
2. **Collection（收藏集）**：继承自 Palette，是实际的角色构建单元。它通过一条**管线（Pipeline）**将所有部件组装成可渲染的角色。Collection 支持构建（Build）、实例化、资产解包等操作。
3. **Instance（实例）**：从 Collection 派生，允许用户通过**槽位选择（Slot Selection）**挑选部件并组装成最终可渲染的角色。Instance 支持参数覆盖、异步组装、烘焙输出等。

这套系统使得 MetaHuman 角色可以像乐高积木一样组合：不同质量等级的身体、面部、衣物、发型可以自由搭配，通过管线系统进行兼容性检查和组装。

---

## 使用场景

- **你正在为 MetaHuman 项目构建角色编辑器** → 使用 `UMetaHumanCollection` 管理角色部件组合，`UMetaHumanInstance` 在运行时组装
- **你需要为自定义角色部件系统（如服装、发型）实现管线化构建流程** → 实现 `UMetaHumanItemPipeline` 和 `UMetaHumanCollectionPipeline` 的子类
- **你需要支持角色部件的动态切换和参数调节** → 通过 Instance 的槽位选择和 Instance Parameter 机制
- **你需要在不同质量等级（Preview/Production）之间切换角色构建** → 使用 `EMetaHumanCharacterPaletteBuildQuality`
- **你需要将内嵌资产解包为独立资产** → 使用 `UMetaHumanCollection::UnpackAssets`

---

## 蓝图用法

本模块提供了大量蓝图可用的 API，通过多个 BlueprintFunctionLibrary 暴露。

### 调色板与项目管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPipelineSpecification` | 获取调色板管线的规格说明 | `UMetaHumanCollectionBlueprintLibrary` |
| `GetSlotNames` | 获取管线定义的所有虚拟槽位名称 | `UMetaHumanCollectionBlueprintLibrary` |
| `GetAllItemKeys` | 获取调色板中所有项目的 Key | `UMetaHumanCollectionBlueprintLibrary` |
| `GetItemKeysForSlot` | 获取指定槽位下所有项目的 Key | `UMetaHumanCollectionBlueprintLibrary` |
| `GetItemKeysForPrincipalAsset` | 按主资产查找项目 Key | `UMetaHumanCollectionBlueprintLibrary` |
| `GetItemKeysForWardrobeItem` | 按外部衣柜物品查找项目 Key | `UMetaHumanCollectionBlueprintLibrary` |
| `GetItemSlotName` | 获取项目所属的槽位名称 | `UMetaHumanCollectionBlueprintLibrary` |

### 项目 Key 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ReferencesSameAsset` | 判断两个 Key 是否引用同一资产（忽略 Variation） | `UMetaHumanPaletteKeyBlueprintLibrary` |
| `ToAssetNameString` | 将 Key 转为可用于资产命名的字符串 | `UMetaHumanPaletteKeyBlueprintLibrary` |
| `IsNull` | 判断 Key 是否为空（不引用任何资产） | `UMetaHumanPaletteKeyBlueprintLibrary` |
| `MakeItemPath` | 从 Key 构造 ItemPath | `UMetaHumanPaletteItemPathBlueprintLibrary` |

### Instance 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DuplicateMetaHumanInstance` | 创建 Instance 的暂态副本 | `UMetaHumanCharacterInstanceBlueprintLibrary` |
| `GetInstanceParameters` | 获取指定项目的所有实例参数 | `UMetaHumanCharacterInstanceBlueprintLibrary` |
| `GetInstanceParameterItemPaths` | 获取有实例参数定义的所有项目路径 | `UMetaHumanCharacterInstanceBlueprintLibrary` |
| `TryGetInstanceParameter` | 按路径和名称查找单个实例参数 | `UMetaHumanCharacterInstanceBlueprintLibrary` |
| `GetAllowedItemKeysForSlot` | 获取当前选择下指定槽位的可选项目 | `UMetaHumanCharacterInstanceBlueprintLibrary` |

### Instance 参数读写

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetBool` / `SetBool` | 读写布尔型实例参数 | `UMetaHumanCharacterInstanceParameterBlueprintLibrary` |
| `GetFloat` / `SetFloat` | 读写浮点型实例参数 | `UMetaHumanCharacterInstanceParameterBlueprintLibrary` |
| `GetName` / `SetName` | 读写 Name 型实例参数 | `UMetaHumanCharacterInstanceParameterBlueprintLibrary` |
| `GetString` / `SetString` | 读写字符串型实例参数 | `UMetaHumanCharacterInstanceParameterBlueprintLibrary` |
| `GetColor` / `SetColor` | 读写颜色型实例参数 | `UMetaHumanCharacterInstanceParameterBlueprintLibrary` |
| `GetObject` / `SetObject` | 读写对象型实例参数 | `UMetaHumanCharacterInstanceParameterBlueprintLibrary` |
| `GetSoftObject` / `SetSoftObject` | 读写软引用型实例参数 | `UMetaHumanCharacterInstanceParameterBlueprintLibrary` |

### 管线槽位选择

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeSlotSelection` | 构造槽位选择结构体 | `UMetaHumanPipelineSlotSelectionBlueprintLibrary` |
| `GetSelectedItemPath` | 获取选中项的完整路径 | `UMetaHumanPipelineSlotSelectionBlueprintLibrary` |
| `GetSelectedSlotName` | 获取槽位名称 | `UMetaHumanPipelineSlotSelectionBlueprintLibrary` |
| `GetSelectedItemKey` | 获取选中项的 Key | `UMetaHumanPipelineSlotSelectionBlueprintLibrary` |

### 使用示例（蓝图描述）

**场景：运行时动态切换角色衣物**

1. 获取一个 `UMetaHumanCollection` 引用（已构建好的）
2. 创建 `UMetaHumanInstance`，调用 `SetMetaHumanCollection` 绑定到 Collection
3. 调用 `GetSlotNames` 获取可用槽位（如 "Torso", "Legs" 等）
4. 调用 `GetItemKeysForSlot` 获取某个槽位下所有可选衣物
5. 调用 `SetSingleSlotSelection` 为槽位选择一个衣物部件
6. 调用 `Assemble`（蓝图节点）组装角色，通过回调获取组装结果
7. 调用 `GetAssemblyOutput` 获取组装输出（网格体、材质等）

**场景：读取和设置实例参数**

1. 在 Instance 上调用 `GetInstanceParameters` 获取某个项目路径的参数列表
2. 遍历返回的 `FMetaHumanCharacterInstanceParameter` 数组
3. 根据参数的 `Type` 字段，调用对应的 Get/Set 函数（如 `GetFloat`/`SetFloat`）
4. 调用 Set 函数后参数会**立即生效**并应用到 Instance

---

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCharacterPalette.h"
#include "MetaHumanCollection.h"
#include "MetaHumanInstance.h"
#include "MetaHumanCollectionBlueprintLibrary.h"
```

### 基本用法：创建 Collection 并添加项目

```cpp
// 创建一个新的 Collection
UMetaHumanCollection* Collection = NewObject<UMetaHumanCollection>();

// 设置默认管线
Collection->SetDefaultPipeline();

// 从主资产添加项目到指定槽位
FMetaHumanPaletteItemKey NewItemKey;
bool bSuccess = Collection->TryAddItemFromPrincipalAsset(
    FName("Body"),
    FSoftObjectPath("/Game/Characters/Body_Mesh.Body_Mesh"),
    NewItemKey
);

// 或从外部 Wardrobe Item 添加
// UMetaHumanWardrobeItem* WardrobeItem = LoadObject<UMetaHumanWardrobeItem>(...);
// Collection->TryAddItemFromWardrobeItem(FName("Torso"), WardrobeItem, NewItemKey);
```

### 基本用法：构建 Collection

```cpp
// 构建 Collection 以便实例可以从中组装
FInstancedStruct BuildInput;
TArray<FMetaHumanPinnedSlotSelection> PinnedSelections;

Collection->Build(
    BuildInput,
    FMetaHumanCollection::FOnBuildComplete::CreateLambda([](EMetaHumanBuildStatus Status) {
        if (Status == EMetaHumanBuildStatus::Succeeded)
        {
            UE_LOG(LogMetaHumanCharacterPalette, Log, TEXT("Collection built successfully"));
        }
    }),
    PinnedSelections
);
```

### 基本用法：组装 Instance

```cpp
// 从 Collection 创建 Instance
UMetaHumanInstance* Instance = NewObject<UMetaHumanInstance>();
Instance->SetMetaHumanCollection(Collection);

// 选择槽位项目
Instance->SetSingleSlotSelection(FName("Head"), HeadItemKey);
Instance->SetSingleSlotSelection(FName("Torso"), TorsoItemKey);

// 组装角色
Instance->Assemble(FMetaHumanCharacterAssembledNative::CreateLambda(
    [](EMetaHumanCharacterAssemblyResult Result) {
        if (Result == EMetaHumanCharacterAssemblyResult::Succeeded)
        {
            // 组装成功，可以获取输出
        }
    }
));

// 获取组装输出（如果已组装则直接返回，否则触发组装）
const FInstancedStruct& Output = Instance->GetAssemblyOutput();
```

### 进阶用法：使用蓝图库查询调色板

```cpp
// 查询 Collection 中某个槽位的所有可选项目
TArray<FMetaHumanPaletteItemKey> ItemKeys =
    UMetaHumanCollectionBlueprintLibrary::GetItemKeysForSlot(Collection, FName("Head"));

// 查询管线规格
UMetaHumanCharacterPipelineSpecification* Spec =
    UMetaHumanCollectionBlueprintLibrary::GetPipelineSpecification(Collection);

TArray<FName> SlotNames =
    UMetaHumanCollectionBlueprintLibrary::GetSlotNames(Collection);

// 查询某个实例参数
FMetaHumanCharacterInstanceParameter Param;
bool bFound = UMetaHumanCharacterInstanceBlueprintLibrary::TryGetInstanceParameter(
    Instance, ItemPath, FName("MaterialIntensity"), Param);

if (bFound)
{
    float Value;
    UMetaHumanCharacterInstanceParameterBlueprintLibrary::GetFloatInstanceParameter(Param, Value);
    Value *= 2.0f;
    UMetaHumanCharacterInstanceParameterBlueprintLibrary::SetFloatInstanceParameter(Param, Value);
}
```

### 进阶用法：遍历 Instance 的兼容选项

```cpp
// 询问："在当前已选内容下，Head 槽位还能选哪些项目？"
TArray<FMetaHumanPaletteItemKey> AllowedKeys =
    UMetaHumanCharacterInstanceBlueprintLibrary::GetAllowedItemKeysForSlot(Instance, FName("Head"));

for (const FMetaHumanPaletteItemKey& Key : AllowedKeys)
{
    FString AssetName = UMetaHumanPaletteKeyBlueprintLibrary::ToAssetNameString(Key);
    UE_LOG(LogMetaHumanCharacterPalette, Log, TEXT("Allowed head: %s"), *AssetName);
}
```

### 进阶用法：Instance 参数覆盖

```cpp
// 获取所有 Assembly 参数
TMap<FMetaHumanPaletteItemPath, FInstancedPropertyBag> AssemblyParams = 
    Instance->GetAssemblyParameters();

// 获取所有 Post-Assembly 参数
TMap<FMetaHumanPaletteItemPath, FInstancedPropertyBag> PostAssemblyParams = 
    Instance->GetPostAssemblyParameters();

// 覆盖某个项目的参数
FMetaHumanPaletteItemPath ItemPath; // 目标项目的路径
FInstancedPropertyBag NewValues;
// ... 设置 NewValues 中的属性 ...
EMetaHumanInstanceParameterOverrideResult Result = 
    Instance->OverrideInstanceParameters(ItemPath, NewValues);
```

---

## Demo 示例

### 头文件：MetaHumanDemoActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanDemoActor.generated.h"

class UMetaHumanCollection;
class UMetaHumanInstance;
struct FMetaHumanPaletteItemKey;

UCLASS()
class AMetaHumanDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMetaHumanDemoActor();

    /** 要使用的 Collection 资产路径 */
    UPROPERTY(EditAnywhere, Category = "MetaHuman")
    TSoftObjectPtr<UMetaHumanCollection> CollectionAsset;

    /** 在 BeginPlay 中自动组装 */
    UPROPERTY(EditAnywhere, Category = "MetaHuman")
    bool bAutoAssemble = true;

    /** 切换到指定槽位的下一件物品 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void CycleSlotItem(FName SlotName);

    /** 获取 Instance 引用 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    UMetaHumanInstance* GetInstance() const { return Instance; }

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanInstance> Instance;

    void OnAssembleComplete();
};
```

### 源文件：MetaHumanDemoActor.cpp

```cpp
#include "MetaHumanDemoActor.h"
#include "MetaHumanCollection.h"
#include "MetaHumanInstance.h"
#include "MetaHumanCollectionBlueprintLibrary.h"
#include "MetaHumanCharacterInstanceBlueprintLibrary.h"

AMetaHumanDemoActor::AMetaHumanDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMetaHumanDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建 Instance
    Instance = NewObject<UMetaHumanInstance>(this);

    // 加载并设置 Collection
    UMetaHumanCollection* Collection = CollectionAsset.LoadSynchronous();
    if (!Collection)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load MetaHuman Collection"));
        return;
    }

    Instance->SetMetaHumanCollection(Collection);

    // 如果启用了自动组装
    if (bAutoAssemble)
    {
        Instance->Assemble(FMetaHumanCharacterAssembledNative::CreateUObject(
            this, &AMetaHumanDemoActor::OnAssembleComplete));
    }
}

void AMetaHumanDemoActor::CycleSlotItem(FName SlotName)
{
    if (!Instance || !Instance->GetMetaHumanCollection())
    {
        return;
    }

    UMetaHumanCollection* Collection = Instance->GetMetaHumanCollection();

    // 获取该槽位的所有可选项目
    TArray<FMetaHumanPaletteItemKey> AvailableItems =
        UMetaHumanCollectionBlueprintLibrary::GetItemKeysForSlot(Collection, SlotName);

    if (AvailableItems.Num() == 0)
    {
        return;
    }

    // 获取当前选中项
    FMetaHumanPaletteItemKey CurrentKey;
    bool bHasCurrent = Instance->TryGetAnySlotSelection(SlotName, CurrentKey);

    // 找到当前项的索引
    int32 CurrentIndex = -1;
    if (bHasCurrent)
    {
        for (int32 i = 0; i < AvailableItems.Num(); ++i)
        {
            if (AvailableItems[i].ReferencesSameAsset(CurrentKey))
            {
                CurrentIndex = i;
                break;
            }
        }
    }

    // 切换到下一项
    int32 NextIndex = (CurrentIndex + 1) % AvailableItems.Num();
    Instance->SetSingleSlotSelection(SlotName, AvailableItems[NextIndex]);

    // 重新组装
    Instance->Assemble(FMetaHumanCharacterAssembledNative::CreateUObject(
        this, &AMetaHumanDemoActor::OnAssembleComplete));
}

void AMetaHumanDemoActor::OnAssembleComplete()
{
    if (!Instance)
    {
        return;
    }

    const FInstancedStruct& Output = Instance->GetAssemblyOutput();
    if (Output.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("MetaHuman assembled successfully"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("MetaHuman assembly produced no output"));
    }
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StructUtils` | FInstancedStruct / FInstancedPropertyBag 的运行时支持 |
| `PropertyBag` | 实例参数的属性包系统 |
| `MetaHumanCore` | MetaHuman 核心类型定义（如质量等级、DNA 等） |

> 无其他特殊依赖（仅标准 Core/CoreUObject/Engine 等）

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `95d906ba` | [UEMHC] Checking for Asset Registry filter validity before using it | 使用前验证资产注册表过滤器有效性 |
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | MetaHuman Titan 版本升级至 v9.0.8 |
| 2026-05-26 | `efb27122` | [UEMHC] Duplicate face/body DNA when duplicating archetype skel meshes | 复制原型骨架网格时同步复制面部/身体 DNA |
| 2026-05-26 | `909bc538` | [MHC] Use safer weak pointers for captured objects in MHC preview delegates | MHC 预览委托中使用更安全的弱指针 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | MetaHuman Titan 版本升级至 v9.0.7 |

### 维护评价

**🟢 活跃维护中**

- **创建时间**：2025-03-17，至今约 1 年
- **更新频率**：最近 5 次提交均在 2026-05-26，表明仍在密集开发
- **状态标记**：`IsBetaVersion=true`，`EnabledByDefault=false` — 属于 Beta 阶段，需要手动启用
- **API 稳定性**：源码中存在大量 `UE_DEPRECATED(5.8, ...)` 标记，说明 API 正在经历快速迭代和重构（如 `UMetaHumanCharacterInstance` 重命名为 `UMetaHumanInstance`，Instance Parameters 分为 Assembly 和 Post-Assembly 两类）
- **推荐程度**：适合开发者探索和实验，但注意 API 在 5.8 版本中有大量破坏性变更。生产环境使用需密切关注版本更新和迁移指南

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter)
- 官方文档：（.uplugin 中 DocsURL 为空，暂无官方文档链接）