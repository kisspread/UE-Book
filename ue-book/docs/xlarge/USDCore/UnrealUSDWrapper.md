# USD Core

> Adds support for USD SDK, UE wrapper classes and USD conversion utilities

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD SDK 包装器、转换工具） |
| 模块 | `UnrealUSDWrapper` (Runtime), `USDClasses` (Runtime), `USDUtilities` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-16 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/USDCore) | |

## 用途

USDCore 是 Unreal Engine 与 Pixar USD (Universal Scene Description) SDK 之间的**核心桥接层**。它解决了以下关键问题：

1. **RTTI 兼容性**：USD SDK 依赖 C++ RTTI，但 UE 的许多模块禁用了 RTTI。USDCore 通过 Pimpl（指向实现的指针）模式包装所有 USD 类型，使得无 RTTI 模块也能安全使用 USD 功能。
2. **内存分配冲突**：USD SDK 使用 C 运行时分配器，而 UE 覆盖了 `new`/`delete`。USDCore 提供了 `FUsdMemoryManager` 和 `TScopedAllocs` 机制，在 UE 分配器和系统分配器之间正确切换，避免跨分配器释放导致的崩溃。
3. **API 统一**：将 USD SDK 的 C++ API 包装为 UE 风格的类（`FUsdStage`、`FUsdPrim`、`FSdfLayer` 等），提供一致的命名约定和生命周期管理。

该插件**默认禁用**且标记为**实验性**，表明 Epic 仍在积极开发中，API 可能发生变化。

## 使用场景

- 你需要在 UE 中**导入/导出 USD 文件**（.usd、.usda、.usdc）→ 使用 USDCore 提供的 Stage 和 Layer 操作
- 你需要**程序化创建或修改 USD 场景层级** → 使用 `FUsdPrim`、`FUsdAttribute` 等包装器
- 你需要**监听 USD 场景变化** → 使用 `FUsdListener` 注册变更通知
- 你需要处理 **USD 骨骼动画**（UsdSkel）→ 使用 `FUsdSkelCache`、`FUsdSkelSkeletonQuery` 等
- 你需要在**无 RTTI 模块**中操作 USD 数据 → 这正是 USDCore 存在的核心原因

## 模块概览

本插件包含三个模块，形成分层架构：

| 模块 | 类型 | 职责 |
|---|---|---|
| **UnrealUSDWrapper** | Runtime | 底层 USD SDK 包装器，提供 Pimpl 封装的 USD 类型 |
| **USDClasses** | Runtime | UE 资产类型和高级 USD 转换类 |
| **USDUtilities** | Runtime | USD 转换工具函数和辅助功能 |

## UnrealUSDWrapper 模块详解

### 核心设计理念

所有包装类遵循统一模式：

```cpp
class FUsdXxx final
{
public:
    // 构造/拷贝/移动
    FUsdXxx();
    FUsdXxx(const FUsdXxx& Other);
    FUsdXxx(FUsdXxx&& Other);
    ~FUsdXxx();

    // 显式 bool 转换（有效性检查）
    explicit operator bool() const;

    // 与 pxr:: 类型的双向转换
    explicit FUsdXxx(const pxr::UsdXxx& InType);
    operator pxr::UsdXxx&();
    operator const pxr::UsdXxx&() const;

    // 包装的 USD SDK 函数
    // ...

private:
    TUniquePtr<Internal::FUsdXxxImpl> Impl;  // Pimpl 隐藏 USD 类型
};
```

### 类型层次结构

