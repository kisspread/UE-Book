# MetaHuman Creator

> MetaHuman Character Asset Creator and Editor.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、纹理、Groom资产、服装资产、动画蓝图） |
| 模块 | `MetaHumanCharacter` (Runtime), `MetaHumanCharacterEditor` (Runtime), `MetaHumanCharacterMigrationEditor` (Runtime), `MetaHumanCharacterPalette` (Runtime), `MetaHumanCharacterPaletteEditor` (Runtime), `MetaHumanDefaultEditorPipeline` (Runtime), `MetaHumanDefaultPipeline` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter) | |

## 用途

MetaHumanCharacter 插件提供了一套完整的、可扩展的流水线（Pipeline）系统，用于在 Unreal Engine 中创建、编辑和组装逼真的数字人类（MetaHuman）。它不仅仅是一个资产导入工具，而是一个完整的角色构建框架。

该插件的核心是解决“如何将分散的数字人类组件（面部网格、身体网格、发型、服装、材质等）高效、一致地组装成一个可交互、可动画的完整角色”的问题。它通过定义标准化的“流水线”（Pipeline）来管理从原始资产到最终可运行角色的整个构建过程，支持运行时动态修改角色外观（如更换发型、服装、调整材质参数），并提供了从旧版云端 MetaHuman Creator 工具迁移的路径。

## 使用场景

- 你需要为游戏或虚拟制片项目创建大量外观各异但基础结构一致的逼真数字人类角色。
- 你需要在运行时（Runtime）动态更换角色的发型、胡须、服装或调整肤色、发色等材质参数。
- 你正在使用旧版的 MetaHuman Creator 云端工具生成资产，并希望将其无缝迁移到 UE5 的本地工作流中。
- 你需要一个可扩展的框架来管理复杂的角色资产依赖关系和构建逻辑。

## 蓝图用法

该插件的蓝图 API 主要集中在运行时应用构建结果和修改材质参数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Apply Groom Assembly Output To Groom Component` | 将构建好的发型（Groom）数据（包括绑定和材质覆盖）应用到一个 `UGroomComponent` 上。 | `UMetaHumanGroomPipeline` |
| `Set Instance Parameters` | 在运行时，根据提供的参数上下文和参数包（PropertyBag），更新材质实例的参数（如颜色、粗糙度等）。 | `UMetaHumanGroomPipeline`, `UMetaHumanSkeletalMeshPipeline`, `UMetaHumanOutfitPipeline` |

### 使用示例（蓝图描述）

1.  **应用发型**：假设你已经通过 C++ 或其他方式获得了 `FMetaHumanGroomPipelineAssemblyOutput` 结构体数据（包含发型绑定和材质信息）。在蓝图中，你可以拖拽出 `Apply Groom Assembly Output To Groom Component` 节点，将输出结构体连接到 `GroomAssemblyOutput` 引脚，并将场景中的 `GroomComponent` 引用连接到 `GroomComponent` 引脚，即可完成发型的最终应用。
2.  **运行时修改发色**：要修改角色的发色，你需要获取到对应发型 Pipeline 的实例。然后，使用 `Set Instance Parameters` 节点。你需要提供一个 `ParameterContext`（通常由 Pipeline 内部管理）和一个包含新参数值的 `FInstancedPropertyBag`（例如，设置 `hairMelanin` 和 `hairRedness` 的值）。执行该节点后，关联的材质实例参数会立即更新。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanDefaultPipeline.h"
#include "Item/MetaHumanGroomPipeline.h"
#include "Item/MetaHumanSkeletalMeshPipeline.h"
#include "Item/MetaHumanOutfitPipeline.h"
```

### 基本用法

以下示例展示了如何获取并配置一个默认的 MetaHuman 流水线。流水线本身是抽象的，需要通过蓝图子类来实例化并引用具体内容资产。

```cpp
// 来源：基于 MetaHumanDefaultPipeline.h 和 MetaHumanDefaultPipelineBase.h 的用法推断
#include "MetaHumanDefaultPipeline.h"
#include "MetaHumanCharacterPipelineSpecification.h"

// 假设你有一个 UMetaHumanDefaultPipeline 的蓝图子类实例
UMetaHumanDefaultPipeline* MyPipeline = GetMyPipelineInstance();

// 获取流水线的规格说明，了解它支持哪些插槽（如面部、身体、发型等）
const UMetaHumanCharacterPipelineSpecification* Spec = MyPipeline->GetSpecification();
if (Spec)
{
    UE_LOG(LogTemp, Log, TEXT("Pipeline supports %d slots."), Spec->GetSlots().Num());
}

// 在编辑器中，可以设置默认的编辑器流水线（用于预览和编辑）
#if WITH_EDITOR
MyPipeline->SetDefaultEditorPipeline();
#endif
```

### 进阶用法

以下示例展示了如何使用流水线来组装一个完整的 MetaHuman 角色。这通常由 `UMetaHumanCollection` 管理，但核心逻辑在 `AssembleCollection` 中。

