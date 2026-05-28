# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可定制对象 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是（Beta） |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一套完整的**运行时可定制对象系统**，用于在不膨胀资产数量的前提下，实现角色外观、装备、载具等的动态组合与变化。

它解决的核心问题是：**如何在资产复用的同时实现大规模视觉多样性**。传统做法需要为每种组合烘焙独立资产（如 N 种肤色 × M 种发型 = N×M 个网格体），导致资产数量指数级膨胀。Mutable 通过图结构定义资产之间的组合关系，在编译期优化这些图，运行时仅通过参数切换来实时组装最终网格体和材质。

系统由三个层次构成：
1. **节点图层**：设计师在编辑器中用 Node（节点）构建定制化逻辑，包括网格体组合、贴图层叠、颜色映射、标量混合等
2. **编译层（MutableTools）**：将节点图编译为优化的 AST（抽象语法树），执行常量折叠、数据去重、语义优化等，最终链接为紧凑的运行时模型
3. **运行时层（MutableRuntime + CustomizableObject）**：接收编译后的模型，根据玩家选择的参数实时生成最终网格体和纹理

本模块 **MutableTools** 是整个系统的编译核心，负责将设计师定义的节点图转换为高效的运行时指令序列。

## 使用场景

- 你在做一个 RPG 游戏，需要角色创建系统支持数千种外观组合 → 用 Mutable
- 你需要大量装备部件可以混搭穿戴，且不能为每种组合制作独立资产 → 用 Mutable
- 你想在运行时根据玩家选择动态修改网格体（如裁剪、变形、贴花） → 用 Mutable
- 你需要根据存档数据实时重建角色外观 → 用 Mutable
- 你想用数据表（Table）批量定义大量结构相似的变体对象 → 用 Mutable

## 蓝图用法

Mutable 的蓝图 API 主要通过 `CustomizableObject` 模块暴露。以下是从源码中提取的核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BeginUpdate` | 开始更新可定制对象实例（应用参数变更） | `UCustomizableObjectInstance` |
| `SetFloatParameter` | 设置浮点标量参数 | `UCustomizableObjectInstance` |
| `SetIntParameter` | 设置整数参数 | `UCustomizableObjectInstance` |
| `SetBoolParameter` | 设置布尔参数 | `UCustomizableObjectInstance` |
| `SetColorParameter` | 设置颜色参数 | `UCustomizableObjectInstance` |
| `SetVectorParameter` | 设置向量参数 | `UCustomizableObjectInstance` |
| `SetTextureParameter` | 设置纹理参数 | `UCustomizableObjectInstance` |
| `SetProjectorParameter` | 设置投影器参数（用于贴花投影） | `UCustomizableObjectInstance` |
| `GetSkeletalMesh` | 获取更新后的骨骼网格体 | `UCustomizableObjectInstance` |
| `GetNumLODs` | 获取当前实例的 LOD 数量 | `UCustomizableObjectInstance` |
| `CreateInstance` | 从可定制对象创建新实例 | `UCustomizableObject` |
| `Compile` | 编译可定制对象（编辑器用） | `UCustomizableObject` |

### 使用示例（蓝图描述）

**创建角色外观变体：**

1. 从 `UCustomizableObject` 调用 `CreateInstance` 创建一个实例
2. 调用 `BeginUpdate` 开始参数修改
3. 用 `SetIntParameter` 设置发型索引（例如 "HairStyle" = 3）
4. 用 `SetColorParameter` 设置发色（例如 "HairColor" = 红色）
5. 用 `SetFloatParameter` 设置体形参数（例如 "BodyWeight" = 0.7）
6. 调用 `UpdateSkeletalMeshAsyncResult` 并绑定回调
7. 在回调中用 `GetSkeletalMesh` 获取最终网格体并应用到角色

**使用投影器进行贴花：**

1. 创建投影器参数（`SetProjectorParameter`），定义位置、方向、缩放
2. 设置投影类型（Planar / Cylindrical / Wrapped）
3. 在编译后的实例中，投影器会自动将贴花图像投射到网格体表面

## C++ 用法

MutableTools 提供了底层编译 API，通常由 CustomizableObject 模块内部调用。以下是基于源码分析的核心用法。

### 头文件引入

```cpp
#include "MuT/Compiler.h"
#include "MuT/Node.h"
#include "MuT/NodeObjectNew.h"
#include "MuT/NodeSkeletalMesh.h"
#include "MuT/NodeImageConstant.h"
#include "MuT/NodeScalarParameter.h"
#include "MuT/NodeBoolParameter.h"
#include "MuT/NodeColorParameter.h"
#include "MuT/Table.h"
```

### 基本用法

以下示例展示如何使用 MutableTools 的编译器将一个节点图编译为运行时模型。

```cpp
// 来源: Internal/MuT/Compiler.h

