# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | 混沌肉体模拟 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、模板资源） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

Chaos Flesh 是 UE5 混沌物理系统的一部分，专门用于模拟生物软组织的力学行为。它基于四面体网格（tetrahedral mesh）实现了可变形体（deformable body）的物理仿真，可用于制作肌肉、脂肪、皮肤等柔软组织的动态效果，比传统骨骼蒙皮（skinning）或简单弹簧质点系统更真实。

该插件提供了一套完整的资产管线：从导入网格、生成四面体、绑定骨骼驱动，到运行时物理求解和渲染。编辑器模块（`ChaosFleshEditor`）则提供了资产创建、缩略图预览、属性自定义面板以及导入导出等工具。

## 使用场景

- **角色肌肉变形**：为游戏或影视角色添加真实的肌肉颤动与挤压效果，例如奔跑时胸肌的晃动、腹部压缩等。
- **生物体仿真**：模拟怪物的触手、水母的伞盖、史莱姆的弹跳等需要体积保持的软体运动。
- **医疗/科学可视化**：对组织力学行为进行预览与验证，辅助医学模拟或生物力学研究。
- **交互式解压玩具**：制作可实时捏揉、拉扯的 3D 软体，提升沉浸感。

## 蓝图用法

当前版本主要通过 **C++ 命令** 和 **Dataflow 图表** 驱动，未直接暴露蓝图可调用函数。如需在蓝图中使用，建议通过自定义 C++ 功能暴露接口，或借助 ChaosFleshEngine 模块中的 `UFleshComponent`（该类可能包含部分属性和事件）。

| 节点 | 说明 | 所在类 |
|---|---|---|
| （暂无） | 蓝图暴露接口尚在开发中 | — |

> 提示：你可以通过 `FleshComponent` 的 `UChaosFleshSimulationProperties` 等属性在细节面板调节物理参数，但这些并非蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosFlesh/ChaosFleshEditorPlugin.h"
#include "ChaosFlesh/Cmd/ChaosFleshCommands.h"
#include "ChaosFlesh/Cmd/FleshAssetConversion.h"
```

### 基本用法

#### 激活编辑器命令

```cpp
// 在控制台或自定义工具栏中调用
FChaosFleshCommands::ImportFile(Args, World);
FChaosFleshCommands::FindQualifyingTetrahedra(Args, World);
FChaosFleshCommands::CreateGeometryCache(Args, World);
```

- `ImportFile`：通过文件对话框导入 `.tet` / `.geo` 网格（当前暂未启用）。
- `FindQualifyingTetrahedra`：根据顶点坐标、体元质量等条件筛选四面体，并可隐藏低质量元素。
- `CreateGeometryCache`：将已缓存的肉体模拟结果烘焙为 GeometryCache 资产，便于回放或导出。

参考源码路径：`Engine/Plugins/Experimental/ChaosFlesh/Source/ChaosFleshEditor/Public/ChaosFlesh/Cmd/ChaosFleshCommands.h`

#### 导入四面体网格（C++）

```cpp
#include "ChaosFlesh/Cmd/FleshAssetConversion.h"

FFleshAssetConversion Converter;
FString FilePath = "/Game/Models/arm.tet";
TUniquePtr<FFleshCollection> Collection = Converter.ImportTetFromFile(FilePath);
if (Collection)
{
    // 将 FFleshCollection 转换为 UFleshAsset
    // （参考内部实现，通常需要创建资产对象并赋值）
}
```

### 进阶用法

#### 自定义 Dataflow 节点（ChaosFleshNodes 模块）

`ChaosFleshNodes` 模块提供了用于生成四面体、创建绑定等操作的 Dataflow 节点。你可以在 Dataflow 图表中组合这些节点，实现从输入网格到物理体的完整管线。例如：

- **`ComputeFleshBindings`**：计算骨骼与四面体的绑定权重。
- **`GenerateTetrahedralGrid`**：从三角形网格生成四面体网格。
- **`CreateFleshAsset`**：生成最终的 `UFleshAsset` 数据。

更多节点请查阅 `Engine/Plugins/Experimental/ChaosFlesh/Source/ChaosFleshNodes/` 下的头文件。

## Demo 示例

以下为创建一个自定义命令，从文件加载四面体并生成 `UFleshAsset` 的简化示例（`Build.cs` 需添加对应依赖）。

### FleshDemoCommand.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Engine/World.h"
#include "ChaosFlesh/Cmd/FleshAssetConversion.h"
#include "ChaosFlesh/ChaosFleshEditorPlugin.h"

class FleshDemoCommand
{
public:
    static void Run(const TArray<FString>& Args, UWorld* World);
};
```

