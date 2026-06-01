# Avalanche Material

> Compositing, designer and broadcasting tool.
Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 材质桥接模块 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheMaterial` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheMaterial) | |

## 用途

AvalancheMaterial 模块为 Motion Design（Avalanche）插件提供**统一的材质访问抽象层**。它解决的核心问题是：Motion Design 系统需要以统一方式操作不同类型的材质容器（Actor、PrimitiveComponent、DecalComponent、StaticMesh、Level 等），而这些容器各自拥有不同的材质 API。

具体而言，该模块提供两大功能：

1. **材质桥接（Material Bridge）**：通过策略模式，为不同类型的材质容器提供统一的读/写接口。系统可以透明地遍历任意对象的材质槽、替换材质、以及保存/恢复材质容器状态（例如临时更换材质后回滚）。

2. **材质缓存（Material Cache）**：跨帧异步缓存材质及其着色器，支持配置不同的着色器缓存策略（通用型 / 指定型 / 跳过），确保在实时播放或离线预加载场景时着色器已编译完成，避免运行时卡顿。

## 使用场景

- 你需要在 Motion Design 编辑器中为场景中的各类物体（网格体、贴花、静态网格等）统一替换材质 → 使用 Material Bridge API
- 你需要临时修改某 Actor 的材质后能快速回滚到原始状态 → 使用 Material Bridge 的 StoreState/ApplyState 流程
- 你需要在关卡加载或节目播放前预先编译材质着色器 → 使用 Material Cache Helper 和 Shader Profile 配置
- 你需要为自定义的材质容器类型接入 Motion Design 的材质系统 → 继承 FMaterialBridge 并注册到 Material Bridge Registry

## 蓝图用法

本模块主要面向 C++ 使用，公有 API 中未暴露 `BlueprintCallable` 或 `BlueprintReadWrite` 接口。材质缓存设置（`UAvaMaterialCacheSettings`）可在编辑器的项目设置面板中通过 UI 配置。

### 编辑器配置节点

在 **Project Settings → Material Cache Settings** 中可配置以下内容：

| 设置项 | 说明 |
|---|---|
| Realtime Profile | 实时播放（如关卡运行）时使用的着色器缓存配置名 |
| Offline Profile | 离线场景（如预加载关卡）时使用的着色器缓存配置名 |
| Shader Profiles | 着色器配置列表，可定义具体的顶点工厂/管线/着色器类型组合 |

## C++ 用法

### 头文件引入

```cpp
// 材质桥接核心
#include "MaterialBridge/AvaMaterialBridge.h"
#include "MaterialBridge/AvaMaterialBridgeRegistry.h"

// 材质桥接上下文
#include "MaterialBridge/Context/AvaMaterialBridgeReadSlotContext.h"
#include "MaterialBridge/Context/AvaMaterialBridgeWriteSlotContext.h"
#include "MaterialBridge/Context/AvaMaterialBridgeApplyStateContext.h"
#include "MaterialBridge/Context/AvaMaterialBridgeStoreStateContext.h"

// 材质缓存
#include "MaterialCache/AvaMaterialCacheHelper.h"
#include "MaterialCache/AvaMaterialCacheSettings.h"
```

### 基本用法 — 读取材质槽

遍历一个对象的所有材质槽并读取材质：

```cpp
// 来源: Public/MaterialBridge/AvaMaterialBridge.h + Context 头文件

using namespace UE::Ava;

// 获取材质桥接注册表并查找适合的桥接
const FMaterialBridgeRegistry& Registry = FMaterialBridgeRegistry::Get();
const FMaterialBridge* Bridge = Registry.GetMaterialBridge(FConstDataView(MyObject));
if (!Bridge)
{
    return;
}

// 构建读取上下文（传入材质容器对象）
FMaterialBridgeReadSlotOptions ReadOptions;
FMaterialBridgeReadSlotContext ReadContext(FConstDataView(MyObject));

// 遍历所有材质槽
Bridge->AccessSlots(ReadContext, [](const FMaterialBridgeReadSlotContext& InContext, const FMaterialBridgeReadSlot& InSlot)
    -> EControlFlow
{
    UMaterialInterface* Material = InSlot.GetMaterial();
    const FAvaMaterialBridgeSlotId& SlotId = InSlot.GetSlotId();

    UE_LOG(LogTemp, Log, TEXT("Slot '%s' (Index: %d): %s"),
        *SlotId.GetName().ToString(),
        SlotId.GetIndex(),
        Material ? *Material->GetName() : TEXT("None"));

    return EControlFlow::Continue;
}, ReadOptions);
```

### 基本用法 — 替换材质

```cpp
using namespace UE::Ava;

