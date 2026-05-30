# Avalanche (AvalancheMaterial Module)

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态材质桥接 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质桥接系统、Shader 缓存配置） |
| 模块 | `AvalancheMaterial` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheMaterial) | |

---

## 用途

AvalancheMaterial 模块是 **Motion Design**（Avalanche）插件的材质子系统，提供了两套核心能力：

### 1. Material Bridge（材质桥接）

UE 中不同对象类型（Actor、StaticMesh、PrimitiveComponent、DecalComponent 等）的材质访问方式各不相同——有的通过 `GetMaterials()`，有的通过 `GetDecalMaterial()`，有的通过 `StaticMaterials` 数组。Material Bridge 通过**桥接模式**将这些差异统一抽象为一套通用 API，使得 Motion Design 工具链可以用同一套逻辑对任何对象类型进行材质的**读取、替换、状态存储与恢复**。

这解决了虚拟制作/广播场景中大量批量材质操作的需求——比如一个 Rundown 页面需要临时替换场景中所有物体的材质以实现合成效果，播放完毕后再恢复原始材质。

### 2. Material Cache（材质缓存）

在实时渲染和离线渲染（MRQ）中，材质的 Shader 编译是性能瓶颈。Material Cache Helper 提供了一个**分帧渐进式 Shader 缓存系统**，允许在多帧之间以受控的时间预算逐步缓存材质 Shader，避免单帧卡顿。

---

## 使用场景

- 你正在构建虚拟制作/广播的 Motion Design 场景 → 需要对场景中大量 Actor 进行批量材质替换和恢复
- 你的工具需要统一处理不同类型对象的材质槽 → 用 Material Bridge 统一接口
- 你正在做 Rundown 播放系统，需要预加载/预缓存场景中的所有材质 Shader → 用 Material Cache Helper
- 你需要自定义材质容器类型（如自定义组件）的桥接行为 → 继承 `FMaterialBridge` 注册自定义桥接

---

## 蓝图用法

AvalancheMaterial 模块主要是 C++ 运行时模块，提供的公开 API 主要面向 C++ 开发者。模块中没有发现 `BlueprintCallable` 或 `BlueprintReadWrite` 的公开函数。

材质桥接系统的使用场景主要通过 Motion Design 插件的上层蓝图工具（如 Scene Rig、Rundown 等）间接暴露，而非直接在蓝图中使用。

---

## C++ 用法

### 头文件引入

```cpp
#include "MaterialBridge/AvaMaterialBridge.h"
#include "MaterialBridge/AvaMaterialBridgeRegistry.h"
#include "MaterialBridge/Common/AvaActorMaterialBridge.h"
#include "MaterialBridge/Common/AvaPrimitiveComponentMaterialBridge.h"
#include "Internal/MaterialCache/AvaMaterialCacheHelper.h"
```

### 基本用法：通过 Material Bridge 读取材质

```cpp
// 从任意对象获取合适的 Material Bridge 并读取材质槽
// 来源: Public/MaterialBridge/AvaMaterialBridge.h, Public/MaterialBridge/AvaMaterialBridgeRegistry.h

using namespace UE::Ava;

// 1. 获取全局材质桥接注册表
const FMaterialBridgeRegistry& Registry = FMaterialBridgeRegistry::Get();

// 2. 为你的材质容器（如 Actor）创建只读上下文
//    传入一个 FConstDataView 指向目标对象
const AActor* MyActor = /* ... */;
FMaterialBridgeReadSlotContext ReadContext(MyActor);

// 3. 查找合适的 Material Bridge
const FMaterialBridge* Bridge = Registry.GetMaterialBridge(FConstDataView(MyActor));
if (Bridge)
{
    // 4. 遍历所有材质槽（只读）
    FMaterialBridgeReadSlotOptions ReadOptions;
    ReadOptions.MaterialBridgeRegistry = &Registry;

    Bridge->AccessSlots(ReadContext,
        [](const FMaterialBridgeReadSlotContext& Context, const FMaterialBridgeReadSlot& Slot) -> EControlFlow
        {
            UMaterialInterface* Material = Slot.GetMaterial();
            const FAvaMaterialBridgeSlotId& SlotId = Slot.GetSlotId();
            // 处理材质...
            UE_LOG(LogTemp, Log, TEXT("Found material: %s"), *GetNameSafe(Material));
            return EControlFlow::Continue;
        },
        ReadOptions);
}
```

### 基本用法：写入材质槽

