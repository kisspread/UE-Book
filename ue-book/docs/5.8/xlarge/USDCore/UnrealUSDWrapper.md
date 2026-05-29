# USD Core

> Adds support for USD SDK, UE wrapper classes and USD conversion utilities

| 属性 | 值 |
|---|---|
| 中文名 | USD 核心 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD 资产、材质模板） |
| 模块 | `UnrealUSDWrapper` (Runtime), `USDClasses` (Runtime), `USDUtilities` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-16 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/USDCore) | |

## 用途

USDCore 是 Unreal Engine 对 Pixar OpenUSD (Universal Scene Description) SDK 的底层集成插件。它提供三层核心能力：

1. **UnrealUSDWrapper**：将 pxr 命名空间下的 USD SDK 原生类型（如 `UsdStage`、`UsdPrim`、`SdfLayer`）封装为可在 UE 无 RTTI 模块中使用的包装类（`UE::FUsdStage`、`UE::FUsdPrim`、`UE::FSdfLayer`），同时解决 USD SDK 与 UE 自定义内存分配器之间的冲突问题。
2. **USDClasses**：提供 UE 风格的 USD 数据类定义（如 `UUsdAssetCache`、`UUsdAssetCache2` 等），用于在 UE 资产系统中管理 USD 相关资产。
3. **USDUtilities**：提供 USD 与 UE 之间的转换工具函数，包括材质转换、几何体转换、骨骼动画转换等高层业务逻辑。

**为什么存在**：USD SDK 使用标准 C 运行时内存分配器（CRT），而 UE 覆盖了每个模块的 `new`/`delete`。当 USD 对象在 UE 模块中被释放时，会导致用 UE 分配器释放 CRT 分配的内存，引发崩溃。USDCore 通过 `FUsdMemoryManager` 实现了自定义的内存管理栈，确保 USD 对象始终使用正确的分配器。

**注意**：此插件默认禁用且标记为实验性（Beta）。使用前需手动启用，并确保项目已包含 USD SDK 依赖。

## 使用场景

- 你需要在 UE 中读取/写入 USD 文件（.usd、.usda、.usdc、.usdz）→ 用 UnrealUSDWrapper 的 Stage/Layer API
- 你需要将 USD 场景中的几何体、材质、骨骼动画导入 UE → 用 USDUtilities 的转换函数
- 你需要在运行时动态加载 USD 场景并查询 Prim 属性 → 用 FUsdPrim、FUsdAttribute 包装类
- 你需要监听 USD Stage 的变更事件（如图层修改、对象变更）→ 用 FUsdListener
- 你需要在自定义工具中创建新的 USD Stage 并写入自定义数据 → 用 UnrealUSDWrapper.NewStage()

## 模块架构

```
USDCore/
├── UnrealUSDWrapper (Runtime)  ← USD SDK 封装层 + 内存管理
│   ├── UsdWrappers/            ← FUsdStage, FUsdPrim, FSdfLayer 等包装类
│   ├── USDMemory.h             ← 内存分配器管理
│   ├── USDListener.h           ← Stage 变更事件监听
│   └── UnrealUSDWrapper.h      ← 枚举定义、工具函数、USD 标识符
├── USDClasses (Runtime)        ← UE 资产类定义
└── USDUtilities (Runtime)      ← 高层转换工具
```

---

## 蓝图用法

此插件主要为 C++ 编程接口，不暴露 BlueprintCallable 节点。如需在蓝图中使用 USD，应使用 `USDImporter` / `USDExporter` 等上层插件提供的蓝图接口。

---

## C++ 用法

### 模块配置

**⚠️ 重要**：使用 `UnrealUSDWrapper` 模块需要特殊配置：

1. 在你的 `.Build.cs` 中添加模块依赖
2. 如果需要直接使用 USD SDK 内存管理工具，需在模块主 .cpp 文件中使用 `IMPLEMENT_MODULE_USD` 代替 `IMPLEMENT_MODULE`
3. 在 `.Build.cs` 中添加 `PrivateDefinitions.Add("SUPPRESS_PER_MODULE_INLINE_FILE");`

### 头文件引入

```cpp
// 包装类（不需要直接 include USD SDK）
#include "UnrealUSDWrapper.h"
#include "UsdWrappers/UsdStage.h"
#include "UsdWrappers/UsdPrim.h"
#include "UsdWrappers/SdfLayer.h"
#include "UsdWrappers/UsdAttribute.h"
#include "UsdWrappers/ForwardDeclarations.h"

// 内存管理（当需要直接操作 USD SDK 对象时）
#include "USDMemory.h"

// 变更监听
#include "USDListener.h"
```

