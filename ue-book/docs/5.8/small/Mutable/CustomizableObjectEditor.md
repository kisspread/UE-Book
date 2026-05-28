# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可定制对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无（纯代码插件） |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `MutableTools` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是 UE5 的**运行时角色/物品自定义系统**，用于创建可由玩家在游戏运行时动态定制外观的游戏对象。它解决的核心问题是：**如何在保证运行时性能的前提下，支持大量视觉变体的组合爆炸**。

传统方式为每种外观变体制作独立资源会导致资产爆炸（如 10 种发型 × 5 种肤色 × 3 种服装 = 150 个独立资产）。Mutable 通过图节点系统定义变体规则，编译为高效的运行时模型，在运行时按需生成最终网格体和材质，将 150 个资产压缩为一组编译数据 + 参数配置。

**核心工作流**：
1. **图编辑**：在 CustomizableObject 图编辑器中用节点定义对象结构（引用网格体、材质、纹理等资产），连接修饰器节点（变形、裁剪、纹理混合等），暴露整数/浮点/颜色/投影器等参数
2. **编译**：将图编译为 Mutable 虚拟机模型（.mut 文件），存入 DerivedDataCache
3. **运行时实例化**：为每个 `UCustomizableObjectInstance` 设置参数值，Mutable 引擎按需生成最终的 `USkeletalMesh`/`UStaticMesh`、纹理和材质
4. **烘焙（可选）**：将特定参数组合的实例序列化为静态资产，用于离线场景

## 使用场景

- 你在做一个角色自定义游戏（捏脸、换装、武器皮肤）→ 用 Mutable
- 你需要在运行时动态组合大量视觉变体且不想资产爆炸 → 用 Mutable
- 你需要材质参数的运行时动态组合（多材质层、纹理替换、颜色混合）→ 用 Mutable
- 你需要基于 LOD 的自动纹理和网格体优化 → 用 Mutable 的 Layout 系统
- 你需要将自定义结果烘焙为静态资产（过场动画、宣传截图）→ 用 Mutable 的 Bake 功能
- 你需要可复用的自定义图逻辑片段 → 用 Mutable 的 Macro Library 系统

## 蓝图用法

Mutable 的核心工作流通过 `UCustomizableObjectEditorFunctionLibrary` 暴露蓝图节点。注意：大部分图编辑操作在 CustomizableObject 编辑器中完成，蓝图主要用于编译和实例管理。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CompileCustomizableObjectSynchronously` | 同步编译指定的 CustomizableObject（已废弃，推荐用 `UCustomizableObject::Compile`） | `UCustomizableObjectEditorFunctionLibrary` |
| `NewCustomizableObject` | 在指定路径创建新的 CustomizableObject 资产，可指定父对象和分组 | `UCustomizableObjectEditorFunctionLibrary` |

### 新建可定制对象参数结构

`FNewCustomizableObjectParameters` 结构体用于创建新对象时的配置：

| 属性 | 类型 | 说明 |
|---|---|---|
| `PackagePath` | `FString` | 包路径（如 "/Game"），不可以斜杠结尾 |
| `AssetName` | `FString` | 资产名称（如 "SampleAssetName"） |
| `ParentObject` | `UCustomizableObject*` | 要附加子对象的父 CustomizableObject |
| `ParentGroupNode` | `FString` | 父对象中的分组节点名称（仅当指定了 ParentObject 时有效） |

### 使用示例（蓝图描述）

**编译对象**：
1. 获取目标 `UCustomizableObject` 的引用
2. 调用 `CompileCustomizableObjectSynchronously`，设置优化等级和纹理压缩模式
3. 返回 `ECustomizableObjectCompilationState`（None/InProgress/Completed/Failed）

**创建新对象**：
1. 填充 `FNewCustomizableObjectParameters`（路径、名称、父对象、分组）
2. 调用 `NewCustomizableObject`
3. 获取返回的 `UCustomizableObject*`

**实例参数编辑**（在 CO Instance Editor 中）：
- 整数参数：下拉列表选择选项（对应图中的 Int Parameter 节点）
- 浮点参数：滑块编辑（对应 Float Parameter 节点）
- 颜色参数：颜色选择器（对应 Color Parameter 节点）
- 投影器参数：视口中的 Gizmo 控件控制位置/方向/缩放（对应 Projector Parameter 节点）
- 布尔参数：复选框（对应 Bool Parameter 节点）
- 变换参数：变换编辑器（对应 Transform Parameter 节点）

## C++ 用法

### 头文件引入

```cpp
// 编辑器函数库（蓝图节点）
#include "MuCOE/CustomizableObjectEditorFunctionLibrary.h"

// 图遍历工具
#include "MuCOE/GraphTraversal.h"

// 编译器接口
#include "MuCOE/CustomizableObjectCompiler.h"