```cpp
// 替换对象的材质槽
// 来源: Public/MaterialBridge/Slot/AvaMaterialBridgeWriteSlot.h

using namespace UE::Ava;

AActor* MyActor = /* ... */;
UMaterialInterface* NewMaterial = /* ... */;

const FMaterialBridgeRegistry& Registry = FMaterialBridgeRegistry::Get();
const FMaterialBridge* Bridge = Registry.GetMaterialBridge(FConstDataView(MyActor));

if (Bridge)
{
    // 写入上下文：MaterialContainer 必须是非 const 的 FDataView
    FMaterialBridgeWriteSlotContext WriteContext(MyActor);

    FMaterialBridgeWriteSlotOptions WriteOptions;
    WriteOptions.MaterialBridgeRegistry = &Registry;

    // 仅替换第一个材质槽
    Bridge->AccessSlots(WriteContext,
        [&NewMaterial](const FMaterialBridgeWriteSlotContext& Context, FMaterialBridgeWriteSlot& Slot) -> EControlFlow
        {
            Slot.SetMaterial(NewMaterial);
            return EControlFlow::Break; // 只替换一个就停止
        },
        WriteOptions);
}
```

### 进阶用法：材质状态存储与恢复

```cpp
// 典型流程：Store → Replace → Apply(恢复)
// 来源: Public/MaterialBridge/AvaMaterialBridge.h, Public/MaterialBridge/Common/AvaActorMaterialBridge.h

using namespace UE::Ava;

AActor* MyActor = /* ... */;
UMaterialInterface* TempMaterial = /* ... */;

const FMaterialBridgeRegistry& Registry = FMaterialBridgeRegistry::Get();
const FMaterialBridge* Bridge = Registry.GetMaterialBridge(FConstDataView(MyActor));

if (Bridge && Bridge->CanCreateContainerState())
{
    // 第一步：创建容器状态实例
    TInstancedStruct<FAvaMaterialContainerState> ContainerState = Bridge->CreateContainerState();

    // 第二步：存储当前材质状态
    FMaterialBridgeStoreStateContext StoreContext(MyActor);
    FMaterialBridgeStoreStateOptions StoreOptions;
    StoreOptions.MaterialBridgeRegistry = &Registry;

    bool bStored = Bridge->StoreState(StoreContext, &ContainerState, StoreOptions);
    check(bStored);

    // 第三步：替换材质
    FMaterialBridgeWriteSlotContext WriteContext(MyActor);
    FMaterialBridgeWriteSlotOptions WriteOptions;
    WriteOptions.MaterialBridgeRegistry = &Registry;

    Bridge->AccessSlots(WriteContext,
        [&TempMaterial](const FMaterialBridgeWriteSlotContext& Context, FMaterialBridgeWriteSlot& Slot) -> EControlFlow
        {
            Slot.SetMaterial(TempMaterial);
            return EControlFlow::Continue;
        },
        WriteOptions);

    // ... 在某个时机恢复 ...

    // 第四步：恢复原始材质状态
    FMaterialBridgeApplyStateContext ApplyContext(MyActor);
    FMaterialBridgeApplyStateOptions ApplyOptions;
    ApplyOptions.MaterialBridgeRegistry = &Registry;

    Bridge->ApplyState(ApplyContext, ContainerState, ApplyOptions);
}
```

### 进阶用法：材质 Shader 渐进式缓存

```cpp
// 分帧缓存材质 Shader，避免单帧卡顿
// 来源: Internal/MaterialCache/AvaMaterialCacheHelper.h, Internal/MaterialCache/AvaMaterialCacheSettings.h

#include "Internal/MaterialCache/AvaMaterialCacheHelper.h"
#include "Internal/MaterialCache/AvaMaterialCacheSettings.h"

using namespace UE::Ava;

// 在场景加载时请求缓存所有 Actor 的材质
FMaterialCacheHelper& CacheHelper = FMaterialCacheHelper::Get();

for (AActor* Actor : AllActors)
{
    // 使用默认 Shader Profile（由 UAvaMaterialCacheSettings 配置）
    CacheHelper.RequestCacheMaterials(Actor);
}

// 每帧调用 Tick() 以处理缓存（通常由模块自动管理）
// CacheHelper.Tick();

// 检查缓存状态
if (CacheHelper.IsCaching())
{
    UE_LOG(LogTemp, Log, TEXT("Still caching materials..."));
}

// 检查特定对象的缓存状态
if (CacheHelper.IsCaching(MyActor))
{
    UE_LOG(LogTemp, Log, TEXT("MyActor materials still caching..."));
}
```

### 进阶用法：自定义 Material Bridge