const FMaterialBridgeRegistry& Registry = FMaterialBridgeRegistry::Get();
const FMaterialBridge* Bridge = Registry.GetMaterialBridge(FConstDataView(MyObject));
if (!Bridge)
{
    return;
}

// 构建写入上下文
FMaterialBridgeWriteSlotOptions WriteOptions;
FMaterialBridgeWriteSlotContext WriteContext(MyObject);

// 替换所有材质槽的材质
Bridge->AccessSlots(WriteContext, [NewMaterial](const FMaterialBridgeWriteSlotContext& InContext, FMaterialBridgeWriteSlot& InSlot)
    -> EControlFlow
{
    InSlot.SetMaterial(NewMaterial);
    return EControlFlow::Continue;
}, WriteOptions);
```

### 基本用法 — 保存与恢复材质状态

材质桥接的核心设计模式：先保存状态 → 修改材质 → 需要时恢复：

```cpp
using namespace UE::Ava;

const FMaterialBridgeRegistry& Registry = FMaterialBridgeRegistry::Get();
const FMaterialBridge* Bridge = Registry.GetMaterialBridge(FConstDataView(MyObject));

// 第一步：保存当前材质容器状态
TInstancedStruct<FAvaMaterialContainerState> ContainerState;
if (Bridge->CanCreateContainerState())
{
    ContainerState = Bridge->CreateContainerState();

    FMaterialBridgeStoreStateOptions StoreOptions;
    FMaterialBridgeStoreStateContext StoreContext(MyObject);
    Bridge->StoreState(StoreContext, &ContainerState, StoreOptions);
}

// 第二步：替换材质（使用之前的写入代码）
// ... (略)

// 第三步：恢复到原始状态
FMaterialBridgeApplyStateOptions ApplyOptions;
FMaterialBridgeApplyStateContext ApplyContext(MyObject);
Bridge->ApplyState(ApplyContext, ContainerState, ApplyOptions);
```

### 进阶用法 — 注册自定义材质桥接

为自定义材质容器类型创建桥接：

```cpp
// 来源: Public/MaterialBridge/AvaMaterialBridgeRegistry.h

#include "MaterialBridge/AvaMaterialBridge.h"
#include "MaterialBridge/AvaMaterialBridgeRegistry.h"

// 定义自定义材质容器状态
USTRUCT()
struct FMyCustomMaterialContainerState : public FAvaMaterialContainerState
{
    GENERATED_BODY()

    UPROPERTY()
    TArray<TObjectPtr<UMaterialInterface>> Materials;
};

// 实现自定义桥接
class FMyCustomMaterialBridge : public FMaterialBridge
{
public:
    using FContainerState = FMyCustomMaterialContainerState;

protected:
    virtual const UStruct* OnGetBridgedType() const override
    {
        return UMyCustomComponent::StaticClass();
    }

    virtual EControlFlow OnAccessSlots(
        const FReadSlotContext& InContext,
        TFunctionRef<EControlFlow(const FReadSlotContext&, const FReadSlot&)> InFunc,
        const FReadSlotOptions& InOptions) const override
    {
        // 遍历自定义组件的材质槽
        // ...
        return EControlFlow::Continue;
    }

    virtual EControlFlow OnAccessSlots(
        const FWriteSlotContext& InContext,
        TFunctionRef<EControlFlow(const FWriteSlotContext&, FWriteSlot&)> InFunc,
        const FWriteSlotOptions& InOptions) const override
    {
        // 写入自定义组件的材质槽
        // ...
        return EControlFlow::Continue;
    }

    virtual TSubScriptStructOf<FAvaMaterialContainerState> OnGetContainerStateType() const override
    {
        return FMyCustomMaterialContainerState::StaticStruct();
    }
};

// 在模块启动时注册
void FMyModule::StartupModule()
{
    FMaterialBridgeRegistry::GetMutable().Register<FMyCustomMaterialBridge>(
        /*Priority=*/100);
}
```

### 进阶用法 — 材质缓存与着色器预编译

```cpp
// 来源: Internal/MaterialCache/AvaMaterialCacheHelper.h

#include "MaterialCache/AvaMaterialCacheHelper.h"
#include "MaterialCache/AvaMaterialCacheSettings.h"

using namespace UE::Ava;

// 请求缓存某个对象的材质（使用默认着色器配置）
FMaterialCacheHelper::Get().RequestCacheMaterials(MyActor);

