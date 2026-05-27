# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可定制对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、测试资源） |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是（Beta） |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一个**编译器驱动的可定制对象系统**，用于在运行时生成高度可变的游戏资产（角色、武器、载具等）。它解决的核心问题是：如何让美术在编辑器中定义大量视觉变体组合，同时在运行时高效地生成最终的网格体、材质和纹理。

系统架构分为三个层次：

1. **节点图层（MutableTools）**：美术通过节点图（Node Graph）定义可定制对象的结构，包括网格体变体、材质切换、纹理叠加、变形等操作
2. **编译器（Compiler）**：将节点图编译为优化后的抽象语法树（AST），经过多轮优化（常量折叠、重复消除、语义优化、下沉优化等）生成高效的运行时程序
3. **运行时（MutableRuntime）**：执行编译后的程序，根据参数值生成最终的游戏资产

与传统的"预制件 + 材质实例"方案相比，Mutable 可以在**网格体几何层面**进行组合和修改（如裁剪、变形、拼接），而不仅仅是材质参数层面。

## 使用场景

- 你在做一个角色捏脸系统，需要组合不同的发型、面部特征、服装 → 用 Mutable
- 你需要武器外观变体，但不想为每种组合烘焙独立资产 → 用 Mutable
- 你需要在运行时根据玩家选择动态生成装备组合，且要求高效的内存和加载 → 用 Mutable
- 你需要在编辑器中预览所有可能的角色组合 → 用 Mutable 的编辑器工具
- 你需要在 LOD 层面为不同组合优化纹理布局 → 用 Mutable 的 Layout 系统

## 蓝图用法

Mutable 的运行时 API 位于 `CustomizableObject` 模块中。`MutableTools` 模块主要面向编译器内部，不直接暴露蓝图节点。以下是 `CustomizableObject` 模块提供的核心蓝图接口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateInstance` | 创建可定制对象实例 | `UCustomizableObject` |
| `SetBoolParameter` | 设置布尔参数值 | `UCustomizableObjectInstance` |
| `SetIntParameter` | 设置整数参数值 | `UCustomizableObjectInstance` |
| `SetFloatParameter` | 设置浮点参数值 | `UCustomizableObjectInstance` |
| `SetColorParameter` | 设置颜色参数值 | `UCustomizableObjectInstance` |
| `SetProjectorParameter` | 设置投影器参数（用于贴花/纹理投射） | `UCustomizableObjectInstance` |
| `UpdateSkeletalMeshAsync` | 异步更新骨骼网格体 | `UCustomizableObjectInstance` |
| `GetSkeletalMesh` | 获取生成的骨骼网格体 | `UCustomizableObjectInstance` |

### 使用示例（蓝图描述）

```
1. 创建 CustomizableObject 引用 → SetBoolParameter("HasHat", true)
2. → SetIntParameter("SkinColor", 2)
3. → SetColorParameter("ShirtColor", FLinearColor::Red)
4. → UpdateSkeletalMeshAsync
5. OnUpdated 回调 → GetSkeletalMesh → SetSkeletalMesh on character
```

## C++ 用法

### 头文件引入

```cpp
#include "MutableToolsModule.h"           // 编译器工具模块
#include "MuR/CustomizableObject.h"        // 运行时对象（在 CustomizableObject 模块中）
#include "MuR/CustomizableObjectInstance.h" // 运行时实例
```

### 基本用法：使用编译器编译节点图

从 `Compiler.h` 提取的编译器使用方式：

```cpp
// 来源: Internal/MuT/Compiler.h
#include "MuT/Compiler.h"

using namespace UE::Mutable::Private;

// 1. 创建编译器选项
Ptr<CompilerOptions> Options = new CompilerOptions();
Options->SetOptimisationEnabled(true);
Options->SetConstReductionEnabled(true);
Options->SetOptimisationMaxIteration(8);
Options->SetImageCompressionQuality(80);
Options->SetEnableProgressiveImages(true);