```cpp
// 继承 FMaterialBridge 为自定义组件创建桥接
// 来源: Public/MaterialBridge/AvaMaterialBridge.h, Public/MaterialBridge/AvaMaterialBridgeRegistry.h

#include "MaterialBridge/AvaMaterialBridge.h"

// 自定义容器状态
USTRUCT()
struct FMyComponentMaterialContainerState : public FAvaMaterialContainerState
{
    GENERATED_BODY()

    UPROPERTY()
    TArray<TObjectPtr<UMaterialInterface>> Materials;
};

// 自定义桥接实现
class FMyComponentMaterialBridge : public UE::Ava::FMaterialBridge
{
    using FContainerState = FMyComponentMaterialContainerState;

protected:
    virtual const UStruct* OnGetBridgedType() const override
    {
        return UMyComponent::StaticClass();
    }

    virtual EControlFlow OnAccessSlots(
        const FReadSlotContext& InContext,
        TFunctionRef<EControlFlow(const FReadSlotContext&, const FReadSlot&)> InFunc,
        const FReadSlotOptions& InOptions) const override
    {
        // 实现自定义的材质槽读取逻辑
        return EControlFlow::Continue;
    }

    // ... 其他虚函数实现 ...
};

// 注册自定义桥接
// 通常在模块启动时调用
UE::Ava::FMaterialBridgeRegistry& MutableRegistry = UE::Ava::FMaterialBridgeRegistry::GetMutable();
MutableRegistry.Register<FMyComponentMaterialBridge>(/* Priority */ 10);
```

---

## Demo 示例

以下是一个完整的最小示例，演示如何创建自定义 Material Bridge 并注册到全局注册表中：

**MyCustomMaterialBridge.h**

```cpp
#pragma once

#include "MaterialBridge/AvaMaterialBridge.h"
#include "MaterialBridge/AvaMaterialContainerState.h"
#include "MaterialBridge/AvaMaterialBridgeRegistry.h"
#include "MaterialBridge/Context/AvaMaterialBridgeContext.h"

class UMyCustomMaterialContainer;

/** 自定义容器状态，保存原始材质列表 */
USTRUCT()
struct FMyCustomContainerState : public FAvaMaterialContainerState
{
    GENERATED_BODY()

    UPROPERTY()
    TArray<TObjectPtr<UMaterialInterface>> OriginalMaterials;
};

/** 自定义 Material Bridge：为 UMyCustomMaterialContainer 提供材质桥接 */
class FMyCustomMaterialBridge : public UE::Ava::FMaterialBridge
{
public:
    using FContainerState = FMyCustomContainerState;

protected:
    //~ Begin FMaterialBridge
    virtual const UStruct* OnGetBridgedType() const override;
    virtual EControlFlow OnAccessSlots(
        const FReadSlotContext& InContext,
        TFunctionRef<EControlFlow(const FReadSlotContext&, const FReadSlot&)> InFunc,
        const FReadSlotOptions& InOptions) const override;
    virtual EControlFlow OnAccessSlots(
        const FWriteSlotContext& InContext,
        TFunctionRef<EControlFlow(const FWriteSlotContext&, FWriteSlot&)> InFunc,
        const FWriteSlotOptions& InOptions) const override;
    virtual TSubScriptStructOf<FAvaMaterialContainerState> OnGetContainerStateType() const override;
    virtual void OnApplyState(
        const FApplyStateContext& InContext,
        TConstStructView<FAvaMaterialContainerState> InContainerState,
        const FApplyStateOptions& InOptions) const override;
    virtual void OnStoreState(
        const FStoreStateContext& InContext,
        TStructView<FAvaMaterialContainerState> InContainerState,
        const FStoreStateOptions& InOptions) const override;
    //~ End FMaterialBridge
};
```

**MyCustomMaterialBridge.cpp**