// 扩展数据编译接口
#include "MuCOE/ExtensionDataCompilerInterface.h"

// 编辑器模块接口
#include "MuCOE/ICustomizableObjectEditorModulePrivate.h"
```

### 基本用法

**同步编译 Customizable Object**

来源：`Source/CustomizableObjectEditor/Public/MuCOE/CustomizableObjectEditorFunctionLibrary.h`

```cpp
#include "MuCOE/CustomizableObjectEditorFunctionLibrary.h"

// 获取目标 CustomizableObject
UCustomizableObject* MyObject = LoadObject<UCustomizableObject>(nullptr, TEXT("/Game/MyCO"));

// 同步编译（会阻塞当前线程）
ECustomizableObjectCompilationState State = UCustomizableObjectEditorFunctionLibrary::CompileCustomizableObjectSynchronously(
    MyObject,
    ECustomizableObjectOptimizationLevel::None,
    ECustomizableObjectTextureCompression::Fast,
    /*bGatherReferences=*/ false
);

if (State == ECustomizableObjectCompilationState::Completed)
{
    UE_LOG(LogTemp, Log, TEXT("编译成功"));
}
else if (State == ECustomizableObjectCompilationState::Failed)
{
    UE_LOG(LogTemp, Error, TEXT("编译失败"));
}
```

**创建新的 Customizable Object**

来源：`Source/CustomizableObjectEditor/Public/MuCOE/CustomizableObjectEditorFunctionLibrary.h`

```cpp
FNewCustomizableObjectParameters Params;
Params.PackagePath = TEXT("/Game/Characters");
Params.AssetName = TEXT("HeroCustomizable");

// 创建子对象附加到父对象的指定分组
Params.ParentObject = LoadObject<UCustomizableObject>(nullptr, TEXT("/Game/Characters/BaseCharacter"));
Params.ParentGroupNode = TEXT("HeadGroup");

UCustomizableObject* NewCO = UCustomizableObjectEditorFunctionLibrary::NewCustomizableObject(Params);
```

### 进阶用法

**图遍历与根对象查找**

来源：`Source/CustomizableObjectEditor/Private/MuCOE/GraphTraversal.h`

```cpp
#include "MuCOE/GraphTraversal.h"

UCustomizableObject* ChildObject = LoadObject<UCustomizableObject>(nullptr, TEXT("/Game/Characters/ChildCO"));

// 获取整个 CO 层级的根对象
UCustomizableObject* RootObject = GraphTraversal::GetRootObject(ChildObject);

// 检查某个 CO 是否是根对象
bool bIsRoot = GraphTraversal::IsRootObject(*ChildObject);

// 获取图中所有相关的 CustomizableObject
TSet<UCustomizableObject*> AllObjects;
GraphTraversal::GetAllObjectsInGraph(RootObject, AllObjects);

// 遍历图中的所有节点
UCustomizableObjectNodeObject* RootNode = GetRootNode(RootObject);
if (RootNode)
{
    GraphTraversal::VisitNodes(*RootNode, [](UCustomizableObjectNode& Node)
    {
        UE_LOG(LogTemp, Log, TEXT("Node: %s (%s)"), *Node.GetName(), *Node.GetClass()->GetName());
    });
}
```

**追踪引脚连接**

来源：`Source/CustomizableObjectEditor/Private/MuCOE/GraphTraversal.h`

```cpp
#include "MuCOE/GraphTraversal.h"

// 追踪输入引脚到其连接的输出引脚
UEdGraphPin* InputPin = SomeNode->FindPin(TEXT("Mesh"));
UEdGraphPin* ConnectedOutput = FollowInputPin(InputPin);

if (ConnectedOutput)
{
    UCustomizableObjectNode* SourceNode = Cast<UCustomizableObjectNode>(ConnectedOutput->GetOwningNode());
    // 处理源节点...
}

// 追踪输出引脚（返回连接到该输出的所有输入引脚）
TArray<UEdGraphPin*> ConnectedInputs = FollowOutputPinArray(OutputPin);

// 通过宏上下文追踪引脚（跨宏边界）
TArray<const UCustomizableObjectNodeMacroInstance*> MacroContext;
const UEdGraphPin* SourcePin = GraphTraversal::FindIOPinSourceThroughMacroContext(SomePin, &MacroContext);
```

**扩展数据编译接口**

来源：`Source/CustomizableObjectEditor/Public/MuCOE/ExtensionDataCompilerInterface.h`

```cpp
#include "MuCOE/ExtensionDataCompilerInterface.h"

