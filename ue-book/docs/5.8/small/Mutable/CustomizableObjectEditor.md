# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可定制对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、图表编辑器、调试工具） |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `MutableTools` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一个**运行时角色/物体自定义系统**，它允许开发者通过可视化节点图定义可定制对象（Customizable Object），在运行时根据参数组合动态生成最终的网格体、材质和纹理，而无需预先烘焙所有变体。

**核心问题**：在角色自定义游戏（如 MMO、RPG、换装系统）中，装备、发型、肤色等组合会产生指数级的资产变体。如果预先烘焙所有组合，内存和磁盘空间将爆炸性增长。

**Mutable 的解决方案**：
- **编译时**：将 UE 图表编译为 Mutable 虚拟机字节码（Model），描述所有可能的资产组合逻辑
- **运行时**：根据参数（如"发型=3"、"护甲=皮革"、"颜色=红色"）执行字节码，动态生成最终的 SkeletalMesh、StaticMesh、材质和纹理
- **流式加载**：支持 LOD 流式和纹理流式，按需生成不同精度的资产

与传统方法相比，100 个装备 × 10 种肤色 × 20 种发型 = 20,000 种组合，Mutable 只需要存储原始资产 + 一份编译后的 Model，运行时按需生成。

## 使用场景

- 你在做 MMO / RPG 的角色自定义系统（捏脸 + 装备换装）→ 用 Mutable 定义完整的角色定制流程
- 你需要武器/装备有大量材质变体但不想烘焙 1000+ 个独立资产 → 用 Mutable 动态组合纹理参数
- 你的游戏需要运行时修改物体外观（如涂装系统、破坏系统）→ 用 Mutable 的参数驱动系统
- 你需要在编辑器中快速预览所有参数组合的效果 → 用 Mutable 编辑器的实时预览功能
- 你有 DataTable 驱动的大量装备数据，需要自动生成对应的网格/材质 → 用 Table 节点将 DataTable 映射到 Mutable 图表

## 编辑器用法

Mutable 的核心工作流是**图表编辑器**：在 Customizable Object 编辑器中通过节点图定义资产的组合逻辑。

### 核心概念

| 概念 | 说明 |
|---|---|
| Customizable Object (CO) | 定义可定制对象逻辑的 UAsset，包含节点图 |
| Customizable Object Instance (COI) | CO 的运行时实例，持有参数值 |
| Model | CO 编译后的虚拟机字节码，运行时执行 |
| State | CO 的状态（如"完整"、"低配"），定义运行时可用参数 |
| Parameter | 运行时可修改的参数（Int、Float、Bool、Color、Projector 等） |
| Layout | 纹理打包策略，定义 UV 区域到运行时生成纹理的映射 |
| Macro Library | 可复用的子图表库 |

### 主要节点类型

| 节点 | 用途 |
|---|---|
| Object Node | CO 的根节点，定义对象名称、状态列表、组件设置 |
| Skeletal Mesh Node | 引入骨骼网格体，为每个 LOD/Section 生成输出引脚 |
| Material Section Node | 定义材质，自动从连接的网格体获取材质参数引脚 |
| Table Node | 从 DataTable/Struct 自动生成参数选项 |
| Group Node | 定义可附加子 CO 的插槽（如"护甲"插槽） |
| Modifier Nodes | 裁剪、变形、材质覆盖等修改器 |
| Switch/Variation Node | 条件分支，根据参数选择不同子图 |
| Macro Instance Node | 引用 Macro Library 中的可复用子图 |

### 编辑器面板

打开 CO 资产后，编辑器包含以下面板：

| 面板 | 功能 |
|---|---|
| Viewport | 实时预览当前参数组合的最终效果 |
| Graph | 可视化节点图，定义资产组合逻辑 |
| Details | 选中节点的属性面板 |
| Instance Properties | 实例参数调节面板（预览用） |
| Texture Analyzer | 分析运行时生成纹理的内存占用 |
| Performance Analyzer | 批量测试实例更新性能 |
| Code Viewer | 查看 Mutable 虚拟机字节码（调试用） |
| Tag Explorer | 浏览 CO 层级中所有标签 |

### 编译选项

| 选项 | 说明 |
|---|---|
| Optimization Level | 编译优化等级，影响生成速度与运行时质量 |
| Texture Compression | 纹理压缩策略（Fast / High Quality） |
| Embedded Data Limit | 嵌入数据大小限制 |

### 烘焙 (Baking)

将实例的运行时生成资产序列化到磁盘，用于制作宣传截图、LOD 回退资产等。

```
FCustomizableObjectEditorViewportClient::BakeInstance()
  → ScheduleCOCompilationForBaking()    // 编译 CO
  → ScheduleInstanceUpdateForBaking()   // 更新实例
  → BakeCustomizableObjectInstance()    // 序列化资产到磁盘
```