### 基本用法：打开 Stage 并遍历 Prim

```cpp
// 引自 UnrealUSDWrapper.h 中 UnrealUSDWrapper 类
#include "UnrealUSDWrapper.h"
#include "UsdWrappers/UsdStage.h"
#include "UsdWrappers/UsdPrim.h"

// 打开一个 USD 文件
UE::FUsdStage Stage = UnrealUSDWrapper::OpenStage(
    TEXT("/path/to/scene.usd"),
    EUsdInitialLoadSet::LoadAll
);

if (Stage)
{
    // 获取默认 Prim
    UE::FUsdPrim DefaultPrim = Stage.GetDefaultPrim();
    
    // 获取伪根节点并遍历子级
    UE::FUsdPrim PseudoRoot = Stage.GetPseudoRoot();
    TArray<UE::FUsdPrim> Children = PseudoRoot.GetChildren();
    
    for (const UE::FUsdPrim& Child : Children)
    {
        UE_LOG(LogTemp, Log, TEXT("Prim: %s, Type: %s"),
            *Child.GetName().ToString(),
            *Child.GetTypeName().ToString());
    }
}
```

### 基本用法：读取 Prim 属性

```cpp
// 引自 UsdWrappers/UsdAttribute.h
#include "UsdWrappers/UsdAttribute.h"
#include "UsdWrappers/VtValue.h"

// 获取 Prim 的特定属性
UE::FUsdAttribute Attr = Prim.GetAttribute(TEXT("xformOp:translate"));

if (Attr)
{
    UE::FVtValue Value;
    if (Attr.Get(Value))
    {
        // 获取为 FVector3f（USD 到 UE 的自动转换）
        FVector3f Translation = Value.Get<FVector3f>();
        UE_LOG(LogTemp, Log, TEXT("Translation: %s"), *FString::Printf(TEXT("%s"), *FVector(Translation).ToString()));
    }
}
```

### 基本用法：SdfLayer 操作

```cpp
// 引自 UsdWrappers/SdfLayer.h
#include "UsdWrappers/SdfLayer.h"

// 创建新 Layer
UE::FSdfLayer NewLayer = UE::FSdfLayer::CreateNew(TEXT("/path/to/new.usda"));

// 打开已有 Layer
UE::FSdfLayer ExistingLayer = UE::FSdfLayer::FindOrOpen(TEXT("/path/to/existing.usd"));

if (ExistingLayer)
{
    // 获取时间码范围
    double Start = ExistingLayer.GetStartTimeCode();
    double End = ExistingLayer.GetEndTimeCode();
    
    // 设置帧率
    ExistingLayer.SetFramesPerSecond(24.0);
    
    // 保存
    ExistingLayer.Save();
    
    // 导出为不同格式
    ExistingLayer.Export(TEXT("/path/to/exported.usda"), TEXT("Exported from UE"));
}
```

### 进阶用法：内存安全的 USD SDK 直接操作

```cpp
// 引自 USDMemory.h
#include "USDMemory.h"
#include "USDIncludesStart.h"
#include "pxr/usd/usd/prim.h"
#include "USDIncludesEnd.h"

// 使用 FScopedUsdAllocs 确保 USD 对象使用 CRT 分配器
{
    FScopedUsdAllocs UsdAllocs;  // 激活系统/CRT 分配器
    
    // 这里创建的任何 pxr:: 原生对象都使用 CRT 分配器
    pxr::UsdPrim NativePrim = Stage->GetPseudoRoot();
    
    // 遍历属性
    std::vector<pxr::UsdAttribute> Attributes = NativePrim.GetAttributes();
    for (const auto& Attr : Attributes)
    {
        // ... 处理属性
    }
}  // UsdAllocs 析构时自动恢复 UE 分配器

// 如果需要在 UE 分配器活跃的上下文中使用 USD 分配器创建的共享指针：
{
    FScopedUnrealAllocs UnrealAllocs;  // 激活 UE 分配器
    TSharedRef<FMyObject> Obj = MakeShared<FMyObject>();
}
```

### 进阶用法：TUsdStore 跨作用域存储 USD 对象