using namespace UE::Mutable::Private;

// 1. 创建编译器选项
Ptr<CompilerOptions> Options = new CompilerOptions();
Options->SetLogEnabled(true);
Options->SetOptimisationEnabled(true);
Options->SetConstReductionEnabled(true);
Options->SetImageCompressionQuality(100);

// 2. 定义等待回调（编译可能需要跨线程同步）
TFunction<void()> WaitCallback = []()
{
    FPlatformProcess::Sleep(0.01f);
};

// 3. 创建编译器
Ptr<Compiler> MutableCompiler = new Compiler(Options, WaitCallback);

// 4. 构建节点图（示例：一个带标量参数的对象）
Ptr<NodeObjectNew> RootObject = new NodeObjectNew();
RootObject->SetName(TEXT("MyCharacter"));

// 设置状态数量
RootObject->SetStateCount(1);
RootObject->SetStateName(0, TEXT("Default"));

// 添加标量参数节点
Ptr<NodeScalarParameter> WeightParam = new NodeScalarParameter();
WeightParam->SetName(TEXT("BodyWeight"));

// 5. 编译
TMap<FOperation::ADDRESS, FInstancedStruct> ExternalOperations;
TSharedPtr<FModel> Model = MutableCompiler->Compile(RootObject, ExternalOperations);

// 6. 检查日志
TSharedPtr<FErrorLog> Log = MutableCompiler->GetLog();
if (Log->GetMessageCount() > 0)
{
    for (int32 i = 0; i < Log->GetMessageCount(); ++i)
    {
        UE_LOG(LogTemp, Warning, TEXT("Mutable: %s"), *Log->GetMessageText(i));
    }
}
```

### 进阶用法

#### 使用数据表批量定义变体

```cpp
// 来源: Internal/MuT/Table.h

using namespace UE::Mutable::Private;

// 创建一个数据表，定义武器变体
Ptr<FTable> WeaponTable = new FTable();
WeaponTable->SetName(TEXT("WeaponVariants"));

// 添加列
int32 NameCol = WeaponTable->AddColumn(TEXT("Name"), ETableColumnType::String);
int32 DamageCol = WeaponTable->AddColumn(TEXT("Damage"), ETableColumnType::Scalar);
int32 ColorCol = WeaponTable->AddColumn(TEXT("Tint"), ETableColumnType::Color);
int32 MeshCol = WeaponTable->AddColumn(TEXT("Mesh"), ETableColumnType::Mesh);
int32 TexCol = WeaponTable->AddColumn(TEXT("Texture"), ETableColumnType::Image);

// 添加行数据
WeaponTable->AddRow(0); // 基础剑
WeaponTable->SetCell(NameCol, 0, FString(TEXT("Basic Sword")));
WeaponTable->SetCell(DamageCol, 0, 10.0f);
WeaponTable->SetCell(ColorCol, 0, FVector4f(0.8f, 0.8f, 0.8f, 1.0f));

WeaponTable->AddRow(1); // 火焰剑
WeaponTable->SetCell(NameCol, 1, FString(TEXT("Fire Sword")));
WeaponTable->SetCell(DamageCol, 1, 25.0f);
WeaponTable->SetCell(ColorCol, 1, FVector4f(1.0f, 0.3f, 0.1f, 1.0f));
```

#### 使用布局系统管理纹理拼接

```cpp
// 来源: Internal/MuT/NodeLayout.h

using namespace UE::Mutable::Private;

