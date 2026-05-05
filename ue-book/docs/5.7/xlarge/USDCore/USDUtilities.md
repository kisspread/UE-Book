# USD Core

> Adds support for USD SDK, UE wrapper classes and USD conversion utilities

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、项目设置） |
| 模块 | `UnrealUSDWrapper` (Runtime), `USDClasses` (Runtime), `USDUtilities` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-16 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/USDCore) | |

## 用途

USDCore 是 Unreal Engine 与 Pixar USD（Universal Scene Description）SDK 之间的核心桥接层。它解决的核心问题是：**如何在 UE 的对象模型与 USD 的 Prim/Attribute 体系之间进行高效、准确的双向转换**。

这个插件存在是因为 UE 需要一个统一的 USD 基础设施层，为上层的 USD Stage、USD Interchange 等功能提供：
- **USD SDK 的 C++ 封装**（`UnrealUSDWrapper`）：将 pxr 命名空间下的原始 USD 类型包装为 UE 友好的 `UE::FUsdPrim`、`UE::FUsdStage` 等类型
- **UE 资产转换工具**（`USDClasses`）：定义 USD 与 UE 之间的资产缓存、元数据等共享数据结构
- **转换工具库**（`USDUtilities`）：提供几何体、材质、灯光、骨骼、毛发等几乎所有 UE 资产类型与 USD Schema 之间的双向转换函数

**注意**：此插件默认禁用（`EnabledByDefault: false`）且标记为实验性（`IsBetaVersion: true`），需要手动启用。

## 使用场景

- 你需要在运行时或编辑器中加载/解析 USD 文件 → 用 USDCore 提供的 Stage 和 Prim 封装
- 你需要将 USD 的 UsdGeomMesh 转换为 UE 的 UStaticMesh/FMeshDescription → 用 `USDGeomMeshConversion`
- 你需要将 USD 的 UsdShadeMaterial 转换为 UE 的 UMaterialInterface → 用 `USDShadeConversion`
- 你需要将 USD 的灯光 Schema（UsdLuxDistantLight 等）映射到 UE 灯光组件 → 用 `USDLightConversion`
- 你需要将 USD 的骨骼动画（UsdSkel）转换为 UE 的 USkeletalMesh/UAnimSequence → 用 `USDSkeletalDataConversion`
- 你需要自定义 USD Schema 到 UE 资产的翻译逻辑 → 继承 `FUsdSchemaTranslator` 并注册
- 你需要在导出时确保文件路径唯一 → 用 `USDExportUtils` 的 UniquePathScope
- 你需要管理 USD 层（sublayer、reference、payload）→ 用 `USDLayerUtils`

## 蓝图用法

USDUtilities 模块主要面向 C++ 开发者，提供的 API 均为原生 C++ 函数，不包含 BlueprintCallable 节点。蓝图层面的 USD 交互由上层插件（如 USDStageImporter）提供。

## C++ 用法

### 头文件引入

```cpp
// 类型转换（向量、矩阵、路径等）
#include "USDTypesConversion.h"

// 几何网格转换
#include "USDGeomMeshConversion.h"

// 材质/着色转换
#include "USDShadeConversion.h"

// 灯光转换
#include "USDLightConversion.h"

// Prim/变换转换
#include "USDPrimConversion.h"

// 骨骼数据转换
#include "USDSkeletalDataConversion.h"

// 层管理
#include "USDLayerUtils.h"

// 属性工具
#include "USDAttributeUtils.h"

// 导出工具
#include "USDExportUtils.h"

// 错误/日志工具
#include "USDErrorUtils.h"

// Schema 翻译框架
#include "USDSchemaTranslator.h"

// Prim-资产链接缓存
#include "USDPrimLinkCache.h"

// 信息缓存
#include "USDInfoCache.h"
```

### 基本用法：类型转换

将 USD 原生类型转换为 UE 类型，这是最基础的操作。

```cpp
// 来源: USDTypesConversion.h
#include "USDTypesConversion.h"

// 字符串转换
std::string UsdStr = "Hello";
FString UeStr = UsdToUnreal::ConvertString(UsdStr);

// 路径转换
pxr::SdfPath UsdPath("/Root/MyPrim");
FString UePathStr = UsdToUnreal::ConvertPath(UsdPath);

// 向量转换
pxr::GfVec3f UsdVec(1.0f, 2.0f, 3.0f);
FVector UeVec = UsdToUnreal::ConvertVector(UsdVec);

// 带 Stage 信息的向量转换（处理坐标轴和单位）
FUsdStageInfo StageInfo(Stage);  // 从 Stage 获取 UpAxis 和 MetersPerUnit
FVector UeVecScaled = UsdToUnreal::ConvertVector(StageInfo, UsdVec);

// 矩阵转换
pxr::GfMatrix4d UsdMatrix;
FMatrix UeMatrix = UsdToUnreal::ConvertMatrix(UsdMatrix);

// 带 Stage 信息的矩阵转换（返回 FTransform，自动处理轴向和缩放）
FTransform UeTransform = UsdToUnreal::ConvertMatrix(StageInfo, UsdMatrix);

// 颜色转换（假设输入为线性空间）
pxr::GfVec3f UsdColor(0.5f, 0.3f, 0.1f);
FLinearColor UeColor = UsdToUnreal::ConvertColor(UsdColor);
```