```
FUsdStage / FUsdStageWeak          ← pxr::UsdStageRefPtr / WeakPtr
├── FUsdPrim                        ← pxr::UsdPrim
│   ├── FUsdAttribute               ← pxr::UsdAttribute
│   ├── FUsdRelationship            ← pxr::UsdRelationship
│   ├── FUsdReferences              ← pxr::UsdReferences
│   ├── FUsdPayloads                ← pxr::UsdPayloads
│   └── FUsdVariantSets             ← pxr::UsdVariantSets
│       └── FUsdVariantSet          ← pxr::UsdVariantSet
│
├── FUsdTyped (基类)                ← pxr::UsdTyped
│   ├── FUsdGeomXformable           ← pxr::UsdGeomXformable
│   ├── FUsdGeomSubset              ← pxr::UsdGeomSubset
│   └── FUsdSkelBlendShape          ← pxr::UsdSkelBlendShape
│
├── FUsdSkelCache                   ← pxr::UsdSkelCache
│   ├── FUsdSkelSkeletonQuery       ← pxr::UsdSkelSkeletonQuery
│   ├── FUsdSkelAnimQuery           ← pxr::UsdSkelAnimQuery
│   ├── FUsdSkelSkinningQuery       ← pxr::UsdSkelSkinningQuery
│   ├── FUsdSkelBlendShapeQuery     ← pxr::UsdSkelBlendShapeQuery
│   └── FUsdSkelBinding             ← pxr::UsdSkelBinding
│
├── FSdfLayer / FSdfLayerWeak       ← pxr::SdfLayerRefPtr / WeakPtr
│   ├── FSdfPrimSpec                ← pxr::SdfPrimSpecHandle
│   └── FSdfAttributeSpec           ← pxr::SdfAttributeSpecHandle
│
├── FSdfPath                        ← pxr::SdfPath
├── FVtValue                        ← pxr::VtValue
├── FUsdGeomBBoxCache               ← pxr::UsdGeomBBoxCache（线程安全）
│
└── Pcp 层（Prim Composition）
    ├── FPcpPrimIndex               ← pxr::PcpPrimIndex
    ├── FPcpNodeRef                 ← pxr::PcpNodeRef
    ├── FPcpLayerStack              ← pxr::PcpLayerStackRefPtr
    └── FPcpMapExpression           ← pxr::PcpMapExpression
```

### 内存管理

USDCore 的内存管理是理解该插件的关键。USD SDK 使用 C 运行时分配器，而 UE 覆盖了全局 `new`/`delete`。当 USD 对象在 UE 上下文中被释放时，会导致分配器不匹配崩溃。

**解决方案**：

```cpp
#include "USDMemory.h"

// 在操作 USD 对象时，必须使用作用域分配器
{
    FScopedUsdAllocs UsdAllocs;  // 切换到系统分配器
    std::vector<UsdAttribute> Attributes = Prim.GetAttributes();
    // 在此作用域内，所有 new/delete 使用系统分配器
}

// 对于需要跨作用域保存的 USD 对象，使用 TUsdStore
TUsdStore<pxr::UsdPrim> RootPrim = UsdStage->GetPseudoRoot();
```

**关键类**：

| 类 | 说明 |
|---|---|
| `FUsdMemoryManager` | 管理每线程的分配器栈 |
| `FScopedUsdAllocs` | 作用域内使用系统分配器（用于 USD 对象） |
| `FScopedUnrealAllocs` | 作用域内使用 UE 分配器（在 USD 作用域内需要 UE 对象时） |
| `TUsdStore<T>` | 跨作用域安全持有 USD 对象的容器 |

### 变更监听

`FUsdListener` 提供 USD 场景变更的事件通知：

```cpp
#include "USDListener.h"

// 注册监听器
FUsdListener Listener;
Listener.Register(UsdStage);

// 监听变更事件
Listener.OnUsdObjectChanged.AddLambda([](const UsdUtils::FObjectChangesByPath& Changes)
{
    for (const auto& [Path, Entries] : Changes)
    {
        for (const auto& Entry : Entries)
        {
            if (Entry.Flags.bDidAddNonInertPrim)
            {
                // 新增 Prim
            }
            if (Entry.Flags.bDidChangeAttributeTimeSamples)
            {
                // 属性时间采样变化
            }
        }
    }
});
```

**变更标志**（`FPrimChangeFlags`）：

| 标志 | 说明 |
|---|---|
| `bDidAddNonInertPrim` | 添加了实质 Prim |
| `bDidRemoveNonInertPrim` | 移除了实质 Prim |
| `bDidChangeAttributeTimeSamples` | 属性时间采样变化 |
| `bDidChangePrimReferences` | Prim 引用变化 |
| `bDidReorderChildren` | 子节点重排序 |
| `bDidRename` | 对象重命名 |

## C++ 用法

### 头文件引入

```cpp
// USD 包装器核心
#include "UnrealUSDWrapper.h"
#include "UsdWrappers/UsdStage.h"
#include "UsdWrappers/UsdPrim.h"
#include "UsdWrappers/UsdAttribute.h"
#include "UsdWrappers/SdfLayer.h"
#include "UsdWrappers/SdfPath.h"
#include "UsdWrappers/VtValue.h"

// 内存管理（必须）
#include "USDMemory.h"

// 变更监听
#include "USDListener.h"
```

