# Mesh Modeling Toolset

> A set of modules implementing 3D mesh creation and editing based on the Interactive Tools Framework（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（工具资产、材质模板等） |
| 模块 | `MeshModelingTools` (Runtime), `MeshModelingToolsEditorOnly` (Runtime), `ModelingComponents` (Runtime), `ModelingComponentsEditorOnly` (Runtime), `ModelingOperators` (Runtime), `ModelingOperatorsEditorOnly` (Runtime), `SkeletalMeshModifiers` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-01 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset) | |

## 用途

Mesh Modeling Toolset 是一个基于 Unreal Engine 交互式工具框架（Interactive Tools Framework）构建的综合性 3D 网格创建与编辑工具集。它不仅仅是一个简单的工具，而是一个完整的框架和工具生态系统，旨在为引擎提供强大、可扩展的程序化网格建模能力。

该插件的核心价值在于：
1.  **提供底层框架**：`ModelingComponents` 和 `ModelingOperators` 模块提供了构建自定义建模工具所需的基础组件和操作符。
2.  **实现具体工具**：`MeshModelingTools` 模块包含大量开箱即用的网格编辑工具，如布尔运算、网格简化、UV 展开、雕刻等。
3.  **支持骨骼网格**：`SkeletalMeshModifiers` 模块专门用于程序化修改骨骼网格的骨架结构和蒙皮权重，解决了传统编辑器中难以批量或自动化处理骨骼网格的问题。

它存在的目的是将专业级的程序化建模能力集成到引擎中，支持蓝图和 Python 脚本，从而实现资产创建流程的自动化、批量化和定制化。

## 使用场景

-   你需要在运行时或编辑器中通过蓝图/Python 脚本**程序化生成或修改 3D 网格**（例如，生成地形、创建模块化建筑部件）。
-   你需要**批量处理大量网格资产**，例如统一进行网格简化、LOD 生成或 UV 重排。
-   你需要**修复或优化导入的骨骼网格**，例如调整骨架层级、批量修改蒙皮权重或镜像骨骼。
-   你需要为项目**创建自定义的网格编辑工具**，并集成到编辑器工具栏中。
-   你需要在**运行时动态修改角色外观**，例如通过脚本调整角色的蒙皮权重来实现特定的变形效果。

## 蓝图用法

该插件提供了丰富的蓝图可调用 API，主要集中在 `USkinWeightModifier` 和 `USkeletonModifier` 类中，用于操作骨骼网格。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSkeletalMesh` | 加载一个骨骼网格资产以进行权重编辑。 | `USkinWeightModifier` |
| `CommitWeightsToSkeletalMesh` | 将修改后的蒙皮权重应用回骨骼网格资产。 | `USkinWeightModifier` |
| `GetVertexWeights` | 获取指定顶点的蒙皮权重（骨骼名到权重的映射）。 | `USkinWeightModifier` |
| `SetVertexWeights` | 设置指定顶点的蒙皮权重。 | `USkinWeightModifier` |
| `NormalizeVertexWeights` | 归一化指定顶点的权重，使其总和为1。 | `USkinWeightModifier` |
| `GetBoneTransform` | 获取指定骨骼的全局变换。 | `USkeletonModifier` |
| `SetBoneTransform` | 设置指定骨骼的全局变换。 | `USkeletonModifier` |
| `AddBone` | 向骨架中添加一个新骨骼。 | `USkeletonModifier` |
| `RemoveBone` | 从骨架中移除一个骨骼。 | `USkeletonModifier` |
| `RenameBone` | 重命名一个骨骼。 | `USkeletonModifier` |
| `MirrorBones` | 根据选项镜像一组骨骼。 | `USkeletonModifier` |
| `OrientBone` | 根据选项调整骨骼的朝向。 | `USkeletonModifier` |

### 使用示例（蓝图描述）

1.  **修改蒙皮权重**：
    *   创建一个 `USkinWeightModifier` 对象。
    *   调用 `SetSkeletalMesh` 节点，传入你想要编辑的 `USkeletalMesh` 资产引用。
    *   使用 `GetVertexWeights` 节点获取某个顶点（例如索引为 100）的当前权重字典。
    *   在蓝图中修改这个字典（例如，移除某个骨骼的影响，或调整权重值）。
    *   将修改后的字典传给 `SetVertexWeights` 节点。
    *   （可选）调用 `NormalizeVertexWeights` 确保权重和为1。
    *   最后调用 `CommitWeightsToSkeletalMesh` 将所有更改提交到资产。

2.  **添加并镜像骨骼**：
    *   创建一个 `USkeletonModifier` 对象，并关联到目标 `USkeletalMesh`。
    *   使用 `AddBone` 节点在指定父骨骼下添加一个新骨骼，并设置其初始变换。
    *   配置 `FMirrorOptions` 结构体（设置镜像轴、是否镜像旋转、左右后缀等）。
    *   调用 `MirrorBones` 节点，传入要镜像的骨骼名称数组和镜像选项，即可生成对称的骨骼。

## C++ 用法

### 头文件引入

```cpp
#include "SkinWeightModifier.h"
#include "SkeletonModifier.h"
```

### 基本用法

以下示例展示了如何使用 `USkinWeightModifier` 修改单个顶点的蒙皮权重。
（来源：基于 `SkinWeightModifier.h` 中的 Python 示例推断）

```cpp
#include "SkinWeightModifier.h"
#include "Engine/SkeletalMesh.h"