### 基本用法：几何网格转换

```cpp
// 来源: USDGeomMeshConversion.h
#include "USDGeomMeshConversion.h"

// 配置转换选项
UsdToUnreal::FUsdMeshConversionOptions Options;
Options.TimeCode = pxr::UsdTimeCode::Default();
Options.PurposesToLoad = EUsdPurpose::Default;
Options.RenderContext = pxr::UsdShadeTokens->universalRenderContext;

// 将 USD Mesh 转换为 FMeshDescription
FMeshDescription MeshDescription;
bool bSuccess = UsdToUnreal::ConvertGeomMesh(
    Stage,          // pxr::UsdStageRefPtr
    UsdGeomMesh,    // pxr::UsdGeomMesh
    MeshDescription,
    Options
);
```

### 基本用法：灯光转换

```cpp
// 来源: USDLightConversion.h
#include "USDLightConversion.h"

// 将 USD 远光灯转换为 UE 方向光组件
UDirectionalLightComponent* DirLight = /* 获取或创建组件 */;
bool bSuccess = UsdToUnreal::ConvertDistantLight(Prim, *DirLight, UsdTimeCode);

// 将 USD 球形光转换为 UE 点光源
UPointLightComponent* PointLight = /* 获取或创建组件 */;
bSuccess = UsdToUnreal::ConvertSphereLight(Prim, *PointLight, UsdTimeCode);

// 将 USD 矩形光转换为 UE 矩形光
URectLightComponent* RectLight = /* 获取或创建组件 */;
bSuccess = UsdToUnreal::ConvertRectLight(Prim, *RectLight, UsdTimeCode);
```

### 基本用法：日志系统

```cpp
// 来源: USDErrorUtils.h
#include "USDErrorUtils.h"

// 输出到 Output Log（不显示在 Message Log）
USD_LOG_INFO(TEXT("Processing prim: %s"), *PrimName);
USD_LOG_WARNING(TEXT("Unsupported attribute type: %s"), *AttrName);
USD_LOG_ERROR(TEXT("Failed to convert mesh: %s"), *ErrorMsg);

// 输出到 Message Log（用户可见，需要在 FScopedUsdMessageLog 作用域内）
{
    FScopedUsdMessageLog MessageLog;
    USD_LOG_USERWARNING(LOCTEXT("InvalidBinding", "Material binding is invalid"));
    USD_LOG_USERERROR(FText::Format(
        LOCTEXT("ConversionFailed", "Failed to convert {0}"),
        FText::FromString(PrimName)
    ));
    // 离开作用域后自动显示累积的消息
}

// 检查是否有错误累积
if (FUsdLogManager::HasAccumulatedErrors())
{
    // 处理错误情况
}
```

### 进阶用法：Prim-资产链接缓存

```cpp
// 来源: USDPrimLinkCache.h
#include "USDPrimLinkCache.h"

FUsdPrimLinkCache LinkCache;

// 将 UE 资产链接到 USD Prim 路径
UE::FSdfPath PrimPath(TEXT("/Root/Mesh1"));
LinkCache.LinkAssetToPrim(PrimPath, MyStaticMesh);

// 查询某个 Prim 关联的所有资产
TArray<TWeakObjectPtr<UObject>> Assets = LinkCache.GetAllAssetsForPrim(PrimPath);

// 查询某个 Prim 关联的特定类型资产（模板函数，从后向前搜索优先返回最新版本）
UStaticMesh* Mesh = LinkCache.GetSingleAssetForPrim<UStaticMesh>(PrimPath);

// 查询某个资产关联的所有 Prim 路径
TArray<UE::FSdfPath> Prims = LinkCache.GetPrimsForAsset(MyStaticMesh);

// 序列化支持（可保存到磁盘）
LinkCache.Serialize(Archive);
```

### 进阶用法：导出路径唯一性保证

```cpp
// 来源: USDExportUtils.h
#include "USDExportUtils.h"

// 使用 RAII 方式开启唯一路径作用域
{
    UsdUnreal::ExportUtils::FUniquePathScope Scope;

    // 在作用域内，每次调用都会返回全局唯一的路径
    FString Path1 = UsdUnreal::ExportUtils::GetUniqueFilePathForExport(TEXT("/Export/Mesh.usda"));
    // Path1: "/Export/Mesh.usda"

    FString Path2 = UsdUnreal::ExportUtils::GetUniqueFilePathForExport(TEXT("/Export/Mesh.usda"));
    // Path2: "/Export/Mesh_1.usda"  （自动添加后缀避免冲突）

} // 离开作用域后清除路径缓存
```

### 进阶用法：Schema 翻译器注册