## 蓝图用法

Mutable 的核心 API 主要面向 C++ 和编辑器，蓝图暴露有限。以下是可蓝图调用的函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CompileCustomizableObjectSynchronously` | 同步编译 CO（仅编辑器） | `UCustomizableObjectEditorFunctionLibrary` |
| `NewCustomizableObject` | 创建新 CO 资产（仅编辑器） | `UCustomizableObjectEditorFunctionLibrary` |

### 编译状态枚举

```cpp
UENUM(BlueprintType)
enum class ECustomizableObjectCompilationState : uint8
{
    None,       // 未开始
    InProgress, // 编译中
    Completed,  // 完成
    Failed      // 失败
};
```

### 创建新 CO

```
// 蓝图：NewCustomizableObject
参数：
  - PackagePath: "/Game/Characters"     // 包路径
  - AssetName: "MyCustomizableObject"   // 资产名
  - ParentObject: (可选) 父 CO 引用
  - ParentGroupNode: (可选) 父 CO 中的 Group 节点名
```

## C++ 用法

### 头文件引入

```cpp
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "MuCO/CustomizableObjectSystem.h"
```

### 基本用法：创建和更新实例

```cpp
// 来源: 基于 CustomizableObjectInstanceEditor.h 和 FCustomizableObjectEditorViewportClient 的使用模式

// 1. 获取 CO 引用（在编辑器中通常通过资产引用获取）
UCustomizableObject* CustomizableObject = ...; // 加载或获取 CO 资产

// 2. 创建实例
UCustomizableObjectInstance* Instance = NewObject<UCustomizableObjectInstance>();
Instance->SetCustomizableObject(CustomizableObject);

// 3. 设置参数（示例：设置整数参数）
// Instance->SetIntParameter("HatType", 2);

// 4. 更新实例（异步生成最终资产）
// Instance->UpdateSkeletalMeshAsyncResult();

// 5. 监听更新完成
// 绑定 FObjectInstanceUpdatedDelegate 回调
```

### 编译 CO（编辑器时）

```cpp
// 来源: CustomizableObjectEditorFunctionLibrary.h
#include "MuCOE/CustomizableObjectEditorFunctionLibrary.h"

// 同步编译
ECustomizableObjectCompilationState State = 
    UCustomizableObjectEditorFunctionLibrary::CompileCustomizableObjectSynchronously(
        MyCustomizableObject,
        ECustomizableObjectOptimizationLevel::None,
        ECustomizableObjectTextureCompression::Fast,
        false  // bGatherReferences
    );

if (State == ECustomizableObjectCompilationState::Completed)
{
    UE_LOG(LogTemp, Log, TEXT("Compilation succeeded"));
}
```

### 进阶用法：烘焙实例到磁盘

```cpp
// 来源: CustomizableObjectInstanceBakingUtils.h

#include "MuCOE/CustomizableObjectInstanceBakingUtils.h"

// 1. 先确保 CO 已编译
// 2. 配置烘焙参数
FBakingConfiguration BakingConfig;
// BakingConfig.Prefix = TEXT("SKM_");
// BakingConfig.AssetPath = TEXT("/Game/BakedAssets/");
// BakingConfig.UserGivenName = TEXT("DefaultCharacter");

// 3. 执行烘焙
TMap<UPackage*, const FResourceBakingData> SavedPackages;
bool bSuccess = BakeCustomizableObjectInstance(
    *Instance,
    BakingConfig,
    false,  // bIsUnattendedExecution
    SavedPackages
);

if (bSuccess)
{
    // 保存所有标记的包
    for (auto& Pair : SavedPackages)
    {
        UPackage* Package = Pair.Key;
        // 保存到磁盘
    }
}
```

### 进阶用法：通过图遍历分析 CO 层级

```cpp
// 来源: GraphTraversal.h

#include "MuCOE/GraphTraversal.h"

// 获取 CO 的根节点
UCustomizableObjectNodeObject* RootNode = GetRootNode(MyCustomizableObject);

// 获取完整的 CO 层级中所有对象
TSet<UCustomizableObject*> AllObjects;
GraphTraversal::GetAllObjectsInGraph(MyCustomizableObject, AllObjects);

// 判断是否为根对象
bool bIsRoot = GraphTraversal::IsRootObject(*MyCustomizableObject);

// 获取根 CO（对于子对象）
UCustomizableObject* RootCO = GraphTraversal::GetRootObject(ChildCustomizableObject);

// 遍历节点
GraphTraversal::VisitNodes(*RootNode, [](UCustomizableObjectNode& Node)
{
    // 对每个节点执行操作
    UE_LOG(LogTemp, Log, TEXT("Node: %s"), *Node.GetNodeTitle(ENodeTitleType::FullTitle).ToString());
});
```

## Demo 示例

以下示例展示如何在编辑器工具中编译一个 CO 并创建预览实例。

```cpp
// MyCustomizableObjectTool.h
#pragma once