// 使用指定的着色器配置文件
const UAvaMaterialCacheSettings* Settings = GetDefault<UAvaMaterialCacheSettings>();
FName ProfileName = Settings->GetRealtimeProfile();
FMaterialCacheHelper::Get().RequestCacheMaterials(MyActor, ProfileName);

// 每帧调用 Tick() 以异步推进缓存进度
void MyManager::Tick(float DeltaTime)
{
    FMaterialCacheHelper::Get().Tick();
}

// 检查是否还有材质正在缓存中
if (FMaterialCacheHelper::Get().IsCaching())
{
    // 还在编译着色器...
}

// 检查特定对象是否仍在缓存
if (FMaterialCacheHelper::Get().IsCaching(MyActor))
{
    // 该对象的材质还在编译...
}

// 调试：输出所有仍在处理中的材质到日志
FMaterialCacheHelper::Get().DumpMaterials();
```

### 进阶用法 — 请求材质槽特性（Feature）

通过 `RequestFeature` 为材质槽配置额外属性：

```cpp
// 来源: Public/MaterialBridge/Slot/CommonFeatures/AvaMaterialBridgeBlendModeFeature.h

// 在写入上下文中请求混合模式特性
Bridge->AccessSlots(WriteContext, [](const FMaterialBridgeWriteSlotContext& InContext, FMaterialBridgeWriteSlot& InSlot)
    -> EControlFlow
{
    // 先设置材质
    InSlot.SetMaterial(MyMaterial);

    // 请求设置混合模式为半透明
    FAvaMaterialBridgeBlendModeFeature BlendFeature;
    BlendFeature.BlendMode = BLEND_Translucent;
    InSlot.RequestFeature(BlendFeature);

    return EControlFlow::Continue;
}, WriteOptions);
```

## Demo 示例

### 自定义材质桥接完整示例

```cpp
// MyCustomMaterialBridge.h
#pragma once

#include "MaterialBridge/AvaMaterialBridge.h"
#include "MaterialBridge/AvaMaterialContainerState.h"
#include "Components/ActorComponent.h"

// 自定义组件：拥有一个材质列表
UCLASS()
class UMyMaterialComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY()
    TArray<TObjectPtr<UMaterialInterface>> Materials;
};

// 材质容器状态
USTRUCT()
struct FMyComponentMaterialState : public FAvaMaterialContainerState
{
    GENERATED_BODY()

    UPROPERTY()
    TArray<TObjectPtr<UMaterialInterface>> SavedMaterials;
};

// 自定义材质桥接
class FMyComponentMaterialBridge : public UE::Ava::FMaterialBridge
{
protected:
    virtual const UStruct* OnGetBridgedType() const override;
    virtual EControlFlow OnAccessSlots(
        const UE::Ava::FReadSlotContext& InContext,
        TFunctionRef<EControlFlow(const UE::Ava::FReadSlotContext&, const UE::Ava::FReadSlot&)> InFunc,
        const UE::Ava::FReadSlotOptions& InOptions) const override;
    virtual EControlFlow OnAccessSlots(
        const UE::Ava::FWriteSlotContext& InContext,
        TFunctionRef<EControlFlow(const UE::Ava::FWriteSlotContext&, UE::Ava::FWriteSlot&)> InFunc,
        const UE::Ava::FWriteSlotOptions& InOptions) const override;
    virtual TSubScriptStructOf<FAvaMaterialContainerState> OnGetContainerStateType() const override;
    virtual void OnApplyState(
        const UE::Ava::FApplyStateContext& InContext,
        TConstStructView<FAvaMaterialContainerState> InContainerState,
        const UE::Ava::FApplyStateOptions& InOptions) const override;
    virtual void OnStoreState(
        const UE::Ava::FStoreStateContext& InContext,
        TStructView<FAvaMaterialContainerState> InContainerState,
        const UE::Ava::FStoreStateOptions& InOptions) const override;
};
```

```cpp
// MyCustomMaterialBridge.cpp
#include "MyCustomMaterialBridge.h"

#include "MaterialBridge/Context/AvaMaterialBridgeReadSlotContext.h"
#include "MaterialBridge/Context/AvaMaterialBridgeWriteSlotContext.h"
#include "MaterialBridge/Context/AvaMaterialBridgeApplyStateContext.h"
#include "MaterialBridge/Context/AvaMaterialBridgeStoreStateContext.h"
#include "MaterialBridge/Slot/AvaMaterialBridgeReadSlot.h"
#include "MaterialBridge/Slot/AvaMaterialBridgeWriteSlot.h"
#include "MaterialBridge/Slot/AvaMaterialBridgeSlotId.h"