// 2. 创建编译器（WaitCallback 用于线程同步）
TFunction<void()> WaitCallback = []() { FPlatformProcess::Sleep(0.001f); };
Ptr<Compiler> CompilerInstance = new Compiler(Options, WaitCallback);

// 3. 编译节点图为运行时模型
TMap<FOperation::ADDRESS, FInstancedStruct> ExternalOperations;
TSharedPtr<FModel> Model = CompilerInstance->Compile(RootNode, ExternalOperations);

// 4. 检查编译错误
TSharedPtr<FErrorLog> Log = CompilerInstance->GetLog();
if (Log->GetMessageCount(ErrorLogMessageType::ELMT_ERROR) > 0)
{
    for (int32 i = 0; i < Log->GetMessageCount(); ++i)
    {
        UE_LOG(LogMutable, Warning, TEXT("%s"), *Log->GetMessageText(i));
    }
}
```

### 基本用法：构建节点图

从各种 Node 头文件提取的节点图构建方式：

```cpp
// 来源: Internal/MuT/NodeObjectNew.h, NodeSurfaceNew.h, NodeMesh.h, NodeImage.h
using namespace UE::Mutable::Private;

// 创建一个可定制对象节点
Ptr<NodeObjectNew> ObjectNode = new NodeObjectNew();
ObjectNode->SetName("CustomCharacter");

// 创建网格体常量节点（通常从资产加载）
Ptr<NodeMeshConstant> MeshNode = new NodeMeshConstant();
MeshNode->Mesh = LoadMeshFromAsset(...);

// 创建材质节点
Ptr<NodeMaterialConstant> MaterialNode = new NodeMaterialConstant();

// 创建 Surface（网格体 + 材质的组合）
Ptr<NodeSurfaceNew> SurfaceNode = new NodeSurfaceNew();
SurfaceNode->Mesh = MeshNode;
SurfaceNode->Material = MaterialNode;
SurfaceNode->Tags.Add("Body");

// 将 Surface 关联到 Component
Ptr<NodeComponentNew> ComponentNode = new NodeComponentNew();
ComponentNode->SkeletalMeshObject = ...;  // 关联骨骼网格体对象

// 将 Component 添加到 Object
ObjectNode->Components.Add(ComponentNode);
```

### 基本用法：定义参数和变体

```cpp
// 来源: Internal/MuT/NodeBool.h, NodeScalar.h
using namespace UE::Mutable::Private;

// 创建布尔参数（用于条件切换）
Ptr<NodeBoolParameter> HasHatParam = new NodeBoolParameter();
HasHatParam->SetName("HasHat");
HasHatParam->DefaultValue = false;

// 创建标量参数（用于连续值控制）
Ptr<NodeScalarParameter> SizeParam = new NodeScalarParameter();
SizeParam->SetName("BodySize");
SizeParam->DefaultValue = 1.0f;

// 创建条件切换节点
Ptr<NodeMeshSwitch> MeshSwitch = new NodeMeshSwitch();
MeshSwitch->Parameter = HasHatParam;
MeshSwitch->Options.Add(BaseMesh);       // false: 基础网格体
MeshSwitch->Options.Add(BaseMeshWithHat); // true: 带帽子的网格体
```

### 进阶用法：自定义编译选项和纹理布局

```cpp
// 来源: Internal/MuT/Compiler.h, Private/MuT/CodeGenerator.h
using namespace UE::Mutable::Private;

// 配置详细的优化选项
Ptr<CompilerOptions> Options = new CompilerOptions();
CompilerOptions::Private* PrivateOptions = Options->GetPrivate();

// 启用高级优化
PrivateOptions->OptimisationOptions.bOptimiseOverlappedMasks = true;
PrivateOptions->OptimisationOptions.bUniformizeSkeleton = true;
PrivateOptions->OptimisationOptions.bEnableProgressiveImages = true;

// 配置纹理布局策略
Options->SetDataPackingStrategy(
    3,           // MinTextureResidentMipCount
    1024 * 64    // EmbeddedDataBytesLimit (64KB)
);