### FleshDemoCommand.cpp

```cpp
#include "FleshDemoCommand.h"
#include "ChaosFlesh/FleshAsset.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "PackageTools.h"

void FleshDemoCommand::Run(const TArray<FString>& Args, UWorld* World)
{
    if (Args.Num() < 1)
    {
        UE_LOG(LogTemp, Error, TEXT("Usage: FleshDemoCommand <FilePath>"));
        return;
    }

    FString FilePath = Args[0];

    // 1. 读取四面体网格
    auto Collection = FFleshAssetConversion::ImportTetFromFile(FilePath);
    if (!Collection)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to import file: %s"), *FilePath);
        return;
    }

    // 2. 创建资产对象
    FString PackageName = "/Game/DemoFleshAsset";
    UPackage* Package = CreatePackage(*PackageName);
    UFleshAsset* NewAsset = NewObject<UFleshAsset>(Package, FName("DFA"), RF_Public | RF_Standalone);
    NewAsset->SetCollection(*Collection);

    // 3. 保存
    FAssetRegistryModule::AssetCreated(NewAsset);
    Package->MarkPackageDirty();
    UPackage::SavePackage(Package, NewAsset, RF_Public | RF_Standalone, *FPackageName::LongPackageNameToFilename(PackageName, FPackageName::GetAssetPackageExtension()));

    UE_LOG(LogTemp, Log, TEXT("Created FleshAsset at %s"), *PackageName);
}
```

## 模块依赖

### ChaosFleshEditor 的依赖

该模块在 `Build.cs` 中声明了以下独特依赖（省略了 Core/Engine/UnrealEd 等通用依赖）：

| 模块 | 用途 |
|---|---|
| `ChaosFlesh` | 运行时核心模拟逻辑与数据定义 |
| `ChaosFleshEngine` | 引擎层集成（如 `UFleshComponent`） |
| `ChaosFleshNodes` | Dataflow 节点定义 |
| `DataflowCore` / `DataflowEditor` | Dataflow 图表编辑基础设施 |
| `FleshCollection` | 四面体集合数据处理 |
| `MeshDescription` | 三角形网格导入与转换 |
| `AssetTools` / `AssetRegistry` | 资产管理 |
| `ThumbnailRendering` | 缩略图渲染 |
| `SlateStyle` | 图标与样式 |

## 维护状态

### 近期更新

- 2025-10-22 a1039b21 — USD: Disabled UE allocator in USD for Windows.
- 2025-10-17 7ab79237 — USD: Disabled UE allocator in USD for Windows.
- 2025-10-17 be609b71 — [Backout] - CL47041219
- 2025-10-03 71e223a6 — Dataflow: (内容未完整提供，推测为 Dataflow 改进)
- 2025-10-01 dca9c2ee — Add a way for each dataflow editors to hide geometry cache properties in the preview menu based on t...

### 维护评价

| 指标 | 状态 |
|---|---|
| 创建时间 | 2025-10-01（不足一个月） |
| 最近更新 | 2025-10-22（持续活跃） |
| 功能性更新 | 是（Dataflow、USD 支持） |
| 已知问题 | 部分导入功能（ImportTetFromFile）当前被禁用，需等待后续修复 |
| 是否推荐生产使用 | **不推荐**。插件仍标记为实验性（IsExperimentalVersion = true），API 可能不稳定，功能尚未完备。建议用于原型验证和技术研究。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh)
- [官方文档](https://docs.unrealengine.com/5.7/)（暂未提供独立文档页）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh/Tests)（若存在）