// 创建纹理布局节点，用于将多个贴图区域拼接到一张大图
Ptr<NodeLayout> Layout = new NodeLayout();
Layout->Size = FIntVector2(2048, 2048);
Layout->MaxSize = FIntVector2(4096, 4096);
Layout->Strategy = EPackStrategy::Resizeable;
Layout->ReductionMethod = EReductionMethod::Halve;
Layout->TexCoordsIndex = 0; // 使用第一套 UV

// 自动生成布局块（基于网格体 UV 岛）
// Layout->GenerateLayoutBlocks(MeshData, 0);
```

#### 使用表面修改器裁剪和变形

```cpp
// 来源: Internal/MuT/NodeSurfaceModifierMeshClipMorphPlane.h

using namespace UE::Mutable::Private;

// 创建裁剪变形修改器
Ptr<NodeSurfaceModifierMeshClipMorphPlane> ClipModifier = new NodeSurfaceModifierMeshClipMorphPlane();

// 设置裁剪平面
ClipModifier->SetPlane(
    FVector3f(0.0f, 0.0f, 100.0f),  // 中心
    FVector3f(0.0f, 0.0f, 1.0f)     // 法线
);

// 设置变形参数
ClipModifier->SetParams(50.0f, 0.5f);  // 距离, 线性因子

// 设置变形椭圆
ClipModifier->SetMorphEllipse(20.0f, 20.0f, 0.0f);  // 半径1, 半径2, 旋转

// 可选：选择受影响的骨骼子层级
ClipModifier->SetVertexSelectionBone(FName(TEXT("spine_01")), 50.0f);
```

#### 裁剪和变形的几何操作

```cpp
// 来源: Internal/MuT/NodeSurfaceModifierSurfaceEdit.h

using namespace UE::Mutable::Private;

// 创建表面编辑修改器
Ptr<NodeSurfaceModifierSurfaceEdit> SurfaceEdit = new NodeSurfaceModifierSurfaceEdit();

// 对每个 LOD 配置编辑操作
NodeSurfaceModifierSurfaceEdit::FLOD LODData;

// 添加新网格体到表面
LODData.MeshAdd = NewMeshToAdd;

// 从表面移除网格体
LODData.MeshRemove = MeshToRemove;

// 修改纹理
NodeSurfaceModifierSurfaceEdit::FTexture TextureData;
TextureData.MaterialParameterKey = BaseColorKey;
TextureData.PatchImage = OverlayTexture;
TextureData.PatchMask = MaskTexture;
TextureData.PatchBlendType = EBlendType::BT_BLEND;
TextureData.bPatchApplyToAlpha = false;
LODData.Textures.Add(TextureData);

SurfaceEdit->LODs.Add(LODData);
```

## Demo 示例

以下是一个最小的可编译示例，展示如何创建一个带参数的可定制对象并编译它。

```cpp
// MutableDemo.h
#pragma once

#include "CoreMinimal.h"
#include "MuT/Compiler.h"
#include "MuT/NodeObjectNew.h"
#include "MuT/NodeComponentNew.h"
#include "MuT/NodeSkeletalMeshNew.h"
#include "MuT/NodeMeshConstant.h"
#include "MuT/NodeScalarParameter.h"
#include "MuT/NodeScalarSwitch.h"
#include "MuT/NodeMaterialConstant.h"
#include "MuT/NodeSurfaceNew.h"

using namespace UE::Mutable::Private;

class FMutableDemo
{
public:
    /** 创建一个简单的可定制对象并编译 */
    static TSharedPtr<FModel> CreateAndCompileDemo();
};

// MutableDemo.cpp
#include "MutableDemo.h"