// 设置外部资源回调（用于引用引擎资源）
FReferencedImageResourceFunc ImageProvider = [](PASSTHROUGH_ID Id, 
    TSharedPtr<TManagedPtr<FImage>> OutImage, bool bRunImmediately) -> UE::Tasks::FTask
{
    // 异步加载引擎纹理资源
    return UE::Tasks::Launch(TEXT("LoadReferencedImage"), [Id, OutImage]() { /* ... */ });
};

FReferencedMeshResourceFunc MeshProvider = [](PASSTHROUGH_ID Id, const FString& MorphName,
    TSharedPtr<TManagedPtr<FMesh>> OutMesh, bool bRunImmediately) -> UE::Tasks::FTask
{
    return UE::Tasks::Launch(TEXT("LoadReferencedMesh"), [Id, OutMesh]() { /* ... */ });
};

Options->SetReferencedResourceCallback(ImageProvider, MeshProvider);

// 禁用材质生成（用于纯数据编译）
Options->SetDisableMaterialGeneration(true);
```

### 进阶用法：使用 Layout 系统优化纹理

```cpp
// 来源: Internal/MuT/NodeLayout.h
using namespace UE::Mutable::Private;

// 创建纹理布局节点
Ptr<NodeLayout> LayoutNode = new NodeLayout();
LayoutNode->Size = FIntVector2(4096, 4096);
LayoutNode->MaxSize = FIntVector2(4096, 4096);  // 0,0 = 无限制
LayoutNode->Strategy = EPackStrategy::Resizeable;
LayoutNode->ReductionMethod = EReductionMethod::Halve;
LayoutNode->AutoBlockStrategy = EAutoBlocksStrategy::Rectangles;
LayoutNode->TexCoordsIndex = 0;

// 从网格体 UV 自动生成布局块
TManagedPtr<FMesh> Mesh = LoadMesh(...);
LayoutNode->GenerateLayoutBlocks(Mesh, 0);
// 或者使用 UV 岛生成
LayoutNode->GenerateLayoutBlocksFromUVIslands(Mesh, 0);
```

### 进阶用法：使用 Surface Modifier 修改已有表面

```cpp
// 来源: Internal/MuT/NodeSurfaceModifierSurfaceEdit.h
using namespace UE::Mutable::Private;

// 创建表面编辑修改器（用于在运行时修改网格体和纹理）
Ptr<NodeSurfaceModifierSurfaceEdit> EditModifier = new NodeSurfaceModifierSurfaceEdit();

// 配置 LOD 0 的修改
NodeSurfaceModifierSurfaceEdit::FLOD LODData;

// 移除部分网格体
LODData.MeshRemove = RemoveMeshNode;

// 添加新网格体片段
LODData.MeshAdd = AddMeshNode;

// 修改纹理
NodeSurfaceModifierSurfaceEdit::FTexture TextureEdit;
TextureEdit.MaterialParameterKey = FParameterKey("DiffuseTexture");
TextureEdit.PatchImage = PatchImageNode;
TextureEdit.PatchMask = MaskImageNode;
TextureEdit.PatchBlocks.Add(FBox2f(FVector2f(0.0f, 0.0f), FVector2f(0.5f, 0.5f)));
TextureEdit.PatchBlendType = EBlendType::BT_BLEND;
LODData.Textures.Add(TextureEdit);

EditModifier->LODs.Add(LODData);

// 设置目标标签（只有带有这些标签的表面会被修改）
EditModifier->RequiredTags.Add("Body");
EditModifier->MultipleTagsPolicy = EMutableMultipleTagPolicy::AllRequired;
```

### 进阶用法：使用 MeshClipMorphPlane 进行网格体裁剪和变形

```cpp
// 来源: Internal/MuT/NodeMeshClipMorphPlane.h, NodeSurfaceModifierMeshClipMorphPlane.h
using namespace UE::Mutable::Private;

Ptr<NodeMeshClipMorphPlane> ClipNode = new NodeMeshClipMorphPlane();
ClipNode->SetSource(SourceMesh);