```cpp
// 来源: USDSchemaTranslator.h
#include "USDSchemaTranslator.h"

// 自定义 Schema 翻译器
class FMyCustomTranslator : public FUsdSchemaTranslator
{
public:
    FMyCustomTranslator(TSharedRef<FUsdSchemaTranslationContext> InContext, const UE::FUsdTyped& InSchema)
        : FUsdSchemaTranslator(InContext, InSchema)
    {}

    virtual void CreateAssets() override { /* 创建 UE 资产 */ }
    virtual void UpdateComponents(USceneComponent* Parent) override { /* 更新组件 */ }
    // ... 其他重写
};

// 在模块启动时注册
FUsdSchemaTranslatorRegistry::Get().RegisterSchemaTranslator(
    TEXT("MyCustomSchema"),
    [](TSharedRef<FUsdSchemaTranslationContext> Context, const UE::FUsdTyped& Schema) -> TSharedRef<FUsdSchemaTranslator>
    {
        return MakeShared<FMyCustomTranslator>(Context, Schema);
    }
);
```

### 进阶用法：属性静音（Mute）

```cpp
// 来源: USDAttributeUtils.h
#include "USDAttributeUtils.h"

// 静音某个属性，使其在 UE 加载时不被动画化
UE::FUsdAttribute Attr = Prim.GetAttribute(TEXT("xformOp:translate"));
UsdUtils::MuteAttribute(Attr, Stage);

// 检查属性是否被静音
if (UsdUtils::IsAttributeMuted(Attr, Stage))
{
    // 该属性不会被动画化
}

// 取消静音
UsdUtils::UnmuteAttribute(Attr, Stage);
```

## Demo 示例

### 最小示例：USD 类型转换

**MyUsdUtils.Build.cs**：
```csharp
using UnrealBuildTool;

public class MyUsdUtils : ModuleRules
{
    public MyUsdUtils(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "USDUtilities"    // 依赖 USDUtilities 模块
        });
    }
}
```

**MyUsdUtils.h**：
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyUsdUtils
{
public:
    /** 将 USD 向量转换为 UE 向量并打印 */
    static void ConvertAndPrintVector(const pxr::GfVec3f& UsdVec);

    /** 将 USD 路径转换为 UE 字符串 */
    static FString ConvertUsdPath(const pxr::SdfPath& UsdPath);
};
```

**MyUsdUtils.cpp**：
```cpp
#include "MyUsdUtils.h"
#include "USDTypesConversion.h"

void FMyUsdUtils::ConvertAndPrintVector(const pxr::GfVec3f& UsdVec)
{
    FVector UeVec = UsdToUnreal::ConvertVector(UsdVec);
    UE_LOG(LogTemp, Log, TEXT("Converted vector: X=%.2f Y=%.2f Z=%.2f"),
        UeVec.X, UeVec.Y, UeVec.Z);
}

FString FMyUsdUtils::ConvertUsdPath(const pxr::SdfPath& UsdPath)
{
    return UsdToUnreal::ConvertPath(UsdPath);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealUSDWrapper` | USD SDK 的 UE 封装层，提供 `UE::FUsdPrim`、`UE::FUsdStage` 等类型 |
| `USDClasses` | USD 共享数据结构，资产缓存（`UUsdAssetCache2`/`UUsdAssetCache3`）、元数据定义 |
| `Python3` | UnrealUSDWrapper 依赖，用于 USD 的 Python 绑定支持 |

**使用者需注意**：你的模块需要同时依赖 `USDUtilities` 和 `USDClasses`，因为转换函数大量使用 `USDClasses` 中定义的类型（如 `FUsdPrimMaterialSlot`、`FUsdSchemaTranslationContext` 等）。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 近期 | `4b44b880de84` | 修复导出 Geometry Cache 到 USD 时因缺少速度数据导致的潜在崩溃 | Bug 修复：导入 Geometry Cache 时丢失了速度数据 |
| 近期 | `a39dbc0a835e` | 修复因禁用自定义分配器时缺少作用域分配导致的崩溃 | 底层内存管理修复 |
| 近期 | `a1039b21e066` | 在 Windows 上禁用 UE 分配器用于 USD | 平台特定的分配器策略调整 |

### 维护评价

- **创建时间**：2024 年 5 月，是一个相对较新的插件
- **更新频率**：近期有连续的 bug 修复提交，表明处于**活跃维护**状态
- **实验性标记**：`IsBetaVersion: true` 且 `EnabledByDefault: false`，API 可能发生变化
- **代码规模**：1822 个源文件，属于超大型插件，涵盖 USD 集成的方方面面
- **已知限制**：作为实验性功能，部分 API 标记了 `UE_DEPRECATED`（如旧版错误监控 API 在 5.6 中被废弃），建议使用新版 `FScopedUsdMessageLog`
- **推荐程度**：如果你需要 USD 集成功能，这是必经之路。但需注意它是实验性的，API 可能在版本间变化。建议锁定 UE 版本使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/USDCore)
- [USD 官方文档](https://graphics.pixar.com/usd/docs/index.html)
- [USDUtilities 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/USDCore/Source/USDUtilities)
- [USDClasses 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/USDCore/Source/USDClasses)
- [UnrealUSDWrapper 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/USDCore/Source/UnrealUSDWrapper)