### 基本用法：打开 Stage 并遍历 Prim

```cpp
#include "UsdWrappers/UsdStage.h"
#include "UsdWrappers/UsdPrim.h"
#include "UsdWrappers/SdfPath.h"
#include "USDMemory.h"

void OpenAndTraverseUSD(const FString& FilePath)
{
    // 打开 USD Stage
    FScopedUsdAllocs UsdAllocs;
    
    UE::FUsdStage Stage = UE::FUsdStage::Open(*FilePath);
    if (!Stage)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open USD stage: %s"), *FilePath);
        return;
    }

    // 获取默认 Prim
    UE::FUsdPrim DefaultPrim = Stage.GetDefaultPrim();
    if (DefaultPrim)
    {
        UE_LOG(LogTemp, Log, TEXT("Default prim: %s"), *DefaultPrim.GetName().ToString());
    }

    // 遍历所有子 Prim
    UE::FUsdPrim RootPrim = Stage.GetPseudoRoot();
    if (RootPrim)
    {
        TArray<UE::FUsdPrim> Children = RootPrim.GetAllChildren();
        for (const UE::FUsdPrim& Child : Children)
        {
            UE_LOG(LogTemp, Log, TEXT("Child: %s, Type: %s"),
                *Child.GetPath().GetString(),
                *Child.GetTypeName().ToString());
        }
    }
}
```

### 基本用法：读取属性值

```cpp
#include "UsdWrappers/UsdAttribute.h"
#include "UsdWrappers/VtValue.h"

void ReadAttribute(const UE::FUsdPrim& Prim)
{
    FScopedUsdAllocs UsdAllocs;

    // 获取属性
    UE::FUsdAttribute Attr = Prim.GetAttribute(TEXT("xformOp:translate"));
    if (!Attr)
    {
        return;
    }

    // 读取值
    UE::FVtValue Value;
    if (Attr.Get(Value))
    {
        FString TypeName = Value.GetTypeName();
        UE_LOG(LogTemp, Log, TEXT("Attribute type: %s"), *TypeName);
    }

    // 检查是否有时变数据
    TArray<double> TimeSamples;
    if (Attr.GetTimeSamples(TimeSamples))
    {
        UE_LOG(LogTemp, Log, TEXT("Has %d time samples"), TimeSamples.Num());
    }
}
```

### 进阶用法：骨骼动画查询

```cpp
#include "UsdWrappers/UsdSkelCache.h"
#include "UsdWrappers/UsdSkelSkeletonQuery.h"
#include "UsdWrappers/UsdSkelAnimQuery.h"
#include "UsdWrappers/UsdSkelSkinningQuery.h"

void QuerySkeletalAnimation(const UE::FUsdPrim& SkelRootPrim, double TimeCode)
{
    FScopedUsdAllocs UsdAllocs;

    // 创建并填充骨骼缓存
    UE::FUsdSkelCache SkelCache;
    SkelCache.Populate(SkelRootPrim, false);

    // 获取骨骼绑定
    TArray<UE::FUsdSkelBinding> Bindings;
    SkelCache.ComputeSkelBindings(SkelRootPrim, Bindings, false);

    for (const UE::FUsdSkelBinding& Binding : Bindings)
    {
        UE::FUsdPrim SkeletonPrim = Binding.GetSkeleton();
        if (!SkeletonPrim)
        {
            continue;
        }

        // 获取骨骼查询
        UE::FUsdSkelSkeletonQuery SkelQuery = SkelCache.GetSkelQuery(SkeletonPrim);
        if (!SkelQuery)
        {
            continue;
        }

        // 计算关节局部变换
        TArray<FTransform> JointTransforms;
        SkelQuery.ComputeJointLocalTransforms(JointTransforms, TimeCode);

        // 获取动画查询
        UE::FUsdSkelAnimQuery AnimQuery = SkelQuery.GetAnimQuery();
        if (AnimQuery)
        {
            TArray<FString> JointOrder = AnimQuery.GetJointOrder();
            UE_LOG(LogTemp, Log, TEXT("Skeleton has %d joints"), JointOrder.Num());
        }

        // 获取蒙皮目标
        TArray<UE::FUsdSkelSkinningQuery> SkinningTargets = Binding.GetSkinningTargets();
        for (const UE::FUsdSkelSkinningQuery& SkinningQuery : SkinningTargets)
        {
            FMatrix BindTransform = SkinningQuery.GetGeomBindTransform(TimeCode);
            // 处理蒙皮变换...
        }
    }
}
```