// 设置裁剪平面
ClipNode->SetPlane(
    FVector3f(0, 0, 50),   // 平面中心
    FVector3f(0, 0, 1)     // 法线方向
);

// 设置变形参数
ClipNode->SetParams(
    10.0f,  // DistanceToPlane - 最后受影响顶点到平面的距离
    0.5f    // LinearityFactor - 影响的线性度
);

// 设置变形椭圆区域
ClipNode->SetMorphEllipse(
    20.0f,  // radius1
    20.0f,  // radius2
    0.0f    // rotation
);

// 使用骨骼选择顶点（用于角色特定部位的裁剪）
ClipNode->SetVertexSelectionBone(FName("spine_01"), 30.0f);
// 或使用盒体选择
ClipNode->SetVertexSelectionBox(FVector3f(0, 0, 50), FVector3f(30, 30, 30));
```

## Demo 示例

```cpp
// MyMutableCharacterBuilder.h
#pragma once

#include "CoreMinimal.h"

namespace UE::Mutable::Private
{
    class NodeObjectNew;
    class NodeMeshConstant;
    class NodeMaterialConstant;
    class NodeSurfaceNew;
    class NodeComponentNew;
    class NodeBoolParameter;
    class NodeImageParameter;
    class NodeMeshSwitch;
    class NodeImageLayer;
    class Compiler;
    class CompilerOptions;
    class FModel;
    class FErrorLog;
}

class FMyMutableCharacterBuilder
{
public:
    /** 构建一个简单的可定制角色对象 */
    static TSharedPtr<UE::Mutable::Private::FModel> BuildCharacterModel();
    
private:
    /** 创建基础网格体节点 */
    static TSharedPtr<UE::Mutable::Private::NodeMeshConstant> CreateBaseMesh();
    
    /** 创建材质节点 */
    static TSharedPtr<UE::Mutable::Private::NodeMaterialConstant> CreateBaseMaterial();
};
```

```cpp
// MyMutableCharacterBuilder.cpp
#include "MyMutableCharacterBuilder.h"

// MutableTools headers
#include "MuT/Compiler.h"
#include "MuT/NodeObjectNew.h"
#include "MuT/NodeSurfaceNew.h"
#include "MuT/NodeComponentNew.h"
#include "MuT/NodeMesh.h"
#include "MuT/NodeMaterial.h"
#include "MuT/NodeBool.h"
#include "MuT/NodeImage.h"
#include "MuT/ErrorLog.h"

using namespace UE::Mutable::Private;

TSharedPtr<FModel> FMyMutableCharacterBuilder::BuildCharacterModel()
{
    // 1. 创建根对象节点
    Ptr<NodeObjectNew> Object = new NodeObjectNew();
    Object->SetName("Character");
    
    // 2. 设置对象状态（用于运行时更新）
    Object->SetStateCount(1);
    Object->SetStateName(0, "Default");
    Object->AddStateParam(0, "BodyTexture");
    
    // 3. 创建网格体
    Ptr<NodeMeshConstant> BodyMesh = CreateBaseMesh();
    
    // 4. 创建材质
    Ptr<NodeMaterialConstant> BodyMaterial = CreateBaseMaterial();
    
    // 5. 创建纹理参数（运行时可替换）
    Ptr<NodeImageParameter> BodyTextureParam = new NodeImageParameter();
    BodyTextureParam->SetName("BodyTexture");
    
    // 6. 创建 Surface（网格体 + 材质组合）
    Ptr<NodeSurfaceNew> BodySurface = new NodeSurfaceNew();
    BodySurface->Mesh = BodyMesh;
    BodySurface->Material = BodyMaterial;
    BodySurface->Tags.Add("Body");
    
    // 7. 创建 Component
    Ptr<NodeComponentNew> Component = new NodeComponentNew();
    
    // 8. 组装对象层级
    Object->Components.Add(Component);
    
    // 9. 编译
    Ptr<CompilerOptions> Options = new CompilerOptions();
    Options->SetOptimisationEnabled(true);
    Options->SetConstReductionEnabled(true);
    Options->SetOptimisationMaxIteration(4);
    
    TFunction<void()> WaitCallback = []() { FPlatformProcess::Sleep(0.001f); };
    Ptr<Compiler> CompilerInstance = new Compiler(Options, WaitCallback);
    
    TMap<FOperation::ADDRESS, FInstancedStruct> ExternalOps;
    TSharedPtr<FModel> Model = CompilerInstance->Compile(Object, ExternalOps);
    
    // 10. 检查错误
    TSharedPtr<FErrorLog> Log = CompilerInstance->GetLog();
    int32 ErrorCount = Log->GetMessageCount(ErrorLogMessageType::ELMT_ERROR);
    if (ErrorCount > 0)
    {
        UE_LOG(LogTemp, Error, TEXT("Mutable compilation failed with %d errors"), ErrorCount);
        for (int32 i = 0; i < Log->GetMessageCount(); ++i)
        {
            if (Log->GetMessageType(i) == ELMT_ERROR)
            {
                UE_LOG(LogTemp, Error, TEXT("  %s"), *Log->GetMessageText(i));
            }
        }
        return nullptr;
    }
    
    return Model;
}