```cpp
#include "USDMemory.h"

class FMyUsdHandler
{
    // TUsdStore 确保 USD 对象在构造、复制、移动和销毁时使用正确的分配器
    TUsdStore<pxr::UsdPrim> StoredPrim;
    TUsdStore<pxr::UsdStageRefPtr> StoredStage;
    
public:
    void Init(UE::FUsdStage& Stage)
    {
        // 自动使用 CRT 分配器构造
        StoredPrim = Stage->GetPseudoRoot();
    }
};
```

### 进阶用法：Stage 变更监听

```cpp
#include "USDListener.h"

class FMyStageListener
{
    FUsdListener Listener;
    
    void StartListening(UE::FUsdStage& Stage)
    {
        Listener.Register(Stage);
        
        // 监听对象变更
        Listener.GetOnObjectsChanged().AddLambda(
            [](const UsdUtils::FObjectChangesByPath& InfoChanges,
               const UsdUtils::FObjectChangesByPath& ResyncChanges)
            {
                for (const auto& [Path, Entries] : ResyncChanges)
                {
                    UE_LOG(LogTemp, Log, TEXT("Prim resynced: %s"), *Path);
                }
            }
        );
        
        // 监听图层变更
        Listener.GetOnSdfLayersChanged().AddLambda(
            [](const UsdUtils::FLayerToSdfChangeList& Changes)
            {
                for (const auto& [Layer, ChangeList] : Changes)
                {
                    for (const auto& [PrimPath, Entry] : ChangeList)
                    {
                        if (Entry.Flags.bDidAddNonInertPrim)
                        {
                            UE_LOG(LogTemp, Log, TEXT("New prim added: %s"), *PrimPath.GetString());
                        }
                    }
                }
            }
        );
    }
    
    // 使用 FScopedBlockNotices 临时阻断通知
    void BatchEdit()
    {
        FScopedBlockNotices Blocker(Listener);
        // ... 执行大量编辑操作，不会触发变更通知
    }
};
```

### 进阶用法：Variant Set 操作

```cpp
#include "UsdWrappers/UsdVariantSets.h"

UE::FUsdVariantSets VarSets = Prim.GetVariantSets();
TArray<FString> Names = VarSets.GetNames();

for (const FString& Name : Names)
{
    UE::FUsdVariantSet VarSet = VarSets.GetVariantSet(Name);
    TArray<FString> Variants = VarSet.GetVariantNames();
    
    // 选择一个变体
    if (Variants.Num() > 0)
    {
        VarSet.SetVariantSelection(Variants[0]);
    }
}
```

### 进阶用法：骨骼动画查询

```cpp
#include "UsdWrappers/UsdSkelCache.h"
#include "UsdWrappers/UsdSkelSkeletonQuery.h"
#include "UsdWrappers/UsdSkelAnimQuery.h"

UE::FUsdSkelCache SkelCache;

// 填充缓存（从 SkelRoot prim 开始）
SkelCache.Populate(SkelRootPrim, /*bTraverseInstanceProxies=*/false);

// 获取骨骼查询
UE::FUsdSkelSkeletonQuery SkelQuery = SkelCache.GetSkelQuery(SkeletonPrim);
if (SkelQuery)
{
    TArray<FTransform> JointTransforms;
    SkelQuery.ComputeJointLocalTransforms(JointTransforms, /*TimeCode=*/0.0);
}

// 获取动画查询
UE::FUsdSkelAnimQuery AnimQuery = SkelCache.GetAnimQuery(SkelAnimPrim);
if (AnimQuery)
{
    TArray<double> TimeCodes;
    AnimQuery.GetJointTransformTimeSamples(TimeCodes);
    TArray<FString> JointOrder = AnimQuery.GetJointOrder();
}
```

## Demo 示例

### 最小可编译示例：打开 USD 文件并打印 Prim 树

**MyUsdModule.Build.cs**（依赖配置）：
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "UnrealUSDWrapper"
});
```

**MyUsdReader.h**：
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyUsdReader
{
public:
    static void ReadUsdFile(const FString& FilePath);
    static void PrintPrimTree(const class UE::FUsdPrim& Prim, int32 Depth = 0);
};
```