```cpp
#include "MyCustomMaterialBridge.h"
#include "MyCustomMaterialContainer.h"
#include "MaterialBridge/AvaMaterialBridgeSlotId.h"
#include "MaterialBridge/Slot/AvaMaterialBridgeReadSlot.h"
#include "MaterialBridge/Slot/AvaMaterialBridgeWriteSlot.h"

const UStruct* FMyCustomMaterialBridge::OnGetBridgedType() const
{
    return UMyCustomMaterialContainer::StaticClass();
}

EControlFlow FMyCustomMaterialBridge::OnAccessSlots(
    const FReadSlotContext& InContext,
    TFunctionRef<EControlFlow(const FReadSlotContext&, const FReadSlot&)> InFunc,
    const FReadSlotOptions& InOptions) const
{
    const UMyCustomMaterialContainer* Container = Cast<UMyCustomMaterialContainer>(
        InContext.GetMaterialContainerObject());
    if (!Container)
    {
        return EControlFlow::Continue;
    }

    for (int32 i = 0; i < Container->GetMaterialSlotCount(); ++i)
    {
        FMaterialBridgeReadSlot Slot(Container->GetMaterial(i), FAvaMaterialBridgeSlotId(i));
        EControlFlow Result = InFunc(InContext, Slot);
        if (Result == EControlFlow::Break)
        {
            return EControlFlow::Break;
        }
    }
    return EControlFlow::Continue;
}

EControlFlow FMyCustomMaterialBridge::OnAccessSlots(
    const FWriteSlotContext& InContext,
    TFunctionRef<EControlFlow(const FWriteSlotContext&, FWriteSlot&)> InFunc,
    const FWriteSlotOptions& InOptions) const
{
    UMyCustomMaterialContainer* Container = Cast<UMyCustomMaterialContainer>(
        InContext.GetMaterialContainerObject());
    if (!Container)
    {
        return EControlFlow::Continue;
    }

    for (int32 i = 0; i < Container->GetMaterialSlotCount(); ++i)
    {
        FMaterialBridgeWriteSlot Slot(Container->GetMaterial(i), FAvaMaterialBridgeSlotId(i));
        EControlFlow Result = InFunc(InContext, Slot);
        if (Slot.GetMaterial() != Container->GetMaterial(i))
        {
            Container->SetMaterial(i, Slot.GetMaterial());
        }
        if (Result == EControlFlow::Break)
        {
            return EControlFlow::Break;
        }
    }
    return EControlFlow::Continue;
}

TSubScriptStructOf<FAvaMaterialContainerState> FMyCustomMaterialBridge::OnGetContainerStateType() const
{
    return FMyCustomContainerState::StaticStruct();
}

void FMyCustomMaterialBridge::OnStoreState(
    const FStoreStateContext& InContext,
    TStructView<FAvaMaterialContainerState> InContainerState,
    const FStoreStateOptions& InOptions) const
{
    FMyCustomContainerState& State = InContainerState.Get<FMyCustomContainerState>();
    const UMyCustomMaterialContainer* Container = Cast<UMyCustomMaterialContainer>(
        InContext.GetMaterialContainerObject());
    if (!Container)
    {
        return;
    }

    State.OriginalMaterials.Reset();
    for (int32 i = 0; i < Container->GetMaterialSlotCount(); ++i)
    {
        State.OriginalMaterials.Add(Container->GetMaterial(i));
    }
}

void FMyCustomMaterialBridge::OnApplyState(
    const FApplyStateContext& InContext,
    TConstStructView<FAvaMaterialContainerState> InContainerState,
    const FApplyStateOptions& InOptions) const
{
    const FMyCustomContainerState& State = InContainerState.Get<FMyCustomContainerState>();
    UMyCustomMaterialContainer* Container = Cast<UMyCustomMaterialContainer>(
        InContext.GetMaterialContainerObject());
    if (!Container)
    {
        return;
    }

    for (int32 i = 0; i < State.OriginalMaterials.Num(); ++i)
    {
        Container->SetMaterial(i, State.OriginalMaterials[i]);
    }
}

// 注册（通常在你的模块 StartupModule 中调用）
void RegisterMyCustomBridge()
{
    UE::Ava::FMaterialBridgeRegistry::GetMutable().Register<FMyCustomMaterialBridge>(
        /* Priority */ 100);
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | — |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 的场景设置和大纲面板移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在 Rundown 页面设置中添加 MRQ 分析统计 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中添加页面加载选项 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加项目设置以强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/解除关联的通知机制 |

### 维护评价

**状态：活跃维护**

- **创建时间**：2025-05-09 从 Experimental 迁移至 VirtualProduction，约 1 年历史
- **更新频率**：非常活跃，最近一周内有多次提交，涉及功能增强和重构
- **维护团队**：Epic Games 官方维护，属于 Virtual Production / Motion Design 核心功能
- **注意**：AvalancheMaterial 本身是一个子模块，其最近提交多为上层 Motion Design 功能变更；材质桥接系统架构稳定，属于基础设施层
- **推荐**：✅ 如果你在做虚拟制作/Motion Design 相关的材质操作，这是官方推荐的统一材质访问方案

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheMaterial)
- [插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/en-US/animation/motion-design-in-unreal-engine/)