```cpp
// 来源：基于 MetaHumanDefaultPipelineBase.h 中 AssembleCollection 的签名和 FMetaHumanDefaultAssemblyOutput 结构
#include "MetaHumanDefaultPipelineBase.h"
#include "MetaHumanCollection.h"
#include "MetaHumanCharacterGeneratedAssets.h"

// 假设你有一个已配置好的 MetaHumanCollection 和 Pipeline
const UMetaHumanCollection* MyCollection = GetMyCollection();
UMetaHumanDefaultPipelineBase* MyPipeline = GetMyPipeline();

// 定义组装完成的回调
FOnAssemblyComplete OnComplete;
OnComplete.BindLambda([](const FInstancedStruct& InOutput)
{
    // 从输出中提取组装结果
    const FMetaHumanDefaultAssemblyOutput& AssemblyOutput = InOutput.Get<FMetaHumanDefaultAssemblyOutput>();
    
    // 现在你可以使用 AssemblyOutput.FaceMesh, AssemblyOutput.BodyMesh, AssemblyOutput.Hair 等
    // 来设置你的角色 Actor
    UE_LOG(LogTemp, Log, TEXT("MetaHuman assembled. Face mesh: %s"), *GetNameSafe(AssemblyOutput.FaceMesh));
});

// 定义组装输入（例如，选择哪个角色变体）
FInstancedStruct AssemblyInput;
// ... 填充 AssemblyInput ...

// 开始异步组装过程
MyPipeline->AssembleCollection(
    MyCollection,
    EMetaHumanCharacterPaletteBuildQuality::High, // 构建质量
    {}, // 插槽选择数据
    AssemblyInput,
    GetTransientPackage(), // 生成资产的外部对象
    OnComplete
);
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何创建一个自定义的 Groom Pipeline 子类并应用其构建输出。

**MyCustomGroomPipeline.h**
```cpp
#pragma once

#include "Item/MetaHumanGroomPipeline.h"
#include "MyCustomGroomPipeline.generated.h"

UCLASS()
class UMyCustomGroomPipeline : public UMetaHumanGroomPipeline
{
    GENERATED_BODY()

public:
    // 可以重写函数来自定义行为，例如修改默认材质参数
    virtual void SetDefaultEditorPipeline() override;
};
```

**MyCustomGroomPipeline.cpp**
```cpp
#include "MyCustomGroomPipeline.h"
#include "GroomComponent.h"

void UMyCustomGroomPipeline::SetDefaultEditorPipeline()
{
    Super::SetDefaultEditorPipeline();
    
    // 在这里可以添加自定义的编辑器流水线设置逻辑
    UE_LOG(LogTemp, Log, TEXT("Custom Groom Pipeline editor pipeline set."));
}

// 使用示例（在另一个类中）
void ApplyCustomGroom(UGroomComponent* TargetComponent)
{
    // 假设我们通过某种方式获得了构建输出
    FMetaHumanGroomPipelineAssemblyOutput GroomOutput;
    // ... 填充 GroomOutput，例如从资产加载 ...
    
    // 使用静态函数应用
    UMetaHumanGroomPipeline::ApplyGroomAssemblyOutputToGroomComponent(GroomOutput, TargetComponent);
}
```

## 模块依赖

从代码结构推断，使用此插件的核心功能（如 `MetaHumanDefaultPipeline`）需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanCharacter` | 提供核心的 MetaHuman 角色数据结构和接口。 |
| `MetaHumanCharacterPalette` | 提供调色板（Palette）系统，用于管理角色资产变体和组合。 |
| `MetaHumanDefaultEditorPipeline` | 提供默认的编辑器端流水线实现，用于资产预览和编辑。 |
| `ChaosOutfitAsset` | 提供基于 Chaos 物理系统的服装资产支持。 |
| `GeometryFramework` | 可能用于处理几何体相关的操作（如隐藏面映射）。 |

## 维护状态

### 近期更新

```
- 5eb1962481de [UEMHC] Re-enabled baked grooms by baking them to a separate texture ahead of the skin material bake. This saves 2 SRVs in the skin material and gets it back below the limit.
- 57e640423ca0 [UEMHC] Groom material instances are now generated with deterministic names. This fixes an issue where unique assets were being created each time the MH was assembled.
- f4642186721c [UEMHC] Remove switching hair cards off and on while applying the groom assets to the editor preview actor, as it's no longer needed and is causing crashes
```

### 维护评价

- **创建时间**：插件创建于 2025 年 3 月，非常新。
- **更新频率**：从提供的 git 历史看，近期有持续的提交，主要集中在修复 Groom（发型）相关的材质和组装问题，表明开发团队正在积极修复 bug 和优化性能。
- **活跃度**：**活跃维护中**。作为 Epic 官方支持的 MetaHuman 核心工具链的一部分，预计会持续更新以支持新功能和引擎版本。
- **已知限制**：插件标记为 **实验性（IsBetaVersion=true）** 且 **默认未启用（EnabledByDefault=false）**，这意味着其 API 和功能在未来版本中可能发生不兼容的变更。目前主要面向愿意尝试前沿功能的开发者。
- **推荐使用**：如果你正在开发需要高质量数字人类的项目，并且愿意接受实验性功能的潜在风险，那么强烈推荐使用此插件。它是 Epic 官方提供的最完整、最集成的 MetaHuman 解决方案。对于生产环境，建议密切关注其版本更新和稳定性说明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter/Tests)