### 进阶用法：修改 USD 场景

```cpp
#include "UsdWrappers/UsdStage.h"
#include "UsdWrappers/UsdPrim.h"
#include "UsdWrappers/UsdAttribute.h"
#include "UsdWrappers/UsdReferences.h"
#include "UsdWrappers/UsdPayloads.h"
#include "UsdWrappers/UsdVariantSets.h"
#include "UsdWrappers/SdfLayer.h"
#include "UsdWrappers/UsdEditContext.h"

void ModifyUSDScene(const FString& FilePath)
{
    FScopedUsdAllocs UsdAllocs;

    UE::FUsdStage Stage = UE::FUsdStage::Open(*FilePath);
    if (!Stage)
    {
        return;
    }

    // 设置编辑目标
    UE::FSdfLayer RootLayer = Stage.GetRootLayer();
    Stage.SetEditTarget(RootLayer);

    // 使用编辑上下文
    {
        UE::FUsdEditContext EditCtx(Stage, RootLayer);

        // 获取或创建 Prim
        UE::FUsdPrim Prim = Stage.GetPrimAtPath(UE::FSdfPath(TEXT("/MyPrim")));
        if (Prim)
        {
            // 添加引用
            UE::FUsdReferences Refs = Prim.GetReferences();
            Refs.AddReference(
                TEXT("OtherAsset.usd"),
                UE::FSdfPath(TEXT("/Root")),
                UE::FSdfLayerOffset(0.0, 1.0)
            );

            // 添加 Payload
            UE::FUsdPayloads Payloads = Prim.GetPayloads();
            Payloads.AddPayload(TEXT("HeavyAsset.usd"), UE::FSdfLayerOffset());

            // 操作变体集
            UE::FUsdVariantSets VarSets = Prim.GetVariantSets();
            TArray<FString> SetNames = VarSets.GetNames();
            for (const FString& SetName : SetNames)
            {
                UE::FUsdVariantSet VarSet = VarSets.GetVariantSet(SetName);
                TArray<FString> VarNames = VarSet.GetVariantNames();
                if (VarNames.Num() > 0)
                {
                    VarSet.SetVariantSelection(VarNames[0]);
                }
            }
        }
    }

    // 导出为扁平化文件
    Stage.Export(TEXT("C:/Output/Flattened.usda"), true);
}
```

### 进阶用法：SdfPath 操作

```cpp
#include "UsdWrappers/SdfPath.h"

void PathOperations()
{
    // 创建路径
    UE::FSdfPath RootPath = UE::FSdfPath::AbsoluteRootPath();
    UE::FSdfPath PrimPath(TEXT("/World/MyMesh"));

    // 路径查询
    bool bIsPrim = PrimPath.IsPrimPath();           // true
    bool bIsAbsolute = !PrimPath.IsEmpty();          // true
    FString Name = PrimPath.GetName();               // "MyMesh"

    // 路径构建
    UE::FSdfPath ChildPath = RootPath.AppendChild(TEXT("World"));
    UE::FSdfPath PropPath = PrimPath.AppendProperty(FName(TEXT("visibility")));

    // 路径关系
    UE::FSdfPath ParentPath = PrimPath.GetParentPath();  // "/World"
    bool bHasPrefix = PrimPath.HasPrefix(ChildPath);     // true

    // 相对/绝对路径转换
    UE::FSdfPath AbsPath = PrimPath.MakeAbsolutePath(RootPath);
    UE::FSdfPath RelPath = PrimPath.MakeRelativePath(ChildPath);

    // 获取所有前缀
    TArray<UE::FSdfPath> Prefixes = PrimPath.GetPrefixes();
    // ["/", "/World", "/World/MyMesh"]
}
```

## Demo 示例

### Build.cs 依赖配置

```csharp
// MyModule.Build.cs
using UnrealBuildTool;

public class MyModule : ModuleRules
{
    public MyModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "UnrealUSDWrapper"  // USD 包装器模块
        });

        // 如果需要 USDClasses 的高级功能
        // PrivateDependencyModuleNames.Add("USDClasses");

        // 如果需要转换工具函数
        // PrivateDependencyModuleNames.Add("USDUtilities");
    }
}
```

