# Mutable Asset User Data

> Adds Asset User Data type and operations.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableAssetUserData` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-06 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutableAssetUserData) | |

## 用途

该插件是 **Mutable** 程序化资产生成系统的一个扩展。它解决了一个特定问题：在使用 Mutable 程序化生成网格（Mesh）资产时，如何自动地、可配置地为生成的资产附加 `UAssetUserData`。

`UAssetUserData` 是 UE 中用于向资产附加自定义数据的通用机制（例如，动画蓝图引用、物理资产等）。在程序化生成流程中，手动管理这些数据的附加是繁琐且容易出错的。此插件通过提供一个专用的 **Mutable 外部操作（External Operation）**，允许用户在 Mutable 图表中定义规则，将特定的 `UAssetUserData` 实例附加到生成的网格资产上，从而实现自动化和数据驱动的资产配置。

## 使用场景

- 你正在使用 **Mutable** 系统程序化生成角色或装备的网格。
- 生成的网格需要自动附加特定的 `UAssetUserData`，例如：
    - 一个指向特定动画蓝图的引用。
    - 物理资产配置。
    - 自定义的渲染或碰撞数据。
- 你希望在 Mutable 图表中可视化地配置这些附加规则，而不是在生成后通过代码或手动操作完成。

## 蓝图用法

该插件主要通过其定义的 **结构体** 和 **外部操作** 与蓝图系统交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FMutableAssetUserData` | 一个蓝图可用的结构体，用于包装一个 `UAssetUserData` 对象指针。可以在蓝图中创建、传递和操作此结构体。 | `FMutableAssetUserData` |
| `FMeshAddAssetUserData` | 一个 **Mutable 外部操作**。在 Mutable 编辑器中使用，定义如何将 `FMutableAssetUserData` 中的数据附加到输入的网格资产上。 | `FMeshAddAssetUserData` |

### 使用示例（蓝图描述）

1.  **在蓝图中创建数据**：在蓝图图表中，使用 `Make MutableAssetUserData` 节点创建一个 `FMutableAssetUserData` 结构体。将其 `AssetUserData` 属性设置为一个具体的 `UAssetUserData` 对象（例如，通过 `Create Asset User Data` 节点创建或从资产引用获取）。
2.  **在 Mutable 图表中使用**：在 **Mutable** 的对象编辑器或图表中，找到“外部操作”列表。添加 `Mesh Add Asset User Data` 操作。将步骤1中创建的蓝图变量（或直接创建的 `FMutableAssetUserData` 实例）连接到该操作的 `InputAssetUserData` 引脚。将需要附加数据的网格资产连接到 `InputMesh` 引脚。该操作的输出即为附加了用户数据的网格。

## C++ 用法

### 头文件引入

```cpp
#include "MutableAssetUserData.h"
#include "MeshAddAssetUserData.h"
```

### 基本用法

该插件的核心是定义了两个结构体，通常用于与 Mutable 系统集成，而非直接在游戏逻辑中使用。

```cpp
// 创建一个 FMutableAssetUserData 实例并设置其数据
FMutableAssetUserData MyUserData;
MyUserData.AssetUserData = NewObject<UMyCustomAssetUserData>(GetTransientPackage());

// FMeshAddAssetUserData 作为 Mutable 的外部操作，其生命周期和调用由 Mutable 系统管理。
// 通常，你需要继承或配置它，而不是直接实例化。
```

### 进阶用法

要创建自定义的、类似 `FMeshAddAssetUserData` 的外部操作，你需要继承 `UE::Mutable::FExternalOperation` 并实现其虚函数。

```cpp
// 假设你要创建一个添加自定义数据的外部操作
USTRUCT()
struct FMyCustomExternalOperation : public UE::Mutable::FExternalOperation
{
    GENERATED_BODY()

    // 定义操作需要的输入
    virtual TArray<TPair<FText, const UScriptStruct*>> GetInputs() const override
    {
        return { { NSLOCTEXT("MyOp", "MeshIn", "Input Mesh"), FMutableMesh::StaticStruct() } };
    }

    // 定义操作的输出
    virtual TPair<FText, const UScriptStruct*> GetOutput() const override
    {
        return { NSLOCTEXT("MyOp", "MeshOut", "Output Mesh"), FMutableMesh::StaticStruct() };
    }

    // 实现操作逻辑
    virtual void Evaluate(UE::Mutable::FContext& Context) const override
    {
        // 从 Context 获取输入网格
        const FMutableMesh* InputMesh = Context.GetInput<FMutableMesh>(0);
        if (!InputMesh) return;

        // 创建输出网格（通常基于输入网格）
        FMutableMesh OutputMesh = *InputMesh;

        // ... 在这里对 OutputMesh 进行修改，例如附加你的自定义数据 ...

        // 设置输出
        Context.SetOutput(0, OutputMesh);
    }
};
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何定义一个简单的、用于添加静态用户数据的外部操作。

**MyStaticUserDataOperation.h**
```cpp
#pragma once