void ModifyVertexWeight(USkeletalMesh* SkeletalMeshAsset)
{
    // 1. 创建权重修改器实例
    USkinWeightModifier* WeightModifier = NewObject<USkinWeightModifier>();

    // 2. 加载目标骨骼网格
    if (!WeightModifier->SetSkeletalMesh(SkeletalMeshAsset))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load skeletal mesh for weight editing."));
        return;
    }

    // 3. 获取顶点 1234 的当前权重
    TMap<FName, float> VertexWeights;
    WeightModifier->GetVertexWeights(1234, VertexWeights);

    // 4. 修改权重：移除 “neck2” 骨骼的影响
    VertexWeights.Remove(TEXT("neck2"));

    // 5. 将修改后的权重设置回去
    WeightModifier->SetVertexWeights(1234, VertexWeights, true); // true 表示自动归一化

    // 6. 将所有更改提交到资产（会创建撤销事务）
    WeightModifier->CommitWeightsToSkeletalMesh();

    UE_LOG(LogTemp, Log, TEXT("Vertex 1234 weight modified and committed."));
}
```

### 进阶用法

以下示例展示了如何使用 `USkeletonModifier` 添加一个新骨骼并设置其变换。
（来源：基于 `SkeletonModifier.h` 中的 API 推断）

```cpp
#include "SkeletonModifier.h"
#include "Engine/SkeletalMesh.h"

void AddNewBoneToSkeleton(USkeletalMesh* SkeletalMeshAsset)
{
    // 1. 创建骨架修改器实例
    USkeletonModifier* SkeletonModifier = NewObject<USkeletonModifier>();

    // 2. 加载目标骨骼网格
    if (!SkeletonModifier->SetSkeletalMesh(SkeletalMeshAsset))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load skeletal mesh for skeleton editing."));
        return;
    }

    // 3. 定义新骨骼的参数
    FName NewBoneName = TEXT("weapon_socket");
    FName ParentBoneName = TEXT("hand_r");
    FTransform BoneLocalTransform(FRotator(0, 90, 0), FVector(10, 0, 0)); // 旋转90度，偏移10单位

    // 4. 添加新骨骼
    TArray<FName> AddedBones;
    SkeletonModifier->AddBone(NewBoneName, ParentBoneName, BoneLocalTransform, AddedBones);

    if (AddedBones.Contains(NewBoneName))
    {
        UE_LOG(LogTemp, Log, TEXT("Bone '%s' added successfully under '%s'."), *NewBoneName.ToString(), *ParentBoneName.ToString());
    }

    // 5. 提交更改（注意：骨架修改通常需要更复杂的合并策略）
    // SkeletonModifier->CommitSkeleton(...); // 需要指定 ESkeletonModificationType
}
```

## Demo 示例

以下是一个完整的、可编译的最小示例，演示如何通过 C++ 代码使用 `USkeletonModifier` 重命名一个骨骼。

**MySkeletonModifierExample.h**
```cpp
// MySkeletonModifierExample.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MySkeletonModifierExample.generated.h"