using namespace UE::Ava;

const UStruct* FMyComponentMaterialBridge::OnGetBridgedType() const
{
    return UMyMaterialComponent::StaticClass();
}

EControlFlow FMyComponentMaterialBridge::OnAccessSlots(
    const FReadSlotContext& InContext,
    TFunctionRef<EControlFlow(const FReadSlotContext&, const FReadSlot&)> InFunc,
    const FReadSlotOptions& InOptions) const
{
    const UObject* Obj = InContext.GetMaterialContainerObject();
    const UMyMaterialComponent* Comp = Cast<UMyMaterialComponent>(Obj);
    if (!Comp)
    {
        return EControlFlow::Continue;
    }

    for (int32 i = 0; i < Comp->Materials.Num(); ++i)
    {
        FMaterialBridgeReadSlot Slot(Comp->Materials[i], FAvaMaterialBridgeSlotId(i));
        EControlFlow Result = InFunc(InContext, Slot);
        if (Result == EControlFlow::Break)
        {
            break;
        }
    }
    return EControlFlow::Continue;
}

EControlFlow FMyComponentMaterialBridge::OnAccessSlots(
    const FWriteSlotContext& InContext,
    TFunctionRef<EControlFlow(const FWriteSlotContext&, FWriteSlot&)> InFunc,
    const FWriteSlotOptions& InOptions) const
{
    UObject* Obj = InContext.GetMaterialContainerObject();
    UMyMaterialComponent* Comp = Cast<UMyMaterialComponent>(Obj);
    if (!Comp)
    {
        return EControlFlow::Continue;
    }

    for (int32 i = 0; i < Comp->Materials.Num(); ++i)
    {
        FMaterialBridgeWriteSlot Slot(Comp->Materials[i], FAvaMaterialBridgeSlotId(i));
        EControlFlow Result = InFunc(InContext, Slot);
        if (Result == EControlFlow::Break)
        {
            break;
        }
    }
    return EControlFlow::Continue;
}

TSubScriptStructOf<FAvaMaterialContainerState> FMyComponentMaterialBridge::OnGetContainerStateType() const
{
    return FMyComponentMaterialState::StaticStruct();
}

void FMyComponentMaterialBridge::OnApplyState(
    const FApplyStateContext& InContext,
    TConstStructView<FAvaMaterialContainerState> InContainerState,
    const FApplyStateOptions& InOptions) const
{
    UObject* Obj = InContext.GetMaterialContainerObject();
    UMyMaterialComponent* Comp = Cast<UMyMaterialComponent>(Obj);
    const FMyComponentMaterialState* State = InContainerState.GetPtr<FMyComponentMaterialState>();
    if (Comp && State)
    {
        Comp->Materials = State->SavedMaterials;
    }
}

void FMyComponentMaterialBridge::OnStoreState(
    const FStoreStateContext& InContext,
    TStructView<FAvaMaterialContainerState> InContainerState,
    const FStoreStateOptions& InOptions) const
{
    const UObject* Obj = InContext.GetMaterialContainerObject();
    const UMyMaterialComponent* Comp = Cast<UMyMaterialComponent>(Obj);
    FMyComponentMaterialState* State = InContainerState.GetMutablePtr<FMyComponentMaterialState>();
    if (Comp && State)
    {
        State->SavedMaterials = Comp->Materials;
    }
}
```

## 模块依赖

从 Build.cs 和头文件推断的依赖关系。无特殊依赖（仅标准 Core/Engine/Slate 等常见模块）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将 Motion Design 的场景设置和大纲面板移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用节目单页面设置时新增 MRQ 分析统计 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and added | 在节目控制工具栏中新增页面加载选项（全部/下一个/选中） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置以强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport | 重构视口关联/解耦时的客户端通知逻辑 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2025-05-09，从 Experimental 迁移到 VirtualProduction，约 1 年历史
- **更新频率**：非常活跃，最近一周内有多次实质性功能更新（截至 2026-05-20）
- **成熟度**：虽然从 Experimental 升级，但作为 Motion Design（Avalanche）的核心子模块，已作为正式插件发布
- **模块规模**：2060 个源文件的整体插件中，AvalancheMaterial 聚焦于材质桥接和缓存，设计清晰
- **推荐程度**：强烈推荐在 Motion Design / Virtual Production 场景中使用。Material Bridge 模式为不同类型的材质容器提供了优雅的统一抽象，材质缓存系统有效解决了着色器编译卡顿问题

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheMaterial)
- [Avalanche 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)