### 完整示例：USD Stage 检查器

```cpp
// UsdStageInspector.h
#pragma once

#include "CoreMinimal.h"

class FUsdStageInspector
{
public:
    /** 打开 USD 文件并打印场景信息 */
    static void InspectStage(const FString& UsdFilePath);

    /** 列出指定 Prim 的所有属性 */
    static void ListPrimAttributes(const FString& UsdFilePath, const FString& PrimPath);

    /** 检查骨骼信息 */
    static void InspectSkeleton(const FString& UsdFilePath);
};
```

```cpp
// UsdStageInspector.cpp
#include "UsdStageInspector.h"

#include "UnrealUSDWrapper.h"
#include "USDMemory.h"
#include "UsdWrappers/UsdStage.h"
#include "UsdWrappers/UsdPrim.h"
#include "UsdWrappers/UsdAttribute.h"
#include "UsdWrappers/SdfLayer.h"
#include "UsdWrappers/SdfPath.h"
#include "UsdWrappers/VtValue.h"
#include "UsdWrappers/UsdSkelCache.h"
#include "UsdWrappers/UsdSkelSkeletonQuery.h"

DEFINE_LOG_CATEGORY_STATIC(LogUsdInspector, Log, All);

void FUsdStageInspector::InspectStage(const FString& UsdFilePath)
{
    FScopedUsdAllocs UsdAllocs;

    UE::FUsdStage Stage = UE::FUsdStage::Open(*UsdFilePath);
    if (!Stage)
    {
        UE_LOG(LogUsdInspector, Error, TEXT("Failed to open: %s"), *UsdFilePath);
        return;
    }

    // 基本信息
    UE::FSdfLayer RootLayer = Stage.GetRootLayer();
    UE_LOG(LogUsdInspector, Log, TEXT("Root layer: %s"), *RootLayer.GetIdentifier());

    UE::FSdfLayer SessionLayer = Stage.GetSessionLayer();
    UE_LOG(LogUsdInspector, Log, TEXT("Session layer: %s"), *SessionLayer.GetIdentifier());

    // 层栈
    TArray<UE::FSdfLayer> LayerStack = Stage.GetLayerStack();
    UE_LOG(LogUsdInspector, Log, TEXT("Layer stack has %d layers"), LayerStack.Num());

    // 遍历场景
    UE::FUsdPrim Root = Stage.GetPseudoRoot();
    int32 PrimCount = 0;

    TFunction<void(const UE::FUsdPrim&, int32)> Traverse;
    Traverse = [&](const UE::FUsdPrim& Prim, int32 Depth)
    {
        FString Indent = FString::ChrN(Depth * 2, ' ');
        UE_LOG(LogUsdInspector, Log, TEXT("%s%s [%s] - %s"),
            *Indent,
            *Prim.GetName().ToString(),
            *Prim.GetTypeName().ToString(),
            Prim.IsActive() ? TEXT("Active") : TEXT("Inactive"));

        PrimCount++;

        TArray<UE::FUsdPrim> Children = Prim.GetAllChildren();
        for (const UE::FUsdPrim& Child : Children)
        {
            Traverse(Child, Depth + 1);
        }
    };

    Traverse(Root, 0);
    UE_LOG(LogUsdInspector, Log, TEXT("Total prims: %d"), PrimCount);
}

void FUsdStageInspector::ListPrimAttributes(const FString& UsdFilePath, const FString& PrimPath)
{
    FScopedUsdAllocs UsdAllocs;

    UE::FUsdStage Stage = UE::FUsdStage::Open(*UsdFilePath);
    if (!Stage)
    {
        return;
    }

    UE::FUsdPrim Prim = Stage.GetPrimAtPath(UE::FSdfPath(*PrimPath));
    if (!Prim)
    {
        UE_LOG(LogUsdInspector, Warning, TEXT("Prim not found: %s"), *PrimPath);
        return;
    }

    TArray<UE::FUsdAttribute> Attributes = Prim.GetAttributes();
    UE_LOG(LogUsdInspector, Log, TEXT("Prim '%s' has %d attributes:"), *PrimPath, Attributes.Num());

    for (const UE::FUsdAttribute& Attr : Attributes)
    {
        FString TypeName = Attr.GetTypeName().ToString();
        bool bTimeVarying = Attr.ValueMightBeTimeVarying();
        size_t NumSamples = Attr.GetNumTimeSamples();

        UE_LOG(LogUsdInspector, Log, TEXT("  %s (type: %s, timeSamples: %llu, timeVarying: %s)"),
            *Attr.GetName().ToString(),
            *TypeName,
            NumSamples,
            bTimeVarying ? TEXT("Yes") : TEXT("No"));
    }
}

void FUsdStageInspector::InspectSkeleton(const FString& UsdFilePath)
{
    FScopedUsdAllocs UsdAllocs;

    UE::FUsdStage Stage = UE::FUsdStage::Open(*UsdFilePath);
    if (!Stage)
    {
        return;
    }

    // 查找 SkelRoot
    UE::FUsdPrim Root = Stage.GetPseudoRoot();
    UE::FUsdSkelCache SkelCache;

    // 遍历查找 SkelRoot 类型的 Prim
    TFunction<void(const UE::FUsdPrim&)> FindSkelRoots;
    FindSkelRoots = [&](const UE::FUsdPrim& Prim)
    {
        if (Prim.IsA(TEXT("SkelRoot")))
        {
            UE_LOG(LogUsdInspector, Log, TEXT("Found SkelRoot: %s"), *Prim.GetPath().GetString());

            SkelCache.Populate(Prim, false);

            TArray<UE::FUsdSkelBinding> Bindings;
            SkelCache.ComputeSkelBindings(Prim, Bindings, false);

            for (const UE::FUsdSkelBinding& Binding : Bindings)
            {
                UE::FUsdPrim SkelPrim = Binding.GetSkeleton();
                if (SkelPrim)
                {
                    UE::FUsdSkelSkeletonQuery Query = SkelCache.GetSkelQuery(SkelPrim);
                    if (Query)
                    {
                        UE::FUsdSkelAnimQuery AnimQuery = Query.GetAnimQuery();
                        if (AnimQuery)
                        {
                            TArray<FString> Joints = AnimQuery.GetJointOrder();
                            UE_LOG(LogUsdInspector, Log, TEXT("  Skeleton '%s' has %d joints"),
                                *SkelPrim.GetName().ToString(), Joints.Num());
                        }
                    }
                }

                TArray<UE::FUsdSkelSkinningQuery> Targets = Binding.GetSkinningTargets();
                UE_LOG(LogUsdInspector, Log, TEXT("  Skinning targets: %d"), Targets.Num());
            }
        }

        for (const UE::FUsdPrim& Child : Prim.GetAllChildren())
        {
            FindSkelRoots(Child);
        }
    };

    FindSkelRoots(Root);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Python3` | UnrealUSDWrapper 依赖 Python3（USD SDK 的 Boost.Python 绑定） |