#include "MuR/External/Operation.h"
#include "MyStaticUserDataOperation.generated.h"

class UMyStaticUserData;

USTRUCT()
struct FMyStaticUserDataOperation : public UE::Mutable::FExternalOperation
{
    GENERATED_BODY()

    // 输入：一个网格
    static const FText TextInputMesh;
    // 输入：要附加的静态用户数据资产
    static const FText TextInputUserDataAsset;

    virtual TArray<TPair<FText, const UScriptStruct*>> GetInputs() const override;
    virtual TPair<FText, const UScriptStruct*> GetOutput() const override;
    virtual void Evaluate(UE::Mutable::FContext& Context) const override;
};
```

**MyStaticUserDataOperation.cpp**
```cpp
#include "MyStaticUserDataOperation.h"
#include "MuR/Mesh.h"
#include "MuR/External/Context.h"
#include "Engine/AssetUserData.h"

const FText FMyStaticUserDataOperation::TextInputMesh = NSLOCTEXT("MyOp", "Mesh", "Input Mesh");
const FText FMyStaticUserDataOperation::TextInputUserDataAsset = NSLOCTEXT("MyOp", "UserData", "User Data Asset");

TArray<TPair<FText, const UScriptStruct*>> FMyStaticUserDataOperation::GetInputs() const
{
    return {
        { TextInputMesh, FMutableMesh::StaticStruct() },
        { TextInputUserDataAsset, FSoftObjectPath::StaticStruct() } // 假设输入是资产路径
    };
}

TPair<FText, const UScriptStruct*> FMyStaticUserDataOperation::GetOutput() const
{
    return { NSLOCTEXT("MyOp", "OutMesh", "Output Mesh"), FMutableMesh::StaticStruct() };
}

void FMyStaticUserDataOperation::Evaluate(UE::Mutable::FContext& Context) const
{
    // 1. 获取输入网格
    const FMutableMesh* InputMesh = Context.GetInput<FMutableMesh>(0);
    if (!InputMesh) return;

    // 2. 获取用户数据资产路径
    const FSoftObjectPath* UserDataPath = Context.GetInput<FSoftObjectPath>(1);
    if (!UserDataPath || !UserDataPath->IsValid()) return;

    // 3. 加载资产（注意：在实际的 Mutable 操作中，资源加载策略需要仔细考虑）
    UAssetUserData* UserData = Cast<UAssetUserData>(UserDataPath->TryLoad());
    if (!UserData) return;

    // 4. 创建输出网格（复制输入）
    FMutableMesh OutputMesh = *InputMesh;

    // 5. 将用户数据附加到网格的资产用户数据列表中
    // 注意：FMutableMesh 可能没有直接的 AssetUserData 列表。
    // 实际实现可能需要通过其他方式（如修改生成的 UStaticMesh 或 USkeletalMesh）。
    // 这里仅为逻辑演示。
    // OutputMesh.AssetUserData.Add(UserData);

    // 6. 设置输出
    Context.SetOutput(0, OutputMesh);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Mutable` | 核心依赖。提供 `FExternalOperation` 基类、`FContext` 以及程序化资产生成的核心框架。 |

## 维护状态

### 近期更新

- 2026-03-25 `6d0250b3` [Mutable] 修复了因指向私有成员而无法保存 MutableAssetUserData 默认值的问题。
- 2026-03-09 `3b7441b0` [Mutable] 将 Asset User Data 暴露给蓝图。
- 2026-03-06 `c355e4ce` [Mutable] 添加了缺失的 Mutable Asset User Data 插件文件。

### 维护评价

- **创建时间**：2026年3月，是一个非常新的插件。
- **最近更新**：在创建后的一周内有多次提交，主要是功能添加（暴露给蓝图）和关键bug修复（保存问题、崩溃修复）。
- **活跃度**：**活跃维护中**。作为实验性插件，正处于快速开发和问题修复阶段。
- **已知限制**：标记为 `IsExperimentalVersion: true`，意味着API和功能可能不稳定，未来版本可能发生破坏性更改。
- **推荐使用**：**推荐在实验性项目或需要快速原型验证的场景中使用**。对于生产环境，需谨慎评估其稳定性，并准备好应对未来可能的API变更。它是Mutable生态系统的一个有价值的补充，解决了资产用户数据附加的自动化痛点。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutableAssetUserData)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutableAssetUserData/Tests) (如果存在)