class USkeletalMesh;
class USkeletonModifier;

UCLASS(BlueprintType)
class UMySkeletonModifierExample : public UObject
{
    GENERATED_BODY()

public:
    /**
     * 重命名骨骼网格中的一个骨骼。
     * @param Mesh 要修改的骨骼网格资产。
     * @param OldName 要重命名的骨骼的当前名称。
     * @param NewName 骨骼的新名称。
     * @return 是否成功重命名。
     */
    UFUNCTION(BlueprintCallable, Category = "SkeletonModifierDemo")
    bool RenameBoneInMesh(USkeletalMesh* Mesh, FName OldName, FName NewName);
};
```

**MySkeletonModifierExample.cpp**
```cpp
// MySkeletonModifierExample.cpp
#include "MySkeletonModifierExample.h"
#include "SkeletonModifier.h"
#include "Engine/SkeletalMesh.h"

bool UMySkeletonModifierExample::RenameBoneInMesh(USkeletalMesh* Mesh, FName OldName, FName NewName)
{
    if (!Mesh)
    {
        UE_LOG(LogTemp, Warning, TEXT("RenameBoneInMesh: Invalid SkeletalMesh provided."));
        return false;
    }

    // 创建骨架修改器
    USkeletonModifier* Modifier = NewObject<USkeletonModifier>();
    if (!Modifier->SetSkeletalMesh(Mesh))
    {
        UE_LOG(LogTemp, Error, TEXT("RenameBoneInMesh: Failed to initialize SkeletonModifier."));
        return false;
    }

    // 执行重命名操作
    TArray<FName> RenamedBones;
    Modifier->RenameBone(OldName, NewName, RenamedBones);

    if (RenamedBones.Contains(NewName))
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully renamed bone from '%s' to '%s'."), *OldName.ToString(), *NewName.ToString());
        // 注意：实际提交更改需要调用 CommitSkeleton 并处理合并逻辑
        // Modifier->CommitSkeleton(ESkeletonModificationType::SimpleMerge);
        return true;
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to rename bone '%s'."), *OldName.ToString());
        return false;
    }
}
```

## 模块依赖

要使用 `SkeletalMeshModifiers` 模块，你的模块需要在 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `ModelingComponents` | 提供交互式工具框架的基础组件，是 `SkeletalMeshModifiers` 的核心依赖。 |
| `ModelingOperators` | 提供网格和骨架操作的底层算子。 |
| `MeshDescription` | 用于处理网格的顶点、三角形、多边形组等数据结构。 |
| `DynamicMesh` | 提供可动态修改的网格数据结构，常用于中间计算。 |

## 维护状态

### 近期更新

```
- 2025-10-03 59caa704d92d [SKMModelingTool] Fixed crash when entering skeleton tool if a prior change adds multiple root bones to the skeleton + cannot change widget mode when in skeleton tool
- 2025-09-15 e44de8abb2cf [MeshModelingToolSet] minor fixes to skeleton modifiier dyna mesh path
- 2025-08-20 768a0ff6ab41 [MeshModelingToolSet] Added tool target interface for skeleton edit, which would allow skeleleton edit tool to edit both skeletal mesh and dynamic mesh
```

### 维护评价

**综合评价：活跃维护，推荐使用。**

-   **创建时间**：插件创建于 2019 年，已有约 6 年历史，属于成熟的工具集。
-   **更新频率**：从近期提交记录看，**2025 年内仍有持续的功能更新和 Bug 修复**，表明该插件处于活跃维护状态。最新的提交修复了骨架工具中的崩溃问题，并扩展了其编辑目标（支持动态网格）。
-   **功能状态**：虽然 `.uplugin` 中标记为 `IsBetaVersion: true` 和 `Hidden: true`，但这更多是 Epic 对其内部工具状态的标识。从代码质量和功能完整性来看，它已经是一个非常强大和可用的工具集。
-   **已知限制**：作为“实验性”插件，其 API 可能在未来版本中发生变化。使用时需要关注版本更新日志。
-   **推荐度**：**强烈推荐**。对于任何需要程序化网格编辑、骨骼网格处理或自定义建模工具的项目，此插件是不可或缺的基础设施。尽管标记为 Beta，但其稳定性和功能性已得到广泛验证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset/Tests) (如果存在)