无其他特殊依赖（仅标准 Core/Engine 等）。

> **注意**：USDCore 默认禁用（`EnabledByDefault: false`），需要在项目设置中手动启用，或在 `.uproject` 文件中添加 `"USDCore": { "Enabled": true }`。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 近期 | `a39dbc0a835e` | 修复因禁用自定义分配器时缺少作用域分配导致的崩溃 |
| 近期 | `a1039b21e066` | 在 Windows 上禁用 UE 分配器用于 USD |
| 近期 | `be609b717cf7` | 回退 CL47041219（关于禁用 UE 分配器的变更） |

**解读**：最近的三次提交全部围绕**内存分配器问题**，表明该插件在内存管理方面仍存在稳定性挑战。禁用/启用 UE 分配器的反复操作说明这是一个复杂的技术难题。

### 维护评价

- **年龄**：约 1 年，属于较新的插件
- **实验性状态**：标记为 `IsBetaVersion: true`，`EnabledByDefault: false`
- **活跃度**：近期有更新，但全部是内存分配器相关的修复，表明核心功能仍在打磨中
- **已知问题**：
  - 内存分配器兼容性是主要痛点，Windows 平台上需要特殊处理
  - 仅支持非单体（non-monolithic）构建的内存管理
  - API 可能随版本更新发生变化
- **推荐程度**：**谨慎使用**。如果你需要在 UE 中使用 USD，这是必经之路，但要做好应对 breaking changes 和内存相关问题的准备。建议密切关注每个引擎版本的更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/USDCore)
- [USD 官方文档](https://openusd.org/release/index.html)
- [USD GitHub](https://github.com/PixarAnimationStudios/OpenUSD)