**MyUsdReader.cpp**：
```cpp
#include "MyUsdReader.h"
#include "UnrealUSDWrapper.h"
#include "UsdWrappers/UsdStage.h"
#include "UsdWrappers/UsdPrim.h"
#include "UsdWrappers/UsdAttribute.h"
#include "UsdWrappers/VtValue.h"

void FMyUsdReader::ReadUsdFile(const FString& FilePath)
{
    // 打开 Stage，不加载 Payload（流式加载）
    UE::FUsdStage Stage = UnrealUSDWrapper::OpenStage(
        *FilePath,
        EUsdInitialLoadSet::LoadNone
    );

    if (!Stage)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open USD file: %s"), *FilePath);
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("Opened USD stage: %s"), *FilePath);

    // 获取时间码信息
    UE_LOG(LogTemp, Log, TEXT("  Start Time: %.2f, End Time: %.2f, FPS: %.2f"),
        Stage.GetStartTimeCode(),
        Stage.GetEndTimeCode(),
        Stage.GetFramesPerSecond());

    // 打印图层栈
    TArray<UE::FSdfLayer> Layers = Stage.GetLayerStack();
    for (const UE::FSdfLayer& Layer : Layers)
    {
        UE_LOG(LogTemp, Log, TEXT("  Layer: %s"), *Layer.GetDisplayName());
    }

    // 遍历 Prim 树
    UE::FUsdPrim Root = Stage.GetPseudoRoot();
    PrintPrimTree(Root);
}

void FMyUsdReader::PrintPrimTree(const UE::FUsdPrim& Prim, int32 Depth)
{
    if (!Prim) return;

    FString Indent = FString::ChrN(Depth * 2, ' ');
    FString TypeName = Prim.GetTypeName().ToString();
    FString Purpose;

    // 读取 Purpose 属性
    UE::FUsdAttribute PurposeAttr = Prim.GetAttribute(TEXT("purpose"));
    if (PurposeAttr)
    {
        UE::FVtValue PurposeValue;
        if (PurposeAttr.Get(PurposeValue))
        {
            Purpose = TEXT(" [purpose: ") + PurposeValue.Get<FString>() + TEXT("]");
        }
    }

    UE_LOG(LogTemp, Log, TEXT("%s%s (%s)%s%s"),
        *Indent,
        *Prim.GetName().ToString(),
        TypeName.IsEmpty() ? TEXT("untyped") : *TypeName,
        Prim.IsInstance() ? TEXT(" [instance]") : TEXT(""),
        *Purpose);

    // 递归子级
    TArray<UE::FUsdPrim> Children = Prim.GetChildren();
    for (const UE::FUsdPrim& Child : Children)
    {
        PrintPrimTree(Child, Depth + 1);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Python3` | UnrealUSDWrapper 模块依赖，USD SDK 内部 Python 绑定支持 |

无特殊依赖（仅标准 Core/Engine/Slate 等 + Python3）。使用 USDClasses 或 USDUtilities 模块时可能需要额外依赖，请查阅各自的 Build.cs。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `561d9c2d` | USD Pregen: Fix materials inside instances not being deduplicated | 修复实例内部材质未被去重的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的乱码输出 |
| 2026-04-28 | `5b5d2b22` | [USD] Harden USDZ extraction in InterchangeUSD against path traversal (Zip Slip) and unsafe archive | 加固 USDZ 解压过程，防止路径遍历攻击 |
| 2026-04-28 | `bf5d0e5b` | USD: Add Nanite/mesh build settings schemas | 添加 Nanite/网格构建设置的 USD Schema |

### 维护评价

- **创建时间**：2024-05-16，约 1 年历史，属于较新的插件
- **更新频率**：近期（2026年4-5月）有多次实质性更新，涵盖 bug 修复、安全加固和新功能（Nanite Schema），说明插件处于**活跃维护**状态
- **实验性状态**：`IsBetaVersion=true` 且 `EnabledByDefault=false`，Epic 标记此插件为实验性质，API 可能发生变化
- **代码规模**：1838 个源文件，是 UE 中最大的 Runtime 插件之一，涵盖完整的 USD SDK 封装
- **已知限制**：
  - 内存管理工具仅在非 Monolithic 构建中生效（`!IS_MONOLITHIC`）
  - Linux/Mac 平台上 USD SDK 不需要内存重载（使用系统分配器即可）
  - `FUsdGeomBBoxCache` 不是线程安全的，内置了 `FRWLock` 但仍需注意

**推荐使用**：适合需要在 UE 中深度集成 USD 工作流的项目。由于标记为实验性且默认禁用，建议在生产环境中小心使用，并做好 API 变更的准备。此插件是 USDImporter、USDExporter 等上层插件的基础依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/USDCore)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/USDCore/Source/UnrealUSDWrapper/Tests)（如有）