#include "CoreMinimal.h"
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"

class FMyCustomizableObjectTool
{
public:
    /** 编译 CO 并创建预览实例 */
    void CompileAndPreview(UCustomizableObject* InObject);
    
    /** 更新预览实例 */
    void UpdatePreview();

private:
    UPROPERTY()
    TObjectPtr<UCustomizableObject> CustomizableObject;
    
    UPROPERTY()
    TObjectPtr<UCustomizableObjectInstance> PreviewInstance;
    
    void OnInstanceUpdated(UCustomizableObjectInstance* Instance);
};
```

```cpp
// MyCustomizableObjectTool.cpp
#include "MyCustomizableObjectTool.h"
#include "MuCOE/CustomizableObjectEditorFunctionLibrary.h"

void FMyCustomizableObjectTool::CompileAndPreview(UCustomizableObject* InObject)
{
    if (!InObject)
    {
        UE_LOG(LogTemp, Error, TEXT("Invalid Customizable Object"));
        return;
    }
    
    CustomizableObject = InObject;
    
    // 编译 CO
    ECustomizableObjectCompilationState State = 
        UCustomizableObjectEditorFunctionLibrary::CompileCustomizableObjectSynchronously(
            CustomizableObject,
            ECustomizableObjectOptimizationLevel::None,
            ECustomizableObjectTextureCompression::Fast
        );
    
    if (State != ECustomizableObjectCompilationState::Completed)
    {
        UE_LOG(LogTemp, Error, TEXT("Compilation failed for %s"), 
            *CustomizableObject->GetName());
        return;
    }
    
    UE_LOG(LogTemp, Log, TEXT("Compilation succeeded, creating preview instance"));
    
    // 创建预览实例
    PreviewInstance = NewObject<UCustomizableObjectInstance>();
    PreviewInstance->SetCustomizableObject(CustomizableObject);
    
    // 绑定更新回调并触发更新
    PreviewInstance->UpdatedDelegate.AddRaw(this, 
        &FMyCustomizableObjectTool::OnInstanceUpdated);
    UpdatePreview();
}

void FMyCustomizableObjectTool::UpdatePreview()
{
    if (!PreviewInstance)
    {
        return;
    }
    
    // 触发实例异步更新
    // PreviewInstance->UpdateSkeletalMeshAsyncResult();
}

void FMyCustomizableObjectTool::OnInstanceUpdated(UCustomizableObjectInstance* Instance)
{
    UE_LOG(LogTemp, Log, TEXT("Preview instance updated successfully"));
    
    // 此时 Instance 持有生成的 SkeletalMesh 和材质
    // 可以将其附加到 Actor 上进行预览
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MutableRuntime` | Mutable 虚拟机运行时，执行编译后的 Model 生成最终资产 |
| `MutableTools` | Mutable 图表编译工具，将 UE 节点图编译为虚拟机字节码 |
| `DerivedDataCache` | 编译产物的派生数据缓存（DDC），避免重复编译 |
| `MessageLog` | 编译过程中的日志和错误报告 |

**说明**：`CustomizableObject` 模块依赖 `UnrealEd` 和 `MutableTools`，表明其 Editor 类型属性（虽然标记为 Runtime，实际在编辑器和 Cook 时使用）。对于纯运行时使用，只需依赖 `MutableRuntime`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复多个同名骨骼网格体导致几何体重复的问题 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复 UV Mask 裁剪操作未加载正确的 mask mip 级别 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. | 修复纹理参数使用错误方法计算 LODBias |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过 ClothingAssetBase 接口支持更多服装资产类型 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较 PassthroughObject 时可能出现的数据竞争 |

### 维护评价

**活跃维护中** ✅

- **创建时间**：2024-09-05 从 Experimental 升级为 Beta（实际开发历史更长，此前在 Experimental 目录下）
- **更新频率**：最近一周内有 5 次 commit，且均为实质性的 bug 修复，维护非常活跃
- **版本状态**：Beta 阶段（`IsBetaVersion=true`，默认不启用），但已在生产环境使用
- **代码规模**：1206 个源文件，是 UE 中规模最大的插件之一
- **已知限制**：
  - Beta 状态，API 可能在后续版本中发生变化
  - 编译过程对复杂 CO 可能耗时较长
  - 某些高级功能（如 LiveUpdate 模式）会显著增加内存使用
- **推荐程度**：**推荐使用**。对于需要角色自定义/装备换装系统的项目，Mutable 是 UE 官方提供的唯一成熟方案。Beta 状态主要意味着 API 可能有变化，核心功能已经足够稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://github.com/anticto/Mutable-Documentation/wiki)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)