TSharedPtr<FModel> FMutableDemo::CreateAndCompileDemo()
{
    // --- 1. 构建节点图 ---

    // 标量参数：选择武器样式
    Ptr<NodeScalarParameter> StyleParam = new NodeScalarParameter();
    StyleParam->SetName(TEXT("WeaponStyle"));
    StyleParam->SetDefaultValue(0.0f);

    // 两种网格体变体
    Ptr<NodeMeshConstant> MeshA = new NodeMeshConstant();
    // MeshA->SetMesh(MeshDataA);

    Ptr<NodeMeshConstant> MeshB = new NodeMeshConstant();
    // MeshB->SetMesh(MeshDataB);

    // 根据参数选择网格体
    Ptr<NodeScalarSwitch> MeshSwitch = new NodeScalarSwitch();
    MeshSwitch->Parameter = StyleParam;
    MeshSwitch->Options.Add(MeshA);
    MeshSwitch->Options.Add(MeshB);

    // 创建表面（网格体 + 材质）
    Ptr<NodeMaterialConstant> Material = new NodeMaterialConstant();

    Ptr<NodeSurfaceNew> Surface = new NodeSurfaceNew();
    Surface->Mesh = MeshSwitch;
    Surface->Material = Material;
    Surface->Name = FName(TEXT("Body"));
    Surface->Tags.Add(TEXT("Visible"));

    // 创建组件
    Ptr<NodeComponentNew> Component = new NodeComponentNew();
    Component->Id = 0;
    // Component 中会通过 SkeletalMeshObject 引用 Surface

    // 创建对象
    Ptr<NodeObjectNew> RootObject = new NodeObjectNew();
    RootObject->SetName(TEXT("DemoWeapon"));
    RootObject->SetUid(FGuid::NewGuid().ToString());
    RootObject->SetStateCount(1);
    RootObject->SetStateName(0, TEXT("Default"));
    // RootObject->Components.Add(Component);

    // --- 2. 配置编译器 ---

    Ptr<CompilerOptions> Options = new CompilerOptions();
    Options->SetOptimisationEnabled(true);
    Options->SetConstReductionEnabled(true);
    Options->SetImageCompressionQuality(100);

    TFunction<void()> WaitCallback = []() {};

    // --- 3. 编译 ---

    Ptr<Compiler> MutableCompiler = new Compiler(Options, WaitCallback);

    TMap<FOperation::ADDRESS, FInstancedStruct> ExternalOperations;
    TSharedPtr<FModel> Model = MutableCompiler->Compile(RootObject, ExternalOperations);

    // --- 4. 验证 ---

    TSharedPtr<FErrorLog> Log = MutableCompiler->GetLog();
    int32 ErrorCount = 0;
    for (int32 i = 0; i < Log->GetMessageCount(); ++i)
    {
        if (Log->GetMessageType(i) == ELMT_ERROR)
        {
            UE_LOG(LogTemp, Error, TEXT("Mutable compile error: %s"), *Log->GetMessageText(i));
            ++ErrorCount;
        }
    }

    if (ErrorCount == 0 && Model.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Mutable compilation succeeded. Model ready for runtime."));
    }

    return Model;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DerivedDataCache` | 编译产物的派生数据缓存存储 |
| `MutableRuntime` | 运行时模型执行引擎，MutableTools 编译目标 |
| `MessageLog` | 编译错误和警告消息的编辑器日志输出 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复同名多骨骼网格体时几何体重复的问题 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复 UV 遮罩裁剪操作未加载正确 mipmap 的问题 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias | 修复纹理参数计算 LODBias 方法错误的问题 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用 ClothingAssetBase 接口支持更多布料资产类型 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较 PassthroughObjects 时可能的数据竞争 |

### 维护评价

**活跃维护**。Mutable 是 Epic 从 Mutable 公司收购后整合到 UE 核心的系统，2024 年 9 月从 Experimental 状态升级为 Beta，表明 Epic 对其持续投入。从 git 历史看，截至 2026 年 5 月仍有密集的 bug 修复和功能改进（最近一周内有多次提交），维护非常活跃。

- **创建时间**：2024 年从 Experimental 迁移到 Beta（实际核心代码历史更长，源自 Mutable 公司）
- **更新频率**：高，持续有功能性修复和改进
- **状态**：Beta，但仍标记为实验性
- **已知限制**：作为 Beta 版本，API 可能在未来版本中有变动
- **推荐使用**：✅ 推荐。对于需要运行时可定制对象的项目，这是 UE5 原生且经过大规模验证的解决方案。尽管标记为 Beta，但已有大型商业项目在使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/mutable-customizable-objects-in-unreal-engine)