// 在编译过程中注册扩展数据
void MyExtensionNode::GenerateMutableNode(FMutableGraphGenerationContext& GenerationContext)
{
    FExtensionDataCompilerInterface Interface(GenerationContext);
    
    // 注册扩展数据对象（bDuplicate=true 表示烘焙时复制）
    UE::Mutable::Private::PASSTHROUGH_ID Id = Interface.MakeExtensionData(*MyExtensionDataObject, true);
    
    // 记录编译日志
    Interface.CompilerLog(FText::FromString(TEXT("Extension data registered")), this);
}
```

## Demo 示例

以下示例展示如何在 C++ 中以编程方式管理 CustomizableObject 的编译流程：

```cpp
// CustomObjectManager.h
#pragma once

#include "CoreMinimal.h"
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "MuCOE/CustomizableObjectEditorFunctionLibrary.h"
#include "MuCOE/GraphTraversal.h"

class FCustomObjectManager
{
public:
    // 编译指定的 CustomizableObject 并创建运行时实例
    static UCustomizableObjectInstance* CompileAndCreateInstance(UCustomizableObject* Object);
    
    // 获取对象层级信息
    static void LogObjectHierarchy(UCustomizableObject* Object);
};
```

```cpp
// CustomObjectManager.cpp
#include "CustomObjectManager.h"

UCustomizableObjectInstance* FCustomObjectManager::CompileAndCreateInstance(UCustomizableObject* Object)
{
    if (!Object)
    {
        UE_LOG(LogTemp, Error, TEXT("CustomObjectManager: Object is null"));
        return nullptr;
    }
    
    // 同步编译
    ECustomizableObjectCompilationState State = 
        UCustomizableObjectEditorFunctionLibrary::CompileCustomizableObjectSynchronously(
            Object,
            ECustomizableObjectOptimizationLevel::None,
            ECustomizableObjectTextureCompression::Fast,
            false
        );
    
    if (State != ECustomizableObjectCompilationState::Completed)
    {
        UE_LOG(LogTemp, Error, TEXT("CustomObjectManager: Compilation failed for %s"), *Object->GetName());
        return nullptr;
    }
    
    // 编译成功后，正常流程中实例由 UE 自动管理
    // 这里展示如何获取根对象信息
    UCustomizableObject* Root = GraphTraversal::GetRootObject(Object);
    if (Root)
    {
        UE_LOG(LogTemp, Log, TEXT("Root object: %s"), *Root->GetName());
    }
    
    return nullptr; // 实例由引擎管理
}

void FCustomObjectManager::LogObjectHierarchy(UCustomizableObject* Object)
{
    if (!Object) return;
    
    // 获取所有相关对象
    TSet<UCustomizableObject*> AllObjects;
    GraphTraversal::GetAllObjectsInGraph(Object, AllObjects);
    
    UE_LOG(LogTemp, Log, TEXT("Object %s has %d related COs"), *Object->GetName(), AllObjects.Num());
    
    for (UCustomizableObject* CO : AllObjects)
    {
        bool bIsRoot = GraphTraversal::IsRootObject(*CO);
        UE_LOG(LogTemp, Log, TEXT("  - %s (Root: %s)"), *CO->GetName(), bIsRoot ? TEXT("Yes") : TEXT("No"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MutableRuntime` | Mutable 虚拟机运行时引擎，执行模型生成最终网格体/纹理/材质 |
| `MutableTools` | Mutable 编译工具链，将图节点编译为优化的运行时模型 |
| `MutableValidation` | Mutable 数据验证模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复同名多个骨骼网格体时几何数据重复的问题 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复 UV 遮罩裁剪操作未正确加载对应 mipmap 的问题 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. | 修复纹理参数使用错误方法计算 LODBias 的问题 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过 ClothingAssetBase 接口支持更多服装资产类型 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较 PassthroughObject 时可能发生的数据竞争 |

### 维护评价

**活跃维护** — Mutable 是 Epic 官方维护的大型运行时自定义系统，处于**积极开发**状态：

- **创建时间**：2024-09-05 从 Experimental 升级为 Beta 状态（代码库实际历史更久，可追溯至 UE4 时代）
- **更新频率**：极其活跃，最近的 commit 密集出现在 2026-05-25 至 2026-05-26，持续修复运行时 bug 和改进编译流程
- **维护状态**：⚠️ **Beta 阶段**（`IsBetaVersion=true`）。2024 年 9 月从 Experimental 移入 Beta，尚未标记为正式版（GA）
- **代码规模**：1206 个源文件，包含完整的编辑器图系统、编译器、运行时引擎、调试工具
- **已知限制**：Beta 版本可能存在 API 变化，生产环境使用需谨慎评估稳定性
- **推荐**：✅ **推荐使用** — 作为 UE5 官方的角色自定义方案，是当前最成熟的解决方案。虽然是 Beta 状态，但已具备完整的工具链和运行时支持，适合新项目采用。需注意定期跟进官方更新以获取 bug 修复

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://github.com/anticto/Mutable-Documentation/wiki)（社区维护）