TSharedPtr<NodeMeshConstant> FMyMutableCharacterBuilder::CreateBaseMesh()
{
    Ptr<NodeMeshConstant> MeshNode = new NodeMeshConstant();
    // 实际使用中，这里会从 FMesh 资源加载网格体数据
    // MeshNode->Mesh = LoadMeshFromPath(...);
    return MeshNode;
}

TSharedPtr<NodeMaterialConstant> FMyMutableCharacterBuilder::CreateBaseMaterial()
{
    Ptr<NodeMaterialConstant> MatNode = new NodeMaterialConstant();
    // 实际使用中，这里会配置材质参数映射
    return MatNode;
}
```

## 模块依赖

从各模块的 Build.cs 提取的独特依赖（省略常见的 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `MutableRuntime` | Mutable 运行时虚拟机，执行编译后的可定制对象程序 |
| `MutableTools` | Mutable 编译器工具，将节点图编译为运行时程序 |
| `MutableValidation` | Mutable 数据验证模块 |
| `DerivedDataCache` | 编译产物缓存，加速重复编译 |
| `MessageLog` | 编译错误/警告消息日志 |
| `ImageCore` / `ImageWrapper` | 纹理格式转换和压缩 |

**注意**：`CustomizableObject` 模块依赖 `UnrealEd`、`EditorStyle`、`MessageLog` 和 `MutableTools`，这些主要在编辑器环境下使用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复多个同名骨骼网格体导致几何体重复的问题 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复 UV 遮罩裁剪操作加载错误 Mip 级别的问题 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias | 修复纹理参数计算 LODBias 方法错误的问题 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过 ClothingAssetBase 接口支持更多服装资产类型 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较 PassthroughObjects 时可能出现的数据竞争 |

### 维护评价

**活跃维护中** ✅

- **创建时间**：2024 年 9 月从 Experimental 迁移到 Beta 状态，是 UE5 中相对较新的系统级插件
- **更新频率**：非常活跃，最近的提交集中在 2026 年 5 月，且每天都有多个修复
- **代码规模**：1206 个源文件，属于超大型插件，说明这是一个功能完整且复杂度很高的系统
- **维护质量**：近期更新主要是 bug 修复和质量改进，涵盖骨骼网格体、纹理压缩、数据竞争等核心功能
- **Beta 状态**：当前仍标记为 Beta，意味着 API 可能会有变化，但核心功能已基本稳定
- **推荐使用**：推荐用于需要高度可定制化的游戏角色/装备系统，但需注意 Beta 状态可能带来的 API 变更

⚠️ **注意**：该插件仍在 Beta 阶段，使用时需关注版本升级可能带来的兼容性变化。建议在生产环境中做好回归测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/mutable-objects-in-unreal-engine)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable/Tests)